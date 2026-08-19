"""``mijual.bodydoc`` — the deterministic 본문 layer (P2.S3).

Everything here is a **pure function of one stored document snapshot**: no
network, no database, no LLM. That is the point. The phase constraint reads
*"anything deterministically readable must not be paid for with an LLM call"*,
and field-matrix §1.3 measured that the ① skeleton — 10 numbered labels — is
readable 10/10 in 9/9 filings. So it is read here, for free, and the extractor
(``P2.S4``) only ever sees the ~5 prose fields that genuinely need it.

The layer has four jobs:

``document`` / ``tables``
    Decode a 본문 ZIP into character-addressable XML and walk its tables with
    **offset preservation**. Every value carries a
    :class:`~mijual.bodydoc.document.Span` into the snapshot as stored, which is
    what makes §3.6 layer 2's *원문 인용 스팬 존재* gate possible at all
    (``P2.S5``). The P1 spike's ``text_of`` collapsed whitespace and lost
    positions; this does not.

``labels``
    ① 유상증자결정 numbered rows → typed values (Korean dates → ``date``, ratios →
    ``float``, 양도여부 → ``bool``), each with its span and DART's own
    ``AUNIT``/``AUNITVALUE`` machine value.

``correction``
    The ``<CORRECTION>`` header: target report, the 최초제출일 **hint** (N3 — a
    hint, never a key) and the ``3. 정정사항`` before/after table.

``sections``
    ``<TITLE>``-delimited slicing of a 증권신고서. §5: 0.6M–1.9M text chars, never
    fed whole to anything.

Nothing here writes to the database. The two jobs that *do* —
:mod:`mijual.bodydoc.backfill` — live behind ``python -m mijual.bodydoc``.
"""

from __future__ import annotations

from mijual.bodydoc.correction import (
    CorrectionBlock,
    CorrectionItem,
    correction_span,
    parse_correction,
)
from mijual.bodydoc.document import BodyDocument, Flat, Span, flatten, normalize
from mijual.bodydoc.labels import (
    LABEL_FIELDS,
    TARGET_LABELS,
    LabeledValue,
    LabelSet,
    extract_labels,
    parse_korean_date,
    parse_number,
    parse_yes_no,
)
from mijual.bodydoc.sections import Section, find_sections, sections
from mijual.bodydoc.tables import Cell, Row, Table, cell_grid, parse_table, tables, top_tables

__all__ = [
    "BodyDocument",
    "Cell",
    "CorrectionBlock",
    "CorrectionItem",
    "Flat",
    "LABEL_FIELDS",
    "LabelSet",
    "LabeledValue",
    "Row",
    "Section",
    "Span",
    "TARGET_LABELS",
    "Table",
    "cell_grid",
    "correction_span",
    "extract_labels",
    "find_sections",
    "flatten",
    "normalize",
    "parse_correction",
    "parse_korean_date",
    "parse_number",
    "parse_table",
    "parse_yes_no",
    "sections",
    "tables",
    "top_tables",
]
