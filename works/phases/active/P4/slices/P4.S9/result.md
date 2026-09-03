# P4.S9 — result

- **status**: `done`
- **summary**: Released the CWV batch (F5 + F6 + F8 + F10) to production as one frontend-only
  `deploy/deploy.sh` run — production now serves `4aa8ddd`, released 2026-09-03 08:45 KST with no
  rollback. Measured on production through Cloudflare in real headful Chrome over CDP against a
  same-morning baseline taken 17 minutes earlier on the same instrument: cold-cache mobile CLS
  `/` **0.0951 → 0.0000**, `/stocks` **0.1378 → 0.0003**, `/ask` **0.0893 → 0.0003**, a live event
  **0.0327 → 0.0000**; landing document **354,671 → 289,590 B (−18.3 %)** with `window_state` **465
  → 0**; the chrome loads the **6,405 b** wordmark at `max-age=31536000, immutable`; 「이 마감 알림
  받기 →」 is in the server HTML. `make smoke-prod` **17/17**, the four R7 no-harm assertions
  identical before and after, and only `mijual-web` was recreated.
- **files_changed**:
  - `works/phases/active/P4/phase.md`
  - `works/phases/active/P4/slices/P4.S9/result.md`
  (no source file was touched — this slice ships already-committed code)
- **validation**:
  | command | result |
  |---|---|
  | `git fetch origin && git rev-parse origin/main main HEAD` | **pass** — all three `4aa8ddd` |
  | box preflight: `celery -A mijual.scheduler.app inspect active` | **pass** — `- empty -`, 1 node online (twice: 08:31 and 08:45 KST) |
  | the four R7 no-harm assertions, before | **pass** — recorded below |
  | `deploy/deploy.sh` (nohup + log + poll) | **pass** — `DONE — released at ref origin/main`, no rollback |
  | `docker compose -f compose.prod.yml ps` | **pass** — six services up, `mijual-schema` `exited exit=0` |
  | the four R7 no-harm assertions, after | **pass** — byte-identical to before |
  | `curl -s https://jujutower.com/api/health` | **pass** — `{"status":"ok","version":"0.1.0",…}` |
  | `make smoke-prod` | **pass** — **17 pass · 0 fail**, 10.3 s |
  | production proofs (F5/F6/F8/F10, through Cloudflare) | **pass** — all four, tables below |
  | cold-cache mobile CLS sweep, real Chrome over CDP | **pass** — every route ≤ 0.0003 |
  | `git diff --stat` | **pass** — `phase.md` + this `result.md`, plus the orchestrator's own pre-existing `start-slice` edits |
  | `python3 scripts/workflow.py validate` | **pass** |
