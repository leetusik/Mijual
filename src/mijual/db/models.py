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
    BigInteger,
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
    "Account",
    "AuthSession",
    "Base",
    "Corp",
    "CorrectionKind",
    "Event",
    "Extraction",
    "ExtractionCall",
    "FilingVersion",
    "Holding",
    "LapseClaim",
    "NotificationPref",
    "OfferingInput",
    "PasswordReset",
    "PerformanceReport",
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
    #: ``20260410003732`` / ``…3738``), ``detail_conflict`` (the detail rows
    #: collapsed onto this key disagree about whether a right exists) and
    #: ``withdrawn`` (``P2.S5``: a 정정사항 row retracted the decision). Not a
    #: suppression: the event keeps every snapshot and every extraction.
    review_flags: Mapped[str | None] = mapped_column(String(200))

    # -- P2.S5's exposure contract (re-derived on every gate run) ----------
    #: ``exposable`` | ``withdrawn`` | ``flagged`` | ``suppressed`` |
    #: ``no_document`` — the single verdict P3 reads. Never hand-written: it is
    #: re-derived from suppression + flags + the 철회 detector on every run, so a
    #: stale verdict cannot outlive the evidence that produced it.
    exposure_state: Mapped[str | None] = mapped_column(String(30))
    #: Why, when the state is not ``exposable`` (a flag name, a suppression
    #: reason, or ``withdrawn``). Plain VARCHAR — a new code costs no migration.
    exposure_reason: Mapped[str | None] = mapped_column(String(60))
    #: The evidence line behind the state — for ``withdrawn``, the 정정사항 row
    #: (``rcept_no``, 항목, 정정 전 → 정정 후, span) that says so.
    exposure_note: Mapped[str | None] = mapped_column(Text)
    exposure_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

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
    def is_exposable(self) -> bool:
        """The one-liner P3 filters on. Derived by :mod:`mijual.gates.exposure`."""
        return self.exposure_state == "exposable"

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
    #: ``split`` (``P5.S5``: the hint named an original this corpus does not hold,
    #: so the version was moved onto a chain head of its own instead of staying on
    #: the different 사채 nearest-earlier pairing had picked),
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
        return self.hint_status in ("confirmed", "reattached", "split")

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
    #: Thinking level this call asked for (``LOW`` … ``HIGH``); ``NULL`` means the
    #: credential's project preset was inherited. Recorded because the same prompt
    #: costs different money at different levels, so a ▷ cost figure is only
    #: comparable across runs if the level it was measured at is known
    #: (operator directive 2026-08-20, D-4 amendment). Additive nullable column —
    #: lands through ``schema_sync.ensure_columns`` (N27), no reset.
    thinking_level: Mapped[str | None] = mapped_column(String(20))
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

    The ``gate_*`` columns are ``P2.S5``'s §3.6 layer-2 verdict: ``passed`` /
    ``failed`` / ``tbd`` / ``not_evaluable`` with a reason code, re-derived from
    scratch on every gate run. Only ``passed`` and ``tbd`` are ever shown — a
    failed field is **recorded with its reason and never exposed**.
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

    # -- P2.S5, the deterministic gate (§3.6 layer 2) -----------------------
    #: ``passed`` | ``failed`` | ``tbd`` | ``not_evaluable`` — set by
    #: :mod:`mijual.gates`, never by the extractor.
    gate_status: Mapped[str | None] = mapped_column(String(20))
    #: The named reason a field is not shown (``span_unresolved``,
    #: ``method_not_enumerated``, …). :data:`mijual.gates.outcome.REASON_LABELS_KO`
    #: holds its Korean rendering.
    gate_reason_code: Mapped[str | None] = mapped_column(String(60))
    #: One audit line: every check the gate ran, in order, with its outcome.
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

    @property
    def is_exposable(self) -> bool:
        """Passed its §7 gate, or is an honest ``추후결정``. Nothing else shows."""
        return self.gate_status in ("passed", "tbd")

    def __repr__(self) -> str:
        return (
            f"<Extraction {self.field_key} {self.status} span={self.span} "
            f"{self.rcept_no}>"
        )


