# 주주의관제탑 — deploy runbook

The operator + agent script for putting this product on the Oracle box at
**`https://jujutower.com`**, behind the shared `edge-nginx` and Cloudflare.

**Written by `P4.S3`, off the box. Executed by `P4.S4`, on it.** Everything here
was rehearsed on the operator's Mac against a throwaway compose project; nothing
in it has yet touched the box, Cloudflare or the edge.

## Gate map

| Stage | Who runs it | What it needs from the other party |
|---|---|---|
| **R1 provisioning** | **operator** (Cloudflare + box console) | nothing — it is the first step |
| **R2 box prep** | agent over `ssh oracle-cloud` | R1's cert pair in place |
| **R3 first deploy** | agent | R2's `.env.prod` |
| **R4 edge** | agent (+ operator runs `stage.sh`) | R3 healthy |
| **R5 Cloudflare cut-over** | **operator** (console) | R4's origin curls green |
| **R6 post-deploy product checks** | agent, then operator | R5 live |
| **R7 rollback / restore / no-harm** | agent | — (rehearse once, then leave it) |

**Two hard rules the whole runbook rests on.**

1. **Never `up`, `restart` or `--force-recreate` `edge-nginx`.** It owns
   `:80`/`:443` for every co-tenant on this box; recreating it drops the shared
   network attachment and takes them all down. A config change is: drop the file
   → `nginx -t` → `nginx -s reload`.
2. **Never stop, restart or `down` anything you did not start.** The box hosts
   changple5, changple_web, hi2vi, knowledge and vocky. Mijual adds containers;
   it removes nothing.

⚠ **DEPLOY FREEZE — 2026-09-07 11:00 → 2026-09-11 23:59 KST.** No deploy in that
window, **`deploy/rollback.sh` excepted**. `deploy.sh` recreates `mijual-web`
for a few seconds, and the 결격 rule the submitted URL is judged under
(`operations.md` § Deployment) disqualifies on a single outage. Anything that
wants to ship in those five days waits; anything already broken rolls back,
because a rollback is a tag flip and the fastest way back to serving. Recorded
by `P4.S6`; it is also a `## Decisions` entry in the phase notebook.

---

## R1 — provisioning (OPERATOR, in a browser + one box command)

Nothing an agent can do: it needs the Cloudflare account.

1. **Add the zone `jujutower.com`** to Cloudflare and point the registrar at the
   two Cloudflare nameservers it gives you. Wait for the zone to read *Active*.
2. **Leave DNS alone for now.** Do **not** create the `A` record yet — R5 does
   that, in an order that matters.
3. **Mint an Origin CA certificate**: SSL/TLS → Origin Server → *Create
   Certificate*. Private key type RSA, validity **15 years**.
   **SANs:** `jujutower.com` — **and `www.jujutower.com` if you want the www
   alias.** ⚠ This is the one decision that cannot be changed later without
   re-minting: see *Open questions* at the bottom.
4. **Put the pair on the box**, readable by `opc` (this mirrors hi2vi's layout,
   and `stage.sh` reads these two exact paths):

   ```sh
   ssh oracle-cloud 'mkdir -p /home/opc/jujutower_tls'
   # paste the certificate body:
   ssh oracle-cloud 'cat > /home/opc/jujutower_tls/jujutower.com.crt'
   # paste the private key body (it is shown ONCE, in the same dialog):
   ssh oracle-cloud 'cat > /home/opc/jujutower_tls/jujutower.com.key'
   ssh oracle-cloud 'chmod 644 /home/opc/jujutower_tls/jujutower.com.crt;
                     chmod 600 /home/opc/jujutower_tls/jujutower.com.key;
                     chown opc:opc /home/opc/jujutower_tls/jujutower.com.*'
   ```

5. **Do NOT touch the SSL/TLS mode yet.** A new zone defaults to *Flexible*, and
   R5 changes it to Full (Strict) at the right moment.

**Report back:** zone Active (yes/no); the cert's SAN list as minted; that both
files exist with those modes; and **the www decision**.

**Facts you will need:** the box is `ssh oracle-cloud` → **`140.245.64.173`**,
user `opc`, repos under `/home/opc/`. This repo's remote is
`https://github.com/leetusik/Mijual.git`.

---

## R2 — box prep (AGENT, additive only)

**Record the baseline first. Nothing below is safe to skip.**

