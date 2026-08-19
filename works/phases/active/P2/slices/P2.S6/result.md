# Result: P2.S6 — Celery beat scheduling of the collect / extract / gate pipeline

_Executed 2026-08-20 (KST) by `slice-executor-high`. Live spend: **62 OpenDART requests, 0 LLM
calls, ▷ $0.0000**._

## What landed

`src/mijual/scheduler/` — five modules, no state of its own, and deliberately Celery-free below the
task layer:

| module | what it is |
|---|---|
| `config.py` | `PipelineConfig` — the window and **every ceiling**, plus `window_for()` (KST-anchored, inclusive) |
| `locks.py` | `RedisLock` (`SET NX PX` + compare-and-delete), `FileLock` (single-host fallback), `NullLock`, `make_lock()` |
| `pipeline.py` | the four stages in order, one lock around the run, per-stage `StageResult` + `PipelineResult` |
| `app.py` | the Celery app, five tasks, `BEAT_SCHEDULE`, `describe_schedule()` |
| `__main__.py` | `once` (the inline runner) and `schedule` |

Celery only decides **when**. Everything a task does is one call to `run_pipeline()`, so the identical
code path runs from a worker, from `python -m mijual.scheduler once`, and from a test.

### The job topology

`collect → bodydoc → extract → gates`, in that order, because each stage consumes what the previous
one persisted (collection writes versions + 본문 snapshots → the 본문 layer parses them into hints,
labels and the ① 증서 verdict → extraction reads only 본문-confirmed events → the gate layer judges
only what extraction stored). Out of order it would not crash; it would silently gate yesterday's
corpus.

| task name | stage(s) | notes |
|---|---|---|
| `mijual.daily_pipeline` | all four | the scheduled job |
| `mijual.collect_recent` | collect | rolling window, discovery + pairing + detail + 본문 |
| `mijual.bodydoc_sync` | bodydoc | `<CORRECTION>` hint backfill + ① `18. 신주인수권양도여부` |
| `mijual.extract_new` | extract | prose fields of versions that have none yet + 정정 재추출 |
| `mijual.gates_run` | gates | re-derive every verdict + exposure. 0 requests, 0 calls |

### Beat schedule (timezone **Asia/Seoul**, `enable_utc = False`)

| entry | when (KST) | why that time |
|---|---|---|
| `daily-pipeline-morning` | 07:30 daily | before the market opens — the board is current for the day a 청약 deadline actually falls on |
| `daily-pipeline-evening` | 19:30 daily | after 공시 접수 closes (18:00) plus a margin — the day's filings and 정정 land the same evening |
| `weekly-resync` | Sunday 04:30 | 90-day straggler pass: corrections whose original sits outside the daily window, and pairings that only resolve once more filings exist |

Timezone is a decision, not a default: every date this product prints is a Korean calendar date, so
"07:30" must mean 07:30 KST on a worker running anywhere. `window_for()` is anchored on
`mijual.calc.today_kst`, not on the host clock, for the same reason.

`BEAT_SCHEDULE` is a plain dict — `P2.S7` adds `@app.task(name="mijual.collect_cb")` and one entry
beside these.

### Budgets (structural, defaults stated)

| knob | daily default | weekly | reaches |
|---|---|---|---|
| `collect_max_requests` | **500** | 1500 | `DartClient(max_requests=…)` |
| `collect_max_documents` | 150 | 400 | 본문 fetch cap inside collection |
| `bodydoc_max_requests` | **200** | 600 | `DartClient(max_requests=…)` |
| `bodydoc_max_documents` | 100 | 100 | live 본문 fetches per backfill pass |
| `extract_max_calls` | **60** | 60 | `GeminiClient(max_calls=…)`, **per run**, shared by the prose and 정정 passes |

Nothing new was invented for enforcement: both clients already refuse the next unit past the ceiling
(N25, N42) and both runners already catch that cleanly and keep what they collected. So a
budget-exhausted stage is a **reported status**, not an exception — demonstrated live below.

