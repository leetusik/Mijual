# P4.S10 — Release P4.F7 + P4.F11 (the landing idle-cost cut) to production — frontend-only deploy

`kind: implementation`, `risk: high`, `slice-executor-high`. One dispatch, **after the operator has
pushed `main`** (the orchestrator stops this slice `pending` for the push and appends the
confirmation below before dispatching). Deploy freeze: **must land before 2026-09-07 11:00 KST**;
otherwise it waits for 09-12.

## What ships (all `frontend/`; `src/` untouched since `1a93d7b`)

- `P4.F7` — the star twinkle on `.star::before` with literal keyframes (`components/landing/
  Cosmos.tsx`, `Cosmos.module.css`): byte-identical field, 2.4 kB less markup.
- `P4.F11` — the Hero orbiter as a composited `transform` animation (93 generated stops,
  `Hero.module.css`, provenance `frontend/scripts/gen_orbiter_keyframes.py`) on desktop and the
  **whole orbit block removed at ≤767px** (operator, 2026-09-03); the twinkles handed CSS → WAAPI
  after hydration (`components/landing/StarTwinkle.tsx`). Measured locally: `UpdateLayoutTree`
  480 → 8 per 8 s at 1280 and 390, `animationiteration` → 0, `compositeFailed` → 0, total Chrome
  CPU −25 % / −7 % over 70 s idle. Detail: `slices/P4.F11/result.md`.

Production is at `4aa8ddd` (the CWV batch, `P4.S9`). Only `frontend/` changed since, so
`deploy/deploy.sh` rebuilds **`mijual-web`** and `mijual-api` is a build-cache hit — the `P4.S9`
shape: `mijual-web:previous` becomes the real rollback point (= the `4aa8ddd` web image) and
`mijual-api:previous == :latest`. Record both.

## Do

1. **Preconditions.** `git fetch origin && git rev-parse origin/main main` equal and carrying
   `P4.F10`'s commit; `docker compose -f compose.prod.yml exec -T mijual-worker celery -A
   mijual.scheduler.app inspect active` → empty, and no beat window within 15 minutes (07:30 /
   19:30 / Sun 04:30 KST; the box clock is GMT). The four R7 no-harm assertions **before**
   (`deploy/runbook.md` § *The standing no-harm assertions*: the three co-tenant `HTTP` lines,
   `edge-nginx` `StartedAt` = `2026-07-02T19:22:12.325478595Z`, the `:80/:443` owner, the sorted
   `docker ps`).
2. **Launch** exactly as `P4.F4` did (its `result.md` § Dispatch 2 has the working line and the two
   quirks): `ssh oracle-cloud 'cd /home/opc/Mijual && nohup deploy/deploy.sh > var/deploy-$(date -u
   +%Y%m%dT%H%M%S).log 2>&1 < /dev/null &'` — **no local `timeout` wrapper** (macOS has none; F4's
   first attempt died `exit 127`), and if the local ssh is killed by the harness's Bash timeout
   after the remote `nohup` started, **do not relaunch**: confirm the remote pid/log exists and poll
   (`tail -5`, `grep -n 'DONE\|ROLLBACK\|healthy on poll' …`) to the final line. A rollback is a
   `needs_operator` return with the log excerpt.
