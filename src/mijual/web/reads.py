"""The read layer: persisted rows in, :mod:`mijual.present` shapes out.

Routers do transport. This module does loading — and **only** loading: it decides
which rows a surface needs and hands them to the derivation layer, which decides
what they mean. Nothing here computes a displayed number, and nothing here
re-decides exposure: :func:`mijual.gates.exposure.exposure_of` is the one
derivation and this module feeds it.

Three loading rules worth stating, because each is a performance decision that
had to stay a *correctness* decision too.

**The board batches; it does not loop.** A row needs its event, its current
readable version, that version's governing countdown field and — for ① — its
stored offering inputs. Fetching those per row would be four queries × ~500 rows.
So each is one query over the whole page, and the per-event assembly is pure
Python afterwards. The version choice comes from
:func:`mijual.db.repository.current_versions`, which is the *same* rule as
:func:`~mijual.db.repository.current_version` (see its docstring for the one way
they could differ, and the measurement that says they do not).

**The board loads one field per event, on purpose.** A board row renders no field
values — R2's row is chip · 회사 · countdown · ①'s extras · D-day — so loading all
409 gate-passing fields would ship 600-character quotes nobody renders. The
detail endpoint loads them all; the board loads the countdown's.

**One 종목 is loaded once and read twice.** ``P5.S4``'s lookup surface asks two
questions about the same events — what is live, and what already lapsed — so
:func:`load_stock` loads the issuer's events a single time (batched the same way
the board batches) and derives both sections from that one reading. Two loaders
would eventually describe two different versions of one offering.

**A detail request may cost a document decode; a board request may not.** One
event's 본문 is read once (:func:`mijual.db.repository.current_document`) and used
for both the exposure and the 회사명 the filing prints. That is a stored-bytes
read and a ZIP decode — no OpenDART request, no model call — and it happens for
one event, never for a page of them.

**What is not here:** the 소멸가치 and the ① money inputs. Deriving those needs
:mod:`mijual.estimate`, which imports the three spending modules, so a worker
precomputes them (``python -m mijual.estimate snapshot``) into
:class:`~mijual.db.models.OfferingInput` and ``PerformanceReport.lapse``, and this
module reads those rows like any others.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from mijual.calc import KST
from mijual.cb import ConvertibleFacts, facts_from_row
from mijual.db.models import (
    Corp,
    Event,
    Extraction,
    FilingVersion,
    OfferingInput,
    PerformanceReport,
    RightsType,
    Snapshot,
)
from mijual.db.repository import current_document, current_versions
from mijual.gates.exposure import EventExposure, exposure_of
from mijual.present import (
    BoardRow,
    BoardSummary,
    CorrectionStory,
    EventView,
    bare_name,
    board_row,
    board_summary,
    convertible_view,
    correction_story,
    event_view,
    iso_day,
    issuer_disagreement,
    lapse_result,
    lapse_totals,
    offering_inputs,
)

__all__ = [
    "CONVERTIBLE_COVERAGE_START",
    "COUNTDOWN_FIELDS",
    "DEFAULT_CUTOFF_TIME",
    "LAPSE_COVERAGE_START",
    "STOCK_FIELDS",
    "Detail",
    "corpus_as_of",
    "countdown_target",
    "load_board",
    "load_detail",
    "load_stock",
    "load_summary",
    "resolve_corp",
    "resolve_event",
    "rights_of",
    "stock_by_code",
]

#: The one field each 본문-tier type counts down to. ② is absent because its
#: countdown is `API` tier (``cvbdIsDecsn``), not a 본문 reading.
COUNTDOWN_FIELDS = ("warrant_trading_period", "dissent_notice_procedure")

#: The default 소멸 instant: **end of the 청약 day**, i.e. 00:00 KST of the next
#: day. R2 assumed exactly this (2026-09-04 24:00 KST for 계양전기) and the real
#: 접수 마감 시각 is still an open operator question — so the assumption is the
#: stated default and ``MIJUAL_COUNTDOWN_CUTOFF_TIME`` replaces it without a code
#: change. Nothing else in the product invents an instant from a calendar day.
DEFAULT_CUTOFF_TIME = "24:00"

_RIGHTS = {r.value: r for r in RightsType}


def rights_of(tab: str | None) -> RightsType | None:
    """``"R1"`` → the enum; ``None``/unknown → no filter (the 전체 tab)."""
    return _RIGHTS.get(tab or "")


# ---------------------------------------------------------------------------
# freshness and the countdown instant
# ---------------------------------------------------------------------------
def corpus_as_of(session: Session) -> datetime | None:
    """기준시각 — when the pipeline last observed the corpus this board describes.

    ``max(Event.last_seen_at)``: every collection run stamps the events it saw,
    so this is the answer to *when did we last look at DART*, which is the
    question the freshness chip asks. Deliberately **not** the request time (that
    would make a dead worker look healthy) and not a per-row timestamp (the board
    is one corpus, and a reader is owed one 기준시각 for it).
    """
    return session.scalar(select(func.max(Event.last_seen_at)))


def countdown_target(day: date | None, *, cutoff: str | None = None) -> datetime | None:
    """The absolute KST instant the landing ticks down to, from a calendar day.

    The browser only diffs an instant; turning 2026-09-04 into one is a service
    decision, and this is where it is made — once, with the operator's real
    cut-off substitutable by setting. ``24:00`` means the end of that day.
    """
    if day is None:
        return None
    text = (cutoff or DEFAULT_CUTOFF_TIME).strip()
    if text in ("24:00", "2400", "24"):
        return datetime.combine(day + timedelta(days=1), time(0, 0), tzinfo=KST)
    try:
        hour, _, minute = text.partition(":")
        moment = time(int(hour), int(minute or 0))
    except ValueError:  # a mistyped env var must not take the countdown down
        return datetime.combine(day + timedelta(days=1), time(0, 0), tzinfo=KST)
    return datetime.combine(day, moment, tzinfo=KST)


# ---------------------------------------------------------------------------
# the board
# ---------------------------------------------------------------------------
def _exposable_events(session: Session) -> list[Event]:
    return list(
        session.scalars(
            select(Event)
            .where(Event.exposure_state == "exposable")
            .options(joinedload(Event.corp), selectinload(Event.versions))
        ).all()
    )


def _field_rows(
    session: Session, version_ids: Sequence[int], fields: Sequence[str] = COUNTDOWN_FIELDS
) -> dict[int, list[Extraction]]:
    """Named fields of a page of versions — one query, gate verdicts included.

    ``fields`` is always a **subset**, never "all of them": a surface that renders
    five values must not ship four hundred, and :func:`exposure_of` accepts a
    subset of rows precisely so a caller can load only what it will show.
    """
    if not version_ids:
        return {}
    rows: dict[int, list[Extraction]] = {}
    for row in session.scalars(
        select(Extraction).where(
            Extraction.filing_version_id.in_(version_ids),
            Extraction.field_key.in_(tuple(fields)),
        )
    ).all():
        rows.setdefault(row.filing_version_id, []).append(row)
    return rows


def _detail_facts(session: Session, events: Sequence[Event]) -> dict[int, ConvertibleFacts]:
    """②'s API-tier facts for a whole page — the newest detail snapshot per event.

    Same selection as :func:`mijual.cb.detail_row` (scoped to the event's own
    ``report_subtype``, newest ``captured_at`` first), batched.
    """
    ids = [event.id for event in events if event.rights_type is RightsType.CONVERTIBLE_OVERHANG]
    if not ids:
        return {}
    newest: dict[int, tuple[datetime, Any]] = {}
    for event_id, captured_at, payload in session.execute(
        select(FilingVersion.event_id, Snapshot.captured_at, Snapshot.payload_json)
        .join(FilingVersion, Snapshot.filing_version_id == FilingVersion.id)
        .join(Event, Event.id == FilingVersion.event_id)
        .where(FilingVersion.event_id.in_(ids), Snapshot.source == Event.report_subtype)
    ).all():
        seen = newest.get(event_id)
        if seen is None or captured_at > seen[0]:
            newest[event_id] = (captured_at, payload)
    return {
        event_id: facts_from_row(payload if isinstance(payload, dict) else {})
        for event_id, (_, payload) in newest.items()
    }


def _offering_inputs(session: Session, events: Sequence[Event]) -> dict[int, Mapping[str, Any]]:
    """The worker's precomputed ① inputs, keyed by event."""
    ids = [event.id for event in events if event.rights_type is RightsType.SUBSCRIPTION_WARRANT]
    if not ids:
        return {}
    return {
        row.event_id: row.inputs
        for row in session.scalars(
            select(OfferingInput).where(OfferingInput.event_id.in_(ids))
        ).all()
        if isinstance(row.inputs, Mapping)
    }


