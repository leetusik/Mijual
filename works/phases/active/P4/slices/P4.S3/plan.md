# P4.S3 — Deploy artifacts: the `jujutower.conf` edge vhost, `deploy.sh` / `rollback.sh`, backup/restore, runbook

## What this slice is

Everything the box deploy (`P4.S4`) will *run*, authored and rehearsed here, off the box. S1 gave
the stack its shape (`compose.prod.yml`, two images, the schema one-shot, the volumes); S2 filled
the mail seam. This slice produces: (1) the one file that lands in the edge repo,
`deploy/edge/jujutower.conf`, plus the exact edge-repo edits it needs; (2) `deploy/deploy.sh` and
`deploy/rollback.sh` — the tag-flip, health-gated release for **two** images; (3) the still-owed
**backup/restore path** for the `mijual-pgdata` volume; (4) `deploy/runbook.md` + `deploy/README.md`
— the operator-console steps (Cloudflare) and the box steps in the order that does not 526/loop.
**Nothing here touches the Oracle box, the edge checkout, Cloudflare, or the operator's running dev
stack.** Rehearsals run on this Mac's Docker under a throwaway compose project name.

Read first: `phase.md` whole — the S1 note `(from P4.S1, for P4.S3/S4)` is your stack contract, the
DECOMP notes `for P4.S3/S4` (no-harm contract, vhost rules) and `for P4.S3/S4/S6` (streaming) are
binding, the S2 note `for P4.S4/P4.REVIEW` tells you what the runbook's mail step is. Then
`compose.prod.yml`, `Dockerfile.api`, `frontend/Dockerfile`, `.env.prod.example` (all S1/S2 output),
and `docs/current/operations.md` § *Deployment — the two 결격-grade constraints*. Do not read the
whole doc set.

## Verified facts (already checked — build on them)

