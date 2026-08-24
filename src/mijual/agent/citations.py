"""인용 강제 — **strip, don't drop** (R16 §2.5, Q-B).

R6 put this gate on the generation boundary and had it *judge*: a sentence whose
markers did not resolve, or that cited nothing, or that stated a number no tool
returned, was discarded before the reader could see it. R16 supersedes the
judgement and keeps the boundary. The model's text still does not stream to the
reader — it streams *into here* — but what leaves is now the prose the model
wrote, with everything unverifiable **taken out of it** rather than the sentence
taken away:

1. **markers leave.** Every ``[[cite:…]]`` is removed from the prose (the reader
   sees numbered chips, never marker syntax). One that names a citation the tools
   actually returned becomes that chip; one naming an id nothing returned, or one
   that is malformed or still half-arrived, is simply gone — 「인식되지 않는
   마커는 제거되고 문장은 남는다」 (build-prompt §3.1). The horizontal whitespace
   that introduced it goes with it, so 「…입니다 [[cite:c1]].」 reads
   「…입니다.」 and not 「…입니다 .」 (§4 check 3).
2. **an uncited sentence ships.** A greeting, a short confirmation, a meta answer
   about 미주얼 — none of them has anything to cite, and dropping them is the
   defect this phase exists to fix (「안녕」 must not return a refusal). A sentence
   that is verbatim a string a tool returned still travels as **copy**: it leaves
   byte for byte as the payload wrote it and borrows that result's 근거 (`P8` —
   the signed 0건 sentence and the 철회 notice reach the reader unparaphrased).
3. **an untraceable figure is marked, not deleted.** Every 공시-shaped figure in
   the prose — an amount, a share count, a rate, a date, a 접수번호 — is looked up
   in the values the turn's tools returned (:meth:`CitationGate.learn`). One that
   is in none of them is reported as an :attr:`~mijual.agent.events.TextEvent.
   unverified` span, which the surface draws as the 「미확인」 marker (R16 D6).
   The sentence stands and the turn stands: Q-B is **claim level**, never a
   turn-replacing gate. §2.5's bar is 마커도 칩도 없는 숫자는 존재해서는 안 된다,
   so the check runs on cited sentences too — a chip says *this filing*, it does
   not say *this number came from it*.
4. **a fabricated quote loses its quotation marks, not its sentence.**
   「인용문 재구성 금지」 is explicitly **not** superseded by R16 (result.md §5), and
   the strip-era reading of it is the same move as stripping a marker: a 「…」 span
   that occurs verbatim in nothing a tool returned is released **without the
   marks**. The words survive as the assistant's own prose (and their figures are
   then traced like any other), and what does not survive is the *claim of being
   원문* — which is the whole of what that rule protects.

**What a released sentence is respelled to.** Once a sentence has passed, its raw
figures are written the way the rest of the product writes them — ``3200원`` →
``3,200원`` (:mod:`mijual.agent.figures`, `P6.F1`). Only tokens that are literally
a figure this turn's tools returned, only outside a 「…」 span, and never a sentence
that is itself a tool's own string: verbatim stays verbatim, and the number a
sentence states never changes. The reader's form is what
:attr:`CitationGate.released` keeps, so the 대화 로그 stores what was read.

**What :attr:`CitationGate.blocked` counts.** Removed markers, not dropped
sentences (R16 §1: 「삭제된 문장 수가 아니라 제거된 마커 수」) — and only the ones
that were removed *without being honoured*: an id no tool returned, a malformed
marker, a marker cut in half by the end of the stream. It rides
:class:`~mijual.agent.events.TurnEnd` so an operator can watch the model's citing
rather than infer it; nothing the reader saw is missing because of it.

**Same 근거 = same 번호** (R6-4). Two id spaces, on purpose: the model cites
``c7`` (assigned when the tool ran), the reader sees chip ``1`` (assigned when the
answer first rests on it). The reader's numbering is therefore in reading order
and stable for the whole answer, without the model having to know or manage it.

**Honest limits of the figure check.** It is *membership*, not semantics: a token
that appears anywhere in a tool payload passes, so a value quoted in the wrong
unit or about the wrong field passes too, and a turn that read a filing has a
large set. What it catches is the failure that matters: a figure that exists
**nowhere upstream**, which is the shape of every computed, converted or invented
one. The structural half of the promise is upstream anyway — a 확정 전 won amount
is *unconstructable* (`P6` Finding 6), so it cannot be in the set to begin with.
Two deliberate readings ride on top of it: a figure the **reader** typed is not
traced (nothing verified it, and echoing it back unmarked would be the laundering
§2.5 forbids — the calculator tool returns its inputs, which is what makes a
reader's number traceable once `P9.S5` lands), and a number carrying none of the
product's figure shapes (「3가지」, 「2026년」) is not a 공시 수치 at all and is never
marked. Q-B is about 공시 특정 수치, not about digits.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any

from mijual.agent import copy as ko
from mijual.agent import figures
from mijual.agent.events import AgentEvent, CitationEvent, RefusalEvent, TextEvent
from mijual.agent.tools import Citation, ToolResult

__all__ = ["CitationGate"]

#: The marker the system instruction requires: ``[[cite:c1]]`` / ``[[cite:c1,c4]]``.
_MARKER = re.compile(r"\[\[\s*cite\s*:\s*([^\]]*?)\s*\]\]", re.IGNORECASE)
#: Anything marker-shaped, so a malformed one leaves the prose rather than being
#: shown to the reader — **without** taking its sentence with it. Deliberately
#: total: it opens at ``[[`` and closes at ``]]``, at the two brackets a typo left,
#: or at the end of the piece (a marker cut in half by a dying stream). Marker
#: debris on the reader's screen is the one thing stripping exists to prevent.
#: The leading ``[ \t]*`` is the space that introduced the marker — it goes with it
#: (build-prompt §4 check 3: 선행 공백도 함께 정리된다).
_ANY_MARKER = re.compile(r"[ \t]*\[\[[^\[\]]*\]{0,2}")
#: A numeric token as either side writes it: ``13,220`` · ``15.22`` · ``2026``.
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
#: A quoted span in Korean prose, in the three forms the record and the model use.
#: One pattern, shared with :mod:`mijual.agent.figures`: the spans this gate
#: verifies are exactly the spans the grouping refuses to touch.
_QUOTED = figures.QUOTED_SPAN
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
#: A full stop left floating by a removed marker. End of sentence only, and the
#: backstop for the whitespace :data:`_ANY_MARKER` cannot eat (a line break).
_LOOSE_STOP = re.compile(r"\s+([.!?…])\s*\Z")

#: A **공시 figure as this product's prose writes one** — the shapes Q-B is about
#: (도구가 반환하지 않은 공시 특정 수치), and nothing else. A bare number is not one:
#: 「3가지」 and 「2026년」 are readings, not 공시 수치, and marking them would put a
#: 「미확인」 marker in the middle of ordinary conversation (build-prompt §4 check 1:
#: 「안녕」 is a greeting, not a hedged one). A date is matched **whole** so one date
#: draws one marker rather than three, and the span the surface marks includes the
#: unit — 「3,200원」 reads as one value and the marker follows it, never splits it.
_FILING_FIGURE = re.compile(
    r"""
      \d{4}-\d{2}-\d{2}                              # 2026-08-30
    | \d{4}년\s*\d{1,2}월(?:\s*\d{1,2}일)?           # 2026년 8월 30일 · 2026년 8월
    | \d{1,2}월\s*\d{1,2}일                          # 8월 30일
    | \d{14}                                         # 접수번호 꼴
    | \d[\d,]*(?:\.\d+)?\s*[만억조]?\s*(?:원|주|%|배)   # 3,200원 · 1,000주 · 15.22% · 2배
    | \d{1,3}(?:,\d{3})+(?:\.\d+)?                   # 13,220 — 자릿점이 곧 금액 꼴
    | \d+\.\d+                                      # 15.22 — 소수점이 곧 비율 꼴
    """,
    re.VERBOSE,
)


class CitationGate:
    """One turn's citation forcing: learn from tools, release stripped prose."""

    def __init__(self) -> None:
        self._by_ref: dict[str, Citation] = {}
        self._ref_of: dict[tuple[str, str | None], str] = {}
        self._number_of: dict[tuple[str, str | None], int] = {}
        self._values: set[Decimal] = set()
        #: ``{as a payload writes a figure: as the reader reads it}`` — the
        #: turn's own numerals, and the only tokens :meth:`_release` may respell.
        self._grouping: dict[str, str] = {}
        self._verbatim: list[str] = []
        self._verified: dict[str, tuple[Citation, ...]] = {}
        self._buffer = ""
        #: Every chip the answer actually used, in reading order.
        self.chips: list[CitationEvent] = []
        #: Every sentence released, in order — the answer as the reader read it.
        self.released: list[str] = []
        #: How many markers were removed without being honoured (R16 §1). A count,
        #: not a list of losses: nothing is dropped any more.
        self.blocked: int = 0
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
        figures.grouping_table(result.payload, self._grouping)
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
        """Take streamed model text; give back the sentences it completed."""
        self._buffer += text
        return self._drain(final=False)

    def flush(self) -> list[AgentEvent]:
        """End of a model round: release whatever is left in the buffer."""
        return self._drain(final=True)

    def _drain(self, *, final: bool) -> list[AgentEvent]:
        events: list[AgentEvent] = []
        while True:
            self._buffer = self._buffer.lstrip()
            if not self._buffer:
                break

            family = self._family_at_head()
            if family is not None:
                sentence = ko.LIVE_REFUSAL_SENTENCES[family]
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
            # the rest of it — a family sentence may carry an internal full stop,
            # and half of one is neither a refusal nor prose worth releasing.
            if not final and _is_family_prefix(piece):
                break
            self._buffer = rest
            events += self._release(piece)
        return events

    def _family_at_head(self) -> str | None:
        """The signed sentence the buffer starts with, if it is a **live** family.

        Exact string match, longest first. A **retired** family (R16 §0: 계산 요청
        and 검증 미통과 폴백 are read-only, for past rows) is deliberately not
        recognised here: recognising one would newly record it the moment the
        model happened to type its words. Those sentences release as ordinary
        prose instead, which is what strip-don't-drop does with any prose.
        """
        for family, sentence in sorted(
            ko.LIVE_REFUSAL_SENTENCES.items(), key=lambda item: -len(item[1])
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
        """Strip, don't drop: markers out, chips resolved, the prose released."""
        stripped, markers = _strip_markers(piece)
        # A marker is *honoured* when every id it named exists; anything else —
        # an invented id, a malformed marker, half of one — was removed for
        # nothing, and that is what the terminal's count is about.
        self.blocked += sum(
            1
            for marker in markers
            if not marker or any(ref not in self._by_ref for ref in marker)
        )
        text = _LOOSE_STOP.sub(r"\1", stripped.strip())
        if not text:
            return []  # a marker alone is not a sentence

        cited = _unique(
            self._by_ref[ref]
            for marker in markers
            for ref in marker
            if ref in self._by_ref
        )
        # A sentence that *is* a tool's own string (a locked notice, the signed
        # 0건 sentence) is copy, not prose (`P8`): it leaves exactly as the payload
        # wrote it — unrespelled, unmarked — and borrows that result's 근거.
        lends = None if cited else self._verified.get(_norm(text))
        unverified: tuple[tuple[int, int], ...] = ()
        if lends is not None:
            cited = _unique(lends)
        else:
            # 「인용문 재구성 금지」 first (a fabricated quote must not reach the
            # reader **as a quote**), then 3,200원 like every other surface
            # (`P6.F1`) — only this turn's own figures, only outside a quoted
            # span — and last the 미확인 spans, whose offsets are into the text
            # the reader will actually receive.
            text = figures.regroup(self._dequote(text), self._grouping)
            unverified = self._unverified(text)

        events: list[AgentEvent] = []
        numbers: list[int] = []
        for citation in cited:
            number, chip = self.cite(citation)
            numbers.append(number)
            if chip is not None:
                events.append(chip)
        self.released.append(text)
        events.append(
            TextEvent(
                text=text,
                citations=tuple(dict.fromkeys(numbers)),
                unverified=unverified,
            )
        )
        return events

    def _dequote(self, text: str) -> str:
        """A 「…」 span nothing returned loses its **marks**, never its sentence.

        R16 does not supersede 「인용문 재구성 금지」 (result.md §5), and under
        strip-don't-drop the honest reading of it is the marker rule applied to
        quotation: what must not reach the reader is the *claim* that these are
        공시 원문, so the claim is what is removed. The words stay as the
        assistant's own prose and their figures are traced like any others.
        """

        def unmark(match: re.Match[str]) -> str:
            inner = next((group for group in match.groups() if group is not None), "")
            verbatim = inner.strip()
            if not verbatim or any(verbatim in source for source in self._verbatim):
                return match.group(0)
            return inner

        return _QUOTED.sub(unmark, text)

    def _unverified(self, text: str) -> tuple[tuple[int, int], ...]:
        """「미확인」 — the 공시 figures in this sentence that no tool returned.

        Character offsets **within the sentence** (R16 §1), over the figure as the
        reader reads it, unit included. A verified 「…」 span is skipped: it is the
        filing's own words, and its numbers are the payload's by construction.
        """
        protected = [match.span() for match in _QUOTED.finditer(text)]
        spans: list[tuple[int, int]] = []
        for match in _FILING_FIGURE.finditer(text):
            if any(start <= match.start() < end for start, end in protected):
                continue
            tokens = _NUMBER.findall(match.group(0))
            if all(_decimal(token) in self._values for token in tokens):
                continue
            spans.append((match.start(), match.end()))
        return tuple(spans)

    def cite(self, citation: Citation) -> tuple[int, CitationEvent | None]:
        """This 근거's chip number, and its **definition** the first time only.

        The one door to the reader's numbering, for prose *and* for the places
        R16 §2.6 adds a chip to (a 데이터 행's value, a 계산 블록's input): a
        caller emits the returned :class:`~mijual.agent.events.CitationEvent`
        immediately before the block that names the number, and 같은 근거 = 같은
        번호 holds across all of them because they share this one counter.
        """
        number, chip = self._number_for(citation)
        if chip is not None:
            self.chips.append(chip)
        return number, chip

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
    """Is this cut the *beginning* of a live family sentence, still arriving?

    Live only, for :meth:`CitationGate._family_at_head`'s reason. It stays
    load-bearing because a signed family sentence can carry an internal full stop
    — R16's 보안 sentence is two of them (`P9.S6`) — and half of one is neither a
    refusal nor prose the reader should see arrive on its own.
    """
    text = piece.strip()
    return bool(text) and any(
        sentence.startswith(text) and sentence != text
        for sentence in ko.LIVE_REFUSAL_SENTENCES.values()
    )


def _strip_markers(piece: str) -> tuple[str, list[list[str]]]:
    """The prose without its markers, and the ids each removed marker named.

    Every marker leaves — the reader sees chips, never marker syntax — so what
    comes back is one list per removed marker: the reference ids it named, or an
    empty list when it named none the protocol could read (a malformed marker, or
    one the end of the stream cut in half). The caller resolves the ids it knows
    and counts the markers it could not honour.
    """
    markers: list[list[str]] = []

    def take(match: re.Match[str]) -> str:
        cite = _MARKER.fullmatch(match.group(0).strip())
        markers.append(
            [ref.strip() for ref in cite.group(1).split(",") if ref.strip()]
            if cite is not None
            else []
        )
        return ""

    return _ANY_MARKER.sub(take, piece), markers


def _decimal(token: str) -> Decimal | None:
    """A numeric token as a value, **with its separators normalized away**.

    ``3,200`` and ``3200`` are one number written two ways, and the membership
    check has to trace both — the payload may carry either and the reader is shown
    the grouped one (:mod:`mijual.agent.figures`). Grouping is presentation, never
    computation: it can neither put a number into the traceable set nor take one
    out, which is why normalizing here does not weaken the never-compute rule.
    """
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
