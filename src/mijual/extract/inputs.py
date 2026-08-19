"""What text the model is allowed to see, and at what size.

Field-matrix §5 measured two regimes and the phase turned them into a rule:

* **주요사항보고서 — 2.6k–10k text chars: the one-shot unit.** Fed whole, because
  the ① prose fields (§7 #1–#5) all live in one ``24. 기타 투자판단에 참고할 사항``
  block whose sub-headings drift between filers; cutting it up is how you lose
  the field you came for.
* **증권신고서 — 0.6M–1.9M text chars: never fed whole.** Sliced by ``<TITLE>``
  section (:mod:`mijual.bodydoc.sections`), and only ever as a *secondary*
  confirmation source when the 주요사항보고서 does not carry the field.

A third case turned up in the corpus and is handled here rather than by
exception: a handful of 합병 주요사항보고서 are 100k–180k chars (아시아나항공
``20260713000482`` is 181k), far outside §5's measured 주요사항보고서 band. Those
are **windowed** around the field's anchor instead of being sent whole.

Offsets survive every one of those paths, which is the whole point: a window and
a section are both built by re-flattening a *raw range* of the same document, so
a span located inside one is still a real offset into the stored snapshot.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from mijual.bodydoc.document import BodyDocument, Flat, Span, flatten
from mijual.bodydoc.sections import find_sections
from mijual.extract.fields import FieldSpec, TaskSpec

__all__ = ["DocumentInput", "WHOLE_DOCUMENT_LIMIT", "build_input"]

#: Above this many normalized characters a 주요사항보고서 is windowed, not sent
#: whole. §5's measured band is 2.6k–10k; 25k leaves generous headroom for the
#: 합병 forms while still refusing a 180k-char body.
WHOLE_DOCUMENT_LIMIT = 25_000
#: Characters kept before / after the anchor region when windowing.
WINDOW_LEAD = 2_000
WINDOW_TAIL = 18_000


@dataclass(frozen=True)
class DocumentInput:
    """The text handed to the model, plus the flat it must be located against."""

    #: ``document`` | ``window:<anchor>`` | ``section:<title>``.
    scope: str
    text: str
    flat: Flat
    doc: BodyDocument
    #: Raw range of the document this input covers.
    span: Span

    @property
    def chars(self) -> int:
        return len(self.text)


def _anchor_of(task: TaskSpec | None, spec: FieldSpec | None) -> str | None:
    if spec is not None:
        return spec.anchor
    if task is not None:
        parts = [s.anchor for s in task.specs if s.anchor]
        return "|".join(parts) if parts else None
    return None


def _window(doc: BodyDocument, flat: Flat, anchor: str | None) -> tuple[Flat, str, Span]:
    """Slice ``flat`` down to the anchor's neighbourhood, keeping offsets real."""
    matches = list(re.finditer(anchor, flat.text)) if anchor else []
    if not matches:
        # No anchor hit: keep the head of the document rather than guessing.
        start, end = 0, min(len(flat.text), WHOLE_DOCUMENT_LIMIT)
        label = "window:head"
    else:
        start = max(0, matches[0].start() - WINDOW_LEAD)
        end = min(len(flat.text), max(matches[-1].end() + 200, start + WINDOW_TAIL))
        if end - start > WHOLE_DOCUMENT_LIMIT:
            end = start + WHOLE_DOCUMENT_LIMIT
        label = f"window:{len(matches)}hit"
    raw = flat.span(start, end)
    if raw is None:  # pragma: no cover - only on an empty document
        return (flat, "document", flat.origin)
    return (flatten(doc.text, raw.start, raw.end), label, raw)


def build_input(
    doc: BodyDocument,
    *,
    task: TaskSpec | None = None,
    spec: FieldSpec | None = None,
    section_pattern: str | None = None,
    limit: int = WHOLE_DOCUMENT_LIMIT,
) -> DocumentInput:
    """Choose the regime for one document and return exactly what to send.

    ``section_pattern`` is required for a 증권신고서 — there is no sanctioned way
    to read one whole (field-matrix §5), so an unmatched pattern returns the
    document's **first** section rather than the document.
    """
    if doc.is_registration_statement:
        pattern = section_pattern or (spec.anchor if spec else None) or (
            _anchor_of(task, spec) or "."
        )
        found = find_sections(doc, pattern)
        if not found:
            found = find_sections(doc, ".")
        section = max(found, key=lambda s: s.size) if found else None
        if section is not None:
            flat = flatten(doc.text, section.span.start, section.span.end)
            return DocumentInput(
                scope=f"section:{section.title[:80]}",
                text=flat.text[:limit],
                flat=flat,
                doc=doc,
                span=section.span,
            )

    flat = doc.flat
    if len(flat.text) <= limit:
        return DocumentInput(
            scope="document", text=flat.text, flat=flat, doc=doc, span=flat.origin
        )

    windowed, label, raw = _window(doc, flat, _anchor_of(task, spec))
    return DocumentInput(
        scope=label, text=windowed.text[:limit], flat=windowed, doc=doc, span=raw
    )
