"""Collection schema: **corp → event → filing version → snapshot**.

This shape is not a style preference; it is forced by three measured OpenDART
behaviours (field-matrix §4.2, phase note N2):

* a detail endpoint returns **one row per event — the newest version only**
  (SKC's 3 유증 filings collapse to 1 row, 디모아's 6 to 1);
* ``rcept_no`` **mutates** to the newest version, so it is not a stable key
  (only 7/39 ``estkRs.rpt_rcpn`` values still match today's ``piicDecsn``);
* the superseded version's structured values are **unrecoverable** from the API.

Therefore the event key is ``(corp_code, report_subtype, original_rcept_dt)``,
every observed ``rcept_no`` is a :class:`FilingVersion`, and every version is
:class:`Snapshot`-ed **at collection time with its raw body retained**. Without
that snapshot there is no old→new diff and the 정정 story — the product's whole
point — cannot be told.

**No Alembic in P2** (deliberate, recorded in ``P2.S1``'s ``result.md``): the
schema evolves through ``create_all`` / drop-and-recreate because every row is
re-collectable from the response cache or the API. Revisit only if P3 needs
migrations against data that cannot be rebuilt.

``P2.S4`` added the **extraction** side (:class:`ExtractionCall` /
:class:`Extraction`) at the bottom of this module: what the LLM read, where in
the stored snapshot it read it, and what the call cost. The gate columns on
:class:`Extraction` are declared nullable and unused here — they are ``P2.S5``'s
to fill.
"""

from __future__ import annotations

import enum
import hashlib
import re
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

__all__ = [
    "Base",
    "Corp",
    "CorrectionKind",
    "Event",
    "Extraction",
    "ExtractionCall",
    "FilingVersion",
    "RightsType",
    "Snapshot",
    "SnapshotSource",
    "sha1_hex",
    "parse_dart_date",
]

