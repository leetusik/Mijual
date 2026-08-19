"""① 유상증자결정 본문: numbered labeled rows → typed values with citation spans.

This is the **`본문-label` tier** of the three-tier field model
(``docs/current/data.md``). The phase constraint is blunt about why it exists:
*anything deterministically readable must not be paid for with an LLM call*.
Field-matrix §1.3 measured the 10 target labels present in **9/9** 주주배정 filings,
10/10 each — so every one of them belongs here, never in the extractor.

Two independent handles are read for each row and both are reported:

* the **Korean numbered label** in the row's header cell (``18. 신주인수권양도여부``)
  — the thing §1.3 actually measured, and what a human sees;
* DART's own **``AUNIT`` / ``AUNITVALUE``** (and ``ACODE``) attributes on the value
  cell — e.g. ``AUNIT="NST_GV_YN" AUNITVALUE="Y"``, ``AUNIT="ALL_BS_DT"
  AUNITVALUE="20260728"``. Verified stable across every ① filing in the P1 cache
  that carries the row.

Typed parsing prefers ``AUNITVALUE`` and falls back to the printed text, so
``2026년 07월 28일`` and ``20260728`` both land as ``date(2026, 7, 28)`` — and the
span still points at the printed text, because that is what a citation must show.

Multi-date rows are handled **conservatively, as the plan requires**:
``11. 청약예정일`` is not flattened into one value. Its four physical rows become
four :class:`LabeledValue` entries distinguished by their ``qualifier``
(``('우리사주조합', '시작일')``, ``('구주주', '종료일')``, …), each with its own
span. Nothing is guessed about which 대상자 a caller wants.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from mijual.bodydoc.document import BodyDocument, Span
from mijual.bodydoc.tables import Cell, cell_grid, tables

__all__ = [
    "LABEL_FIELDS",
    "TARGET_LABELS",
    "LabeledValue",
    "LabelSet",
    "extract_labels",
    "parse_korean_date",
    "parse_number",
    "parse_yes_no",
]

#: The 10 stable numbered labels of field-matrix §1.3 / ``survey.py``'s ``LABELS``,
#: mapped to the canonical field key this package exposes. Keys are the label text
#: with whitespace removed; the leading ``N.`` / ``-`` marker is stripped first.
LABEL_FIELDS: dict[str, str] = {
    # --- the 10 measured 10/10 labels -----------------------------------
    "신주배정기준일": "allotment_record_date",
    "1주당신주배정주식수": "shares_per_share",
    "청약예정일": "subscription_dates",
    "납입일": "payment_date",
    "실권주처리계획": "forfeited_share_plan",
    "신주의상장예정일": "new_share_listing_date",
    "대표주관회사": "lead_underwriter",
    "신주인수권양도여부": "warrant_transferable",
    "신주인수권증서의상장여부": "warrant_certificate_listed",
    "신주인수권증서의매매및매매의중개를담당할금융투자업자": "warrant_broker",
    # --- free extras from the same table (no extra parsing cost) --------
    "신주의종류와수": "new_shares",
    "1주당액면가액": "par_value",
    "증자전발행주식총수": "shares_before",
    "자금조달의목적": "use_of_funds",
    "증자방식": "issue_method",
    "신주발행가액": "issue_price",
    "발행가산정방법": "issue_price_method",
    "우리사주조합원우선배정비율": "esop_ratio",
    "신주의배당기산일": "dividend_start_date",
    "신주권교부예정일": "share_delivery_date",
    "이사회결의일": "board_resolution_date",
    "증권신고서제출대상여부": "registration_required",
}

#: The 10 §1.3 labels, as canonical field keys — the completeness check.
TARGET_LABELS: tuple[str, ...] = (
    "allotment_record_date",
    "shares_per_share",
    "subscription_dates",
    "payment_date",
    "forfeited_share_plan",
    "new_share_listing_date",
    "lead_underwriter",
    "warrant_transferable",
    "warrant_certificate_listed",
    "warrant_broker",
)

_NUMBERED = re.compile(r"^\s*(\d{1,2})\s*[.．]\s*(.+)$", re.S)
_DASHED = re.compile(r"^\s*[-–ㆍ·]\s*(.+)$", re.S)
_KDATE = re.compile(r"(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일")
_ISO8 = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
_NUMBER = re.compile(r"^-?[\d,]+(?:\.\d+)?$")
#: Trailing unit/qualifier parentheses DART prints inside the label cell.
_LABEL_TAIL = re.compile(r"[（(][^)）]*[)）]\s*$")
_EMPTY = {"", "-", "–", "—", "해당사항없음", "해당사항 없음", "미해당"}
_YES = {"예", "y", "yes", "가능", "양도가능", "해당"}
_NO = {"아니오", "아니요", "n", "no", "불가", "양도불가", "미발행", "부"}


def parse_korean_date(text: str | None) -> date | None:
    """``2026년 07월 28일`` or ``20260728`` → :class:`datetime.date`."""
    if not text:
        return None
    stripped = text.strip()
    iso = _ISO8.match(stripped.replace("-", "").replace(".", ""))
    if iso:
        try:
            return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
        except ValueError:
            return None
    match = _KDATE.search(stripped)
    if match is None:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def parse_number(text: str | None) -> float | int | None:
    """``8,200,000`` → ``int``; ``0.2314082845`` / ``20.0`` → ``float``."""
    if not text:
        return None
    stripped = text.strip()
    if stripped in _EMPTY or not _NUMBER.match(stripped):
        return None
    plain = stripped.replace(",", "")
    return float(plain) if "." in plain else int(plain)


def parse_yes_no(text: str | None) -> bool | None:
    """``예`` / ``Y`` → ``True``; ``아니오`` / ``N`` / ``미발행`` → ``False``."""
    if text is None:
        return None
    key = text.strip().lower()
    if key in _YES:
        return True
    if key in _NO:
        return False
    return None


@dataclass(frozen=True)
class LabeledValue:
    """One labeled row: what it says, what it means, and where it is."""

    #: Canonical key from :data:`LABEL_FIELDS`, or ``None`` for an unmapped row.
    field_key: str | None
    #: ``"18"`` for a numbered label, ``None`` for a ``- `` sub-row.
    number: str | None
    #: The label exactly as printed (``18. 신주인수권양도여부``).
    label: str
    #: Intermediate header cells (``('우리사주조합', '시작일')``).
    qualifier: tuple[str, ...]
    #: Normalized printed value.
    raw: str
    #: Where ``raw`` lives in :attr:`BodyDocument.text` — the citation span.
    span: Span | None
    #: Where the label lives (useful when a value cell is empty).
    label_span: Span | None
    #: ``date`` | ``number`` | ``boolean`` | ``text`` | ``empty``.
    kind: str
    #: Typed value: ``date`` / ``int`` / ``float`` / ``bool`` / ``str`` / ``None``.
    value: object | None
    unit: str | None = None
    unit_value: str | None = None
    acode: str | None = None

    @property
    def is_empty(self) -> bool:
        return self.kind == "empty"

    @property
    def iso(self) -> str | None:
        return self.value.isoformat() if isinstance(self.value, date) else None


@dataclass
class LabelSet:
    """Every labeled row of one document, indexed by canonical field key."""

    rows: tuple[LabeledValue, ...] = ()
    form_code: str | None = None
    by_field: dict[str, list[LabeledValue]] = field(default_factory=dict, repr=False)

    def get(self, field_key: str) -> LabeledValue | None:
        """The first row for ``field_key`` (see :meth:`all` for multi-row labels)."""
        found = self.by_field.get(field_key)
        return found[0] if found else None

    def all(self, field_key: str) -> list[LabeledValue]:
        return list(self.by_field.get(field_key, ()))

    def value(self, field_key: str) -> object | None:
        found = self.get(field_key)
        return found.value if found else None

    def qualified(self, field_key: str, *needles: str) -> LabeledValue | None:
        """A multi-row label's entry whose qualifier contains every needle.

        ``labels.qualified('subscription_dates', '구주주', '종료일')``
        """
        for row in self.by_field.get(field_key, ()):
            joined = " ".join(row.qualifier)
            if all(n in joined for n in needles):
                return row
        return None

    @property
    def target_coverage(self) -> tuple[int, int]:
        """``(found, 10)`` over the field-matrix §1.3 label list."""
        return (sum(1 for k in TARGET_LABELS if k in self.by_field), len(TARGET_LABELS))

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.rows)


def _label_key(text: str) -> str:
    """Label text → the whitespace-free key used by :data:`LABEL_FIELDS`."""
    return re.sub(r"\s+", "", _LABEL_TAIL.sub("", text)).replace("*", "")


def _classify(cell: Cell, printed: str) -> tuple[str, object | None]:
    """Typed value for one value cell — ``AUNITVALUE`` first, printed text after."""
    unit_value = (cell.unit_value or "").strip()
    unit = (cell.unit or "") + (cell.acode or "")
    candidates = [c for c in (unit_value, printed) if c]

    if printed.strip() in _EMPTY and unit_value in _EMPTY | {""}:
        return ("empty", None)
    if unit.endswith(("_DT", "_YMD")) or any(_KDATE.search(c) for c in candidates):
        for candidate in candidates:
            parsed = parse_korean_date(candidate)
            if parsed is not None:
                return ("date", parsed)
    if unit.endswith(("_YN", "_AT")) or unit_value in ("Y", "N"):
        decided = parse_yes_no(unit_value) if unit_value else None
        if decided is None:
            decided = parse_yes_no(printed)
        if decided is not None:
            return ("boolean", decided)
    number = parse_number(printed)
    if number is not None:
        return ("number", number)
    decided = parse_yes_no(printed)
    if decided is not None and len(printed.strip()) <= 4:
        return ("boolean", decided)
    return ("text", printed)


def extract_labels(
    doc: BodyDocument, within: Span | None = None, *, include_correction: bool = False
) -> LabelSet:
    """Every ``N. 라벨 → 값`` row of a 주요사항보고서 본문, with spans.

    Works on any 주요사항보고서 form — the numbered-label + ``TE``/``TU`` shape is
    the form family's, not ①'s — but :data:`LABEL_FIELDS` names ① fields only.
    On a 증권신고서 pass a section span (see :mod:`mijual.bodydoc.sections`);
    never run it over a whole one.

    The ``<CORRECTION>`` block is **excluded by default**: its 정정사항 table
    repeats the body's labels with *superseded* values in the 정정 전 column, so
    including it would let a stale value win. Read it with
    :func:`mijual.bodydoc.correction.parse_correction` instead.
    """
    result = LabelSet(form_code=doc.form_code)
    collected: list[LabeledValue] = []
    current_number: str | None = None
    current_label: str | None = None
    current_label_span: Span | None = None

    scanned = tables(doc, within)
    if not include_correction:
        from mijual.bodydoc.correction import correction_span

        block = correction_span(doc)
        if block is not None:
            scanned = [t for t in scanned if not block.covers(t.span)]

    for table in scanned:
        for line in cell_grid(table):
            if not line:
                continue
            # De-duplicate the horizontal repetition COLSPAN/ROWSPAN produces.
            cells: list[Cell] = []
            for cell in line:
                if not cells or cells[-1] is not cell:
                    cells.append(cell)
            if len(cells) < 2:
                continue

            # A row may carry more than one label→value pair (``6. 신주 발행가액``
            # puts 예정발행가 and 확정예정일 side by side), so each TE/TU value
            # cell closes its own group. Forms without TE/TU fall back to
            # "the last cell is the value".
            value_positions = [i for i, c in enumerate(cells) if c.is_value_cell]
            if not value_positions:
                value_positions = [len(cells) - 1]

            heads = cells[: value_positions[0]]
            if not heads:
                continue
            numbered = _NUMBERED.match(heads[0].text)
            dashed = _DASHED.match(heads[0].text)
            if numbered:
                current_number = numbered.group(1)
                current_label = " ".join(numbered.group(2).split())
                current_label_span = heads[0].span
                lead = 1
            elif dashed:
                current_number = None
                current_label = " ".join(dashed.group(1).split())
                current_label_span = heads[0].span
                lead = 1
            elif current_label is not None and cells[value_positions[0]].is_value_cell:
                # A continuation row of a ROWSPAN group (``종료일``), whose label
                # cell lives in an earlier <TR>.
                lead = 0
            else:
                continue

            previous = lead
            for position in value_positions:
                value_cell = cells[position]
                qualifier = tuple(c.text for c in cells[previous:position] if c.text)
                previous = position + 1
                printed = value_cell.text
                kind, typed = _classify(value_cell, printed)
                collected.append(
                    LabeledValue(
                        field_key=LABEL_FIELDS.get(_label_key(current_label or "")),
                        number=current_number,
                        label=current_label or "",
                        qualifier=qualifier,
                        raw=printed,
                        span=value_cell.span if printed else None,
                        label_span=current_label_span,
                        kind=kind,
                        value=typed,
                        unit=value_cell.unit,
                        unit_value=value_cell.unit_value,
                        acode=value_cell.acode,
                    )
                )

    by_field: dict[str, list[LabeledValue]] = {}
    for row in collected:
        if row.field_key:
            by_field.setdefault(row.field_key, []).append(row)
    result.rows = tuple(collected)
    result.by_field = by_field
    return result
