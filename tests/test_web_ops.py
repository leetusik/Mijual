"""운영 관제 (P5.S9): the door's prohibitions, and the panel's read-only shape.

In-memory SQLite and dependency overrides, the established pattern. The cases are
the things R7 §6.4/§6.5 and `security` state as prohibitions — a failure that
names which field was wrong, a reader cookie that opens the operator's panel (or
the reverse), a mutation endpoint anywhere in the panel, a reader surface that
links it, and a conversation port that invents rows it does not have.
"""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.config import Settings
from mijual.db.models import Base, Extraction, ExtractionCall, PipelineRun, utcnow
from mijual.mail import ConsoleMailer
from mijual.web.app import create_app
from mijual.web.auth import OPS_COOKIE, SESSION_COOKIE
from mijual.web.conversationstore import (
    DbConversations,
    new_session_hash,
    record_feedback,
    record_turn,
)
from mijual.web.csrf import CSRF_HEADER
from mijual.web.deps import get_session, get_write_session
from mijual.web.opsreads import open_decisions
from test_web_auth import signup_and_verify

OPS_ID, OPS_PASSWORD = "operator", "ops-password-1"


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    # P13: a reader account now takes 가입 + 인증, and the code is printed here.
    outbox = io.StringIO()

    app = create_app(
        Settings(
            session_secret="test-session-secret",
            ops_id=OPS_ID,
            ops_password=OPS_PASSWORD,
            # No broker in a test: the lock chip must degrade, not fail.
            redis_url="",
        ),
        # `P6.S1`'s real port over the same in-memory database — the panel is
        # exercised against what it will actually serve, not against a stub.
        conversations=DbConversations(factory),
        mailer=ConsoleMailer(stream=outbox),
    )
    app.dependency_overrides[get_session] = lambda: session

    def _write():
        # Mirrors :func:`get_write_session` — commit on a normal return, roll
        # back on any exception (``P13.F1``). These tests sign up and verify
        # through the shared helper, so a fixture more forgiving than the runtime
        # would let a broken write path pass here too.
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    app.dependency_overrides[get_write_session] = _write
    with TestClient(app, headers={CSRF_HEADER: "1"}) as test_client:
        test_client.outbox = outbox  # type: ignore[attr-defined]
        test_client.db = session  # type: ignore[attr-defined]
        yield test_client
    session.close()


def _open_the_door(client):
    response = client.post("/ops/login", json={"id": OPS_ID, "password": OPS_PASSWORD})
    assert response.status_code == 200 and response.json() == {"authenticated": True}
    return response


def test_every_way_to_fail_the_door_fails_identically(client) -> None:
    """R7: 실패 응답 균일 + 어느 필드가 틀렸는지 구분 금지.

    Unknown 운영자 ID, wrong password and an unconfigured credential are one
    answer — byte-identical body, same status, same code — so a failure discloses
    neither whether an operator exists nor which half was wrong.
    """
    wrong_password = client.post("/ops/login", json={"id": OPS_ID, "password": "nope-nope"})
    unknown_id = client.post("/ops/login", json={"id": "someone", "password": OPS_PASSWORD})
    assert wrong_password.status_code == unknown_id.status_code == 401
    assert wrong_password.content == unknown_id.content
    assert wrong_password.json()["error"]["code"] == "invalid_credentials"
    # No Korean is invented for it: 「자격증명이 올바르지 않습니다」 is client copy.
    assert "message_ko" not in wrong_password.json()["error"]
    # Neither failure minted a session.
    assert OPS_COOKIE not in wrong_password.cookies

    # …and a service with no credential configured answers exactly the same way.
    closed = create_app(Settings(redis_url=""))
    closed.dependency_overrides[get_session] = lambda: client.db
    closed.dependency_overrides[get_write_session] = lambda: client.db
    with TestClient(closed, headers={CSRF_HEADER: "1"}) as shut:
        unset = shut.post("/ops/login", json={"id": OPS_ID, "password": OPS_PASSWORD})
    assert unset.status_code == 401 and unset.content == wrong_password.content