**The edge, as it really is** (`~/projects/personal/edge/edge/` — the operator's separate git repo;
**read it, never write into it**). `compose.yml`: `nginx:1.27-alpine`, `container_name: edge-nginx`,
`./conf.d:/etc/nginx/conf.d:ro`, `./certs:/etc/nginx/certs:ro`, external network
**`changple_shared_network`**. Its README's *Add a site* is the contract: **one conf file + one cert
+ a graceful reload**. The standing loop is `./validate.sh` (local: generates gitignored dummy certs
for every basename in `CERT_NAMES=(changple5 changple-web hi2vi default)`, `docker compose config
-q`, then `nginx -t` over the whole `conf.d/` tree in a throwaway container) → `bash stage.sh`
(operator-run: rsyncs the tree to `oracle-cloud:/home/opc/edge` with **no `--delete`**, stages the
**real** cert pairs from fixed box paths in its `[4/6]` step — `/etc/changple5/tls/…` and
`/home/opc/hi2vi_tls/hi2vi.com.{crt,key}` — into `/home/opc/edge/certs/`, verifies sha256 + crt/key
pair match, expects exactly **8** files, then runs `validate.sh` on the VM and asserts `edge-nginx`'s
`StartedAt` and the 80/443 owner are unchanged) → `bash deploy.sh` **on the VM** (`docker compose
exec -T nginx nginx -t` hard gate → `nginx -s reload`; never `up`/`restart`/recreate). A **new cert
basename therefore needs three edge-repo edits**: `validate.sh` `CERT_NAMES` (+ `jujutower`),
`stage.sh` `[4/6]` (copy the real pair from a source path — use `/home/opc/jujutower_tls/
jujutower.com.{crt,key}`, mirroring hi2vi's — add its sha256 source check and its pair-match
basename, bump the count 8 → 10), and the new `conf.d/jujutower.conf`. Those edits are **S4's to
apply** (and the operator's to commit in that repo); **you author them exactly** — as a unified
diff against the current `validate.sh`/`stage.sh` produced from a scratch copy, embedded in
`deploy/edge/README.md`.

**House rules of the `conf.d/` tree** (from `vocky.conf`, `hi2vi.conf`, `00-default.conf`):
`00-default.conf` is the **only** `default_server` on both ports (unknown Host → 444) — never
declare one; **no IPv6 listen**; **no `limit_req_zone`** (its name is global; `hi2vi.conf` owns the
tree's only one) and **no `map`** (same reason); all zone/upstream/variable names must be unique
across the tree — prefix yours `jujutower_`. Per server: `resolver 127.0.0.11 valid=30s ipv6=off;
resolver_timeout 5s;` + `set $jujutower_web mijual-web;` + a **variable** `proxy_pass
http://$jujutower_web:3010;` (a literal name resolves once at load and 502s forever after a
recreate). The Cloudflare real-IP block (`set_real_ip_from …` ×22 + `real_ip_header
CF-Connecting-IP`) — copy the list **verbatim** from `vocky.conf`. HSTS house style:
`add_header Strict-Transport-Security "max-age=300" always;` (short, no preload, no
includeSubDomains; bumping is a later decision). Siblings also add `add_header
Content-Security-Policy "upgrade-insecure-requests" always;` — this app emits **no** security
headers of its own (checked: nothing in `next.config.ts` or the API), so the edge's are the only
ones and there is nothing to conflict with. **No gzip** (Cloudflare compresses; `no-transform`
needs it off anyway). `http2 on` is fine (hi2vi/vocky have it). The **header-inheritance
footgun**: server-level `proxy_set_header` is inherited by a location **only if that location sets
none** — hoist the shared set (`Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`,
`proxy_http_version 1.1`, `Connection ""`) to server level and let ordinary locations set none;
the one location that must set its own (below) re-declares **all** of them.

**Routing for this product**: *everything* → `mijual-web:3010`. `/api/*` is Next's own rewrite to
FastAPI over the project network — **never split `/api/` off at nginx** (changes the origin model,
breaks same-origin CSRF). One special location: **`/api/ask`** (`POST`, SSE) needs the streaming
block — copy `changple-web.conf` `location /bff/` wholesale (it re-declares every header, then
`proxy_buffering off; proxy_request_buffering off; proxy_cache off; chunked_transfer_encoding on;
proxy_read_timeout 3600s; add_header X-Accel-Buffering no;`) with the upstream swapped. The
app already sets `Cache-Control: no-store, no-transform` and `X-Accel-Buffering: no` itself;
nginx must pass them through untouched. Idle timeout must exceed ~10 s (longest observed gap
6.0 s); Cloudflare caps any origin response at ~100 s (524) whatever nginx allows. Use
`location = /api/ask` or a prefix — your call, say why. `/ops` stays routable (the login door is
public by design; D15's copy change is S4's).

**Cloudflare, for a NEW zone** (`jujutower.com` — the hi2vi wildcard cert does **not** cover it):
its own **Origin CA** cert (SAN: `jujutower.com`, and `www.jujutower.com` if the operator wants the
alias — an Operator Question, see below), 15-year, key `600 opc:opc` at
`/home/opc/jujutower_tls/`. **The loop hazard**: a new zone's SSL/TLS mode defaults to *Flexible*;
if the record goes proxied while the mode is Flexible and `:80` redirects to https, Cloudflare
fetches http → gets 301 → loop. hi2vi avoided it by shipping `:443` commented and doing HTTP-first;
on the standalone edge `validate.sh`'s dummy certs let the file ship with `:443` live, so the safe
order is: real pair staged on the box → conf in → `nginx -t` → reload → prove the origin directly
(`curl -sI --resolve jujutower.com:80:140.245.64.173 http://jujutower.com/` → 301; `curl -skI
--resolve jujutower.com:443:140.245.64.173 https://jujutower.com/api/health` → 200) → Cloudflare
**SSL/TLS = Full (Strict) FIRST** → DNS `A jujutower.com → 140.245.64.173` **proxied** → external
`https://` 200 → HSTS. 522 = wrong A / origin unreachable; 526 = Full (Strict) with an invalid
origin cert; 524 = origin took > 100 s. **Cloudflare Web Analytics stays OFF** (decided). Search
Console = a DNS TXT Domain property via the Cloudflare integration (S5's business; mention only).
The box: ssh alias **`oracle-cloud`** → `140.245.64.173`, user `opc`, repos under `/home/opc/`
(hi2vi at `/home/opc/hi2vi_web`), Docker Compose v2 (needs `COMPOSE_BAKE=false` for `build`), no
systemd. This repo's remote: `https://github.com/leetusik/Mijual.git`; clone it to
`/home/opc/Mijual`.

**The stack contract (S1)**: images `mijual-api:latest` + `mijual-web:latest` (both built by
`docker compose -f compose.prod.yml build`; `mijual-schema`, worker and beat run the api image with
**no `build:`**, so the api must be built before `up`); `mijual-schema` is a one-shot that must exit
0 (`service_completed_successfully`); health gates: **`mijual-web`** (probes `/api/health` through
the rewrite — the honest rollback trigger) and `mijual-api` (`/health`); worker has `celery inspect
ping`; beat and schema have healthchecks **disabled** (never poll them). Volumes:
`mijual-pgdata` (the one non-regenerable volume), `mijual-redisdata`, `mijual-var`. `MIJUAL_EDGE_
NETWORK` selects the external network (unset on the box). `.env.prod` keys are documented in
`.env.prod.example` (S2 filled the SMTP block; only `SMTP_PASS` is left blank for the box);
`POSTGRES_PASSWORD` and the password inside `DATABASE_URL` are one secret written twice; `POSTGRES_*`
are read on **first init only**. `mem_limit`s are placeholders S4 tunes. Never `print(load_settings())`
in a script (fixed in S2 for the URL password, but keep the rule).

**THE LOCAL HAZARD — read twice.** `compose.prod.yml` declares `name: mijual`. The operator's dev
stack on this Mac is the compose project **`mijual`** too (`compose.yaml`, directory-derived), with
volumes **`mijual_mijual-pgdata`** and **`mijual_mijual-redisdata`** — the dev database. Running
`docker compose -f compose.prod.yml …` here **without `-p`** would attach the production stack to the
operator's dev Postgres volume. Verified: `-p mijual-rehearsal` overrides `name:` (volumes become
`mijual-rehearsal_mijual-pgdata` …). So: **every local invocation carries `-p <throwaway>`**, your
scripts take the project name from an env knob and pass `-p` whenever it is set, and the runbook says
that on the box the knob stays unset. The operator's stack (`make stack-status`: Postgres up, API pid
on 8010, `next dev` on 3010) and the `changple*` co-tenants stay untouched — never stop, restart or
`down` anything you did not start.

**Tooling here**: Docker Desktop (`linux/aarch64`, same arch as the box), `uv 0.8.14` → `uvx --from
shellcheck-py shellcheck …` gives you shellcheck without installing anything; `openssl` present.

## Deliverables

1. **`deploy/edge/jujutower.conf`** — `:80` server (`server_name jujutower.com;` + `return 301
   https://$host$request_uri;`) and `:443 ssl` server per the house rules above: cert paths
   `/etc/nginx/certs/jujutower.crt|key`, resolver + variable upstream, real-IP list, HSTS +
   `upgrade-insecure-requests`, hoisted proxy headers, `client_max_body_size` modest (the product
   uploads nothing — say 1m), `location /` → `http://$jujutower_web:3010`, and the `/api/ask`
   streaming location. Header comment in the sibling files' style: what it is, where it lands, the
   loop, the rules it obeys, and **why no gzip / no zone / no map**. If the operator wants `www`,
   the alias is a second `server_name` + a 301 to the apex — draft it commented-out with a note.
2. **`deploy/edge/README.md`** — how the file reaches the edge: copy into the edge checkout's
   `conf.d/`, apply the **exact** `validate.sh` / `stage.sh` edits (embed the unified diff you made
   in your scratch copy), the cert source path on the box, `./validate.sh` → `bash stage.sh` →
   `bash deploy.sh` on the VM, and the verification (`curl --resolve` against the box IP; co-tenant
   `curl -sI https://hi2vi.com https://vocky.hi2vi.com https://changple.ai` still 200;
   `docker inspect -f '{{.State.StartedAt}}' edge-nginx` unchanged). State plainly that the edge
   repo is the operator's and that S4 applies these edits without committing there.
3. **`deploy/deploy.sh`** — adapted from `hi2vi_web/deploy/deploy.sh` (read it; do not copy its
   comments verbatim, write this stack's). `set -euo pipefail`; knobs via env: `APP_DIR`,
   `COMPOSE_FILE`, `ENV_FILE`, `PROJECT` (→ `-p` when set; **unset on the box**), `REF`
   (default `origin/main`; **empty = skip the fetch/checkout**, for a rehearsal or a box that was
   just cloned), `HEALTH_TRIES`/`HEALTH_INTERVAL` (a cold start is schema + api + standalone
   Next — give it 40 × 5 s), `MIJUAL_EDGE_NETWORK` passthrough. Preflight: git/docker/compose v2,
   compose file, env file, the external network exists (`docker network inspect`), the edge
   container is **not** something this script touches (assert it never names `edge-nginx`).
   Steps: fetch + checkout (unless skipped) → tag **both** `mijual-api:latest` and
   `mijual-web:latest` → `:previous` (skip any that is absent; first deploy has none) →
   `COMPOSE_BAKE=false dc build` → `dc up -d` (this runs `mijual-schema`; on its failure print its
   logs — the likeliest first-deploy fault is the `POSTGRES_PASSWORD`/`DATABASE_URL` mismatch) →
   health-gate **`mijual-web`** (and `mijual-api`) on `.State.Health.Status` → on failure retag
   both `:previous → :latest`, `dc up -d --no-build`, re-gate; **first deploy: leave up, exit
   non-zero, never roll back**. Print `dc ps` at the end. Also print the one mail line to look
   for (`mail transport:`) in `dc logs mijual-api`.
4. **`deploy/rollback.sh`** — the manual counterpart: both `:previous` tags required, retag, `up
   -d --no-build`, gate.
5. **`deploy/db/backup.sh`** and **`deploy/db/restore.sh`** — the owed path. Backup: `dc exec -T
   mijual-postgres pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB"` → `deploy/backups/mijual-
   <UTC stamp>.dump` (dir gitignored, `700`), keep the newest N (default 14), print size and the
   `pg_restore --list` table count. Read `POSTGRES_USER/DB` from the env file **without echoing
   the file** (parse the two keys only). Restore: takes a dump path, refuses without an explicit
   `--yes`, `pg_restore --clean --if-exists --no-owner` over `exec -T` stdin into the running
   database, then `dc run --rm mijual-schema` (or `exec mijual-api python -m mijual.db ensure`) so a
   dump older than the code still gets its missing tables/columns, then the health gate. **A dump
   holds reader emails + password hashes** — say so in the script header and in the runbook
   (stays on the box, `700`, never leaves it, never committed). Suggest a `crontab` line for the
   box (`0 4 * * * …`) in the runbook as an S4 decision; the box has cron? unknown — S4 checks.
6. **`deploy/runbook.md`** (this product's, not a copy of hi2vi's) with a gate map and these
   stages, each with commands and a "report back" line: **R1 provisioning** (operator console:
   zone, nameservers, Origin CA cert with the SAN decision, place the pair at
   `/home/opc/jujutower_tls/`, box public IP is `140.245.64.173`); **R2 box prep** (agent over
   ssh, additive: clone to `/home/opc/Mijual`, `.env.prod` from the example — what to mint, what to
   copy from `/home/opc/hi2vi_web/.env.prod` (`SMTP_PASS` only), `MIJUAL_OPERATOR_CONTACT` from the
   dev `.env`, `free -m` → `mem_limit`s, confirm `changple_shared_network` + that `edge-nginx` is on
   it, record the `docker ps` baseline and `edge-nginx` `StartedAt`); **R3 first deploy**
   (`deploy/deploy.sh` with `REF=` since it was just cloned, `ps` healthy, 19 tables, the mail
   transport log line, worker `[tasks]` + beat schedule lines, `curl` from a scratch container on
   the shared network to `http://mijual-web:3010/api/health`); **R4 edge** (per `deploy/edge/
   README.md`); **R5 Cloudflare cut-over** (Full (Strict) first, then proxied A, external checks,
   HSTS); **R6 post-deploy product checks** (real-browser `/ask` streaming frame-by-frame — the
   instrument is Aside per the workspace rule, or whatever real browser the manifest names; the
   ops door; the S2 gate-demo mail command; the footer contact links; and the **Doc impact** S4
   owes: the production origin in `## Operator Runtime`); **R7 rollback / restore / the no-harm
   assertions** (co-tenant curls 200, `StartedAt` unchanged, port owner unchanged). Keep it
   operational — commands, expected output, what a wrong result looks like (522/526/524).
7. **`deploy/README.md`** — the contract table like hi2vi's (images, services, ports, network,
   secrets, build arg, health, rollback, edge, TLS, backups) + the lifecycle two-liner.
8. `.gitignore`: `deploy/backups/`.

Do **not** modify `compose.prod.yml`, the Dockerfiles or any product code unless a rehearsal
proves a defect; if you must, keep it minimal and record the deviation.

## Rehearsal (all of it, on this Mac; record every command + outcome in `result.md`)

1. **Static:** `bash -n` on every script; `uvx --from shellcheck-py shellcheck deploy/*.sh
   deploy/db/*.sh` clean (or each remaining warning justified in a comment).
2. **The vhost against the real tree:** `cp -R ~/projects/personal/edge/edge <scratch>/edge`,
   drop `jujutower.conf` into its `conf.d/`, apply your `validate.sh`/`stage.sh` edits **to the
   scratch copy only**, run `./validate.sh` there — it must pass over the whole tree (that is the
   global-name collision check). Save the diff of the two scripts for `deploy/edge/README.md`.
   Then a functional proof: run a throwaway `nginx:1.27-alpine` with the scratch `conf.d/` + dummy
   certs on the rehearsal network (below), `curl -H 'Host: jujutower.com' http://<nginx>/` → 301,
   `curl -k -H 'Host: jujutower.com' https://<nginx>/api/health` → the health JSON **through the
   edge → mijual-web → rewrite → api** chain, and `curl -k -N -X POST https://<nginx>/api/ask …`
   (or a GET that streams, if one exists — check `docs/current/backend.md` § Streaming for the
   request shape and whether it needs a model; if a real turn needs `GEMINI_API_KEY`, prove the
   streaming *directives* instead by inspecting the proxied response headers for `X-Accel-Buffering:
   no` and `Cache-Control: no-store, no-transform` surviving the hop, and say so).
3. **The release loop:** `docker network create mijual-edge-smoke`; throwaway `.env.prod` with
   dummy secrets (gitignored — check `git status`); `PROJECT=mijual-rehearsal
   MIJUAL_EDGE_NETWORK=mijual-edge-smoke REF= deploy/deploy.sh` → first deploy healthy, "no
   :previous" branch taken; run it **again** → both `:previous` tags written, healthy; then
   `deploy/rollback.sh` with the same knobs → healthy on `:previous`. Exercise the **automatic
   rollback branch** if you can do it honestly and cheaply (e.g. a deliberately broken build via
   a knob you would ship anyway — say what you did); otherwise state it was not exercised.
4. **Backup/restore on the rehearsal stack:** `deploy/db/backup.sh` → a `.dump` whose
   `pg_restore --list` names 19 tables; `deploy/db/restore.sh <dump> --yes` → succeeds, `schema ok`
   afterwards, api still healthy; rotation keeps N.
5. **Tear down only what you made:** `docker compose -p mijual-rehearsal -f compose.prod.yml down
   -v`, the throwaway nginx, `docker network rm mijual-edge-smoke`, the scratch edge copy, the
   throwaway `.env.prod`, `deploy/backups/*`. Then `make stack-status`, `docker ps`, `docker volume
   ls | grep mijual` must show exactly the operator's state (`mijual_mijual-pgdata` untouched,
   the dev pids unchanged, every `changple*` container unchanged). Paste it.
