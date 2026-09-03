# P12.R1 — Research: the flicker hunt (findings-only, no product code)

`kind: research`, `risk: high` → `slice-executor-high` (by kind). Written 2026-09-04 by the
orchestrator in `auto` mode, after `P12.S1` landed (`62d78ec`).

## What this slice is for

`P12.DECOMP2` cannot cut the fix slices until someone has watched every user-facing page in a
real browser and written down what visibly jumps, resizes, re-paints or pops in after first
paint. That is this slice. **What you learn is the product**: findings land in `phase.md`
(ranked, located, reproducible, each with a proposed fix + risk) so `DECOMP2` can cut from them;
`result.md` keeps the log, the numbers, the refuted hypotheses and the dead ends. You write **no
product code**; a throwaway probe you delete before finishing is fine.

"Flicker" (intent.md): anything that visibly jumps, resizes, re-paints or pops in after first
paint — layout shift on load or on state change, hover/open states that move their neighbours,
content rendered twice, icons or fonts swapping after paint — watched **over time** and across
interactions, not in one static pass.

## Read first

- `phase.md` whole: `## Decisions` (instrument incl. **S1's correction** — tabs do not survive
  between `aside repl` calls, each call `openTab(url)`s and does its whole job in one script, the
  profile's cookies persist; runtime; viewports; the landing constraint; scope) and every note
  tagged `for P12.R1` — three from `P12.S1` (nav frame fixed: do not re-report; the screenshot
  traps and the recipe that works; the Space-key oddity) and four from `P12.DECOMP` (inventory,
  states, finding format, landing constraint). Consume all seven when you finish.
- `docs/current/qa.md` § *Real-browser verification (the P5 method)* — the P7 floor: both
  runtimes on `127.0.0.1` (never only `localhost`), a production build in a **copy** of `frontend/`,
  liveness ≥ 60 s for a countdown (the dev reload lands at ~40 s, so a 30 s wait is a false
  negative), locate controls by a stable key never by index, **a browser-probe FAIL is a
  hypothesis** (re-measure with a scoped selector), and **a control for every zero** (a probe that
  can only report 0 proves nothing — show it catching a known shift before trusting its zeros).
  The "Hygiene rule for a browser pass" paragraph.
- `works/phases/active/P4/slices/P4.R1/result.md` (head + the CLS section) and `P4.F5/result.md`
  (head): P4 already measured cold-cache CLS and fixed the Korean font swap. Cite, do not redo
  blindly — see *Known and accepted* below.

## Known and accepted — classify against these, do not re-litigate them

- **Cold-cache CLS from the Noto Sans KR swap is fixed** (`P4.F5`: metric-matched fallback faces
  `notoSansKr Fallback Apple / Noto / Malgun` in `app/shell.css`; mobile CLS `/` 0.0953 → 0.0002,
  `/stocks` 0.1378 → 0.0003, `/ask` 0.0894 → 0.0003). **Accepted residual, recorded by P4.REVIEW:**
  no element changes vertical position or height on the swap, but **inline advance widths may
  differ by up to ~10px** (a phone number `dx` 10.32px, an email `dw` 7.45px, Strip chips 2.9–7.2px)
  — i.e. text re-flows horizontally inside its line during the swap window. If you see it, record
  it as *known (P4), accepted*, with what it looks like at the throttled mobile profile; if you
  judge it visibly bad on some surface, that is an **`## Operator Questions`** entry (the remedy —
  `font-display`, `size-adjust` per surface, or living with it — is a product decision), not a
  silent fix proposal.
- **The event page's 「이 마감 알림 받기 →」 late insert is fixed** (`P4.F10`: auth resolved server-side
  and passed as `initialAuthenticated`). Confirm it still holds in both runtimes; a regression is a
  finding.
- **The landing's twinkle and orbiter** are byte-identical by construction (`P4.F7`/`F11`) and off
  limits; report what you see there, default answer "leave it".
- **The nav account frame's toggle** is fixed by `P12.S1` — do not re-report it.

## Hypotheses to confirm or refute (advisory, from a read-only code scan — verify every one)

