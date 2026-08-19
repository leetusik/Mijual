"""The two persisted jobs of ``P2.S3``: CORRECTION backfill and the ① 본문 filter.

Both are *readers* of the deterministic parse layer plus a very small set of
writes. They add **no field-materialization tables** — extracted-field storage
(tier, span, gate status) is ``P2.S4``'s schema design, shared with the LLM tier,
and inventing a second one here would guarantee two incompatible shapes. What is
persisted is only what the pipeline cannot recompute for free:

* ``FilingVersion.declared_original_dt`` / ``hint_status`` / ``pairing_note``
  — the ``<CORRECTION>`` 최초제출일 hint's verdict on ``P2.S2``'s pairing;
* ``Event.review_flags`` and ``Event.suppress(...)`` — the ① 본문 filter's outcome.

Everything else (labels, spans, 정정사항 rows) is recomputed on demand from the
stored snapshot, which is what makes the layer testable offline and what keeps
the citation spans honest: they are always spans into the snapshot as stored.

Two rules from the phase are enforced here rather than assumed:

* **evidence is relabelled, never deleted** — ``pairing_method`` keeps exactly
  what ``P2.S2`` wrote and an emptied placeholder is re-suppressed
  ``superseded_by_pairing`` (S2's own pattern), never dropped;
* **never suppress on conflicting evidence** — an event whose 본문 and whose
  ``ic_mthn`` disagree about whether a 신주인수권증서 exists stays live and is
  flagged. Hiding it is the exact bug ``P2.S2`` had to fix once already (N20).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.bodydoc.correction import CorrectionBlock, parse_correction
from mijual.bodydoc.document import BodyDocument
from mijual.bodydoc.labels import extract_labels
from mijual.collect.filters import WARRANT_BEARING_IC_MTHN
from mijual.dart import CacheMiss, DartClient, DartError, RequestBudgetExceeded
from mijual.db.models import CorrectionKind, Event, FilingVersion, RightsType, Snapshot
from mijual.db.repository import ensure_snapshot
from mijual.db.session import session_scope

__all__ = [
    "BackfillReport",
    "WarrantReport",
    "backfill_corrections",
    "confirm_warrants",
    "load_document",
]

#: New suppression reason: the 본문 itself says no 신주인수권증서 is issued.
#: Plain string, like every other reason code — no enum, no migration (N15).
NO_WARRANT_REASON = "no_warrant_bodymun"

#: The ① 본문 filter's own verdict flags — re-derived, never accumulated.
WARRANT_FLAGS = ("warrant_confirmed", "warrant_conflict", "warrant_unverified")


# ---------------------------------------------------------------------------
# document access — database first, then the response cache, then (budgeted) live
# ---------------------------------------------------------------------------
def load_document(
    session: Session,
    client: DartClient | None,
    version: FilingVersion,
    *,
    fetch: bool = True,
    persist: bool = True,
) -> tuple[bytes | None, str]:
    """Raw 본문 ZIP for one version, and where it came from.

    Order matters for the request budget (O-1): a snapshot already in the
    database costs nothing, the on-disk response cache costs nothing, and only a
    genuine miss spends quota.
    """
    snapshot = session.scalar(
        select(Snapshot)
        .where(Snapshot.filing_version_id == version.id, Snapshot.source == "document")
        .order_by(Snapshot.captured_at.desc())
        .limit(1)
    )
    if snapshot is not None and snapshot.payload_bytes:
        return (snapshot.payload_bytes, "snapshot")
    if client is None or not fetch:
        return (None, "missing")

    cached = client.cache_path("document", {"rcept_no": version.rcept_no}, "zip").exists()
    try:
        blob = client.get_document(version.rcept_no)
    except RequestBudgetExceeded:
        raise
    except CacheMiss:
        return (None, "missing")  # offline client, nothing on disk — not an error
    except DartError:
        return (None, "error")
    if persist:
        ensure_snapshot(session, version, source="document", payload_bytes=blob)
    return (blob, "cache" if cached else "live")


# ---------------------------------------------------------------------------
# job 1 — <CORRECTION> backfill and pairing re-evaluation
# ---------------------------------------------------------------------------
@dataclass
class BackfillReport:
    considered: int = 0
    parsed: int = 0
    hints: int = 0
    documents_from_snapshot: int = 0
    documents_from_cache: int = 0
    documents_fetched_live: int = 0
    documents_missing: int = 0
    document_errors: int = 0
    outcomes: Counter = field(default_factory=Counter)
    ambiguous_before: int = 0
    ambiguous_after: int = 0
    unpaired_events_before: int = 0
    unpaired_events_after: int = 0
    unpaired_identified_before: int = 0
    unpaired_identified_after: int = 0
    collisions_before: int = 0
    collisions_after: int = 0
    detail_conflicts_before: int = 0
    detail_conflicts_after: int = 0
    reattached: list[str] = field(default_factory=list)
    retired: list[str] = field(default_factory=list)
    split_evidence: list[str] = field(default_factory=list)
    items_parsed: int = 0
    requests: int = 0
    budget_exhausted: bool = False
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"candidates : {self.considered} 기재정정 version(s) considered, {self.parsed} parsed, "
            f"{self.hints} carried a 최초제출일 hint, {self.items_parsed} 정정사항 row(s)",
            f"documents  : snapshot {self.documents_from_snapshot}, cache "
            f"{self.documents_from_cache}, live {self.documents_fetched_live}, missing "
            f"{self.documents_missing}, errors {self.document_errors}",
            "outcomes   : " + (" ".join(f"{k}={v}" for k, v in sorted(self.outcomes.items())) or "-"),
            f"ambiguous  : {self.ambiguous_before} -> {self.ambiguous_after} version(s)",
            f"unpaired   : {self.unpaired_events_before} -> {self.unpaired_events_after} event(s), "
            f"of which identified by 본문 hint {self.unpaired_identified_before} -> "
            f"{self.unpaired_identified_after}",
            f"collisions : {self.collisions_before} -> {self.collisions_after} "
            f"(detail_conflict {self.detail_conflicts_before} -> {self.detail_conflicts_after})",
            f"requests   : {self.requests} live OpenDART request(s)"
            + (" — BUDGET EXHAUSTED" if self.budget_exhausted else ""),
        ]
        if self.reattached:
            lines.append(f"reattached : {len(self.reattached)} {self.reattached[:6]}")
        if self.retired:
            lines.append(f"retired    : {len(self.retired)} placeholder(s) superseded_by_pairing")
        if self.split_evidence:
            lines.append(
                f"split      : {len(self.split_evidence)} collided key(s) whose 본문 hints "
                f"disagree {self.split_evidence[:6]}"
            )
        lines.extend(f"note       : {n}" for n in self.notes)
        return "\n".join(lines)


def _priority(version: FilingVersion) -> tuple[int, str]:
    """Fetch order under the request ceiling, straight from the slice plan.

    (a) versions of the 53 exposable events, (b) the ``*_ambiguous`` /
    collision worklist, (c) ``unpaired_correction`` placeholders' own 본문 —
    their header may be the only thing that can identify them at all.
    """
    event = version.event
    if not event.is_suppressed:
        return (0, version.rcept_no)
    if version.pairing_is_ambiguous or {"event_key_collision", "detail_conflict"} & set(
        event.flags
    ):
        return (1, version.rcept_no)
    if event.suppressed_reason == "unpaired_correction":
        return (2, version.rcept_no)
    return (3, version.rcept_no)


def _worklist_counts(session: Session) -> tuple[int, int, int, int, int]:
    versions = session.scalars(select(FilingVersion)).all()
    ambiguous = sum(1 for v in versions if v.pairing_is_ambiguous)
    events = session.scalars(select(Event)).all()
    unpaired = [e for e in events if e.suppressed_reason == "unpaired_correction"]
    identified = sum(1 for e in unpaired if "hint_identified" in e.flags)
    collisions = sum(1 for e in events if "event_key_collision" in e.flags)
    conflicts = sum(1 for e in events if "detail_conflict" in e.flags)
    return (ambiguous, len(unpaired), identified, collisions, conflicts)


def _apply_hint(
    session: Session, version: FilingVersion, block: CorrectionBlock, report: BackfillReport
) -> str:
    """One version's hint → its verdict on ``P2.S2``'s pairing."""
    event = version.event
    if not block.present:
        version.note_pairing("no_correction_block", "본문에 <CORRECTION> 블록 없음")
        return "no_correction_block"
    if block.declared_original_dt is None:
        version.note_pairing("absent", "<CORRECTION>에 2. 최초제출일 기재 없음")
        return "absent"

    hint = block.declared_original_dt
    version.declared_original_dt = hint
    if event.original_rcept_dt == hint:
        if version.hint_status == "reattached":
            # Sticky: a version this job *moved* keeps saying so, and keeps the
            # note naming where it came from. A later pass must not quietly
            # relabel the move as a plain confirmation — that is the audit trail.
            return "reattached"
        version.note_pairing(
            "confirmed", f"본문 최초제출일 {hint} = 이벤트 원본 접수일 ({version.pairing_method})"
        )
        return "confirmed"

    twin = session.scalar(
        select(Event).where(
            Event.corp_code == event.corp_code,
            Event.report_subtype == event.report_subtype,
            Event.original_rcept_dt == hint,
            Event.id != event.id,
        )
    )
    if twin is None:
        # The hint is filer-entered and sometimes years stale (N3 /
        # ``20260429000902`` declares 2022-08-01), so a hint that names nothing we
        # have is recorded — never allowed to move a version.
        if event.suppressed_reason == "unpaired_correction":
            # A placeholder minted *because* the original was invisible. The hint
            # does not pair it (the original really is not in the corpus — it
            # predates the collection window), but it does **identify** it: we now
            # know the original's 접수일. That is a genuine worklist reduction,
            # so it is a distinct outcome, not a mismatch.
            version.note_pairing(
                "identified",
                f"본문 최초제출일 {hint} — 원본 공시가 수집 범위 밖 (플레이스홀더 유지)",
            )
            event.add_flag("hint_identified")
            event.suppressed_note = (
                f"원본 공시를 찾지 못한 정정 — 본문 <CORRECTION> 최초제출일 {hint} "
                "(원본은 수집 창 밖). 이벤트 동일성은 이 날짜로 확정됨 (P2.S3)"
            )
            return "identified"
        version.note_pairing(
            "mismatch",
            f"본문 최초제출일 {hint} — 같은 corp/subtype의 해당 이벤트 없음 "
            f"(현재 부착: {event.original_rcept_dt} / {version.pairing_method})",
        )
        event.add_flag("hint_mismatch")
        return "mismatch"

    duplicate = session.scalar(
        select(FilingVersion).where(
            FilingVersion.event_id == twin.id, FilingVersion.rcept_no == version.rcept_no
        )
    )
    if duplicate is not None:
        version.note_pairing(
            "duplicate",
            f"본문 최초제출일 {hint} 이벤트가 이미 같은 rcept_no를 보유 — 중복 레코드 (N21)",
        )
        event.add_flag("hint_duplicate")
        return "duplicate"

    was = event
    version.event_id = twin.id
    version.note_pairing(
        "reattached",
        f"본문 최초제출일 {hint} 기준으로 {was.original_rcept_dt} -> {twin.original_rcept_dt} "
        f"이벤트로 재부착 (P2.S2 pairing_method={version.pairing_method})",
    )
    session.flush()
    report.reattached.append(f"{version.rcept_no}:{was.original_rcept_dt}->{hint}")
    if was.suppressed_reason != "unpaired_correction":
        # A real event lost a version: this is the N20(b) mis-merge being undone.
        was.add_flag("hint_split")
    return "reattached"


def _retire_emptied(session: Session, report: BackfillReport) -> None:
    """A placeholder whose every version moved away is relabelled, not deleted."""
    for event in session.scalars(
        select(Event).where(Event.suppressed_reason == "unpaired_correction")
    ).all():
        if event.versions:
            continue
        event.suppress(
            "superseded_by_pairing",
            "본문 <CORRECTION> 최초제출일로 모든 버전이 실제 이벤트에 재부착됨 — 폐기 대상 (P2.S3)",
        )
        report.retired.append(
            f"{event.corp_code}/{event.report_subtype}/{event.original_rcept_dt}"
        )


def _flag_split_evidence(session: Session, report: BackfillReport) -> None:
    """Collided event keys whose versions' 본문 hints disagree really are two events.

    N20(b): two concurrent filings of one corp+subtype collapse onto one key when
    only one original is visible. The hints are per-filing, so two distinct
    declared 최초제출일 under one key is direct evidence of the split. The split
    itself is **not** performed here — minting an event whose original filing we
    have never seen is a collector decision, not a parser's — it is flagged with
    the competing dates so ``P2.S5`` (or a wider re-collection) can act.
    """
    for event in session.scalars(select(Event).where(Event.review_flags.isnot(None))).all():
        if "event_key_collision" not in event.flags:
            continue
        declared = {v.declared_original_dt for v in event.versions if v.declared_original_dt}
        if len(declared) > 1:
            event.add_flag("hint_split_evidence")
            event.suppressed_note = (event.suppressed_note or "") + (
                f" | 본문 최초제출일이 {sorted(str(d) for d in declared)}로 갈림 — 실제로 2개 이벤트"
            )
            report.split_evidence.append(
                f"{event.corp_code}/{event.report_subtype}/{event.original_rcept_dt}"
            )


def backfill_corrections(
    client: DartClient | None,
    session_factory,
    *,
    limit: int | None = None,
    max_documents: int | None = None,
    fetch: bool = True,
    priorities: tuple[int, ...] = (0, 1, 2, 3),
    log=None,
) -> BackfillReport:
    """Parse every reachable 기재정정 본문 and re-judge ``P2.S2``'s pairing."""
    report = BackfillReport()
    started = client.request_count if client else 0

    with session_scope(session_factory) as session:
        (
            report.ambiguous_before,
            report.unpaired_events_before,
            report.unpaired_identified_before,
            report.collisions_before,
            report.detail_conflicts_before,
        ) = _worklist_counts(session)

        candidates = [
            v
            for v in session.scalars(
                select(FilingVersion).where(
                    FilingVersion.correction_kind == CorrectionKind.DISCLOSURE
                )
            ).all()
            if _priority(v)[0] in priorities
        ]
        candidates.sort(key=_priority)
        if limit is not None:
            candidates = candidates[:limit]
        report.considered = len(candidates)

        fetched = 0
        for version in candidates:
            allow_fetch = fetch and (max_documents is None or fetched < max_documents)
            try:
                blob, origin = load_document(session, client, version, fetch=allow_fetch)
            except RequestBudgetExceeded:
                report.budget_exhausted = True
                report.notes.append("stopped early: live request budget exhausted (O-1 guard)")
                break
            if origin == "live":
                fetched += 1
                report.documents_fetched_live += 1
            elif origin == "cache":
                report.documents_from_cache += 1
            elif origin == "snapshot":
                report.documents_from_snapshot += 1
            elif origin == "error":
                report.document_errors += 1
            if blob is None:
                if origin == "missing":
                    report.documents_missing += 1
                version.note_pairing("no_document", "본문 스냅샷 없음 (예산/캐시 미확보)")
                report.outcomes["no_document"] += 1
                continue

            try:
                doc = BodyDocument.from_bytes(blob, rcept_no=version.rcept_no)
                block = parse_correction(doc)
            except Exception as exc:  # noqa: BLE001 - a bad body must not stop the run
                version.note_pairing("unparsed", f"본문 파싱 실패: {type(exc).__name__}")
                report.outcomes["unparsed"] += 1
                continue

            report.parsed += 1
            report.items_parsed += len(block.items)
            if block.has_hint:
                report.hints += 1
            outcome = _apply_hint(session, version, block, report)
            report.outcomes[outcome] += 1
            if log and report.parsed % 100 == 0:
                log(f"  parsed {report.parsed}/{len(candidates)} …")

        _retire_emptied(session, report)
        _flag_split_evidence(session, report)
        session.flush()
        (
            report.ambiguous_after,
            report.unpaired_events_after,
            report.unpaired_identified_after,
            report.collisions_after,
            report.detail_conflicts_after,
        ) = _worklist_counts(session)

    report.requests = (client.request_count - started) if client else 0
    return report


