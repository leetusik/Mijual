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
**server-side only**. ``P13``'s 가입 인증 adds two codes and no third answer to
"who has an account": ``verification_code_invalid`` (the code was wrong, the
grant is still live) and ``verification_code_expired`` (there is no live grant at
all — expired, spent, never issued, or killed by the attempt cap). They are two
codes rather than one because the panel must point at 재전송 for the second and
must not for the first, and neither is reachable without the account's own
password, so neither discloses anything. 재전송 and /auth/verify answer
``invalid_credentials`` — the login code, byte for byte — to a wrong password and
an unknown address alike, and signup answers the identical 201 whether the
address was free or was held by an **unverified** account, so the gate discloses
no more about who exists than P5 did. No error here carries Korean: the single
body line a reader sees (불일치 / 중복 가입 / 8자 미만 / 인증번호) is the client's,
from the design's own copy.

**가입 is a hard gate, and the enforcement point is one function.**
:func:`start_session` **raises** on an account whose
:attr:`~mijual.db.models.Account.verification_pending_since` is not ``NULL``. It
is unreachable through any route here — every caller clears the column first, or
never reaches it — and that is the point: it is a structural backstop, so a route
added later cannot mint a session for a mailbox nobody has proven. ``NULL`` means
verified, which is also why every account that existed before P13 is verified
without a migration.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import re
import secrets
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import Depends, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mijual.config import Settings
from mijual.db.models import (
    Account,
    AuthSession,
    EmailVerification,
    PasswordReset,
    utcnow,
)
from mijual.mail import PASSWORD_RESET, SIGNUP_VERIFICATION, Mailer, Message
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
    "VERIFICATION_LIFETIME",
    "VERIFICATION_MAX_ATTEMPTS",
    "VERIFICATION_RESEND_COOLDOWN",
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
    "issue_verification",
    "live_verification",
    "new_code",
    "new_token",
    "normalize_email",
    "request_reset",
    "resend_verification",
    "revoke_sessions",
    "set_session_cookie",
    "start_session",
    "token_digest",
    "verification_payload",
    "verify_code",
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

#: How long a 가입 인증번호 lives. Ten minutes, not the reset link's hour: the
#: reader is sitting in front of the panel with the mail app one tap away, and a
#: 6-digit secret is short enough that its window is part of its strength.
VERIFICATION_LIFETIME = timedelta(minutes=10)
#: Wrong codes one grant tolerates before it stops being live. A 6-digit code has
#: 10^6 values, so five guesses is a 1-in-200,000 shot — and the sixth wrong entry
#: does not answer "wrong", it answers "expired", which is the honest state: that
#: code is dead and 재전송 is the way forward.
VERIFICATION_MAX_ATTEMPTS = 5
#: The floor between two mails to the same address. Without it, 재전송 (and
#: re-signup on an unverified address) is a mail-bomb aimed at any mailbox, sent
#: by this product, on somebody else's behalf. Measured from the most recent
#: grant's ``created_at``.
VERIFICATION_RESEND_COOLDOWN = timedelta(seconds=60)

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


def new_token() -> str:
    """A cookie/link value: 256 bits of ``secrets`` randomness, URL-safe.

    Public because ``P5.S9``'s operator session mints one the same way — one
    definition of "unguessable" for every credential this service hands out.
    """
    return secrets.token_urlsafe(_TOKEN_BYTES)


def new_code() -> str:
    """A 가입 인증번호: six digits, uniform over ``000000``–``999999``.

    ``secrets``, not ``random`` — this is a credential, however short. It is a
    **string** from here to the mail to the comparison, and it is formatted with
    leading zeros deliberately: an integer would turn ``012345`` into ``12345``
    somewhere between here and the panel, and the reader would type six
    characters that could never match.

    Its shortness is why :class:`~mijual.db.models.EmailVerification` carries an
    attempt counter and this module a resend cooldown: unguessable-per-try is not
    a property a six-digit number has on its own.
    """
    return f"{secrets.randbelow(1_000_000):06d}"


# ---------------------------------------------------------------------------
# accounts
# ---------------------------------------------------------------------------
def account_by_email(db: Session, email: str) -> Account | None:
    return db.scalars(select(Account).where(Account.email == email)).first()


