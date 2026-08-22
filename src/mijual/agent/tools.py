"""The five tools the agent calls — verified-contract values, and nothing else.

R6 §Agent names them and fixes what they are for: ``search_events(query)`` →
이벤트 목록/단건, ``get_event(rcept_no)`` → 검증 계약, ``get_portfolio()`` →
포트폴리오 + 상류 계산, ``save_feedback(text, email?)`` → 운영자 대기열,
``get_contact()`` → 운영자 연락처. Everything here is deterministic and
model-free: no LLM call, no HTTP, no SSE. `P6.S3` owns the loop that decides
*which* of these to call and `P6.S5` renders their fact rows.

**No tool computes a number, and that is enforced by construction.** Every value
a tool returns is the object :mod:`mijual.present` already derived and
:mod:`mijual.web.reads` already assembled — the same payload the corresponding
reader surface serves, passed through untouched. D-day, 환산, 금액 and 소멸률 are
therefore *readings*, 「추정」 tags survive because they are carried in the payload
rather than re-applied here, and a won amount before 확정발행가 is absent for the
one reason that matters: it is unconstructable upstream (R6 §Hard rules,
`api` §The presentation contract).

**Figures travel display-ready.** Beside each figure's exact ``value`` sits the
same number in the product's own thousands grouping (``3200`` → ``3,200``), so the
agent's prose reads like every other surface (:mod:`mijual.agent.figures`).
Formatting, not arithmetic: the contract's value is untouched and an identifier is
never a figure.

**Citations travel with the values.** :func:`citations_in` walks a tool's payload
and collects every ``rcept_no`` in it with the verbatim ``quote`` and ``span``
sitting beside it, so `P6.S3` can enforce 「인용 없는 주장은 생성 단계에서 차단」
against a machine-readable list rather than against prose. A fact with no quote
keeps its ``rcept_no`` as the citation handle — R3's API-tier rule, which R6
restates for the 인용 블록.

**Each result carries its signed fact row.** 도구 호출은 숨기지 않고 사실 행으로
표시 (R6: 「무엇을 읽었는지가 근거의 일부」), and the string is composed here — once
— so the surface renders it verbatim (:mod:`mijual.agent.copy`).

**The package imports no spending module.** ``mijual.dart`` / ``mijual.collect`` /
``mijual.extract`` are unreachable from here by rule (`P6` Finding 1) and by test:
the agent reads persisted rows, it never collects or extracts.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from mijual.agent import copy as ko
from mijual.agent import figures
from mijual.agent.context import ToolContext
from mijual.present import EventView
from mijual.web import portfolio as portfolio_service
from mijual.web.conversationstore import record_feedback
from mijual.web.reads import (
    event_payload,
    find_corps,
    load_corp_events,
    load_detail,
    load_portfolio,
    resolve_event,
)

__all__ = [
    "MAX_SEARCH_RESULTS",
    "TOOL_NAMES",
    "Citation",
    "ToolResult",
    "UnknownTool",
    "call_tool",
    "citations_in",
    "fact_rows",
    "get_contact",
    "get_event",
    "get_portfolio",
    "save_feedback",
    "search_events",
]

#: How many events one search may list. The row states the true count either way
#: (:func:`mijual.agent.copy.search_row`), so a capped list is visible rather than
#: silent — and a model handed forty events picks worse than one handed eight.
MAX_SEARCH_RESULTS = 8

#: A DART 접수번호 as every surface in this product links by.
_FILING_NUMBER = re.compile(r"\A\d{14}\Z")


class UnknownTool(ValueError):
    """The model called a name that is not one of the five. `P6.S3` decides what
    to tell it; there is deliberately no fallback tool to absorb the mistake."""


# ---------------------------------------------------------------------------
# citations
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Citation:
    """One thing a claim may rest on: a filing, and the words it prints.

    ``quote is None`` is the **API-tier** citation (R3, restated by R6-4): a
    ``cvbdIsDecsn`` figure has no 본문 span, so 접수번호 is the handle and the
    citation block says exactly that. It is a citation, not a missing one.
    """

    rcept_no: str
    quote: str | None = None
    span: tuple[int, int] | None = None
    #: Which contract field it came from, when it came from one.
    field_key: str | None = None

    @property
    def api_tier(self) -> bool:
        return self.quote is None

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"rcept_no": self.rcept_no, "api_tier": self.api_tier}
        if self.quote is not None:
            out["quote"] = self.quote
        if self.span is not None:
            out["span"] = list(self.span)
        if self.field_key is not None:
            out["field_key"] = self.field_key
        return out


def citations_in(payload: Any) -> tuple[Citation, ...]:
    """Every citation a contract payload carries, in reading order, deduplicated.

    A walk rather than a per-shape reader, because the shapes that carry a
    citation are many (:class:`~mijual.present.FieldPayload`,
    :class:`~mijual.present.Figure`, the ② fact strip, a 소멸 row) and they share
    one convention: ``rcept_no`` names the filing, ``quote``/``span`` are the
    filing's own words where they exist. Walking the convention means a shape
    added later is cited automatically instead of silently uncited.

    A **multi-part** citation (``parts``: a figure the filing prints as addends
    that sum — D4) yields one citation per addend under the parent's filing
    number, because that is what the reader must be shown; the sum itself has no
    passage to point at and is never given one.
    """
    found: list[Citation] = []
    seen: set[tuple[str, str | None, tuple[int, int] | None]] = set()

    def keep(citation: Citation) -> None:
        key = (citation.rcept_no, citation.quote, citation.span)
        if key not in seen:
            seen.add(key)
            found.append(citation)

    def span_of(node: Mapping[str, Any]) -> tuple[int, int] | None:
        raw = node.get("span")
        if isinstance(raw, (list, tuple)) and len(raw) == 2:
            return (int(raw[0]), int(raw[1]))
        return None

    def walk(node: Any) -> None:
        if isinstance(node, Mapping):
            rcept_no = node.get("rcept_no")
            if isinstance(rcept_no, str) and rcept_no:
                parts = node.get("parts")
                if isinstance(parts, Sequence) and not isinstance(parts, (str, bytes)):
                    for part in parts:
                        if isinstance(part, Mapping) and isinstance(part.get("quote"), str):
                            keep(
                                Citation(
                                    rcept_no=rcept_no,
                                    quote=part["quote"],
                                    span=span_of(part),
                                    field_key=node.get("field_key"),
                                )
                            )
                else:
                    quote = node.get("quote")
                    keep(
                        Citation(
                            rcept_no=rcept_no,
                            quote=quote if isinstance(quote, str) else None,
                            span=span_of(node),
                            field_key=node.get("field_key"),
                        )
                    )
            for value in node.values():
                walk(value)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for value in node:
                walk(value)

    walk(payload)
    return tuple(found)


# ---------------------------------------------------------------------------
# the result shape
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ToolResult:
    """What one tool call gives back: the values, the row, and the citations.

    Three consumers, three fields:

    * ``payload`` — the verified-contract values, JSON-ready, fed back to the
      model as the function response (`P6.S3`);
    * ``fact_row`` — the signed mono 도구 행 (`P6.S5` renders it verbatim);
    * ``citations`` — the machine-readable spans the generation boundary checks a
      claim against, and the source of :attr:`evidence` / :attr:`quotes`, which
      are exactly ``record_turn``'s 근거 rcept_no 목록 and 인용 칩 원문 (`P6.S4`).

    ``ok`` is **not** an error state in the UI sense: it is ``False`` only where
    the design has a signed answer for failure (``save_feedback`` → 재시도 행).
    A tool that found nothing is ``ok`` and says so in its payload — R6 answers
    「찾지 못했습니다」 as a fact, never as an error.
    """

    tool: str
    fact_row: str
    payload: dict[str, Any] = field(default_factory=dict)
    citations: tuple[Citation, ...] = ()
    ok: bool = True

    def __post_init__(self) -> None:
        # Figures leave every tool **display-ready**: a value the reader would see
        # grouped gains its ``value_display`` string beside the exact contract
        # ``value`` (:mod:`mijual.agent.figures`), so the model can write 3,200원
        # like every other surface without restating a number in another form.
        # Presentation only — nothing is derived, converted or rounded, and an
        # identifier (접수번호) is not a figure and is never touched. Done here
        # rather than at the five call sites so no tool can forget it.
        object.__setattr__(self, "payload", figures.with_display(self.payload))

    @property
    def evidence(self) -> tuple[str, ...]:
        """근거 rcept_no 목록 — unique, in reading order."""
        return tuple(dict.fromkeys(citation.rcept_no for citation in self.citations))

    @property
    def quotes(self) -> tuple[str, ...]:
        """인용 칩 원문 — verbatim, unique, in reading order. Never reconstructed."""
        return tuple(
            dict.fromkeys(
                citation.quote for citation in self.citations if citation.quote is not None
            )
        )

    def response(self) -> dict[str, Any]:
        """The whole result as one JSON object, for the model's function response."""
        return {
            "ok": self.ok,
            "fact_row": self.fact_row,
            "result": self.payload,
            "citations": [citation.payload() for citation in self.citations],
        }


