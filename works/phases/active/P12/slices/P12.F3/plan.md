# P12.F3 — `/portfolio`'s two late bands: 계정 이전 carry-over and 전환 제안 offer (R1 F2, F6)

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.F2` (`82d6c07`). Closes the hunt's rank-2 finding (the worst shift measured) and
rank-6. **Family A** — client-only truth rendered in a mount effect.

## Read first

- `phase.md`: `## Decisions` (families, instrument seam, build recipe, the F1/F2 mechanism lines),
  the shared bar `**(from P12.DECOMP2, for P12.F1 … P12.F9)**` (keep it), and **F1's
  measurement-seams note** — a `git stash` sweep against `next dev` is not a control (build HEAD
  as a second production build on another port), and **browser storage is port-scoped**: seed
  `mijual.portfolio.sample` on the port you measure or the band never renders and the "before"
  is a false clean.
- `slices/P12.R1/result.md` § F2 and § F6 — the "before": F2 signed-in `/portfolio` with a sample
  in `localStorage`: `div.Portfolio-module__carry` inserted at `[184, 76, 912, 195.28]` at
  t = 220 ms (FCP 148), **CLS 0.06097**, 보유 종목 panel y 76 → 291.28, everything **+215.28 px**.
  F6 anonymous `/portfolio` (sample mode): `div.Auth-module__offer` `[184, 1142.83, 912, 110]` at
  1280 / `[16, 1815.8, 380, 106]` at 390, document +130 / +126 px, inserted +53 ms (dev), +7 ms
  (production build), **t = 2981 ms vs FCP 772 ms on the cold throttled mobile profile**.
