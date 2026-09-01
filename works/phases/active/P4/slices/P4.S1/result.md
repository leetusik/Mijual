# P4.S1 — result

- **verdict:** `done`
- **summary:** The product is a Docker Compose co-tenant stack: one Python image (`Dockerfile.api`)
  running the API, the Celery worker, beat and an idempotent schema one-shot; one Next image
  (`frontend/Dockerfile`, `output: "standalone"`) that is the only container the edge ever sees;
  Postgres + Redis as internal services on named volumes; a pinned `uv.lock`; and a committed
  `.env.prod.example`. Proven end-to-end in an isolated local smoke (`-p mijual-smoke` on a
  throwaway network, torn down with `down -v`) — all six services healthy, **18 tables**,
  `/api/health` answered through the Next rewrite from the edge network while the API stayed
  unresolvable from it. Nothing touched the operator's running dev stack, the box, or any co-tenant.
- **files_changed:**
  - new: `uv.lock`, `.python-version`, `Dockerfile.api`, `.dockerignore`, `compose.prod.yml`,
    `.env.prod.example`, `frontend/Dockerfile`, `frontend/.dockerignore`,
    `src/mijual/web/__main__.py`, `src/mijual/db/__main__.py`
  - edited: `.gitignore` (`!.env.prod.example`), `Makefile` (`db-ensure` delegates),
    `frontend/next.config.ts` (`output: "standalone"`), `src/mijual/web/opsreads.py`
    (`DECISIONS_DOC` resolves in an installed package too), `works/phases/active/P4/phase.md`,
    this file
- **validation:** see *Commands run* below. All green.
- **deviations:** four, all recorded under *Deviations* below (the local `next build` was run on an
  APFS clone of `frontend/` instead of in place; `make api-up` was **not** repointed; `.dockerignore`
  keeps two paths the plan proposed excluding; worker/beat/schema override the inherited HEALTHCHECK).
- **doc_impact:** five lines appended to `phase.md` § *Doc impact*, tagged `(P4.S1)` —
  `operations`, `architecture`, `backend`, `frontend`, `security`.
- **escalation:** none

---

## Commands run

### 1. Repo checks

| Command | Outcome |
|---|---|
| `.venv/bin/python -m pytest` | **158 passed**, 1 warning, 3.46 s (the plan said 142; the suite has grown since) |
| `cd frontend && npm run typecheck` | pass (`tsc --noEmit`, silent) |
| `cd frontend && npm run smoke` | **22 pass / 0 fail**, 191 ms |
| `npm run build` (isolated clone — see *Deviations*) | pass, 18 routes, `.next/standalone/server.js` emitted |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` (pre-existing `oversized_doc_sections=11` warning only) |
| `uv lock --check` | pass — the lock is reproducible |

The isolated build also proved the build-time seam directly: `MIJUAL_API_ORIGIN=http://mijual-api:8010`
appears baked in `.next/standalone/.next/routes-manifest.json` and `required-server-files.json`.
That is why the frontend needs the value **twice** (build arg *and* runtime env) and why the
Dockerfile asserts the arg non-empty.

### 2. Lock sanity — locked vs. the pip-installed pins

| Package | pip freeze (dev `.venv`) | `uv.lock` |
|---|---|---|
| fastapi | 0.141.1 | 0.141.1 |
| starlette | 1.6.0 | 1.6.0 |
| uvicorn | 0.52.4 | 0.52.4 |
| SQLAlchemy | 2.0.52 | 2.0.52 |
| celery | 5.6.3 | 5.6.3 |
| redis | 8.1.0 | 8.1.0 |
| httpx | 0.28.1 | 0.28.1 |
| psycopg / psycopg-binary | 3.3.4 | **3.3.5** (patch) |
| google-genai | 2.18.1 | **2.21.0** (minor) |

56 packages resolved. Same major lines throughout; the two drifts are a patch and a minor within
the ranges `pyproject.toml` already declares, so **no range was pinned or bumped** — no operator
question needed. The image runs the *locked* set and the suite is green against the *installed*
set; the container additionally imported and served cleanly on the locked set (below). The dev
`.venv` was **not** replaced — the dev workflow stays pip/`make`.