# ---------------------------------------------------------------------------
# search_events
# ---------------------------------------------------------------------------
def _scope_event_id(ctx: ToolContext) -> int | None:
    if not ctx.scope_rcept_no:
        return None
    event = resolve_event(ctx.session, ctx.scope_rcept_no)
    return event.id if event is not None else None


def _rank(view: EventView, scope_event_id: int | None) -> tuple[int, int, int, str]:
    """Search order: the 범위 event first, then the board's own ranking.

    Reads the countdown the contract already computed and orders by it — the
    three populations :func:`mijual.web.reads.load_board` keeps apart, plus the
    past ones a search must still surface: dated-and-ahead (D-day ascending), an
    ② 진행 중, 일정 추후결정, then behind us. **Ordering only**; not one number is
    derived here.
    """
    scoped = 0 if (scope_event_id is not None and view.event_id == scope_event_id) else 1
    countdown = view.countdown
    days = countdown.days
    if countdown.date is None:
        bucket, key = 2, 0
    elif days is not None and days >= 0:
        bucket, key = 0, days
    elif view.rights_type == "R2" and countdown.is_open:
        bucket, key = 1, -(days or 0)
    else:
        bucket, key = 3, -(days or 0)
    return (scoped, bucket, key, view.rcept_no or "")


def _search_result(view: EventView) -> dict[str, Any]:
    """One search hit: which event it is, and when it is due. No field values.

    A hit is an *identification* — the row the model picks a candidate from — so
    it carries the identity, the type, the filing number and the governing
    countdown, and stops there. Loading four hundred characters of quote per hit
    would ship 본문 the answer has not decided to use; ``get_event`` is one call
    away and returns the whole verification contract for the one that matters.
    """
    return {
        "event_id": view.event_id,
        "corp_code": view.corp_code,
        "corp_name": view.identity.corp_name,
        "rights_type": view.rights_type,
        "rights_type_ko": ko.RIGHTS_TOOL_LABEL_KO.get(view.rights_type, view.rights_type),
        "rcept_no": view.rcept_no,
        "state": view.state,
        "countdown": view.countdown.payload(),
    }


