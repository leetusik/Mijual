# P4.R1 — research: Core Web Vitals on production (LCP / INP / CLS) — what Cloudflare RUM reports, why, and the fix breakdown

`kind: research`, `risk: high`, `slice-executor-high`. Findings-only: **no product code**. Operator
instruction, 2026-09-02 ~22:20 KST, verbatim: 「you look up the cloudflare's poor LCP, INP, and CLS
performance stuffs … and create slices for fix them.」 The operator saw Cloudflare Web Analytics
(enabled by them, `P4.F2`) rating the site's Core Web Vitals **poor**. This slice finds out **which
routes, which metric, how bad, and why**, and proposes the fix slices; the orchestrator cuts them
from your findings (fix slices, not a `DECOMP2`). Every fix must be deployable **before the freeze
opens 2026-09-07 11:00 KST**, so favour findings that map to small, certain changes.

## What is already known (orchestrator, 2026-09-02, read-only GETs through Cloudflare)

| route | TTFB (3 samples) | HTML size |
|---|---|---|
| `/` | 0.60–0.75 s | **345 KB** |
| `/stocks` | 0.43–0.66 s | 26 KB |
| `/stocks/00547510` | 0.26–0.31 s | 32 KB |
| `/events/20260806000329` | 0.24–0.77 s | 56 KB |
| `/ask` | 0.38–0.54 s | 21 KB |
| `/portfolio?sample=1` | 0.39–0.63 s | 56 KB |

`/api/board` alone is 164 KB and answers in 0.40–0.58 s. Nothing is prerendered (every reader route is
request-time SSR + a FastAPI round trip). The landing's `Board` is a client component holding the
whole board in state (`components/landing/Board.tsx`, 472 lines), `Countdown.tsx` re-renders on a
1 s `setInterval`, `Cosmos.tsx` (146 lines) is the animated background, fonts are self-hosted
`next/font/local` subsets with `display: "swap"` (`app/fonts.ts`). 46 client components in all.
Cloudflare injects the RUM beacon (`static.cloudflareinsights.com`) and Email Obfuscation
(`/cdn-cgi/scripts/…/email-decode.min.js`) at the edge. These are leads, not conclusions.

## Deliverable 1 — the RUM numbers (if a credential is available; otherwise say so and go on)

The orchestrator will append an addendum below naming **where** a Cloudflare API token with
*Account Analytics: Read* lives (a file path; never print it). If it is present, query the GraphQL
Analytics API (`https://api.cloudflare.com/client/v4/graphql`) for the last 7 days:
`rumWebVitalsEventsAdaptiveGroups` (dimensions `requestPath`, `deviceType`, `userAgentBrowser`;
quantiles `largestContentfulPaintP75`, `interactionToNextPaintP75`, `cumulativeLayoutShiftP75`;
`count`), and `rumPageloadEventsAdaptiveGroups` for visit counts per path — the account id and the
site tag (`siteTag`) come from `accounts { rumPageloadEventsAdaptiveGroups … }` or the dashboard
URL the operator gives. Record: per path × device the p75 of each metric, sample counts, and which
of the three is *poor* by Google's thresholds (LCP > 4 s, INP > 500 ms, CLS > 0.25; *needs
improvement* above 2.5 s / 200 ms / 0.1). Read the token into a shell variable from the file and
pass it only as an `Authorization: Bearer` header; if the file is absent or the API refuses, record
that in one line and continue with Deliverable 2 — **do not stop the slice for it**.

## Deliverable 2 — lab reproduction with attribution (required)

