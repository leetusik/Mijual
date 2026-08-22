"""The agent — one autonomous function-calling turn, as a control-flow property.

Read :func:`run_turn` and ask the question the operator's binding addition asks
("we need to build a agent not just llm chain"): *who decides what happens next?*
The answer has to be legible in the code, not argued for in a docstring, so the
loop is written to make it checkable:

    generate → (function_call? → execute → feed the result back) → repeat → answer

There is **no tool name in the control flow**. Nothing is fetched before the model
speaks, nothing is fetched after it, no tool is called because the question
matched a pattern, and no ordering is imposed on the calls it asks for. The model
receives five declarations and a system instruction that *advises*; every call in
a turn, including the decision to make none, is its own. A turn ends when the
model emits a round with no function calls — that is, when it decides it is ready
to answer.

What the loop owns instead is everything that must not be left to a model:

* **the fact rows** — 도구 호출은 숨기지 않고 사실 행으로 표시 (R6), emitted as the
  tool runs, from the tool's own signed string;
* **the citation gate** — the model's prose does not reach the reader, it reaches
  :class:`~mijual.agent.citations.CitationGate`, and only verified sentences leave
  (see that module: this is R6's 「생성 단계에서 차단」);
* **the refusal families** — the five signed sentences are recognised, not
  generated, and the loop states the 검증 미통과 폴백 itself when a turn produced
  nothing verifiable;
* **the 갈 곳 links and the 답변 푸터** — composed from the turn's own tool results
  as *data*, so the model never writes a URL or points at a filing it did not read;
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

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
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
    FooterEvent,
    LinksEvent,
    RefusalEvent,
    ToolRowEvent,
    TurnEnd,
)
from mijual.agent.instructions import system_instruction
from mijual.agent.tools import TOOL_NAMES, ToolResult, UnknownTool, call_tool
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
    status: str = "done"
    reason: str | None = None


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

        if turn.tool_calls + len(calls) > limits.max_tool_calls:
            turn.status, turn.reason = "aborted", "tool_budget"
            break

        messages.append(ModelMessage(text=said, calls=tuple(calls)))
        for call in calls:
            turn.tool_calls += 1
            yield from _execute(ctx, call, turn, messages)
    else:
        turn.status, turn.reason = "aborted", "round_budget"

    yield from _finish(ctx, turn, now=now)


def _execute(
    ctx: ToolContext, call: ModelCall, turn: _Turn, messages: list[Message]
) -> Iterator[AgentEvent]:
    """Run one call the model asked for, and hand the result back to the model."""
    try:
        result = call_tool(call.name, ctx, call.args)
    except UnknownTool:
        # Told, not absorbed: there is no sixth tool and no fallback that would
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


def _finish(ctx: ToolContext, turn: _Turn, *, now: datetime | None) -> Iterator[AgentEvent]:
    """Close the turn: the fallback family if needed, the links, the footer, the end."""
    gate = turn.gate

    if turn.status == "done" and not gate.released:
        # Everything the model produced was dropped at the gate (or it produced
        # nothing at all). 「이 데이터는 검증을 통과하지 못했습니다」 is the family the
        # record signs for exactly that, and it is the one family the *loop* may
        # select on its own, because it is a statement about the data rather than
        # about the reader's question.
        family = ko.REFUSAL_FALLBACK
        sentence = ko.REFUSAL_SENTENCES[family]
        gate.family = family
        gate.released.append(sentence)
        yield RefusalEvent(family=family, text=sentence)

    links = _links(turn.results)
    if turn.status == "done":
        if gate.family is not None:
            # ③ 갈 곳 링크 — the third move of R6's refusal, as data.
            yield LinksEvent(links=links)
        # 완료 → 푸터. A 중단/오류 turn gets none: R6 gives that state its own
        # signed inset row and 재시도, and a footer under a half-answer would read
        # as a finished one.
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
        blocked=len(gate.blocked),
        rounds=turn.rounds,
        tool_calls=turn.tool_calls,
        reason=turn.reason,
        usage=turn.ledger.payload(),
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
