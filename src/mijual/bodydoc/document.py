"""The document model: decoded 본문 XML with **character-offset preservation**.

Why this exists at all. The P1 spike read 본문 with
``re.sub(r"\\s+", " ", re.sub(r"<[^>]+>", " ", text))`` — correct for a survey,
useless for the product, because it destroys positions. §3.6 layer 2's
**원문 인용 스팬 존재** gate has to answer "where in the stored snapshot does this
value live?", so every value this package extracts carries a :class:`Span` into
``BodyDocument.text`` — the decoded XML **exactly as the snapshot stores it**.

The mechanism is an offset map, not a re-search: :func:`flatten` walks the raw
range once, emitting tag-stripped, entity-decoded, whitespace-collapsed text
while recording, per emitted character, the raw ``[start, end)`` it came from.
A normalized slice therefore converts back to an exact raw span even when the
value was interrupted by markup (``신주인수권증서의 매매 및 매매의 중개를<BR/>
담당할 금융투자업자``) or written with entities.

The round trip is *normalized* equality, not byte equality: ``doc.text[span]``
is the raw XML, which may still hold tags and line breaks.
:meth:`BodyDocument.verify` states the contract the gate will use —
``normalize(doc.text[start:end]) == value``.

Nothing here talks to the network, the database, or an LLM: a
:class:`BodyDocument` is a pure function of one snapshot's bytes.
"""

from __future__ import annotations

import html
import io
import re
import zipfile
from array import array
from dataclasses import dataclass
from functools import cached_property

__all__ = [
    "BodyDocument",
    "Flat",
    "Span",
    "flatten",
    "normalize",
]

_TAG = re.compile(r"<[^>]*>", re.S)
_ENTITY = re.compile(r"&(?:#\d{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});")
_DOC_NAME = re.compile(r"<DOCUMENT-NAME\b([^>]*)>(.*?)</DOCUMENT-NAME>", re.S | re.I)
_ATTR = re.compile(r"([A-Za-z][\w:-]*)\s*=\s*\"([^\"]*)\"")


@dataclass(frozen=True, slots=True, order=True)
class Span:
    """A ``[start, end)`` character range into :attr:`BodyDocument.text`."""

    start: int
    end: int

    def __len__(self) -> int:  # pragma: no cover - trivial
        return max(0, self.end - self.start)

    def __contains__(self, index: int) -> bool:
        return self.start <= index < self.end

    def covers(self, other: "Span") -> bool:
        return self.start <= other.start and other.end <= self.end

    def as_tuple(self) -> tuple[int, int]:
        return (self.start, self.end)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Span({self.start}, {self.end})"


def normalize(fragment: str) -> str:
    """Tag-stripped, entity-decoded, whitespace-collapsed text of ``fragment``.

    The single definition of "the text of this XML" used everywhere in the
    package — including by :meth:`BodyDocument.verify`, so a span produced by
    :class:`Flat` and a span checked by the gate agree by construction.
    """
    return " ".join(html.unescape(_TAG.sub(" ", fragment)).split())


def _attrs(chunk: str) -> dict[str, str]:
    """``NAME="value"`` pairs of one start tag, upper-cased names."""
    return {k.upper(): v for k, v in _ATTR.findall(chunk)}


class Flat:
    """Normalized text of a raw range, plus the map back to raw offsets.

    ``starts[i]`` / ``ends[i]`` are the raw ``[start, end)`` of ``text[i]`` — a
    pair rather than a single index because one normalized character can come
    from several raw ones (``&amp;`` → ``&``).
    """

    __slots__ = ("text", "_starts", "_ends", "origin")

    def __init__(self, text: str, starts: array, ends: array, origin: Span) -> None:
        self.text = text
        self._starts = starts
        self._ends = ends
        #: The raw range this was flattened from.
        self.origin = origin

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.text)

    def span(self, start: int, end: int) -> Span | None:
        """Normalized slice ``[start, end)`` → the raw span it came from.

        Leading/trailing spaces are trimmed first: a collapsed space carries no
        raw width, so including one would make the span start or end nowhere.
        Returns ``None`` when the slice is empty or all whitespace.
        """
        start = max(0, start)
        end = min(len(self.text), end)
        while start < end and self.text[start] == " ":
            start += 1
        while end > start and self.text[end - 1] == " ":
            end -= 1
        if start >= end:
            return None
        return Span(self._starts[start], self._ends[end - 1])

    def span_of(self, value: str, *, start: int = 0) -> Span | None:
        """Raw span of the first occurrence of normalized ``value``."""
        index = self.text.find(value, start)
        return None if index < 0 else self.span(index, index + len(value))

    def match_span(self, match: re.Match, group: int | str = 0) -> Span | None:
        """Raw span of one group of a match taken against :attr:`text`."""
        if match.start(group) < 0:
            return None
        return self.span(match.start(group), match.end(group))


