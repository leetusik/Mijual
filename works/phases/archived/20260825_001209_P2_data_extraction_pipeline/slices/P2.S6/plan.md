# Plan: P2.S6 — Celery beat scheduling of the collect / extract / gate pipeline

_Mode: auto. Plan written inline by the orchestrator._

## Context

The pipeline's four stages exist as idempotent CLIs: `mijual.collect` (discovery/pairing/snapshots, request-budgeted), `mijual.bodydoc` (본문 fetch + hint backfill + warrants), `mijual.extract` (Gemini, call-budgeted, idempotent by `(version, field, schema_version)`), `mijual.gates` (LLM-free re-derivation). Re-running any window is nearly free (S2's measured property). This slice makes them run on a schedule: Celery beat + worker + the Redis that `compose.yaml` already reserves behind the `scheduling` profile (host 6380, `DEFAULT_REDIS_URL` matches). "Scheduled jobs" is in the phase objective; ②'s collection task registration is S7's (it will add its task to the schedule this slice creates).

Binding constraints: the scheduler must be fully decoupled from serving (P3 reads persisted snapshots only — a dead worker must never darken the board, 결격 rule); overlapping runs must not double-fetch (locking); every live stage keeps its structural budget (quota 20,000/day known, but ceilings stay); secrets stay in `.env`.

Read first: `works/phases/active/P2/phase.md` (N41–N51 now included), `compose.yaml`, the four packages' `__main__.py` entry points (wire their run functions, not subprocesses, where practical).

## Deliverables

1. **Celery app** (`src/mijual/scheduler/` — layout yours): broker/backend from `Settings.redis_url`; add `celery>=5` + `redis>=5` to pyproject. Timezone **Asia/Seoul** explicitly.
2. **Tasks** wrapping the existing run functions (imports, not subprocess): `collect_recent` (rolling window, default ~14 days back to today — catches new filings and 정정 rows whose original is older, since pairing re-windows on the original date; parameterized), `bodydoc_sync` (fetch missing 본문 for target events + hint backfill + warrants pass), `extract_new` (only versions without stored rows — the idempotent skip makes this cheap; call ceiling per run), `gates_run` (full re-derivation), and a `daily_pipeline` chaining the four in order with a short summary log line per stage (counts only, no secrets).
3. **Beat schedule**: `daily_pipeline` once or twice daily during KST business-adjacent hours (your call, state it); optionally a weekly wider re-sync window (e.g. 90 days) for stragglers. Registered via `beat_schedule` so S7 can append the ② task the same way.
4. **Locking + budgets**: a Redis-based lock (or DB advisory lock — your call) so overlapping `daily_pipeline` runs are impossible; per-stage budgets passed explicitly (e.g. collect ≤ 500 requests, extract ≤ 60 calls per run — parameterized defaults, stated in result.md). A budget-exhausted stage stops cleanly (both clients already raise) and the chain reports it without crashing the run.
5. **Inline runner**: `python -m mijual.scheduler once [--offline] [--window N]` — runs the same `daily_pipeline` logic synchronously without a broker. This is the testable path, the S7/S8 reuse path, and the ops fallback.
6. **Evidence**: bring up Redis (`docker compose --profile scheduling up -d redis`), start a worker + beat locally, trigger `daily_pipeline` once (small live window is fine — budgets apply; offline mode acceptable if you prefer $0/0-request evidence), and show the four stages' summary lines. Document the ops runbook (compose profile, worker/beat commands, how P3's serving stays decoupled) in result.md.

## Tests (terse)

No live Celery/Redis in pytest: test the schedule registry (entries, timezone, task names resolve), the window computation, the lock semantics (fake/local), and `once --offline` end-to-end against the caches (0 requests, 0 calls). A few high-value cases only.

## Out of scope

② collection/backfill (S7 — it registers its task into this schedule), estimation (S8), evalset (S9), deployment to `ssh h` (P4). No commits, no state transitions, no doc-new-version. Findings → N-notes from N52; durable truth (job topology) → Doc impact one-liner extending the stack note.

## Verification

- `.venv/bin/python -m pytest` green (31 existing + new).
- `python -m mijual.scheduler once --offline` runs all four stages cleanly (0 requests / 0 calls) twice, idempotent.
- Live worker + beat demonstrated once with budget-capped stages; overlapping-run lock shown to hold (e.g. second trigger while first runs → skipped with a log line).
- `python3 scripts/workflow.py validate` passes.
