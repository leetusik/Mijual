# P4.R1 — result

- **status:** done
- **summary:** Reproduced the site's Core Web Vitals in real Google Chrome 152 over CDP (headful,
  throwaway profile, mobile + desktop, six routes × production and the local production build,
  3 cold loads each = 72 loads) and cross-checked with Lighthouse. LCP and INP are **good
  everywhere** (worst LCP 1.56 s, worst INP-proxy 72 ms); the site's **only** layout shift is the
  291 KB Korean webfont swapping on a cold cache — proved causally by blocking the font (CLS
  0.138 → 0.000). Cloudflare's "poor" rating rests on a RUM CLS field that is an **integer 0/1 per
  event**, not a Google score, over a sample that is almost entirely this workspace's own automation.
  Findings + a ranked `P4.F5`–`P4.F9` fix list are in `phase.md`.
- **files_changed:** `works/phases/active/P4/phase.md`, `works/phases/active/P4/slices/P4.R1/result.md`
- **validation:** `python3 scripts/workflow.py validate` → PASS (0 errors); `git diff --stat` → the
  two files above only. All measurement artefacts live outside the repo in the session scratchpad.
- **deviations:** three, all recorded below — (1) the RUM re-query is by `avg`/`quantiles` per path ×
  device rather than only the plan's quantile set, because the `avg` block exposes Cloudflare's own
  LCP sub-parts; (2) the local production build runs `node .next/standalone/server.js` (what the box
  runs) rather than `next start`, which Next 16 refuses under `output: "standalone"`; (3) Lighthouse
  ran headless (it launches its own browser) — it is a cross-check only, every primary number is from
  the headful CDP browser.
