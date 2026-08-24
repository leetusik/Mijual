"""The agent — one autonomous function-calling turn, as a control-flow property.

Read :func:`run_turn` and ask the question the operator's binding addition asks
("we need to build a agent not just llm chain"): *who decides what happens next?*
The answer has to be legible in the code, not argued for in a docstring, so the
loop is written to make it checkable:

    generate → (function_call? → execute → feed the result back) → repeat → answer

There is **no tool name in the control flow**. Nothing is fetched before the model
speaks, nothing is fetched after it, no tool is called because the question
matched a pattern, and no ordering is imposed on the calls it asks for. The model
receives six declarations and a system instruction that *advises*; every call in
a turn, including the decision to make none, is its own. A turn ends when the
model emits a round with no function calls — that is, when it decides it is ready
to answer.

What the loop owns instead is everything that must not be left to a model:

* **the fact rows** — 도구 호출은 숨기지 않고 사실 행으로 표시 (R6), emitted as the
  tool runs, from the tool's own signed string;
* **the citation gate** — the model's prose does not reach the reader, it reaches
  :class:`~mijual.agent.citations.CitationGate`, which strips what cannot be
  verified and releases the prose (R16 §2.5: strip, don't drop). The gate no
  longer judges, so the loop has no unverified-turn state to state;
* **the refusal families** — the live signed sentences are recognised, never
  generated. The loop selects **no** family of its own since `P9.S4`: 검증 미통과
  폴백 was the one it could, and R16 retired it with the sentence-dropping gate
  that made it true;
* **the 갈 곳 links and the 답변 푸터** — composed from the turn's own tool results
  as *data*, so the model never writes a URL or points at a filing it did not read;
* **the 진행 표시 line** — R16 D5's five signed phrases, one alive at a time,
  replaced as the turn moves from 질문을 읽고 → 공시를 찾고 → 원문을 읽고 → 답변을
  정리하고, and silent from the first released sentence onward. Transient: it is
  the one block the 대화 로그 never keeps;
* **the 데이터 블록** — 공시에서 읽은 값, composed from a tool result's own
  label/value reading (:func:`mijual.agent.tools.value_rows`) with each row's
  근거 chip taken from the same numbering the prose uses. The loop does not know
  *which* tool that is: any result that reads as labelled values gets a block;
* **the 계산 블록** — drawn **before** the call runs, from the arguments themselves
  (:func:`mijual.agent.tools.calc_plan`), and replaced in place on the same
  ``block_id`` when the result arrives. Auditability is half inputs and half
  result, so the inputs are on the reader's screen while the calculation is still
  ``pending``. Again no tool name reaches the control flow: the loop asks whether
  *this call* reads as a calculation, exactly as it asks whether *this result*
  reads as labelled values;
* **the budget** — rounds, tool calls and live model calls are all capped, and
  every cap maps to an honest ``aborted`` terminal. A turn is never silently
  truncated;
* **the ledger** — calls · tokens · thinking level · ▷ estimated cost, on the
  terminal event (D-4). Agent spend joins no signed ops panel (`P6` Finding 14).

The turn is a **generator**, which is what makes the transport thin: `P6.S4`
iterates it and writes one SSE frame per event, and the reader's 중지 is the
consumer closing the generator. No HTTP, no SSE and no persistence exists here.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

from mijual.agent import copy as ko
from mijual.agent.citations import CitationGate
from mijual.agent.client import (
    AgentGeminiClient,
    CallBudgetExceeded,
    CallChunk,
    GeminiError,
    Message,
    ModelCall,
    ModelClient,
    ModelMessage,
    TextChunk,
    ToolMessage,
    UsageChunk,
    UsageLedger,
    UserMessage,
)
from mijual.agent.context import ToolContext
from mijual.agent.events import (
    AgentEvent,
    CalcBlockEvent,
    DataBlockEvent,
    DataRow,
    FooterEvent,
    LinksEvent,
    StatusEvent,
    ToolRowEvent,
    TurnEnd,
)
from mijual.agent.instructions import system_instruction
from mijual.agent.tools import (
    BUDGET_EXEMPT,
    STATUS_PHASE,
    TOOL_NAMES,
    CalcPlan,
    ToolResult,
    UnknownTool,
    calc_outcome,
    calc_plan,
    call_tool,
    value_rows,
)
from mijual.web import clock
from mijual.web.conversationstore import KIND_ANSWER, KIND_REFUSAL

__all__ = ["HistoryTurn", "TurnBudget", "run_turn"]


@dataclass(frozen=True)
class TurnBudget:
    """The structural ceiling on one turn — money and latency, not the reader.

    R6-5 removed the quota: 질문 수 무제한, and no surface may say otherwise. This
    is the other kind of limit — the one that stops *one* conversation from
    looping forever, the way ``DartClient(max_requests=…)`` stops a collector
    (N25). Every cap here ends the turn with an honest ``aborted`` terminal
    carrying its reason; none of them is ever rendered as copy.
    """

    #: Model rounds. Enough for search → read → read again → answer.
    max_rounds: int = 6
    #: Tool executions across the whole turn.
    max_tool_calls: int = 10
    #: Live model calls, enforced *inside* the client so the ceiling refuses the
    #: call rather than being asked to stop after it.
    max_model_calls: int = 8


@dataclass(frozen=True)
class HistoryTurn:
    """One earlier exchange in this thread, as the reader saw it.

    Plain text in, plain text out: the citation numbering is **per answer**
    (R6-4), so an earlier turn's chips are not carried forward — the model gets
    the prose it wrote and cites the current turn's results afresh.
    """

    question: str
    answer: str


@dataclass
class _Turn:
    """The turn's own bookkeeping — everything the terminal event reports."""

    gate: CitationGate = field(default_factory=CitationGate)
    ledger: UsageLedger = field(default_factory=UsageLedger)
    results: list[ToolResult] = field(default_factory=list)
    rounds: int = 0
    tool_calls: int = 0
    #: Tool calls that **cost budget** — every call except a zero-I/O one
    #: (:data:`mijual.agent.tools.BUDGET_EXEMPT`). Separate from ``tool_calls`` on
    #: purpose: the terminal reports how many tools ran, the ceiling counts what
    #: running them costs, and conflating the two would make the ▷ ledger lie.
    billed: int = 0
    status: str = "done"
    reason: str | None = None
    #: The 진행 표시 phase currently on the reader's screen, if any.
    phase: str | None = None
    #: How many 구조화 블록 this turn has emitted — the source of their ids.
    blocks: int = 0


