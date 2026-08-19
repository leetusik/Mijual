"""The corpus run: §3.6 layer 1 over the events the phase actually exposes.

Scope, straight from the slice plan and D-1's drop order:

* **① fields 1–5** for the ``warrant_confirmed`` events — the countdown-critical
  ones. The single ``warrant_conflict`` event (제이알글로벌리츠, N30) is read too
  when asked for, **flagged and never exposed**: ``P2.S5`` owns that decision.
* **③ field 9** for the exposable 매수청구권 events.
* **정정 재추출 + diff (field 10)** on top of both.
* **② (fields 6–8) is not run here** — ``P2.S7`` owns that corpus, and its
  countdown fields are ``API`` anyway (N6), so the LLM would be spending money on
  something already deterministic.

Two invariants hold everywhere in this module:

**Nothing deterministic is paid for.** Documents come from stored snapshots
(zero OpenDART requests), the 정정사항 rows come from :mod:`mijual.bodydoc`, and
the value diff between two versions is computed here in Python. The model is
asked only for prose no parser can read.

**A re-run costs nothing.** A ``(version, field, schema_version)`` already stored
is skipped unless ``refresh=True``, so the normal recovery from a budget stop —
run again — spends only on what is missing (N34's rule, applied to money instead
of quota).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.bodydoc.correction import parse_correction
from mijual.bodydoc.document import BodyDocument
from mijual.db.models import (
    CorrectionKind,
    Event,
    Extraction,
    FilingVersion,
    RightsType,
    Snapshot,
)
from mijual.db.session import session_scope
from mijual.extract.client import CallBudgetExceeded, CallResult, GeminiClient
from mijual.extract.fields import FIELDS, SCHEMA_VERSION, TASKS, response_schema
from mijual.extract.inputs import build_input
from mijual.extract.locate import QuoteLocator
from mijual.extract.prompt import build_correction_prompt, build_field_prompt
from mijual.extract.store import existing_fields, record_call, upsert_extraction

__all__ = [
    "ExtractionReport",
    "relocate_spans",
    "run_corrections",
    "run_extraction",
    "select_targets",
]

#: Which task reads which rights type.
TASK_BY_RIGHTS = {
    RightsType.SUBSCRIPTION_WARRANT: "r1_prose",
    RightsType.APPRAISAL_RIGHT: "r3_prose",
    RightsType.CONVERTIBLE_OVERHANG: "r2_prose",
}
#: How much of a deterministic 정정 cell is kept inside the stored JSON.
STORED_CELL_LIMIT = 1_000


@dataclass
class ExtractionReport:
    """What one run read, resolved, skipped and spent."""

    task: str = ""
    events: int = 0
    documents: int = 0
    calls: int = 0
    call_failures: int = 0
    skipped_versions: int = 0
    missing_documents: list[str] = field(default_factory=list)
    per_field: dict[str, Counter] = field(default_factory=dict)
    budget_exhausted: bool = False
    prompt_tokens: int = 0
    thoughts_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    notes: list[str] = field(default_factory=list)
    planned_chars: int = 0

    def count(self, field_key: str, *keys: str) -> None:
        counter = self.per_field.setdefault(field_key, Counter())
        for key in keys:
            counter[key] += 1

    def render(self) -> str:
        lines = [
            f"task       : {self.task}",
            f"targets    : {self.events} event(s), {self.documents} document(s) read, "
            f"{self.skipped_versions} version(s) already extracted (skipped)",
            f"calls      : {self.calls} ({self.call_failures} failed)"
            + (" — BUDGET EXHAUSTED" if self.budget_exhausted else ""),
        ]
        for key in sorted(self.per_field):
            counter = self.per_field[key]
            lines.append(
                f"  {key:<28} extracted={counter['extracted']:>3} absent={counter['absent']:>3} "
                f"span_resolved={counter['span_resolved']:>3} "
                f"span_unresolved={counter['span_unresolved']:>3} "
                f"no_quote={counter['span_no_quote']:>3} verified={counter['verified']:>3}"
            )
        if self.missing_documents:
            lines.append(
                f"no 본문    : {len(self.missing_documents)} event(s) "
                f"{self.missing_documents[:6]}"
            )
        lines.append(
            f"tokens     : prompt {self.prompt_tokens:,} + thinking {self.thoughts_tokens:,} "
            f"+ output {self.output_tokens:,} | cost ▷ ${self.cost_usd:.4f}"
        )
        lines.extend(f"note       : {n}" for n in self.notes)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# target selection
# ---------------------------------------------------------------------------
def select_targets(
    session: Session, rights: RightsType, *, include_conflict: bool = False
) -> list[Event]:
    """Exposable events of one rights type, in a stable order.

    ① is additionally restricted to the events whose **본문** confirmed the
    신주인수권증서 (``warrant_confirmed``, ``P2.S3``): ``ic_mthn`` alone never
    confirms a right (N26/N30). ``warrant_conflict`` joins only on request, and
    the caller must keep it flagged and unexposed.
    """
    events = session.scalars(
        select(Event).where(Event.rights_type == rights, Event.suppressed_reason.is_(None))
    ).all()
    if rights is RightsType.SUBSCRIPTION_WARRANT:
        wanted = {"warrant_confirmed"} | ({"warrant_conflict"} if include_conflict else set())
        events = [e for e in events if wanted & set(e.flags)]
    return sorted(events, key=lambda e: (e.corp_code, e.original_rcept_dt))


def readable_versions(event: Event) -> list[FilingVersion]:
    """Versions that can carry a 본문, newest last (첨부-only 정정 skipped, §4.1)."""
    return sorted(
        (v for v in event.versions if v.correction_kind is not CorrectionKind.ATTACHMENT),
        key=lambda v: (v.rcept_dt or date.min, v.rcept_no),
    )


def document_of(session: Session, version: FilingVersion) -> tuple[Snapshot, BodyDocument] | None:
    """Newest stored 본문 snapshot of a version, decoded. Zero requests."""
    snapshot = session.scalar(
        select(Snapshot)
        .where(Snapshot.filing_version_id == version.id, Snapshot.source == "document")
        .order_by(Snapshot.captured_at.desc())
        .limit(1)
    )
    if snapshot is None or not snapshot.payload_bytes:
        return None
    try:
        return (snapshot, BodyDocument.from_bytes(snapshot.payload_bytes, rcept_no=version.rcept_no))
    except Exception:  # noqa: BLE001 - a bad body must not stop a corpus run
        return None


# ---------------------------------------------------------------------------
# one document, one task
# ---------------------------------------------------------------------------
def extract_document(
    session: Session,
    client: GeminiClient,
    version: FilingVersion,
    snapshot: Snapshot,
    doc: BodyDocument,
    task_key: str,
    report: ExtractionReport,
) -> CallResult | None:
    """Read one task's fields out of one document and store them with spans."""
    task = TASKS[task_key]
    document = build_input(doc, task=task)
    prompt = build_field_prompt(task, document)
    report.planned_chars += document.chars

    result = client.generate_json(
        prompt=prompt, schema=response_schema(task), task=task_key
    )
    if result.status == "dry_run":
        report.calls += 1
        return result

    call = record_call(
        session,
        result,
        event_id=version.event_id,
        filing_version_id=version.id,
        schema_version=SCHEMA_VERSION,
        prompt_version=task.prompt_version,
        input_scope=document.scope,
        input_chars=document.chars,
    )
    report.calls += 1
    report.prompt_tokens += result.usage.prompt_tokens
    report.thoughts_tokens += result.usage.thoughts_tokens
    report.output_tokens += result.usage.output_tokens
    report.cost_usd += result.cost_usd

    if not result.ok:
        report.call_failures += 1
        for spec in task.specs:
            report.count(spec.key, "error")
            upsert_extraction(
                session,
                version,
                field_key=spec.key,
                schema_version=SCHEMA_VERSION,
                status="error",
                snapshot_id=snapshot.id,
                call=call,
                input_scope=document.scope,
                model=result.model,
                model_version=result.model_version,
                prompt_version=task.prompt_version,
                model_note=result.error,
            )
        return result

    locator = QuoteLocator(document.flat, doc)
    payload = (result.payload or {}).get("fields") or {}
    for spec in task.specs:
        envelope = payload.get(spec.key) or {}
        present = bool(envelope.get("present"))
        quote = envelope.get("quote")
        value = envelope.get("value") if present else None
        located = locator.locate(quote) if present else None

        status = "extracted" if present and value is not None else "absent"
        report.count(spec.key, status)
        if located is not None:
            report.count(spec.key, f"span_{located.status}")
            if located.verified:
                report.count(spec.key, "verified")
            if located.method:
                report.count(spec.key, f"method_{located.method}")

        upsert_extraction(
            session,
            version,
            field_key=spec.key,
            schema_version=SCHEMA_VERSION,
            status=status,
            value=value,
            quote=quote,
            located=located,
            snapshot_id=snapshot.id,
            call=call,
            input_scope=document.scope,
            model=result.model,
            model_version=result.model_version,
            prompt_version=task.prompt_version,
            model_note=envelope.get("note"),
        )
    return result