- The code: `app/portfolio/page.tsx` (server: `?sample=1` → sample; `getPortfolio` 401 → sample;
  else account — **the server already knows anonymous-vs-account and both served payloads**),
  `components/portfolio/Portfolio.tsx` (`useSample()` → `hasSample` → effect `getSamplePortfolio()`
  → `sampleForCarry` → `useCarryOffer` at ~L420, which also fetches a `getStock` name per
  candidate → `<CarryOver>` at the **top** of `.surface`; `ConversionOffer ready={…} lead={false}`
  after 지나간 마감 in sample mode), `components/portfolio/CarryOver.tsx`, `Portfolio.module.css`
  (`.carry` grid: padding 14px / `--space-4`, `.carryLabel`, `.carryList` rows, `.carryActions`),
  `components/auth/ConversionOffer.tsx` (`eligible` ← effect: `ready` && `useAuthState()` says
  anonymous && `markSeen()` on `sessionStorage["mijual.convert.offer"]`; `dismissed` local state),
  `Auth.module.css` (`.offer`), `lib/sample.ts` (`readSample` from `localStorage["mijual.portfolio.sample"]`
  — removals, share overrides, claims; `useSample` = `useSyncExternalStore(…, readSample, () => null)`),
  `lib/session.ts`, and `app/layout.tsx` (`<html suppressHydrationWarning>` — P11.F3, covers
  `<html>`'s own attributes only).

## One constraint that rules out DECOMP2's "cookie mirror" option

`docs/current/security.md` line 188: **"Anonymous state never reaches the server, and that is now
structural: there is no anonymous write endpoint at all."** — 조회 holdings in `sessionStorage`, the
sample's edits in `localStorage`, the offer-declined flags in `sessionStorage`; migration is
"offered, never automatic". A cookie mirroring any of that would send it to the server on every
request. **Do not.** The server may use only what it already knows: the session, the 401, the
served payloads. Everything the browser alone knows stays in the browser — and is read **before
first paint** by the browser itself.

## The mechanism: a pre-hydration mirror of the browser's own facts, reserved space, and an
## SSR-consistent first client render

Three parts, one idea — the same shape `P12.F2` used for the launcher (CSS before hydration, React
after), extended with the browser's storage:

1. **A tiny inline `<script>`, parser-blocking, that runs before the affected content paints** and
   stamps what it learns onto `<html>` as `data-mj-*` attributes (`<html>` is the one element whose
   attribute mismatches are already suppressed — P11.F3 — so React never complains). It reads only
   named keys, in `try/catch`, writes nothing, sends nothing, loads nothing (the edge CSP is
   `upgrade-insecure-requests` only, so inline is allowed; no third-party origin, which is a
   measured property of this product). Design it as a **shared seam** — one small module (e.g.
   `components/chrome/PreHydration.tsx` rendered from the root layout's `<head>`, or a page-level
   inline script where the computation needs server-rendered data attributes beside it — see the
   carry band below) with a documented attribute contract, because `P12.F4` (the lookup holding
   cells from `mijual.lookup.holdings`) and `P12.F5` (the `mijual.auth.flash` logout line) will
   reuse it. Record the contract in `## Decisions`.
2. **CSS reserves the exact box from those attributes** before React runs, in the state where the
   band will exist, and reserves **nothing** otherwise — the resting layout with no band stays
   pixel-identical (`AE = 0`).
3. **React's first client render matches the server markup** (no hydration mismatch), and the
   effect that today *inserts* the band now only *fills or removes* an already-sized element —
   removal of a `display: none` element moves nothing.

Applied to the two bands:

- **R1 F6, the 전환 제안 offer in sample mode (anonymous).** The server knows everything but the
  once-per-session flag: it rendered sample mode from a 401 / no cookie (anonymous), and `ready`
  is `holdings.length > 0` on the served sample. So `page.tsx` passes that knowledge down (an
  `initialAnonymous` / `initialEligible` prop on `ConversionOffer`, the `DeadlineOffer`
  `initialAuthenticated` shape from P4.F10 — it switches the `useAuthState` probe off) and the
  band is **in the server HTML**. The seen flag: the pre-hydration script stamps
  `data-mj-offer-seen` when `sessionStorage["mijual.convert.offer"]` is set, CSS hides the band
  under it, the first client render still renders it (matching the server), and the existing
  effect then calls `markSeen()` — `false` (already seen) → unmount, `true` → keep, exactly the
  once-per-session semantics, with the flag written at the same moment as today. 닫기 unchanged.
  `/stocks`'s `lead` variant keeps its current behaviour (no prop passed → probe as before); do
  not widen this slice to it.
- **R1 F2, the 계정 이전 carry-over in account mode (signed in, browser holds a sample).** The
  server knows the account's holdings (`heldCorpCodes`) and can fetch today's served sample
  composition (anonymous, cheap — it already does client-side); it does **not** know whether this
  browser holds a sample, which rows it removed, or the `MIGRATE_FLAG` dismissal. So: the server
  renders an always-present, zero-height **slot** at the band's position in account mode carrying
  the served sample's `corp_code`s and the held codes as data attributes; an inline script placed
  right after it (parser-blocking, before the holdings below are parsed) reads
  `localStorage["mijual.portfolio.sample"]` and the dismissal flag, computes the candidate row
  count (served − removed − held; 0 if no sample or dismissed), and stamps it on `<html>`
  (`data-mj-carry-rows="n"`); CSS sizes the slot to the band's exact height for `n` rows (label +
  n rows + actions, from `.carry`'s own numbers — measure it at 1280 and 390 rather than deriving
  it; row text does not wrap). `useCarryOffer` then fills the slot with `<CarryOver>` once the
  names arrive — same element, same height, **no push**. With no sample: attribute absent, slot
  0 px, resting layout identical. If the reserved height and the filled band differ by a pixel,
  fix the number, not the mechanism. Keep the label/rows/actions markup and `CarryOver.tsx`'s
  copy untouched.
  - If, while building, the slot-plus-script placement proves unable to beat first paint in the
    production build (measure it — the probe decides), fall back to stamping the raw facts from
    the head script and reserving from CSS alone, and say so; a residual smaller than today's
    215 px is progress, but the target is zero.