def search_events(ctx: ToolContext, query: str) -> ToolResult:
    """공시 검색 — 이벤트 목록/단건, over **exposable events only**.

    A different contract from 내 종목 조회's resolution and deliberately so
    (`P6` Finding 15): R4 resolves *unique-or-decline* because opening the wrong
    company's 놓친 돈 page would be a wrong number, while R6's tool returns a
    list, so two 계양 companies are two candidates the answer may name rather than
    a miss. What does **not** change is the exposure contract: a suppressed,
    flagged or 철회된 event is not a search result
    (:func:`mijual.web.reads.load_corp_events`), so an answer cannot be built on
    gate-failed data by this path at all.

    A 14-digit query is a filing number and resolves to the single event it names
    (still gated). Everything else is an issuer lookup.

    **0건 is an answer, not an error**: the signed 「「{q}」에 해당하는 공시를 찾지
    못했습니다」 fact plus the 관제 현황판 pointer, and the tool returns no guess for
    the model to elaborate on.
    """
    text = (query or "").strip()
    views: list[EventView] = []

    if _FILING_NUMBER.match(text):
        event = resolve_event(ctx.session, text)
        if event is not None:
            views = [
                view
                for view in load_corp_events(ctx.session, [event.corp_code], today=ctx.today)
                if view.event_id == event.id
            ]
    elif text:
        corps = find_corps(ctx.session, text)
        views = load_corp_events(
            ctx.session, [corp.corp_code for corp in corps], today=ctx.today
        )

    scoped = _scope_event_id(ctx) if views else None
    ordered = sorted(views, key=lambda view: _rank(view, scoped))
    listed = ordered[:MAX_SEARCH_RESULTS]
    results = [_search_result(view) for view in listed]

    payload: dict[str, Any] = {
        "query": text,
        "count": len(ordered),
        "listed": len(results),
        "results": results,
    }
    if not ordered:
        # The signed sentence travels as a *fact* the answer may state verbatim.
        payload["none_found_ko"] = ko.NOT_FOUND_KO.format(q=text)
        payload["pointer"] = {"label_ko": ko.BOARD_POINTER_KO}
        if _FILING_NUMBER.match(text):
            # An event can be *readable* without being *searchable*: a 철회된
            # filing has a page and a locked notice, and answering 「찾지
            # 못했습니다」 about it would be the weaker of two true statements.
            # A machine hint, not copy — the answer still comes from get_event.
            payload["hint"] = (
                "call get_event with this rcept_no before concluding: an event can be "
                "readable (withdrawn, for example) without being searchable"
            )
    return ToolResult(
        tool="search_events",
        fact_row=ko.search_row(
            text,
            [(view.rights_type, view.rcept_no) for view in listed],
            count=len(ordered),
        ),
        payload=payload,
        citations=citations_in(results),
    )