def run_extraction(
    client: GeminiClient,
    session_factory,
    *,
    rights: RightsType = RightsType.SUBSCRIPTION_WARRANT,
    include_conflict: bool = False,
    limit: int | None = None,
    refresh: bool = False,
    log=None,
) -> ExtractionReport:
    """Extract one rights type's prose fields across the exposable corpus."""
    task_key = TASK_BY_RIGHTS[rights]
    report = ExtractionReport(task=task_key)

    with session_scope(session_factory) as session:
        events = select_targets(session, rights, include_conflict=include_conflict)
        if limit is not None:
            events = events[:limit]
        report.events = len(events)

        for event in events:
            loaded = None
            version = None
            for version in reversed(readable_versions(event)):  # newest 본문 wins (N4)
                loaded = document_of(session, version)
                if loaded is not None:
                    break
            if loaded is None:
                report.missing_documents.append(
                    f"{event.corp_code}/{event.original_rcept_dt}"
                )
                continue
            snapshot, doc = loaded
            report.documents += 1

            stored = existing_fields(session, version.id, SCHEMA_VERSION)
            wanted = set(TASKS[task_key].fields)
            if not refresh and wanted <= set(stored):
                report.skipped_versions += 1
                for key in wanted:
                    row = stored[key]
                    report.count(key, row.status, f"span_{row.span_status or 'none'}")
                    if row.span_verified:
                        report.count(key, "verified")
                continue

            try:
                extract_document(
                    session, client, version, snapshot, doc, task_key, report
                )
            except CallBudgetExceeded as exc:
                report.budget_exhausted = True
                report.notes.append(f"stopped early: {exc}")
                break
            if log:
                log(f"  {event.corp_code} {version.rcept_no} {event.corp.corp_name}")

    return report


