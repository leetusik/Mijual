"""② CB 오버행 — the structured reading of ``cvbdIsDecsn`` and the 오버행 캘린더.

② is the phase's one **zero-LLM** rights type (N6): 전환가액, 전환비율,
전환청구기간 and the 오버행 수량·비율 are all `API` tier, measured 47/47 in P1 and
re-measured here over the whole collected corpus. So this module is deliberately
*not* an extractor: it reads the stored detail-endpoint snapshot, parses its
values into typed facts, and derives the calendar the board counts down to.

Three rules it keeps.

**One reading, one place.** ``ConvertibleFacts`` is the only place a ``cv_prc``
string becomes a number and a ``2026년 11월 10일`` becomes a ``date``. The
exposure contract, the calendar and ``P2.S8``'s estimation all call it, so a
parsing fix lands everywhere at once.

**The API row belongs to the CURRENT version and to no other** (N2/N46). The
detail endpoints collapse an event to one row carrying the newest ``rcept_no``,
so these facts describe today's reading of the event — never a superseded one.

**Absence is recorded, never guessed.** A field the filing does not carry lands
in :attr:`ConvertibleFacts.missing` and blocks exposure (see
:data:`R2_REQUIRED_API_FIELDS`); nothing is defaulted, interpolated or inferred.

    .venv/bin/python -m mijual.cb calendar --today 2026-09-07
    .venv/bin/python -m mijual.cb documents --limit 40
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.db.models import Event, RightsType, Snapshot, FilingVersion
from mijual.gates.context import korean_date

__all__ = [
    "CB_ENDPOINT",
    "CalendarEntry",
    "ConvertibleFacts",
    "OverhangCalendar",
    "R2_REQUIRED_API_FIELDS",
    "detail_row",
    "event_facts",
    "facts_from_row",
    "overhang_calendar",
    "urgency_events",
]

#: The one ② source. ``bdRs`` is not a second one (N5, field-matrix §2.2).
CB_ENDPOINT = "cvbdIsDecsn"

#: The API fields ②'s countdown cannot be rendered without, with the Korean name
#: the board would print. This list **is** ②'s exposure test: a filing missing any
#: of them cannot be shown as a live 오버행 event, because either the price, the
#: window or the size of the dilution would be blank.
R2_REQUIRED_API_FIELDS: tuple[tuple[str, str], ...] = (
    ("cv_prc", "전환가액"),
    ("cvrqpd_bgd", "전환청구기간 개시일"),
    ("cvrqpd_edd", "전환청구기간 종료일"),
    ("cvisstk_cnt", "전환 발행주식수"),
    ("cvisstk_tisstk_vs", "주식총수 대비 비율"),
)

#: OpenDART writes an unfilled field as ``-``.
_EMPTY = {"", "-", "–", "—", "해당사항없음", "해당사항 없음", "해당없음"}


def _text(value: Any) -> str | None:
    text = str(value or "").strip()
    return None if text in _EMPTY else text


def _number(value: Any) -> Decimal | None:
    """``'2,255,808'`` → ``Decimal('2255808')``; ``'-'`` → ``None``.

    Decimal, not float: 전환가액 × 주식수 is money, and §3.6's *계산은 결정론*
    clause means it must not pick up binary-floating-point noise on the way in.
    """
    text = _text(value)
    if text is None:
        return None
    try:
        return Decimal(text.replace(",", "").replace("%", "").replace("원", "").strip())
    except (InvalidOperation, ValueError):
        return None


@dataclass(frozen=True)
class ConvertibleFacts:
    """One CB issuance as the API states it. Every field is measured or ``None``."""

    rcept_no: str | None = None
    #: 전환가액 (원/주) — ``cv_prc``.
    conversion_price: Decimal | None = None
    #: 전환비율 (%) — ``cv_rt``.
    conversion_ratio: Decimal | None = None
    #: 전환청구기간 — ``cvrqpd_bgd`` / ``cvrqpd_edd``.
    request_begin: date | None = None
    request_end: date | None = None
    #: 전환 시 발행될 주식수 — ``cvisstk_cnt``.
    shares: Decimal | None = None
    #: 주식총수 대비 비율 (%) — ``cvisstk_tisstk_vs``. **The 오버행 number.**
    overhang_pct: Decimal | None = None
    #: 리픽싱 최저 조정가액 — ``act_mktprcfl_cvprc_lwtrsprc`` (gate 6's reference).
    refixing_floor: Decimal | None = None
    refixing_basis: str | None = None
    #: 권면총액 / 사채 만기일 / 납입일 — gates 7·8's reference values.
    face_amount: Decimal | None = None
    maturity_date: date | None = None
    pay_date: date | None = None
    #: 발행방법 (사모/공모) — ``bdis_mthn``.
    issue_method: str | None = None
    #: 해외발행 통화, when ``ovis_fta_crn`` is filled (헝셩그룹 HKD is the one case).
    overseas_currency: str | None = None
    #: Required fields this filing does not carry, as ``(key, 한국어 이름)``.
    missing: tuple[tuple[str, str], ...] = ()

    @property
    def complete(self) -> bool:
        """Are all of :data:`R2_REQUIRED_API_FIELDS` present and parseable?"""
        return not self.missing

    @property
    def overseas(self) -> bool:
        return self.overseas_currency is not None

    def days_to_open(self, today: date) -> int | None:
        """Days until 전환청구 opens; negative once it has opened. KST dates."""
        if self.request_begin is None:
            return None
        return (self.request_begin - today).days

    def is_open(self, today: date) -> bool:
        """Inclusive at both ends, like every window in this codebase (N50)."""
        if self.request_begin is None:
            return False
        if self.request_begin > today:
            return False
        return self.request_end is None or today <= self.request_end


def facts_from_row(row: Mapping[str, Any] | None) -> ConvertibleFacts:
    """Parse one ``cvbdIsDecsn`` detail row. Pure; no I/O, no defaults.

    A row whose KRW fields do not parse comes back with them ``None`` and named
    in :attr:`ConvertibleFacts.missing` — which is the whole 해외/USD rule: an
    offshore issue is exposable **iff its KRW conversion fields parse**, not
    because of what ``ovis_*`` says. The one 해외 case in the corpus (헝셩그룹
    ``20260213002703``, 16,000,000 HKD) states 전환가액 174원 and 17,110,804주 in
    KRW/shares like any domestic issue, so it passes on its own merits.
    """
    row = row or {}
    facts = ConvertibleFacts(
        rcept_no=_text(row.get("rcept_no")),
        conversion_price=_number(row.get("cv_prc")),
        conversion_ratio=_number(row.get("cv_rt")),
        request_begin=korean_date(row.get("cvrqpd_bgd")),
        request_end=korean_date(row.get("cvrqpd_edd")),
        shares=_number(row.get("cvisstk_cnt")),
        overhang_pct=_number(row.get("cvisstk_tisstk_vs")),
        refixing_floor=_number(row.get("act_mktprcfl_cvprc_lwtrsprc")),
        refixing_basis=_text(row.get("act_mktprcfl_cvprc_lwtrsprc_bs")),
        face_amount=_number(row.get("bd_fta")),
        maturity_date=korean_date(row.get("bd_mtd")),
        pay_date=korean_date(row.get("pymd")),
        issue_method=_text(row.get("bdis_mthn")),
        overseas_currency=_text(row.get("ovis_fta_crn")),
    )
    parsed = {
        "cv_prc": facts.conversion_price,
        "cvrqpd_bgd": facts.request_begin,
        "cvrqpd_edd": facts.request_end,
        "cvisstk_cnt": facts.shares,
        "cvisstk_tisstk_vs": facts.overhang_pct,
    }
    missing = tuple((key, name) for key, name in R2_REQUIRED_API_FIELDS if parsed[key] is None)
    return replace(facts, missing=missing)


def detail_row(session: Session, event: Event) -> dict:
    """Newest stored ``cvbdIsDecsn`` snapshot payload of an event (``{}`` if none).

    Scoped to the event's own ``report_subtype`` rather than "not a list row", so
    an unrelated snapshot source can never be read as a CB detail row.
    """
    snapshot = session.scalar(
        select(Snapshot)
        .join(FilingVersion, Snapshot.filing_version_id == FilingVersion.id)
        .where(FilingVersion.event_id == event.id, Snapshot.source == event.report_subtype)
        .order_by(Snapshot.captured_at.desc())
        .limit(1)
    )
    payload = snapshot.payload_json if snapshot is not None else None
    return payload if isinstance(payload, dict) else {}


def event_facts(session: Session, event: Event) -> ConvertibleFacts:
    """The CB facts of one event, from its stored detail snapshot. Zero requests."""
    return facts_from_row(detail_row(session, event))


# ---------------------------------------------------------------------------
# the 오버행 캘린더
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CalendarEntry:
    """One ② event on the calendar, with the evidence behind every number."""

    corp_code: str
    corp_name: str | None
    rcept_no: str | None
    original_rcept_dt: date | None
    exposure_state: str | None
    facts: ConvertibleFacts

    def days_to_open(self, today: date) -> int | None:
        return self.facts.days_to_open(today)

    def line(self, today: date) -> str:
        days = self.days_to_open(today)
        when = (
            "-"
            if days is None
            else (f"D-{days}" if days > 0 else ("D-DAY" if days == 0 else f"개시 {-days}일 경과"))
        )
        pct = f"{self.facts.overhang_pct}%" if self.facts.overhang_pct is not None else "-"
        # ``str()`` first: ``date.__format__`` treats a format spec as a strftime
        # pattern, so ``f"{a_date:<11}"`` silently prints the literal ``<11``.
        opens = str(self.facts.request_begin or "?")
        return (
            f"  {opens:<11} {when:<14} {pct:>8}  "
            f"{(self.corp_name or self.corp_code):<16} {self.rcept_no or '-'}"
        )


@dataclass
class OverhangCalendar:
    """The ② evidence deliverable: who dilutes, by how much, and when."""

    today: date
    entries: list[CalendarEntry]
    blocked: dict[str, int]
    events_total: int = 0
    by_filing_year: dict[str, int] | None = None

    def opening_within(self, days: int) -> list[CalendarEntry]:
        """Events whose 전환청구 **opens** in ``(today, today+days]`` — future only.

        Already-open events are excluded on purpose: an overhang that opened
        months ago is a fact about the past, and the calendar's claim is about
        what lands during the judging window.
        """
        out = []
        for entry in self.entries:
            delta = entry.days_to_open(self.today)
            if delta is not None and 0 <= delta <= days:
                out.append(entry)
        return sorted(out, key=lambda e: (e.facts.request_begin, e.corp_code))

    @property
    def already_open(self) -> list[CalendarEntry]:
        return [e for e in self.entries if e.facts.is_open(self.today)]

    def largest_ratio(self, days: int) -> CalendarEntry | None:
        window = [e for e in self.opening_within(days) if e.facts.overhang_pct is not None]
        return max(window, key=lambda e: e.facts.overhang_pct) if window else None

    def render(self, *, horizons: tuple[int, ...] = (30, 90, 180), show: int = 12) -> str:
        lines = [
            f"today      : {self.today} (KST)",
            f"events     : {self.events_total} ② event(s) held, {len(self.entries)} exposable "
            f"with a complete API countdown",
            f"blocked    : {dict(sorted(self.blocked.items())) or '-'}",
        ]
        if self.by_filing_year:
            lines.append(f"vintage    : {dict(sorted(self.by_filing_year.items()))} (by 최초 접수연도)")
        lines.append(f"open now   : {len(self.already_open)} event(s) already inside 전환청구기간")
        for days in horizons:
            window = self.opening_within(days)
            biggest = self.largest_ratio(days)
            lines.append(
                f"opens ≤{days:>4}d: {len(window):>3} event(s)"
                + (
                    f" | 최대 오버행 {biggest.facts.overhang_pct}% "
                    f"({biggest.corp_name} {biggest.rcept_no}, {biggest.facts.request_begin})"
                    if biggest
                    else ""
                )
            )
        soonest = self.opening_within(max(horizons))[:show]
        if soonest:
            lines.append(f"  {'개시일':<11} {'D':<14} {'오버행':>8}  회사 / rcept_no")
            lines.extend(entry.line(self.today) for entry in soonest)
        return "\n".join(lines)


def _r2_events(session: Session) -> list[Event]:
    return list(
        session.scalars(
            select(Event).where(Event.rights_type == RightsType.CONVERTIBLE_OVERHANG)
        ).all()
    )


def overhang_calendar(session: Session, *, today: date, exposable_only: bool = True) -> OverhangCalendar:
    """Build the calendar from persisted rows only. Zero requests, zero calls."""
    entries: list[CalendarEntry] = []
    blocked: dict[str, int] = {}
    years: dict[str, int] = {}
    events = _r2_events(session)

    for event in events:
        facts = event_facts(session, event)
        state = event.exposure_state
        if exposable_only and state != "exposable":
            key = event.exposure_reason or state or "ungated"
            blocked[key] = blocked.get(key, 0) + 1
            continue
        if not facts.complete:
            blocked["incomplete_api_row"] = blocked.get("incomplete_api_row", 0) + 1
            continue
        if event.original_rcept_dt is not None:
            year = str(event.original_rcept_dt.year)
            years[year] = years.get(year, 0) + 1
        entries.append(
            CalendarEntry(
                corp_code=event.corp_code,
                corp_name=event.corp.corp_name if event.corp else None,
                rcept_no=facts.rcept_no,
                original_rcept_dt=event.original_rcept_dt,
                exposure_state=state,
                facts=facts,
            )
        )

    return OverhangCalendar(
        today=today,
        entries=sorted(entries, key=lambda e: (e.facts.request_begin or date.max, e.corp_code)),
        blocked=blocked,
        events_total=len(events),
        by_filing_year=years,
    )


def urgency_events(
    session: Session,
    *,
    until: date,
    today: date | None = None,
    exposable_only: bool = True,
) -> list[Event]:
    """② events whose 전환청구 opens on or before ``until`` — **most urgent first**.

    The 본문 fetch and the (capped) prose pass both run over this list rather than
    over the whole corpus: fields 6–8 are narrative colour on a countdown that is
    already complete without them, so paying for the event that opens in 2029
    before the one that opens next month would be the wrong order of spending.

    "Most urgent" is not simply "earliest ``cvrqpd_bgd``". An event that opened in
    2024 has the earliest date in the corpus and the least to say about the
    weeks ahead, so the order is **upcoming openings first (soonest first), then
    already-open events (most recently opened first)** — under a ceiling that is
    the difference between documenting the events that open during the judging
    window and documenting a 2024 vintage that no longer moves.
    """
    anchor = today or date.today()
    scored: list[tuple[int, int, str, Event]] = []
    for event in _r2_events(session):
        if exposable_only and event.exposure_state != "exposable":
            continue
        opens = event_facts(session, event).request_begin
        if opens is None or opens > until:
            continue
        upcoming = opens >= anchor
        # Bucket 0 ascending = soonest to open; bucket 1 with a negated ordinal =
        # most recently opened first.
        scored.append(
            (0 if upcoming else 1, opens.toordinal() * (1 if upcoming else -1),
             event.corp_code, event)
        )
    return [event for _, _, _, event in sorted(scored, key=lambda s: s[:3])]
