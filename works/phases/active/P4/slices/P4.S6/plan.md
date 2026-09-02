# P4.S6 — Production smoke suite + uptime monitoring with email alerting

Orchestrator plan, written 2026-09-02 after `P4.S5` landed (`09d56e6`). Kind `qa`, risk `high`.
Three jobs in one slice, because they share the same push-and-redeploy moment:

1. **A production smoke suite** the operator can run in one command against the public origin.
2. **External uptime monitoring with email alerting** — the intent's exact words: "email alerts via
   the `hi2vi_web` credentials, `hi@hi2vi.com` → `swangle2100@gmail.com`". The 결격 window
   (2026-09-07 11:00 → 09-11 23:59 KST, `operations.md` §Deployment) is why this is a requirement:
   an external check on the submitted URL with an alert path that reaches the operator.
3. **The redeploy that puts `P4.S5`'s SEO live**, and its five live re-checks — S5 verified on a
   local production build only and deployed nothing.

Read first: `works/phases/active/P4/phase.md` whole — especially **(from P4.DECOMP, for P4.S6)**,
**(from P4.S3, for P4.S6)**, **(from P4.S4, for P4.S6)** and **(from P4.S5, for P4.S6)** (the five
live re-checks, verbatim), and `## Now`; `works/phases/active/P4/intent.md` (the hardening Q/A);
`deploy/runbook.md` (R6, R7 and the no-harm assertions), `deploy/deploy.sh` (header: knobs,
`REF` default `origin/main`, `:previous` tagging), `deploy/README.md`;
`.github/workflows/workspace-ci.yml` (the repo's existing CI shape); the template to mirror:
`~/projects/personal/hi2vi_web/.github/workflows/synthetic-contact-probe.yml` (read-only, another
repo — curl, two attempts, off-minute cron, `permissions: contents: read`, GitHub emails the owner
on a failed scheduled run); `Makefile` (target style, lines 46–105); `scripts/` (Python scripts
live at the repo root `scripts/`, stdlib preferred); `docs/current/operations.md` §Deployment and
§Observability; `docs/current/qa.md` headings only.

## Facts you build on (verified by the orchestrator, 2026-09-02)

- **The GitHub repo `leetusik/Mijual` is PUBLIC**, default branch `main`, Actions enabled, **no
  secrets and no variables exist**, `gh` is authenticated as the operator. Public means: unlimited
  Actions minutes, and **nothing sensitive may sit in a workflow file** — the alert address, the
  SMTP host/user/password all go in **repository secrets**.
- Live and measured: `GET https://jujutower.com/api/health` → 200 + `{"status":"ok","version":…,
  "now_kst":…}`; `GET /` → 200 with `strict-transport-security` + `content-security-policy` +
  `cf-ray`; `https://www.jujutower.com/…` → 301 to the apex. **`HEAD /api/health` answers 405** —
  assert on the body of a `GET`, never on a `HEAD`. Bare `urllib` gets Cloudflare's `403 error
  1010` — always send a `User-Agent`.
- `robots.txt` / `sitemap.xml` 404 at the origin **until this slice deploys S5**; Cloudflare
  prepends its own 1,836-byte managed robots block to whatever the origin serves.
- The SMTP credentials the alert must use are already on the box in `/home/opc/Mijual/.env.prod`
  (`SMTP_HOST=mail.privateemail.com`, `SMTP_PORT=587`, `SMTP_USER=hi@hi2vi.com`, `SMTP_PASS=…`,
  STARTTLS) — proven live by S4's password-reset mail.
- Local `main` is ahead of GitHub by the S5 commit (`09d56e6`) and will be by this slice's commit
  too; **the push is the operator's**, and it is this slice's one stop.

## Hard rules

1. **No secret value ever enters your transcript.** The SMTP password moves box → GitHub in one
   pipe: `ssh oracle-cloud "grep -m1 '^SMTP_PASS=' /home/opc/Mijual/.env.prod | cut -d= -f2-" | gh secret set SMTP_PASS -R leetusik/Mijual`
   (and nothing prints it). The alert address is a fact from `intent.md` and may appear in your
   report, but goes into a secret, not the file. Verify secrets by **name** (`gh secret list`).
   Setting repository secrets on the operator's own repo is an outward-facing write that the
   monitoring ask covers — this plan authorizes exactly these: `SMTP_HOST`, `SMTP_USER`,
   `SMTP_PASS`, `SMTP_FROM`, `ALERT_TO`. Name them all in the report.
2. **Never push, never commit, never deploy before the push has happened.** Dispatch 1 ends
   `needs_operator` for the push; dispatch 2 deploys.
3. **The no-harm contract stands** (`deploy/runbook.md`): never touch `edge-nginx` or any
   container you did not start; a Mijual redeploy is `deploy/deploy.sh` on the box and nothing
   else; long remote commands run detached (`nohup … > var/deploy-<ts>.log 2>&1 &`) and are polled;
   ssh only via `oracle-cloud`; a harness denial is recorded, never worked around. Every box step
   ends with the four no-harm assertions against the R2 baseline in `## Now`
   (`edge-nginx` `StartedAt` `2026-07-02T19:22:12.325478595Z`, port owner, 22 co-tenants, network 17).
4. **Never spend on a probe.** `POST /api/ask` costs a model call; the probe and the smoke suite
   read only (`GET /api/ask/start-cards` is the free sibling). Nothing here creates a reader
   account or writes to production data.
5. **Do not touch the operator's dev stack** (`make stack-*`, `frontend/.next`), and do not run
   `compose.prod.yml` locally.
6. **Deploy freeze during the 결격 window**: this slice's redeploy happens now, days before
   2026-09-07 11:00. Record as a `## Decision` and in `deploy/runbook.md`: **no deploy between
   09-07 11:00 and 09-11 23:59 KST except `rollback.sh`** — a redeploy recreates `mijual-web` for
   a few seconds, and a single outage disqualifies.

## Deliverables

### D1. `scripts/smoke_production.py` — the operator's smoke suite

Stdlib only (`urllib`, `json`, `re`, `argparse`), one file, `--base` (default
`https://jujutower.com`), `--light` (only the two probe checks), `--no-cotenants`, a compact
PASS/FAIL table, non-zero exit on any failure, a `User-Agent` on every request, 20 s timeouts,
no redirects followed unless the check is about the redirect. Checks (each named, each one line):

- `health`: `GET /api/health` 200, JSON `status == "ok"`, `now_kst` parses and is within 10 minutes
  of now (KST) — the freshness of the process, not the corpus.
- `landing`: `GET /` 200, body contains `주주의관제탑`, headers carry `strict-transport-security`,
  `content-security-policy`, `cf-ray` (through Cloudflare, not a stale local origin).
- `www`: `GET https://www.jujutower.com/x?y=1` (derived from `--base`'s host) → 301 with
  `Location: <base>/x?y=1`.
- `http-redirect`: `http://<host>/` → 301 to https.
- `board`: `GET /api/board` 200 JSON with `rows` non-empty; pick one exposable row with a
  `rcept_no` and one `corp_code` for the next two checks.
- `event-page`: `GET /events/{rcept_no}` 200, `<title>` present and not just the bare brand.
- `stock-page`: `GET /stocks/{corp_code}` 200.
- `bad-event`: `GET /events/00000000000000` → 404, not 500.
- `start-cards`: `GET /api/ask/start-cards` 200 JSON.
- `ops-door`: `GET /ops` 200, contains 운영자 ID, and **none** of D15's four rule strings.
- `robots`: `GET /robots.txt` 200; body contains the origin's `Sitemap: <base>/sitemap.xml` line
  (Cloudflare's block may precede it).
- `sitemap`: `GET /sitemap.xml` 200; count `<loc>`; every loc starts with `<base>/`; none contain
  `www.`, `/ops`, `/auth`, `/portfolio`; count ≥ 3 static + some events.
- `manifest`: `GET /manifest.webmanifest` 200 JSON; every icon `src` fetches 200.
- `og-image`: `GET /opengraph-image.png` 200 `image/png`.
- `noindex`: `GET /auth/login` and `/portfolio` carry `<meta name="robots" content="noindex…`.
- `third-party`: the landing HTML has no `src=`/`href=` to a host other than the base host and
  `dart.fss.or.kr` (`schema.org` inside JSON-LD is a string, not a fetch).
- `cotenants` (unless `--no-cotenants`): `https://hi2vi.com/`, `https://vocky.hi2vi.com/`,
  `https://changple.ai/` → 200 — the box's other doors, the no-harm guard.

In dispatch 1 the SEO checks (`robots`, `sitemap`, `manifest`, `og-image`, `noindex`) **will fail
against production** because S5 is not deployed yet — expected; say so in the run's report and in
`result.md`. Everything else must pass in dispatch 1. A `make smoke-prod` target (Makefile style
as the existing ones) and a pointer from `deploy/runbook.md` R6 + `deploy/README.md`.

### D2. `.github/workflows/production-probe.yml` — the external monitor

Mirror hi2vi's probe (structure, comment header explaining cost and caveats, two attempts with a
pause, off-minute cron, `permissions: contents: read`, `timeout-minutes`) with these differences:

- **Cadence: every 10 minutes**, off-minute (e.g. `3,13,23,33,43,53 * * * *`). GitHub's floor is
  5 minutes and scheduled runs can lag under load — say so in the header.
- **Checks = the `--light` pair**: `GET <base>/api/health` body `"status":"ok"` and `GET <base>/`
  200 containing `주주의관제탑`, through Cloudflare, with a `User-Agent`. Use `curl` inline like the
  template (no checkout needed), **or** check out and run `scripts/smoke_production.py --light`
  — choose one and say why (the inline curl needs no checkout and cannot break when the repo does;
  the script keeps one definition of the checks).
- **`workflow_dispatch` with an input `base`** (default `https://jujutower.com`) — the failure
  drill points it at a URL that must fail (e.g. `https://jujutower.com/api/nope`) so the alert
  path is exercised without touching production.
- **The alert step, `if: failure()`**: send one mail with stdlib Python (`python3 - <<'PY' …
  smtplib … starttls()`), no third-party action: from `${{ secrets.SMTP_FROM }}` (which is
  `주주의관제탑 <hi@hi2vi.com>`, the same display name the product's mail uses) via
  `${{ secrets.SMTP_HOST }}`:587 as `${{ secrets.SMTP_USER }}` / `${{ secrets.SMTP_PASS }}`, to
  `${{ secrets.ALERT_TO }}`. Subject and body are operator-facing (not reader-facing product
  copy, so not a gate item — keep them clear; Korean or English, your call, say which): the
  failing check, the base URL, the UTC/KST time, the run URL (`${{ github.server_url }}/${{
  github.repository }}/actions/runs/${{ github.run_id }}`). GitHub's own failed-run email to the
  owner remains a second path — say so in the header.
- Optional, only if cheap and reliable: alert on **transition** (previous run green → this run
  red) plus one recovery mail, using `gh run list --workflow production-probe.yml --limit 2
  --json conclusion` with the default `GITHUB_TOKEN` (`permissions: actions: read`). If you skip
  it, say that an outage mails every 10 minutes and that this is acceptable for the window.
- Header caveats verbatim from the template: 60-day inactivity auto-disable (a push re-arms it),
  starts only once the file is on the default branch, cron lag.

### D3. The five secrets (dispatch 1, rule 1)

`SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` (piped from the box), `SMTP_FROM`, `ALERT_TO`
(`swangle2100@gmail.com`, from `intent.md`). `gh secret list -R leetusik/Mijual` afterwards shows
the five names. If `gh secret set` is denied by the harness, record it and hand the five `gh
secret set` commands to the operator as part of the stop (the password one as a pipe from the
box, so they never paste it either).

### D4. UptimeRobot — an operator to-do, not a blocker

The DECOMP note: a free UptimeRobot account cannot create monitors via the API. Write the exact
monitor for the gate walkthrough (`## Notes for later slices` **(from P4.S6, for P4.REVIEW)**):
HTTP(S) keyword monitor, URL `https://jujutower.com/api/health`, keyword `"status":"ok"`, interval
5 min, alert contact `swangle2100@gmail.com`. The Actions probe alone satisfies "monitoring with
email alerting"; UptimeRobot is the belt-and-braces second observer with its own 5-minute clock.

### D5. Docs and notebook (both dispatches; finalize in dispatch 2)

`## Doc impact`: `operations` (Observability: the probe workflow, its cadence, its five secrets by
name, the alert path, the caveats, the UptimeRobot to-do; the smoke suite and `make smoke-prod`;
the deploy freeze during the 결격 window; the S5 SEO deploy date); `qa` (the smoke suite as the
production regression instrument, and the five SEO live checks with their measured results);
`security` (five secrets live in GitHub Actions secrets on a public repo, never in a file; the
probe reads only; **note for a hardening job: `deploy/runbook.md` and `deploy/edge/README.md`
carry the box's IP, user and paths in a public repo** — not this slice's to fix, an Operator
Question / deferred-job candidate); `architecture` (Repo Shape: `scripts/smoke_production.py`,
`.github/workflows/production-probe.yml`). `## Decisions`: the alerting design (every failure vs
transition), the deploy freeze, why GitHub Actions and not a paid monitor. Notes **(from P4.S6,
for P4.REVIEW)** (the walkthrough items: the alert mail to look for, the UptimeRobot to-do, the
`make smoke-prod` command, the SEO now live) and **(for P4.S8)** (the site now has robots/sitemap/
OG live as of the deploy date; the monitoring exists). Drop the consumed `for P4.S6` notes.
Rewrite `## Now` (≤ 15 lines) last.

## Dispatch ladder

**Dispatch 1** (this one): Stage 0 orientation → D1 written and run against production (SEO checks
expected-fail, everything else pass; `--light` pass; `--no-cotenants` variant pass) → D2 written
(YAML parses; `python3 -c 'import yaml'` via `uv run --with pyyaml` if PyYAML is absent; structure
mirrors the proven template) → D3 secrets set and listed by name → D4/D5 notebook work for what is
durable now → `validate` → return **`needs_operator`** with exactly one ask: **push `main`** (the
orchestrator commits first; the push carries S5's SEO, this slice's script, the workflow and the
Makefile target). Say what dispatch 2 will do the moment the push lands.

**Dispatch 2** (after the push): Stage 0 → confirm `git ls-remote origin refs/heads/main` equals
local `HEAD` → on the box `git -C /home/opc/Mijual pull --ff-only` is **not** needed (`deploy.sh`'s
default `REF=origin/main` fetches and checks out) → **`deploy/deploy.sh` detached and polled**
(rule 3; expect `:previous` tags written, both images rebuilt, `mijual-schema` exit 0, api/web
healthy, six services) → no-harm ×4 → the **five live SEO re-checks** from the S5 note, verbatim,
plus `python3 scripts/smoke_production.py` **fully green** → the probe: `gh workflow run
production-probe.yml -R leetusik/Mijual` then `gh run watch` → green; then the **failure drill**:
`gh workflow run production-probe.yml -f base=https://jujutower.com/api/nope` → the run fails,
the alert step ran (`gh run view --log` shows the SMTP step's own success line; the mail body is
never in the log), and the operator confirms the mail at `swangle2100@gmail.com` (walkthrough
item) → D5 finalized → `validate`, `.venv/bin/python -m pytest -q` (untouched, one minute) →
return **`done`**.

## What "done" means

- `make smoke-prod` runs the suite against the live origin and is fully green, SEO included.
- `production-probe.yml` is on `main` on GitHub, has run green on schedule or dispatch, and its
  failure drill sent one alert mail through `hi@hi2vi.com` to the operator's address.
- The five secrets exist by name; nothing sensitive is in any file.
- S5's SEO is live and re-checked through Cloudflare (robots with both blocks, sitemap shape, OG
  image, an event page's head, the third-party grep).
- The UptimeRobot monitor is written up as the gate's to-do; the deploy freeze is recorded.
- `edge-nginx` untouched; co-tenants unchanged; the box left exactly as documented.

## Dispatch 2 — facts as of 2026-09-02 (orchestrator addendum)

- **The push is done:** GitHub `main` = local `HEAD` = `811dec5` (operator, `git push origin main`,
  `bcdde73..811dec5`). Everything dispatch 2 needs is on the default branch: S5's SEO, this slice's
  smoke suite, `production-probe.yml`, the Makefile target, and the `deploy/` pointers.
- **Six, not five**: the expected-failure set from dispatch 1 is `robots`, `sitemap`, `manifest`,
  `og-image`, `noindex`, **`event-page`** — all six must be green after the deploy, and
  `make smoke-prod` must exit 0 with 17/17.
- **`P4.F1` now exists** (order 6.5, after this slice, before S8): the R5-4 sample portfolio's four
  fixed issuers have aged out, and F1 makes the sample pick live issuers per state at request time.
  It will carry its **own** push + `deploy.sh` stop afterwards — do not wait for it, do not fold it
  in; this dispatch deploys `origin/main` as it is now.
- The deploy tags `:previous` first, so a bad release rolls back on its own; poll the detached log
  until the script's final summary. After it: no-harm ×4 against the R2 baseline in `## Now`.
- The failure drill uses the `workflow_dispatch` `base` input (`https://jujutower.com/api/nope`);
  the alert mail's **receipt** is the operator's to confirm (gate walkthrough item) — the log shows
  only that the SMTP step succeeded, never the message.
