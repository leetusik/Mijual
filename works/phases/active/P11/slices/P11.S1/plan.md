# Plan — P11.S1 (Re-cut the ask citation chip onto the R10 popover anatomy)

Kind `implementation`, risk `high`, executed by `slice-executor-high`.

## The defect

A sentence resting on two or more 근거 renders as `…입니다.[1]` ⏎ `[2]` ⏎ `[3]`,
and even a single chip breaks the line after it. Root cause, already established
and confirmed by `P11.DECOMP` — do not re-derive it:
`components/ask/InlineCitation.tsx` mounts its quote panel **unconditionally**
after every chip, and `Ask.module.css` `.quoteWrap` is `display: grid`. A
block-level box inside `<p class={styles.prose}>`'s inline formatting context
splits the paragraph into anonymous block boxes, so every chip forces a break.
`.sentence + .sentence { margin-left: .25em }` assumes inline siblings and is
defeated by the same box.

**Server-side numbering is correct and out of scope.** Do not touch
`agent/citations.py` `_number_for()` or `agent/events.py` `TextEvent.citations`.

## The fix

Re-cut `InlineCitation` onto the anatomy `components/Citation.tsx` +
`Citation.module.css` already ship (the R10 re-cut, `P8.S7`): a **conditionally
mounted, absolutely positioned popover** in place of the always-mounted
`display: grid` panel. Read both files first — they are the pattern, including
`fit()`, the ref-callback clamp, and the document-level close listeners.

Read `works/phases/active/P11/phase.md` in full before starting. Its
`## Decisions` and its `**(from P11.DECOMP, for P11.S1)**` notes are binding; the
substance is not repeated here. Consume that note block when you are done (drop
it from `## Notes for later slices`) — the detail lives in your `result.md`.

The two placements, as `P11.DECOMP` decided them:

- **프로즈** — the wrap becomes `position: relative; display: inline-block`, as
  `Citation.module.css` `.wrap`; the popover opens under the chip.
- **행** (데이터 행 값 · 계산 입력 — one code path, `DataRowLine`) —
  `.citationRow { display: contents }` **stays**; `.row` (`Blocks.module.css`,
  which currently has no `position`) takes `position: relative` and the popover
  anchors to it, opening under the row across the block. An absolutely positioned
  box sizes no grid track, so the value-column collapse R16 measured becomes
  structurally impossible. `.quoteWrap` / `.quoteClip` / `.citationRow >
  .quoteWrap` retire with the panel they placed, and `inert` retires with them.

## Three decisions this slice must make and record

1. **The popover's ground must be opaque, and `--surface-inset` is not.** R16
   signed the 인용 블록 as `--surface-inset` + a 2px `--live` left edge with a
   180px quote cap. That was an *in-flow inset panel* with nothing behind it. As
   an **overlay** it sits on top of the prose, and in the dark theme
   `--surface-inset` is `rgba(255,255,255,.08)` (`public/foundations/tokens.css`
   L51) — the sentence would read straight through the quote. This is exactly why
   `Citation.module.css` uses the record's own opaque `#0e1a15` and says so in a
   comment. Decide the ground deliberately: the expectation is the opaque
   surface, keeping the 2px `--live` left edge and the **180px** cap (the ask
   surface's number, not the primitive's 200px) so what R16 signed about the
   quote block survives everything except the one property the overlay makes
   impossible. Record it as a **deliberate, documented deviation** in `result.md`
   and as a `## Decisions` line in `phase.md`, and note it for the gate
   walkthrough — the operator should be told the ground changed and why.
2. **Which closes the chip gets.** 닫기 = **칩 재탭** is R6-4-signed and must
   survive. `Citation.tsx` additionally offers a `×`, an outside click and
   Esc-with-focus-return. Adopt them deliberately or not at all — do not end up
   with half a close model. An overlay that cannot be dismissed by clicking away
   is worse than the panel it replaces, so outside-click and Esc are strongly
   indicated; the `×` is a judgment call against the chip's small scale.
