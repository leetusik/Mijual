"""One summary, so the landing's two cards can never disagree.

R2 puts the same numbers on the page twice — the hero's mono stat line (소멸가치
· 감시 중 · 30일 이내) and the countdown/stats card's 2×2 grid — and R3 adds two
board strips (② 진행 중, 일정 추후결정) counted from the same population. The
build prompt is explicit that the stats card is "fed live from the same summary
the board uses", because two independently computed readouts of one number are
how a product ends up contradicting itself on its own front page.

:class:`BoardSummary` is that one object. Every count in it is defined once, here,
and :func:`board_summary` is the reference derivation over a phase's
:class:`~mijual.present.event.EventView` list — a caller that counts in SQL
instead must produce the same numbers, and the definitions below are what it
matches against.

Two things this module refuses to do:

*Invent the countdown instant.* R2 assumed 2026-09-04 24:00 KST for 계양전기 and
the real 접수 마감 시각 is still an open operator question, so
:attr:`BoardSummary.countdown_target` is whatever the **caller** passes and
``None`` when nobody passes one. ``P5.S3`` serves R2's own assumption as a stated
default (end of the 청약 day, KST) behind a setting the operator replaces without
a code change — see :func:`mijual.web.reads.countdown_target`. The policy is the
service's; this layer only carries the instant it was handed.

*Blur facts into estimates.* 소멸 증서 and 발행 증서 are cited counts and the
소멸률 is their ratio — facts. The 718.1억원 headline and its 548.7억원 band edge
are derived by inverting each filing's own 발행가 산식 — 「추정」, at every size,
including the 44px one (`states-and-trust.md` §1).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from mijual.present.event import EventView
from mijual.present.values import Figure, decimal_str, instant, iso_day

__all__ = [
    "DEFAULT_STALE_AFTER_HOURS",
    "URGENT_DAYS",
    "BoardSummary",
    "Freshness",
    "LapseTotals",
    "board_summary",
    "freshness",
    "lapse_totals",
]

#: The 임박 window the landing counts: inclusive, anchored at the reference day.
#: ``0 <= days <= 30`` — the definition ``board-snapshot.md`` measured 34 with.
URGENT_DAYS = 30

#: How old the corpus may get before the board says so. **18 hours**, and the
#: number comes from the beat schedule rather than from taste: the pipeline runs
#: 07:30 and 19:30 KST (`mijual.scheduler.app.BEAT_SCHEDULE`), so the widest
#: healthy gap is 12 hours and data older than that is normal right before a run.
#: 18h is the smallest threshold that cannot fire on a *healthy* schedule and
#: still fires on the first **missed** beat (a miss reaches ~24h). Below 12h the
#: chip would cry stale twice a day; at 24h a whole skipped run would look fine.
#: R2 left the threshold open; this is the stated default, overridable per
#: deployment (``MIJUAL_STALE_AFTER_HOURS``).
DEFAULT_STALE_AFTER_HOURS = 18


@dataclass(frozen=True)
class Freshness:
    """How old the corpus is, and whether that is old enough to say out loud.

    The board goes **stale, never dark**: when the worker stops, the page keeps
    serving the last known board and states its age. So this is computed for
    every response, not only for a bad one, and the *client never computes it* —
    a browser that diffs its own clock against 기준시각 would report the reader's
    laptop being wrong as the data being stale.

    ``age_hours`` is what the signed chip renders as ``· N시간 전 데이터`` and is
    floored, not rounded: 데이터 that is 5 h 50 m old is 5시간 전, never 6시간 전 —
    a freshness figure must not round *upwards* into an alarm.
    """

    #: 기준시각 — the corpus's most recent observation, absolute KST.
    as_of: datetime | None
    stale: bool
    #: ``None`` when there is no 기준시각 at all (an empty corpus).
    age_hours: int | None
    stale_after_hours: int

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "as_of": instant(self.as_of),
            "stale": self.stale,
            "stale_after_hours": self.stale_after_hours,
        }
        if self.age_hours is not None:
            out["age_hours"] = self.age_hours
        return out


def _aware(moment: datetime) -> datetime:
    return moment if moment.tzinfo is not None else moment.replace(tzinfo=timezone.utc)


def freshness(
    as_of: datetime | None,
    *,
    now: datetime,
    stale_after_hours: int = DEFAULT_STALE_AFTER_HOURS,
) -> Freshness:
    """Age the corpus against ``now``. Both instants, never a date.

    An unknown 기준시각 counts as **stale**: a board that cannot say when it was
    refreshed has not earned the reader's assumption that it is current.
    """
    if as_of is None:
        return Freshness(
            as_of=None, stale=True, age_hours=None, stale_after_hours=stale_after_hours
        )
    # Naive values come from Postgres columns written by a worker in UTC — the
    # same reading :func:`mijual.present.values.instant` makes.
    seconds = (_aware(now) - _aware(as_of)).total_seconds()
    age_hours = int(max(seconds, 0) // 3600)
    return Freshness(
        as_of=as_of,
        stale=seconds > stale_after_hours * 3600,
        age_hours=age_hours,
        stale_after_hours=stale_after_hours,
    )


@dataclass(frozen=True)
class BoardSummary:
    """The board's population and the retrospective headline, in one shape."""

    #: 기준시각 — when the corpus this summary describes was last refreshed, as an
    #: absolute KST instant. The board goes **stale, never dark**: a page that
    #: knows how old it is keeps serving and says so.
    as_of: datetime | None = None
    #: 감시 중 N건 — exposable events, all types.
    watching: int = 0
    #: The tab counts: ``{"R1": 50, "R2": 422, "R3": 16}``.
    by_rights: dict[str, int] = field(default_factory=dict)
    #: 30일 이내 마감 N건.
    within_30d: int = 0
    #: ② 전환청구 **진행 중** — opened and not yet closed. Never labelled 종료.
    open_now: int = 0
    #: 일정 추후결정 — exposable, watched, and with no countdown date at all.
    tbd: int = 0
    #: 소멸 앞둔 신주인수권 N건 — ① offerings whose 청약 has not closed yet.
    lapse_pending: int = 0
    #: 읽은 실적보고서 N건.
    performance_reports: int = 0
    #: 「추정」 2026년에 소멸한 신주인수권 가치, in 원.
    lapsed_value: Figure | None = None
    #: 「추정」 밴드 하한 (권리락 조정 가정), in 원.
    lapsed_value_floor: Figure | None = None
    lapsed_warrants: Figure | None = None
    issued_warrants: Figure | None = None
    lapse_rate: Figure | None = None
    #: The soonest 소멸 — its calendar day and whose it is (소멸주의보 strip).
    next_lapse_date: str | None = None
    next_lapse_corp_name: str | None = None
    #: How many offerings share that earliest 청약 마감 (R9 §6, ``P8.S5``). ``1``
    #: when only the named one does. The surface prints 「N개 종목」 instead of a
    #: company name when it is more, so the strip and the board's own first rows
    #: stop naming different companies for the same date; deriving it here keeps
    #: the count and the name from ever being computed against different lists.
    next_lapse_tie_count: int | None = None
    #: The absolute KST instant the browser ticks down to. ``None`` until the
    #: 소멸 instant is known — the *policy* for turning ``next_lapse_date`` into an
    #: instant belongs to the service (``P5.S3``'s settings), never to this layer.
    countdown_target: datetime | None = None
    #: How old the corpus is (``P5.S3``). ``None`` when the caller passed no clock.
    freshness: "Freshness | None" = None

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "as_of": instant(self.as_of),
            "watching": self.watching,
            "by_rights": dict(self.by_rights),
            "within_30d": self.within_30d,
            "open_now": self.open_now,
            "tbd": self.tbd,
            "lapse_pending": self.lapse_pending,
            "performance_reports": self.performance_reports,
        }
        for key in ("lapsed_value", "lapsed_value_floor", "lapsed_warrants",
                    "issued_warrants", "lapse_rate"):
            figure: Figure | None = getattr(self, key)
            if figure is not None:
                out[key] = figure.payload()
        next_lapse = {
            "date": self.next_lapse_date,
            "corp_name": self.next_lapse_corp_name,
            "target": instant(self.countdown_target),
        }
        if any(value is not None for value in next_lapse.values()):
            payload = {k: v for k, v in next_lapse.items() if v is not None}
            # The tie count is part of *this* object or of nothing: it describes
            # the 마감 the three keys above name.
            if self.next_lapse_tie_count is not None:
                payload["tie_count"] = self.next_lapse_tie_count
            out["next_lapse"] = payload
        if self.freshness is not None:
            out["freshness"] = self.freshness.payload()
        return out


