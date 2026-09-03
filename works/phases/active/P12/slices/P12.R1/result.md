# P12.R1 — result

- **status:** done
- **summary:** Walked all 10 user-facing routes in a real browser (Aside, agent account `u2`) at 1280 /
  390 / 412-cold-throttled, signed out and signed in, in `next dev`, a local production build and on
  `https://jujutower.com`, watching over time rather than in snapshots. **All 28 hypotheses are
  settled — 13 confirmed, 8 refuted with controls, 6 confirmed-clean, 1 an instrument artefact — plus
  3 findings the list never named**, delivered as a ranked, located, reproducible **F1–F14** in
  `phase.md` with a proposed fix, a risk and a root cause each. The 14 collapse into **four root-cause
  families**, which is how `P12.DECOMP2` should cut them. No product code was written.
- **files_changed:** `works/phases/active/P12/phase.md`,
  `works/phases/active/P12/slices/P12.R1/result.md` — **no product files** (`git diff --stat -- frontend/`
  is empty). Every probe lived in the session scratchpad, outside the repo, or inside a browser tab that
  was closed.
- **validation:**
  - `python3 scripts/workflow.py validate` → **passed** (pre-existing warnings only: `consolidation_owed=P4`,
    `stale_docs=product`, `oversized_doc_sections=11`)
  - `git diff --stat -- frontend/` → **empty** (no product code written, the slice's central constraint)
  - `git show HEAD:…/phase.md | diff` on the `<!-- slices:begin/end -->` block → identical but for the
    engine's own `todo` → `in_progress` cell
  - **Instrument control #1 (the LS observer + rect diff work):** injected a deliberate 40 px spacer on
    `/` at 1280 → the `layout-shift` observer caught it (**v = 0.03125**, source `SiteChrome__frame`) and
    the rect diff reported **324 elements at dy +40**. Both instruments proven before any zero was trusted.
  - **Instrument control #2 (the H9 zero is a measurement):** the board tabs are byte-identical at
    font-weight 400 / 600 / 900, so the probe was re-run with one label swapped to Latin — it caught
    **69.36 → 72.34 px (+2.98)**. The Korean zero is real, not a dead probe.
  - **Idle noise floor established before any diff was believed:** 9 s idle on `/` at 1280 → 246 moved
    elements, **all** of them `Cosmos-module__star` / `__streak` / `Hero-module__orbiter`, CLS 0.
  - Per-route load sweep with `PerformanceObserver({type:"layout-shift", buffered:true})` +
    `MutationObserver` + a 12 ms rect sampler: **10 routes × 1280 dev**, **10 × 390 dev**,
    **10 × 1280 production build**, **3 × 412 cold-throttled production build**, **2 × 412 cold-throttled
    `jujutower.com`** — 45 instrumented loads.
  - Timed windows: **78 s** on `/` (78 countdown ticks), **one live `/ask` turn end to end** (~50 s,
    433 chars of answer), 16 s per cold-throttled load.
  - Hover sweep: **87 controls** across `/`, `/stocks/00547510`, `/portfolio` — hover then rect-diff the
    control *and its neighbours*.
  - Resize sweep: **12 widths** (390 · 479 · 481 · 600 · 767 · 769 · 1000 · 1119 · 1121 · 1255 · 1257 · 1440).
  - Click sweeps on the event page and the landing; signed-in pass on a throwaway account created and
    deleted through the product's own 계정 삭제.
- **deviations:** five, all recorded below — (1) **H4 could not be reproduced on this machine** and I did
  not claim the zero (macOS overlay scrollbars ignore a forced `html::-webkit-scrollbar` width), so F14 is
  filed as latent-by-inspection with an operator question rather than a verified defect; (2) **H10 needed a
  throwaway in-page `window.fetch` patch** to move `as_of`, because the dev corpus is static and `Board.tsx`
  deliberately no-ops on an unchanged stamp — the patch lived in one closed tab and touched no file;
  (3) **F4, F2 and F13 are measured in dev only** (they need a signed-in session and the throwaway account
  was deleted for hygiene) — F3, the same Family-A cause, *was* re-measured on the production build and came
  out numerically identical, which is the runtime evidence for the family; (4) **two real feedback rows were
  written to the dev DB** (receipts `3db29cc4…`, `d316b57b…`) — the plan permits a dev-DB write for H7;
  production was never written to; (5) the plan's `p12s1-build` was **reused** rather than rebuilt after
  `diff` showed both `AccountSlot.*` files byte-identical to HEAD.
- **doc_impact:** two `qa.md` lines appended to `phase.md` — the **Aside repl measurement seam** (CDP via
  `page._sendToTarget`; an init script runs while `document.documentElement` is still `null` so a
  `MutationObserver` must `observe(document)` or it returns a **false clean zero**; `page.evaluate` takes one
  argument; ~80 s per invocation; tabs die between calls, cookies do not; the two screenshot traps) naming
  both `P12.S1` and `P12.R1`; and the **rect-diff key must be insertion-robust** + the landing's Cosmos idle
  noise floor.
- **doc_versions:** n/a (not a review slice — versioning is deferred to a docs phase)
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a
- **operator_need:** none to proceed — `P12.DECOMP2` can cut 12 of the 14 findings today. But **F1 and F5
  cannot be cut until the operator answers Q1 and Q2**, and `## Operator Questions` now carries **Q1–Q5**
  (the first entries this phase has raised), every one of which must be routed at the review.

---

## 1. Instrument, and what it cost to make it trustworthy

**Aside, `aside repl --account u2` (profile 「claude2」), throughout.** The operator's `u0` was never
driven, `aside account use` was never run, and `aside profile list` was never called. The CDP fallback was
not needed. Roughly 40 invocations.

Four sharp edges cost real time and are now durable `qa` truth (see *Doc impact*):

1. **There is no top-level `cdp`.** `page.context()` returns `null`, so `newCDPSession` does not exist.
   CDP is `page._sendToTarget(method, params)` — proven with `Browser.getVersion` → `Chrome/151.0.7922.171`.
   Everything else (device metrics, CPU/network throttling, cache clearing, emulated media, and the
   `Input.dispatchKeyEvent` that settled H28) went through that one call.
2. **The MutationObserver silently died on every route, and looked like a clean result.** An init script
   installed with `Page.addScriptToEvaluateOnNewDocument` runs *before* the document exists, so
   `document.documentElement` is `null` and `observe()` throws:

   ```
   {"log":["mo TypeError: Failed to execute 'observe' on 'MutationObserver': parameter 1 is not of type 'Node'."],
    "nMut":0,"hasMo":false}
   ```

   Until this was caught, the whole first sweep reported `lateIns: []` on all 10 routes — a perfect,
   entirely false, clean bill of health. `observe(document)` fixes it. **This is the P7 "a control for
   every zero" rule paying for itself**: the zero looked like the answer and was a broken probe.
3. **`page.evaluate` accepts exactly one argument.** `evaluate(fn, a, b)` throws; pass `[a, b]`.
4. **An invocation running much past ~80 s loses the daemon** (`fetch failed: other side closed`), so the
   10-route sweeps were split one route per invocation.

**Two keying facts, both learned the hard way.** A rect-diff key built from a DOM path renames every later
sibling when a node is inserted — so the very first control (the 40 px spacer) showed up as
`movedCount: 1` with only `#doc` changing, hiding a shift the LS observer had plainly caught. Keying on
`tag#id.classes` + occurrence index fixed it. And on `/` the **idle noise floor is the Cosmos star field
alone** — 246 elements move over 9 s and every one is `Cosmos-module__star` / `__streak` /
`Hero-module__orbiter`, with CLS 0 — so any landing diff must filter them or drown.

## 2. Runtimes, and the difference between them

| runtime | how | what it was for |
|---|---|---|
| `next dev` | `http://127.0.0.1:3010`, StrictMode, already up, left as found | the primary sweep, all interactions, the signed-in pass |
| local production build | `p12s1-build` on **3014**, `node .next/standalone/server.js`, reused after `diff` | the P7 second runtime + cold-cache font work |
| production | `https://jujutower.com` (`a74c58a`), **read-only** | real font delivery through Cloudflare |

**The P7 rule's answer: no product behaviour differs between dev and the production build — only speed.**
The strongest single piece of evidence is F3, measured on both:

| | dev 3010 | production build 3014 |
|---|---|---|
| FCP | 88 ms | 88 ms |
| cells inserted at | t = 124 ms (+36) | t = 91 ms (**+3**) |
| CLS | **0.04785** | **0.04785** |
| `Lookup__section` | y 631.67 → 643.72 | y 631.67 → 643.72 |
| `Lookup__chainfoot` | y 503.67 → 538.67, h 65 → 42.05 | y 503.67 → 538.67, h 65 → 42.05 |

The chrome pop-in (F1) is the one place the runtimes visibly diverge, and only in degree: dev lands it
**44–293 ms after FCP on 10/10 routes**; the production build lands it **3–165 ms** after FCP, and on
`/stocks`, `/stocks/00547510`, `/auth/login` and `/auth/reset` it arrives *before* first paint and is
invisible. Production is milder everywhere and absent nowhere that matters. F5 reproduced on
`jujutower.com` with **byte-identical deltas** to the local build.

## 3. Per-route numbers

### The load sweep, 1280 dev (warm), 10/10 routes

Every route: **CLS 0**, and exactly two late inserts — the launcher and the account slot.

```
/                     fcp=364  launcher +288  slot +293   cls=0
/stocks               fcp=224  launcher  +46  slot  +46   cls=0
/stocks?q=zzz         fcp=172  launcher  +67  slot  +69   cls=0
/stocks/00547510      fcp=168  launcher  +46  slot  +49   cls=0
/portfolio            fcp=168  launcher  +51  slot  +52   cls=0   + Auth__offer 110px @ +53
/portfolio/notif.     fcp=196  launcher  +44  slot  +46   cls=0
/ask                  fcp=160  launcher   —   slot  +70   cls=0   (no launcher on /ask, by design)
/events/2026080600…   fcp=200  launcher  +49  slot  +51   cls=0   (no DeadlineOffer insert → P4.F10 holds)
/auth/login           fcp=112  launcher  +53  slot  +56   cls=0
/auth/reset           fcp=144  launcher  +69  slot  +73   cls=0   (no post-paint fetch → H24 clean)
```

At **390 there is no launcher and no visible slot pop-in at all** (the launcher is gated on
`DESKTOP_QUERY` 768; the desktop slot is not rendered below 481 and the sheet's login row is 0×0 until
the sheet opens), and CLS is 0 on all ten routes. **F1 is a desktop-only defect.**

### Cold-cache throttled mobile (412×915, DPR 2.625, 4× CPU, ≈1.6 Mbps, cache cleared)

The font attribution, from resource timing on `/stocks/00547510`:

```
NotoSansKR_subset.woff2          171 -> 2973 ms   284 kB
IBMPlexMono_Regular_subset.woff2 574 -> 1075 ms    12 kB
IBMPlexMono_SemiBold_subset.woff2 578 -> 1245 ms   13 kB

t=610   dday w=106.13 @272.88   cval w=113.53 @250.47     (fallback metrics)
t=1110  dday w= 92.42 @286.58   cval w=113.53 @250.47     <- Plex Mono Regular landed at 1075
t=1269  dday w= 92.42 @286.58   cval w= 97.20 @266.80     <- Plex Mono SemiBold landed at 1245
```

Two separate reflows, ~170 ms apart, at ~350 ms and ~510 ms after FCP. **Noto finished at 2,973 ms and
produced no element shift whatsoever** — `P4.F5` is doing exactly what it was built to do, and the whole
remaining cold-cache font problem is the 25 kB mono pair that never got the same treatment.

`document.fonts.ready` is **useless here** — it resolved at ~180 ms on every cold load, long before any
font was requested. Resource timing is the instrument.

### The signed-in pass

A throwaway account (`p12r1+…@example.com`) was created through the signup form in dev, driven, and
deleted through `/portfolio/notifications` → 계정 삭제 (which landed on `/`, signed out, 로그인 link
restored). While signed in:

```
/portfolio            fcp=148  cls=0.06097  Portfolio__carry 195.28px inserted @ +72ms, page +215.28px
/portfolio/notif.     fcp= 88  cls=0        (quietest route in the product)
/stocks/00547510      fcp=148  cls=0        frame 261.28px pops in @ +37ms
/events/2026080600…   fcp=188  cls=0        no DeadlineOffer insert — P4.F10 holds signed in too
```

Signed in, the pop-in is **much worse in area** than signed out — the 261.28 px account frame rather than
the 37.27 px 로그인 link — which is what makes F1's rank-1 frequency argument matter.

### The 78-second landing window

78 samples over 77.3 s: countdown text ticked **6일 22:02:23 → 6일 22:01:06** (77 real seconds, so
liveness is proven), and its rect held **one distinct value** — `x 861, w 290, h 35` — for all 78. Board
row count 15, document height 2154, header width 1022, header text, and the `.more` row were each a
single distinct value. **CLS 0, zero layout-shift entries.** The 60 s refresh fired against an unchanged
`as_of` and, per `Board.tsx`'s explicit contract (「기준시각 unchanged → … Not even a flicker」), correctly
did nothing.

### The resize sweep — 12 widths, all clean

```
w     stars vis  launcher menuBtn links doc   cls  ovfX
390   240   160  False    yes     1     2822  0    0
479   240   160  False    yes     1     2756  0    0
481   240   240  False    yes     4     2656  0    0
767   240   240  False    yes     4     2540  0    0
769   240   240  True     yes     4     2246  0    0
1440  240   240  True     yes     4     2154  0    0
```

**Zero horizontal overflow at every one of the 12 widths**, CLS 0 at each, and both boundaries (480 for
the star cull and the chrome sheet, 768 for the launcher) behave exactly as their CSS and JS say.

### The hover sweep — 87 controls, one effect

Across `/` (48 controls), `/stocks/00547510` (17) and `/portfolio` (22), exactly **one** hover changes
geometry: `Launcher__mark` at `d = [-5.6, -5.6, +11.2, +11.2]`, i.e. `scale(1.35)` on a 32 px mark. It is
composited, moves nothing else, and is Q4. Every other control's hover is colour and border only.

## 4. Dead ends and things that surprised me

- **The first full sweep was worthless and looked perfect.** Ten routes, `lateIns: []` on every one. The
  MutationObserver had never attached (§1.2). Had I trusted it, F1, F2, F3, F4 and F6 — the whole of Family A —
  would have been reported as "no late inserts anywhere".
- **The 40 px control appeared to fail.** It reported one moved element (`#doc`) while the LS observer
  simultaneously reported a 0.03125 shift of the site frame. Two instruments disagreeing is what exposed
  the sibling-renaming key bug; had only one been running, either answer would have been believed.
- **H9 was the plan's highest-confidence item and is simply false.** `.tabActive { font-weight: 600 }` with
  no ghost twin *is* the fragile pattern the plan describes — but Noto Sans KR's Hangul glyphs carry one
  advance width at every weight (the same fact `app/shell.css`'s own P4.F5 comment records), so a Korean
  label cannot re-flow on bolding. The Latin control (+2.98 px) proves the pattern *would* break the moment
  a tab label contained Latin. Worth knowing; not worth a slice.
- **H4's reproduction attempt failed and I left it failed.** `html::-webkit-scrollbar { width: 15px }` does
  not make the root scrollbar take layout space while macOS is using overlay scrollbars, so the probe could
  only ever return 0. Per the plan's own rule, that 0 is not evidence, and F14 is filed as latent with Q5
  rather than as a refutation or a verified defect.
- **H28 needed the instrument taken out of the loop.** `keyboard.press(' ')` and `press('Space')` both left
  `aria-expanded="false"`; `Enter` opened the menu. A hand-built CDP `Input.dispatchKeyEvent`
  `rawKeyDown` / `char` / `keyUp` triple for Space **did** open it. The native `<button>` is fine;
  `P12.S1`'s oddity was Aside.
- **H10 looked like a clean 78-second null and was really "the data never moved".** Reading `Board.tsx`
  rather than the screen showed the `as_of` guard. Forcing a changed payload turned a null into F11.
- **My first `/ask` turn drove the wrong widget.** `[...querySelectorAll('button')].find(/보내기/)` matched
  the hidden 의견 보내기 sheet action first and opened the feedback dialog; the "three widths" I recorded
  were the feedback dialog's. Inspecting the DOM first (`.send` / `.input`, no `Composer-module` on the
  page at all) got the real numbers. **Locate by a stable key, never by the first regex match** — the P7
  rule again, in a new costume.

## 5. What the numbers mean for `P12.DECOMP2`

The ranked F1–F14 with reproductions, proposed fixes, risks and root causes are in
`works/phases/active/P12/phase.md` under `## Notes for later slices`, tagged
`**(from P12.R1, for P12.DECOMP2)**`; the four root-cause families and the method facts the next slices
must rely on are in that file's `## Decisions`; the five operator questions are in
`## Operator Questions`. They are not restated here.

The one-line version: **cut by cause, not by page.** Family B (F8, F9, F10, F12) is a single slice
applying a ghost-width technique this repo already owns and has already used once in this very phase.
Family A (F2, F3, F4, F6) shares a cause but not a remedy and is probably two or three. F5 and F1 are
blocked on Q2 and Q1. F13 and F14 are legitimate "no slice" candidates.

## 6. Hygiene

Throwaway account created through the product and deleted through the product's own 계정 삭제. The 3014
server was stopped (`pid 4500`, killed; port free). The dev stack is exactly as found —
`api pid 60158`, `web pid 61423`, both unchanged from the values `P12.S1` recorded. `NEXT_PUBLIC_VOCKY_SRC`
was never set. Production was opened only for read-only cold-cache loads of public routes: no signup, no
sign-in, no writes. Every probe file lives in the session scratchpad outside the repo; every patched
`window.fetch` died with its tab. `git diff --stat -- frontend/` is empty.
