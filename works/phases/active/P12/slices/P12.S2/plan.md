# P12.S2 — Release P12 (S1 + F1–F10) to production — frontend-only deploy, before the 2026-09-07 11:00 KST freeze

`kind: implementation`, `risk: high` → `slice-executor-high`. One dispatch, **after the operator has
pushed `main`** — at planning time `origin/main` was still `a74c58a` (production) and every P12
commit was local, so the orchestrator stopped this slice `pending` for the push and appends the
confirmation at the end of this file before dispatching. Written 2026-09-04 by the orchestrator in
`auto` mode, after `P12.F9` (`8b54422`). Deploy freeze: **land before 2026-09-07 11:00 KST**, or
this slice waits for 09-12 and says so.

## What ships (all `frontend/`; `src/`, `deploy/`, `compose.prod.yml` untouched since `a74c58a`)

The phase's eleven fix commits, `62d78ec` … `8b54422`: `P12.S1` (the account caret — one glyph
flipped), `F1` (server-seeded account state), `F2` (the launcher in the first paint), `F3` (the
pre-hydration mirror seam + the `/portfolio` bands), `F4` (lookup holding cells reserved), `F10`
(edited-sample rows hidden pre-paint), `F5` (the logout flash reserved), `F6` (the 정정 이력 button's
one width), `F7` (the feedback dialog's one body height), `F8` (the search-miss box), `F9` (the
metric-matched mono fallback faces). Numbers per fix: `phase.md` `## Decisions`; the "before" for
production is `slices/P12.R1/result.md` (its load sweep and its cold-cache mobile table were
measured on `https://jujutower.com` itself).

Production is at `a74c58a` (`P4.S10`). Only `frontend/` changed since — verify with
`git diff --stat a74c58a..HEAD -- src deploy compose.prod.yml Makefile pyproject.toml` (empty) — so
`deploy/deploy.sh` rebuilds **`mijual-web`** and `mijual-api` is a build-cache hit, the `P4.S10`
shape: `mijual-web:previous` becomes the real rollback point (= the `a74c58a` web image) and
`mijual-api:previous == :latest`. Record both.

## Read first

- `phase.md`: `## Decisions` (every fix's line, the runtime line, the freeze line, the instrument
  seam), the shared bar, and the **two notes tagged `for P12.S2`** (F1: one new server → API
  `GET /auth/me` per signed-in page render — frontend-only, no env var, no new file; DECOMP: the
  release precedent by path) — consume both. Any `for P12.S2` note F9 added.