def run_turn(
    ctx: ToolContext,
    question: str,
    history: Sequence[HistoryTurn] = (),
    *,
    client: ModelClient | None = None,
    budget: TurnBudget | None = None,
    now: datetime | None = None,
) -> Iterator[AgentEvent]:
    """Run one question. Yields :mod:`~mijual.agent.events` until a terminal.

    Args:
        ctx: the server-side half of every tool call (`P6.S2`). A **write**
            session when the turn may reach ``save_feedback``.
        question: the reader's question, verbatim.
        history: earlier exchanges in this sessionStorage thread, oldest first.
        client: the model. Defaults to a fresh :class:`AgentGeminiClient` for this
            turn, so the budget and the ledger are per turn by construction.
        budget: the structural ceiling (:class:`TurnBudget`).
        now: the 생성시각 for the footer; the KST clock by default.

    The iterator always ends with exactly one :class:`~mijual.agent.events.TurnEnd`
    unless the consumer closes it first (the reader's 중지) — in which case
    nothing is retracted and `P6.S4` stores what was released.
    """
    limits = budget or TurnBudget()
    model = client or AgentGeminiClient(
        settings=ctx.settings, max_calls=limits.max_model_calls
    )
    instruction = system_instruction(ctx)
    messages: list[Message] = []
    for earlier in history:
        messages.append(UserMessage(earlier.question))
        if earlier.answer:
            messages.append(ModelMessage(text=earlier.answer))
    messages.append(UserMessage(question))

    turn = _Turn()

    while turn.rounds < limits.max_rounds:
        turn.rounds += 1
        # 질문을 읽고 있습니다 → (tools) → 답변을 정리하고 있습니다. A round after the
        # first is the model composing with what the tools gave it; if it asks for
        # another tool instead, that call replaces the line before it runs.
        yield from _status(turn, "read" if turn.rounds == 1 else "write")
        said = ""
        calls: list[ModelCall] = []
        try:
            for chunk in model.stream(messages=messages, system_instruction=instruction):
                if isinstance(chunk, TextChunk):
                    said += chunk.text
                    yield from turn.gate.feed(chunk.text)
                elif isinstance(chunk, CallChunk):
                    calls.append(chunk.call)
                elif isinstance(chunk, UsageChunk):
                    turn.ledger.model = chunk.model or turn.ledger.model
                    turn.ledger.add(chunk.usage, thinking_level=chunk.thinking_level)
        except CallBudgetExceeded:
            turn.status, turn.reason = "aborted", "call_budget"
            break
        except GeminiError as exc:
            # Type name only — never a message that could carry a credential.
            turn.status, turn.reason = "error", str(exc) or "model_error"
            break

        yield from turn.gate.flush()

        if not calls:
            break  # the model decided it was ready to answer

        # 계산 is **budget-exempt** (changple5's zero-I/O precedent, `P9.S1` item 3):
        # it spends no request and no token, and a turn that stopped calculating
        # because a *search* ceiling was near would be a limit the reader can feel
        # with nothing behind it. The exemption is a property declared beside the
        # tools, so no tool name enters this control flow.
        billable = sum(1 for call in calls if call.name not in BUDGET_EXEMPT)
        if turn.billed + billable > limits.max_tool_calls:
            turn.status, turn.reason = "aborted", "tool_budget"
            break

        messages.append(ModelMessage(text=said, calls=tuple(calls)))
        for call in calls:
            turn.tool_calls += 1
            if call.name not in BUDGET_EXEMPT:
                turn.billed += 1
            yield from _execute(ctx, call, turn, messages)
    else:
        turn.status, turn.reason = "aborted", "round_budget"

    yield from _finish(ctx, turn, now=now)


