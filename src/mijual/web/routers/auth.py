"""계정 만들기 · 가입 인증 · 로그인 · 로그아웃 · 세션 확인 · 재설정 · 계정 삭제.

The transport half of :mod:`mijual.web.auth`, which holds every decision. The
route map, so ``P5.S15``'s panel and ``P5.S10``'s client can hard-code it:

============================  =============================================
``POST /auth/signup``         email + password → **unverified account, a
                              mailed code, and no session** (201)
``POST /auth/verify``         email + password + code → session
``POST /auth/verify/resend``  a fresh code, under a cooldown
``POST /auth/login``          → session, **or** ``verification_required``.
                              One failure code, never a field
``POST /auth/logout``         immediate; the session row is deleted
``GET  /auth/me``             who am I — ``{authenticated: bool, account?}``
``POST /auth/reset/request``  always the same answer (가입 여부 비노출)
``POST /auth/reset/confirm``  token + new password → new session (and it
                              **verifies**: the mailbox is proven)
``PATCH /auth/account``       수신 주소 변경 (``P5.S8``) — the email *is* the account
``DELETE /auth/account``      the email is gone now, and the session with it
============================  =============================================

**``P13`` made 가입 a hard gate, and the shape of that is two response shapes
where there was one.** 계정 만들기 no longer logs anybody in — it answers
``{"verification": {"email", "expires_at"?}}`` and sets no cookie — and 로그인 on
an unverified account answers ``{"verification_required": true, "verification":
{…}}`` with no cookie either, rather than 401: the password was right, and telling
that reader "틀렸습니다" would be a lie. Both routes land the panel in the same
code-entry state, which is why both carry the identical ``verification`` block.
``expires_at`` is **absent** (never ``null``) when no live code exists.

**Every route here writes except ``/auth/me``**, so every route here except
``/auth/me`` takes :data:`~mijual.web.deps.WriteSession` — the first committing
dependency in this service — and every one of them carries the CSRF header
requirement :mod:`mijual.web.csrf` enforces service-wide.

**No Korean, anywhere in this module.** A failure travels as a structural
``code``; the one body line a reader sees (불일치 / 중복 가입 / 8자 미만) is the
signed client copy, and inventing a second Korean phrasing here would be a design
change. The success payloads carry the account's own facts and nothing composed.

**Nothing here gates an existing route.** Anonymous surfaces stay anonymous
(R5: 내 포트폴리오 is the only gated surface, and ``P5.S8`` builds it).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, Request, Response
from pydantic import BaseModel, Field

from mijual.config import Settings
from mijual.mail import Mailer
from mijual.web import auth
from mijual.web.deps import DbSession, WriteSession

router = APIRouter(tags=["auth"])


class Credentials(BaseModel):
    """Signup / login input. Length rules are checked in the service layer.

    ``min_length`` is deliberately **not** declared on ``password``: a pydantic
    violation is a 422 with English ``fields``, and "8자 미만" is a normal,
    expected product state that owns a Korean line — so it must arrive as
    ``password_too_short`` in the ordinary envelope, not as a validation error.
    """

    email: str = Field(max_length=320)
    password: str = Field(max_length=1024)


class EmailOnly(BaseModel):
    email: str = Field(max_length=320)


class VerifyCode(BaseModel):
    """가입 인증 input: the credentials **and** the code.

    The password travels with the code on purpose (see
    :func:`mijual.web.auth.verify_code`): it is what makes the reader who
    verifies the reader who signed up. The panel holds both fields in state
    across the transition into the code step, on both routes into it.

    ``max_length`` is generous rather than exactly six: a length mismatch is not
    a validation error with English ``fields``, it is simply a wrong code, and it
    is answered with the same structural code every other wrong code gets.
    """

    email: str = Field(max_length=320)
    password: str = Field(max_length=1024)
    code: str = Field(max_length=16)


class ResetConfirm(BaseModel):
    token: str = Field(max_length=256)
    password: str = Field(max_length=1024)


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _mailer(request: Request) -> Mailer:
    return request.app.state.mailer


@router.post("/auth/signup", status_code=201, summary="계정 만들기 (인증번호 발송)")
def signup(
    request: Request,
    db: WriteSession,
    body: Annotated[Credentials, Body()],
) -> dict[str, Any]:
    """Creates an **unverified** account, mails a code, and opens **no session**.

    There is no ``Response`` parameter any more, which is the point: this route
    cannot set a cookie because it has nothing to set one from. The account
    exists, and it cannot be used until the code lands.

    A free address and an address held by an unverified account produce the
    **identical** body — see :func:`mijual.web.auth.create_account` — so 가입
    still discloses nothing about who has an account. A **verified** address is
    ``409 email_taken``, exactly as in P5.
    """
    settings = _settings(request)
    account = auth.create_account(db, email=body.email, password=body.password)
    _sent, grant = auth.issue_verification(
        db, account, settings=settings, mailer=_mailer(request), force=True
    )
    return {"verification": auth.verification_payload(account.email, grant)}


@router.post("/auth/verify", summary="가입 인증 (6자리 인증번호)")
def verify(
    request: Request,
    response: Response,
    db: WriteSession,
    body: Annotated[VerifyCode, Body()],
) -> dict[str, Any]:
    """The code that was mailed → a verified account and a session.

    Two failure codes, and the panel needs both: ``verification_code_invalid``
    (wrong code, the one in the mailbox still works) and
    ``verification_code_expired`` (there is nothing live to type — 재전송). A wrong
    password is ``invalid_credentials``, the same answer 로그인 gives.
    """
    settings = _settings(request)
    account = auth.verify_code(
        db,
        email=body.email,
        password=body.password,
        code=body.code,
        settings=settings,
    )
    token = auth.start_session(db, account, settings)
    auth.set_session_cookie(response, token, settings)
    return {"account": auth.account_payload(account)}


@router.post("/auth/verify/resend", summary="인증번호 재전송 (쿨다운)")
def verify_resend(
    request: Request, db: WriteSession, body: Annotated[Credentials, Body()]
) -> dict[str, Any]:
    """재전송. ``{"resent": bool, "verification": {…}}`` — and ``false`` is not an error.

    ``resent: false`` means the cooldown has not elapsed and the code already in
    the mailbox is still the one to type. It is a state the panel has an honest
    line for, so it is a 200 with a boolean rather than a 429 with a timer.
    """
    resent, grant = auth.resend_verification(
        db,
        email=body.email,
        password=body.password,
        settings=_settings(request),
        mailer=_mailer(request),
    )
    # The address is the normalized one: `resend_verification` authenticated it,
    # so this is the account's own spelling and the one the mail went to.
    payload = auth.verification_payload(auth.normalize_email(body.email), grant)
    return {"resent": resent, "verification": payload}


@router.post("/auth/login", summary="로그인")
def login(
    request: Request,
    response: Response,
    db: WriteSession,
    body: Annotated[Credentials, Body()],
) -> dict[str, Any]:
    settings = _settings(request)
    account = auth.authenticate(db, email=body.email, password=body.password)
    if account.verification_pending_since is not None:
        # The password was right, so this is not a failure — it is the code step.
        # A fresh code goes out only when none is live (and never inside the
        # cooldown), so a reader who logs in seconds after 가입 gets no second
        # mail and one who comes back tomorrow gets a working code without
        # having to find 재전송.
        _sent, grant = auth.issue_verification(
            db, account, settings=settings, mailer=_mailer(request), force=False
        )
        return {
            "verification_required": True,
            "verification": auth.verification_payload(account.email, grant),
        }
    token = auth.start_session(db, account, settings)
    auth.set_session_cookie(response, token, settings)
    return {"account": auth.account_payload(account)}


@router.post("/auth/logout", summary="로그아웃 (즉시)")
def logout(request: Request, response: Response, db: WriteSession) -> dict[str, Any]:
    """Idempotent: logging out without a session is not an error, it is the state.

    The cookie is cleared either way, so a reader whose session was already
    revoked (a reset elsewhere, an expiry) still ends up in the anonymous state
    the design draws rather than holding a cookie that will never resolve.
    """
    auth.end_session(db, request)
    auth.clear_session_cookie(response, _settings(request))
    return {"authenticated": False}


@router.get("/auth/me", summary="세션 확인 — who am I")
def me(request: Request, db: DbSession) -> dict[str, Any]:
    """Anonymous is a **result, not a 401**.

    Every surface but 내 포트폴리오 is anonymous, so the chrome asks this on every
    page load and gets an honest answer either way. Reporting 401 for "not logged
    in" would make the normal state of the product an error in the console — and
    the same shape ``P5.S4`` already uses for a search that found nothing.
    """
    account = auth.current_account(db, request)
    if account is None:
        return {"authenticated": False}
    return {"authenticated": True, "account": auth.account_payload(account)}


@router.post("/auth/reset/request", summary="비밀번호 재설정 요청 (가입 여부 비노출)")
def reset_request(
    request: Request, db: WriteSession, body: Annotated[EmailOnly, Body()]
) -> dict[str, Any]:
    """One answer for both branches — see :func:`mijual.web.auth.request_reset`."""
    auth.request_reset(
        db, email=body.email, settings=_settings(request), mailer=_mailer(request)
    )
    return {"requested": True}


@router.post("/auth/reset/confirm", summary="비밀번호 재설정 확인")
def reset_confirm(
    request: Request,
    response: Response,
    db: WriteSession,
    body: Annotated[ResetConfirm, Body()],
) -> dict[str, Any]:
    """Spends the single-use grant and logs the reader in on the new password.

    They just proved control of the mailbox and chose the password, so sending
    them back to the login panel to type it again would be ceremony. Every
    session that existed before this call is already gone.

    ``P13``: the same reasoning **verifies** an account that never finished 가입
    인증 — the token only ever arrived in that mailbox, so the gate has been
    satisfied by another route. The shape of this response is unchanged.
    """
    settings = _settings(request)
    account = auth.confirm_reset(
        db, token=body.token, password=body.password, settings=settings
    )
    token = auth.start_session(db, account, settings)
    auth.set_session_cookie(response, token, settings)
    return {"account": auth.account_payload(account)}


@router.patch("/auth/account", summary="수신 주소(계정 이메일) 변경")
def change_email(
    db: WriteSession, account: auth.WriteAccount, body: Annotated[EmailOnly, Body()]
) -> dict[str, Any]:
    """R5's 알림 설정 "수신 주소 · 변경" — the address *is* the account.

    ``P5.S8`` added this beside 계정 삭제 rather than under ``/portfolio`` because
    it edits the account resource, not a portfolio row. See
    :func:`mijual.web.auth.change_email` for what it revokes and what it does not.
    """
    auth.change_email(db, account, email=body.email)
    return {"account": auth.account_payload(account)}


@router.delete("/auth/account", summary="계정 삭제 (이메일 즉시 삭제)")
def delete_account(
    request: Request, response: Response, db: WriteSession, account: auth.WriteAccount
) -> dict[str, Any]:
    """R5's 계정 삭제: no confirmation dialog here — the surface owns that."""
    auth.delete_account(db, account)
    auth.clear_session_cookie(response, _settings(request))
    return {"deleted": True, "authenticated": False}