def create_account(db: Session, *, email: str, password: str) -> Account:
    """계정 만들기 — and after ``P13``, an **unverified** account with no session.

    The row is created with :attr:`Account.verification_pending_since` set **in
    this function body**, never as a column default: a default would make the
    column unsafe for :func:`mijual.db.schema_sync.ensure_columns`, which is this
    repo's whole schema-evolution path, and would also have rewritten every
    existing row into "unverified" — the opposite of the grandfathering NULL
    gives for free.

    **An address held by an unverified account is re-taken, not refused.** Nobody
    has proven that mailbox, so the address is not really *held*; refusing it with
    ``email_taken`` would strand a reader who mistyped their password, closed the
    tab, and came back — with an address they own and cannot use. So this branch:

    * **replaces the password hash** with the one just typed. The reader may have
      chosen a different password this time, and the one they typed must be the
      one that works. It is safe precisely because the previous one was never
      proven either — no session ever existed on this account, and
      :func:`start_session` refuses to make one until the code lands.
    * leaves the code issuing to the caller (:func:`issue_verification` with
      ``force=True``), which supersedes the outstanding code under the cooldown.
    * answers with the **identical** 201 shape the free-address branch does, so
      signup still discloses nothing about who has an account.

    A **verified** address is ``email_taken``, unchanged: that mailbox has been
    proven, and letting a stranger overwrite its password hash would be an account
    takeover with an extra step.
    """
    address = _validated_email(email)
    secret = _validated_password(password)
    existing = account_by_email(db, address)
    if existing is not None:
        if existing.verification_pending_since is None:
            raise ApiError(
                "email_taken", "an account with this email exists", status_code=409
            )
        existing.password_hash = passwords.hash_password(secret)
        # A new signup restarts the clock on how long this address has been
        # pending; the column doubles as that age.
        existing.verification_pending_since = utcnow()
        db.flush()
        return existing

    account = Account(
        email=address,
        password_hash=passwords.hash_password(secret),
        verification_pending_since=utcnow(),
    )
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
    """Mint a session for ``account`` and return the raw token for the cookie.

    **Refuses an unverified account**, and does so by raising rather than by
    returning a code: no route can reach this state (login branches before it,
    :func:`verify_code` and :func:`confirm_reset` clear the column first), so
    reaching it is a *programming* error — a new route that forgot the gate — and
    the loudest possible failure is the correct one. This is the single
    enforcement point for ``P13``'s hard gate: nothing else has to remember it.
    """
    if account.verification_pending_since is not None:
        raise RuntimeError(
            "refusing to start a session for an unverified account "
            f"(id={account.id}) — the 가입 인증 gate was bypassed"
        )
    now = utcnow()
    # A login is a write already, so it is the cheapest honest place to drop this
    # account's dead rows. No background job, no growth without bound.
    db.execute(
        delete(AuthSession).where(
            AuthSession.account_id == account.id, AuthSession.expires_at <= now
        )
    )
    token = new_token()
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
    token = new_token()
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
    # A completed reset **is** proof of the mailbox — the token only ever arrived
    # in it — so it verifies an account that never finished 가입 인증 (``P13``).
    # Without this a reader who reset instead of verifying would be locked out by
    # a gate they had already satisfied, and :func:`start_session` two lines below
    # would refuse them.
    account.verification_pending_since = None
    grant.used_at = utcnow()
    # Whoever was logged in before the password changed no longer is: a reset is
    # what a reader does when they suspect someone else has the old one.
    revoke_sessions(db, account)
    db.flush()
    return account