### 3. Images

`COMPOSE_BAKE=false docker compose -f compose.prod.yml build` — both built, `linux/arm64`
(Docker Desktop server arch, the same as the OCI box, so this is a real rehearsal).

| Image | Size |
|---|---|
| `mijual-api:latest` | **399 MB** |
| `mijual-web:latest` | **443 MB** |

`mijual-api` runtime layout is `/app/{.venv,evalset,docs,var}` on Python 3.13.15, user
`uid=10001(mijual)`.

### 4. The isolated smoke stack

Setup: `docker network create mijual-edge-smoke`; a throwaway `.env.prod` (confirmed ignored —
`git check-ignore -v .env.prod` → `.gitignore:3:.env.*`, and `git status --ignored` listed it as
`!!`) with dummy values, no real DART/Gemini/vocky credential; then
`MIJUAL_EDGE_NETWORK=mijual-edge-smoke docker compose -f compose.prod.yml -p mijual-smoke up -d`.

**Services** (`docker compose -p mijual-smoke ps`, after the corrected healthchecks):

```
mijual-api       running   Up 2 minutes (healthy)
mijual-beat      running   Up 20 seconds
mijual-postgres  running   Up 2 minutes (healthy)
mijual-redis     running   Up 2 minutes (healthy)
mijual-web       running   Up 2 minutes (healthy)
mijual-worker    running   Up 20 seconds (healthy)
```

`mijual-schema` **exited 0**, log: `schema ok`. The dependency chain ordered itself with no sleeps:
postgres healthy → schema completed → api → web healthy.

**18 tables** (`psql -c "\dt"`, and `count(*) from information_schema.tables` = **18**), including
both of the tables whose absence silently breaks every `/ask` turn:

```
account · auth_session · conversation_feedback · conversation_turn · corp · event ·
extraction · extraction_call · filing_version · holding · lapse_claim · notification_pref ·
offering_input · ops_session · password_reset · performance_report · pipeline_run · snapshot
```

**The edge path — exactly what nginx will take**, from a scratch container on the edge network only:

```
$ docker run --rm --network mijual-edge-smoke curlimages/curl -s http://mijual-web:3010/api/health
{"status":"ok","version":"0.1.0","now_kst":"2026-09-02T07:25:48+09:00"}

$ ... http://mijual-web:3010/      → status=200, 133,700 bytes, contains `<html lang="ko"` and 주주의관제탑
```