Instrument: real Google Chrome over CDP, headful, throwaway profile, fresh port (`open -na "Google
Chrome" --args --remote-debugging-port=<p> --user-data-dir=<scratchpad dir>`; a `nohup` launch is
headless and does not count; never the operator's profile). Two device profiles: **mobile** (412×915,
DPR 2.625, `Emulation.setCPUThrottlingRate` 4, `Network.emulateNetworkConditions` ≈ slow 4G:
150 ms RTT, 1.6 Mbps down) and **desktop** (1280×800, no throttling). Routes: `/`, `/stocks`,
`/stocks/00547510`, one live `/events/{rcept_no}` from `/api/board`, `/ask`, `/portfolio?sample=1`.
Targets: **production `https://jujutower.com`** (the real thing, through Cloudflare) and the **local
production build** (`cd frontend && NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build && npm
run start -- -p 3014` against the dev API on `127.0.0.1:8010`, started additively — never stop the
operator's stack) for attribution without network noise. Three cold loads per route × profile ×
target; report medians.

Measure, per load, with `PerformanceObserver` injected via `Page.addScriptToEvaluateOnNewDocument`
(buffered `largest-contentful-paint`, `layout-shift` with `sources`, `longtask`, `event` /
`first-input`, `navigation` and `resource` timing):

- **LCP**: the element (tag, class, text prefix), its time, and the breakdown TTFB → resource load
  delay → load time → render delay. Is the LCP a text block, the hero, a board row, an image, the
  Cosmos canvas? Does the 345 KB HTML or hydration delay it?
- **CLS**: every shift ≥ 0.01 with its source nodes and when it happens — font swap (does
  `fonts.ts` set fallback metrics / `adjustFontFallback`?), the countdown mounting, the 갱신됨 banner,
  the board's tab or window change, images without dimensions, the Cosmos background.
- **INP** (lab proxy): drive the interactions a reader actually makes and read Event Timing —
  board tab switch, 「15건 더 보기」, a row click, typing in the hero search, opening `[근거]`, the
  composer on `/ask` — plus **long tasks** during hydration (count, total, the longest) and the
  main-thread cost of the 1 s countdown tick and the 자동 갱신 poll.
- **Payload**: per route the HTML bytes, the RSC payload bytes, JS transferred and executed (from
  `npm run build`'s route table and the resource entries), fonts, and whether anything render-blocking
  precedes first paint.
- **Lighthouse** as a cross-check only (`npx lighthouse <url> --preset=…` for mobile and desktop,
  three runs, report LCP / CLS / TBT and the top opportunities) — it does not measure INP.

Keep production read-only: no `/api/ask` turn (open `/ask`, type, do not send), no account, no writes.

## Deliverable 3 — the findings and the fix breakdown, in `phase.md`

Write into `phase.md` (this is the point of the slice; `result.md` keeps the raw numbers and the
method): a **findings** block under `## Notes for later slices` tagged `(from P4.R1, for the fix
slices)` and a `## Decisions` line for anything settled. For each poor/needs-improvement metric ×
route: the measured value (RUM p75 if available, lab median), the **attributed cause**, and the
**smallest change that fixes it**, with a confidence and an estimated effect. Then a proposed fix
list — `P4.F5`, `P4.F6`, … — one line each: scope, files, risk, expected gain, deploy needed
(yes for anything in `frontend/` or `src/`). Rank by gain ÷ risk; say which are safe to land
before 09-07 11:00 KST and which should wait for 09-12. Candidate directions to test, not to assume:
the landing SSRs only the first window per tab and streams or lazily loads the rest (345 KB → ?);
the RSC payload duplicating the board; `Countdown`'s 1 s re-render isolated from the board; font
fallback metrics for swap; explicit sizes for whatever shifts; deferring `Cosmos`; `revalidate`/
cache headers for the board API through Cloudflare (mind `no-store` on `/ask` only); anything
render-blocking. Also note what is **not** fixable app-side (Cloudflare's own injected scripts,
the edge round trip).

Rewrite `## Now` (≤ 15 lines) for the orchestrator: which fix slices to cut, in what order, and the
freeze arithmetic.

## Hard rules

No product code, no `docs/current` edits, no deploy, nothing on the box, production read-only, never
the operator's Chrome profile, keep the operator's dev stack up, stop every server and browser you
start (record pids/ports), no secret values anywhere (the API token is read from a file into a
variable and never echoed; the repo is public), no `git commit`/`push`, no workflow state commands,
`uv run` without `--with`. Model calls: **0**.

## Validate

`python3 scripts/workflow.py validate` passes; `git diff --stat` → `phase.md` and this slice's
`result.md` only (plus any scratchpad files outside the repo). `result.md` verdict-block-first with
the instrument, profiles, sample counts, and the RUM status (fetched / unavailable — why).

## Addendum (orchestrator, 2026-09-02 ~22:50 KST) — the RUM numbers are already fetched; here they are

**Credential (operator-authorized, 2026-09-02):** the Cloudflare API token lives in
`/Users/sugang/projects/personal/changple5/.dev.env` as `CLOUDFLARE_ANALYTICS_API_TOKEN`, with
`CLOUDFLARE_ACCOUNT_ID` beside it (Account Analytics: Read; it sees every Web Analytics site in the
account). Read both with `grep -m1 '^KEY=' … | cut -d= -f2-` into shell variables; never print them,
never copy the file. **jujutower.com's site tag is `069a0b8251634dc09e6cd7cf2f1b4111`.** A working
query script is at
`/private/tmp/claude-502/-Users-sugang-projects-personal-Mijual/79e813fa-984f-4074-b1b7-7f62151138db/scratchpad/cf_cwv.py`
(`python3 cf_cwv.py <siteTag> <days> [device|path|elem|perf|all]`) — reuse it, extend it, do not
re-derive the field names. Quantile values are **microseconds** (LCP `612000` = 612 ms); CLS comes
back as an **integer 0/1 per event** (avg 0.27 desktop), which is either Cloudflare rounding the
score or a scale quirk — treat RUM CLS as "shifted / did not shift", not a score, and let the lab
give the number.

**The sample is polluted and you must say so in the findings:** the site went public today; every
one of the 170 pageloads (30 visits) is dated 2026-09-02, and most were this workspace's own
automated review / 첨부2 / F2 sessions (real Chrome over CDP at 1280 and 390, many rapid loads,
background tabs). The p99 LCP of 73 s on `/stocks` and 14 s on `/events/00000000000000` are almost
certainly tabs that were not visible when they loaded. Weight the lab; recommend re-reading RUM
after a few days of real readers.

Last 7 d (= today), p75 unless noted:

| cut | n | LCP | INP | CLS (0/1) | notes |
|---|---|---|---|---|---|
| desktop, all | 173 | 612 ms (p50 364) | 48 ms | p75 1, avg 0.27 | FCP 492 ms |
| mobile, all | 11 | 1.91 s (p50 1.75) | n/a | 1 | FCP 1.9 s |
| `/` desktop | 31 | **1.23 s** | 8 ms | 1 | nav timing: request 924 ms, response 384 ms, render 329 ms, FCP 1.12 s, load 2.37 s |
| `/` mobile | 11 | **1.91 s** | n/a | 1 | |
| `/portfolio` desktop | 38 | 468 ms | 64 ms | 0 | |
| `/ask` desktop | 20 | 416 ms | 48 ms | 1 | |
| `/ops` desktop | 16 | **5.17 s** | n/a | 0 | operator-only surface; LCP = the run-log table |
| `/events/20260806000329` | 16 | 220 ms | 0 | 0 | |
| `/stocks/00547510` | 14 | 232 ms | 40 ms | 0 | |
| `/stocks` | 9 | 73 s (!) | n/a | 0 | background-tab artefact? verify |
| `/events/00000000000000` (404) | 9 | 14.2 s (!) | n/a | 0 | same question |

LCP elements (RUM): the landing **hero `h1`** (`Hero-module__title`, n=22, 1.75 s p75), the footer's
`p.source` (n=18), the portfolio banner (n=16), the 실적 anchor card paragraph (n=8), and 86 events
with an empty element (early-abandoned or hidden loads). **CLS elements (RUM):** `Hero-module__stats`
(n=13 — the landing headline pair; does it mount or resize after first paint?), the `LapseAlert`
aside (n=6 — the 소멸주의보 panel), `Event-module__facts` / `Event-module__sec` (n=4), the portfolio
`deadlines` block (n=2), the footer (n=1), an ask 답변 block (n=2). INP elements: the portfolio
primary action (64 ms), lookup presets (40 ms), the ask launcher (48 ms) — all far inside "good".

**So the questions to answer, in priority order:** (1) the landing at mobile: what part of the
1.9 s is TTFB (the 924 ms request time is the SSR + `getBoard`/`getBoardSummary` round trips — are
they sequential? is `/api/board` itself slow at 0.4–0.58 s for a persisted read, and would a short
in-process cache keyed on `as_of` cut it?), what part is the 345 KB HTML, what part render delay;
(2) what actually shifts on the landing (`Hero-module__stats`, the `LapseAlert` aside) and on the
event page (`facts`), with a lab CLS number per route; (3) whether `/ops`'s 5 s LCP is the table's
SSR or the agent's throttled sessions (low priority: operator-only). INP needs no fix unless the
lab contradicts RUM. Then the fix list, ranked, with the freeze arithmetic.

## Addendum 2 (orchestrator, 2026-09-03 00:55 KST) — state at dispatch

- **Production is now at `1a93d7b`** (`P4.F4` deployed 2026-09-03 00:26 KST; rollback point
  `96f7141`), not `96f7141` as the F2-era notes say. The frontend did not change in that release, so
  every landing/route measurement above still describes what is live. Measure production as it is.
- **It is 2026-09-03**, so "last 7 days" now spans two calendar days; the RUM sample is still the
  workspace's own traffic (the F4 deploy's smoke runs are `curl`, which never fires the beacon).
  Re-query with `cf_cwv.py` for the day split if it is cheap; do not spend the slice on it.
- **Local target:** the dev API answers on `127.0.0.1:8010` (its health is `/health`, not
  `/api/health`; the Next rewrite maps `/api/*` onto it), the operator's dev frontend is on `3010`.
  Your production build goes on **3014**, additively; the dev API's data predates `P4.F1`'s sample
  portfolio, which is irrelevant to rendering-cost attribution but means `/portfolio?sample=1`
  locally may not match production's content — say so if it matters, measure production for it.
- **No beat window is near for the lab** (next `daily-pipeline-morning` 07:30 KST) — irrelevant to
  a read-only lab, noted only so you do not wait for one.
- The fix list you propose is cut by the orchestrator as `fix` slices **`P4.F5`, `P4.F6`, …**
  ordered before `P4.REVIEW`; give each a one-line name the orchestrator can use verbatim.