```sh
ssh oracle-cloud 'docker ps --format "{{.Names}}\t{{.Status}}" | sort'          # the co-tenant baseline
ssh oracle-cloud 'docker inspect -f "{{.State.StartedAt}}" edge-nginx'          # ← WRITE THIS DOWN
ssh oracle-cloud 'docker ps --format "{{.Names}} {{.Ports}}" | grep -E "0.0.0.0:(80|443)->"'  # → edge-nginx
ssh oracle-cloud 'docker network inspect changple_shared_network -f "{{range .Containers}}{{.Name}} {{end}}"'
ssh oracle-cloud 'free -m; df -h /home; docker compose version; crontab -l 2>&1 | head'
```

`edge-nginx` must appear on `changple_shared_network`. `free -m` decides the
`mem_limit`s. `crontab -l` answers whether cron exists at all (R7's backup
question).

**Clone and configure:**

```sh
ssh oracle-cloud 'git clone https://github.com/leetusik/Mijual.git /home/opc/Mijual'
ssh oracle-cloud 'cp /home/opc/Mijual/.env.prod.example /home/opc/Mijual/.env.prod && chmod 600 /home/opc/Mijual/.env.prod'
```

Then fill `/home/opc/Mijual/.env.prod`. **Read `.env.prod.example`'s comments —
they are the specification.** In short:

| Key | Where the value comes from |
|---|---|
| `POSTGRES_PASSWORD` | **mint**: `python3 -c "import secrets;print(secrets.token_urlsafe(24))"` |
| `DATABASE_URL` | the **same** password, written a second time inside the URL |
| `MIJUAL_SESSION_SECRET` | **mint**: `token_urlsafe(48)` |
| `DART_API_KEY`, `GEMINI_API_KEY` | copy from the operator's dev `.env` |
| `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` | **mint** — a separate credential, no reader account |
| `MIJUAL_OPERATOR_CONTACT` | copy from the dev repo-root `.env` — it is in **no** commit, and unset means every reader page silently loses its two footer links |
| `MIJUAL_VOCKY_API_BASE` / `_KEY` | copy from the operator's vocky config; unset makes 의견 보내기 answer 503 on a **reader** surface |
| `SMTP_PASS` | **copy from `/home/opc/hi2vi_web/.env.prod` on the box** — the existing Namecheap Private Email account. It is the only mail key left blank; the other four are already filled in the example |
| `MIJUAL_APP_BASE_URL` | already `https://jujutower.com` |
| `MIJUAL_COOKIE_SECURE` | already `1` |

⚠ **`POSTGRES_PASSWORD` and the password inside `DATABASE_URL` are ONE secret
written twice.** A mismatch is `password authentication failed` against a
Postgres reporting perfectly healthy — and `POSTGRES_*` are read **only on first
init**, so editing them after the volume exists changes nothing.

⚠ **Never `print(load_settings())`** in any step here. `Settings.__repr__` masks
the keys and passwords (including, since `P4.S2`, the one inside `database_url`),
but the rule stands: do not print settings objects in a deploy step.

**Tune the memory limits** in `compose.prod.yml` from `free -m` (today's values
are placeholders: api 768m · web 512m · worker 1g · beat 256m · postgres 512m ·
redis 128m · schema 256m). Commit that change in **this** repo.

**Report back:** the baseline `docker ps`, `edge-nginx`'s `StartedAt`, `free -m`,
whether cron exists, and that `.env.prod` is filled with nothing left blank
except the deliberately optional keys.

---

## R3 — first deploy (AGENT)

```sh
ssh oracle-cloud
cd /home/opc/Mijual
REF= deploy/deploy.sh          # REF= because the clone is already at the ref you want
```

`REF=` (empty) skips the fetch/checkout. **`PROJECT` and `MIJUAL_EDGE_NETWORK`
stay unset on the box** — the compose file's own `name: mijual` and the default
`changple_shared_network` are correct there.

The first run builds both images and takes a few minutes. Expected: the schema
one-shot exits 0, then `mijual-api` healthy, then `mijual-web` healthy, then a
`ps` table with six services.

**Then check, by hand:**

```sh
# 19 tables
docker compose -f compose.prod.yml exec -T mijual-postgres \
  psql -U mijual -d mijual -tAc "select count(*) from pg_stat_user_tables;"

# the mail transport — the fastest way to catch a forgotten SMTP_PASS
docker compose -f compose.prod.yml logs mijual-api | grep 'mail transport:'
#   want: mail transport: smtp ...
#   NOT:  mail transport: console (SMTP_HOST unset ...)   ← serves fine, mails NOBODY

# beat is alive and carries four entries (the banner does NOT print the schedule)
docker compose -f compose.prod.yml exec -T mijual-beat python -c \
  "from mijual.scheduler.app import app; [print(k, v['task'], v['schedule']) for k, v in sorted(app.conf.beat_schedule.items())]"
#   want four, including notify-deadlines @ crontab 30 8 * * *

# the worker registered its tasks
docker compose -f compose.prod.yml logs mijual-worker | grep -A12 '\[tasks\]'

# the app answers on the edge network, by service name, exactly as nginx will reach it
docker run --rm --network changple_shared_network curlimages/curl:latest \
  -sS http://mijual-web:3010/api/health
#   want: {"status":"ok", ...}
```

