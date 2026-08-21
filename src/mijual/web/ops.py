"""The operator door — a separate credential, a separate session, one failure.

R7 §6.4 and `security` fix what this is, and every word of it is a prohibition:

    운영자 ID + 비밀번호, R5 계정 테이블과 완전 분리 (조인 없음, admin flag 아님).
    자격은 배포 환경에서 발급·회전 — 가입·재설정 UI 없음. 실패 응답 균일
    「자격증명이 올바르지 않습니다」 + 상수 시간; 어느 필드가 틀렸는지 구분 금지.
    세션 쿠키 httpOnly·secure, reader 세션과 별도 이름.

**Separate is structural, not careful.** The credential lives in the environment
(``MIJUAL_OPS_ID`` / ``MIJUAL_OPS_PASSWORD``), so there is no operator row, no
``admin`` column on :class:`~mijual.db.models.Account`, and nothing to join.
:class:`~mijual.db.models.OpsSession` has no ``account_id`` and no operator
identifier either: a row means "somebody proved they hold the credential", which
is the entire fact this service needs. Rotating the credential is editing the
environment and restarting; there is no reset flow to attack, because there is
nothing to reset.

**One failure, one cost.** Unknown ID, wrong password, and *credential not
configured at all* return a byte-identical body with one structural code
(``invalid_credentials``, 401), and each of the three spends exactly one scrypt
verification — the configured password is hashed once per process and the miss
path burns a verification against a dummy hash, the shape ``P5.S7`` established
for the reader login. The ID comparison is
:func:`hmac.compare_digest` and both checks are always evaluated: a short-circuit
would leak "the ID exists" in the timing the constant-time body is there to hide.

**Attempt limiting is recorded, not built.** `security`: "Admin login attempt
limiting: server-side, no UI copy". Doing it honestly needs state shared across
processes (Redis, or the reverse proxy), which is **P4**'s to own — the same call
``P5.S7`` made for the reader login. A per-process counter would be security
theatre in front of a two-worker deployment.

**The cookie, decided** (the reader's, with the two differences that matter):

======================  ==========================================================
name                    ``mj_ops`` — reserved by ``P5.S7`` as
                        :data:`mijual.web.auth.OPS_COOKIE` precisely so the two
                        could never collide. `security` requires it to be
                        differently named from ``mj_session``.
flags                   ``HttpOnly``, ``SameSite=Lax``, ``Path=/``, ``Secure``
                        from ``MIJUAL_COOKIE_SECURE`` (**P4 must turn it on**;
                        a ``Secure`` cookie on a plain-http dev server silently
                        never arrives).
lifetime                **12 hours, absolute**, never extended on a read — a
                        working day. A reader session lasts 30 days because a
                        reader is on their own device; an operator console is a
                        surface that should not still be open tomorrow morning.
                        Expiry answers **401** and the client returns to the door
                        and restores the tab afterwards (R7's own words).
CSRF                    inherited: :mod:`mijual.web.csrf` refuses every unsafe
                        method without ``X-Mijual-CSRF``, including this login.
======================  ==========================================================

**Read-only is the rest of the panel.** The two routes here are the only
state-changing ones under ``/ops`` and they touch nothing but this session's own
row. Every other ops route is a ``GET`` (§6.5: mutation 엔드포인트 없음).
"""

from __future__ import annotations

import hmac
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from mijual.config import Settings
from mijual.db.models import OpsSession, utcnow
from mijual.web import passwords
from mijual.web.auth import OPS_COOKIE, new_token, token_digest
from mijual.web.deps import DbSession
from mijual.web.errors import ApiError

__all__ = [
    "OPS_COOKIE",
    "OPS_SESSION_LIFETIME",
    "OpsGate",
    "authenticate_operator",
    "clear_ops_cookie",
    "end_ops_session",
    "has_ops_session",
    "set_ops_cookie",
    "start_ops_session",
]

#: 12 hours, absolute. See the module docstring for why it is not the reader's 30
#: days — and why it is not extended on a read (a sliding window would have to
#: write during a ``GET``, which this service structurally refuses).
OPS_SESSION_LIFETIME = timedelta(hours=12)

#: Hash of the configured password, derived once per process. ``None`` = not yet
#: derived; the dummy below is what a miss verifies against so every outcome
#: costs one scrypt.
_ops_hash: str | None = None
_dummy_hash: str | None = None


def _invalid_credentials() -> ApiError:
    """The **only** thing this door ever says about a failure.

    One code, one message, one status, for a wrong password, an unknown 운영자 ID
    and an unconfigured credential alike. R7: "어느 필드가 틀렸는지 구분 금지"; and
    no Korean travels in it — 「자격증명이 올바르지 않습니다」 is the signed client
    copy, and a second phrasing invented here would be a design change
    (:mod:`mijual.web.errors`).
    """
    return ApiError("invalid_credentials", "operator credentials are wrong", status_code=401)


