"""The AI 질문 transport (P6.S4): the wire, the row, and the things that say nothing.

The **real** endpoint over the **real** loop and the **real** tools, driven by
`test_agent_loop`'s scripted model through ``create_app(agent_client=…)``. No
model call, no key, no network — ``GEMINI_API_KEY`` is required neither to import
this module nor to build the app, which is the property the seam exists for.

The endpoint opens its **own** session rather than borrowing a request
dependency's (a streaming response outlives the handler), so there is nothing to
override here: filling ``app.state.session_factory`` with the in-memory engine
exercises exactly the path production takes.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.agent import ToolContext, run_turn
from mijual.config import Settings
from mijual.db.models import Base, ConversationTurn
from mijual.web.app import create_app
from mijual.web.ask import TurnLimiter, _Released
from mijual.web.conversationstore import is_session_hash, new_session_hash
from mijual.web.csrf import CSRF_HEADER
from mijual.web.errors import ApiError
from test_agent_loop import QUOTE, ScriptedModel, calls, says
from test_agent_tools import R1_RCEPT, WITHDRAWN_RCEPT, _corpus

#: search → read → answer. The same shape `test_agent_loop` proves the loop with.
ANSWER_TURN = (
    calls("search_events", query="계양전기"),
    calls("get_event", rcept_no=R1_RCEPT),
    says(f"매매기간은 「{QUOTE}」로 공시되어 있습니다[[cite:c3]]."),
)
#: 철회 — ① the cited status fact, ② the signed family sentence.
REFUSAL_TURN = (
    calls("get_event", rcept_no=WITHDRAWN_RCEPT),
    says("이 유상증자는 철회되었습니다. 철회된 공시는 해설하지 않습니다."),
)


class _Ask:
    """The client, the app and the store — one handle so a test reads as one story."""

    def __init__(self, client: TestClient, factory, today) -> None:
        self.client = client
        self.app = client.app
        self.factory = factory
        self.today = today

    def turn(self, question: str, *rounds, **body):
        self.app.state.agent_client = lambda: ScriptedModel(*rounds)
        return self.client.post("/ask", json={"question": question, **body})

    def rows(self) -> list[ConversationTurn]:
        with self.factory() as session:
            return list(session.scalars(select(ConversationTurn).order_by(ConversationTurn.id)))


def frames(response) -> list[tuple[str, dict]]:
    """``event:``/``data:`` pairs, in arrival order."""
    assert response.headers["content-type"].startswith("text/event-stream")
    parsed = []
    for block in response.text.strip().split("\n\n"):
        name, data = block.splitlines()
        parsed.append((name.removeprefix("event: "), json.loads(data.removeprefix("data: "))))
    return parsed


@pytest.fixture()
def ask():
    today = datetime.now(timezone(timedelta(hours=9))).date()
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        _corpus(session, today=today)
        session.commit()

    app = create_app(Settings(session_secret="test-session-secret", redis_url=""))
    app.state.session_factory = factory
    with TestClient(app, headers={CSRF_HEADER: "1"}) as client:
        yield _Ask(client, factory, today)


def test_the_handle_arrives_first_and_the_turn_lands_as_one_row(ask) -> None:
    """The contract `P6.S5` renders, and the log R7 signs — from one stream."""
    handle = new_session_hash()
    response = ask.turn(
        "계양전기 증서 언제까지예요?", *ANSWER_TURN, session=handle, scope_rcept_no=R1_RCEPT
    )
    assert response.status_code == 200
    # 스트림은 캐시되지 않고, 프록시 버퍼링을 끄라고 말한다.
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-accel-buffering"] == "no"

    sent = frames(response)
    # The handle is frame one, so the browser can keep the thread before a single
    # sentence arrives — and a valid client token round-trips untouched.
    assert sent[0] == ("session", {"session_hash": handle, "scope": R1_RCEPT})
    assert [name for name, _ in sent] == [
        "session", "tool_row", "tool_row", "citation", "text", "footer", "done"
    ]
    # 칩은 그 문장과 함께 도착한다: the definition precedes the sentence naming it.
    assert sent[3][1]["number"] == 1 and sent[3][1]["quote"] == QUOTE
    assert sent[4][1]["citations"] == [1] and QUOTE in sent[4][1]["text"]
    end = sent[-1][1]

    (row,) = ask.rows()
    # The row is the terminal, field for field — the log cannot disagree with the
    # reader, because it was never re-read out of the prose.
    assert row.session_hash == handle and row.scope_rcept_no == R1_RCEPT
    assert row.question == "계양전기 증서 언제까지예요?"
    assert (row.kind, row.answer) == (end["kind"], end["answer"])
    assert row.evidence == end["evidence"] == [R1_RCEPT]
    assert row.quotes == end["quotes"] == [QUOTE]
    assert row.refusal_category is None


def test_a_refusal_stores_its_family_and_a_junk_handle_is_replaced(ask) -> None:
    """거절도 저장 시 인용 동반 (R7) — and nothing client-controlled reaches the column."""
    response = ask.turn("썸에이지 증자 어떻게 됐나요?", *REFUSAL_TURN, session="../etc/passwd")
    sent = frames(response)
    minted = sent[0][1]["session_hash"]
    assert minted != "../etc/passwd" and is_session_hash(minted)
    assert "scope" not in sent[0][1]  # 전체 공시 — an absent value is absent
    assert [name for name, _ in sent].count("refusal") == 1

    (row,) = ask.rows()
    assert row.session_hash == minted and row.kind == "refusal"
    assert row.refusal_category == "철회"  # one of the five signed families
    assert row.answer.endswith("철회된 공시는 해설하지 않습니다.")
    # 거절도 인용 동반: the 철회 fact carries its 근거. This fixture's filing has no
    # 본문 span, so the chip is the **API-tier** one (R3: 접수번호가 인용 핸들) — a
    # citation, not a missing one, and 인용 칩 원문 is honestly empty for it.
    assert row.evidence == [WITHDRAWN_RCEPT] and row.quotes == []
    chips = [data for name, data in sent if name == "citation"]
    assert len(chips) == 1 and chips[0]["api_tier"] is True and "quote" not in chips[0]


def test_a_refusable_request_never_becomes_a_stream(ask) -> None:
    """Before the first frame there is an envelope; after it, only typed terminals."""
    empty = ask.client.post("/ask", json={"question": "   "})
    assert empty.status_code == 400
    error = empty.json()["error"]
    # No Korean is invented for an error the design wrote no copy for.
    assert error["code"] == "invalid_question" and "message_ko" not in error

    junk = ask.client.post("/ask", json={"question": "언제요?", "scope_rcept_no": "nope"})
    assert junk.status_code == 400 and junk.json()["error"]["code"] == "invalid_scope"

    # The service-wide guard, inherited without opting in (`P5.S7`).
    bare = ask.client.post("/ask", json={"question": "언제요?"}, headers={CSRF_HEADER: ""})
    assert bare.status_code == 403 and bare.json()["error"]["code"] == "csrf_required"

    assert ask.rows() == []


def test_a_disconnected_turn_cannot_disagree_with_a_terminal(ask) -> None:
    """중지 leaves no terminal, so the row is built from the frames that were sent."""
    with ask.factory() as session:
        events = list(
            run_turn(
                ToolContext(
                    session=session,
                    today=ask.today,
                    session_hash=new_session_hash(),
                    settings=Settings(),
                ),
                "계양전기 증서 언제까지예요?",
                client=ScriptedModel(*ANSWER_TURN),
            )
        )

    partial = _Released()
    for event in events[:-1]:  # everything the reader received, and no terminal
        partial.absorb(event)
    end = events[-1]
    assert (partial.kind, partial.answer, partial.refusal_category) == (
        end.kind, end.answer, end.refusal_category
    )
    assert (partial.evidence, partial.quotes) == (end.evidence, end.quotes)
    assert partial.storable
    # 중지 pressed before the first sentence: no 답변 to replay, so no row.
    assert not _Released().storable


def test_rate_limiting_refuses_without_a_word_of_copy(ask) -> None:
    """An operations decision with zero UI copy — and no identity anywhere in it."""
    ask.app.state.ask_limiter = TurnLimiter(per_session=0)
    refused = ask.turn("언제요?", *ANSWER_TURN)
    assert refused.status_code == 429
    error = refused.json()["error"]
    assert error["code"] == "rate_limited" and "message_ko" not in error
    assert ask.rows() == []  # a refused turn is not a turn

    limiter = TurnLimiter(max_concurrent=1, per_session=2, window_s=60)
    limiter.acquire("a" * 32)
    with pytest.raises(ApiError) as busy:  # the ceiling that actually bounds spend
        limiter.acquire("b" * 32)
    assert busy.value.status_code == 429 and busy.value.message_ko is None
    limiter.release()

    handle = "d" * 32
    for _ in range(2):
        limiter.acquire(handle)
        limiter.release()
    with pytest.raises(ApiError):
        limiter.acquire(handle)
    # The window *is* the retention: nothing outlives it and nothing is written —
    # and a slot that was never released expires rather than wedging the endpoint.
    limiter.acquire("e" * 32)
    limiter._sweep(time.monotonic() + 3_600)
    assert limiter._recent == {} and limiter._live == []
