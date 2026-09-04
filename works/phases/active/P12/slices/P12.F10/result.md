# P12.F10 — result

- **status:** done
- **summary:** The anonymous 보유 종목 surface no longer drops a removed issuer's row after paint. The pre-hydration mirror's **third use**: the `<head>` script stamps `data-mj-sample-removed="<code> …"` from the browser's own sample store, `SampleRules.tsx` emits one static rule per **served** code (plus one per D-day section, and a `border-top` rule for the first visible row), every removable row carries `data-corp`, and `Portfolio` releases the stamp once `useSample()` has answered. Against a HEAD production build: **CLS 0.05206 → 0** at 1280 (doc 1324 → 1208 becomes 1208 from the first frame), **0.11225 → 0** at 390, **0.16078 → 0** when a whole D-day section empties, and **0.19581 → 0.00064** (font swap only) on the cold throttled 412×915 profile where the row used to drop **2.0 s after first paint**. Unedited samples and settled edited pages are **`AE = 0`** against HEAD at both viewports.
- **validation:**
  - `cd frontend && npm run typecheck` — pass
  - `cd frontend && npm run smoke` — pass (22/22)
  - `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build` in a fresh copy outside the repo — pass, **no warnings**; the rule sheet is in the served HTML of `/portfolio` (anonymous), the head stamp in every page's `<head>`
  - Aside `--account u2`, anonymous, 1280 + 390 + the cold 412×915 profile, dev (3010) + fixed production build (3014) against a HEAD production build (3015) — pass (tables below)
  - one signed-in dev load through a throwaway account created **and deleted** through the product — F3's 계정 이전 slot unchanged (CLS 0)
  - `python3 scripts/workflow.py validate` — pass
- **deviations:** five, all recorded below (§ Deviations) — the biggest is **two rule shapes the plan did not name**, added because the measurements demanded them.
- **doc_impact:** `frontend.md` — Surfaces / 보유 종목 sample mode: the seam's third use (attribute, per-served-code rules, section rules, `data-corp` hooks, the release).

---

## What landed

| file | change |
|---|---|
| `frontend/components/chrome/PreHydration.tsx` | `HEAD_SOURCE` reads `localStorage["mijual.portfolio.sample"]` and stamps `data-mj-sample-removed` (space-separated **digit strings only**); `SAMPLE_REMOVED_ATTR` exported so the two sides of the seam cannot drift; new row in the attribute table |
| `frontend/components/portfolio/SampleRules.tsx` **(new)** | a server component that turns **this render's served composition** into the rules that hide what the browser removed |
| `frontend/app/portfolio/page.tsx` | renders `<SampleRemovedRules payload={…} />` above `<Portfolio>` in both sample branches (the parser meets the rules before the rows) |
| `frontend/components/portfolio/Holdings.tsx` | `data-corp={row.corp_code}` on `li.holdingRow` |
| `frontend/components/portfolio/Deadlines.tsx` | `data-corp` on each D-day row; `data-corp-group` on the block and on each section |
| `frontend/components/portfolio/Portfolio.tsx` | `clearMirror("sample-removed")` in an effect gated on `mode === "sample" && sample !== null` |
| `frontend/components/portfolio/index.ts` | exports `SampleRemovedRules` |

**The three rule shapes** (all generated from the composition the server just rendered, codes validated as digit strings before they enter a selector):

1. `html[data-mj-sample-removed~="c"] [data-corp="c"]{display:none}` — one per served code. `~=` matching one word of the attribute is what lets a *static* rule serve a list the server may never be told.
2. `html[…every code of the section…] [data-corp-group="upcoming|past|deadlines"]{display:none}` — because `Deadlines` and `Section` **unmount** when all their rows go, title and panel with them. Not in the plan; see § Deviations.
3. `html[…everything before me…]:not([…me…]) [data-corp-group="g"] [data-corp="c"]{border-top:0}` — `.row:first-child` drops its border and `:first-child` counts a `display: none` element, so without this the first *visible* row keeps a 1 px hairline the settled page does not have.

---

## Before / after — 1280, production builds (HEAD 3015 vs fixed 3014)

Store, written by the product's own 삭제 and 수정·저장 controls: `{"v":2,"shares":{"00162461":740},"removed":["00102618"],"claims":[]}` — F3's finding plus a count override. Served composition (stable all day): holdings `00102618 00109310 00162461 00133618`, upcoming `00109310`, past `00102618 00162461 00109310 00133618`.

