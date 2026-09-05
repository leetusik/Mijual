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
    "ConversationFeedback",
    "ConversationTurn",
    "Corp",
    "CorrectionKind",
    "EmailVerification",
    "Event",
    "Extraction",
    "ExtractionCall",
    "FilingVersion",
    "Holding",
    "LapseClaim",
    "NotificationPref",
    "NotificationSend",
    "OfferingInput",
    "OpsSession",
    "PasswordReset",
    "PerformanceReport",
    "PipelineRun",
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

    **``P13`` added one column, deliberately, and it is account *state* — not
    PII.** :attr:`verification_pending_since` says whether this account has ever
    proven control of its own mailbox, and **NULL means verified**. It is a fact
    about the account's own credential, in the same family as
    ``password_hash``; it is not a name, not an identity, and not an activity
    trail — it is written once at 가입 and cleared once at 인증, and no read ever
    touches it. The must-stay-absent list above is unchanged by it.

    That the column is nullable **with no default** is what makes P13's
    grandfathering a property of the schema rather than a migration somebody
    runs: :func:`mijual.db.schema_sync.ensure_columns` adds it as NULL to every
    existing row, and NULL is verified. There is no backfill step because there
    is nothing to back-fill.
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
    #: **NULL means verified.** Set to :func:`utcnow` **in the body of**
    #: :func:`mijual.web.auth.create_account` — never as a column ``default``,
    #: which :func:`mijual.db.schema_sync.ensure_columns` refuses — and cleared
    #: back to ``NULL`` by 인증 and by a completed password reset (both prove the
    #: mailbox). It doubles as the age of a pending signup; nothing sweeps on it.
    verification_pending_since: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    resets: Mapped[list["PasswordReset"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    verifications: Mapped[list["EmailVerification"]] = relationship(
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
    notification_sends: Mapped[list["NotificationSend"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
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


class EmailVerification(Base):
    """A single-use, expiring **6-digit** signup code, addressed by account.

    ``P13``'s grant. It is :class:`PasswordReset` with three deliberate
    differences, and each one follows from the secret being short:

    * **No ``UniqueConstraint`` on ``code_digest``, and the lookup is by
      ``account_id`` — never by digest.** A reset token is 256 bits and is
      addressed *by itself*; a 6-digit code has 10^6 values, so two accounts can
      legitimately hold the same digest under the same pepper. A unique
      constraint would turn that collision into a 500 at 가입 time. The code is
      only ever meaningful **with** the address, which is why
      :func:`mijual.web.auth.verify_code` checks the password first.
    * **An ``attempts`` counter.** A 6-digit code is guessable at scale in a way
      a token is not, so a wrong code costs an attempt and a row at
      :data:`mijual.web.auth.VERIFICATION_MAX_ATTEMPTS` is **not live** — the
      same lookup predicate that rejects expired and spent rows. This is a
      per-row counter, not cross-process login rate limiting.
    * **A resend cooldown**, read from :attr:`created_at`
      (:data:`mijual.web.auth.VERIFICATION_RESEND_COOLDOWN`). Without one,
      재전송 — and re-signup on an unverified address — is a mail-bomb aimed at
      any mailbox its owner never asked about.

    Everything else is copied from :class:`PasswordReset` exactly: the row holds
    a **digest, never the code** (keyed with ``MIJUAL_SESSION_SECRET`` through
    :func:`mijual.web.auth.token_digest`, so rotating that secret kills every
    outstanding code), ``expires_at`` bounds it, ``used_at`` makes it single-use,
    and a fresh issue supersedes the unused rows rather than adding a second live
    key.
    """

    __tablename__ = "email_verification"
    __table_args__ = (Index("ix_email_verification_account", "account_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    #: The digest of the 6-digit code. **Not unique** — see the class docstring.
    code_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    #: Wrong codes entered against this row. At the cap the row stops being live.
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    account: Mapped[Account] = relationship(back_populates="verifications")

    def __repr__(self) -> str:  # pragma: no cover - never log the code or digest
        return (
            f"<EmailVerification account={self.account_id} "
            f"used={self.used_at is not None} attempts={self.attempts}>"
        )


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


class NotificationSend(Base):
    """One 마감 임박 이메일 that was actually sent. **The idempotency record.**

    ``P4.S2`` — the D-day send. Until this table existed nothing in the product
    remembered a mail, so a second run of the notify stage (a retried beat, a
    hand-run smoke, a worker restarted at 08:31) would have mailed every reader
    again. The record is therefore written **only after the transport accepted
    the message**, and committed per message: a crash halfway through a batch
    re-sends nothing it already sent.

    **The key is one deadline occurrence per reader: ``(account, event, lead_day,
    anchor_date)``.**

    * ``lead_day`` is which 시점 칩 fired (7 / 3 / 1 / 0), so a reader who chose
      7일 **and** 1일 gets two mails about the same deadline — which is what they
      asked for — and never two for one chip;
    * ``anchor_date`` is the governing 마감 as it stood when the mail went out
      (``countdown.date``). **A 정정 that moves the date is a new deadline and
      sends again**, deliberately: the whole point of the alert is the date, and
      a reader told "D-7 = 9월 9일" who is never told the deadline moved to 9월
      3일 has been actively misled. A 정정 that leaves the date alone re-uses the
      same key and sends nothing.

    ``rcept_no`` is carried beside the key as the **filing the mail cited** — the
    footer's 출처 — and is not part of the key, because an ``rcept_no`` mutates to
    its newest version when a 정정 lands (N2) and a key that moved with it would
    re-send every deadline on every correction.

    **The one caveat, stated rather than discovered later:** ``event_id`` is an
    internal autoincrement, and a full corpus rebuild (``reset_schema``, N16) does
    not preserve it — so a rebuild can cost one repeated mail per live deadline
    per reader. That is the accepted trade for a key that is stable against 정정;
    :class:`Holding` keeps ``corp_code`` un-FK'd for the opposite reason (a
    holding must *survive* a rebuild), and a sent-mail record has no such duty.

    **What is deliberately absent: the address, the subject and the body.** The
    address is :attr:`Account.email` and is not copied here (`security`: stored
    PII is exactly email + password hash), and storing what a mail *said* would
    put reader-facing prose in a table nothing renders.
    """

    __tablename__ = "notification_send"
    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "event_id",
            "lead_day",
            "anchor_date",
            name="uq_notification_send_once",
        ),
        Index("ix_notification_send_account", "account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("event.id", ondelete="CASCADE"), nullable=False
    )
    #: The filing the mail's 출처 footer cited, at send time. Not part of the key.
    rcept_no: Mapped[str | None] = mapped_column(String(14))
    #: Which 시점 칩 fired: 7 / 3 / 1 / 0 (``mijual.web.portfolio.LEAD_DAY_CHOICES``).
    lead_day: Mapped[int] = mapped_column(Integer, nullable=False)
    #: The governing 마감 as an ISO calendar day, stored **exactly as the payload
    #: served it** (``countdown.date``) so the key cannot drift on formatting.
    anchor_date: Mapped[str] = mapped_column(String(10), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    account: Mapped[Account] = relationship(back_populates="notification_sends")

    def __repr__(self) -> str:  # pragma: no cover - never log the address
        return (
            f"<NotificationSend account={self.account_id} event={self.event_id} "
            f"D-{self.lead_day} {self.anchor_date}>"
        )


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


# ---------------------------------------------------------------------------
# P5.S9 — 운영 관제 (R7). The operator's door, and the pipeline's own record.
# ---------------------------------------------------------------------------
class OpsSession(Base):
    """One logged-in **operator** session. Deliberately unrelated to everything.

    R7 §6.4 and `security` require the operator credential to have *no join* to
    the reader account table and no admin flag on a reader row. That promise is
    kept the same way the 계정↔대화 promise is: **structurally**. This table has
    no ``account_id``, no foreign key, and no operator identifier at all — the
    credential lives in the deployment environment
    (:attr:`mijual.config.Settings.ops_id`), so storing a copy of the ID here
    would add an identifier that buys nothing and can leak. A row means "somebody
    proved they hold the operator credential"; that is the whole fact.

    ``token_digest`` is a digest of the cookie value, never the value, keyed with
    ``MIJUAL_SESSION_SECRET`` exactly as :class:`AuthSession` is — so one rotation
    of that key logs out readers *and* operators, which is the lever you want in
    the hour you discover a database dump.

    The cookie is **``mj_ops``**, not ``mj_session``: `security` requires the two
    to be differently named, and ``P5.S7`` reserved the name so the two could not
    collide by accident.
    """

    __tablename__ = "ops_session"
    __table_args__ = (UniqueConstraint("token_digest", name="uq_ops_session_token"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    #: Absolute expiry, never extended on a read (the reader session's rule, and
    #: for the same reason: extending it would make a GET write). An operator
    #: session is deliberately much shorter than a reader's — see
    #: :data:`mijual.web.ops.OPS_SESSION_LIFETIME`.
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OpsSession until={self.expires_at}>"


class PipelineRun(Base):
    """One scheduled or hand-fired pipeline run — R7's 최근 실행 표, persisted.

    R7's 개요 tab requires a 최근 실행 표 with per-stage counts, request/call spend
    and the ▷ cost line, and "**스케줄된 beat가 안 돌았으면 「실행 기록 없음」 행을
    alert 잉크로**". None of that was derivable before this table existed: a run
    printed its summary to a worker log and the record died with the process. This
    is backing work the design implies (D-15's rule), not a rendering choice.

    Three properties worth stating, because each one is a decision:

    * **The row is opened when the run starts and closed when it ends.** A run
      that crashes therefore leaves a row with ``finished_at`` NULL rather than
      no row at all — an unfinished run is exactly the thing an operator needs to
      see, and it is also what gives the lock chip an honest 시작 시각 while a run
      holds the lock.
    * **Every number comes from the run's own report.** ``stages`` is
      :meth:`mijual.scheduler.pipeline.StageResult.as_dict` verbatim and
      ``spend_line`` is the very line ``PipelineResult.render()`` prints, ▷ and
      all — R7: "▷는 파이프라인 출력 verbatim … admin에서 「추정」으로 바꿔치기
      금지 (경계 = 출처)". Nothing here is re-derived from the corpus.
    * **A skipped run writes no row.** A run that could not take the lock did
      nothing; the lock chip is where contention shows up, and a row for it would
      make the 최근 실행 표 count non-runs as runs.
    """

    __tablename__ = "pipeline_run"
    __table_args__ = (Index("ix_pipeline_run_started", "started_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    #: ``daily-morning`` / ``weekly-resync`` / ``cli`` … — the run's own label.
    label: Mapped[str | None] = mapped_column(String(60))
    #: ``beat`` | ``manual`` — see :attr:`mijual.scheduler.config.PipelineConfig.trigger`.
    trigger: Mapped[str | None] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    #: NULL while the run is in flight, and permanently NULL if it never finished.
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    seconds: Mapped[float | None] = mapped_column(Float)

    window_bgn: Mapped[str | None] = mapped_column(String(8))
    window_end: Mapped[str | None] = mapped_column(String(8))
    #: ``PipelineConfig.describe()`` — counts and ceilings, never a URL (N-secret).
    config_line: Mapped[str | None] = mapped_column(Text)
    #: ``redis`` | ``file`` | ``none``.
    lock: Mapped[str | None] = mapped_column(String(20))
    ok: Mapped[bool | None] = mapped_column(Boolean)

    requests: Mapped[int | None] = mapped_column(Integer)
    calls: Mapped[int | None] = mapped_column(Integer)
    #: ▷ estimate, summed from the run's stages — the same figure the CLI prints.
    cost_usd: Mapped[float | None] = mapped_column(Float)
    #: The run's own spend line, verbatim (``spend     : … ▷ $0.0000 estimated``).
    spend_line: Mapped[str | None] = mapped_column(Text)

    #: One entry per stage: name, status, summary, requests, calls, cost, seconds,
    #: and the stage's own ``detail`` counts.
    stages: Mapped[dict | list | None] = mapped_column(JSONBody)
    notes: Mapped[dict | list | None] = mapped_column(JSONBody)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PipelineRun {self.label} {self.started_at} ok={self.ok}>"


# ---------------------------------------------------------------------------
# P6.S1 — 익명 대화 저장소 (R6-6 / R7 §대화 로그). Rows about a *conversation*,
# never about a person: the two tables below are the implementation of
# 「대화는 익명으로 저장됩니다 (품질 점검용)」.
# ---------------------------------------------------------------------------
class ConversationTurn(Base):
    """One AI 질문 turn — the question, the reply, and what backed it.

    **R7 §대화 로그 signs this column list**, so it is transcribed rather than
    designed: *세션 = 익명 해시 · 시각 KST · 범위 (이벤트 rcept_no 또는 전체) ·
    질문 · 답변/거절 · 거절 카테고리 (가족 5종) · 근거 rcept_no 목록 · 인용 칩
    원문*. Nothing is dropped and nothing else is added.

    **What is absent is the promise.** R7: 「계정·이메일·IP·UA 컬럼은 저장하지
    않음 — 표시 정책이 아니라 스키마」, and 「계정↔대화 연결 컴럼·조인·추정 매칭
    금지」. So this table has **no** ``account_id``, no foreign key of any kind, no
    email, no IP, no user agent, and no column a later join could be built on —
    the same structural absence :class:`OpsSession` uses for the operator door and
    :class:`Account` refuses in the other direction.
    ``tests/test_web_conversations.py`` walks these columns and asserts it, so the
    promise is checked rather than remembered.

    ``session_hash`` is an **opaque random handle** minted by
    :func:`mijual.web.conversationstore.new_session_hash` — never derived from an
    address, an agent string or an account, because hashing an identifier would
    smuggle the forbidden join back in as a lookup. It groups turns into a thread
    (R7's 익명 세션 집계면 is exactly a ``GROUP BY`` on it) and identifies nobody.

    Three column choices worth stating:

    * **``scope_rcept_no`` is NULL for 전체 공시**, and carries the event's
      ``rcept_no`` when the reader asked inside one event. The panel renders the
      signed 「전체 공시」 for the NULL case
      (:data:`mijual.web.conversationstore.SCOPE_ALL_KO`); the column stores the
      fact, not the copy.
    * **``evidence`` and ``quotes`` are two lists, exactly as R7 lists them** —
      근거 rcept_no 목록 and 인용 칩 원문. Quotes are stored **verbatim**: R6
      forbids a reconstructed quote, and a stored summary would make the log's
      대화 재생 a paraphrase of what the reader saw.
    * **``blocks`` — added by R16, and the one thing beyond prose this table
      keeps.** P6 answered its Open Question 1 with 「a turn keeps the prose the
      reader saw and nothing more」; R16 superseded exactly that line for
      *structured blocks the prose cannot carry* (result.md §3-15) and nothing
      else — it is still no portfolio, no holdings and no raw tool payload, only
      the blocks the reader was actually shown.

    ``kind`` is constrained at the database (``answer`` | ``refusal`` — the port's
    own vocabulary). ``refusal_category`` is **not**: the family names are *signed
    Korean copy*, and copy can be re-signed, while these rows — unlike every
    pipeline table (N16) — are not re-collectable. R16 re-signing five families
    into six (보안 added, two kept read-only for past rows) cost this table nothing
    at all, which is the argument the choice was made for. The vocabulary is
    enforced on write instead
    (:func:`mijual.web.conversationstore.record_turn`), so a re-signed family
    never costs a destructive migration.
    """

    __tablename__ = "conversation_turn"
    __table_args__ = (
        CheckConstraint("kind IN ('answer', 'refusal')", name="ck_conversation_turn_kind"),
        Index("ix_conversation_turn_created", "created_at"),
        Index("ix_conversation_turn_session", "session_hash", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    #: The anonymous thread handle. Opaque, random, and a key to nothing else.
    session_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    #: Stored UTC, rendered KST by :func:`mijual.web.clock.iso` like every instant.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    #: 범위 — the event's ``rcept_no``, or NULL for 전체 공시.
    scope_rcept_no: Mapped[str | None] = mapped_column(String(14))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    #: ``answer`` | ``refusal`` (R7's 유형 filter, `P5.S9`'s query parameter).
    kind: Mapped[str] = mapped_column(String(8), nullable=False)
    #: The prose the reader saw — an answer, or the refusal's 3-part sentence.
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    #: One of the six stored families (R16: four live, two read-only for past
    #: rows), and only on a refusal.
    refusal_category: Mapped[str | None] = mapped_column(String(20))
    #: 근거 rcept_no 목록 — the filings the reply rests on.
    evidence: Mapped[dict | list | None] = mapped_column(JSONBody, nullable=False)
    #: 인용 칩 원문 — verbatim spans, never reconstructed (R6).
    quotes: Mapped[dict | list | None] = mapped_column(JSONBody, nullable=False)
    #: 구조화 블록 원형 — the turn's data/calculation blocks as the **frames** the
    #: reader received (R16 §7 계약 확장 1/2: 「프로즈로 환언하지 않는다」). A
    #: calculation's audit path — inputs, each input's 근거, the expression — does
    #: not exist in the prose, so storing only ``answer`` would lose it.
    #: **Nullable and default-free on purpose**: this repo has no Alembic (N16) and
    #: :func:`mijual.db.schema_sync.ensure_columns` adds exactly that shape to a
    #: live table — every other shape it refuses. NULL is a turn with no blocks and
    #: also every row written before R16; the two read the same, which is the
    #: honest reading of both.
    blocks: Mapped[dict | list | None] = mapped_column(JSONBody)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ConversationTurn {self.session_hash} {self.kind} {self.created_at}>"


class ConversationFeedback(Base):
    """R7's ``save_feedback`` 대기열 row: 시각 · 의견 · 답장 이메일(선택) · 원 대화.

    **``email`` is the one signed exception to "no email column"** and it earns it
    by being nothing like an identity: R6 §의견 makes it 선택 입력 for a reply
    (「선택 이메일 입력 (답장용)」) and R7 records it as 「사용자가 자발 입력한
    경우에만 값 존재」. It lives on the feedback row, it joins to nothing — least
    of all to :class:`Account`, which has its own email and must stay unreachable
    from here — and an operator replies from a mail client, outside the panel.

    ``session_hash`` is R7's 원 대화 링크: the same opaque handle
    :class:`ConversationTurn` carries, so the queue can point at the conversation
    a comment came from. It is nullable because a comment with no thread behind it
    is still the operator's to read, and the panel then renders an empty 원 대화
    cell rather than a fabricated one.

    Read-only in the panel by rule (R7: 읽기 전용 — 처리 상태 비트 없음), which is
    why there is no ``handled``/``status`` column to tempt one into existence, and
    no merge with the vocky collection (§save_feedback: 병합 금지 — 상호 링크만).
    """

    __tablename__ = "conversation_feedback"
    __table_args__ = (Index("ix_conversation_feedback_created", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    #: 의견 텍스트, as the reader typed it.
    text: Mapped[str] = mapped_column(Text, nullable=False)
    #: 답장 이메일 — present only when volunteered. 254 = the RFC 5321 limit.
    email: Mapped[str | None] = mapped_column(String(254))
    #: 원 대화 링크 (세션 해시로). Not a foreign key — the turns are a log, not a
    #: parent, and a comment must survive a thread it can no longer point at.
    session_hash: Mapped[str | None] = mapped_column(String(64))

    def __repr__(self) -> str:  # pragma: no cover - never log the comment itself
        return f"<ConversationFeedback {self.id} {self.created_at}>"
