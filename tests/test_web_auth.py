"""Reader auth (P5.S7): what a session is, and what a failure is allowed to say.

DB-free, the established pattern — in-memory SQLite, dependency overrides, no
docker and no network. The cases are the prohibitions R5 states: a login error
never distinguishes the two ways to be wrong, a reset request never reveals
whether the address has an account, deletion takes the email and the session with
it, and a GET still cannot write.
"""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.config import Settings
from mijual.db.models import Account, AuthSession, Base, Corp
from mijual.mail import ConsoleMailer
from mijual.web.app import create_app
from mijual.web.auth import SESSION_COOKIE
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

    def _write():  # the write path really does commit
        yield session
        session.commit()

    app.dependency_overrides[get_write_session] = _write
    with TestClient(app, headers={CSRF_HEADER: "1"}) as test_client:
        test_client.outbox = outbox  # type: ignore[attr-defined]
        test_client.db = session  # type: ignore[attr-defined]
        yield test_client
    session.close()


def _signup(client, email=EMAIL, password=PASSWORD):
    return client.post("/auth/signup", json={"email": email, "password": password})


def test_signup_login_me_logout_is_one_session_and_a_normalized_email(client) -> None:
    created = _signup(client)
    assert created.status_code == 201
    # The address is stored in one spelling, case-folded — 중복 가입 does not
    # depend on the shift key.
    assert created.json()["account"]["email"] == "reader@mijual.kr"
    cookie = created.cookies[SESSION_COOKIE]
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

    assert client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD}).status_code == 200


def test_a_login_failure_never_says_which_field_and_a_duplicate_is_structural(
    client,
) -> None:
    _signup(client)
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

    duplicate = _signup(client, email="READER@mijual.kr")
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "email_taken"
    assert _signup(client, email="new@mijual.kr", password="short").json()["error"][
        "code"
    ] == "password_too_short"


def test_a_state_changing_call_without_the_csrf_header_is_refused(client) -> None:
    naked = client.post(
        "/auth/signup",
        json={"email": EMAIL, "password": PASSWORD},
        headers={CSRF_HEADER: ""},
    )
    assert naked.status_code == 403 and naked.json()["error"]["code"] == "csrf_required"
    assert client.db.scalars(select(Account)).all() == []  # refused before the route


def test_a_reset_round_trip_says_the_same_thing_to_a_stranger(client) -> None:
    _signup(client)
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
    _signup(client)
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