# ---------------------------------------------------------------------------
# P2.S8 — 증권발행실적보고서 (the 청약 결과, i.e. what actually lapsed)
# ---------------------------------------------------------------------------
class PerformanceReport(Base):
    """One 증권발행실적보고서, attached to the ① event whose 청약 it reports.

    Deliberately **not** a :class:`FilingVersion` of that event. A 실적보고서 is a
    different filing about the same offering: it is filed on the 납입일, weeks
    after the last 정정, and it carries no 유상증자결정 form. Adding it as a
    version would make it the event's ``latest_version`` — the row the gates, the
    exposure contract and the ② calendar all read as "today's reading" — and the
    countdown would then be derived from a document that has no schedule in it.
    So it is a sibling table keyed by its own ``rcept_no``, with the same
    evidence contract as :class:`Snapshot`: **the raw ZIP is retained** and
    ``content_sha1`` makes re-collection idempotent.

    ``facts`` holds every parsed number as ``{value, raw, span:[start, end]}``
    into the decoded XML of *this* report, so each figure the estimate quotes can
    be re-sliced from the stored bytes (the N33 discipline, applied to a second
    document family).
    """

    __tablename__ = "performance_report"
    __table_args__ = (
        UniqueConstraint("rcept_no", name="uq_performance_report_rcept_no"),
        Index("ix_performance_report_event", "event_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    #: ``NULL`` when the offering's 유상증자결정 is not in the corpus — the report
    #: is still evidence and is still counted, it just names its own corp.
    event_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("event.id", ondelete="SET NULL")
    )
    corp_code: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    corp_name: Mapped[str | None] = mapped_column(String(200))
    rcept_no: Mapped[str] = mapped_column(String(14), nullable=False)
    rcept_dt: Mapped[date | None] = mapped_column(Date)
    report_nm: Mapped[str | None] = mapped_column(String(300))

    #: ``standard`` (Ⅶ/Ⅷ form) | ``reit`` (집합투자증권 form) | ``none`` (no 증서
    #: table at all — an IPO, a 스팩 or a 제3자배정, kept with its reason).
    form: Mapped[str | None] = mapped_column(String(20))
    #: How the report was bound to its event: ``schedule_match`` (its own
    #: 청약개시/종료일 equal the event's 본문 ``11. 청약예정일``), ``corp_only``,
    #: ``unlinked``.
    link_status: Mapped[str | None] = mapped_column(String(30))
    link_note: Mapped[str | None] = mapped_column(Text)
    #: ``parsed`` | ``no_warrant_table`` | ``unparsed``.
    parse_status: Mapped[str | None] = mapped_column(String(30))
    parse_note: Mapped[str | None] = mapped_column(Text)
    #: Every parsed figure with its raw text and citation span.
    facts: Mapped[dict | list | None] = mapped_column(JSONBody)

    #: ``P5.S3``: this offering's **valued** outcome — one
    #: :meth:`mijual.estimate.LapseRow.as_json` mapping, written by the worker
    #: (``python -m mijual.estimate snapshot``). ``facts`` alone cannot carry it:
    #: 소멸가치 needs the 확정발행가 and the gate-passed 할인율, which live in the
    #: **유상증자결정's** 본문 and extraction rows, and reading those costs a ZIP
    #: decode that a request path must not pay. A reader serves it through
    #: :func:`mijual.present.lapse_result`, which accepts exactly this mapping.
    #: Additive nullable column — lands through ``schema_sync.ensure_columns``.
    lapse: Mapped[dict | list | None] = mapped_column(JSONBody)

    payload_bytes: Mapped[bytes | None] = mapped_column(LargeBinary)
    content_sha1: Mapped[str | None] = mapped_column(String(40))
    byte_size: Mapped[int | None] = mapped_column(Integer)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    def __repr__(self) -> str:
        return f"<PerformanceReport {self.rcept_no} {self.corp_name} {self.parse_status}>"


# ---------------------------------------------------------------------------
# P5.S3 — the serving precomputation (① money inputs)
# ---------------------------------------------------------------------------
class OfferingInput(Base):
    """One ① offering's 확정발행가 · 할인율 · 배정비율 · 청약일정, precomputed.

    **Why this table exists at all.** Everything a reader sees comes from
    persisted rows, and the ① money chain's inputs are the one part of it that is
    *not* persisted: :func:`mijual.estimate.event_inputs` reads them by decoding
    the event's stored 본문 ZIP and parsing its labels. That is a worker's job
    twice over — it costs a parse, and :mod:`mijual.estimate` imports
    :mod:`mijual.dart` / :mod:`mijual.collect` / :mod:`mijual.extract` at module
    level, so the HTTP layer may not import it at all (`architecture` boundary,
    enforced by ``tests/test_web_smoke.py``). So the worker computes and writes;
    the request path reads.

    It holds **inputs, not products**: no 소멸가치, no 환산액, no board row. Every
    figure a surface shows is still derived on read by :mod:`mijual.present`, so
    there is one derivation and this table can never disagree with it — it can
    only be *older* than the corpus, which is the freshness question the board
    already answers out loud (기준시각).

    Refreshed by ``python -m mijual.estimate snapshot`` (0 requests, 0 LLM calls).
    """

    __tablename__ = "offering_input"
    __table_args__ = (UniqueConstraint("event_id", name="uq_offering_input_event"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("event.id", ondelete="CASCADE"), nullable=False
    )
    corp_code: Mapped[str | None] = mapped_column(String(8), index=True)
    #: The 유상증자결정 version these inputs were read from (the current readable one).
    decision_rcept_no: Mapped[str | None] = mapped_column(String(14))

    #: Is a won figure permitted for this offering at all? Mirrors
    #: ``inputs["confirmed_price"] is not None`` as a column so the board can
    #: filter and count the 발행가 확정 전 state in SQL.
    price_confirmed: Mapped[bool | None] = mapped_column(Boolean)
    #: 구주주(주주배정) 청약 window — the anchor of "소멸 앞둔 신주인수권" and of the
    #: 소멸주의보 strip's earliest date. A column, not only JSON, because those two
    #: are **counted** over the whole corpus on every landing request.
    subscription_start: Mapped[date | None] = mapped_column(Date)
    subscription_end: Mapped[date | None] = mapped_column(Date)

    #: The whole :meth:`mijual.estimate.EventInputs.as_json` mapping — prices as
    #: exact decimal strings, dates as ISO days.
    inputs: Mapped[dict | list | None] = mapped_column(JSONBody)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    def __repr__(self) -> str:
        return f"<OfferingInput event={self.event_id} {self.decision_rcept_no}>"


# ---------------------------------------------------------------------------
# P5.S7 — reader accounts (R5). The first tables that hold a *person*.
# ---------------------------------------------------------------------------
class Account(Base):
    """One reader account. **Email + password hash, and nothing else.**

    Every other table in this module records a *filing*; this one records a
    person, so its column list is a security property rather than a modelling
    choice (`security` — "Stored PII for a reader account is exactly: email +
    password hash"). What is deliberately **absent**, and must stay absent
    unless a new operator signoff says otherwise:

    * no name, no phone, no brokerage or market identity;
    * no admin flag — the operator door is a **separate credential** issued in
      the deployment environment, with no join to this table (R7 §6.4), so
      ``P5.S9`` must not add one here;
    * no column that could ever join an account to a conversation. The AI 질문
      anonymity promise is structural — "the 계정 ↔ 대화 join is absent at the
      schema level" — and P6 owns the conversation storage. A ``session_hash``,
      an ``anonymous_id`` or a "last seen from" column here would quietly turn
      that promise back into a procedure;
    * no login/activity trail. ``created_at`` is 가입일, which R7's 독자 계정
      table renders; nothing else about *when a reader read* is stored, and the
      session rows below carry no IP and no user agent.

    **The FK seam ``P5.S8`` built on.** :class:`Holding`,
    :class:`NotificationPref` and :class:`LapseClaim` hang off ``account.id``
    with ``ondelete="CASCADE"`` and an ORM-side ``cascade="all, delete-orphan"``
    relationship — the same pair :class:`AuthSession` uses below. Both halves are
    needed: SQLite (the test engine) does not enforce foreign keys by default,
    and 계정 삭제 must wipe the row *and* everything hanging off it in every
    environment.

    Email is stored **normalized** (see :func:`mijual.web.auth.normalize_email`)
    and only in that form: the address a reader typed is not additionally kept,
    because two spellings of one identity are two things to leak.
    """

    __tablename__ = "account"
    __table_args__ = (UniqueConstraint("email", name="uq_account_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    #: NFKC-normalized, stripped, case-folded. 254 = the RFC 5321 address limit.
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    #: ``scrypt$n=…,r=…,p=…$<salt>$<key>`` — see :mod:`mijual.web.passwords`.
    #: The plaintext never reaches this column, a log, or an error body.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    #: 가입일 (R7's 독자 계정 table renders it).
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    #: Last credential change — a password reset or a rehash. Not an activity trail.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    resets: Mapped[list["PasswordReset"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    holdings: Mapped[list["Holding"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    lapse_claims: Mapped[list["LapseClaim"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    notification_pref: Mapped["NotificationPref | None"] = relationship(
        back_populates="account", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:  # pragma: no cover - never log the address itself
        return f"<Account {self.id}>"


class AuthSession(Base):
    """One logged-in reader session — a **server-side** row, not a signed token.

    The mechanism is a decision this slice made and recorded: logout is
    immediate and 계정 삭제 must kill access *now*, and both are trivially true
    when the session is a row (delete it / cascade it) and awkward when it is a
    self-contained signed cookie (which needs a revocation list to be revocable,
    i.e. this table anyway). The request path already loads the account from the
    database on every authenticated request, so a stateless token would have
    saved no query.

    ``token_digest`` is a **digest of the cookie value, never the value**: a
    database dump therefore contains nothing that can be replayed as a cookie.
    It is keyed with ``MIJUAL_SESSION_SECRET`` when one is configured (see
    :func:`mijual.web.auth.token_digest`), which is also why rotating that secret
    logs every reader out — a property, not a bug.

    No IP, no user agent, no "last used" column. The last one is not squeamish:
    updating it would make an authenticated **GET write**, and this phase's HTTP
    layer is built so a GET structurally cannot.
    """

    __tablename__ = "auth_session"
    __table_args__ = (
        UniqueConstraint("token_digest", name="uq_auth_session_token"),
        Index("ix_auth_session_account", "account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    token_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    #: Absolute expiry. Never extended on a read — see the class docstring.
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    account: Mapped[Account] = relationship(back_populates="sessions")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AuthSession account={self.account_id} until={self.expires_at}>"


class PasswordReset(Base):
    """A single-use, expiring password-reset grant, addressed by email.

    Stored the same way as a session: a **digest** of the token that travelled
    in the link, so the row cannot be turned back into a working link. ``used_at``
    is what makes it single-use, and it is set in the same transaction that
    changes the password.

    The *response* to a reset request never depends on whether the address
    exists (가입 여부 비노출, R5) — so the branch that finds no account writes no
    row and still answers exactly like the branch that does.
    """

    __tablename__ = "password_reset"
    __table_args__ = (
        UniqueConstraint("token_digest", name="uq_password_reset_token"),
        Index("ix_password_reset_account", "account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    token_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    account: Mapped[Account] = relationship(back_populates="resets")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PasswordReset account={self.account_id} used={self.used_at is not None}>"


# ---------------------------------------------------------------------------
# P5.S8 — 내 포트폴리오 (R5). The reader's own rows, and only ever their own.
# ---------------------------------------------------------------------------
class Holding(Base):
    """One 종목 the reader holds, and how many shares. **Nothing else.**

    A holding is an issuer and a count — no cost basis, no broker, no purchase
    date, no note. `security`'s PII boundary is about the *account*, but the same
    reasoning governs here: every column is a thing that can leak, and the product
    needs exactly two to compute a 마감 알림 and an N주 환산.

    **``corp_code`` is deliberately not a foreign key to :class:`Corp`.** The corp
    table is pipeline data — re-collectable, and reset outright when the schema
    changes (N16) — while a holding is a reader's own row that must survive that.
    A FK would make a corpus rebuild either delete a reader's portfolio or fail on
    it. The reference is validated **on write** instead
    (:func:`mijual.web.portfolio.add_holding` resolves the code through
    :func:`mijual.web.reads.stock_by_code`, so a holding always names a real
    issuer at the moment it is created), and a code that later resolves to nothing
    degrades to a row with no 회사명 and no rights rather than to a 500.

    **One row per (account, corp): a duplicate 담기 is refused, never merged.**
    Merging would invent a share count the reader never typed and replacing would
    discard one they did; R5 already ships the honest way to change a 보유량 — the
    row's inline 수정. The client holds the whole list and routes a repeat 담기 to
    that edit, so the constraint is a last-resort invariant (two tabs, one
    account) rather than a path a reader walks.

    ``shares`` is a :class:`~sqlalchemy.BigInteger` because Postgres ``integer``
    tops out at 2.1 billion and 삼성전자 alone has ~5.97 billion shares
    outstanding — a real holder of a real company must not overflow the column.
    """

    __tablename__ = "holding"
    __table_args__ = (
        UniqueConstraint("account_id", "corp_code", name="uq_holding_account_corp"),
        CheckConstraint("shares > 0", name="ck_holding_shares_positive"),
        Index("ix_holding_account", "account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    #: The DART ``corp_code`` — the stable handle every reader surface links by.
    corp_code: Mapped[str] = mapped_column(String(8), nullable=False)
    shares: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    account: Mapped[Account] = relationship(back_populates="holdings")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Holding account={self.account_id} {self.corp_code} {self.shares}>"


class NotificationPref(Base):
    """마감 임박 이메일 settings for one account — **when**, and nothing else.

    R5's 알림 설정 has three rows and only one of them is stored here:

    * **수신 주소** is the account's own email (`security`: stored PII is exactly
      email + password hash), so there is no address column — "변경" edits
      :attr:`Account.email` through :func:`mijual.web.auth.change_email`. A second
      copy of the address would be a second thing to leak and a second thing to
      keep in sync;
    * **시점 칩** (7일 / 3일 / 1일 / 당일) are :attr:`lead_days`;
    * **KakaoTalk** renders a 「예정」 chip and **no working control**, so it has
      **no column at all**. A stored flag for a channel that cannot be turned on
      would be a switch pretending to be wired up — the exact thing R5 forbids.

    **A missing row means the default, not "off".** The row is written the first
    time a reader changes the setting; until then
    :data:`mijual.web.portfolio.DEFAULT_LEAD_DAYS` (7일 + 1일, R5's own default)
    is what is served and what P4's sender must read. Creating a row at signup
    would have meant editing the auth flow to carry a preference it does not own,
    and would freeze today's default into every account ever created.

    **An empty list is a valid setting: it means no mail.** R5's mail footer
    promises "알림 설정에서 끌 수 있습니다" and deselecting every chip is the only
    off switch the signed surface offers, so the empty list must persist rather
    than fall back to the default.
    """

    __tablename__ = "notification_pref"
    __table_args__ = (
        UniqueConstraint("account_id", name="uq_notification_pref_account"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    #: Days before the governing 마감, as a sorted list out of ``(7, 3, 1, 0)``
    #: — ``0`` is 당일. ``[]`` is "no mail"; the column is never ``NULL``.
    lead_days: Mapped[dict | list | None] = mapped_column(JSONBody, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    account: Mapped[Account] = relationship(back_populates="notification_pref")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NotificationPref account={self.account_id} {self.lead_days}>"


class LapseClaim(Base):
    """챙긴 돈 (R5-8) — the reader's own claim about one past ① offering.

    "청약·매도로 챙겼습니다" is a **user assertion**, not disclosure data, and the
    separation is structural rather than careful: this table stores an account,
    a filing number and a timestamp — **no amount** — so a claim can re-label the
    reader's own row and can never reach an aggregate, a statistic or anything
    another reader sees. Nothing in :mod:`mijual.present` reads it.

    **The key is the 증권발행실적보고서's own ``rcept_no``**, and the choice
    matters. The 유상증자결정's number *mutates* to its newest version (N2), so a
    mark keyed on it would come unstuck the day a 정정 lands; an ``event.id`` is an
    internal autoincrement that a corpus rebuild does not preserve, and P5.S5
    showed versions being re-parented between events. The 실적보고서 is terminal —
    it is filed after the 청약 it reports — its ``rcept_no`` is unique
    (:class:`PerformanceReport`) and it is exactly what makes the reader's row
    exist at all: no report, no 소멸 row, no mark. It is also the key an anonymous
    or sample reader stores in ``localStorage``, because it is what the payload
    carries (``lapse.performance_rcept_no``), so both storages address one row the
    same way.
    """

    __tablename__ = "lapse_claim"
    __table_args__ = (
        UniqueConstraint(
            "account_id", "performance_rcept_no", name="uq_lapse_claim_account_report"
        ),
        Index("ix_lapse_claim_account", "account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    #: :attr:`PerformanceReport.rcept_no` — see the class docstring.
    performance_rcept_no: Mapped[str] = mapped_column(String(14), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    account: Mapped[Account] = relationship(back_populates="lapse_claims")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LapseClaim account={self.account_id} {self.performance_rcept_no}>"
