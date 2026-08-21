"""Reader auth — accounts, sessions, and the reset grant.

This is the service layer behind :mod:`mijual.web.routers.auth`: it holds the
decisions, the router holds the transport. `security` (v0002, R5-signed) fixes
what the product promises; the apply-phase decisions it left open are made here
and each one is written down where it is made.

**Identity is an email and a password, and the stored form is normalized.**
:func:`normalize_email` NFKC-normalizes, strips and case-folds the whole address
— local part included. Case-folding only the domain is the technically pure
reading of RFC 5321, and it is the wrong product: no consumer mail provider
treats ``A@x.kr`` and ``a@x.kr`` as two people, so honouring the distinction
would only mint accidental duplicate accounts and make 중복 가입 depend on the
shift key. Plus-tags are **not** stripped: ``a+alerts@x.kr`` is a deliverable
address a reader may deliberately want for D-day mail.

**A session is a row, not a signed cookie** (:class:`~mijual.db.models.AuthSession`
records why). The cookie carries a 256-bit random token; the row stores only a
digest of it, keyed with ``MIJUAL_SESSION_SECRET`` when one is configured. The
cookie decisions, all of them apply-phase decisions `security` names:

======================  ==========================================================
name                    ``mj_session`` — the ops door (``P5.S9``) gets its own,
                        differently named cookie (``mj_ops``), never this one.
flags                   ``HttpOnly`` (no script reads it, so an XSS cannot post
                        it anywhere), ``SameSite=Lax`` (never attached to a
                        cross-site POST; still attached to a top-level link, so
                        arriving from a mail link keeps you logged in),
                        ``Path=/``, and ``Secure`` from ``MIJUAL_COOKIE_SECURE``
                        — configurable because local development is plain http
                        and a ``Secure`` cookie there silently never arrives.
lifetime                30 days, **absolute**, never extended on a read. A
                        sliding window would have to write on a ``GET``, and this
                        service is built so a ``GET`` structurally cannot
                        (:func:`mijual.web.deps.get_write_session`). Extending on
                        the next login is a write on a write, and that already
                        happens.
CSRF                    ``SameSite=Lax`` **and** a required custom header on
                        every unsafe method — see :mod:`mijual.web.csrf`.
======================  ==========================================================

**Immediacy is the reason for every mechanism above.** 로그아웃 is immediate
(delete the row), 계정 삭제 wipes the email *now* and kills access with it (delete
the account; the ORM cascade takes the sessions and the reset grants, and the FK
``ondelete="CASCADE"`` takes whatever ``P5.S8`` hangs off the account).

**What a failure is allowed to say.** A login failure is one code —
``invalid_credentials`` — for a wrong password and for an address that has no
account alike, and the miss path burns a scrypt verification against a dummy hash
so the two do not differ in timing either. A reset request answers identically
whether or not the address exists (가입 여부 비노출) and prints its link
**server-side only**. No error here carries Korean: the single body line a reader
sees (불일치 / 중복 가입 / 8자 미만) is the client's, from the design's own copy.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import re
import secrets
import unicodedata
from datetime import timedelta
from typing import Annotated, Any

from fastapi import Depends, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mijual.config import Settings
from mijual.db.models import Account, AuthSession, PasswordReset, utcnow
from mijual.mail import PASSWORD_RESET, Mailer, Message
from mijual.web import clock, passwords
from mijual.web.deps import DbSession, WriteSession
from mijual.web.errors import ApiError

__all__ = [
    "OPS_COOKIE",
    "RESET_LIFETIME",
    "RESET_PATH",
    "ReadAccount",
    "SESSION_COOKIE",
    "SESSION_LIFETIME",
    "WriteAccount",
    "account_payload",
    "authenticate",
    "change_email",
    "clear_session_cookie",
    "confirm_reset",
    "create_account",
    "current_account",
    "delete_account",
    "end_session",
    "normalize_email",
    "request_reset",
    "revoke_sessions",
    "set_session_cookie",
    "start_session",
    "token_digest",
]

log = logging.getLogger(__name__)

#: The reader session cookie.
SESSION_COOKIE = "mj_session"
#: Reserved for ``P5.S9``'s operator door, stated here so the two can never
#: collide: `security` requires the ops cookie to be **differently named** and
#: the two credentials to have no relation at all.
OPS_COOKIE = "mj_ops"

SESSION_LIFETIME = timedelta(days=30)
#: A reset link is a key to an account that arrived in a mailbox. One hour is
#: long enough for a reader who checks mail on a phone and short enough that a
#: forwarded or archived message stops being a key by lunchtime.
RESET_LIFETIME = timedelta(hours=1)
#: The frontend route the reset link points at (``P5.S15`` builds the page). The
#: origin comes from ``MIJUAL_APP_BASE_URL``; only the path is fixed here.
RESET_PATH = "/auth/reset"

#: 256 bits of ``secrets`` randomness, URL-safe. Unguessable is the whole
#: security of both a session cookie and a reset link.
_TOKEN_BYTES = 32

#: Deliberately permissive: an address is *delivered to*, not parsed for
#: correctness, and every stricter regex on the internet rejects a valid address
#: somebody actually owns. This rejects only what cannot be an address at all —
#: no ``@``, whitespace, or no dot in the domain.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_EMAIL_MAX = 254  # RFC 5321's path limit, and the column width.

_dummy_hash: str | None = None
_warned_unkeyed = False


# ---------------------------------------------------------------------------
# email + password
# ---------------------------------------------------------------------------
def normalize_email(raw: str) -> str:
    """The one stored spelling of an address. See the module docstring."""
    return unicodedata.normalize("NFKC", raw or "").strip().casefold()


def _validated_email(raw: str) -> str:
    email = normalize_email(raw)
    if len(email) > _EMAIL_MAX or not _EMAIL_RE.match(email):
        raise ApiError("invalid_email", "email is not a deliverable address")
    return email


def _validated_password(raw: str) -> str:
    """≥ 8 characters, and no other rule (R5). The copy is the client's."""
    if len(raw or "") < passwords.MIN_LENGTH:
        raise ApiError(
            "password_too_short",
            f"password must be at least {passwords.MIN_LENGTH} characters",
        )
    return raw