def board_summary(
    views: Sequence[EventView],
    *,
    as_of: datetime | None = None,
    performance_reports: int = 0,
    lapse_pending: int = 0,
    lapsed_value: Decimal | int | None = None,
    lapsed_value_floor: Decimal | int | None = None,
    lapsed_warrants: int | None = None,
    issued_warrants: int | None = None,
    lapse_rate: Decimal | None = None,
    next_lapse_date: date | str | None = None,
    next_lapse_corp_name: str | None = None,
    next_lapse_tie_count: int | None = None,
    countdown_target: datetime | None = None,
    now: datetime | None = None,
    stale_after_hours: int = DEFAULT_STALE_AFTER_HOURS,
) -> BoardSummary:
    """Count one board, and tag the retrospective totals a caller passes in.

    The counts are derived here so their definitions live in one place; the
    retrospective figures come from :mod:`mijual.estimate`'s report, which a
    request path cannot build itself (it imports the extractor), so they arrive
    as arguments — already computed by a worker or read from persisted rows.

    ``lapse_rate`` is **derived from the two counts** when it is not passed, with
    the same 4-decimal quantization :attr:`mijual.estimate.LapseReport.overall_lapse_rate`
    uses, so 소멸률 cannot come out as 14.02 % in one place and 14.0 % in another.
    ``now`` turns ``as_of`` into a :class:`Freshness`; without it the summary
    carries the 기준시각 and says nothing about its age.
    """
    watched = [view for view in views if view.state == "exposable"]
    by_rights: dict[str, int] = {}
    within_30d = open_now = tbd = 0
    for view in watched:
        by_rights[view.rights_type] = by_rights.get(view.rights_type, 0) + 1
        countdown = view.countdown
        if countdown.date is None:
            tbd += 1
            continue
        if countdown.days is not None and 0 <= countdown.days <= URGENT_DAYS:
            within_30d += 1
        # ②'s past opening is the live state, not the closed one: it counts here
        # and must never be counted as 종료 (ui-traps #5).
        if view.rights_type == "R2" and countdown.is_open and countdown.is_past:
            open_now += 1

    return BoardSummary(
        as_of=as_of,
        watching=len(watched),
        by_rights=by_rights,
        within_30d=within_30d,
        open_now=open_now,
        tbd=tbd,
        lapse_pending=lapse_pending,
        performance_reports=performance_reports,
        lapsed_value=Figure.estimate(decimal_str(lapsed_value)),
        lapsed_value_floor=Figure.estimate(decimal_str(lapsed_value_floor)),
        lapsed_warrants=Figure.fact(lapsed_warrants),
        issued_warrants=Figure.fact(issued_warrants),
        lapse_rate=Figure.fact(
            decimal_str(
                lapse_rate if lapse_rate is not None else _rate(lapsed_warrants, issued_warrants)
            )
        ),
        next_lapse_date=iso_day(next_lapse_date),
        next_lapse_corp_name=next_lapse_corp_name,
        next_lapse_tie_count=next_lapse_tie_count,
        countdown_target=countdown_target,
        freshness=(
            freshness(as_of, now=now, stale_after_hours=stale_after_hours)
            if now is not None
            else None
        ),
    )


