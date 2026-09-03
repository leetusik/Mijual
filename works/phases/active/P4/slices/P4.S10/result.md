# P4.S10 — result

- **status**: `done`
- **summary**: Released the landing idle-cost batch (`P4.F7` + `P4.F11`) to production as one
  frontend-only `deploy/deploy.sh` run — production now serves **`a74c58a`**, released
  2026-09-03 19:47 KST with no rollback, after tonight's 19:30 evening pipeline had finished
  (`daily-evening` succeeded 19:31:02, `celery inspect active` `- empty -` twice). Measured on
  production through Cloudflare in real headful Chrome over CDP against a same-evening baseline
  taken 15 minutes earlier on the same instrument: over 70 s idle on `/`, style recalculation
  **6.235 → 0.416 s** at 1280 and **5.021 → 0.153 s** at 390 + 4× CPU, main-thread task
  **13.604 → 1.154 s** and **10.528 → 0.478 s**, **total Chrome CPU 32.20 → 22.30 s (−31 %)** and
  **60.94 → 56.96 s (−6.5 %)**; in an 8 s trace `UpdateLayoutTree` **480 → 14 / 480 → 8**,
  `animationiteration` **453/294 → 0**, `compositeFailed` **1 → 0**. The served CSS lost
  `offset-distance`/`offset-path` and gained the 93-stop `translate` orbit; the twinkle keyframes
  are literals; `[data-twinkle=waapi]` is live. The paused star field is **byte-identical** to the
  local production build of the same commit at 1280 and 390 (`AE = 0`, equal sha256). At 390 the
  hero renders **no orbit at all**. `make smoke-prod` **17/17**, the four R7 no-harm assertions
  identical before and after, cold-cache mobile CLS on `/` **0.0000 ×3**, and only `mijual-web` was
  recreated.
- **files_changed**:
  - `works/phases/active/P4/phase.md`
  - `works/phases/active/P4/slices/P4.S10/result.md`
  (no source file was touched — this slice ships already-committed code)
- **validation**:
  | command | result |
  |---|---|
  | `git fetch origin && git rev-parse origin/main main HEAD` | **pass** — all three `a74c58a` (F7 `a608b86`, F11 `be3230b`) |
  | evening-pipeline wait: worker log + `celery … inspect active` | **pass** — `daily-evening` succeeded 19:31:02 (62.4 s); `- empty -` at 19:31 and 19:46:52 KST |
  | the four R7 no-harm assertions, before | **pass** — recorded in § 1 |
  | `deploy/deploy.sh` (nohup + log + poll) | **pass** — `DONE — released at ref origin/main`, `grep -c ROLLBACK` = 0 |
  | `docker compose -f compose.prod.yml ps` | **pass** — six services up, `mijual-schema` `exit=0` |
  | the four R7 no-harm assertions, after | **pass** — identical; the sorted `docker ps` differs in exactly one line |
  | `curl -s https://jujutower.com/api/health` | **pass** — `{"status":"ok","version":"0.1.0",…}` |
  | `make smoke-prod` | **pass** — **17 pass · 0 fail**, 10.5 s |
  | served markup + CSS markers (F7 + F11), before vs after | **pass** — table in § 4 |
  | 70 s idle windows on `/`, 1280 and 390 + 4× CPU, medians of 3 | **pass** — table in § 5 |
  | 8 s `blink.animations` trace, both viewports | **pass** — § 5, `compositeFailed` 0, `animationiteration` 0 |
  | paused star-field frames, production vs local production build | **pass** — `AE = 0`, equal sha256, both viewports |
  | cold-cache mobile CLS on `/`, 3 loads | **pass** — 0.0000 ×3, no shift ≥ 0.002 |
  | `git diff --stat` | **pass** — `phase.md` + this `result.md`, plus the orchestrator's own pre-existing `works/` edits |
  | `python3 scripts/workflow.py validate` | **pass** |