# ---------------------------------------------------------------------------
# 가입 인증 — the 6-digit code grant (P13)
# ---------------------------------------------------------------------------
def live_verification(db: Session, account: Account) -> EmailVerification | None:
    """This account's usable code grant, or ``None``. **Looked up by account.**

    Never by digest: a 6-digit code has 10^6 values, so two accounts can hold the
    same digest under the same pepper, and a digest lookup would then verify the
    wrong reader. The code is only meaningful *with* the address — which is why
    :func:`verify_code` checks the password before it looks at the code at all.

    "Live" is one predicate with three ways to be false, and every caller uses
    this one: unspent (``used_at IS NULL``), unexpired, and under the attempt cap.
    A row at the cap is dead exactly like an expired one — that is what makes
    :data:`VERIFICATION_MAX_ATTEMPTS` a cap rather than a suggestion.
    """
    return db.scalars(
        select(EmailVerification)
        .where(
            EmailVerification.account_id == account.id,
            EmailVerification.used_at.is_(None),
            EmailVerification.expires_at > utcnow(),
            EmailVerification.attempts < VERIFICATION_MAX_ATTEMPTS,
        )
        .order_by(EmailVerification.created_at.desc())
    ).first()


def _stored_utc(moment: datetime | None) -> datetime | None:
    """A timestamp as an **aware** UTC value, whichever database it came back from.

    Postgres (the real target) returns ``DateTime(timezone=True)`` as aware;
    SQLite — the test engine — returns the same column naive, and subtracting one
    from :func:`~mijual.db.models.utcnow` is a ``TypeError`` rather than a wrong
    answer. A naive stored value is read as UTC, the same convention
    :func:`mijual.web.clock.to_kst` states for exactly this reason: naive
    datetimes here come from the database, never from a wall clock.
    """
    if moment is None or moment.tzinfo is not None:
        return moment
    return moment.replace(tzinfo=timezone.utc)


def _last_issued_at(db: Session, account: Account) -> datetime | None:
    """When this account was last mailed a code — live or not. The cooldown's clock."""
    return _stored_utc(
        db.scalars(
            select(EmailVerification.created_at)
            .where(EmailVerification.account_id == account.id)
            .order_by(EmailVerification.created_at.desc())
        ).first()
    )


def issue_verification(
    db: Session,
    account: Account,
    *,
    settings: Settings,
    mailer: Mailer,
    force: bool,
) -> tuple[bool, EmailVerification | None]:
    """Make sure a code is out there, and say whether this call mailed one.

    Returns ``(sent, grant)``: ``sent`` is whether a mail left the building, and
    ``grant`` is the code that is currently valid — the fresh one, the live one
    that was already out, or ``None`` when there is none and none may be issued
    yet. Both callers-of-record answer ``expires_at`` from ``grant``.

    ``force`` is the difference between the two ways a caller can want a code:

    * ``force=False`` — 로그인 on an unverified account: *ensure* one exists. A
      live code is left alone however old it is, so logging in seconds after 가입
      does not send a second mail, and a reader returning an hour later (the code
      long expired) gets a working one without having to find 재전송.
    * ``force=True`` — 가입 on an unverified address, and 재전송: *replace* the
      live one. Superseding is what keeps a mailbox from accumulating several
      working keys to one account.

    **The cooldown outranks ``force``.** Nothing here mails twice inside
    :data:`VERIFICATION_RESEND_COOLDOWN` of the last mail, because the sender of
    these mails is not necessarily their recipient: 재전송 and re-signup both take
    an address, and an unthrottled one aims this product at any mailbox. Under the
    cooldown the live code simply stands and ``sent`` is ``False`` — a state, not
    an error.

    The row holds a **digest**, and the code itself exists in exactly two places:
    the local variable below, and the mail. It is never returned, logged, or put
    in a response body — proving the mailbox is the entire point of the gate.
    """
    live = live_verification(db, account)
    if live is not None and not force:
        return False, live

    last_issued = _last_issued_at(db, account)
    if last_issued is not None and utcnow() - last_issued < VERIFICATION_RESEND_COOLDOWN:
        # Too soon. The live code (if any) stands; if the cap or a spend killed it,
        # `grant` is None and the caller answers a `verification` block with no
        # `expires_at` — absent, never a stand-in for a code that does not exist.
        return False, live

    # Last issue wins: two live codes in one mailbox is two keys to one account.
    db.execute(
        delete(EmailVerification).where(
            EmailVerification.account_id == account.id,
            EmailVerification.used_at.is_(None),
        )
    )
    code = new_code()
    expires_at = utcnow() + VERIFICATION_LIFETIME
    grant = EmailVerification(
        account_id=account.id,
        code_digest=token_digest(code, settings),
        expires_at=expires_at,
    )
    db.add(grant)
    db.flush()
    mailer.send(
        Message(
            to=account.email,
            kind=SIGNUP_VERIFICATION,
            data={"code": code, "expires_at": clock.iso(expires_at)},
        )
    )
    return True, grant