② is deliberately not in `extract_rights`: it needs zero LLM (N6), so a scheduled prose read of it
would be pure waste. `P2.S7` registers its own structured task.

### The lock

One lock, `mijual:lock:pipeline`, taken by **every** corpus-writing entry point (the pipeline task,
each stage task, and the inline `once`). Re-running a window is nearly free and duplicates nothing
(N14/N25) — repetition is safe. **Concurrency is not:** two overlapping runs both see "no 본문 held
for this version yet" and both fetch it, and spent quota is the one thing an idempotent upsert cannot
repair.

* `RedisLock` — `SET key token NX PX ttl`, released by **compare-and-delete**: a run that overran its
  TTL must not delete the lock its successor now holds (unit-tested against a fake client).
* `FileLock` — same contract on one host via `O_CREAT|O_EXCL`, for the inline path when no broker is
  running. An expired lock is stolen (a crashed run must not wedge the schedule forever) and the
  steal is reported in the run's notes.
* A run that cannot take the lock **returns `skipped`** — it does not wait and does not run anyway.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest -q` | **37 passed** (31 existing + 6 new in `tests/test_scheduler.py`) |
| `python3 scripts/workflow.py validate` | **Workflow validation passed.** |
| `.venv/bin/python -m mijual.scheduler once --offline` ×2 | 4/4 stages, **0 requests / 0 calls**, byte-identical stage lines |
| live worker + beat + two concurrent `daily_pipeline` | one ran, one **skipped on the lock** (0 requests) |
| `.venv/bin/python -m mijual.scheduler once --stages bodydoc --bodydoc-max-requests 3` | `BUDGET EXHAUSTED`, exit **0**, run continued |
| `.venv/bin/python -m mijual.scheduler schedule` | 3 entries, `Asia/Seoul`, all 5 task names resolve |

Tests are terse and touch no broker and no database: the window arithmetic, every beat entry
resolving to a registered task **with a ceiling** in its kwargs, both lock implementations' mutual
exclusion (including the late-release case), the skipped-on-lock run, and one stage's failure being a
reported status rather than a dead run.

### Offline, twice (deterministic evidence)

```
collect  : 20260806~20260820 | 0 list row(s) -> 0 target(s) | events 0 (live 0), versions 0 | 본문 +0
           | db (435, 1227, 2008)->(435, 1227, 2008) | 0 req | gaps 2
bodydoc  : 정정 403/803 parsed, hints 397, reattached 0, retired 0 | ① 본문 18. over 38 event(s)
           {'confirmed': 28, 'conflict': 1, 'denied': 9} | 본문 +0 | 0 req
extract  : [dry-run] r1_prose 28ev/0call; r3_prose 15ev/0call; 정정 R1 22ev/0call; 정정 R3 8ev/0call
           | 0 live call(s), 0 token(s), ▷ $0.0000
gates    : 435 event(s) judged, 304 field row(s) | passed 275 tbd 4 failed 5 n/a 20
           | exposable 35 event(s), 157 renderable field(s) | 철회 7 flagged event(s)
spend    : 0 OpenDART request(s), 0 LLM call(s), ▷ $0.0000 estimated | 4.4s total
```

(Regenerated from the final corpus state into `var/s6-pipeline-final.json` — gitignored, N8's rule:
the numbers quoted above come from the last run, not from an earlier open one.)

`gaps 2` is honest, not a failure: the rolling window is not in the response cache, so offline
discovery reports the two chunks it could not read instead of pretending the window was empty. Point
the run at a cached window (`--bgn 20260101 --end 20260331 --cache-dir scripts/spike/samples`) for a
non-empty offline collection.

Offline `extract` builds every prompt and sends none (`dry_run`), and reports **0 calls** rather than
the planned count — money is counted from the client's ledger, never from a report's own tally.

### Live: worker + beat + the lock

```
$ docker compose --profile scheduling up -d redis           # host 6380
$ .venv/bin/celery -A mijual.scheduler.app worker -l info -c 2   # -c 2 only to force the overlap
[tasks] mijual.bodydoc_sync mijual.collect_recent mijual.daily_pipeline mijual.extract_new mijual.gates_run

