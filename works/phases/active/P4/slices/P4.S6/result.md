# P4.S6 — result (dispatch 1 of 2)

- **status:** `needs_operator`
- **summary:** Built the production smoke suite (`scripts/smoke_production.py`, 17 read-only checks,
  `make smoke-prod`) and the external uptime monitor (`.github/workflows/production-probe.yml`, a
  10-minute probe that mails the operator itself over stdlib SMTP on failure), set the five
  repository secrets on `leetusik/Mijual` with the password piped box → GitHub so it never entered a
  transcript, and pointed `deploy/runbook.md` R6 + `deploy/README.md` at both. The suite ran against
  production **11 pass / 6 fail**, every failure the expected consequence of `P4.S5` not being
  deployed. Nothing was deployed, nothing on the box changed (reads only), no mail was sent.
- **files_changed:**
  - `scripts/smoke_production.py` (new)
  - `.github/workflows/production-probe.yml` (new)
  - `Makefile` (the `smoke-prod` target + header line + `.PHONY`)
  - `deploy/runbook.md` (deploy freeze; R6 opens with the smoke suite; R6 tail names the probe)
  - `deploy/README.md` (the lifecycle section names the suite)
  - `works/phases/active/P4/phase.md` (3 Decisions, 5 Doc impact, 1 Operator Question, notes pruned
    + 2 added, `## Now` rewritten)
  - `works/phases/active/P4/slices/P4.S6/result.md` (this file)
- **validation:**
  - `python3 scripts/smoke_production.py` → **11 pass / 6 fail, exit 1** — the 6 are expected (below)
  - `python3 scripts/smoke_production.py --light` → **2 pass / 0 fail, exit 0**
  - `python3 scripts/smoke_production.py --no-cotenants` → 10 pass / 6 fail (16 checks), exit 1
  - `python3 scripts/smoke_production.py --base https://jujutower.com/api/nope --light` → 2 fail,
    exit 1 (the failure path is real)
  - `make smoke-prod ARGS="--light"` → **pass**
  - YAML parse of `production-probe.yml` via `uv run --with pyyaml` → **parses**; cron, dispatch
    input, permissions, timeout and both steps confirmed
  - probe bash step extracted and run locally: green base → **rc 0**; drill base → **rc 1** and the
    right three `GITHUB_ENV` lines
  - alert python step extracted and run locally: missing-secrets branch → **exit 1, names only**;
    stubbed-SMTP dry run → message renders (no mail sent)
  - `gh secret list -R leetusik/Mijual` → **the five names**, no values
  - the four R7 no-harm assertions → **all match the R2 baseline**
  - `.venv/bin/python -m pytest` → **165 passed** (run because this dispatch inadvertently synced
    the venv — see *Deviations*)
  - `python3 scripts/workflow.py validate` → **pass**
- **deviations:** three, all small — a sixth expected failure the plan predicted as five, the
  alert-address wording in the runbook, and an inadvertent `.venv` sync. Detail below.
- **doc_impact:** five lines appended to `phase.md` — `qa` (the smoke suite as the production
  regression instrument), `operations` (Observability: the probe, its cadence, its five secret names,
  the alert path, the caveats, the UptimeRobot to-do), `operations` (Deployment: the deploy freeze +
  the R6/README pointers), `security` (the five secrets live in Actions secrets on a public repo and
  in no file; the probe reads only), `architecture` (Repo Shape: the two new files).
- **doc_versions:** n/a (no slice versions docs; a later docs phase consolidates)
- **review_verdict:** n/a
- **walkthrough:** none (not a review slice)
- **explain:** n/a
- **operator_need:** **push `main`** — one command, after the orchestrator commits. The workflow's
  schedule only starts once the file is on the default branch, and `deploy/deploy.sh` releases
  `origin/main`, so the push is what unblocks both halves of dispatch 2.

---

## D1 — `scripts/smoke_production.py` + `make smoke-prod`