A research agent read the frontend while `P12.S1` ran (it did **not** read the account slot files
or `phase.md`). Treat each item as a hypothesis with a stated mechanism; the browser decides.
Refuting one with evidence is as much a result as confirming it.

**Shared chrome, every route**
1. `components/chrome/useAccount.ts`: module store + `useSyncExternalStore`; `null` = not answered;
   the effect is keyed on `pathname`, so `GET /auth/me` **re-probes on every client-side
   navigation** and the slot re-enters `null → answered` on each route change, not only at boot.
   Signed-out the 로그인 link pops in; signed-in the frame pops in. The nav's right end reflows
   each time. Measure the gap (first paint → slot rendered) and whether anything else in the bar
   moves when the slot appears, at 1280 and 390, dev and production build, cold and warm.
2. `components/ask/AskSurface.tsx` + `useAsk.ts` `useDesktop()` starts `useState(false)` and flips
   in an effect → the fixed launcher **pops in after hydration** at ≥ 768 on every non-`/ask` route.
3. `lib/motion.ts` `useReducedMotion()` starts `false` then corrects → `Nav` / `Countdown` briefly
   "motion on" under `prefers-reduced-motion: reduce`.
4. `lib/scrollLock.ts` sets `body { overflow: hidden }` (counted) with **no `scrollbar-gutter` and
   no padding compensation** → opening the nav sheet, or the ≤ 480 feedback sheet, shifts the whole
   page horizontally by the scrollbar width on any browser with classic (non-overlay) scrollbars.
   On this Mac, overlay scrollbars hide it: check `innerWidth - documentElement.clientWidth`, and
   if it is 0 here, reproduce by forcing classic scrollbars (Chromium `--enable-features=` is not
   available through Aside; use `Emulation.setScrollbarsHidden`/a CSS probe that widens the
   gutter, or reason from the measured gutter width and say so) and record it as
   platform-conditional (Windows / Linux / macOS "always show").