def _invalid_credentials() -> ApiError:
    """One answer for a wrong password and for an address with no account.

    R5: "로그인 오류는 필드 특정 없음". A code that named the field would tell an
    attacker which addresses have accounts, and would tell a reader nothing the
    single body line does not already say.
    """
    return ApiError(
        "invalid_credentials", "email or password is wrong", status_code=401
    )


def _burn_a_hash(password: str) -> None:
    """Spend a scrypt verification on nothing, so a miss costs what a hit costs."""
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = passwords.hash_password("not-a-real-password")
    passwords.verify(password, _dummy_hash)


# ---------------------------------------------------------------------------
# tokens
# ---------------------------------------------------------------------------
def session_pepper(settings: Settings) -> bytes:
    """The key the stored token digests are computed under, or ``b""`` in dev.

    Unset is a development state and says so **once** in the log rather than on
    every request. It is not an exception: ``P4`` sets the secret, and
    :meth:`mijual.config.Settings.require_session_secret` exists for a deployment
    that wants to fail rather than start without one.
    """
    global _warned_unkeyed
    secret = settings.session_secret
    if not secret:
        if not _warned_unkeyed:
            _warned_unkeyed = True
            log.warning(
                "MIJUAL_SESSION_SECRET is unset — reader session tokens are "
                "digested unkeyed. Development only; set it before deploying."
            )
        return b""
    return secret.encode("utf-8")


def token_digest(token: str, settings: Settings) -> str:
    """What the database stores for a cookie/link value it must never hold.

    Keyed with the session secret when there is one, so a stolen database dump
    contains nothing that can be replayed — the attacker would also need the key,
    which lives in the environment. Rotating the key invalidates every session and
    every outstanding reset link, which is exactly the lever you want in the hour
    you discover a dump.
    """
    pepper = session_pepper(settings)
    raw = token.encode("utf-8")
    if pepper:
        return hmac.new(pepper, raw, hashlib.sha256).hexdigest()
    return hashlib.sha256(raw).hexdigest()


def _new_token() -> str:
    return secrets.token_urlsafe(_TOKEN_BYTES)


# ---------------------------------------------------------------------------
# accounts
# ---------------------------------------------------------------------------
def account_by_email(db: Session, email: str) -> Account | None:
    return db.scalars(select(Account).where(Account.email == email)).first()


