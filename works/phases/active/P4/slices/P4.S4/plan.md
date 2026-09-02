# P4.S4 — Execute the deploy on the Oracle box; Cloudflare zone, DNS, Origin CA, edge reload

Orchestrator plan, written 2026-09-02 after `P4.S3` landed (`bbcb490`). This slice was promoted from
**D15** (the `/ops` door copy) and absorbed the whole box deploy at `P4.DECOMP`. It runs
`deploy/runbook.md` R1 → R7 **for real**, on the operator's shared Oracle box, and it is the first
slice of this phase whose actions reach outside this Mac.

Read, in this order, before touching anything: `works/phases/active/P4/phase.md` (whole — the
`## Now` block tells you which **stage** of this plan you are resuming at), `deploy/runbook.md`,
`deploy/edge/README.md`, `deploy/README.md`, `.env.prod.example`, `compose.prod.yml`. The runbook
is your script; this plan is the ladder around it — what each dispatch does, where it must stop,
and what it must never do.

## What this slice is — and why it stops more than once

Some runbook stages are the **operator's**: R1 (the Cloudflare zone, the registrar's nameservers,
the Origin CA certificate) and R5 (the DNS cut-over in the Cloudflare console). Nothing an agent can
do, and R1 is long-lead (nameserver propagation). So this slice is dispatched **more than once**:

- **Dispatch 1** does everything that is safe and useful before the operator has provisioned
  anything, then returns `needs_operator` with one consolidated ask list (STOP POINT 1).
- **Dispatch 2** (after the push + R1) deploys the stack (R3), wires the edge (R4), proves the
  origin grey, then returns `needs_operator` for the cut-over (STOP POINT 2).
- **Dispatch 3** (after R5) verifies through Cloudflare, runs R6 in a real browser, closes R7, the
  Doc impact, the notebook, and returns `done`.

**Resumption rule.** Every dispatch starts at Stage 0. Read `## Now` in `phase.md` for the
recorded stage and the facts already gathered (baseline values, decisions the operator gave), then
**verify the recorded state against reality** before acting on it (`test -f` the cert, `docker ps`
the stack, `git -C … log -1` the clone) — the notebook is a handoff, not a proof. `result.md` is
written from scratch each dispatch with the verdict block first; on a resumed dispatch, carry the
previous dispatch's stage log forward under a `## Earlier dispatches` heading **below** the fresh
verdict block, so the evidence of every stage survives to the review. Keep `phase.md`'s `## Now`
the authoritative "where we are": the stage reached, the values the next dispatch needs, and the
exact asks outstanding.

## Hard rules — the no-harm contract and the secrets rule

These are not preferences. Any of them broken is a failed slice.

1. **Never `up`, `restart`, `stop`, `rm` or `--force-recreate` `edge-nginx`, and never `down`
   the `edge` compose project.** A config change on the edge is: file in `conf.d/` → `nginx -t`
   → `nginx -s reload`, and only through the edge repo's own `validate.sh` → `stage.sh` →
   on-VM `deploy.sh` loop.
