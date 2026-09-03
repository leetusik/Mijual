# P12.F2 — Chrome first paint II: the AI 질문 launcher in the first paint (R1 F1, launcher half)

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.F1` (`4730c41`). Closes the launcher half of the hunt's rank-1 finding.

## Read first

- `phase.md`: `## Decisions` — **Ruling 2** (this slice's mechanism), the instrument seam, the
  build recipe; the shared bar `**(from P12.DECOMP2, for P12.F1 … P12.F9)**` (keep it); the two
  `P12.F1` notes tagged for you — the seam you may reuse (you will not need a server value here)
  and, more importantly, the **two measurement seams**: take "before" numbers from a **second
  production build from HEAD on another port**, never from a `git stash` sweep against `next dev`.
  Consume the `for P12.F2` note; leave the `for P12.F2 … P12.F9` one for the others.
- `slices/P12.R1/result.md` § F1 — the "before": `button.Launcher-module__launcher` (68×50 at
  [1188, 726]) inserted **+44 to +288 ms after FCP** in dev and **+3 to +165 ms** on the production
  build, on the 9 non-`/ask` routes at ≥768; nothing at 390 (not rendered). CLS 0 — a pop-in.
- The code: `components/ask/AskSurface.tsx` (`if (!desktop) return null;` then the launcher, and
  the widget only when `state.open`), `components/ask/useAsk.ts` (`useDesktop()`: `useState(false)`
  + a `matchMedia("(min-width: 768px)")` effect; its header comment explains the "server-rendered
  as `false`" choice as a flash guard), `components/ask/AskLauncher.tsx` (DOM only),
  `components/ask/Launcher.module.css` (`.launcher { position: fixed; … }`, no media query today),
  and **`components/ask/QuestionStrip.tsx`**, which also calls `useDesktop()` — only inside its
  `press` handler (desktop → `store.open()`, else `router.push("/ask")`), never in render.

## The change

The signed rule is 「≤767px: nothing — not hidden, not rendered」, argued from tab order and from "a
launcher merely not painted would still open a widget". A `display: none` element is in no tab
order and cannot be activated, so the rule's substance survives a pre-hydration CSS guard, and the
post-hydration state stays exactly what is signed: **not rendered**. Concretely:

1. **`useAsk.ts`** — give `useDesktop` an `initial` parameter: `useDesktop(initial = false)`.
   `QuestionStrip` keeps calling it bare (its handler runs after hydration, and a 390 press
   during the effect window must still route to `/ask`, so its default stays `false`).
   `AskSurface` calls `useDesktop(true)`: the server render and the hydrating client render
   both say `true`, so the launcher is in the HTML and hydration matches; the effect then sets
   the real answer — `false` at ≤767 **unmounts** it (the signed end state), `true` at ≥768 changes
   nothing. Update the hook's header comment: the "would flash a launcher onto a phone" guard is
   now the CSS rule below, for the one caller that opts in.
2. **`Launcher.module.css`** — add `@media (max-width: 767px) { .launcher { display: none; } }`
   with a comment: this is the **pre-hydration** guard only (the component unmounts ≤767 after
   hydration — `AskSurface`), it exists so the server can render the launcher for desktop without
   painting it on a phone for the ~100 ms before React runs, and `display: none` keeps it out of
   the tab order and unactivatable in that window. Nothing else in the file changes — same
   frame, tail, mark, hover, open state.
3. **`AskSurface.tsx`** — `const desktop = useDesktop(true);`; update the header comment's first
   rule to say: ≤767 → not rendered after hydration, and not painted before it (the CSS guard),
   pointing at `P12.F2`. `/ask` and `/ops` rules unchanged. The widget still renders only on
   `state.open` (closed in the server snapshot), so nothing else enters the first paint.

Nothing visual changes: same launcher, same corner, same states, same absence on a phone. **RESPECT
THE DESIGN.** Do not touch `AskLauncher.tsx`'s DOM or any launcher number.

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`.
- **Markup:** `curl -s http://127.0.0.1:3010/` contains `Launcher-module__launcher`; `/ask` does
  not. Same on the fresh local production build (3014).
- **Before/after with the hunt's probe**, Aside `--account u2`, signed out: the R1 late-insert
  timeline on the **9 non-`/ask` routes at 1280** in dev and on the fresh production build — the
  launcher must be present at or before FCP (F1's numbers for the slot are the shape to expect),
  against a **HEAD control build on another port** (F1's seam), never a stash sweep.
- **The phone end state is unchanged:** at **390** and at **767**, after hydration the launcher is
  **absent from the DOM** (`document.querySelector` null), and a full-viewport screenshot taken
  as early as the repl allows after `goto` shows nothing in the bottom-right corner (the CSS
  guard). At **768** it is present. Resize 767 ↔ 768 toggles existence exactly as today. Tab
  through the whole page at 390 — focus never reaches a launcher.
- **Function:** at 1280, the launcher opens the widget, the launcher goes inert/hidden under it,
  the widget closes, focus returns; `QuestionStrip` at 390 (an event page) still routes a chip
  press to `/ask`, and at 1280 opens the widget — unchanged.
- **Resting-layout proof:** paired screenshots of the bottom-right corner at 1280 (rest, hover,
  open) against the HEAD build — `AE = 0`.
- `npm run build` in the copy: no warnings; route table unchanged.
- Hygiene: no account needed (signed-out suffices; if you sign in for any reason, create and delete
  through the product); production read-only; 3014/3015 stopped; `make stack-status` as found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the launcher is server-rendered behind a ≤767 CSS guard and unmounted
  after hydration (files, the `useDesktop(initial)` seam, the `QuestionStrip` default kept), with
  the after-numbers (present at FCP on 9/9 routes, both runtimes; absent after hydration at ≤767).
- `## Doc impact`: `frontend.md` — the ask surface's ≤767 rule is now "not painted before
  hydration (CSS), not rendered after it (unmount)", and `useDesktop(initial)` exists for the one
  caller that renders on the server (P12.F2).
- `## Notes for later slices`: remove the `for P12.F2` note; add a `for P12.S2` line only if the
  release needs to know something (nothing expected). Do not touch the shared bar or F1's
  measurement-seams note.
- `## Now` (≤ 15 lines): F2 landed with the numbers; `P12.F3` next (the two `/portfolio` bands —
  remind it of the port-scoped-storage seam); freeze date; production on `a74c58a`.

`result.md`, verdict block first, with the before/after table per route.

## Do not

- change any launcher number, the widget, `AskLauncher.tsx`'s DOM, or `QuestionStrip`'s
  behaviour; add a test file; commit; run any workflow state command; write on production; drive
  Aside `u0`.
