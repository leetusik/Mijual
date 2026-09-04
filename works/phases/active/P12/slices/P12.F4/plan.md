# P12.F4 — `/stocks/[corp_code]` revisit: the holding cells inserted from `sessionStorage` (R1 F3)

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.F3` (`39908ff`). Closes the hunt's rank-3 finding. **Family A**, and the second
user of the pre-hydration mirror seam `P12.F3` built.

## Read first

- `phase.md`: `## Decisions` — **the pre-hydration mirror seam** line (F3, landed: entry points,
  rules, attribute contract, why `<html>`), the instrument seam (**including F3's three additions**:
  end a repl script with `console.log` never `return`; no `page.waitForTimeout`; screenshots
  resolve inside the invocation's session directory, so capture everything a comparison needs in
  one invocation), the build recipe; the shared bar `**(from P12.DECOMP2, for P12.F1 … P12.F9)**`
  (keep it); F1's measurement-seams note (HEAD control build on another port; **storage is
  port-scoped** — type the holding on the port you measure); and **F3's note tagged `for P12.F4`**
  — the placement (`<InlineScript>` right after the slot, the server's `corp_code` through
  `jsonLiteral()`), the CSS pattern (`display: contents` slot; `html[data-mj-…] .slot:empty
  { display: block; height: … }` is the only rule that reserves), "measure the reserved height,
  never derive it", and `clearMirror(…)` no earlier than the commit that fills the slot. Consume
  that note when you finish.
- `components/chrome/PreHydration.tsx` — the seam itself and its header table (add your row).
- `slices/P12.R1/result.md` § F3 — the "before": `/stocks/00547510` with `300` typed earlier in
  the session, fresh load: three `div.Lookup-module__cell` (보유 300주 / 배정 신주 25주 = … / 초과청약
  한도 +5주, each 217 × 101.75 at y 436.92) inserted **+36 ms after FCP in dev, +3 ms on the
  production build**, **CLS 0.04785 in both**; `Lookup__section` y 631.67 → 643.72 (+12.05) and
  `Lookup__chainfoot` y 503.67 → 538.67 (+35) while shrinking 65 → 42.05 tall. The restore chip
  never appears on this path.
- The code: `components/lookup/StockView.tsx` (`digits` starts `""` → `shares = null` on the
  server and the first client render; a mount effect reads `readSessionHoldings()` and either
  `setDigits(String(own))` for this `corp_code` or `setRestore(last.shares)` for a different
  one, then `ready`), `lib/holding.ts` (`SESSION_KEY = "mijual.lookup.holdings"`, the JSON shape
  `{v, entries: {corp_code: shares}, last}`), `components/lookup/Conversion.tsx`
  (`ConversionChain`: with a holding **four** cells — 보유 · 배정비율 · 배정 신주 with its sub
  caption · 초과청약 한도, the last three conditional on `ratio` / `allotted` / `excess`; without one
  **two** — 배정비율 · 초과청약 비율, or fewer; the `.chainfoot` carries the price state left and, only
  while `shares === null`, the R11 §6 `prompt` right), `Lookup.module.css` (`.chainwrap`, `.chain`
  grid, `.cell` min-height 44 / column-gap, `.chainfoot` padding 10px 14px, flex-wrap), and
  `HoldingStrip.tsx` (the input the digits fill).

## The change

The server renders the no-holding state; the browser alone knows `entries[corp_code]`. Two
things move when the holding lands: the chain row grows (two short cells → the four-cell row
whose tallest cell carries the sub caption) and the foot shrinks (the prompt leaves). Reserve
both from the mirror, so the content *changes inside a box that does not move*:

1. **Server-side facts beside the slot.** The server knows this stock's factors — whether
   `ratio`, an allotment and `excess` exist, so how many cells and whether the sub caption will
   render — and the `corp_code`. Render the chain as today, wrapped so an empty/with-holding
   geometry can be selected by CSS, and place `<InlineScript code={…}>` right after it with
   `jsonLiteral(corp_code)` (and the cell/caption facts if the reserved height depends on them).