Stdlib only (`urllib`, `json`, `re`, `argparse`, `datetime`), one file, no venv, so the operator can
run it from a laptop and CI can run it with no dependency step. `--base` (default
`https://jujutower.com`), `--light` (the two probe checks), `--no-cotenants`, a compact PASS/FAIL
table with per-check timings, non-zero exit on any failure. Every request sends a `User-Agent`
(bare `urllib` gets Cloudflare's `403 error 1010`), has a 20 s timeout, and — this is load-bearing —
**does not follow redirects** unless the check is about the redirect, because a followed 301 would
let `www` and `http-redirect` silently pass and would hide a redirected page behind a 200.

The no-redirect opener is a `HTTPRedirectHandler` whose `redirect_request` returns `None`; urllib
then raises the 3xx as an `HTTPError`, which carries `.code` and `.headers`, so `fetch()` returns it
as an ordinary response. That is why nothing in the file needs `try/except` around a status check.

Seventeen checks, in dependency order (`board` feeds `event-page`/`stock-page`, `landing` feeds
`third-party`, so a run costs 17 requests plus the manifest's icons):

| check | what it asserts |
|---|---|
| `health` | `GET /api/health` 200, JSON `status == "ok"`, `now_kst` parses and is within 10 min of now KST |
| `landing` | `/` 200, body carries 주주의관제탑, headers carry HSTS + CSP + `cf-ray` |
| `www` | `https://www.<host>/x?y=1` → 301 with `Location` = apex, path **and query** preserved |
| `http-redirect` | `http://<host>/` → 301 to https |
| `board` | `/api/board` 200, `rows` non-empty; picks one `exposable` row for the next two |
| `event-page` | `/events/{rcept_no}` 200, `<title>` present and **not** the bare brand |
| `stock-page` | `/stocks/{corp_code}` 200 |
| `bad-event` | `/events/00000000000000` → **404, not 500** |
| `start-cards` | `/api/ask/start-cards` 200 JSON (the free sibling of the model call) |
| `ops-door` | `/ops` 200, renders 운영자 ID, and **none** of D15's four rule strings |
| `robots` | `/robots.txt` 200 **containing the origin's own `Sitemap:` line** (Cloudflare's block may precede it) |
| `sitemap` | 200; every `<loc>` on the apex, no duplicates, no `www.`/`/ops`/`/auth`/`/portfolio`, the 3 static routes present, some `/events/` |
| `manifest` | `/manifest.webmanifest` 200 JSON, **every icon `src` fetches 200** |
| `og-image` | `/opengraph-image.png` 200 `image/png`, dimensions read from the PNG IHDR |
| `noindex` | `/auth/login` and `/portfolio` carry a `robots` meta containing `noindex` |
| `third-party` | the landing HTML has no `src=`/`href=` to a host other than the base and `dart.fss.or.kr` |
| `cotenants` | `hi2vi.com`, `vocky.hi2vi.com`, `changple.ai` → 200 — runbook R7's no-harm assertion, in code |

Everything is a GET. Nothing creates an account, writes production data or calls `POST /api/ask`
(the one endpoint that costs a model call).

### The run against production, 2026-09-02 (S5 not deployed)

```
── production smoke (full): https://jujutower.com ─────────────────────
PASS  health            365ms  200 · status=ok · v0.1.0 · now_kst 1s off
PASS  landing           873ms  200 · 339589 bytes · HSTS + CSP · cf-ray a3495b48eea484b7-HKG
PASS  www               407ms  301 → https://jujutower.com/x?y=1
PASS  http-redirect     249ms  301 → https://jujutower.com/
PASS  board             440ms  200 · 375 rows · sample 제이에스링크 20250902000288
FAIL  event-page        327ms  <title> is the bare brand: '주주의관제탑'
PASS  stock-page        290ms  200 · /stocks/00642541 (제이에스링크)
PASS  bad-event         369ms  404 (not 500)
PASS  start-cards       614ms  200 · JSON dict
PASS  ops-door          298ms  200 · 운영자 ID present · none of D15's four rule lines
FAIL  robots            260ms  the ORIGIN's own block is missing … in 1836 bytes
FAIL  sitemap           225ms  HTTP 404 (want 200)
FAIL  manifest          301ms  HTTP 404 (want 200)
FAIL  og-image          389ms  HTTP 404 (want 200)
FAIL  noindex           271ms  /auth/login has no robots meta tag
PASS  third-party        11ms  no off-origin src/href beyond dart.fss.or.kr
PASS  cotenants        1425ms  200 ×3 — hi2vi.com, vocky.hi2vi.com, changple.ai
── 11 pass · 6 fail · 7.1s ──
```

**All six failures are the same cause: `P4.S5`'s SEO code is in the repository and not on the box.**
`robots` fails against exactly 1,836 bytes — Cloudflare's managed content-signals block alone, which
is `P4.S4`'s measured number, so the origin is serving no `robots.txt` at all. `sitemap`, `manifest`
and `og-image` 404. `noindex` finds no robots meta because `P4.S5` is what adds it. And
`event-page` — the deviation below — fails for the same reason.

Every check that does **not** depend on the undeployed code passed, including the two the plan
called the probe pair, the two redirects, the `/ops` door still free of D15's four rule lines, the
third-party grep, and the three co-tenant sites.

`make smoke-prod` wraps it with an `ARGS=` passthrough, in the Makefile's existing comment-block
style. `deploy/runbook.md` R6 now **opens** with it ("the machine half of this section; the bullets
below are the half only a human with a browser can do") and `deploy/README.md` names it in the
lifecycle section, with the advice to run it *before* a release too so a red check afterwards is
attributable.

## D2 — `.github/workflows/production-probe.yml`

Mirrors `hi2vi_web`'s `synthetic-contact-probe.yml`: the same comment-header shape (what it probes,
why it is safe, cost and caveats), the same two-attempts-with-a-pause loop, an off-minute cron,
`permissions: contents: read`, a `timeout-minutes`. Differences, all deliberate:

- **Cadence `3,13,23,33,43,53 * * * *`** — every 10 minutes, off-minute. GitHub's floor is 5 minutes
  and scheduled runs lag under load; the header says so and says to treat the cadence as "about
  every 10 minutes".
- **Checks = the `--light` pair**, `GET <base>/api/health` asserting `"status":"ok"` in the **body**
  and `GET <base>/` asserting 200 + 주주의관제탑, both with a `User-Agent`. GET, never HEAD: `HEAD
  /api/health` answers 405, so a HEAD monitor would alert forever on a healthy product.
- **`workflow_dispatch` with a `base` input** (default `https://jujutower.com`) — the failure drill
  points it at `https://jujutower.com/api/nope`, exercising the alert path without touching
  production.
- **The alert step, `if: failure()`** — one mail, stdlib `smtplib`, no third-party action, 587 +
  `starttls()`, from `${{ secrets.SMTP_FROM }}` via `${{ secrets.SMTP_HOST }}` as
  `${{ secrets.SMTP_USER }}` / `${{ secrets.SMTP_PASS }}` to `${{ secrets.ALERT_TO }}`. The body
  carries the failed check, the detail, the base URL, **UTC and KST** times, the trigger, the run
  URL, and four first things to try (open `/api/health`, `make smoke-prod`, `docker compose ps` on
  the box, `deploy/rollback.sh`). The step prints only the check name, the recipient and the host —
  never the body, never the credential — and if a secret is missing it prints the missing **names**
  and exits 1, loudly, rather than failing silently.

**Inline `curl`, not the checked-out script** — the plan asked for a choice with a reason. A monitor
must go red only when the *product* is broken. A checkout would let a bad commit, a moved file or a
Python error turn the monitor red for a reason that has nothing to do with the live site, and would
add a checkout to ~4,320 runs a month. The cost is that the two checks are defined twice; they are
three lines of `curl`, and both definitions carry a "change one, change the other" comment.

**No transition/recovery logic** — an outage mails every 10 minutes until it clears. `gh run list`
inside the alert path is a second API call that can itself fail or race, which is a new failure mode
inside the one thing whose job is to be reliable. Loud is the right failure mode for the 결격
window, and GitHub's own failed-scheduled-run email to the owner remains an independent second path.

**Alert body language: English.** It is an operations artifact for the operator, not reader-facing
product copy (so not a gate copy item), and it matches every other operations artifact in this repo.

### Verified before the push, without running it on GitHub

The workflow cannot run until it is on the default branch, so both steps were extracted from the
parsed YAML and exercised locally:

- YAML parses (`uv run --no-project --with pyyaml`); cron, the dispatch input, `permissions`,
  `timeout-minutes` and both step definitions read back as intended.
- The bash step, green base → `probe OK: both checks green`, rc 0. Drill base → two attempts, then
  `PRODUCTION PROBE FAILED: health — HTTP 404 …`, rc 1, and `GITHUB_ENV` receives exactly
  `PROBE_CHECK` / `PROBE_DETAIL` / `PROBE_BASE`. (Values written to `$GITHUB_ENV` by a *failed* step
  are still exported to later steps, which is what lets the alert name the failing check.)
- The alert step with no secrets → `ALERT NOT SENT — missing repository secret(s): SMTP_HOST,
  SMTP_USER, SMTP_PASS, ALERT_TO`, exit 1. With `smtplib.SMTP` stubbed (**no mail sent**), the
  message renders with the right subject, the Korean display name in `From`, and the whole body.

## D3 — the five repository secrets

Set on `leetusik/Mijual`, which is **public** — so no address and no credential goes in any file:

| secret | how it was set |
|---|---|
| `SMTP_PASS` | `ssh oracle-cloud "grep -m1 '^SMTP_PASS=' /home/opc/Mijual/.env.prod \| cut -d= -f2-" \| tr -d '\r\n' \| gh secret set SMTP_PASS -R leetusik/Mijual` — **one pipe, box → GitHub, never printed** |
| `SMTP_HOST` | `mail.privateemail.com` |
| `SMTP_USER` | `hi@hi2vi.com` |
| `SMTP_FROM` | `주주의관제탑 <hi@hi2vi.com>` (the display name the product's own mail uses) |
| `ALERT_TO` | the operator's address from `intent.md` |

`gh secret list -R leetusik/Mijual` afterwards returns the five **names** with timestamps and no
values. Nothing was denied by the harness; `gh` was already authenticated as the operator.

Before the pipe, `SMTP_PASS`'s *shape* was checked remotely without revealing it (`len=9 quoted=no
empty=no`) so the value could be piped verbatim with no quote-stripping guesswork. The four
non-secret values were set with `--body` because each is already public in this repo
(`.env.prod.example` carries `SMTP_HOST`/`SMTP_USER`/`SMTP_FROM` verbatim) — reading them from the
box confirmed they match: `SMTP_HOST=mail.privateemail.com`, `SMTP_PORT=587`,
`SMTP_USER=hi@hi2vi.com`, `SMTP_FROM="주주의관제탑 <hi@hi2vi.com>"` (the box's quoting is stripped
for the secret, or the `From` header would be a display name with no address).

## No-harm — nothing on the box changed

This dispatch's only box contact was three read-only `ssh oracle-cloud` calls (the SMTP key shapes
and the four assertions). All four match the R2 baseline exactly:

| assertion | baseline | measured |
|---|---|---|
| `edge-nginx` `StartedAt` | `2026-07-02T19:22:12.325478595Z` | **identical** |
| `:80`/`:443` owner | `edge-nginx` | `edge-nginx 0.0.0.0:80->80/tcp, …:443->443/tcp` |
| containers up | 28 (22 co-tenants + 6 Mijual) | **28**, of which **6** `mijual-*` |
| `changple_shared_network` members | 17 | **17** |

Plus the three co-tenant sites at 200, from the smoke suite's own `cotenants` check. No container
was started, stopped or recreated; `.env.prod` was read and not written; no `psql`, no account, no
`POST /api/ask`, no mail.

## Deviations from `plan.md`

1. **Six expected failures, not five.** The plan predicted `robots`, `sitemap`, `manifest`,
   `og-image`, `noindex`. `event-page` also fails, and for the same reason: its assertion (the plan's
   own wording — "`<title>` present and **not just the bare brand**") only holds once `P4.S5`'s
   `generateMetadata` is deployed; today the root layout's bare `주주의관제탑` is the whole title.
   The check is right and was left as written; dispatch 2 expects it to read
   `제이에스링크 — 전환청구 개시 | 주주의관제탑`. **Six green, not five, is dispatch 2's bar.**
2. **The alert address is not in `deploy/runbook.md`.** The plan's D5 sketch would have had the
   runbook name `hi@hi2vi.com → <the operator's address>`; hard rule 1 says the address "goes into a
   secret, not the file", and the repo is public, so the runbook paragraph names the **secrets**
   (`ALERT_TO`) instead of the address. (The address is already in `works/**` from `intent.md`, which
   is why the new `## Operator Questions` entry exists.)
3. **The project `.venv` was inadvertently re-synced.** The first PyYAML check ran
   `uv run --with pyyaml` *inside the project*, which syncs `.venv` to `uv.lock` — it uninstalled
   four packages that were never declared in `pyproject.toml` (`ruff`, `mypy`, `aiosmtpd`,
   `alembic`, all ad-hoc installs from earlier slices) and left the declared set intact.
   Consequence checked immediately: `.venv/bin/python -m pytest` → **165 passed**, and
   `mijual`/`fastapi`/`sqlalchemy`/`celery`/`redis`/`pytest` all import. Nothing in the Makefile, CI
   or `pyproject.toml` references the four. Restore any of them with
   `uv pip install <name>` if wanted (`aiosmtpd` was `P4.S2`'s local mail sink; SMTP is proven live
   now, so it is not needed). **The correct invocation, used for every later check, is
   `uv run --no-project --with pyyaml …`** — it touches no project environment.

## What dispatch 2 does the moment the push lands

1. `git ls-remote origin refs/heads/main` equals local `HEAD`.
2. `deploy/deploy.sh` on the box, detached and polled (`REF` defaults to `origin/main`, so the
   checkout is the script's own job; a `NEXT_PUBLIC_*` change is a rebuild, which `deploy.sh` does).
3. No-harm ×4 against the same baseline.
4. `P4.S5`'s five live SEO re-checks verbatim, plus `make smoke-prod` **fully green — all 17**.
5. `gh workflow run production-probe.yml` → `gh run watch` → green.
6. The failure drill: `-f base=https://jujutower.com/api/nope` → the run fails, the alert step's own
   success line appears in `gh run view --log` (the body never does), and the operator confirms the
   mail. That confirmation is a gate walkthrough item.
7. Finalize `## Doc impact` (the SEO-live line and the qa line with the five measured results),
   `validate`, `pytest`, return `done`.
