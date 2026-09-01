# P4.S1 — Containerize: Dockerfile(s), `compose.prod.yml`, schema bootstrap, production config seam

## What this slice is

The first deploy slice of P4. It turns the product — FastAPI API, Next.js frontend, Postgres,
Redis, Celery beat + worker — into a **Docker Compose co-tenant stack** that `P4.S3` (deploy
scripts + edge vhost + runbook) and `P4.S4` (the actual deploy on the Oracle box) can ship
additively behind the shared `edge-nginx` on that box. **Nothing in this slice touches the box.**
Everything is authored here and proven locally on Docker Desktop (server `linux/aarch64`, the same
architecture as the OCI box, so a local build is a real rehearsal).

Read first: `works/phases/active/P4/phase.md` whole (the *Notes for later slices* tagged `for
P4.S1` are your constraints), `intent.md` for the confirmed intent, and the two reference repos
named below. Read `docs/current/operations.md` §*Environment Variables*, §*Observability*, §*Local
Development*, §*The one setting a deploy silently gets wrong*, and `docs/current/backend.md`
§*Background Jobs* / §*Error Handling and Logging*. Do not read the whole doc set.

## Verified facts you can build on (already checked; do not re-derive)

**Toolchain on this Mac.** Python 3.13.5 (`.venv` is a plain `venv`, pip-installed, `-e .`),
`uv 0.8.14` at `~/.local/bin/uv`, Docker 28.2.2 + Compose v2.37.1 (Docker Desktop, server
`linux/aarch64`), Node v24.3.0 / npm 11.4.2. **No `uv.lock`, no `requirements*.txt`, no
`.python-version`, no `.dockerignore` anywhere.** Installed pins today (pip freeze): fastapi
0.141.1, starlette 1.6.0, uvicorn 0.52.4, SQLAlchemy 2.0.52, psycopg 3.3.4, celery 5.6.3,
redis 8.1.0, google-genai 2.18.1, pytest 9.1.1, httpx 0.28.1.

**The operator's dev stack is RUNNING right now and must keep running:** `make stack-status`
shows `mijual-postgres` (docker, host 5434) up 2 days, the API pid on `127.0.0.1:8010`, `next dev`
on `0.0.0.0:3010`; a dev `mijual-redis` container (host 6380) is also up. Other tenants of this
Mac's Docker: the `changple5-*` stack, `changple_web_dev_postgres`, networks `changple5_app_network`,
`changple_web_default`, `mijual_default`, `knowledge_default`, `vocky_default`. **Never run
`make stack-down`, never stop/restart/`down` any container you did not start, and publish no host
ports** — your smoke stack must be invisible to all of that.

**The API.** `mijual.web.app:app` (factory `create_app`), `GET /health` touches no database
(`{"status":"ok","version":...,"now_kst":...}`) — the liveness probe by design. The engine is
lazy; the serving process creates **no** tables. `Settings` (`src/mijual/config.py`) reads env
first, then `ROOT/.env`; `repo_root()` honours **`MIJUAL_ROOT`** and otherwise walks up to a
`pyproject.toml`/`.git` — inside an image with the package installed into site-packages there is
none, so **set `MIJUAL_ROOT=/app`** or the cache dir lands in the cwd. Defaults that must be
overridden in production: `DEFAULT_DATABASE_URL = postgresql+psycopg://mijual:mijual@localhost:5434/mijual`,
`DEFAULT_REDIS_URL = redis://localhost:6380/0`, `app_base_url = http://localhost:3010`,
`cookie_secure = False`. The DART response cache is `ROOT/var/dart-cache` (regenerable, but it
saves quota across redeploys — persist it). Nothing in `src/mijual/web` reads `request.client.host`
or `X-Forwarded-*`, so no proxy-header configuration is needed.

**The ▷ ledger trap.** The per-turn agent-spend line is `log.info` on the ask module's logger; a
bare `uvicorn` never installs a root logging config, so it is recorded nowhere. The Makefile's
`api-up` inlines `logging.basicConfig(level=logging.INFO, ...)` + `uvicorn.run(..., log_config=None)`
for exactly this reason. The container entrypoint must do the same.

