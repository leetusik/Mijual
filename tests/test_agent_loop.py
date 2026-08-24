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
    CalcBlockEvent,
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


def computes(**args) -> list[CallChunk]:
    """A `calculate` call. Its own helper because the tool has an argument `name`."""
    return [CallChunk(ModelCall(name="calculate", args=args))]


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


def test_an_unverified_claim_is_stripped_and_marked_never_dropped(ctx) -> None:
    """R16 §2.5: 문장은 남고, 검증되지 않은 것만 문장에서 빠진다 — the four ways.

    One turn covers the whole of `P9.S4`: a sentence with nothing to cite ships,
    an unresolvable marker is removed (and counted) while its sentence stands, a
    figure no tool returned becomes a 「미확인」 span instead of a deletion, and a
    quote the filing never contained loses its **quotation marks** rather than its
    words (「인용문 재구성 금지」 is not superseded — result.md §5).
    """
    model = ScriptedModel(
        calls("get_event", rcept_no=R1_RCEPT),
        says(
            "계양전기는 자금 사정이 어렵습니다. "  # no marker at all
            "증자 규모는 확정되었습니다[[cite:c99]]. "  # an id no tool returned
            "총 조달금액은 1,234,567원입니다[[cite:c2]]. "  # a number from nowhere
            "공시는 「신주인수권증서 매매기간」이라고 적었습니다[[cite:c2]]. "  # not verbatim
            f"공시 원문은 「{QUOTE}」입니다[[cite:c2]]."  # verbatim, and cited
        ),
    )
    events = list(run_turn(ctx, "얼마나 조달하나요?", client=model))

    texts = of(events, TextEvent)
    assert [text.text for text in texts] == [
        "계양전기는 자금 사정이 어렵습니다.",
        "증자 규모는 확정되었습니다.",  # 마커만 사라지고 문장은 남는다 (§4 check 3)
        "총 조달금액은 1,234,567원입니다.",
        "공시는 신주인수권증서 매매기간이라고 적었습니다.",  # 「…」만 벗겨진다
        f"공시 원문은 「{QUOTE}」입니다.",  # verbatim → 그대로
    ]
    # 미확인: the span covers the figure **with its unit**, so the surface marks
    # one value rather than splitting it — and only that sentence carries one.
    marked = texts[2]
    assert [marked.text[start:end] for start, end in marked.unverified] == ["1,234,567원"]
    assert all(not text.unverified for text in texts if text is not marked)

    end = events[-1]
    # blocked = **제거된 마커 수** (R16 §1): only `c99`, which named nothing.
    assert end.blocked == 1 and end.kind == "answer" and end.refusal_category is None
    assert "1,234,567원입니다" in end.answer  # 저장도 읽힌 그대로

    # A stream that dies mid-marker leaves no debris on the reader's screen: half
    # a marker is removed like any other, and the prose in front of it stands.
    cut = ScriptedModel(says("공시를 읽었습니다[[cite:c"))
    events = list(run_turn(ctx, "읽었어요?", client=cut))
    assert [text.text for text in of(events, TextEvent)] == ["공시를 읽었습니다"]
    assert events[-1].blocked == 1


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


def test_a_greeting_is_answered_and_a_budget_ends_a_turn_honestly(ctx) -> None:
    """Degrade rules: nothing to cite is not a refusal, `aborted` when a ceiling trips.

    `P9.S4` retires the 검증 미통과 폴백 producer: the family said 「이 데이터는
    검증을 통과하지 못했습니다」 about a turn whose every sentence the gate had
    dropped, and nothing is dropped any more. Build-prompt §4 check 1 is the bar —
    도구 행 0 · 칩 0 · 푸터 없음 · **거절 아님**.
    """
    hello = ScriptedModel(says("안녕하세요. 무엇을 도와드릴까요?"))
    events = list(run_turn(ctx, "안녕", client=hello))
    assert of(events, RefusalEvent) == [] and of(events, ToolRowEvent) == []
    assert of(events, CitationEvent) == [] and of(events, FooterEvent) == []
    assert [event.text for event in of(events, TextEvent)] == [
        "안녕하세요.",
        "무엇을 도와드릴까요?",
    ]
    end = events[-1]
    assert end.kind == "answer" and end.refusal_category is None and end.blocked == 0

    # A retired family arriving **as words** is prose, not a stored family: nothing
    # newly records 검증 미통과 폴백 (R16 §0 「새로 기록하지 않음」).
    retired = ScriptedModel(
        says("이 데이터는 검증을 통과하지 못했습니다. 검증되지 않은 내용은 해설하지 않습니다.")
    )
    events = list(run_turn(ctx, "괜찮나요?", client=retired))
    assert of(events, RefusalEvent) == []
    assert events[-1].kind == "answer" and events[-1].refusal_category is None

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