- **deviations**: three, all small — § *Deviations*. None changed what shipped.
- **doc_impact**: two lines appended to `phase.md` § *Doc impact* — `operations` (the release: sha,
  log path, image ids, which `:previous` is real, the assertions, the production CWV numbers) and
  `qa` (the checklist gains the production cold-cache CLS line plus F8's two header checks and the
  landing's `grep -c window_state` → 0).
- **doc_versions**: n/a (not a review slice) — deferred to a docs phase.
- **review_verdict**: n/a
- **walkthrough**: none
- **explain**: n/a
- **operator_need**: none

---

## 1. Preconditions

| check | reading |
|---|---|
| `git rev-parse origin/main main HEAD` | all three **`4aa8ddd`** — carries F5 `70daeaf`, F6 `a8d327b`, F8 `fd21529`, F10 `4e6a921` |
| box HEAD before | `1a93d7b` (F4's release), clean tree — what `deploy.sh`'s `REF=origin/main` expects |
| box clock | UTC 23:26 = **KST 08:26** (the box is GMT) |
| beat run in flight | `celery … inspect active` → **`- empty -`**, 1 node online |
| the 08:30 KST notify window | **fired and finished before the launch**: `Task mijual.notify_deadlines … received` at 08:30:00,005 and `succeeded in 0.39 s` at 08:30:00,398 (`1 account(s), 0 candidate(s) -> sent 0`) — read from the worker log, not assumed |
| the 07:30 morning pipeline | already complete (nothing active) |
| next beat window | `daily-pipeline-evening` **19:30 KST** — 10.7 h after the launch |
| launch gate | plan says **no earlier than 08:45 KST**; launched **08:45:31 KST** |
| deploy freeze | opens 2026-09-07 11:00 KST — this landed **four days early** |

**The four R7 no-harm assertions, BEFORE** (2026-09-03 08:26 KST):

| assertion | reading |
|---|---|
| co-tenants | `hi2vi.com` · `vocky.hi2vi.com` · `changple.ai` → **HTTP/2 200 ×3** |
| `edge-nginx` `StartedAt` | **`2026-07-02T19:22:12.325478595Z`** |
| `:80` / `:443` owner | **`edge-nginx`** (`0.0.0.0:80->80, :::80->80, 0.0.0.0:443->443, :::443->443`) |
| sorted `docker ps` | **28 containers** (22 co-tenants + 6 Mijual), all `Up … (healthy)` except `vocky-worker` and `mijual-mijual-beat-1`, which carry no healthcheck; `changple_shared_network` **17 members** |

Full listing saved outside the repo (`scratchpad/s9_ps_before.txt`).

## 2. The deploy

```sh
ssh oracle-cloud 'cd /home/opc/Mijual && nohup deploy/deploy.sh > var/deploy-20260902T234531.log 2>&1 < /dev/null &'
# launched pid=2994449   (2026-09-03 08:45:31 KST = 2026-09-02 23:45:31 UTC)
```

No local `timeout` wrapper (macOS has none — `P4.F4`'s `exit 127`). The launch `ssh` returned
cleanly, so the "do not relaunch" branch was never needed.

Log `/home/opc/Mijual/var/deploy-20260902T234531.log`, **287 lines**, ~90 s:

| step | evidence (line) |
|---|---|
| baseline captured | `edge-nginx StartedAt before: 2026-07-02T19:22:12.325478595Z` (1) |
| checkout | `1a93d7b..4aa8ddd  main -> origin/main`; `HEAD is now at 4aa8ddd` (5–7) |
| rollback points | `tagging mijual-api:latest -> mijual-api:previous` (8), `… mijual-web …` (9) |
| build-arg asserts | `MIJUAL_API_ORIGIN` = `http://mijual-api:8010`, `NEXT_PUBLIC_SITE_URL` = `https://jujutower.com` — both non-empty (147, 150) |
| both images built | `naming to docker.io/library/mijual-api:latest done` (125), `… mijual-web:latest done` (220); the Next build itself is `#38 DONE 18.7s` |
| recreate set | **`mijual-web` Recreate → Recreated`; `postgres`, `redis`, `api`, `worker`, `beat` all `Running`** |
| schema one-shot | `mijual-mijual-schema-1 Exited`; `docker inspect` → **`exited exit=0`** |
| health gate | `mijual-web healthy on poll 7` (259), `mijual-api healthy on poll 1` (260) |
| verdict | `deploy healthy — mijual-api:latest + mijual-web:latest are live` (261) |
| worker | `not gated, reported: mijual-worker = healthy` (262) |
| edge assertion (in-script) | `ok — edge-nginx StartedAt unchanged (2026-07-02T19:22:12.325478595Z)` (286) |
| final | `DONE — released at ref origin/main` (287) |

`grep -c 'ROLLBACK'` over the log → **0**. Box `git rev-parse HEAD` after → **`4aa8ddd`**.

### Image table — and which half is a real rollback point

| image | before | after | rollback value |
|---|---|---|---|
| `mijual-api:latest` | `e0a479095f7b` | **`e0a479095f7b`** (unchanged — full build-cache hit) | — |
| `mijual-api:previous` | `caac2ad1e440` | **`e0a479095f7b`** (retagged to the same id) | **NO-OP** — flipping it changes nothing |
| `mijual-web:latest` | `b82aaa9c5b20` | **`028b480a7b37`** (rebuilt) | — |
| `mijual-web:previous` | `b82aaa9c5b20` | **`b82aaa9c5b20`** | **THE REAL ROLLBACK POINT** — the pre-CWV `1a93d7b` image |

Exactly the `P4.S6` shape and the **mirror of `P4.F4`**, where the api half was the live one: nothing
under `src/` changed since `1a93d7b`, so the api image was a cache hit and `mijual-api:previous` now
points at the running image.

**One thing worth recording because it confirms an earlier finding rather than contradicting it.**
`P4.F4` saw `mijual-postgres` recreated on a release whose image never moved, and attributed it to
its own `.env.prod` append (compose hashes the `env_file` into every service that carries one). This
release edited **no** `.env.prod` line — and postgres, redis, api, worker and beat all stayed
`Running`, with only `mijual-web` recreated. That is the control experiment for F4's explanation, and
it passes. The API's startup line is still the one from 8 h ago
(`mail transport: smtp mail.privateemail.com:587 tls=starttls …`), because the api container was
never restarted.

## 3. After — the box

**The four R7 no-harm assertions, AFTER** (08:47 KST) — identical to before on all four:

| assertion | before (08:26) | after (08:47) |
|---|---|---|
| co-tenants | 200 ×3 | **200 ×3** |
| `edge-nginx` `StartedAt` | `2026-07-02T19:22:12.325478595Z` | **identical** |
| `:80`/`:443` owner | `edge-nginx` | **`edge-nginx`**, same port map |
| `docker ps` | 28 containers, network 17 | **28 containers, network 17** |

The container **name set** diffs clean, and the whole sorted `docker ps` differs in exactly **one
line** — `mijual-mijual-web-1  Up 15 hours (healthy)` → `Up About a minute (healthy)`, i.e. the one
container a frontend-only release is supposed to recreate. `edge-nginx` was named by no command but
`docker inspect`.

```
mijual-api        mijual-api:latest   Up 8 hours (healthy)
mijual-beat       mijual-api:latest   Up 8 hours
mijual-postgres   postgres:16         Up 8 hours (healthy)
mijual-redis      redis:7             Up 22 hours (healthy)
mijual-schema     mijual-api:latest   Exited (0) About a minute ago
mijual-web        mijual-web:latest   Up About a minute (healthy)
mijual-worker     mijual-api:latest   Up 8 hours (healthy)
```

`curl -s https://jujutower.com/api/health` →
`{"status":"ok","version":"0.1.0","now_kst":"2026-09-03T08:47:17+09:00"}`

### `make smoke-prod` — 17 pass · 0 fail (10.3 s)

All 17 green from the laptop. Three lines moved with the corpus and the batch, not with a
regression: `landing … 289090 bytes` (was 354,671 pre-deploy — that is F6), `board 394 rows`,
`sitemap 832 URLs (465 events)`. `www` passed. `third-party` names both allowed hosts
(`dart.fss.or.kr`, `static.cloudflareinsights.com`) and found nothing else.

## 4. The batch's own proofs, on production, through Cloudflare

Before at **08:32 KST** (pre-deploy) and after at **08:47 KST**, same commands.

### F5 — the Korean fallback faces are the ones being served

| reading | before | after |
|---|---|---|
| `notoSansKr Fallback…` families in the served CSS | **1** — `notoSansKr Fallback` (Next's generated one) | **3** — `notoSansKr Fallback Apple` · `… Malgun` · `… Noto` |
| `@font-face` blocks carrying `local(Arial)` | `notoSansKr Fallback` **and** `plexMono Fallback` | **`plexMono Fallback` only** |
| distinct `local(...)` names | 1 | 24 (the eight Apple SD Gothic Neo names, the eight Noto names, the six Malgun names, plus Plex Mono's Arial) |
| served CSS bytes (4 chunks) | 126,752 | 128,802 (**+2,050 B** — the three families) |

The surviving `local(Arial)` is the deliberate one: `font-display`/metrics for **Plex Mono**, whose
Latin numerals Arial matches correctly. The defect face — `notoSansKr Fallback` with
`src: local(Arial)` and no Hangul — is gone from production.

### F6 — the landing serialises a projection

| reading | before | after | delta |
|---|---|---|---|
| landing document | **354,671 B** | **289,590 B** | **−65,081 B / −18.3 %** |
| `window_state` occurrences | **465** | **0** | — |
| wire, brotli (`Accept-Encoding: br`) | 40,188 B | 37,111 B | **−3,077 B / −7.7 %** |
| wire, `curl --compressed` | 43,026 B | 39,569 B | −3,457 B |

The board grew by ~1 row between the two reads (the smoke suite counts 394), so the byte delta is
approximate at the last hundred; the `window_state` count is exact and is the load-bearing number.
The wire saving is again **~3 KB**, matching F6's own correction of the R1 estimate.

**And the refresh still works on the real payload.** A 70 s landing session in the browser made
exactly **one** `/api/board` request; the board held **15 rows before and after** it; and
`window.onerror`, `unhandledrejection` and `console.error` were **all empty**. 갱신됨 stayed 0
because the corpus itself did not move (기준 2026-09-03 07:31 KST) — correct behaviour, not a missed
refresh.

### F8 — the display-size wordmark and `public/`'s own cache lifetimes

| path | before | after |
|---|---|---|
| chrome's wordmark ref | `/assets/juju2-wordmark-white.png` · **21,920 b** · `max-age=14400` | **`/assets/juju2-wordmark-white-273-73c23508.png`** · **6,405 b** · **`public, max-age=31536000, immutable`** |
| `/foundations/tokens.css` | `public, max-age=14400` | **`public, max-age=604800, stale-while-revalidate=86400`** |
| `/assets/juju2-symbol-white.png` (fixed name) | `public, max-age=14400` | **`public, max-age=604800, stale-while-revalidate=86400`** |
| `/_next/static/chunks/*.css` | `public, max-age=31536000, immutable` | **unchanged** |

**−15,515 b per cold load**, and Cloudflare honoured the origin `Cache-Control` exactly as F8
predicted — no edge cache rule was needed and none was added (`cf-cache-status: MISS` on the first
hit of the brand-new name, as expected).

Rendered on production in real Chrome, both viewports:

```
src="/assets/juju2-wordmark-white-273-73c23508.png"  natural 273×81  complete=true
box 91×27   alt="주주의관제탑"   transform: matrix(1, 0, 0, 1, 0, -8)
```

**91.000 px** is F8's predicted nav width (was 90.75) and the only value that moved. Full-page
screenshots at 390 and 1280 were taken and eyeballed: the chrome, the cosmos backdrop, the hero, the
검색 box, the 소멸 가치 card and the live countdown all render as designed.

### F10 — the offer line is in the server HTML

| page | state | before | after |
|---|---|---|---|
| `/events/20260806000329` (툴젠) | 매매 마감 **D-4** | `grep -c '이 마감 알림 받기'` = **0** | **1** |
| `/events/20250902000288` (제이에스링크) | 전환청구 개시 **D-DAY** | **0** | **1** |
| `/events/20260623000409` (경남제약) | **추후결정** (no date) | 0 | **0** |
| `/events/20260713000482` (아시아나항공) | **추후결정** (no date) | 0 | **0** |

The deadline-ahead gate is intact — the line appears only where a date exists. Live at 390 the page
carries exactly **one** such control, reading 「이 마감 알림 받기 →」. The **logged-in** variant was
deliberately not exercised (production is read-only for an agent); it is a walkthrough item.

### The off-origin host set is unchanged

Across all **16** instrumented cold loads (4 routes × mobile ×3 + desktop ×1) the only
non-`jujutower.com` host is **`static.cloudflareinsights.com`** — the operator-enabled beacon. The
property the phase signs still holds on the new build.

## 5. Cold-cache CWV on production — the table

**Instrument:** real **Google Chrome 152.0.7977.65**, headful, launched through LaunchServices with
a **throwaway profile** (`scratchpad/chrome-s9`) on CDP port **9393** — never the operator's Chrome
profile — driven from `scratchpad/s9_cls.py` over `P4.R1`'s `r1_cdp.py` client, reused unchanged.
Aside is the workspace default instrument; this workspace has no Aside account, so the documented
fallback (a real browser, same viewports, same runtime) was used, exactly as `P4.R1`, `P4.F2`,
`P4.F5` and `P4.F10` did. **Runtime and access path:** `https://jujutower.com` through Cloudflare —
the deployed production origin, which is the surface this slice exists to change. R1's mobile
profile: **412×915 @ DPR 2.625, 4× CPU, ≈1.6 Mbps / 150 ms**, `Network.clearBrowserCache` +
`setCacheDisabled` per load, fresh tab per load, 9 s settle; desktop 1280×800 @ DPR 1, unthrottled,
5 s settle. Mobile is 3 loads per route (median), desktop 1.

**Both columns are measurement.** The before column is a **same-morning production sweep at 08:28
KST**, 17 minutes before the deploy, on this same instrument — it reproduced `P4.R1`'s production
baseline to four decimals, which is what makes the after column a paired comparison rather than a
comparison against a quotation.

### Mobile, cold cache — CLS (medians of 3)

| route | R1 baseline | this slice, before (08:28) | **after (08:49)** | verdict |
|---|---|---|---|---|
| `/` | 0.095 | **0.0951** | **0.0000** | ✅ |
| `/stocks` | 0.138 | **0.1378** | **0.0003** | ✅ |
| `/ask` | 0.089 | **0.0893** | **0.0003** | ✅ |
| `/events/20260806000329` | 0.033 | **0.0327** | **0.0000** | ✅ |

Every run is stable to four decimals across its three loads (before: 0.0951 ×3, 0.1378 ×3, 0.0893
×3, 0.0327 ×3; after: 0.0000 ×3, 0.0003 ×3, 0.0003 ×3, 0.0000 ×3). **No shift ≥ 0.002 was recorded
on any after-load, on any route** — the `shifts` column is empty everywhere, where before it named
`content page-module__…` on the landing and `Footer-module__…` on `/stocks` and `/ask` at ~3.2–3.7 s,
i.e. the font-swap moment. The landing's 0.0000 is better than F5's local prediction (0.0002) and the
event page's 0.0000 better than F10's (0.0003).

### Mobile FCP / LCP (medians of 3) — LCP == FCP on every load, as in R1

| route | before FCP/LCP | after FCP/LCP | delta |
|---|---|---|---|
| `/` | 1640 ms | **1544 ms** | −96 ms |
| `/stocks` | 1472 ms | **1420 ms** | −52 ms |
| `/ask` | 1380 ms | **1336 ms** | −44 ms |
| `/events/…329` | 1356 ms | **1296 ms** | −60 ms |

The landing's −96 ms is larger than F6's local −16 ms, but three of the four routes moved by a
similar amount and only the landing was touched by F6 — so most of this is **F8's 15.5 KB** off a
1.6 Mbps link plus ordinary network variance, not F6. Treat these as directionally good, not as a
measured attribution: TTFB on these loads ranges 107–648 ms and is the dominant term.

### Desktop (1 load each)

| route | before CLS | after CLS | before FCP/LCP | after FCP/LCP |
|---|---|---|---|---|
| `/` | 0.0001 | **0.0001** | 576 ms | 688 ms |
| `/stocks` | 0.0001 | **0.0001** | 560 ms | 548 ms |
| `/ask` | 0.0000 | **0.0000** | 400 ms | 452 ms |
| `/events/…329` | **0.0105** | **0.0000** | 288 ms | 384 ms |

The one CLS that mattered on desktop — the event page's 0.0105 — is **0.0000**, better than F10's
local 0.0017 (F5's Plex Mono residual did not appear in this run). **The desktop FCP column is a
single load per route and TTFB-dominated (143–414 ms); the +112 / +52 / +96 ms swings are network
noise and must not be read as a regression** — the mobile column, which is a median of three under a
fixed throttle, is the one to quote.

## 6. Deviations

1. **A same-morning production "before" sweep the plan did not ask for.** The plan said to report
   the after medians against R1's baseline. Two extra sweeps were run first — mobile ×3 and desktop
   ×1 on the *pre-deploy* production build — during the mandated wait for the 08:45 launch window.
   Read-only, cost nothing but the wait that was already required, and it upgrades every number in
   § 5 from "compared with last night's figures" to a paired same-instrument comparison. It also
   independently reproduced R1's baseline, which is a useful check on R1 itself.
2. **Two extra negative checks on F10.** The plan asked for one event page with a deadline ahead.
   Two deadline-ahead pages (D-4 and D-DAY) and two **추후결정** pages were checked, because "the
   line is present" is only half of F10's claim — the other half is that the gate still withholds it
   where there is no date. No past-dated event exists in the board's ranked rows to check the third
   state, so that state is unverified on production (it is verified locally in `P4.F10`).
3. **Two extra liveness checks beyond the plan's list**: the 70 s board-refresh session (§ 4, F6) and
   the two full-page screenshots (§ 4, F8). Both are read-only navigations. The refresh check exists
   because F6's projection is the one change in this batch that could break a behaviour rather than
   a measurement, and it had only ever been proved on the local build.

Nothing was skipped. The one plan item that could not be executed as written is noted in § 4 (F10's
logged-in variant), and it was excluded by the plan's own "no login, no writes" rule rather than by
circumstance.

## 7. What this slice did not do

- **No code changed.** `git diff --stat` is `phase.md` and this `result.md` (plus the orchestrator's
  own pre-existing `start-slice` / plan-addendum edits to `works/`). This slice ships code that was
  already committed and pushed.
- **No commit, no push, no workflow state command** other than `python3 scripts/workflow.py validate`.
- **No hand edit on the box.** `deploy/deploy.sh` did all of it. `.env.prod` was neither edited nor
  `cat`'d; **no environment value of any kind was read this slice**, so no secret appears here or in
  any transcript. `edge-nginx` was addressed by nothing but `docker inspect`.
- **Production stayed read-only in the browser**: no `/api/ask` turn, no login, no `/ops` session
  (the `P4.F4` boundary — an ops login mints an `OpsSession` row), no writes of any kind. The
  throwaway Chrome profile was created for this slice and its process was closed at the end.
- **No doc version.** Two `## Doc impact` lines were appended to `phase.md` instead; nothing under
  `docs/` was touched.
- **Model spend: 0.** No pipeline run, no LLM call.

## 8. Artefacts (all outside the repo, in the session scratchpad)

`s9_cls.py` (the production sweep, over `P4.R1`'s `r1_cdp.py`, reused unchanged) +
`s9_cls_{before,beforeD,after,afterD}.jsonl`; `s9_proofs.sh` + `s9_landing_{before,after,after2}.html`,
`s9_css_{before,after,after2}.css`, `s9_ev_*_{before,after}.html`; `s9_shot.py` +
`s9_after_landing_{390,1280}.png`; `s9_live.py` and `s9_refresh2.py` (the F10 live render and the
60 s refresh session) + `s9_after_event_390.png`; `s9_ps_{before,after}.txt` (the two `docker ps`
snapshots); `chrome-s9/` (the throwaway profile). The deploy log stays on the box at
`/home/opc/Mijual/var/deploy-20260902T234531.log`.
