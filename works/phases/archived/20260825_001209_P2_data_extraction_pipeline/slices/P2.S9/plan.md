# Plan: P2.S9 — ~100-filing labeled evalset + extraction-accuracy report

_Mode: auto. Plan written inline by the orchestrator. This slice has an operator co-work gate in the middle: prepare everything, then return `needs_operator` — do NOT fabricate labels._

## Context

The judging evidence artifact (handoff §3.6): ~100 hand-labeled filings → per-field precision + gate-block-rate. The corpus is rich now (N79/F1): 50 ① `warrant_confirmed` events (+3 withdrawn), 16 ③, the ② urgency set with prose extractions, 32 실적보고서 with span-verified numbers, 30+ 정정 해석 records, and the known hard cases (LB세미콘 span-unresolved; 추후결정 ×2; 철회 ×3+8; the 제이알글로벌리츠 conflict). Labels come from the operator (O-3); this slice's job is to make that labeling pass as fast and unambiguous as possible, then (after the labels return) compute the report.

Measurement design principle: measure **both error directions** — (a) precision of what the product would show (gate-passed/tbd fields vs human judgment), and (b) the gate's over-blocking price (gate-blocked fields the human marks as actually-correct readings — the ▷ 49.2억 pattern from S8). Also report gate-block-rate per field and the 정정-해석 recall proxy S4 stored (`deterministic_check.uncovered`).

Read first: `works/phases/active/P2/phase.md` (Findings through N83, O-3), `src/mijual/extract/` (stored rows: value, quote, span, gate verdict), `src/mijual/gates/` (verdict vocabulary), `src/mijual/estimate/perf.py` (실적보고서 figures, if sampled).

## Phase A — prepare (this dispatch)

1. **Sampling** (`src/mijual/evalset/` — layout yours): deterministic, seeded, stratified sample of **~100 filings** (filing = one `rcept_no`'s reading, may carry several fields): cover every §7 field with usable n; include ①/②/③, corrections (field 10), 실적보고서 figures, and **all known hard cases** (they are the point, not noise). State the strata and counts. Persist the sample (table or JSON) so the report is regenerable against exactly this sample.
2. **Labeling sheet**: one file the operator edits — CSV (spreadsheet-friendly) at a stable path, one row per (rcept_no, field): corp/name, field key (with a short Korean gloss), **extracted value (normalized)**, **verbatim quote**, ±120 chars of surrounding snapshot context, gate verdict + reason, and two empty columns: `label` (`correct` / `wrong` / `partial`) and `corrected_value` (optional free text). Sort so one filing's rows sit together. Also write `LABELING.md` beside it: 5–10 lines of instructions (what `partial` means, that the quote — not the DB — is the ground the operator judges against the original text, how long it should take, and the one-command re-import). Target ≤ 60–90 minutes of operator time; state your estimate.
3. **Import + report machinery now, not later**: `python -m mijual.evalset import <csv>` (validates labels, refuses unknown values), `python -m mijual.evalset report` (per-field precision with n, gate-block-rate, both error directions, 95% binomial CI or an honest ▷ note if you skip it), both regenerable at 0 requests / 0 calls. Terse tests for sampler determinism + import validation + report math on a tiny fixture.
4. **Return `needs_operator`** with: the sheet's path, the instruction file's path, row count, and your time estimate. Do not guess labels, do not label anything yourself, do not proceed to the report.

## Phase B — after the operator's labels (a later dispatch will say so explicitly)

Import, compute, write the accuracy report into result.md (per-field table + the two error directions + gate-block-rate + the 정정 recall proxy), and a Doc impact line (`data`/`qa` — first measured extraction accuracy). Not this dispatch.

## Budget

0 LLM calls. OpenDART ~0 (stored snapshots; a stray 본문 fetch ≤ 20 requests is acceptable if a sampled filing lacks one).

## Out of scope

Fixing whatever accuracy issues the labels reveal (that's review/fix-slice material), UI, re-extraction experiments. No commits, no state transitions, no doc-new-version.

## Verification (Phase A)

- `pytest` green; sampler ×2 → identical sample; sheet + instructions exist and open cleanly; `import` on a hand-made 3-row test CSV works and the sample report math checks; `workflow.py validate` passes.

## Amendment — operator directive (2026-08-20): Claude self-evaluation replaces the human labeling pass

The operator's verbatim direction: "you self evaluate and self validate. since the extraction done by gemini and you are a claude fable. try by yourself."

Phase B therefore proceeds now with **Claude (the slice executor) as the labeler** instead of the operator:
1. Judge every row of `evalset/sheet.csv` yourself: compare the extracted value against the verbatim quote and context; for any row where ±120 chars is not enough to judge confidently, pull the fuller 본문 from the stored snapshot (bodydoc) before deciding. Use `correct` / `wrong` / `partial` honestly; use `skip` only where even the full document leaves the judgment genuinely undecidable — never to save effort.
2. **0 Gemini calls** — the graded model must not grade itself. The judge is you (Claude). OpenDART ≤ 20 requests only if a sampled snapshot is missing.
3. Fill the sheet, run `python -m mijual.evalset import`, then `report`, and write the Phase B accuracy report into result.md: per-field precision with Wilson CIs (random picks only), the forced hard cases case-by-case, gate-block-rate, and both error directions.
4. **Provenance is load-bearing**: everywhere the numbers appear (result.md, Doc impact, any stored metadata the machinery has for it), the labels are "Claude-judged (cross-model: Claude Fable-orchestrated executor judging Gemini extractions), operator-directed 2026-08-20 — not human ground truth; human spot-check possible via the same sheet". No inflation, no "hand-labeled" phrasing anywhere. Record the intent amendment as an N-note and reflect it in the Doc impact line (`qa`/`decisions`).