def create_account(db: Session, *, email: str, password: str) -> Account:
    """계정 만들기. Duplicate email → ``email_taken``, structurally, not by copy."""
    address = _validated_email(email)
    secret = _validated_password(password)
    if account_by_email(db, address) is not None:
        raise ApiError("email_taken", "an account with this email exists", status_code=409)

    account = Account(email=address, password_hash=passwords.hash_password(secret))
    db.add(account)
    try:
        db.flush()
    except IntegrityError as exc:  # two signups for one address, same instant
        db.rollback()
        raise ApiError(
            "email_taken", "an account with this email exists", status_code=409
        ) from exc
    return account


def authenticate(db: Session, *, email: str, password: str) -> Account:
    """로그인. One failure code, one failure cost — see :func:`_invalid_credentials`."""
    account = account_by_email(db, normalize_email(email))
    if account is None:
        _burn_a_hash(password or "")
        raise _invalid_credentials()
    if not passwords.verify(password or "", account.password_hash):
        raise _invalid_credentials()
    if passwords.needs_rehash(account.password_hash):
        # The one moment the plaintext is legitimately in hand and the request is
        # already a write. See ``mijual.web.passwords`` for the upgrade path.
        account.password_hash = passwords.hash_password(password)
    return account


def change_email(db: Session, account: Account, *, email: str) -> Account:
    """수신 주소 변경 (R5's 알림 설정 row) — which **is** the account's address.

    `security` fixes stored PII to email + password hash, so the D-day mail has no
    second address to go to: 변경 edits this account. The decisions, recorded here
    because the surface asks a smaller question than the endpoint answers:

    * **The session is the authority; no password is re-entered.** R5's signed
      Notify row is a 수신 주소 with a 변경 affordance and nothing else, and
      ``P5.S7`` already established the precedent by the same reasoning: 계정 삭제
      — the strictly more destructive action, with the same signed shape — takes
      no password either. Adding a password field would be inventing a control
      the round does not have, and inventing UI is a design change.
    * **A duplicate address is refused, not merged** — same code as 가입
      (``email_taken``), because two accounts cannot share a login identity.
    * **Outstanding reset links are revoked.** A grant was issued *to an address*
      that is no longer this account's; leaving it live would keep a working key
      to the account sitting in a mailbox the reader has just moved away from.
      Sessions are **not** revoked: the reader is the one doing this.
    """
    address = _validated_email(email)
    if address == account.email:
        return account
    if account_by_email(db, address) is not None:
        raise ApiError("email_taken", "an account with this email exists", status_code=409)
    account.email = address
    db.execute(
        delete(PasswordReset).where(
            PasswordReset.account_id == account.id, PasswordReset.used_at.is_(None)
        )
    )
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(
            "email_taken", "an account with this email exists", status_code=409
        ) from exc
    return account


def delete_account(db: Session, account: Account) -> None:
    """계정 삭제: the email is gone now, and so is every session it held.

    The ORM cascade removes the sessions and reset grants in this transaction —
    SQLite does not enforce foreign keys by default, so relying on
    ``ondelete="CASCADE"`` alone would make the guarantee environment-dependent.
    """
    db.delete(account)
    db.flush()


# ---------------------------------------------------------------------------
# sessions
# ---------------------------------------------------------------------------
def start_session(db: Session, account: Account, settings: Settings) -> str:
    """Mint a session for ``account`` and return the raw token for the cookie."""
    now = utcnow()
    # A login is a write already, so it is the cheapest honest place to drop this
    # account's dead rows. No background job, no growth without bound.
    db.execute(
        delete(AuthSession).where(
            AuthSession.account_id == account.id, AuthSession.expires_at <= now
        )
    )
    token = _new_token()
    db.add(
        AuthSession(
            account_id=account.id,
            token_digest=token_digest(token, settings),
            expires_at=now + SESSION_LIFETIME,
        )
    )
    db.flush()
    return token


def _session_row(db: Session, request: Request) -> AuthSession | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    settings: Settings = request.app.state.settings
    return db.scalars(
        select(AuthSession).where(
            AuthSession.token_digest == token_digest(token, settings),
            AuthSession.expires_at > utcnow(),
        )
    ).first()


