# P12.S2 — result

- **status**: `done`
- **summary**: Released the whole P12 flicker batch (`P12.S1` + `F1`–`F10`, commits `62d78ec` …
  `8b54422`, at `main` = `004d936`) to production as one frontend-only `deploy/deploy.sh` run —
  production serves **`004d936`** since **2026-09-04 15:13 KST**, no rollback, three days before the
  09-07 11:00 KST freeze and four hours before the 19:30 pipeline. `mijual-web` was the only
  container recreated; `mijual-web:previous` = **`a9195a0c0689`** is the real rollback point (the
  `a74c58a` image) and `mijual-api:previous == :latest` is a no-op. The four R7 no-harm assertions
  are identical before and after (the sorted `docker ps` differs in exactly one line, `mijual-web`'s
  uptime), `make smoke-prod` **17/17**, `curl /api/health` ok. Every fix's mechanism is in the bytes
  production now serves, and all of it was re-measured **on production through Cloudflare** in
  **Aside `--account u2`**, anonymous and read-only: the account slot and the launcher now enter the
  DOM **65–162 ms *before* FCP on 10/10 routes** (R1's before: 3–165 ms *after*), CLS 0 on 10/10;
  the 검색 불일치 box, the 정정 이력 button, the 환산 row, the removed sample row, the 의견 보내기
  dialog and the cold-cache mono faces all reproduce their landed numbers; and the landing is
  **`AE = 0`** against a local production build of the same commit at 1280 and 390.
- **files_changed**:
  - `works/phases/active/P12/phase.md`
  - `works/phases/active/P12/slices/P12.S2/result.md`
  (no source file was touched — this slice ships already-committed code)
- **validation**:
  | command | result |
  |---|---|
  | `git fetch origin && git rev-parse origin/main main HEAD` | **pass** — all three `004d936` (carries `62d78ec` … `8b54422`) |
  | `git diff --stat a74c58a..HEAD -- src deploy compose.prod.yml Makefile pyproject.toml` | **pass** — empty; only `frontend/`, `docs/`, `works/` changed |
  | box `git rev-parse HEAD` before / clean tree | **pass** — `a74c58a`, no local modifications |
  | `celery … inspect active` + beat window | **pass** — `- empty -`, 1 node; next window 19:30 KST, 4 h 19 min away |
  | freeze check | **pass** — launched 2026-09-04 15:11 KST, freeze opens 09-07 11:00 KST |
  | the four R7 no-harm assertions, **before** | **pass** — § 1 |
  | `deploy/deploy.sh` (nohup + log + poll) | **pass** — `DONE — released at ref origin/main`; `grep -c ROLLBACK` = **0** |
  | `docker compose -f compose.prod.yml ps` + schema | **pass** — six services up, `mijual-schema` `exited exit=0` |
  | box `git rev-parse HEAD` after | **pass** — `004d936` |
  | the four R7 no-harm assertions, **after** | **pass** — identical; `docker ps` differs in exactly one line |
  | `curl -s https://jujutower.com/api/health` | **pass** — `{"status":"ok","version":"0.1.0","now_kst":"2026-09-04T15:13:53+09:00"}` |
  | `make smoke-prod` | **pass** — **17 pass · 0 fail**, 11.0 s |
  | served bytes per fix, production before vs after | **pass** — § 4 |
  | R1 load sweep repeated on production, 10 routes @ 1280 | **pass** — § 5, no post-paint insert anywhere |
  | six per-fix reproductions on production | **pass** — § 6 |
  | cold-cache 412×915 mono profile, 3 loads × 2 routes | **pass** — § 7 |
  | paused-frame `AE = 0` of `/` vs the local production build | **pass** — § 8, both viewports, controls included |
  | `git diff --stat` | **pass** — `phase.md` + this `result.md` (plus the orchestrator's pre-existing `works/` edits) |
  | `python3 scripts/workflow.py validate` | **pass** (three pre-existing P4 warnings) |
- **deviations**: five, all small — § *Deviations*. None changed what shipped.
- **doc_impact**: two lines appended to `phase.md` § *Doc impact* — `operations` (the release: sha,
  log path, image ids, which `:previous` is real, the assertions) and `qa` (the checklist gains this
  phase's two production checks: the no-pop-in load sweep line and the cold-cache mono line).
- **doc_versions**: n/a (not a review slice) — deferred to a docs phase.
- **review_verdict**: n/a
- **walkthrough**: none
- **explain**: n/a
- **operator_need**: none

---

## 1. Preconditions, and the launch window

| check | reading |
|---|---|
| `git rev-parse origin/main main HEAD` | all three **`004d936`** — the S2 planning commit on top of `8b54422` (`P12.F9`), which sits on `62d78ec` (`P12.S1`) |
| frontend-only | `git diff --stat a74c58a..HEAD -- src deploy compose.prod.yml Makefile pyproject.toml` → **empty**. 31 files changed, all under `frontend/` (plus `docs/` and `works/`, neither of which is built) |
| box HEAD before | **`a74c58a`** (`P4.S10`), clean tree — what `deploy.sh`'s `REF=origin/main` expects |
| box clock | UTC 06:10 = **KST 15:10** (the box is GMT) |
| `celery -A mijual.scheduler.app inspect active` | **`- empty -`**, 1 node online |
| next beat window | `daily-pipeline-evening` **19:30 KST** — 4 h 19 min after the launch; nothing to wait for |
| deploy freeze | opens **2026-09-07 11:00 KST** — this landed **three days early** |

**The four R7 no-harm assertions, BEFORE** (2026-09-04 15:10 KST):

| assertion | reading |
|---|---|
| co-tenants | `hi2vi.com` · `vocky.hi2vi.com` · `changple.ai` → **HTTP/2 200 ×3** |
| `edge-nginx` `StartedAt` | **`2026-07-02T19:22:12.325478595Z`** |
| `:80` / `:443` owner | **`edge-nginx`** (`0.0.0.0:80->80, :::80->80, 0.0.0.0:443->443, :::443->443`) |
| sorted `docker ps` | **28 containers**; `changple_shared_network` **17 members** |

Full listing outside the repo (`scratchpad/s2_ps_before.txt`).

## 2. The deploy

```sh
ssh oracle-cloud 'cd /home/opc/Mijual && nohup deploy/deploy.sh > var/deploy-20260904T061127.log 2>&1 < /dev/null &'
# launched pid=2933897  (2026-09-04 15:11:27 KST = 06:11:27 UTC)
```

No local `timeout` wrapper (macOS has none — `P4.F4`'s `exit 127`). The launch `ssh` returned
immediately with the pid; the remote log was then polled to its final line.

Log `/home/opc/Mijual/var/deploy-20260904T061127.log`, **280 lines**, ~110 s:

| step | evidence |
|---|---|
| baseline captured | `edge-nginx StartedAt before: 2026-07-02T19:22:12.325478595Z` |
| checkout | `a74c58a..004d936  main -> origin/main`; `HEAD is now at 004d936` |
| rollback points | `tagging mijual-api:latest -> mijual-api:previous`, `… mijual-web …` |
| build-arg asserts | `MIJUAL_API_ORIGIN` = `http://mijual-api:8010`, `NEXT_PUBLIC_SITE_URL` = `https://jujutower.com` — both non-empty |
| both images named | `naming to docker.io/library/mijual-api:latest done` (line 131), `… mijual-web:latest done` (213); the Next build itself `#38 DONE 19.7s` |
| recreate set | **`mijual-web` Recreate → Recreated**; `redis`, `postgres`, `beat`, `api`, `worker` all `Running` — nothing else moved |
| schema one-shot | `mijual-mijual-schema-1 Exited`; `docker inspect` → **`exited exit=0`** |
| health gate | `mijual-web healthy on poll 7`, `mijual-api healthy on poll 1` |
| verdict | `deploy healthy — mijual-api:latest + mijual-web:latest are live`; `not gated, reported: mijual-worker = healthy` |
| edge assertion (in-script) | `ok — edge-nginx StartedAt unchanged (2026-07-02T19:22:12.325478595Z)` |
| final | `DONE — released at ref origin/main; the edge proxies jujutower.com to mijual-web:3010.` |

`grep -c ROLLBACK` over the log → **0**. Box `git rev-parse HEAD` after → **`004d936`**.

### Image table — and which half is a real rollback point

| image | before | after | rollback value |
|---|---|---|---|
| `mijual-api:latest` | `e0a479095f7b` | **`e0a479095f7b`** (unchanged — full build-cache hit) | — |
| `mijual-api:previous` | `e0a479095f7b` | **`e0a479095f7b`** (same id) | **NO-OP** — flipping it changes nothing |
| `mijual-web:latest` | `a9195a0c0689` | **`8ed77c901705`** (rebuilt) | — |
| `mijual-web:previous` | `028b480a7b37` | **`a9195a0c0689`** | **THE REAL ROLLBACK POINT** — the `a74c58a` (`P4.S10`) web image |

Exactly the `P4.S9`/`P4.S10` shape the plan predicted: nothing under `src/` has changed since
`1a93d7b`, so the api image was a cache hit and `mijual-api:previous` still points at the running
image. `deploy/rollback.sh` therefore returns the **frontend** to `a74c58a` and leaves the API where
it is. The pre-P12 rollback point one step further back (`028b480a7b37`, the `4aa8ddd` CWV image) is
no longer reachable through `rollback.sh`; going back further is `REF=<sha> deploy/deploy.sh`, per
runbook R7.

## 3. After — the box

**The four R7 no-harm assertions, AFTER** (15:13 KST) — identical to before on all four:

| assertion | before (15:10) | after (15:13) |
|---|---|---|
| co-tenants | 200 ×3 | **200 ×3** |
| `edge-nginx` `StartedAt` | `2026-07-02T19:22:12.325478595Z` | **identical** |
| `:80`/`:443` owner | `edge-nginx` | **`edge-nginx`**, same port map |
| `docker ps` | 28 containers, network 17 | **28 containers, network 17** |

The container **name set** is identical, and the whole sorted `docker ps` differs in exactly **one
line** — `mijual-mijual-web-1  Up 19 hours (healthy)` → `Up About a minute (healthy)`, i.e. the one
container a frontend-only release is supposed to recreate. `api`, `beat`, `worker` and `postgres`
all still read `Up 39 hours`, `redis` `Up 2 days` — no `.env.prod` line changed, so nothing with an
`env_file` moved (the control `P4.S9` established, and the postgres-recreate rule `P4.F4` recorded
did not fire). `edge-nginx` was addressed by nothing but `docker inspect`.

`curl -s https://jujutower.com/api/health` →
`{"status":"ok","version":"0.1.0","now_kst":"2026-09-04T15:13:53+09:00"}`

### `make smoke-prod` — 17 pass · 0 fail (11.0 s)

All 17 green from the laptop. `landing 288222 bytes` (287,567 pre-deploy — the +655 B the batch's
head script and server-rendered chrome cost), `board 395 rows`, `sitemap 834 URLs (467 events)`,
`www` 301, `third-party` exactly the two allowed hosts, `ops-door` still carrying none of D15's rule
lines.

## 4. What production now serves — the mechanism, before vs after

Fetched through Cloudflare with `curl`, seven routes plus every CSS chunk they declare
(`scratchpad/fetch.sh`, `served/{before,after}_*`). The **before** column is production at
`a74c58a`, fetched 90 seconds before the launch, so this is a paired comparison and not a quotation.

| reading | before (`a74c58a`) | after (`004d936`) |
|---|---|---|
| `<head>` pre-hydration mirror script | **absent on all 7 routes** | **present on all 7**, in `<head>`, reading only `mijual.convert.offer`, `mijual.auth.flash`, `mijual.portfolio.sample`, in `try/catch`, writing nothing (F3/F5/F10 seam) |
| account slot in the first HTML | `href="/auth/login"` **0 ×** on every route | **2–3 ×** on every route — the desktop 로그인 link *and* the sheet row (F1) |
| launcher in the first HTML | **absent** | **present** on every route (F2) |
| `@media (max-width:767px){.launcher{display:none}}` | **absent** | **present** (F2's pre-hydration guard) |
| `/portfolio` 전환 제안 band | offer class **0** | **present, server-rendered**, carrying the `offerPre` state class (F3) |
| `/portfolio?sample=1` `SampleRules` `<style>` | **0** rules | **32** rules — one `display:none` per served code plus the per-section container rules; `data-corp` **21 ×**, `data-corp-group` **13 ×** (F10) |
| `/stocks/00547510` page-level lookup script | **0** | **1** — reads `mijual.lookup.holdings` for this page's own `corp_code` (F4) |
| `data-mj-cells` / `data-mj-foot` published by the server | **absent** | `data-mj-cells="4"`, `data-mj-foot="steady"` (F4) |
| `html[data-mj-lookup-holding]` reservation rules in the CSS | 0 | **12** (`4 cells 101.75px @1280 / 201.25px @390`, `3 → 86.25 / 155`, `1 → 66.75 / 45.25`, the prompt-hide and the desktop column pins) |
| `.flashSlot` + `html[data-mj-auth-flash=logout] … :empty{min-height:40.5938px;display:block}` | 0 | **present** (F5; the minifier rounds F5's 40.59375) |
| `.historyButton::after{content:attr(data-label);visibility:hidden;height:0}` twin | 0 (`display:inline-flex`) | **present**, `.historyButton` now `display:inline-grid` with `grid-template-areas:"label"` (F6) |
| `.noMatchStale{visibility:hidden}` | 0 | **1** (F8) |
| mono fallback faces | `@font-face{font-family:plexMono Fallback;src:local(Arial);size-adjust:131.49%}` — Next's generated proportional face, first behind `plexMono` | **gone under that name**; `plexMono Fallback Apple` (Menlo, **99.66% / 102.85% / 27.59% / 0%**, 3 weights) and `plexMono Fallback Windows` (Consolas, 100%), both `unicode-range`-limited to the subsets' 211 codepoints, with `plexMono Fallback Arial` re-declaring the old face **verbatim** behind them (F9) |
| `--font-plex-mono` stack | `"plexMono", "plexMono Fallback", ui-monospace, …` | `"plexMono", plexMono Fallback Apple, plexMono Fallback Windows, plexMono Fallback Arial, ui-monospace, …` |
| route CSS total (7 routes' chunks) | 133,142 B | **137,613 B** (+4,471 B) |

**One correction to the plan's wording.** The plan asked for "**no** `local(Arial)` mono face";
`local(Arial)` and `size-adjust: 131.49%` each still appear **once**, and must — F9 deliberately
re-declares Next's generated face *verbatim* as `"plexMono Fallback Arial"`, third in the stack,
because the `←`/`→` inside `.mono` elements are outside the Plex subsets and only ever painted in
that face. What is gone is the generated `plexMono Fallback` family sitting **first** behind
`plexMono`, which is the defect. Both readings above are recorded so the review can see which is
which.

**One honest note on ordering.** The mirror script is in `<head>` on every route, but it sits
*after* the three `data-precedence` `<link rel="stylesheet">` chunks React hoists to the top of the
head, and *before* `/foundations/tokens.css`. That is Next's own head ordering and it does not
matter for correctness — a parser-blocking inline script in `<head>` runs before the body exists, so
every stamp is on `<html>` before first paint, which §§ 6–7 measure directly rather than infer.

## 5. The R1 load sweep, repeated on production as the "after"

Aside `--account u2`, one route per invocation (the ~80 s daemon limit), 1280×800 DPR 1,
`Emulation.setDeviceMetricsOverride`, warm cache, anonymous. The probe is R1's: an init script
installed with `Page.addScriptToEvaluateOnNewDocument` **before** `goto`, whose `MutationObserver`
observes `document` (not `documentElement`, which is `null` at that moment), plus buffered `paint`
and `layout-shift` observers. **Δ is the account slot / launcher's DOM entry minus FCP: negative
means it is in the first paint.**

| route | FCP (ms) | account slot Δ | launcher Δ | CLS | shift entries |
|---|---|---|---|---|---|
| `/` | 516 | **−67** | **−16** | **0** | none |
| `/stocks` | 872 | **−154** | **−154** | 0.00009 | one 9e-05 entry, source with no class (see below) |
| `/stocks?q=zzz` | 448 | **−117** | **−117** | **0** | none |
| `/stocks/00547510` | 316 | **−111** | **−110** | **0** | none |
| `/portfolio` | 468 | **−69** | **−69** | **0** | none |
| `/portfolio/notifications` | 388 | **−70** | **−70** | **0** | none |
| `/ask` | 380 | **−65** | — (no launcher on `/ask`, by design) | **0** | none |
| `/events/20260806000329` | 344 | **−162** | **−162** | **0** | none |
| `/auth/login` | 248 | **−80** | **−80** | **0** | none |
| `/auth/reset` | 408 | **−104** | **−104** | **0** | none |

**No post-paint insert of either element on any of the ten routes** — R1's production-build "before"
put both **+3 to +165 ms after FCP** (dev +44 to +293), and every one of those pop-ins is now
**65–162 ms before it**. The account slot's rect is **one distinct value across all ten routes**,
`[1138.73, 15.03, 37.27, 20.92]`, and the launcher's is `[1188, 726, 68, 50]` — the same numbers
`P12.F1` and `P12.F2` measured off-box.

The landing's CLS is **0** with no entry at all, so the star-field filter the plan allowed for was
never needed. `/stocks`'s single `9e-05` entry (one source, empty class name) did **not** reproduce:
two further loads of that route read **CLS 0 with no `layout-shift` entry**. It is 1/1000th of the
"good" threshold and is recorded rather than explained.

## 6. Per-fix reproductions on production

All anonymous, read-only, Aside `--account u2`; storage seeded in the profile is browser-only and
reaches no server (which is the seam's whole point). Rects are sampled frame-by-frame with
`requestAnimationFrame` inside the init script and CLS is treated as corroboration, not evidence
(`P12.F4`'s `hadRecentInput` rule).

### F8 — `/stocks?q=zzz`, one keystroke

| viewport | 검색 불일치 box before | after one keystroke | elements moved (60 frames) | doc height | shift entries |
|---|---|---|---|---|---|
| 1280 | `[354, 254.92, 572, 18.59]` visible | **same rect**, `+noMatchStale`, `visibility: hidden` | **0** | 800 → **800** | **none** |
| 390 | `[16, 254.92, 358, 37.19]` (two-line box) | **same rect**, hidden | **0** | 911 → **911** | **none** |

`role="status"` is retained on the element and `elementFromPoint` at its centre returns
`div.Lookup__entry`, not the `<p>` — it leaves hit-testing exactly as the old unmount did. R1's
before: **−30.594 px / 25 elements / CLS 0.00299** at 1280 and **−49.187 px / 45 elements /
0.03213** at 390.

### F6 — `/events/20260806000329`, the 정정 이력 toggle

Four real states driven with `Input.dispatchMouseEvent` (the button is scrolled to the viewport
centre first — a synthetic click below the fold silently does nothing, which is how the first
attempt read as "one rect" without ever toggling):

| viewport | closed | open | closed | open | distinct rects |
|---|---|---|---|---|---|
| 1280 | `[125, 514.94, 77.53, 36]` | same | same | same | **1** |
| 390 | `[33, 400.81, 324, 44]` | same | same | same | **1** |

The label really does swap (정정 이력 ↔ 접기 ×, `aria-expanded` false ↔ true, document 1464 ↔ 2130 at
1280 and 2197 ↔ 3470 at 390) — the **button box never moves**, where HEAD narrowed it
77.53 → 66.70 px. The disclosure's own expansion moves what is below it, as designed (all entries
`hadRecentInput: true`, CLS 0); the only entry naming the button names `historyLabel` at
**v = 0 (1280) / 2e-05 (390)** — the label re-centring inside a fixed box.

### F4 — `/stocks/00547510` with a remembered holding

`sessionStorage["mijual.lookup.holdings"] = {"v":1,"entries":{"00547510":100}}` seeded on the origin,
then navigated; 150 rAF frames sampled from before first paint.

| viewport | `data-mj-lookup-holding` at DOMContentLoaded | ① 환산 row rect | document height | shift entries | CLS |
|---|---|---|---|---|---|
| 1280 | **set** (released later — `null` at the end) | **one distinct value** `[206, 436.92, 868, 101.75]` across 150 frames | **1108, one value** | **none** | 0 |
| 390 | **set** / released | **one distinct value** `[34, 587.63, 322, 201.25]` | **1619, one value** | one, `v = 0.00531`, `hadRecentInput`, source = a cell **inside** the row | 0 |

The row draws its four-cell with-holding geometry (`data-mj-cells="4"`, the measured 101.75 / 201.25
px) from the first frame and the cells then fill with `100주 / 0.0863800841 / 8주 / +1주`. R1's
before: **+35 px @1280 / +111 px @390, foot −22.95 / −56, CLS 0.05548**.

**One honest residual, recorded for the review.** Inside the reserved box the cells settle into
their final columns one frame after the first sampled frame — at 1280 `cell@1` moves x 423 → 206 at
t = 236 ms with FCP at 232 ms (so the pre-fill column arrangement was never painted, and there is no
`layout-shift` entry at all); at 390 the cell heights settle 99.5 → 45.25 at t = 229 ms with FCP at
216 ms, which is the single sub-threshold entry above. The row's box, the document height and
everything below the row are immobile in both cases. `P12.F4` measured **0 px moved** for this on
dev and the local production build; production's faster fill lands it at the paint boundary instead
of before it.

### F10 — `/portfolio` with an edited sample

`localStorage["mijual.portfolio.sample"] = {"v":2,"shares":{},"removed":["00787057"],"claims":[]}`
(one of the four served codes; deliberately not one of the two that would empty a section), 180
frames sampled at 1280, tracking every `[data-corp]` element's display and height directly:

```
t=425 (FCP 440)  doc 1243  n=9  00542898:64,00157991:64,01409022:63,00787057:none,
                                00157991:110,00542898:163,00542898:111,00787057:none,01409022:164
t=436            doc 1243  n=7  … (the two 00787057 nodes unmounted; every other row unchanged)
```

**The removed issuer's row never has a painted box in any of the 180 frames** (`everPainted:
false`): the `<head>` stamp `data-mj-sample-removed="00787057"` is on `<html>` before first paint
and the server-generated per-code rule hides both nodes, then React unmounts them. Document height
is **one value, 1243, from the first frame to the last**; **no `layout-shift` entry at all**; CLS 0.
Same at 390: doc **1987 constant**, no entries. R1/F10's before: **doc 1324 → 1208, CLS 0.05206 at
1280**, **−205 px / 0.11225 at 390**. The stamp is released once `useSample()` answers
(`data-mj-sample-removed` is `null` at the end), so 되돌리기 still works.

### F7 — the 의견 보내기 dialog, opened from the footer (no send)

| viewport | dialog rect | body rect | body inline style | 보내기 | shift entries |
|---|---|---|---|---|---|
| 1280 | `[796, 425.516, **380 × 318.016**]` | `[797, 479.516, 378, **263.016**]` | **none** | `[1087.734, 690.531, **71.266**, 36]` | none |
| 390 (sheet) | `[0, 498.984, **390 × 345.016**]` | `[0, 552.984, 390, **291.016**]` | **none** | `[302.734, 780, **71.266**, 48]` | none |

The dialog's **318.016 / 345.016 px** and the body's **263.016 px** are `P12.F7`'s pinned numbers to
the thousandth, and the editing body carries **no inline `min-height`** — which is exactly why the
resting dialog is byte-identical to HEAD; the pin is installed at the press, and no press was made
(a send forwards to vocky and is a write). The 보내기 button is **71.266 px**, its unchanged resting
width — Q9's decision is still open and untouched. `닫기` is mounted, as signed.

### F1 / F2 — `/` at 1280

Covered by § 5's first row and by § 8's screenshot: 로그인 link at **−67 ms** and launcher at
**−16 ms** relative to FCP, rects `[1138.73, 15.03, 37.27, 20.92]` and `[1188, 726, 68, 50]`, CLS 0;
both are visible in the paused frame.

## 7. The cold-cache mobile profile — the mono swap on production

412×915 @ DPR 2.625, 4× CPU, ≈1.6 Mbps / 150 ms, `Network.setCacheDisabled` +
`Network.clearBrowserCache` per load, 3 loads per route, every element whose computed
`font-family` resolves to `plexMono` tracked over 220 rAF frames.

| route | loads | FCP (ms) | Plex Regular / SemiBold arrive | **max mono width delta across the whole load** | worst element | CLS | shift entries |
|---|---|---|---|---|---|---|---|
| `/stocks/00547510` | 3 | 852 / 840 / 836 | 1485 / 1531 ms (13.0 / 14.0 kB) | **0.031 px** (all three loads) | `Lookup__cval` 97.172 → 97.203 | **0** | **none** |
| `/portfolio` | 3 | 1452 / 1588 / 1516 | same files | **0.016 px** (all three loads) | `DDay__date` 92.406 → 92.422 | **0** | **none** |

R1's production "before" on the same profile and the same page: `DDay__dday` **106.13 → 92.42**
(Δ 13.71) and `Lookup__cval` **113.53 → 97.20** (Δ 16.33) when the Plex files landed. The elements
now **start at the Plex value** and stay within 0.031 px of it — the swap moves **0 px** in any
practical sense, and neither Plex file produces a `layout-shift` entry near its `responseEnd`.
`NotoSansKR_subset` still arrives at 3,128 ms and still moves nothing (`P4.F5` holding).

## 8. 「The same landing」 — paused-frame `AE = 0` against the local production build

A local production build of the **same commit** (`004d936`, `frontend/` clean against HEAD) built in
a copy outside the repo with `NEXT_PUBLIC_SITE_URL=https://jujutower.com`, served with
`node .next/standalone/server.js` on **:3014** with `MIJUAL_API_ORIGIN=https://jujutower.com/api` so
both renders read the **same** data (the dev DB has 445 events, production 467 — pointing the local
build at the dev API would have compared two different landings). Normalised token diff of the two
served landings: **26 differing tokens of 1,144, all of them one thing** — Cloudflare's edge email
obfuscation in the footer (`/cdn-cgi/l/email-protection`), plus the live countdown, which ticks.

Captures: **one `page.screenshot()` per `aside repl` invocation** (F6 trap (a): a second capture in
one invocation returns the first one's bytes), **no `fullPage` under emulation** (trap (b)),
mobile at **DPR 1** so the tile fits the window (F9 trap (b)), and the Cosmos star field, the
orbiter/streaks, the countdown and the footer masked before the capture — F9's trap: two captures of
the *same build* differ by 50,800 px @1280 on the star field alone, so an unmasked AE means nothing.
Animations paused, scrolled to the top, 1.3 s settle.

| comparison | 1280 | 390 |
|---|---|---|
| **production vs the local production build of the same commit** | **`AE = 0`** (equal sha256) | **`AE = 0`** (equal sha256) |
| cropped to the emulated tile only (1280×800 / 390×844) | **`AE = 0`** | **`AE = 0`** |
| control: production vs production, second load | **`AE = 0`** | — |
| live positive control (1280 vs 390) | **4.41 × 10⁹** | — |

All three 1280 PNGs hash to one value and both 390 PNGs to another. The frame was looked at, not
only hashed: the nav carries the 로그인 link, the launcher bubble is at (1188, 726), the hero, search
row and stat line (`감시 중 467건` — production's number, served by the local build too) render as
designed, and the orbit rings are present at 1280.

## 9. Deviations

1. **A production "before" fetch the plan did not ask for.** § 4's before column is production at
   `a74c58a`, curled 90 seconds before the launch, so every served-bytes reading is a paired
   comparison instead of a claim about the after alone. Read-only, cost ~2 s.
2. **The plan's "no `local(Arial)` mono face"** is stated more precisely in § 4: the *generated*
   `plexMono Fallback` face is gone from the front of the stack, while `local(Arial)` survives once
   as F9's deliberate verbatim re-declaration behind the two matched families. Reporting it as a
   flat "0 occurrences" would have been wrong.
3. **The load sweep's "before" is R1's local-production-build table, not a production one.** The
   plan quotes "3–165 ms after FCP on production"; R1 measured that band on the local production
   build and verified production reproduced its behaviour. A genuine production before-sweep was not
   taken (the sweep is the "after" by the plan's own design), so § 5 compares against R1's recorded
   band and says so.
4. **Two extra loads of `/stocks`** to characterise its lone `9e-05` shift entry (§ 5). Both read
   CLS 0 with no entry.
5. **The local build for § 8 points at the production API** (`MIJUAL_API_ORIGIN=https://jujutower.com/api`,
   GETs only) rather than the dev API, because the two databases differ by 22 events and the
   comparison is meaningless if the two landings show different data.

Nothing was skipped. F3's two `/portfolio` bands were exercised through § 4's served-bytes reading
(the server-rendered 전환 제안 band, present with its `offerPre` class) and § 6's F10 run (a seeded
sample on `/portfolio` with the document height constant from the first frame).

## 10. What this slice did not do

- **No code changed.** `git diff --stat` is `phase.md` and this `result.md` (plus the orchestrator's
  pre-existing `works/` edits). This slice ships code that was already committed and pushed.
- **No commit, no push, no workflow state command** other than `python3 scripts/workflow.py validate`.
- **No hand edit on the box.** `deploy/deploy.sh` did all of it. `.env.prod` was neither read nor
  edited; **no environment value of any kind was read this slice**, so no secret appears here or in
  any transcript. `edge-nginx` was addressed by nothing but `docker inspect`.
- **Production stayed read-only**: anonymous throughout — no login, no signup, no `/api/ask` turn,
  no feedback send, no `/ops` session, no write of any kind. Browser storage was seeded in the
  Aside profile only, which reaches no server.
- **Instrument: Aside, `aside repl --account u2` (profile 「claude2」), never `u0`.** Every
  invocation carried the flag; `aside account use` was never run. Runtime and access path:
  `https://jujutower.com` through Cloudflare — the production half of `## Operator Runtime` — plus
  the local production build of the same commit for § 8's comparison.
- **The dev stack was left as found**: the operator's `next dev` on :3010 answered 200 before and
  after; the only server this slice started (`node server.js` on :3014, pid 22230) was stopped, and
  :3014 now refuses connections.
- **No doc version.** Two `## Doc impact` lines were appended to `phase.md`; nothing under `docs/`
  was touched.
- **Model spend: 0.** No pipeline run, no LLM call.

## 11. Artefacts (all outside the repo, in the session scratchpad)

`fetch.sh` + `served/{before,after}_{root,portfolio,portfolio_sample,stock,stocksmiss,login,events}.html`
and `served/{before,after}_all.css` and `served/local_root.html`; `s2_deploy.log` (a copy),
`s2_ps_{before,after}.txt`, `s2_images_before.txt`; `sweep_tpl.js` + `sweep_1280.jsonl`;
`prelude.js` with `f8.js`, `f6.js`, `f4.js`/`f4b.js`, `f10.js`/`f10c.js`, `f7.js`; `cold.js`;
`shot.js` + `shots/{prod,local,prodctl}_{1280,390}.png`; `s2build/` (the local production build) and
`s2_build.log` / `s2_3014.log`. The deploy log stays on the box at
`/home/opc/Mijual/var/deploy-20260904T061127.log`.