def _status(turn: _Turn, phase: str) -> Iterator[AgentEvent]:
    """The one live 진행 표시 line: replace it, never add to it — and stop at prose.

    Same ``block_id`` every time, so the surface swaps the sentence in place
    (R16 §2.1: 항상 1개, phase가 바뀌면 텍스트만 교체). Two silences are deliberate:
    the same phase twice says nothing new, and once anything has been **released**
    the line is gone for good — the reader is reading, and a status under a
    sentence would be a second thing moving on a surface with no animation.
    """
    if phase == turn.phase or turn.gate.released:
        return
    turn.phase = phase
    yield StatusEvent(phase=phase, text=ko.STATUS_KO[phase])


def _data_block(turn: _Turn, result: ToolResult) -> Iterator[AgentEvent]:
    """공시에서 읽은 값 — a tool's labelled values, each row with its own 근거.

    The chips are **defined first**, in the same emission as the block that names
    their numbers (R6: 자리표시 칩 금지), and they come from
    :meth:`~mijual.agent.citations.CitationGate.cite`, so a 근거 shown in a row and
    later cited by a sentence carries one number in both places. A result with no
    stateable rows emits nothing at all: an empty block is not a block, and the
    wire stays additive.
    """
    rows: list[DataRow] = []
    chips: list[AgentEvent] = []
    for row in value_rows(result.payload):
        number: int | None = None
        if row.citation is not None:
            number, chip = turn.gate.cite(row.citation)
            if chip is not None:
                chips.append(chip)
        rows.append(
            DataRow(
                label=row.label,
                value=row.value,
                citation=number,
                reader_input=row.reader_input,
            )
        )
    if not rows:
        return
    turn.blocks += 1
    yield from chips
    yield DataBlockEvent(rows=tuple(rows), block_id=f"data-{turn.blocks}")


def _calc_pending(turn: _Turn, plan: CalcPlan) -> tuple[CalcBlockEvent, list[AgentEvent]]:
    """The 계산 블록 as it appears **at call time** — inputs drawn, result unknown.

    Half of auditability is here (R16 §2.4: 「블록은 도구 호출 시점에 입력만이라도 먼저
    나타난다」): the reader sees what the calculation was handed and where each value
    came from before there is any number to be persuaded by. Each input that names a
    근거 is resolved through :meth:`~mijual.agent.citations.CitationGate.cite_ref`,
    so its chip is the **same number** the prose will use for that filing; one that
    names none is the reader's own value and carries the 「입력」 marker instead.
    """
    rows: list[DataRow] = []
    chips: list[AgentEvent] = []
    for row in plan.inputs:
        number, chip = turn.gate.cite_ref(row.cite)
        if chip is not None:
            chips.append(chip)
        rows.append(
            DataRow(
                label=row.label,
                value=row.display,
                citation=number,
                reader_input=number is None,
            )
        )
    turn.blocks += 1
    block = CalcBlockEvent(
        mode=plan.mode,
        name=plan.name,
        inputs=tuple(rows),
        state="pending",
        block_id=f"calc-{turn.blocks}",
    )
    return block, chips


