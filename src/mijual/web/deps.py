"""Request-scoped dependencies — the database session, in two flavours.

**One engine per app, one session per request, and a GET that cannot write.**

*One engine.* The engine (and its connection pool) is built **once per app
instance** and cached on ``app.state``. It is built **lazily**, on the first
request that actually asks for a session — importing :mod:`mijual.web.app`, or
constructing the app in a test, connects to nothing. That is what lets
``GET /health`` answer while Postgres is down: the board must be **stale, never
dark**, and a health check that flaps with the database is worse than none.

*One session per request.* :func:`get_session` yields a session for the duration
of one request and closes it after. Sessions are cheap; connections are not, and
the pool is the thing being shared.

*No writes — on the read dependency.* :func:`get_session` **rolls back**, always
— on the way out of a successful request too. Everything the product *shows* is a
read over what the pipeline persisted, so a reading session that reaches the end
of a request holding pending changes is a bug, and rolling back turns that bug
into "nothing happened" instead of "something was quietly written by a GET". This
is deliberately **not** :func:`mijual.db.session.session_scope`, which commits:
that wrapper is the pipeline's, and it is the right one there and the wrong one
here. The engine itself comes from :func:`mijual.db.session.make_engine` — one
engine convention for the whole codebase, not a second one for the web.

*Writes are a second, explicit dependency.* ``P5.S7`` introduced the first ones
(accounts, sessions) and ``P5.S8`` adds holdings. They take
:data:`WriteSession`, which commits on success and rolls back on any exception —
and which **refuses a safe HTTP method outright**: asking for a committing
session inside a ``GET`` raises before the handler runs. That keeps "a GET never
writes" a property of the wiring rather than a habit, which is what ``P5.S1``
recorded when it made the read session rollback-only. A route that declares both
dependencies would get two independent sessions, so a route picks one; FastAPI
caches each per request, so declaring :data:`WriteSession` beside a dependency
that also uses it (:data:`mijual.web.auth.WriteAccount`) still yields exactly one
session and one transaction.

Deployment concerns that belong to **P4**, noted so they are not rediscovered:
pool sizing, ``pool_pre_ping`` for a long-lived process against a database that
recycles connections, and whether serving points at a read replica.
"""

from __future__ import annotations

from typing import Annotated, Iterator

from fastapi import Depends, Request
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from mijual.config import Settings
from mijual.db.session import make_engine, make_session_factory

__all__ = [
    "DbSession",
    "SAFE_METHODS",
    "WriteSession",
    "dispose_engine",
    "get_session",
    "get_write_session",
    "session_factory",
]

#: HTTP methods that may not acquire a committing session. Not a subset of
#: "methods this service serves" — it is the whole idempotent half of HTTP.
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def session_factory(app_state) -> sessionmaker[Session]:
    """The app's session factory, built on first use and cached on ``app.state``.

    ``app_state`` is a Starlette ``State``; it carries the :class:`Settings` the
    factory was created with (``app.state.settings``).
    """
    factory: sessionmaker[Session] | None = getattr(app_state, "session_factory", None)
    if factory is None:
        settings: Settings = app_state.settings
        engine: Engine = make_engine(settings.database_url)
        factory = make_session_factory(engine)
        app_state.engine = engine
        app_state.session_factory = factory
    return factory


def dispose_engine(app_state) -> None:
    """Release the pool at shutdown. A no-op if no request ever needed the DB."""
    engine: Engine | None = getattr(app_state, "engine", None)
    if engine is not None:
        engine.dispose()
        app_state.engine = None
        app_state.session_factory = None


def get_session(request: Request) -> Iterator[Session]:
    """A read-only session for one request. Rolls back and closes, never commits."""
    session = session_factory(request.app.state)()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def get_write_session(request: Request) -> Iterator[Session]:
    """A committing session for one state-changing request.

    Commits once, at the end, if the handler returned; rolls back if anything
    raised — including an :class:`~mijual.web.errors.ApiError` a handler raises
    deliberately, so a rejected signup leaves no half-written account behind.

    The ``SAFE_METHODS`` guard is not defensive coding, it is the boundary: a
    ``GET`` that reaches for this dependency is a bug in the route declaration,
    and it fails loudly at the first request rather than quietly writing on a
    read for a year. It raises :class:`RuntimeError` — a 500 in the envelope,
    because there is nothing the caller did wrong and nothing they can fix.
    """
    if request.method.upper() in SAFE_METHODS:
        raise RuntimeError(
            f"{request.method} {request.url.path} asked for a committing session; "
            "a safe method must not write"
        )
    session = session_factory(request.app.state)()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


#: What a reading endpoint signature says: ``def board(db: DbSession) -> …``.
DbSession = Annotated[Session, Depends(get_session)]
#: …and a writing one: ``def signup(db: WriteSession) -> …``.
WriteSession = Annotated[Session, Depends(get_write_session)]