def test_the_two_credentials_cannot_open_each_other_s_surface(client) -> None:
    """Separate credential, separate cookie, separate table — and no join anywhere."""
    assert client.get("/ops/overview").status_code == 401
    assert client.get("/ops/session").json() == {"authenticated": False}

    # A reader account opens 내 포트폴리오 and nothing under /ops.
    signup_and_verify(client, email="reader@mijual.kr", password="portfolio-8")
    assert client.get("/portfolio").status_code == 200
    assert client.get("/ops/overview").status_code == 401
    assert client.get("/ops/overview").json()["error"]["code"] == "ops_unauthenticated"
    assert SESSION_COOKIE in client.cookies and OPS_COOKIE not in client.cookies

    _open_the_door(client)
    assert client.cookies[OPS_COOKIE] != client.cookies[SESSION_COOKIE]
    assert client.get("/ops/overview").status_code == 200
    assert client.get("/ops/session").json() == {"authenticated": True}

    # An operator session is not a reader session: dropping the reader's cookie
    # leaves 내 포트폴리오 shut while the panel stays open.
    client.cookies.delete(SESSION_COOKIE)
    assert client.get("/portfolio").status_code == 401
    assert client.get("/ops/overview").status_code == 200

    # 로그아웃 is immediate — the row is gone, so the cookie is worthless.
    client.post("/ops/logout")
    assert client.get("/ops/overview").status_code == 401


def test_the_panel_has_no_mutation_endpoint_and_no_reader_surface_links_it(client) -> None:
    """§6.5 전 화면 읽기 전용, and R7's "reader chrome 어디에서도 링크 금지"."""
    unsafe = {"post", "put", "patch", "delete"}
    paths = {
        path: {method for method in methods if method in unsafe}
        for path, methods in client.app.openapi()["paths"].items()
        if path.startswith("/ops")
    }
    assert paths, "the ops surface is missing entirely"
    # The door's own session handling is the only exception, and it touches
    # nothing but its own row.
    assert {p: sorted(m) for p, m in paths.items() if m} == {
        "/ops/login": ["post"],
        "/ops/logout": ["post"],
    }
    # §6.3: the vocky route exists now that `P5.S18` decided the shape — and it is
    # a read like the rest (the `unsafe` map above already proves it has no other
    # method). Unwired, it reports 연결 전 rather than failing the tab.
    assert "/ops/vocky" in paths
    _open_the_door(client)
    observation = client.get("/ops/vocky").json()
    assert observation["state"] == "unconfigured" and observation["rows"] == []

    client.post("/ops/logout")
    for path in ("/board/summary", "/board", "/stocks?q=none", "/portfolio/sample", "/health"):
        body = client.get(path).text
        assert "/ops" not in body, f"{path} mentions the ops path"


def test_the_conversation_port_serves_honest_zeros_and_no_join(client) -> None:
    """An empty store answers 0건 — not 「준비 중」, not a 404 — and a full one answers rows.

    `P6.S1` replaced ``EmptyConversations`` with a real implementation of the same
    port, so the three tabs come alive **through no route change at all**: the
    last block below writes two rows with the storage's write API and reads them
    back through the very endpoints P5 shipped.

    And the 사용자 tab is two independent reads: nothing in either block can be
    matched against the other (계정↔대화 연결·조인·추정 매칭 금지).
    """
    _open_the_door(client)
    for path in ("/ops/conversations", "/ops/sessions", "/ops/feedback"):
        body = client.get(path).json()
        assert body == {"count": 0, "rows": []}, path
        assert "next_cursor" not in body  # absent, never null

    signup_and_verify(client, email="reader@mijual.kr", password="portfolio-8")
    users = client.get("/ops/users").json()
    account = users["accounts"]["rows"][0]
    assert account["email"] == "reader@mijual.kr"
    assert account["holdings"] == 0
    # 최소 열람: a count, never the contents; and the password is not mentioned.
    assert "password_hash" not in account and "shares" not in account
    # An absent preference row means the default (7일 + 1일), not "off".
    assert account["notifications"] == {"lead_days": [7, 1], "stored": False}
    # R7's 샘플 로드 여부 has no server-side fact in P5 — absent, never a false.
    assert "sample_loaded" not in account
    assert users["sessions"] == {"count": 0, "rows": []}

    # …and the same three routes, once the store holds a turn and a comment.
    thread = new_session_hash()
    record_turn(
        client.db,
        session_hash=thread,
        question="증서 매매 언제 끝나나요?",
        kind="answer",
        answer="증서 매매기간은 2026-05-20까지입니다.",
        scope_rcept_no="20260508000928",
        evidence=["20260508000928"],
        quotes=["신주인수권증서의 매매기간: 2026.05.14 ~ 2026.05.20"],
    )
    record_feedback(client.db, text="설명이 좋았어요", session_hash=thread)
    client.db.commit()

    log = client.get("/ops/conversations").json()
    assert log["count"] == 1 and log["rows"][0]["session_hash"] == thread
    assert log["rows"][0]["scope"] == "20260508000928"
    assert log["rows"][0]["at"].endswith("+09:00")
    assert client.get("/ops/sessions").json()["rows"][0]["questions"] == 1
    assert client.get("/ops/feedback").json()["rows"][0]["text"] == "설명이 좋았어요"
    # The 사용자 tab's second table is the same aggregate, still unjoined.
    assert client.get("/ops/users").json()["sessions"]["count"] == 1
    # 유형 filter, already wired by `P5.S9` — no refusal was stored.
    assert client.get("/ops/conversations?kind=refusal").json() == {"count": 0, "rows": []}