def _calc_settled(block: CalcBlockEvent, result: ToolResult | None) -> CalcBlockEvent:
    """The same block, later: ``pending`` → ``done`` | ``error``, **same id**.

    A replacement rather than a second block (R16 §1), so the surface swaps the
    result row in place and the block does not jump (§4 check 5). The inputs are
    carried through unchanged — they are what the calculation ran on, whatever it
    returned.

    ``result is None`` is the defensive branch: the tool raised, which it does not
    do (it answers a shape it cannot read with guidance), and a block already on the
    reader's screen must still settle. It settles as the honest thing — this
    calculation did not happen — named by the calculation itself.
    """
    outcome = calc_outcome(result) if result is not None else None
    if outcome is None:
        return replace(block, state="error", why=block.name)
    computed = outcome.get("result")
    return replace(
        block,
        state=str(outcome.get("state") or "error"),
        expr=outcome.get("expr"),
        result=computed.get("display") if isinstance(computed, Mapping) else None,
        why=outcome.get("why"),
    )


def _execute(
    ctx: ToolContext, call: ModelCall, turn: _Turn, messages: list[Message]
) -> Iterator[AgentEvent]:
    """Run one call the model asked for, and hand the result back to the model."""
    # Narration, not control flow: the phase is looked up and the line is replaced
    # *before* the call runs, because the wait is the call. A tool none of R16's
    # five phrases describes changes nothing (:data:`mijual.agent.tools.STATUS_PHASE`).
    phase = STATUS_PHASE.get(call.name)
    if phase is not None:
        yield from _status(turn, phase)

    # Does *this call* read as a calculation? The same question shape as 「does this
    # result read as labelled values」 — argument knowledge lives with the tools
    # (:func:`mijual.agent.tools.calc_plan`), never as a name in this function.
    plan = calc_plan(call.name, call.args)
    block: CalcBlockEvent | None = None
    if plan is not None:
        block, chips = _calc_pending(turn, plan)
        yield from chips
        yield block

    try:
        result = call_tool(call.name, ctx, call.args)
    except UnknownTool:
        # Told, not absorbed: there is no seventh tool and no fallback that would
        # let an invented call quietly succeed. The model gets to correct itself.
        messages.append(
            ToolMessage(
                name=call.name,
                response={"ok": False, "error": f"no such tool; the tools are {TOOL_NAMES}"},
                call_id=call.call_id,
            )
        )
        return
    except Exception as exc:  # noqa: BLE001 — reported structurally, never as prose
        if block is not None:
            yield _calc_settled(block, None)
        messages.append(
            ToolMessage(
                name=call.name,
                response={"ok": False, "error": type(exc).__name__},
                call_id=call.call_id,
            )
        )
        return

    turn.results.append(result)
    yield ToolRowEvent(tool=result.tool, row=result.fact_row, ok=result.ok)

    response: dict[str, Any] = result.response()
    # The citations go back **with their reference ids**: the model can only cite
    # what a tool returned, because an id is the only way to name one.
    response["citations"] = turn.gate.learn(result)
    messages.append(
        ToolMessage(name=result.tool, response=response, call_id=call.call_id)
    )
    if block is not None:
        yield _calc_settled(block, result)
    yield from _data_block(turn, result)


