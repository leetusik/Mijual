# P4.F4 — result (both dispatches; the slice is complete)

- **status**: `done`
- **summary**: `MIJUAL_EXTRACT_MAX_CALLS` is now live on production at **300**. Dispatch 1 landed the
  knob (`Settings` → `PipelineConfig.from_kwargs()` for every beat run → `once --max-calls` as the
  per-run override), one test, `.env.prod.example` and the box's `.env.prod` line; dispatch 2
  released `origin/main` `1a93d7b` with `deploy/deploy.sh` (log
  `var/deploy-20260902T152615.log`, ~90 s, `mijual-api` rebuilt `caac2ad1e440`→`e0a479095f7b`,
  `mijual-web` a full cache hit, schema one-shot exit 0, both health gates on poll 1, the four R7
  no-harm assertions identical before and after) and ran the first drain: **34 of 300 calls,
  312,553 tokens, $0.3920, 205.8 s, no `BUDGET EXHAUSTED`** — the 정정 backlog that exhausted the
  60-call ceiling the night before is drained with the ceiling never approached.
- **files_changed** (dispatch 2 touched no code):
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/slices/P4.F4/result.md`
  - dispatch 1's six repo files are listed under `## Dispatch 1` below
  - (on the box, not in the repo) `/home/opc/Mijual` checked out `96f7141`→`1a93d7b` by
    `deploy.sh`; new logs `var/deploy-20260902T152615.log` and `var/f4-drain-20260902T152910.log`
- **validation**: dispatch 1 — `uv run pytest -q` **167 passed**, the offline `extract<=300 calls`
  proof, `workflow.py validate` (table in `### Validation`). Dispatch 2 — `git rev-parse origin/main
  main` both `1a93d7b`; celery `inspect active` empty before deploying; the R7 four ×2 (before/after,
  all identical); `deploy.sh` `DONE — released at ref origin/main`; `printenv
  MIJUAL_EXTRACT_MAX_CALLS` = **300** in worker/api/beat; the drain's own `budgets` line
  `extract<=300 calls` and its run row's `max_calls: 300`; `docker compose ps` six up +
  `mijual-schema` `exited exit=0`; `curl /api/health` ok; **`make smoke-prod` 17/17 twice** (after
  the deploy, and again after the drain); `python3 scripts/workflow.py validate` passed.
- **deviations**: four in dispatch 2 (§ *Dispatch 2 · Deviations*), three in dispatch 1
  (§ *Dispatch 1 · Deviations*). The load-bearing one: **`/ops` was not logged into** — the
  `f4-drain` row was read from the panel's own source (`pipeline_run` id 45) instead of minting a
  production ops session from an agent.
- **doc_impact**: dispatch 1's two lines (`operations` Environment Variables, `backend` Background
  Jobs) plus **one new `operations` line** for this release — log path, image ids, `:previous` = the
  `96f7141` api image while the web half is a **no-op**, the `.env.prod` edit recreating every
  `env_file` service including **postgres**, and the four assertions holding.
- **operator_need**: none blocking. Two things for the gate/re-review: the `/ops` 개요 render of the
  `f4-drain` run row is the operator's to eyeball, and the ceiling's remaining half — the D-4
  thinking-*level* question — stays open as deferred `D40`.

---

## Dispatch 1 — the knob, its docs, the box value

_Verdict at the time: `needs_operator` (the push gate). The block and body below are dispatch 1's own,
unchanged; only heading levels were demoted one step to nest under this section._


- **status**: `needs_operator`
- **summary**: Added the `MIJUAL_EXTRACT_MAX_CALLS` env knob — read by `Settings`, applied to every
  beat/Celery run through `PipelineConfig.from_kwargs()` and to `once` unless `--max-calls` is typed,
  with the dataclass default unchanged at 60 — plus one test, the `.env.prod.example` entry, and the
  single `MIJUAL_EXTRACT_MAX_CALLS=300` line appended to `/home/opc/Mijual/.env.prod` (mode 600
  preserved, inert until the containers are recreated). Nothing was deployed and nothing on the box
  was restarted. The slice now stops for the operator's `git push origin main`; dispatch 2 deploys
  and drains.
