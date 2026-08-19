"""The corpus run: re-derive every verdict from evidence, then persist it.

**Drop and re-derive, every run** — S3's pattern (``Event.drop_flags``), applied
to verdicts. A gate verdict is a *conclusion*, not evidence: leaving a stale one
beside a fresh one would make the record say two things at once. So each run
clears the ``gate_*`` columns and the exposure state it is about to rewrite, and
recomputes them from the snapshots, the labels, the API rows and the extraction
values. Evidence itself — snapshots, extractions, quotes, spans, suppression
reasons — is never touched.

That makes the run **idempotent and free**: zero OpenDART requests, zero LLM
calls, and two consecutive runs print identical numbers. It is also the only
honest design after a re-collection: if a snapshot moved under a span, the
citation gate fails on the next run instead of silently vouching for a citation
that no longer exists.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.bodydoc import BodyDocument
from mijual.db.models import Event, Extraction, FilingVersion, RightsType, Snapshot, utcnow
from mijual.db.session import session_scope
from mijual.gates.context import VersionContext, version_context
from mijual.gates.exposure import (
    BLOCKING_FLAGS,
    current_version,
    event_exposure,
    exposure_of_all,
)
from mijual.gates.outcome import Outcome
from mijual.gates.rules import evaluate_field
from mijual.gates.withdrawal import detect_withdrawal

__all__ = ["GateReport", "gate_event", "run_gates"]

#: The flag the 철회 detector writes. Re-derived every run, like S3's ``warrant_*``.
WITHDRAWN_FLAG = "withdrawn"


@dataclass
class GateReport:
    """What one run judged — per field, per reason code, per event state."""

    events: int = 0
    versions: int = 0
    rows: int = 0
    unreadable: list[str] = field(default_factory=list)
    per_field: dict[str, Counter] = field(default_factory=dict)
    reasons: Counter = field(default_factory=Counter)
    event_states: Counter = field(default_factory=Counter)
    withdrawals: list[str] = field(default_factory=list)
    exposable_fields: Counter = field(default_factory=Counter)

    def count(self, field_key: str, outcome: Outcome) -> None:
        counter = self.per_field.setdefault(field_key, Counter())
        counter[outcome.status] += 1
        if outcome.reason_code:
            self.reasons[f"{outcome.status}:{outcome.reason_code}"] += 1

    def render(self) -> str:
        lines = [
            f"events     : {self.events} judged, {self.versions} version(s), {self.rows} field row(s)",
            f"  {'field':<28}{'passed':>7}{'tbd':>5}{'failed':>7}{'n/a':>5}",
        ]
        for key in sorted(self.per_field):
            c = self.per_field[key]
            lines.append(
                f"  {key:<28}{c['passed']:>7}{c['tbd']:>5}{c['failed']:>7}{c['not_evaluable']:>5}"
            )
        lines.append("reason codes:")
        for code, count in sorted(self.reasons.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"  {count:>4}  {code}")
        lines.append(f"event states: {dict(sorted(self.event_states.items()))}")
        if self.withdrawals:
            lines.append("withdrawn   :")
            lines.extend(f"  {w}" for w in self.withdrawals)
        if self.exposable_fields:
            lines.append(
                "exposable   : "
                + ", ".join(f"{k} {v}" for k, v in sorted(self.exposable_fields.items()))
            )
        if self.unreadable:
            lines.append(f"unreadable  : {len(self.unreadable)} {self.unreadable[:5]}")
        return "\n".join(lines)


def _documents_of(session: Session, version: FilingVersion) -> tuple[Snapshot, BodyDocument] | None:
    from mijual.extract.runner import document_of

    return document_of(session, version)


def gate_event(session: Session, event: Event, report: GateReport) -> None:
    """Judge every stored extraction of one event and refresh its exposure state.

    Every version's rows are gated — not only the current one — because each row
    is a value with its own citation and ``P2.S9`` measures all of them. Each is
    judged against **its own** document, so a superseded version's verdict is
    true about superseded values; the exposure contract simply never reads it.
    """
    versions = {v.id: v for v in event.versions}
    rows = session.scalars(
        select(Extraction).where(Extraction.event_id == event.id)
    ).all()
    contexts: dict[int, VersionContext | None] = {}
    current = current_version(session, event)

    for row in rows:
        version = versions.get(row.filing_version_id)
        if version is None:  # pragma: no cover - FK guarantees it
            continue
        if version.id not in contexts:
            loaded = _documents_of(session, version)
            contexts[version.id] = (
                version_context(
                    session,
                    event,
                    version,
                    loaded[1],
                    is_current=bool(current and current.id == version.id),
                )
                if loaded
                else None
            )
            if loaded is None:
                report.unreadable.append(version.rcept_no)
        ctx = contexts[version.id]
        if ctx is None:
            outcome = Outcome("not_evaluable", "no_document")
        else:
            outcome = evaluate_field(row, ctx)

        row.gate_status = outcome.status
        row.gate_reason_code = outcome.reason_code
        row.gate_note = outcome.note
        row.gate_checked_at = utcnow()
        report.count(row.field_key, outcome)
        report.rows += 1

    report.versions += len([c for c in contexts.values() if c is not None])

    # -- event level: the 철회 detector, then the exposure contract ---------
    event.drop_flags(WITHDRAWN_FLAG)
    withdrawal = detect_withdrawal(session, event)
    if withdrawal is not None:
        event.add_flag(WITHDRAWN_FLAG)
        report.withdrawals.append(f"{event.corp.corp_name} {withdrawal.note}")

    exposure = event_exposure(session, event)
    event.exposure_state = exposure.state
    event.exposure_reason = exposure.reason_code
    # A suppressed event can also be withdrawn (two of this corpus's four
    # withdrawals sit on `unpaired_correction` placeholders). Suppression wins the
    # state — it was never our event — but the 철회 evidence is kept beside it.
    if withdrawal is None:
        event.exposure_note = exposure.note
    elif exposure.state == "withdrawn":
        event.exposure_note = withdrawal.note
    else:
        event.exposure_note = f"{exposure.note or exposure.reason_code}; 철회 근거 {withdrawal.note}"
    event.exposure_checked_at = utcnow()
    report.event_states[f"{event.rights_type.value}:{exposure.state}"] += 1
    if exposure.exposable:
        for view in exposure.exposable_fields:
            report.exposable_fields[view.field_key] += 1
    report.events += 1


def run_gates(
    session_factory,
    *,
    rights: RightsType | None = None,
    only_exposable: bool = False,
    log=None,
) -> GateReport:
    """Gate the whole extraction corpus. Zero requests, zero calls, idempotent.

    **Every** event is visited by default, suppressed ones included, so a run
    leaves no event without a verdict (and so the 철회 detector sees the whole
    corpus — 2 of its 4 findings sit on suppressed placeholders). The whole pass
    costs ~7 s over 434 events / 364 documents; ``only_exposable`` narrows it to
    the exposure-relevant set when that matters.
    """
    report = GateReport()
    with session_scope(session_factory) as session:
        query = select(Event)
        if rights is not None:
            query = query.where(Event.rights_type == rights)
        if only_exposable:
            query = query.where(Event.suppressed_reason.is_(None))
        events = sorted(
            session.scalars(query).all(),
            key=lambda e: (e.rights_type.value, e.corp_code, e.original_rcept_dt),
        )
        for event in events:
            gate_event(session, event, report)
            if log:
                log(f"  {event.rights_type.value} {event.corp_code} {event.corp.corp_name}")
        session.flush()
    return report


def exposure_summary(session: Session, *, include_suppressed: bool = False) -> str:
    """The exposure contract's counts, regenerated from the database (N8)."""
    views = exposure_of_all(session, include_suppressed=include_suppressed)
    lines: list[str] = []
    by_state: Counter = Counter()
    by_field: Counter = Counter()
    tbd_fields: Counter = Counter()
    for view in views:
        by_state[f"{view.rights_type}:{view.state}"] += 1
        if view.exposable:
            for shown in view.exposable_fields:
                by_field[shown.field_key] += 1
                if shown.display == "추후결정":
                    tbd_fields[shown.field_key] += 1
    exposable = [v for v in views if v.exposable]
    lines.append(f"events      : {len(views)} considered, {len(exposable)} exposable")
    lines.append(f"  by state  : {dict(sorted(by_state.items()))}")
    lines.append("  fields exposable on an exposable event:")
    for key in sorted(by_field):
        extra = f" (추후결정 {tbd_fields[key]})" if tbd_fields[key] else ""
        lines.append(f"    {key:<28}{by_field[key]:>4}{extra}")
    blocked = Counter(
        v.reason_code for v in views if not v.exposable and v.reason_code
    )
    lines.append(f"  blocked   : {dict(sorted(blocked.items()))}")
    lines.append(
        "  blocking flags: "
        + ", ".join(f"{k}" for k in sorted(BLOCKING_FLAGS))
    )
    return "\n".join(lines)