def test_the_calculation_block_is_drawn_before_the_number_exists(ctx) -> None:
    """R16 §2.4 / §4 checks 4–6: 입력이 먼저, 제자리 교체, 근거 N건에는 안 센다.

    The calculator is the round's headline element, and its auditability is *half*
    inputs: the block reaches the reader while the calculation is still `pending`,
    carrying each input with its own 근거 — or with the 「입력」 marker when the value
    is the reader's. The result then replaces it **on the same block_id**.
    """
    model = ScriptedModel(
        calls("get_event", rcept_no=R1_RCEPT),
        computes(
            op="excess_subscription_cap",
            inputs=[
                {"key": "allotted", "label": "보유 주식수", "value": "1000",
                 "display": "1,000주"},
                {"key": "excess_ratio", "label": "초과청약 비율", "value": "0.2",
                 "display": "0.2주", "cite": "c2"},
            ],
        ),
        says("초과청약은 200주까지 할 수 있습니다[[cite:c2]]."),
    )
    events = list(run_turn(ctx, "계양전기 1,000주면 초과청약 몇 주?", client=model))

    pending, settled = of(events, CalcBlockEvent)
    assert pending.state == "pending" and pending.result is None and pending.persistent
    # 제자리 교체 — the same block, later, so the surface does not make it jump.
    assert settled.block_id == pending.block_id and settled.inputs == pending.inputs
    assert settled.state == "done" and settled.mode == "verified"
    assert settled.name == "초과청약 한도" and settled.result == "200주"
    assert settled.expr == "1,000주 × 0.2주 = 200주"
    # 입력 2행: 독자가 준 값은 「입력」(칩 없음), 공시에서 온 값은 칩 — 그리고 그 칩은
    # 프로즈가 쓰는 것과 **같은 번호**다 (같은 근거 = 같은 번호).
    assert [(row.value, row.reader_input, row.citation) for row in pending.inputs] == [
        ("1,000주", True, None),
        ("0.2주", False, 1),
    ]
    # The block is on screen before its own tool row, and the turn said 계산하고 있습니다.
    calc_row = [row for row in of(events, ToolRowEvent) if row.tool == "calculate"][0]
    assert events.index(pending) < events.index(calc_row)
    assert "calc" in [event.phase for event in of(events, StatusEvent)]

    text = of(events, TextEvent)[0]
    # `P9.S4`'s deliberate gap closes here: a figure the calculator returned is
    # traceable, so restating it in prose is no longer marked 미확인.
    assert text.text == "초과청약은 200주까지 할 수 있습니다." and text.unverified == ()
    # 계산 결과는 「근거 N건」에 세지 않는다 — 근거는 칩의 수다 (§2.4).
    assert of(events, FooterEvent)[0].count == 1 and events[-1].evidence == (R1_RCEPT,)


def test_a_calculation_fails_as_guidance_and_costs_no_tool_budget(ctx) -> None:
    """§4 check 6 and the zero-I/O precedent — the two halves nothing else covers."""
    stuck = ScriptedModel(
        computes(
            op="expr",
            name="청약 필요 금액",
            expr="shares * price",
            inputs=[
                {"key": "shares", "label": "청약 주식수", "value": "200", "display": "200주"},
                {"key": "price", "label": "확정 발행가액", "value": "미공시",
                 "display": "미공시"},
            ],
        ),
        says("확정 전 금액은 해설하지 않습니다."),
    )
    events = list(run_turn(ctx, "200주 청약하면 얼마 필요해요?", client=stuck))
    blocks = of(events, CalcBlockEvent)
    assert [block.state for block in blocks] == ["pending", "error"]
    # 무엇이 막았는지는 그 입력의 이름과 값이 말한다 (서명된 문장은 표면이 쓴다), and
    # a failed calculation draws no 식 줄 at all.
    assert blocks[1].why == "확정 발행가액 미공시" and blocks[1].expr is None
    assert of(events, ToolRowEvent)[0].row == "계산 → 확정 발행가액 미공시 · 0건"
    assert of(events, RefusalEvent)[0].family == "확정 전"

    # Budget-exempt: four calculations under a ceiling of one, and the turn still
    # ends `done` — while the terminal still reports every tool that ran.
    counting = ScriptedModel(
        *[
            computes(op="expr", name="합", expr="a + a",
                     inputs=[{"key": "a", "label": "수", "value": "1", "display": "1"}])
            for _ in range(4)
        ],
        says("2입니다."),
    )
    events = list(
        run_turn(ctx, "1 더하기 1?", client=counting, budget=TurnBudget(max_tool_calls=1))
    )
    assert events[-1].status == "done" and events[-1].tool_calls == 4


def test_a_saved_의견_is_confirmed_and_never_refused(ctx) -> None:
    """R6 §의견 signs 「자동 저장 + 확인 한 줄」 — and no refusal (`P6.S7`).

    The confirmation is what the 대화 로그 replays when the model says nothing at
    all; when it does say something, strip-don't-drop ships that instead. Either
    way the turn is an answer — the 폴백 family that once contradicted the save is
    gone with the gate that produced it (`P9.S4`).
    """
    saved = ScriptedModel(calls("save_feedback", text="인용이 좋네요"), says("저장했습니다."))
    events = list(run_turn(ctx, "의견 남길게요", client=saved))
    assert of(events, ToolRowEvent)[0].ok is True
    assert of(events, RefusalEvent) == []
    assert events[-1].kind == "answer" and events[-1].answer == "저장했습니다."

    silent = ScriptedModel(calls("save_feedback", text="인용이 좋네요"), [TextChunk("")])
    events = list(run_turn(ctx, "의견 남길게요", client=silent))
    assert of(events, RefusalEvent) == []
    assert events[-1].answer == "의견을 저장했습니다 — 운영자가 확인합니다."
