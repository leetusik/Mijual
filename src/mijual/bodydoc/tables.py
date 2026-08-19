"""Nesting-aware table parsing with spans, and ROWSPAN/COLSPAN grid expansion.

Ported from ``scripts/spike/corrections.py`` (``top_tables`` / ``table_rows``),
which was proven against real filings, with three deliberate changes:

1. **Everything carries a** :class:`~mijual.bodydoc.document.Span`, so a cell's
   value can be cited back into the stored snapshot.
2. **Cells are ``TD`` | ``TH`` | ``TE`` | ``TU``.** The spike matched ``T[DH]``
   only — which silently drops *every value cell* of a 주요사항보고서 form: DART
   puts labels in ``TD`` and values in ``TE`` (free text/number, with a stable
   ``ACODE``) or ``TU`` (typed unit, with ``AUNIT`` + a machine-readable
   ``AUNITVALUE``, e.g. ``AUNIT="ALL_BS_DT" AUNITVALUE="20260728"``). Reading
   those attributes is what makes the label tier deterministic rather than
   regex-ish.
3. **Nested-table text is kept, not collapsed to ``[표]``.** In a ``<CORRECTION>``
   the 정정 전 / 정정 후 cells are frequently whole nested tables (계양전기
   ``20260724000546``: ``4. 자금조달의 목적``), so the spike's marker threw away
   the actual before/after values. Nested tables are skipped for *structure*
   (they must not contribute rows or cells to their parent) and included for
   *text*.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property

from mijual.bodydoc.document import BodyDocument, Flat, Span, flatten

__all__ = ["Cell", "Row", "Table", "cell_grid", "parse_table", "tables", "top_tables"]

# ``(?![-\w])`` is load-bearing: DART wraps every form table in ``<TABLE-GROUP>``,
# and a plain ``<TABLE\b`` matches that too — which desynchronises the nesting
# depth and makes the whole body look like one unclosed table.
_TABLE_EDGE = re.compile(r"<TABLE(?![-\w])[^>]*>|</TABLE\s*>", re.I)
_TR_EDGE = re.compile(r"<TR(?![-\w])[^>]*>|</TR\s*>", re.I)
_CELL_OPEN = re.compile(r"<(TD|TH|TE|TU)(?![-\w])([^>]*)>", re.I)
_CELL_CLOSE = re.compile(r"</(TD|TH|TE|TU)\s*>", re.I)
_ATTR = re.compile(r"([A-Za-z][\w:-]*)\s*=\s*\"([^\"]*)\"")


def _outside(spans: tuple[Span, ...], index: int) -> bool:
    return not any(s.start <= index < s.end for s in spans)


def top_tables(text: str, within: Span | None = None) -> list[Span]:
    """Top-level ``<TABLE>…</TABLE>`` spans; nested tables stay inside their parent."""
    start, end = (within.start, within.end) if within else (0, len(text))
    out: list[Span] = []
    depth, opened = 0, None
    for match in _TABLE_EDGE.finditer(text, start, end):
        if match.group(0)[1] not in "/":
            if depth == 0:
                opened = match.start()
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0 and opened is not None:
                out.append(Span(opened, match.end()))
    return out


@dataclass(frozen=True)
class Cell:
    """One ``TD``/``TH``/``TE``/``TU`` cell.

    ``span`` is the cell's **content** range (between the tags), which is what a
    citation should point at; ``text`` is its normalized text.
    """

    tag: str
    span: Span
    text: str
    attrs: dict[str, str] = field(default_factory=dict, repr=False)
    flat: Flat | None = field(default=None, repr=False, compare=False)

    @property
    def rowspan(self) -> int:
        return _positive(self.attrs.get("ROWSPAN"))

    @property
    def colspan(self) -> int:
        return _positive(self.attrs.get("COLSPAN"))

    @property
    def acode(self) -> str | None:
        """Stable form field code on a value cell (``CST_CNT``, ``NEW_ASN_CNT``…)."""
        return self.attrs.get("ACODE")

    @property
    def unit(self) -> str | None:
        """``AUNIT`` — the typed-unit code (``ALL_BS_DT``, ``NST_GV_YN``…)."""
        return self.attrs.get("AUNIT")

    @property
    def unit_value(self) -> str | None:
        """``AUNITVALUE`` — DART's own machine value (``20260728``, ``Y``, ``-``)."""
        return self.attrs.get("AUNITVALUE")

    @property
    def is_value_cell(self) -> bool:
        """``TE``/``TU`` are the form's value cells; ``TD``/``TH`` are labels."""
        return self.tag in ("TE", "TU")