def _board_views(session: Session, *, today: date) -> list[tuple[EventView, Any]]:
    """Every exposable event as an :class:`EventView`, with its ① inputs beside it."""
    events = _exposable_events(session)
    versions = current_versions(session, events)
    rows = _field_rows(session, [v.id for v in versions.values()])
    facts = _detail_facts(session, events)
    offerings = _offering_inputs(session, events)

    views: list[tuple[EventView, Any]] = []
    for event in events:
        version = versions.get(event.id)
        exposure = exposure_of(
            event,
            version=version,
            rows=rows.get(version.id, []) if version is not None else [],
            facts=facts.get(event.id),
        )
        view = event_view(exposure, facts=facts.get(event.id), today=today)
        views.append((view, offerings.get(event.id)))
    return views


def load_board(
    session: Session, *, today: date, rights: RightsType | None = None
) -> dict[str, Any]:
    """The 관제 현황판: tab counts, the ranked rows, and the two pinned strips.

    Ranking is **D-day ascending across types**, and three populations are kept
    apart because the design keeps them apart:

    * ``rows`` — everything still ahead (``days >= 0``). A past ① is a lapsed
      right and a past ③ a passed deadline; neither is on the landing.
    * ``open_now`` — ② whose 전환청구 has **opened and not closed**. Past, and
      live: the dilution is happening right now, so it is a pinned strip and is
      never labelled 종료 (`ui-traps.md` #5).
    * ``tbd`` — exposable with no countdown date at all. **Unranked**, by R3's
      board-strip decision, and carrying no date anywhere near it.

    Two events sharing an ``rcept_no`` (2 in the corpus, ``hint_duplicate``) are
    two truthful rows and are **not** de-duplicated here — see the phase note on
    D2: a display-level ``DISTINCT`` would paper over a corpus fact.
    """
    views = _board_views(session, today=today)
    summary = board_summary([view for view, _ in views])

    ranked: list[BoardRow] = []
    open_now: list[BoardRow] = []
    tbd: list[BoardRow] = []
    for view, offering in views:
        if view.state != "exposable":
            # The persisted column said exposable and the contract disagreed —
            # a gate run that has not landed yet. The contract wins: the API
            # renders what ``gates.exposure`` says, never its own reading.
            continue
        row = board_row(view, offering=offering)
        countdown = view.countdown
        if countdown.date is None:
            tbd.append(row)
        elif countdown.days is not None and countdown.days >= 0:
            ranked.append(row)
        elif view.rights_type == "R2" and countdown.is_open:
            open_now.append(row)

    ranked.sort(key=lambda row: (row.days if row.days is not None else 10**6, row.corp_code))
    # Most recently opened first: the freshest dilution is the interesting one.
    open_now.sort(key=lambda row: (-(row.days or 0), row.corp_code))
    tbd.sort(key=lambda row: (row.corp_name or row.corp_code))

    def keep(rows: list[BoardRow]) -> list[dict[str, Any]]:
        return [
            row.payload()
            for row in rows
            if rights is None or row.rights_type == rights.value
        ]

    def strip(rows: list[BoardRow], total: int) -> dict[str, Any]:
        """A pinned strip. ``count`` is what this response holds, ``total`` what
        the whole board holds — a tab filters the rows, never the board's own
        count of them."""
        kept = keep(rows)
        return {"count": len(kept), "total": total, "rows": kept}

    return {
        "reference": today.isoformat(),
        "counts": {"all": summary.watching, **summary.by_rights},
        "rows": keep(ranked),
        "open_now": strip(open_now, summary.open_now),
        "tbd": strip(tbd, summary.tbd),
    }


