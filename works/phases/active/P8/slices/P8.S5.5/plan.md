# Plan — P8.S5.5 · Account-menu 「의견 보내기」 row (R9 session instruction, Operator Question Q12)

## What this slice is

One operator instruction given inside the R9 design session, recorded in
`docs/reference/design/rounds/09-landing-board/output/build-prompt.md` §12 and drawn in the landed
card `docs/reference/design/rounds/09-landing-board/output/chrome/AccountSlot.html` (R9-session
revision): the **desktop account menu gains a third row** — `알림 설정 / 의견 보내기 / 로그아웃` — and
the row is a **third entry point to the feedback surface 미주알 already owns** (`chrome/Feedback.tsx`,
R8 build-prompt §6), beside the footer link and the mobile sheet row. *No new surface, no new copy*:
the label is the existing `VOCKY_ROW_KO` (「의견 보내기」 — the build-prompt calls it `FEEDBACK_OPEN_KO`;
the repo's constant is `VOCKY_ROW_KO` in `frontend/components/chrome/copy.ts:133`, and that is the one
to reuse), the behaviour is the footer link's (open the R8 panel).

RESPECT THE DESIGN: build exactly this, nothing else. Not in scope: the mobile sheet (it already has
its own 의견 보내기 row, R8 §3 — leave `AccountSlotSheet` and `Nav.tsx` alone), the anonymous state,
any change to `Feedback.tsx`'s states/copy, any restyle of the menu.

## Operator runtime (verify here, not in the executor's convenience runtime)

`docs/current/operations.md` `## Operator Runtime`: `make stack-up` dev stack — `next dev` on
`http://127.0.0.1:3000` (Chrome desktop on this Mac) and the tailnet origin `http://100.77.164.42:3000`;
a production build (`cd frontend && npm run build && npm run start` on another port) when behaviour
differs. Desktop only for this slice (the row exists only in the desktop menu), plus a 390 check that
nothing changed in the sheet. Signed-in state: use the operator's existing session in that browser
profile if present, otherwise the dev login path the auth surface provides — **never type credentials
into anything; never print `.env`**.

## Build

1. `frontend/components/chrome/AccountSlot.tsx`, `AccountSlotDesktop` only:
   - Import `VOCKY_ROW_KO` from `./copy` and `FeedbackDialog` from `./Feedback`.
   - Add state `feedbackOpen` + a ref for the frame button (`returnFocusTo`).
   - Insert between the 알림 설정 `Link` and the 로그아웃 `button` a `<button type="button"
     role="menuitem" className={styles.menuRow} aria-haspopup="dialog"
     aria-expanded={feedbackOpen}>` with label `{VOCKY_ROW_KO}` whose click **closes the menu and
     opens the dialog** (`setOpen(false); setFeedbackOpen(true)`) — the same order `Nav.tsx` uses for
     its sheet row, because the menu closes on outside clicks and a dialog living inside it would be
     closed by its own first click.
   - Render the dialog **outside the menu, inside the slot `div`** (so the slot's outside-click
     listener does not matter once the menu is closed): `<FeedbackDialog channel="web"
     variant="anchored" onClose={() => setFeedbackOpen(false)} returnFocusTo={frameRef} />`.
     `channel="web"` — it is the desktop web chrome, the same vocky channel as the footer.
   - **Placement decision — the one thing the record does not draw**: the `anchored` variant
     positions `.asPanel` as `position:absolute; right:0; bottom: calc(100% + 10px)` relative to a
     `position:relative` parent (`.anchor` in `Feedback.module.css`), i.e. *above* the entry — right
     for the footer, wrong under a top bar where "above" is off-screen. Give the slot a positioning
     context and place the panel **below** the frame, right edges aligned (mirror the footer rule:
     `top: calc(100% + 10px)` instead of `bottom`), by adding a modifier in
     `AccountSlot.module.css` / a wrapper class — **do not edit `Feedback.module.css`'s existing rules**
     (other entry points own them); a new, additive rule scoped to the account slot is fine. If that
     needs a prop on `FeedbackDialog` (e.g. a `placement` / `className` passthrough), add the smallest
     additive prop with a default that leaves the footer and nav untouched. Keep the ≤480 bottom-sheet
     behaviour as the variant already does (the desktop menu does not exist ≤480 anyway).
   - Do not invent a dialog title/copy/state: the panel is exactly R8's.
2. Mobile sheet: **no change** — confirm `AccountSlotSheet` untouched and the sheet still shows
   identity row / 알림 설정 / 로그아웃, divider, 의견 보내기 (Nav's own row).
3. `docs/reference/design/grounding/copy-inventory.md`: no new string; if the inventory lists
   entry points per string, add the account menu as a third entry point for 「의견 보내기」.
   `phase.md`: one Doc impact line (**frontend** — account menu 3 rows, third 의견 entry point; R9
   build-prompt §12 executed).

## Verify (operator runtime)

- `cd frontend && npm run typecheck` clean; `npm run smoke` passes (add no new test; if the smoke
  list has a chrome menu case, extend that one assertion only).
- In `next dev` on `127.0.0.1:3000` **and** `100.77.164.42:3000`, signed in, desktop 1280+: open the
  account menu → three rows in order 알림 설정 / 의견 보내기 / 로그아웃; click 의견 보내기 → menu closes,
  the R8 panel opens below the frame, right-aligned, fully on screen, focus in the textarea; Esc / ×
  closes it and focus returns to the frame; the footer 의견 보내기 and the mobile sheet row still work
  unchanged; 390: sheet unchanged. Console: 0 errors (favicon 404 = D5, known).
- Production build once (`npm run build` → `npm run start` on a spare port): same menu + panel check
  on one page.
- Don't send a real feedback message as part of verification unless you label it as a test; the
  operator can delete test rows in `/ops/feedback`.

## Return

`done` with `files_changed`, the placement rule you used, and the Doc impact line; `needs_operator`
if signed-in access in the operator runtime is not available to you; `escalate` to high if the
placement needs more than an additive modifier (this slice is rated `low` → mid tier on the
assumption that it is a few lines + one CSS rule).