3. **Vertical clipping in the widget.** The widget thread is `overflow-y: auto`
   at 440×620, so a popover opened on the **last** answer can be clipped by the
   scroll container. `Citation.tsx`'s `fit()` clamps **horizontally only**.
   Check it in the browser; if it clips, extend the clamp to flip the popover
   above the chip when there is no room below, rather than leaving evidence
   unreadable. Same check on the `/ask` page near the viewport bottom.

## Hold everything else R16 signed

Chip: mono 10px, 1px `rgba(95,208,165,.4)` border, hover `--live` border, open
`--live-tint` fill, and the chip after the sentence's **period**. ≤767 = 44px
targets (`Citation.module.css`'s media block is the shipped pattern). In a row,
the chip keeps the fixed third column and never scrolls away with the value.

**Every element in the component must stay phrasing content** — it sits inside
`<p class=prose>`, and a `<div>` is reparented by the HTML parser and breaks
hydration. `Citation.tsx` observes the same rule; follow it exactly.

Update `InlineCitation.tsx`'s doc comment: it currently describes the grid height
animation, the `inert` collapse and 「블록형과 스타일 공유」 as present tense. After
this slice the sharing is *closer*, not looser — say what the anatomy now is, why
the ground is opaque, and keep the R6-4 / R16 §2.6 citations. Same for the
retired rules' comments in `Ask.module.css`.

## Verify — in the operator's runtime, through a real browser

`docs/current/operations.md` `## Operator Runtime`: `make stack-up`,
`http://127.0.0.1:3010`, Chrome desktop **plus** a mobile viewport (≤767, check
390), and again in the production build (`cd frontend && npm run build && npm run
start`) since hydration and StrictMode are exactly what this change could break.
Prefer **Aside** (`aside mcp`); name the instrument you actually used in
`result.md` and never claim a run you did not make.

The matrix: **3 placements** (프로즈 · 데이터 행 값 · 계산 입력) × **`/ask` page +
widget** × **desktop + ≤767**. The headline case is a sentence resting on **two or
more** 근거 — `conversation_turn` turns **28, 17 and 103** each carry 5 quotes
across 4 sentences, so reproduce with one of those rather than hoping a fresh
question produces one. Confirm, explicitly:

- a sentence with 2–3 chips renders on **one line**, chips side by side after the
  period, no break before or after;
- `.sentence + .sentence`'s `.25em` gap works again (it is part of the defect);
- opening a chip **moves nothing** — no row shifts, no reflow of the paragraph;
- a data row's value column does not collapse when its chip opens (the R16
  measurement that made the old placement necessary);
- the API-tier chip (no `quote`) still opens to the solo `DART 원문 … ↗` link;
- the DART link of a **closed** popover is unreachable (it is unmounted — that is
  what `inert` was buying);
- keyboard: focus the chip, open, Esc returns focus to it; 44px targets at ≤767.

Also run the frontend's own checks (lint / typecheck / build — whatever
`package.json` provides) before finishing.

## Scope

`frontend/components/ask/InlineCitation.tsx`, `Ask.module.css`,
`Blocks.module.css`, and `Answer.tsx` / `DataBlock.tsx` only if the re-cut
genuinely requires it (it should not — the component's props are unchanged). No
backend. No card work — that is `P11.S2`. If you find you need anything outside
this scope, say so in `result.md` rather than widening silently.

## Notebook and result

Edit `phase.md` under its budget (200 lines / 16 KB — it is at 157/12.6 KB, so
compress as you add): replace superseded `## Decisions` lines rather than stacking
them, append your `## Doc impact` line (the `frontend.md` chip-anatomy note is
already foreseen there — refine it to what you actually shipped, including the
opaque ground), drop the note block you consumed, add any note `P11.S2` or
`P11.REVIEW` needs, and rewrite `## Now` last. Do **not** run `doc-new-version`.

Write `result.md` **verdict block first**, with your validation commands and their
outcomes, the instrument you used, the deviations (decision 1 above is one), and
what you rejected. Return the structured verdict with a one-line `summary`.