**Schema bootstrap.** No migrations by design. The Makefile's `db-ensure` inlines
`create_all(engine)` + `ensure_columns(engine, Base)` (`mijual.db.session`, `mijual.db.schema_sync`,
`mijual.db.models.Base`) — additive and idempotent. A fresh database has **18** tables after it
(P4.DECOMP: 16 without the two conversation tables, and every `/ask` turn then fails at persistence).

**The scheduler.** `celery -A mijual.scheduler.app worker -l info -c 1` and
`celery -A mijual.scheduler.app beat -l info -s var/celerybeat-schedule` (`-s` keeps beat's shelve
out of the repo root — put it on the persisted `var/` volume). Broker + backend + run-lock are all
`Settings.redis_url`. `timezone=Asia/Seoul`, `enable_utc=False`. The worker needs `DART_API_KEY`,
`GEMINI_API_KEY`, `DATABASE_URL`, `REDIS_URL`; beat needs `REDIS_URL` (it imports the same app).
Redis is optional to the **API** at request time (the lock chip degrades), so the API depends on
Postgres/schema, not on Redis.

**The frontend.** Next 16.3.2 / React 19.2.8 / TS 5.9.3, `package-lock.json` present, scripts
`dev`/`build`/`start -p 3010`/`typecheck`/`smoke`. **No `next/image` anywhere** (the `Wordmark`
uses a plain `<img>`; `sharp 0.35.3` is only Next's optional dep in the lock — irrelevant). Fonts are
self-hosted under `app/fonts/` (`next/font/local`), `public/foundations/tokens.css` and
`public/assets/` are static. `next.config.ts` has **no `output` key yet**; its `rewrites()` sends
`/api/:path*` to `MIJUAL_API_ORIGIN` (default `http://localhost:8010`) and that is resolved at
**build** time. Separately, `frontend/lib/api.ts` reads `process.env.MIJUAL_API_ORIGIN` at
**runtime** for server-component fetches (`SERVER_ORIGIN`). So the container needs the same value
**both** as a build arg **and** as a runtime env var: `http://mijual-api:8010` (the compose service
name). `allowedDevOrigins` is dev-only; `next build`/`next start` ignore it. Nothing is
prerendered (`connection()` everywhere), so `next build` needs no API. `MIJUAL_OPERATOR_CONTACT`
and every secret belong on the **API** process, never on the web container.

**The reference implementation next door — read, never edit:**
`~/projects/personal/hi2vi_web/{Dockerfile,compose.prod.yml,.dockerignore,.env.prod.example}`
and `deploy/deploy.sh` (tag-flip + container-healthcheck gate: `IMAGE:latest` → `:previous`,
`COMPOSE_BAKE=false docker compose build`, `up -d`, poll `docker inspect .State.Health.Status`).
The edge's compose is `~/projects/personal/edge/edge/compose.yml`: `nginx:1.27-alpine`,
`container_name: edge-nginx`, and the external network is **`changple_shared_network`** — that is
the network the web container must join so the edge can reach it by **service name**.

**`.gitignore` ignores `.env.*`** — a committed `.env.prod.example` needs the negation
`!.env.prod.example` (hi2vi does exactly this).

## Deliverables

1. **`uv.lock`** (committed) from `uv lock` against the existing `pyproject.toml`, plus a
   `.python-version` of `3.13`. Add `pytest`/`httpx` under the existing `dev` extra only if the
   lock needs it (it already declares them). Check the locked versions are the same major lines as
   the pip-installed ones above; if `uv lock` picks something newer that breaks the test suite,
   pin the range in `pyproject.toml` and say so. **Do not** replace the operator's `.venv` — the
   dev workflow stays pip/`make`.
2. **`Dockerfile.api`** (repo-root context). `python:3.13-slim`, uv copied from
   `ghcr.io/astral-sh/uv:0.8.14`, two-layer install (`uv sync --frozen --no-dev --no-install-project`
   on `pyproject.toml`+`uv.lock`, then copy `src/` and `uv sync --frozen --no-dev --no-editable`),
   non-root user, `WORKDIR /app`, `ENV MIJUAL_ROOT=/app PYTHONUNBUFFERED=1 TZ=Asia/Seoul`, a
   writable `/app/var` owned by the app user (the volume mount point), `HEALTHCHECK` with
   `python -c "urllib.request..."` on `http://127.0.0.1:8010/health` (no curl in slim), default
   `CMD ["python","-m","mijual.web"]`. The worker and beat services reuse **this same image** with
   their own `command:`.
3. **`src/mijual/web/__main__.py`** — the production entrypoint: install the root logging config
   (same format the Makefile uses), then `uvicorn.run("mijual.web.app:app", host=..., port=...,
   log_config=None, workers=1)` with host/port from `MIJUAL_API_HOST`/`MIJUAL_API_PORT` (defaults
   `0.0.0.0` / `8010`) or `--host/--port` flags. One worker on purpose: the ask limiter and login
   attempt state are per process (N workers = N× the cap) and the box is small — say so in the
   docstring. Optionally point the Makefile's `api-up` at it so the logging config is stated once;
   if you do, keep `127.0.0.1:8010` and verify by running it on a **spare** port by hand (e.g.
   `--port 8011`, then `curl /health`, then stop it) — never by restarting the operator's stack.
4. **`src/mijual/db/__main__.py`** — `python -m mijual.db ensure`: `create_all` + `ensure_columns`,
   printing the Makefile's `schema ok (+N columns)` line, exit non-zero on failure. Point the
   Makefile's `db-ensure` at it (a one-line change; verify with `make db-ensure` against the
   running dev Postgres — it is idempotent and prints `schema ok`).
