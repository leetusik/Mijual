"""``<CORRECTION>`` block: target report, 최초제출일 hint, and the 정정사항 table.

Every 기재정정 filing opens with a ``<CORRECTION>`` element carrying three things
(field-matrix §4.1, **40/40 parseable** in P1):

1. ``1. 정정대상 공시서류`` — which report subtype was corrected;
2. ``2. 정정대상 공시서류의 최초제출일`` — the original's 접수일. **A hint, never a
   key** (N3): it is filer-entered and sometimes years stale (``20260429000902``
   declares 2022-08-01). ``P2.S2`` paired without it; this slice backfills it and
   uses it to *confirm or challenge* an existing pairing, never to override one
   blindly.
3. ``3. 정정사항`` — 항목 / 정정사유 / 정정 전 / 정정 후, the authoritative
   what-changed list. §4.3 measured `기타 투자판단에 참고할 사항` as the most
   corrected 항목 (11/40), which is exactly why S4 must re-read prose on a
   correction rather than diff structured fields.

Both the table path and the free-text fallback produce **spans**, so a 정정
interpretation can cite the header it came from.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from mijual.bodydoc.document import BodyDocument, Span, flatten
from mijual.bodydoc.labels import parse_korean_date
from mijual.bodydoc.tables import Table, cell_grid, tables

__all__ = [
    "CorrectionBlock",
    "CorrectionItem",
    "correction_span",
    "parse_correction",
]

_CORRECTION = re.compile(r"<CORRECTION\b[^>]*>.*?</CORRECTION\s*>", re.S | re.I)
_TARGET_TEXT = re.compile(
    r"정정대상\s*공시서류\s*[:：]?\s*(.{0,80}?)\s*(?:\d\s*[.．]|정정대상\s*공시서류의|$)"
)
_FIRST_SUBMIT_TEXT = re.compile(
    r"최초제출일\s*[:：]?\s*((?:\d{4}\s*년\s*\d{1,2}\s*월\s*\d{1,2}\s*일)|\d{8})"
)
_ITEM_LABEL = re.compile(r"항\s*목")
_BEFORE_LABEL = re.compile(r"정\s*정\s*전")
_AFTER_LABEL = re.compile(r"정\s*정\s*후")
_REASON_LABEL = re.compile(r"정정\s*사유")
#: How much of a 정정 전 / 정정 후 cell is carried in memory. The cells are
#: occasionally whole nested tables; the span always covers the full cell.
CELL_TEXT_LIMIT = 4000


@dataclass(frozen=True)
class CorrectionItem:
    """One row of the ``3. 정정사항`` table."""

    item: str
    item_span: Span | None
    reason: str | None
    reason_span: Span | None
    before: str
    before_span: Span | None
    after: str
    after_span: Span | None

    @property
    def item_number(self) -> str | None:
        """The leading form number of the 항목 (``12`` for ``12. 납입일``)."""
        match = re.match(r"\s*(\d{1,2})\s*[.．]", self.item)
        return match.group(1) if match else None

    @property
    def changed(self) -> bool:
        return self.before.strip() != self.after.strip()


@dataclass(frozen=True)
class CorrectionBlock:
    """Everything the ``<CORRECTION>`` header states, with its spans."""

    present: bool
    span: Span | None = None
    target_report: str | None = None
    target_report_span: Span | None = None
    #: ``2. 정정대상 공시서류의 최초제출일`` — the pairing **hint**.
    declared_original_dt: date | None = None
    declared_original_span: Span | None = None
    items: tuple[CorrectionItem, ...] = ()
    #: ``table`` (parsed from the 1./2. tables) or ``text`` (regex fallback).
    source: str | None = None

    @property
    def has_hint(self) -> bool:
        return self.declared_original_dt is not None

    @property
    def changed_items(self) -> tuple[CorrectionItem, ...]:
        return tuple(i for i in self.items if i.changed)


def correction_span(doc: BodyDocument) -> Span | None:
    """The ``<CORRECTION>…</CORRECTION>`` range, or ``None`` on an original."""
    match = _CORRECTION.search(doc.text)
    return None if match is None else Span(match.start(), match.end())


def _is_revision_table(table: Table) -> bool:
    head = table.head_text
    return bool(_ITEM_LABEL.search(head) and (_BEFORE_LABEL.search(head) or _AFTER_LABEL.search(head)))


def _header_columns(table: Table) -> dict[str, int]:
    """Column index of 항목 / 정정사유 / 정정 전 / 정정 후 in the header row."""
    grid = cell_grid(table)
    for line in grid[:2]:
        found: dict[str, int] = {}
        for index, cell in enumerate(line):
            text = cell.text
            if _ITEM_LABEL.fullmatch(text.strip()) or text.replace(" ", "") == "항목":
                found.setdefault("item", index)
            elif _REASON_LABEL.search(text):
                found.setdefault("reason", index)
            elif _BEFORE_LABEL.search(text):
                found.setdefault("before", index)
            elif _AFTER_LABEL.search(text):
                found.setdefault("after", index)
        if "item" in found and ("before" in found or "after" in found):
            return found
    return {}


def _rows_of(table: Table) -> list[CorrectionItem]:
    columns = _header_columns(table)
    items: list[CorrectionItem] = []
    for line in cell_grid(table):
        cells = []
        for cell in line:
            if not cells or cells[-1] is not cell:
                cells.append(cell)
        if len(cells) < 3:
            continue
        first = cells[0].text
        if not first or _ITEM_LABEL.fullmatch(first.strip()) or first.replace(" ", "") == "항목":
            continue
        # The 정정사유 column is routinely ROWSPAN-merged, so a continuation row
        # carries 3 cells (항목 / 전 / 후) while the header row carries 4. Taking
        # the last two columns is what the P1 spike did and what survives both.
        before_cell, after_cell = cells[-2], cells[-1]
        reason_cell = None
        if len(cells) >= 4:
            reason_index = columns.get("reason", 1)
            reason_cell = cells[min(reason_index, len(cells) - 3)]
        items.append(
            CorrectionItem(
                item=first[:200],
                item_span=cells[0].span,
                reason=(reason_cell.text[:200] if reason_cell else None),
                reason_span=(reason_cell.span if reason_cell else None),
                before=before_cell.text[:CELL_TEXT_LIMIT],
                before_span=before_cell.span,
                after=after_cell.text[:CELL_TEXT_LIMIT],
                after_span=after_cell.span,
            )
        )
    return items


def parse_correction(doc: BodyDocument) -> CorrectionBlock:
    """Parse the ``<CORRECTION>`` header of a 정정 filing. Pure; no I/O."""
    block = correction_span(doc)
    if block is None:
        return CorrectionBlock(present=False)

    parsed = tables(doc, block)
    target: str | None = None
    target_span: Span | None = None
    declared: date | None = None
    declared_span: Span | None = None
    source = "table"

    for table in parsed:
        if _is_revision_table(table):
            continue
        for line in cell_grid(table):
            cells = []
            for cell in line:
                if not cells or cells[-1] is not cell:
                    cells.append(cell)
            if len(cells) < 2:
                continue
            head, value = cells[0].text, cells[-1].text
            if target is None and "정정대상" in head and "최초제출일" not in head:
                target, target_span = value, cells[-1].span
            elif declared is None and "최초제출일" in head:
                parsed_date = parse_korean_date(value)
                if parsed_date is not None:
                    declared, declared_span = parsed_date, cells[-1].span

    if declared is None or target is None:
        # Free-text layouts exist (the P1 spike only ever used this path).
        flat = flatten(doc.text, block.start, block.end)
        if target is None:
            match = _TARGET_TEXT.search(flat.text)
            if match and match.group(1).strip():
                target, target_span = match.group(1).strip(), flat.match_span(match, 1)
                source = "text"
        if declared is None:
            match = _FIRST_SUBMIT_TEXT.search(flat.text)
            if match:
                declared = parse_korean_date(match.group(1))
                declared_span = flat.match_span(match, 1)
                source = "text"

    items: list[CorrectionItem] = []
    for table in parsed:
        if _is_revision_table(table):
            items.extend(_rows_of(table))

    return CorrectionBlock(
        present=True,
        span=block,
        target_report=target,
        target_report_span=target_span,
        declared_original_dt=declared,
        declared_original_span=declared_span,
        items=tuple(items),
        source=source,
    )