# ---------------------------------------------------------------------------
# get_event
# ---------------------------------------------------------------------------
def get_event(ctx: ToolContext, rcept_no: str) -> ToolResult:
    """One event's **verification contract** — literally what its page renders.

    :func:`mijual.web.reads.event_payload` is the single assembly behind
    ``GET /events/{rcept_no}``, so the agent can quote nothing a reader could not
    see on the page, down to the key. Gate-blocked fields are absent (never null,
    never "확인 필요"), 추후결정 carries no date, and each renderable field brings
    its quote + span + 접수번호.

    A **철회된** event is a surface, not a miss: it comes back with its locked
    notice and the 정정사항 row that retracted the decision, which is what lets
    R6's 철회 refusal carry a 근거 칩 (「거절도 인용 강제 대상」). Everything else
    that is not renderable — suppressed, flagged, no_document — answers *not
    found*, exactly as the route answers 404: the reason is internal, and an event
    the contract does not expose must not become an explanation of why.

    The tool **never refuses in prose.** It reports what exists; `P6.S3` chooses
    the refusal family and writes the signed sentence.
    """
    key = (rcept_no or "").strip()
    event = resolve_event(ctx.session, key) if key else None
    detail = load_detail(ctx.session, event, today=ctx.today) if event is not None else None

    if detail is None or not detail.view.renderable:
        payload = {
            "found": False,
            "rcept_no": key,
            "none_found_ko": ko.NOT_FOUND_KO.format(q=key),
            "pointer": {"label_ko": ko.BOARD_POINTER_KO},
        }
        return ToolResult(tool="get_event", fact_row=ko.EVENT_MISS_ROW, payload=payload)

    payload = event_payload(ctx.session, detail)
    payload["found"] = True
    payload["rights_type_ko"] = ko.RIGHTS_TOOL_LABEL_KO.get(
        detail.view.rights_type, detail.view.rights_type
    )

    citations = list(citations_in(payload))
    withdrawal = payload.get("withdrawal")
    if isinstance(withdrawal, Mapping) and isinstance(withdrawal.get("after"), str):
        # 철회's own words: the 정정 후 cell is the verbatim passage, and the walk
        # above sees it as an rcept_no with no quote (the row's keys are 항목·
        # 정정 전·정정 후, not ``quote``). Stated here rather than taught to the
        # walker, because this is the one shape whose quote lives under a
        # different name.
        span = withdrawal.get("span")
        citations.insert(
            0,
            Citation(
                rcept_no=str(withdrawal.get("rcept_no") or detail.view.rcept_no or ""),
                quote=withdrawal["after"],
                span=(int(span[0]), int(span[1]))
                if isinstance(span, (list, tuple)) and len(span) == 2
                else None,
                field_key="withdrawal",
            ),
        )

    return ToolResult(
        tool="get_event",
        fact_row=ko.EVENT_ROW.format(
            corp_name=detail.view.identity.corp_name or detail.view.corp_code,
            rights_ko=payload["rights_type_ko"],
            rcept_no=detail.view.rcept_no or key,
        ),
        payload=payload,
        citations=tuple(citations),
    )