# two daily_pipeline tasks sent back to back, window 3d, collect<=120 req, bodydoc<=40 req, extract<=6 calls
ForkPoolWorker-1  pipeline : live-b 20260817~20260820 lock=redis SKIPPED (lock held)   # 0 req, 0 calls
ForkPoolWorker-2  collect  : 20260817~20260820 | 54 list row(s) -> 23 target(s) | events 19 (live 1),
                             versions 23 | db (434,1226,1963)->(435,1227,1965) | 19 req [4.6s]
ForkPoolWorker-2  bodydoc  : 정정 400/803 parsed, hints 394 | ① 본문 18. over 38 event(s)
                             {'confirmed': 28, 'conflict': 1, 'denied': 9} | 본문 +40 | 40 req [10.5s]
ForkPoolWorker-2  extract  : r1_prose 28ev/0call; r3_prose 15ev/0call; 정정 R1 22ev/0call;
                             정정 R3 8ev/0call | 0 live call(s), ▷ $0.0000 [0.4s]
ForkPoolWorker-2  gates    : 435 event(s) judged, 304 field row(s) | passed 275 tbd 4 failed 5 n/a 20
                             | exposable 35 event(s), 157 renderable field(s) [8.1s]
```

`live-b`'s returned record: `"skipped": true, "requests": 0, "calls": 0,
"notes": ["another run holds redis lock 'pipeline' — this run did nothing"]`.

Beat was then run against an **isolated** demo entry (a 20-second `mijual.gates_run`) so the demo
could not fire a real daily job at an unplanned budget; it dispatched on schedule and the worker
executed and returned the JSON record each time:

```
beat   : Scheduler: Sending due task demo-gates-every-20s (mijual.gates_run)   ×3
worker : Task mijual.gates_run[…] succeeded in 2.79s: {'label': 'beat-demo', …, 'ok': True,
         'requests': 0, 'calls': 0, 'cost_usd': 0.0, …}
```

A budget-exhausted stage, live and deliberate:

```
$ .venv/bin/python -m mijual.scheduler once --stages bodydoc --bodydoc-max-requests 3
bodydoc  : 정정 319/803 parsed … | 본문 +3 | 3 req — BUDGET EXHAUSTED   ← exit code 0
```

The run then finished with an offline pass (N34's rule, now one command) and converged.

### What the live run changed in the corpus

| | before S6 | after |
|---|---|---|
| events / versions / snapshots | 434 / 1226 / 1963 | **435 / 1227 / 2008** |
| 정정 본문 parsed | 360 / 803 | **403 / 803** |
| 철회-flagged events | 5 (4 distinct filings) | **7 (6 distinct filings)** |
| exposable events | 35 (① 25, ③ 10) | **35 (unchanged)** |
| renderable field instances | 157 | **157 (unchanged)** |
| field verdicts | 275 passed / 4 tbd / 5 failed / 20 n/a | **unchanged** |

The two newly detected withdrawals — 베노티앤알 `20260211001005` and 앱튼 `20260213002873` — both sit
on `unpaired_correction` placeholders, so nothing exposable moved. They are new because the
scheduled 본문 backfill fetched their documents, not because the detector changed (see N55).

## Ops runbook

```bash
docker compose up -d postgres                          # corpus, host 5433
docker compose --profile scheduling up -d redis        # broker + backend + lock, host 6380

.venv/bin/celery -A mijual.scheduler.app worker -l info -c 1
.venv/bin/celery -A mijual.scheduler.app beat   -l info -s var/celerybeat-schedule

