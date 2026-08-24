# P9.DECOMP2 — cut the build slices from the signed R16 design

## Context

The R16 design landed and is signed (see `phase.md` → `### P9.S2 — R16 design landed`). This second decomposition pass cuts the phase's build slices from the landed spec — **backend first, the design implementation after**, then fidelity verification — per the design-cowork mixed-phase pattern. The binding sources, in order of authority: `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` (§0 copy verbatim, §1 events, §2 element specs, §3 prompt/loop, §4 regression checklist) and `output/result.md`; `phase.md`'s build inventory (items 1–8), S1 transfer report, and S1B survey (esp. P9 input segregation, P10 stable block ids first, P11 tool descriptions, P12 cache measurement). Note the three known-stale lines in build-prompt (§2.7b "5 cards"/meta card, regression item 15's rail) — the signed copy governs.

## What the executor (slice-executor-high) does

1. **Read**: `phase.md` (landed-design section, build inventory, S1/S1B reports), the R16 record (`build-prompt.md` fully, `result.md` §1/§5/§6), and skim `src/mijual/agent/` + `frontend/components/ask/` + `frontend/lib/ask.ts` + `src/mijual/web/ask.py` + `src/mijual/web/conversationstore.py` enough to cut honest boundaries. No product code changes.

2. **Cut the build slices** with `new-slice` — bare folders, `--order` starting after 3 (DECOMP2) and before REVIEW; every slice that writes real code or spans files is `--risk high` (expect all of them; use `low` only if a genuine few-line/docs slice emerges). Decide the exact cut yourself, but honor these constraints from the record and research:
   - **Backend before frontend.** The stream must carry the new vocabulary before the surface draws it.
   - **P10 first among backend work**: stable `block_id` + `persistent` + in-place replacement semantics land in the first backend slice — later structured elements build on it.
   - Backend scope to cover (group into sensibly-sized slices, don't force one-per-item): event vocabulary (`StatusEvent`, `DataBlockEvent`, `CalcBlockEvent`, `TextEvent.unverified`, `TurnEnd` semantics); strip-don't-drop citations replacing the sentence-dropping gate (with the P8 signed-string path and the marker-count `blocked` semantics); calculator tool (named ops over `mijual.calc` + AST-whitelist expr escape hatch, budget-exempt, error-as-guidance); budgets to ~20 rounds (`max_model_calls ≥ max_rounds`, tool calls scaled); `security_check` guard + after-model hard-reject + 「보안」 sixth family (DB whitelist `conversationstore.REFUSAL_FAMILIES`, ops filter mirror) + Q-D logging; prompt rewrite per build-prompt §3 (citations third, never-compute→calculator, refusal block 4 families, FINALLY ceiling-not-floor, static-prefix-first + cached-token field in `client.Usage`/`cost_of` — P12 measure); input segregation (P9, ~10 lines); thinking LOW→MID with docstring rewrite; structured-block storage in `record_turn`/`_Released.absorb`.
   - Frontend scope: `copy.ts` R16 strings; the five element renderers (CalcBlock, DataRow, StatusLine, ToolTrace fold, markers) shared by both views; `/ask` page re-cut (rail retired, start screen, 새 대화, sticky composer); widget empty-state intro; retirements (scope chip, anonymity line, 다시 질문); keyed block reduce in `lib/ask.ts`.
   - **A fidelity/verification slice last**: real-browser walk in the Operator Runtime (dev + production build), RESPECT THE DESIGN, the functional sweep, build-prompt §4's 26 checks — per the design-cowork skill's Verifying section.
   - Set `--depends-on` chains to reflect backend→frontend→fidelity.
3. **Record in `phase.md`** under `## Decomposition`: a `### DECOMP2 (2026-08-25)` subsection — the slice table, rationale, and how the record's sections map to slices. Put **RESPECT THE DESIGN** and the operator-runtime pointer in the notes so every build slice's plan inherits them.
4. Write `result.md`; run `python3 scripts/workflow.py validate`. No commits, no state transitions beyond the decomposition carve-outs, no code, never pre-fill another slice's `plan.md`.

## Verification

- `validate` passes; backlog shows the new slices ordered between DECOMP2 and REVIEW; `phase.md` carries the DECOMP2 breakdown.
