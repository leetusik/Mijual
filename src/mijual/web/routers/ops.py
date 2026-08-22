"""운영 관제 — the operator door and the six tabs' read endpoints.

The transport half of :mod:`mijual.web.ops` (the door) and
:mod:`mijual.web.opsreads` (the numbers). The route map, so ``P5.S17`` can
hard-code it:

===================================  ==========================================
``POST /ops/login``                  운영자 ID + 비밀번호 → ``mj_ops`` cookie
``POST /ops/logout``                 immediate; the session row is deleted
``GET  /ops/session``                ``{authenticated: bool}`` — the door asks
``GET  /ops/overview``               개요: tiles · beat · 최근 실행 · lock · 미결
``GET  /ops/lock``                   lock 칩만 — 모든 탭의 ops 바가 폴링한다
``GET  /ops/gates``                  게이트 대기열: reason 카운트 · 이벤트 상태 · 철회
``GET  /ops/gates/rows``             행 검사, filtered + paged
``GET  /ops/accuracy``               정확도·비용: evalset report + 스펜드 + quota
``GET  /ops/conversations``          대화 로그 (the P6 port)
``GET  /ops/sessions``               익명 세션 (the P6 port)
``GET  /ops/feedback``               save_feedback 대기열 (the P6 port)
``GET  /ops/users``                  사용자: 독자 계정 **and** 익명 세션, unjoined
``GET  /ops/vocky``                  vocky 관찰 뷰 (§6.3, ``P5.S18``'s decision)
===================================  ==========================================

**Everything but the door is a ``GET``, and that is the security property.**
§6.5: 전 화면 읽기 전용 — mutation 엔드포인트 없음. There is no review, clear,
approve or re-run route here and there must never be one: the guarantee that a
field failing its gate is never shown would be worth nothing if an operator could
click it away. The two ``POST`` routes touch only this session's own row, and both
inherit the service-wide CSRF header requirement (:mod:`mijual.web.csrf`).

**Linked from nowhere.** R7 forbids any reader-chrome link to this path — nav,
footer, account menu, sitemap. Nothing under ``/ops`` appears in a reader payload
and no reader router mentions it; ``tests/test_web_ops.py`` asserts the backend
half of that, and ``P5.S17``/``P5.S19`` own the frontend half.

**The vocky route is the one call outside this service.** §6.3 delegated the
observation API's shape to the build; ``P5.S18`` decided it against vocky's
running product and wrote it back into that section of the landed record, so
``GET /ops/vocky`` reads vocky's own ``/api/project/feedback`` server-side
(:mod:`mijual.web.vocky`) instead of inventing a field set. It is read-only, it is
not merged with the ``save_feedback`` queue (§save_feedback: vocky 수집분과 병합
금지 — 상호 링크만), and it degrades to a state rather than a 500 when vocky is
unconfigured or does not answer.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, Query, Request, Response
from pydantic import BaseModel, Field

from mijual.config import Settings
from mijual.web import clock, ops, opsreads, vocky
from mijual.web.conversations import Conversations
from mijual.web.deps import DbSession, WriteSession

router = APIRouter(prefix="/ops", tags=["ops"])


class OperatorCredentials(BaseModel):
    """The door's only input. Both fields travel together and fail together."""

    id: str = Field(max_length=200)
    password: str = Field(max_length=1024)


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _conversations(request: Request) -> Conversations:
    """The P6 port. P5 wires :class:`~mijual.web.conversations.EmptyConversations`."""
    return request.app.state.conversations


# ---------------------------------------------------------------------------
# the door
# ---------------------------------------------------------------------------
@router.post("/login", summary="운영자 로그인 (별도 자격증명)")
def login(
    request: Request,
    response: Response,
    db: WriteSession,
    body: Annotated[OperatorCredentials, Body()],
) -> dict[str, Any]:
    """One failure for every cause, and the same cost for every one of them.

    See :func:`mijual.web.ops.authenticate_operator`. No Korean travels in the
    failure: 「자격증명이 올바르지 않습니다」 is the signed client copy.
    """
    settings = _settings(request)
    ops.authenticate_operator(
        operator_id=body.id, password=body.password, settings=settings
    )
    token = ops.start_ops_session(db, settings)
    ops.set_ops_cookie(response, token, settings)
    return {"authenticated": True}


