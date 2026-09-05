"""Reader auth (P5.S7): what a session is, and what a failure is allowed to say.

DB-free, the established pattern — in-memory SQLite, dependency overrides, no
docker and no network. The cases are the prohibitions R5 states: a login error
never distinguishes the two ways to be wrong, a reset request never reveals
whether the address has an account, deletion takes the email and the session with
it, and a GET still cannot write.

``P13`` added the 가입 인증 gate, and with it the four cases that are core auth
behaviour rather than surface: 가입 opens **no** session and the mailed code does,
로그인 with the right password on an unverified account opens no session either,
:data:`~mijual.web.auth.VERIFICATION_MAX_ATTEMPTS` wrong codes kill the grant, and
a completed password reset verifies the account (the token only ever arrived in
that mailbox). The panel itself is verified live in a browser, not here.

:func:`signup_and_verify` is this file's export: the P5-era "signup logs you in"
shortcut, restored under the gate, so ``test_web_portfolio`` and ``test_web_ops``
have one helper to change rather than an assertion re-pointed per call site.
"""

from __future__ import annotations

import io
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.config import Settings
from mijual.db.models import Account, AuthSession, Base, Corp, EmailVerification
from mijual.mail import ConsoleMailer
from mijual.web.app import create_app
from mijual.web.auth import SESSION_COOKIE, VERIFICATION_MAX_ATTEMPTS
from mijual.web.csrf import CSRF_HEADER
from mijual.web.deps import get_session, get_write_session

EMAIL, PASSWORD = "Reader@Mijual.KR", "portfolio-8"


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    outbox = io.StringIO()

    # A configured session secret is the deployed shape: the stored digest is
    # keyed with it, so a database dump holds nothing replayable as a cookie.
    app = create_app(
        Settings(session_secret="test-session-secret"), mailer=ConsoleMailer(stream=outbox)
    )
    app.dependency_overrides[get_session] = lambda: session

    def _write():
        # Mirrors :func:`get_write_session`: commit on a normal return, **roll
        # back on any exception** — including an ``ApiError`` a handler raises
        # deliberately. A fixture that only ever committed was more forgiving
        # than the runtime, and it hid ``P13.F1``'s bug (the wrong-code attempt
        # counter died with the 400 it caused) behind a passing test. No
        # ``close()``: one long-lived session serves the whole test.
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    app.dependency_overrides[get_write_session] = _write
    with TestClient(app, headers={CSRF_HEADER: "1"}) as test_client:
        test_client.outbox = outbox  # type: ignore[attr-defined]
        test_client.db = session  # type: ignore[attr-defined]
        yield test_client
    session.close()


def _signup(client, email=EMAIL, password=PASSWORD):
    return client.post("/auth/signup", json={"email": email, "password": password})


def last_code(client) -> str:
    """The 인증번호 the :class:`ConsoleMailer` most recently printed.

    Server-side only, and that is the point of reading it from here: the code
    never travels in an HTTP response, so a test that could get it from one would
    be proving the gate is broken. The fixtures of the other two web suites
    install the same stream for the same reason.
    """
    printed = [
        line
        for line in client.outbox.getvalue().splitlines()
        if "[mail:signup_verification]" in line
    ]
    assert printed, "no 가입 인증 mail was printed"
    return printed[-1].split("code=")[1].split()[0]


def signup_and_verify(client, email=EMAIL, password=PASSWORD):
    """가입 + 인증, i.e. what a bare ``POST /auth/signup`` did before ``P13``.

    Imported by ``test_web_portfolio`` and ``test_web_ops``, whose subject is not
    the gate: they need a logged-in reader in one line, and this is the one line.
    """
    created = client.post("/auth/signup", json={"email": email, "password": password})
    assert created.status_code == 201, created.text
    verified = client.post(
        "/auth/verify",
        json={"email": email, "password": password, "code": last_code(client)},
    )
    assert verified.status_code == 200, verified.text
    return verified


def test_signup_login_me_logout_is_one_session_and_a_normalized_email(client) -> None:
    created = _signup(client)
    assert created.status_code == 201
    # P13: 가입 opens no session at all — the mailbox has not been proven yet.
    assert SESSION_COOKIE not in created.cookies
    assert "account" not in created.json()
    # The address is stored in one spelling, case-folded — 중복 가입 does not
    # depend on the shift key — and the pending block echoes that one spelling.
    assert created.json()["verification"]["email"] == "reader@mijual.kr"
    assert client.get("/auth/me").json() == {"authenticated": False}

    verified = signup_and_verify(client)
    assert verified.json()["account"]["email"] == "reader@mijual.kr"
    cookie = verified.cookies[SESSION_COOKIE]
    assert client.get("/auth/me").json()["account"]["email"] == "reader@mijual.kr"

    # The cookie value itself is never what the database holds.
    stored = client.db.scalars(select(AuthSession)).all()
    assert len(stored) == 1 and stored[0].token_digest != cookie

    assert client.post("/auth/logout").json() == {"authenticated": False}
    assert client.get("/auth/me").json() == {"authenticated": False}
    assert client.db.scalars(select(AuthSession)).all() == []  # immediate

    # A stale cookie resolves to nobody rather than to its old owner.
    client.cookies.set(SESSION_COOKIE, cookie)
    assert client.get("/auth/me").json() == {"authenticated": False}
    client.cookies.clear()

    again = client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert again.status_code == 200 and "account" in again.json()  # verified: a session