3. **After:** the four assertions again; `docker compose -f compose.prod.yml ps` six up +
   `mijual-schema` exit 0; the image table (`latest`/`previous` ids for both images, and which half
   is a real rollback point); `curl -s https://jujutower.com/api/health`; from the laptop `make
   smoke-prod` → **17/17**. Then the batch's own proofs **on production, through Cloudflare**:
   - the served landing HTML/CSS carries F7's mechanism (grep for what `slices/P4.F7/result.md`
     names — the star paint / `will-change`, or the canvas element) and no longer the old
     `opacity: var(--star-opacity)` twinkle keyframe;
   - **the idle cost on production**: `Performance.getMetrics` deltas over a 70 s idle window on `/`
     at 1280 unthrottled and at 390 with 4× CPU (R1's baseline: 7,203 / 16,584 ms and 5,884 /
     13,100 ms RecalcStyle / Task), plus renderer + GPU process CPU sampled over the window — the
     numbers F7 measured locally must reproduce through Cloudflare;
   - one paused-frame comparison of `/` at 1280 and 390 (T = 1.3 s) against the local production
     build of the same commit — the field must be the same field;
   - a cold-cache mobile load of `/` still measures CLS ≈ 0 (one route, three loads — the batch's
     numbers are `P4.S9`'s and need no re-run), `make smoke-prod` 17/17.
     No `/api/ask` turn, no login, no writes — production is read-only for you.
4. **`phase.md`**: `## Decisions` — the batch is live (release sha, timestamp); `## Doc impact` —
   `operations` (Deployment: release, log path, image ids, which `:previous` is real, assertions
   identical, the production CWV numbers after) and `qa` (the checklist gains the production
   cold-cache CLS line with the measured values); consume the `(from P4.F5, for … P4.S10 …)` and any
   `for P4.S10` notes; rewrite `## Now` (≤ 15 lines): the batch is deployed, **`P4.REVIEW` next, from
   the top, gate stages included** — its notes are above; the gate stays shut; production sha and
   rollback point; the freeze line.
5. **`result.md`** verdict-block-first: the log table, image ids, before/after assertions, the
   production proofs and CLS table, deviations.

## Hard rules

Production additive-only (never `edge-nginx`); ssh only via `oracle-cloud`; long remote commands via
nohup + log + poll; never `cat .env.prod`; no secret values in any file or transcript (the repo is
public); no `git commit`/`push`; no workflow state commands other than `python3 scripts/workflow.py
validate`; `uv run` without `--with`; never the operator's Chrome profile; model calls: 0.

## Validate

`git diff --stat` → `phase.md` and this slice's `result.md` only; `python3 scripts/workflow.py
validate` passes; `make smoke-prod` 17/17; the R7 assertions identical before/after; the CLS table.

## Note (orchestrator, 2026-09-03, at planning)

`P4.F7` landed as commit `HEAD` of `main` at planning time; its measured effect on the landing's
idle cost is **modest** (−21 % / −31 % style recalculation, total CPU unchanged) because the real
driver — the main-thread frame the page produces on every display frame — is the Hero orbiter's
`offset-distance` animation plus the twinkles' iteration events, both outside what F7 was allowed to
touch. The operator has been asked whether to take those in a further slice (`P4.F11`); if they say
yes, the orchestrator appends that slice to **What ships** above before this deploy runs, and the
production idle-cost measurement in **Do** then has a floor worth measuring against (R1's "stars
hidden + orbiter off" line: ~20 `UpdateLayoutTree` per 8 s). Either way this slice waits for the
operator's `git push origin main` first.

## Addendum — GO (orchestrator, 2026-09-03 19:30 KST)

**Pushed**: the orchestrator ran `git push origin main` on the operator's instruction 「you deploy and
finish this phase with the report」 (`4aa8ddd..a74c58a`); `origin/main` == local `main` == `a74c58a`,
carrying F7 (`a608b86`) and F11 (`be3230b`). Re-check it yourself. This deploy makes `a74c58a` live;
production is at `4aa8ddd`.

**Timing — read this before anything else.** It is **19:30 KST**: `daily-pipeline-evening` is
starting **now** on the box. Do all read-only preparation first (fetch check, the four assertions
before, image ids), then **wait for that run to finish** — poll `docker compose -f compose.prod.yml
exec -T mijual-worker celery -A mijual.scheduler.app inspect active` until it is `- empty -` **and**
the worker log shows the evening run's final line (a `pipeline_run` row for tonight with its stages
done) — and only then launch `deploy/deploy.sh`. A run can take from a few minutes (nothing new to
extract) to ~30 min; do not launch while anything is active. The next window after that is
tomorrow 07:30 KST, hours away, so once the run is done you have all night. Only `mijual-web`
should be recreated (frontend-only release); the worker is not touched by the rebuild, but the
health gate and the image tag flip happen while the stack is live, so the rule stands.
