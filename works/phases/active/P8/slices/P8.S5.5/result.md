# Result — P8.S5.5 · Account-menu 「의견 보내기」 row (R9 §12, Operator Question Q12)

**Status: done.** The desktop account menu is three rows — 알림 설정 / **의견 보내기** / 로그아웃 — and
the new row is the third entry point to the 의견 surface 미주알 already owns (R8's `Feedback.tsx`),
opened with the existing `VOCKY_ROW_KO` label and R8's own panel. No new surface, no new copy, no
restyle. Verified signed-in in the operator's runtime on `127.0.0.1:3000` **and** the tailnet origin
`100.77.164.42:3000` in `next dev`, **and** in a production build on `:3100`.

## 1. What changed

| file | change |
|---|---|
| `frontend/components/chrome/AccountSlot.tsx` | `AccountSlotDesktop` only: `feedbackOpen` state + a `frame` ref; a third `role="menuitem"` button between 알림 설정 and 로그아웃 carrying `{VOCKY_ROW_KO}`, `aria-haspopup="dialog"` and `aria-expanded`, whose click does `setOpen(false); setFeedbackOpen(true)`; `<FeedbackDialog channel="web" variant="anchored" placement="below" returnFocusTo={frame}>` rendered **outside the menu, inside the `.slot` div**; one breakpoint effect (see §4). Doc comment updated to cite R9 §12. |
| `frontend/components/chrome/Feedback.tsx` | one additive prop — `placement?: "above" \| "below"`, default **`"above"`** — appending `styles.asPanelBelow` to the anchored surface when asked. The footer (`FeedbackEntry`) and the nav's sheet row pass nothing and are byte-identical in behaviour. Class doc now names three entry points instead of two. |
| `frontend/components/chrome/Feedback.module.css` | one **new** rule at the end of the file (no existing rule touched): `@media (min-width: 481px) { .asPanel.asPanelBelow { top: calc(100% + 10px); bottom: auto; } }`. |
| `docs/reference/design/grounding/copy-inventory.md` | hand-registered tail: no new string; `VOCKY_ROW_KO`'s 어디에 column now names three placements. |

`AccountSlotSheet`, `Nav.tsx`, `Footer.tsx`, `copy.ts` and every state/copy inside `Feedback.tsx`:
**untouched** (`git diff --stat` covers exactly the three frontend files above).

## 2. The placement decision — the one thing the record does not draw

R8 drew a single anchored entry point, the footer, at the bottom of the page, so `.asPanel` is
`position:absolute; right:0; **bottom**: calc(100% + 10px)` — the panel hangs *above* its entry. The
account slot's entry is in the 52px top bar, where "above" is off-screen. The rule chosen is the
mirror of R8's own, nothing more: same 10px offset, same right-edge alignment, `top` instead of
`bottom`, gated to ≥481 so the ≤480 bottom-sheet form is untouched.

It lives in `Feedback.module.css` rather than `AccountSlot.module.css` because the panel's geometry is
the panel's, and a cross-file CSS-module override would depend on bundler emission order. The doubled
selector `.asPanel.asPanelBelow` wins **by specificity rather than source order** — the rule
`Nav.module.css` already states for `.sheet.sheetOpen`. `.slot` was already `position: relative`, so
no new positioning context was introduced.

Measured (dev, signed in, panel open): panel `top = slot.bottom + 10` and `panel.right = frame.right`
(gap **0**) at **1512 / 1280 / 1024 / 768 / 600 / 481**, width 380, fully inside the viewport at every
one, `document` overflow **0**. The footer's own panel still hangs **10px above** its entry, right
edges aligned, width 380 — unchanged.

## 3. Validation

| command | result |
|---|---|
| `cd frontend && npm run typecheck` | clean |
| `cd frontend && npm run smoke` | **16/16** |
| `cd frontend && npm run build` | ✓ 15/15 pages (`next-env.d.ts` rewritten by the build, restored with `git checkout --`) |
| `.venv/bin/python -m pytest` | **142 passed** (no Python touched; the phase's regression floor) |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

No test was added: the change is a menu row and one CSS rule, `npm run smoke` globs `lib/*.test.ts`
only (`P8.S3` note 9), and the behaviour lives in components, so a new file there would never run.

## 4. Verified in the operator's runtime

Harness: headless Chrome over raw CDP, fresh profile per run (the shape `P7.S9`/`P8.S3`/`P8.S5` used);
scripts in session scratch. Signed-in state was obtained the way `P8.S3` did it — a **throwaway
account created through the product's own 계정 만들기 panel and deleted through the product's own
계정 삭제 control** in the same run. No credential of the operator's was typed anywhere, no `.env` was
read or printed, and the vocky key was never touched. **The database is exactly as found**: `account`
holds `s19-fidelity@example.com` (14) and `swangle2100@gmail.com` (25), same as `P8.S3` left it.

| check | dev `127.0.0.1:3000` | tailnet `100.77.164.42:3000` | prod build `:3100` |
|---|---|---|---|
| menu rows, in order: `A 알림 설정` · `BUTTON 의견 보내기` (`aria-haspopup="dialog"`, `aria-expanded="false"`) · `BUTTON 로그아웃` | ✓ | ✓ | ✓ |
| the row is the menu's own row shape — same class as its siblings, **40px**, 13.5px, `0 12px`, hairline separators only between rows (`0 / 1 / 1`) | ✓ | ✓ | ✓ |
| click 의견 보내기 → the **menu closes** (`[role=menu]` gone, frame `aria-expanded=false`) and R8's panel opens: `role="dialog"`, `aria-label` 의견 보내기, title 의견 보내기 | ✓ | ✓ | ✓ |
| panel geometry: `top` 52 = slot bottom 42 + 10, right edge 1176 = frame's, 380 wide, on screen, 0 overflow, `z-index` 20, **no backdrop** (`display:none`) | ✓ | ✓ | ✓ |
| focus lands in the textarea (placeholder 예: 계양전기 …) | ✓ | ✓ | ✓ |
| idle state is R8's: 보내기 **disabled** + 「내용을 입력하면 보낼 수 있습니다.」, no error colour | ✓ | ✓ | ✓ |
| **Esc** closes it and focus returns to the account frame button | ✓ | ✓ | ✓ |
| **×** closes it and focus returns to the frame | ✓ | ✓ | ✓ |
| the **footer** 의견 보내기 still opens its own panel, still 10px **above** its entry, right-aligned, focus in the textarea, Esc closes | ✓ | ✓ | ✓ |
| **390px**: the sheet is unchanged — AI 질문 / 보유 종목 / divider / identity row / 알림 설정 / 로그아웃 / divider / 의견 보내기; the desktop slot has no box at all; the sheet's own 의견 row opens the full-width bottom sheet (390×345, flush bottom), focus in the textarea, Esc closes and the body scroll lock is released | ✓ | ✓ | ✓ |
| console: **only** `GET /favicon.ico` 404 (deferred D5) — the only ≥400 response of the whole run; 0 exceptions, 0 React warnings | ✓ | ✓ | ✓ |

Keyboard-only: focus the row, Enter → the panel opens with focus in the textarea (the row is a plain
`<button>` in the menu's DOM order, so it needs nothing of its own).

**One bug found and fixed inside this slice.** Below 480px the whole desktop slot is `display: none`
(`Nav.module.css .utility`), so an open account panel goes invisible **with its ancestor** while
`FeedbackDialog`'s ≤480 branch still holds the counted body-scroll lock. Measured at 400px before the
fix: dialog in the DOM, `offsetParent === null`, zero-size rect, `body { overflow: hidden }` — the
page silently unscrollable with nothing on screen to close, exactly the family `P8.S3` note 3 warns
about. Fixed with one effect in `AccountSlotDesktop` that closes the panel when
`(max-width: 480px)` matches — the honest end for a panel whose entry point has left the layout, and
the width where the sheet's own 의견 row takes over. Re-measured after: dialog gone, `body` scrollable,
on dev, tailnet and production alike.

**Not done on purpose:** no feedback message was actually sent from the new entry point. The send path
is R8's, `P8.S3` already proved it end to end (its three test rows are the standing Operator Question
Q9), and the new row hands `FeedbackDialog` exactly the footer's props (`channel="web"`), so sending
again would only add another row to the operator's real vocky project.

## 5. Deviations from `plan.md`

1. **The placement rule lives in `Feedback.module.css`, not `AccountSlot.module.css`.** The plan
   allowed either ("a new, additive rule scoped to the account slot is fine … or add the smallest
   additive prop"). Both were taken in their smallest form: the additive `placement` prop, and a new
   rule beside the rule it mirrors. No existing rule in that file was edited, and `.slot` already had
   the positioning context the plan asked for, so `AccountSlot.module.css` needed no change at all.
2. **One extra effect** — the ≤480 close described above. It is not in the plan because the plan could
   not know the measurement; it is not a design decision (nothing visible changes at any width the
   menu exists at) and it repairs a real lock. Recorded here and in `phase.md` rather than hidden.
3. **`copy-inventory.md`**: the plan said "if the inventory lists entry points per string". It does
   (the 어디에 column), but `VOCKY_ROW_KO` is R2-era and was never in a hand-registered table, so a
   short third tail section registers it with its three placements rather than editing R8's table.

## 6. Open, for the review to route

- **Two 의견 panels can be open at once** (measured: footer panel open → scroll up → account menu →
  의견 보내기 = 2 `[role=dialog]` nodes; Esc closes both). Each entry point owns its own state, and the
  design record never says one should close the other. Nothing was invented — catalogued as
  **Operator Question Q19** in `phase.md`.
- Q12 itself is now **executed**, not deferred: this slice is the "home" the question asked for.

## 7. State of the machine, left as found

- Dev stack untouched and up (`make stack-status`): postgres healthy, api pid 3182, web pid 13009.
  Nothing was restarted — no Python changed.
- The temporary production server on `:3100` is stopped; `frontend/next-env.d.ts` restored;
  `.next/` is the build's own artifact, untracked as always.
- Session scratch (harness, probes, screenshots):
  `…/scratchpad/p8s55/` — `cdp.mjs`, `check.mjs`, `extra.mjs`, `cleanup.mjs`, `panel-*.png`,
  `sheet-*.png`.