def test_a_login_failure_never_says_which_field_and_a_duplicate_is_structural(
    client,
) -> None:
    signup_and_verify(client)
    client.cookies.clear()

    wrong_password = client.post(
        "/auth/login", json={"email": EMAIL, "password": "wrong-password"}
    )
    unknown_email = client.post(
        "/auth/login", json={"email": "nobody@mijual.kr", "password": PASSWORD}
    )
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()  # byte-identical
    assert wrong_password.json()["error"]["code"] == "invalid_credentials"
    assert "message_ko" not in wrong_password.json()["error"]  # no invented Korean

    # A **verified** address is taken, structurally, in any spelling.
    duplicate = _signup(client, email="READER@mijual.kr")
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "email_taken"

    # An **unverified** one is not: nobody proved that mailbox, so 가입 re-takes
    # the address with the password just typed and answers the identical 201 the
    # free-address branch does — 가입 여부 비노출 survives the gate.
    pending = _signup(client, email="pending@mijual.kr", password="first-pass-8")
    retaken = _signup(client, email="pending@mijual.kr", password="second-pass-8")
    assert retaken.status_code == 201
    assert retaken.json().keys() == pending.json().keys() == {"verification"}
    assert _signup(client, email="new@mijual.kr", password="short").json()["error"][
        "code"
    ] == "password_too_short"


def test_the_gate_is_hard_at_signup_and_at_login_and_the_code_is_what_opens_it(
    client,
) -> None:
    """P13's whole point, in one path: no session until the mailbox is proven.

    The code is read from the outbox rather than from a response **because it is
    never in a response** — the assertions below say so directly, since a code
    that leaked into the body would make the gate a formality.
    """
    created = _signup(client)
    assert created.status_code == 201 and SESSION_COOKIE not in created.cookies
    code = last_code(client)
    assert len(code) == 6 and code.isdigit()
    assert code not in created.text  # server-side only, always
    assert client.get("/auth/me").json() == {"authenticated": False}

    # The right password on an unverified account is not a failure and not a
    # session: it is the same code step 가입 lands in.
    routed = client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert routed.status_code == 200 and SESSION_COOKIE not in client.cookies
    assert routed.json()["verification_required"] is True
    assert routed.json()["verification"]["email"] == "reader@mijual.kr"
    assert code not in routed.text
    assert client.get("/auth/me").json() == {"authenticated": False}
    assert last_code(client) == code  # a live code is not re-mailed

    # 재전송 inside the cooldown is a state, not an error, and mails nothing.
    resend = client.post("/auth/verify/resend", json={"email": EMAIL, "password": PASSWORD})
    assert resend.status_code == 200 and resend.json()["resent"] is False
    assert last_code(client) == code

    # …and the code does what the correct password could not.
    verified = client.post(
        "/auth/verify", json={"email": EMAIL, "password": PASSWORD, "code": code}
    )
    assert verified.status_code == 200 and SESSION_COOKIE in verified.cookies
    assert client.get("/auth/me").json()["account"]["email"] == "reader@mijual.kr"
    account = client.db.scalars(select(Account)).one()
    assert account.verification_pending_since is None  # NULL means verified
    assert client.db.scalars(select(EmailVerification)).one().used_at is not None


def test_five_wrong_codes_kill_the_grant_and_the_mailed_code_stops_working(
    client,
) -> None:
    _signup(client)
    code = last_code(client)
    wrong = "000000" if code != "000000" else "111111"

    def submit(value):
        return client.post(
            "/auth/verify", json={"email": EMAIL, "password": PASSWORD, "code": value}
        )

    for _ in range(VERIFICATION_MAX_ATTEMPTS - 1):
        miss = submit(wrong)
        assert miss.status_code == 400
        assert miss.json()["error"]["code"] == "verification_code_invalid"

    # The attempt that reaches the cap answers with the state it just created:
    # there is nothing live to type, so the panel must point at 재전송.
    killed = submit(wrong)
    assert killed.json()["error"]["code"] == "verification_code_expired"
    # …and the code that really was mailed is dead with it.
    assert submit(code).json()["error"]["code"] == "verification_code_expired"
    assert SESSION_COOKIE not in client.cookies
    assert client.db.scalars(select(Account)).one().verification_pending_since is not None

    # A wrong password on this route is the login's answer, never the code's.
    wrong_password = client.post(
        "/auth/verify", json={"email": EMAIL, "password": "not-it-8", "code": code}
    )
    assert wrong_password.status_code == 401
    assert wrong_password.json()["error"]["code"] == "invalid_credentials"