# ---------------------------------------------------------------------------
# the landing summary
# ---------------------------------------------------------------------------
def _pending_lapses(
    session: Session, *, today: date, corp_code: str | None = None
) -> list[tuple[str | None, date, str | None]]:
    """① offerings whose 청약 has not closed yet — "소멸 앞둔 신주인수권".

    The same population :func:`mijual.estimate.build_report` calls ``청약 예정``,
    read from the worker's precomputed rows instead of from a 본문 parse: an
    exposable ① event with no **parsed** 실적보고서 and a 구주주 청약 마감 still in
    the future. 철회 and flagged events are excluded because a withdrawn offering
    has no 소멸 to await, and a flagged one is not on the board at all.

    Ordered ``(마감일, 접수번호)`` so the strip's "가장 빠른 청약 마감" names the same
    company on every request and in every deployment. Three offerings share
    2026-09-04 today and the pipeline's own ``min()`` picks whichever row the
    database happened to return first; sorting by the filing number breaks the tie
    on **which offering has been public longest** (an ``rcept_no`` opens with its
    접수일) and, unlike sorting by 회사명, does not depend on the database's Korean
    collation.

    ``corp_code`` narrows the same population to one issuer — R4's 놓친 돈 section
    says "진행 중인 건의 소멸 여부는 청약 종료(…) 후 집계됩니다" from exactly this
    list, so it must be **the same definition** the landing counts 15건 with, not
    a second one that happens to agree today.
    """
    rows = session.execute(
        select(OfferingInput.decision_rcept_no, OfferingInput.subscription_end, Corp.corp_name)
        .join(Event, Event.id == OfferingInput.event_id)
        .outerjoin(Corp, Corp.corp_code == Event.corp_code)
        .outerjoin(
            PerformanceReport,
            and_(
                PerformanceReport.event_id == Event.id,
                PerformanceReport.parse_status == "parsed",
            ),
        )
        .where(
            Event.rights_type == RightsType.SUBSCRIPTION_WARRANT,
            Event.suppressed_reason.is_(None),
            Event.exposure_state == "exposable",
            PerformanceReport.id.is_(None),
            OfferingInput.subscription_end.is_not(None),
            OfferingInput.subscription_end > today,
            *([Event.corp_code == corp_code] if corp_code is not None else []),
        )
        .order_by(OfferingInput.subscription_end, OfferingInput.decision_rcept_no, Event.id)
    ).all()

    # One 유상증자결정 can sit under two event keys (N21) and the sentence counts
    # offerings, not rows.
    seen: set[str] = set()
    pending: list[tuple[str | None, date, str | None]] = []
    for rcept_no, end, corp_name in rows:
        if rcept_no is not None:
            if rcept_no in seen:
                continue
            seen.add(rcept_no)
        pending.append((rcept_no, end, corp_name))
    return pending