**What a wrong result looks like:** `up` exiting with *"dependency failed to
start: container … is unhealthy"* means `mijual-api` never came up — compose
enforces `mijual-web`'s `depends_on: service_healthy` itself, so this is the
usual shape of a bad release. `deploy.sh` treats it as a release failure and
rolls back (on a first deploy there is nothing to roll back to, so it leaves the
stack up, exits non-zero and dumps the schema/postgres/api logs — read them).

**Report back:** `ps` output, the table count (19), the mail-transport line, the
four beat entries, and the in-network `/api/health` JSON.

---

## R4 — the edge (AGENT authors, OPERATOR runs `stage.sh`)

Follow **[`deploy/edge/README.md`](edge/README.md)** exactly — it carries the
copy step, the two verbatim `validate.sh` / `stage.sh` diffs, the loop
(`./validate.sh` → `bash stage.sh` → on-VM `bash deploy.sh`) and the
verification.

The short form:

```sh
cp ~/projects/personal/Mijual/deploy/edge/jujutower.conf ~/projects/personal/edge/edge/conf.d/
# apply the two diffs from deploy/edge/README.md to validate.sh and stage.sh
cd ~/projects/personal/edge/edge && ./validate.sh        # must PASS over the whole tree
bash stage.sh                                            # operator-run
ssh oracle-cloud 'cd /home/opc/edge && bash deploy.sh'   # nginx -t → nginx -s reload
```

**Prove the origin directly, still grey (no Cloudflare in the path):**

```sh
curl -sI  --resolve jujutower.com:80:140.245.64.173  http://jujutower.com/            # 301 → https
curl -skI --resolve jujutower.com:443:140.245.64.173 https://jujutower.com/api/health # 200 + JSON
```

**Prove nothing else moved:**

```sh
curl -sI https://hi2vi.com/ https://vocky.hi2vi.com/ https://changple.ai/ | grep -E '^HTTP'  # 200 ×3
ssh oracle-cloud "docker inspect -f '{{.State.StartedAt}}' edge-nginx"    # SAME as R2's baseline
ssh oracle-cloud 'docker ps --format "{{.Names}} {{.Ports}}" | grep -E "0.0.0.0:(80|443)->"'  # edge-nginx
```

⚠ The edge repo is the **operator's**. Apply the edits there; **do not commit in
it**. Mijual commits only its own repo.

**Report back:** `validate.sh` PASS, the two origin curls, the three co-tenant
200s, and `edge-nginx`'s unchanged `StartedAt`.

---

## R5 — the Cloudflare cut-over (OPERATOR, in the console) — ORDER IS LOAD-BEARING

A new zone defaults to SSL/TLS **Flexible**. If the record goes proxied while
the mode is still Flexible, Cloudflare fetches the origin over plain `http`,
gets the `:80` → `https` redirect, and **loops**. Full (Strict) with a bad or
absent origin cert is an instant **526**. So:

1. **SSL/TLS → Overview → Full (Strict). FIRST.** Before any record is proxied.
2. **DNS → add `A  jujutower.com → 140.245.64.173`, Proxy status: Proxied
   (orange).**
3. Wait a minute, then from anywhere:
   ```sh
   curl -sI https://jujutower.com/ | head -3          # 200 (or 3xx to a real page), plus cf-ray
   curl -s  https://jujutower.com/api/health          # the health JSON
   ```
4. **Only after that is green: HSTS.** The origin already sends
   `Strict-Transport-Security: max-age=300`; raising it, or enabling
   Cloudflare's own HSTS, is a deliberate later decision (a long `max-age` on a
   domain that later loses TLS is unrecoverable from the visitor's side).

**Reading the failures:**

| Symptom | Meaning |
|---|---|
| **522** | wrong `A` record, or the origin is unreachable on 443 |
| **526** | Full (Strict) with an invalid/absent origin certificate |
| **524** | the origin took longer than Cloudflare's ~100 s ceiling — an `/ask` turn must stay well under it |
| redirect loop | SSL/TLS still *Flexible* while the record is proxied |

