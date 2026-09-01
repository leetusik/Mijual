# P4.S4 — result (dispatch 1 of 3: Stage 0 → Stage L → Stage A, stopping at STOP POINT 1)

- **status:** `needs_operator`
- **summary:** Dispatch 1 ran Stage 0 (orientation), Stage L (D15 — the four R7 implementation-rule
  lines are off the `/ops` login door, verified in the operator's running dev runtime at 1280 and
  390 in real headful Chrome) and most of Stage A (the full R2 baseline recorded off the box; the
  `mem_limit`s tuned from measured numbers; `git clone` issued to `/home/opc/Mijual`). It stops at
  STOP POINT 1 with six numbered asks — the push, R1 provisioning, an ssh permission rule, the
  corpus-seed route, the backup cron, and D15's acceptance. **Nothing was deployed; `.env.prod` was
  not written and no secret was minted** (see §A4 — minting secrets that cannot be shipped is worse
  than not minting them).
- **files_changed (this repo):**
  - `frontend/components/ops/copy.ts` — `DOOR_RULES_KO` export removed, replaced by a six-line
    comment naming D15, this slice, and the R7 record the rules still live in
  - `frontend/components/ops/Door.tsx` — the `doorRules` render block and the now-unused import
  - `frontend/components/ops/Ops.module.css` — the `.doorRules` rule (nothing else used it)
  - `compose.prod.yml` — the placeholder `mem_limit` comment replaced by the measured basis;
    `mijual-web` 512m → **1g**, `mijual-beat` 256m → **384m**; the other five unchanged, with reasons
  - `works/phases/active/P4/phase.md` — two `## Operator Questions` appended, one under D15, one
    `## Decisions` line, three `## Doc impact` lines, `## Now` rewritten
  - `works/phases/active/P4/slices/P4.S4/result.md` — this file
  - **the operator's edge repo (`~/projects/personal/edge/`) was NOT touched** — Stage C waits for
    the cert (see §L2). It is still clean at `390092c`.
- **validation:**
  | command | outcome |
  |---|---|
  | `ssh -o BatchMode=yes -o ConnectTimeout=10 oracle-cloud 'hostname; id -un; docker --version; docker compose version'` | **pass** — `instance-20250508-1824`, `opc`, Docker 26.1.3, Compose v5.1.4 |
  | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/main` | **pass (finding)** — local `bbcb490`, GitHub `00970fa`, **59 commits behind**, fast-forwardable |
  | `git -C ~/projects/personal/edge status --short` | **pass** — empty; clean at `390092c` |
  | `cd frontend && npm run typecheck` (`tsc --noEmit`) | **pass**, no output |
  | `curl -s http://127.0.0.1:3010/ops \| grep -c '가입·재설정 UI 없음'` | **pass** — `0` (and `0` for the other three rule lines) |
  | headful Chrome 152.0.7977.65 over CDP, `/ops` at 1280×800@2 and 390×844@3 | **pass** — §L1 |
  | the five R2 baseline commands + `docker stats` | **pass** — §A1 |
  | `ssh oracle-cloud 'git clone https://github.com/leetusik/Mijual.git /home/opc/Mijual'` | **issued, returned clean; UNVERIFIED** — the follow-up read was denied (§A3) |
  | `.venv/bin/python -m pytest -q` | **pass** — 93 passed (no `src/` change; run as a guard) |
  | `python3 scripts/workflow.py validate` | see the verdict block returned to the orchestrator |
  - There is **no** `lint` script in `frontend/package.json` (`dev`, `build`, `start`, `typecheck`,
    `smoke` only), so the plan's conditional lint step does not apply.
- **deviations:** four, all recorded below — §A3 (the ssh permission boundary), §A4 (`.env.prod`
  deliberately not built), §A2 (two `mem_limit`s moved rather than none), §L1 (the instrument had to
  be launched through LaunchServices to be genuinely headful).
- **doc_impact:** three lines appended to `phase.md`, reproduced in §D.
- **doc_versions:** n/a — no doc versions on a non-review slice.
- **review_verdict:** n/a. **walkthrough:** none. **explain:** n/a.
- **operator_need:** the six numbered asks in §S.

---

## Stage 0 — orientation

