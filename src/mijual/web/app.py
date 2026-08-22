"""The app factory, and the module-level target uvicorn is pointed at.

:func:`create_app` builds a fully wired :class:`~fastapi.FastAPI`: settings on
``app.state``, the error envelope's handlers, the lazy DB engine's lifespan, and
every router. Nothing it does reaches outside the process — no connection, no
request, no model call — so constructing an app is free and a test can build as
many as it likes.

**Why a factory and not a module-level app with setup around it.** A test, a
future admin app on its own path, and the dev server must all be able to get a
*fresh* app with *chosen* settings; anything configured at import time is
configured exactly once, in whatever order the imports happened to run. The
module-level :data:`app` below exists only because ``uvicorn`` needs an import
path to point at, and it is nothing more than a call to the factory::

    .venv/bin/uvicorn mijual.web.app:app --reload

**Serving is decoupled from the pipeline** and stays that way: this module
imports the deterministic side (:mod:`mijual.calc` through
:mod:`mijual.web.clock`, :mod:`mijual.db` through :mod:`mijual.web.deps`) and
none of the spending side. See the rule in :mod:`mijual.web`.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from mijual import __version__
from mijual.config import Settings, load_settings
from mijual.mail import ConsoleMailer, Mailer
from mijual.web.conversations import Conversations
from mijual.web.conversationstore import DbConversations
from mijual.web.csrf import register_csrf_guard
from mijual.web.deps import dispose_engine, session_factory
from mijual.web.errors import register_error_handlers
from mijual.web.routers import auth, board, events, health, ops, portfolio, stocks

__all__ = ["app", "create_app"]

TITLE = "미주알 API"
DESCRIPTION = (
    "HTTP layer over the persisted pipeline output. Everything the product "
    "shows is a read; the only writes are a reader's own account and holdings. "
    "No OpenDART call and no LLM call happens in a request path."
)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup connects to nothing; shutdown releases a pool only if one was made.

    The engine is created lazily by :func:`mijual.web.deps.session_factory`, on
    the first request that needs a row — so a database that is down delays
    nothing at startup and never keeps ``/health`` from answering.
    """
    yield
    dispose_engine(app.state)


def create_app(
    settings: Settings | None = None,
    *,
    mailer: Mailer | None = None,
    conversations: Conversations | None = None,
) -> FastAPI:
    """A fully wired app. Pass ``settings`` to point one at another database.

    ``mailer`` is the seam :mod:`mijual.mail` describes: P5 defaults to the
    console transport, which prints a password-reset link server-side and sends
    nothing, and **P4** passes a real transport here without touching a route.

    ``conversations`` is the same shape of seam for the AI 질문 agent's storage
    (:mod:`mijual.web.conversations`). P5 defaulted it to
    :class:`~mijual.web.conversations.EmptyConversations` because that build
    stored no conversations; **`P6.S1` filled the seam**, so the default is now
    :class:`~mijual.web.conversationstore.DbConversations` over the anonymous
    conversation tables — and the 대화 로그 / 익명 세션 / 피드백 tabs serve real
    rows **with no route change**, which is the whole point of the seam.
    ``EmptyConversations`` remains for a caller that wants a source with nothing
    in it. The factory below builds on the app's own lazy engine, so constructing
    an app still opens no connection.
    """
    app = FastAPI(
        title=TITLE,
        description=DESCRIPTION,
        version=__version__,
        lifespan=_lifespan,
    )
    app.state.settings = settings or load_settings()
    app.state.engine = None
    app.state.session_factory = None
    app.state.mailer = mailer or ConsoleMailer()
    app.state.conversations = conversations or DbConversations(
        lambda: session_factory(app.state)()
    )

    register_error_handlers(app)
    register_csrf_guard(app)
    app.include_router(health.router)
    app.include_router(board.router)
    app.include_router(events.router)
    app.include_router(stocks.router)
    app.include_router(auth.router)
    app.include_router(portfolio.router)
    # 운영 관제 (R7). Behind its own credential and its own cookie, read-only
    # everywhere but its two session routes, and linked from no reader surface.
    app.include_router(ops.router)
    return app


#: The uvicorn target (``mijual.web.app:app``). Built at import, but importing
#: this module still opens no connection and spends nothing — see the lifespan.
app = create_app()
