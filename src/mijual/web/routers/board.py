"""The 관제 현황판 and the landing summary — the two reads the front page makes.

``GET /board/summary``
    Every number on the landing, in one object: 감시 중 · 30일 이내 · 소멸 앞둔 ·
    읽은 실적보고서, the 「추정」 소멸가치 headline and its band edge, the 소멸주의보
    strip's soonest 청약 마감, the absolute countdown instant, and 기준시각 with its
    staleness. **One object because the page shows the same numbers twice** — the
    hero's stat line and the countdown/stats card — and two independently computed
    readouts of one number are how a product contradicts itself on its own front
    page (R2's build prompt: the card is "fed live from the same summary the board
    uses").

``GET /board``
    The rows: tab counts, the D-day-ascending list, and the two pinned strips
    (② 전환청구 진행 중, 일정 추후결정). ``?rights=R1|R2|R3`` filters the rows to one
    tab; **the counts stay whole-board**, because the tabs must keep showing what
    the other tabs hold.

Both endpoints take their reference day from the same instant they report as
``now``, so a request that crosses midnight KST cannot compute one D-day against
today and the next against tomorrow. Neither touches OpenDART or a model, neither
writes, and neither decides exposure: they read :class:`~mijual.db.models.Event`'s
persisted verdict and render what :mod:`mijual.present` derives from it.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Query, Request

from mijual.config import Settings
from mijual.present import DEFAULT_STALE_AFTER_HOURS, freshness
from mijual.web import clock
from mijual.web.deps import DbSession
from mijual.web.errors import ApiError
from mijual.web.reads import corpus_as_of, load_board, load_summary, rights_of

router = APIRouter(tags=["board"])

#: The three tabs, as the client names them. 전체 is the absence of a filter.
RIGHTS_TABS = ("R1", "R2", "R3")


def _stale_after(settings: Settings) -> int:
    return settings.stale_after_hours or DEFAULT_STALE_AFTER_HOURS


@router.get("/board/summary", summary="Every landing number, from one summary")
def summary(request: Request, db: DbSession) -> dict[str, Any]:
    settings: Settings = request.app.state.settings
    now = clock.now()
    return load_summary(
        db,
        today=now.date(),
        now=now,
        stale_after_hours=_stale_after(settings),
        cutoff=settings.countdown_cutoff_time,
    ).payload()


@router.get("/board", summary="The board: tab counts, ranked rows, pinned strips")
def board(
    request: Request,
    db: DbSession,
    rights: Annotated[str | None, Query(description="R1 | R2 | R3; omit for 전체")] = None,
) -> dict[str, Any]:
    if rights is not None and rights not in RIGHTS_TABS:
        # A malformed tab is our own client's bug, so it travels as a machine
        # code with no Korean: the design writes state copy, not error copy.
        raise ApiError(
            "unknown_rights_type",
            f"rights must be one of {', '.join(RIGHTS_TABS)}",
            status_code=422,
        )
    settings: Settings = request.app.state.settings
    now = clock.now()
    payload = load_board(db, today=now.date(), rights=rights_of(rights))
    # The chip lives above the tabs, so the board carries its own 기준시각 rather
    # than drawing rows before a second request can say how old they are.
    payload["freshness"] = freshness(
        corpus_as_of(db), now=now, stale_after_hours=_stale_after(settings)
    ).payload()
    return payload
