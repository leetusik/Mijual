"""The typed event stream one turn produces — the vocabulary `P6.S4` serializes.

A turn is an **iterator of these**, not a string. That is what lets the transport
be a thin adapter (`P6.S4`: one SSE frame per event) and the surface a renderer
(`P6.S5`: one component per event kind), while the decisions that matter — which
tool ran, which sentence passed the citation gate, which refusal family was
selected — stay in one module with tests that need no HTTP.

**Four properties this vocabulary is shaped by.**

*The chip arrives with its claim.* R6: 「인용 칩은 해당 주장과 동시에 도착 —
자리표시 칩·후행 부착 금지」. So a :class:`TextEvent` carries the chip **numbers**
its sentence rests on, and every number it names has already been *defined* by a
:class:`CitationEvent` in the same emission — a definition, never a placeholder.
A renderer that has the definition can draw the chip in the same paint as the
sentence, and nothing is ever attached to text that is already on screen.

*A refusal is not an error state.* It travels the same prose path (`text` events
with their chips for ① 상태 사실), and only the family sentence itself gets its own
:class:`RefusalEvent` — because the family is a stored fact (R7's 거절 카테고리),
not because the surface should style it differently (R6: alert 색·아이콘 금지).

*The stream never retracts released text.* 중단 and 오류 are terminal events that
*end* a turn; the partial answer above them stands (R6 §SSE: 부분 답변 유지 —
지우기 금지). There is deliberately no "replace" or "clear" event.

*The terminal carries what persistence needs.* :class:`TurnEnd` holds the released
prose, the ``kind``, the ``refusal_category``, the 근거 rcept_no 목록 and the 인용
칩 원문 — exactly :func:`mijual.web.conversationstore.record_turn`'s arguments —
so `P6.S4` stores a turn without re-reading a single sentence of prose, and the
log can never disagree with what the reader saw.

Every event is a frozen dataclass with :meth:`AgentEvent.payload`; ``frame()``
pairs it with its event name for SSE. Nothing here imports the SDK, the web layer
or a model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

__all__ = [
    "AgentEvent",
    "CitationEvent",
    "FooterEvent",
    "LinksEvent",
    "RefusalEvent",
    "TextEvent",
    "ToolRowEvent",
    "TurnEnd",
    "TERMINAL_STATUSES",
]

#: How a turn can end. ``done`` = the model finished; ``aborted`` = a structural
#: budget or the reader's 중지 stopped it; ``error`` = the model call failed.
#: All three are terminals and all three carry the same summary, because the
#: partial answer above them is real and must be storable (R6 §SSE).
TERMINAL_STATUSES = ("done", "aborted", "error")


@dataclass(frozen=True)
class AgentEvent:
    """One thing the reader's surface is told. Serializable by construction."""

    #: The event name the transport puts in the SSE ``event:`` line.
    EVENT: ClassVar[str] = "event"

    def payload(self) -> dict[str, Any]:
        raise NotImplementedError

    @property
    def event(self) -> str:
        return self.EVENT

    def frame(self) -> dict[str, Any]:
        """``{"event": …, "data": …}`` — the shape `P6.S4` writes to the wire."""
        return {"event": self.event, "data": self.payload()}


@dataclass(frozen=True)
class ToolRowEvent(AgentEvent):
    """도구 행 — 무엇을 읽었는지가 근거의 일부 (R6 §Agent).

    The row string is the tool's own (:mod:`mijual.agent.copy`), already composed
    and rendered **verbatim** by the surface: mono, `--text-xs`, 좌측 2px hairline,
    모바일에서도 생략 금지.
    """

    EVENT: ClassVar[str] = "tool_row"

    tool: str
    row: str
    ok: bool = True

    def payload(self) -> dict[str, Any]:
        return {"tool": self.tool, "row": self.row, "ok": self.ok}


@dataclass(frozen=True)
class CitationEvent(AgentEvent):
    """A numbered 근거 — the chip's data, taken from a tool result and nowhere else.

    ``quote is None`` is the **API-tier** citation (R3/R6-4): 원문 스팬 없음,
    접수번호가 인용 핸들. It is a citation, not a missing one, and the 인용 블록
    says so in the signed words.

    Emitted **once per turn per 근거**, the first time a sentence rests on it —
    same 근거 = same 번호 (R6-4), and the number is stable for the whole answer.
    """

    EVENT: ClassVar[str] = "citation"

    number: int
    rcept_no: str
    quote: str | None = None
    span: tuple[int, int] | None = None
    field_key: str | None = None

    @property
    def api_tier(self) -> bool:
        return self.quote is None

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "number": self.number,
            "rcept_no": self.rcept_no,
            "api_tier": self.api_tier,
        }
        if self.quote is not None:
            out["quote"] = self.quote
        if self.span is not None:
            out["span"] = list(self.span)
        if self.field_key is not None:
            out["field_key"] = self.field_key
        return out


