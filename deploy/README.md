# `deploy/` — how 주주의관제탑 ships

The product runs as a **Docker Compose stack** on the operator's shared Oracle
Cloud box, behind the standalone **`edge`** nginx project and Cloudflare, at
**`https://jujutower.com`**. There is no VM provisioning, no systemd and no
release symlink: **a release is a rebuilt image pair, and a rollback is a tag
flip.**

The **container contract lives at the repo root** — [`compose.prod.yml`](../compose.prod.yml),
[`Dockerfile.api`](../Dockerfile.api), [`frontend/Dockerfile`](../frontend/Dockerfile)
and [`.env.prod.example`](../.env.prod.example) (frozen by `P4.S1`/`P4.S2`).
This folder holds the **lifecycle, the edge integration, the data path and the
runbook**.

```
deploy/
  README.md        # this file — the contract table + the lifecycle
  runbook.md       # the operator + agent script, R1..R7, for the actual deploy
  deploy.sh        # tag :previous -> build -> up -> health-gate -> roll back on failure
  rollback.sh      # manual revert to the :previous image pair
  db/
    backup.sh      # pg_dump -Fc of mijual-pgdata, rotated
    restore.sh     # pg_restore + schema bootstrap + health gate  (DESTRUCTIVE)
  edge/
    jujutower.conf # the vhost that lands in the edge repo's conf.d/
    README.md      # how it gets there + the two verbatim edge-script diffs
  backups/         # dumps live here on the box. GITIGNORED. Reader PII inside.
```

## Serving contract

| Thing | Value |
|---|---|
| Images | `mijual-api:latest` (Dockerfile.api) and `mijual-web:latest` (frontend/Dockerfile), both `linux/arm64` — the box's architecture, so a local build is a real rehearsal |
| Services | `mijual-postgres`, `mijual-redis`, `mijual-api`, `mijual-web`, `mijual-worker`, `mijual-beat`, plus the one-shot `mijual-schema` |
| One image, four processes | `mijual-api`, `mijual-worker`, `mijual-beat` and `mijual-schema` all run `mijual-api:latest` with a different `command:` — the worker can never drift from the code whose results the API reads |
| Ports | **none published.** `expose:` only; the edge reaches the stack by service name |
| Networks | project-internal `default` for everything; **`mijual-web` alone** also joins the external `changple_shared_network` (`MIJUAL_EDGE_NETWORK` overrides the name for a rehearsal; **unset on the box**) |
| Edge sees | **only `mijual-web:3010`.** `mijual-api` does not resolve from the edge network (measured, `P4.S1`) |
| Routing | *everything* → `mijual-web`. `/api/*` is Next's own rewrite to FastAPI inside the project network — **never split at nginx** (it would break same-origin CSRF) |
| Secrets | compose `env_file: .env.prod`, operator-created on the box, gitignored. **`mijual-web` has no `env_file` and must never get one** |
| Build arg | `MIJUAL_API_ORIGIN=http://mijual-api:8010`, needed at build **and** runtime; the frontend Dockerfile asserts it non-empty |
| Schema | `mijual-schema` runs `python -m mijual.db ensure` on every `up`, must exit 0; the API gates on `service_completed_successfully`. Additive and idempotent; **19 tables** as of `P4.S2` |
| Health gates | `mijual-web` (fetches `/api/health` **through the rewrite** — the honest rollback trigger) and `mijual-api` (`/health`, no DB). `mijual-worker` reports `celery inspect ping` but is not gated; `mijual-beat` and `mijual-schema` have healthchecks **disabled** and are never polled |
| Rollback | image tags: `mijual-api:previous` + `mijual-web:previous` → `:latest`. `deploy.sh` writes both at the start of every run |
| Volumes | `mijual-pgdata` (**the only non-regenerable one**), `mijual-redisdata`, `mijual-var` |
| Backups | `deploy/db/backup.sh` → `deploy/backups/`, 700/600, **reader PII inside**, never leaves the box |
| Edge | the standalone `edge` project (`edge-nginx`); Mijual's whole footprint there is `conf.d/jujutower.conf` + `certs/jujutower.{crt,key}` |
| TLS | Cloudflare **Full (Strict)** + a `jujutower.com` **Origin CA** cert (15-year) mounted into the edge. The hi2vi wildcard does not cover this zone |
| Mail | SMTP over the operator's existing Namecheap Private Email account; `SMTP_HOST` unset is a supported state that serves fine and mails nobody — check the `mail transport:` log line after every deploy |

## Lifecycle (on the box, from `/home/opc/Mijual`)

```sh
deploy/deploy.sh                       # release origin/main: checkout → build → up → health-gate
REF=<sha> deploy/deploy.sh             # release a specific ref
REF= deploy/deploy.sh                  # skip the checkout (a fresh clone, or a rehearsal)
deploy/rollback.sh                     # revert to the :previous pair, no rebuild
deploy/db/backup.sh                    # nightly / pre-deploy dump
deploy/db/restore.sh <dump> --yes      # DESTRUCTIVE data restore
```

- **`deploy.sh`** tags **both** live images `:previous` *before* it builds, then
  `COMPOSE_BAKE=false docker compose build`, `up -d` (which runs the schema
  one-shot), then health-gates `mijual-web` and `mijual-api`. On failure — **at
  the gate _or_ at `up`**, because compose enforces `mijual-web`'s
  `depends_on: service_healthy` itself and exits non-zero first — it retags both
  `:previous → :latest`, re-ups without a rebuild and re-gates. A **first
  deploy** has no `:previous`: it is left up for inspection and exits non-zero,
  never silently.
- **`PROJECT`** adds `-p` to every compose call and exists for one reason: the
  operator's **dev** stack on their Mac is also compose project `mijual`, and
  running this file without `-p` there would attach the production stack to the
  dev database volume. **On the box it stays unset.**
- **`rollback.sh`** requires **both** `:previous` images. If they are gone, use a
  deeper git-ref rebuild: `REF=<prior-good-sha> deploy/deploy.sh`.
- **Nothing here ever touches `edge-nginx`.** Both scripts record its
  `StartedAt` before and assert it unchanged at the end.

The full operator + agent script — Cloudflare, box prep, the first deploy, the
edge, the cut-over order and the post-deploy checks — is
**[`runbook.md`](runbook.md)**.