def _rate(lapsed: int | None, issued: int | None) -> Decimal | None:
    """소멸 / 발행, to 4 decimals — 51,253,956 / 365,527,824 → ``0.1402`` (14.02%)."""
    if not lapsed or not issued:
        return None
    return (Decimal(lapsed) / Decimal(issued)).quantize(Decimal("0.0001"))


@dataclass(frozen=True)
class LapseTotals:
    """2026's whole 소멸 story, added up from the per-offering rows."""

    #: Σ 소멸 증서 and Σ 발행 증서 over **every** offering with a 청약 결과 —
    #: including the ones the product could not value (`counted_only`), because
    #: the shares really did lapse and only their *worth* is unknown.
    lapsed: int | None = None
    issued: int | None = None
    #: Σ 소멸가치 over the **valued** rows only. An offering whose 할인율 failed
    #: its citation gate contributes 0원 here and is the gap the product states
    #: out loud (`states-and-trust.md` §6) rather than filling in.
    value: Decimal | None = None
    value_floor: Decimal | None = None
    offerings: int = 0
    valued: int = 0

    def payload(self) -> dict[str, Any]:
        """JSON — the same fact/estimate split :class:`BoardSummary` makes.

        Used where a *subset* of the corpus is added up (``P5.S4``'s per-stock
        2026 놓친 돈 total). ``offerings``/``valued`` are always present because a
        count of rows is never in doubt; every **figure** is omitted when there is
        nothing to state, so a stock with no 소멸 has no ``value`` key rather than
        ``0원`` — outside the coverage boundary a number is *unstated*, never zero
        (R4-3), and inside it a 0 would still be a claim this product has not
        earned.
        """
        out: dict[str, Any] = {"offerings": self.offerings, "valued": self.valued}
        figures = {
            "lapsed": Figure.fact(self.lapsed),
            "issued": Figure.fact(self.issued),
            "lapse_rate": Figure.fact(decimal_str(_rate(self.lapsed, self.issued))),
            "value": Figure.estimate(decimal_str(self.value)),
            "value_floor": Figure.estimate(decimal_str(self.value_floor)),
        }
        out.update({key: fig.payload() for key, fig in figures.items() if fig is not None})
        return out


def lapse_totals(rows: Sequence[Mapping[str, Any]]) -> LapseTotals:
    """Add up stored ``LapseRow`` mappings (``PerformanceReport.lapse``).

    The same four sums :class:`mijual.estimate.LapseReport` reports, over the
    rows a worker already computed — so the landing headline and
    ``python -m mijual.estimate report`` cannot drift apart. Money is summed as
    :class:`~decimal.Decimal` from the stored strings: 718.1억원 built out of
    JSON floats would not survive the round trip intact.
    """
    lapsed = issued = 0
    value = floor = Decimal(0)
    valued = 0
    for row in rows:
        lapsed += int(row.get("lapsed") or 0)
        issued += int(row.get("warrants_issued") or 0)
        if row.get("status") == "valued" and row.get("value_krw"):
            valued += 1
            value += Decimal(str(row["value_krw"]))
            floor += Decimal(str(row.get("value_floor_krw") or 0))
    return LapseTotals(
        lapsed=lapsed or None,
        issued=issued or None,
        value=value if valued else None,
        value_floor=floor if valued else None,
        offerings=len(rows),
        valued=valued,
    )
