"""The HTTP layer — the service over what the pipeline persisted, plus the
reader's own rows.

`P5.S1` created this package; `architecture` had deferred it ("there is no HTTP
layer yet"). Everything the product **shows** is a read: board, event detail,
내 종목 조회, the ops panel are served from rows the P2 pipeline already wrote,
and no request path derives a displayed number of its own. `P5.S7` added the only
kind of write this layer does — **a reader's own data**: their account, their
session, and (from `P5.S8`) their holdings. Those go through a separate
committing dependency, and a safe HTTP method cannot acquire it, so "a GET never
writes" stayed true when writes arrived. `P5.S9`'s 운영 관제 adds no third kind:
its two ``POST`` routes touch only the operator's own session row, and every other
ops route is a ``GET`` **by rule** (R7 §6.5 — mutation 엔드포인트 없음).

**The request-path rule (a boundary, not a guideline) — re-aimed by `P6.S4`.**

Through P5 it read *"No OpenDART call and no LLM call may happen in a request
path"*. R6's AI 질문 agent **is** a model call in a request path — SSE streaming
cannot be anything else — so the boundary was moved deliberately rather than
allowed to quietly become false (`P6` Finding 1). It now reads:

    No OpenDART call happens in any request path; the model is reached **only**
    through :mod:`mijual.agent`; and ``mijual.web`` itself speaks HTTP in exactly
    one file.

The first clause is the one that keeps a dead worker leaving the board **stale,
never dark** — the 결격 uptime rule. Everything the product *shows* is still read
from persisted state; if the data is old, the product says how old (the freshness
기준시각) and keeps serving. Nothing about the board's availability depends on the
agent: :mod:`mijual.web.ask` is one route, and a model that is down costs that
route its answers and no other surface anything.

The rule is kept **structurally**, not by discipline, and all three clauses are
scanned:

* nothing under ``mijual.web`` imports :mod:`mijual.dart`, :mod:`mijual.collect`
  or :mod:`mijual.extract` — the three spending modules
  (``tests/test_web_smoke.py``);
* nothing under ``mijual.web`` imports a model SDK — the seam is
  :mod:`mijual.agent`, which owns the credential, the call budget and the ▷
  ledger (``tests/test_web_smoke.py``);
* only :mod:`mijual.web.vocky` imports an HTTP client
  (``tests/test_web_vocky.py``);
* and :mod:`mijual.agent` itself imports no spending module either
  (``tests/test_agent_tools.py``) — the agent reads persisted rows, it never
  collects or extracts.

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
    mijual.web.portfolio — 내 포트폴리오: holdings, 챙긴 돈 marks, 알림 preferences
    mijual.web.ops       — the operator door: a **separate** credential, a
                           differently named cookie, one uniform failure (R7 §6.4)
    mijual.web.opsreads  — 운영 관제's numbers, each re-read from the source that
                           already owns it (발명 수치 금지)
    mijual.web.conversations — the AI 질문 storage port: framed by P5
    mijual.web.conversationstore — `P6.S1`'s implementation of it: the anonymous
                           conversation/feedback tables, their write API, and the
                           newest-first cursor reads the three ops tabs render
    mijual.web.ask       — `P6.S4`'s transport for the AI 질문 agent: the SSE
                           stream, the turn's transaction and row, and the
                           identity-free rate limiter that says nothing
    mijual.web.routers   — one module per surface (health · board · events ·
                           stocks · auth · portfolio · ops · ask)

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
