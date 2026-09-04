# P12.F10 — anonymous 보유 종목 with an edited sample: a removed row drops after paint (from P12.F3's finding)

`kind: fix`, `risk: high` → `slice-executor-high`. Cut by the orchestrator at order 3.45 from the
finding `P12.F3` recorded (its note tagged `for P12.REVIEW`), written 2026-09-04 after `P12.F4`
(`7b09efc`). **Family A**, the pre-hydration mirror seam's third use.

## Read first

- `phase.md`: `## Decisions` — the seam line (F3), F4's line (the second use: server-published
  facts + a presence stamp + measured CSS), the instrument seam with F3's three additions, the
  build recipe; the shared bar (keep it); F1's measurement-seams note (**storage is
  port-scoped**); **F3's note tagged `for P12.REVIEW`** about this very shift — consume it (this
  slice is its route); and F4's note tagged `for P12.F5` (placement: where the parser meets the
  script before the thing it reserves) — read, do not consume.
- `slices/P12.F3/result.md` § "An edited sample still shifts the anonymous surface at hydration"
  — the "before": dev, anonymous, 1280, `localStorage["mijual.portfolio.sample"]` with
  `removed: ["00102618"]` → the server renders 4 rows, the client drops to 3 **at hydration**,
  **CLS 0.05206**, document 1208 px.
- `components/chrome/PreHydration.tsx` (the seam: `HEAD_SOURCE`, `<PreHydrationMirror>`,
  `<InlineScript>`, `jsonLiteral`, `clearMirror`, the header table — add your row).
- The code: `components/portfolio/Portfolio.tsx` ~L100–150 — `useSample()` is
  `useSyncExternalStore(subscribe, readSample, () => null)`, so the hydrating render has
  `local = null` (every served row) and the first post-hydration render applies `shown()` /
  `sharesFor()`: **three lists** filter on `shown` — `holdings`, `upcoming`, `past` — and the
  share override changes text only; `components/portfolio/Holdings.tsx` (`li.holdingRow` keyed by
  `corp_code`, the head row `aria-hidden`), the components that render `upcoming` / `past`
  (`Portfolio.tsx` ~L450 — find them), `Portfolio.module.css`, `lib/sample.ts` (`readSample`:
  `removed`, share overrides, `claims`; `restoreSampleHolding` puts a row back), and
  `app/portfolio/page.tsx` (the server knows every served `corp_code`).

## The change

The server renders every served row; the browser alone knows which issuers it removed. Hide the
removed rows **before first paint** by CSS driven from the mirror, so hydration (all rows, matching
the server) paints nothing extra and the post-hydration unmount removes an element that already
had no box:

1. **The stamp — head half.** `mijual.portfolio.sample` is page-independent, so add its
   `removed` list to `HEAD_SOURCE`: stamp `data-mj-sample-removed="<code> <code> …"`
   (space-separated `corp_code`s, validated as digit strings, empty → no attribute). Add the row
   to the seam's header table. Nothing else from the sample state is stamped (counts change text,
   not geometry — verify that below; `claims` are not rendered as rows).
2. **The rows — a stable hook.** Every rendered sample row that `shown()` can drop — in
   `Holdings`, and in whatever renders `upcoming` and `past` — carries `data-corp={corp_code}`
   (markup only, no visual change). Do this for `mode === "sample"` at least; harmless in account
   mode.
3. **The rules — server-generated, per served code.** The server knows the served composition,
   so `page.tsx` (or a tiny server component beside `Portfolio`) renders a `<style>` with one
   rule per served `corp_code` `c`:
   `html[data-mj-sample-removed~="c"] [data-corp="c"] { display: none; }` — the `~=`
   space-separated attribute match is what makes a static rule per code work. A handful of
   rules, in the served HTML, before the list. (If you prefer the seam's page-level
   `<InlineScript>` to emit the rules, it must still be CSS, never DOM edits to the rows — a
   row attribute set by script would mismatch at hydration on an element P11.F3 does not
   suppress.)
4. **Release.** `clearMirror("data-mj-sample-removed")` once React's own `local` state has
   taken over the lists (no earlier than the commit after `useSample()` returns non-null),
   otherwise a later 되돌리기 (`restoreSampleHolding`) would bring a row back into state that CSS
   still hides.
5. **Share overrides:** confirm a changed count re-renders the row's number (and the 환산액 /
   D-day text it drives) **without** changing any row's height; if a wider numeral changes a
   width, that is text within a fixed row (F9's font territory) — note it, do not widen.

**RESPECT THE DESIGN:** an unedited sample renders pixel-identically (no stamp, no rule
matches); an edited one renders exactly what it renders today after hydration — just from the
first frame. No placeholder, no reordering, no copy change.

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`; `npm run build` in a fresh copy (no
  warnings; the `<style>` rules in the served HTML of `/portfolio` anonymous).
- **Controls:** HEAD production build on 3015 beside the fixed build 3014, plus dev 3010; on
  **each** port, anonymous: load `/portfolio`, remove one issuer (the product's own control) and
  change one count, so `mijual.portfolio.sample` carries `removed` + an override there.
- **Before/after**, Aside `--account u2`, anonymous, **1280 and 390**, dev + fixed vs HEAD: the R1
  probe (late insert/removal timeline, layout-shift observer with sources, rect diff keyed by
  `data-corp` on the holdings rows, the upcoming/past rows, and every section below). Pass =
  the removed issuer's row(s) never paint (no box from the first frame), CLS from this source
  **0**, remaining rows' rects identical from first frame to settled; HEAD shows the drop
  (CLS ≈ 0.052 at 1280 — reproduce it as the control). Then **unedited sample**: no stamp, full
  page `AE = 0` vs HEAD at both viewports. Then **되돌리기** on the removed issuer: the row comes
  back after hydration exactly as at HEAD (the `clearMirror` proof). Then the count override
  alone: no shift, text updated. Also confirm F3's carry-over slot and offer band still behave
  (one signed-in load with a sample, one anonymous cold load) — same seam, no interference.
- **Hydration:** console capture on every measured load — no warning, no error.
- Hygiene: a throwaway account only if you exercise the signed-in check (create + delete through
  the product); production read-only; 3014/3015 stopped; the dev profile's sample restored to
  unedited; `make stack-status` as found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the edited sample's removed rows are hidden pre-paint by
  server-generated per-code rules under `data-mj-sample-removed` (files, the release point, the
  after-numbers).
- `## Doc impact`: `frontend.md` — Surfaces / 보유 종목 sample mode: the seam's third use (the
  attribute, the per-served-code rules, `data-corp` hooks, the release) (P12.F10).
- `## Notes for later slices`: consume F3's `for P12.REVIEW` note (this slice is its route). Do
  not touch the shared bar, F1's seams note, F3's/F4's `for P12.F5` notes, or F4's
  `for P12.REVIEW` note (놓친 돈 rows — the review routes that one).
- `## Now` (≤ 15 lines): F10 landed with numbers; `P12.F5` next (the logout flash — the head half
  of the seam, F3's and F4's notes); freeze date; production on `a74c58a`.

`result.md`, verdict block first, before/after tables at both viewports.

## Do not

- set attributes on row elements from script, read storage during render, send any browser-only
  state to the server, reorder or restyle rows, add a test file, commit, run any workflow state
  command, write on production, or drive Aside `u0`.