@dataclass(frozen=True)
class TextEvent(AgentEvent):
    """One **verified** sentence of the answer, with the chip numbers it rests on.

    Nothing reaches this event that has not passed the generation-boundary gate
    (:mod:`mijual.agent.citations`): the markers resolved to real citations, the
    numbers traced to tool values, and any quoted span was verbatim. A sentence
    that failed is not emitted at all — there is no "blocked" event, because a
    blocked claim must not exist on the stream in any form.

    ``citations`` are display numbers whose :class:`CitationEvent` definitions
    were emitted immediately before this event.
    """

    EVENT: ClassVar[str] = "text"

    text: str
    citations: tuple[int, ...] = ()

    def payload(self) -> dict[str, Any]:
        return {"text": self.text, "citations": list(self.citations)}


@dataclass(frozen=True)
class RefusalEvent(AgentEvent):
    """② of R6's 3-part refusal: the signed family sentence, verbatim.

    ``family`` is one of the five signed Korean categories
    (:data:`mijual.web.conversationstore.REFUSAL_FAMILIES`) — the most specific
    thing the surface may say, because a reader payload carries no gate reason
    code and R6 forbids per-reason-code wording.

    The surface renders it as **ordinary prose** in body ink: 오류 상태가 아님,
    alert 색·아이콘 금지.
    """

    EVENT: ClassVar[str] = "refusal"

    family: str
    text: str

    def payload(self) -> dict[str, Any]:
        return {"family": self.family, "text": self.text}


@dataclass(frozen=True)
class LinksEvent(AgentEvent):
    """③ of R6's 3-part refusal: 갈 곳 — as **link data**, never as prose.

    Composed by the loop from the turn's own tool results (DART 원문 rcept_no
    verbatim · 이벤트 상세 · 내 종목 조회), so the model never writes a URL and
    cannot point at a filing it did not read. `P6.S5` decides the words.
    """

    EVENT: ClassVar[str] = "links"

    links: tuple[dict[str, Any], ...] = ()

    def payload(self) -> dict[str, Any]:
        return {"links": [dict(link) for link in self.links]}


@dataclass(frozen=True)
class FooterEvent(AgentEvent):
    """답변 푸터 — `근거 N건 · {rcept_no} · {생성시각 KST}` as composed **data**.

    R6 §인라인 인용 fixes the elements; the sentence is `P6.S5`'s. ``generated_at``
    is an absolute KST timestamp from :func:`mijual.web.clock.now` — the browser
    only ever diffs one, it never derives one.
    """

    EVENT: ClassVar[str] = "footer"

    evidence: tuple[str, ...] = ()
    generated_at: str = ""
    links: tuple[dict[str, Any], ...] = ()

    @property
    def count(self) -> int:
        """근거 N건 — how many distinct 근거 the answer rests on."""
        return len(self.evidence)

    def payload(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "evidence": list(self.evidence),
            "generated_at": self.generated_at,
            "links": [dict(link) for link in self.links],
        }


@dataclass(frozen=True)
class TurnEnd(AgentEvent):
    """The terminal event — one shape, three statuses, everything persistence needs.

    ``status`` is ``done`` / ``aborted`` / ``error``. The first is a completed
    generation; the other two end a turn whose **partial answer stands** (R6 §SSE:
    부분 답변 유지, `--ink-2`로 감쇠 + the signed inset row + 재시도 — all of that is
    the surface's, and none of it is a new string here).

    ``kind`` / ``refusal_category`` / ``answer`` / ``evidence`` / ``quotes`` map
    one-to-one onto :func:`mijual.web.conversationstore.record_turn`, so `P6.S4`
    persists a turn from this object alone. ``evidence`` and ``quotes`` are the
    **chips the reader saw** — R7's column is 「인용 칩 원문」 — not the union of
    everything the tools returned, so the log replays the answer rather than the
    research.

    ``blocked`` counts sentences the citation gate refused to release. It is not
    an error; it is the gate working, and it is on the terminal so an operator can
    see the rate rather than infer it from prose.
    """

    EVENT: ClassVar[str] = "done"

    status: str = "done"
    kind: str = "answer"
    answer: str = ""
    refusal_category: str | None = None
    scope_rcept_no: str | None = None
    evidence: tuple[str, ...] = ()
    quotes: tuple[str, ...] = ()
    blocked: int = 0
    rounds: int = 0
    tool_calls: int = 0
    #: Why an ``aborted`` / ``error`` turn stopped — structural, never key material.
    reason: str | None = None
    #: The turn's ▷ ledger (calls · tokens · thinking level · estimated cost).
    usage: dict[str, Any] = field(default_factory=dict)

    @property
    def event(self) -> str:
        return self.status

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "status": self.status,
            "kind": self.kind,
            "answer": self.answer,
            "evidence": list(self.evidence),
            "quotes": list(self.quotes),
            "blocked": self.blocked,
            "rounds": self.rounds,
            "tool_calls": self.tool_calls,
            "usage": dict(self.usage),
        }
        if self.refusal_category is not None:
            out["refusal_category"] = self.refusal_category
        if self.scope_rcept_no is not None:
            out["scope"] = self.scope_rcept_no
        if self.reason is not None:
            out["reason"] = self.reason
        return out
