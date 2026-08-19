"""Idempotent upserts for the collection schema.

Storage-side only: re-running a collection must never duplicate an event, a
version or an unchanged snapshot. **Collector/polling logic belongs to
``P2.S2``** — this module knows nothing about windows, paging or 정정 discovery.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.db.models import (
    Corp,
    CorrectionKind,
    Event,
    FilingVersion,
    RightsType,
    Snapshot,
    parse_dart_date,
    sha1_hex,
    utcnow,
)

__all__ = ["ensure_corp", "ensure_event", "ensure_version", "ensure_snapshot"]


def ensure_corp(
    session: Session,
    corp_code: str,
    *,
    corp_name: str | None = None,
    stock_code: str | None = None,
    corp_cls: str | None = None,
) -> Corp:
    corp = session.get(Corp, corp_code)
    if corp is None:
        corp = Corp(corp_code=corp_code)
        session.add(corp)
    corp.corp_name = corp_name or corp.corp_name
    corp.stock_code = stock_code or corp.stock_code
    corp.corp_cls = corp_cls or corp.corp_cls
    session.flush()
    return corp


def ensure_event(
    session: Session,
    *,
    corp_code: str,
    report_subtype: str,
    original_rcept_dt: str | date,
    rights_type: RightsType,
    report_nm: str | None = None,
) -> Event:
    """Get-or-create on the N2 key ``(corp_code, report_subtype, original_rcept_dt)``."""
    original_dt = parse_dart_date(original_rcept_dt)
    if original_dt is None:
        raise ValueError(f"unparseable original_rcept_dt: {original_rcept_dt!r}")
    event = session.scalar(
        select(Event).where(
            Event.corp_code == corp_code,
            Event.report_subtype == report_subtype,
            Event.original_rcept_dt == original_dt,
        )
    )
    if event is None:
        event = Event(
            corp_code=corp_code,
            report_subtype=report_subtype,
            original_rcept_dt=original_dt,
            rights_type=rights_type,
            report_nm=report_nm,
        )
        session.add(event)
    else:
        event.last_seen_at = utcnow()
        if report_nm and not event.report_nm:
            event.report_nm = report_nm
    session.flush()
    return event


def ensure_version(
    session: Session,
    event: Event,
    *,
    rcept_no: str,
    rcept_dt: str | date | None = None,
    report_nm: str | None = None,
    correction_kind: CorrectionKind | None = None,
    declared_original_dt: str | date | None = None,
    pairing_method: str | None = None,
) -> FilingVersion:
    """Get-or-create on ``(event, rcept_no)`` — every observed version is kept."""
    version = session.scalar(
        select(FilingVersion).where(
            FilingVersion.event_id == event.id, FilingVersion.rcept_no == rcept_no
        )
    )
    if version is None:
        version = FilingVersion(
            event_id=event.id,
            rcept_no=rcept_no,
            rcept_dt=parse_dart_date(rcept_dt),
            report_nm=report_nm,
            correction_kind=correction_kind or CorrectionKind.from_report_nm(report_nm),
            declared_original_dt=parse_dart_date(declared_original_dt),
            pairing_method=pairing_method,
        )
        session.add(version)
    else:
        if declared_original_dt is not None:
            version.declared_original_dt = parse_dart_date(declared_original_dt)
        if report_nm and not version.report_nm:
            version.report_nm = report_nm
        if pairing_method and not version.pairing_method:
            version.pairing_method = pairing_method
    session.flush()
    return version


def ensure_snapshot(
    session: Session,
    version: FilingVersion,
    *,
    source: str,
    payload_json: Any | None = None,
    payload_bytes: bytes | None = None,
    captured_at: datetime | None = None,
) -> Snapshot:
    """Store one raw body. Re-storing an identical body is a no-op.

    Identity is ``(version, source, sha1(body))``: a changed body always gets a
    new row, so the old→new diff the 정정 story needs is never lost.
    """
    if (payload_json is None) == (payload_bytes is None):
        raise ValueError("exactly one of payload_json / payload_bytes is required")

    if payload_bytes is not None:
        blob = payload_bytes
        digest = sha1_hex(blob)
        size = len(blob)
    else:
        import json as _json

        canonical = _json.dumps(payload_json, ensure_ascii=False, sort_keys=True)
        digest = sha1_hex(canonical)
        size = len(canonical.encode("utf-8"))

    existing = session.scalar(
        select(Snapshot).where(
            Snapshot.filing_version_id == version.id,
            Snapshot.source == source,
            Snapshot.content_sha1 == digest,
        )
    )
    if existing is not None:
        return existing

    snapshot = Snapshot(
        filing_version_id=version.id,
        source=source,
        payload_json=payload_json,
        payload_bytes=payload_bytes,
        content_sha1=digest,
        byte_size=size,
        captured_at=captured_at or utcnow(),
    )
    session.add(snapshot)
    session.flush()
    return snapshot