**Cloudflare Web Analytics stays OFF** — it injects `beacon.min.js` from a third
party at the edge, against the measured, signed property that no page contacts a
third-party origin (`security.md`). Search Console verification is a **DNS TXT
Domain property** through the Cloudflare integration, not an HTML meta token
(that is `P4.S5`'s business; noted here so nobody adds a meta tag by reflex).
Cloudflare also **prepends its own managed content-signals block to
`/robots.txt`** — do not duplicate it at the origin.

**Report back:** the external `curl -sI` output, and the SSL/TLS mode as set.

---

## R6 — post-deploy product checks (AGENT, then OPERATOR)

The runtime and access path are whatever `## Operator Runtime` in
`docs/current/operations.md` records — and **`P4.S4` owes that section the
production origin**, with a `## Doc impact` line, or `P4.REVIEW`'s acceptance
gate has no manifest to walk and must stop for the operator.

**Start with the smoke suite — one command, read-only, from a laptop:**

```sh
make smoke-prod                                  # or: python3 scripts/smoke_production.py
make smoke-prod ARGS="--light"                   # just the two probe checks
```

Seventeen checks in ~7 s, all GETs, nothing spent and nothing written: health
(body, not status), the landing's HSTS/CSP/`cf-ray`, the www and http 301s, the
board plus one 종목 and one 이벤트 page built from its own rows, a bad
`rcept_no` staying **404 and not 500**, `/api/ask/start-cards`, the `/ops` door
**without** D15's four rule lines, robots/sitemap/manifest/OG/noindex, no
off-origin `src`/`href` on the landing, and the three **co-tenant** sites still
answering 200 (the R7 no-harm assertion, in code). Non-zero exit on any failure.
Run it **before** a deploy as well, so a red check afterwards is attributable.

It is the machine half of this section. The bullets below are the half only a
human with a real browser can do:

- **The `/ask` stream, in a real browser, frame by frame.** The instrument is
  Aside (`aside repl --account <id> "<js>"`) per the workspace rule, or whatever
  real browser the manifest names. Watch the answer *grow*: 도구 행 appearing as
  the agent reads, prose arriving sentence by sentence, the caret. **A single
  late blob is a failure**, not a slow answer — it means something re-encoded or
  buffered the stream. `curl` cannot see this (it sends no `Accept-Encoding`).
- **The board, a 종목 page and an 이벤트 page** render with real data.
- **The `/ops` door** opens with the R2 credential — and `P4.S4` also owes D15's
  copy change there (removing the R7 implementation rules from the public login
  page).
- **The footer's 운영자 연락처 links** are present on every page. If they are
  missing, `MIJUAL_OPERATOR_CONTACT` is unset on the API — and note the footer
  caches for **10 minutes**, so a fix is not instant.
- **Password reset sends a real mail** now: `POST /auth/reset/request` (that
  exact path). Worth one live check.
- **The gate demo — one real D-day mail.** Pick an anchor day that puts a real
  deadline at D-7/3/1/0 for the operator's own account:
  ```sh
  docker compose -f compose.prod.yml exec mijual-worker \
      python -m mijual.scheduler once --stages notify --no-lock \
      --label gate-demo --notify-today YYYYMMDD
  ```
  It is **idempotent by design**: a second run on the same anchor mails nobody
  (`already-sent`). To re-demo, use a different anchor or delete that
  `notification_send` row.
- **The ops 개요 tab** shows the fourth beat entry, `notify-deadlines 08:30`.
  Until beat has actually fired once it will honestly render 「실행 기록 없음」
  for its due instants — correct, not a bug, and the first thing that proves
  beat is alive on the box.

**Report back:** a browser observation of the stream (not a curl), the ops door,
the mail actually received, and the `## Operator Runtime` Doc impact line.

**And the standing watch, which needs no deploy step.**
`.github/workflows/production-probe.yml` runs the suite's `--light` pair from
GitHub every 10 minutes and, on failure, mails the operator's alert address
over the same SMTP account the product uses. Both endpoints and the credential
are **repository secrets** — `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`,
`ALERT_TO` — so no address and no credential sits in this public repo. Its header carries
the caveats — GitHub disables a scheduled workflow after 60 days of repo
inactivity (a push re-arms it), the schedule only starts once the file is on the
default branch, and cron can lag. `gh workflow run production-probe.yml -f
base=https://jujutower.com/api/nope` is the failure drill: it exercises the
alert path without touching production.

---

## R7 — rollback, restore, and the standing no-harm assertions

### Roll the CODE back (no data touched)

```sh
deploy/rollback.sh                    # retag both :previous → :latest, up -d --no-build, health-gate
REF=<prior-good-sha> deploy/deploy.sh # deeper: rebuild an older ref
```

`deploy.sh` writes **both** `:previous` tags at the start of every run, so
`rollback.sh` reverts to exactly the pair that was live before the last release.
It requires both — half a stack rolled back is not a state anyone can reason
about.

⚠ **After a failed deploy that could NOT roll back (a first deploy, or a
rollback that was itself unhealthy): do not re-run `deploy.sh` before you have
fixed the cause.** The next run tags the *current* — broken — `:latest` as
`:previous` and destroys the last good rollback point.

### Back up and restore the DATA

```sh
deploy/db/backup.sh                                  # → deploy/backups/mijual-<UTC>.dump, keeps 14
deploy/db/restore.sh deploy/backups/<file>.dump --yes # DESTRUCTIVE — see below
```

⚠ **A dump contains reader email addresses and password hashes.** It stays on
this box, mode 600 inside a 700 directory, never committed (`.gitignore` carries
`deploy/backups/`), never copied to a laptop or pasted anywhere. If it must
move, it moves encrypted and the copy is deleted.

`restore.sh` **is not a rollback**: it drops and recreates every object in the
dump, so everything readers did since that dump is gone. It refuses without an
explicit `--yes`. After restoring it runs the schema bootstrap (so a dump older
than the code still gets its missing tables/columns) and health-gates. **Take a
fresh backup before restoring, even when the database looks broken.**

**Nightly backup — installed.** The box has cron (`crontab -l`, confirmed in
R2: one prior entry, changple2's 03:00 certbot line). `P4.S4` added the second
line:

```cron
0 4 * * * cd /home/opc/Mijual && /home/opc/Mijual/deploy/db/backup.sh >> /home/opc/Mijual/var/backup.log 2>&1
```

It fires at **04:00 GMT = 13:00 KST**, not at 04:00 local time — the box's
system clock is GMT (`timedatectl` → `Time zone: GMT (GMT, +0000)`), while the
app containers log in KST. 13:00 KST still sits between the 07:30 and 19:30
KST pipeline collections, so there is no operational harm; the line just sits
in a different gap than the earlier draft argued. (For a run at 04:00 local
time (KST) instead, the line is `0 19 * * *` — 19:00 GMT — recorded here as
the alternative, not applied.) The first cron run produced
`deploy/backups/mijual-20260902T040001Z.dump` (30,356,321 B, mode 600);
`KEEP=14` rotation; log `var/backup.log`.

### The standing no-harm assertions (run after ANY box work)

```sh
curl -sI https://hi2vi.com/ https://vocky.hi2vi.com/ https://changple.ai/ | grep -E '^HTTP'   # 200 ×3
ssh oracle-cloud "docker inspect -f '{{.State.StartedAt}}' edge-nginx"                        # unchanged
ssh oracle-cloud 'docker ps --format "{{.Names}} {{.Ports}}" | grep -E "0.0.0.0:(80|443)->"'  # edge-nginx
ssh oracle-cloud 'docker ps --format "{{.Names}}\t{{.Status}}" | sort'                        # vs the R2 baseline
```

---

## Open questions this runbook cannot answer

1. ~~**`www.jujutower.com` — yes or no?**~~ **ANSWERED: yes** (operator,
   2026-09-02). It needed no new certificate in the end — the Origin CA pair was
   minted with a **wildcard** SAN (`DNS:*.jujutower.com, DNS:jujutower.com`), so
   www was already covered. `P4.S4` enabled it: `www.jujutower.com` on the `:80`
   `server_name` and the www `:443` block uncommented in `jujutower.conf`,
   applied through the edge loop, verified grey (`301` →
   `https://jujutower.com$request_uri`, path and query preserved). **The apex
   stays canonical** — www serves nothing but that redirect. The one remaining
   piece is the DNS record: `www` must be a **proxied** record at the box
   (`A 140.245.64.173` or `CNAME jujutower.com`); until it is, Cloudflare answers
   from the old imported record (a 525). See `deploy/edge/README.md` §
   *The `www.jujutower.com` alias*.
2. ~~**The nightly backup cron — install it, or operator-run only?**~~
   **ANSWERED: install it** (operator, 2026-09-02). `opc`'s crontab carries
   exactly one Mijual line, `0 4 * * *` → `deploy/db/backup.sh`, the second
   line after changple2's 03:00 certbot entry. The box's system clock is GMT,
   so it fires at 04:00 GMT = **13:00 KST**, not at 04:00 local time. The
   first cron run produced `deploy/backups/mijual-20260902T040001Z.dump`.

Both are answered; the record is in `phase.md`'s `## Operator Questions` list,
both entries marked DONE.
