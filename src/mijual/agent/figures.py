"""Thousands-grouped numerals — ``3,200원``, the way the rest of the product prints.

Every other surface groups its figures: ``frontend/lib/format.ts`` puts the commas
back on every won amount, every count and every ratio it renders, because that is
how a Korean reader reads a number. The agent's prose was the one surface that did
not — the model was handed ``{"value": "3200"}`` and wrote ``3200원`` (`P6.REVIEW`
finding 4; the operator's disposition: 「make it 3,200원」).

This module is the whole mechanism, and it is deliberately **presentation only**:

* :func:`grouped` turns a figure into the string a reader reads. It never rounds,
  never converts a unit and never drops a digit — the commas are inserted into the
  integer part and nothing else moves, exactly as ``format.ts``'s ``group()`` does.
* :func:`with_display` walks a tool payload and puts that string **beside** the
  contract's own ``value`` under :data:`DISPLAY_KEY`, so the model sees both and
  the exact served value is still there to be quoted.
* :func:`grouping_table` gives the gate the same figures as
  ``{as the payload writes it: as the reader reads it}``, and :func:`regroup`
  rewrites a released sentence with it — the guarantee, for when a model writes the
  raw digits anyway.

**What is a figure, and what is not.** Only a node the contract itself marks as
one: :meth:`mijual.present.values.Figure.payload` and
:meth:`mijual.present.event.FieldPayload.payload` both emit ``value`` **and**
``estimated``, and that pair is the whole predicate. So 접수번호 (its own key, and
14 digits), a D-day, a span offset, a year, an ``event_id`` and a date are not
figures and are never touched — they are identifiers and readings, not amounts.
A 14-digit bare integer is refused even where it *is* a figure's value: that shape
is a 접수번호 in this product, and leaving one amount ungrouped is cheaper than
grouping one filing number.

**Nothing here computes.** Grouping cannot change which number a sentence states,
so it can neither satisfy nor defeat the never-compute rule — the gate's membership
check normalizes separators away on both sides for that reason
(:func:`mijual.agent.citations._decimal`).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

__all__ = [
    "DISPLAY_KEY",
    "QUOTED_SPAN",
    "grouped",
    "grouping_table",
    "regroup",
    "with_display",
]

#: Where the reader's form travels. Not ``display`` — ``FieldPayload`` already
#: uses that key for its render mode (``"value"`` / ``"추후결정"``).
DISPLAY_KEY = "value_display"

#: The two keys every contract figure carries (``Figure``/``FieldPayload``).
_FIGURE_KEYS = ("value", "estimated")

#: A bare figure: digits, optionally a fraction. A date, a range or an object is
#: not one, and neither is anything with a sign or a unit inside it.
_PLAIN = re.compile(r"\A\d+(?:\.\d+)?\Z")

#: A DART 접수번호's length. Identifier-shaped, therefore never grouped.
_IDENTIFIER_DIGITS = 14

#: Comma positions, counted from the decimal point — ``format.ts``'s own rule.
_GROUP = re.compile(r"(?<=\d)(?=(?:\d{3})+\Z)")

#: A raw (ungrouped) figure in prose. The guards are the requirement, written as
#: lookarounds: not part of a longer number (``15.22``, an already-grouped
#: ``3,200``), not an ISO date's year (``2026-08-26``), not a year the sentence
#: counts in (``2026년``), and not the ``3`` of ``D-3``.
_RAW_FIGURE = re.compile(r"(?<![\d,.\-])\d+(?:\.\d+)?(?![\d,]|년|-\d)")

#: A quoted span, in the three forms the record and the model use. Owned here so
#: :mod:`mijual.agent.citations` checks the same spans this module protects.
QUOTED_SPAN = re.compile(r"「([^「」]*)」|“([^”]*)”|\"([^\"]*)\"")


def grouped(value: Any) -> str | None:
    """``"3200"`` → ``"3,200"``. ``None`` when the value is not a groupable figure.

    ``None`` covers everything that must stay as it is: a value below 1000 (there
    is nothing to group), a date or an object, a 14-digit identifier, and anything
    that is not a bare decimal string or integer.
    """
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    text = str(value).strip()
    if not _PLAIN.match(text):
        return None
    whole, dot, frac = text.partition(".")
    if len(whole) < 4:
        return None
    if not dot and len(whole) == _IDENTIFIER_DIGITS:
        return None
    return _GROUP.sub(",", whole) + (dot + frac)


def _is_figure(node: Any) -> bool:
    return isinstance(node, Mapping) and all(key in node for key in _FIGURE_KEYS)


def with_display(node: Any) -> Any:
    """A copy of a tool payload with :data:`DISPLAY_KEY` beside every figure.

    The contract's ``value`` is untouched and still exact — this only adds the
    reader's spelling of it, which is what lets the model write the same numeral
    the event page prints without ever restating a number in another form.
    """
    if isinstance(node, Mapping):
        out: dict[Any, Any] = {key: with_display(value) for key, value in node.items()}
        if _is_figure(node) and DISPLAY_KEY not in out:
            display = grouped(node.get("value"))
            if display is not None:
                out[DISPLAY_KEY] = display
        return out
    if isinstance(node, list):
        return [with_display(item) for item in node]
    if isinstance(node, tuple):
        return tuple(with_display(item) for item in node)
    return node


def grouping_table(node: Any, table: dict[str, str] | None = None) -> dict[str, str]:
    """Every figure in a payload as ``{raw: grouped}`` — the gate's rewrite table.

    Keyed by the payload's own spelling, so a token in prose is rewritten only when
    it is *literally* a figure this turn's tools returned. Nothing else can match.
    """
    out = table if table is not None else {}
    if isinstance(node, Mapping):
        if _is_figure(node):
            value = node.get("value")
            display = grouped(value)
            if display is not None:
                out[str(value).strip()] = display
        for value in node.values():
            grouping_table(value, out)
    elif isinstance(node, (list, tuple)):
        for value in node:
            grouping_table(value, out)
    return out


def regroup(text: str, table: Mapping[str, str]) -> str:
    """Rewrite the raw figures in a sentence — **never inside a quoted span**.

    A 「…」 span is 공시 원문 the gate verified character for character, so it is
    copied through byte for byte; the grouping only ever reaches the model's own
    prose around it.
    """
    if not table:
        return text
    protected = [match.span() for match in QUOTED_SPAN.finditer(text)]

    def swap(match: re.Match[str]) -> str:
        token = match.group(0)
        if any(start <= match.start() < end for start, end in protected):
            return token
        return table.get(token, token)

    return _RAW_FIGURE.sub(swap, text)
