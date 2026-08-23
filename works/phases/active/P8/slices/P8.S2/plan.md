# Plan — P8.S2: R8 design polish — surface 1: foundations/tokens + global chrome

Orchestrator plan, written inline (auto mode) on 2026-08-23. Kind `co-work`, risk `high`. **Run inline by the orchestrator on the main thread — never dispatched** (design-cowork: DesignSync is main-thread only). No implementation code is written in this slice.

## Surface (from `phase.md` § Surface 1)

Tokens/type (`frontend/public/foundations/tokens.css`, `fonts.css`, `app/shell.css`, `app/layout.tsx`), the chrome (`frontend/components/chrome/*` — `SiteChrome`, `Nav`, `Footer`, `AccountSlot`, `Wordmark`, `VockyTrigger`, `VockyScript`, `copy.ts`), and the shared trust primitives (`Citation`, `DDay`, `StateBadge`, `RightsChip`, `CraftPanel`, `EstimateMarker`, `LapseAlert` + `lib/{copy,format,motion,routes}.ts`). Designed by R1 and R2/R2.1; overrides in force: P7 nav 3→2 slots, P7 focus split, P6 launcher in the persistent layout. Widest blast radius in the phase (shared-component table in `phase.md`).

## Steps

1. **Walk first** — in the operator's runtime (`## Operator Runtime`: dev stack already up, `http://127.0.0.1:3000` in Chrome desktop, plus a mobile viewport; the tailnet URL when access-path behaviour could differ). Cover the polish inventory item 1: tokens as rendered under `.cosmos`, Pretendard prose / Plex Mono numerals, the 52px bar, wordmark, two nav slots, 로그인 / account slot (signed-out and signed-in), the `[의견]` triggers (known dead — Operator Questions Q2), the ≤480 top bar + sheet menu, footer provenance / gate-cost / disclaimer sentences, both halves of the P7 focus split on every focusable, reduced-motion floor, the default 404 page (Q3), favicon 404 (S1 finding), and the shared primitives as they render on the pages that carry them. Control by control; type-and-wait where live; note everything dead, confusing, off, or inconsistent — URLs + screenshots, not adjectives. Do not judge against the record; judge as a first-time user.
2. **Ask** — set the slice `pending` and report the findings list together with the inherited P7 decisions that map to this surface (P7 Q1, Q2, Q9, Q10, Q11, Q6 #1/#4, Q7 ③; P8 Q1–Q4 where they touch chrome) and ask the operator: *what's wrong, and how should each be fixed?* STOP the loop.
3. **Handoff** (resume, after the operator answers) — write `docs/reference/design/rounds/08-foundations-chrome/handoff.md` per design-cowork: product context, scope checklist (the operator's answers as direction + labelled REFERENCE data, polish only, no new features), locked vs. in-play (copy in play only if the operator says so — name and date it), where to look (real paths above, `SIGNOFF.md` precedence, the shared-component table), the strict required-output manifest (card set with `@dsCard` markers under `⏳ P8.S2 · <group>` addresses, card paths named, a new `tokens.css` only if tokens move, the record + the implementation contract / Claude Design's own handoff bundle), open questions posed back, definition of done. Commit `feat(design): P8.S2 handoff — …`, set `pending`, STOP.
4. **Read back** (resume) — DesignSync `list_files` against the named card paths; concreteness check; land as-is under `rounds/08-foundations-chrome/output/`; spec into `phase.md`; SIGNOFF entry (operator's literal words, supersedes, token delta); regroup to retire the round address; commit `feat(design): P8.S2 read-back — …`; `finish-slice`.

## Don't

No visual decisions of my own, no code, no edits to the record, no dispatching, no `plan.md` for `P8.S3` (written only after SIGNOFF from the landed `build-prompt.md`).