def test_the_overview_serves_both_halves_of_the_missing_beat_row_and_degrades(client) -> None:
    """The backend states when a run was due and what ran; it fabricates neither.

    R7 wants 「실행 기록 없음」 in alert ink for a beat that did not fire, derived
    from the scheduled time — so the panel gets the schedule's due instants and
    the run log, and joins them itself.
    """
    _open_the_door(client)
    client.db.add(
        PipelineRun(
            label="daily-morning",
            trigger="beat",
            started_at=utcnow(),
            finished_at=utcnow(),
            ok=True,
            requests=12,
            calls=0,
            cost_usd=0.0,
            spend_line="spend     : 12 OpenDART request(s), 0 LLM call(s), ▷ $0.0000 estimated",
            stages=[{"name": "gates", "status": "ok", "summary": "…"}],
        )
    )
    client.db.commit()

    body = client.get("/ops/overview").json()
    assert body["beat"]["timezone"] == "Asia/Seoul"
    assert {e["name"] for e in body["beat"]["entries"]} == {
        # `notify-deadlines` (P4.S2) is here for a reason the panel makes
        # load-bearing: the 개요 tab joins `beat.entries[].due` against the run
        # log **by the entry's own kwargs label**, so a scheduled send that
        # wrote no `pipeline_run` row would render as 「실행 기록 없음」 forever.
        "daily-pipeline-morning", "daily-pipeline-evening", "weekly-resync",
        "notify-deadlines",
    }
    assert all("due" in entry for entry in body["beat"]["entries"])
    run = body["runs"]["rows"][0]
    assert run["trigger"] == "beat" and run["requests"] == 12
    # ▷ is quoted pipeline output in this panel and must never become 「추정」.
    assert run["spend_line"].endswith("▷ $0.0000 estimated") and "추정" not in run["spend_line"]
    # Redis is unreachable here: the chip says so, and the tab still renders.
    assert body["lock"]["key"] == "mijual:lock:pipeline"
    assert body["lock"]["state"] == "unknown"
    assert body["gates"]["events"]["exposable"] == 0


