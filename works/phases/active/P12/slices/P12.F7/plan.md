# P12.F7 — the 의견 보내기 dialog: three body heights, and the ≤480 sheet's top edge jumping 91.46 px (R1 F9)

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.F6` (`b777ada`). **Family D** (one dialog, three bodies of different heights) with
a **Family B** half (보내기 ↔ 보내는 중입니다) that this plan settles the way `P12.F6` settled F8.

## Read first

- `phase.md`: `## Decisions` — F6's ruling (the ghost is resting-identical **only where the resting
  label is the widest state**), the instrument seam with F6's three screenshot traps (**one capture
  per `aside repl` invocation, never `{fullPage: true}` under an emulated viewport, exclude the
  scrollbar strip, a console shim via `Page.addScriptToEvaluateOnNewDocument` proven live**), the
  build recipe; the shared bar (keep it); F1's seams note. `## Now` says why this slice must check
  the precondition first — it is checked below.
- The finding's numbers, from the R1-era notebook:
  `git show 8519f45:works/phases/active/P12/phase.md | grep -n "F9 (rank"` — at **1280** the
  footer's anchored panel is editing **[796, 426, 380, 318.02]** → sending (same box; 닫기 removed;
  the send button **71.27 → 124.73 px**, +53.46) → sent **[796, 501.45, 380, 242.56]**: **−75.46 px**
  tall and the **top edge drops 75.45 px** (the panel hangs *above* its entry, so a shorter body
  moves its top). At **390** the bottom sheet is **[0, 498.98, 390, 345.02]** → sent
  **[0, 590.44, 390, 253.56]**: **−91.46**, the **top edge jumps down 91.46**. Measured with one
  real send in the dev DB. The failed state was not measured.
- The code, all of it in two files: `components/chrome/Feedback.tsx` — `FeedbackDialog` (`phase`:
  editing / sending / sent / failed; the `sent` body = notice + 접수 번호 inset + fine + actions[닫기];
  the `failed` body = notice + the preserved message in `.inset.kept` (**variable height**, up to
  4,000 chars) + fine + actions[닫기, 다시 시도 when retryable]; the form body = guide + textarea
  (`resize: vertical`) + fine + actions[hint when empty, 닫기 **unmounted while sending**, the
  submit button 보내기 / 보내는 중입니다]) and `FeedbackEntry`; `Feedback.module.css` — `.surface`
  (flex column), `.asPanel` (`position: absolute; bottom: calc(100% + 10px)` — **bottom-anchored**,
  so the top edge moves), `.asPanel.asPanelBelow` (≥481 only, the account menu's entry:
  `top: calc(100% + 10px)` — top-anchored, the bottom edge moves instead), `.asSheet` and the
  ≤480 `.asPanel` override (`position: fixed; bottom: 0` — bottom-anchored), `.body` (flex column,
  `gap: var(--space-3)`, `padding: var(--space-4)`), `.field` (`min-height: 104px`, 120 at ≤480),
  `.actions` (`justify-content: flex-end`), `.quiet` / `.send` (`height: 36px`, `min-height: 48px`
  at ≤480). Copy in `components/chrome/copy.ts` L272–295 — do not change a string.
- The record the code cites: R8 build-prompt §6 (`Feedback.html` / `FeedbackStates.html`) — the
  state machine in `Feedback.tsx`'s doc comment is its transcription: sending = 「the textarea locks
  and dims, the button says 보내는 중입니다 and **닫기 disappears**, and there is no spinner」.
- Entry points (three): `Footer.tsx` → `FeedbackEntry` (anchored above; a bottom sheet at ≤480);
  `Nav.tsx` ~L209 (the ≤767 menu sheet's row, `variant="sheet"`); `AccountSlot.tsx` ~L218 (signed-in
  desktop, `placement="below"`).

## The change