def _configured_hash(settings: Settings) -> str | None:
    """The configured password's hash, derived once. ``None`` when unset."""
    global _ops_hash
    secret = settings.ops_password
    if not secret:
        return None
    if _ops_hash is None or not passwords.verify(secret, _ops_hash):
        # Derived from the *current* setting, so a rotated credential in a
        # re-created app takes effect without a stale hash lingering in a global.
        _ops_hash = passwords.hash_password(secret)
    return _ops_hash


def _burn_a_hash(password: str) -> None:
    """Spend a verification on nothing, so a miss costs what a hit costs."""
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = passwords.hash_password("not-a-real-operator-password")
    passwords.verify(password, _dummy_hash)


def authenticate_operator(*, operator_id: str, password: str, settings: Settings) -> None:
    """Verify the operator credential, or raise the one uniform failure.

    Returns nothing on success: there is no operator *identity* to return, which
    is the whole point of a credential that has no row. Both halves are always
    evaluated and exactly one scrypt verification is always spent.
    """
    configured_id = settings.ops_id or ""
    configured_hash = _configured_hash(settings)

    id_ok = bool(configured_id) and hmac.compare_digest(
        (operator_id or "").encode("utf-8"), configured_id.encode("utf-8")
    )
    if configured_hash is None:
        # No credential is configured: the door never opens, and it takes exactly
        # as long to say so as a wrong password does.
        _burn_a_hash(password or "")
        raise _invalid_credentials()
    password_ok = passwords.verify(password or "", configured_hash)

    if not (id_ok and password_ok):
        raise _invalid_credentials()


# ---------------------------------------------------------------------------
# sessions
# ---------------------------------------------------------------------------
def start_ops_session(db: Session, settings: Settings) -> str:
    """Mint an operator session and return the raw token for the cookie."""
    now = utcnow()
    # A login is a write already — the cheapest honest place to drop dead rows.
    db.execute(delete(OpsSession).where(OpsSession.expires_at <= now))
    token = new_token()
    db.add(
        OpsSession(
            token_digest=token_digest(token, settings),
            expires_at=now + OPS_SESSION_LIFETIME,
        )
    )
    db.flush()
    return token


def _ops_row(db: Session, request: Request) -> OpsSession | None:
    token = request.cookies.get(OPS_COOKIE)
    if not token:
        return None
    settings: Settings = request.app.state.settings
    return db.scalars(
        select(OpsSession).where(
            OpsSession.token_digest == token_digest(token, settings),
            OpsSession.expires_at > utcnow(),
        )
    ).first()


def has_ops_session(db: Session, request: Request) -> bool:
    """Is this request an authenticated operator? **Never raises.**

    The door itself asks this to decide whether to render the Access card or to
    restore the tab the operator was on, so "no session" is a state, not an error.
    """
    return _ops_row(db, request) is not None


def end_ops_session(db: Session, request: Request) -> None:
    """로그아웃, immediately: the row is gone, so the cookie is worthless."""
    row = _ops_row(db, request)
    if row is not None:
        db.delete(row)
        db.flush()


def set_ops_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        OPS_COOKIE,
        token,
        max_age=int(OPS_SESSION_LIFETIME.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


def clear_ops_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        OPS_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


# ---------------------------------------------------------------------------
# FastAPI wiring
# ---------------------------------------------------------------------------
def require_operator(request: Request, db: DbSession) -> None:
    """The gate on every ops read. Expiry → 401, and the client returns to the door.

    A reader's ``mj_session`` cookie cannot satisfy this and an operator's
    ``mj_ops`` cookie cannot satisfy :data:`mijual.web.auth.ReadAccount`: the two
    cookies have different names and their digests live in different tables with
    no relation between them.
    """
    if not has_ops_session(db, request):
        raise ApiError(
            "ops_unauthenticated", "this surface needs an operator session", status_code=401
        )


#: What every ops read declares: ``def overview(db: DbSession, _: OpsGate) -> …``.
#:
#: There is deliberately **no write-side twin.** 로그아웃 is the only state-changing
#: route that could want one, and it is idempotent on purpose: logging out without a
#: session is the state, not an error, and the cookie is cleared either way — so a
#: reader whose session was already revoked ends up anonymous rather than holding a
#: cookie that will never resolve. Same reasoning as the reader's ``POST /auth/logout``.
OpsGate = Annotated[None, Depends(require_operator)]