def relocate_spans(session_factory, *, log=None) -> ExtractionReport:
    """Re-run the **deterministic** locator over every stored quote. Zero calls.

    Span resolution is a pure function of (quote, stored snapshot), so improving
    it must never mean paying for the extraction again. This re-derives every
    span — row-level and the per-change spans inside a 정정 interpretation — and
    reports what moved. It is also the honest way to re-check citations after a
    snapshot is re-collected: if a document changed under a stored span, the
    quote stops locating and the row goes ``unresolved`` instead of pointing at
    the wrong characters.
    """
    report = ExtractionReport(task="relocate")
    with session_scope(session_factory) as session:
        rows = session.scalars(
            select(Extraction).where(Extraction.quote.isnot(None))
        ).all()
        report.events = len(rows)
        for row in rows:
            snapshot = session.get(Snapshot, row.snapshot_id) if row.snapshot_id else None
            if snapshot is None or not snapshot.payload_bytes:
                report.count(row.field_key, "no_snapshot")
                continue
            try:
                doc = BodyDocument.from_bytes(snapshot.payload_bytes, rcept_no=row.rcept_no)
            except Exception:  # noqa: BLE001
                report.count(row.field_key, "unreadable")
                continue
            spec = FIELDS.get(row.field_key)
            document = build_input(doc, spec=spec)
            locator = QuoteLocator(document.flat, doc)

            located = locator.locate(row.quote)
            before = (row.span_status, row.span_start, row.span_end)
            row.span_status = located.status
            row.locate_method = located.method
            row.span_verified = located.verified
            row.span_start = located.span.start if located.span else None
            row.span_end = located.span.end if located.span else None
            report.count(row.field_key, f"span_{located.status}")
            if before != (row.span_status, row.span_start, row.span_end):
                report.count(row.field_key, "changed")
                if log:
                    log(f"  {row.rcept_no} {row.field_key}: {before} -> "
                        f"({row.span_status}, {row.span_start}, {row.span_end})")

            value = row.value if isinstance(row.value, dict) else None
            changes = ((value or {}).get("interpretation") or {}).get("changes")
            if changes:
                for change in changes:
                    sub = locator.locate(change.get("quote"))
                    change["span"] = sub.span.as_tuple() if sub.span else None
                    change["span_status"] = sub.status
                    change["locate_method"] = sub.method
                    change["span_verified"] = sub.verified
                    report.count("correction_change", f"span_{sub.status}")
                # JSON columns are replaced, not mutated in place.
                row.value = dict(value or {})
        session.flush()
    return report


