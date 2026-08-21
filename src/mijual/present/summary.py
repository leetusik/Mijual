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

*Invent the countdown instant.* R2 assumed 2026-09-04 24:00 KST for 계양전기 but
the real 접수 마감 시각 is still TBC, so :attr:`BoardSummary.countdown_target` is
``None`` until an operator supplies one. A ticker with no instant renders the
calendar date; a ticker with a made-up instant is a wrong number.

*Blur facts into estimates.* 소멸 증서 and 발행 증서 are cited counts and the
소멸률 is their ratio — facts. The 718.1억원 headline and its 548.7억원 band edge
are derived by inverting each filing's own 발행가 산식 — 「추정」, at every size,
including the 44px one (`states-and-trust.md` §1).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from mijual.present.event import EventView
from mijual.present.values import Figure, decimal_str, instant, iso_day

__all__ = ["URGENT_DAYS", "BoardSummary", "board_summary"]

#: The 임박 window the landing counts: inclusive, anchored at the reference day.
#: ``0 <= days <= 30`` — the definition ``board-snapshot.md`` measured 34 with.
URGENT_DAYS = 30


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
    #: The absolute KST instant the browser ticks down to. ``None`` until the
    #: real 접수 마감 시각 is known — never assumed.
    countdown_target: datetime | None = None

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
            out["next_lapse"] = {k: v for k, v in next_lapse.items() if v is not None}
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
    countdown_target: datetime | None = None,
) -> BoardSummary:
    """Count one board, and tag the retrospective totals a caller passes in.

    The counts are derived here so their definitions live in one place; the
    retrospective figures come from :mod:`mijual.estimate`'s report, which a
    request path cannot build itself (it imports the extractor), so they arrive
    as arguments — already computed by a worker or read from persisted rows.
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
        lapse_rate=Figure.fact(decimal_str(lapse_rate)),
        next_lapse_date=iso_day(next_lapse_date),
        next_lapse_corp_name=next_lapse_corp_name,
        countdown_target=countdown_target,
    )
