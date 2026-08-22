"""인용 강제 — as a **gate on the generation boundary**, not a check after the fact.

R6 is unambiguous about where this lives: 「검증된 span 없는 주장은 생성 단계에서
차단 (스트림에 나올 수 없음)」. A post-processor that scrubs a finished answer would
already have failed, because on an SSE surface the claim reached the reader the
moment it was generated. So the model's text does not stream to the reader at all:
it streams *into here*, and only what passes leaves.

**How a sentence earns its way out.** Every tool result the turn executes is
:meth:`CitationGate.learn`-ed: its :class:`~mijual.agent.tools.Citation` objects
get short reference ids (``c1``, ``c2``, …) that travel back to the model inside
the function response, and its payload's strings and numbers become the two
vocabularies below. The system instruction then requires an inline
``[[cite:c1]]`` marker on every factual sentence. This gate buffers the stream,
cuts it into sentences, and for each one:

1. **resolves the markers.** Every id must name a citation the tools actually
   returned. One unknown id blocks the sentence — a fabricated citation is worse
   than a missing one, because it *looks* verified.
2. **requires a citation at all.** A sentence with no resolving marker is
   released only when it is verbatim a string a tool returned (the signed 0건
   sentence, a 잠긴 notice, a 본문 quote) — that is a *verified value being
   stated*, not a model claim. Everything else is dropped.
3. **traces every number** (the never-compute rule, R6 §3.6 + Hard rules). Each
   numeric token in the sentence must appear among the values the tools returned.
   A sum, a ratio, a 환산 or a 원 amount the model worked out itself is not in
   that set, so it cannot be released. Its honest limits are recorded below.
4. **requires quotes to be verbatim** (「인용문 재구성·요약 금지」). Any 「…」 or
   "…" span in the prose must occur verbatim in something a tool returned.

**What a blocked sentence does.** It is dropped — never emitted, never marked on
the stream (a visible hole would be a placeholder, and R6 forbids those). The
count rides the terminal event so the rate is observable. If a turn ends with
*nothing* released, the loop states the 검증 미통과 폴백 family: the honest reading
of "the model produced only unverifiable prose" is that this data did not pass
verification, and that is the family the record signs for it.

**Same 근거 = same 번호** (R6-4). Two id spaces, on purpose: the model cites
``c7`` (assigned when the tool ran), the reader sees chip ``1`` (assigned when the
answer first rests on it). The reader's numbering is therefore in reading order
and stable for the whole answer, without the model having to know or manage it.

**Honest limits of the number check.** It is *membership*, not semantics: a token
that appears anywhere in a tool payload passes, so a small integer (1, 2, 3 — or a
year) is effectively always allowed, and a value quoted in the wrong unit or about
the wrong field would pass too. What it catches is the failure that matters and
the one this product cannot ship: a number that exists **nowhere upstream**, which
is exactly the shape of every computed, converted or invented figure. The
structural half of the promise is upstream anyway — a 확정 전 won amount is
*unconstructable* (`P6` Finding 6), so it cannot be in the set to begin with.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from mijual.agent import copy as ko
from mijual.agent.events import AgentEvent, CitationEvent, RefusalEvent, TextEvent
from mijual.agent.tools import Citation, ToolResult

__all__ = ["Blocked", "CitationGate"]

#: The marker the system instruction requires: ``[[cite:c1]]`` / ``[[cite:c1,c4]]``.
_MARKER = re.compile(r"\[\[\s*cite\s*:\s*([^\]]*?)\s*\]\]", re.IGNORECASE)
#: Anything marker-shaped, so a malformed one is stripped from the prose rather
#: than shown to the reader — and takes its sentence down with it (rule 2).
_ANY_MARKER = re.compile(r"\[\[[^\[\]]*\]\]")
#: A numeric token as either side writes it: ``13,220`` · ``15.22`` · ``2026``.
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
#: A quoted span in Korean prose, in the three forms the record and the model use.
_QUOTED = re.compile(r"「([^「」]+)」|“([^”]+)”|\"([^\"]+)\"")
#: A sentence ends at a terminator followed by whitespace **or by a marker** — or
#: at a line break. The lookahead is what keeps ``15.22`` one token instead of two
#: sentences; the ``\[\[`` half is measured behaviour, not defensiveness: the live
#: model writes ``…입니다.[[cite:c2]]`` with no space, and requiring whitespace
#: silently glued a whole answer into one sentence carrying every citation at once.
_SENTENCE_END = re.compile(r"[.!?…](?=\s|\[\[)|\n")
#: A complete marker sitting just past a sentence terminator belongs to the
#: sentence before it — models put it on either side of the full stop.
_TRAILING_MARKER = re.compile(r"\A[ \t]*\[\[[^\[\]]*\]\]")
#: …and a marker that is still streaming means the sentence is not finished.
_PARTIAL_MARKER = re.compile(r"\A[ \t]*\[\[?[^\]]*\Z")
#: A full stop left floating by a removed marker. End of sentence only.
_LOOSE_STOP = re.compile(r"\s+([.!?…])\s*\Z")


@dataclass(frozen=True)
class Blocked:
    """A sentence that did not reach the reader, and why. Never an event."""

    text: str
    reason: str


class CitationGate:
    """One turn's citation forcing: learn from tools, release verified prose."""

    def __init__(self) -> None:
        self._by_ref: dict[str, Citation] = {}
        self._ref_of: dict[tuple[str, str | None], str] = {}
        self._number_of: dict[tuple[str, str | None], int] = {}
        self._values: set[Decimal] = set()
        self._verbatim: list[str] = []
        self._verified: dict[str, tuple[Citation, ...]] = {}
        self._buffer = ""
        #: Every chip the answer actually used, in reading order.
        self.chips: list[CitationEvent] = []
        #: Every sentence released, in order — the answer as the reader read it.
        self.released: list[str] = []
        #: Every sentence the gate refused, with its reason.
        self.blocked: list[Blocked] = []
        #: The refusal family this turn selected, if the model stated one.
        self.family: str | None = None

    # -- learning ---------------------------------------------------------
    def learn(self, result: ToolResult) -> list[dict[str, Any]]:
        """Register a tool result and return its citations **with reference ids**.

        The ids are what makes the marker protocol possible at all: the model can
        only cite something it has been handed an id for, so the citation space is
        closed by construction — there is no id for a filing no tool returned.
        """
        payloads: list[dict[str, Any]] = []
        for citation in result.citations:
            payloads.append({"id": self._ref_for(citation), **citation.payload()})

        # A result that names exactly one filing can lend its citation to a
        # verbatim string of its own (the 철회 notice is the case R6 signs:
        # 「철회 사실 등 검증된 상태에는 근거 칩을 붙임」). Two filings would be a
        # guess, so it lends nothing.
        lends = result.citations if len(set(result.evidence)) == 1 else ()
        for text in _strings_in(result.payload):
            self._verbatim.append(text)
            self._verified.setdefault(_norm(text), lends)
        self._values |= _numbers_in(result.payload)
        return payloads

    def _ref_for(self, citation: Citation) -> str:
        key = _key(citation)
        ref = self._ref_of.get(key)
        if ref is None:
            ref = f"c{len(self._ref_of) + 1}"
            self._ref_of[key] = ref
            self._by_ref[ref] = citation
        return ref

    # -- streaming --------------------------------------------------------
    def feed(self, text: str) -> list[AgentEvent]:
        """Take streamed model text; give back whatever passed the gate."""
        self._buffer += text
        return self._drain(final=False)

    def flush(self) -> list[AgentEvent]:
        """End of a model round: release or drop whatever is left in the buffer."""
        return self._drain(final=True)

    def _drain(self, *, final: bool) -> list[AgentEvent]:
        events: list[AgentEvent] = []
        while True:
            self._buffer = self._buffer.lstrip()
            if not self._buffer:
                break

            family = self._family_at_head()
            if family is not None:
                sentence = ko.REFUSAL_SENTENCES[family]
                self._buffer = self._buffer[len(sentence) :]
                self.family = self.family or family
                self.released.append(sentence)
                events.append(RefusalEvent(family=family, text=sentence))
                continue

            cut = self._cut(final=final)
            if cut is None:
                break
            piece, rest = cut
            # A sentence that is the *start* of a signed family sentence waits for
            # the rest of it — 폴백 is two sentences, and half of it is neither a
            # refusal nor a citable claim.
            if not final and _is_family_prefix(piece):
                break
            self._buffer = rest
            events += self._release(piece)
        return events

    def _family_at_head(self) -> str | None:
        for family, sentence in sorted(
            ko.REFUSAL_SENTENCES.items(), key=lambda item: -len(item[1])
        ):
            if self._buffer.startswith(sentence):
                return family
        return None

    def _cut(self, *, final: bool) -> tuple[str, str] | None:
        """The first complete sentence in the buffer, with its markers attached."""
        match = _SENTENCE_END.search(self._buffer)
        if match is None:
            return (self._buffer, "") if final and self._buffer.strip() else None
        piece, rest = self._buffer[: match.end()], self._buffer[match.end() :]
        while True:
            trailing = _TRAILING_MARKER.match(rest)
            if trailing is None:
                break
            piece, rest = piece + rest[: trailing.end()], rest[trailing.end() :]
        if not final and rest and _PARTIAL_MARKER.match(rest):
            return None  # a marker is still arriving — the sentence is not done
        return piece, rest

    # -- the gate itself --------------------------------------------------
    def _release(self, piece: str) -> list[AgentEvent]:
        refs: list[str] = []
        for marker in _MARKER.finditer(piece):
            refs += [ref.strip() for ref in marker.group(1).split(",") if ref.strip()]
        # Stripping a marker can leave the space that stood before it hanging in
        # front of the full stop (「…입니다 [[cite:c1]].」 → 「…입니다 .」 — measured,
        # 2026-08-22). Closed at the end of the sentence only, so nothing inside a
        # 「verbatim」 span is ever touched.
        text = _LOOSE_STOP.sub(r"\1", _ANY_MARKER.sub("", piece).strip())
        if not text:
            return []  # a marker alone is not a sentence, and not a block either

        unknown = [ref for ref in refs if ref not in self._by_ref]
        if unknown:
            return self._block(text, "unresolved_citation")

        cited = _unique([self._by_ref[ref] for ref in refs])
        if not cited:
            lends = self._verified.get(_norm(text))
            if lends is None:
                return self._block(text, "uncited")
            cited = _unique(lends)

        loose = [token for token in _NUMBER.findall(text) if _decimal(token) not in self._values]
        if loose:
            return self._block(text, "untraceable_number")

        for quoted in _quoted_spans(text):
            if not any(quoted in source for source in self._verbatim):
                return self._block(text, "reconstructed_quote")

        events: list[AgentEvent] = []
        numbers: list[int] = []
        for citation in cited:
            number, chip = self._number_for(citation)
            numbers.append(number)
            if chip is not None:
                events.append(chip)
                self.chips.append(chip)
        self.released.append(text)
        events.append(TextEvent(text=text, citations=tuple(dict.fromkeys(numbers))))
        return events

    def _block(self, text: str, reason: str) -> list[AgentEvent]:
        self.blocked.append(Blocked(text=text, reason=reason))
        return []

    def _number_for(self, citation: Citation) -> tuple[int, CitationEvent | None]:
        """This 근거's chip number — assigned once, on first use (R6-4)."""
        key = _key(citation)
        existing = self._number_of.get(key)
        if existing is not None:
            return existing, None
        number = len(self._number_of) + 1
        self._number_of[key] = number
        return number, CitationEvent(
            number=number,
            rcept_no=citation.rcept_no,
            quote=citation.quote,
            span=citation.span,
            field_key=citation.field_key,
        )

    # -- what the turn ends with ------------------------------------------
    @property
    def answer(self) -> str:
        """The prose exactly as the reader read it — what `P6.S4` stores."""
        return " ".join(self.released)

    @property
    def evidence(self) -> tuple[str, ...]:
        """근거 rcept_no 목록 — the chips shown, in order, deduplicated."""
        return tuple(dict.fromkeys(chip.rcept_no for chip in self.chips))

    @property
    def quotes(self) -> tuple[str, ...]:
        """인용 칩 원문 — verbatim, never reconstructed (R7's own column)."""
        return tuple(
            dict.fromkeys(chip.quote for chip in self.chips if chip.quote is not None)
        )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _key(citation: Citation) -> tuple[str, str | None]:
    """What makes two citations the same 근거: the filing and the words."""
    return (citation.rcept_no, citation.quote)