5. `Nav.module.css`: the active link's bold uses a `::after { content: attr(data-label);
   font-weight: 600; visibility: hidden; height: 0 }` ghost to reserve width — the correct pattern.
   Confirm the bar does not move on route change; the pattern is the reference for item 9.
6. The bar's 메뉴 ↔ `×` swap inside a 44×44 hit at ≤ 480: confirm the floor holds and neighbours
   do not move.
7. `components/chrome/Feedback.tsx`: phase swap `editing → sending → sent | failed` **replaces the
   whole dialog body** at three heights, 닫기 is removed while sending, and the ≤ 480 bottom-sheet
   variant is bottom-anchored so its top edge jumps. Exercise one send in **dev** (a dev-DB write
   is acceptable here; say so; never on production).
8. `components/chrome/Wordmark.tsx`: raw `<img>` with `width`/`height` reserved and a
   `translateY(-8px | -6px)` ink offset — expected stable; confirm on a cold load.

**`/` landing**
9. `components/landing/Board.module.css` `.tabActive { font-weight: 600 }` with **no ghost-width
   twin** → clicking 전체 / 유증 / CB / 매수청구 re-flows the tab strip. Highest-confidence item.
10. `components/landing/Board.tsx`: a 60 s `setInterval` + `visibilitychange` refetch; a real refresh
    replaces rows, re-ranks, trims `shown`, adds a `REFRESHED_KO` chip in the header → row count and
    header width move. Watch ≥ 70 s idle and one hide/show of the tab; distinguish a product refresh
    from a dev HMR reload (~40 s).
11. `components/landing/Countdown.tsx`: 1 s tick, mono `tabular-nums` at 28px so `HH:MM:SS` is
    stable, but the head is `${days}일 ${HH}` with **unpadded `days`** → a 10 → 9 rollover shrinks the
    block (rare; note it, do not wait for it). Watch ≥ 60 s for any per-second jitter.
12. The `.more` footer row (더 보기 / 남은 N건 / 처음 N건으로 접기) appears and disappears; `Strip`'s
    펼치기 ↔ 접기 toggles an `<ol>` — expected content changes; judge whether anything **else** moves.
13. `Cosmos.module.css` `.star:nth-child(n+161) { display: none }` at ≤ 480 → a resize across 480
    re-lays 80 elements and `StarTwinkle` resyncs (250 ms debounce). Does the page visibly blink?

**`/stocks` and `/stocks/[corp_code]`**
14. `/stocks?q=…` with a match is a **server 307** (no client flash); confirm. `LookupHeader`'s
    "no match" line is gated on `typedText === submitted` → it **vanishes on the first keystroke**
    after a miss (reflow).
15. `components/lookup/StockView.tsx` reads `sessionStorage` in a mount effect → `digits` and the
    restore chip 「N주로 되돌리기」 materialise inside an already-painted `HoldingStrip` (and change its
    wrap point). Reproduce by typing a holding, navigating away and back.
16. `components/auth/ConversionOffer.tsx` inserts a multi-line band mid-page once `ready` + the
    `useAuthState()` probe + a `sessionStorage` seen-check all resolve — a post-paint insertion.
    Anonymous vs signed-in, first visit vs seen.

**`/portfolio` and `/portfolio/notifications`**
17. `Portfolio.tsx` `SessionCarry` reads `sessionStorage` in an effect → mounts `CarryOver` (a list +
    two buttons) after paint. The undo strip disappears 8 s after a delete (`UNDO_SECONDS`). Sample
    mode (anonymous) adds `ConversionOffer`.
18. `NotificationsView.tsx`: no post-paint fetch (expected quietest route); an email change
    re-publishes to the chrome store, so the frame's width changes — expected, not flicker, unless
    the bar's neighbours move.

**`/ask`**
19. `AskPage.tsx` with the module store in `lib/ask.ts`: `useSyncExternalStore`'s server snapshot is
    an empty thread → can the centred empty state swap for a thread column after hydration? A mount
    effect calls `store.close()`.
20. `components/ask/Composer.tsx`: one button cycles 보내기 / 답변 준비 중… / 중지 — **three widths in
    one slot**, resizing the input beside it; `ToolTrace` folds/unfolds mid-stream; the widget pins
    `scrollTop` per block. Run **one** live turn in dev and watch the composer row and the thread
    (the widget is `≥ 768` only; at 390 the page is the surface).

**`/events/[rcept_no]`**
21. `DeadlineOffer` with `initialAuthenticated` — confirm no late insert (the P4.F10 fix), both
    runtimes, anonymous and signed-in.
22. `components/event/Corrections.tsx`: the history button **gains a `×` span when open** (widens);
    fetch-on-open expands a hidden panel; failure leaves it empty (a press that visibly does
    nothing). `useScopePresets` sets `[]` then fills a chip row inside the open widget.

**`/auth/login` and `/auth/reset`**
23. `AuthPanel.tsx`: `useEffect` → `readFlashOnce()` → after a logout the **로그아웃되었습니다 line is
    inserted above the form after paint** — real CLS on a small panel. Reproduce: sign in, 로그아웃
    from the menu, measure the landing on `/auth/login`.
24. `/auth/reset`: no post-paint fetch expected; confirm.

**Cross-cutting**
25. **IBM Plex Mono ships `display: swap`, `preload: false`, generic fallbacks only and no metric
    overrides** (`app/fonts.ts`), while Noto got the full P4.F5 treatment → every mono numeral
    (D-days, won totals, 기준시각, 접수번호, 종목코드, the 28px countdown) can re-flow when Plex Mono
    lands on a cold cache. The highest-value font-swap suspect; measure it at the throttled mobile
    profile on `/`, `/stocks/[corp_code]`, `/portfolio`, `/events/[rcept_no]`, and correlate shifts
    with the font's load event.
26. `components/Citation.tsx` / `ask/InlineCitation.tsx` measure `getBoundingClientRect()` in a ref
    callback at the mounting commit (so the first paint is already clamped) and re-fit on resize —
    confirm no double paint under StrictMode in dev vs none in production.
27. `Launcher.module.css` `.launcher:hover .mark { transform: scale(1.35) }` on a fixed element —
    composited, but large enough to read as a jump: report as a judgment call for the operator, not
    a defect.
28. `P12.S1`'s oddity: the account frame did not open on **Space** through Aside; `Enter` did. One
    real key event settles whether the native `<button>` ignores Space (a genuine finding) or the
    instrument does.

Anything the scan did not name is exactly what the walk is for: **also look where the list does
not point**, page by page, with fresh eyes.

## Method

**Instrument.** Aside, `aside repl --account u2 "<js>"`, one tab per invocation via
`await openTab(url)`, top-level `await`, cookies persisting across calls (S1's corrected recipe).
CDP is reachable inside the repl (`cdp.send(...)` — S1 used it); use it for device metrics, CPU and
network throttling, and cache control. Screenshot recipe and traps: S1's note (full-viewport
`page.screenshot()` cropped outside the browser; `Page.captureScreenshot` with `clip` is stale;
`clip` is in device pixels of the real 1440×900 window). Name the instrument in `result.md`; the CDP
fallback only if Aside is genuinely unavailable, and then say so.

**Runtimes.** Dev `http://127.0.0.1:3010` (already up — `make stack-status`; leave it as found) and
the local production build on **3014**. S1's build sits at
`/private/tmp/claude-502/-Users-sugang-projects-personal-Mijual/4d8eac95-f4f0-458f-9341-c63977936afe/scratchpad/p12s1-build/`
and was built from S1's final tree; reuse it only after `diff`-ing its two `AccountSlot.*` files
against HEAD's (identical → reuse; else rebuild in a fresh copy outside the repo, the recipe in
`phase.md`). Stop the server when done. **Production `https://jujutower.com` is read-only:** use
it for the cold-cache mobile loads of the public routes (real font delivery through Cloudflare is
the thing dev cannot show) and nothing that signs in or writes.

