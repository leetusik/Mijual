# P4.S9 — Release the CWV batch (F5 + F6 + F8 + F10) to production — frontend-only deploy

`kind: implementation`, `risk: high`, `slice-executor-high`. One dispatch, **after the operator has
pushed `main`** (the orchestrator stops this slice `pending` for the push and appends the
confirmation below before dispatching). Deploy freeze: **must land before 2026-09-07 11:00 KST**;
otherwise it waits for 09-12.

## What ships (all `frontend/`; `src/` untouched since `1a93d7b`)

- `P4.F5` — metric-matched Korean fallback faces (`app/fonts.ts`, `app/shell.css`): cold-cache
  mobile CLS `/` 0.095 → 0.0002, `/stocks` 0.138 → 0.0003, `/ask` 0.089 → 0.0003 on the local build.
- `P4.F6` — the landing serialises a projection of `/board` (`app/page.tsx`, `lib/types.ts`,
  `components/landing/Board.tsx`, `BoardRow.tsx`): document −18 %, flight −23 %.
- `P4.F8` — the wordmark at display size + `public/` cache headers (`public/assets/*`, its README,
  `components/chrome/copy.ts`, `next.config.ts`) — see its `result.md` for the file name and TTLs.
- `P4.F10` — the event page renders 「이 마감 알림 받기 →」 from the request's session
  (`app/events/[rcept_no]/page.tsx`, `components/event/*`, `components/auth/DeadlineOffer.tsx`):
  event-page CLS 0.0325 → ≤ 0.01, no `GET /auth/me` from that page.

Because only `frontend/` changed, `deploy/deploy.sh` rebuilds **`mijual-web`** and `mijual-api` is a
build-cache hit — the `P4.S6` shape: `mijual-web:previous` becomes the real rollback point and
`mijual-api:previous == :latest` (the mirror of `P4.F4`, where it was the api half). Record both.

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
   - served CSS carries the three `notoSansKr Fallback` faces and no `local(Arial)` face
     (`curl -s -H 'Accept: text/html' https://jujutower.com/ | grep -o '/_next/static/css/[^"]*'` →
     fetch each → grep);
   - landing document bytes (`curl -s -H 'Accept: text/html' https://jujutower.com/ | wc -c`) and
     `grep -c window_state` → 0; the brotli wire size if `curl --compressed` reports it;
   - the new wordmark file is what the chrome loads (`grep -o '/assets/juju2-wordmark[^"]*'`), its
     `cache-control` through the edge is what F8 set, `/foundations/tokens.css` likewise, and
     `/_next/static/*` still a year;
   - an event page with a deadline ahead has 「이 마감 알림 받기」 in its **HTML** (`grep -c`);
   - **cold-cache mobile CLS in real headful Chrome over CDP** (throwaway profile, R1's profile:
     412×915 @ 2.625, 4× CPU, ≈1.6 Mbps / 150 ms; three loads each; `Network.clearBrowserCache`
     between) on `/`, `/stocks`, `/ask`, a live `/events/{rcept_no}` — report medians against R1's
     production baseline (0.095 / 0.138 / 0.089 / 0.033); plus one desktop load each for LCP/FCP.
     No `/api/ask` turn, no login, no writes — production is read-only for you.
4. **`phase.md`**: `## Decisions` — the batch is live (release sha, timestamp); `## Doc impact` —
   `operations` (Deployment: release, log path, image ids, which `:previous` is real, assertions
   identical, the production CWV numbers after) and `qa` (the checklist gains the production
   cold-cache CLS line with the measured values); consume the `(from P4.F5, for … P4.S9 …)` and any
   `for P4.S9` notes; rewrite `## Now` (≤ 15 lines): the batch is deployed, **`P4.REVIEW` next, from
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

## Addendum — GO (orchestrator, 2026-09-03 08:24 KST)

**The push landed**: the operator ran `git push origin main` (`1a93d7b..4aa8ddd`); `origin/main` ==
local `main` == `4aa8ddd`, which carries F5 (`70daeaf`), F6 (`a8d327b`), F8 (`fd21529`) and F10
(`4e6a921`). Re-check it yourself first. Production is at `1a93d7b` (F4's release); this deploy makes
`4aa8ddd` live. Nothing under `src/` changed since `1a93d7b`, so expect `mijual-api` to be a
build-cache hit and `mijual-web` to rebuild. The next beat window is 19:30 KST today; check it is
not within 15 minutes when you launch. Everything in **Do** and **Hard rules** above stands.

**Timing at dispatch (08:24 KST):** the beat entries are `daily-pipeline-morning` 07:30,
`notify-deadlines` **08:30**, `daily-pipeline-evening` 19:30, `weekly-resync` Sun 04:30 (all KST; the
box clock is GMT). The 08:30 mail send is minutes away and the morning pipeline may still be
finishing — do the read-only preparation first (fetch check, the four assertions before, the
image ids), then **launch no earlier than 08:45 KST and only with `inspect active` empty**; poll it
if a task is still running. Recreating the worker mid-run is exactly what this precondition exists
to prevent.
