---
doc_id: backend
version: v0002
created_at: 2026-08-22T18:06:00+09:00
source: P5.REVIEW
summary: P5 apply phase: the mijual.web HTTP layer, the mijual.present derivation layer, auth/portfolio/ops modules, the mailer and conversation seams, and the label-field reader
previous: v0001_bootstrap
---

# Backend

## Status

Implemented in P5. The service is a FastAPI app over the P2 pipeline package, with a pure
derivation layer between them. It adds **no new runtime dependency beyond `fastapi` and
`uvicorn`** — auth, hashing, mail and the vocky client are all stdlib.

## Purpose

Server-side module layout, domain boundaries, jobs, auth, errors, and logging.

## Stack

- **Language/runtime:** Python 3.13
- **Framework:** FastAPI `>=0.115` (resolved 0.141.1 / starlette 1.6.0) on
  uvicorn `>=0.30`; `httpx` is a **dev extra** for `TestClient`
- **Package manager:** `uv` / `pyproject`, virtualenv at `.venv`
- **Server entrypoint:** `.venv/bin/uvicorn mijual.web.app:app --reload`
  (module-level `app` exists only as uvicorn's target; code calls
  `mijual.web.app.create_app`). There is deliberately **no compose service for the web app** —
  deployment is P4's.

## Module / Service Layout

- **`mijual.web`** — the HTTP layer. `app.py` (factory), `deps.py` (session dependencies),
  `errors.py` (the one envelope), `clock.py` (KST policy), `csrf.py`, `auth.py`,
  `passwords.py`, `portfolio.py`, `ops.py`, `opsreads.py`, `conversations.py`, `reads.py`,
  `vocky.py`, and one module per surface under `routers/`.
- **`mijual.present`** — the pure derivation layer (`values` · `event` · `money` · `summary`).
  **Every surface reads it; no endpoint re-derives a number.** Its constructors *refuse* to
  build what the design forbids: a blocked field, a date beside 추후결정, an untagged estimate,
  a won amount before 확정발행가 and a one-addend quote on a summed figure are
  **unconstructable**, not merely discouraged.
- **`mijual.web.reads`** — the batched read layer (`load_board` · `load_summary` ·
  `resolve_event` + `load_detail` · `load_stock` · `load_portfolio` · `corpus_as_of` ·
  `countdown_target` · `resolve_corp`). It loads only the fields a surface renders.
- **`mijual.db.repository`** — `readable_versions` · `document_of` · `current_version` ·
  `current_versions` (batched, no decode). Moved here from `mijual.extract.runner`, which
  re-exports them, so the exposure contract no longer reaches the extractor.
- **`mijual.beat`** — stdlib-only declaration of the beat schedule, window constants and the
  run-lock key, read by **both** the Celery app and the ops panel, so the panel can never
  render a schedule the worker is not running.
- **`mijual.mail`** — the mailer seam. `Message(to, kind, data)` carries **data, not rendered
  copy**; a `ConsoleMailer` dev transport prints and sends nothing.
- **`mijual.extract.labelfields`** — the free deterministic `본문-label` reader beside the paid
  schema-based one. It writes the same `Extraction` rows, so it is invisible to the gate layer,
  the exposure contract and the presentation contract. A second label field is a registry entry
  plus a gate, nothing more.

## Domain Boundaries

- **`web → present`, never the reverse.** `present` restates the instant-serialization policy
  rather than importing it back; a test pins the two together byte-for-byte.
- **No request-path module may import a spending module.** An AST import scan over
  `src/mijual/web/` fails the suite if one imports `mijual.dart`, `mijual.collect` or
  `mijual.extract`; `tests/test_present.py` applies the same scan to the derivation layer.
  Measured consequence: **`mijual.estimate` pulls `dart` + `collect` + `extract` at module
  level**, so retrospective 소멸가치 numbers reach a request path only from **persisted** state
  (`offering_input.inputs`, `performance_report.lapse`), written by an offline worker.
  Verified: `import mijual.web.app` pulls none of
  `dart`/`collect`/`extract`/`estimate`/`scheduler`/`evalset`, and no Celery.
