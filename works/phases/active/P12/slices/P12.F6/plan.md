# P12.F6 — Family B: one slot, two label widths — the 정정 이력 button (R1 F12), and why the composer (R1 F8) and the auth mode switch (R1 F10) become operator questions instead

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.F5` (`0a6fd0a`). **Family B**, the ghost-width technique the repo already owns.

## Read first

- `phase.md`: `## Decisions` — the four families, the instrument seam (every addition through F10),
  the build recipe, the **F11 no-slice verdict** (the precedent this plan applies); the shared bar
  (keep it); F1's measurement-seams note; and the note tagged **`for P12.F6`** from F5 (consume it —
  it tells you what moved in `AuthPanel.tsx`; this plan does not touch that file, but you read it
  because R1 F10 lives there and you will measure it).
- **The three findings' own numbers are not in today's `phase.md`** — `DECOMP2` consumed the R1 list.
  Read them from the R1-era notebook in git:
  `git show 8519f45:works/phases/active/P12/phase.md | grep -n "F8 (rank\|F10 (rank\|F12 (rank"`.
  In short — **F12**: `/events/20260806000329` at 1280, `components/event/Corrections.tsx`'s button
  swaps 「정정 이력」 for 「접기」 + a mono × (`span.historyMark`, 6.61 × 14) and its width goes
  **77.53 → 66.70 px** (−10.83) on open; left-aligned in its own row, nothing else moves, the 666 px
  disclosure below is intended; **≤767 `Event.module.css` gives it `width: 100%`, so mobile is
  immune**. **F8**: `/ask` at 1280, `components/ask/Composer.tsx`'s send button is 보내기 **59.13** →
  답변 준비 중… **99.92** → 중지 **48.09** → 보내기 **59.13** px across one turn; the input beside it
  swings **572.88 → 652.08 → 703.91 → 692.88** (131 px). **F10**: `/auth/login` at 1280, pressing
  계정 만들기 grows the panel **404.1 → 425.5** (+21.37) — `Auth__intro` wraps to a second line
  (+20.92) and the form and every field move down 20.92; a `span.Auth__rule` (41.75 × 17.05) is
  inserted beside the password label; the reset link disappears and the switch link goes
  58.56 → 33.13 wide.
- The technique: `components/chrome/Nav.module.css` ~L55–71 — `.link` is a grid with one area
  `label`; the visible `<span>` and a `::after { content: attr(data-label); grid-area: label;
  font-weight: 600; height: 0; overflow: hidden; visibility: hidden; pointer-events: none }` twin
  share that cell, so the cell is as wide as the widest state while the twin contributes no height,
  no accessible name and no hit target. R1 H5 proved it holds the bar still.
- The code: `components/event/Corrections.tsx` ~L102–116 and `Event.module.css` `.historyButton`
  (~L931: `inline-flex`, `gap: var(--space-2)`, `padding-inline: 14px`, `min-height: 36px`,
  `white-space: nowrap`), `.historyButton[aria-expanded="true"]`, `.historyMark` (~L960), and the
  ≤767 block (~L1347: `min-height: 44px; width: 100%; justify-content: center`).
  `components/ask/Composer.tsx` ~L77–90 + `Ask.module.css` `.send` (~L515, and the comment above it
  quoting the record: 「버튼 텍스트 교체 + disabled」 — one button, three texts). `components/auth/AuthPanel.tsx`
  (mode markup: `.head` = `h1.title` + `p.intro` with `signingUp ? SIGNUP_INTRO_KO : LOGIN_INTRO_KO`,
  the `.rule` span only when signing up, the `.quietRow` links) + `Auth.module.css`.

## The ruling this slice applies

The shared bar says the **resting** layout is pixel-identical after a fix, and `DECOMP2`'s F11
verdict applied it literally: a ghost that widens or moves something *in the resting state* is a
visible change to a signed surface, and that is the operator's decision, not ours. Family B's ghost
reserves the **widest** label. So:

- **F12 — fix.** The resting label 「정정 이력」 *is* the widest state; the ghost keeps the button at
  its resting 77.53 px when it opens. Resting pixels unchanged by construction. This is exactly
  `P12.S1`'s shape (the frame stays 261.28 px across the toggle).
- **F8 — no code; an operator question.** The resting label 「보내기」 is the *narrowest* of the
  three; every fix that keeps the composer still during a turn makes the resting button ≈ 40.8 px
  wider and the input that much narrower on both `/ask` and the 440 px widget. There is no
  resting-identical mechanism: the pending label does not fit the resting box, and changing what
  the button says or where the pending text sits changes signed copy (the record names all three
  texts). Do **not** implement it. Append **Q7** to `## Operator Questions` — the numbers above,
  the proposal (ghost of 「답변 준비 중…」: resting 보내기 59.13 → ≈ 99.92 px, input −40.8 px, and
  the turn then moves nothing), and the alternative (leave as signed). Quote R1's numbers; no live
  `/ask` turn is needed for this.