.venv/bin/python -m mijual.scheduler schedule          # what beat will do
.venv/bin/python -m mijual.scheduler once --window 14  # ops fallback: no broker needed
.venv/bin/python -m mijual.scheduler once --offline    # $0 / 0 requests, safe anywhere
```

* `-c 1` is the honest concurrency — a second slot would only take the lock and skip.
* `-s var/celerybeat-schedule` keeps beat's shelve DB out of the repo root (`var/` is gitignored;
  `celerybeat-schedule*` is now ignored too, after beat dropped one there during this slice).
* No broker running? `once` degrades the lock to a single-host file lock under `var/locks/` and says
  so in the run's `lock=` field, rather than pretending to be distributed.
* **Serving stays decoupled (hard rule).** Nothing in `mijual.scheduler` is importable from a request
  path, no task returns anything a page renders, and every stage's output is persisted rows. P3 reads
  those rows: a worker that never runs leaves the board **stale, never dark** — the 결격 rule read
  from the scheduling side. The board's exposure filter is `Event.exposure_state` (N48), refreshed by
  the `gates` stage, so a stalled scheduler cannot leak an ungated field either.
* **Secrets:** no key is echoed, logged, written to a run report, or used as a cache filename.
  `Settings.__repr__` masks, and a grep for each of the two key values across the new package, the
  tests, the JSON run reports and the worker log returned **0 files**.

## Deviations from `plan.md`

1. **`daily_pipeline` orders the four stages in-process rather than as a Celery `chain`.** One lock
   has to span the whole run, and a chain's links are separate tasks that could interleave with
   another run's links — the exact double-fetch the lock exists to prevent. Ordering here is a data
   dependency, not parallelism, so a chain would have bought nothing and cost correctness. Each stage
   is still separately callable as its own task (`collect_recent`, `bodydoc_sync`, `extract_new`,
   `gates_run`), which is what the plan wanted the chain for.
2. **The 본문 stage fetches from cache even in `--offline` mode.** `fetch=True` is passed regardless;
   the *client* decides, and an offline client resolves a 본문 from the on-disk response cache and
   reports a genuine miss as *missing*, never as an error. This makes N34's "finish a budget-capped
   live run with an offline pass" a property of the pipeline rather than a habit.
3. **`extract` also runs the 정정 재추출 pass** (§7 #10) under the same call ceiling, because a
   scheduled run that collects a new 정정 but never interprets it would leave the product's headline
   feature stale. Off with `--no-corrections`.
4. **Two small additions** the plan did not name: `PipelineConfig.lock_dir` (so the file-lock
   fallback is testable and multi-checkout-safe) and `--bgn/--end` on `once` (so an offline run can
   be pointed at a window the response cache actually holds).

Not deviations, but worth stating: the beat demo used an isolated 20-second entry rather than waiting
for 07:30 KST, and `-c 2` was used only to force the overlap the plan asked to be demonstrated.

## Doc impact recorded (in `phase.md`, not versioned here)

One entry extending the running architecture/operations note: the job topology, the beat schedule and
its timezone, the per-stage ceilings, the single run lock, and the restatement that **nothing in the
scheduler is in a request path**.

## Findings appended to `phase.md`

**N52** (job topology + task names + schedule), **N53** (the lock, and why overlap — not repetition —
is the failure mode), **N54** (measured steady-state cost of a scheduled run: the 본문 backfill is the
only stage that keeps spending), **N55** (the 철회 count is a function of documents held, 4 → 6), and
**N56** (`once` as the reusable inline path for `P2.S7`/`P2.S8` and the ops fallback).

## Left running

`mijual-redis` (compose `scheduling` profile, host 6380) is up; the worker and beat processes started
for the evidence run were stopped, no `mijual:*` keys remain in Redis, and no stray beat state file is
left in the repo. Stop the broker with `docker compose --profile scheduling stop redis`.
