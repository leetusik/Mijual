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
from mijual.gates.withdrawal import detect_withdrawal
from mijual.present import (
    RANKED,
    TBD,
    BoardRow,
    BoardSummary,
    CorrectionStory,
    EventView,
    bare_name,
    board_bucket,
    board_offering,
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
    "COMFORTABLE_DDAY",
    "CONVERTIBLE_COVERAGE_START",
    "COUNTDOWN_FIELDS",
    "DEFAULT_CUTOFF_TIME",
    "LAPSE_COVERAGE_START",
    "SAMPLE_FALLBACK",
    "STOCK_FIELDS",
    "Detail",
    "HoldingEntry",
    "corpus_as_of",
    "countdown_target",
    "event_payload",
    "find_corps",
    "load_board",
    "load_corp_events",
    "load_detail",
    "load_portfolio",
    "load_sample_composition",
    "load_start_cards",
    "load_stock",
    "load_summary",
    "resolve_corp",
    "resolve_event",
    "rights_of",
    "stock_by_code",
    "suggest_corps",
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

    An exposable event on none of the three — a past ① or ③ — is on no list, and
    :func:`~mijual.present.summary.board_bucket` is where that is decided *once*,
    for the rows here and for ``counts`` in
    :func:`~mijual.present.summary.board_summary` alike. The two used to decide
    it separately, and the tabs counted 38 events the board renders nowhere.

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
        bucket = board_bucket(view)
        if bucket is None:
            continue
        row = board_row(view, offering=offering)
        if bucket == TBD:
            tbd.append(row)
        elif bucket == RANKED:
            ranked.append(row)
        else:
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
    # 동시 마감 (R9 §6): how many offerings share that earliest 청약 마감. The list
    # is ordered by (마감일, 접수번호), so the head's date is the earliest and the
    # count is simply how many entries carry it. The 소멸주의보 strip names the
    # company when it is one and says 「N개 종목」 when it is not — the screen must
    # not have to guess, and the board's own first row would otherwise look like
    # a contradiction (three offerings tie on 2026-09-04 today).
    tie_count = sum(1 for _, end, _ in pending if end == soonest[1]) if pending else None

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
        next_lapse_tie_count=tie_count,
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


def event_payload(session: Session, detail: Detail) -> dict[str, Any]:
    """One event's whole **verification contract**, as JSON. One assembly, two callers.

    ``GET /events/{rcept_no}`` serves this and ``mijual.agent``'s ``get_event``
    tool returns it (`P6.S2`), which is the point of it living here rather than in
    the router: the agent may quote nothing the detail page would not show, and
    two assemblies of "one event" would eventually differ by a key — the exact
    failure mode :func:`_load_views` exists to prevent one level down.

    Composition only; every value arrives from :mod:`mijual.present`, and the two
    per-state rules are the contract's:

    * **철회 replaces the body** — "no fields, no countdown, no old dates" (R3).
      The exposure contract already empties the fields and the countdown; the
      money block, the ② fact strip and the 정정 teaser would put the old card back
      one key at a time, so a withdrawn event gets its notice and its evidence and
      nothing else. R6 §거절 needs exactly that evidence: 철회 is a *verified state
      fact* and carries its own 근거 칩.
    * everything else gets the 정정 teaser, ①'s money and ②'s fact strip.
    """
    payload = detail.view.payload()

    if detail.view.state == "withdrawn":
        evidence = _withdrawal(session, detail)
        if evidence:
            payload["withdrawal"] = evidence
        return payload

    story = detail.story
    payload["corrections"] = {
        "corrected": story.corrected,
        "versions": len(story.versions),
    }
    # The 정정 strip's teaser: the summary and the schedule sentence, verbatim.
    # The rail itself is one more request away — it is a separate view.
    for key in ("summary", "schedule_impact"):
        value = getattr(story, key)
        if value is not None:
            payload["corrections"][key] = value

    if detail.view.rights_type == "R1":
        _add_offering(payload, detail)
    if detail.view.rights_type == "R2":
        strip = convertible_view(detail.facts)
        if strip is not None:
            payload["convertible"] = strip.payload()
    return payload


def _add_offering(payload: dict[str, Any], detail: Detail) -> None:
    """①'s money: the 환산 블록's inputs, and the 청약 결과 once it exists.

    Both come from what the worker precomputed — the request path cannot build
    either (:mod:`mijual.estimate` imports the three spending modules). An
    offering with no stored inputs simply has no ``offering`` key: absent, never
    an empty object, and never a zero.
    """
    if detail.offering is not None:
        payload["offering"] = offering_inputs(detail.exposure, detail.offering).payload()
    report = detail.performance
    if report is None:
        return
    facts = report.facts if isinstance(report.facts, Mapping) else {}
    if isinstance(report.lapse, Mapping):
        payload["lapse_result"] = lapse_result(report.lapse, facts=facts).payload()
    # 발행사 기재 불일치: two readings, both cited, no verdict. It exists only
    # when the filing genuinely disagrees with itself.
    disagreement = issuer_disagreement(facts, rcept_no=report.rcept_no) if facts else None
    if disagreement is not None:
        payload["issuer_disagreement"] = disagreement.payload()


def _withdrawal(session: Session, detail: Detail) -> dict[str, Any]:
    """The 철회 evidence: the 정정사항 row that retracted the decision.

    R3's 철회 page is the locked notice plus *one sentence naming the evidence and
    a Citation with the withdrawal quote* — so the payload carries the row's own
    words (항목 · 정정 전 → 정정 후) and the span they were read at, and the
    surface writes the sentence. ``notice_ko`` is already on the view.

    Re-detected on the request rather than parsed out of the stored operator note:
    the note is one prose line for a person, and a Citation needs the parts. This
    reads stored bytes only — no OpenDART request, no model call — and a 철회 page
    is 11 events in the whole corpus.
    """
    found = detect_withdrawal(session, detail.event)
    if found is None:
        return {}
    out: dict[str, Any] = {
        "rcept_no": found.rcept_no,
        "item": found.item,
        "before": found.before,
        "after": found.after,
    }
    if found.span is not None:
        out["span"] = list(found.span)
    return out


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
    company's 놓친 돈 would be the one defect class this product cannot ship. That
    rule is about **this** function — what the system does with a query nobody
    confirmed — and P7 left it exactly as it was. A reader who *chooses* 계양전기
    out of the suggestion list (:func:`suggest_corps`, ``GET /stocks/suggest``) is
    not being guessed at: the choice travels as a ``corp_code`` to
    :func:`stock_by_code` and never comes back through this resolver. A miss still
    carries no reason — the surface renders R4's locked 검색 불일치 copy, and the
    payload says only that nothing matched.

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


def _corps_in_order(session: Session, corp_codes: Sequence[str]) -> list[Corp]:
    """The ``Corp`` rows for a decided order of codes, in one query and that order."""
    if not corp_codes:
        return []
    found = {
        corp.corp_code: corp
        for corp in session.scalars(select(Corp).where(Corp.corp_code.in_(tuple(corp_codes))))
    }
    return [found[code] for code in corp_codes if code in found]


def suggest_corps(session: Session, query: str, *, limit: int = 8) -> list[Corp]:
    """What a half-typed 종목 could be — the list a reader **chooses** from.

    ``GET /stocks/suggest``'s reading (`P7.S4`, operator item 2). It looks like the
    opposite of :func:`resolve_corp`'s unique-or-decline rule and is not: that rule
    exists so that *the system* never silently opens a different company's 놓친 돈,
    and a reader picking 계양전기 out of a list is the opposite of a silent guess.
    What keeps it safe is the handle — every candidate carries its ``corp_code``,
    the surface navigates to ``/stocks/{corp_code}``, and nothing a reader chose is
    ever re-resolved from its name.

    Tiers, **unioned** rather than first-wins — unlike :func:`find_corps`, which
    answers R6's 「이벤트 목록/단건」 contract and stops at the first tier that
    matches:

    1. **All digits** → ``stock_code`` **prefix**, plus the zero-padded exact
       (``12200`` → ``012200``), so a ticker :func:`resolve_corp` would resolve is
       always in the list. Ordered by 종목코드.
    2. **Otherwise** → normalized name (:func:`_name_key`), **prefix first and
       substring after**, each group alphabetical **by the normalized name**, so a
       legal form or a space cannot jump a row to the top of it. Prefix before
       substring because 삼성전 means 삼성전자/삼성전기 before it means anything that merely contains
       those syllables — and because every tier :func:`resolve_corp` can hit is a
       prefix hit here, so the row a bare submit would land on is at the **top** of
       the list rather than lost in the middle of it.

    ``limit`` caps the list: a two-character query matches dozens, and a listbox a
    reader has to scroll is not a shortlist. Nothing is filtered out of the corpus —
    an issuer with no events still belongs here, because it has an honest "권리가
    없습니다" page to land on. One narrow scan of ``(corp_code, corp_name,
    stock_code)``, the same reading :func:`resolve_corp` does over the same ~614
    rows, and the normalization is Python's for the same reason it is there.
    """
    text = (query or "").strip()
    if not text:
        return []

    rows = session.execute(select(Corp.corp_code, Corp.corp_name, Corp.stock_code)).all()

    digits = text.replace("-", "")
    if digits.isdigit():
        padded = digits.zfill(6) if len(digits) <= 6 else None
        hits = sorted(
            (
                row
                for row in rows
                if row.stock_code
                and (row.stock_code.startswith(digits) or row.stock_code == padded)
            ),
            key=lambda row: (row.stock_code or "", row.corp_name or ""),
        )
        return _corps_in_order(session, [row.corp_code for row in hits[:limit]])

    key = _name_key(text)
    if not key:
        return []
    keyed = sorted(
        ((_name_key(name), code) for code, name, _ in rows),
        key=lambda item: (item[0], item[1]),
    )
    ordered = [code for name_key, code in keyed if name_key.startswith(key)]
    ordered += [
        code for name_key, code in keyed if key in name_key and not name_key.startswith(key)
    ]
    return _corps_in_order(session, ordered[:limit])


def find_corps(session: Session, query: str, *, limit: int = 5) -> list[Corp]:
    """Issuers a search text may mean — **several are legitimate**, unlike
    :func:`resolve_corp`.

    R4's resolution is *unique-or-decline* because opening the wrong company's
    놓친 돈 page is the one defect class this product cannot ship. R6's
    ``search_events`` tool is a different contract — 「이벤트 목록/단건」 — so
    ambiguity here is a **list**, not a miss: the agent may say "두 곳이 있습니다"
    and name both, which is the honest answer 조회 has no surface for
    (`P6` phase note, Finding 15).

    Same normalization and the same tier order as :func:`resolve_corp`, so the two
    can never disagree about *what matches*, only about how many matches are
    allowed: 종목코드 → 회사명 verbatim → normalized → normalized prefix →
    normalized substring. The **first tier that matches wins** (a company whose
    whole name was typed is that company, even though 13 corp names are a strict
    prefix of another's), results are ordered by name for a stable answer, and
    ``limit`` caps the list because a two-character query matches dozens.
    """
    text = (query or "").strip()
    if not text:
        return []

    digits = text.replace("-", "")
    if digits.isdigit() and len(digits) <= 6:
        hit = session.scalars(select(Corp).where(Corp.stock_code == digits.zfill(6))).first()
        if hit is not None:
            return [hit]

    key = _name_key(text)
    if not key:
        return []
    names = session.execute(select(Corp.corp_code, Corp.corp_name)).all()
    for match in (
        [code for code, name in names if (name or "") == text],
        [code for code, name in names if _name_key(name) == key],
        [code for code, name in names if _name_key(name).startswith(key)],
        [code for code, name in names if key in _name_key(name)],
    ):
        if match:
            found = list(
                session.scalars(select(Corp).where(Corp.corp_code.in_(tuple(match)))).all()
            )
            found.sort(key=lambda corp: (corp.corp_name or "", corp.corp_code))
            return found[:limit]
    return []


def _events_for_corps(session: Session, corp_codes: Sequence[str]) -> list[Event]:
    """Every event of a set of issuers, in one query. Shared by 조회 and 포트폴리오."""
    if not corp_codes:
        return []
    return list(
        session.scalars(
            select(Event)
            .where(Event.corp_code.in_(tuple(dict.fromkeys(corp_codes))))
            .options(joinedload(Event.corp), selectinload(Event.versions))
        ).all()
    )


def _stock_events(session: Session, corp_code: str) -> list[Event]:
    return _events_for_corps(session, [corp_code])


@dataclass(frozen=True)
class _Loaded:
    """One batched reading of a set of events — exposures, views and their extras."""

    exposures: dict[int, EventExposure]
    views: dict[int, EventView]
    facts: dict[int, ConvertibleFacts]
    offerings: dict[int, Mapping[str, Any]]


def _load_views(session: Session, events: Sequence[Event], *, today: date) -> _Loaded:
    """Batch the four per-event reads a rights surface needs, and derive once.

    Shared by 내 종목 조회 and 내 포트폴리오 on purpose: a portfolio is N issuers'
    rights, so if it loaded or derived them its own way the two surfaces would
    eventually describe the same offering differently — the one thing R5 states
    as a prohibition ("내 종목 조회와 수치 불일치 금지 — 같은 contract 소스").
    """
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
    return _Loaded(exposures=exposures, views=views, facts=facts, offerings=offerings)


def load_corp_events(
    session: Session, corp_codes: Sequence[str], *, today: date
) -> list[EventView]:
    """Every **exposable** event of a set of issuers, as views. `P6.S2`'s search.

    The listing behind ``search_events``: batched exactly like 조회 and 포트폴리오
    (:func:`_load_views`), so a search result is the same reading of an event the
    board and the detail page give — and gated the same way twice over, by the
    persisted verdict *and* by the derived contract, because a gate run that has
    not landed yet must not surface a row (:func:`load_board`'s rule).

    A non-exposable event is not a search result (Finding 15): 철회·suppressed·
    flagged events are absent here, which is what keeps 「게이트 실패 데이터로 답변」
    structurally impossible on this path. A withdrawn event is still *reachable*
    by filing number through :func:`resolve_event` — that is how the agent tells a
    reader 「이 유상증자는 철회되었습니다」 with its evidence instead of nothing.

    Unlike :func:`load_stock`'s 진행 중인 권리 this keeps the **past** ones too: a
    lapsed ① is the subject of a 놓친 돈 question, and a search that could not find
    it would answer 「찾지 못했습니다」 about an event the product renders.
    """
    events = [
        event
        for event in _events_for_corps(session, corp_codes)
        if event.exposure_state == "exposable"
    ]
    loaded = _load_views(session, events, today=today)
    return [
        view
        for view in (loaded.views[event.id] for event in events)
        if view.state == "exposable"
    ]


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
    loaded = _load_views(session, events, today=today)

    return {
        "stock": {
            "corp_code": corp.corp_code,
            "corp_name": corp.corp_name,
            "stock_code": corp.stock_code,
        },
        "reference": today.isoformat(),
        "rights": _live_rights(
            events, loaded.views, loaded.exposures, loaded.facts, loaded.offerings
        ),
        "lapse": _stock_lapse(
            session,
            corp,
            today=today,
            views=loaded.views,
            exposures=loaded.exposures,
            offerings=loaded.offerings,
        ),
    }


# ---------------------------------------------------------------------------
# 내 포트폴리오 (P5.S8)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HoldingEntry:
    """One line of a portfolio: an issuer and a share count.

    The same shape whether it came from the reader's own ``holding`` rows or from
    the fixed sample composition, which is what lets both go through one
    composition function and therefore produce one set of numbers.
    """

    corp_code: str
    shares: int
    #: The ``holding.id`` the 수정·삭제 actions address. ``None`` in sample mode —
    #: a sample holding is the browser's, and the server stores none.
    holding_id: int | None = None


def _lapse_by_event(
    session: Session, events: Sequence[Event], *, today: date
) -> dict[int, tuple[PerformanceReport, Mapping[str, Any]]]:
    """Each ① event's 소멸 outcome, when one has been filed and parsed.

    Newest 실적보고서 per event, and **the same coverage membership 내 종목 조회
    applies** (:func:`_closed_on` inside ``2026-01-01 … today``): a 소멸 row that
    the breakdown would not count must not appear with a figure in the portfolio
    either, or the two surfaces would disagree about what happened to the same
    offering. Outside the boundary the row keeps its 기간 지남 chip and states no
    money — unstated, never zero (R4-3).

    A report whose ``event_id`` is ``NULL`` (its 유상증자결정 is not in the corpus,
    or hangs off a flagged event) has **no row here at all**: 지나간 마감 is a list
    of deadlines, and a report with no event has no 매매기간 to have passed. The
    figure still reaches the reader through 조회's breakdown, which is keyed on
    the issuer rather than on an event.
    """
    ids = [
        event.id
        for event in events
        if event.rights_type is RightsType.SUBSCRIPTION_WARRANT
    ]
    if not ids:
        return {}
    found: dict[int, tuple[PerformanceReport, Mapping[str, Any]]] = {}
    for report in session.scalars(
        select(PerformanceReport).where(
            PerformanceReport.event_id.in_(ids), PerformanceReport.lapse.is_not(None)
        )
    ).all():
        lapse = report.lapse
        if not isinstance(lapse, Mapping) or report.event_id is None:
            continue
        closed = _closed_on(lapse, report)
        if closed is None or not (LAPSE_COVERAGE_START <= closed <= today):
            continue
        seen = found.get(report.event_id)
        if seen is None or (report.rcept_no or "") > (seen[0].rcept_no or ""):
            found[report.event_id] = (report, lapse)
    return found


def _portfolio_row(
    entry: HoldingEntry,
    view: EventView,
    loaded: _Loaded,
    lapse: tuple[PerformanceReport, Mapping[str, Any]] | None,
    claims: frozenset[str] | None,
) -> dict[str, Any]:
    """One D-day row: the event exactly as 조회 serves it, plus this holding.

    The event half is :func:`_rights_row` — the *same* function 내 종목 조회 uses,
    not a portfolio-flavoured copy of it — so an ① carries the full factor set
    (배정비율 to ten decimals · 초과청약 비율 · 증서 1주 이론가치 + 하한 ·
    ``final_price_date``), an ② carries R3's six-value dilution strip and neither
    ② nor ③ can carry a won amount, because :class:`mijual.present.OfferingInputs`
    has no field for one on a type that has none.

    What this adds is ``shares`` — a **stored count, not a derived number** — and,
    on a past ① whose 실적보고서 has landed, the offering's ``lapse``. The row
    still serves **factors, not products**: the 500주 기준 「추정」 amount R5 draws
    is ⌊shares × 배정비율⌋ × 증서 1주 이론가치, composed in the browser by the same
    client code 내 종목 조회 uses. Pre-multiplying here would put a second
    multiplication site in the product for one number, which is exactly the
    "두 divergent readouts for the same number" R4 names as the failure mode.
    """
    payload = _rights_row(
        view,
        loaded.exposures[view.event_id],
        loaded.facts.get(view.event_id),
        loaded.offerings.get(view.event_id),
    )
    payload["shares"] = entry.shares
    if entry.holding_id is not None:
        payload["holding_id"] = entry.holding_id
    if lapse is not None:
        report, mapping = lapse
        facts = report.facts if isinstance(report.facts, Mapping) else {}
        payload["lapse"] = lapse_result(mapping, facts=facts).payload()
        if claims is not None:
            # 챙긴 돈 (R5-8): the reader's own assertion about their own row.
            # Absent — never ``false`` — when nobody is logged in, because a
            # sample or anonymous reader keeps this mark in ``localStorage`` and
            # a server-side ``false`` would be the product asserting something
            # about a person it has no account for.
            payload["claimed"] = report.rcept_no in claims
    return payload


def load_portfolio(
    session: Session,
    entries: Sequence[HoldingEntry],
    *,
    today: date,
    claims: frozenset[str] | None = None,
) -> dict[str, Any]:
    """내 포트폴리오 홈: the holdings, 다가오는 마감 and 지나간 마감.

    **Two sections, because R5 signs two** — and the placement rule inside them is
    forced by the hard rules rather than chosen:

    * **다가오는 마감**, D-day ascending, is every deadline still ahead. After
      them, unranked by date, come the two populations that have no future
      deadline but are not over: an ② whose 전환청구 has **opened and not closed**
      (most recently opened first — 진행 중, *never* 종료, `ui-traps` #5, and it
      ranks below every date still ahead because there is nothing to exercise
      against a clock, R4-4), and 일정 추후결정, which cannot be ranked at all and
      carries no date anywhere near it (`ui-traps` #4).
    * **지나간 마감**, most recent first, is every anchor already behind the
      reference day — a passed ① 매매 마감, a passed ③ 통지 마감, and an ② whose
      window has fully closed. An *open* ② is never here: filing it under
      "지나간" is the 종료 label R5 forbids, spelled as a section heading.

    ``reference`` is the KST day every D-day was computed against — R5's
    "기준 YYYY-MM-DD (KST)" line, served rather than computed in the browser.

    ``claims`` is the set of 실적보고서 ``rcept_no`` this reader has marked
    챙겼습니다; pass ``None`` for the anonymous sample, which carries no
    ``claimed`` key at all. **No total is served anywhere in this payload**: R5-8
    requires the 챙긴 돈 mark to stay out of every 집계·통계, and the surest way for
    a user claim never to reach an aggregate is for the surface to have none.
    """
    events = _events_for_corps(session, [entry.corp_code for entry in entries])
    loaded = _load_views(session, events, today=today)
    lapses = _lapse_by_event(session, events, today=today)

    by_corp: dict[str, list[Event]] = {}
    for event in events:
        by_corp.setdefault(event.corp_code, []).append(event)
    codes = tuple(dict.fromkeys(entry.corp_code for entry in entries))
    corps = (
        {
            corp.corp_code: corp
            for corp in session.scalars(select(Corp).where(Corp.corp_code.in_(codes))).all()
        }
        if codes
        else {}
    )

    holdings: list[dict[str, Any]] = []
    upcoming: list[tuple[int, str, dict[str, Any]]] = []
    open_now: list[tuple[int, str, dict[str, Any]]] = []
    tbd: list[tuple[str, str, dict[str, Any]]] = []
    past: list[tuple[int, str, dict[str, Any]]] = []

    for entry in entries:
        live: list[dict[str, Any]] = []
        for event in by_corp.get(entry.corp_code, []):
            view = loaded.views[event.id]
            if view.state != "exposable":
                continue
            row = _portfolio_row(
                entry, view, loaded, lapses.get(event.id), claims
            )
            countdown = view.countdown
            key = view.rcept_no or ""
            if countdown.date is None:
                tbd.append((view.original_rcept_dt or "", key, row))
                live.append(row)
            elif countdown.days is not None and countdown.days >= 0:
                upcoming.append((countdown.days, key, row))
                live.append(row)
            elif view.rights_type == "R2" and countdown.is_open:
                open_now.append((-(countdown.days or 0), key, row))
                live.append(row)
            else:
                past.append((-(countdown.days or 0), key, row))

        corp = corps.get(entry.corp_code)
        holding: dict[str, Any] = {
            "corp_code": entry.corp_code,
            "shares": entry.shares,
            "rights": _rights_summary(live),
        }
        if entry.holding_id is not None:
            holding["id"] = entry.holding_id
        if corp is not None:
            # A corp the corpus no longer knows keeps its holding and loses its
            # name — an absent key, never a null or an invented placeholder.
            holding["corp_name"] = corp.corp_name
            if corp.stock_code:
                holding["stock_code"] = corp.stock_code
        holdings.append(holding)

    upcoming.sort(key=lambda item: item[:2])
    open_now.sort(key=lambda item: item[:2])
    tbd.sort(key=lambda item: item[:2])
    past.sort(key=lambda item: item[:2])

    return {
        "reference": today.isoformat(),
        "holdings": holdings,
        "upcoming": [row for *_, row in (*upcoming, *open_now, *tbd)],
        "past": [row for *_, row in past],
    }


def _live_rank(row: Mapping[str, Any]) -> tuple[int, int, str]:
    """The 다가오는 section's order, as a sort key: dated → open ② → 추후결정."""
    countdown = row["countdown"]
    days = countdown.get("days")
    if countdown.get("date") is None:
        return (2, 0, row.get("rcept_no") or "")
    if days is not None and days >= 0:
        return (0, days, row.get("rcept_no") or "")
    return (1, -(days or 0), row.get("rcept_no") or "")


def _rights_summary(live: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """R5's 진행 중인 권리 요약 for one holding row: how many, and the next one.

    ``next`` points at a row this same payload already carries and reuses its
    **already-serialized** countdown, so the chip on the 보유 row and the D-day row
    it summarizes cannot say two different things about one deadline. Ranked by
    :func:`_live_rank` — the same order the 다가오는 마감 section uses, because
    "the next one" must mean the row a reader sees at the top of that list.
    """
    ordered = sorted(live, key=_live_rank)
    summary: dict[str, Any] = {"count": len(ordered)}
    if ordered:
        head = ordered[0]
        summary["next"] = {
            "event_id": head["event_id"],
            "rcept_no": head["rcept_no"],
            "rights_type": head["rights_type"],
            "countdown": head["countdown"],
        }
    return summary


# ---------------------------------------------------------------------------
# the /ask start cards
# ---------------------------------------------------------------------------
#: 「가장 여유로운」 창 for the 계산 card's deadline. A card whose 마감 expires the
#: day after a reader presses it is a dead question in slower motion, and one
#: dated a year out reads like a filing nobody is waiting on.
COMFORTABLE_DDAY = (20, 60)

#: How many ranked candidates a card checks against :func:`find_corps` before it
#: gives up. Each check is one narrow scan of the ~600-row corp table, so the
#: work is bounded whatever the corpus does.
_CARD_CANDIDATES = 8


def _findable(session: Session, corp_code: str, corp_name: str | None) -> bool:
    """Would the agent's **own** search find exactly this company by this name?

    The card names a company and the reader presses it, so the sentence travels
    to ``search_events`` → :func:`find_corps` (never :func:`resolve_corp`: the
    tool's contract is a list). A name that reaches two issuers would make the
    card's own count a claim about somebody else's filings, so it is not picked —
    which is a *selection* rule, not a new resolution rule.
    """
    if not corp_name:
        return False
    found = find_corps(session, corp_name)
    return len(found) == 1 and found[0].corp_code == corp_code


def _search_card(
    session: Session, by_corp: Mapping[str, list[EventView]], *, family: str
) -> dict[str, Any] | None:
    """A company whose 검색 visibly lists **several** filings of one 권리 가족.

    Ranked so the card demonstrates 「여러 건이 정상이다」 where the corpus allows
    it: multi-hit first, then issuers whose *whole* exposable set is that family
    (so the 도구 행's 건수 and the card's own question count the same thing), then
    the largest set, then ``corp_code`` — the last only so two equal candidates
    resolve the same way on every request.
    """
    ranked: list[tuple[tuple[int, int, int, str], str, list[EventView]]] = []
    for corp_code, views in by_corp.items():
        family_views = [view for view in views if view.rights_type == family]
        if not family_views:
            continue
        if not any(board_bucket(view) is not None for view in family_views):
            # Not on the board at all: every filing of that family is history.
            continue
        filings = len({view.rcept_no for view in family_views})
        pure = len(family_views) == len(views)
        key = (0 if filings > 1 else 1, 0 if pure else 1, -filings, corp_code)
        ranked.append((key, corp_code, family_views))

    ranked.sort(key=lambda item: item[0])
    for _, corp_code, family_views in ranked[:_CARD_CANDIDATES]:
        corp_name = family_views[0].identity.corp_name
        if not _findable(session, corp_code, corp_name):
            continue
        return {
            "corp_name": corp_name,
            "corp_code": corp_code,
            "filings": len({view.rcept_no for view in family_views}),
        }
    return None


def _dday_tier(days: int) -> int:
    """0 = the comfortable window, 1 = further out, 2 = soon, 3 = about to pass."""
    low, high = COMFORTABLE_DDAY
    if low <= days <= high:
        return 0
    if days > high:
        return 1
    return 2 if days >= 7 else 3


def _calculate_card(
    session: Session,
    by_corp: Mapping[str, list[EventView]],
    offerings: Mapping[int, Mapping[str, Any]],
    *,
    avoid: str | None,
) -> dict[str, Any] | None:
    """An ① whose filing **exposes what the question asks about**, still ahead.

    The question is 「1,000주 보유 시 배정 신주는 몇 주인가요」, so the event has to
    carry a 신주배정비율 the answer can cite and a deadline that has not passed —
    otherwise the chain 검색 → 이벤트 → 계산 ends in a number about a right nobody
    can exercise. Preference order: the comfortable window, then an issuer whose
    ① is its only one (so the read cannot land on a sibling filing), then the
    latest deadline inside the window (the pick with the most headroom), then
    ``rcept_no``.
    """
    ranked: list[tuple[tuple[int, int, int, str], str, EventView]] = []
    for corp_code, views in by_corp.items():
        offers = [view for view in views if view.rights_type == "R1"]
        for view in offers:
            inputs = offerings.get(view.event_id) or {}
            days = view.countdown.days
            if inputs.get("allotment_ratio") is None or days is None or days < 0:
                continue
            if board_bucket(view) is None:
                continue
            tier = _dday_tier(days)
            key = (
                tier,
                0 if len(offers) == 1 else 1,
                days if tier == 1 else -days,
                view.rcept_no or "",
            )
            ranked.append((key, corp_code, view))

    ranked.sort(key=lambda item: item[0])
    # The two derived cards should not collapse onto one company when the corpus
    # offers another — a start screen naming the same issuer twice reads as a
    # thin corpus rather than as a product with a corpus behind it.
    pools = [[item for item in ranked if item[1] != avoid], ranked] if avoid else [ranked]
    for pool in pools:
        for _, corp_code, view in pool[:_CARD_CANDIDATES]:
            corp_name = view.identity.corp_name
            if not _findable(session, corp_code, corp_name):
                continue
            return {
                "corp_name": corp_name,
                "corp_code": corp_code,
                "rcept_no": view.rcept_no,
                "dday": view.countdown.dday,
                "days": view.countdown.days,
            }
    return None


def load_start_cards(session: Session, *, today: date) -> dict[str, Any]:
    """The companies the `/ask` start cards name, chosen **at request time**.

    R16 D11's rule is that a 공시 question carries a 회사, and `P11.S2` shipped
    those companies as fixed strings. The operator rejected exactly that at the
    P11 acceptance gate — 「when they are outdated, what happen? we should make
    them to be real time catch. not fixed.」 — because a filing ages out of the
    corpus while the sentence stays on the screen, and the first thing a reader
    presses is then a question the product can no longer answer.

    So the two company-bearing cards name whoever can answer them **today**: the
    검색 card an issuer with live 전환사채 filings, the 계산 card an ① that still
    exposes a 신주배정비율 before its deadline. Nothing here writes Korean — the
    sentence is a template in ``components/ask/copy.ts`` with a company slot, and
    a card with no candidate comes back ``null`` so that surface can fall back to
    its static sentence rather than draw an empty grid.

    Read from :func:`_board_views` — the board's own reading of the corpus — so a
    card can only name a company the board would show, gated by the persisted
    verdict *and* the derived contract like every other surface.
    """
    views: dict[str, list[EventView]] = {}
    offerings: dict[int, Mapping[str, Any]] = {}
    for view, offering in _board_views(session, today=today):
        if view.state != "exposable":
            continue
        views.setdefault(view.corp_code, []).append(view)
        if offering is not None:
            offerings[view.event_id] = offering

    search = _search_card(session, views, family="R2")
    calculate = _calculate_card(
        session, views, offerings, avoid=search["corp_code"] if search else None
    )
    return {"reference": today.isoformat(), "search_events": search, "calculate": calculate}


# ---------------------------------------------------------------------------
# 샘플 포트폴리오 — the composition, chosen at request time
# ---------------------------------------------------------------------------
#: The four states R5-4 draws the sample in, the 보유량 each card states as an
#: **example**, and the issuer R5 pinned for that slot on 2026-08-22 — kept here
#: as the slot's **fallback**, in R5-4's own order:
#:
#: ===================================  ==========  ==================
#: 상태                                  예시 보유량   R5가 고정한 발행사
#: ===================================  ==========  ==================
#: ① 발행가 확정 전 (카운트다운 진행)        500주       계양전기 · 20260724000546
#: ② 전환청구 개시                        300주       대동기어 · 20251016000315
#: ① 소멸 — 놓친 돈                       500주       한화솔루션 · 20260720000067
#: ③ 통지 마감 지남                       100주       세기상사 · 20260713000345
#: ===================================  ==========  ==================
#:
#: **The share counts never move** — they are the signed examples the banner
#: 「보유량은 예시입니다」 refers to. The issuers do: see
#: :func:`load_sample_composition`.
SAMPLE_FALLBACK = (
    ("00102618", 500),
    ("00109310", 300),
    ("00162461", 500),
    ("00133618", 100),
)

#: How many past ① candidates the 소멸 slot checks for a filed 실적보고서 before
#: it gives up. A 실적보고서 lands weeks after the 매매 마감 it reports, so the most
#: recent past ① usually has none yet and the scan has to walk back a little —
#: bounded, like :data:`_CARD_CANDIDATES`, so the work cannot grow with the corpus.
_SAMPLE_LAPSE_CANDIDATES = 24


def _sample_offering_slot(
    views: Mapping[str, list[EventView]],
    offerings: Mapping[int, Mapping[str, Any]],
    taken: frozenset[str],
) -> EventView | None:
    """Slot ① — an offering still counting down, 발행가 **확정 전** if one exists.

    That state is the whole point of the slot: 발행가 확정 전 is the moment the
    product exists for, and a fixed list stops showing it within a week (an ①
    매매기간 is about that long). The predicate is the presenter's own —
    :func:`mijual.present.board_offering`'s ``price_confirmed``, which is what the
    signed 「발행가 확정 전」 chip renders from — so this picks what the row will say
    rather than a second reading of the same inputs.

    Order: 확정 전 first, then :func:`_dday_tier`'s comfortable window (a D-0 card
    is a sample that expires while it is being read), then an issuer whose ① is
    its only one, then the latest deadline inside the tier, then ``rcept_no``.
    With no 확정 전 candidate at all the slot still fills — any upcoming ① — because
    an ① counting down is more of R5-4's state than an empty slot is.
    """
    ranked: list[tuple[tuple[int, int, int, int, str], EventView]] = []
    for corp_code, corp_views in views.items():
        if corp_code in taken:
            continue
        offers = [view for view in corp_views if view.rights_type == "R1"]
        for view in offers:
            days = view.countdown.days
            if view.countdown.date is None or days is None or days < 0:
                continue
            offering = board_offering(offerings.get(view.event_id))
            pending = offering is not None and not offering.price_confirmed
            tier = _dday_tier(days)
            ranked.append(
                (
                    (
                        0 if pending else 1,
                        tier,
                        0 if len(offers) == 1 else 1,
                        days if tier == 1 else -days,
                        view.rcept_no or "",
                    ),
                    view,
                )
            )
    ranked.sort(key=lambda item: item[0])
    return ranked[0][1] if ranked else None


def _sample_convertible_slot(
    views: Mapping[str, list[EventView]], taken: frozenset[str]
) -> EventView | None:
    """Slot ② — 전환청구 개시: the soonest one still ahead, else the newest open one.

    Both are 진행 중 and neither is 종료 (`ui-traps` #5), which is exactly why the
    fallback within the slot is *open* rather than *past*: an ② whose window has
    fully closed would put the sample's ② row in 지나간 마감, and R5-4 draws it
    among the live states.
    """
    ranked: list[tuple[tuple[int, int, str], EventView]] = []
    for corp_code, corp_views in views.items():
        if corp_code in taken:
            continue
        for view in corp_views:
            if view.rights_type != "R2":
                continue
            countdown = view.countdown
            days = countdown.days
            if countdown.date is not None and days is not None and days >= 0:
                key = (0, days, view.rcept_no or "")
            elif countdown.is_open:
                key = (1, -(days or 0), view.rcept_no or "")
            else:
                continue
            ranked.append((key, view))
    ranked.sort(key=lambda item: item[0])
    return ranked[0][1] if ranked else None


def _sample_lapsed_slot(
    session: Session,
    views: Mapping[str, list[EventView]],
    taken: frozenset[str],
    *,
    today: date,
) -> EventView | None:
    """Slot ③ — a past ① whose 실적보고서 landed **and states the 놓친 돈**.

    The slot's job is R5-4's 놓친 돈 lesson, so a row that can only say 「기간 지남」
    does not fill it: the candidate must have a :func:`_lapse_by_event` row (which
    is where the 2026 coverage boundary is applied, once, for every surface) whose
    :func:`mijual.present.lapse_result` carries a ``value``. Most recent first,
    over a bounded head of candidates.
    """
    ranked: list[tuple[tuple[int, str], EventView]] = []
    for corp_code, corp_views in views.items():
        if corp_code in taken:
            continue
        for view in corp_views:
            days = view.countdown.days
            if view.rights_type != "R1" or view.countdown.date is None:
                continue
            if days is None or days >= 0:
                continue
            ranked.append(((-days, view.rcept_no or ""), view))
    ranked.sort(key=lambda item: item[0])
    head = [view for _, view in ranked[:_SAMPLE_LAPSE_CANDIDATES]]
    if not head:
        return None

    events = list(
        session.scalars(
            select(Event).where(Event.id.in_([view.event_id for view in head]))
        ).all()
    )
    lapses = _lapse_by_event(session, events, today=today)
    for view in head:
        found = lapses.get(view.event_id)
        if found is None:
            continue
        report, mapping = found
        facts = report.facts if isinstance(report.facts, Mapping) else {}
        if lapse_result(mapping, facts=facts).value is None:
            continue
        return view
    return None


def _sample_appraisal_slot(
    views: Mapping[str, list[EventView]], taken: frozenset[str]
) -> EventView | None:
    """Slot ④ — a ③ whose 통지 마감 has passed, most recent first."""
    ranked: list[tuple[tuple[int, str], EventView]] = []
    for corp_code, corp_views in views.items():
        if corp_code in taken:
            continue
        for view in corp_views:
            days = view.countdown.days
            if view.rights_type != "R3" or view.countdown.date is None:
                continue
            if days is None or days >= 0:
                continue
            ranked.append(((-days, view.rcept_no or ""), view))
    ranked.sort(key=lambda item: item[0])
    return ranked[0][1] if ranked else None


def load_sample_composition(session: Session, *, today: date) -> list[HoldingEntry]:
    """샘플 포트폴리오's four issuers, chosen **at request time** — one per state.

    R5-4 asks the sample to show the surface in its four states at once (① 발행가
    확정 전 · ② 전환청구 개시 · ① 소멸 · ③ 통지 마감 지남) and pinned four issuers
    for them. A pinned list cannot hold those states: an ① 매매기간 lasts about a
    week, so 「구성 (고정)」 was measured wrong within days — on 2026-09-02 the
    pinned sample had **no ① counting down at all** and three of its four rows had
    fallen into 지나간 마감. The `/ask` start cards had the identical problem and
    the operator settled it at the P11 gate — 「real time catch. not fixed.」 — so
    this is :func:`load_start_cards`'s rule applied to the other fixed surface
    (operator, 2026-09-02; see the phase notebook's `## Decisions`).

    **What is fixed and what is not.** The four *states* and the four *example
    보유량* (500 · 300 · 500 · 100) are R5-4's and never move; the *issuers* are
    whoever is in that state today. The banner 「종목·공시·마감은 실제, 계정·보유량은
    예시입니다」 stays literally true, and more so than before.

    Read from :func:`_board_views` — the board's own reading of the corpus, gated
    by the persisted verdict *and* the derived contract — so the sample can only
    name a company the board itself would show. An issuer that qualifies for two
    slots takes the first and the next slot skips it, so the four rows are four
    companies. A slot with no candidate falls back to :data:`SAMPLE_FALLBACK`'s
    entry for that slot (dropped only if that issuer is already in the list, which
    is the one way this returns fewer than four rows).

    **Cost: one whole-board read per request** — the same read the board and
    ``/ask/start-cards`` already pay, plus one bounded lookup of 실적보고서 rows for
    the 소멸 slot. There is deliberately **no cache**: a cached composition is a
    fixed list with an expiry date, which is the thing this replaces.
    """
    views: dict[str, list[EventView]] = {}
    offerings: dict[int, Mapping[str, Any]] = {}
    for view, offering in _board_views(session, today=today):
        if view.state != "exposable":
            continue
        views.setdefault(view.corp_code, []).append(view)
        if offering is not None:
            offerings[view.event_id] = offering

    slots = (
        lambda taken: _sample_offering_slot(views, offerings, taken),
        lambda taken: _sample_convertible_slot(views, taken),
        lambda taken: _sample_lapsed_slot(session, views, taken, today=today),
        lambda taken: _sample_appraisal_slot(views, taken),
    )

    entries: list[HoldingEntry] = []
    taken: set[str] = set()
    for (fallback_code, shares), pick in zip(SAMPLE_FALLBACK, slots):
        view = pick(frozenset(taken))
        corp_code = view.corp_code if view is not None else fallback_code
        if corp_code in taken:
            continue
        taken.add(corp_code)
        entries.append(HoldingEntry(corp_code=corp_code, shares=shares))
    return entries
