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
    board_row,
    board_summary,
    correction_story,
    event_view,
    lapse_totals,
)

__all__ = [
    "COUNTDOWN_FIELDS",
    "DEFAULT_CUTOFF_TIME",
    "Detail",
    "corpus_as_of",
    "countdown_target",
    "load_board",
    "load_detail",
    "load_summary",
    "resolve_event",
    "rights_of",
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


def _countdown_rows(
    session: Session, version_ids: Sequence[int]
) -> dict[int, list[Extraction]]:
    """The governing field of each version — one query, gate verdicts included."""
    if not version_ids:
        return {}
    rows: dict[int, list[Extraction]] = {}
    for row in session.scalars(
        select(Extraction).where(
            Extraction.filing_version_id.in_(version_ids),
            Extraction.field_key.in_(COUNTDOWN_FIELDS),
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
    rows = _countdown_rows(session, [v.id for v in versions.values()])
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
def _pending_lapses(session: Session, *, today: date) -> list[tuple[str | None, date, str | None]]:
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
