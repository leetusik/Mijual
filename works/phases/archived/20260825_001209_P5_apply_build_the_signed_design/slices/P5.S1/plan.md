# Plan — P5.S1: FastAPI service skeleton + read-layer foundations

## Context

First build slice of P5 (apply phase). Read `works/phases/active/P5/phase.md` first —
its *Context* read order, *Constraints*, and the S1 row are binding. The repo today is
`src/mijual` (P2 pipeline: collect → bodydoc → extract → gates, plus `calc`, `estimate`,
`db`, `scheduler`) with **no HTTP layer**. This slice creates it — the skeleton only.
Later slices (S2 presentation contract, S3+ endpoints) build on what you leave here, so
the deliverable is a clean, small foundation, not features.

## Deliverables

1. **New package `src/mijual/web/`** — the HTTP layer:
   - `app.py` — `create_app() -> FastAPI` app factory. No module-level app-with-side-
     effects; the factory wires settings, DB, and routers. Expose a module-level
     `app = create_app()` only if needed for the uvicorn target, and keep it
     side-effect-free at import (no DB connect at import time; engine/session made
     lazily per the dependency below).
   - `deps.py` (or similar) — DB session dependency built on the existing
     `mijual.db.session.make_engine` / `make_session_factory` / `session_scope`
     conventions (reuse them; do not invent a second engine convention). One engine per
     app lifetime, sessions per request, read-only usage pattern.
   - `errors.py` — the **error envelope**: one consistent JSON error shape for the
     whole service (e.g. `{"error": {"code": ..., "message_ko": ...}}` — pick a shape
     and document it in the module docstring; user-facing `message_ko` strings are
     Korean, and only strings that already exist in the product copy — do not invent
     Korean copy where a code suffices; internal/log messages English). Register
     handlers on the factory so unhandled errors, 404s, and validation errors all
     return the envelope.
   - `time.py` (or similar) — the **KST time policy**: KST tzinfo constant, `now_kst()`,
     and serialization policy — every timestamp the API emits is an **absolute KST
     timestamp (ISO-8601 with +09:00 offset)**; D-day/diffs are computed upstream,
     never left to the browser. This module is what S2/S3 will import.
   - `GET /health` — trivial JSON (status + server now_kst), proving app + envelope +
     time policy wiring. No DB requirement for health (the board must be stale, never
     dark; health must not flap with the DB).
2. **The request-path rule, in code and stated:** no OpenDART call and no LLM call may
   happen in a request path (`docs/current/architecture.md` boundary). Encode it as a
   package-level docstring rule in `mijual/web/__init__.py` (the structural guarantee:
   `mijual.web` imports nothing from `mijual.dart`, `mijual.collect`, `mijual.extract`;
   keep it true).
3. **Dependencies** — add `fastapi` and `uvicorn` to `pyproject.toml` dependencies
   (and `httpx` under dev extras for the TestClient). Follow the existing commented
   style there (a one-line comment saying which slice/why). Install into `.venv`.
4. **Dev run command** — document it where a developer will find it: a short comment
   block in `compose.yaml`'s header alongside the existing run commands (e.g.
   `.venv/bin/uvicorn mijual.web.app:app --reload`), and/or the `web` package
   docstring. No Docker service for the web app — deployment is P4.
5. **One terse smoke test** — `tests/test_web_smoke.py`: TestClient against
   `create_app()`; assert `/health` 200 + shape, and one unknown route returns the
   error envelope shape. No DB, no network, no fixtures beyond the client. Keep the
   whole suite fast (baseline: 59 passed ≈ 1 s) — do not add fixture sprawl.

## Constraints (from `phase.md` — do not rediscover)

- RESPECT THE DESIGN — not visually relevant here, but the KST/absolute-timestamp and
  stale-never-dark rules originate in the signed design and are binding on this layer.
- Korean-only product surface: any string a user could see (error messages) is Korean;
  code, comments, logs English.
- No Alembic; this slice should need no schema change at all.
- Keep the P2 pipeline untouched — no refactors of existing modules beyond what reuse
  requires (which should be zero edits outside `pyproject.toml` and the new package).

## Validation

- `.venv/bin/python -m pytest` — full suite green (59 existing + new smoke test).
- `.venv/bin/uvicorn mijual.web.app:app` starts and serves `/health` (curl it, then
  stop it).
- `python3 scripts/workflow.py validate` passes.

## Wrap-up

Write `result.md` (free-form) in this slice folder; append to `phase.md` *Findings &
Notes* anything later slices need (e.g. the chosen error-envelope shape, the uvicorn
target, the deps module import path) and a *Doc impact* line (this creates the HTTP
layer — durable truth for `backend`/`architecture`/`api`). Return the structured
verdict. Do not commit; do not transition status.