# ---------------------------------------------------------------------------
# job 2 — the ① filter's final test: 본문 `18. 신주인수권양도여부`
# ---------------------------------------------------------------------------
@dataclass
class WarrantVerdict:
    event_key: str
    corp_name: str | None
    rcept_no: str | None
    ic_mthn: str | None
    transferable: bool | None
    certificate_listed: bool | None
    label_present: bool
    outcome: str
    span: tuple[int, int] | None = None
    raw: str | None = None


@dataclass
class WarrantReport:
    events: int = 0
    outcomes: Counter = field(default_factory=Counter)
    verdicts: list[WarrantVerdict] = field(default_factory=list)
    documents_fetched_live: int = 0
    requests: int = 0
    budget_exhausted: bool = False
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"① events   : {self.events} unsuppressed 유상증자 event(s) checked against 본문 18.",
            "outcomes   : " + (" ".join(f"{k}={v}" for k, v in sorted(self.outcomes.items())) or "-"),
            f"documents  : {self.documents_fetched_live} fetched live",
            f"requests   : {self.requests} live OpenDART request(s)"
            + (" — BUDGET EXHAUSTED" if self.budget_exhausted else ""),
        ]
        lines.extend(f"note       : {n}" for n in self.notes)
        return "\n".join(lines)


def _ic_mthn(session: Session, event: Event) -> str | None:
    """``증자방식`` from the newest ``piicDecsn`` snapshot on this event."""
    newest: tuple[str, str] | None = None
    for version in event.versions:
        for snapshot in version.snapshots:
            if snapshot.source != event.report_subtype or not isinstance(
                snapshot.payload_json, dict
            ):
                continue
            # ``pifricDecsn`` (유무상증자결정) names the same field ``piic_ic_mthn``.
            value = snapshot.payload_json.get("ic_mthn") or snapshot.payload_json.get(
                "piic_ic_mthn"
            )
            if value and (newest is None or version.rcept_no > newest[0]):
                newest = (version.rcept_no, str(value).strip())
    return newest[1] if newest else None