- **deviations**: four, all small — § *Deviations*. None changed what shipped.
- **doc_impact**: two lines appended to `phase.md` § *Doc impact* — `operations` (the release: sha,
  log path, image ids, which `:previous` is real, the assertions, the production idle-cost numbers)
  and `qa` (the checklist gains the landing idle-cost line and the production cold-cache CLS on `/`).
- **doc_versions**: n/a (not a review slice) — deferred to a docs phase.
- **review_verdict**: n/a
- **walkthrough**: none
- **explain**: n/a
- **operator_need**: none

---

## 1. Preconditions, and the wait the plan imposed

| check | reading |
|---|---|
| `git rev-parse origin/main main HEAD` | all three **`a74c58a`** — carries `P4.F7` (`a608b86`) and `P4.F11` (`be3230b`) |
| box HEAD before | **`4aa8ddd`** (the CWV batch, `P4.S9`), clean tree — what `deploy.sh`'s `REF=origin/main` expects |
| box clock | UTC 10:31 = **KST 19:31** (the box is GMT) |
| **the 19:30 evening pipeline** | **finished before anything was launched**: `mijual.daily_pipeline` received **19:30:00,003**, `succeeded in 62.36 s` at **19:31:02,368** — `label daily-evening`, `ok: True`, 101 requests, **0 calls**, stages collect→snapshot all `ok`. Read from the worker log, not assumed. |
| `celery … inspect active` | **`- empty -`**, 1 node online — checked at **19:31** and again at **19:46:52**, immediately before the launch |
| next beat window | `daily-pipeline-morning` **07:30 KST tomorrow** — 11.7 h after the release |
| deploy freeze | opens 2026-09-07 11:00 KST — this landed **four days early** |

**The four R7 no-harm assertions, BEFORE** (2026-09-03 19:33 KST):

| assertion | reading |
|---|---|
| co-tenants | `hi2vi.com` · `vocky.hi2vi.com` · `changple.ai` → **HTTP/2 200 ×3** |
| `edge-nginx` `StartedAt` | **`2026-07-02T19:22:12.325478595Z`** |
| `:80` / `:443` owner | **`edge-nginx`** (`0.0.0.0:80->80, :::80->80, 0.0.0.0:443->443, :::443->443`) |
| sorted `docker ps` | **28 containers**; `changple_shared_network` **17 members** |

Full listing outside the repo (`scratchpad/s10_ps_before.txt`).

## 2. The deploy

```sh
ssh oracle-cloud 'cd /home/opc/Mijual && nohup deploy/deploy.sh > var/deploy-20260903T104712.log 2>&1 < /dev/null &'
# launched pid=331200  (2026-09-03 19:47 KST = 10:47 UTC)
```