5. **`frontend/Dockerfile`** (context `frontend/`) and **`frontend/.dockerignore`**
   (`node_modules`, `.next`, `*.tsbuildinfo`, `.env*`, `.DS_Store`). Multi-stage on `node:22-slim`:
   `npm ci` from the lock, `ARG MIJUAL_API_ORIGIN` **asserted non-empty** (`test -n` — the hi2vi
   trap: a defaulted origin lets a wrong build succeed silently) and exported to the build, `next
   build`; runtime stage copies `.next/standalone`, `.next/static`, `public`, runs as `node`, `ENV
   NODE_ENV=production PORT=3010 HOSTNAME=0.0.0.0 NEXT_TELEMETRY_DISABLED=1`, `HEALTHCHECK` with
   `node -e "fetch(...)"`, `CMD ["node","server.js"]`. Keep the container port **3010** so every
   origin the docs name stays the same number. **`NODE_ENV=production` only in the runtime stage.**
6. **`frontend/next.config.ts`**: add `output: "standalone"` with a two-line comment (P4.S1, why).
   `next dev` ignores it, so the operator's runtime is unchanged.
7. **Root `.dockerignore`** for the API context: `.git`, `.venv`, `frontend`, `node_modules`,
   `works`, `docs`, `var`, `scripts/spike/samples`, `evalset`? (keep `evalset/` **in** only if the
   package imports it at runtime — check `src/mijual/evalset`; otherwise exclude), `tests`,
   `.env`, `.env.*`, `*.zip`, `.pytest_cache`, `__pycache__`, `.claude`, `.DS_Store`. Full-line
   comments only (Docker ignores inline ones).
