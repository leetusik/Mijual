# Plan: P2.F4 — fix the check_against_items matcher and re-freeze the 정정 recall proxy (review finding 3)

_Mode: auto. Plan written inline by the orchestrator._

## Context

`src/mijual/extract/runner.py:464–475` (`check_against_items`) evaluates its value-fallback arm inside the item-name loop with no one-to-one claim, so identical corrected strings all bind to item 0 (에이전트AI's five `-(추후 확정)` rows). The stored `deterministic_check` therefore understates recall: 85.3% stored vs 88.7% re-matched read-only (N92, confirmed by the review). S9 deliberately did not fix it to avoid desynchronizing code and stored evidence; this slice fixes both sides together.

## Work

1. **Fix the matcher** in `check_against_items`: one-to-one matching between deterministic 정정사항 rows and model changes (each row consumed at most once; the fallback arm cannot multi-bind). Keep the function pure; keep its output shape (`covered`/`uncovered`/`unsupported` counts + ids) so stored records stay comparable.
2. **Recompute the stored evidence deterministically** (0 LLM calls): re-run the check over every stored correction-interpretation record against the stored 정정사항 rows and update each record's `deterministic_check` (this is derived data, recomputable — the model outputs and quotes are untouched). Make it a command (e.g. `python -m mijual.extract recheck`), idempotent, ×2 identical — the relocate pattern.
3. **Re-freeze the number**: report old → new corpus recall proxy (expect ≈ 85.3% → ≈ 88.7%; state the exact figure), confirm `unsupported` stays 0 both ways, and verify the evalset report's recall line (if it reads the stored records) reflects the new figure — rerun `python -m mijual.evalset report` and state what changed (labels untouched).
4. **Tests**: one terse case for the multi-bind trap (two identical corrected strings must consume two distinct rows), plus the recheck idempotence via the existing fixture style.

## Out of scope

Any change to extraction prompts/schemas, any LLM call, relabeling. No commits/state transitions/doc-new-version. N-note + a one-line Doc impact (`qa`/`data` — the recall proxy's corrected value and that the defect was matcher-side, not model-side).

## Verification

- `.venv/bin/python -m pytest` green (57 + new); `recheck` ×2 identical; old→new figures stated with the command that regenerates them; `unsupported` 0 both ways; `workflow.py validate` passes; 0 LLM calls, 0 OpenDART requests.
