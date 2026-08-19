"""Deterministic arithmetic — every number the product ever shows.

Handoff §3.6 fixes the AI's role: it **reads** (schema extraction) and it
**speaks** (grounded generation); **all calculation — 금액 환산, D-day — is
deterministic**. This module is that clause in code, and it is the only place a
displayed number may come from.

Four properties are deliberate:

*Pure.* No database, no network, no clock unless one is passed. Every function is
a function of its arguments, so a wrong number is always reproducible.

*KST.* A D-day is a Korean calendar fact. :func:`today_kst` reads the real clock
in Asia/Seoul; every other function takes the reference date as an argument, so
tests never depend on when they run.

*Integer 주식, Decimal 원.* Shares are floored (단수주는 절사) and money is
computed in :class:`~decimal.Decimal` and rounded once, at the end — a float
₩-total over ~10^15 is silently wrong and this is the number the presentation
opens with.

*Small.* The high-value primitives only: the countdown, the 청약 arithmetic §7 #4
names, and the lapsed-warrant shape ``주수 × 배정비율 × 증서가치`` that ``P2.S8``
sums. Anything bigger belongs to the slice that needs it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from math import floor

__all__ = [
    "DDay",
    "KST",
    "allotted_shares",
    "d_day",
    "excess_subscription_cap",
    "lapsed_warrant_value",
    "today_kst",
    "window_state",
]

#: Asia/Seoul. Fixed offset — Korea has had no DST since 1988.
KST = timezone(timedelta(hours=9), name="KST")

#: Window states a countdown can be in.
UPCOMING, OPEN, CLOSED, UNKNOWN = "upcoming", "open", "closed", "unknown"


def today_kst(now: datetime | None = None) -> date:
    """Today in Korea. The single definition of "today" for every countdown."""
    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(KST).date()


@dataclass(frozen=True)
class DDay:
    """A countdown to one gated date. ``days`` is negative once the date passes."""

    target: date
    reference: date
    days: int

    @property
    def label(self) -> str:
        """``D-3`` / ``D-DAY`` / ``D+2`` — the board's own vocabulary."""
        if self.days > 0:
            return f"D-{self.days}"
        if self.days == 0:
            return "D-DAY"
        return f"D+{abs(self.days)}"

    @property
    def is_past(self) -> bool:
        return self.days < 0


def d_day(target: date | None, reference: date | None = None) -> DDay | None:
    """Days from ``reference`` (default: today in KST) to ``target``.

    ``None`` in, ``None`` out — a countdown to a date that does not exist is not
    zero, and a field whose gate said ``tbd`` has no date to count to.
    """
    if target is None:
        return None
    base = reference or today_kst()
    return DDay(target=target, reference=base, days=(target - base).days)


def window_state(start: date | None, end: date | None, on: date | None = None) -> str:
    """Where ``on`` sits relative to a ``[start, end]`` window, inclusive.

    Inclusive on both ends because a 청약 period's last day is a day you can still
    subscribe on — an exclusive end would tell a user the window shut a day early,
    which is the one direction of error this product cannot afford.
    """
    today = on or today_kst()
    if start is None and end is None:
        return UNKNOWN
    if start is not None and today < start:
        return UPCOMING
    if end is not None and today > end:
        return CLOSED
    return OPEN


def allotted_shares(held: int, allotment_ratio: float | Decimal) -> int:
    """``9. 1주당 신주배정주식수`` applied to a holding. **Floored** (단수주 절사).

    The ratio is printed with 10 decimal places (``0.2314082845``), so the
    multiplication runs in :class:`Decimal`: a float here drifts by a share on
    large holdings, and a share is a number a user can check.
    """
    if held <= 0:
        return 0
    return int(floor(Decimal(held) * Decimal(str(allotment_ratio))))


def excess_subscription_cap(allotted: int, excess_ratio: float | Decimal) -> int:
    """§7 #4's arithmetic: 초과청약 한도 = 배정주식수 × 초과청약비율, floored.

    The gate checks the *ratio* against the document (a ratio is all a filing
    states); this is the multiplication itself, which needs a holder's 배정주식수
    and therefore belongs to the calculator P3 puts in front of a user.
    """
    if allotted <= 0:
        return 0
    return int(floor(Decimal(allotted) * Decimal(str(excess_ratio))))


def lapsed_warrant_value(
    shares: int, allotment_ratio: float | Decimal, certificate_price: float | Decimal
) -> Decimal:
    """``주수 × 배정비율 × 증서가치`` — one holder's (or one issue's) lapsed value, in 원.

    The shape ``P2.S8`` sums into the presentation's opening number. Kept here so
    the estimation slice inherits an arithmetic that is already unit-tested, and
    so that every ₩ figure in the phase comes from one function.

    Rounded to the won at the end, once (``ROUND_HALF_UP`` — the Korean
    convention), never per factor.
    """
    if shares <= 0:
        return Decimal(0)
    total = (
        Decimal(shares) * Decimal(str(allotment_ratio)) * Decimal(str(certificate_price))
    )
    return total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