| | HEAD (3015) | fixed (3014) |
|---|---|---|
| document, first frame → settled | **1324 → 1208** (−116) | **1208 → 1208** |
| CLS | **0.05206** (one entry, 5 sources, vertical) | **0.00005** — one entry, horizontal, the mono font swap (HEAD's own run shows 0.00039 of the same) |
| removed issuer's two rows, first frame | painted (910×62.8 holdings, 910×52 past) then gone | **0 × 0 from the first frame**, unmounted at t≈184 ms |
| every remaining row, first frame → settled | moves up 62.8–116 px | **identical rect** (holdings `[185,173.09,910,64]`, `[185,237.09,910,62.8]`, `[185,299.89,910,62.8]`; past `[185,601.25,910,164.05]`, `[185,765.3,910,165.05]`, `[185,930.34,910,75.64]`) |
| removal **only** (no count override) | — | doc **1208 → 1208**, CLS **0**, zero moved rects |

`0.05206` and `document 1208 px` are exactly the numbers `P12.F3`'s note recorded, reproduced as the control.

## Before / after — 390

| | HEAD | fixed |
|---|---|---|
| document | **2131 → 1926** (−205) | removal only: **1894 → 1894**; with the count override: 1894 → 1926 (**+31.92**, and see the residual) |
| CLS | **0.11225** (vertical) | **0** |
| rows | all move up | identical, removed rows 0 × 0 from the first frame |

## A whole D-day section emptied — 1280 (`removed: ["00109310"]`, the only 다가오는 마감 row)

| HEAD | fixed |
|---|---|
| doc **1324 → 940** (−384 px), **CLS 0.16078** | doc **940 → 940**, **CLS 0** — section, eyebrow and panel have no box from the first frame |

This is the worst shift on the surface and the plan did not name it; rule shape 2 is why it is zero.

## Cold, throttled — 412 × 915 @ DPR 2.625, 4× CPU, ≈1.6 Mbps / 150 ms (`removed: ["00102618"]`)

| HEAD | fixed |
|---|---|
| FCP 692 ms; doc **2131 until t = 2,608 ms** (≈**2.0 s after first paint**), then 1894 — **CLS 0.19581** | FCP 736 ms; doc **1894 from the first sampled frame (t = 700 ms)** — **CLS 0.00064**, entirely the horizontal mono swap (HEAD's own 0.0005) |

## dev (3010, StrictMode)

| viewport | result |
|---|---|
| 1280, edited | doc **1208 → 1208**, CLS 5e-05 (font swap), every remaining rect identical, stamp released |
| 390, removal only | doc **1894 → 1894**, CLS **0** |
| 390, edited | 1894 → 1926 (the override wrap only) |

The P7 rule holds again: dev and the production build differ in speed, not behaviour.

## Resting states — RESPECT THE DESIGN

- **Unedited sample** (`{"v":2,"shares":{},"removed":[],"claims":[]}`): **no stamp**, no rule matches, doc **1324** (1280) and **2131** (390) on *both* builds in every frame, CLS 0, and full-page screenshots **`AE = 0`** against HEAD at both viewports.
- **Settled edited page**: full-page screenshots **`AE = 0`** against HEAD at both viewports — the fixed build renders exactly what HEAD renders once HEAD stops moving.
- **Console: nothing.** `logs: []` in all 14 measured loads (the probe hooks `console.{error,warn,log,info}` and `window.onerror` before the document exists) — no hydration warning, no error, in dev or production.

## The release (`clearMirror`)

One tab, 3014, 1280, loaded with `removed: ["00102618"]`:

| step | observation |
|---|---|
| after load | stamp **released** (`null`); the two hidden rows unmounted; doc 1208 |
| store rewritten to `removed: []` + the module's own `mijual:sample` event | both rows come back with **real boxes** (910×63, 910×52), doc **1208 → 1324**. Had the stamp still stood, CSS would have kept them at zero — this is the proof |
| product 삭제 on 세기상사 → **되돌리기** | row goes (doc 1238), comes back (doc 1324), store back to `removed: []` — the 8초 undo is untouched |

## Neighbouring seam uses, re-checked

- **전환 제안 (F3, anonymous):** fixed — band at `[184,1027,912,110]` in the **first and only** state, doc 1338 stable; HEAD — present at first paint too but riding the row drop (`y 1143 → 1027`). 세션당 1회 still written at the same moment (`SEENFLAG 1` on both).
- **계정 이전 (F3, signed in):** a throwaway account created through 계정 만들기 in dev, browser holding the edited sample → the band offers 3 rows (계양전기 correctly absent), fills the reserved slot with **doc 900 stable and CLS 0**, and the account was then deleted through 계정 삭제 (redirect to `/`, chrome back to 로그인).
- **조회 (F4):** `/stocks/00109310` on the fixed build — one state, CLS 0, no console output. The new stamp sits on `<html>` there and matches nothing, because the rules are only ever rendered by the sample surface.

## Cost

- head script **171 → 455 B** per page (**+284 B** of source; **+612 B** per served document, since the flight payload carries the same string) — site-wide, because the sample store is page-independent (the plan's choice, and the seam's rule).
- `/portfolio` in sample mode: **+3,668 B** — the ~1.4 kB rule sheet (twice: DOM + flight payload) plus `data-corp` on 9 rows and `data-corp-group` on 3 containers.

---

## Deviations

1. **The rules are a small server component** (`components/portfolio/SampleRules.tsx`) rendered by `page.tsx` above `<Portfolio>`, not code inside `page.tsx` — the plan's own second option, chosen so the generator stays out of the client bundle and can be read beside the seam it serves.
2. **Two rule shapes the plan did not name** (container, first-visible-border). Both were forced by measurement, not preference: a section whose every row is removed is *unmounted*, and hiding only its rows left a **−384 px / CLS 0.16078** collapse at HEAD — a worse shift than the one this slice was cut for; and `.row:first-child` counts a `display: none` element, so the top visible row kept a 1 px hairline. Neither adds an attribute or changes any resting pixel (`AE = 0` stands).
3. **The stamped list is not de-duplicated** — `removeSampleHolding` already writes through a `Set` and `~=` is indifferent to a repeated word, so the loop the plan implied became a `filter` and the head script got ~130 B shorter.
4. **The count override is not stamped**, exactly as instructed — but the plan's premise for that ("counts change text, not geometry") is **false at ≤767**: see the residual below. The finding is recorded, not acted on.
5. **Seeding.** The edited store was created on each of 3010/3014/3015 through the product's own 삭제 and 수정 → 저장 controls (CDP mouse and key events), which produced `{"v":2,"shares":{"00162461":740},"removed":["00102618"],"claims":[]}` on all three. Later repeat loads wrote that same JSON directly rather than re-clicking; storage is port-scoped (F1's note), so each port carries its own.

## Residuals, measured and left alone

1. **A count override re-wraps a past ① row at ≤767 — pre-existing and identical on both builds.** With `shares: {"00162461": 740}` and *no* removal, the 한화솔루션 past row grows **255.69 → 288.61 px** after hydration (the 소멸 금액 line takes one more line at 390) and everything below it moves down 31.92 px; doc **2131 → 2163 on HEAD and on the fixed build alike**, 59 identical changed keys. At 1280 the same override moves nothing. It is the same family as this slice but a different fact — a *height* the server cannot derive, because it depends on how the reader's own number wraps — so widening the stamp to `shares` would mean reserving a text-dependent height. Recorded for routing (note in `phase.md`).
2. **Every issuer removed** — the holdings list swaps for the 「없습니다」 empty panel, which is a different element, not a hidden one: the panel grows **33.5 → 106.44 px** at t≈90 ms (no `layout-shift` entry; nothing below it moves at that page height). HEAD in the same state collapses **1324 → 900, CLS 0.02686**. Hiding the list would trade one shift for another and rendering both panels is precisely the hydration mismatch the seam exists to avoid, so it is documented in `SampleRules.tsx` rather than fixed.
3. **The mono font swap** shows up as 0.00005–0.00064 of horizontal CLS on *both* builds in any load whose first sampled frame precedes the swap — R1 F5, `P12.F9`'s slice.

## Instrument

**Aside `aside repl --account u2`** (profile 「claude2」), never `u0`. CDP through `page._sendToTarget`; the probe installed with `Page.addScriptToEvaluateOnNewDocument` before `goto`, its `MutationObserver` on `document`; rects sampled every `requestAnimationFrame`, distinct states only; CLS read as corroboration, never as the evidence. Two additions to the seam, both in `phase.md`:

- the repl's globals include node-ish `fs`/`pwd` **scoped to the invocation's own session directory**, so a probe file cannot be read from the repo — the script is generated with the probe inlined as a JSON literal and passed as `aside repl --account u2 "$CODE"` from a shell **variable** (a literal `"$(cat …)"` would let the shell eat the backslashes in it);
- `page` carries `click`/`fill`/`getByRole`/`console` beside `evaluate`, and `Input.dispatchMouseEvent` + `Input.insertText` over CDP drive the product's own controls faithfully (this is how the sample was edited, and how the throwaway account was created and deleted).
- **A rect key must ignore `display: none` elements**, not just insertions: a hidden row still walks the DOM, so counting it into the occurrence index renames every later sibling the moment React unmounts it, and a clean run reads as 123 changed keys. Index over *visible* elements only, and carry the hidden ones as a separate list.

## Hygiene

Production untouched and unvisited. Signed-in work in dev only, through a throwaway account created and deleted through the product. Scratch servers 3014/3015 stopped (ports free); the fresh build copies live outside the repo. The dev profile's sample store restored to unedited (`{"v":2,"shares":{},"removed":[],"claims":[]}`) and its sessionStorage cleared. `make stack-status` as found (postgres up, api 8010, web 3010). No test file added.