**And the API is not on that path** (the isolation this stack's whole shape depends on):

```
from mijual-edge-smoke : curl: (6) Could not resolve host: mijual-api
from mijual-smoke_default : {"status":"ok","version":"0.1.0","now_kst":"..."}
```

Attachments, per container: `mijual-web` → `mijual-edge-smoke` **and** `mijual-smoke_default`;
`mijual-api`, `mijual-worker`, `mijual-beat`, `mijual-postgres`, `mijual-redis` → default only.

**The root logging config is live** — and this is the one claim worth reading the evidence for,
because it is the ▷ ledger trap. Two proofs, one mechanical and one real:

1. Every uvicorn line in the container log comes out in *our* format
   (`2026-09-02 07:23:19,638 uvicorn.error INFO Started server process [1]`), not uvicorn's own
   `INFO:     …`. That means `logging.basicConfig` installed the root handler and `log_config=None`
   did not let uvicorn replace it.
2. A **real application logger, from the serving process**, triggered by a real request
   (`POST /feedback` with vocky unconfigured → `503 feedback_unconfigured`):

   ```
   2026-09-02 07:26:53,042 mijual.web.routers.feedback WARNING 의견 forward not accepted: state=unconfigured status=None reason=None
   ```

   Same handler, same format, from `mijual.*`. And inside the container, the root level is **INFO**
   with the config installed and **WARNING** without it — which is precisely why a bare `uvicorn`
   records the ▷ line nowhere:

   ```
   2026-09-02 07:26:23,960 mijual.web.ask INFO agent turn done (synthetic probe: … the exact logger the ▷ ledger uses)
   root level: 20 = INFO
   root level with no basicConfig: WARNING
   ```

   The ▷ line **itself** was not produced: it needs a real `/ask` turn and therefore a real
   `GEMINI_API_KEY`, which the smoke deliberately does not carry. What is proven is the mechanism —
   the exact logger, at INFO, reaching the configured root handler in the shipped image.
   The `session_pepper` warning did **not** fire, as expected: `MIJUAL_SESSION_SECRET` was set.

**Worker + beat.** Worker log: transport and results `redis://mijual-redis:6379/0`,
`concurrency: 1 (prefork)`, `[tasks]` listing all five —
`mijual.bodydoc_sync · mijual.collect_recent · mijual.daily_pipeline · mijual.extract_new ·
mijual.gates_run` — then `Connected to redis://mijual-redis:6379/0` and `celery@… ready.`
Beat log: `scheduler -> celery.beat.PersistentScheduler`, `db -> /app/var/celerybeat-schedule`,
`beat: Starting...`; and on the volume, owned by the app user:

```
-rw-r--r-- 1 mijual mijual 12288 celerybeat-schedule
-rw-r--r-- 1 mijual mijual 32768 celerybeat-schedule-shm
-rw-r--r-- 1 mijual mijual 57712 celerybeat-schedule-wal
```

`python -m mijual.scheduler schedule` inside the API container printed the three entries
(`daily-pipeline-morning` 07:30, `daily-pipeline-evening` 19:30, `weekly-resync` Sun 04:30) under
`timezone : Asia/Seoul (enable_utc=False)`.

**Config seam**, inside the API container:

```
Settings(dart_api_key=<unset>, gemini_api_key=<unset>, session_secret=<set>, ops_id=<set>,
         ops_password=<set>, vocky_api_key=<unset>,
         database_url='postgresql+psycopg://mijual:…@mijual-postgres:5432/mijual',
         redis_url='redis://mijual-redis:6379/0', cache_dir='/app/var/dart-cache')
ROOT: /app   cookie_secure: True   app_base_url: https://jujutower.com
```

`MIJUAL_ROOT=/app` does its job: `cache_dir` is `/app/var/dart-cache` (on the persisted volume), not
the cwd. `date` in both app containers reads **KST**. The non-root user can write the volume
(`uid=10001(mijual)`, `mkdir /app/var/dart-cache` + `touch` succeeded).

**The two packaged read-off-disk surfaces** (see *Findings* 1) resolve inside the image:

```
accuracy.available : True | rows 344 | labelled 344
DECISIONS_DOC      : /app/docs/current/decisions.md
open_decisions     : True | items 3
```

**Persistence / idempotency.** `docker compose -p mijual-smoke restart mijual-api`, then `up -d`
again: the schema one-shot re-ran, printed `schema ok` a second time, exited **0**, table count
still **18**, API healthy again, and `/api/health` + the landing still answered 200 through the
edge network.

### 5. Teardown, and the operator's stack afterwards

`docker compose -f compose.prod.yml -p mijual-smoke down -v` (three volumes and the project network
removed), `docker network rm mijual-edge-smoke`, `rm .env.prod`.

`docker ps` afterwards is byte-for-byte the pre-work baseline — `mijual-postgres` Up 2 days
(healthy) on 5434, `mijual-redis` Up 13 days on 6380, and every `changple5-*` /
`changple_web_dev_postgres` container at its original uptime. `docker network ls` is back to the
original eight. `make stack-status` shows the **same pids** as before the slice (api 60158,
web 61423); `GET :8010/health` → 200 JSON, `GET :3010/` → 200.

The one thing that did move on the operator's stack, unavoidably: `next dev` watches
`next.config.ts` and re-ran it when `output: "standalone"` landed (`✓ Running next.config.ts took
21ms`, `✓ Ready in 344ms` in `var/stack/web.log`). Same pid, still serving; `output` is ignored by
`next dev`, so the operator's runtime is behaviourally unchanged.

### 6. Instrument

**No browser run is claimed.** This slice used `curl` (from throwaway containers on the smoke
networks), `docker` / `docker compose`, `psql` inside the Postgres container, and `python` inside
the app container. No Aside, no browser.

---

## Findings

**1. Two directories the *running* app reads off disk — and the image would have shipped without
either.** The plan asked me to check `evalset/`; the check turned up a second one of the same class.

- `mijual.evalset.sample.EVALSET_DIR = ROOT / "evalset"`, and `opsreads.accuracy()` — the ops
  **정확도·비용** tab — loads `sample.json` + `labels.json` at request time. With `MIJUAL_ROOT=/app`
  and no copy, that signed tab renders its empty state (`{"available": false}`) forever.
- `opsreads.DECISIONS_DOC` pointed at `Path(__file__).parents[3]/docs/current/decisions.md`, which
  is the repo root **only in a source checkout**. The container installs a wheel, so `parents[3]`
  lands inside `site-packages` and the **가동 전 미결** panel on the ops 개요 tab goes dark. The
  function's own docstring anticipates exactly this ("**P4 note:** a deployment that ships `src/`
  without `docs/` turns the panel off — package the doc, or point this constant at where it lands").

Both are fixed: `Dockerfile.api` copies `evalset/{labels.json,sample.json}` and
`docs/current/decisions.md` into `/app`, `.dockerignore` carries two `!` negations for them with the
reason on the line above, and `DECISIONS_DOC` now takes the first of two candidates that exists
(source checkout, then `MIJUAL_ROOT`). Verified in the image (evidence above). No other module reads
a repo file at request time — `grep`ed for `read_text` / `read_bytes` / `open(` across `src/`; the
only other hits are the DART cache (on the volume) and the scheduler's file lock (likewise).

**2. The single-image design has one sharp edge: the inherited `HEALTHCHECK`.** The worker, beat
and the schema one-shot run `mijual-api:latest`, so they inherited its `urllib` probe on
`127.0.0.1:8010` — which none of them serves. Measured, not theorised: on the first `up -d` both
`mijual-worker` and `mijual-beat` went **`unhealthy`** and stayed there. `restart: unless-stopped`
does not act on health, so nothing flapped, but a permanently-unhealthy container is a lie an
operator (and P4.S3's health gate) would have to work around. Fixed in `compose.prod.yml`:

- **worker** — a real probe, `celery -A mijual.scheduler.app inspect ping -t 10` (verified by hand
  in the container: `-> celery@…: OK / pong / 1 node online.`). It answers over Redis, so a broker
  outage reads as unhealthy, which is correct *for the worker* — and deliberately not how the API is
  treated, where Redis is optional at request time.
- **beat** and **schema** — `healthcheck: {disable: true}`. Beat exposes nothing honest to ask (a
  missed beat is detected on the ops 개요 tab's 「실행 기록 없음」 row, which reads the run log); the
  one-shot's gate is its exit code, which `service_completed_successfully` already reads.

**3. `Settings.__repr__` masks the secrets but not the database password.** `database_url` is
printed verbatim, so a deploy script that does `print(load_settings())` (or a helpful debug line in
a runbook) puts the Postgres password in a log. It is pre-existing, designed behaviour — the
masking contract is about `dart_api_key` / `gemini_api_key` / `session_secret` / `ops_password` /
`vocky_api_key` — and changing it is out of this slice's scope, but S3's runbook should not invite
it. Recorded as a note for S3/S4 in `phase.md`.

**4. `.env.prod` has one coupling that fails confusingly.** `POSTGRES_PASSWORD` (which initialises
the container's role) and the password inside `DATABASE_URL` (which the app connects with) are the
same secret written twice; a mismatch is `password authentication failed` against a Postgres that
reports perfectly healthy. Worse, `POSTGRES_*` are read **only on first init**, so editing them
later changes nothing inside an existing `mijual-pgdata`. Both are called out in
`.env.prod.example` and in the note for S3/S4.

---

## Deviations from `plan.md`

1. **The local `next build` ran on an APFS clone of `frontend/`, not in place.** The plan's
   verification step 1 asks for `npm run build` in the repo, but the operator's `next dev` is
   running against that same `frontend/.next` directory and a concurrent production build writes
   into it — the likeliest way this slice could have disturbed the running stack, which the hard
   constraints forbid. So `frontend/` was `cp -Rc`'d (clonefile, near-instant) into the session
   scratchpad, its stale `.next` moved aside, and `MIJUAL_API_ORIGIN=… npm run build` run there.
   Same source, same lockfile, same config; the operator's `.next` was never written. The build was
   then run **a second time for real** inside `frontend/Dockerfile`'s build stage. `typecheck` and
   `smoke` ran in place (neither writes `.next`). The scratch clone was deleted.
2. **`make api-up` was not repointed at `python -m mijual.web`.** The plan offers this as optional
   ("Optionally point the Makefile's `api-up` at it"). I declined: the operator's API is running
   from the current `api-up` body right now, and rewriting its start path is a change whose only
   honest verification is a restart of the operator's process — which the hard constraints forbid.
   The Makefile still states the logging config in one inlined place and the module states it in the
   other; both use the identical `LOG_FORMAT`. `python -m mijual.web` **was** verified by hand on a
   spare port (`--host 127.0.0.1 --port 8011` → `{"status":"ok",…}`, log lines in the root format,
   process stopped, port free, operator pids unchanged) and as PID 1 in the container. Repointing
   `api-up` is a one-line change any later slice can make at a moment when a restart is free.
3. **`.dockerignore` keeps `evalset/labels.json`, `evalset/sample.json` and
   `docs/current/decisions.md`.** The plan proposed excluding `docs` outright and left `evalset`
   conditional on the runtime check; the check said keep both. See *Findings* 1.
4. **`compose.prod.yml` overrides the inherited healthcheck on `mijual-worker`, `mijual-beat` and
   `mijual-schema`.** Not in the plan's service list, added from measured behaviour. See
   *Findings* 2.

Everything else is as specified: no `container_name`, no `ports:`, `restart: unless-stopped` on
every long-running service, `mem_limit` placeholders (API 768m / web 512m / worker 1g / beat 256m /
postgres 512m / redis 128m / schema 256m) with the comment that S4 tunes them from `free -m`, the
`MIJUAL_EDGE_NETWORK` knob (documented "leave unset on the box"), the three named volumes, and
`compose.yaml` (dev) untouched.

---

## Dead ends and small notes

- **`curl` is not in `python:3.13-slim` or `node:22-slim`.** Both healthchecks are therefore
  stdlib: `python -c "import urllib.request…"` and `node -e "fetch(…)"`. Worth knowing before
  someone "simplifies" one into a `curl -f`.
- **`docker images mijual-api mijual-web` is not valid** (`requires at most 1 argument`);
  `docker image ls --format … | grep` is the two-image form.
- **`curlimages/curl` had to be pulled** on first use — it is now in the local image cache, which
  costs nothing and makes the same probe instant for S3/S4.
- The `mijual-schema` service carries **no `build:`** on purpose: it names `image: mijual-api:latest`
  so it can never be built from different source than the API it gates. `deploy.sh` (S3) must
  therefore build `mijual-api` before it `up`s.
- The `mijual-web` healthcheck probes `/api/health`, i.e. **through** the rewrite, not `/`. That
  makes an API outage mark the web container unhealthy too. Deliberate and commented in both files:
  it is the deploy's rollback trigger, and a web container that cannot reach its API is not a
  release when every page is server-rendered from that API.

Phase-level state — the stack contract for S3/S4, the SMTP placement note for S2, the S6 probe
path, the decision, and the five doc-impact lines — is in
[`works/phases/active/P4/phase.md`](../../phase.md) (§ *Decisions*, § *Doc impact*,
§ *Notes for later slices*, § *Now*) and is not restated here.
