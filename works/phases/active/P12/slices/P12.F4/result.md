# P12.F4 — result

- **status:** done
- **summary:** `/stocks/[corp_code]`'s holding cells no longer insert after paint: `StockView` renders `P12.F3`'s `<InlineScript>` above the ① panels, which reads `sessionStorage["mijual.lookup.holdings"]` for this page's own `corp_code` and stamps `data-mj-lookup-holding` on `<html>`, and `Lookup.module.css` holds the row's with-holding geometry (measured per server-known cell count and viewport) and hides the prompt until React fills them. Against a HEAD production build the row's **+35 px at 1280 / +111 px at 390**, the foot's **−22.95 / −56**, the **+12.05 / +55** push on everything below and **CLS 0.05548** become **0 px moved and CLS 0**, with the resting and filled states byte-identical to HEAD (`AE = 0`).
- **files_changed:**
  - `/Users/sugang/projects/personal/Mijual/frontend/components/lookup/StockView.tsx`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/lookup/Conversion.tsx`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/lookup/Lookup.module.css`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/chrome/PreHydration.tsx` (header table row only)
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P12/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P12/slices/P12.F4/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — pass
  - `cd frontend && npm run smoke` — pass (22/22)
  - `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build` in a fresh copy — pass, **no warnings**; the inline script is in the served HTML of `/stocks/00547510` (+498 B/page)
  - Aside `--account u2`, anonymous, 1280 + 390, dev (3010) + fixed production build (3014) against a HEAD production build (3015) — pass (tables below)
  - `python3 scripts/workflow.py validate` — pass
- **deviations:** three, all recorded below under *Deviations from the plan* — the script is rendered **above** the row it reserves rather than after it; the desktop rules also **pin the surviving cells' columns** (without that, the fill still slid the 배정비율 cell 217 px sideways: CLS 0.00654); and the reservation is **withheld** from a priced ① foot and from 놓친 돈 rather than guessed at.
- **doc_impact:** `frontend.md`: Surfaces / 조회 — the ① 환산 row's holding cells no longer insert after paint (the pre-hydration seam's second use: `data-mj-lookup-holding` from the page's own `corp_code`, the row's with-holding height reserved per served cell count, the prompt hidden pre-paint) (P12.F4)
- **doc_versions:** none — deferred to a docs phase
- **instrument:** **Aside `aside repl --account u2`** (profile 「claude2」), never `u0`. Every number below was read in that browser; no `aside exec`, no MCP registration, no Chrome-over-CDP fallback.

---

## What changed

Three files carry the fix; a fourth gains a table row.

**`StockView.tsx`** renders `<InlineScript code={holdingReservationCode(corpCode)} />` once per page,
immediately **above** `<RightsSection>`, and releases the stamp in a new effect
(`useEffect(() => { if (ready) clearMirror("lookup-holding"); }, [ready])`). The script mirrors
`readSessionHoldings()`'s validation exactly — one key, JSON or nothing, a positive safe integer
under this page's `corp_code` (through `jsonLiteral`) — and stamps **presence only**. The count is
deliberately not stamped: no rule reads it, and it is the reader's own holding.

**`Conversion.tsx`** (`ConversionChain`) publishes the two facts the **server** already holds:
`data-mj-cells` on `.chain` — how many cells a holding will draw, `1 + (ratio ? 2 : 0) +
(ratio && excessRatio ? 1 : 0)` → 4, 3 or 1 — and `data-mj-foot="steady"` on `.chainwrap` when the
foot's note is the same with and without a holding (i.e. unless a money line is coming, which needs
a confirmed price, a `unit_value` and a 배정비율 at once). Nothing else in the component moved.

**`Lookup.module.css`** turns the stamp into geometry: `min-height` per cell count per viewport,
the desktop column pinning, and `display: none` on the prompt under a `steady` foot. `min-height`
rather than `height` on purpose — a caption that wraps one line further makes the row taller than
the reservation instead of being clipped by it.

**The measured reservation** (dev and the local production build, 툴젠 00547510 at 300주,
cross-checked on 이렘 00116426 — identical to the pixel):

| cells | ≤767 (390) | ≥768 (1280) | how it was measured |
|---|---|---|---|
| 4 (보유 · 배정비율 · 배정 신주 + caption · 초과청약 한도) | **201.25px** | **101.75px** | the real filled row, both runtimes, two stocks |
| 3 (no 초과청약비율) | **155px** | **86.25px** | the same row with the cell its missing factor would not have drawn removed |
| 1 (no 배정비율) | **45.25px** | **66.75px** | the same, reduced to 보유 alone |

Three cells are **shorter** than four at desktop (86.25 vs 101.75) because three cells are wider, so
the 배정 신주 caption wraps less — which is why the count has to be published and the height cannot
be derived from one number.

---

## Before / after

Frame-by-frame rects (a `requestAnimationFrame` sampler installed by
`Page.addScriptToEvaluateOnNewDocument`, distinct states only), a `layout-shift` PerformanceObserver
with sources, and the FCP mark. Every load is a **fresh `page.goto`** after typing 300주 on that
port and navigating away — storage is port-scoped, so it was seeded on each port measured.

### 1280 — HEAD control (3015) vs fixed (3014), 6× CPU

| | HEAD, first frame | HEAD, after fill | fixed, first frame | fixed, after fill |
|---|---|---|---|---|
| `.chain` | y 436.92 h **66.75** | y 436.92 h **101.75** | y 436.92 h **101.75** | y 436.92 h **101.75** |
| `.chainfoot` | y **503.67** h 65 | y **538.67** h 42.05 | y **538.67** h 42.05 | y **538.67** h 42.05 |
| 놓친 돈 `section` | y **631.67** | y **643.72** | y **643.72** | y **643.72** |
| `.rowfoot` | 574 | 586 | — | — |
| document height | **1096** | **1108** | **1108** | **1108** |
| cells in the row | 2 | 4 | 2 | 4 |

**CLS: HEAD 0.05548** (one entry, sources: `section` 632→644, `section` 760→772, `chainfoot`
504→539, `rowfoot` 574→586, `cell`) → **fixed 0**, with **no `layout-shift` entry of any kind**.

### 390 — same pair

| | HEAD, first frame | HEAD, after fill | fixed, first frame | fixed, after fill |
|---|---|---|---|---|
| `.chain` | y 587.63 h **90.25** | y 587.63 h **201.25** | y 587.63 h **201.25** | y 587.63 h **201.25** |
| `.chainfoot` | y **677.88** h 139.23 | y **788.88** h 83.23 | y **788.88** h 83.23 | y **788.88** h 83.23 |
| 놓친 돈 `section` | y **892.11** | y **947.11** | y **947.11** | y **947.11** |
| document height | **1564** | **1619** | **1619** | **1619** |

HEAD's own shift entry reads **0.03298** and the fixed build's **0.00531**; Chrome marked both
`hadRecentInput: true` (see *Instrument seams*, below — this is why the frames table above, not the
CLS number, is the evidence at this viewport). The fixed build's 0.00531 has exactly **one source**:
the 배정비율 cell moving y 588 → 633 **inside** the reserved box, x unchanged — the row's own
content changing, with nothing below it moving. At 1280 the column pinning removes even that.

### The stamp's timing (ms, `<html>` attribute mutation vs FCP)

| run | stamped | FCP | released |
|---|---|---|---|
| dev 1280 | 76.3 | 88 | 109.1 |
| dev 390 | 55.8 | 68 | 88.5 |
| production build 1280 | 41.1 | 56 | 57.7 |
| production build 390 | 34.8 | 52 | 51.6 |
| production build 390, 6× CPU | 68.9 | 104 | 233.1 |

The stamp is always on `<html>` **before first contentful paint** and always released **after** the
commit that fills the row.

---

## Controls — every zero has one

- **Resting, no holding in storage** (fixed vs HEAD, both viewports): no `data-mj-*` on `<html>`
  (`getAttributeNames()` = `["lang","class"]`), identical rects (`.chain` 66.75 / 90.25, `.chainfoot`
  65 / 139.234, prompt at [514.672, 44] / [763.109, 44], document 1096 / 1564), and full-page
  screenshots that are **byte-identical** — `compare -metric AE` **0 (0)** and equal md5 at 1280 and
  390. RESPECT THE DESIGN holds: the no-stamp page is the HEAD page.
- **Filled state vs HEAD's filled state:** rects, cell widths and text identical (cells at x 206 /
  423 / 640 / 857, h 101.75 at 1280; h 45.25 / 44 / 65.75 / 46.25 at 390) and screenshots **AE = 0**
  at both viewports.
- **Second stock, 이렘 00116426** (different 배정비율 digits, different derived values): `.chain`
  101.75 / 201.25, `.chainfoot` 42.047 / 83.234, cell heights identical — the reservation is exact
  on a stock it was not measured on.
- **Typing live** (storage cleared, no stamp): the row is at its untouched no-holding geometry
  before the reader types (66.75 / 65 at 1280, 90.25 / 139.234 at 390) — nothing is reserved ahead
  of a reader who has not typed — and typing 300 fills it to exactly HEAD's filled geometry.
- **Clearing the field after hydration:** ⌘A + Backspace returns the row to 66.75 / 90.25, the foot
  to 65 / 139.234, the prompt to its exact HEAD position and the document to 1096 / 1564 — the
  release is what makes that true, and it is why `clearMirror` is not skipped.
- **The restore chip path** (00547510 seeded, then 00116426 met fresh): identical on both builds —
  strip [211.234, 65, 185, 910], chip [226.234, 36, 634.359, 107.234], `.chain` 66.75, sections and
  document height equal, **no stamp** (the chip's stock has no entry of its own), and **zero**
  layout-shift entries on either build. Its behaviour is untouched, as the plan required.
- **Hydration / console:** `console.error|warn|log|info` and `window.onerror` captured on every
  measured load. Production build: **empty on all four runs**. Dev: only React DevTools' info line
  and `[HMR] connected`, which every dev page prints. No hydration warning anywhere.
- **Cost:** the served `/stocks/[corp_code]` HTML grows **498 B** (32,378 → 32,876), all of it the
  inline script and the two data attributes. Nothing is loaded, written or sent.

---

## Deviations from the plan

1. **The script is rendered above the row it reserves, not after it.** `PreHydration.tsx`'s own
   guidance says "immediately after the element it sizes" — F3's slot needed the page's served
   composition beside it. Here the reservation applies to a row **below** the script, so placing it
   above is the same rule applied: the stamp is on `<html>` before the row is parsed, let alone laid
   out. Measured: stamped 15–35 ms before FCP on every run.
2. **The desktop rules also pin the surviving cells' columns.** Reserving only the height left one
   shift behind at 1280 — the 배정비율 cell is the first of two before the fill and the second of
   four after it, so it slid 217 px sideways (measured, CLS **0.00654**, y unchanged at 437). The
   rules name the columns the row is about to have and put the pre-fill cells in the ones they are
   about to occupy; every selector counts the cells present (`:nth-last-child`), so it stops
   matching the instant React fills the row, one commit before the stamp is dropped — a pinning rule
   that outlived the fill would put 보유 in the second column for a frame. With it, 1280 is 0 with
   no layout-shift entry at all.
3. **Two shapes are deliberately left unreserved rather than guessed at** (the plan's "record the
   residual honestly"): a **priced** ① foot, where the money line replaces nothing and the foot's
   height is a number this product's data cannot produce today (0 of 11 live ① offerings carry a
   confirmed price), and **놓친 돈**, whose own cells and 계산 근거 band move with the holding as
   well. The chain reservation — the dominant mover — still applies on a priced stock; only the
   prompt-hiding rule is withheld there.

## Residuals, measured and named

1. **390, inside the box:** one 0.00531 shift entry, the 배정비율 cell moving between rows of the
   reserved box. Nothing below it moves. Pinning rows at 390 would mean fixing each cell's height,
   which would make the *filled* row differ from HEAD's by a pixel or two on any stock whose cells
   measure differently — a worse trade than the residual.
2. **A very long count at 390:** the 배정 신주 caption takes a second line (cell 65.75 → 81.25, row
   201.25 → 216.75) at e.g. 1,234,567,890주, so the row grows 15.5 px at fill. `min-height` is why it
   grows rather than clips. 300주 and 이렘's 178주 fit; at 1280 the caption is two lines at every
   count measured (300 and 1,234,567,890 both give 101.75).
3. **놓친 돈 on a lapse-bearing stock** (00109310, 1280, fresh load with a holding): the per-holding
   cells fill, the 계산 근거 band inserts and the mmhead prompt leaves, moving the breakdown **up**
   52 px (`bkd` 649→597, `mmcap` 619→567, `section` 888→876, `disc` 834→822) — one entry, **0.01006**,
   **identical on the fixed and HEAD builds**. Same family, different element, outside this slice's
   cut; noted for the review, not silently widened into. Four stocks serve lapse rows today.
4. **A chain that does not exist without a holding** (no 배정비율, no 초과청약비율, no confirmed
   price, no 확정 예정일, and the prompt drawn in 놓친 돈): the whole `.chainwrap` would insert, and
   there is no element to reserve. 0 of 11 live ① offerings; the plan's slot pattern would be the
   remedy if one appears.
5. **A client navigation** into a stock page has no pre-hydration window at all (`InlineScript`
   renders inert by design), so the fill is a normal React render there, exactly as at HEAD.

## Instrument seams worth the next slice's time

Both are now in `phase.md`'s `## Decisions` instrument line.

- **After you type, Chrome marks later `layout-shift` entries `hadRecentInput: true` — across
  navigations.** The HEAD control's real 390 shift (the row growing 111 px, the page 55) came back
  with `hadRecentInput: true` and therefore a **CLS of 0**. A slice that seeds state by typing and
  then trusts a CLS sum will report a clean zero for a shift it can see in the rects. Sample the
  rects frame by frame (`requestAnimationFrame` inside the init script) and treat CLS as corroboration.
- **`Page.addScriptToEvaluateOnNewDocument` accumulates per tab.** Calling it once per loop
  iteration installs the probe again, so observers fire N times and entries are duplicated — the
  values stay right, sums do not. Install once per tab, or divide.

## Hygiene

No account was needed (every measurement anonymous); **production was never touched**; the two
scratch servers on 3014/3015 were stopped and their ports are free; the dev stack is as found (same
api/web pids, `make stack-status` unchanged). Build copies live outside the repo, under the
session scratchpad. No test file was added (phase decision).