def load_summary(
    session: Session,
    *,
    today: date,
    now: datetime,
    stale_after_hours: int,
    cutoff: str | None = None,
) -> BoardSummary:
    """One summary for the whole landing — counts, headline and freshness.

    Every landing number comes from this single object, so the hero's stat line
    and the countdown/stats card cannot disagree about 감시 중 or 30일 이내: they
    are the same field read twice.
    """
    views = [view for view, _ in _board_views(session, today=today)]
    stored = list(session.scalars(select(PerformanceReport)).all())
    totals = lapse_totals([r.lapse for r in stored if isinstance(r.lapse, Mapping)])
    pending = _pending_lapses(session, today=today)
    soonest = pending[0] if pending else (None, None, None)

    return board_summary(
        views,
        as_of=corpus_as_of(session),
        performance_reports=len(stored),
        lapse_pending=len(pending),
        lapsed_value=totals.value,
        lapsed_value_floor=totals.value_floor,
        lapsed_warrants=totals.lapsed,
        issued_warrants=totals.issued,
        next_lapse_date=soonest[1],
        next_lapse_corp_name=soonest[2],
        countdown_target=countdown_target(soonest[1], cutoff=cutoff),
        now=now,
        stale_after_hours=stale_after_hours,
    )


# ---------------------------------------------------------------------------
# one event
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Detail:
    """One event, fully loaded: its view, its ① money, and its 정정 story."""

    event: Event
    exposure: EventExposure
    view: EventView
    facts: ConvertibleFacts | None
    offering: Mapping[str, Any] | None
    performance: PerformanceReport | None
    story: CorrectionStory


def resolve_event(session: Session, rcept_no: str) -> Event | None:
    """The event a filing number belongs to — **any** of its versions.

    ``rcept_no`` mutates to the newest version (N2), so a link taken from the
    board in the morning can name a superseded filing by the afternoon. Resolving
    against every stored :class:`~mijual.db.models.FilingVersion` keeps that link
    working, and the page it opens is still today's reading: the event renders
    from its current readable version, never from the one in the URL.

    **A filing number does not identify an event by itself**, and this is not a
    corner case: 840 stored ``rcept_no`` values sit under two event keys, almost
    all of them N21's pairing residue — one live event plus a
    ``superseded_by_pairing`` twin that keeps its evidence. So the renderable
    event wins (``exposable`` before ``withdrawn`` before everything else); 계양전기
    ``20260724000546`` is exactly that pair, and ordering by 접수일 alone opens the
    suppressed twin and answers 404 for a row the board is showing. Ties beyond
    that go to the newest 최초 접수일, so one URL always opens one page.
    """
    renderable_first = case(
        (Event.exposure_state == "exposable", 0),
        (Event.exposure_state == "withdrawn", 1),
        else_=2,
    )
    return session.scalars(
        select(Event)
        .join(FilingVersion, FilingVersion.event_id == Event.id)
        .where(FilingVersion.rcept_no == rcept_no)
        .order_by(renderable_first, Event.original_rcept_dt.desc(), Event.id)
        .options(joinedload(Event.corp), selectinload(Event.versions))
        .limit(1)
    ).first()


