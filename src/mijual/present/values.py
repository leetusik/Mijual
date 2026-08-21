"""The tagged value — a number the product may render, and how it must be marked.

Everything a surface displays passes through :class:`Figure`, and a ``Figure``
cannot exist without saying which of the product's two kinds of number it is:

===========  =====================================================  ===============
             what it is                                             marked
===========  =====================================================  ===============
**fact**     read from a filing, usually with a verbatim quote and   never
             a span into the stored document — 확정발행가 22,100원,
             소멸 증서 3,734,925주, 전환청구 개시 2026-10-24
**estimate** *derived* — computed from facts by a formula the        「추정」, always
             product owns — 증서 1주 이론가치, 소멸가치, 환산액
===========  =====================================================  ===============

`grounding/states-and-trust.md` §1 states the rule (*an estimate never renders
untagged; a fact never carries the mark*) and R3's contract makes 「추정」 the one
system-wide mark. Both were, until this module, promises a frontend author had to
remember. :attr:`Figure.estimated` has **no default**, so a value that forgets to
say which it is does not construct — the tag is contract-borne.

Three smaller rules are enforced here for the same reason:

*An absent value is absent.* :meth:`Figure.fact` and :meth:`Figure.estimate`
propagate ``None`` (the ``None``-in-``None``-out convention :mod:`mijual.calc`
and :mod:`mijual.web.clock` already use), and :meth:`Figure.payload` omits an
optional key rather than emitting ``null``. A missing number never becomes a
placeholder, a dash or a stale stand-in.

*A derived value carries no verbatim quote.* There is no passage in any filing
that says 「추정」 5,525원 — a quote pinned to an estimate would be a fabricated
citation. The estimate's inputs carry the citations instead.

*Money and ratios serialize as exact decimal strings.* 배정비율 is printed to ten
decimal places (``0.2314082845``) and a ₩ total runs past 10^10; a JSON float
would quietly round both. :func:`decimal_str` never rounds — it only drops a
trailing all-zero fraction, which carries no information.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from mijual.calc import KST

__all__ = ["Figure", "decimal_str", "instant", "iso_day", "to_decimal"]


def to_decimal(value: Any) -> Decimal | None:
    """``6580.0`` → ``Decimal('6580.0')``. Via ``str``, never from a float directly.

    ``Decimal(0.1)`` is ``0.1000000000000000055511151231257827…``; ``Decimal("0.1")``
    is ``0.1``. Every conversion in :mod:`mijual.calc` goes through ``str`` for
    exactly that reason and this one follows it.
    """
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def decimal_str(value: Any) -> str | None:
    """An exact decimal string — ``Decimal('6580.0')`` → ``'6580'``. Never rounded.

    A trailing all-zero fraction is dropped because it says nothing (a price of
    ``6580.0``원 is a price of ``6580`` 원); every other digit survives, so
    ``0.2314082845`` and ``1321.887018868234491362722196`` come through whole. The
    ``"f"`` format is deliberate: ``str(Decimal("1E+3"))`` is ``'1E+3'``, and a
    client parsing a ₩ amount in scientific notation is a bug waiting to happen.
    """
    number = to_decimal(value)
    if number is None:
        return None
    if number == number.to_integral_value():
        return format(number.to_integral_value(), "f")
    return format(number, "f")


def iso_day(value: Any) -> str | None:
    """A **calendar** date as ``2026-08-25`` — bare, with no offset. ``None`` → ``None``.

    Same policy as :func:`mijual.web.clock.iso_date`, and for the same reason:
    청약일, 매매기간 and 전환청구 개시일 are Korean calendar days, not instants.
    Pinning one to midnight+09:00 invites a client to shift it into the previous
    day. Accepts the ISO strings the extraction values carry after their JSON
    round-trip as well as real :class:`~datetime.date` objects.
    """
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and len(value) == 10:
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            return None
    return None


def instant(moment: datetime | None) -> str | None:
    """An **instant** as ``2026-08-22T01:23:45+09:00``. ``None`` → ``None``.

    This is :func:`mijual.web.clock.iso`'s policy — absolute KST, second
    precision, offset always present — restated here rather than imported,
    because the dependency runs ``web → present`` and must not run back. The two
    are pinned together by ``tests/test_present.py`` so they cannot drift.

    A naive value is read as UTC, matching :func:`mijual.calc.today_kst`: naive
    datetimes in this codebase come from Postgres (``timestamp without time
    zone``, written by a worker in UTC), never from a Korean wall clock.
    """
    if moment is None:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(KST).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class Figure:
    """One value a surface may render, and whether it is a fact or an estimate."""

    #: Already serializable — a decimal **string** for money and ratios, an
    #: ``int`` for share and event counts, a bare ISO string for a date.
    value: Any
    #: ``True`` → the surface renders 「추정」 beside it. No default, on purpose.
    estimated: bool
    #: The filing's own words, never paraphrased, corrected or re-punctuated.
    quote: str | None = None
    #: Character offsets of ``quote`` in the stored document.
    span: tuple[int, int] | None = None
    #: The filing the value (or its quote) came from.
    rcept_no: str | None = None

    def __post_init__(self) -> None:
        if self.value is None:
            raise ValueError(
                "a value that does not exist is absent from the payload, never a "
                "Figure carrying None — use Figure.fact()/Figure.estimate()"
            )
        if self.estimated and (self.quote is not None or self.span is not None):
            raise ValueError(
                "an estimate has no verbatim quote: no filing states a derived "
                "number. Cite its inputs instead."
            )

    @classmethod
    def fact(
        cls,
        value: Any,
        *,
        quote: str | None = None,
        span: tuple[int, int] | None = None,
        rcept_no: str | None = None,
    ) -> "Figure | None":
        """A value read from a filing. ``None`` in → ``None`` out (key omitted)."""
        if value is None:
            return None
        return cls(value=value, estimated=False, quote=quote, span=span, rcept_no=rcept_no)

    @classmethod
    def estimate(cls, value: Any, *, rcept_no: str | None = None) -> "Figure | None":
        """A derived value. Always 「추정」. ``None`` in → ``None`` out."""
        if value is None:
            return None
        return cls(value=value, estimated=True, rcept_no=rcept_no)

    def payload(self) -> dict[str, Any]:
        """JSON for one value. Absent optionals are **omitted**, never ``null``."""
        out: dict[str, Any] = {"value": self.value, "estimated": self.estimated}
        if self.quote is not None:
            out["quote"] = self.quote
        if self.span is not None:
            out["span"] = list(self.span)
        if self.rcept_no is not None:
            out["rcept_no"] = self.rcept_no
        return out
