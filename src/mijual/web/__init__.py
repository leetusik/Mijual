"""The HTTP layer — the service over what the pipeline persisted, plus the
reader's own rows.

`P5.S1` created this package; `architecture` had deferred it ("there is no HTTP
layer yet"). Everything the product **shows** is a read: board, event detail,
내 종목 조회, the ops panel are served from rows the P2 pipeline already wrote,
and no request path derives a displayed number of its own. `P5.S7` added the only
kind of write this layer does — **a reader's own data**: their account, their
session, and (from `P5.S8`) their holdings. Those go through a separate
committing dependency, and a safe HTTP method cannot acquire it, so "a GET never
writes" stayed true when writes arrived.

**The request-path rule (a boundary, not a guideline).**

    No OpenDART call and no LLM call may happen in a request path.

That is the `architecture` boundary in one sentence, and it is why a dead worker
leaves the board **stale, never dark** — the 결격 uptime rule. Serving may only
read persisted state; if the data is old, the product says how old (the
freshness 기준시각) and keeps serving.

The rule is kept **structurally**, not by discipline: nothing under
``mijual.web`` imports :mod:`mijual.dart`, :mod:`mijual.collect` or
:mod:`mijual.extract` — the three modules that spend requests or model calls.
``tests/test_web_smoke.py`` asserts it by walking this package's imports, so a
later slice cannot reintroduce a spending call without the suite saying so.
What this layer *may* import is the deterministic side: :mod:`mijual.calc` (all
displayed arithmetic), :mod:`mijual.gates.exposure` (the exposure contract, which
P5 renders and never re-decides) and :mod:`mijual.db` (persisted rows).

Layout::

    mijual.web.app       — create_app() factory + the module-level uvicorn target
    mijual.web.deps      — request-scoped DB sessions: reading (rollback-only)
                           and writing (commits; refuses a safe method)
    mijual.web.errors    — the one JSON error envelope for the whole service
    mijual.web.csrf      — the required unsafe-method header, service-wide
    mijual.web.clock     — the KST time policy every timestamp goes through
    mijual.web.reads     — loading: persisted rows in, ``mijual.present`` shapes out
    mijual.web.auth      — reader accounts, sessions, the reset grant (R5)
    mijual.web.passwords — scrypt hashing, parameters carried in the hash
    mijual.web.routers   — one module per surface (health · board · events ·
                           stocks · auth)

Routers stay transport-thin: they read settings, call :mod:`mijual.web.reads`, and
serialize. Loading lives in ``reads``; meaning lives in :mod:`mijual.present`. An
endpoint that starts computing a displayed number is an endpoint that will
eventually disagree with another one about it.

Run it in development (no Docker service — deployment is P4)::

    docker compose up -d postgres
    .venv/bin/uvicorn mijual.web.app:app --reload

Two house rules this layer inherits and must not relax:

*Korean-only product surface.* Any string a user could read is Korean, and it
comes from copy the product already owns (`grounding/copy-inventory.md`).
Inventing a Korean string is a design change, not an implementation detail — so
an error the design has not written copy for travels as a machine ``code`` and
no Korean at all. Code, comments and logs are English.

*Absolute KST timestamps.* Every instant this service emits carries ``+09:00``
and every D-day is computed upstream. See :mod:`mijual.web.clock`.
"""

from __future__ import annotations

__all__ = ["create_app"]


def __getattr__(name: str) -> object:
    # Lazy re-export: ``from mijual.web import create_app`` works without making
    # importing the package drag in FastAPI (and its Starlette/pydantic tail).
    if name == "create_app":
        from mijual.web.app import create_app

        return create_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
