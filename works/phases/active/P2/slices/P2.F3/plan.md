# Plan: P2.F3 — stamp judged_by provenance into labels.json + report (review finding 2)

_Mode: auto. Plan written inline by the orchestrator._

## Context

`evalset/labels.json` is the repo's only non-regenerable artifact, and its provenance ("Claude-judged, cross-model, operator-directed 2026-08-20 — not human ground truth") lives only in prose (LABELING.md footer, result.md, phase notes). The artifact must carry it itself, and the rendered report must print it.

## Work

1. `src/mijual/evalset/labels.py` (+ CLI in `__main__.py`): the import path records a `judged_by` provenance block into `labels.json` — at minimum: judge identity (e.g. `"claude (slice-executor, cross-model vs gemini-3.7-flash)"` for the current round), `basis` (e.g. `"operator directive 2026-08-20 — not human ground truth"`), and the import timestamp it already has. Design: a `--judged-by` CLI flag with validation (refuse an import without provenance, or default it explicitly — your call, but silence must not produce an unstamped artifact). Preserve every existing label byte.
2. **Re-stamp the current round**: regenerate `labels.json` from the already-labeled `sheet.csv` through the new path so the existing 344 labels carry the stamp (labels themselves unchanged — verify by comparing the label maps before/after).
3. `src/mijual/evalset/report.py`: the rendered report prints the provenance line from the artifact (not from a hardcoded string).
4. One terse test: import without provenance behaves as designed; report carries the stamp.

## Out of scope

No relabeling, no sampling changes, no touching sheet evidence columns. No commits/state transitions/doc-new-version. A one-line phase.md N-note recording that the artifact is now self-describing.

## Verification

- `.venv/bin/python -m pytest` green; `python -m mijual.evalset report` prints the provenance; label values identical before/after re-stamp (diff of the label map); `python -m mijual.evalset status` still 344/344; `workflow.py validate` passes. 0 LLM calls, 0 OpenDART requests.