# ---------------------------------------------------------------------------
# get_portfolio
# ---------------------------------------------------------------------------
def get_portfolio(ctx: ToolContext) -> ToolResult:
    """내 포트폴리오 읽기 — the caller's own, or the **labelled** 샘플.

    It takes no argument beyond the context, and that is the whole security
    design (`P6` Finding 5): there is no account id to pass, no email to pass and
    no holdings payload to post. R5 made anonymous state structurally
    client-side — 「Anonymous state never reaches the server … there is no
    anonymous write endpoint at all」 — so an anonymous caller has no server-side
    portfolio to read, and R6-3's designed answer is the R5 sample, said out loud:
    the signed fact row names it 샘플 포트폴리오 · 구성 예시 and the answer must
    carry 「구성 예시」 with the 샘플 배너 rule.

    Both branches go through :func:`mijual.web.reads.load_portfolio`, the same
    composition ``GET /portfolio`` and ``GET /portfolio/sample`` serve, so the
    D-day list, the 「추정」 amounts and the 발행가 확정 전 rows are the reader's own
    numbers and not a second reading of them. **No total is served**, here or
    there — R5-8 keeps the 챙긴 돈 mark out of every aggregate by giving the
    surface none.
    """
    account = ctx.account
    if account is None:
        payload = load_portfolio(
            ctx.session, portfolio_service.sample_entries(), today=ctx.today, claims=None
        )
        payload["sample"] = True
        payload["sample_label_ko"] = ko.PORTFOLIO_SAMPLE_LABEL_KO
        fact_row = ko.PORTFOLIO_SAMPLE_ROW.format(n=len(payload["holdings"]))
    else:
        payload = load_portfolio(
            ctx.session,
            portfolio_service.entries_of(ctx.session, account),
            today=ctx.today,
            claims=portfolio_service.claimed_reports(ctx.session, account),
        )
        payload["sample"] = False
        fact_row = ko.PORTFOLIO_ROW.format(n=len(payload["holdings"]))

    return ToolResult(
        tool="get_portfolio",
        fact_row=fact_row,
        payload=payload,
        citations=citations_in(payload),
    )


