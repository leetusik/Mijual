"""One row of the 관제 현황판 — and the only extras a row is allowed to carry.

A board row is deliberately **not** a small detail page. R2's row is five cells —
type chip · 회사 + DART 링크 · countdown label + date · per-type extras · D-day —
and the extras cell exists for exactly one type: ① shows its 청약 window and,
while the 발행가 is not fixed, the `발행가 확정 전` chip. **②/③ extras are empty,
and that absence is the design** ("no dash").

So :class:`BoardRow` carries no ``fields`` at all. That is not an omission to be
filled in later by a helpful slice: a row renders no field values, so putting 409
gate-passing fields (some with 600-character quotes) on the board response would
be paying for a payload nobody renders — and it is what lets the board's loader
read one field per event instead of all of them.

Two rules the row inherits and cannot restate wrongly, because it does not
restate them at all:

* the countdown is :class:`~mijual.present.event.Countdown`, computed upstream in
  KST with its own ``window_state`` — the row never says 종료 about a ② whose
  opening is behind us (`ui-traps.md` #5);
* an ① with no 확정발행가 carries **no money**, only the state that says so; the
  extras here are dates and a boolean, never a won amount.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from mijual.present.event import Countdown, EventView
from mijual.present.money import _read, _shareholder_window

if TYPE_CHECKING:  # pragma: no cover - imported for types only
    from mijual.estimate import EventInputs

__all__ = ["BoardOffering", "BoardRow", "board_offering", "board_row"]


@dataclass(frozen=True)
class BoardOffering:
    """①'s extras cell: the 청약 window, and whether the 발행가 is fixed yet.

    Not money and not a price — the two things a row is allowed to say about an
    offering whose value cannot be stated yet. ``price_confirmed=False`` is what
    the signed `발행가 확정 전` chip renders from.
    """

    price_confirmed: bool
    subscription_start: str | None = None
    subscription_end: str | None = None

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"price_confirmed": self.price_confirmed}
        if self.subscription_start is not None:
            out["subscription_start"] = self.subscription_start
        if self.subscription_end is not None:
            out["subscription_end"] = self.subscription_end
        return out


def board_offering(inputs: "EventInputs | Mapping[str, Any] | None") -> BoardOffering | None:
    """The ① extras of one offering, from stored inputs (or ``None`` if none)."""
    if inputs is None:
        return None
    start, end = _shareholder_window(_read(inputs, "subscription"))
    return BoardOffering(
        price_confirmed=_read(inputs, "confirmed_price") is not None,
        subscription_start=start,
        subscription_end=end,
    )


@dataclass(frozen=True)
class BoardRow:
    """One event as the board lists it: identity, countdown, and ①'s extras."""

    event_id: int
    corp_code: str
    corp_name: str | None
    rights_type: str
    #: The filing the row links to on DART. The current readable version's.
    rcept_no: str | None
    state: str
    countdown: Countdown
    offering: BoardOffering | None = None

    @property
    def days(self) -> int | None:
        return self.countdown.days

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "event_id": self.event_id,
            "corp_code": self.corp_code,
            "corp_name": self.corp_name,
            "rights_type": self.rights_type,
            "rcept_no": self.rcept_no,
            "state": self.state,
            "countdown": self.countdown.payload(),
        }
        if self.offering is not None:
            out["offering"] = self.offering.payload()
        return out


def board_row(
    view: EventView, *, offering: "EventInputs | Mapping[str, Any] | None" = None
) -> BoardRow:
    """Project one :class:`~mijual.present.event.EventView` onto a board row.

    ``offering`` is the ① event's stored ``OfferingInput.inputs`` and is ignored
    for ②/③ — their extras cell is empty by design, and passing one would be the
    first step towards a money number on a deadline row.
    """
    return BoardRow(
        event_id=view.event_id,
        corp_code=view.corp_code,
        corp_name=view.identity.corp_name,
        rights_type=view.rights_type,
        rcept_no=view.rcept_no,
        state=view.state,
        countdown=view.countdown,
        offering=board_offering(offering) if view.rights_type == "R1" else None,
    )