2. **Never stop, restart, `down`, or remove anything on the box you did not start.** The box
   hosts changple5, changple_web (and its beta), hi2vi, knowledge and vocky. Mijual adds
   containers; it removes nothing. `docker compose -f compose.prod.yml` commands run **only** from
   `/home/opc/Mijual` and only for this project (its compose file's own `name: mijual`).
3. **Never commit in the operator's edge repo** (`~/projects/personal/edge/`). Apply the edits
   there; leave them uncommitted; say so. Commit nothing anywhere yourself — the orchestrator
   commits this repo.
4. **Never push.** The orchestrator never pushes either. If the box needs commits that GitHub does
   not have yet, that is an **ask** to the operator at a stop point, not an action.
5. **Secrets never enter the transcript.** No `cat .env`, no `cat .env.prod`, no
   `print(load_settings())`, no `echo $VAR` of a secret, no `docker compose config` (it expands
   `env_file` values into the output), no `set -x` around secret handling. Move values by
   **redirection and remote-side substitution** (Stage A says how). Verify presence with
   **names-only** checks (`grep -oE '^[A-Z_]+=' file` and `grep -cE '^KEY=.+' file`), never by
   printing a line that carries a value. The minted `/ops` credential is reported by **where the
   operator can read it on the box**, never by value.
6. **Reach the box only through the ssh alias `oracle-cloud`.** If the harness's permission system
   **denies** an `ssh`/`scp`/`rsync` call, do not work around it — no alternate transports, no
   reworded commands to slip past the check, no `expect`, nothing. Record "ssh denied by the
   harness at <command>" and continue with the local-only work; the stop-point report carries the
   permission ask (`Bash(ssh oracle-cloud:*)` and `Bash(scp:*)` allow rules in
   `.claude/settings.local.json`, or the operator running those commands by hand and pasting the
   output). One clean probe per dispatch is enough to learn which world you are in.
7. **The operator's dev stack on this Mac is off limits**: do not run `compose.prod.yml` locally
   in this slice at all (the local project-name collision `mijual` ↔ `mijual_mijual-pgdata` is
   real; S3 already rehearsed everything that needed a local run), do not restart `make stack-*`,
   and do not touch `frontend/.next` (the operator's `next dev` owns it).
8. **Long remote commands run detached and are polled.** The Bash tool's ceiling is 10 minutes and
   killing the ssh client SIGHUPs the remote process — a deploy killed mid-build is the worst
   outcome. Anything that can run longer than a minute on the box (the first `deploy.sh`, a
   restore, a backfill) is started as
   `ssh oracle-cloud 'cd /home/opc/Mijual && mkdir -p var && nohup env REF= deploy/deploy.sh > var/deploy-$(date +%Y%m%dT%H%M%S).log 2>&1 & echo started'`
   and then polled with `tail -n 40 var/deploy-*.log` at intervals until the script's final line
   appears. Never a foreground `deploy.sh` over ssh.
9. **Cloudflare order is load-bearing** (runbook R5): SSL/TLS **Full (Strict) FIRST**, only then
   the proxied `A` record. You do not run that console step; you verify after it and you say the
   order in the ask.

## Stage 0 — orientation (every dispatch)

1. Read `## Now`; determine the stage. Note the operator's answers recorded there (www alias,
   backup cron, corpus seed, D15) and the outstanding asks.
2. **The ssh probe**, once:
   `ssh -o BatchMode=yes -o ConnectTimeout=10 oracle-cloud 'hostname; id -un; docker --version; docker compose version'`.
   Allowed and answering → the box path is open. Denied by the harness → rule 6; the rest of this
   dispatch is local-only.
3. **Is the deploy tree on GitHub?** `git rev-parse HEAD` vs `git ls-remote origin refs/heads/main`
   (a read; not a fetch into local refs, not a push). If `origin/main` is behind, the box cannot
   clone the deploy tree until the operator pushes — an ask at STOP POINT 1, and Stage B waits
   for it. Say by how many commits (`git rev-list --count <remote-sha>..HEAD`).
4. Confirm the edge checkout is clean before you ever edit it:
   `git -C ~/projects/personal/edge status --short` must print nothing (it was clean at `390092c`
   when this plan was written). If it is dirty with someone else's work, do not touch it — report.

## Stage L — the local work (dispatch 1; safe with or without ssh)

### L1. D15 — take the R7 implementation rules off the `/ops` door

`frontend/components/ops/copy.ts` exports `DOOR_RULES_KO` (four Korean lines transcribed from the
R7 record: 「reader chrome 어디에서도 링크 금지 …」, 「자격은 배포 환경에서 발급·회전 … 가입·재설정 UI
없음」, 「실패 응답 균일 + 상수 시간 …」, 「세션 만료 → 문으로 복귀 …」), and
`frontend/components/ops/Door.tsx` renders them as 11px text under the login button. They are
implementation rules addressed to us, not copy addressed to an operator, and two of them describe
the security posture on a page that is about to be public.

- Remove the `doorRules` block from `Door.tsx`, the `DOOR_RULES_KO` export (and its import), and
  the `.doorRules` CSS in `Ops.module.css` if nothing else uses it. Leave a two-line comment in
  `copy.ts` where the export was: what was removed, that it was D15 in `P4.S4`, and that the
  rules themselves still live in the R7 record (name the record path the existing comments cite).
  Do **not** replace them with new copy — R7 wrote none for that spot and this phase drafts no
  invented ops copy.
- Verify: `cd frontend && npm run typecheck` (and `npm run lint` if the repo has it — check
  `package.json`); then in the operator's **running dev runtime** (`http://127.0.0.1:3010` — do not
  restart it): `curl -s http://127.0.0.1:3010/ops | grep -c '가입·재설정 UI 없음'` must be `0`
  (the door is server-rendered by `app/ops/layout.tsx` when no ops session is present), and a
  headful-Chrome/CDP look at `/ops` at 1280 and 390 to confirm the card closes cleanly under the
  button with no orphaned gap (the P11 fallback instrument — real Google Chrome over the DevTools
  protocol with `setDeviceMetricsOverride`; Aside's daemon is not running on this Mac and the
  manifest names no agent account). Fast Refresh picks the edit up; if it does not, say so
  rather than restarting anything.
- The Operator Question about D15 (from `P4.DECOMP`) stays on the list; note under it that the
  removal is now **applied and visible on the dev `/ops` door** for the operator to accept or
  reverse at the gate. It is the operator's own filed deferred job, so applying it is the
  proposal, and reversing it is one `git revert`.

### L2. Nothing else local yet