No local `timeout` wrapper (macOS has none — `P4.F4`'s `exit 127`). The launch `ssh` returned late
(~64 s, with most of the run already done); it was **not** relaunched — the remote log was polled to
its final line instead, which is exactly the branch the plan describes.

Log `/home/opc/Mijual/var/deploy-20260903T104712.log`, **280 lines**, ~85 s:

| step | evidence |
|---|---|
| baseline captured | `edge-nginx StartedAt before: 2026-07-02T19:22:12.325478595Z` |
| checkout | `4aa8ddd..a74c58a  main -> origin/main`; `HEAD is now at a74c58a` |
| rollback points | `tagging mijual-api:latest -> mijual-api:previous`, `… mijual-web …` |
| build-arg asserts | `MIJUAL_API_ORIGIN` = `http://mijual-api:8010`, `NEXT_PUBLIC_SITE_URL` = `https://jujutower.com` — both non-empty |
| both images built | `naming to docker.io/library/mijual-api:latest done`, `… mijual-web:latest done`; the Next build itself `#38 DONE 19.6s` |
| recreate set | **`mijual-web` Recreate → Recreated**; `postgres`, `redis`, `api`, `beat`, `worker` all `Running` |
| schema one-shot | `mijual-mijual-schema-1 Exited`; `docker inspect` → **`exit=0`** |
| health gate | `mijual-web healthy on poll 7`, `mijual-api healthy on poll 1` |
| verdict | `deploy healthy — mijual-api:latest + mijual-web:latest are live`; `not gated, reported: mijual-worker = healthy` |
| edge assertion (in-script) | `ok — edge-nginx StartedAt unchanged (2026-07-02T19:22:12.325478595Z)` |
| final | `DONE — released at ref origin/main` |

`grep -c ROLLBACK` over the log → **0**. Box `git rev-parse HEAD` after → **`a74c58a`**.

### Image table — and which half is a real rollback point

| image | before | after | rollback value |
|---|---|---|---|
| `mijual-api:latest` | `e0a479095f7b` | **`e0a479095f7b`** (unchanged — full build-cache hit) | — |
| `mijual-api:previous` | `e0a479095f7b` | **`e0a479095f7b`** (same id) | **NO-OP** — flipping it changes nothing |
| `mijual-web:latest` | `028b480a7b37` | **`a9195a0c0689`** (rebuilt) | — |
| `mijual-web:previous` | `b82aaa9c5b20` | **`028b480a7b37`** | **THE REAL ROLLBACK POINT** — the `4aa8ddd` CWV image |

The `P4.S9` shape again, exactly as the plan predicted: nothing under `src/` has changed since
`1a93d7b`, so the api image was a cache hit and `mijual-api:previous` still points at the running
image. `deploy/rollback.sh` therefore returns the **frontend** to the CWV batch and leaves the API
where it is. Note that the pre-CWV rollback point (`b82aaa9c5b20`) is no longer reachable through
`rollback.sh`; going back further is `REF=<sha> deploy/deploy.sh`, per runbook R7.

## 3. After — the box

**The four R7 no-harm assertions, AFTER** (19:49 KST) — identical to before on all four:

| assertion | before (19:33) | after (19:49) |
|---|---|---|
| co-tenants | 200 ×3 | **200 ×3** |
| `edge-nginx` `StartedAt` | `2026-07-02T19:22:12.325478595Z` | **identical** |
| `:80`/`:443` owner | `edge-nginx` | **`edge-nginx`**, same port map |
| `docker ps` | 28 containers, network 17 | **28 containers, network 17** |

The container **name set** is identical, and the whole sorted `docker ps` differs in exactly **one
line** — `mijual-mijual-web-1  Up 11 hours (healthy)` → `Up About a minute (healthy)`, i.e. the one
container a frontend-only release is supposed to recreate. `edge-nginx` was named by no command but
`docker inspect`. `api`, `beat`, `worker` and `postgres` all still read `Up 19 hours`, `redis`
`Up 33 hours` — no `.env.prod` line changed, so nothing with an `env_file` moved (the control
`P4.S9` established).

`curl -s https://jujutower.com/api/health` →
`{"status":"ok","version":"0.1.0","now_kst":"2026-09-03T19:49:22+09:00"}`

### `make smoke-prod` — 17 pass · 0 fail (10.5 s)

All 17 green from the laptop. `landing 286998 bytes` (289,231 pre-deploy), `board 394 rows`,
`sitemap 832 URLs (465 events)`, `www` 301, `third-party` names exactly the two allowed hosts.

## 4. What production now serves — the mechanism, before vs after

Fetched through Cloudflare: `GET /` plus the four `/_next/static/chunks/*.css` files the landing
declares (`scratchpad/s10_markup.sh`, `s10_markers.py`).

| reading | before (`4aa8ddd`) | after (`a74c58a`) |
|---|---|---|
| landing document | 289,231 B | **287,139 B** (−2,092 B) |
| the route's CSS (4 chunks) | 128,806 B | **114,420 B** (−14,386 B) |
| `offset-distance` in the CSS | **2** | **0** |
| `offset-path` in the CSS | **1** | **0** |
| `@keyframes …orbit` body | `{0%{offset-distance:0%}to{offset-distance:100%}}` | **93 `translate` stops**, opening `{0%{transform:translate(-492.5px,-2.5px)}.3095%{transform:translate(-492px,4.1px)}…` |
| `@keyframes …twinkle` body | `{0%,to{opacity:var(--star-opacity)}50%{opacity:calc(var(--star-opacity) * .28)}}` | **`{0%,to{opacity:1}50%{opacity:.28}}`** (F7's literals) |
| `.star::before` rules | 0 | **3** |
| `[data-twinkle=waapi]` rule | 0 | **1** |
| `--star-duration` / `--star-delay` in the HTML | 0 / 0 | **480 / 480** |
| `data-starfield` in the HTML | 0 | **2** |
| `--star-opacity` in the HTML | 480 | 480 (unchanged — the base alpha never moved) |

Two things worth naming. The minifier rewrites `translate3d(x,y,0)` → `translate(x,y)`, exactly as
`P4.F11` recorded, and `compositeFailed` is still 0 with it (§ 5). And the CSS **shrank by 14.4 kB**
even though the orbit keyframes add 4.2 kB — the chunk regroup `P4.F11` predicted (−14,466 B
locally, −14,386 B here), because the landing no longer downloads `Portfolio.module`.

## 5. The idle cost on production, through Cloudflare

**Instrument.** Real **Google Chrome 152.0.7977.65**, headful, launched with a **throwaway profile**
(`scratchpad/chrome-s10`) on CDP port **9394**, driven from `scratchpad/s10_idle.py` over `P4.F7`'s
own harness `f7_cdp.py`, reused unchanged — never the operator's Chrome profile. Aside is the
workspace's default instrument; this workspace has no Aside account and its daemon does not run on
this Mac, so the documented fallback (a real browser, same viewports, the manifest runtime) was used
— as in `P4.R1`, `P4.F2`, `P4.F5`, `P4.F7`, `P4.F10`, `P4.F11` and `P4.S9`. **Runtime and access
path:** `https://jujutower.com` through Cloudflare, the deployed production origin. Profiles are
`P4.F7`/`P4.F11`'s: **1280×800 DPR 1 unthrottled** and **390×844 DPR 3 with 4× CPU**. One navigation
per window, 9 s load + 3 s settle, then a **70 s** window with no interaction at all.

**Both columns are measurement.** The before column is a **same-evening production sweep at
19:34–19:43 KST**, 4–13 minutes before the deploy, on this same instrument — so this is a paired
comparison, not a comparison against a quotation. It also independently reproduces `P4.R1`'s
production baseline (7.2 s / 16.6 s at 1280 and 5.9 s / 13.1 s at 390) to within the same order.

### 70 s idle on `/`, medians of 3 windows

| | 1280 unthrottled | | 390 + 4× CPU | |
|---|---|---|---|---|
| | before (`4aa8ddd`) | **after (`a74c58a`)** | before | **after** |
| style recalculation | 6.235 s | **0.416 s (−93 %)** | 5.021 s | **0.153 s (−97 %)** |
| recalc count | 4,200 | **204 (−95 %)** | 4,200 | **138 (−97 %)** |
| main-thread task | 13.604 s | **1.154 s (−92 %)** | 10.528 s | **0.478 s (−95 %)** |
| script | 0.167 s | 0.045 s | 0.114 s | 0.025 s |
| renderer process CPU | 22.17 s | **9.01 s (−59 %)** | 58.48 s | **54.87 s (−6 %)** |
| GPU process CPU | 9.94 s | 13.16 s (**+32 %**) | 2.43 s | 2.04 s (−16 %) |
| **TOTAL Chrome CPU** | 32.20 s | **22.30 s (−31 %)** | 60.94 s | **56.96 s (−6.5 %)** |

Run-to-run spread is small: at 1280 the three after windows read 0.354 / 0.416 / 0.455 s of
recalculation and 22.30 / 22.19 / 22.83 s of total CPU; at 390, 0.144 / 0.153 / 0.162 s and
56.97 / 56.95 / 56.96 s.

**This reproduces `P4.F11`'s local numbers through Cloudflare**, which is what the plan asked: F11
measured 0.417 s / 0.152 s of recalculation and 1.196 s / 0.485 s of task on local production
builds; production reads 0.416 s / 0.153 s and 1.154 s / 0.478 s. The two honest readings F11
recorded hold here too — **the GPU process takes back part of what the renderer saved at 1280**
(+3.2 s against −13.2 s; the net is still −31 %), and **the phone's remaining 57 s is the
compositing of 160 star layers**, not style (F7 measured the stars-removed floor at 56.0 s, so this
is within 2 % of it while keeping every star).

### 8 s `blink.animations` trace (`scratchpad/s10_trace.py`)

| reading | 1280 before | **1280 after** | 390 before | **390 after** |
|---|---|---|---|---|
| `UpdateLayoutTree` per 8 s | **480** (683.4 ms) | **14** (22.3 ms) | **480** (512.6 ms) | **8** (10.7 ms) |
| `animationiteration` dispatches | **453** | **0** | **294** | **0** |
| `compositeFailed` animations | **1** | **0** | **1** | **0** |
| running animations | 247 | 247 | 165 | **164** |
| rendered stars / shooters | 240 / 5 | 240 / 5 | 160 / 3 | 160 / 3 |
| `.orbits` computed `display` | `block` | `block` | `block` | **`none`** |
| field `data-twinkle` | (absent) | **`waapi`** | (absent) | **`waapi`** |

The note's live-check bar — 「0 `compositeFailed`, 0 `animationiteration`, `UpdateLayoutTree`
≤ ~30」 — is met at both viewports, and the single `compositeFailed` the before column shows is the
orbiter's `offset-distance`, now gone. 165 → 164 animations at 390 is the orbit block's own
animation, which a `display: none` element does not run.

## 6. 「Same effect」, on production

**Paused star-field frames** (`scratchpad/s10_frames.py`, `P4.F11`'s own technique): everything but
`[data-motion="tick"] .field` hidden, every animation paused at **T = 1.3 s**, full-viewport
screenshot, at 1280 and 390.

| comparison | 1280 | 390 |
|---|---|---|
| **production vs the local production build of the same commit** | **`AE = 0`** (equal sha256) | **`AE = 0`** (equal sha256) |
| control: production vs production, second load | `AE = 0` | `AE = 0` |

All three PNGs at each viewport hash to one value (`cbcb6075…` at 1280, `eb605b21…` at 390), so the
field production paints *is* the field `P4.F11` proved byte-identical off-box. 247 animations were
paused at 1280 and 164 at 390 on every target. The local build served for this comparison is
`P4.F11`'s own `f11af` tree, diffed against the repo at `a74c58a` first (identical but for the
generated `next-env.d.ts`), served with `node .next/standalone/server.js` on 3015 and stopped
afterwards.

**What the landing actually renders** (`scratchpad/s10_live.py`, one navigation per viewport,
full-page screenshots kept):

| reading | 1280 | 390 |
|---|---|---|
| stars in the DOM / visible | 240 / **240** | 240 / **160** (the ≤480px cut) |
| shooters in the DOM / visible | 5 / **5** | 5 / **3** |
| `.orbits` computed `display` | **`block`** | **`none`** — no star, no rings |
| orbiter animation | **`Hero-module__…__orbit 26s`**, `offset-path: none` | same declaration, inside the hidden block |
| hero | h1 「내 종목 조회」 at (512.2, 248.2), search form present | h1 at (111.5, 116.0), search form present |
| board rows / `scrollHeight` | 16 / 2154 | 16 / 2826 |
| page errors (`error`, `unhandledrejection`) | **none** | **none** |

Both screenshots were looked at: at 1280 the two ellipse rings and the orbiting star are there and
the whole page renders as designed; at 390 the hero is title, subtitle, search row and stat line
with **no orbit ink at all**, which is the operator's own call. One caveat recorded so the JSON is
not misread: the probe's `orbiterVisible` / `ringsVisible` read the element's own computed style, so
they say `true` at 390 — the load-bearing reading is `.orbits` = `display: none`, which paints
nothing (`P4.F11` measured 14,498 px of ink → 0 off-box).

**Cold-cache mobile CLS on `/`** (`scratchpad/s10_cls.py` over `P4.R1`'s `r1_cdp.py`, cache cleared
per load, 412×915 @ 2.625, 4× CPU, ≈1.6 Mbps / 150 ms, 3 loads):

| load | CLS | FCP = LCP | TTFB | document |
|---|---|---|---|---|
| #0 | **0.0000** | 1732 ms | 637 ms | 287,498 B |
| #1 | **0.0000** | 1776 ms | 741 ms | 287,498 B |
| #2 | **0.0000** | 1512 ms | 398 ms | 287,498 B |

No shift ≥ 0.002 on any load, and the chrome still loads
`juju2-wordmark-white-273-73c23508.png` at 6,405 b — `P4.S9`'s batch is undisturbed. **There is no
CWV movement to look for here by design**, and there is none: FCP/LCP sits in the same band as
`P4.S9`'s post-deploy median (1,544 ms) on a TTFB-dominated link.

## 7. Deviations

1. **A same-evening production "before" sweep the plan did not ask for** — three 70 s idle windows
   per viewport, one 8 s trace per viewport, and the served markup/CSS — all on the *pre-deploy*
   build, during the mandated wait after the evening pipeline. Read-only, cost nothing but the wait
   that was already required, and it upgrades every number in § 5 from "compared with R1's quoted
   baseline" to a paired same-instrument comparison.
2. **The paused-frame comparison reuses `P4.F11`'s existing local production build** (`f11af`)
   rather than rebuilding the same commit. The tree was diffed against the repo first — identical
   source but for the generated `next-env.d.ts` — which is a stronger check than trusting a fresh
   build to be equivalent, and it kept a multi-minute `next build` off the machine whose CPU was
   being measured.
3. **Two extra read-only checks beyond the plan's list**: the live-render probe and two full-page
   screenshots at 1280/390 (§ 6). The plan's own note asked for the star/shooter counts and the
   mobile orbit removal to be re-checked live; this is that check, plus the page-error listeners.
4. **The 8 s trace was run as its own pass** rather than folded into the idle windows, because
   tracing perturbs exactly the counters the 70 s windows measure. Same instrument, separate
   throwaway profile and port.

Nothing was skipped. The plan's `/`-only CLS check was run as written (the batch's other CWV numbers
are `P4.S9`'s and were not re-run).

## 8. What this slice did not do

- **No code changed.** `git diff --stat` is `phase.md` and this `result.md` (plus the orchestrator's
  own pre-existing `works/` edits). This slice ships code that was already committed and pushed.
- **No commit, no push, no workflow state command** other than `python3 scripts/workflow.py validate`.
- **No hand edit on the box.** `deploy/deploy.sh` did all of it. `.env.prod` was neither edited nor
  read; **no environment value of any kind was read this slice**, so no secret appears here or in
  any transcript. `edge-nginx` was addressed by nothing but `docker inspect`.
- **Production stayed read-only in the browser**: navigations to `/` only, no `/api/ask` turn, no
  login, no `/ops` session, no writes. Every throwaway Chrome profile was created for this slice and
  every browser was closed at the end; the local 3015 build server was stopped, and the operator's
  own dev stack on 3010 answered 200 throughout.
- **No doc version.** Two `## Doc impact` lines were appended to `phase.md` instead; nothing under
  `docs/` was touched.
- **Model spend: 0.** No pipeline run, no LLM call.

## 9. Artefacts (all outside the repo, in the session scratchpad)

`s10_markup.sh` + `s10_markers.py` with `s10_landing_{before,after}.html` / `s10_css_{before,after}.css`;
`s10_idle.py` + `s10_idle_{before,after}.{log,json}`; `s10_trace.py` + `s10_trace_{before,after}_{1280,390}.json`;
`s10_frames.py` + `s10shots/field_{1280,390}_{prod,local,prodctl}_1.3.png`; `s10_live.py` +
`s10_after_landing_{390,1280}.png`; `s10_cls.py` + `s10_cls_after.jsonl`; `s10_ps_{before,after}.txt`;
`s10_deploy.log` (a copy) and the throwaway profiles `chrome-s10*`. The deploy log stays on the box at
`/home/opc/Mijual/var/deploy-20260903T104712.log`.
