"""The typed event stream one turn produces — the vocabulary `P6.S4` serializes.

A turn is an **iterator of these**, not a string. That is what lets the transport
be a thin adapter (`P6.S4`: one SSE frame per event) and the surface a renderer
(`P6.S5`: one component per event kind), while the decisions that matter — which
tool ran, what the citation gate stripped from a sentence, which refusal family was
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

*A block is identified, and a second event with its id replaces it.* R16 §1:
every structured event carries a turn-stable ``block_id`` and a ``persistent``
flag, and 「같은 ``block_id``의 후속 이벤트는 추가가 아니라 제자리 교체」 — which is
what lets a 계산 블록 go ``pending`` → ``done`` without jumping, and the 진행 표시
line be *replaced* rather than accumulated. An event with **no** ``block_id`` is
today's append, so the addition is backward compatible (§1 「추가만 한다」).
``persistent`` says whether the block belongs to the message history: a data or
calculation block does (the 대화 로그 stores it verbatim — replaying prose alone
would lose the audit path), a :class:`StatusEvent` does not.

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
    "CalcBlockEvent",
    "CitationEvent",
    "DataBlockEvent",
    "DataRow",
    "FooterEvent",
    "LinksEvent",
    "RefusalEvent",
    "StatusEvent",
    "TextEvent",
    "ToolRowEvent",
    "TurnEnd",
    "CALC_MODES",
    "CALC_STATES",
    "STATUS_PHASES",
    "TERMINAL_STATUSES",
]

#: How a turn can end. ``done`` = the model finished; ``aborted`` = a structural
#: budget or the reader's 중지 stopped it; ``error`` = the model call failed.
#: All three are terminals and all three carry the same summary, because the
#: partial answer above them is real and must be storable (R6 §SSE).
TERMINAL_STATUSES = ("done", "aborted", "error")

#: The five phases a :class:`StatusEvent` may report, R16 D5. The **sentence** for
#: each is signed copy and lives in :data:`mijual.agent.copy.STATUS_KO`; this is
#: the vocabulary the surface switches on.
STATUS_PHASES = ("read", "search", "open", "calc", "write")

#: What a :class:`CalcBlockEvent` computed, R16 §2.4 / D6. ``verified`` is a named
#: :mod:`mijual.calc` operation — the product's own money math — and ``expr`` is the
#: escape hatch's arithmetic. The surface heads them with **different words**
#: (검증된 계산 / 식 계산) because rendering them identically launders arithmetic
#: into product truth (result.md §3-7).
CALC_MODES = ("verified", "expr")

#: A calculation's lifecycle on one ``block_id``: it appears at call time with its
#: inputs already drawn and is **replaced in place** by its outcome (R16 §2.4).
CALC_STATES = ("pending", "done", "error")


@dataclass(frozen=True)
class AgentEvent:
    """One thing the reader's surface is told. Serializable by construction.

    ``block_id`` and ``persistent`` are the two fields R16 §1 puts on *every*
    structured event, and both are keyword-only so no subclass's own field order
    changes. ``block_id is None`` means "append me", which is what every event
    before R16 did and still does — the id is the opt-in to **replacement**, and
    it rides on the wire only when it exists.
    """

    #: The event name the transport puts in the SSE ``event:`` line.
    EVENT: ClassVar[str] = "event"

    #: Turn-stable id of the block this event *is*. A second event with the same
    #: id replaces it in place; ``None`` appends.
    block_id: str | None = field(default=None, kw_only=True)
    #: Does this block belong to the stored turn? ``False`` = transient: sent to
    #: the reader, never written to the 대화 로그 (R16: 진행 표시 한 줄뿐).
    persistent: bool = field(default=True, kw_only=True)

    def payload(self) -> dict[str, Any]:
        raise NotImplementedError

    def _block_fields(self, out: dict[str, Any]) -> dict[str, Any]:
        """Add the block identity — **only when there is one** (additive on the wire)."""
        if self.block_id is not None:
            out["block_id"] = self.block_id
            out["persistent"] = self.persistent
        return out

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
        return self._block_fields({"tool": self.tool, "row": self.row, "ok": self.ok})


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
        return self._block_fields(out)


@dataclass(frozen=True)
class TextEvent(AgentEvent):
    """One **stripped** sentence of the answer, with the chip numbers it rests on.

    Every sentence the model completes reaches this event (R16 §2.5: strip,
    don't drop) — what does not reach it is anything unverifiable *inside* the
    sentence. The generation-boundary gate (:mod:`mijual.agent.citations`) removed
    every ``[[cite:…]]`` marker, kept the chips whose ids the tools actually
    returned, and took the quotation marks off a 「…」 span that occurs verbatim in
    nothing a tool returned. The sentence itself is never withheld: a greeting has
    nothing to cite and must still be answered.

    ``citations`` are display numbers whose :class:`CitationEvent` definitions
    were emitted immediately before this event.

    ``unverified`` is R16 §2.5 / Q-B: character offsets, **within this sentence's
    ``text``**, of a filing-specific figure no tool returned — an amount, a share
    count, a rate, a date, a 접수번호, with its unit inside the span so the surface
    marks one value rather than splitting it. The surface draws the 「미확인」 marker
    on exactly those spans; the sentence and the turn both stand (Q-B is claim
    level — no turn is replaced by a fixed one). It rides the wire only when it is
    non-empty, so a turn with nothing to hedge is byte-identical to a pre-R16 one.
    """

    EVENT: ClassVar[str] = "text"

    text: str
    citations: tuple[int, ...] = ()
    unverified: tuple[tuple[int, int], ...] = ()

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"text": self.text, "citations": list(self.citations)}
        if self.unverified:
            out["unverified"] = [list(span) for span in self.unverified]
        return self._block_fields(out)


@dataclass(frozen=True)
class RefusalEvent(AgentEvent):
    """② of R6's 3-part refusal: the signed family sentence, verbatim.

    ``family`` is one of the **six** stored Korean categories
    (:data:`mijual.web.conversationstore.REFUSAL_FAMILIES`) — the most specific
    thing the surface may say, because a reader payload carries no gate reason
    code and R6 forbids per-reason-code wording. R16 re-signed that vocabulary:
    four families are live (철회 · 확정 전 · 공시에 없음 · 보안) and two — 계산 요청
    and 검증 미통과 폴백 — stay in the whitelist **read-only, for past rows**, so a
    turn may still be *found* by them and none may be newly written.

    The surface renders it as **ordinary prose** in body ink: 오류 상태가 아님,
    alert 색·아이콘 금지.
    """

    EVENT: ClassVar[str] = "refusal"

    family: str
    text: str

    def payload(self) -> dict[str, Any]:
        return self._block_fields({"family": self.family, "text": self.text})


@dataclass(frozen=True)
class StatusEvent(AgentEvent):
    """진행 표시 — the one **transient** block: what the turn is doing right now.

    R16 D5 signs five phases and five sentences, and the sentence travels with the
    phase for the same reason a 도구 행 does: the agent's Korean is composed
    server-side (:data:`mijual.agent.copy.STATUS_KO`) and rendered **verbatim**, so
    the signed strings live in one file rather than two.

    Three properties, all of them structural rather than stylistic:

    * **exactly one is alive.** Every status of a turn carries the same
      ``block_id``, so each new phase *replaces* the line instead of adding one.
    * **it is never stored.** ``persistent=False``: the 대화 로그 replays the turn,
      and a 찾는 중 line replayed a week later is noise, not evidence.
    * **it dies at the first sentence.** The surface drops it when prose arrives;
      the loop stops emitting once anything has been released, so the two agree.

    R16 §2.1 is explicit that the surface draws it with **no animation** — the
    spinner/typing-dot ban is not superseded.
    """

    EVENT: ClassVar[str] = "status"

    phase: str
    text: str
    block_id: str | None = field(default="status", kw_only=True)
    persistent: bool = field(default=False, kw_only=True)

    def __post_init__(self) -> None:
        if self.phase not in STATUS_PHASES:
            raise ValueError(f"phase must be one of {STATUS_PHASES}, not {self.phase!r}")

    def payload(self) -> dict[str, Any]:
        return self._block_fields({"phase": self.phase, "text": self.text})


@dataclass(frozen=True)
class DataRow:
    """One 라벨/값 pair — the row schema R16 §2.3 fixes, shared with the 계산 블록.

    ``value`` is a **string the server states**, never a shape the surface has to
    know how to render: the block is 「공시에서 읽은 값」, and a value the server
    cannot state without inventing a format is not a row (see
    :func:`mijual.agent.tools.value_rows`).

    ``citation`` is the reader's chip **number** (the same number the same 근거
    carries in prose — R6-4), or ``None``. ``reader_input`` marks a value the
    reader supplied, which the surface labels 「입력」 and gives no chip.
    """

    label: str
    value: str
    citation: int | None = None
    reader_input: bool = False

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"label": self.label, "value": self.value}
        if self.citation is not None:
            out["citation"] = self.citation
        if self.reader_input:
            out["reader_input"] = True
        return out


@dataclass(frozen=True)
class DataBlockEvent(AgentEvent):
    """공시에서 읽은 값 — label/value rows, each with its own 근거 (R16 §2.3).

    Persistent: the 대화 로그 stores the block **verbatim**, because the rows carry
    what prose does not (which value, from which filing, under which label). The
    heading is the surface's ``DATA_HEADING`` unless the server sends a ``title``;
    ``None`` is the ordinary case and means "use the signed default".
    """

    EVENT: ClassVar[str] = "data"

    rows: tuple[DataRow, ...] = ()
    title: str | None = None

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"rows": [row.payload() for row in self.rows]}
        if self.title is not None:
            out["title"] = self.title
        return self._block_fields(out)


@dataclass(frozen=True)
class CalcBlockEvent(AgentEvent):
    """계산 블록 — 입력 · 식 · 결과, R16's headline element (§2.4, D6).

    **Auditability is half inputs, half result**, so the block is emitted at the
    moment the tool is called, carrying the inputs the model handed it and
    ``state="pending"``; the same ``block_id`` arrives again with ``done`` or
    ``error`` and *replaces* it, which is what keeps the block from jumping
    (§4 check 5). Nothing is retracted: a replacement is the same block, later.

    ``mode`` is the one thing that must never be rendered identically
    (:data:`CALC_MODES`): a ``verified`` result is what :mod:`mijual.calc` — the
    product's own money math — computed, and an ``expr`` result is what a whitelisted
    arithmetic expression evaluated. Both are auditable; only the first is *product
    truth*, and the heading's single word is what keeps them apart.

    ``inputs`` reuse :class:`DataRow` exactly (§2.4: 같은 행 스키마): a value the
    reader supplied carries ``reader_input`` (the 「입력」 marker, no chip) and a
    value read from a filing carries its citation **number**, from the same
    numbering the prose uses (:meth:`~mijual.agent.citations.CitationGate.cite`).

    ``result`` is the reader's spelling of the computed value, unit included, and
    the surface marks it 「계산」. It is **not** counted in 근거 N건 (§2.4): a
    calculation is not a filing, and the 근거 count is the chips'.

    ``why`` is the guidance an ``error`` carries — data, never a traceback; the
    signed 「계산할 수 없습니다 — {이유}」 sentence is composed by the surface.
    """

    EVENT: ClassVar[str] = "calc"

    mode: str = "verified"
    name: str = ""
    inputs: tuple[DataRow, ...] = ()
    expr: str | None = None
    result: str | None = None
    state: str = "pending"
    why: str | None = None

    def __post_init__(self) -> None:
        if self.mode not in CALC_MODES:
            raise ValueError(f"mode must be one of {CALC_MODES}, not {self.mode!r}")
        if self.state not in CALC_STATES:
            raise ValueError(f"state must be one of {CALC_STATES}, not {self.state!r}")

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "mode": self.mode,
            "name": self.name,
            "inputs": [row.payload() for row in self.inputs],
            "state": self.state,
        }
        for key, value in (("expr", self.expr), ("result", self.result), ("why", self.why)):
            if value is not None:
                out[key] = value
        return self._block_fields(out)


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
        return self._block_fields({"links": [dict(link) for link in self.links]})


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
        return self._block_fields(
            {
                "count": self.count,
                "evidence": list(self.evidence),
                "generated_at": self.generated_at,
                "links": [dict(link) for link in self.links],
            }
        )


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

    ``blocked`` counts **markers the gate removed**, not sentences it dropped
    (R16 §1: 「삭제된 문장 수가 아니라 제거된 마커 수」). Under strip-don't-drop the
    prose survives and only an unresolvable marker is taken out, so the number is
    a signal about the model's citing rather than about what the reader lost. It
    still rides the terminal so an operator sees the rate rather than infers it.
    (`P9.S3` re-documents it; `P9.S4` is what makes the counter count markers.)

    ``filings`` is 「공시 M건 읽음」's M — how many **distinct 접수번호** this turn
    actually read. The server knows it because a tool returned each filing's
    contract, and the surface must never parse it back out of the 도구 행 strings
    (R16 §1).
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
    filings: int = 0
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
            "filings": self.filings,
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
