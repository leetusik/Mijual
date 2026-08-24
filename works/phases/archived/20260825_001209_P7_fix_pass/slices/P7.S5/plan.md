# Plan — P7.S5: focus treatment — the clipped blue ring off the inputs, keyboard focus kept

## Why

Operator item 3: "when 내 종목 조회 input box selected, the focusing blue box is just annoying,
and its right side is covered by the 조회 box — remove it; and no selected focus on all the
input boxes." `P7.DECOMP` measured the seat (`phase.md` → "Item 3" and **Design-collision
reading #1** — the contract for this slice; Q2 in Open Questions is unanswered, so reading #1
stands): the only outline rule in the app is `frontend/app/shell.css` `:focus-visible { outline:
2px solid var(--focus-ring); outline-offset: 2px }`, `--focus-ring` aliases `--r1` (the ① 유상증자
rights hue — `#8fb2e8` in the `.cosmos` scope, `#2b5aa0` light), and on the hero/`/stocks` search
rows the input's right edge touches the 조회 button (gap 0), so a 2px outline at offset 2px paints
4px under the button. Two facts drive the design:

- Browsers apply `:focus-visible` to **text inputs on mouse click** (not just keyboard) — that is
  why the operator sees the box on every click. For buttons/links `:focus-visible` is keyboard-only.
- The record's a11y floor ("Focus ring: 2px `--focus-ring`", `frontend` v0002/v0004; R2 §vocky
  trigger "focus = 2px `--focus-ring`") stays: the defect is the **treatment on text fields**, not
  the existence of keyboard focus indication. Never leave a focusable element with no keyboard
  indicator.

## What to change

1. **Text fields lose the ring and get an in-idiom focused border instead.** In `app/shell.css`
   add a rule for text-entry controls (`input:not([type=checkbox]):not([type=radio])`,
   `textarea`, `select` — scope it precisely; checkboxes/radios keep the ring) on `:focus-visible`
   (and `:focus`): `outline: none`, and the field's own hairline brightens/strengthens — a
   `border-color` change only, in that field's colour family, no new hue, **no blue**, nothing that
   can overflow the box (no outline, no outer box-shadow). Because fields are styled per module
   (the hero's dark console `rgba(163,196,180,.4)` hairline, R4's `/stocks` console field,
   `HoldingStrip`/`SharesInput` mono fields, the auth panel, `AddHolding`, `NotificationsView`,
   the ask `Composer`, the `/ops` fields), put the generic rule in `shell.css` with a CSS custom
   property hook (e.g. `--field-focus-border`, defaulting to `var(--ink-3)` or a brightened
   `--border-strong`) and set that property in the modules whose field colours differ (the
   cosmos/hero dark console → `rgba(163,196,180,.8)`-style brightening of its own hairline).
   Read each module's existing field rule first; change border colour on focus only — never
   radius, height, padding, or background. `:where()`/low specificity so module rules still win
   where they already set a focus style (grep shows none do today).
2. **Buttons, links, tabs, chips, checkboxes keep the signed 2px `--focus-ring` ring** on
   `:focus-visible` — unchanged. Do not change the `--focus-ring` token or the vocky trigger focus.
3. Check the two zero-gap rows after the change: on `/` and `/stocks` the focused input's border
   must be fully visible and nothing paints under the 조회 button; if the shared border edge
   between input and button (input has `border-right: none` on the hero) makes the focused
   border look one-sided, that is acceptable and signed geometry — do **not** move the button or
   add a gap. (If S4 landed a typeahead listbox under these inputs, keep its styling untouched.)
4. Update the shell.css comment (one short paragraph: text fields indicate focus by border, the
   ring stays for everything else; cite `P7.S5`).

## Verify — operator runtime first

Dev stack up; Fast Refresh. Headless Chrome over CDP on **`http://127.0.0.1:3000`** (once on
Tailscale), fresh profile, 1440 + 390:
- `/` hero input: click into it → computed `outline-style` is `none`, `border-color` changed vs
  blurred, and no pixel of the input's focus treatment lies under the 조회 button (compare
  rects / screenshot the row at 2× and check the right edge);
- `/stocks` search input: same; `/stocks/{corp_code}` 보유 주식 수 field: same;
  `/auth/login` email/password fields: same; the ask widget's composer textarea: same;
- Tab (keyboard) onto the 조회 button, a nav link, a board tab, a 펼치기 button, a portfolio
  checkbox → the 2px `--focus-ring` outline is still present (computed `outline-width: 2px`);
- keyboard Tab **into** a text field → the border treatment is visible (contrast it against the
  blurred field: compute both border colours and report them);
- `prefers-reduced-motion` irrelevant (no animation added);
- `npm run typecheck && npm run smoke`; isolated production build + `next start -p 3100`, spot-check
  the hero input on `127.0.0.1:3100`, kill it; `python3 scripts/workflow.py validate`. Leave the
  dev stack running.

## Record

`result.md` (commands/outcomes, per-surface measurements, before/after colours, deviations).
`phase.md`: Findings note + a **`frontend`** Doc impact line (focus: text fields indicate focus by
an in-idiom border change with no outline; the 2px `--focus-ring` ring remains the floor for every
other focusable; P7 reading of item 3 — if the operator wants zero indication it is Q2). No
`doc-new-version`, no commits, no state transitions.

## Out of scope

Typeahead (S4), nav (S6), copy (S7), portfolio layout (S8). No token edits in `tokens.css`.

## Reconciled against P7.S4 (landed after this plan was drafted)

- The two search inputs now render inside `components/lookup/SearchRow.tsx`: the `<input>` sits in
  `span.SearchRow.field` (position: relative — the typeahead panel hangs off it) and carries the
  surface's own input class (`Hero.module.css .input` / `Lookup.module.css .input`). `:focus-visible`
  still lands on the `<input>` itself. Do not restructure the row; style the input's focus border
  via the class it already carries / the custom-property hook.
- `Hero.module.css`: `overflow: hidden` moved from `.hero` to `.orbits` in S4 — leave that as is.
- `SearchRow.module.css` (the candidate listbox) is S4's and stays untouched; if the focused input
  border colour should continue as the open panel's top edge, note it but change nothing there.
- With the listbox open, the input's `aria-expanded` state does not change its focus treatment.
