"""증권신고서 section slicer — the **only** sanctioned access to that regime.

Field-matrix §5 measured the two size regimes:

* 주요사항보고서 — 2.6k–10k text chars: the one-shot unit;
* 증권신고서 — 0.6M–1.9M text chars (``20260713000459`` 합병: 9.5M XML chars,
  1.87M text chars): **100–300× larger**. Feeding one whole to anything is a bug,
  not a cost problem.

DART marks every section with ``<TITLE ATOC="Y" AASSOCNOTE="D-1-1-4-0"
ATOCID="11">4. 모집 또는 매출절차 등에 관한 사항</TITLE>``. A section runs from the
end of its ``</TITLE>`` to the start of the next ``<TITLE>`` — so the slices tile
the document and every offset stays a real offset into the stored snapshot,
which keeps citation spans valid for values read out of a section.

``AASSOCNOTE`` carries the outline position (``D-1-3-2-0`` = part 1, chapter 3,
section 2) and is turned into :attr:`Section.level`; where it is absent the
section still slices, it just has no depth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from mijual.bodydoc.document import BodyDocument, Span, normalize

__all__ = ["Section", "find_sections", "sections"]

_TITLE = re.compile(r"<TITLE\b([^>]*)>(.*?)</TITLE\s*>", re.S | re.I)
_ATTR = re.compile(r"([A-Za-z][\w:-]*)\s*=\s*\"([^\"]*)\"")
_OUTLINE = re.compile(r"^[A-Z]-((?:\d+|L\d+)(?:-(?:\d+|L\d+))*)$")


@dataclass(frozen=True)
class Section:
    """One ``<TITLE>``-delimited section, with the offsets to slice it."""

    title: str
    #: Content range: end of ``</TITLE>`` → start of the next ``<TITLE>``.
    span: Span
    title_span: Span
    #: The full range including the title (what to hand a reader).
    outer_span: Span
    assoc_note: str | None = None
    atoc_id: str | None = None
    eng: str | None = None
    #: Outline depth from ``AASSOCNOTE`` (``D-1-3-2-0`` → 3), else ``None``.
    level: int | None = None

    @property
    def size(self) -> int:
        return len(self.span)

    def text_of(self, doc: BodyDocument) -> str:
        """Normalized text of this section — safe to hand to a reader."""
        return normalize(doc.raw(self.span))

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Section {self.title[:40]!r} {self.span.start}..{self.span.end}>"


def _level(assoc_note: str | None) -> int | None:
    if not assoc_note:
        return None
    match = _OUTLINE.match(assoc_note.strip())
    if match is None:
        return None
    parts = [p for p in match.group(1).split("-")]
    depth = sum(1 for p in parts if p not in ("0",))
    return depth or None


def sections(doc: BodyDocument, *, marked_only: bool = True) -> list[Section]:
    """Every ``<TITLE>`` section in document order; the slices tile the document.

    ``marked_only`` keeps only ``ATOC="Y"`` titles (the table-of-contents ones),
    which is what the outline actually is.
    """
    matches = list(_TITLE.finditer(doc.text))
    if marked_only:
        matches = [m for m in matches if _ATTR.findall(m.group(1)) and
                   {k.upper(): v for k, v in _ATTR.findall(m.group(1))}.get("ATOC") == "Y"]
    out: list[Section] = []
    for index, match in enumerate(matches):
        attrs = {k.upper(): v for k, v in _ATTR.findall(match.group(1))}
        end = matches[index + 1].start() if index + 1 < len(matches) else len(doc.text)
        note = attrs.get("AASSOCNOTE")
        out.append(
            Section(
                title=normalize(match.group(2)),
                span=Span(match.end(), end),
                title_span=Span(match.start(2), match.end(2)),
                outer_span=Span(match.start(), end),
                assoc_note=note,
                atoc_id=attrs.get("ATOCID"),
                eng=attrs.get("ENG"),
                level=_level(note),
            )
        )
    return out


def find_sections(doc: BodyDocument, pattern: str, *, marked_only: bool = True) -> list[Section]:
    """Sections whose title matches ``pattern`` (a regex, searched case-insensitively).

    The 증권신고서 entry points the MVP cares about, by measurement (§5, §7):
    ``모집 또는 매출에 관한 일반사항`` / ``공모방법`` / ``모집 또는 매출절차`` for the
    ① 청약 일정 and 신주인수권증서 sections, ``주식매수청구권`` for ③.
    """
    rx = re.compile(pattern, re.I)
    return [s for s in sections(doc, marked_only=marked_only) if rx.search(s.title)]
