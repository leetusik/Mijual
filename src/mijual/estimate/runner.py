"""Collect the 청약 결과: census → 본문 → parse → link (→ adopt) → persist.

Request discipline is the same one ``P2.S2`` made structural (N25): the client
carries a ceiling, a budget-exhausted run keeps everything it already collected
and says ``BUDGET EXHAUSTED``, and re-running is nearly free — a 실적보고서 whose
bytes are unchanged is a no-op.

The ordering is deliberate. Linking happens **before** adoption so the corpus is
tried first and only a genuinely absent 유상증자결정 costs the extra 3–4 requests;
adoption then re-links, so an adopted offering is indistinguishable downstream
from a natively collected one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy import select

from mijual.bodydoc import BodyDocument
from mijual.bodydoc.backfill import load_document
from mijual.dart import CacheMiss, DartClient, DartError, RequestBudgetExceeded
from mijual.db.models import Event, PerformanceReport, RightsType, parse_dart_date, sha1_hex
from mijual.db.session import session_scope
from mijual.estimate.adopt import adopt_offering
from mijual.estimate.perf import PERF_REPORT_PREFIX, PerformanceFacts, census, parse_performance
from mijual.extract.runner import readable_versions
from mijual.gates.context import version_context

__all__ = ["CollectionReport", "collect_performance"]


@dataclass
class CollectionReport:
    """What one collection run saw, fetched, linked and adopted."""

    scanned: int = 0
    reports_in_window: int = 0
    candidates: int = 0
    fetched: int = 0
    stored: int = 0
    parsed: int = 0
    no_warrant_table: int = 0
    linked: int = 0
    adopted: int = 0
    backstopped: int = 0
    unlinked: int = 0
    errors: int = 0
    requests: int = 0
    budget_exhausted: bool = False
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"census     : {self.scanned:,} 발행공시 row(s) → "
            f"{self.reports_in_window:,} 증권발행실적보고서, {self.candidates} equity candidate(s)",
            f"documents  : {self.fetched} fetched, {self.stored} stored, "
            f"{self.parsed} with a 신주인수권증서 table, {self.no_warrant_table} without, "
            f"{self.errors} error(s)",
            f"linking    : {self.linked} bound to a collected ① event, "
            f"{self.adopted} 유상증자결정 adopted, {self.backstopped} found by the per-event backstop, {self.unlinked} unlinked",
            f"requests   : {self.requests} live OpenDART request(s)"
            + (" — BUDGET EXHAUSTED" if self.budget_exhausted else ""),
        ]
        lines.extend(f"  ! {note}" for note in self.notes)
        return "\n".join(lines)


def _event_windows(session, event: Event) -> dict[str, dict[str, date]]:
    """One event's 본문 ``11. 청약예정일``, per 대상자 — the link key."""
    versions = readable_versions(event)
    if not versions:
        return {}
    blob, _ = load_document(session, None, versions[-1], fetch=False)
    if blob is None:
        return {}
    try:
        doc = BodyDocument.from_bytes(blob, rcept_no=versions[-1].rcept_no)
    except Exception:  # noqa: BLE001 — a corrupt snapshot must not stop a run
        return {}
    return version_context(session, event, versions[-1], doc).subscription_dates


def _report_window(facts: PerformanceFacts) -> tuple[date | None, date | None]:
    """The 실적보고서's own 구주주 청약 window (its 일반공모 row is a later one)."""
    for row in facts.schedule:
        if "일반공모" in row.group or "우리사주" in row.group:
            continue
        begin = row.begin.value if row.begin else None
        end = row.end.value if row.end else None
        if isinstance(begin, date):
            return (begin, end if isinstance(end, date) else None)
    return (None, None)