6. `.venv/bin/python -m pytest`, `python3 scripts/workflow.py validate` still green (you changed
   no product code, but say so with the run).
7. Instrument: `curl` + Docker; no browser run is claimed; no box, no Cloudflare, no real cert.

If anything needs the box, a real credential, the operator's Cloudflare account, or a decision
you cannot draft around, return `needs_operator` with the exact question.

## Notebook duties (`phase.md`, edited under budget — never append-only)

- **Consume** the S3 half of `(from P4.DECOMP, for P4.S3/S4)` and of `(from P4.DECOMP, for
  P4.S3/S4/S6)` — keep only what S4/S6 still need (the prohibitions and the Cloudflare order
  stay; the "author it here as deploy/edge/jujutower.conf" line is done). Rewrite the S1 note's
  "restore path is still OWED" line to point at `deploy/db/`.
- **Add** `(from P4.S3, for P4.S4)`: the runbook is the script for S4 — stage order, the knobs
  (`PROJECT` unset on the box, `REF=` on the first run), the edge-repo edits to apply, the cert
  source path, what to record before touching anything (`docker ps` baseline, `edge-nginx`
  `StartedAt`), the Cloudflare order with Full (Strict) first, the backup cron decision, and
  the exact Doc impact S4 owes for `## Operator Runtime`. One line `(for P4.S6)`: the probe and
  smoke should target `/api/health` + `/` and may reuse the runbook's R6 checks; the release
  scripts' health gate is the same `/api/health`.