def test_resend_past_the_cooldown_supersedes_the_code_in_the_mailbox(client) -> None:
    """재전송 replaces the live code rather than adding a second key to one account.

    The cooldown is back-dated rather than waited out — the clock is not the
    subject here, and a test that sleeps a minute is a test nobody runs.
    """
    _signup(client)
    first = last_code(client)
    grant = client.db.scalars(select(EmailVerification)).one()
    grant.created_at = grant.created_at - timedelta(minutes=5)
    client.db.flush()

    resend = client.post("/auth/verify/resend", json={"email": EMAIL, "password": PASSWORD})
    assert resend.status_code == 200 and resend.json()["resent"] is True
    second = last_code(client)
    assert second != first
    assert second not in resend.text  # still server-side only
    # One grant, not two: the superseded row is gone, and the old code is dead.
    assert len(client.db.scalars(select(EmailVerification)).all()) == 1
    stale = client.post(
        "/auth/verify", json={"email": EMAIL, "password": PASSWORD, "code": first}
    )
    assert stale.json()["error"]["code"] == "verification_code_invalid"
    fresh = client.post(
        "/auth/verify", json={"email": EMAIL, "password": PASSWORD, "code": second}
    )
    assert fresh.status_code == 200 and SESSION_COOKIE in fresh.cookies


def test_a_reset_completed_on_an_unverified_account_verifies_it(client) -> None:
    """The token only ever arrived in that mailbox — the gate has been satisfied."""
    _signup(client)
    client.post("/auth/reset/request", json={"email": EMAIL})
    token = client.outbox.getvalue().split("token=")[1].split()[0]

    confirmed = client.post(
        "/auth/reset/confirm", json={"token": token, "password": "brand-new-8"}
    )
    assert confirmed.status_code == 200 and SESSION_COOKIE in confirmed.cookies
    assert client.db.scalars(select(Account)).one().verification_pending_since is None

    client.cookies.clear()
    on_the_new_one = client.post(
        "/auth/login", json={"email": EMAIL, "password": "brand-new-8"}
    )
    assert on_the_new_one.status_code == 200 and "account" in on_the_new_one.json()


def test_a_state_changing_call_without_the_csrf_header_is_refused(client) -> None:
    naked = client.post(
        "/auth/signup",
        json={"email": EMAIL, "password": PASSWORD},
        headers={CSRF_HEADER: ""},
    )
    assert naked.status_code == 403 and naked.json()["error"]["code"] == "csrf_required"
    assert client.db.scalars(select(Account)).all() == []  # refused before the route


def test_a_reset_round_trip_says_the_same_thing_to_a_stranger(client) -> None:
    signup_and_verify(client)
    client.cookies.clear()

    known = client.post("/auth/reset/request", json={"email": EMAIL})
    unknown = client.post("/auth/reset/request", json={"email": "nobody@mijual.kr"})
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json() == {"requested": True}
    # …and only the real address produced a link, server-side only.
    printed = client.outbox.getvalue()
    assert "nobody@mijual.kr" not in printed
    token = printed.split("token=")[1].split()[0]
    assert token not in known.text

    confirmed = client.post(
        "/auth/reset/confirm", json={"token": token, "password": "brand-new-8"}
    )
    assert confirmed.status_code == 200
    # Single use, and the old password is gone.
    assert client.post(
        "/auth/reset/confirm", json={"token": token, "password": "another-one-8"}
    ).json()["error"]["code"] == "invalid_reset_token"
    client.cookies.clear()
    assert client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD}).status_code == 401
    assert client.post(
        "/auth/login", json={"email": EMAIL, "password": "brand-new-8"}
    ).status_code == 200


def test_deleting_an_account_takes_the_email_and_the_session_with_it(client) -> None:
    signup_and_verify(client)
    assert client.delete("/auth/account").json()["deleted"] is True
    assert client.db.scalars(select(Account)).all() == []  # the email is gone now
    assert client.db.scalars(select(AuthSession)).all() == []  # so is access
    assert client.get("/auth/me").json() == {"authenticated": False}
    assert client.delete("/auth/account").status_code == 401


def test_a_get_still_cannot_write(client) -> None:
    """P5.S1's guarantee, from both sides: the read session rolls back, and a
    safe method cannot even ask for the committing one."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    app = create_app()
    app.state.engine = engine
    app.state.session_factory = sessionmaker(bind=engine)

    request = type("R", (), {"app": app, "method": "GET", "url": None})()
    reading = get_session(request)  # type: ignore[arg-type]
    reader = next(reading)
    reader.add(Corp(corp_code="00000001", corp_name="쓰기금지"))
    reader.flush()  # as far as a GET can get: pending, never committed
    next(reading, None)  # the request ends — and the session rolls back
    assert sessionmaker(bind=engine)().scalars(select(Corp)).all() == []

    request.url = type("U", (), {"path": "/board"})()
    with pytest.raises(RuntimeError, match="must not write"):
        next(get_write_session(request))  # type: ignore[arg-type]
