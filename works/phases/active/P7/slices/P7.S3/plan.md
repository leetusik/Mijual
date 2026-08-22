# Plan — P7.S3: board — a limited firm list at a time, with the signed 펼치기 disclosures working

## Why

Operator item 4a: "the 관제 현황판 list should show some amount of firms, not all at once."
`components/landing/Board.tsx` renders every ranked row (`GET /board` → 386 ranked rows today;
`open_now` 60 / `tbd` 4 are the two pinned strips). R2 (`docs/reference/design/rounds/
02-landing-chrome/output/build-prompt.md` §Board) specifies sort (D-day ascending across types),
the row anatomy, the tabs, and the two pinned strips with their hairline 펼치기 button — but **no
list length and no pagination control** (`P5.S3` note 11: "the design paginates nothing").
So this is an operator override of an unsigned gap, and the 펼치기 half of item 4 (4b) is already
closed by `P7.S1` — the toggles work once the page hydrates; verify, do not rework them.

Read first: `phase.md` → "Item 4a", "Design-collision readings" #3, Constraints, the `P7.S1`/`S2`
findings (StrictMode warning: any new effect touching module state must be re-checked in
`next dev`). Read the R2 build-prompt §Board and the round's `result.md` for the board section so
you restyle nothing.

## What to build

1. **A display window on the ranked list, in `Board.tsx`.** Initial window: **30 rows**
   (operator gave no number; 30 is the orchestrator's default — it is roughly the "30일 이내 마감"
   horizon R2's stat card names, and small enough to scan. Record it as a P7 decision in
   `phase.md` and in the Doc impact line; the review lists it for the operator). The window is a
   **display** limit, never a filter: the tab counts stay whole-board (`counts` — 전체 keeps
   reading 488), the served corpus is untouched, and the ranked order is unchanged. Tab switch
   resets the window to the initial 30 (a tab is a new list).
2. **The "more" control reuses the record's own disclosure idiom — the 펼치기 hairline button**
   (`EXPAND_KO`, `styles.expand` — same class, same hover, same 44px mobile floor), placed
   directly under the visible rows in the same position/feel as the strips' disclosure. Do **not**
   mint a new label word: the button reads `펼치기`. Clicking reveals the next 30 (or all
   remaining — pick one and say why; revealing in chunks of 30 keeps the page scannable, which is
   what the operator asked for). When every ranked row is shown, the button goes away (a
   disclosure with nothing to disclose is a sentence about nothing — the same rule `Strip` keeps).
   If you add a count beside the button (e.g. the remaining rows as a mono `N건` like the strip
   counts), keep it to the signed mono-count idiom and **no new sentence**; list any string you
   could not avoid under Doc impact and in `result.md` for the review's operator questions.
   Prefer zero new Korean copy.
3. **The strips are unchanged** (`Strip` already works; the operator's 60건/4건 quotes are those
   strips). Confirm in the browser that both expand/collapse and that the new ranked-list
   control does not visually collide with the ② strip below it (spacing via existing tokens only).
4. State lives in component state (`useState`) — no module store, no effects needed.
   `prefers-reduced-motion` irrelevant unless you animate (don't).
5. Keep the board's doc comment truthful: its "Why the tabs filter in the browser" paragraph
   says "the design paginates nothing" — extend it with one sentence about the P7 display window.

## Verify — operator runtime first

Dev stack is up (`make stack-status`); Fast Refresh picks up the edit. Headless Chrome over CDP
(see `P7.S1` / `P7.S2` `result.md` for the approach), on **`http://127.0.0.1:3000`** (and once on
the Tailscale URL), fresh profile, at 1440 and 390:

- ranked rows rendered initially: **30** (was 386); the 펼치기 control present under them;
- click → **60** rows (or all), and the control disappears when exhausted (click through to the
  end once and count: total must equal the ranked count for that tab — e.g. 386 on 전체);
- tab counts unchanged: 전체 488 etc. (read the tab `mono` counts);
- switch to a type tab → window resets to ≤30, rows all of that type, order preserved;
- both pinned strips still expand (row counts grow) and collapse;
- the new control measures like the strip's 펼치기 (same computed border/font/min-height at 1440
  and 44px at 390);
- no console errors; no extra network requests on click (it is all client-side).
Production build: `next build` + `next start -p 3100` in an isolated copy of `frontend/` (the way
`P7.S2` did — no `--dist-dir` in Next 16.3.2; real copy, not a symlinked `node_modules`), spot-check
the 30/펼치기 behaviour on `127.0.0.1:3100`, kill it. Leave the dev stack running.
`cd frontend && npm run typecheck && npm run smoke`; `python3 scripts/workflow.py validate`.

## Record

`result.md` (commands, before/after numbers, what the control looks like, any copy minted,
deviations). `phase.md`: a short Findings note + a **`frontend` Doc impact line** ("the board shows
30 ranked rows at a time with a 펼치기 disclosure; display window, never a filter; P7 operator
override of R2's unlimited list") and, if `product.md`/`experience.md` describe the landing board as
showing everything, a line for those too. No `doc-new-version`, no commits, no state transitions.

## Out of scope

The strips' behaviour (done), the board's data/API, copy elsewhere, focus styling (S5), nav (S6).