def flatten(raw: str, start: int = 0, end: int | None = None, *, skip: tuple[Span, ...] = ()) -> Flat:
    """Flatten ``raw[start:end]`` to normalized text with an offset map.

    ``skip`` omits sub-ranges entirely (used for nested ``<TABLE>``s when the
    caller is reading a table's *own* rows); each skipped range still acts as a
    token separator, exactly as a tag does.
    """
    end = len(raw) if end is None else end
    skips = sorted(skip)
    chars: list[str] = []
    starts, ends = array("i"), array("i")
    pending = False
    cursor = start
    skip_at = 0

    def emit(ch: str, at: int, upto: int) -> None:
        nonlocal pending
        if pending and chars:
            chars.append(" ")
            starts.append(at)
            ends.append(at)
        pending = False
        chars.append(ch)
        starts.append(at)
        ends.append(upto)

    while cursor < end:
        while skip_at < len(skips) and skips[skip_at].end <= cursor:
            skip_at += 1
        if skip_at < len(skips) and skips[skip_at].start <= cursor:
            cursor = min(end, skips[skip_at].end)
            pending = True
            continue

        ch = raw[cursor]
        if ch == "<":
            tag = _TAG.match(raw, cursor, end)
            if tag is not None:
                cursor = tag.end()
                pending = True
                continue
        if ch == "&":
            entity = _ENTITY.match(raw, cursor, end)
            if entity is not None:
                decoded = html.unescape(entity.group(0))
                if decoded == entity.group(0):
                    # Unknown entity — keep it literally, one raw char each.
                    for offset, dch in enumerate(decoded):
                        emit(dch, cursor + offset, cursor + offset + 1)
                elif not decoded or decoded.isspace():
                    pending = True  # &nbsp; is a separator, not a character
                else:
                    for dch in decoded:
                        emit(dch, cursor, entity.end())
                cursor = entity.end()
                continue
        if ch.isspace():
            pending = True
            cursor += 1
            continue
        emit(ch, cursor, cursor + 1)
        cursor += 1

    return Flat("".join(chars), starts, ends, Span(start, end))


class BodyDocument:
    """One 본문 XML document, addressable by character offset.

    ``text`` is the decoded XML *as the snapshot stores it* — do not normalise,
    re-indent or re-encode it, or every persisted span silently rots.
    """

    __slots__ = ("text", "rcept_no", "member", "__dict__")

    def __init__(self, text: str, *, rcept_no: str | None = None, member: str | None = None) -> None:
        self.text = text
        self.rcept_no = rcept_no
        self.member = member

    # -- construction ------------------------------------------------------
    @classmethod
    def from_bytes(
        cls, blob: bytes, *, rcept_no: str | None = None, member: str | None = None
    ) -> "BodyDocument":
        """Decode a 본문 ZIP snapshot (``Snapshot.payload_bytes``)."""
        from mijual.dart import decode_document  # local: keeps this module import-light

        if not blob.startswith(b"PK"):
            return cls(
                blob.decode("utf-8", errors="replace"), rcept_no=rcept_no, member=member
            )
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            name = member or zf.namelist()[0]
        return cls(decode_document(blob, member=member), rcept_no=rcept_no, member=name)

    @classmethod
    def from_text(cls, text: str, *, rcept_no: str | None = None) -> "BodyDocument":
        return cls(text, rcept_no=rcept_no)

    # -- identity ----------------------------------------------------------
    @cached_property
    def _doc_name(self) -> tuple[str | None, str | None]:
        match = _DOC_NAME.search(self.text)
        if match is None:
            return (None, None)
        return (_attrs(match.group(1)).get("ACODE"), normalize(match.group(2)) or None)

    @property
    def form_code(self) -> str | None:
        """DART form code — ``11306`` 유상증자결정, ``11324`` CB, ``11344`` 합병,
        ``10001`` 증권신고서(지분증권), ``10081`` 증권신고서(합병)."""
        return self._doc_name[0]

    @property
    def doc_name(self) -> str | None:
        """``주요사항보고서(유상증자결정)`` etc., as printed in the document."""
        return self._doc_name[1]

    @cached_property
    def company_name(self) -> str | None:
        """The 회사명 **this filing prints** — not always the DART master name.

        ``rcept_no 20250930000508`` stores master ``풍전약품`` while its own
        ``<COMPANY-NAME>`` reads ``에스씨엠생명과학 주식회사``. That is a
        master-data artifact affecting display only, and the product's rule is to
        show the master name and *state* the disagreement rather than silently
        correct it (`ui-traps.md` #3) — which needs this value, so it is read here
        once rather than re-typed by every surface that compares the two.
        """
        start = self.text.find("<COMPANY-NAME")
        if start < 0:
            return None
        open_end, close = self.text.find(">", start), self.text.find("</COMPANY-NAME>", start)
        if open_end < 0 or close < 0:
            return None
        return " ".join(self.text[open_end + 1 : close].split()) or None

    @property
    def is_registration_statement(self) -> bool:
        """증권신고서 regime: 0.6M–1.9M text chars — **never feed it whole**.

        Field-matrix §5. Use :func:`mijual.bodydoc.sections.sections` and hand a
        named section to the reader instead.
        """
        return (self.form_code or "").startswith("100")

    # -- spans -------------------------------------------------------------
    @cached_property
    def flat(self) -> Flat:
        """Whole-document flat text + offset map.

        Cheap for a 주요사항보고서 (30k–200k chars). For a 증권신고서 slice a
        section first — flattening 3.4M chars costs ~30 MB.
        """
        return flatten(self.text)

    def raw(self, span: Span) -> str:
        """The stored XML under ``span`` — what a citation actually points at."""
        return self.text[span.start : span.end]

    def value_at(self, span: Span) -> str:
        """Normalized text under ``span``."""
        return normalize(self.raw(span))

    def verify(self, span: Span, value: str) -> bool:
        """The layer-2 citation-span contract: does ``span`` still hold ``value``?

        Normalized equality, because the raw slice keeps its markup.
        """
        return self.value_at(span) == normalize(value)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return (
            f"<BodyDocument {self.rcept_no or '?'} {self.doc_name or '?'} "
            f"{len(self.text):,} chars>"
        )
