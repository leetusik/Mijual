# Plan — P1.REVIEW: phase review of P1 "Foundation Spike & Confirmations"

## Goal

Validate the whole phase against its objective and intent, judge it, and — only on a **pass** — consolidate the phase's Doc impact notes into new durable doc versions. P1 is NOT in parallel mode, so consolidation happens here.

## Inputs

- `works/phases/active/P1/intent.md` (confirmed intent) and `phase.md` (objective, F1–F25, Doc impact list, Open Questions).
- Slice records: `slices/P1.{DECOMP,S1,S3,S2}/plan.md` + `result.md` (note execution order was DECOMP → S1 → S3 → S2).
- Durable artifacts: `docs/reference/dart/field-matrix.md`, `docs/reference/challenge/submission/` (README + two .hwpx), `slices/P1.S2/recommendation.md`.

## Review procedure

1. **Re-run validation across the phase** (complete ALL validation before judging; return the whole picture in one cycle):
   - `python3 scripts/workflow.py validate`.
   - S1's spike entry points still pass from a clean shell (the 8 commands listed in `P1.S1/result.md` §Validation — they hit the on-disk cache; the key must never appear in output).
   - Spot-check the matrix's evidence discipline: a sample of "structured" claims carry `rcept_no` evidence; estimates are marked `▷`.
   - S3's facts: files exist (templates + README), findings F17–F23 are sourced.
   - S2: `recommendation.md` covers 3 types + package + question set; F25 decision record matches the operator's verbatim answers; the two-pass `result.md` shows the closed gate.
2. **Judge against the objective**: (a) matrix produced incl. ≥5 정정 samples (30 paired — bar exceeded)? (b) MVP rights scope finalized *with the operator* (F25)? (c) daker.ai submission requirements + domain availability reconned (F17–F23)? (d) Constraints honored (no inflation, evidence tags, no LLM calls in P1, key never leaked — re-grep the repo for the key value pattern `crtfc_key=`/the key literal being absent from tracked files)? (e) Hard rules honored (no doc-new-version run by earlier slices; slices own exactly plan.md/result.md + declared artifacts)?
3. **On pass — consolidate docs** (writing only docs, never source):
   - The Doc impact list in `phase.md` has notes against **`data`** (S1), **`operations`** (S3), and **`decisions`** (S3 domain fact sheet + S2 confirmed scope — consolidate both into one new `decisions` version).
   - For each: `python3 scripts/workflow.py doc-new-version --doc <doc> --summary "..." --source P1.REVIEW`, then edit the created `docs/versions/<doc>/vNNNN_*.md` with the consolidated content (pull substance from phase.md findings + the artifacts; keep each doc focused on durable truth, not narrative). Run `python3 scripts/workflow.py rebuild-docs` afterward and confirm `docs/current/*.md` regenerated.
   - Mark the Doc impact list entries as consolidated (a one-line annotation in phase.md is fine).
4. **On non-pass**: STOP before any doc consolidation; return verdict with numbered findings and proposed fix slices (names + kinds), not doing any pass-only work.
5. Write `result.md` (review record: what was validated, judgment rationale, docs created or findings). Append a closing note to `phase.md`.

## Verdict contract

Return `review_verdict: pass | changes_requested | blocked` with rationale; on pass list the created doc versions; always include `explain: not written — run /explain for this phase`. Never run `review-phase` yourself and never commit — the orchestrator records the verdict and commits.
