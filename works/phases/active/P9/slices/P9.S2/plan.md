# P9.S2 — design round 1: unified assistant & rich chat surface (R16)

## Context

The co-work design round of P9 (see `phase.md` and `intent.md`). Everything this phase changes that a reader can see or read goes through this round: the superseded signed copy (R6's five refusal families, the never-compute rule, `AGENT_INTRO_KO`, the 검증 line in the `/ask` rail), the unified conversational register, and the phase's headline — the structured display elements (data rows, calculation results, status signals) the thread will render. The evidence base is landed: `phase.md` carries S1's changple5 transfer report (design inputs 1–9) and S1B's best-practice survey (inputs 10–18, proposals P1–P16, per-item verdicts).

Run **inline on the main thread** per the `design-cowork` skill — never dispatched, never writing implementation code. Mode is auto, but this slice's own gate is unconditional: it ends `pending` for the operator's Claude Design session.

## Steps (this session, before the gate)

1. Write `docs/reference/design/rounds/16-smart-assistant/handoff.md` — one handoff for the round, built from the R14 handoff's proven shape: product context; scope checklist (the 18 design inputs + the copy to supersede + the required elements); locked vs in-play (copy is **in play this round — the dated exception**; `foundations/tokens.css` stays frozen per R8 unless the session signs a delta; data contracts, loop structure, a11y floor locked); where to look (real repo paths — the design project reads this repo via Connect GitHub, so `phase.md`'s S1/S1B sections are readable in-repo); the required card set under the round address `⏳ P9.S2 · …` groups with exact paths; the required outputs (`output/result.md` with every decision and signed Korean string, `output/build-prompt.md` as the binding implementation contract); operator questions posed back (the design-gating subset of `## Operator Questions`); hard rules restated with the explicit list of signed decisions this round is empowered to supersede.
2. Commit: `feat(design): P9.S2 handoff — round 16 smart assistant & rich chat surface opened`.
3. Push so Claude Design reads current code — the one push the design slice authorizes.
4. `set-slice-status P9.S2 pending`, report the operator's to-do, STOP the loop.

## On resume (after the operator's design session)

Read back with `DesignSync` (main-thread only): `list_files` → verify the named card paths and `_ds_manifest.json`; concreteness check ("no design decisions left to invent"); land the returned record AS-IS under `rounds/16-smart-assistant/output/`; write the SIGNOFF entry (operator's literal words, supersessions, token delta); pure regroup to retire the round address; fold the signed decisions into `phase.md` for `P9.DECOMP2`; `finish-slice P9.S2`; commit `feat(design): P9.S2 read-back — …`; continue the loop into `P9.DECOMP2`.

## Constraints

- No implementation code. No invented visual decisions or Korean copy — the handoff poses questions; Claude Design + the operator answer them.
- The returned record is read-only; gaps go back as `needs_operator`, never filled by me.
- `validate` before finishing any state step.
