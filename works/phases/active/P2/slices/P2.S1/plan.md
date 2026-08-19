# Plan: P2.S1 — package scaffold, storage schema (event/version/snapshot), DART client port

## Context

First real (non-throwaway) code in the repo. Everything downstream (S2–S9) imports this slice's package, writes through its models, and calls DART through its client. The stack is decided (phase.md N1): plain Python package + SQLAlchemy + Postgres; Celery beat + Redis arrive in S6; FastAPI is P3's. The entity design is non-negotiable (N2): event key `(corp_code, report_subtype, original_rcept_dt)`, every observed `rcept_no` a version, every version snapshotted at collection time with raw body retained — a wrong key here silently destroys the 정정 story. Environment facts are measured (N9): Docker up, Python 3.13.5, no packages installed, `.venv/` gitignored, `.env` holds `DART_API_KEY` only.

Executor: `slice-executor-high` (risk high, multi-file real code).

## Deliverables

1. **Package scaffold** — `pyproject.toml` at repo root, `src/mijual/` layout, `.venv` (create + install editable). Dependencies now: `sqlalchemy`, `psycopg[binary]`; do **not** add celery/redis/fastapi yet (S6/P3 own those). Dev deps: `pytest` only.
2. **Config module** (`src/mijual/config.py`) — port the spike's in-process `.env` parsing, generalized: `DART_API_KEY`, `DATABASE_URL` (default pointing at the local docker Postgres), `REDIS_URL` (reserved for S6), `GEMINI_API_KEY` (reserved for S4; absent today — must not crash when missing, only when used). Secrets never echoed/logged (binding constraint).
3. **Local infra** — `compose.yaml` with `postgres:16` (+ named volume) and `redis:7` (S6 will use it; adding it now is one line — but Redis stays unstarted-by-default if compose makes that awkward, executor's call). Document `docker compose up -d postgres` as the dev path; `psql` is not on PATH, so verification goes through SQLAlchemy, not psql.
4. **DART client port** (`src/mijual/dart/client.py`) — port `scripts/spike/dart.py` **keeping the four proven behaviors** (N7): drop `None` params (never serialize them), `group[]` vs flat `list` handling, 503 retry/backoff, ZIP-vs-error-XML detection (`PK` magic). Make it a small class (or module with injectable settings) so the **cache directory and key are injectable**: default cache under a new location, but the **cache filename scheme must stay byte-compatible with the spike's** (`_safe_query` → sorted key-stripped querystring → sha1[:12] digest + hint), so pointing the cache dir at `scripts/spike/samples/` makes all 1,002 cached responses (59 본문 ZIPs) a working offline fixture path — no key, no network. Key-safety invariants carry over: key stripped from cache filenames and the recorded `_url`; exception text never carries the URL. Spike files themselves stay untouched.
5. **Storage schema** (`src/mijual/db/models.py`, `src/mijual/db/session.py`) — SQLAlchemy models for the collection side only (extraction/gate tables belong to S4/S5, don't pre-design them):
   - `Corp` — `corp_code` PK, name, `corp_cls`.
   - `Event` — the N2 key: unique `(corp_code, report_subtype, original_rcept_dt)`; `report_subtype` = source endpoint/subtype discriminator (e.g. `piicDecsn`, `cvbdIsDecsn`, merger 계열); a rights-type classification column (①/②/③) and room for S2's correctness-filter outcome (e.g. nullable `suppressed_reason` — exact columns are the executor's call, but the schema must let S2 record "collected but excluded/suppressed, and why" without a migration).
   - `FilingVersion` — FK event, `rcept_no`, `rcept_dt`, correction marker (`[기재정정]`/`[첨부정정]`/original), observed_at; unique `(event_id, rcept_no)`.
   - `Snapshot` — FK version, source (endpoint name or `document`), captured_at, raw payload (JSONB for JSON bodies, bytea for 본문 ZIP bytes).
   - **No Alembic.** Schema evolves via `metadata.create_all` + drop/recreate during P2 — all data is re-collectable from cache/API. Record this as a deliberate decision in `result.md`/phase notes; revisit only if P3 demands migrations.
6. **Smoke path + terse tests** — one runnable smoke (e.g. `python -m mijual.smoke`): create tables against docker Postgres, read one cached `list` response and one cached 본문 ZIP through the client with the cache dir pointed at the spike samples (offline), persist one event→version→snapshot chain, print a short evidence summary (no key material). Pytest: a few high-value cases only — cache-path byte-compatibility against a real existing spike cache file, `None`-param dropping, `group[]` normalization, event-key uniqueness. No fixture sprawl.

## What this slice does NOT do

No collector polling logic (S2), no 본문 parsing beyond ZIP decode (S3), no LLM anything (S4), no gates (S5), no Celery wiring (S6), no doc-new-version. Executor writes `result.md`, appends findings + any Doc impact note (schema shape is durable truth — extend the N1 stack note) to `phase.md`, runs `python3 scripts/workflow.py validate`.

## Verification

- `.venv/bin/python -m pytest` green (terse suite).
- Smoke run against `docker compose up -d postgres` + offline cache: event/version/snapshot chain persisted and re-read; second run idempotent on the unique keys (expected failure or upsert — executor states which).
- `grep`-level check: no secret value in any new file, cache filename, or log line.
- `python3 scripts/workflow.py validate` passes.

## Orchestrator lifecycle

1. `start-slice P2.S1`; copy this approved plan to `works/phases/active/P2/slices/P2.S1/plan.md`.
2. Dispatch `slice-executor-high` (background). Idle window: prepare S2 (collector) advisory notes read-only.
3. On `done`: read `result.md`, `workflow.py validate`, `finish-slice P2.S1`, commit `feat(pipeline): ...`.
4. Gate again for P2.S2.