def _link(session, corp_code: str, facts: PerformanceFacts) -> tuple[Event | None, str, str]:
    """Bind a 실적보고서 to an ① event **by its own 청약일정**, not by corp alone.

    A corp can run two offerings in one year, and the whole estimate hangs on
    attaching the right 확정발행가 and 할인율 to the right 실권 count. So the link
    is an equality between two independently filed schedules — the report's
    ``1. 청약 및 납입일정`` and the 주요사항보고서's ``11. 청약예정일`` — and a corp
    with exactly one candidate event falls back to ``corp_only``, labelled.
    """
    events = [
        e
        for e in session.scalars(
            select(Event).where(
                Event.corp_code == corp_code,
                Event.rights_type == RightsType.SUBSCRIPTION_WARRANT,
                Event.suppressed_reason.is_(None),
            )
        ).all()
    ]
    if not events:
        return (None, "unlinked", "corp has no unsuppressed ① event")
    begin, end = _report_window(facts)
    for event in events:
        windows = _event_windows(session, event)
        for group, window in windows.items():
            if "일반공모" in group:
                continue
            if window.get("start") == begin and (end is None or window.get("end") == end):
                return (event, "schedule_match", f"본문 11. {group} {begin}~{end}")
    # The fallback still has to respect time: a corp's *only* ① event may be a
    # later offering than the one this report closes (트리니티항공's single event
    # is dated 2026-06-22 against a 2026-03-19 report), and binding those would
    # attach the wrong 확정발행가 and the wrong 할인율 to a real 실권 count.
    plausible = [
        e
        for e in events
        if begin is not None and e.original_rcept_dt and e.original_rcept_dt <= begin
    ]
    if len(plausible) == 1:
        return (
            plausible[0],
            "corp_only",
            "corp has exactly one ① event predating the 청약; schedules did not match",
        )
    return (None, "unlinked", f"{len(events)} ① events for this corp, no schedule match")


def collect_performance(
    client: DartClient,
    session_factory,
    *,
    bgn_de: str,
    end_de: str,
    markets: tuple[str, ...] = ("Y", "K"),
    max_documents: int | None = None,
    adopt: bool = True,
    log=None,
) -> CollectionReport:
    """Discover, read and persist every 증권발행실적보고서 of the window."""
    report = CollectionReport()
    started = client.request_count

    try:
        found = census(client, bgn_de, end_de, markets=markets, log=log)
    except RequestBudgetExceeded:
        report.budget_exhausted = True
        report.notes.append("census stopped: live request budget exhausted (O-1)")
        report.requests = client.request_count - started
        return report
    report.scanned = found.scanned
    report.reports_in_window = len(found.reports)
    report.candidates = len(found.candidates)
    if log:
        log(found.render())

    for row in found.candidates:
        rcept_no = row["rcept_no"]
        with session_scope(session_factory) as session:
            stored = session.scalar(
                select(PerformanceReport).where(PerformanceReport.rcept_no == rcept_no)
            )
            blob = stored.payload_bytes if stored is not None else None
            if blob is None:
                if max_documents is not None and report.fetched >= max_documents:
                    continue
                try:
                    blob = client.get_document(rcept_no)
                    report.fetched += 1
                except RequestBudgetExceeded:
                    report.budget_exhausted = True
                    report.notes.append("stopped: live request budget exhausted (O-1)")
                    break
                except (CacheMiss, DartError) as exc:
                    report.errors += 1
                    report.notes.append(f"{rcept_no}: {type(exc).__name__}")
                    continue

            try:
                facts = parse_performance(BodyDocument.from_bytes(blob, rcept_no=rcept_no))
            except Exception as exc:  # noqa: BLE001 — one bad document is not a failed run
                report.errors += 1
                report.notes.append(f"{rcept_no}: parse {type(exc).__name__}")
                continue

            if not facts.has_warrant_table:
                report.no_warrant_table += 1
                _persist(session, row, blob, facts, event=None, link=("none", "no 증서 table"))
                report.stored += 1
                continue

            event, link_status, link_note = _link(session, row["corp_code"], facts)
            if event is None and adopt:
                _, end = _report_window(facts)
                if end is not None:
                    try:
                        outcome = adopt_offering(
                            session,
                            client,
                            corp_code=row["corp_code"],
                            corp_name=row.get("corp_name"),
                            subscription_end=end,
                        )
                    except RequestBudgetExceeded:
                        report.budget_exhausted = True
                        report.notes.append("stopped during adoption: budget exhausted (O-1)")
                        break
                    if outcome.status == "adopted":
                        report.adopted += 1
                        event, link_status, link_note = _link(session, row["corp_code"], facts)
                        link_note = f"adopted {outcome.versions} version(s); {link_note}"
                    else:
                        report.notes.append(
                            f"{row['corp_name']} {rcept_no}: adopt {outcome.status} "
                            f"({outcome.note})"
                        )

            _persist(session, row, blob, facts, event=event, link=(link_status, link_note))
            report.stored += 1
            report.parsed += 1
            if event is not None:
                report.linked += 1
            else:
                report.unlinked += 1

    if not report.budget_exhausted:
        _backstop(client, session_factory, report, end_de=end_de, log=log)
    report.requests = client.request_count - started
    return report


