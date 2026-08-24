"""The agent core (P6.S3): does the **model** drive, and can an unverified claim exist?

No live call, no key, no network. A twenty-line scripted client implements
:class:`~mijual.agent.client.ModelClient` and drives the **real**
:func:`~mijual.agent.loop.run_turn` against the **real** tools over the same
in-memory corpus ``test_agent_tools.py`` builds — which is the only way the
phase's two load-bearing properties can be tested rather than asserted:

* *agent, not chain* — the script decides when a tool is called, so a loop with a
  hardcoded fetch would fail the no-tool-round test, and a loop that could not
  chain rounds would fail the multi-round one;
* *citation forcing at the generation boundary* — the script can say anything at
  all, and what reaches the stream is decided by the gate.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mijual.agent import ToolContext, TurnBudget, run_turn
from mijual.agent.client import (
    AgentGeminiClient,
    CallChunk,
    GeminiError,
    ModelCall,
    TextChunk,
    ToolMessage,
    Usage,
    UsageChunk,
)
from mijual.agent.events import (
    CitationEvent,
    DataBlockEvent,
    FooterEvent,
    LinksEvent,
    RefusalEvent,
    StatusEvent,
    TextEvent,
    ToolRowEvent,
    TurnEnd,
)
from mijual.config import Settings
from mijual.db.models import Base
from mijual.web.conversationstore import new_session_hash
from test_agent_tools import R1_RCEPT, R2_RCEPT, WITHDRAWN_RCEPT, _corpus

#: The one verbatim 본문 span the fixture carries, and its citation ref.
QUOTE = "신주인수권증서의 상장·매매기간"


class ScriptedModel:
    """A model that says exactly what the script says — and chooses the tools."""

    def __init__(self, *rounds: list) -> None:
        self.rounds = list(rounds)
        self.seen: list[list] = []

    def stream(self, *, messages, system_instruction):
        self.seen.append(list(messages))
        self.instruction = system_instruction
        script = self.rounds.pop(0) if self.rounds else [TextChunk("")]
        yield from script
        yield UsageChunk(
            usage=Usage(prompt_tokens=1000, output_tokens=80, total_tokens=1080),
            thinking_level="LOW",
        )


def says(text: str, size: int = 7) -> list[TextChunk]:
    """Prose delivered in small chunks — sentences and markers must survive them."""
    return [TextChunk(text[i : i + size]) for i in range(0, len(text), size)]


def calls(name: str, **args) -> list[CallChunk]:
    return [CallChunk(ModelCall(name=name, args=args))]


@pytest.fixture()
def ctx():
    today = datetime.now(timezone(timedelta(hours=9))).date()
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    _corpus(session, today=today)
    yield ToolContext(
        session=session,
        today=today,
        session_hash=new_session_hash(),
        settings=Settings(),
    )
    session.close()


def of(events, kind):
    return [event for event in events if isinstance(event, kind)]


def test_the_model_chooses_the_tools_and_chains_rounds_until_it_can_answer(ctx) -> None:
    """search → (look at the result) → read → answer: three rounds, all its own."""
    model = ScriptedModel(
        calls("search_events", query="계양전기"),
        calls("get_event", rcept_no=R1_RCEPT),
        # c3 = the 본문 quote get_event added; c1/c2 were the search's two API-tier
        # handles. Reference ids are the **turn's**, so the second tool continues
        # the numbering instead of restarting it. The two markers sit on opposite
        # sides of the full stop because the live model uses both (and the
        # no-space `.[[cite:…]]` form is what it actually wrote on 2026-08-22).
        says(f"매매기간은 「{QUOTE}」로 공시되어 있습니다[[cite:c3]]. 같은 공시가 근거입니다.[[cite:c3]]"),
    )
    events = list(run_turn(ctx, "계양전기 증서 언제까지예요?", client=model))

    rows = of(events, ToolRowEvent)
    assert [row.tool for row in rows] == ["search_events", "get_event"]
    assert rows[0].row.startswith("이벤트 검색 「계양전기」 → 2건")

    # Round 2 was decided *after* round 1's result went back to the model — the
    # chain exists because the model asked for it, not because the loop scripted it.
    assert any(isinstance(m, ToolMessage) for m in model.seen[1])
    fed = [m for m in model.seen[1] if isinstance(m, ToolMessage)][0]
    assert fed.name == "search_events"
    assert all("id" in citation for citation in fed.response["citations"])

    texts = of(events, TextEvent)
    assert len(texts) == 2 and QUOTE in texts[0].text
    # 같은 근거 = 같은 번호, and the chip is defined once, before its sentence.
    assert texts[0].citations == (1,) and texts[1].citations == (1,)
    chips = of(events, CitationEvent)
    assert len(chips) == 1 and chips[0].number == 1 and chips[0].quote == QUOTE
    assert events.index(chips[0]) < events.index(texts[0])

    end = events[-1]
    assert isinstance(end, TurnEnd) and end.status == "done" and end.kind == "answer"
    assert end.rounds == 3 and end.tool_calls == 2 and end.blocked == 0
    assert end.evidence == (R1_RCEPT,) and end.quotes == (QUOTE,)
    assert end.usage["calls"] == 3 and end.usage["thinking_levels"] == ["LOW"] * 3
    assert end.usage["cost_usd_estimate"] > 0  # ▷ estimate, never a billed figure
    assert of(events, FooterEvent)[0].count == 1
    # 공시 M건 읽음 (R16 D8): the search *listed* two events, the turn **read** one —
    # a server-known number, never parsed back out of a 도구 행.
    assert end.filings == 1


def test_the_status_line_narrates_the_turn_and_the_data_block_carries_its_근거(ctx) -> None:
    """R16 §1/§2.1/§2.3: one transient line, replaced — and 공시에서 읽은 값 rows."""
    model = ScriptedModel(
        calls("search_events", query="계양전기"),
        calls("get_event", rcept_no=R1_RCEPT),
        says(f"공시 원문은 「{QUOTE}」입니다[[cite:c3]]."),
    )
    events = list(run_turn(ctx, "계양전기 증서 매매기간요?", client=model))

    status = of(events, StatusEvent)
    # 항상 하나 (one id = replacement, never accumulation), transient, and the last
    # one is emitted **before** the first sentence — nothing narrates over prose.
    assert [event.phase for event in status] == ["read", "search", "write", "open", "write"]
    assert {event.block_id for event in status} == {"status"}
    assert not any(event.persistent for event in status)
    assert events.index(status[-1]) < events.index(of(events, TextEvent)[0])

    (block,) = of(events, DataBlockEvent)
    assert block.persistent and block.block_id == "data-1" and block.title is None
    (row,) = block.rows
    # The label is the field's own Korean name and the value is stated as one
    # string (a period as `Fields.tsx`'s `Period` writes it) — never a shape the
    # surface has to know how to render.
    assert row.label == "신주인수권증서 상장·매매기간" and " ~ " in row.value
    # 같은 근거 = 같은 번호: the row and the sentence carry one chip, defined once.
    assert row.citation == 1 and of(events, TextEvent)[0].citations == (1,)
    assert len(of(events, CitationEvent)) == 1


def test_an_unverified_claim_cannot_enter_the_stream(ctx) -> None:
    """R6: 인용 없는 주장은 생성 단계에서 차단 — and the four ways to fail it."""
    model = ScriptedModel(
        calls("get_event", rcept_no=R1_RCEPT),
        says(
            "계양전기는 자금 사정이 어렵습니다. "  # no marker at all
            "증자 규모는 확정되었습니다[[cite:c99]]. "  # an id no tool returned
            "총 조달금액은 1,234,567원입니다[[cite:c2]]. "  # a number from nowhere
            "공시는 「신주인수권증서 매매기간」이라고 적었습니다[[cite:c2]]. "  # not verbatim
            f"공시 원문은 「{QUOTE}」입니다[[cite:c2]]."  # the one that survives
        ),
    )
    events = list(run_turn(ctx, "얼마나 조달하나요?", client=model))

    texts = of(events, TextEvent)
    assert len(texts) == 1 and texts[0].text.endswith(f"「{QUOTE}」입니다.")
    end = events[-1]
    assert end.blocked == 4 and end.kind == "answer"
    assert "1,234,567" not in end.answer and "어렵습니다" not in end.answer


def test_the_five_families_are_selected_by_their_signed_sentences(ctx) -> None:
    """거절 = 3단 구조, 인용 강제 포함 — and a family is never paraphrased."""
    # 철회: ① the locked status fact with its own chip, ② the family sentence.
    withdrawn = ScriptedModel(
        calls("get_event", rcept_no=WITHDRAWN_RCEPT),
        says("이 유상증자는 철회되었습니다. 철회된 공시는 해설하지 않습니다."),
    )
    events = list(run_turn(ctx, "썸에이지 증자 어떻게 됐나요?", client=withdrawn))
    assert of(events, TextEvent)[0].text == "이 유상증자는 철회되었습니다."
    assert of(events, TextEvent)[0].citations == (1,)  # 거절도 인용 강제 대상
    refusal = of(events, RefusalEvent)[0]
    assert refusal.family == "철회"
    assert refusal.text == "철회된 공시는 해설하지 않습니다."
    assert {link["kind"] for link in of(events, LinksEvent)[0].links} >= {"dart", "event", "stocks"}
    end = events[-1]
    assert end.kind == "refusal" and end.refusal_category == "철회"
    assert end.evidence == (WITHDRAWN_RCEPT,)

    # 계산 요청: the fixed redirect sentence — and **not one tool call**, which is
    # the loop having no mandatory pre-fetch rather than the model being lucky.
    asked = ScriptedModel(
        says("해설은 계산하지 않습니다 — 계산은 검증된 수치로 내 종목 조회가 합니다.")
    )
    events = list(run_turn(ctx, "300주면 얼마예요?", client=asked))
    assert not of(events, ToolRowEvent)
    assert events[-1].tool_calls == 0 and events[-1].refusal_category == "계산 요청"

    # 확정 전 금액: say the known cited facts, refuse **only** the amount.
    partial = ScriptedModel(
        calls("get_event", rcept_no=R1_RCEPT),
        says(f"공시에 적힌 기간은 「{QUOTE}」입니다[[cite:c2]]. 확정 전 금액은 해설하지 않습니다."),
    )
    events = list(run_turn(ctx, "발행가 얼마예요?", client=partial))
    end = events[-1]
    assert end.refusal_category == "확정 전" and end.quotes == (QUOTE,)
    assert end.answer.startswith("공시에 적힌 기간은") and end.answer.endswith(
        "확정 전 금액은 해설하지 않습니다."
    )


def test_a_figure_reaches_the_reader_grouped_and_a_quote_reaches_it_verbatim(ctx) -> None:
    """`P6.F1`: 3,200원 like every other surface — and nothing else respelled.

    One turn covers the whole rule: the raw form is grouped, the already-grouped
    form is traced and left alone (membership normalizes separators), 접수번호 and
    a year are not figures, and a verified 「…」 span is copied byte for byte even
    when the same digits outside it are grouped.
    """
    model = ScriptedModel(
        calls("get_event", rcept_no=R1_RCEPT),
        says(
            "예정발행가액은 3200원입니다[[cite:c2]]. 같은 값은 3,200원으로도 적습니다[[cite:c2]]. "
            f"접수번호 {R1_RCEPT}는 2026년 공시입니다[[cite:c2]]. "
            f"원문은 「{QUOTE}」입니다[[cite:c2]]."
        ),
    )
    events = list(run_turn(ctx, "발행가 얼마로 적혀 있나요?", client=model))

    texts = [event.text for event in of(events, TextEvent)]
    assert texts[0] == "예정발행가액은 3,200원입니다." and texts[1].startswith("같은 값은 3,200원")
    # An identifier is not a figure, and neither is a year.
    assert texts[2] == f"접수번호 {R1_RCEPT}는 2026년 공시입니다."
    assert texts[3] == f"원문은 「{QUOTE}」입니다."
    end = events[-1]
    # 로그는 읽힌 그대로 (P6.S4's rule): the stored answer carries the reader's form.
    assert end.blocked == 0 and "3,200원" in end.answer and "3200원" not in end.answer

    # The same figure inside a verified span stays exactly as the filing writes it.
    quoted = ScriptedModel(
        calls("get_event", rcept_no=R2_RCEPT),
        says("전환가액은 1591원입니다[[cite:c1]]. 원문 표기는 「1591」입니다[[cite:c1]]."),
    )
    said = [event.text for event in of(list(run_turn(ctx, "전환가?", client=quoted)), TextEvent)]
    assert said == ["전환가액은 1,591원입니다.", "원문 표기는 「1591」입니다."]


def test_a_turn_that_verifies_nothing_falls_back_and_a_budget_ends_it_honestly(ctx) -> None:
    """Degrade rules: 폴백 when nothing survived, `aborted` when a ceiling trips."""
    nothing = ScriptedModel(says("잘 모르겠지만 아마 괜찮을 겁니다."))
    events = list(run_turn(ctx, "괜찮나요?", client=nothing))
    assert of(events, RefusalEvent)[0].family == "검증 미통과 폴백"
    assert events[-1].kind == "refusal" and events[-1].blocked == 1
    assert events[-1].answer.startswith("이 데이터는 검증을 통과하지 못했습니다.")

    # A model that never stops asking for tools is stopped by the round ceiling —
    # and the partial output above it stands (nothing is retracted).
    forever = ScriptedModel(*[calls("get_portfolio") for _ in range(5)])
    events = list(run_turn(ctx, "뭐가 급한가요?", client=forever, budget=TurnBudget(max_rounds=2)))
    assert events[-1].status == "aborted" and events[-1].reason == "round_budget"
    assert len(of(events, ToolRowEvent)) == 2

    # The client's own ceiling refuses the call **before** spending (N25) — the
    # real client, with no key touched, because the budget is checked first.
    broke = AgentGeminiClient(settings=Settings(), max_calls=0)
    events = list(run_turn(ctx, "안녕하세요", client=broke))
    assert events[-1].status == "aborted" and events[-1].reason == "call_budget"

    class Falls:
        """Reads a filing, releases one verified sentence, then the stream dies."""

        def __init__(self) -> None:
            self.round = 0

        def stream(self, *, messages, system_instruction):
            self.round += 1
            if self.round == 1:
                yield from calls("get_event", rcept_no=R1_RCEPT)
                yield UsageChunk(usage=Usage(), thinking_level="LOW")
                return
            yield TextChunk(f"공시 원문은 「{QUOTE}」입니다[[cite:c2]]. ")
            raise GeminiError("ServerError")

    events = list(run_turn(ctx, "매매기간요?", client=Falls()))
    assert events[-1].status == "error" and events[-1].reason == "ServerError"
    assert events[-1].answer.endswith(f"「{QUOTE}」입니다.")  # 부분 답변 유지
    assert not of(events, FooterEvent)  # 완료가 아니므로 푸터 없음


def test_a_saved_의견_is_confirmed_and_never_refused(ctx) -> None:
    """R6 §의견 signs 「자동 저장 + 확인 한 줄」 — and no refusal (`P6.S7`).

    Nothing citable is expected from a feedback turn, so the 폴백 family (a claim
    about *data* that failed verification) would contradict the confirmation the
    surface prints under the tool's own row.
    """
    saved = ScriptedModel(calls("save_feedback", text="인용이 좋네요"), says("저장했습니다."))
    events = list(run_turn(ctx, "의견 남길게요", client=saved))
    assert of(events, ToolRowEvent)[0].ok is True
    assert of(events, RefusalEvent) == []
    assert events[-1].kind == "answer"
    assert events[-1].answer == "의견을 저장했습니다 — 운영자가 확인합니다."
