"""The ``본문-label`` tier as **stored fields** — read for free, gated like any other.

``fields.py`` is §7's closed list: the ten values *no parser can read*. This
module is its mirror image — values a parser **can** read, promoted to the same
:class:`~mijual.db.models.Extraction` row shape so that the gate layer, the
exposure contract and the presentation contract need to know nothing about where
a field came from.

Why it exists, and why it is not a ``FieldSpec`` (``P5.S6`` / D-15). R3's ③ card
does not render 매수예정가 because the value was never in the exposure contract.
Measuring the corpus before adding it settled the layer question outright:

* the 본문 states it as a **form cell** — ``13. 주식매수청구권에 관한 사항`` →
  ``매수예정가격`` — in **95 of 95** stored ③ 본문 (70 with a number, 25 with ``-``),
  never twice in one document (so there is no per-주식종류 split to model);
* the ③ detail API row carries the same number in ``aprskh_plnprc``, and over
  every comparable current version (17) the two agree **17/17, 0 mismatches**.

A value with two deterministic witnesses is exactly what the phase constraint
forbids paying a model for, and what ``fields.py`` says belongs in
:mod:`mijual.bodydoc` rather than in the §7 registry. So the *reading* is
``bodydoc``'s (:func:`~mijual.bodydoc.labels.extract_labels`), the *judging* is
:mod:`mijual.gates`' (``gate_appraisal_price`` cross-checks the API value), and
what lives here is only the mapping between them:

**The citation is composed from the document's own cells, and self-checked.**
The quote is ``"<qualifier> <printed value>"`` (``매수예정가격 5,649``) — the two
adjacent cells as the flattened 본문 prints them — located with the same
:class:`~mijual.extract.locate.QuoteLocator` an LLM quote goes through, and
**accepted only if its span ends exactly where the label parser's own value cell
ends**. Measured over the whole ③ corpus: 70/70 quotes resolve with matching
ends. When they ever do not, the fall-back is the label parser's span with the
printed value as the quote (``locate_method='label'``) — a narrower citation,
never an invented one.

**An empty cell is ``absent``, not zero.** ``매수예정가격 -`` means the filing
does not state a price (a 소규모합병 grants no right at all; a 스팩 합병 defers the
price to the 증권신고서). ``status='absent'`` makes it ``not_evaluable`` in the
gate layer and therefore missing from the payload — the one shape in which a
surface renders no row at all.

**Zero calls, zero requests, idempotent.** Re-running rewrites the same rows in
place through :func:`~mijual.extract.store.upsert_extraction`, so this pass is
free to run on every pipeline beat and needs no budget of any kind.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.bodydoc.document import BodyDocument, Span
from mijual.bodydoc.labels import LabeledValue, extract_labels
from mijual.db.models import Event, FilingVersion, RightsType, Snapshot
from mijual.db.repository import document_of, readable_versions
from mijual.db.session import session_scope
from mijual.extract.fields import SCHEMA_VERSION
from mijual.extract.locate import Located, QuoteLocator
from mijual.extract.store import upsert_extraction

__all__ = [
    "LABEL_SPECS",
    "LabelFieldReport",
    "LabelFieldSpec",
    "Reading",
    "label_field_keys_for",
    "read_document",
    "read_label_fields",
]

#: Prompt-version equivalent for a deterministic reading: which reader wrote the
#: row. Bumped if the composition of the quote or the value shape changes.
READER_VERSION = "label-v1"


@dataclass(frozen=True)
class LabelFieldSpec:
    """One 본문-label field, declared the way :class:`FieldSpec` declares an LLM one."""

    key: str
    #: Korean name — **the form's own label**, never a coined one. It becomes the
    #: row label on the ③ card (``present.FIELD_NAMES_KO``).
    name: str
    #: ``R1`` ① / ``R2`` ② / ``R3`` ③.
    rights: str
    #: 본문 위치, as the form prints it.
    location: str
    #: Canonical :data:`~mijual.bodydoc.labels.LABEL_FIELDS` key of the label block.
    label_field: str
    #: Whitespace-free needle identifying the sub-row inside that block.
    qualifier: str
    #: JSON key the normalized value is stored under.
    value_key: str
    #: The gate that judges it — documentation here, code in :mod:`mijual.gates.rules`.
    #: There is no ``anchor``: unlike a :class:`FieldSpec`, nothing here is ever
    #: windowed for a prompt, so the citation is located against the whole document.
    gate: str


LABEL_SPECS: dict[str, LabelFieldSpec] = {
    "appraisal_price": LabelFieldSpec(
        key="appraisal_price",
        name="매수예정가격",
        rights="R3",
        location="13. 주식매수청구권에 관한 사항 → 매수예정가격",
        label_field="appraisal_rights",
        qualifier="매수예정가",
        value_key="price",
        gate="본문 13. 매수예정가격 == API `aprskh_plnprc` (D-15)",
    )
}


def label_field_keys_for(rights: str | RightsType) -> tuple[str, ...]:
    """Field keys of one rights type — the label-tier half of its field list."""
    wanted = rights.value if isinstance(rights, RightsType) else rights
    return tuple(k for k, s in LABEL_SPECS.items() if s.rights == wanted)


# ---------------------------------------------------------------------------
# reading one document
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Reading:
    """What one document says about one label field — value, quote and span."""

    status: str
    value: dict[str, Any] | None = None
    quote: str | None = None
    located: Located | None = None
    note: str | None = None

    @property
    def extracted(self) -> bool:
        return self.status == "extracted"


def _row_for(doc_labels, spec: LabelFieldSpec) -> LabeledValue | None:
    """The sub-row of the label block this spec names, by its qualifier."""
    for row in doc_labels.all(spec.label_field):
        if spec.qualifier in "".join("".join(q.split()) for q in row.qualifier):
            return row
    return None


def _cite(doc: BodyDocument, row: LabeledValue, spec: LabelFieldSpec) -> tuple[str, Located]:
    """Compose the citation from the two adjacent cells, and verify its span.

    The composed quote is accepted only when it lands on the cell the label
    parser already found (same end offset). Otherwise the citation narrows to the
    value cell itself — the span the parser owns — rather than trusting a first
    match somewhere else in a 180k-character 합병 본문.
    """
    qualifier = next(
        (q for q in row.qualifier if spec.qualifier in "".join(q.split())), spec.name
    )
    quote = f"{qualifier} {row.raw}".strip()
    located = QuoteLocator(doc.flat, doc).locate(quote)
    if located.resolved and row.span is not None and located.span is not None:
        if located.span.end == row.span.end:
            return (quote, located)
    if row.span is None:  # pragma: no cover - a printed value always has a span
        return (quote, Located(status="unresolved"))
    span = Span(row.span.start, row.span.end)
    return (
        row.raw,
        Located(
            status="resolved",
            span=span,
            method="label",
            verified=doc.verify(span, row.raw),
            text=doc.value_at(span),
        ),
    )


def read_document(doc: BodyDocument, spec: LabelFieldSpec) -> Reading:
    """Read one label field out of one 본문. Pure; no I/O, no model, no cost."""
    row = _row_for(extract_labels(doc), spec)
    if row is None:
        return Reading("absent", note=f"본문에 '{spec.location}' 행이 없습니다")
    if row.is_empty or row.value is None:
        return Reading("absent", note=f"'{spec.name}' 셀이 '{row.raw or '-'}'")
    number = row.value
    if isinstance(number, bool) or not isinstance(number, (int, float)):
        # The cell says something a parser cannot turn into 원 (a sentence, a
        # date). Recorded as absent **with what it did say**, never guessed at.
        return Reading("absent", note=f"'{spec.name}' 셀이 금액이 아닙니다: {row.raw[:60]}")
    value = {spec.value_key: int(number) if float(number).is_integer() else float(number)}
    quote, located = _cite(doc, row, spec)
    return Reading("extracted", value=value, quote=quote, located=located)


# ---------------------------------------------------------------------------
# the corpus pass
# ---------------------------------------------------------------------------
@dataclass
class LabelFieldReport:
    """What one deterministic pass read. No calls, no tokens, no cost — by design."""

    specs: tuple[str, ...] = ()
    events: int = 0
    documents: int = 0
    rows: int = 0
    missing_documents: list[str] = field(default_factory=list)
    per_field: dict[str, Counter] = field(default_factory=dict)

    def count(self, field_key: str, *keys: str) -> None:
        counter = self.per_field.setdefault(field_key, Counter())
        for key in keys:
            counter[key] += 1

    def render(self) -> str:
        lines = [
            f"task       : labels ({', '.join(self.specs) or '-'})",
            f"targets    : {self.events} event(s), {self.documents} document(s) read, "
            f"{self.rows} row(s) written",
            "calls      : 0 (deterministic — 본문-label tier)",
        ]
        for key in sorted(self.per_field):
            counter = self.per_field[key]
            lines.append(
                f"  {key:<28} extracted={counter['extracted']:>3} absent={counter['absent']:>3} "
                f"span_resolved={counter['span_resolved']:>3} "
                f"span_unresolved={counter['span_unresolved']:>3} "
                f"verified={counter['verified']:>3} label_span={counter['method_label']:>3}"
            )
        if self.missing_documents:
            lines.append(
                f"no 본문    : {len(self.missing_documents)} version(s) "
                f"{self.missing_documents[:6]}"
            )
        return "\n".join(lines)


def _targets(session: Session, spec: LabelFieldSpec, event_ids: list[int] | None) -> list[Event]:
    """Non-suppressed events of the spec's rights type — the extractor's own scope.

    A suppressed event is never rendered, so reading its cells buys nothing; the
    filter matches :func:`mijual.extract.runner.select_targets` so the two halves
    of layer 1 cover the same corpus.
    """
    events = list(
        session.scalars(
            select(Event).where(
                Event.rights_type == RightsType(spec.rights),
                Event.suppressed_reason.is_(None),
            )
        ).all()
    )
    if event_ids is not None:
        by_id = {e.id: e for e in events}
        return [by_id[i] for i in event_ids if i in by_id]
    return sorted(events, key=lambda e: (e.corp_code, e.original_rcept_dt))


def _store(
    session: Session,
    version: FilingVersion,
    snapshot: Snapshot,
    spec: LabelFieldSpec,
    reading: Reading,
    report: LabelFieldReport,
) -> None:
    located = reading.located
    report.count(spec.key, reading.status)
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
        status=reading.status,
        value=reading.value,
        quote=reading.quote,
        located=located,
        snapshot_id=snapshot.id,
        # No call, no model: the three columns that name one stay NULL, which is
        # how a report tells a free reading from a paid one.
        call=None,
        input_scope=f"label:{spec.label_field}",
        prompt_version=READER_VERSION,
        model_note=reading.note,
    )
    report.rows += 1


def read_label_fields(
    session_factory,
    *,
    rights: str | None = None,
    event_ids: list[int] | None = None,
    current_only: bool = False,
    limit: int | None = None,
    log=None,
) -> LabelFieldReport:
    """Read every declared label field across the corpus. 0 calls, 0 requests.

    Every **readable version** is read by default, not only the current one:
    each version's row is judged against its own document (the gate layer's rule)
    and the pair of them is what a 정정 diff compares. ``current_only`` narrows it
    to the version the product actually renders.
    """
    specs = [s for s in LABEL_SPECS.values() if rights is None or s.rights == rights]
    report = LabelFieldReport(specs=tuple(s.key for s in specs))
    if not specs:
        return report

    with session_scope(session_factory) as session:
        for spec in specs:
            events = _targets(session, spec, event_ids)
            if limit is not None:
                events = events[:limit]
            report.events += len(events)
            for event in events:
                versions = readable_versions(event)
                read_any = False
                for version in reversed(versions):
                    loaded = document_of(session, version)
                    if loaded is None:
                        continue
                    snapshot, doc = loaded
                    report.documents += 1
                    _store(session, version, snapshot, spec, read_document(doc, spec), report)
                    read_any = True
                    if current_only:
                        break
                if not read_any:
                    report.missing_documents.append(
                        f"{event.corp_code}/{event.original_rcept_dt}"
                    )
                elif log:
                    log(f"  {event.corp_code} {event.corp.corp_name} {spec.key}")
        session.flush()
    return report
