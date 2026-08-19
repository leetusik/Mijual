"""The gate's **independent witnesses**: 본문 labels + the stored API detail row.

§7 states each gate as a comparison against something the LLM never saw. That is
deliberate and it is N38's rule read from the other side: the extraction prompt
carries *only the document* — no label values, no API values — so the reference
values assembled here are genuinely independent evidence and a gate is not
checking the prompt against itself.

Everything in this module is read from **stored snapshots**: the 본문 ZIP the
extraction's span points into, and the newest detail-endpoint snapshot of the
event. Zero OpenDART requests, zero LLM calls, and no value is re-derived from
anything the model produced.

One rule is load-bearing for the countdown (N4/N40): a version's context is built
from **that version's own document**, never from a sibling's. A gate verdict on a
superseded version therefore judges the superseded values, and the exposure
contract simply never reads it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.bodydoc import BodyDocument, LabelSet, Span, extract_labels, parse_correction
from mijual.bodydoc.correction import CorrectionBlock
from mijual.db.models import Event, Extraction, FilingVersion, Snapshot

__all__ = [
    "VersionContext",
    "api_detail",
    "iso_date",
    "korean_date",
    "squash",
    "version_context",
]

_KDATE = re.compile(r"(\d{4})\s*[년.\-/]\s*(\d{1,2})\s*[월.\-/]\s*(\d{1,2})\s*일?")
#: What a filer writes when a date exists but has not been fixed yet (N40).
TBD_TEXT = re.compile(r"추후\s*(?:결정|확정|공시|정함|지정)|미확정|미정(?!산)")
#: Detail-endpoint snapshots, i.e. everything except the ``list.json`` rows.
_LIST_SOURCES = {"list", "document"}


def squash(text: object) -> str:
    """Whitespace-free text — the comparison form for short label/table values."""
    return re.sub(r"\s+", "", str(text or ""))


def korean_date(value: object) -> date | None:
    """``2026년 09월 17일`` / ``2026-09-17`` / ``20260917`` → ``date``; ``-`` → None."""
    text = str(value or "").strip()
    if not text or text in {"-", "–", "—"}:
        return None
    digits = text.replace("-", "").replace(".", "").replace("/", "")
    if len(digits) == 8 and digits.isdigit():
        try:
            return date(int(digits[:4]), int(digits[4:6]), int(digits[6:8]))
        except ValueError:
            return None
    match = _KDATE.search(text)
    if match is None:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def iso_date(value: object) -> date | None:
    """A model-normalized ``YYYY-MM-DD`` → ``date``. Anything else → ``None``."""
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if len(text) < 10:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return korean_date(text)


def api_detail(session: Session, event: Event) -> dict:
    """Newest stored **detail-endpoint** payload of an event (``piicDecsn``…).

    The detail row is the API tier of the three-tier field model and the
    reference value for gates 6–9. ``list`` rows and 본문 ZIPs are excluded: a
    ``list.json`` row carries no field values, and the 본문 is the *other*
    witness, read through :mod:`mijual.bodydoc`.
    """
    snapshot = session.scalar(
        select(Snapshot)
        .join(FilingVersion, Snapshot.filing_version_id == FilingVersion.id)
        .where(FilingVersion.event_id == event.id, Snapshot.source.not_in(_LIST_SOURCES))
        .order_by(Snapshot.captured_at.desc())
        .limit(1)
    )
    payload = snapshot.payload_json if snapshot is not None else None
    return payload if isinstance(payload, dict) else {}


@dataclass
class VersionContext:
    """Every deterministic value one version's gates may compare against."""

    event: Event
    version: FilingVersion
    doc: BodyDocument
    labels: LabelSet
    correction: CorrectionBlock
    api: dict = field(default_factory=dict)
    #: Is this the event's **current** version? The detail endpoints return one
    #: row per event — the newest version only (N2) — so the stored API payload
    #: is a reference value for the newest version and for **no other**. Comparing
    #: a superseded 본문 against today's API row measures the correction, not the
    #: reading: 3 of this corpus's ③ rows failed exactly that way before the
    #: scoping existed. A gate whose only reference is the API therefore reports
    #: ``superseded_api_reference`` on an older version instead of a false failure.
    api_is_current: bool = True

    def api_value(self, *keys: str) -> object | None:
        """An API detail value — but only where it is a valid reference (N2)."""
        if not self.api_is_current:
            return None
        for key in keys:
            value = self.api.get(key)
            if value not in (None, "", "-"):
                return value
        return None

    # -- ① 본문-label references (field-matrix §1.3) ----------------------
    @property
    def record_date(self) -> date | None:
        """본문 ``8. 신주배정기준일`` — gate 1's lower bound."""
        value = self.labels.value("allotment_record_date")
        return value if isinstance(value, date) else None

    @property
    def subscription_dates(self) -> dict[str, dict[str, date]]:
        """본문 ``11. 청약예정일``, per 대상자 — gate 2's reference and gate 1's upper bound.

        Never flattened into one range (S3's rule): the label is 대상자별 and the
        gate compares 우리사주조합 against 우리사주조합.
        """
        found: dict[str, dict[str, date]] = {}
        for row in self.labels.all("subscription_dates"):
            joined = " ".join(row.qualifier)
            group = "우리사주" if "우리사주" in joined else ("구주주" if "구주주" in joined else joined)
            edge = "end" if "종료" in joined else "start"
            if isinstance(row.value, date):
                found.setdefault(group, {})[edge] = row.value
        return found

    @property
    def first_subscription_date(self) -> date | None:
        """Earliest 청약 시작일 across 대상자 — the 매매기간's hard upper bound."""
        starts = [d["start"] for d in self.subscription_dates.values() if "start" in d]
        return min(starts) if starts else None

    @property
    def shareholder_subscription(self) -> dict[str, date]:
        """구주주 청약 시작/종료일 (the 일반공모 청약 must follow it)."""
        return self.subscription_dates.get("구주주", {})

    @property
    def price_confirm_date(self) -> date | None:
        """본문 ``6. 신주 발행가액 → 확정예정일`` — gate 5's lower bound.

        The label is the day the price is *determined*; the prose routinely names
        the day it is *공시*, one trading day later. Measured over this corpus:
        16 filings state the same date, 3 state exactly +1 day (계양전기, HLB제약,
        SG). So gate 5 checks a **window**, not equality — see :mod:`rules`.
        """
        for row in self.labels.all("issue_price"):
            if "확정예정일" in " ".join(row.qualifier) and isinstance(row.value, date):
                return row.value
        return None

    @property
    def confirmed_price(self) -> float | None:
        """본문 ``6. 확정발행가 보통주식``, once it exists."""
        return self._price("확정발행가")

    @property
    def planned_price(self) -> float | None:
        """본문 ``6. 예정발행가 보통주식``."""
        return self._price("예정발행가")

    def _price(self, kind: str) -> float | None:
        for row in self.labels.all("issue_price"):
            joined = " ".join(row.qualifier)
            if kind in joined and "보통주" in joined and isinstance(row.value, (int, float)):
                return float(row.value)
        return None

    # -- evidence helpers -------------------------------------------------
    def span_text(self, row: Extraction) -> str:
        """The stored snapshot's own text under the row's span (not the model's)."""
        span = row.span
        if span is None:
            return ""
        return self.doc.value_at(Span(span[0], span[1]))

    def says_tbd(self, row: Extraction) -> bool:
        """Does the **cited document text** say the schedule is suspended? (N40)

        Positive evidence is required: a null date alone is a missing value, and
        only a document that actually writes ``추후결정`` earns a ``tbd``.
        """
        return bool(TBD_TEXT.search(self.span_text(row)) or TBD_TEXT.search(row.quote or ""))


def version_context(
    session: Session,
    event: Event,
    version: FilingVersion,
    doc: BodyDocument,
    *,
    is_current: bool = True,
) -> VersionContext:
    """Assemble one version's reference values. Pure reads; zero requests."""
    return VersionContext(
        event=event,
        version=version,
        doc=doc,
        labels=extract_labels(doc),
        correction=parse_correction(doc),
        api=api_detail(session, event),
        api_is_current=is_current,
    )
