# P12.S1 — Account dropdown: one caret box in both states (stop the +5.38px width jump)

`kind: fix`, `risk: high` → `slice-executor-high`. Two product files, a real-browser proof in
Aside, a signed design to respect. Written 2026-09-03 by the orchestrator in `auto` mode.

## Read first

- `works/phases/active/P12/phase.md` — `## Decisions` (instrument, runtime, freeze, R8 rule) and
  the four notes tagged `for P12.S1` under `## Notes for later slices`. Consume those four notes
  when you finish (remove them; their detail lives in this slice's `result.md`).
- `frontend/components/chrome/AccountSlot.tsx` (header comment, `CARET_CLOSED` / `CARET_OPEN` at
  ~87-88, the caret span at ~160-161) and `frontend/components/chrome/AccountSlot.module.css`
  (`.frame`, `.frame[aria-expanded="true"]`, `.caret` at 82-86, `.menu`).
- `docs/current/operations.md` § `## Operator Runtime` for the runtime, remembering the one stale
  point `phase.md` records: the instrument is **Aside, `aside repl --account u2 "<js>"`**, never
  `u0`, never `aside account use`, never `aside profile list`. The repl preamble and sharp edges
  are in `.claude/skills/design-cowork/SKILL.md` from line ~425.
- `docs/current/qa.md` § *Real-browser verification* — the "Hygiene rule for a browser pass"
  paragraph (test accounts through the product, deleted through 계정 삭제).

## The defect, and one fact that decides the fix

The frame swaps `▾` (closed) for `▴` (open). Measured in dev at 1280 (`intent.md` § Notes):
`▾` advances **5.67px**, `▴` **11.05px** (`▼`/`▲` 11.05px too), so the frame goes **239.67 →
245.05px** with its right edge anchored and the whole control's left edge slides on every toggle.
Height stays 32px; nothing else changes.

**Why the two glyphs differ — verified by the orchestrator with fontTools on
`frontend/app/fonts/NotoSansKR.subset.woff2`: U+25BE `▾`, U+25B4 `▴`, U+25BC `▼` and U+25B2 `▲`
are all absent from the subset** (they are not in `frontend/scripts/korean-charset.txt` either).
Both carets are therefore fallback glyphs drawn by whatever system face Chromium reaches next in
`--font-sans` (`var(--font-noto-sans-kr), "Noto Sans KR", system-ui, -apple-system, sans-serif`),
and the two code points land in faces with different advances — and would land differently again
on Windows or Android. Any fix that keeps two code points keeps a platform-dependent pair of boxes.

## The fix: one glyph, flipped by a layout-neutral transform

Render **`▾` in both states** — the closed-state pixels stay exactly what R8 signed and what the
operator sees today — and when the menu is open flip that same glyph vertically with a CSS
transform, so the open state reads as `▴` (a mirrored `▾` *is* the `▴` shape) without a second
code point, a second fallback face, or a second box. Concretely:

- `AccountSlot.tsx`: the span renders `CARET_CLOSED` always (retire `CARET_OPEN`; keep one
  constant, and correct the `/** 열림 시 ▴ … */` comment and the header sketch to say the open
  reading is the same glyph flipped). `aria-expanded` on the button already carries the state for
  assistive tech; the caret stays `aria-hidden`. Keep `{open ? … : …}` out of the caret's text.
- `AccountSlot.module.css`: add `.frame[aria-expanded="true"] .caret { transform: scaleY(-1); }`
  (or `rotate(180deg)` — pick whichever lands the ink where the measurement says; see below). The
  span is a flex item, so it is already blockified and the transform applies with no `display`
  change. **No transition** on the transform: R8 signed an instant swap and nothing in this phase
  adds motion the operator did not sign. Add a short comment naming the reason (glyphs absent from
  the subset → fallback advances differ → one glyph, flipped, is the only platform-independent
  constant box) and pointing at `P12.S1`.
- Nothing else in `.frame`, the hover state, the open state's colours, the menu, the mobile sheet,
  or `Nav.tsx` changes. **RESPECT THE DESIGN**: no restyle, no new affordance, no icon swap.

If, while measuring, the flipped `▾`'s ink lands visibly off the vertical centre the closed `▾`
occupies (a flip pivots on the span's box, not on the ink), tune `transform-origin` (or switch
between `scaleY(-1)` and `rotate(180deg)`) until the two states' caret ink share a centre within
1px. That is the only tuning this slice does; if it cannot be done without touching the frame's
geometry, stop and report rather than widen the change.

## Verification — all live, no test file

Repo rule: tests only for core behaviour; this is cosmetic surface, verified live. The dev stack is
already up (`make stack-status` at plan time: postgres healthy, api `127.0.0.1:8010`, web
`127.0.0.1:3010`); leave it as you found it.

1. `cd frontend && npm run typecheck` and `npm run smoke` — both pass.
2. **Dev runtime, 1280, Aside `--account u2`** — open `http://127.0.0.1:3010/auth/login`, create a
   throwaway account **through the product** (signup: email + password ≥ 8 chars, the panel's own
   form), so the nav shows the signed-in frame. Then, over **at least five toggles** (click,
   Escape, outside-click, keyboard), record per state: the frame's `getBoundingClientRect()`
   (`width`, `left`, `right`, `height`), the caret span's rect, and the menu's `left`/`right` when
   open. Pass = frame `width` and `left` identical across every toggle (was +5.38px / left edge
   sliding), height 32px, menu still aligned to the frame's right edge with `min-width` = frame
   width. Hover the frame and confirm nothing moves. Take a paired screenshot (closed / open) of
   the slot region and compare the caret's ink position across the pair — the flip must not move
   the caret's centre by more than 1px.
3. **Local production build** — copy `frontend/` to a scratch directory **outside the repo** (e.g.
   `/private/tmp/claude-502/-Users-sugang-projects-personal-Mijual/4d8eac95-f4f0-458f-9341-c63977936afe/scratchpad/p12s1-build/`;
   never build into the working tree's `.next`), build with
   `NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`,
   stage `.next/static` and `public/` into `.next/standalone/` (the recipe `phase.md` records and
   `P4.F7`'s `result.md` used), serve `node .next/standalone/server.js` on **3014**, and repeat the
   step-2 measurement there (the same throwaway account works — it lives in the shared dev API).
   Stop that server afterwards.
4. **390 (mobile)** — the desktop slot is `display: none` at ≤480 (`Nav.module.css` `.utility`) and
   the sheet has no caret: open the sheet once at 390 in dev, signed in, and confirm the account
   rows are unchanged (no rect moves between opening and closing the sheet).
5. **Hygiene:** delete the throwaway account through `/portfolio/notifications` → 계정 삭제 (press
   once to arm, then confirm) before you finish; leave `NEXT_PUBLIC_VOCKY_SRC` unset; never open the
   operator's `.env`; `make stack-status` shows the stack as it was. Production
   (`https://jujutower.com`) is **read-only** — do not sign up or toggle anything there; it still
   serves `a74c58a` and this fix reaches it only through `P12.S2`.
6. `python3 scripts/workflow.py validate`.

Name the instrument you actually used in `result.md` (Aside `--account u2` is expected; the CDP
fallback only if Aside is genuinely unavailable, and then say so). Never claim a browser run you
did not make.

## Notebook (`phase.md`) when you finish

- `## Decisions`: one line — the caret is a single `▾` flipped by transform in the open state
  because neither caret code point is in the Noto subset and fallback advances differ per
  platform; the frame is pixel-equal across the toggle (numbers).
- `## Doc impact`: one line for `frontend` — Surfaces / the chrome's account slot: the caret
  mechanism (one glyph + transform, why), so the docs phase can carry it.
- `## Notes for later slices`: remove the four `for P12.S1` notes. Add, tagged
  `**(from P12.S1, for P12.R1)**`, only what the hunt needs: that the nav's account frame is now
  stable across the toggle (so the hunt does not re-report it), and any other flicker you
  *noticed* in the chrome while measuring but did not touch (route, viewport, what moved) —
  seeds for the hunt, not fixes.
- `## Operator Questions`: append only if something genuinely needs the operator (none expected).
- `## Now` (≤ 15 lines): S1 landed with the numbers; `P12.R1` (the flicker hunt) is next; the
  freeze date; production still on `a74c58a`.

## Do not

- restyle the frame, add a transition, swap to an SVG icon, or touch any file beyond the two
  named plus `phase.md` and this slice's `result.md`;
- write a test file; commit; run any workflow state command; touch production.

## Return

The structured verdict, `result.md` first with the same block at its head (status, summary worth
quoting, files_changed, validation table with the measured widths before/after in both runtimes,
deviations, doc_impact).