def load_detail(session: Session, event: Event, *, today: date) -> Detail:
    """Everything one event's page renders, from persisted rows only."""
    loaded = current_document(session, event)
    version = loaded[0] if loaded is not None else None
    document = loaded[2] if loaded is not None else None

    rows: list[Extraction] = []
    if version is not None:
        rows = list(
            session.scalars(
                select(Extraction).where(Extraction.filing_version_id == version.id)
            ).all()
        )
    facts = None
    if event.rights_type is RightsType.CONVERTIBLE_OVERHANG:
        from mijual.cb import event_facts

        facts = event_facts(session, event)

    exposure = exposure_of(event, version=version, rows=rows, facts=facts)
    view = event_view(
        exposure,
        facts=facts,
        corp_name_in_body=document.company_name if document is not None else None,
        today=today,
    )
    offering = None
    performance = None
    if event.rights_type is RightsType.SUBSCRIPTION_WARRANT:
        stored = session.scalar(
            select(OfferingInput).where(OfferingInput.event_id == event.id)
        )
        offering = stored.inputs if stored is not None and isinstance(stored.inputs, Mapping) else None
        performance = session.scalar(
            select(PerformanceReport)
            .where(PerformanceReport.event_id == event.id)
            .order_by(PerformanceReport.rcept_dt.desc())
            .limit(1)
        )
    return Detail(
        event=event,
        exposure=exposure,
        view=view,
        facts=facts,
        offering=offering,
        performance=performance,
        story=correction_story(
            event.versions,
            current_rcept_no=version.rcept_no if version is not None else None,
            interpretation=view.fields.get("correction_interpretation"),
        ),
    )


# ---------------------------------------------------------------------------
# one 종목 (P5.S4)
# ---------------------------------------------------------------------------
#: What a 종목 page reads and nothing more: the two 본문 countdown fields, plus
#: the two the ① money factors are cited from (할인율 rides on the 발행가 산식, and
#: 초과청약 비율 is its own field). R4 renders no other field on this surface.
STOCK_FIELDS = COUNTDOWN_FIELDS + ("issue_price_formula", "excess_subscription")

#: 집계 범위, and it is a **corpus** fact, not a preference. The ① family was
#: collected from ``--bgn 20260101`` (``python -m mijual.estimate collect``) and
#: the ② backfill from ``--bgn 20250601`` (``python -m mijual.collect``), which is
#: exactly what R4-3 fixed the coverage line to: 집계 범위 2026-01-01 ~ 오늘 (KST),
#: ① 2026-01-01부터 · ② 2025-06부터. **Outside it a figure is unstated, never 0.**
LAPSE_COVERAGE_START = date(2026, 1, 1)
CONVERTIBLE_COVERAGE_START = date(2025, 6, 1)


def stock_by_code(session: Session, corp_code: str) -> Corp | None:
    """One issuer by its DART ``corp_code`` — the stable handle a link carries."""
    return session.get(Corp, corp_code)


def _name_key(name: str | None) -> str:
    """The normalized form two 회사명 are compared in: bare, spaceless, caseless."""
    return bare_name(name).casefold()