def verification_payload(
    email: str, grant: EmailVerification | None
) -> dict[str, Any]:
    """What a surface is told about a pending 인증: the address, and the deadline.

    ``expires_at`` is **absent when there is no live grant** rather than ``null``
    — the contract's rule for a fact that does not exist (`states-and-trust` §4),
    and the panel reads its absence as "there is no code to type right now"
    instead of rendering a countdown to nothing. The address is echoed back
    **normalized**, because it is the one the mail actually went to and the panel
    prints it in its intro line — it takes the address rather than the account so
    that 재전송, which has already authenticated, need not look the row up again.
    """
    payload: dict[str, Any] = {"email": email}
    if grant is not None:
        payload["expires_at"] = clock.iso(grant.expires_at)
    return payload


def verify_code(
    db: Session, *, email: str, password: str, code: str, settings: Settings
) -> Account:
    """인증. **Password first, then the code** — and the order is the security.

    Checking the password through :func:`authenticate` (so a miss burns a hash and
    answers ``invalid_credentials``, byte for byte as 로그인 does) means the one
    who verifies is the one who chose the password. That closes the pending-signup
    race: a second 가입 on an unverified address replaces the hash, so without this
    check a stranger could sit on somebody's half-finished signup and wait for the
    mailbox's owner to type the code they were mailed.

    **An already-verified account with the right password is a login.** A correct
    password proves everything the code was ever asked to prove, and inventing a
    failure here would strand a reader who pressed 확인 twice, or who verified in
    another tab.

    Two failure codes, and the difference matters to the panel: a wrong code
    against a live grant is ``verification_code_invalid`` (try again — the counter
    moved), and **no live grant at all** is ``verification_code_expired`` (재전송
    is the way forward). Expired, spent, never issued, and killed-by-this-very-
    attempt are one code, because they are one state: there is nothing to type.

    **Any wrong value costs an attempt, including one that is not six digits.** A
    value that cannot be the code is simply not the code; exempting malformed
    input would add a branch whose only observable effect is a cheaper guess, and
    the panel gates an empty field before it ever posts.
    """
    account = authenticate(db, email=email, password=password)
    if account.verification_pending_since is None:
        return account

    grant = live_verification(db, account)
    if grant is None:
        raise ApiError("verification_code_expired", "no live verification code")

    submitted = (code or "").strip()
    if not hmac.compare_digest(grant.code_digest, token_digest(submitted, settings)):
        grant.attempts += 1
        db.flush()
        if grant.attempts >= VERIFICATION_MAX_ATTEMPTS:
            # That increment just killed the grant, so the honest answer is the
            # state the reader is now in, not the one they were in a moment ago.
            raise ApiError("verification_code_expired", "no live verification code")
        raise ApiError("verification_code_invalid", "verification code is wrong")

    grant.used_at = utcnow()
    account.verification_pending_since = None  # NULL means verified
    db.flush()
    return account


def resend_verification(
    db: Session, *, email: str, password: str, settings: Settings, mailer: Mailer
) -> tuple[bool, EmailVerification | None]:
    """재전송. Password required, so it cannot be pointed at a stranger's mailbox.

    Returns ``(resent, grant)``. ``resent=False`` is a **state, not an error**:
    the cooldown has not elapsed and the code already in the mailbox is still the
    one to type. The panel has one honest line for that, and no timer.

    An already-verified account answers ``(False, None)`` rather than 400: it is
    the same reasoning as :func:`verify_code`'s already-verified branch, and the
    caller who somehow got here has nothing to wait for.
    """
    account = authenticate(db, email=email, password=password)
    if account.verification_pending_since is None:
        return False, None
    return issue_verification(
        db, account, settings=settings, mailer=mailer, force=True
    )


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
