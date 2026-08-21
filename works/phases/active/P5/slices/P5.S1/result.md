# Result — P5.S1: FastAPI service skeleton + read-layer foundations

**Status: done.** The repo has an HTTP layer. `architecture` v0002 said "there is no HTTP layer
yet — FastAPI is P3's"; `src/mijual/web/` is now that layer, as a skeleton only: an app factory,
a read-only DB session dependency, one error envelope, the KST time policy, `GET /health`, and
three tests. No endpoint that renders product data was written — those are S3/S4's, over S2's
presentation contract.

## What landed

| path | what it is |
|---|---|
| `src/mijual/web/__init__.py` | the package rule: **no OpenDART call and no LLM call in a request path**, kept structurally (imports nothing from `mijual.dart` / `collect` / `extract`), plus the layout and the dev run command |
| `src/mijual/web/app.py` | `create_app(settings=None) -> FastAPI` + the module-level `app` uvicorn points at; lifespan disposes the pool at shutdown and connects to nothing at startup |
| `src/mijual/web/deps.py` | `get_session` / `DbSession` — one engine per app (**lazy**, cached on `app.state`), one session per request, **rollback always, never commit** |
| `src/mijual/web/errors.py` | `ApiError` / `NotFound` / `envelope()` / `register_error_handlers()` — the one JSON error shape |
| `src/mijual/web/clock.py` | `KST` (re-exported from `mijual.calc`, never redefined), `now()`, `to_kst()`, `iso()`, `iso_date()` |
| `src/mijual/web/routers/{__init__,health}.py` | where S3+ put one router per signed surface; `GET /health` today |
| `tests/test_web_smoke.py` | 3 tests: health up + KST, unknown route → envelope, and the import-boundary scan |
| `pyproject.toml` | `fastapi>=0.115`, `uvicorn>=0.30` (runtime), `httpx>=0.27` (dev) — each with the existing one-line why-comment style |
| `compose.yaml` | the dev run command in the header block; **no** web service (deployment is P4) |

Nothing outside `pyproject.toml`, `compose.yaml` and the two new paths was touched — the P2
pipeline is byte-identical.

## The three decisions this slice had to make

**1. The error envelope, and why `message_ko` is usually absent.**

```json
{"error": {"code": "not_found", "message": "…English, developer-facing…",
           "message_ko": "…", "fields": [ … ]}}
```

`code` is a stable English `snake_case` token (the thing a client branches on); `message` is
English and never rendered to a user; `fields` is 422-only. `message_ko` is **present only when
the product already owns that Korean string** — e.g. an `ApiError` raised with
`WITHDRAWN_NOTICE_KO` — and **omitted** otherwise.

The plan's constraint drove this: inventing a Korean string is a design change, and the signed
design writes no HTTP-error copy at all. It writes *state* copy (철회 / 추후결정 / 발행사 기재
불일치), which reaches the user in a normal 200 payload, not an error. So the envelope ships the
code alone and lets the surface decide once, in the design's own words. Optional keys are
**omitted rather than null**, the same discipline the exposure contract applies to a gate-blocked
field.

Handlers are registered for `ApiError`, `StarletteHTTPException` (404/405 and any raised
`HTTPException`), `RequestValidationError` and bare `Exception`, so there is no path back to
FastAPI's default `{"detail": …}` body. The 500 handler logs the traceback and tells the client
nothing but the code — verified below that a raised `RuntimeError("secret table name leaked
here")` produces `{"error": {"code": "internal_error", "message": "the request could not be
served"}}`.

**2. `/health` does not touch the database — deliberately.** A liveness check that fails when
Postgres is unreachable turns one outage into two (the process gets restarted or pulled while it
is still able to serve the last known board). "Stale, never dark" is a product rule, and this is
its operational half. Freshness — the landing 기준시각 — is a *different question about the
corpus* and belongs to S3's summary endpoint, not to a liveness probe.

**3. Lazy engine, rollback-only sessions.** The engine is built on the **first request that
actually needs a row**, not at import and not at startup, which is what lets `/health` answer
while the database is down (verified: `app.state.engine is None` until the first DB request).
The request path calls `session.rollback()` on the way out of *successful* requests too: P5's
HTTP layer is a read layer, so a session holding pending changes at the end of a request is a
bug, and rolling back makes that bug "nothing happened" instead of "a GET wrote something". This
is explicitly **not** `mijual.db.session.session_scope`, which commits — that wrapper is the
pipeline's and is correct there. The *engine* still comes from `make_engine`: one engine
convention for the codebase, per the plan.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **62 passed, 0.90 s** (59 baseline + 3 new), 1 warning — no network, no model, no DB |
| `.venv/bin/uvicorn mijual.web.app:app --port 8099` + curl | **served**; see the transcript below; process stopped afterwards |
| `python3 scripts/workflow.py validate` | **Workflow validation passed.** |

Live transcript (server started, curled, stopped):

```
GET  /health  → 200 {"status":"ok","version":"0.1.0","now_kst":"2026-08-22T00:25:39+09:00"}
GET  /nope    → 404 {"error":{"code":"not_found","message":"Not Found"}}
POST /health  → 405 {"error":{"code":"method_not_allowed","message":"Method Not Allowed"}}
                    (with `allow: GET` preserved from the exception's headers)
```

Additionally verified with a throwaway app in scratch (**not committed** — these paths get real
tests when a real endpoint needs them, per the terse-tests rule):

```
500 → {"error":{"code":"internal_error","message":"the request could not be served"}}   (traceback logged, not sent)
409 → {"error":{"code":"withdrawn","message":"event withdrawn","message_ko":"이 유상증자는 철회되었습니다"}}
422 → {"error":{"code":"invalid_request","message":"request failed validation",
                "fields":[{"loc":["query","n"],"msg":"Input should be a valid integer, …"}]}}
DbSession → 200 {"one":1} against the live docker Postgres; engine None before, live after
```

The third smoke test is the one worth keeping: it walks every `.py` under `src/mijual/web/` with
`ast` and fails if any of them imports `mijual.dart`, `mijual.collect` or `mijual.extract`. The
`architecture` boundary is now enforced by the suite rather than by whoever remembers it, and it
keeps working as S3–S9 add modules.

## Deviations from plan.md

1. **`time.py` → `clock.py`.** The plan allowed "`time.py` (or similar)". `mijual.web.time` would
   shadow the stdlib module by name for every reader (absolute imports mean it is safe, but it
   reads as a trap). **S2/S3 import `mijual.web.clock`.**
2. **A `routers/` subpackage** rather than the health route inline in `app.py`. One module per
   signed surface is where S3+ are going anyway, and it costs ~10 lines now.
3. **Three tests, not one.** The extra one is the import-boundary scan (deliverable #2 says "keep
   it true"; this is what makes that mechanical). Still no fixtures, and the suite grew 0.9 s → 0.9 s.
4. **`compose.yaml` only** for the dev run command (the plan said "and/or the `web` package
   docstring") — it is in both, since the package docstring is where an executor looks first.

## Not done here, on purpose

- `pool_pre_ping` / pool sizing / read-replica routing — **P4** deploy decisions, noted in
  `deps.py` so they are not rediscovered.
- CORS, compression, request-id middleware, auth — nothing was added speculatively. S7 owns the
  session cookie; the Next.js origin question is S10's when there is a frontend to have an origin.
- No `mijual.gates` / `mijual.calc` import beyond `clock`'s `KST` — S2 is the layer that reaches
  for the exposure contract, and it should be the one to decide how.