def resolve_corp(session: Session, query: str) -> Corp | None:
    """A reader's 종목명/종목코드 → the issuer, or ``None`` — **never a guess**.

    Four tiers, tried in order, each of which either names exactly one company or
    declines:

    1. **종목코드** — all digits, ``6`` after zero-padding, matched on
       ``Corp.stock_code``. A ticker is exact or it is nothing.
    2. **회사명, verbatim** — the DART master name as printed.
    3. **회사명, normalized** — legal form, spacing and case removed
       (:func:`mijual.present.bare_name`), so ``한화솔루션(주)`` and ``한화 솔루션``
       reach 한화솔루션. Measured 2026-08-22: **0 of 614** corps share a normalized
       name, so a hit here is unique by construction of the corpus.
    4. **normalized prefix, and only when it is unique** — ``계양`` → 계양전기.
       ``삼성전`` names both 삼성전자 and 삼성전기 and therefore resolves to
       **neither**.

    Tier 3 runs before tier 4 for a reason that is not hypothetical: **13 corp
    names are a strict prefix of another corp's** (금양 / 금양그린파워, 디와이 /
    디와이디·디와이씨·디와이에이, 한창 / 한창제지 …). Typing a company's whole name
    must resolve to that company, not become ambiguous because a longer name
    exists.

    Ambiguity is a miss, not a pick: a lookup that silently opened a *different*
    company's 놓친 돈 would be the one defect class this product cannot ship. A
    miss carries no reason — the surface renders R4's locked 검색 불일치 copy, and
    the payload says only that nothing matched.

    The corpus is the universe of resolvable 종목: a :class:`~mijual.db.models.Corp`
    row exists only because the collector saw a filing from that issuer
    (``ensure_corp`` is called while creating an event), so every resolvable stock
    has at least one event today — measured 614/614 on 2026-08-22. A corp that
    ever *did* arrive without events still resolves, and lands on the honest
    "이 종목에는 … 권리가 없습니다" empty state rather than on 검색 불일치.
    """
    text = (query or "").strip()
    if not text:
        return None

    digits = text.replace("-", "")
    if digits.isdigit() and len(digits) <= 6:
        hit = session.scalars(
            select(Corp).where(Corp.stock_code == digits.zfill(6))
        ).first()
        if hit is not None:
            return hit

    exact = session.scalars(select(Corp).where(Corp.corp_name == text)).all()
    if len(exact) == 1:
        return exact[0]

    key = _name_key(text)
    if not key:
        return None
    # One narrow scan of (code, name) — the whole corp table is ~600 tiny rows and
    # the normalization has to be Python's, so that "the same company written
    # differently" means here exactly what it means in ``identity_of``.
    names = session.execute(select(Corp.corp_code, Corp.corp_name)).all()
    for match in (
        [code for code, name in names if _name_key(name) == key],
        [code for code, name in names if _name_key(name).startswith(key)],
    ):
        if len(match) == 1:
            return session.get(Corp, match[0])
    return None


def _stock_events(session: Session, corp_code: str) -> list[Event]:
    return list(
        session.scalars(
            select(Event)
            .where(Event.corp_code == corp_code)
            .options(joinedload(Event.corp), selectinload(Event.versions))
        ).all()
    )


