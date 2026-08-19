"""Quote → citation span, **deterministically**. The model never supplies one.

This module is the reason the extractor is allowed to exist at all. §3.6's layer
2 requires a *원문 인용 스팬* per exposed value, and a span invented by a language
model is not evidence — it is a second thing to verify. So the model is asked for
one thing only, a **verbatim quote**, and this code finds that string in the
stored snapshot through :mod:`mijual.bodydoc`'s offset map (N33). What comes back
is a span into the document *as stored*, or nothing.

Four location methods, tried in order, all of them exact string matches — no
fuzzy scoring, no "closest paragraph":

``exact``
    the normalized quote is a substring of the normalized document text. This is
    the case ``BodyDocument.verify(span, quote)`` accepts, and the only one that
    sets ``span_verified``.
``trimmed``
    the same, after stripping quotation marks, brackets, bullets and trailing
    ellipses the model added around a genuine quote — and after dropping a
    **leading list marker**, which is the single most common way a faithful
    quote stops being byte-faithful: the 본문 numbers an item ``①`` and the model
    writes ``1)``. The remainder must still match exactly.
``nospace``
    the same with **all** whitespace removed on both sides. DART's 본문 breaks
    words with ``<BR/>`` and non-breaking spaces, so a faithfully copied quote can
    still differ from the flattened text by one space. The span is real; only the
    spacing differs, which is why it is resolved but not ``verified``.
``head``
    the quote's leading segment before an ellipsis (``…`` / ``...``), at least
    :data:`MIN_HEAD_CHARS` characters. A partial citation, recorded as such.

Anything else is **span-unresolved**: recorded with the model's quote kept, never
promoted to a citation. ``P2.S5``'s gate blocks on it; nothing is silently
dropped, because "the model said X and X is not in the document" is exactly the
finding the accuracy report needs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from mijual.bodydoc.document import BodyDocument, Flat, Span, normalize

__all__ = ["Located", "QuoteLocator", "locate_quote"]

#: A quote shorter than this cannot identify a position in a 10k-char document.
MIN_QUOTE_CHARS = 4
#: An ellipsis head shorter than this is not a citation, it is a coincidence.
MIN_HEAD_CHARS = 12

_ELLIPSIS = re.compile(r"\s*(?:\.{3}|…|~중략~|중략)\s*")
_EDGES = re.compile(r"^[\s\"'“”‘’「」『』<>《》\[\](){}·ㆍ•\-–—:;,.]+|[\s\"'“”‘’「」『』<>《》\[\](){}·ㆍ•\-–—:;,.]+$")
#: A leading list marker the model re-rendered: ``①`` / ``1)`` / ``1.`` / ``가.``.
_MARKER = re.compile(r"^\s*(?:[①-⑳㉠-㉻]|\(?\d{1,2}\s*[.)]|[가-힣]\s*[.)]|[▶▷■□○●※])\s*")


@dataclass(frozen=True)
class Located:
    """Where a quote turned out to live — or that it does not."""

    #: ``resolved`` | ``unresolved`` | ``no_quote``.
    status: str
    span: Span | None = None
    #: ``exact`` | ``trimmed`` | ``nospace`` | ``head`` — how it was found.
    method: str | None = None
    #: ``BodyDocument.verify(span, quote)``: strict normalized equality (N33).
    verified: bool | None = None
    #: The normalized text the span actually covers — what a citation will show.
    text: str | None = None

    @property
    def resolved(self) -> bool:
        return self.status == "resolved"


class QuoteLocator:
    """Locates quotes in one :class:`~mijual.bodydoc.document.Flat`.

    Holds the space-stripped index of the flattened text, which costs one pass
    and makes the ``nospace`` method free for every later quote of the same
    document.
    """

    __slots__ = ("flat", "doc", "_nospace", "_map")

    def __init__(self, flat: Flat, doc: BodyDocument | None = None) -> None:
        self.flat = flat
        self.doc = doc
        self._nospace: str | None = None
        self._map: list[int] | None = None

    def _build_nospace(self) -> tuple[str, list[int]]:
        if self._nospace is None:
            chars: list[str] = []
            positions: list[int] = []
            for index, char in enumerate(self.flat.text):
                if char.isspace():
                    continue
                chars.append(char)
                positions.append(index)
            self._nospace = "".join(chars)
            self._map = positions
        return (self._nospace, self._map or [])

    # -- the four methods -------------------------------------------------
    def _exact(self, needle: str) -> Span | None:
        return self.flat.span_of(needle) if needle else None

    def _nospace_span(self, needle: str) -> Span | None:
        stripped = "".join(needle.split())
        if len(stripped) < MIN_QUOTE_CHARS:
            return None
        haystack, positions = self._build_nospace()
        at = haystack.find(stripped)
        if at < 0:
            return None
        return self.flat.span(positions[at], positions[at + len(stripped) - 1] + 1)

    def locate(self, quote: str | None) -> Located:
        """Find ``quote`` in the document. Pure; no I/O, no model involved."""
        if quote is None or not quote.strip():
            return Located(status="no_quote")
        normalized = normalize(quote)
        if len(normalized) < MIN_QUOTE_CHARS:
            return Located(status="no_quote")

        candidates: list[tuple[str, str]] = [("exact", normalized)]
        for variant in (_EDGES.sub("", normalized), _MARKER.sub("", normalized)):
            if variant and len(variant) >= MIN_QUOTE_CHARS and all(
                variant != seen for _, seen in candidates
            ):
                candidates.append(("trimmed", variant))

        for method, needle in candidates:
            span = self._exact(needle)
            if span is not None:
                return self._resolved(span, quote, method)

        for _, needle in candidates:
            span = self._nospace_span(needle)
            if span is not None:
                return self._resolved(span, quote, "nospace")

        head = _ELLIPSIS.split(normalized)[0].strip()
        if len(head) >= MIN_HEAD_CHARS and head != normalized:
            span = self._exact(head) or self._nospace_span(head)
            if span is not None:
                return self._resolved(span, quote, "head")

        return Located(status="unresolved")

    def _resolved(self, span: Span, quote: str, method: str) -> Located:
        verified = self.doc.verify(span, quote) if self.doc is not None else None
        text = self.doc.value_at(span) if self.doc is not None else None
        return Located(status="resolved", span=span, method=method, verified=verified, text=text)


def locate_quote(flat: Flat, quote: str | None, doc: BodyDocument | None = None) -> Located:
    """One-shot convenience wrapper around :class:`QuoteLocator`."""
    return QuoteLocator(flat, doc).locate(quote)