- The `session` variant of the carry-over (an empty account portfolio + 조회 holdings in
  `sessionStorage`) rides on the same slot: the head script can count `mijual.lookup.holdings`
  entries (minus held codes from the slot's attribute) when the served portfolio is empty. Cover
  it if it falls out naturally; otherwise note it for the record — R1 measured only `migrate`.

**RESPECT THE DESIGN.** Both bands render exactly as today once present — same copy, same
geometry, same position (the carry-over at the top of the surface as R5-3/R5-4 sign it; the offer
after 지나간 마감 as R13 signs it). No skeleton, no placeholder text, no reordering.

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`; `npm run build` in a fresh copy (no
  warnings; the inline script is in the HTML).
- **Controls:** a HEAD production build on another port (3015) beside the fixed build (3014), plus
  dev (3010). Storage is port-scoped: on **each** port, load `/portfolio?sample=1`, edit one row
  (remove one, change one count) so `mijual.portfolio.sample` exists there; for F2 create the
  throwaway account through the signup form on that port and sign in; for F6 stay anonymous with
  a fresh session (`sessionStorage` cleared).
- **F2 before/after**, Aside `--account u2`, signed in with a sample, at 1280 and 390, dev + fixed
  build vs HEAD build: the R1 late-insert timeline + layout-shift observer + rect diff on
  `.Portfolio-module__carry` / the 보유 종목 panel / `.Portfolio-module__section`. Pass = the slot's
  height is set before the holdings paint, the band fills it with **0 px** movement of anything
  below (CLS from this source 0), band rect and copy identical to HEAD's band once filled. Then
  with **no** sample in storage: no attribute, no slot height, page `AE = 0` against HEAD. Then
  dismissed (담지 않기, `MIGRATE_FLAG`): reload → no reservation, no band. Then 담기: rows land in
  the account and the band leaves — as today.
- **F6 before/after**, anonymous sample mode, 1280 / 390 / **412×915 cold-cache throttled** (this
  is the load-related one), fixed vs HEAD: the offer band is in the server HTML (`curl` grep),
  present at FCP, document height stable from first paint; second load in the same session (seen
  flag set) → hidden pre-hydration, unmounted after, **no shift either way**; 닫기 works; the
  `/stocks/[corp_code]` offer is unchanged (one load, lead variant, still probe-gated).
- **Hydration:** console capture on every measured load — no hydration warning, no error.
- **Resting-layout proof:** `/portfolio` anonymous (no offer eligible: seen flag set) and signed
  in (no sample) against HEAD — `AE = 0`, with a positive control.
- Hygiene: throwaway account deleted through 계정 삭제; production read-only; 3014/3015 stopped;
  `make stack-status` as found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: two lines — (a) **the pre-hydration mirror seam**: where the script lives, the
  `data-mj-*` attribute contract (name → source key → meaning), the rules (reads named keys only,
  never writes, never sends, `<html>` attributes only, CSS reserves/hides, React's first render
  matches the server, effects reconcile after) and that `security.md`'s "anonymous state never
  reaches the server" still holds; (b) the two bands' mechanism and after-numbers.
- `## Doc impact`: `frontend.md` (the seam + the two bands), `security.md` (one line: the seam
  reads browser storage before hydration and sends nothing — the principle is unchanged).
- `## Notes for later slices`: `**(from P12.F3, for P12.F4)**` and `**(for P12.F5)**` — how to reuse
  the seam (the key each will read, where to add its attribute, the CSS pattern), in a few lines
  each. Do not touch the shared bar or F1's seams note.
- `## Operator Questions`: only if something genuinely needs the operator.
- `## Now` (≤ 15 lines): F3 landed with numbers; `P12.F4` next and reuses the seam; freeze date;
  production on `a74c58a`.

`result.md`, verdict block first, before/after tables for both bands.

## Do not

- send any browser-only state to the server (no cookie, no query param, no header); restyle,
  move or reword either band; add a skeleton; add a test file; commit; run any workflow state
  command; write on production; drive Aside `u0`.