# ---------------------------------------------------------------------------
# save_feedback
# ---------------------------------------------------------------------------
def save_feedback(ctx: ToolContext, text: str, email: str | None = None) -> ToolResult:
    """의견 저장 — straight into R7's 운영자 검토 대기열, with no form.

    R6 §의견: 자유 텍스트 → 자동 저장, one confirmation line, and 답장용 이메일 as an
    optional field the reader may volunteer. The write is `P6.S1`'s
    :func:`~mijual.web.conversationstore.record_feedback`, which is where the
    anonymity rules live (an address is stored only when it was typed; the
    session handle is a minted token or nothing).

    **Flushed, not committed** — the transport's write session owns the
    transaction. A failure comes back ``ok=False`` with a structural reason code
    and the 재시도 row; the tool writes no Korean sentence about it, because R6
    signs the confirmation copy and the surface renders it.
    """
    try:
        row = record_feedback(
            ctx.session,
            text=text or "",
            email=email,
            session_hash=ctx.session_hash,
        )
    except ValueError as exc:
        return ToolResult(
            tool="save_feedback",
            fact_row=ko.FEEDBACK_RETRY_ROW,
            payload={"saved": False, "reason": "invalid_input", "detail": str(exc)},
            ok=False,
        )
    except SQLAlchemyError:
        # The write failed and the session must stay usable for the rest of the
        # turn's reads — this tool is the only writer, so nothing else is lost.
        ctx.session.rollback()
        return ToolResult(
            tool="save_feedback",
            fact_row=ko.FEEDBACK_RETRY_ROW,
            payload={"saved": False, "reason": "write_failed"},
            ok=False,
        )

    return ToolResult(
        tool="save_feedback",
        fact_row=ko.FEEDBACK_ROW,
        payload={"saved": True, "email_recorded": row.email is not None},
    )


# ---------------------------------------------------------------------------
# get_contact
# ---------------------------------------------------------------------------
def get_contact(ctx: ToolContext) -> ToolResult:
    """운영자 연락처 — the deploy setting, or an honest "there is none yet".

    R6: 「연락처 문자열은 배포 설정값 — **미정, 운영자 지정** (하드코딩 발명 금지)」,
    and `security` records it as the one operator-identifying string the product
    will publish. So this reads :attr:`mijual.config.Settings.operator_contact`
    and, when it is unset, says so — no address, no placeholder, and **no
    「준비 중」 line**, which would be an invented Korean sentence and therefore a
    design change (`P6` Finding 9).
    """
    contact = (ctx.config().operator_contact or "").strip()
    if not contact:
        return ToolResult(
            tool="get_contact",
            fact_row=ko.CONTACT_UNSET_ROW,
            payload={"configured": False},
        )
    return ToolResult(
        tool="get_contact",
        fact_row=ko.CONTACT_ROW.format(contact=contact),
        payload={"configured": True, "contact": contact},
    )


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------
#: The five, in the order R6 lists them. `P6.S3` hands the same five to the SDK
#: (:func:`mijual.agent.declarations.declarations`) — one list, one truth.
TOOL_NAMES: tuple[str, ...] = (
    "search_events",
    "get_event",
    "get_portfolio",
    "save_feedback",
    "get_contact",
)


def call_tool(name: str, ctx: ToolContext, arguments: Mapping[str, Any] | None = None) -> ToolResult:
    """Execute one function call the model asked for.

    Arguments arrive from a model and are treated as such: the declared ones are
    read by name and coerced to text, and anything else is ignored rather than
    passed on — there is no argument on any tool that could carry an identity, so
    ignoring extras costs nothing and closes the shape entirely. An unknown name
    raises :class:`UnknownTool`; inventing a sixth tool is the model's mistake to
    be told about, not something to absorb silently.
    """
    args: Mapping[str, Any] = arguments or {}

    def text(key: str) -> str:
        value = args.get(key)
        return value.strip() if isinstance(value, str) else ("" if value is None else str(value))

    if name == "search_events":
        return search_events(ctx, text("query"))
    if name == "get_event":
        return get_event(ctx, text("rcept_no"))
    if name == "get_portfolio":
        return get_portfolio(ctx)
    if name == "save_feedback":
        return save_feedback(ctx, text("text"), text("email") or None)
    if name == "get_contact":
        return get_contact(ctx)
    raise UnknownTool(f"{name!r} is not one of {TOOL_NAMES}")


def fact_rows(results: Iterable[ToolResult]) -> list[str]:
    """The turn's 도구 행 in call order — what `P6.S5` renders above the answer."""
    return [result.fact_row for result in results]
