"""Request-scoped dependencies — today, the read-only database session.

**One engine per app, one session per request, and no writes.**

*One engine.* The engine (and its connection pool) is built **once per app
instance** and cached on ``app.state``. It is built **lazily**, on the first
request that actually asks for a session — importing :mod:`mijual.web.app`, or
constructing the app in a test, connects to nothing. That is what lets
``GET /health`` answer while Postgres is down: the board must be **stale, never
dark**, and a health check that flaps with the database is worse than none.

*One session per request.* :func:`get_session` yields a session for the duration
of one request and closes it after. Sessions are cheap; connections are not, and
the pool is the thing being shared.

*No writes.* The request path **rolls back**, always — on the way out of a
successful request too. P5's HTTP layer is a read layer over what the pipeline
persisted, so a session that reaches the end of a request holding pending changes
is a bug, and rolling back turns that bug into "nothing happened" instead of
"something was quietly written by a GET". This is deliberately **not**
:func:`mijual.db.session.session_scope`, which commits: that wrapper is the
pipeline's, and it is the right one there and the wrong one here. The engine
itself comes from :func:`mijual.db.session.make_engine` — one engine convention
for the whole codebase, not a second one for the web.

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

__all__ = ["DbSession", "dispose_engine", "get_session", "session_factory"]


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


#: What an endpoint signature says: ``def board(db: DbSession) -> …``.
DbSession = Annotated[Session, Depends(get_session)]