The edge edits (Stage C) wait for the cert: `stage.sh`'s `[2/6]` FATALs on a missing
`/home/opc/jujutower_tls/jujutower.com.crt`, so applying the diffs before R1 would break the
operator's **next hi2vi/changple edge deploy**, not ours. Do not pre-apply them.

## Stage A — R2 box prep (needs ssh; runs in dispatch 1 if ssh is open, else in dispatch 2)

Follow runbook **R2** exactly, and record the baseline **before anything else**:

- The five baseline commands (co-tenant `docker ps`, **`edge-nginx`'s `StartedAt` — write it
  down**, the 80/443 port owner, the `changple_shared_network` membership, `free -m` / `df -h
  /home` / compose version / `crontab -l`). Put the values in `result.md` **and** the ones later
  stages compare against (`StartedAt`, the port owner, the sorted co-tenant name list, `free -m`'s
  `total`/`available`, whether cron exists) into `## Now`.
- Also `docker stats --no-stream --format '{{.Name}}\t{{.MemUsage}}'` — the co-tenants' actual
  footprint, which is what the `mem_limit` tuning is really against.

**Tune the `mem_limit`s** in `compose.prod.yml` (locally, in this repo — the orchestrator commits
it and the operator's push carries it to the box). State the rule you used in a comment next to the
values: the sum of Mijual's limits must fit inside `available` minus a safety margin after the
co-tenants' measured usage, with the worker (a collection + LLM extraction pass) and Postgres given
the headroom and beat/redis/schema kept small. If `free -m` shows the placeholders already fit
comfortably, keep them and say so — a change without a reason is noise. Replace the "P4.S4 tunes
every mem_limit" placeholder comment with the measured basis.

**Clone** `https://github.com/leetusik/Mijual.git` to `/home/opc/Mijual` (`git clone`, default
branch). If Stage 0 found GitHub behind, the clone is still fine to make now — dispatch 2 does
`git -C /home/opc/Mijual pull --ff-only` once the operator has pushed. If `/home/opc/Mijual`
already exists, do not delete it; `git -C … status` and `log -1` it and continue from what is there.

**Fill `.env.prod`** — the design that keeps every value out of the transcript:

1. On this Mac, a small script in the **scratchpad** (never in the repo) builds the complete
   file from `.env.prod.example`: mint `POSTGRES_PASSWORD` (`secrets.token_urlsafe(24)`) and write
   it in **both** places (`POSTGRES_PASSWORD=` and inside `DATABASE_URL`, replacing
   `<POSTGRES_PASSWORD>`); mint `MIJUAL_SESSION_SECRET` (`token_urlsafe(48)`); mint
   `MIJUAL_OPS_PASSWORD` (`token_urlsafe(24)`) and set `MIJUAL_OPS_ID=operator`; copy
   `DART_API_KEY`, `GEMINI_API_KEY`, `MIJUAL_OPERATOR_CONTACT`, `MIJUAL_VOCKY_API_BASE`,
   `MIJUAL_VOCKY_API_KEY` from the repo-root dev `.env` (those five keys exist there — checked
   by name when this plan was written); leave `SMTP_PASS=` blank for step 3. The script prints
   only key names and a per-key `filled`/`blank` word. Output file mode 600 in the scratchpad.
2. `scp` it to `oracle-cloud:/home/opc/Mijual/.env.prod`, then `ssh oracle-cloud 'chmod 600
   /home/opc/Mijual/.env.prod'`, then **delete the scratchpad copy** (`rm -P` on macOS).
3. `SMTP_PASS` **remote-side only**: first list hi2vi's mail key **names** (`ssh oracle-cloud
   "grep -oE '^SMTP[A-Z_]*=' /home/opc/hi2vi_web/.env.prod"`) to learn the exact key (it may be
   `SMTP_PASS` or `SMTP_PASSWORD`), then substitute on the box in one remote command that reads
   the value into a shell variable and `sed`s it into place — the value never crosses to this
   Mac and never prints. Also confirm hi2vi's `SMTP_HOST`/`SMTP_PORT`/`SMTP_USER` names and
   whether their values match `.env.prod.example`'s defaults **by comparison on the box**
   (`cmp <(grep …) <(grep …)` style, printing only `same`/`different`), not by printing them.
4. Verify names-only: every key in `.env.prod.example` that must be set is non-empty
   (`grep -cE '^KEY=.+'` per key, remote), `SMTP_PASS` included; the optional ones may stay
   commented. Report the table of key → `set`/`blank`.
5. Tell the operator **where** the minted `/ops` credential is:
   `grep '^MIJUAL_OPS_' /home/opc/Mijual/.env.prod` on the box. Never paste it.

## STOP POINT 1 — return `needs_operator` (end of dispatch 1)

Before returning: update `## Now` (stage reached, the baseline values, the exact asks below),
append the new `## Operator Questions` entries (the corpus seed; the ssh permission if denied),
write `result.md`. Then return `needs_operator` with these asks, **numbered, in this order**, each
one sentence of what and why:

1. **Push `main` to GitHub** (if Stage 0 found it behind): the deploy tree (`Dockerfile.api`,
   `compose.prod.yml`, `deploy/`, the mail transport, the `mem_limit` tuning and D15 from this
   dispatch) exists only on this Mac; the box clones from GitHub. The orchestrator commits before
   this stop, so the push is one `git push` by the operator.
2. **R1 provisioning** — verbatim from `deploy/runbook.md` R1: add the zone `jujutower.com` to
   Cloudflare, switch Namecheap's nameservers to the two Cloudflare gives, wait for *Active*,
   **create no DNS record yet**, mint the Origin CA certificate (RSA, 15 years, SANs
   `jujutower.com` **plus `www.jujutower.com` only if the www alias is wanted** — the decision
   that cannot be changed later), put the pair at `/home/opc/jujutower_tls/jujutower.com.{crt,key}`
   (crt 644, key 600, `opc:opc`; the runbook's four `ssh` lines), and leave SSL/TLS mode alone.
   Report back: zone Active, the SAN list as minted, the two files with their modes, the www
   decision.
3. **The ssh permission**, only if the harness denied it: either add the allow rules or run the R2
   commands yourself and paste the output; without one of the two, dispatch 2 cannot deploy.
4. **Corpus seed — the production database starts empty.** A fresh `mijual-pgdata` has 19 tables
   and no rows; the board, the landing headline (2026년 소멸 신주인수권 가치, a snapshot over the
   year's corpus) and the gate demo mail all need the corpus. Two routes, the operator's call:
   **(recommended)** seed once from the dev database — `pg_dump -Fc` of the dev Postgres on this
   Mac, `scp` to the box, `deploy/db/restore.sh <dump> --yes` **before** R5 makes the site public,
   then decide whether to keep or truncate the dev `account` / session / conversation rows (they
   are the operator's own test data; the dump carries their hashes, so it moves once and is deleted
   from the Mac afterwards); the DART response cache (`var/dart-cache`, regenerable but quota-
   costly) can ride along the same way into the `mijual-var` volume. **Or** let beat populate the
   box from scratch — the 07:30/19:30 runs collect a rolling 14-day window under the 500-request /
   60-call ceilings, so the year's history (and the landing headline) would need capped backfill
   runs by hand over days. Ask; do not choose.
5. **Nightly backup cron** — install the runbook R7 line, or operator-run only (state whether cron
   exists, from R2).
6. **D15** — the four rule lines are off the `/ops` door on the dev runtime now; accept or
   reverse at the gate (no action needed to proceed).

The other Operator Questions on the list (mail copy, meta copy, 정정 preset, 구성원 성명) are
gate items; do not re-ask them here.

## Stage B — R3 first deploy (dispatch 2, after the push and R1; needs ssh)

1. `ssh oracle-cloud 'cd /home/opc/Mijual && git pull --ff-only && git log --oneline -1'` — the
   head must be the orchestrator's latest commit (compare to `git rev-parse HEAD` here).
2. **Corpus seed first if the operator chose it** (ask 4): dump the dev database on this Mac
   (`pg_dump -Fc` against the dev Postgres — find its URL by name from `make`/`compose.yaml`,
   never print it; the dump goes to the scratchpad, mode 600), `scp` it to
   `/home/opc/Mijual/deploy/backups/seed-<UTC>.dump` (`mkdir -p`, mode 700 dir), `rm -P` the local
   copy. The restore itself runs **after** the stack is up (step 4), because `restore.sh` needs the
   running `mijual-postgres`. If the operator asked for the cache too, `rsync` `var/dart-cache/`
   into the `mijual-var` volume's mount after the first `up` (via `docker compose cp` or a
   `docker run --rm -v mijual_mijual-var:/v` helper — check the actual volume name with
   `docker volume ls` first; under `name: mijual` it is `mijual_mijual-var`).
3. **The first deploy, detached and polled** (rule 8): `REF=` (empty — the clone is already at
   the ref), `PROJECT` and `MIJUAL_EDGE_NETWORK` **unset**. Expected in the log: both images
   built, `:previous` skipped (first deploy), `mijual-schema` exit 0, `mijual-api` healthy,
   `mijual-web` healthy, a `ps` table with six services. On failure the runbook's "what a wrong
   result looks like" applies: read the schema/postgres/api logs it dumps, fix the **cause**
   (most likely `.env.prod`), and only then re-run — never re-run blind (the hazard: the next run
   tags the broken `:latest` as `:previous`; on a first deploy there is no `:previous` yet, so
   this is the one time re-running is cheap).
4. **Seed restore** (if chosen): `deploy/db/restore.sh deploy/backups/seed-<UTC>.dump --yes`
   (detached + polled), then `schema ok` and the health gate as the script reports them. If the
   operator asked to drop the dev accounts, do it with one explicit `psql` `TRUNCATE … CASCADE`
   on the named tables **after** the restore and say exactly which tables — `account` cascades
   into sessions, portfolio rows, `notification_send`; do not truncate anything the operator did
   not name.
5. **The runbook's hand checks**, all of them: 19 tables; `mail transport: smtp …` in the API log
   (if it says `console`, `SMTP_PASS` is blank — fix and `docker compose … up -d mijual-api`
   which recreates only that service); the four beat entries via the `python -c` one-liner
   (`notify-deadlines` at `30 8 * * *` among them); the worker's `[tasks]` banner; the in-network
   `curl` from a throwaway container on `changple_shared_network` to `http://mijual-web:3010/api/health`.
6. **No-harm** (runbook R7's four assertions) — the co-tenant list, `edge-nginx`'s `StartedAt`,
   the port owner, the three public 200s — against the Stage A baseline. Any drift = stop and
   report; do not proceed to the edge.

## Stage C — R4 the edge (dispatch 2, after Stage B is healthy)

Prerequisite check, remote: both cert files exist with the right modes, and
`openssl x509 -in /home/opc/jujutower_tls/jujutower.com.crt -noout -subject -ext subjectAltName -enddate`
shows `DNS:jujutower.com` (note whether `www` is in the SAN — it decides whether the alias block in
`jujutower.conf` may be uncommented; if the operator chose www **and** the SAN has it, uncomment
per the four steps in the file; otherwise leave it commented). The key/cert pair must match
(`openssl` pubkey sha256 on both, as `stage.sh` does).

Then `deploy/edge/README.md` **exactly**: copy `jujutower.conf` into
`~/projects/personal/edge/edge/conf.d/`, apply the two diffs (`patch -p1` from the README's
blocks, or the equivalent edits — then `diff` against the README to prove they are byte-identical
in effect), `./validate.sh` **must PASS over the whole tree**. Then the loop:

- `bash stage.sh` — the runbook labels this operator-run; **this plan authorizes you to run it**:
  it is the edge repo's documented idempotent loop (rsync without `--delete`, cert staging with
  its own sha256 + pair-match gates, an on-VM `validate.sh`), and running it is not different in
  kind from the on-VM `deploy.sh` the runbook already assigns to the agent. It is an ssh-driven
  script; if the harness denies it, rule 6 applies and `stage.sh` becomes an ask.
- `ssh oracle-cloud 'cd /home/opc/edge && bash deploy.sh'` — `nginx -t` hard gate, then
  `nginx -s reload`. A failed `nginx -t` reloads nothing; read it, fix the conf in the edge
  checkout, re-run the loop from `validate.sh`.
- **Prove the origin grey** (runbook R4's two `--resolve` curls: `:80` → 301, `:443
  /api/health` → 200 + JSON) and **prove nothing else moved** (the three co-tenant 200s,
  `edge-nginx`'s `StartedAt` **identical** to the baseline, the port owner). Also
  `curl -sk --resolve … -D - -o /dev/null https://jujutower.com/` and check that
  `strict-transport-security` and `content-security-policy` are present, and a
  `POST /api/ask` (or its `GET /api/ask/start-cards` sibling) answers through the chain.
- Leave the edge checkout's edits **uncommitted** and say so in the report; the operator commits
  their repo.

## STOP POINT 2 — return `needs_operator` (end of dispatch 2)

Update `## Now` (stage C complete, the origin-grey evidence in one line, the outstanding ask),
write `result.md`, return `needs_operator` with runbook **R5 verbatim as the ask**, in its order:
(1) SSL/TLS → Full (Strict) **first**; (2) DNS → `A jujutower.com → 140.245.64.173`, **Proxied**;
(3) the two external curls to expect green; (4) HSTS stays as is. Include the failure table
(522/526/524/redirect loop). If the corpus seed was chosen, say it is in place so the site goes
public with data. Report back: the SSL/TLS mode as set and the external `curl -sI` output.

## Stage D — R5 verification and R6 product checks (dispatch 3, after the cut-over)

1. **Through Cloudflare, from this Mac**: `curl -sI https://jujutower.com/` (200 + `cf-ray`),
   `curl -s https://jujutower.com/api/health` (JSON), `curl -sI http://jujutower.com/` (a 301 to
   https — Cloudflare's or the origin's, say which), `curl -sI https://jujutower.com/robots.txt`
   (whatever exists today — S5 owns its content; just record the status), and the
   `strict-transport-security` / `content-security-policy` headers as served. Any 52x → the
   runbook table; report, do not guess.
2. **R6, in a real browser** — the instrument is the P11 fallback: **real Google Chrome over the
   DevTools protocol, headful**, with `setDeviceMetricsOverride` for 390 (Aside's daemon is not
   running on this Mac and `## Operator Runtime` names no agent account id; if `aside account
   list` answers on this dispatch and an **agent** account exists, you may use
   `aside repl --account <id>` instead — never the operator's personal profile; name whichever you
   used in `result.md`). At **`https://jujutower.com`** (the production origin — the whole point),
   1280 **and** 390:
   - **The `/ask` stream, frame by frame**: ask a real question; observe the 도구 행 appearing as
     the agent reads, prose arriving incrementally, the caret; record the number of distinct
     paint updates or SSE chunks you observed over time (page JS reading the DOM at intervals, or
     the network panel's chunk timing). **One late blob = failure** — report it as a finding, do
     not tune anything at nginx or Cloudflare yourself.
   - The board `/`, one `/stocks/{corp_code}` and one `/events/{rcept_no}` render with real data
     (only meaningful if the corpus was seeded or collected — say which).
   - The `/ops` door: log in with the credential read from the box **into a shell variable**
     (never echoed), the 개요 tab shows **four** beat entries including `notify-deadlines 08:30`,
     with 「실행 기록 없음」 for instants beat has not reached — correct, not a bug.
   - The footer's 운영자 연락처 links on a reader page (if missing: `MIJUAL_OPERATOR_CONTACT`,
     and the 10-minute footer cache).
   - **Password reset**: `POST /auth/reset/request` for an account whose address is the
     operator's own (create one on production for this if none exists, and say so) — check the
     API log for the send and the SMTP acceptance; the **receipt** is the operator's to confirm.
   - **The gate demo mail**: one `once --stages notify --no-lock --label gate-demo
     --notify-today YYYYMMDD` on `mijual-worker` with an anchor that puts a real deadline at
     D-7/3/1/0 for that same account's holdings + chips (set them up on production through the
     product if they do not exist; say what you set). Record the run's summary line (sent /
     already-sent / budget) — not the address, not the subject. A second run on the same anchor
     must report `already-sent`.
3. **No-harm again** after all of it (R7's four assertions).

## Stage E — R7 close-out, docs, notebook (dispatch 3)

1. `deploy/db/backup.sh` once, for real — the first production dump; report the file name and
   the `pg_restore --list` table count (19). Install the cron line **only if the operator said
   yes** (ask 5) and show `crontab -l` afterwards; otherwise record "operator-run only".
   Do **not** rehearse `rollback.sh` on production (no `:previous` exists after a first deploy;
   S3 rehearsed it).
2. **`## Doc impact`** — append, verbatim in shape:
   - `operations` — `## Operator Runtime` gains the **production** runtime and access path:
     origin `https://jujutower.com` (Cloudflare-proxied → `edge-nginx` → `mijual-web` container,
     production build via `deploy/deploy.sh` on the box), logs
     `docker compose -f compose.prod.yml logs <service>` in `/home/opc/Mijual`, the `/ops` door's
     credential location (path only), the browser instrument used for production checks (Chrome
     over CDP, or the Aside agent account id if one was used) at 1280 and 390. (P4.S4)
   - `operations` — Deployment: the deploy is **live** on the box as of <date>; `mem_limit`s are
     now measured values with their basis; the nightly backup decision; the edge repo carries
     `conf.d/jujutower.conf` + the two script edits (uncommitted there until the operator commits).
     (P4.S4)
   - `security` — the `/ops` door no longer prints the R7 implementation rules (D15); the
     production `/ops` credential is the minted `MIJUAL_OPS_ID`/`_PASSWORD` in the box's
     `.env.prod`; `.env.prod` and the seed dump (if any) exist on the box only. (P4.S4)
   - `product` — the `/ops` door copy change (D15) pending acceptance at the gate. (P4.S4)
   - Anything else durable you changed (the www alias if enabled; the seed's provenance).
3. **`phase.md`**: replace superseded `## Decisions` (e.g. the seed route chosen, the www
   decision, the cron decision — each as one line with its reason); drop the `## Notes for later
   slices` addressed to `P4.S4` that you consumed; add notes **(from P4.S4, for P4.S5 / P4.S6 /
   P4.S8 / P4.REVIEW)**: the live origin and what it serves today, the production `/ops`
   credential location, the seed state of the corpus, the gate demo's anchor and result, the
   browser instrument that worked against production, `robots.txt` as served by Cloudflare, the
   `www` state, and anything the review's walkthrough must include (receiving the mail; the
   stream). Rewrite `## Now` (≤ 15 lines) last.
4. `python3 scripts/workflow.py validate`. `.venv/bin/python -m pytest` is unaffected by this
   slice unless you touched `src/` — you should not have; run it anyway, it is a minute.
5. Return `done` with the verdict block: `files_changed` (this repo only — list the edge repo's
   uncommitted edits under a separate line), `validation` (every command and its outcome, per
   stage), `deviations` from this plan and from the runbook, the Doc impact list, `walkthrough:
   none` (the review builds its own).

## What "done" means for this slice

- The stack runs on the box under `compose.prod.yml` with measured `mem_limit`s, a filled
  `.env.prod` (mail transport `smtp`), 19 tables and (if chosen) the seeded corpus.
- `https://jujutower.com` answers through Cloudflare → `edge-nginx` → `mijual-web`, with the
  security headers and the `/api/ask` stream verified **in a real browser** at 1280 and 390.
- The edge repo holds `conf.d/jujutower.conf` + the two script edits, uncommitted, and
  `edge-nginx` was never recreated (its `StartedAt` unchanged from the R2 baseline).
- The first production backup exists; the cron decision is recorded and applied if yes.
- D15 is applied; the Doc impact lines (including `## Operator Runtime`'s production origin) are
  on the notebook; every co-tenant is exactly as it was.

Anything short of that at a stop point is a `needs_operator`, never a `done`.

## Dispatch 2 — operator inputs and facts as of 2026-09-02 (orchestrator addendum)

Everything STOP POINT 1 asked for is answered or done. Read this section as an override wherever
it contradicts the ladder above.

**Done, verified by the orchestrator over `ssh`/`scp` (both went through the harness cleanly):**

- **R1 is complete.** The Origin CA pair is at `/home/opc/jujutower_tls/jujutower.com.crt` (644)
  and `.key` (600), `opc:opc`, directory 700. `subjectAltName = DNS:*.jujutower.com,
  DNS:jujutower.com`, valid 2026-09-02 → 2041-08-29, key matches cert (`REMOTE PAIR OK`). The
  **wildcard covers `www`**, so the www question no longer gates anything; the alias stays **off**
  (apex canonical, the vhost's www block stays commented) unless the operator asks later.
- **Nameservers are Cloudflare's** (`mack.ns.cloudflare.com`, `rihana.ns.cloudflare.com`) and the
  zone resolves through Cloudflare, i.e. it is Active.
- **`main` is pushed.** GitHub `refs/heads/main` = `bcdde73`, which carries the whole deploy
  tree, the measured `mem_limit`s and D15. The box's clone must reach **`bcdde73` or later**
  (`git -C /home/opc/Mijual pull --ff-only`); local `HEAD` here may be one workspace-only commit
  ahead of that, which is expected and needs nothing on the box.
- **A proxied DNS record already exists** — Cloudflare imported Namecheap's parking `A` record
  (and, most likely, a `www` record) when the zone was added. Observed from outside:
  `https://jujutower.com/` → Cloudflare **522**, `http://jujutower.com/` → **302** to
  `http://www.jujutower.com/` (the parking server's behaviour). So the SSL mode is already not
  Flexible (the https fetch went to the origin's 443), and nothing on our box is being reached
  yet. Consequence for **STOP POINT 2's ask**: R5 becomes (1) SSL/TLS → **Full (Strict)** set
  explicitly, then (2) **edit** the existing `A jujutower.com` record to `140.245.64.173`,
  Proxied — not "create" — and (3) **delete the imported `www` record** (a proxied `www` pointed
  at the box with no www vhost would answer 444 → a Cloudflare 520). Write the ask that way.

**Operator decisions (2026-09-02):**

1. **Corpus seed: seed from the dev database, keeping the dev accounts.** Stage B step 2 and step 4
   apply as written: `pg_dump -Fc` of the dev Postgres on this Mac (its URL comes from
   `compose.yaml` / `Makefile` / `mijual.config` defaults — find it by name, never print it), copy
   to `/home/opc/Mijual/deploy/backups/seed-<UTC>.dump`, `rm -P` the local copy, restore with
   `deploy/db/restore.sh … --yes` **after** the stack is up and **before** the R5 ask. **Do not
   truncate anything.** Also carry the DART response cache (`var/dart-cache/` on this Mac) into
   the `mijual-var` volume — check the volume's real name with `docker volume ls` on the box first.
   Report the restored table count (19 after `schema ok`) and the row counts of `event`,
   `account` and `pipeline_run` (counts only).
2. **Nightly backup cron: install it** — the runbook R7 line at `0 4 * * *`, in dispatch 3 after
   the first real `backup.sh` run (Stage E as written). Cron exists on the box with one entry
   (changple2 certbot at 03:00).
3. **D15: applied; accept/reverse at the gate.** Nothing to do.
4. **ssh permission:** the orchestrator's `ssh oracle-cloud` and `scp` calls were allowed. No
   allow rule was added. Hard rule 6 still stands: a denial is recorded and becomes an ask, never
   worked around.

**Scope of this dispatch:** Stage 0 → Stage A steps 1–5 (`.env.prod`, as one uninterrupted
sequence — nothing was minted in dispatch 1) → Stage B (first deploy, the runbook's hand checks,
the seed restore + cache, no-harm) → Stage C (edge: copy, diffs, `validate.sh`, `stage.sh`,
on-VM `deploy.sh`, origin-grey proofs, no-harm) → STOP POINT 2 with the amended R5 ask above.
Return `needs_operator` there. Dispatch 3 remains Stage D + Stage E.

## Dispatch 3 — operator inputs and facts as of 2026-09-02 11:10 KST (orchestrator addendum)

**R5 is done for the apex** (orchestrator-verified from outside, 2026-09-02 11:09 KST):
`https://jujutower.com/` → **200**, `cf-ray` present, `strict-transport-security: max-age=300`
and `content-security-policy: upgrade-insecure-requests` served through Cloudflare;
`https://jujutower.com/api/health` → the health JSON (`now_kst` 11:09); `http://jujutower.com/` →
**301** to https. The SSL mode is therefore Full or Full (Strict) — ask the operator to confirm
which in the final report, but do not block on it.

**The operator wants the `www` alias** (answered 2026-09-02: "I want www as well"). This closes
the open Operator Question. The Origin CA cert already carries `*.jujutower.com`, so nothing is
re-minted. `www.jujutower.com` currently resolves to Cloudflare (the imported record, proxied)
and answers a Cloudflare **525** — the TLS handshake fails against whatever it points at today.

**Stage C-bis — enable www, first thing in this dispatch, before Stage D:**

1. In **this repo**, `deploy/edge/jujutower.conf`: (a) add `www.jujutower.com` to the `:80`
   server's `server_name`; (b) uncomment the `www.jujutower.com` `:443` server block (it 301s
   every request to `https://jujutower.com$request_uri` — the apex stays canonical, which is
   what `P4.S5`'s canonical/sitemap work assumes); (c) rewrite the block's header comment from
   "OPTIONAL … NOT ENABLED" to a record that it is enabled as of `P4.S4` on the operator's
   decision, cert SAN wildcard, and that the apex is canonical. Keep every house rule the file
   already states (no `default_server`, no IPv6 listen, no global names).
2. Mirror the resulting file **byte-identically** into `~/projects/personal/edge/edge/conf.d/jujutower.conf`
   (`cmp` them). Leave the edge repo uncommitted, as before.
3. Run the loop from the edge checkout: `./validate.sh` (whole tree) → `bash stage.sh` → on-VM
   `bash deploy.sh` (`nginx -t` → reload). `edge-nginx`'s `StartedAt` must stay
   `2026-07-02T19:22:12.325478595Z`.
4. Prove it grey: `curl -skI --resolve www.jujutower.com:443:140.245.64.173 https://www.jujutower.com/x?y=1`
   → **301** with `Location: https://jujutower.com/x?y=1`; and
   `curl -sI --resolve www.jujutower.com:80:140.245.64.173 http://www.jujutower.com/` → 301 to
   https (the `:80` server now matches www too — check that its redirect target is the apex or
   the same host, and say which; either lands on the apex within two hops).
5. Then through Cloudflare: `curl -sI https://www.jujutower.com/`. **If 301 → apex:** the
   record already points at the box; done. **If still 525/526/520/522:** the imported `www`
   record still points at the parking server — that is the one remaining operator action:
   **edit `www` to `A 140.245.64.173`, Proxied** (or a proxied `CNAME jujutower.com`). Put it
   in the final report as a one-line ask **and still return `done`** if everything else in
   Stage D/E passed — the vhost side is complete and verified grey, and the record edit needs no
   agent step after it. Re-check once more right before returning, in case the operator does it
   while you work.
6. Update `deploy/edge/README.md`'s www section and `deploy/runbook.md`'s open question #1 to
   record the decision (taken; apex canonical; the DNS record for www). One `## Decisions` line
   in the notebook, and a note **(from P4.S4, for P4.S5)**: `www` 301s to the apex, so the
   canonical, `metadataBase` and sitemap are apex-only.

**Then Stage D and Stage E exactly as the plan states**, with these facts: the `/ops` credential
location and the seed state are in `## Now`; the corpus is seeded (1359 events), so the board,
a 종목 page and an 이벤트 page have real data; two accounts exist from the dev seed — use the
operator's own for the reset mail and the gate demo mail if it is one of them (say which account
id, never the address), otherwise create one on production and say so. The `## Operator Runtime`
Doc impact line is owed **in this dispatch** (production origin `https://jujutower.com`, the
instrument you used, 1280 and 390). The backup cron: **install** the runbook's `0 4 * * *` line
after the first real `backup.sh`, and show `crontab -l`.

**Return `done`** when Stage C-bis, D and E are complete — with the www DNS ask, if still
outstanding, as a one-liner in the report — or `needs_operator` if Stage D finds something only
the operator can resolve.