def _rights_row(
    view: EventView,
    exposure: EventExposure,
    facts: ConvertibleFacts | None,
    offering: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """One 진행 중인 권리 panel: the event, plus its type's per-holding context.

    Richer than a board row and deliberately so — this surface, not the detail
    page, owns the N주 conversion (R3 shows per-unit only), so an ① row carries
    the **whole** :func:`mijual.present.offering_inputs` factor set: 배정비율 to its
    ten decimals, 초과청약 비율, unit_value and its floor, and ``final_price_date``
    when there is no 확정발행가 yet (in which case the money keys are absent
    entirely — the client renders the `발행가 확정 전` chip and no won amount).

    An ② row carries R3's six-value fact strip, because R4 puts the dilution
    context (오버행 % · 전환 시 주식수 · 전환가액) on the row itself. An ③ row
    carries neither: 매수예정가 is not in the exposure contract (D-15, ``P5.S6``)
    and the 2단계 dependency line is signed copy over the ``dissent_notice_procedure``
    field the payload already holds.
    """
    payload = view.payload()
    if view.rights_type == "R1" and offering is not None:
        payload["offering"] = offering_inputs(exposure, offering).payload()
    if view.rights_type == "R2":
        strip = convertible_view(facts)
        if strip is not None:
            payload["convertible"] = strip.payload()
    return payload


def _live_rights(
    events: Sequence[Event],
    views: Mapping[int, EventView],
    exposures: Mapping[int, EventExposure],
    facts: Mapping[int, ConvertibleFacts],
    offerings: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    """진행 중인 권리 — the stock's renderable events, most urgent first.

    The same three populations the board keeps apart, in one ranked list because
    R4's section is one list:

    1. **upcoming** (``days >= 0``), D-day ascending — a deadline you can still
       act on is the most urgent thing on the page;
    2. **② 진행 중** (opened, not closed), most recently opened first — live, but
       there is no deadline to miss and nothing a holder exercises (R4-4), so it
       ranks below every date still ahead. Never labelled 종료 (`ui-traps` #5);
    3. **일정 추후결정** — no date at all, so it cannot be ranked and is not
       (`ui-traps` #4), oldest filing first.

    A past ① (the right has lapsed) and a past ③ (the deadline passed) are **not
    here at all**: the ① reappears in 2026 놓친 돈 with its 소멸 계산, which is the
    only honest place for it.
    """
    upcoming: list[EventView] = []
    open_now: list[EventView] = []
    tbd: list[EventView] = []
    for event in events:
        view = views[event.id]
        if view.state != "exposable":
            continue
        countdown = view.countdown
        if countdown.date is None:
            tbd.append(view)
        elif countdown.days is not None and countdown.days >= 0:
            upcoming.append(view)
        elif view.rights_type == "R2" and countdown.is_open:
            open_now.append(view)

    upcoming.sort(key=lambda view: (view.countdown.days or 0, view.rcept_no or ""))
    open_now.sort(key=lambda view: (-(view.countdown.days or 0), view.rcept_no or ""))
    tbd.sort(key=lambda view: (view.original_rcept_dt or "", view.rcept_no or ""))

    ordered = [*upcoming, *open_now, *tbd]
    return {
        "count": len(ordered),
        "rows": [
            _rights_row(
                view,
                exposures[view.event_id],
                facts.get(view.event_id),
                offerings.get(view.event_id),
            )
            for view in ordered
        ],
    }


def _closed_on(lapse: Mapping[str, Any], report: PerformanceReport) -> date | None:
    """The day an offering's 청약 closed — what places it inside 2026's coverage.

    The 실적보고서's own 청약종료일, falling back to its 접수일 (a report is filed
    *after* the 청약 it reports, so the fallback can only be later, never earlier —
    it can drop a row out of coverage but never pull an older one in). Measured
    2026-08-22: all 32 stored ``lapse`` rows carry a 청약종료일, so the fallback is
    a guard rather than a path.
    """
    text = iso_day(lapse.get("subscription_end"))
    if text is not None:
        return date.fromisoformat(text)
    return report.rcept_dt


def _lapse_row(
    report: PerformanceReport,
    lapse: Mapping[str, Any],
    views: Mapping[int, EventView],
    exposures: Mapping[int, EventExposure],
    offerings: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    """One offering's 놓친 돈 row: the outcome, its evidence, and its factors.

    Four parts, each an existing contract shape:

    * ``lapse`` — :func:`mijual.present.lapse_result`: 발행 · 청약 · 소멸 주수 and
      소멸률 (facts), the 확정발행가, and the market-wide 소멸가치 with its floor
      (「추정」). The share counts carry the Ⅶ cell's verbatim text **only when that
      cell states exactly that number** — the summed-figure guard from ``P5.S3``
      (D4). This slice adds no citation of its own to a summed figure.
    * ``countdown`` — the 증서 매매기간, computed upstream in KST, so the row's
      "기간 지남 · D+{n}" chip is read, never computed in the browser.
    * ``warrant_trading_period`` — the field payload behind that period, which is
      the row's one ``Citation`` (a single-span 본문 quote, safe to attach).
    * ``offering`` — the per-holding factors R4 multiplies by, including the two
      ``lapse`` does not carry: 초과청약 비율 and ``final_price_date``.

    Everything after ``lapse`` is **event-derived, and therefore gated**: it
    appears only when the offering's 유상증자결정 is an *exposable* event of this
    corpus. A 실적보고서 can be linked to a flagged event (한솔테크닉스 and
    트리니티항공, corpus-wide) or to none at all, and a lapse is a fact about the
    past that the report itself attests — so the row still states its 소멸 계산,
    while the 매매기간, its quote, the link to a detail page that would 404, and
    the 본문-read factors all stay behind the gate rather than being reached
    around it. ``lapse`` alone still carries 배정비율 and 증서 1주 이론가치, so the
    N주 math survives the degraded row.
    """
    facts = report.facts if isinstance(report.facts, Mapping) else {}
    out: dict[str, Any] = {
        "rights_type": "R1",
        "lapse": lapse_result(lapse, facts=facts).payload(),
    }
    view = views.get(report.event_id) if report.event_id is not None else None
    if view is not None and view.state == "exposable":
        out["event_id"] = view.event_id
        # The offering's own filing, at the version a link should open today.
        out["rcept_no"] = view.rcept_no
        out["countdown"] = view.countdown.payload()
        period = view.fields.get("warrant_trading_period")
        if period is not None:
            out["warrant_trading_period"] = period.payload()
        stored = offerings.get(view.event_id)
        if stored is not None:
            out["offering"] = offering_inputs(exposures[view.event_id], stored).payload()
    disagreement = issuer_disagreement(facts, rcept_no=report.rcept_no) if facts else None
    if disagreement is not None:
        # The filing contradicts itself; the row says so and reconciles nothing
        # (`ui-traps` #2). The product's own total uses 발행 − 청약, and says which.
        out["issuer_disagreement"] = disagreement.payload()
    return out


def _stock_lapse(
    session: Session,
    corp: Corp,
    *,
    today: date,
    views: Mapping[int, EventView],
    exposures: Mapping[int, EventExposure],
    offerings: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    """2026년 놓친 돈 for one stock: the boundary, the total, and the rows.

    ``totals`` is Σ over **this stock's in-coverage offerings only**, derived once
    here so the section headline and its rows cannot disagree, and it is still a
    market-wide figure: no holding count reaches this server, so the client scales
    it from the per-row factors (R4's hard rule).
    """
    reports = session.scalars(
        select(PerformanceReport).where(
            PerformanceReport.corp_code == corp.corp_code,
            PerformanceReport.lapse.is_not(None),
        )
    ).all()

    covered: list[tuple[date, Mapping[str, Any], PerformanceReport]] = []
    for report in reports:
        lapse = report.lapse
        if not isinstance(lapse, Mapping):
            continue
        closed = _closed_on(lapse, report)
        if closed is None or not (LAPSE_COVERAGE_START <= closed <= today):
            continue
        covered.append((closed, lapse, report))
    # Most recent 청약 종료 first: the retrospective reads newest-first, the same
    # direction the board's own past-facing strip is ordered in.
    covered.sort(key=lambda item: (item[0], item[2].rcept_no), reverse=True)

    payload: dict[str, Any] = {
        "coverage": {
            "start": LAPSE_COVERAGE_START.isoformat(),
            "end": today.isoformat(),
            "convertible_start": CONVERTIBLE_COVERAGE_START.isoformat(),
        },
        "totals": lapse_totals([lapse for _, lapse, _ in covered]).payload(),
        "rows": [
            _lapse_row(report, lapse, views, exposures, offerings)
            for _, lapse, report in covered
        ],
    }
    pending = _pending_lapses(session, today=today, corp_code=corp.corp_code)
    if pending:
        # R4's zero state adds "…소멸 여부는 청약 종료({subscription_end}) 후
        # 집계됩니다" when this stock has an ① still ahead of its 청약. The soonest
        # one answers it; the count says how many are behind that date.
        payload["pending"] = {
            "count": len(pending),
            "subscription_end": pending[0][1].isoformat(),
        }
    return payload


def load_stock(session: Session, corp: Corp, *, today: date) -> dict[str, Any]:
    """One 종목's whole page: identity, 진행 중인 권리, and 2026 놓친 돈.

    One load, two sections, because they are two readings of the *same* events:
    an ① whose 매매기간 is still ahead is a live right, and the same ① a month
    later is a 놓친 돈 row with a 소멸 계산 attached. Loading the issuer's events
    once — and batching versions, fields, ② facts and stored ① inputs exactly as
    the board does — is what keeps the two sections from disagreeing about which
    version of an offering they are describing.

    **No holding count reaches this function**, and none reaches the server at
    all: every money figure here is market-wide, and the N주 math is composed in
    the browser from the factors each row carries (R4's hard rule, and the reason
    the 보유량 lives in ``sessionStorage``).
    """
    events = _stock_events(session, corp.corp_code)
    versions = current_versions(session, events)
    rows = _field_rows(session, [v.id for v in versions.values()], STOCK_FIELDS)
    facts = _detail_facts(session, events)
    offerings = _offering_inputs(session, events)

    exposures: dict[int, EventExposure] = {}
    views: dict[int, EventView] = {}
    for event in events:
        version = versions.get(event.id)
        exposure = exposure_of(
            event,
            version=version,
            rows=rows.get(version.id, []) if version is not None else [],
            facts=facts.get(event.id),
        )
        exposures[event.id] = exposure
        views[event.id] = event_view(exposure, facts=facts.get(event.id), today=today)

    return {
        "stock": {
            "corp_code": corp.corp_code,
            "corp_name": corp.corp_name,
            "stock_code": corp.stock_code,
        },
        "reference": today.isoformat(),
        "rights": _live_rights(events, views, exposures, facts, offerings),
        "lapse": _stock_lapse(
            session,
            corp,
            today=today,
            views=views,
            exposures=exposures,
            offerings=offerings,
        ),
    }
