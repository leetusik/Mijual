# P4.S3 — result

- **status**: `done`
- **summary**: Authored and rehearsed everything the box deploy will run: the
  `jujutower.conf` edge vhost (validated by `nginx -t` over the real `conf.d/`
  tree and proven functionally against a live stack), the exact `validate.sh` /
  `stage.sh` edge-repo diffs, `deploy/deploy.sh` + `rollback.sh` for the two-image
  tag-flip release, the still-owed `deploy/db/backup.sh` + `restore.sh` for
  `mijual-pgdata`, and `deploy/runbook.md` + `deploy/README.md`. The rehearsal
  found three real defects in my own scripts and one in the vhost, all fixed and
  re-proven; the operator's dev stack and every `changple*` co-tenant are
  byte-identical to the pre-slice baseline.
- **files_changed**:
  - `deploy/edge/jujutower.conf` (new)
  - `deploy/edge/README.md` (new)
  - `deploy/deploy.sh` (new)
  - `deploy/rollback.sh` (new)
  - `deploy/db/backup.sh` (new)
  - `deploy/db/restore.sh` (new)
  - `deploy/runbook.md` (new)
  - `deploy/README.md` (new)
  - `.gitignore` (added `deploy/backups/`)
  - `works/phases/active/P4/phase.md` (notebook)
  - `works/phases/active/P4/slices/P4.S3/result.md` (this file)
- **validation**:
  - `bash -n` on all four scripts — pass
  - `uvx --from shellcheck-py shellcheck deploy/*.sh deploy/db/*.sh` — **clean, zero findings**
  - `./validate.sh` in a scratch copy of the real edge tree, with `jujutower.conf` + both script edits applied — **PASS** (dummy certs for 5 basenames, `docker compose config -q`, `nginx -t` over the whole `conf.d/` tree)
  - both README-embedded diffs `patch -p1 --dry-run` cleanly against the **pristine** edge scripts — pass
  - functional edge proof through a throwaway `nginx:1.27-alpine` on a throwaway network: `:80` → 301; `https://jujutower.com/api/health` → **200 + health JSON** through edge → `mijual-web` → Next rewrite → FastAPI; `POST /api/ask` → SSE with `cache-control: no-store, no-transform` and `x-accel-buffering: no` intact and **no gzip** despite `Accept-Encoding: gzip`
  - release loop under `-p mijual-rehearsal`: first deploy (no `:previous`) → healthy; second run → both `:previous` tags written → healthy; `rollback.sh` → healthy on `:previous`; `rollback.sh` with `:previous` absent → correct refusal, exit 1
  - **automatic rollback exercised for real** with a deliberately broken image: release fails, both `:previous` retagged to `:latest`, re-up without rebuild, re-gate healthy, exit 1 with the right message
  - backup/restore on the rehearsal stack: dump → `19` tables in `pg_restore --list`; rotation to `KEEP=2` correct; restore refuses without `--yes` (exit 2); `restore.sh <dump> --yes` → `schema ok`, api + web healthy, `conversation_turn` back from 5 rows to the dumped 2
  - teardown: `docker ps -a` / `docker volume ls` / `docker network ls` **byte-identical** to the pre-slice baseline; dev stack pids 60158 / 61423 unchanged; `127.0.0.1:8010/health` and `127.0.0.1:3010/` → 200
  - `.venv/bin/python -m pytest` — **165 passed**
  - `python3 scripts/workflow.py validate` — **passed** (one pre-existing `oversized_doc_sections` warning, untouched by this slice)
- **deviations**: three, all recorded below — (1) the vhost gained two re-declared
  security headers in the `/api/ask` location after the rehearsal measured them
  missing; (2) `deploy.sh` treats a failed `up -d` as a release failure that rolls
  back, which the plan did not anticipate because compose's own dependency gate
  fires first; (3) the plan's description of `stage.sh`'s `[6/6]` assertions was
  slightly wrong — corrected in `deploy/edge/README.md`. No product code changed.