8. **`compose.prod.yml`** (`name: mijual`). Mirror hi2vi's shape, no `container_name` anywhere
   (the dev compose already owns `mijual-postgres`/`mijual-redis` on this Mac; the edge resolves
   **service names**), **no `ports:` anywhere**, `restart: unless-stopped` on every long-running
   service, `mem_limit` co-tenant guards (reasonable defaults — API 768m, web 512m, worker 1g,
   beat 256m, postgres 512m, redis 128m — with a comment that `P4.S4` tunes them from the box's
   `free -m`). Services:
   - `mijual-postgres` — `postgres:16`, `env_file: .env.prod` (it reads `POSTGRES_USER/PASSWORD/DB`
     from there), named volume `mijual-pgdata`, `pg_isready` healthcheck, internal network only.
   - `mijual-redis` — `redis:7` with `--appendonly yes`, named volume `mijual-redisdata`,
     `redis-cli ping` healthcheck, internal only.
   - `mijual-schema` — the one-shot: `image: mijual-api:latest`, `command: python -m mijual.db
     ensure`, `env_file: .env.prod`, `restart: "no"`, `depends_on: mijual-postgres:
     condition: service_healthy`.
   - `mijual-api` — `build: {context: ., dockerfile: Dockerfile.api}`, `image: mijual-api:latest`,
     `env_file: .env.prod`, volume `mijual-var:/app/var`, `expose: ["8010"]`, `depends_on:
     mijual-schema: condition: service_completed_successfully`, internal network only.
   - `mijual-web` — `build: {context: ./frontend, args: {MIJUAL_API_ORIGIN: "http://mijual-api:8010"}}`,
     `image: mijual-web:latest`, `environment: {MIJUAL_API_ORIGIN: "http://mijual-api:8010"}`
     (no `env_file` — the frontend holds no secret), `expose: ["3010"]`, `depends_on: mijual-api:
     condition: service_healthy`, on **both** the internal network and the external `edge`
     network. Its healthcheck fetches `http://127.0.0.1:3010/api/health` — it is the deploy's
     rollback trigger (S3), and a web that cannot reach its API through the rewrite is not a
     release; note the trade-off in a comment.
   - `mijual-worker` — `image: mijual-api:latest`, `command: celery -A mijual.scheduler.app worker
     -l info -c 1`, `env_file`, `mijual-var` volume, depends on redis healthy + schema completed.
   - `mijual-beat` — same image, `command: celery -A mijual.scheduler.app beat -l info -s
     /app/var/celerybeat-schedule`, `env_file`, `mijual-var` volume, same depends.
   - `networks:` — the default internal one, plus `edge: {external: true, name:
     ${MIJUAL_EDGE_NETWORK:-changple_shared_network}}` so the local smoke can substitute a
     throwaway network without an override file (comment: **on the box leave it unset**).
   - `volumes:` `mijual-pgdata`, `mijual-redisdata`, `mijual-var`.
   `TZ=Asia/Seoul` on the app containers is fine (log timestamps); the app already computes KST
   itself.
9. **`.env.prod.example`** (committed, `!.env.prod.example` added to `.gitignore`), every key
   named with a one-line purpose and no real value: `POSTGRES_USER=mijual`, `POSTGRES_DB=mijual`,
   `POSTGRES_PASSWORD=` (**must match** the password inside `DATABASE_URL` — say so),
   `DATABASE_URL=postgresql+psycopg://mijual:<POSTGRES_PASSWORD>@mijual-postgres:5432/mijual`,
   `REDIS_URL=redis://mijual-redis:6379/0`, `DART_API_KEY=`, `GEMINI_API_KEY=`,
   `MIJUAL_SESSION_SECRET=` (how to mint: `python3 -c "import secrets;print(secrets.token_urlsafe(48))"`),
   `MIJUAL_COOKIE_SECURE=1`, `MIJUAL_OPS_ID=`, `MIJUAL_OPS_PASSWORD=`,
   `MIJUAL_APP_BASE_URL=https://jujutower.com`, `MIJUAL_OPERATOR_CONTACT=` (public by decision,
   but travels in no commit — it lives in the dev `.env`, so the deploy copies it by hand),
   `MIJUAL_VOCKY_API_BASE=`, `MIJUAL_VOCKY_API_KEY=`, and the optional
   `MIJUAL_COUNTDOWN_CUTOFF_TIME` / `MIJUAL_STALE_AFTER_HOURS` commented. Leave a clearly marked
   **`# --- mail (P4.S2 adds SMTP_* here) ---`** placeholder section so S2 extends one file. Note
   in the header that `MIJUAL_API_ORIGIN` is **not** in this file: it rides `compose.prod.yml`
   `build.args` + `environment` because it is baked at build.