**1. One body height, pinned at the moment the reader presses 보내기 — Family D.** Do not add a
measured constant: the editing body's height depends on the viewport *and* on a textarea the reader
may have dragged taller, so a CSS number would be wrong exactly when it matters. Instead, in the
submit handler (and in 다시 시도's `send`), read the current body's rendered height
(`bodyRef.current.getBoundingClientRect().height` — the `.body` element, not the surface) **before**
`setPhase("sending")`, keep it in state, and render every later body (sending, sent, failed) with
`style={{ minHeight }}` — `min-height`, never `height` (F4's rule: a failed body carrying a long
message may legitimately exceed it and then grows; a sent body never does). Set the state in the same
handler call as the phase change so React commits both together and no intermediate frame exists.
The editing state renders **no** inline style → the resting dialog is byte-identical.

Inside a pinned body the content keeps the record's order and styles. **Pin the actions row to the
bottom of the body** (`.actions { margin-top: auto }` — it is already the last child of a flex
column, so this only takes effect when the body is taller than its content, i.e. only in a pinned
body): the reader's cursor was on 보내기 at the bottom-right, and 닫기 / 다시 시도 then sit where their
hand is, instead of 75–91 px of empty panel below them. This is the one visible consequence of the
fix — the sent and failed panels are as tall as the form was — and it is what `DECOMP2` cut
(「one body height across editing / sending / sent / failed」); record it plainly for the walkthrough.

**2. 닫기 while sending — measure before touching.** The record says 닫기 *disappears* while
sending, and `DECOMP2`'s cut line says 「keep it mounted-but-disabled」. Those conflict, and the
measurement decides: unmounting a 36 px button from a 36 px-tall right-aligned row should move
nothing but itself. If the rect sweep shows its unmount moving **nothing else** (the send button's
own growth is a separate matter, below), leave the record's behaviour exactly as it is. If it does
move something, hold its box with `visibility: hidden` (not `disabled`, not `opacity`): the record's
「disappears」 still holds for eyes, assistive tech and hit-testing, and the box stays.

**3. 보내기 ↔ 보내는 중입니다 (+53.46 px) — no code; a question.** F6's precondition fails here: the
resting label 「보내기」 is the *narrower* one, so the only ghost that holds the row makes the resting
button 53.46 px wider in a signed dialog. Do not implement it. Append **Q9** to `## Operator
Questions`: the numbers (button 71.27 → 124.73 px, the label's left edge moving 53.46 px left while
sending, at 1280 and whatever 390 shows), the proposal (the twin, 「보내기」 rendered in a 124.73 px
box at rest), the alternative (leave as signed — the reader's own press starts it), and one line
saying it is the same decision as **Q7** one surface over, so the operator can answer both at once.

**4. Nothing else.** No copy change, no transition, no change to the backdrop, the header, the ×,
Esc / backdrop / route-change close paths, focus return, the scroll lock, `TIMEOUT_MS`, the
`retryable` rule, or the 8 s abort. `Nav.tsx`, `Footer.tsx`, `AccountSlot.tsx` untouched.

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`; `npm run build` in a fresh copy outside the
  repo (no warnings). HEAD control build on 3015 beside the fixed build on 3014, plus dev 3010.
- **A real send lands a row in the dev DB** (R1 did the same; the build ports use the dev API on
  127.0.0.1:8010, so every port writes there and never production). Keep the message short and
  say in `result.md` how many rows you sent. **Force the failed state** without a network outage:
  CDP `Fetch.enable` on the feedback POST + `Fetch.failRequest` (or an abort past `TIMEOUT_MS`),
  so it fails deterministically and you can measure it.
- **Before/after**, Aside `--account u2`, **1280 and 390**, dev + fixed vs HEAD, from the footer
  entry at both viewports and the nav sheet's row at 390: sample the `[role=dialog]` rect (and
  the actions row, the send button, 닫기) with `requestAnimationFrame` through editing → sending →
  sent, and editing → sending → failed. Pass = the dialog's rect is **one distinct value** from
  editing through sent at each viewport (HEAD: top edge −75.45 @1280, −91.46 @390); failed with a
  short message likewise, and with a long message it grows only downward from the pinned height
  (say by how much, and that it is `min-height` doing it); the actions row's y is identical in
  sent and failed; the resting (editing) dialog `AE = 0` vs HEAD at both viewports **with a
  positive control**; the sent and failed states screenshot-diffed against HEAD show only the
  taller box and the actions' new position (name the diff box).
- **The dragged textarea:** at 1280 drag the resize handle ~60 px taller (CDP mouse), then send —
  the pin equals the enlarged form and the top edge still holds.
- **The `below` placement** (account menu, signed in) is the same mechanism with the opposite
  anchored edge; verify it **only if cheap** (a throwaway account created and deleted through the
  product) — otherwise say it was not measured and why it holds by construction.
- Close paths after a send (×, 닫기, Esc, backdrop at 390) and focus return to the entry: unchanged.
- **Console / hydration:** the F6 shim, proven live with an injected `console.error`, on every
  measured load — nothing on the production build.
- Hygiene: production read-only; 3014/3015 stopped; `make stack-status` as found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the dialog's body is pinned at press time (files, the mechanism,
  actions bottom-pinned in a pinned body, the after-numbers at both viewports, what 닫기 does and
  why).
- `## Operator Questions`: append **Q9** as above.
- `## Doc impact`: `frontend.md` — Surfaces / 의견 보내기: one body height across sending / sent /
  failed, pinned at the press (`min-height`), the actions row at the bottom of a pinned body; the
  ≤480 sheet's top edge no longer moves; 닫기's behaviour as measured (P12.F7).
- `## Notes for later slices`: add nothing unless `P12.S2` needs it. Do not touch the shared bar,
  F1's seams note, or the `for P12.REVIEW` / `for P12.S2` notes.
- `## Now` (≤ 15 lines): F7 landed with numbers; Q9 raised; `P12.F8` next (the search-miss line —
  `LookupHeader.tsx`, Family D); freeze date; production on `a74c58a`.

`result.md`, verdict block first, before/after tables at both viewports, the failed-state numbers,
the 닫기 measurement and what it decided, the dev-DB rows sent.

## Do not

- add a measured height constant, change a string, ghost the send button, add a transition, touch
  `Nav.tsx` / `Footer.tsx` / `AccountSlot.tsx`, add a test file, commit, run any workflow state
  command, write on production, or drive Aside `u0`.