def _unique(citations: Iterable[Citation]) -> list[Citation]:
    seen: dict[tuple[str, str | None], Citation] = {}
    for citation in citations:
        seen.setdefault(_key(citation), citation)
    return list(seen.values())


def _norm(text: str) -> str:
    """A sentence without its final punctuation — how a payload string is matched."""
    return text.strip().rstrip(" .!?…")


def _is_family_prefix(piece: str) -> bool:
    text = piece.strip()
    return bool(text) and any(
        sentence.startswith(text) and sentence != text
        for sentence in ko.REFUSAL_SENTENCES.values()
    )


def _quoted_spans(text: str) -> list[str]:
    spans: list[str] = []
    for match in _QUOTED.finditer(text):
        spans += [group.strip() for group in match.groups() if group and group.strip()]
    return spans


def _decimal(token: str) -> Decimal | None:
    try:
        return Decimal(token.replace(",", ""))
    except (InvalidOperation, ValueError):
        return None


def _strings_in(node: Any) -> list[str]:
    """Every string a tool payload carries — the verbatim vocabulary."""
    found: list[str] = []
    if isinstance(node, str):
        if len(node.strip()) > 1:
            found.append(node)
    elif isinstance(node, Mapping):
        for value in node.values():
            found += _strings_in(value)
    elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        for value in node:
            found += _strings_in(value)
    return found


def _numbers_in(node: Any) -> set[Decimal]:
    """Every numeric value a tool payload carries, however it is written."""
    values: set[Decimal] = set()
    if isinstance(node, bool):
        return values
    if isinstance(node, (int, float)):
        values.add(Decimal(str(node)))
    elif isinstance(node, Decimal):
        values.add(node)
    elif isinstance(node, str):
        for token in _NUMBER.findall(node):
            parsed = _decimal(token)
            if parsed is not None:
                values.add(parsed)
    elif isinstance(node, Mapping):
        for value in node.values():
            values |= _numbers_in(value)
    elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        for value in node:
            values |= _numbers_in(value)
    return values