def current_account(db: Session, request: Request) -> Account | None:
    """Who this request is, or ``None``. **Never raises** — anonymity is normal.

    Every surface but 내 포트폴리오 is anonymous, so "no session" is a state the
    product renders (the 로그인 link), not a failure it reports.
    """
    row = _session_row(db, request)
    return row.account if row is not None else None


def end_session(db: Session, request: Request) -> None:
    """로그아웃, immediately: the row is gone, so the cookie is worthless."""
    row = _session_row(db, request)
    if row is not None:
        db.delete(row)
        db.flush()


def revoke_sessions(db: Session, account: Account) -> None:
    """Kill every session this account holds (a password reset does this)."""
    db.execute(delete(AuthSession).where(AuthSession.account_id == account.id))


def set_session_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(SESSION_LIFETIME.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


def clear_session_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


# ---------------------------------------------------------------------------
# password reset — 가입 여부 비노출
# ---------------------------------------------------------------------------
def request_reset(
    db: Session, *, email: str, settings: Settings, mailer: Mailer
) -> None:
    """Issue a reset link **if** the address has an account. Tell the caller nothing.

    Both branches return ``None``; the router's response does not depend on which
    one ran. The link travels only through the mailer — in P5 that is
    :class:`mijual.mail.ConsoleMailer`, which prints it to the server's log.
    """
    account = account_by_email(db, normalize_email(email))
    if account is None:
        return

    now = utcnow()
    # Last request wins: a reader who clicks 재설정 twice because the first mail
    # was slow must not leave two live keys to their account lying in a mailbox.
    db.execute(
        delete(PasswordReset).where(
            PasswordReset.account_id == account.id, PasswordReset.used_at.is_(None)
        )
    )
    token = _new_token()
    expires_at = now + RESET_LIFETIME
    db.add(
        PasswordReset(
            account_id=account.id,
            token_digest=token_digest(token, settings),
            expires_at=expires_at,
        )
    )
    db.flush()
    mailer.send(
        Message(
            to=account.email,
            kind=PASSWORD_RESET,
            data={
                "url": f"{settings.app_base_url}{RESET_PATH}?token={token}",
                "expires_at": clock.iso(expires_at),
            },
        )
    )


def confirm_reset(
    db: Session, *, token: str, password: str, settings: Settings
) -> Account:
    """Spend the grant, set the new password, and kill every existing session."""
    secret = _validated_password(password)
    grant = db.scalars(
        select(PasswordReset).where(
            PasswordReset.token_digest == token_digest(token or "", settings),
            PasswordReset.used_at.is_(None),
            PasswordReset.expires_at > utcnow(),
        )
    ).first()
    if grant is None:
        # Expired, already spent, or never existed — one code for all three. A
        # reset link is a credential, and a credential's failure is uniform.
        raise ApiError("invalid_reset_token", "reset link is not valid")

    account = grant.account
    account.password_hash = passwords.hash_password(secret)
    grant.used_at = utcnow()
    # Whoever was logged in before the password changed no longer is: a reset is
    # what a reader does when they suspect someone else has the old one.
    revoke_sessions(db, account)
    db.flush()
    return account


# ---------------------------------------------------------------------------
# FastAPI wiring
# ---------------------------------------------------------------------------
def account_payload(account: Account) -> dict[str, Any]:
    """What a surface is told about the reader. The email, and when they joined.

    The chrome renders the abbreviated form (앞 4자 + … + 도메인 끝), so it needs
    the whole address; abbreviating server-side would put a second spelling of
    the identity in the payload for no gain.
    """
    return {"email": account.email, "created_at": clock.iso(account.created_at)}


def read_account(request: Request, db: DbSession) -> Account:
    """The gate for a **read** of an owner-only surface (``P5.S8``'s holdings)."""
    account = current_account(db, request)
    if account is None:
        raise ApiError("unauthenticated", "this surface needs a session", status_code=401)
    return account


def write_account(request: Request, db: WriteSession) -> Account:
    """The same gate on a state-changing route, sharing the request's write session."""
    account = current_account(db, request)
    if account is None:
        raise ApiError("unauthenticated", "this surface needs a session", status_code=401)
    return account


#: 내 포트폴리오 is the only gated surface (R5). ``P5.S8``/``P5.S16`` build it;
#: nothing this slice adds gates an existing route.
ReadAccount = Annotated[Account, Depends(read_account)]
WriteAccount = Annotated[Account, Depends(write_account)]