**Viewports.** 1280 and 390 as the primary pair; **412×915 @ DPR 2.625, 4× CPU, ≈1.6 Mbps / 150 ms,
cache cleared** for the cold-cache loads; a resize sweep through **390 · 479 · 481 · 600 · 767 ·
769 · 1000 · 1119 · 1121 · 1255 · 1257 · 1440** (the chrome's and pages' breakpoints are 480/481,
767/768, 1119, 1255; the JS boundaries are `DESKTOP_QUERY` 768 in `useAsk.ts` and `MOBILE_QUERY`
480 in `Feedback.tsx`). `prefers-reduced-motion: reduce` once on `/` and the nav sheet.

**Signed-out and signed-in.** Create one throwaway account through the signup form in dev,
exercise the signed-in states (`/portfolio` real, `/portfolio/notifications`, `/stocks/[corp_code]`
and `/events/[rcept_no]` signed in, the account menu, 로그아웃 → the `/auth/login` flash), and delete
it through `/portfolio/notifications` → 계정 삭제 before you finish. Never sign in on production.

**Live ids.** Pull them from the dev API, not from memory: `GET http://127.0.0.1:8010/board`
(`rows[]` with `corp_code`, `corp_name`, `rcept_no`, `countdown.dday`, optional `offering`),
`/board/summary` (`next_lapse.target` drives the ticking countdown), `/stocks/suggest?q=…`,
`/stocks?q=…`, `/events/{rcept_no}`. At plan time 툴젠 `00547510` / `20260806000329` (D-4, has an
`offering`), 제이에스링크 `00642541` / `20250902000288` (D-DAY), 알에프텍 `00309831` /
`20260804000294` (D-19); `/stocks?q=툴젠` → 307 → `/stocks/00547510`, `/stocks?q=zzz` → the
no-match surface. Re-fetch; D-days move daily.

**Measurements** (pick per page; these are the primary evidence, screenshots the secondary):
- **`PerformanceObserver({ type: "layout-shift", buffered: true })`** installed before navigation
  completes (inject at `openTab` time or as early as the repl allows), recording `value`,
  `hadRecentInput`, `startTime` and each `sources[]` entry's node (a stable path: tag + id/class +
  text head) with `previousRect → currentRect`. Bucket by window: load (0–5 s), each interaction,
  idle. **Control:** before trusting any zero, show the observer catching a deliberate shift (e.g.
  inject a 40px spacer once and remove it).
