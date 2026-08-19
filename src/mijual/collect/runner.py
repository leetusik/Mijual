"""The collection run: discover → pair → detail → filter → snapshot → persist.

One pass over a date window, idempotent by construction (storage-side ``ensure_*``
upserts, note N14; pairing is a pure function of the discovered rows).

Request discipline (**O-1: the daily quota is unmeasured**) is a first-class
concern here, not an afterthought:

* discovery costs ``ceil(months/3) × markets × pages`` requests;
* pairing history is fetched **once per corp**, and only for corps whose
  correction found no original inside the window;
* the detail endpoint is fetched **once per (corp, subtype)**, not per event;
* 본문 ZIPs are fetched only for versions that have none yet, never for
  ``[첨부정정]`` (attachment-only, field-matrix §4.1) and by default not for
  suppressed events — that alone is ~90% of the raw universe;
* :class:`~mijual.dart.RequestBudgetExceeded` stops the run *cleanly*, keeping
  everything collected so far, so a budget cap can never corrupt a run.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Callable, Iterable

from sqlalchemy import func, select

from mijual.collect.discovery import (
    DEFAULT_MARKETS,
    PBLNTF_TY,
    Discovery,
    discover,
    parse_report_nm,
)
from mijual.collect.filters import Suppression, evaluate
from mijual.collect.pairing import FilingIndex, pair_correction
from mijual.collect.targets import BY_SUBTYPE_NM, DEFAULT_ENDPOINTS, TARGETS
from mijual.dart import DartClient, DartError, RequestBudgetExceeded, rows
from mijual.db.models import (
    CorrectionKind,
    Event,
    FilingVersion,
    RightsType,
    Snapshot,
    parse_dart_date,
)
from mijual.db.repository import ensure_corp, ensure_event, ensure_snapshot, ensure_version
from mijual.db.session import session_scope

__all__ = ["CollectionReport", "PlannedEvent", "PlannedVersion", "collect_window"]

#: How far before the earliest known original the detail window opens. The
#: window filters on the **original** 접수일 (N3); the margin only guards against
#: 접수일/결의일 skew and costs nothing (still one request per corp+subtype).
DETAIL_WINDOW_MARGIN_DAYS = 30
#: Default reach of the corp-scoped pairing query (``list.json`` with
#: ``corp_code`` has no 3-month cap).
HISTORY_YEARS = 3
#: Unpaired corrections of the same corp+subtype filed within this many days of
#: each other are treated as one chain (디모아 filed 6 against one 유증), instead
#: of minting one review-flagged event per correction.
UNPAIRED_CHAIN_DAYS = 240


@dataclass
class PlannedVersion:
    rcept_no: str
    rcept_dt: str
    report_nm: str | None
    kind: CorrectionKind
    pairing_method: str
    list_row: dict | None = None
    detail_row: dict | None = None


@dataclass
class PlannedEvent:
    corp_code: str
    endpoint: str
    original_rcept_dt: str
    rights_type: RightsType
    report_nm: str
    corp_row: dict
    versions: dict[str, PlannedVersion] = field(default_factory=dict)
    suppression: Suppression | None = None
    #: Detail rows that landed on this event key. Normally 0 or 1 — the detail
    #: endpoint returns one row per event (§4.2) — so **2+ means the event key
    #: collided**: two filings of the same corp and subtype share one 접수일.
    detail_rows: list[dict] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)

    @property
    def detail_row(self) -> dict | None:
        """The newest detail row on this key (``None`` when none was fetched)."""
        if not self.detail_rows:
            return None
        return max(self.detail_rows, key=lambda r: r.get("rcept_no") or "")

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.corp_code, self.endpoint, self.original_rcept_dt)


@dataclass
class CollectionReport:
    """Everything a run did, in numbers. Rendered into ``result.md`` verbatim."""

    window: tuple[str, str]
    markets: tuple[str, ...]
    endpoints: tuple[str, ...]
    chunks: list[tuple[str, str]] = field(default_factory=list)
    list_rows_scanned: int = 0
    target_rows: int = 0
    rows_by_kind: Counter = field(default_factory=Counter)
    events_planned: int = 0
    events_by_endpoint: Counter = field(default_factory=Counter)
    versions_planned: int = 0
    pairing: Counter = field(default_factory=Counter)
    suppressed: Counter = field(default_factory=Counter)
    live_events: int = 0
    live_by_endpoint: Counter = field(default_factory=Counter)
    undecided_events: int = 0
    history_queries: int = 0
    detail_calls: int = 0
    detail_rows: int = 0
    detail_matched: int = 0
    detail_adopted: int = 0
    detail_unmatched: list[str] = field(default_factory=list)
    detail_missing: int = 0
    key_collisions: list[str] = field(default_factory=list)
    retired_unpaired: list[str] = field(default_factory=list)
    documents_fetched: int = 0
    documents_skipped_attachment: int = 0
    documents_skipped_suppressed: int = 0
    documents_already_held: int = 0
    document_errors: Counter = field(default_factory=Counter)
    db_before: tuple[int, int, int] = (0, 0, 0)
    db_after: tuple[int, int, int] = (0, 0, 0)
    requests: int = 0
    budget_exhausted: bool = False
    missing_chunks: list[tuple[str, str, str]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"window     : {self.window[0]}~{self.window[1]} "
            f"markets={','.join(self.markets)} endpoints={','.join(self.endpoints)}",
            f"discovery  : {self.list_rows_scanned} list rows scanned in "
            f"{len(self.chunks)} chunk(s) -> {self.target_rows} target rows "
            + " ".join(f"{k.value}={v}" for k, v in sorted(
                self.rows_by_kind.items(), key=lambda kv: kv[0].value)),
            f"events     : {self.events_planned} planned "
            + " ".join(f"{k}={v}" for k, v in sorted(self.events_by_endpoint.items()))
            + f" | versions {self.versions_planned}",
            "pairing    : "
            + " ".join(f"{k}={v}" for k, v in sorted(self.pairing.items()))
            + f" | corp-history queries {self.history_queries}",
            f"detail     : {self.detail_calls} call(s) -> {self.detail_rows} row(s), "
            f"matched {self.detail_matched}, adopted {self.detail_adopted}, "
            f"unmatched {len(self.detail_unmatched)}, events without detail {self.detail_missing}",
            f"filters    : live {self.live_events} "
            + "(" + " ".join(f"{k}={v}" for k, v in sorted(self.live_by_endpoint.items())) + ")"
            + f", undecided {self.undecided_events}, suppressed "
            + (" ".join(f"{k}={v}" for k, v in sorted(self.suppressed.items())) or "0"),
            f"documents  : fetched {self.documents_fetched}, already held "
            f"{self.documents_already_held}, skipped 첨부정정 "
            f"{self.documents_skipped_attachment}, skipped suppressed "
            f"{self.documents_skipped_suppressed}"
            + (f", errors {dict(self.document_errors)}" if self.document_errors else ""),
            f"database   : (event, version, snapshot) "
            f"{self.db_before} -> {self.db_after}",
            f"requests   : {self.requests} live OpenDART request(s)"
            + (" — BUDGET EXHAUSTED" if self.budget_exhausted else ""),
        ]
        if self.retired_unpaired:
            lines.append(
                f"retired    : {len(self.retired_unpaired)} placeholder event(s) "
                "superseded_by_pairing"
            )
        if self.key_collisions:
            lines.append(
                f"flags      : event-key collisions {len(self.key_collisions)} "
                f"{self.key_collisions[:5]}"
            )
        if self.missing_chunks:
            lines.append(f"gaps       : {self.missing_chunks}")
        lines.extend(f"note       : {n}" for n in self.notes)
        return "\n".join(lines)


def _counts(session) -> tuple[int, int, int]:
    def n(model) -> int:
        return int(session.scalar(select(func.count()).select_from(model)) or 0)

    return (n(Event), n(FilingVersion), n(Snapshot))


def _history_loader(
    client: DartClient, report: CollectionReport, history_bgn: str, end_de: str
) -> Callable[[str], Iterable[dict]]:
    def load(corp_code: str) -> list[dict]:
        report.history_queries += 1
        try:
            return client.filings(
                history_bgn, end_de, pblntf_ty=PBLNTF_TY, corp_code=corp_code, pages=10
            )
        except RequestBudgetExceeded:
            report.budget_exhausted = True
            return []
        except DartError:
            return []

    return load


def build_plan(
    discovery: Discovery,
    *,
    endpoints: tuple[str, ...],
    report: CollectionReport,
    load_history: Callable[[str], Iterable[dict]] | None = None,
) -> dict[tuple[str, str, str], PlannedEvent]:
    """Discovered rows → events keyed ``(corp, subtype, original 접수일)`` (N2)."""
    index = FilingIndex()
    index.add(discovery.rows)

    plan: dict[tuple[str, str, str], PlannedEvent] = {}

    def place(target, row: dict, original_dt: str, method: str) -> None:
        key = (row["corp_code"], target.endpoint, original_dt)
        event = plan.get(key)
        if event is None:
            event = plan[key] = PlannedEvent(
                corp_code=row["corp_code"],
                endpoint=target.endpoint,
                original_rcept_dt=original_dt,
                rights_type=target.rights_type,
                report_nm=f"주요사항보고서({target.subtype_nm})",
                corp_row=row,
            )
        event.versions[row["rcept_no"]] = PlannedVersion(
            rcept_no=row["rcept_no"],
            rcept_dt=row["rcept_dt"],
            report_nm=row.get("report_nm"),
            kind=CorrectionKind.from_report_nm(row.get("report_nm")),
            pairing_method=method,
            list_row=row,
        )
        report.pairing[method] += 1

    # Chronological order matters: an original is placed before the corrections
    # that reference it, and an unpaired chain attaches to its earliest member.
    ordered = sorted(discovery.rows, key=lambda r: (r["rcept_dt"], r["rcept_no"]))
    corrections: list[tuple] = []
    for row in ordered:
        _, subtype_nm = parse_report_nm(row.get("report_nm"))
        target = BY_SUBTYPE_NM.get(subtype_nm or "")
        if target is None or target.endpoint not in endpoints:
            continue
        kind = CorrectionKind.from_report_nm(row.get("report_nm"))
        report.rows_by_kind[kind] += 1
        if kind is CorrectionKind.ORIGINAL:
            place(target, row, row["rcept_dt"], "original")
        else:
            corrections.append((target, subtype_nm, row))

    for target, subtype_nm, row in corrections:
        pairing = pair_correction(index, row, subtype_nm, load_history=load_history)
        if pairing.paired:
            place(target, row, pairing.original["rcept_dt"], pairing.method)
            continue

        # Unpaired: the original is not visible even in the corp's own history.
        # Record it as its own event, flagged for review and suppressed rather
        # than exposed — never dropped. Corrections of the same corp+subtype
        # close together are treated as one chain.
        chain = _open_unpaired_chain(plan, row, target.endpoint)
        if chain is not None:
            place(target, row, chain.original_rcept_dt, "unpaired_chain")
        else:
            place(target, row, row["rcept_dt"], "unpaired")
            event = plan[(row["corp_code"], target.endpoint, row["rcept_dt"])]
            event.flags.append("unpaired_correction")

    report.events_planned = len(plan)
    report.versions_planned = sum(len(e.versions) for e in plan.values())
    for event in plan.values():
        report.events_by_endpoint[event.endpoint] += 1
    return plan


def _open_unpaired_chain(plan, row: dict, endpoint: str) -> PlannedEvent | None:
    """An earlier unpaired event of the same corp+subtype, close enough in time."""
    when = parse_dart_date(row["rcept_dt"])
    best: PlannedEvent | None = None
    for event in plan.values():
        if event.corp_code != row["corp_code"] or event.endpoint != endpoint:
            continue
        if "unpaired_correction" not in event.flags:
            continue
        started = parse_dart_date(event.original_rcept_dt)
        if started is None or when is None:
            continue
        if started <= when <= started + timedelta(days=UNPAIRED_CHAIN_DAYS):
            if best is None or started > parse_dart_date(best.original_rcept_dt):
                best = event
    return best


def fetch_details(
    client: DartClient,
    plan: dict,
    *,
    report: CollectionReport,
    detail_window: tuple[str, str] | None = None,
) -> None:
    """One detail call per ``(corp, subtype)``, windowed on the ORIGINAL 접수일.

    Windowing on the correction's date returns ``[]`` in 40/40 measured cases
    (N3), which is why the window is derived from the events' original dates and
    never from the correction rows.
    """
    groups: dict[tuple[str, str], list[PlannedEvent]] = {}
    for event in plan.values():
        groups.setdefault((event.corp_code, event.endpoint), []).append(event)

    for (corp_code, endpoint), events in sorted(groups.items()):
        dates = sorted(e.original_rcept_dt for e in events)
        if detail_window is not None:
            bgn, end = detail_window
        else:
            first = parse_dart_date(dates[0]) - timedelta(days=DETAIL_WINDOW_MARGIN_DAYS)
            bgn, end = first.strftime("%Y%m%d"), dates[-1]

        report.detail_calls += 1
        try:
            body = client.get_json(endpoint, corp_code=corp_code, bgn_de=bgn, end_de=end)
        except DartError as exc:
            report.budget_exhausted |= isinstance(exc, RequestBudgetExceeded)
            report.detail_missing += len(events)
            continue
        detail_rows = rows(body)
        report.detail_rows += len(detail_rows)

        by_rcept_no = {
            rcept_no: event for event in events for rcept_no in event.versions
        }
        for detail_row in sorted(detail_rows, key=lambda r: r.get("rcept_no") or ""):
            rcept_no = detail_row.get("rcept_no")
            event = by_rcept_no.get(rcept_no)
            if event is not None:
                event.detail_rows.append(detail_row)
                event.versions[rcept_no].detail_row = detail_row
                report.detail_matched += 1
                continue
            adopted = _adopt_detail_row(events, detail_row)
            if adopted is None:
                report.detail_unmatched.append(f"{corp_code}/{endpoint}/{rcept_no}")
            else:
                report.detail_adopted += 1

        report.detail_missing += sum(1 for e in events if not e.detail_rows)


def _adopt_detail_row(events: list[PlannedEvent], detail_row: dict) -> PlannedEvent | None:
    """A detail row for a version ``list.json`` did not show us.

    The detail endpoint returns the **newest** version of an event (§4.2), so a
    correction filed after the discovery window ends is invisible to discovery
    but visible here. It is adopted by the newest event whose original predates
    it and which has no detail row yet; anything more ambiguous than that is
    reported instead of guessed.
    """
    rcept_no = detail_row.get("rcept_no") or ""
    filed = parse_dart_date(rcept_no[:8])
    if filed is None:
        return None
    candidates = [
        e
        for e in events
        if not e.detail_rows and (parse_dart_date(e.original_rcept_dt) or filed) <= filed
    ]
    if not candidates:
        return None
    event = max(candidates, key=lambda e: e.original_rcept_dt)
    kind = (
        CorrectionKind.ORIGINAL
        if rcept_no[:8] == event.original_rcept_dt
        else CorrectionKind.DISCLOSURE
    )
    # ``rcept_no[:8]`` is the submission date and is usually — but not always —
    # the ``rcept_dt`` list.json reports (한솔테크닉스 ``20260410003732`` is dated
    # 2026-04-13). It is only a fallback for a version list.json never showed us.
    event.versions[rcept_no] = PlannedVersion(
        rcept_no=rcept_no,
        rcept_dt=rcept_no[:8],
        report_nm=None,
        kind=kind,
        pairing_method="detail_only",
        detail_row=detail_row,
    )
    event.detail_rows.append(detail_row)
    return event


def apply_filters(plan: dict, *, report: CollectionReport) -> None:
    """Decide, per event, whether it may ever be exposed as a live right.

    Two rules keep this from hiding something real:

    * an event with **no** detail row is *undecided*, not suppressed;
    * an event whose detail rows **disagree** (only possible on a collided event
      key) stays live and is flagged — suppressing on the strength of the other
      filing's row is exactly the correctness bug the phase constraint names.
    """
    for event in plan.values():
        if len(event.detail_rows) > 1:
            event.flags.append("event_key_collision")
            report.key_collisions.append(f"{event.corp_code}/{event.endpoint}/{event.original_rcept_dt}")

        if "unpaired_correction" in event.flags:
            event.suppression = Suppression(
                "unpaired_correction",
                "원본 공시를 찾지 못한 정정 — 이벤트 동일성 미확정 (P2.S3의 <CORRECTION> "
                "최초제출일 백필로 재확인 필요)",
            )
        else:
            verdicts = [evaluate(event.endpoint, row) for row in event.detail_rows]
            if verdicts and all(v is not None for v in verdicts):
                event.suppression = verdicts[-1]
            elif any(v is not None for v in verdicts):
                event.flags.append("detail_conflict")

        if event.suppression is not None:
            report.suppressed[event.suppression.reason] += 1
        elif not event.detail_rows:
            report.undecided_events += 1
        else:
            report.live_events += 1
            report.live_by_endpoint[event.endpoint] += 1


def retire_superseded_unpaired(session) -> list[str]:
    """Retire review-flagged events that a later, wider run has resolved.

    A correction whose original is invisible becomes its own
    ``unpaired_correction`` event. When a later run — with a wider window, or
    with the corp-scoped history query answering this time — pairs the same
    filing to its real original, the earlier placeholder is left behind holding
    duplicate versions. Measured after this slice's two runs: 47 of 1,179
    ``rcept_no`` values sat under two event keys.

    Rather than delete evidence, the placeholder is re-suppressed as
    ``superseded_by_pairing`` naming the winner, so a later slice can clean up
    (or a human can audit) without guessing which of the two is real.
    """
    retired: list[str] = []
    stale = session.scalars(
        select(Event).where(Event.suppressed_reason == "unpaired_correction")
    ).all()
    for event in stale:
        rcept_nos = {v.rcept_no for v in event.versions}
        if not rcept_nos:
            continue
        winner = session.scalar(
            select(Event)
            .join(FilingVersion, FilingVersion.event_id == Event.id)
            .where(
                Event.corp_code == event.corp_code,
                Event.report_subtype == event.report_subtype,
                Event.id != event.id,
                (Event.suppressed_reason.is_(None))
                | (Event.suppressed_reason != "unpaired_correction"),
                FilingVersion.rcept_no.in_(rcept_nos),
            )
            .limit(1)
        )
        if winner is None:
            continue
        event.suppress(
            "superseded_by_pairing",
            f"같은 공시가 {winner.corp_code}/{winner.report_subtype}/"
            f"{winner.original_rcept_dt} 이벤트로 정상 페어링됨 — 이 레코드는 폐기 대상",
        )
        retired.append(f"{event.corp_code}/{event.report_subtype}/{event.original_rcept_dt}")
    return retired


def persist(session, plan: dict) -> None:
    for event_plan in sorted(plan.values(), key=lambda e: e.key):
        corp_row = event_plan.corp_row
        ensure_corp(
            session,
            event_plan.corp_code,
            corp_name=corp_row.get("corp_name"),
            stock_code=corp_row.get("stock_code"),
            corp_cls=corp_row.get("corp_cls"),
        )
        event = ensure_event(
            session,
            corp_code=event_plan.corp_code,
            report_subtype=event_plan.endpoint,
            original_rcept_dt=event_plan.original_rcept_dt,
            rights_type=event_plan.rights_type,
            report_nm=event_plan.report_nm,
        )
        for flag in event_plan.flags:
            if flag != "unpaired_correction":  # that one is carried by the reason
                event.add_flag(flag)
        if event_plan.suppression is not None:
            event.suppress(event_plan.suppression.reason, event_plan.suppression.note)
        elif event.is_suppressed:
            # A previously suppressed event that now passes the filter (a 정정
            # changed 증자방식, say) must not stay hidden.
            event.suppressed_reason = event.suppressed_note = event.suppressed_at = None

        for planned in sorted(event_plan.versions.values(), key=lambda v: v.rcept_no):
            version = ensure_version(
                session,
                event,
                rcept_no=planned.rcept_no,
                rcept_dt=planned.rcept_dt,
                report_nm=planned.report_nm,
                correction_kind=planned.kind,
                pairing_method=planned.pairing_method,
            )
            if planned.list_row is not None:
                ensure_snapshot(session, version, source="list", payload_json=planned.list_row)
            if planned.detail_row is not None:
                ensure_snapshot(
                    session,
                    version,
                    source=event_plan.endpoint,
                    payload_json=planned.detail_row,
                )


def fetch_documents(
    client: DartClient,
    session,
    plan: dict,
    *,
    report: CollectionReport,
    max_documents: int | None = None,
    include_suppressed: bool = False,
) -> None:
    """Snapshot the raw 본문 ZIP of every newly observed ``rcept_no``.

    "Newly observed" is answered by the database, not by the run: a version that
    already carries a ``document`` snapshot is never re-fetched, which is what
    makes re-running a window free.
    """
    wanted: list[str] = []
    for event_plan in sorted(plan.values(), key=lambda e: e.key):
        suppressed = event_plan.suppression is not None
        for planned in sorted(event_plan.versions.values(), key=lambda v: v.rcept_no):
            if planned.kind is CorrectionKind.ATTACHMENT:
                report.documents_skipped_attachment += 1
                continue
            if suppressed and not include_suppressed:
                report.documents_skipped_suppressed += 1
                continue
            wanted.append(planned.rcept_no)

    if not wanted:
        return

    held = set(
        session.scalars(
            select(FilingVersion.rcept_no)
            .join(Snapshot, Snapshot.filing_version_id == FilingVersion.id)
            .where(Snapshot.source == "document", FilingVersion.rcept_no.in_(wanted))
        )
    )
    report.documents_already_held += len(held)

    for rcept_no in wanted:
        if rcept_no in held:
            continue
        if max_documents is not None and report.documents_fetched >= max_documents:
            report.notes.append(f"document fetch capped at {max_documents}")
            return
        try:
            blob = client.get_document(rcept_no)
        except RequestBudgetExceeded:
            report.budget_exhausted = True
            report.notes.append("document fetch stopped: request budget exhausted (O-1)")
            return
        except DartError as exc:
            report.document_errors[type(exc).__name__] += 1
            continue
        report.documents_fetched += 1
        for version in session.scalars(
            select(FilingVersion).where(FilingVersion.rcept_no == rcept_no)
        ):
            ensure_snapshot(session, version, source="document", payload_bytes=blob)


def collect_window(
    client: DartClient,
    session_factory,
    *,
    bgn_de: str,
    end_de: str,
    markets: tuple[str, ...] = DEFAULT_MARKETS,
    endpoints: tuple[str, ...] = DEFAULT_ENDPOINTS,
    detail_window: tuple[str, str] | None = None,
    history_bgn: str | None = None,
    pair_history: bool = True,
    with_documents: bool = True,
    max_documents: int | None = None,
    documents_for_suppressed: bool = False,
    dry_run: bool = False,
    log=None,
) -> CollectionReport:
    """Collect one window end to end. Safe to re-run: nothing is duplicated."""
    unknown = [e for e in endpoints if e not in TARGETS]
    if unknown:
        raise ValueError(f"not a P2.S2 target endpoint: {unknown}")

    report = CollectionReport(
        window=(bgn_de, end_de), markets=tuple(markets), endpoints=tuple(endpoints)
    )
    started_requests = client.request_count

    try:
        discovery = discover(
            client, bgn_de, end_de, markets=markets, endpoints=endpoints,
            on_error="skip" if client.offline else "raise", log=log,
        )
        report.chunks = discovery.chunks
        report.list_rows_scanned = discovery.scanned
        report.target_rows = len(discovery.rows)
        report.missing_chunks = discovery.missing_chunks

        if history_bgn is None:
            start = parse_dart_date(bgn_de)
            history_bgn = start.replace(
                year=start.year - HISTORY_YEARS, day=1
            ).strftime("%Y%m%d")
        loader = (
            _history_loader(client, report, history_bgn, end_de) if pair_history else None
        )
        plan = build_plan(discovery, endpoints=tuple(endpoints), report=report, load_history=loader)
        if log:
            log(f"  planned {len(plan)} event(s) from {len(discovery.rows)} target row(s)")

        fetch_details(client, plan, report=report, detail_window=detail_window)
        apply_filters(plan, report=report)

        if dry_run:
            report.notes.append("dry run — nothing persisted")
            return report

        with session_scope(session_factory) as session:
            report.db_before = _counts(session)
            persist(session, plan)
            report.retired_unpaired = retire_superseded_unpaired(session)
        if with_documents:
            with session_scope(session_factory) as session:
                fetch_documents(
                    client, session, plan, report=report,
                    max_documents=max_documents,
                    include_suppressed=documents_for_suppressed,
                )
        with session_scope(session_factory) as session:
            report.db_after = _counts(session)
    except RequestBudgetExceeded:
        report.budget_exhausted = True
        report.notes.append("stopped early: request budget exhausted (O-1 guard)")
    finally:
        report.requests = client.request_count - started_requests

    return report