10. **`phase.md`** and **`result.md`** per the notebook duties below.

Keep `compose.yaml` (dev) untouched except, if you must, a two-line header comment pointing at
`compose.prod.yml`. The dev stack's ports, names and volumes stay exactly as they are.

## Not in this slice

The edge vhost `deploy/edge/jujutower.conf`, `deploy.sh`/`rollback.sh`, the backup/restore
scripts and the runbook (**S3**); anything on the box, Cloudflare, DNS, certs (**S4**); the SMTP
`Mailer` and the D-day beat task (**S2** — you only leave the `.env.prod.example` placeholder);
SEO (**S5**); the probe and monitoring (**S6**). No nginx, no CORS, no host ports, no new routes, no
third-party origin, no changes to signed product surfaces. No new test files — containerization is
verified live, and the existing suites must still pass.

## Verification (all of it, and record every command + outcome in `result.md`)

1. **Repo checks stay green:** `.venv/bin/python -m pytest` (142 tests, no DB/network),
   `cd frontend && npm run typecheck && npm run build && npm run smoke` (the build now emits
   `.next/standalone`), `python3 scripts/workflow.py validate`.
2. **Lock sanity:** `uv lock` is reproducible (`uv lock --check` passes after committing), and
   `uv export`/`uv tree` shows the same major lines as pip freeze above.
3. **Images build locally:** `COMPOSE_BAKE=false docker compose -f compose.prod.yml build` succeeds
   for `mijual-api` and `mijual-web` on this Mac (linux/arm64 — identical to the box). Note the
   image sizes.
4. **The stack comes up in isolation.** Create `docker network create mijual-edge-smoke`; write a
   throwaway **`.env.prod`** (gitignored — confirm with `git status` that it is) with dummy values
   for every key (the smoke needs no real DART/Gemini/vocky credential; leave those empty; copy
   `MIJUAL_OPERATOR_CONTACT` from `.env` if you like, it is public); then
   `MIJUAL_EDGE_NETWORK=mijual-edge-smoke docker compose -f compose.prod.yml -p mijual-smoke up -d`.
   Prove, and paste the evidence:
   - `docker compose -p mijual-smoke ps`: postgres, redis, api, web, worker, beat **healthy/running**;
     `mijual-schema` **exited 0**, and its log prints `schema ok`.
   - **18 tables**: `docker compose -p mijual-smoke exec mijual-postgres psql -U mijual -d mijual -c "\dt"`
     (count them; name `conversation_turn` and `conversation_feedback` explicitly).
   - From a scratch container on the smoke network (`docker run --rm --network mijual-edge-smoke
     curlimages/curl:latest -s http://mijual-web:3010/api/health`): the health JSON **through the
     Next rewrite** — this is exactly the path the edge will take. Also `.../` returns 200 with
     `<html lang="ko"` and `주주의관제탑` in the body, and `http://mijual-api:8010/health` is reachable
     from the **internal** network only (from the edge network it must not resolve — prove it).
   - **The root logging config is live:** the API container's log shows INFO lines from the app's
     own loggers (e.g. the `session_pepper` warning does **not** fire because the secret is set; find
     one INFO line that is not uvicorn's access log — or temporarily set the log level env and show
     an app logger line). State what you saw.
   - **Worker + beat:** the worker log lists the five `mijual.*` tasks under `[tasks]` and
     `connected to redis://mijual-redis:6379/0`; beat's log shows it started and wrote its
     schedule to `/app/var/celerybeat-schedule` (`docker compose exec mijual-beat ls -la /app/var`).
     `python -m mijual.scheduler schedule` inside the API container prints the three entries.
   - **Config seam:** inside the API container, `python -c "from mijual.config import
     load_settings as l; s=l(); print(s)"` shows `database_url` pointing at `mijual-postgres`,
     `cookie_secure` on, secrets masked `<set>`/`<unset>` — and `MIJUAL_ROOT` makes `cache_dir`
     `/app/var/dart-cache`.
   - **Persistence:** `docker compose -p mijual-smoke restart mijual-api` and the schema one-shot
     re-run (`up -d` again) — idempotent, `schema ok`, still 18 tables.