# ---------------------------------------------------------------------------
# 정정 재추출 + diff (§7 #10)
# ---------------------------------------------------------------------------
def _stored_value(row: Extraction | None) -> Any:
    return row.value if row is not None and row.status == "extracted" else None


def field_moves(
    old: dict[str, Extraction], new: dict[str, Extraction], keys: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Prose-value differences between two versions — computed, not asked for.

    The deterministic 정정사항 rows say *what the filer changed*; this says *what
    changed in the values the product will publish*, which is not the same list
    (a filer restates unchanged rows, and a prose rewrite can move a date without
    a row naming it). Both go into the prompt as fact.
    """
    moves: list[dict[str, Any]] = []
    for key in keys:
        before, after = _stored_value(old.get(key)), _stored_value(new.get(key))
        if before == after:
            continue
        moves.append(
            {
                "field_key": key,
                "old": before,
                "new": after,
                "old_rcept_no": old[key].rcept_no if key in old else None,
                "new_rcept_no": new[key].rcept_no if key in new else None,
                "new_span": new[key].span if key in new else None,
                "new_span_status": new[key].span_status if key in new else None,
            }
        )
    return moves


def _norm(text: Any) -> str:
    return re.sub(r"\s+", "", str(text or ""))


def check_against_items(
    changes: list[dict[str, Any]], items: list[dict[str, Any]]
) -> dict[str, Any]:
    """Does the model's story agree with the deterministic 정정사항 rows?

    The rows are ground truth for *what changed*; the model interprets them. So a
    change the rows do not support is recorded as ``unsupported`` (a finding for
    ``P2.S5``/``P2.S9``, not a crash), and a row the model ignored is recorded as
    ``uncovered``. Neither is corrected here — the extractor does not rewrite the
    model, it measures it.
    """
    covered: set[int] = set()
    unsupported = 0
    for change in changes:
        item_key = _norm(change.get("item"))
        new_key = _norm(change.get("new"))
        matched = None
        for index, item in enumerate(items):
            row_item = _norm(item.get("item"))
            if item_key and row_item and (item_key in row_item or row_item in item_key):
                matched = index
                break
            if new_key and len(new_key) >= 4 and new_key in _norm(item.get("after")):
                matched = index
                break
        if matched is None:
            unsupported += 1
            change["supported"] = False
        else:
            covered.add(matched)
            change["supported"] = True
            change["deterministic_item"] = matched
    return {
        "items": len(items),
        "changes": len(changes),
        "unsupported": unsupported,
        "uncovered": len(items) - len(covered),
    }


def _items_of(doc: BodyDocument) -> list[dict[str, Any]]:
    """Deterministic ``3. 정정사항`` rows that actually changed, with their spans."""
    block = parse_correction(doc)
    out: list[dict[str, Any]] = []
    for item in block.changed_items:
        out.append(
            {
                "item": item.item,
                "reason": item.reason,
                "before": item.before[:STORED_CELL_LIMIT],
                "after": item.after[:STORED_CELL_LIMIT],
                "before_span": item.before_span.as_tuple() if item.before_span else None,
                "after_span": item.after_span.as_tuple() if item.after_span else None,
            }
        )
    return out


def run_corrections(
    client: GeminiClient,
    session_factory,
    *,
    rights: RightsType = RightsType.SUBSCRIPTION_WARRANT,
    include_conflict: bool = False,
    limit: int | None = None,
    refresh: bool = False,
    extract_previous: bool = True,
    log=None,
) -> ExtractionReport:
    """Re-extract prose on the newest 정정 and interpret what moved (§7 #10)."""
    task = TASKS["correction"]
    prose_task = TASKS[TASK_BY_RIGHTS[rights]]
    report = ExtractionReport(task="correction")

    with session_scope(session_factory) as session:
        events = select_targets(session, rights, include_conflict=include_conflict)
        pairs: list[tuple[Event, FilingVersion, FilingVersion]] = []
        for event in events:
            with_doc = [
                v for v in readable_versions(event) if document_of(session, v) is not None
            ]
            if len(with_doc) >= 2:
                pairs.append((event, with_doc[-2], with_doc[-1]))
        if limit is not None:
            pairs = pairs[:limit]
        report.events = len(pairs)

        for event, previous, newest in pairs:
            new_loaded = document_of(session, newest)
            old_loaded = document_of(session, previous)
            if new_loaded is None or old_loaded is None:  # pragma: no cover - filtered above
                continue
            new_snapshot, new_doc = new_loaded
            report.documents += 1

            try:
                # The old version's prose values are half of the diff, so they are
                # extracted too — once. A later run reuses them for free.
                if extract_previous:
                    stored_old = existing_fields(session, previous.id, SCHEMA_VERSION)
                    if not set(prose_task.fields) <= set(stored_old):
                        old_snapshot, old_doc = old_loaded
                        extract_document(
                            session,
                            client,
                            previous,
                            old_snapshot,
                            old_doc,
                            prose_task.key,
                            report,
                        )

                stored_new = existing_fields(session, newest.id, SCHEMA_VERSION)
                if "correction_interpretation" in stored_new and not refresh:
                    report.skipped_versions += 1
                    row = stored_new["correction_interpretation"]
                    report.count(
                        "correction_interpretation", row.status, f"span_{row.span_status or 'none'}"
                    )
                    continue

                items = _items_of(new_doc)
                old_rows = existing_fields(session, previous.id, SCHEMA_VERSION)
                moves = field_moves(old_rows, stored_new, prose_task.fields)

                document = build_input(new_doc, spec=FIELDS["correction_interpretation"])
                prompt = build_correction_prompt(
                    task,
                    document,
                    items=items,
                    field_moves=moves,
                    old_rcept_no=previous.rcept_no,
                    new_rcept_no=newest.rcept_no,
                )
                report.planned_chars += document.chars
                result = client.generate_json(
                    prompt=prompt, schema=response_schema(task), task="correction"
                )
            except CallBudgetExceeded as exc:
                report.budget_exhausted = True
                report.notes.append(f"stopped early: {exc}")
                break

            if result.status == "dry_run":
                report.calls += 1
                continue

            call = record_call(
                session,
                result,
                event_id=event.id,
                filing_version_id=newest.id,
                schema_version=SCHEMA_VERSION,
                prompt_version=task.prompt_version,
                input_scope=document.scope,
                input_chars=document.chars,
            )
            report.calls += 1
            report.prompt_tokens += result.usage.prompt_tokens
            report.thoughts_tokens += result.usage.thoughts_tokens
            report.output_tokens += result.usage.output_tokens
            report.cost_usd += result.cost_usd

            envelope = ((result.payload or {}).get("fields") or {}).get(
                "correction_interpretation"
            ) or {}
            value = envelope.get("value") if result.ok else None
            locator = QuoteLocator(document.flat, new_doc)

            changes = list((value or {}).get("changes") or [])
            for change in changes:
                located = locator.locate(change.get("quote"))
                change["span"] = located.span.as_tuple() if located.span else None
                change["span_status"] = located.status
                change["locate_method"] = located.method
                change["span_verified"] = located.verified
            checked = check_against_items(changes, items)

            top = locator.locate(envelope.get("quote"))
            if not top.resolved:
                for change in changes:
                    if change.get("span"):
                        top = locator.locate(change.get("quote"))
                        break

            stored_value = {
                "old_rcept_no": previous.rcept_no,
                "new_rcept_no": newest.rcept_no,
                "deterministic_items": items,
                "field_moves": moves,
                "interpretation": value,
                "deterministic_check": checked,
            }
            status = "extracted" if result.ok and (items or moves or changes) else "absent"
            report.count("correction_interpretation", status)
            report.count(
                "correction_interpretation",
                "span_resolved" if top.resolved else "span_unresolved",
            )
            if top.verified:
                report.count("correction_interpretation", "verified")
            if checked["unsupported"]:
                report.count("correction_interpretation", "unsupported_change")
            if not result.ok:
                report.call_failures += 1

            upsert_extraction(
                session,
                newest,
                field_key="correction_interpretation",
                schema_version=SCHEMA_VERSION,
                status=status if result.ok else "error",
                value=stored_value,
                quote=envelope.get("quote"),
                located=top,
                snapshot_id=new_snapshot.id,
                call=call,
                input_scope=document.scope,
                model=result.model,
                model_version=result.model_version,
                prompt_version=task.prompt_version,
                model_note=envelope.get("note") or result.error,
            )
            if log:
                log(
                    f"  {event.corp_code} {previous.rcept_no} -> {newest.rcept_no} "
                    f"items={len(items)} moves={len(moves)} changes={len(changes)} "
                    f"unsupported={checked['unsupported']}"
                )

    return report