- **doc_impact:** two lines appended to `phase.md` (`frontend`/`qa` — the measured CWV baseline and
  the font-swap CLS mechanism; `operations` — how to read this site's Cloudflare RUM).
- **doc_versions:** n/a (not a review slice)
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a
- **operator_need:** none to proceed; two operator-decision questions were filed in `phase.md`
  `## Operator Questions` (the starfield's continuous CPU cost, and whether landing TTFB work is
  wanted at all).

---

## Instrument, profiles, samples

**Instrument.** Real **Google Chrome 152.0.7977.65**, headful, launched through LaunchServices with
a throwaway profile and a fresh port —
`open -na "Google Chrome" --args --remote-debugging-port=9351 --user-data-dir=<scratchpad>/r1prof …` —
driven over the DevTools protocol from `scratchpad/r1_cdp.py` (a `websockets` client; the same
fallback instrument `## Operator Runtime` records, because Aside's daemon does not run on this Mac
and no agent Aside account exists). **Aside was not used and is not installed here.** The browser was
closed with `Browser.close` at the end; port 9351 and PID are gone (verified).

**Runtime and access path.** Production exactly as `## Operator Runtime` records it:
`https://jujutower.com` through Cloudflare → `edge-nginx` → the `mijual-web` standalone build on the
Oracle box (release `1a93d7b`). Production is a production build, so there is no dev/prod split to
check twice there; the second target is the **local production build** for attribution without the
edge: `frontend/` copied to `scratchpad/r1fe`, built with
`NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`,
served by `node .next/standalone/server.js` on **:3014** (PID file `scratchpad/r1_web3014.pid`,
stopped; port free). The operator's dev stack (8010, 3010) was never touched and answered 200 before
and after. The repo working tree was not built into — the build ran in the scratchpad copy, so
`frontend/.next` (the dev server's) is untouched.

**Device profiles.** *mobile* = 412×915, DPR 2.625, `Emulation.setCPUThrottlingRate 4`,
`Network.emulateNetworkConditions` 150 ms RTT / 1.6 Mbps down / 0.75 Mbps up. *desktop* = 1280×800,
no throttling. Both with `Network.setCacheDisabled(true)` + `Network.clearBrowserCache` per load, a
fresh tab per load, and the observers installed by `Page.addScriptToEvaluateOnNewDocument` (buffered
`largest-contentful-paint`, `layout-shift` with `sources`, `longtask`, `event` (threshold 16 ms),
`first-input`, `paint`, plus navigation/resource timing).

**Samples.** 72 cold loads (2 targets × 2 profiles × 6 routes × 3) in `scratchpad/r1_loads.jsonl`;
13 interaction runs; 4 idle-cost runs (70 s each) + 4 CSS-isolation runs (40 s each); 4 font-block
runs; 4 font-preload runs; 7 Lighthouse runs. **~95 production page loads, every one a GET.** No
`POST /api/ask` (the `/ask` composer was typed into — 삼성전자 — and never submitted; no Enter key was
ever dispatched), no account, no write, nothing on the box, no deploy. Routes: `/`, `/stocks`,
`/stocks/00547510`, `/events/20260806000329` (툴젠 ①, confirmed live on `/api/board` today), `/ask`,
`/portfolio?sample=1`.

**RUM status: fetched.** Token read from `/Users/sugang/projects/personal/changple5/.dev.env` into a
variable inside the query scripts, never printed, never copied. Site tag as the addendum gives it.
The 7-day window is unchanged from the orchestrator's addendum (desktop n 173 → 175) — the sample is
still 2026-09-02–03 and still almost entirely this workspace's own sessions.

---

## 1. The cold-load sweep — medians of 3

Times in ms, `render` = LCP − TTFB, HTML/JS in KB (JS = transferred; `JSdec` = decoded).

| target | prof | route | LCP | FCP | TTFB | render | CLS | LT n / ms | HTML | wire | JS | JSdec | LCP element |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| prod | desktop | `/` | 652 | 652 | 397 | 255 | 0.000 | 0 / 0 | 346 | 41 | 162 | 521 | `h1.Hero…title` |
| prod | desktop | `/stocks` | 792 | 792 | 397 | 395 | 0.000 | 0 / 0 | 26 | 6 | 172 | 558 | `p.Footer…source` |
| prod | desktop | `/stocks/00547510` | 376 | 376 | 142 | 234 | 0.002 | 0 / 0 | 32 | 8 | 172 | 558 | `p.Lookup…zerolead` |
| prod | desktop | `/events/…329` | 352 | 352 | 151 | 201 | 0.011 | 0 / 0 | 56 | 11 | 165 | 533 | `span.Event…agentName` |
| prod | desktop | `/ask` | 524 | 524 | 270 | 254 | 0.000 | 0 / 0 | 21 | 5 | 156 | 508 | `button.AskPage…card` |
| prod | desktop | `/portfolio?sample=1` | 552 | 552 | 312 | 240 | 0.001 | 0 / 0 | 54 | 10 | 180 | 585 | `p.Portfolio…banner` |
| prod | mobile | `/` | **1556** | 1556 | 423 | 1133 | **0.095** | 1 / 61 | 346 | 41 | 162 | 521 | `p.Anchor…fact` |
| prod | mobile | `/stocks` | 1432 | 1432 | 288 | 1144 | **0.138** | 2 / 117 | 26 | 6 | 172 | 558 | `p.Footer…source` |
| prod | mobile | `/stocks/00547510` | 1284 | 1284 | 147 | 1137 | 0.000 | 2 / 123 | 32 | 8 | 172 | 558 | `span` |
| prod | mobile | `/events/…329` | 1276 | 1276 | 142 | 1134 | 0.033 | 1 / 57 | 56 | 11 | 165 | 533 | `span.Event…agentTargetOwner` |
| prod | mobile | `/ask` | 1332 | 1332 | 277 | 1055 | **0.089** | 2 / 114 | 21 | 5 | 156 | 508 | `p.Footer…source` |
| prod | mobile | `/portfolio?sample=1` | 1540 | 1540 | 291 | 1249 | 0.000 | 1 / 58 | 54 | 10 | 180 | 585 | `p.Portfolio…banner` |
| local | desktop | `/` | 232 | 232 | 139 | 93 | 0.000 | 0 / 0 | 338 | 43 | 161 | 520 | `h1.Hero…title` |
| local | desktop | `/stocks` | 188 | 188 | 108 | 80 | 0.000 | 0 / 0 | 26 | 6 | 171 | 557 | `p.Footer…source` |
| local | desktop | `/stocks/00547510` | 108 | 108 | 20 | 88 | 0.000 | 0 / 0 | 31 | 8 | 171 | 557 | `p.Lookup…zerolead` |
| local | desktop | `/events/…329` | 88 | 88 | 18 | 70 | 0.009 | 0 / 0 | 56 | 11 | 164 | 532 | `span.Event…agentName` |
| local | desktop | `/ask` | 192 | 192 | 101 | 91 | 0.000 | 0 / 0 | 21 | 5 | 155 | 507 | `button.AskPage…card` |
| local | desktop | `/portfolio?sample=1` | 100 | 100 | 21 | 79 | 0.000 | 0 / 0 | 50 | 10 | 179 | 584 | `p.Portfolio…banner` |
| local | mobile | `/` | 820 | 820 | 122 | 698 | **0.095** | 2 / 150 | 338 | 43 | 161 | 520 | `p.Anchor…fact` |
| local | mobile | `/stocks` | 760 | 760 | 95 | 665 | **0.138** | 2 / 114 | 26 | 6 | 171 | 557 | `p.Footer…source` |
| local | mobile | `/stocks/00547510` | 780 | 780 | 18 | 762 | 0.000 | 2 / 119 | 31 | 8 | 171 | 557 | `span` |
| local | mobile | `/events/…329` | 844 | 844 | 16 | 828 | 0.033 | 1 / 57 | 56 | 11 | 164 | 532 | `span.Event…agentTargetOwner` |
| local | mobile | `/ask` | 764 | 764 | 79 | 685 | **0.089** | 2 / 107 | 21 | 5 | 155 | 507 | `p.Footer…source` |
| local | mobile | `/portfolio?sample=1` | 820 | 820 | 24 | 796 | 0.000 | 1 / 60 | 50 | 10 | 179 | 584 | `p.Portfolio…banner` |

Three things fall straight out of this table.

1. **LCP == FCP on every single load, on both targets, at both viewports.** The LCP element is always
   a **text** node; `lcpResourceLoadDelay` and `lcpResourceLoadTime` are 0 in Cloudflare's RUM too.
   Nothing on this site waits for an image, a lazy resource or the Cosmos canvas to become the LCP.
   So LCP = TTFB + render delay, and there is no "optimise the LCP image" lever at all.
2. **CLS is identical on production and on the local production build, to three decimals**
   (0.095 / 0.138 / 0.089 / 0.033), and it is a **mobile-profile-only** phenomenon. Nothing about the
   edge, Cloudflare or the box is involved.
3. **The edge + box cost about +250 ms of TTFB** over local for the same route, and the landing costs
   about **+255 ms of SSR over a light route through the same edge** (`/` 397 ms vs
   `/stocks/00547510` 142 ms); locally the same delta is +105 ms (139 vs 20 ms).

Long tasks are negligible: 0 on desktop, 1–2 of ~60 ms on throttled mobile, ≤150 ms in total. There
is no hydration blocking problem to fix.

## 2. CLS — attributed, and proved by removing the cause

Every shift ≥ 0.005 in the whole sweep lands in **one** cluster, and its timestamp tracks the Korean
webfont's `responseEnd` to within ~30 ms on every load:

| route | prof | CLS | shift at | `NotoSansKR_subset…woff2` start → end |
|---|---|---|---|---|
| `/` | mobile | 0.095 | 3460 / 3493 / 3557 ms | 407→3432, 439→3463, 505→3529 |
| `/stocks` | mobile | 0.138 | 3312 / 3314 / 3365 ms | 302→3296, 305→3298, 354→3350 |
| `/ask` | mobile | 0.089 | 3196 / 3200 / 3215 ms | 285→3181, 289→3184, 303→3199 |
| `/events/…329` | mobile | 0.033 | 2379 / 2380 / 2394 ms | 168→3288 (partial swap) |
| `/events/…329` | desktop | 0.011 | 462 / 496 / 535 ms | 148→268, 157→305, 158→268 |

The shift sources are never one element — they are whole bands of the document at once (`footer`,
`section.Lookup…section`, `p.Lookup…cap`, `span.RightsChip…chip`, `div.content.page…stack`,
`span.Hero…ellipseLarge`, `section.Event…facts`), which is the signature of a document-wide reflow
rather than a missing `width`/`height` on something.

**Causal test (mobile, production, `Network.setBlockedURLs ["*NotoSansKR*"]`):**

| route | as shipped | font blocked |
|---|---|---|
| `/` | CLS **0.095**, shift at 3628 ms | CLS **0.000**, no shifts |
| `/stocks` | CLS **0.138**, shift at 3313 ms | CLS **0.000**, no shifts |

**Why the fallback does not hold the layout.** The served CSS carries exactly this:

```
@font-face{font-family:notoSansKr;src:url(…/NotoSansKR_subset-s.p.3b5h9nb258jsu.woff2)…;font-display:swap;font-weight:100 900}
@font-face{font-family:notoSansKr Fallback;src:local(Arial);ascent-override:117.61%;descent-override:29.2%;line-gap-override:0.0%;size-adjust:98.63%}
```

`next/font/local`'s generated metric-matched fallback is **`local(Arial)`** — Arial carries no
Hangul, so every Korean glyph on this site paints in the *next* family in `fonts.ts`'s stack
(`system-ui`, `-apple-system`, `Apple SD Gothic Neo`, …) with **no metric override at all**. When the
291,072-byte subset finishes, the whole document re-wraps. Desktop escapes only because the font
lands in 130–880 ms — *before* first paint (FCP 352–792 ms), so there is nothing painted to shift.

**Why preloading is not the fix — measured, so nobody spends a slice on it.** Injecting a real
`<link rel="preload" as="font" crossorigin>` before the document parses (mobile, production, 2 runs
each interleaved with 2 controls):

| | font start → end | shift at | CLS |
|---|---|---|---|
| as shipped | 549→3581, 399→3424 | 3612, 3456 | 0.095 |
| with early preload | 408→3439, 406→3430 | 3469, 3461 | 0.095 |

The font request already starts at ~400 ms; the ~3 s is **transfer of 291 KB over the emulated
1.6 Mbps link**, so preloading moves nothing and removes nothing. The two levers that actually work
are a **Korean-capable metric-matched fallback** (kills the shift wherever the font lands) and a
**smaller critical subset** (moves the swap earlier); `font-display: optional` would also give CLS 0
at the price of a first visit rendered entirely in the fallback face.

## 3. INP — nothing to fix

Event Timing on production, driving what a reader actually does (each figure is the longest event of
that interaction; `proc` = the script half):

| interaction | desktop | mobile (4× CPU) |
|---|---|---|
| board tab 유증/CB/매수청구/전체 switch | 64 ms (proc 0.3 ms) | 48–56 ms (proc 4.1–4.7 ms) |
| 「15건 더 보기」 (twice) | 64–72 ms (proc 2.2–2.8 ms) | 56 ms (proc 4.4–5.2 ms) |
| hero 조회 typing (삼성전자) | 64 ms | 56 ms |
| `/ask` composer typing | 64 ms | 40 ms |
| `/events` 「[근거]」 open | 64 ms | 48 ms |
| `/stocks` lookup typing | 48 ms | 40 ms |
| `/portfolio?sample=1` 수정 / 메뉴 | 56 ms | 32 ms |
| 펼치기 (pinned strip) | 64 ms | 64 ms (proc 6.7 ms) |

Everything is inside "good" (≤ 200 ms) with a 4× CPU handicap, and the **script** half of even a
464-row tab switch is under 7 ms. Cloudflare's RUM agrees (INP p75 48 ms). This confirms rather than
contradicts RUM, so no INP fix is proposed.

## 4. Payload, per route (production, `Accept: text/html`)

| route | HTML | RSC flight | flight share | visible markup | stylesheet links | `<script src>` |
|---|---|---|---|---|---|---|
| `/` | 354,266 B | 277,870 B | **78 %** | 76,396 B | 4 | 14 |
| `/stocks` | 27,067 | 16,079 | 59 % | 10,988 | 4 | 15 |
| `/stocks/00547510` | 32,816 | 17,491 | 53 % | 15,325 | 4 | 15 |
| `/events/…329` | 57,432 | 39,353 | 69 % | 18,079 | 4 | 14 |
| `/ask` | 21,675 | 12,600 | 58 % | 9,075 | 4 | 13 |
| `/portfolio?sample=1` | 55,492 | 32,470 | 59 % | 23,022 | 4 | 16 |

Compressed on the wire the landing is **40 KB** (br) — the 345 KB is a *parse and hydrate* cost, not
a bandwidth one. Inside it:

- **278 KB is the RSC flight payload**, i.e. the whole board serialised as props for the client
  `Board` component. `/api/board` itself is 164,534 B / 393 rows (median 378 B a row) + a 24,873 B
  `open_now` strip. Only **15 rows** are in the DOM (`WINDOW_STEP = 15`), but all 393 must be there:
  `Board.tsx` filters the tabs in the browser by design ("Why the tabs filter in the browser") and
  diffs previous against next on the 60 s refresh. So the lever is **field width, not row count** —
  `BoardRow` reads `countdown.label_ko/date/dday/days` and `offering` only, while every row also
  carries `countdown.window`, `window_state`, `reference` and `source` (~135 B a row, ~35 % of the
  row) that only the event page and the lookup ever read.
- **44,441 B of the 76 KB visible markup is the Cosmos starfield** (250 elements — 37 % of the
  landing's 683 DOM nodes), and it is serialised a second time inside the flight. Cosmos is
  landing-only: `/stocks`, `/stocks/…`, `/events/…`, `/ask` and `/portfolio` contain zero
  `Cosmos-module` hits.
- JS is ~160–180 KB transferred / ~510–585 KB decoded on every route, fonts 291,072 B (Korean) +
  ~39 KB (three Plex Mono weights, `preload: false`), one image (`juju2-wordmark-white.png`,
  22,408 B, natural **1247×371**, rendered at **91×27** and **81×24**).
- Four stylesheets precede first paint on every route: three hashed chunks (2,614 / 121,497 / 1,599 B
  raw; 698 / 16,034 / 792 B on the wire) and `/foundations/tokens.css` (a `public/` file, 1,911 B on
  the wire, its own request). Nothing else is render-blocking, and Lighthouse's
  `render-blocking-resources` audit scores 1.

## 5. TTFB decomposition

| | `/` | a light route | delta = the landing's own SSR |
|---|---|---|---|
| production (browser, warm connection) | 397 ms | 142 ms (`/stocks/00547510`) | **+255 ms** |
| local production build | 122–139 ms | 18–21 ms | +105 ms |

Locally the two reads are already parallel (`Promise.all([getBoardSummary(), getBoard()])`) and cost
~70 ms together (`/board` 51–84 ms for 157,563 B, `/board/summary` 64–94 ms for 663 B), so the render
half is ~30 ms locally. On the box the same work is ~2.4× more expensive (slower CPU, 1,411 events vs
the dev corpus). Through Cloudflare, `curl` sees `/` at 534–751 ms and `/api/board` at 357–393 ms
(each with its own handshake); Lighthouse independently measures the root document's server response
at **430 / 400 / 505 ms**. Neither `getBoard` nor `getBoardSummary` sets any cache directive, so every
landing request pays the full API round trip.

## 6. Lighthouse (cross-check only, headless, its own Chrome)

| run | score | FCP | LCP | TBT | CLS | SI |
|---|---|---|---|---|---|---|
| `/` desktop ×3 | 99 / 97 / 95 | 0.6–0.7 s | 0.9 / 1.2 / 1.4 s | 0 ms | 0.001 | 0.7–0.9 s |
| `/` mobile ×3 | 86 / 77 / 81 | 1.8 s | **4.1 / 5.7 / 4.8 s** | 0–10 ms | 0–0.001 | 2.0–3.5 s |
| `/stocks` mobile | 85 | 1.7 s | 4.1 s | 10 ms | 0 | 3.1 s |

Lighthouse's mobile preset models a much slower device than the emulation above, and its LCP phase
table says the same thing this slice's own numbers do — **TTFB 684–708 ms, load delay 0, load time 0,
render delay 3,375–5,003 ms**: no resource is involved, it is document + render. Read it as "on a
slow mid-range Android the landing's LCP is at risk of crossing 4 s", not as a contradiction of the
1.56 s measured on a real throttled Chrome. Lighthouse sees no CLS at all because its trace ends
before the font swap it never waits for. Its other findings: `uses-long-cache-ttl` (4 resources —
`/assets/juju2-wordmark-white.png` and `/foundations/tokens.css` at `max-age=14400`, plus the two
Cloudflare scripts), `uses-responsive-images` (21 KB — the wordmark), `unused-javascript` 25 KB and
`legacy-javascript` 13 KB (Next's own bundle), and `bf-cache` failing for `cache-control: no-store`
on the document (inherent to request-time SSR).

## 7. The landing's idle cost — the biggest thing this slice found that is not a CWV metric

`Performance.getMetrics` deltas over a **70 s idle** window after load (production):

| page | prof | ScriptDuration | RecalcStyleDuration | TaskDuration | DOM nodes |
|---|---|---|---|---|---|
| `/` | mobile (4×) | 204 ms | **5,884 ms** | **13,100 ms** | 938 |
| `/` | desktop (no throttle) | 227 ms | **7,203 ms** | **16,584 ms** | 945 |
| `/stocks` | mobile | 0 ms | **0 ms** | 17 ms | 184 |
| `/events/…329` | mobile | 0 ms | **0 ms** | 15 ms | 361 |

The landing keeps ~24 % of a CPU core busy **forever**, on an unthrottled Mac; every Cosmos-free
route is flat zero. Isolated on desktop over 40 s by injecting CSS into a throwaway tab (client-side
only, nothing on the server):

| variant | RecalcStyle | TaskDuration |
|---|---|---|
| as shipped | 4,025 ms | 9,280 ms |
| `[class*=Cosmos-module] * { animation: none }` | 592 ms | 3,855 ms |
| twinkle keyframes rewritten with constant values (no `var()`) | 3,198 ms | 8,992 ms |
| stars hidden (drift + shooters left running) | 709 ms | 3,685 ms |

So it is the **240 simultaneously animating star elements**, not the `opacity: var(--star-opacity)`
keyframe: replacing the variable recovers only ~20 %, hiding the stars recovers ~85 % of the style
recalculation. Script cost is not the issue anywhere (204–227 ms per 70 s — the 1 s `Countdown` tick
plus the 60 s board refresh, and **zero long tasks in 8 s of idle**, which retires the plan's
"countdown re-render" hypothesis). `prefers-reduced-motion` already freezes all of it, so a reader
with that preference pays none of this.

Also measured in the same window: the 60 s 자동 갱신 poll is **one request, 18,360 B on the wire**
(164 KB raw), per open tab per minute, straight to the origin.

## 8. Cloudflare RUM — what the dashboard is actually saying

Re-queried today (7-day window; unchanged from the addendum, desktop n 173 → 175):
desktop LCP p75 **616 ms** / p50 364 ms, INP p75 **48 ms**, FCP p75 528 ms; mobile (n=11) LCP p75
1.91 s. Those are **good** by Google's thresholds. What is not good-looking is CLS — and it cannot be
a Google CLS score:

- The API's CLS is an **integer per event**. Every `(path, element)` group returns exactly
  `1.000` when a CLS element is named and `0.000` when none is, and the `p50/p75` quantiles are only
  ever `0` or `1`.
- Direct correlation against this slice's own loads settles it. In the hour of the sweep, RUM
  reports `/stocks/00547510` desktop n=60 with **CLS avg 0.800** and `/events/…329` desktop n=10
  with **CLS avg 1.000** — while the lab measured **0.000–0.002** and **0.011–0.033** on those exact
  loads. A 0.002 page cannot round to 1 on any scale; the field is "did this page shift at all".
- Cloudflare's `avg` block does expose the real LCP sub-parts, and they corroborate §1 exactly:
  `lcpResourceLoadDelay` and `lcpResourceLoadTime` are **0 on every path** (text LCP), `/` desktop =
  TTFB 625 ms + render delay 716 ms, `/` mobile = TTFB 884 ms + render delay 807 ms.
- The two shocking numbers are artefacts. `/stocks` desktop shows LCP **avg 29.5 s** with
  `lcpElementRenderDelay` **29.2 s** while its FCP is 427 ms, and `/events/00000000000000` (the 404
  echo) shows 4.9 s with a 4.8 s render delay. A visible tab cannot render-delay 29 s after painting
  at 0.4 s; these are loads in **background tabs**, where the LCP is only reported when the tab
  becomes visible. The lab measures `/stocks` at 792 ms desktop / 1,432 ms mobile.
- `/ops` (LCP p75 5.17 s, render delay 5.07 s, TTFB 137 ms) has the same signature and is an
  operator-only `noindex` surface. It was **not** lab-measured on purpose: an `/ops` login would mint
  an `OpsSession` row on production from an agent session — the boundary `P4.F4` already recorded.
- The sample is 100 % first-party: `bot=0` for all 189 events, and the whole 7-day window is
  2026-09-02/03 traffic generated by this workspace. **This slice added ~95 more production loads,
  all with a cleared cache** — which is precisely the condition that makes the font swap fire — so
  the shifted-flag rate for 2026-09-03 will read *worse* than a real reader population would.

## 9. What is not fixable app-side

The Cloudflare beacon (`static.cloudflareinsights.com/beacon.min.js`, 9,722 B, kept ON by operator
decision) and the same-origin `/cdn-cgi/scripts/…/email-decode.min.js` are edge injections; neither
is render-blocking and neither is ever the LCP. The Cloudflare → Oracle round trip is ~120–150 ms of
every TTFB on this Mac (the floor a light route measures), and it is what it is short of edge
caching the HTML — which would change what a page load's freshness means and is raised as an
operator question rather than proposed as a fix.

## Artefacts (all outside the repo, session scratchpad)

`r1_cdp.py` (CDP client + instrumentation), `r1_loads.py` / `r1_loads.jsonl` / `r1_loads.log` (the 72
cold loads, raw), `r1_analyze.py`, `r1_inp.py` / `r1_inp.jsonl`, `r1_cf_avg.py` / `r1_cf_recent.py` /
`r1_cf_probe*.py` (RUM, reusing the addendum's `cf_cwv.py`), `lh_*.json` (7 Lighthouse reports),
`r1_h_*.html` (the six served documents), `r1_board.json`, `r1fe/` (the scratch production build),
`r1_build.log`, `r1_web3014.log`. Nothing was written into the repository except `phase.md` and this
file. `npx lighthouse@12` populated the user's npm cache; nothing was installed into the project.

## Notes on the two smaller deviations

- Next 16 prints `"next start" does not work with "output: standalone"`, so the local target is
  `node .next/standalone/server.js` with `.next/static` and `public/` staged into the standalone
  directory — which is exactly what `frontend/Dockerfile` does on the box, so the local target is
  closer to production than `next start` would have been.
- The build ran in a **copy** of `frontend/` rather than in the repo, because `next build` and the
  operator's running `next dev` share `frontend/.next`; building in place would have disturbed the
  dev server on 3010.