def _positive(value: str | None) -> int:
    try:
        return max(1, int(str(value).strip()))
    except (TypeError, ValueError):
        return 1


@dataclass(frozen=True)
class Row:
    span: Span
    cells: tuple[Cell, ...]

    @property
    def texts(self) -> tuple[str, ...]:
        return tuple(c.text for c in self.cells)

    def __bool__(self) -> bool:
        return any(c.text for c in self.cells)


@dataclass(frozen=True)
class Table:
    span: Span
    rows: tuple[Row, ...]
    nested: tuple[Span, ...]
    attrs: dict[str, str] = field(default_factory=dict, repr=False)

    @cached_property
    def head_text(self) -> str:
        """Text of the first two rows — enough to recognise a table by its header."""
        return " ".join(" ".join(r.texts) for r in self.rows[:2])


def parse_table(doc: BodyDocument, table: Span) -> Table:
    """One table's own rows and cells (nested tables excluded from the structure)."""
    text = doc.text
    open_tag = _TABLE_EDGE.match(text, table.start)
    content_start = open_tag.end() if open_tag else table.start
    nested = tuple(top_tables(text, Span(content_start, table.end)))

    rows: list[Row] = []
    depth, opened, row_open = 0, None, content_start
    for match in _TR_EDGE.finditer(text, content_start, table.end):
        if not _outside(nested, match.start()):
            continue
        if match.group(0)[1] not in "/":
            if depth == 0:
                opened = match.end()
                row_open = match.start()
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0 and opened is not None:
                rows.append(
                    Row(
                        span=Span(row_open, match.end()),
                        cells=_cells(doc, Span(opened, match.start()), nested),
                    )
                )
    return Table(
        span=table,
        rows=tuple(r for r in rows if r),
        nested=nested,
        attrs={k.upper(): v for k, v in _ATTR.findall(open_tag.group(0) if open_tag else "")},
    )


def _cells(doc: BodyDocument, within: Span, nested: tuple[Span, ...]) -> tuple[Cell, ...]:
    text = doc.text
    out: list[Cell] = []
    cursor = within.start
    while cursor < within.end:
        opener = _CELL_OPEN.search(text, cursor, within.end)
        if opener is None:
            break
        if not _outside(nested, opener.start()):
            cursor = next(
                (s.end for s in nested if s.start <= opener.start() < s.end), opener.end()
            )
            continue
        tag = opener.group(1).upper()
        content_start = opener.end()
        closer = None
        for candidate in _CELL_CLOSE.finditer(text, content_start, within.end):
            if candidate.group(1).upper() == tag and _outside(nested, candidate.start()):
                closer = candidate
                break
        content_end = closer.start() if closer else within.end
        # Nested-table text is kept on purpose (see the module docstring).
        flat = flatten(text, content_start, content_end)
        out.append(
            Cell(
                tag=tag,
                span=Span(content_start, content_end),
                text=flat.text,
                attrs={k.upper(): v for k, v in _ATTR.findall(opener.group(2))},
                flat=flat,
            )
        )
        cursor = closer.end() if closer else content_end
    return tuple(out)


def tables(doc: BodyDocument, within: Span | None = None) -> list[Table]:
    """Every top-level table of ``doc`` (or of ``within``), parsed."""
    return [parse_table(doc, span) for span in top_tables(doc.text, within)]


def cell_grid(table: Table) -> list[list[Cell]]:
    """Expand ROWSPAN/COLSPAN into a rectangular grid of (shared) cells.

    DART's 유상증자결정 form leans on ROWSPAN hard — ``11. 청약예정일`` spans four
    physical rows and ``우리사주조합`` / ``구주주`` two each — so the label of a
    value row often lives in an *earlier* ``<TR>``. Without this expansion the
    ``종료일`` rows read as unlabeled.
    """
    grid: list[list[Cell]] = []
    carry: dict[int, tuple[Cell, int]] = {}
    for row in table.rows:
        line: list[Cell] = []
        pending = list(row.cells)
        column = 0
        while pending or (carry and column <= max(carry)):
            held = carry.get(column)
            if held is not None:
                cell, left = held
                line.append(cell)
                if left <= 1:
                    del carry[column]
                else:
                    carry[column] = (cell, left - 1)
                column += 1
                continue
            if not pending:
                column += 1  # a hole under a taller neighbour; keep scanning
                continue
            cell = pending.pop(0)
            for _ in range(cell.colspan):
                line.append(cell)
                if cell.rowspan > 1:
                    carry[column] = (cell, cell.rowspan - 1)
                column += 1
        grid.append(line)
    return grid