- **files_changed**:
  - `/Users/sugang/projects/personal/Mijual/src/mijual/config.py`
  - `/Users/sugang/projects/personal/Mijual/src/mijual/scheduler/config.py`
  - `/Users/sugang/projects/personal/Mijual/src/mijual/scheduler/__main__.py`
  - `/Users/sugang/projects/personal/Mijual/tests/test_scheduler.py`
  - `/Users/sugang/projects/personal/Mijual/.env.prod.example`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/slices/P4.F4/result.md`
  - (on the box, not in the repo) `/home/opc/Mijual/.env.prod` — three appended lines
- **validation**: see § *Validation* — `uv run pytest -q` **167 passed, exit 0**;
  `python3 -m py_compile` on the four touched files clean; `once --help` shows the new default
  wording; the offline proof run prints `extract<=300 calls`; `python3 scripts/workflow.py validate`
  passed; `git diff --stat` is exactly the six repo files above.
- **deviations**: three, all small — see § *Deviations*.
- **doc_impact**: two lines appended to `phase.md`'s `## Doc impact` —
  `operations` (Environment Variables: the new key, default 60, production 300, the ~$3 bound, and
  that a malformed value is fatal rather than ignored) and `backend` (Background Jobs: the extract
  ceiling is env-overridable, all three beat entries inherit it through `from_kwargs`,
  `once --max-calls` wins per run, `DEFAULT_EXTRACT_MAX_CALLS` / `env_extract_max_calls()`).
- **operator_need**: **push `main` to GitHub — `git push origin main`** (after the orchestrator
  commits this slice). The box deploys `origin/main`, and neither the orchestrator nor an executor
  pushes. Dispatch 2 then runs `deploy/deploy.sh` on the box and a first drain run. **It must land
  before the deploy freeze opens 2026-09-07 11:00 KST.**

---

### What changed, and why there

The ceiling was `PipelineConfig.extract_max_calls = 60`, a dataclass default no env var could reach.
Three edits, smallest coherent diff:

1. **`src/mijual/config.py`** — `Settings.extract_max_calls: int | None = None`, read in
   `load_settings()` through the existing `pick()` (environment first, then the repo-root `.env`) and
   parsed by a new `_positive_int(name, raw)` helper. The helper raises `ValueError` naming **the key
   and never the value**, and deliberately does not chain the built-in `int()` error, because that
   one quotes the offending literal.
2. **`src/mijual/scheduler/config.py`** — the literal `60` became `DEFAULT_EXTRACT_MAX_CALLS` (same
   value, one spelling), and a new `env_extract_max_calls()` is **the one reader** both consumers
   use. `PipelineConfig.from_kwargs()` applies it when the kwargs carry no `extract_max_calls` key —
   that is the beat/Celery path, and no beat entry names a ceiling — so all three `daily_pipeline`
   entries (07:30, 19:30, Sun 04:30) inherit it while an entry that names one keeps it.
3. **`src/mijual/scheduler/__main__.py`** — `--max-calls` now defaults to `None` (so "typed 60" and
   "typed nothing" are distinguishable) and `_config()` resolves
   `--max-calls` → `$MIJUAL_EXTRACT_MAX_CALLS` → `60`. Help text updated.

The dataclass default stays **60**, so offline tests, fixtures and the module's own reasoning are
unaffected by the environment; unset behaves exactly as it did yesterday.

#### The one deliberate departure from this codebase's convention