def _backstop(client: DartClient, session_factory, report: CollectionReport, *, end_de: str, log
              ) -> None:
    """Per-event sweep for the offerings the ``pblntf_ty=C`` census cannot see.

    Measured, not anticipated: **a 부동산투자회사(REIT) files its 실적보고서 as
    증권발행실적보고서(집합투자증권) outside 발행공시 entirely** — KB스타리츠
    ``20260423000439`` does not appear in any page of the 2026 발행공시 census, and
    a census-only run would have silently dropped a real 2026 lapse of 2,167,828
    증서. So every collected ① event whose 청약 has closed and that still has no
    실적보고서 gets one corp-scoped, unfiltered ``list.json`` call over
    ``[청약 종료일, +60일]``. One request each, and it is also the general
    completeness check on the census's own equity filter.
    """
    with session_scope(session_factory) as session:
        linked = {
            p.event_id
            for p in session.scalars(select(PerformanceReport)).all()
            if p.event_id is not None
        }
        wanted: list[tuple[Event, date]] = []
        for event in session.scalars(
            select(Event).where(
                Event.rights_type == RightsType.SUBSCRIPTION_WARRANT,
                Event.suppressed_reason.is_(None),
            )
        ).all():
            if event.id in linked or event.exposure_state not in ("exposable", "flagged"):
                continue
            windows = _event_windows(session, event)
            ends = [w["end"] for g, w in windows.items() if "일반공모" not in g and "end" in w]
            if ends and max(ends).strftime("%Y%m%d") <= end_de:
                wanted.append((event, max(ends)))
        targets = [(e.corp_code, e.corp.corp_name if e.corp else None, end) for e, end in wanted]

    for corp_code, corp_name, end in targets:
        try:
            rows = client.filings(
                end.strftime("%Y%m%d"),
                (end + timedelta(days=60)).strftime("%Y%m%d"),
                corp_code=corp_code,
                pages=3,
            )
        except RequestBudgetExceeded:
            report.budget_exhausted = True
            report.notes.append("backstop stopped: live request budget exhausted (O-1)")
            return
        except DartError as exc:
            report.errors += 1
            report.notes.append(f"backstop {corp_code}: {type(exc).__name__}")
            continue
        found = [
            r
            for r in rows
            if (r.get("report_nm") or "").strip().startswith(PERF_REPORT_PREFIX)
            and "(합병등)" not in (r.get("report_nm") or "")
        ]
        if not found:
            continue
        for row in sorted(found, key=lambda r: r["rcept_dt"]):
            with session_scope(session_factory) as session:
                if session.scalar(
                    select(PerformanceReport).where(
                        PerformanceReport.rcept_no == row["rcept_no"]
                    )
                ):
                    continue
                try:
                    blob = client.get_document(row["rcept_no"])
                    report.fetched += 1
                except RequestBudgetExceeded:
                    report.budget_exhausted = True
                    report.notes.append("backstop stopped: budget exhausted (O-1)")
                    return
                except (CacheMiss, DartError) as exc:
                    report.errors += 1
                    report.notes.append(f"backstop {row['rcept_no']}: {type(exc).__name__}")
                    continue
                facts = parse_performance(BodyDocument.from_bytes(blob, rcept_no=row["rcept_no"]))
                if not facts.has_warrant_table:
                    continue
                event, link_status, link_note = _link(session, corp_code, facts)
                _persist(
                    session,
                    row,
                    blob,
                    facts,
                    event=event,
                    link=(link_status, f"backstop; {link_note}"),
                )
                report.stored += 1
                report.parsed += 1
                report.backstopped += 1
                if event is not None:
                    report.linked += 1
                else:
                    report.unlinked += 1
                if log:
                    log(f"  backstop  {corp_name} {row['rcept_no']} → {link_status}")


def _persist(session, row: dict, blob: bytes, facts: PerformanceFacts, *, event, link) -> None:
    """Upsert one 실적보고서, raw bytes included (the Snapshot evidence contract)."""
    link_status, link_note = link
    stored = session.scalar(
        select(PerformanceReport).where(PerformanceReport.rcept_no == row["rcept_no"])
    )
    if stored is None:
        stored = PerformanceReport(rcept_no=row["rcept_no"])
        session.add(stored)
    stored.event_id = event.id if event is not None else None
    stored.corp_code = row["corp_code"]
    stored.corp_name = row.get("corp_name")
    stored.rcept_dt = parse_dart_date(row.get("rcept_dt"))
    stored.report_nm = row.get("report_nm")
    stored.form = facts.form
    stored.link_status = link_status
    stored.link_note = link_note
    stored.parse_status = "parsed" if facts.has_warrant_table else "no_warrant_table"
    stored.parse_note = "; ".join(facts.notes) or None
    stored.facts = facts.as_json()
    stored.payload_bytes = blob
    stored.content_sha1 = sha1_hex(blob)
    stored.byte_size = len(blob)
    session.flush()