#: JSONB on Postgres (the real target), plain JSON elsewhere (offline tests).
#: ``none_as_null`` matters: without it a Python ``None`` is stored as the JSON
#: scalar ``'null'`` rather than SQL ``NULL``, which silently defeats
#: ``ck_snapshot_exactly_one_body``.
JSONBody = JSON(none_as_null=True).with_variant(JSONB(none_as_null=True), "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def sha1_hex(payload: bytes | str) -> str:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def parse_dart_date(value: str | date | None) -> date | None:
    """``'20260508'`` (also ``'2026-05-08'``) → ``date``."""
    if value is None or isinstance(value, date):
        return value
    text = str(value).strip().replace("-", "").replace(".", "")
    if len(text) != 8 or not text.isdigit():
        return None
    return date(int(text[:4]), int(text[4:6]), int(text[6:8]))


class RightsType(enum.Enum):
    """The MVP's three rights types (D-1 keeps all three)."""

    #: ① 유상증자 신주인수권 (증서) — the killer type, the only LLM-reading one
    SUBSCRIPTION_WARRANT = "R1"
    #: ② CB·EB 전환/교환 오버행
    CONVERTIBLE_OVERHANG = "R2"
    #: ③ 주식매수청구권 (합병·주식교환 등)
    APPRAISAL_RIGHT = "R3"


class CorrectionKind(enum.Enum):
    """What one filing version *is*, read off ``report_nm``'s bracketed prefix.

    Three buckets, chosen by **behaviour** rather than by literal prefix, so a
    new prefix never has to become a new native-PG-enum member (which would cost
    a ``reset_schema`` — see N16). ``FilingVersion.report_nm`` keeps the literal
    string, so nothing is lost.
    """

    #: No bracketed prefix — the first submission of an event.
    ORIGINAL = "original"
    #: ``[기재정정]`` (and ``[정정명령부과]``) — content correction; moves a D-day.
    DISCLOSURE = "기재정정"
    #: ``[첨부정정]`` / ``[첨부추가]`` — attachments only; no 본문 re-read (§4.1).
    ATTACHMENT = "첨부정정"

    @classmethod
    def from_report_nm(cls, report_nm: str | None) -> "CorrectionKind":
        """Prefix → kind. **Any** bracketed prefix means "not an original".

        Measured over the 2026 KOSPI+KOSDAQ 주요사항보고 list (P2.S2): besides
        ``[기재정정]``/``[첨부정정]`` the wild also carries ``[첨부추가]`` (6 rows)
        and ``[정정명령부과]`` (2). Reading an unknown prefix as ORIGINAL would
        mint a phantom event and give later corrections the wrong original date,
        so the default for an unrecognised prefix is DISCLOSURE.
        """
        match = re.match(r"\[([^\]]*)\]", (report_nm or "").lstrip())
        if match is None:
            return cls.ORIGINAL
        return cls.ATTACHMENT if "첨부" in match.group(1) else cls.DISCLOSURE


class SnapshotSource(str, enum.Enum):
    """Free-form in the column; these are the values the collector uses."""

    LIST = "list"
    DOCUMENT = "document"


class Base(DeclarativeBase):
    pass


class Corp(Base):
    """One listed issuer, keyed by OpenDART's ``corp_code``."""

    __tablename__ = "corp"

    corp_code: Mapped[str] = mapped_column(String(8), primary_key=True)
    corp_name: Mapped[str | None] = mapped_column(String(200))
    stock_code: Mapped[str | None] = mapped_column(String(6), index=True)
    #: ``Y`` KOSPI / ``K`` KOSDAQ / ``N`` KONEX / ``E`` 기타 (O-4)
    corp_cls: Mapped[str | None] = mapped_column(String(1))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    events: Mapped[list["Event"]] = relationship(back_populates="corp", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Corp {self.corp_code} {self.corp_name}>"


class Event(Base):
    """One rights event — stable across every 정정 of the same filing.

    ``report_subtype`` is the source discriminator: the detail endpoint name
    (``piicDecsn``, ``cvbdIsDecsn``, ``exbdIsDecsn``, ``cmpMgDecsn``,
    ``stkExtrDecsn``, …). ``original_rcept_dt`` is the **original** 접수일, which
    is also the window the detail endpoints filter on (N3).
    """

    __tablename__ = "event"
    __table_args__ = (
        UniqueConstraint(
            "corp_code", "report_subtype", "original_rcept_dt", name="uq_event_key"
        ),
        Index("ix_event_rights_type_dt", "rights_type", "original_rcept_dt"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    corp_code: Mapped[str] = mapped_column(
        String(8), ForeignKey("corp.corp_code", ondelete="CASCADE"), nullable=False
    )
    report_subtype: Mapped[str] = mapped_column(String(40), nullable=False)
    original_rcept_dt: Mapped[date] = mapped_column(Date, nullable=False)
    rights_type: Mapped[RightsType] = mapped_column(
        Enum(RightsType, name="rights_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )

    #: Human-readable label carried over from ``list.json`` (``report_nm`` minus
    #: the correction prefix); convenience only, never a key.
    report_nm: Mapped[str | None] = mapped_column(String(300))

    # -- P2.S2's correctness-filter outcome ------------------------------
    # Collected-but-excluded events stay in the table with a reason, so the
    # filter is auditable (and 소규모합병 suppression is itself a demo asset).
    # Nullable by design: no migration needed when S2 adds a new reason code.
    suppressed_reason: Mapped[str | None] = mapped_column(String(60))
    suppressed_note: Mapped[str | None] = mapped_column(Text)
    suppressed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    #: Comma-separated collector flags that need a human or a later slice to
    #: look — currently ``event_key_collision`` (two distinct filings share this
    #: event key: same corp, same subtype, same 접수일 — measured on 한솔테크닉스
    #: ``20260410003732`` / ``…3738``) and ``detail_conflict`` (the detail rows
    #: collapsed onto this key disagree about whether a right exists). Not a
    #: suppression: a flagged event is still exposed unless a reason is set.
    review_flags: Mapped[str | None] = mapped_column(String(200))

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    corp: Mapped[Corp] = relationship(back_populates="events")
    versions: Mapped[list["FilingVersion"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="FilingVersion.rcept_dt, FilingVersion.rcept_no",
    )

    @property
    def is_suppressed(self) -> bool:
        return self.suppressed_reason is not None

    @property
    def latest_version(self) -> "FilingVersion | None":
        """Newest version by ``(rcept_dt, rcept_no)`` — what the API would return."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: (v.rcept_dt or date.min, v.rcept_no))

    def suppress(self, reason: str, note: str | None = None) -> None:
        self.suppressed_reason = reason
        self.suppressed_note = note
        self.suppressed_at = utcnow()

    @property
    def flags(self) -> list[str]:
        return [f for f in (self.review_flags or "").split(",") if f]

    def add_flag(self, flag: str) -> None:
        if flag not in self.flags:
            self.review_flags = ",".join([*self.flags, flag])[:200]

    def drop_flags(self, *flags: str) -> None:
        """Remove flags a re-run has superseded.

        Not an exception to "never delete evidence": these are *verdicts* a job
        re-derives from scratch every run (``warrant_*``), so leaving a stale one
        beside its replacement would make the record say two things at once. The
        evidence itself — snapshots, versions, suppression reasons — is untouched.
        """
        kept = [f for f in self.flags if f not in flags]
        self.review_flags = ",".join(kept) or None

    def __repr__(self) -> str:
        return (
            f"<Event {self.corp_code}/{self.report_subtype}/{self.original_rcept_dt} "
            f"{self.rights_type.value if self.rights_type else '?'}>"
        )


class FilingVersion(Base):
    """One observed ``rcept_no`` of an event — original or 정정."""

    __tablename__ = "filing_version"
    __table_args__ = (
        UniqueConstraint("event_id", "rcept_no", name="uq_version_event_rcept_no"),
        Index("ix_filing_version_rcept_no", "rcept_no"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("event.id", ondelete="CASCADE"), nullable=False
    )
    rcept_no: Mapped[str] = mapped_column(String(14), nullable=False)
    rcept_dt: Mapped[date | None] = mapped_column(Date)
    report_nm: Mapped[str | None] = mapped_column(String(300))
    correction_kind: Mapped[CorrectionKind] = mapped_column(
        Enum(CorrectionKind, name="correction_kind", values_callable=lambda e: [m.value for m in e]),
        default=CorrectionKind.ORIGINAL,
        nullable=False,
    )
    #: ``<CORRECTION> 2. 정정대상 공시서류의 최초제출일`` — filer-entered, a *hint*
    #: for pairing, never a key (N3). Backfilled by ``P2.S3``.
    declared_original_dt: Mapped[date | None] = mapped_column(Date)
    #: What ``P2.S3``'s 본문 hint did to this version's pairing. ``pairing_method``
    #: is **left exactly as ``P2.S2`` wrote it** — evidence is relabelled, never
    #: overwritten — so the pairing's real standing is the *pair*
    #: ``(pairing_method, hint_status)``. Values: ``confirmed`` (hint equals the
    #: attached event's 접수일), ``reattached`` (hint named a different existing
    #: event of the same corp+subtype and this version was moved there),
    #: ``duplicate`` (that event already holds this ``rcept_no`` — N21's residue),
    #: ``mismatch`` (hint names no event we know), ``absent`` (a ``<CORRECTION>``
    #: block with no 최초제출일), ``no_correction_block``, ``no_document``,
    #: ``unparsed``. Plain ``VARCHAR``: a new value never costs a migration.
    hint_status: Mapped[str | None] = mapped_column(String(30))
    #: One audit line for whatever ``hint_status`` records — including the
    #: superseded pairing when a version is re-attached.
    pairing_note: Mapped[str | None] = mapped_column(Text)
    #: How this version was attached to its event (``P2.S2``): ``original``,
    #: ``earlier``/``earlier_history`` (nearest-earlier original, optionally via
    #: the corp-scoped history query), the ``_ambiguous`` variants of those,
    #: ``unpaired``/``unpaired_chain``, or ``detail_only`` (a version only the
    #: detail endpoint showed us). Plain ``VARCHAR`` on purpose — a new value
    #: must never cost a migration.
    pairing_method: Mapped[str | None] = mapped_column(String(30))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    event: Mapped[Event] = relationship(back_populates="versions")
    snapshots: Mapped[list["Snapshot"]] = relationship(
        back_populates="version", cascade="all, delete-orphan", order_by="Snapshot.captured_at"
    )

    @property
    def is_correction(self) -> bool:
        return self.correction_kind is not CorrectionKind.ORIGINAL

    @property
    def pairing_is_ambiguous(self) -> bool:
        """``P2.S2`` saw more than one plausible original and the 본문 has not settled it."""
        return "ambiguous" in (self.pairing_method or "") and not self.pairing_is_resolved

    @property
    def pairing_is_resolved(self) -> bool:
        """The 본문 ``<CORRECTION>`` hint confirmed or corrected this attachment."""
        return self.hint_status in ("confirmed", "reattached")

    def note_pairing(self, status: str, note: str | None = None) -> None:
        self.hint_status = status
        if note:
            self.pairing_note = note

    def __repr__(self) -> str:
        return f"<FilingVersion {self.rcept_no} {self.correction_kind.value}>"


class Snapshot(Base):
    """A raw body captured for one version at collection time.

    Exactly one of ``payload_json`` (API responses) / ``payload_bytes`` (본문 ZIP)
    is set. ``content_sha1`` makes re-collection idempotent: the unique
    ``(version, source, content_sha1)`` means an unchanged body never grows a
    second row, while a changed one always does.
    """

    __tablename__ = "snapshot"
    __table_args__ = (
        UniqueConstraint(
            "filing_version_id", "source", "content_sha1", name="uq_snapshot_content"
        ),
        CheckConstraint(
            "(payload_json IS NULL) <> (payload_bytes IS NULL)",
            name="ck_snapshot_exactly_one_body",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filing_version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("filing_version.id", ondelete="CASCADE"), nullable=False
    )
    #: Endpoint name (``list``, ``piicDecsn``, ``estkRs``, …) or ``document``.
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    payload_json: Mapped[dict | list | None] = mapped_column(JSONBody)
    payload_bytes: Mapped[bytes | None] = mapped_column(LargeBinary)
    content_sha1: Mapped[str] = mapped_column(String(40), nullable=False)
    byte_size: Mapped[int | None] = mapped_column(Integer)

    version: Mapped[FilingVersion] = relationship(back_populates="snapshots")

    def __repr__(self) -> str:
        return f"<Snapshot {self.source} {self.content_sha1[:8]} {self.byte_size}B>"


# ---------------------------------------------------------------------------
# P2.S4 — the extraction side (§3.6 layer 1)
# ---------------------------------------------------------------------------
class ExtractionCall(Base):
    """One LLM call: what it read, what it returned, what it cost.

    Kept separate from :class:`Extraction` because a call reads a whole document
    and yields **several** fields, while a gate verdict, a citation span and a
    re-run all belong to a single field. Splitting them means the money story
    (calls, tokens, ▷ cost) is auditable per run without duplicating it per
    field, and a field re-extracted under a new prompt version does not lose the
    accounting of the call that produced the old one.

    ``response`` keeps the model's parsed payload verbatim — including any quote
    that failed to locate — because *what the model claimed* is evidence, and a
    span this package refused to trust must still be inspectable afterwards.
    """

    __tablename__ = "extraction_call"
    __table_args__ = (Index("ix_extraction_call_version", "filing_version_id", "task"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("event.id", ondelete="CASCADE"), index=True
    )
    filing_version_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("filing_version.id", ondelete="CASCADE")
    )
    #: Which prompt this was — ``r1_prose``, ``r3_prose``, ``correction``, ``probe``.
    task: Mapped[str | None] = mapped_column(String(40))
    #: ``ok`` | ``error`` | ``invalid_json`` | ``budget`` — plain VARCHAR (N16/N27).
    status: Mapped[str | None] = mapped_column(String(20))
    error: Mapped[str | None] = mapped_column(Text)

    model: Mapped[str | None] = mapped_column(String(60))
    model_version: Mapped[str | None] = mapped_column(String(60))
    schema_version: Mapped[str | None] = mapped_column(String(20))
    prompt_version: Mapped[str | None] = mapped_column(String(20))
    #: ``document`` | ``window:<anchor>`` | ``section:<title>`` — the input regime
    #: (field-matrix §5: a 증권신고서 is never fed whole).
    input_scope: Mapped[str | None] = mapped_column(String(120))
    input_chars: Mapped[int | None] = mapped_column(Integer)

    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    thoughts_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    total_tokens: Mapped[int | None] = mapped_column(Integer)
    #: ▷ estimate from a published rate card, not a billed figure.
    cost_usd: Mapped[float | None] = mapped_column(Float)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    attempts: Mapped[int | None] = mapped_column(Integer)

    response: Mapped[dict | list | None] = mapped_column(JSONBody)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    def __repr__(self) -> str:
        return f"<ExtractionCall {self.task} {self.status} {self.total_tokens}tok>"


class Extraction(Base):
    """One extracted field of one filing version, with its citation span.

    Identity is ``(filing_version_id, field_key, schema_version)``: re-running the
    extractor under the same schema **updates in place** (a re-run never
    duplicates a row), while bumping ``schema_version`` records a new reading
    beside the old one instead of overwriting evidence.

    The span is **never** taken from the model. ``span_start``/``span_end`` are
    resolved deterministically by locating the model's verbatim ``quote`` in the
    stored snapshot through :mod:`mijual.bodydoc`; a quote that cannot be located
    leaves them ``NULL`` with ``span_status='unresolved'`` — recorded, never
    silently promoted.

    The ``gate_*`` columns are ``P2.S5``'s and are nullable and unset here, so
    the gate layer can attach a verdict + reason code without a redesign (and a
    richer per-gate history, if it needs one, can still be a separate table).
    """

    __tablename__ = "extraction"
    __table_args__ = (
        UniqueConstraint(
            "filing_version_id", "field_key", "schema_version", name="uq_extraction_field"
        ),
        Index("ix_extraction_event_field", "event_id", "field_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("event.id", ondelete="CASCADE"), nullable=False
    )
    filing_version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("filing_version.id", ondelete="CASCADE"), nullable=False
    )
    #: The document snapshot the span points into — a span is only meaningful
    #: against the exact bytes it was located in.
    snapshot_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("snapshot.id", ondelete="SET NULL")
    )
    call_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("extraction_call.id", ondelete="SET NULL")
    )
    #: Convenience for reports; the version is the authority.
    rcept_no: Mapped[str | None] = mapped_column(String(14))

    #: Canonical key from :data:`mijual.extract.fields.FIELDS` (§7's 10 targets).
    field_key: Mapped[str] = mapped_column(String(60), nullable=False)
    #: ``extracted`` (the field is in the document) | ``absent`` (the model
    #: reports it is not) | ``error`` (the call failed) — plain VARCHAR.
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="extracted")
    #: Normalized value in the shape the field's schema declares.
    value: Mapped[dict | list | None] = mapped_column(JSONBody)
    #: One-line human rendering, for reports and for the operator's eyes.
    value_summary: Mapped[str | None] = mapped_column(Text)
    #: The model's verbatim 본문 quote — kept even when it fails to locate.
    quote: Mapped[str | None] = mapped_column(Text)
    span_start: Mapped[int | None] = mapped_column(Integer)
    span_end: Mapped[int | None] = mapped_column(Integer)
    #: ``resolved`` | ``unresolved`` | ``no_quote`` | ``not_applicable``.
    span_status: Mapped[str | None] = mapped_column(String(20))
    #: How the quote was located: ``exact`` | ``nospace`` | ``trimmed``…
    locate_method: Mapped[str | None] = mapped_column(String(20))
    #: ``BodyDocument.verify(span, quote)`` — strict normalized equality (N33).
    span_verified: Mapped[bool | None] = mapped_column(Boolean)
    input_scope: Mapped[str | None] = mapped_column(String(120))
    model_note: Mapped[str | None] = mapped_column(Text)

    model: Mapped[str | None] = mapped_column(String(60))
    model_version: Mapped[str | None] = mapped_column(String(60))
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1")
    prompt_version: Mapped[str | None] = mapped_column(String(20))
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # -- P2.S5's room (declared, unused here) ------------------------------
    #: ``pass`` | ``block`` — set by the gate layer, never by the extractor.
    gate_status: Mapped[str | None] = mapped_column(String(20))
    gate_reason_code: Mapped[str | None] = mapped_column(String(60))
    gate_note: Mapped[str | None] = mapped_column(Text)
    gate_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def span(self) -> tuple[int, int] | None:
        if self.span_start is None or self.span_end is None:
            return None
        return (self.span_start, self.span_end)

    @property
    def is_citable(self) -> bool:
        """Has a value **and** a span that re-slices to the quote (N33)."""
        return self.status == "extracted" and self.span_status == "resolved"

    def __repr__(self) -> str:
        return (
            f"<Extraction {self.field_key} {self.status} span={self.span} "
            f"{self.rcept_no}>"
        )