5. **Tear down only what you made:** `docker compose -p mijual-smoke down -v`, `docker network rm
   mijual-edge-smoke`, delete the throwaway `.env.prod`. Then `make stack-status` and `docker ps`
   must show the operator's stack and every other tenant exactly as before (postgres up 2 days,
   api pid, web pid, the `changple*` containers untouched). Paste that.
6. Instrument note for `result.md`: this slice used curl/`docker` — no browser run is claimed.

If any step needs a real credential, an operator decision, or would touch the operator's running
stack or another tenant, stop and return `needs_operator` with the exact question instead of
guessing.

## Notebook duties (`phase.md`, edit under budget — never append-only)

- **Drop** the `(from P4.DECOMP, for P4.S1/S4) — production config the live .env does not have`
  note and the S1 half of the `for P4.S1/S3/S4` "no harm" note that this slice consumed (keep
  what S3/S4 still need: the edge-nginx prohibitions, the vhost rules, the tag-flip loop).
- **Add** one note **(from P4.S1, for P4.S3/S4)** with the stack's contract: image names
  (`mijual-api:latest`, `mijual-web:latest` — the tag-flip targets), service names (the edge
  proxies to **`mijual-web:3010`** on `changple_shared_network`; the API is internal-only), the
  health gates (`mijual-web` healthcheck = `/api/health` through the rewrite; `mijual-schema` must
  exit 0 before the API starts), the three volumes and what each holds, that **the restore path
  (`pg_dump`/`pg_restore` against the `mijual-pgdata` volume) is still owed and is S3's runbook
  work**, the `MIJUAL_EDGE_NETWORK` knob (unset on the box), the `.env.prod` key list and the
  `POSTGRES_PASSWORD` = `DATABASE_URL` password coupling, and that `mem_limit`s are placeholders S4
  tunes. One note **(from P4.S1, for P4.S2)**: where SMTP keys go (`.env.prod.example` placeholder
  section; the API/worker/beat all read `env_file`, so a beat task can send). One line
  **(for P4.S6)**: the probe path is `https://jujutower.com/api/health` (proxied) + the landing.
- **Doc impact** (append one line each, tagged `(P4.S1)`): `operations` — Local Development /
  a new *Production stack* section: `compose.prod.yml`, the services, `.env.prod` keys via
  `.env.prod.example`, `python -m mijual.web` / `python -m mijual.db ensure`, `make db-ensure` now
  delegating; `architecture` — Repo Shape (`Dockerfile.api`, `frontend/Dockerfile`,
  `compose.prod.yml`, `uv.lock`, `.env.prod.example`) and Stack (uv lockfile; `output: standalone`);
  `backend` — the entrypoint module with the root logging config, one worker on purpose;
  `frontend` — `output: "standalone"` and `MIJUAL_API_ORIGIN` being both a build arg and a runtime
  var; `security` — Secret Handling: `.env.prod` on the box, `.env.prod.example` committed, the
  frontend container carries no secret.
- **Decisions**: add "Postgres + Redis are compose services in production (named volumes on the
  box), the web container joins `changple_shared_network` and is the only thing the edge sees; the
  API, worker and beat live on the project-internal network."
- **Operator Questions**: add one only if you actually hit one (e.g. if the locked Python deps
  force a range bump you are unsure about).
- Rewrite **`## Now`** (≤ 15 lines) as the handoff to `P4.S2`: what landed, the smoke evidence in
  one line, what S2 extends (`.env.prod.example` SMTP section, the beat task), and that S3 owes the
  restore path.

## `result.md`

Verdict block first (`verdict`, `summary`, `files_changed`, `validation`, `deviations`,
`doc_impact`, `escalation: none`), then the log: every command and its outcome, the smoke
evidence, image sizes, locked versions vs pip freeze, dead ends. Do not restate what you put in
`phase.md`; reference it by section.
