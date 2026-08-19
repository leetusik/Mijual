"""Persistence for the extraction side — idempotent by identity, not by luck.

The identity is ``(filing_version_id, field_key, schema_version)``: re-running
the extractor over the same corpus **updates rows in place**, so a second run
costs zero calls (it skips what is already there) and can never duplicate a row.
That mirrors ``P2.S1``'s ``ensure_*`` upserts (N14) and is what makes the run
safe to repeat after a budget stop, which S3 measured as the normal case (N34).

Call rows accumulate instead: every :class:`~mijual.db.models.ExtractionCall` is
kept, because the money spent is history and history is not overwritten. A field
row points at the call that last produced it.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.db.models import Extraction, ExtractionCall, FilingVersion, utcnow
from mijual.extract.client import CallResult
from mijual.extract.locate import Located

__all__ = [
    "existing_fields",
    "record_call",
    "summarize_value",
    "upsert_extraction",
]


def record_call(
    session: Session,
    result: CallResult,
    *,
    event_id: int | None,
    filing_version_id: int | None,
    schema_version: str,
    prompt_version: str,
    input_scope: str | None,
    input_chars: int | None,
) -> ExtractionCall:
    """Store one call's accounting + its raw payload (evidence, not decoration)."""
    row = ExtractionCall(
        event_id=event_id,
        filing_version_id=filing_version_id,
        task=result.task,
        status=result.status,
        error=result.error,
        model=result.model,
        model_version=result.model_version,
        schema_version=schema_version,
        prompt_version=prompt_version,
        input_scope=input_scope,
        input_chars=input_chars,
        prompt_tokens=result.usage.prompt_tokens,
        thoughts_tokens=result.usage.thoughts_tokens,
        output_tokens=result.usage.output_tokens,
        total_tokens=result.usage.total_tokens,
        cost_usd=result.cost_usd,
        latency_ms=result.latency_ms,
        attempts=result.attempts,
        response=result.payload if isinstance(result.payload, (dict, list)) else None,
    )
    session.add(row)
    session.flush()
    return row


def existing_fields(
    session: Session, filing_version_id: int, schema_version: str
) -> dict[str, Extraction]:
    """Field rows already stored for one version under one schema version."""
    rows = session.scalars(
        select(Extraction).where(
            Extraction.filing_version_id == filing_version_id,
            Extraction.schema_version == schema_version,
        )
    ).all()
    return {row.field_key: row for row in rows}


def upsert_extraction(
    session: Session,
    version: FilingVersion,
    *,
    field_key: str,
    schema_version: str,
    status: str,
    value: Any = None,
    quote: str | None = None,
    located: Located | None = None,
    snapshot_id: int | None = None,
    call: ExtractionCall | None = None,
    input_scope: str | None = None,
    model: str | None = None,
    model_version: str | None = None,
    prompt_version: str | None = None,
    model_note: str | None = None,
) -> Extraction:
    """Create or update one field row. Never duplicates; never invents a span."""
    row = session.scalar(
        select(Extraction).where(
            Extraction.filing_version_id == version.id,
            Extraction.field_key == field_key,
            Extraction.schema_version == schema_version,
        )
    )
    if row is None:
        row = Extraction(
            event_id=version.event_id,
            filing_version_id=version.id,
            field_key=field_key,
            schema_version=schema_version,
        )
        session.add(row)

    row.rcept_no = version.rcept_no
    row.snapshot_id = snapshot_id
    row.call_id = call.id if call is not None else None
    row.status = status
    row.value = value
    row.value_summary = summarize_value(value)
    row.quote = quote
    row.model_note = model_note
    row.input_scope = input_scope
    row.model = model
    row.model_version = model_version
    row.prompt_version = prompt_version
    row.extracted_at = utcnow()

    if located is None:
        row.span_start = row.span_end = None
        row.span_status = "not_applicable"
        row.locate_method = None
        row.span_verified = None
    else:
        row.span_status = located.status
        row.locate_method = located.method
        row.span_verified = located.verified
        row.span_start = located.span.start if located.span else None
        row.span_end = located.span.end if located.span else None

    # A re-extraction invalidates the previous gate verdict: the gate judges a
    # value, and the value just changed. P2.S5 re-runs; a stale verdict must not
    # look like a fresh one.
    row.gate_status = None
    row.gate_reason_code = None
    row.gate_note = None
    row.gate_checked_at = None

    session.flush()
    return row


def summarize_value(value: Any, limit: int = 400) -> str | None:
    """One human-readable line for a normalized value. Reports read this.

    Display only — ``value`` is the record. Clipping happens on a separator so a
    truncated line never shows half a number (``discount_rate=0`` for 0.2 reads
    as a wrong value, not as a clipped one).
    """
    if value is None:
        return None
    text = _render(value)
    if not text:
        return None
    if len(text) <= limit:
        return text
    cut = text.rfind(", ", 0, limit)
    return (text[:cut] if cut > limit // 2 else text[:limit]) + " …"


def _render(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool, date)):
        return str(value)
    if isinstance(value, list):
        return " · ".join(filter(None, (_render(v) for v in value)))
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            rendered = _render(item)
            if rendered:
                parts.append(f"{key}={rendered}")
        return ", ".join(parts)
    return str(value)