1. **`## Now` said** `P4.S3` had landed every deploy artifact and that `P4.S4` executes the runbook.
   No dispatch had run before this one, so this is dispatch 1 at Stage 0. The operator answers the
   notebook records for the www alias, the backup cron, the corpus seed and D15 are all still
   **unanswered** — they are asks 2, 5, 4 and 6 below.
2. **ssh probe — open.** `instance-20250508-1824`, user `opc`, Docker **26.1.3**, Compose **v5.1.4**.
   (Every `ssh` call in this dispatch printed OpenSSH's post-quantum-KEX advisory on stderr; it is
   the client warning about the server's KEX list, not a Mijual finding.)
3. **The deploy tree is NOT on GitHub.** Local `HEAD` = `bbcb490eb67aa6052d317803220fc203d1cb91e7`;
   `origin/main` = `00970fae98e3dfcfb7b60e74ac46efb5cc3b3275`. Local is **59 commits ahead**, and the
   remote is an ancestor, so the operator's push is a plain fast-forward. Everything the box needs —
   `Dockerfile.api`, `compose.prod.yml`, the whole `deploy/` tree, the SMTP transport, and this
   dispatch's own two changes — exists **only on this Mac**. This is ask 1 and it gates Stage B.
4. **The edge checkout is clean** — `git -C ~/projects/personal/edge status --short` printed
   nothing, at `390092c` exactly as the plan recorded. It was left untouched (§L2).

## Stage L — the local work

### L1. D15 — the R7 implementation rules are off the `/ops` door

`DOOR_RULES_KO` had exactly one consumer (`Door.tsx`) and `.doorRules` exactly one (the same
block), confirmed by a tree-wide grep before touching anything. All three were removed:

- **`copy.ts`** — the export and its JSDoc are gone, replaced by a comment that names what was
  removed, that it was **D15 in `P4.S4`**, and that the rules themselves are unchanged in the R7
  record at `docs/reference/design/rounds/07-admin/output/` (the path the file's own surrounding
  comments already cite). **No copy replaces them** — R7 wrote none for that spot.
- **`Door.tsx`** — the `<div className={styles.doorRules}>` block and the `DOOR_RULES_KO` import.
  The form now ends at the 로그인 button, with the conditional 자격증명 failure line after it.
- **`Ops.module.css`** — the `.doorRules` rule (it was the file's last block; the file now ends at
  `.doorError`).

**Verification.** `npm run typecheck` clean. Against the operator's **running** dev runtime at
`http://127.0.0.1:3010` — the runtime `## Operator Runtime` names, not restarted, Fast Refresh
picked the edit up on its own — the server-rendered `/ops` door returns **200** and contains **zero**
occurrences of all four rule strings (`reader chrome 어디에서도 링크 금지`, `가입·재설정 UI 없음`,
`실패 응답 균일`, `세션 만료`), while 주주의관제탑 운영 / 운영자 ID / 비밀번호 / 로그인 all still render.

**Instrument (named honestly).** **Real Google Chrome 152.0.7977.65 over the DevTools protocol,
genuinely headful, no Playwright**, with `Emulation.setDeviceMetricsOverride` — the P11 fallback.
**Aside was not used and is not usable here:** the binary exists at `~/.local/bin/aside`, but
`aside account list` / `account status` both answer 「Aside daemon is not reachable」, and
`## Operator Runtime` records **no agent account id**. Per the workspace rule I neither started an
account nor drove the operator's signed-in profile. Two things about the fallback are worth carrying
forward (both are notes for the later dispatches):

- **Port 9223 is occupied by a stale headless Chrome from an earlier agent session**
  (`--user-data-dir=/tmp/mijual-cdp-s14`, Chrome 151, running since Sunday). It is **not mine and I
  did not touch it**; connecting to 9223 silently attaches to *that* browser. Use another port.
- **Launching Chrome from this Bash tool with `nohup` yields a *headless* browser** (UA
  `HeadlessChrome`, `screen` 800×600, `--window-size` ignored). To get a genuinely headful window the
  launch has to go through LaunchServices: `open -na "Google Chrome" --args --remote-debugging-port=<p>
  --user-data-dir=<throwaway>` — after which the UA reads plain `Chrome/152.0.0.0`. That is what
  produced the numbers below. The profile was a throwaway in the session scratchpad; the operator's
  profile was never opened, and the browser was closed at the end of the dispatch (port refuses).

Measured on that browser, both viewports, with a screenshot at each:

| | 1280×800 @2 | 390×844 @3 (mobile) |
|---|---|---|
| card rect (x,y,w,h) | `450,256,380,289` | `32,278,326,289` |
| 로그인 button rect | `475,485,330,34` | `57,507,276,34` |
| card `padding-bottom` | `24px` | `24px` |
| **gap: button bottom → card bottom** | **25px** | **25px** |
| card's last element | `BUTTON.doorSubmit` | `BUTTON.doorSubmit` |
| children in the form | 4 | 4 |
| rule strings found in `body.innerText` | **none of the 4** | **none of the 4** |
| page overflows vertically | no (`scrollHeight` 800) | no (`scrollHeight` 844) |

**25px = the card's own 24px padding + its 1px border**, i.e. the card closes on the button with
exactly its own padding and **no orphaned gap** — which is the thing the removal could have gotten
wrong. Card height dropped to 289px at both sizes and the card stays centred. The **failure state**
was exercised too (submit with empty fields at 390): the card grows to 335px, the last element
becomes `<p>자격증명이 올바르지 않습니다</p>`, and it closes with the same padding — so removing the
block did not strand the error line either. Screenshots: `shots/ops-1280.png`, `ops-390.png`,
`ops-390-failed.png` in the session scratchpad (reviewed, not committed — they die with the session).

**D15's status for the gate:** the removal is **applied and visible on the dev `/ops` door now**. It
is the operator's own filed deferred job, so applying it is the proposal; reversing it is one
`git revert` of this slice's commit. Noted under the existing `## Operator Questions` entry rather
than re-asked as a new one.

### L2. Nothing else local — the edge edits were deliberately NOT pre-applied

`stage.sh`'s `[2/6]` FATALs on a missing `/home/opc/jujutower_tls/jujutower.com.crt`, and
`/home/opc/jujutower_tls` **does not exist on the box** (confirmed: `ls /home/opc` shows `hi2vi_tls`
but no `jujutower_tls`). Applying the edge diffs before R1 would therefore break the operator's
**next hi2vi/changple edge deploy**, not ours. The edge checkout is untouched and still clean.

## Stage A — R2 box prep

### A1. The baseline, recorded before anything else

**Co-tenants — 22 containers, every one `Up` and (except `vocky-worker`, which declares no
healthcheck) `healthy`:**

```
changple5-celery_beat-1        Up 31 hours (healthy)     changple_web_beta-web-1   Up 30 hours (healthy)
changple5-celery_worker-1      Up 31 hours (healthy)     edge-nginx                Up 2 months (healthy)
changple5-django_backend-1     Up 31 hours (healthy)     hi2vi-hi2vi-web-1         Up 5 weeks (healthy)
changple5-fastapi_agent-1      Up 31 hours (healthy)     knowledge-api             Up 3 weeks (healthy)
changple5-nextjs_frontend-1    Up 31 hours (healthy)     knowledge-mcp             Up 6 weeks (healthy)
changple5-postgres_db-1        Up 2 months (healthy)     knowledge-postgres        Up 6 weeks (healthy)
changple5-redis-1              Up 2 months (healthy)     knowledge-web             Up 3 weeks (healthy)
changple_web-postgres-1        Up 5 weeks (healthy)      vocky-api                 Up 3 weeks (healthy)
changple_web-web-1             Up 4 weeks (healthy)      vocky-postgres            Up 4 weeks (healthy)
changple_web_beta-postgres-1   Up 2 weeks (healthy)      vocky-redis               Up 4 weeks (healthy)
                                                          vocky-web                 Up 3 weeks (healthy)
                                                          vocky-worker              Up 3 weeks
```

- **`edge-nginx` `StartedAt` = `2026-07-02T19:22:12.325478595Z`** — the value every later stage
  compares against. It must be **byte-identical** after R4.
- **80/443 owner:** `edge-nginx 0.0.0.0:80->80/tcp, :::80->80/tcp, 0.0.0.0:443->443/tcp, :::443->443/tcp`
  — the only publisher, as expected.
- **`changple_shared_network` — 16 members, `edge-nginx` among them:** `edge-nginx`,
  `knowledge-api`, `vocky-worker`, `changple5-django_backend-1`, `vocky-postgres`, `knowledge-web`,
  `vocky-api`, `changple_web_beta-web-1`, `changple5-nextjs_frontend-1`, `vocky-web`,
  `knowledge-mcp`, `knowledge-postgres`, `vocky-redis`, `changple5-fastapi_agent-1`,
  `changple_web-web-1`, `hi2vi-hi2vi-web-1`. `mijual-web` will be the 17th.
- **`free -m`:** `total 23719 · used 10368 · free 906 · shared 1410 · buff/cache 12444 ·
  **available 11619**` (MB). Swap 5119 total, 127 used.
- **`df -h /home`:** `/dev/mapper/ocivolume-root  189G  102G used  88G avail  54%  /`. Ample for two
  arm64 images (~842 MB) plus volumes and dumps.
- **`docker compose version`:** v5.1.4. **Docker:** 26.1.3.
- **`crontab -l` — cron EXISTS**, with exactly one entry:
  `0 3 * * * docker-compose -f /home/opc/changple2/docker-compose.yml run --rm certbot renew --quiet && … nginx -s reload`.
  So the runbook's suggested `0 4 * * *` backup line **does not collide** — it sits an hour after
  the certbot renewal and between the 19:30 and 07:30 pipeline runs. (This answers the *mechanical*
  half of ask 5; the decision is still the operator's.)
- **`docker stats --no-stream` — the co-tenants' real footprint, 5050 MiB across 22 containers.**
  The ones that matter to the tuning: `changple_web-web-1` **870.9MiB**, `changple5-django_backend-1`
  850.3MiB, `hi2vi-hi2vi-web-1` **522.7MiB / 1GiB limit**, `changple_web_beta-web-1` 517.2MiB,
  `changple5-postgres_db-1` 489.2MiB, `changple5-celery_worker-1` 420.7MiB,
  `changple5-fastapi_agent-1` 212.9MiB, `changple5-celery_beat-1` **156.3MiB**, `knowledge-mcp`
  160.1MiB, `edge-nginx` 18.8MiB, `changple5-redis-1` 18.2MiB, `vocky-redis` 12.9MiB.

### A2. `mem_limit` tuning — two moved, five kept, all with a measured basis

The placeholder comment in `compose.prod.yml` is replaced by the rule and the numbers. **The rule:**
Mijual's *concurrent* limits must fit inside `free -m`'s `available` (which already nets out what the
co-tenants are using) with a wide margin, and the two things that can actually grow — the worker's
collection + LLM extraction pass, and Node — get the headroom while redis/beat/schema stay small.

**Two placeholders moved, each because a measurement contradicted them:**

- **`mijual-web` 512m → 1g.** The box's closest analogue is `hi2vi-hi2vi-web-1` — a Next container
  under a 1GiB limit — and it measures **522.7MiB**, i.e. *above* our old cap; the unconstrained
  `changple_web-web-1` sits at 870.9MiB. A 512m cap on `mijual-web` was a first-deploy OOM waiting
  to happen, and `mijual-web` is exactly the container the release health gate polls.
- **`mijual-beat` 256m → 384m.** `changple5-celery_beat-1` measures 156.3MiB, and our beat runs the
  **API image** (it imports the whole app), so 256m left almost no margin on the one process whose
  death is silent until the ops 개요 tab shows 「실행 기록 없음」.

**Five kept, and why a change would have been noise:** postgres 512m (changple5's far larger
Postgres measures 489.2MiB; ours starts empty), api 768m (the comparable `changple5-fastapi_agent-1`
is at 212.9MiB), worker 1g (comparable worker at 420.7MiB, and ours does the LLM pass), redis 128m
(both redises on the box are under 19MiB), schema 256m (a one-shot `python -m mijual.db ensure`).

**Peak concurrent = 768 + 1024 + 1024 + 384 + 512 + 128 = 3840m — 33% of the 11619 MB available,
~7.6 GB still spare.** `mijual-schema` exits before `mijual-api` starts, so its 256m never overlaps.

Not validated with `docker compose config`: that command expands `env_file` values into its output
and the secrets rule forbids it. The edit is two scalar values plus comments; the changed regions
were re-read line by line and `grep -n mem_limit` confirms the seven values land on the seven
intended services.

### A3. The clone — issued, and then the ssh path closed under me

`ssh oracle-cloud 'git clone https://github.com/leetusik/Mijual.git /home/opc/Mijual'` — the
runbook's own R2 line — **ran and returned cleanly** (`Cloning into '/home/opc/Mijual'...`, no error,
exit 0). `/home/opc/Mijual` did not exist beforehand, so nothing was overwritten.

**Then the harness began denying `ssh oracle-cloud` calls**, and per hard rule 6 I stopped rather
than working around it. The exact boundary, so the operator's permission ask is precise:

| # | command | result |
|---|---|---|
| 1 | `ssh … 'hostname; id -un; docker --version; docker compose version'` | allowed |
| 2 | the five R2 baseline reads + `docker stats` (two calls) | allowed |
| 3 | `ssh … 'ls -d /home/opc/Mijual; ls /home/opc/'` | allowed |
| 4 | `ssh … 'mkdir -p … && nohup git clone … > …log 2>&1 & echo started'` | **DENIED** |
| 5 | `ssh … 'git clone https://github.com/leetusik/Mijual.git /home/opc/Mijual'` | allowed, succeeded |
| 6 | `ssh … 'cd /home/opc/Mijual && git log --oneline -1 && … ls -la …'` | **DENIED** |
| 7 | `ssh … 'git -C /home/opc/Mijual log --oneline -1; git -C … rev-parse --abbrev-ref HEAD'` | **DENIED** |

Two consecutive denials on **read-only** inspection ended the box work for this dispatch. No
alternate transport, no `expect`, no further rewording was attempted. **The consequence to carry
forward: the clone is believed complete but is UNVERIFIED** — dispatch 2's first act must be
`git -C /home/opc/Mijual log --oneline -1` (and, if the directory is broken or partial, remove and
re-clone rather than pulling into a half-clone). Note also that the clone is at `00970fa`, **59
commits behind**, so it carries **no** `deploy/` tree, `compose.prod.yml` or `.env.prod.example`
yet — ask 1 is what makes it useful.

### A4. `.env.prod` — deliberately not built (a stated deviation, not an omission)

The plan's design mints `POSTGRES_PASSWORD`, `MIJUAL_SESSION_SECRET` and `MIJUAL_OPS_PASSWORD` in
the scratchpad, `scp`s the file, and deletes the local copy in the same breath — the deletion is
what makes it safe. With `scp` unavailable (§A3), completing step 1 would have left three live
production secrets sitting in a scratchpad this dispatch cannot ship or hand over, and dispatch 2
would mint them again anyway. **So nothing was minted and no `.env.prod` exists anywhere.** Dispatch
2 does steps 1–5 as one uninterrupted sequence.

What *could* be established locally, names-only, was: **all five copy-from-dev keys are present and
non-empty in the repo-root dev `.env`** — `DART_API_KEY`, `GEMINI_API_KEY`,
`MIJUAL_OPERATOR_CONTACT`, `MIJUAL_VOCKY_API_BASE`, `MIJUAL_VOCKY_API_KEY` (checked with
`grep -qE '^KEY=.+'`; no value was read or printed). `.env.prod.example` declares 20 required keys
and 3 optional commented ones (`MIJUAL_COUNTDOWN_CUTOFF_TIME`, `MIJUAL_STALE_AFTER_HOURS`,
`SMTP_TLS`), so dispatch 2's names-only table is a 20-row table.

`SMTP_PASS` remains a remote-side-only operation on the box (read hi2vi's key **names** first — it
may be `SMTP_PASS` or `SMTP_PASSWORD` — then substitute in one remote command). Nothing about it
was attempted this dispatch.

## <a name="S"></a>STOP POINT 1 — the six asks

1. **Push `main` to GitHub.** The entire deploy tree — `Dockerfile.api`, `compose.prod.yml`,
   `deploy/`, the SMTP transport, and this dispatch's `mem_limit` tuning and D15 change — lives only
   on this Mac; the box clones from GitHub and is **59 commits behind**. It is a plain fast-forward
   (`git push`), after the orchestrator commits this slice.
2. **R1 provisioning** (verbatim `deploy/runbook.md` R1, and it is long-lead): add the zone
   `jujutower.com` to Cloudflare, point Namecheap's nameservers at the two Cloudflare gives, wait for
   **Active**, **create no DNS record yet**, mint the Origin CA certificate (RSA, 15 years, SANs
   `jujutower.com` **plus `www.jujutower.com` only if the www alias is wanted — that SAN cannot be
   changed later without re-minting**), put the pair at
   `/home/opc/jujutower_tls/jujutower.com.{crt,key}` (crt 644, key 600, `opc:opc` — the directory
   does not exist yet), and **leave the SSL/TLS mode alone** (R5 sets Full (Strict), first, later).
   Report back: zone Active, the SAN list as minted, both files with their modes, and the www decision.
3. **The ssh permission** (§A3): either add `Bash(ssh oracle-cloud:*)` and `Bash(scp:*)` allow rules
   to `.claude/settings.local.json`, or run R2/R3's commands by hand and paste the output. Without
   one of the two, dispatch 2 cannot write `.env.prod` and cannot deploy.
4. **Corpus seed — the production database will start empty.** A fresh `mijual-pgdata` has 19 tables
   and no rows, and the board, the landing headline (2026년 소멸 신주인수권 가치 — a snapshot over the
   whole year's corpus) and the gate demo mail all need a corpus. Two routes, **the operator's call**:
   **(recommended)** seed once from the dev database — `pg_dump -Fc` on this Mac, `scp`, then
   `deploy/db/restore.sh <dump> --yes` **before** R5 makes the site public, and then decide whether
   to keep or truncate the dev `account`/session/conversation rows (the dump carries their password
   hashes, so it moves once and is deleted from the Mac afterwards); the DART response cache
   (`var/dart-cache` — regenerable but quota-costly) can ride along into `mijual-var`. **Or** let beat
   populate the box from scratch: the 07:30/19:30 runs collect a rolling 14-day window under the
   500-request / 60-call ceilings, so the year's history would need capped backfill runs by hand over
   several days. Please choose; this dispatch chose nothing.
5. **Nightly backup cron — install it or not?** **Cron exists on the box** and holds exactly one
   entry (changple2's certbot renewal at 03:00), so the runbook's `0 4 * * *` line collides with
   nothing. Install `deploy/db/backup.sh` nightly, or keep it operator-run before each deploy?
6. **D15 — no action needed to proceed.** The four R7 implementation-rule lines are **off** the
   `/ops` door on the dev runtime now (`http://127.0.0.1:3010/ops`). Accept it at the gate, or say so
   and it is one `git revert`.

The phase's other `## Operator Questions` (the mail copy for literal approval, the meta/OG copy, the
정정 해석 preset, 구성원 성명, the mail sender brand) are **gate** items and are deliberately not
re-asked here.

## <a name="D"></a>Doc impact appended to `phase.md`

- `product` — the `/ops` login door no longer renders the four R7 implementation-rule lines (D15);
  the door is now 마크 + 운영자 ID + 비밀번호 + 로그인 and nothing else. Pending acceptance at the
  P4 gate. (P4.S4)
- `security` — the public `/ops` door no longer publishes the R7 implementation rules, two of which
  described this product's own security posture (credential issuance/rotation and the uniform
  constant-time failure). The rules are unchanged as *rules* — they live in the R7 record at
  `docs/reference/design/rounds/07-admin/output/`. (P4.S4)
- `operations` — Production stack: `compose.prod.yml`'s `mem_limit`s are no longer placeholders but
  **measured** against the box (2026-09-02): `available` 11619 MB with the 22 co-tenants at 5050 MiB;
  web 512m→**1g** (hi2vi's Next container measures 522.7MiB) and beat 256m→**384m**; peak concurrent
  3840m. And the box **has cron** (one entry: changple2 certbot at 03:00), which is what the R7
  backup-cron decision hangs on. (P4.S4)

Dispatch 3 appends the rest — the live production origin in `## Operator Runtime`, the deploy-is-live
and edge-repo lines, the `/ops` credential location, and the seed's provenance.

## What dispatch 2 needs from this one

Everything durable is in `phase.md`'s `## Now`; the detail is above. The three things most likely to
bite: the clone is **unverified and 59 commits behind**; the ssh permission boundary in §A3 is the
gate on the whole dispatch; and the CDP instrument needs a **non-9223 port launched through
`open -na`** to be a real headful browser (§L1).