def test_the_gate_queue_rates_are_over_distinct_rcept_no_field_key(client) -> None:
    """R7 fixes the basis (633 = distinct pairs, 16 duplicate rows) and it is served.

    A rate whose denominator is implicit is a rate nobody can check, so the
    denominator ships beside the counts — and a code with no Korean carries no
    ``reason_ko`` key at all rather than a fallback phrase (§6.1).
    """
    _open_the_door(client)
    # One rcept_no sitting under two filing_version rows is exactly how the live
    # 649-vs-633 gap arises (N21's pairing residue), so the duplicate is modelled
    # that way rather than invented.
    for version_id, rcept_no, field_key, status, reason in (
        (1, "20260101000001", "warrant_trading_period", "failed", "span_unresolved"),
        (2, "20260101000001", "warrant_trading_period", "failed", "span_unresolved"),
        (3, "20260101000002", "warrant_trading_period", "failed", "span_unresolved"),
        (4, "20260101000003", "issue_price_formula", "passed", None),
    ):
        client.db.add(
            Extraction(
                event_id=version_id,
                filing_version_id=version_id,
                rcept_no=rcept_no,
                field_key=field_key,
                gate_status=status,
                gate_reason_code=reason,
            )
        )
    client.db.commit()

    queue = client.get("/ops/gates").json()
    assert queue["basis"] == {
        "stored_rows": 4,
        "distinct_rows": 3,
        "duplicates": 1,
        "key": "(rcept_no, field_key)",
    }
    unresolved = next(r for r in queue["reasons"] if r["code"] == "span_unresolved")
    # Counted over stored rows, rated over the distinct basis — both served, so
    # nobody has to guess which denominator a percentage came from.
    assert unresolved["count"] == 3 and unresolved["distinct_count"] == 2
    assert unresolved["rate"] == "0.6667"
    # The Korean is the code's own (gates.outcome); an unknown code gets none.
    assert unresolved["reason_ko"] == "인용 구절을 원문에서 찾지 못했습니다"
    passed = next(r for r in queue["reasons"] if r["gate_status"] == "passed")
    assert "reason_ko" not in passed and passed["code"] == ""


def test_the_spend_block_labels_its_window_and_never_shows_cumulative_as_daily(client) -> None:
    """R7: 누적치를 일일치처럼 보이게 하지 말 것 — 라벨에 구간 명시."""
    _open_the_door(client)
    client.db.add(ExtractionCall(task="r1_prose", status="ok", total_tokens=1200, cost_usd=0.0031))
    client.db.add(
        PipelineRun(label="cli", trigger="manual", started_at=utcnow(), requests=41, calls=1)
    )
    client.db.commit()

    spend = client.get("/ops/accuracy").json()["spend"]
    assert spend["llm"]["window"] == "cumulative"
    assert spend["llm"]["calls"] == 1 and spend["llm"]["tokens"] == 1200
    assert spend["llm"]["cost_line"].startswith("▷ $")
    assert spend["dart"]["window"] == "daily"
    assert spend["dart"]["quota"] == {
        "requests_per_day": 20000,
        "source": "operator (decisions O-1)",
    }
    assert spend["dart"]["days"][0]["requests"] == 41


def test_the_open_decisions_panel_quotes_the_document_and_the_lock_chip_stands_alone(
    client, tmp_path
) -> None:
    """P5.S17's two additions: 가동 전 미결's source, and the bar's own lock read.

    R7 fixes both — 「decisions 문서에서 읽어 렌더 — 패널에 직접 쓰지 않음」 and a
    lock chip that is live on every tab — so the panel quotes the doc's own
    still-open bullets verbatim, and the chip has a read that does not walk the
    corpus to answer.
    """
    _open_the_door(client)

    doc = tmp_path / "decisions.md"
    doc.write_text(
        "version: v0009\n\n### D-4 — Application LLM\n\n"
        "- **Status:** accepted\n"
        "- **Open, and operationally load-bearing:** an unattended beat run would\n"
        "  make that preset choice for a human.\n\n"
        "### D-5 — Schedule\n\n- **Decision:** operator-owned\n",
        encoding="utf-8",
    )
    quoted = open_decisions(doc)
    assert quoted["available"] and quoted["version"] == "v0009" and quoted["count"] == 1
    assert quoted["items"][0]["decision"] == "D-4"
    # Verbatim: the doc's own sentence, wrapped lines rejoined and nothing else.
    assert quoted["items"][0]["text"] == (
        "**Open, and operationally load-bearing:** an unattended beat run would "
        "make that preset choice for a human."
    )
    # A missing doc is a state, not a 500 — the panel then renders nothing.
    assert open_decisions(tmp_path / "gone.md") == {
        "available": False,
        "reason": "FileNotFoundError",
    }
    # The live doc is the panel's real source, and it parses.
    assert client.get("/ops/overview").json()["decisions"]["available"] is True

    chip = client.get("/ops/lock").json()
    assert chip["key"] == "mijual:lock:pipeline" and chip["state"] == "unknown"
    client.cookies.delete(OPS_COOKIE)
    assert client.get("/ops/lock").status_code == 401