- **Doc impact** (one line each, `(P4.S3)`): `operations` (Deployment: `deploy/` lifecycle,
  runbook pointer, backup/restore + the dump's PII handling); `architecture` (Repo Shape:
  `deploy/` tree); `security` (the edge's headers — HSTS/CSP upgrade — and the real-IP restore;
  backups carry emails + hashes and stay on the box).
- **Operator Questions** (append): `www.jujutower.com` alias — yes/no (affects the Origin cert
  SAN and one DNS record); the backup cron on the box (install, or operator-run only?).
- **Decisions**: add the routing decision (everything → `mijual-web`; one streaming location for
  `/api/ask`; Full (Strict) before the record goes proxied).
- Housekeeping: D23 is **dropped** (`works/deferred/dropped/D23`) — fix the stale Decisions line
  ("stays in `works/deferred/open/D23/`") and drop the `## Now` line telling the orchestrator to
  run `drop-deferred`.
- Rewrite `## Now` (≤ 15 lines) as the handoff to `P4.S4`: what S3 landed, the rehearsal evidence
  in one line, that S4 executes the runbook on the box and stops `pending` for the Cloudflare
  steps, and what S4 must not do (touch edge-nginx, commit in the edge repo).

## `result.md`

Verdict block first, then the log: every command and its outcome, the validate.sh run over the
real tree, the curl proofs, the rehearsal `ps`/`inspect` output, the backup/restore output, the
teardown proof, dead ends. Reference `phase.md` sections rather than restating them.