@router.post("/logout", summary="운영자 로그아웃 (즉시)")
def logout(request: Request, response: Response, db: WriteSession) -> dict[str, Any]:
    """Idempotent, like the reader's: the cookie is cleared either way."""
    ops.end_ops_session(db, request)
    ops.clear_ops_cookie(response, _settings(request))
    return {"authenticated": False}


@router.get("/session", summary="운영자 세션 확인")
def session(request: Request, db: DbSession) -> dict[str, Any]:
    """Not authenticated is a **result**, not a 401.

    The door asks this on load to decide between the Access card and restoring
    the tab the operator was on (R7: 세션 만료 → 문으로 복귀, 로그인 후 있던 탭
    복원). Answering 401 here would make the pre-auth state an error.
    """
    return {"authenticated": ops.has_ops_session(db, request)}


# ---------------------------------------------------------------------------
# 개요
# ---------------------------------------------------------------------------
@router.get("/overview", summary="개요 — 상태 타일 · beat · 최근 실행 · lock")
def overview(
    request: Request,
    db: DbSession,
    _: ops.OpsGate,
    runs: Annotated[int, Query(ge=1, le=200)] = opsreads.RUN_LOG_LIMIT,
) -> dict[str, Any]:
    """Every 개요 fact in one response — including the two the 「실행 기록 없음」
    row is derived from (the schedule's due times and the run log), which the
    client joins. The backend never fabricates a run row for a gap.

    ``decisions`` is the 가동 전 미결 panel's source, quoted from
    ``docs/current/decisions.md`` (R7: decisions 문서에서 읽어 렌더 — 패널에 직접
    쓰지 않음), added by ``P5.S17`` because the panel is signed and had no source.
    """
    return {
        "as_of": clock.iso(clock.now()),
        "gates": opsreads.gate_summary(db),
        "beat": opsreads.beat_view(),
        "runs": opsreads.run_log(db, limit=runs),
        "lock": opsreads.lock_state(_settings(request), db),
        "decisions": opsreads.open_decisions(),
    }


@router.get("/lock", summary="lock 칩 — mijual:lock:pipeline 실시간 상태")
def lock(request: Request, db: DbSession, _: ops.OpsGate) -> dict[str, Any]:
    """The lock chip alone, so 실시간 costs one Redis read and one indexed row.

    R7 puts the chip in the **ops bar**, i.e. on all six tabs and live. The whole
    of ``/ops/overview`` would answer that too, but it walks every exposable event
    to build the 개요 tiles — a poll nobody asked for. This is the same
    :func:`~mijual.web.opsreads.lock_state` the 개요 tab shows, on its own.
    Added by ``P5.S17``; it invents no number and stays read-only, like the rest.
    An expired session answers the same ``401 ops_unauthenticated`` every tab
    does, which is what sends the chip's client back to the door.
    """
    return {"as_of": clock.iso(clock.now())} | opsreads.lock_state(_settings(request), db)


# ---------------------------------------------------------------------------
# 게이트 대기열
# ---------------------------------------------------------------------------
@router.get("/gates", summary="게이트 대기열 — reason 카운트 · 이벤트 상태 · 철회")
def gates(db: DbSession, _: ops.OpsGate) -> dict[str, Any]:
    return {"as_of": clock.iso(clock.now())} | opsreads.gate_queue(db)