def _newest_readable(event: Event) -> list[FilingVersion]:
    """Versions newest-first, attachment-only 정정 skipped (§4.1)."""
    return sorted(
        (v for v in event.versions if v.correction_kind is not CorrectionKind.ATTACHMENT),
        key=lambda v: (v.rcept_dt or date.min, v.rcept_no),
        reverse=True,
    )


def confirm_warrants(
    client: DartClient | None,
    session_factory,
    *,
    fetch: bool = True,
    max_documents: int | None = None,
    include_suppressed: bool = False,
    dry_run: bool = False,
    log=None,
) -> WarrantReport:
    """Decide each ① event's 신주인수권증서 by its 본문, not by ``ic_mthn`` alone.

    The phase constraint is explicit that ``ic_mthn`` is provisional and 본문
    ``18. 신주인수권양도여부`` is the final test (N26, field-matrix §1.1). Four
    outcomes, and only one of them suppresses:

    ``confirmed``
        본문 says 양도 가능 → flag ``warrant_confirmed``. The right is real.
    ``denied``
        본문 says 양도 불가 **and** ``ic_mthn`` does not claim a 주주배정 계열 issue
        (or there is no detail row at all) → suppress ``no_warrant_bodymun``.
    ``conflict``
        본문 denies while ``ic_mthn`` is warrant-bearing → **stays live**, flagged
        ``warrant_conflict``. Never suppress on conflicting evidence.
    ``unverified``
        no 본문, or the form has no such row → flag ``warrant_unverified`` and
        change nothing. (The 제3자배정 form genuinely has no ``18.`` row, so an
        absent label is only evidence together with ``ic_mthn``.)
    """
    report = WarrantReport()
    started = client.request_count if client else 0

    with session_scope(session_factory) as session:
        query = select(Event).where(Event.rights_type == RightsType.SUBSCRIPTION_WARRANT)
        if not include_suppressed:
            # A previous run's own ``no_warrant_bodymun`` is re-derived, not
            # trusted: the newest 본문 may be a later 정정 that says otherwise.
            query = query.where(
                (Event.suppressed_reason.is_(None))
                | (Event.suppressed_reason == NO_WARRANT_REASON)
            )
        events = session.scalars(query).all()
        report.events = len(events)

        fetched = 0
        for event in sorted(events, key=lambda e: (e.corp_code, e.original_rcept_dt)):
            key = f"{event.corp_code}/{event.report_subtype}/{event.original_rcept_dt}"
            method = _ic_mthn(session, event)
            transferable = listed = None
            label_present = False
            used: FilingVersion | None = None
            span = raw = None

            for version in _newest_readable(event):
                allow = fetch and (max_documents is None or fetched < max_documents)
                try:
                    blob, origin = load_document(session, client, version, fetch=allow)
                except RequestBudgetExceeded:
                    report.budget_exhausted = True
                    report.notes.append("stopped early: live request budget exhausted (O-1)")
                    blob, origin = (None, "missing")
                    fetch = False
                if origin == "live":
                    fetched += 1
                    report.documents_fetched_live += 1
                if blob is None:
                    continue
                try:
                    doc = BodyDocument.from_bytes(blob, rcept_no=version.rcept_no)
                    labels = extract_labels(doc)
                except Exception:  # noqa: BLE001
                    continue
                used = version
                row = labels.get("warrant_transferable")
                listed_row = labels.get("warrant_certificate_listed")
                if row is not None:
                    label_present = True
                    transferable = row.value if isinstance(row.value, bool) else None
                    span = row.span.as_tuple() if row.span else None
                    raw = row.raw
                if listed_row is not None and isinstance(listed_row.value, bool):
                    listed = listed_row.value
                break  # the newest readable version is the current truth (N4)

            warrant_method = re.sub(r"\s+", "", method or "") in WARRANT_BEARING_IC_MTHN
            # This job re-derives its verdict from the newest 본문 every run, so a
            # previous run's verdict flag must not survive beside the new one.
            event.drop_flags(*WARRANT_FLAGS)
            if transferable is True:
                outcome = "confirmed"
                event.add_flag("warrant_confirmed")
                if event.suppressed_reason == NO_WARRANT_REASON:
                    event.suppressed_reason = event.suppressed_note = None
                    event.suppressed_at = None
            elif transferable is False or (label_present and transferable is None):
                if warrant_method:
                    # 본문 denies while the API's 증자방식 says a 증서-bearing issue:
                    # two sources disagreeing about whether the right exists is
                    # exactly the case that must NOT be suppressed (N20).
                    outcome = "conflict"
                    event.add_flag("warrant_conflict")
                    if event.suppressed_reason == NO_WARRANT_REASON:
                        event.suppressed_reason = event.suppressed_note = None
                        event.suppressed_at = None
                else:
                    outcome = "denied"
                    event.suppress(
                        NO_WARRANT_REASON,
                        f"본문 18. 신주인수권양도여부 = {raw or '(판독 불가)'} "
                        f"(ic_mthn={method or '미상'}, {used.rcept_no if used else '?'})",
                    )
            elif used is None:
                outcome = "unverified"
                event.add_flag("warrant_unverified")
                if event.suppressed_reason == NO_WARRANT_REASON:
                    event.suppressed_reason = event.suppressed_note = None
                    event.suppressed_at = None
            elif warrant_method:
                # No `18.` row, but the API says 주주배정 계열: the form differs, not
                # the right. Conflicting evidence → flag, never suppress (N20).
                outcome = "conflict"
                event.add_flag("warrant_conflict")
            else:
                outcome = "denied"
                event.suppress(
                    NO_WARRANT_REASON,
                    "본문에 18. 신주인수권양도여부 행이 없음 — 신주인수권 항목 자체가 없는 서식 "
                    f"(제3자배정/주주우선공모 계열). ic_mthn={method or '미상'}, "
                    f"{used.rcept_no if used else '?'}",
                )

            report.outcomes[outcome] += 1
            report.verdicts.append(
                WarrantVerdict(
                    event_key=key,
                    corp_name=event.corp.corp_name if event.corp else None,
                    rcept_no=used.rcept_no if used else None,
                    ic_mthn=method,
                    transferable=transferable,
                    certificate_listed=listed,
                    label_present=label_present,
                    outcome=outcome,
                    span=span,
                    raw=raw,
                )
            )
            if log:
                log(f"  {outcome:<10} {key} ic_mthn={method} 18.={raw}")

        if dry_run:
            session.rollback()
            report.notes.append("dry run — nothing persisted")

    report.requests = (client.request_count - started) if client else 0
    return report