def _finish(ctx: ToolContext, turn: _Turn, *, now: datetime | None) -> Iterator[AgentEvent]:
    """Close the turn: the 의견 confirmation if that is all it was, links, footer, end.

    **No fallback family (`P9.S4`).** 「이 데이터는 검증을 통과하지 못했습니다」 was
    the honest reading of a turn whose every sentence the gate had dropped — and
    under strip-don't-drop no sentence is dropped, so a turn that releases nothing
    released nothing *because the model said nothing*. Stating a refusal about
    data would be inventing a fact about a silent turn, and R16 retires both the
    family and `REFUSAL_FALLBACK` with the gate that produced them (result.md §5).
    A silent turn is now an ordinary empty answer, and the loop selects no family
    at all: every refusal the reader reads is one the model stated in signed words.
    """
    gate = turn.gate

    if turn.status == "done" and not gate.released and _feedback_only(turn.results):
        # 의견 저장 is the one turn whose **answer is not prose**: R6 §의견 signs
        # 「자동 저장 + 확인 한 줄」 and the confirmation belongs to the surface
        # (`mijual.agent.copy`: 「the surface renders it … the agent never writes it
        # as prose」). Nothing citable is expected, so a model that says nothing at
        # all here still has an answer to replay: the confirmation is recorded as
        # the turn's answer so the 대화 로그 shows what the reader read (`P6.S4`).
        # No event is emitted — it is already on the screen, under the tool's row.
        gate.released.append(ko.FEEDBACK_SAVED_KO)

    links = _links(turn.results)
    if turn.status == "done":
        if gate.family is not None:
            # ③ 갈 곳 링크 — the third move of R6's refusal, as data.
            yield LinksEvent(links=links)
        # 완료 → 푸터, **when the turn read something**. A 중단/오류 turn gets none
        # (R6 gives that state its own signed inset row and 재시도, and a footer
        # under a half-answer would read as a finished one) — and neither does a
        # turn that called no tool at all: 「근거 N건 · 생성시각」 is a statement
        # about what the answer rests on, and a greeting rests on nothing. R16 §4
        # check 1 says it plainly: 「안녕」 → 도구 행 0 · 칩 0 · **푸터 없음**. A turn
        # that *did* read and then cited nothing still gets one — 근거 0건 is then
        # a true reading, and the 관제 현황판 pointer of a 0건 search rides in it.
        if turn.results:
            yield FooterEvent(
                evidence=gate.evidence,
                generated_at=clock.iso(now or clock.now()),
                links=links,
            )

    refusal = gate.family
    yield TurnEnd(
        status=turn.status,
        kind=KIND_REFUSAL if refusal else KIND_ANSWER,
        answer=gate.answer,
        refusal_category=refusal,
        scope_rcept_no=ctx.scope_rcept_no,
        evidence=gate.evidence,
        quotes=gate.quotes,
        blocked=gate.blocked,  # 제거된 마커 수 (R16 §1), not dropped sentences
        filings=_filings_read(turn.results),
        rounds=turn.rounds,
        tool_calls=turn.tool_calls,
        reason=turn.reason,
        usage=turn.ledger.payload(),
    )


def _filings_read(results: Sequence[ToolResult]) -> int:
    """공시 M건 읽음 — how many distinct 접수번호 this turn actually **read**.

    A search *lists* filings; only a read returns one's verification contract, and
    the contract is what says ``found``. So a hit the model never opened is not
    counted, and the number the 도구 흐름 summary states is the one the server
    knows by construction — R16 §1 is explicit that the surface must never parse
    it back out of the 도구 행 strings.
    """
    return len(
        {
            rcept_no
            for result in results
            if result.payload.get("found") is True
            for rcept_no in result.evidence
        }
    )


def _feedback_only(results: Sequence[ToolResult]) -> bool:
    """Did this turn do nothing but save an 의견, successfully?

    Narrow on purpose, and now only about **what to replay**: a turn that also
    read a filing and then said nothing has no confirmation to stand in for its
    prose, so it is stored as the empty answer it was.
    """
    return bool(results) and all(
        result.tool == "save_feedback" and result.ok for result in results
    )


def _links(results: Sequence[ToolResult]) -> tuple[dict[str, Any], ...]:
    """갈 곳 — composed from what the turn actually read, as data not prose.

    **No href is built here.** R6 asks for 「DART 원문 rcept_no verbatim · 이벤트
    상세 · 내 종목 조회」, and the routes for the last two are the frontend's own
    (``frontend/lib/routes.ts``, ``lib/api.ts``'s DART viewer URL). Serving a
    filing number and a destination kind keeps one owner for every route and makes
    it impossible for the agent to point at a page that does not exist.
    """
    filings = tuple(
        dict.fromkeys(rcept_no for result in results for rcept_no in result.evidence)
    )[:3]
    links: list[dict[str, Any]] = []
    for rcept_no in filings:
        links.append({"kind": "dart", "rcept_no": rcept_no})
        links.append({"kind": "event", "rcept_no": rcept_no})
    if any("none_found_ko" in result.payload for result in results):
        links.append({"kind": "board"})  # 관제 현황판 — the signed 0건 pointer
    links.append({"kind": "stocks"})  # 내 종목 조회 — R6's third destination
    return tuple(links)