- **Keyed rect diff:** snapshot `getBoundingClientRect()` for every visible element that has a
  stable key (role + accessible name, `data-*`, or a generated DOM path) before and after each
  interaction and across an idle window; report every rect that moved without being the
  interaction's target or inside its own opened panel.
- **Late-insert timeline:** a `MutationObserver` from as early as possible, logging added/removed
  nodes with `performance.now()` and their rects, alongside `performance.getEntriesByType("paint")`
  and `document.fonts.ready` / per-`FontFace` load timing — this is how item 1, 2, 15–17, 23 and 25
  are attributed.
- **Timed windows:** ≥ 70 s on `/` (the 60 s board refresh + the countdown), ≥ 60 s on any other
  animated surface; one live `/ask` turn end-to-end.
- **Hover sweep:** for every visible control on each page, hover → rect diff of the control **and
  its neighbours**; then focus (keyboard) → the same.
- Screenshot pairs only where pixels are the evidence (font swap, the caret-style ink checks,
  something a rect cannot express).

**Order of work.** Chrome first (items 1–8, every route inherits them), then `/`, then the two
`/stocks` routes, `/portfolio` ×2, `/ask`, the event page, `/auth` ×2; dev at 1280 → dev at 390 →
the production build at both → cold-cache throttled mobile on the production build and on
`jujutower.com` (public routes) → the resize sweep. If time forces a cut, cut the sweep's inner
widths before anything else, and say what you cut.

## What a finding must record (DECOMP's format, restated so nothing is lost)

Route · viewport · runtime(s) where it reproduces (dev / production build / production) · the
element (file + selector or stable key) · what moved and by how many px, or which paint/repaint,
with the measurement that shows it · a reproduction another agent can replay in one paragraph ·
a **proposed fix with its risk** (`low` only for a genuine one-line single-file edit) · the **root
cause**, so `DECOMP2` can merge findings that share one (one slice per independent cause) · a
**rank** (what a reader sees first, worst first) · and, when the remedy is a product decision
rather than a bug, the question for `## Operator Questions` instead of a fix.

Refuted hypotheses get one line each with the control that refuted them. Known-and-accepted items
get their classification and the evidence.

## Notebook (`phase.md`) when you finish

- `## Decisions`: what the hunt settled — the inventory's shape (how many real, how many refuted,
  how many product decisions), the classification of the P4 residual, and any method fact the
  next slices must rely on (e.g. "the observer must be installed before … or it misses …").
- `## Notes for later slices`: **one entry per finding, tagged `**(from P12.R1, for P12.DECOMP2)**`,
  ranked, in the format above** — this list *is* the deliverable. Remove the seven `for P12.R1`
  notes you consumed. Keep the `for P12.DECOMP2` and `for P12.S2` notes from DECOMP.
- `## Operator Questions`: append every product-decision question (font-swap residual, launcher
  hover scale, board re-rank behaviour, anything else that is taste rather than defect).
- `## Doc impact`: append one `qa` line if the Aside method traps S1 and you found (screenshot
  clip semantics, stale `captureScreenshot`, tabs not surviving invocations, top-level `await`)
  are durable qa truth — they are, so write it, naming both slices.
- `## Now` (≤ 15 lines): the hunt is done, `P12.DECOMP2` is next and cuts from the ranked list,
  how many findings and which are top-3, the freeze date, production still on `a74c58a`.

`result.md`, verdict block first: status, summary (the inventory in two sentences), files_changed
(`phase.md` and `result.md` only — no product files), validation (`python3 scripts/workflow.py
validate`, plus every measurement command/script you ran and its outcome, including the controls),
deviations (what you could not reach or cut, and why), doc_impact. Then the log: per route the
numbers, the refutations, the dead ends, and the production-build vs dev differences written down
(the P7 rule).

## Do not

- write or leave any product code, test file, or `plan.md`; commit; run any workflow state command;
- sign in, submit, or write anything on `https://jujutower.com`;
- drive Aside account `u0`; run `aside profile list`;
- skip a route silently — an unreachable route is a stated deviation.

## Return

The structured verdict, `result.md` first with the same block at its head.
