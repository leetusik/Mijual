"""Idempotent upserts for the collection schema, and **which version is read**.

Storage-side only: re-running a collection must never duplicate an event, a
version or an unchanged snapshot. **Collector/polling logic belongs to
``P2.S2``** — this module knows nothing about windows, paging or 정정 discovery.

``P5.S3`` added the second half: :func:`readable_versions` / :func:`document_of`
/ :func:`current_version` — the rule that decides **which stored version of an
event the product reads**. They lived in :mod:`mijual.extract.runner`, where the
gates and the exposure contract had to reach them through a function-local import
because importing that module pulls the whole extractor tree (model client
included) into whatever imports it. Serving reads the same rule on a request
path, so it now lives here, in a neutral home that spends nothing:
:mod:`mijual.extract.runner` re-exports both names, and every existing caller is
unchanged.

**Never fork this rule.** A superseded version's values are true about superseded
facts; a countdown that falls back to one is a wrong number (N4). One
implementation, one place.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.bodydoc.document import BodyDocument
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

__all__ = [
    "current_document",
    "current_version",
    "current_versions",
    "document_of",
    "document_snapshot",
    "ensure_corp",
    "ensure_event",
    "ensure_snapshot",
    "ensure_version",
    "readable_versions",
    "versions_with_document",
]


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


# ---------------------------------------------------------------------------
# which version the product reads (moved here by P5.S3 — see the module docstring)
# ---------------------------------------------------------------------------
def readable_versions(event: Event) -> list[FilingVersion]:
    """Versions that can carry a 본문, newest last (첨부-only 정정 skipped, §4.1)."""
    return sorted(
        (v for v in event.versions if v.correction_kind is not CorrectionKind.ATTACHMENT),
        key=lambda v: (v.rcept_dt or date.min, v.rcept_no),
    )


def document_snapshot(session: Session, version: FilingVersion) -> Snapshot | None:
    """Newest stored 본문 snapshot of a version, **not** decoded. Zero requests."""
    return session.scalar(
        select(Snapshot)
        .where(Snapshot.filing_version_id == version.id, Snapshot.source == "document")
        .order_by(Snapshot.captured_at.desc())
        .limit(1)
    )


def document_of(session: Session, version: FilingVersion) -> tuple[Snapshot, BodyDocument] | None:
    """Newest stored 본문 snapshot of a version, decoded. Zero requests."""
    snapshot = document_snapshot(session, version)
    if snapshot is None or not snapshot.payload_bytes:
        return None
    try:
        return (snapshot, BodyDocument.from_bytes(snapshot.payload_bytes, rcept_no=version.rcept_no))
    except Exception:  # noqa: BLE001 - a bad body must not stop a corpus run
        return None


def current_document(
    session: Session, event: Event
) -> tuple[FilingVersion, Snapshot, BodyDocument] | None:
    """The newest version with a readable 본문, **and that 본문** — one decode.

    Callers that need the document itself (the 회사명 the filing prints, the
    정정사항 table) should use this rather than calling :func:`current_version`
    and decoding again: the ZIP is large and the answer is the same one.
    """
    for version in reversed(readable_versions(event)):
        loaded = document_of(session, version)
        if loaded is not None:
            return (version, loaded[0], loaded[1])
    return None


def current_version(session: Session, event: Event) -> FilingVersion | None:
    """The newest version of the event that has a stored 본문 — the only one read.

    Identical selection to the extractor's (``P2.S4``), so the gate judges exactly
    the values the product would show and never a sibling version's.
    """
    loaded = current_document(session, event)
    return loaded[0] if loaded is not None else None


def versions_with_document(session: Session, version_ids: Iterable[int]) -> set[int]:
    """Which of these versions have a stored 본문 body — one query, no decoding."""
    ids = list(version_ids)
    if not ids:
        return set()
    return set(
        session.scalars(
            select(Snapshot.filing_version_id).where(
                Snapshot.filing_version_id.in_(ids),
                Snapshot.source == "document",
                Snapshot.payload_bytes.is_not(None),
            )
        ).all()
    )


def current_versions(session: Session, events: Sequence[Event]) -> dict[int, FilingVersion]:
    """:func:`current_version` for a whole page of events — two queries, no decode.

    A board request selects one version for each of several hundred events, and
    decoding several hundred 본문 ZIPs to answer "which one" would put a
    multi-second parse on a read path. So the *presence* of a stored body stands
    in for its decodability here, and the rule is otherwise the same one:
    **newest non-첨부정정 version that has a 본문**.

    The two can only disagree about a stored body that fails to decode — measured
    on the live corpus (488 exposable events, 2026-08-22): **0 disagreements**.
    And the disagreement is conservative if it ever happens: an undecodable body
    has no gate-passing extraction rows (the gate marks them ``not_evaluable``),
    so the row loses its date rather than inheriting a superseded version's.
    """
    with_body = versions_with_document(
        session, (v.id for event in events for v in event.versions)
    )
    chosen: dict[int, FilingVersion] = {}
    for event in events:
        for version in reversed(readable_versions(event)):
            if version.id in with_body:
                chosen[event.id] = version
                break
    return chosen
