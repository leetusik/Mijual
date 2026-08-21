"""The KST time policy — the single place this service turns time into JSON.

**The policy, in one rule:** every instant the API emits is an *absolute* KST
timestamp, ISO-8601 with a literal ``+09:00`` offset. The browser only ever
*diffs* such a timestamp; it never derives one.

Why it is a rule and not a preference:

* A D-day is a **Korean calendar fact**. Computed in the browser it becomes a
  fact about the reader's laptop — a 청약 마감 that reads ``D-1`` in Seoul and
  ``D-2`` in Frankfurt is a wrong number, and a wrong number is the one defect
  class this product cannot ship.
* The countdown's direction is per rights type (① 증서 매매 마감 · ② 전환청구
  **개시** · ③ 반대의사 통지 마감), so "지남" means three different things
  (`grounding/ui-traps.md` #5). That judgement belongs upstream, beside the data,
  not in a date library on the client.

Consequences for every later slice:

* Serialize instants with :func:`iso` and calendar dates with :func:`iso_date`.
  A bare ``datetime.isoformat()`` on a naive value silently emits an offsetless
  string, and a client that parses one assumes UTC.
* Compute ``dday`` / ``window_state`` here (server side) with
  :mod:`mijual.calc`, and ship the **absolute** anchor next to the derived
  label so a stale page can recompute rather than lie.
* :data:`KST` is imported from :mod:`mijual.calc`, deliberately re-exported and
  never redefined: the pipeline and the API must agree on what "today" is.

No clock is read anywhere except :func:`now`; everything else takes its
reference as an argument, so tests never depend on when they run — the same
property :mod:`mijual.calc` is built on.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import overload

from mijual.calc import KST, today_kst

__all__ = ["KST", "iso", "iso_date", "now", "to_kst", "today_kst"]


def now() -> datetime:
    """The current instant, as an aware datetime in KST.

    The only clock read in the HTTP layer. Second precision is deliberate: a
    freshness 기준시각 and a countdown anchor are read by humans, and microseconds
    in a rendered timestamp are noise that also breaks byte-exact comparison in
    tests.
    """
    return datetime.now(timezone.utc).astimezone(KST).replace(microsecond=0)


def to_kst(moment: datetime) -> datetime:
    """``moment`` expressed in KST.

    A naive value is read as **UTC**, matching :func:`mijual.calc.today_kst`.
    That is the conservative reading for this codebase: naive datetimes here come
    from the database (Postgres ``timestamp without time zone``, written by a
    worker in UTC), never from a Korean wall clock.
    """
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(KST)


@overload
def iso(moment: datetime) -> str: ...
@overload
def iso(moment: None) -> None: ...


def iso(moment: datetime | None) -> str | None:
    """An instant as ``2026-08-22T01:23:45+09:00``. ``None`` in, ``None`` out.

    ``None`` propagates rather than becoming a placeholder: a timestamp that does
    not exist is not "now", and the contract's rule for an absent value is that
    it is **absent**, never a stand-in.
    """
    if moment is None:
        return None
    return to_kst(moment).replace(microsecond=0).isoformat()


@overload
def iso_date(day: date) -> str: ...
@overload
def iso_date(day: None) -> None: ...


def iso_date(day: date | None) -> str | None:
    """A calendar date as ``2026-08-22``. ``None`` in, ``None`` out.

    Dates carry **no** offset on purpose. 청약일, 매매기간, 전환청구 개시일 are
    Korean calendar days, not instants; pinning one to midnight+09:00 would
    invite a client to shift it back into the previous day.
    """
    return day.isoformat() if day is not None else None