2. **The script** reads `sessionStorage["mijual.lookup.holdings"]`, and if `entries[corp_code]`
   holds a valid count, stamps `data-mj-lookup-holding` on `<html>` (add the row to the seam's
   header table; consider stamping the count too only if a rule needs it — it should not). No
   stamp for the `last` restore chip (R1: not on this path; leave the chip's behaviour alone).
3. **CSS reserves from the stamp** — under `html[data-mj-lookup-holding]`, the chain row and the
   foot take the with-holding geometry (`min-height`s **measured** on the fixed build at 1280 and
   390 against the HEAD build's filled state: the four-cell row is 101.75 at 1280 with the sub
   caption; at 390 the cells may stack — measure) *until React fills them*, and nothing at all
   otherwise. When React's effect sets `digits`, the four cells replace the two and the prompt
   leaves, inside the already-sized boxes: **0 px movement** of `Lookup__section`, `chainfoot`
   and everything below. The numbers repainting inside a fixed box is a repaint, not motion;
   that is the target. Then `clearMirror("data-mj-lookup-holding")` once the holding is in state
   (no earlier than the commit that renders it).
4. **First client render matches the server** (`digits` still `""` on the hydrating render — do
   not read storage during render); the existing effect is what fills. `writeSessionHolding`,
   the `ready` gate, the restore chip, `HoldingStrip`'s input, and every number's derivation
   (`convert()`, the one multiplication site) are untouched.

If the with-holding geometry cannot be reserved to the pixel because the four-cell row's height
depends on a value only the client knows (it should not — the sub caption exists whenever
`ratio` does, and its text is one line at both viewports; verify), reserve the dominant mover
(the foot: −23 px; the row: +12 px) and record the residual honestly. **RESPECT THE DESIGN:** the
no-holding state stays pixel-identical (`AE = 0` with no stamp); the with-holding state renders
exactly as today once filled; no placeholder text, no skeleton.

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`; `npm run build` in a fresh copy (no
  warnings; the inline script in the served HTML of `/stocks/00547510`).
- **Controls:** HEAD production build on 3015 beside the fixed build on 3014, plus dev 3010; on
  **each** port open `/stocks/00547510` (re-fetch a live `corp_code` with an `offering` from
  `GET http://127.0.0.1:8010/board` if that one aged out), type `300` into 보유 주식 수, navigate
  away (`/`), come back with a **fresh load** (`page.goto`, not back).
- **Before/after**, Aside `--account u2`, anonymous, at **1280 and 390**, dev + fixed vs HEAD: the
  R1 late-insert timeline + layout-shift observer + rect diff on `.Lookup-module__section`,
  `.Lookup-module__chainfoot`, `.Lookup-module__cell`, and the strip. Pass = with the holding in
  storage the stamp is on `<html>` before the chain paints, the row and foot are at their
  filled geometry from the first frame, the four cells fill with **0 px** movement of anything
  below (CLS from this source 0); the filled state's rects and text identical to HEAD's filled
  state. Then **no holding** in storage: no stamp, page `AE = 0` against HEAD at both viewports.
  Then a **different** stock with `last` set: the restore chip behaves exactly as at HEAD (rect
  diff of the strip — it is not this slice's fix; if it moves neighbours, note it for the
  review, do not widen).
- **Typing live:** type a count on a fresh page, watch the chain fill as today (this path was
  never a flicker finding — confirm it did not become one: the boxes must not now reserve space
  *before* the reader types, i.e. no stamp → no reservation).
- **Hydration:** console capture on every measured load — no warning, no error.
- Hygiene: no account needed; production read-only; 3014/3015 stopped; `make stack-status` as
  found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the lookup chain reserves its with-holding geometry from
  `data-mj-lookup-holding` (files, the measured heights per viewport, the after-numbers).
- `## Doc impact`: `frontend.md` — Surfaces / 조회: the holding cells no longer insert after paint
  (the seam's second use; the attribute; the measured reservation) (P12.F4).
- `## Notes for later slices`: remove F3's `for P12.F4` note; add `**(from P12.F4, for P12.F5)**`
  only if you learned something F3's `for P12.F5` note does not already say. Do not touch the
  shared bar, F1's seams note, F3's `for P12.F5` note, or F3's `for P12.REVIEW` note (the
  orchestrator has cut `P12.F10` from it).
- `## Now` (≤ 15 lines): F4 landed with numbers; `P12.F10` is next in order (the edited-sample
  holdings-list shift, cut by the orchestrator at 3.45 from F3's finding), then `P12.F5`; freeze
  date; production on `a74c58a`.

`result.md`, verdict block first, before/after tables at both viewports.

## Do not

- read storage during render, send any browser-only state to the server, add a skeleton or
  placeholder text, change any number's derivation, touch the restore chip's behaviour, add a
  test file, commit, run any workflow state command, write on production, or drive Aside `u0`.