- **The exposure contract is not re-decidable.** `gates.exposure.exposure_of` is the single
  derivation and the API renders what it says — `load_board` skips a row whose live verdict
  disagrees with the persisted column.
- **Only `web/vocky.py` may import an HTTP client** (`urllib`/`http.client`/`socket`/
  `requests`/`httpx`), asserted by a test, so a later slice cannot quietly put a second
  external dependency on a request path.

## Auth and Session Logic

- **The session is a row, not a signed cookie.** `auth_session` holds a **digest** of the
  token, never the token; 로그아웃 deletes the row and 계정 삭제 cascades. A stateless cookie
  would have needed a revocation list — i.e. this table — and saved no query.
- **`MIJUAL_SESSION_SECRET` peppers, it does not sign** (HMAC-SHA256 over the token), so a
  database dump holds nothing replayable and rotating the key logs everyone out. Unset is a
  development state: unkeyed SHA-256 plus one log warning.
- **scrypt from the stdlib**, `n=2**14, r=8, p=1` — ~25 ms/hash and the largest `n` that fits
  OpenSSL's **default `maxmem`**. Hashes carry their own parameters, so an upgrade bumps
  `passwords.CURRENT` and `needs_rehash` re-hashes each account at its next successful login.
- **CSRF is service-wide middleware, not a per-route dependency.** Every unsafe method must
  carry `X-Mijual-CSRF` or it is refused before the route runs. A cross-origin page cannot set
  a custom header without a preflight this service does not grant, so nothing is minted,
  stored or rotated.
- **Two session dependencies, and a GET can never write.** `DbSession` is rollback-only (it
  rolls back on the way out of *successful* requests too); `WriteSession` commits on success,
  rolls back on any exception, and **refuses a safe HTTP method outright**.
- **The operator door is a credential with no row.** `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD`
  from the environment; no operator account, no admin flag, no signup, no reset. `ops_session`
  carries **no `account_id`, no FK and no operator identifier at all**.

## Background Jobs / Workers

- **`python -m mijual.estimate snapshot`** — writes the serving precomputation
  (`offering_input` rows + `performance_report.lapse`). 0 requests, 0 LLM calls, idempotent.
- **`python -m mijual.estimate reparse`** — re-reads every stored 실적보고서 from its own
  `payload_bytes` and rewrites only the parse-derived columns. This is how *any* future
  `parse_performance` change reaches the corpus without spending a request.
- **`python -m mijual.extract labels`** — the free label-field pass. Runs **first inside
  `stage_extract` and outside `extract_max_calls`**: budgeting a pass that spends nothing could
  only starve it.
- The beat pipeline is now `collect → bodydoc → extract → gates → reparse → snapshot`, and
  every run writes a `pipeline_run` row (opened before the first stage, closed after the last).

## Error Handling and Logging

- One envelope, four handlers (`ApiError`, `HTTPException`, validation, bare `Exception`); the
  500 handler logs the traceback and returns **only** the code — no exception text in a body.
- The vocky client never logs its key, the response body or the exception text, and vocky's
  error text is never echoed onto the panel.
- A run-log failure is swallowed into a run note: a log that can kill a pipeline is worse than
  no log.
- Redis is optional at request time — the lock chip degrades to `state: "unknown"` with a
  reason and the tab still answers 200.

## Open Questions

- The serving process creates no schema at startup (it must answer while Postgres is down), so
  tables land through a pipeline entry point's `create_all` + `ensure_columns`. **P4** must
  ensure they exist before the API serves a fresh database.
- Pool sizing, `pool_pre_ping` and read-replica routing are noted in `deps.py` as **P4** deploy
  decisions.
- Rate limiting on the two login endpoints needs cross-process state and stays **P4**'s.