- **doc_impact**: three lines appended to `phase.md` — `operations` (the
  `deploy/` lifecycle, the runbook, backup/restore + the dump's PII handling),
  `architecture` (Repo Shape: the `deploy/` tree), `security` (the edge's
  HSTS/CSP + Cloudflare real-IP restore; backups carry emails and password
  hashes and stay on the box).

---

## What landed

Eight files under `deploy/`, plus one `.gitignore` line. `deploy/README.md` is
the contract table and the lifecycle; `deploy/runbook.md` is the R1–R7 script
`P4.S4` executes. Nothing touched the box, Cloudflare, the edge checkout, the
operator's dev stack, or any product file.

**Instrument: `curl` + Docker only. No browser run is claimed** — the `/ask`
stream was verified at the header and frame level through the real proxy chain,
which is what this slice can honestly prove off the box. The frame-by-frame
browser observation is `R6`'s, on the deployed product.

## Rehearsal log

### 1. Static

```
bash -n deploy/deploy.sh deploy/rollback.sh deploy/db/backup.sh deploy/db/restore.sh   → OK
uvx --from shellcheck-py shellcheck deploy/*.sh deploy/db/*.sh                          → clean
```

One shellcheck finding appeared and was fixed rather than justified: `SC2015`
(`A && B || C` is not if-then-else) on the edge-`StartedAt` report, rewritten as
a real `if`. **`mapfile` was deliberately avoided** in `backup.sh`'s rotation:
this Mac runs bash **3.2.57**, the box runs bash 4+, and a script that only
works in one of them is not a rehearsed script.

### 2. The vhost against the real edge tree

`cp -R ~/projects/personal/edge/edge <scratch>/edge` (read-only source; **nothing
was written into the operator's edge repo**), dropped `jujutower.conf` into
`conf.d/`, applied the `validate.sh` + `stage.sh` edits to the scratch copy only:

```
==> [1/3] dummy certs      kept changple5 / changple-web / hi2vi / default, made jujutower
==> [2/3] docker compose config -q            ok
==> [3/3] throwaway nginx -t over the full conf.d/ tree
          nginx: configuration file /etc/nginx/nginx.conf test is successful
PASS: edge config validated locally
```

That run is the global-name collision check: `jujutower.conf` introduces
`$jujutower_web` and the TLS session cache `jujutower_tls`, declares no
`limit_req_zone`, no `map`, no named `upstream {}` and no `default_server`, and
the whole tree still passes. The two diffs are embedded verbatim in
`deploy/edge/README.md`, and were re-extracted from that README and
`patch -p1 --dry-run`'d against the **pristine** edge scripts to prove they still
apply.

**Correction to the plan's premise:** `stage.sh`'s `[6/6]` block asserts
**`changple5-nginx-1`'s** `StartedAt` and the 80/443 port owner — *not*
`edge-nginx`'s, which it only *reports*. So `edge-nginx`'s `StartedAt` must be
recorded and re-checked by hand; `deploy/edge/README.md` and the runbook's R2/R4
both say so.

### 3. The functional edge proof

A throwaway `nginx:1.27-alpine` with the scratch `conf.d/` + dummy certs, on a
throwaway `mijual-edge-smoke` network alongside the rehearsal stack:

```
curl -H 'Host: jujutower.com' http://<nginx>/
  → HTTP/1.1 301 Moved Permanently, Location: https://jujutower.com/

curl -k --resolve jujutower.com:443:<nginx> https://jujutower.com/api/health
  → HTTP/2 200
    strict-transport-security: max-age=300
    content-security-policy: upgrade-insecure-requests
    {"status":"ok","version":"0.1.0","now_kst":"2026-09-02T08:19:03+09:00"}
```

That is the full chain — edge → `mijual-web:3010` → Next's `/api/*` rewrite →
FastAPI `/health` — with `mijual-api` never reachable from the edge network.
`/`, `/ops` and `/api/ask/start-cards` all returned 200 through the same hop.

**The streaming proof.** A real `POST /api/ask` with the CSRF header and
`Accept-Encoding: gzip, deflate, br`:

```
HTTP/2 200
content-type: text/event-stream; charset=utf-8
cache-control: no-store, no-transform
x-accel-buffering: no

event: session   data: {"session_hash": "..."}
event: status    data: {"phase": "read", "text": "질문을 읽고 있습니다", ...}
event: error     data: {..., "reason": "ClientError"}
```

Three frames arrived incrementally; the `error` terminal is the correct outcome
with a dummy `GEMINI_API_KEY`, and it proves the stream **opened** and the
transport-level contract survived the proxy. **No `content-encoding: gzip`**
despite the request offering it — the tree's no-gzip stance holds, which is the
`no-transform` requirement. Idle-timeout headroom is `proxy_read_timeout 3600s`
against a 6.0 s worst observed gap.

**Defect found and fixed (vhost).** The first version of `location = /api/ask`
declared only `add_header X-Accel-Buffering no`, and the measured response
carried **no `Strict-Transport-Security` and no `Content-Security-Policy`** —
`add_header` inherits exactly like `proxy_set_header`, all-or-nothing per
context, and the plan's footgun note covers only the latter. Both are now
re-declared inside that location, re-validated and re-measured present. The
proven sibling `changple-web.conf` `location /bff/` has the same latent hole.

**Resolver re-resolution, proven the hard way.** The throwaway nginx started once
at `23:18:50Z` and was never restarted, while `mijual-web` was recreated ~7 times
across the release rehearsals (new container IP each time). `/api/health` and `/`
still answered 200 at the end. That is the variable `proxy_pass` + `resolver
127.0.0.11 valid=30s` doing exactly the job the DECOMP note says it must.

### 4. The release loop

Throwaway `.env.prod` with minted dummy secrets (`git check-ignore` confirmed it
matched `.gitignore:3 .env.*`), a throwaway network, and **every** invocation
carrying `-p mijual-rehearsal`. The existing `mijual-api:latest` /
`mijual-web:latest` from `P4.S1` were parked under a `:pre-s3` tag first, so the
first-deploy branch was genuinely first.

| Run | Branch exercised | Outcome |
|---|---|---|
| 1 | first deploy, no `:previous` | healthy, exit 0 |
| 2 | both `:previous` tags written | healthy, exit 0 |
| 3 | `rollback.sh` | `:latest` = the `:previous` IDs, healthy, exit 0 |
| 4 | `rollback.sh` with `:previous` absent | correct refusal, exit 1 |
| 5 | deliberately broken image | release fails → **auto-rollback → healthy**, exit 1 |
| 6 | `:latest` deleted, clean volume | `first deploy: neither image exists yet`, healthy, exit 0 |

Run 6's log line, verbatim:

```
[deploy] no existing mijual-api:latest — nothing to tag
[deploy] no existing mijual-web:latest — nothing to tag
[deploy] first deploy: neither image exists yet, so there is no rollback point
```

**The automatic rollback was exercised honestly, not simulated.** I prefixed
`src/mijual/web/__main__.py` with a `raise SystemExit(...)` so the api image
built fine and the process died at import; the source was restored immediately
afterwards and `git status src/` is clean. The dumped logs showed the exact
fault (`SyntaxError: from __future__ imports must occur at the beginning of the
file`), then:

```
[deploy] RELEASE FAILED at 'up' — treating it exactly like a failed health gate
[deploy] rolling back: retagging both :previous -> :latest and re-upping WITHOUT a rebuild
[deploy] mijual-web healthy on poll 2
[deploy] mijual-api healthy on poll 1
[deploy] ERROR: the new build was unhealthy — ROLLED BACK to :previous (now healthy).
```

**Defect found and fixed #1 — the health gate was unreachable.** Because
`mijual-web` declares `depends_on: mijual-api: condition: service_healthy`,
**compose itself** waits for the API and `up -d` exits non-zero with
`dependency failed to start: container … is unhealthy`. The first version of
`deploy.sh` treated that as a hard `die` — measured result: the api
crash-looping, `mijual-web` stuck in `Created` (the site down), **and no
rollback**, with two perfectly good `:previous` images sitting unused. `up` and
the health gate now share one failure path.

**Defect found and fixed #2 — the rollback's own `up` was unguarded.** With
`set -e`, a rollback into an also-broken image aborted the script on the bare
compose error, so the intended "the rollback to `:previous` is ALSO unhealthy —
manual intervention required" message was unreachable. Both `deploy.sh` and
`rollback.sh` now let that `up` fail and hand the verdict to the health gate.

**Defect found and fixed #3 — two wrong operator-facing lines.** `docker inspect`
on a missing container writes an empty line to stdout *before* failing, so
`|| echo absent` yielded `"\nabsent"` and the edge-`StartedAt` guard printed
nonsense; and the printed post-deploy advice claimed `logs mijual-beat` lists
the schedule, which celery's banner does **not** do (measured). The beat check is
now a command that actually answers, and it was run:

```
daily-pipeline-evening: mijual.daily_pipeline @ crontab 30 19 * * *
daily-pipeline-morning: mijual.daily_pipeline @ crontab 30 7 * * *
notify-deadlines:       mijual.notify_deadlines @ crontab 30 8 * * *
weekly-resync:          mijual.daily_pipeline @ crontab 30 4 * * 0
```

Four entries, `notify-deadlines` at 08:30, as `P4.S2` landed it. The health gate
also now reports the container's lifecycle state (`restarting` / `exited`)
rather than telling an operator staring at a crash loop that the service "has no
healthcheck".

Also measured on the cold run: **19 tables**, and
`mail transport: console (SMTP_HOST unset — messages are printed, no mail is
sent)` — exactly the line R3 tells `P4.S4` to look for, since the rehearsal
`.env.prod` carried no SMTP block.

**One hazard worth carrying forward** (documented in `deploy.sh`'s header and
runbook R7, not fixable in code without guessing): a failed deploy that could not
roll back leaves `:latest` broken, and the **next** `deploy.sh` run tags that
broken image as `:previous`, destroying the last good rollback point. Fix the
cause before re-running.

### 5. Backup / restore

```
[backup] wrote deploy/backups/mijual-20260901T232029Z.dump (64K, mode 600)
[backup] verified: valid custom-format archive, 19 tables with data
[backup] retention: 2 dump(s) kept (KEEP=2)      ← after rotating 3 out
```

Directory `700`, file `600`, `git check-ignore` confirms `deploy/backups/`.
Restore, proven with real data movement: dump taken at `conversation_turn` = 2
rows, three more `/api/ask` turns pushed it to 5, then

```
[restore] archive OK: ... (64K, 19 tables with data)
[restore] restoring into mijual as mijual
[restore] running the schema bootstrap (python -m mijual.db ensure)
schema ok
[restore] mijual-api healthy on poll 2 / mijual-web healthy on poll 1
[restore] DONE
→ select count(*) from conversation_turn;  = 2
→ select count(*) from pg_stat_user_tables; = 19
```

Without `--yes` it printed the refusal and exited **2**.

### 6. Teardown

`docker compose -p mijual-rehearsal -f compose.prod.yml down -v` (three
rehearsal volumes removed), the throwaway nginx removed, `mijual-edge-smoke`
removed, the `:pre-s3` parking tags untagged, `.env.prod` deleted,
`deploy/backups/` deleted, the scratch edge copy deleted.

`diff` of the full `docker ps -a` / `docker volume ls` / `docker network ls`
capture, before vs after, shows **exactly two lines**, both expected:
`mijual-api:latest` and `mijual-web:latest` are freshly rebuilt (new IDs, same
399 MB / 443 MB, same tags). Every container, every volume — including
`mijual_mijual-pgdata` — and every network is identical. `make stack-status`
reports the same pids (api 60158, web 61423) as before the slice, both dev URLs
answer 200, and all nine `changple*` containers show their original uptimes.

### 7. Dead ends

- **First attempt at the broken-image rehearsal failed to break anything**: the
  `raise` was *appended* to `__main__.py`, which sits after `sys.exit(main())` —
  and `main()` blocks in uvicorn forever, so the line was never reached and the
  deploy passed. Prefixing it worked. Worth knowing before anyone repeats the
  exercise.
- **`HEALTH_TRIES=1` as a way to force a gate failure was rejected**: the same
  knob governs the rollback's re-gate, so it can only reach the "rollback is
  also unhealthy" branch, never the successful one. Breaking a real image is
  what actually exercises the path.

## Notebook

The state `P4.S4` needs is in
[`phase.md`](../../phase.md) — the new `(from P4.S3, for P4.S4)` note (stage
order, knobs, the edge edits, the cert source path, the Cloudflare order, what to
record before touching anything, and the `## Operator Runtime` Doc impact S4
owes), the one-liner `(for P4.S6)`, the routing decision, the two new
`## Operator Questions`, the three `## Doc impact` lines, and a rewritten
`## Now`. Not restated here.