- The precedent, by path: `works/phases/active/P4/slices/P4.S10/plan.md` and `result.md` (§ 1
  preconditions incl. the pipeline wait, § 2 the deploy log table, § 3 the box after, the image
  table, `make smoke-prod`); `works/phases/active/P4/slices/P4.F4/result.md` § *Dispatch 2* (the
  launch line's two quirks). `deploy/runbook.md` § *R7 — the standing no-harm assertions* (~L402)
  and the freeze paragraph (~L32).

## Do

1. **Preconditions.** `git fetch origin && git rev-parse origin/main main HEAD` — all equal and
   carrying `8b54422`; box `git rev-parse HEAD` = `a74c58a`, clean tree; box clock (GMT) →
   KST; `docker compose -f compose.prod.yml exec -T mijual-worker celery -A mijual.scheduler.app
   inspect active` → `- empty -`, and **no beat window within 15 minutes** (07:30 / 19:30 / Sun
   04:30 KST — if you are inside one, wait for `succeeded` in the worker log and re-check, as
   `P4.S10` did). The four R7 no-harm assertions **before**: the three co-tenant `HTTP` 200 lines
   (`hi2vi.com`, `vocky.hi2vi.com`, `changple.ai`), `edge-nginx` `StartedAt` =
   `2026-07-02T19:22:12.325478595Z`, the `:80/:443` owner = `edge-nginx`, the sorted `docker ps`
   (28 containers at `P4.S10`). Freeze check: launch time < 2026-09-07 11:00 KST, else stop
   `needs_operator` without launching.
2. **Launch** exactly as `P4.S10` did:
   `ssh oracle-cloud 'cd /home/opc/Mijual && nohup deploy/deploy.sh > var/deploy-$(date -u +%Y%m%dT%H%M%S).log 2>&1 < /dev/null &'`
   — **no local `timeout` wrapper** (macOS has none; `P4.F4` died `exit 127`); if the local `ssh`
   is cut by the harness's Bash timeout after the remote `nohup` started, **do not relaunch** —
   confirm the remote log exists and poll it (`tail -5`, `grep -n 'DONE\|ROLLBACK\|healthy on
   poll'`) to the final line. A `ROLLBACK` is a `needs_operator` return with the log excerpt.
3. **After — the box:** the four assertions again (identical); `docker compose -f compose.prod.yml
   ps` six up + `mijual-schema` exit 0; the image table (`latest` / `previous` ids for both
   images, which half is a real rollback point); box `git rev-parse HEAD` = `8b54422`;
   `curl -s https://jujutower.com/api/health`; from the laptop `make smoke-prod` → **17/17**.
4. **After — the phase's own proofs on production, through Cloudflare, read-only, Aside
   `--account u2`** (anonymous throughout: no login, no signup, no `/api/ask` turn, no feedback
   send — a send forwards to vocky and is a write; browser storage seeded in the profile is
   browser-only and reaches no server, which is the seam's whole point):
   - **Served bytes:** the `<head>` mirror script is in every page's HTML before the stylesheet
     link; `/portfolio` carries the server-rendered 전환 제안 band and, with an edited sample seeded,
     the per-code `SampleRules` `<style>`; the served CSS carries the `.flashSlot` reservation, the
     `.historyButton::after` twin, `.noMatchStale`, the two `plexMono Fallback` families with F9's
     numbers, and **no** `local(Arial)` mono face; the launcher's `≤767 display: none` guard; the
     account slot's 로그인 link in the first HTML of every public route.
   - **The R1 load sweep, repeated as the "after"** — 10 public routes at 1280, warm cache: FCP,
     CLS, and the late-insert timeline for the account slot and the launcher (R1's table: pop-ins
     3–165 ms after FCP on production); pass = no post-paint insert of either, CLS 0 on every route
     except the landing's known star-field noise (filter it, `## Decisions`).
   - **Per fix, one reproduction each:** `/stocks?q=zzz` + one keystroke (F8: nothing below moves);
     `/events/20260806000329` 정정 이력 toggle (F6: one rect); `/stocks/00547510` with
     `sessionStorage["mijual.lookup.holdings"]` seeded for that code (F4: the with-holding row
     from the first frame, CLS 0) and `/portfolio` with `mijual.portfolio.sample` carrying one
     `removed` code (F10: the row never paints); the feedback dialog opened from the footer at 1280
     and 390 (F7: the editing state's rect — no send); `/` at 1280 (F1/F2: the link and the launcher
     in the first paint).
   - **The cold-cache mobile profile** (412×915 @ DPR 2.625, 4× CPU, ≈1.6 Mbps / 150 ms, cache
     cleared, 3 loads, medians) on `/stocks/00547510` and `/portfolio`: the Plex Mono swap moves
     **0 px** on every mono element (F9; R1's production "before": `DDay__dday` 106.13 → 92.42,
     `Lookup__cval` 113.53 → 97.20) and CLS ≈ 0 as `P4.S9` left it.
   - One paused-frame `AE = 0` of `/` at 1280 and 390 against the local production build of
     `8b54422` (the landing must be the same landing — the P4.F7/F11 constraint), with F6's
     screenshot traps respected (one capture per invocation, no `fullPage` under emulation).
5. **`phase.md`**: `## Decisions` — the batch is live (release sha, timestamp KST, log path,
   rollback point); `## Doc impact` — `operations` (Deployment: release, log path, image ids,
   which `:previous` is real, assertions identical before/after) and `qa` (the checklist gains this
   phase's production checks: the load sweep's no-pop-in line, the cold-cache mono line); consume
   the two `for P12.S2` notes (and F9's, if any); rewrite `## Now` (≤ 15 lines): released,
   **`P12.REVIEW` next — gate required, the walkthrough to come**, the nine questions and the
   review notes still to route, production sha and rollback point, the freeze line.
6. **`result.md`** verdict-block-first: the preconditions table, the deploy log table, the image
   table, the assertions before/after, `make smoke-prod`, the served-bytes checks, the load-sweep
   table, the per-fix reproductions, the cold-cache table, deviations, artefact paths.

## Hard rules

Production additive-only (never `edge-nginx`; never stop or restart anything you did not start);
ssh only via `oracle-cloud`; long remote commands via nohup + log + poll; never `cat .env.prod`; no
secret values in any file or transcript (the repo is public); no `git commit` / `push`; no workflow
state commands other than `python3 scripts/workflow.py validate`; `uv run` without `--with`; Aside
`--account u2`, never `u0`; model calls: 0; nothing inside the freeze window.

## Validate

`git diff --stat` → `phase.md` and this slice's `result.md` only; `python3 scripts/workflow.py
validate` passes; `make smoke-prod` 17/17; the R7 assertions identical before/after; the load-sweep
and cold-cache tables.

## Confirmation (orchestrator, 2026-09-04 15:09 KST)

The operator pushed `main`: `a74c58a..004d936  main -> main` (their own `git push origin main`,
run in this session). `git fetch origin && git rev-parse origin/main main HEAD` → all three
`004d936`, which carries every P12 commit through `P12.F9` (`8b54422`) plus the S2 planning commit.
The slice is cleared from `pending` back to `in_progress` on that push and dispatched now. Launch
window: it is 15:09 KST — the next beat window is the 19:30 evening pipeline, so the launch must
be **well before 19:15 KST**; if the executor cannot launch by then, it waits for the pipeline to
finish (`succeeded` in the worker log, `inspect active` empty) and launches after, still inside
today. Freeze opens 2026-09-07 11:00 KST.
