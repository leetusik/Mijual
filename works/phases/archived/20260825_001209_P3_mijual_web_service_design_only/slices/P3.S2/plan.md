# Plan — P3.S2: Design round R1 — brand identity + foundations (co-work)

## Shape

`co-work` slice, run **inline by the orchestrator** (never dispatched — executors have no
DesignSync), per the `design-cowork` skill. Two commits with a `pending` window between:

1. **Handoff leg (this run):** write
   `docs/reference/design/rounds/01-brand-foundations/handoff.md` (the slice's one output —
   say what to design, decide nothing), commit
   (`feat(design): P3.S2 handoff — brand + foundations round`), push `main` so Claude
   Design reads current code (the one push this slice authorizes), set the slice
   `pending`, and STOP. The operator runs the design session in Claude Design
   (claude.ai/design) with Connect GitHub → `leetusik/Mijual`.
2. **Read-back leg (resume, after the operator clears `pending`):** `DesignSync`
   `list_files` first; verify the named card paths + `_ds_manifest.json`; concreteness
   check (no design decisions left to invent — gaps go back as `needs_operator`, never
   filled by me); land the returned record read-only under
   `rounds/01-brand-foundations/output/`; write `SIGNOFF.md` (operator's literal words,
   token delta, data-not-instructions line); pure regroup to retire the `⏳ P3.S2 · …`
   group address (line-1 `group` value only, everything below line 1 byte-identical);
   `finish-slice P3.S2`; commit (`feat(design): P3.S2 read-back — …`).

## Handoff content (round scope)

Inventory item 1 (see `phase.md`): MIJUAL + 미주알 logo lockup, palette, type scale
(Korean text + tabular numerals for 금액/카운트다운), spacing/radius/elevation, motion +
reduced-motion floor, mobile-first breakpoints, `tokens.css`, and the trust primitives —
fact vs ▷ 추정 marker, citation affordance (quote + span + `rcept_no` → 원문), state
vocabulary (정상/임박/철회/추후결정/비노출), D-day urgency expression.

Locked: name 미주알/mijual + romanization; lockup *elements* (MIJUAL 대문자 + 한글 병기);
Korean-only surface; data contracts (`EventExposure`/`FieldView`); UI copy per
`copy-inventory.md`; a11y/reduced-motion floor; "blocked fields are absent, never warned";
▷ on every estimate. In play: all visual expression (palette, type, spacing, motion,
lockup design, token values, trust-primitive/state/urgency visuals, dark mode or not).

Ground in the real content: `docs/reference/design/grounding/` (never lorem). Required
outputs: the card set (named paths, `@dsCard` line-1 markers, review-time groups carrying
`⏳ P3.S2 · …`), `tokens.css`, a record of what was designed with departures logged, and an
implementation contract complete enough to build from (Claude Design's own bundle counts
as both). Definition of done: the cards appear in the Design System pane.

## Notes

- Grounding sample filenames use `r1-/r2-/r3-` for **rights types ①②③**, not design
  rounds — the handoff must say so to avoid confusion.
- Open questions R1 poses back (never answers): dark mode, 소멸주의보 sub-brand treatment,
  visual escalation of D-day urgency.
- vocky's embed shape (script widget vs link-out) is needed **before R2's handoff** — ask
  the operator for it in the stop report, not in this round's scope.