- **F10 — no code; an operator question.** The growth is the signup intro's second line; the only
  reservation is a blank line under the login intro at rest (+20.92 px in the panel a reader
  lands on), and `.rule` / the quiet-row swaps change no height. Do **not** implement it. Append
  **Q8** — the numbers above, the proposal (reserve two intro lines in both modes — a blank line
  under 「가입한 이메일과 비밀번호로 로그인합니다.」 at rest; the mode switch then moves nothing), and
  the alternative (leave as signed: the panel re-flows once, on the reader's own press).
  **Measure F10 at 390 as well** on a plain visit (no flash — F5's note says why) so Q8 carries
  both viewports (the intro may wrap differently there); a HEAD build or dev is fine for that — it
  is a "before" only.

If you find a resting-identical mechanism for F8 or F10 that this plan missed, say so in
`result.md` with the measurement and **still ship nothing for it** — the plan's scope for those
two is the question. Do not try to widen this into a design decision.

## The change (F12 only)

1. `Corrections.tsx`: the button carries `data-label={CORRECTION_HISTORY_KO}` (the copy stays in
   `copy.ts`); its visible content moves into one inner `<span>` that holds the label text and, when
   open, the existing `aria-hidden` `historyMark` span — same strings, same `aria-expanded` /
   `aria-controls` / `onClick`, no new copy.
2. `Event.module.css`: `.historyButton` becomes the grid the nav uses — `display: inline-grid;
   grid-template-areas: "label"; align-items: center` (keep `padding-inline: 14px`, `min-height`,
   `white-space: nowrap`, the hover / expanded rules, the transition); the inner span is
   `grid-area: label; display: inline-flex; align-items: center; gap: var(--space-2)` (the gap
   moves from the button to the span so the closed state renders the same 77.53 px box — verify
   that to the pixel); the twin is `.historyButton::after { content: attr(data-label); grid-area:
   label; height: 0; overflow: hidden; visibility: hidden; pointer-events: none }` with no
   `font-weight` change (both labels are the same weight). Keep the open content **centred** in the
   box (`justify-items: center`) — a label sits centred in its button everywhere in this product,
   and the 10.83 px the open state gains splits evenly. ≤767: the `width: 100%` block stays and
   still wins (the twin is narrower than the full row); `justify-content: center` there becomes
   `justify-items: center` on the grid, or stays on the inner span — whichever keeps 390 byte-identical.
3. Nothing else: no transition on width (there is none today), no change to the disclosure panel,
   the `story` rows, or the heading.

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`; `npm run build` in a fresh copy outside the
  repo (no warnings). HEAD control build beside it (F1's note).
- **Before/after**, Aside `--account u2`, **1280 and 390**, dev + fixed vs HEAD, on
  `/events/20260806000329` (or any event serving corrections — say which): rect of the button and
  of every element in its row and above the disclosure, closed → open → closed. Pass = the button's
  rect is **one distinct value** across the toggle at 1280 (HEAD: 77.53 → 66.70); at 390 the full-
  width box is unchanged; nothing but the disclosure moves; the closed state `AE = 0` vs HEAD at
  both viewports; the open state's 「접기 ×」 renders in the same box, centred; keyboard toggle
  (Enter and a real CDP Space, not `keyboard.press(' ')`) and `aria-expanded` unchanged; the
  accessible name is still the visible label only (the twin contributes nothing — check the AX
  name via CDP `Accessibility.getPartialAXTree` or the snapshot).
- **F10's 390 "before"** as above, for Q8.
- **Hydration:** console capture on every measured load — no warning, no error.
- Hygiene: no account needed; production read-only; build servers stopped; `make stack-status` as
  found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the ruling (Family B's ghost ships only where the resting label is the
  widest; F12 fixed with numbers; F8 and F10 are Q7/Q8 because every fix changes the resting
  state, the F11 precedent).
- `## Operator Questions`: append **Q7** (F8) and **Q8** (F10), each with the numbers at both
  viewports where you have them, the concrete proposal, and the cost at rest.
- `## Doc impact`: `frontend.md` — Surfaces / 공시 상세 (`/events/[rcept_no]`): the 정정 이력 button
  keeps one width across the toggle (the `Nav.module.css` twin, `data-label`) (P12.F6).
- `## Notes for later slices`: consume F5's `for P12.F6` note (record in `result.md` that
  `AuthPanel.tsx` was read, not edited). Do not touch the shared bar, F1's seams note, or the
  `for P12.REVIEW` / `for P12.S2` notes. Add a `for P12.F7` note only if you learned something
  about the ghost-in-a-flex-row shape that the feedback dialog's send button (보내기 ↔
  보내는 중입니다, +53.46 px, in a right-aligned actions row) will need.
- `## Now` (≤ 15 lines): F6 landed with numbers; Q7/Q8 raised; `P12.F7` next (the feedback
  dialog's three body heights and the ≤480 sheet's top edge — Family B + D); freeze date;
  production on `a74c58a`.

`result.md`, verdict block first, before/after table at both viewports for F12, the F10 390
reading, and the F8/F10 reasoning in a short section.

## Do not

- implement F8 or F10, change any copy, add a transition, touch `AuthPanel.tsx` / `Composer.tsx` /
  `Ask.module.css` / `Auth.module.css`, add a test file, commit, run any workflow state command,
  write on production, or drive Aside `u0`.