@router.get("/gates/rows", summary="행 검사 — 저장된 게이트 판정 한 페이지")
def gate_rows(
    db: DbSession,
    _: ops.OpsGate,
    field_key: str | None = None,
    reason_code: str | None = None,
    gate_status: str | None = None,
    rcept_no: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return opsreads.gate_rows(
        db,
        field_key=field_key,
        reason_code=reason_code,
        gate_status=gate_status,
        rcept_no=rcept_no,
        limit=limit,
        offset=offset,
    )


# ---------------------------------------------------------------------------
# 정확도·비용
# ---------------------------------------------------------------------------
@router.get("/accuracy", summary="정확도·비용 — evalset report + 스펜드 + quota")
def accuracy(db: DbSession, _: ops.OpsGate) -> dict[str, Any]:
    """The evalset half reads **frozen JSON artifacts only** (no DB); the spend
    half reads ``extraction_call`` and the run log. Two sources, both quoted."""
    return {
        "as_of": clock.iso(clock.now()),
        "evalset": opsreads.accuracy(),
        "spend": opsreads.spend(db),
    }


# ---------------------------------------------------------------------------
# 대화 로그 · 익명 세션 · 피드백 — the P6 port
# ---------------------------------------------------------------------------
@router.get("/conversations", summary="대화 로그 (P6 저장소 포트)")
def conversations(
    request: Request,
    _: ops.OpsGate,
    kind: str | None = None,
    refusal_category: str | None = None,
    session_hash: str | None = None,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    """Honest zeros in P5: this build stores no conversations, so there are none.

    Not 「준비 중」 — that would be an invented Korean string — and not a 404: the
    tab is signed and complete, and its content arrives when P6 implements the
    port (:mod:`mijual.web.conversations`).
    """
    return _conversations(request).conversations(
        kind=kind,
        refusal_category=refusal_category,
        session_hash=session_hash,
        cursor=cursor,
        limit=limit,
    ).payload()


@router.get("/sessions", summary="익명 세션 집계 (P6 저장소 포트)")
def sessions(
    request: Request,
    _: ops.OpsGate,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    return _conversations(request).sessions(cursor=cursor, limit=limit).payload()


@router.get("/feedback", summary="save_feedback 대기열 (P6 저장소 포트)")
def feedback(
    request: Request,
    _: ops.OpsGate,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    return _conversations(request).feedback(cursor=cursor, limit=limit).payload()


# ---------------------------------------------------------------------------
# vocky 관찰 뷰 — the one read that leaves this service
# ---------------------------------------------------------------------------
@router.get("/vocky", summary="vocky 관찰 뷰 — 수집된 피드백 (읽기 전용)")
def vocky_observation(
    request: Request,
    _: ops.OpsGate,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=vocky.MAX_LIMIT)] = vocky.DEFAULT_LIMIT,
) -> dict[str, Any]:
    """One page of vocky's collected feedback, read server-side and never merged.

    The ceiling is **vocky's own** (100), not this panel's usual 200: forwarding a
    larger limit would earn a 400 from vocky rather than more rows. ``cursor`` is
    vocky's opaque keyset cursor, carried through in both directions untouched.

    This route takes no ``DbSession`` of its own — :data:`~mijual.web.ops.OpsGate`
    already opens one to check the operator session, and the observation itself is
    a fact about **vocky's** store, not this one. Nothing is cached and nothing is
    written: a page of it is what vocky said when the operator asked.
    """
    return {"as_of": clock.iso(clock.now())} | vocky.observe(
        _settings(request), limit=limit, cursor=cursor
    ).payload()


# ---------------------------------------------------------------------------
# 사용자 — two tables, no join
# ---------------------------------------------------------------------------
@router.get("/users", summary="사용자 — 독자 계정 + 익명 세션 (조인 없음)")
def users(
    request: Request,
    db: DbSession,
    _: ops.OpsGate,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    """**Two independent reads in one response, and never a third that relates them.**

    ``accounts`` comes from the reader tables; ``sessions`` comes from the P6
    port. There is no key in either block that could be matched against the other,
    and there is no query anywhere that touches both — 계정↔대화 연결
    컴럼·조인·추정 매칭 금지, kept at the schema level, which is what makes
    「대화는 익명으로 저장됩니다」 structural rather than procedural.
    """
    return {
        "accounts": opsreads.reader_accounts(db, limit=limit, offset=offset),
        "sessions": _conversations(request).sessions(limit=limit).payload(),
    }