`MIJUAL_STALE_AFTER_HOURS` and `SMTP_PORT` both **ignore** a malformed value, with the reason in a
comment ("a mistyped ops env var must not take the board down"). This key does not: it raises. The
plan asked for that, and it is right for this key specifically — it is a **spend ceiling**, and
falling back to 60 would run a whole schedule at a budget the operator believes they raised. The
blast radius is accepted knowingly and recorded in `phase.md`'s `## Decisions`: a bad value stops
api/worker/beat at startup, which `deploy/deploy.sh`'s health gate turns into an automatic rollback.
An **empty** value is "unset" (that is `pick()`'s rule for every key), not an error — measured below.

### Validation

| Command | Outcome |
|---|---|
| `python3 -m py_compile src/mijual/config.py src/mijual/scheduler/config.py src/mijual/scheduler/__main__.py tests/test_scheduler.py` | clean |
| `uv run pytest -q` | **167 passed**, exit 0 (72+72+23), no `--with` |
| `uv run python -m mijual.scheduler once --help` | `--max-calls` reads *"LLM call ceiling for the run (default: $MIJUAL_EXTRACT_MAX_CALLS if the environment sets one, else 60); an explicit value here wins over the environment"* |
| `MIJUAL_EXTRACT_MAX_CALLS=300 uv run python -m mijual.scheduler once --offline --stages extract --window 14 --label f4-proof --no-run-log --no-lock` | `config : … budgets collect<=500 req, bodydoc<=200 req, **extract<=300 calls** [offline]`, `spend : 0 OpenDART request(s), **0 LLM call(s)**, ▷ $0.0000` |
| `python3 scripts/workflow.py validate` | passed (one pre-existing `oversized_doc_sections=11` warning, not this slice's) |
| `git diff --stat` | the three source files, the test file, `.env.prod.example`, `phase.md` — nothing else |
| `ssh oracle-cloud` verification (below) | `grep -c` = 1, `stat -c %a` = 600 |

#### The env matrix, probed directly

Run under `MIJUAL_ROOT` pointed at an empty scratch dir so no repo-root `.env` could interfere:

```
unset    -> 60          # unchanged behaviour
"300"    -> 300         # the beat path takes it
explicit -> 5           # from_kwargs(extract_max_calls=5) keeps 5
"6O" / "0" / "-5" / "60.5" -> ValueError: MIJUAL_EXTRACT_MAX_CALLS must be a positive integer (>= 1)
                          (the offending value appears nowhere in the message)
""       -> 60          # empty == unset, per pick(); not an error
```

#### What the dry run says the backlog costs

The offline proof run's extract line is itself evidence for the value 300:

```
extract : [dry-run] label 61row/0call; r1_prose 54ev/0call; r3_prose 18ev/0call;
          정정 R1 50ev/59call; 정정 R3 13ev/10call | 0 live call(s), 0 token(s), ▷ $0.0000
```

**69 정정 calls** (59 + 10) in a 14-day window on the dev corpus — the same number `D40` was filed
with, and above the old 60-call ceiling on its own. 300 is ~4× that, so a run drains rather than
carries, and it bounds one run at roughly $3 (the exhausted 60-call production run cost $0.61 /
466,729 tokens).

### The box

One `ssh oracle-cloud` invocation, additive only, nothing else touched — no `docker` command, no
restart, no deploy, `edge-nginx` never approached, and the file was never `cat`'d:

```
printf '\n# extract ceiling per run (P4.F4, operator 2026-09-02)\nMIJUAL_EXTRACT_MAX_CALLS=300\n' \
  >> /home/opc/Mijual/.env.prod
```

Before: mode `600 opc:opc`, `grep -c '^MIJUAL_EXTRACT_MAX_CALLS='` = **0**, 131 lines.
After: mode `600 opc:opc` (unchanged), `grep -c` = **1** at line **134**, 134 lines (+3: blank,
comment, key). The value is **inert** until the containers are recreated — a running container keeps
the environment it started with — which is dispatch 2's deploy.

### Deviations

1. **The offline proof run added `--no-run-log --no-lock`** to the plan's command. The plan's exact
   form would have written a `pipeline_run` row into the operator's **dev** run log and taken the
   real lock for a slice-internal proof. The flags change nothing about what was being proven (the
   `budgets` line comes from `PipelineConfig.describe()` either way) and leave the dev log untouched.
2. **`DEFAULT_EXTRACT_MAX_CALLS` and `env_extract_max_calls()` were added** rather than repeating the
   literal `60` and the `load_settings()` call in two files. The plan named the two application
   points but not how they share a spelling; one constant and one reader is what keeps the beat path
   and the CLI from ever disagreeing about which value wins.
3. **`.env.prod.example`'s *Optional* block header** said "Both have working defaults" and now says
   "All three" — a one-word correction forced by adding a third key to that block.

Not a deviation but worth stating: the plan's step 5 asked for the D-4 thinking-*level* question to
stay open as `D40`. It is open and untouched; `phase.md`'s `## Operator Questions` records that its
**trigger has fired** and that this slice answers only the ceiling half.

### What dispatch 2 inherits

In `phase.md` under `## Notes for later slices` (**(from P4.F4 dispatch 1, for P4.F4 dispatch 2)**):
the box line is already written and must not be appended twice; both images will genuinely rebuild
because `src/` changed; verify with `printenv` **and** the drain run's `extract<=300 calls` line
(only the second proves the code path took it); expect a low-single-dollar drain; and if it still
reports `BUDGET EXHAUSTED` at 300, report it and stop — the next value is the operator's.

---

## Dispatch 2 — the deploy and the first drain

### 1. Preconditions, all met

| check | reading |
|---|---|
| `git fetch origin && git rev-parse origin/main main HEAD` | all three **`1a93d7b`** (carries dispatch 1's `391cdf0`) |
| box HEAD before | `96f7141`, clean tree — exactly what `deploy.sh`'s `REF=origin/main` expects |
| beat run in flight | `celery -A mijual.scheduler.app inspect active` → `- empty -`, 1 node online |
| next beat window | `daily-pipeline-morning` 07:30 KST = 22:30 GMT — **7 hours** after this deploy |
| deploy freeze | opens 2026-09-07 11:00 KST; this landed **2026-09-03 00:26 KST**, four days early |

**The four R7 no-harm assertions, before** (2026-09-03 00:25 KST / 15:25Z):
`hi2vi.com` · `vocky.hi2vi.com` · `changple.ai` **200 ×3**; `edge-nginx` `StartedAt`
**`2026-07-02T19:22:12.325478595Z`**; `:80`/`:443` owned by **`edge-nginx`**
(`0.0.0.0:80->80, :::80->80, 0.0.0.0:443->443, :::443->443`); **28 containers** (22 co-tenants + 6
Mijual), `changple_shared_network` **17 members**; the sorted `docker ps` status list recorded
(22 co-tenant containers, all `Up … (healthy)` except `vocky-worker`, which carries no healthcheck).

### 2. The deploy

```sh
ssh oracle-cloud 'cd /home/opc/Mijual && nohup deploy/deploy.sh > var/deploy-20260902T152615.log 2>&1 < /dev/null &'
# launched pid=1880019
```

Log `/home/opc/Mijual/var/deploy-20260902T152615.log`, **242 lines**, done in ~90 s:

| step | evidence (line) |
|---|---|
| baseline captured | `edge-nginx StartedAt before: 2026-07-02T19:22:12.325478595Z` (1) |
| checkout | `96f7141..1a93d7b  main -> origin/main`; `HEAD is now at 1a93d7b` (4–7) |
| rollback points | `tagging mijual-api:latest -> mijual-api:previous` (8), `… mijual-web …` (9) |
| both images built | `naming to docker.io/library/mijual-web:latest done` (111), `… mijual-api:latest done` (170) |
| schema one-shot | `mijual-mijual-schema-1 Exited`; `docker inspect` → **`exited exit=0`** |
| health gate | `mijual-web healthy on poll 1` (214), `mijual-api healthy on poll 1` (215) |
| verdict | `deploy healthy — mijual-api:latest + mijual-web:latest are live` (216) |
| worker | `not gated, reported: mijual-worker = starting` (217) — `healthy` at the next check |
| edge assertion | `ok — edge-nginx StartedAt unchanged (2026-07-02T19:22:12.325478595Z)` (241) |
| final | `DONE — released at ref origin/main` (242) |

**Image ids — and the rollback point moved on one half only:**

```
mijual-api:latest   caac2ad1e440  ->  e0a479095f7b      mijual-api:previous   caac2ad1e440
mijual-web:latest   b82aaa9c5b20  ->  b82aaa9c5b20      mijual-web:previous   b82aaa9c5b20
```

`src/` changed, so the api image genuinely rebuilt; **`frontend/` did not change between `96f7141`
and `1a93d7b`**, so `mijual-web` was a full build-cache hit and the running web container was left
alone (`Running`, uptime 7 h — never recreated, so the site never blinked). The consequence is the
**mirror image of `P4.S6`'s release**: `mijual-api:previous` is a real rollback point (the `96f7141`
api image), while the **web half of a `rollback.sh` flip is a no-op** for this release.

**Unexpected and worth carrying: `mijual-postgres` was recreated, though its image never moved.**
The `up` section reads `postgres Recreate → Recreated`, then `schema`, `worker`, `api`, `beat`
recreated, `web` and `redis` `Running`. The cause is dispatch 1's own `.env.prod` append: compose
hashes the `env_file` into a service's config, so **every service carrying `env_file: .env.prod`**
— api, worker, beat, the schema one-shot **and postgres** — was recreated, while `redis` and `web`
(which carry no `env_file`; the web container holds no secret by design) were not. Data is on the
named pgdata volume and survived, verified read-only afterwards:

```
19 tables · event 1411 · account 2 · pipeline_run 44        (the seed was 19 · 1359 · 2 · 21)
```

— growth from the beat runs since 09-02, nothing truncated. The practical rule this earns: **an
`.env.prod` edit costs a postgres recreate at the next deploy** (a few seconds of DB downtime while
`mijual-web` keeps serving), which is worth knowing before a deploy inside any sensitive window.

Post-deploy the API still announces
`mail transport: smtp mail.privateemail.com:587 tls=starttls from=주주의관제탑 <hi@hi2vi.com>`.

### 3. The knob, verified twice

```
docker compose -f compose.prod.yml exec -T {mijual-worker,mijual-api,mijual-beat} \
    printenv MIJUAL_EXTRACT_MAX_CALLS      ->  300   300   300
```

and — the half that proves the **code path** took it, not just the container environment — the drain
run's own config line:

```
config    : window 20260820~20260903 (14d) stages=extract budgets collect<=500 req, bodydoc<=200 req, extract<=300 calls
```

with `max_calls: 300` recorded inside the run row's `stages` JSON as well.

### 4. The drain

```sh
ssh oracle-cloud 'cd /home/opc/Mijual && nohup docker compose -f compose.prod.yml exec -T mijual-worker \
  python -m mijual.scheduler once --stages extract --label f4-drain --trigger operator \
  > var/f4-drain-20260902T152910.log 2>&1 < /dev/null &'
```

Log `/home/opc/Mijual/var/f4-drain-20260902T152910.log`; it took the normal `redis` lock, so no beat
run could overlap it.

```
extract  : label 67row/0call; r1_prose 57ev/0call; r3_prose 21ev/0call;
           정정 R1 53ev/23call; 정정 R3 13ev/11call | 34 live call(s), 312,553 token(s), ▷ $0.3920 [205.6s]
spend    : 0 OpenDART request(s), 34 LLM call(s), ▷ $0.3920 estimated  |  205.8s total
```

| number | value |
|---|---|
| calls used | **34 of 300** (11 % of the ceiling) |
| tokens | 312,553 |
| cost | **$0.3920** estimated |
| wall time | 205.8 s |
| `BUDGET EXHAUSTED` | **no** — the string does not occur in the log at all |
| rows / events touched | label_fields 67 rows / 21 events (`appraisal_price` extracted **and** verified ×52, absent 15); 정정 R1 53 events / 23 calls / 39 versions skipped as already processed; 정정 R3 13 events / 11 calls / 7 skipped |
| run row | `pipeline_run` **id 45** — `label f4-drain`, `trigger operator`, `ok t`, `lock redis`, `seconds 205.85`, `calls 34`, `cost_usd 0.391996`, `config_line … extract<=300 calls` |

**Why 34 and not the 69 dispatch 1 priced.** That 69 was a *dev-corpus* 14-day dry run. On
production the 19:30 run the night before had already spent its whole 60-call ceiling on this same
backlog, and 46 of the versions this run looked at (39 R1 + 7 R3) were skipped as already processed.
The point the number makes is the one that matters: **at 300 the run drained rather than carried**,
and it did so with 266 calls of headroom, so the value is comfortable rather than marginal.

### 5. After

- **The four R7 assertions again** (00:43 KST): co-tenants **200 ×3**; `edge-nginx` `StartedAt`
  **identical**; `:80`/`:443` still `edge-nginx`; **28 containers / 6 Mijual**, network **17**. Nothing
  outside the `mijual` compose project was addressed and `edge-nginx` was never named by any command
  but `docker inspect`.
- `docker compose -f compose.prod.yml ps` — six services up: api/worker/beat `Up 16 minutes`
  (recreated, api + worker `healthy`), postgres `Up 17 minutes (healthy)`, redis `Up 14 hours`, web
  `Up 7 hours (healthy)`; `mijual-schema` `exited exit=0`.
- `curl -s https://jujutower.com/api/health` → `{"status":"ok","version":"0.1.0","now_kst":"2026-09-03T00:43:34+09:00"}`
- **`make smoke-prod` — 17 pass · 0 fail, twice**: 11.2 s right after the deploy and 14.2 s after the
  drain. `www` **passed both times** — `P4.F1`'s Tailscale-resolver false FAIL did not recur from this
  machine tonight, which is worth recording because it makes that finding intermittent, not constant.
  Two numbers moved with the corpus, not with a regression: `board 393 rows` (was 375) and
  `sitemap 830 URLs (464 events)` (was 800 / 445).

### Deviations

1. **One aborted launch, nothing ran.** The first deploy attempt wrapped the `ssh` in a local
   `timeout 60` — macOS has no `timeout`, so the call died `exit 127` and the box never heard from
   it. Verified before relaunching: the log file did not exist and no `deploy.sh` process was
   running. The real launch is the one recorded above; there was no double deploy.
2. **The `P4.F1` ssh quirk recurred, on the drain launch only.** That local `ssh` was killed by the
   harness's 2-minute Bash timeout (exit 143) after the remote `nohup` had already started; pid
   1888525 was confirmed alive with the log growing, **nothing was relaunched**, and the run was
   polled to its own final line. The deploy launch itself returned cleanly.
3. **`/ops` was not logged into.** The plan asked to see the `f4-drain` row in the panel. An ops
   login is a `POST` that mints an `OpsSession` **row in the production database** and would put the
   operator's credential into an agent-driven request, so the same evidence was taken read-only from
   the panel's own source — `pipeline_run` id 45, quoted in § 4 — and the door itself is covered by
   the smoke suite's `ops-door` check (200, 운영자 ID present, none of D15's four rule lines). Seeing
   the row rendered is left to the operator at the gate.
4. **Two read-only `psql` queries the plan did not list** (schema/row counts, and the run row). The
   postgres recreate above is why: a container that was not supposed to be recreated came back, and
   "the data is fine" deserved a measurement rather than an assumption.

### What this dispatch did not do

- **No code changed.** `git diff --stat` is `phase.md` and this `result.md` only.
- **No commit, no push, no workflow state command** other than `python3 scripts/workflow.py validate`.
- **No hand edit on the box** — `deploy/deploy.sh` did all of it; `.env.prod` was not touched again
  (dispatch 1 had already written the one line), never `cat`'d, and no secret value appears anywhere
  in this file or in any transcript. `printenv` of the one non-secret key is the only env read.
- **No model spend beyond the drain's own 34 extract calls** ($0.3920).
- **The D-day gate demo mail is still not sent** — unchanged by this slice, still the operator's one
  action.
