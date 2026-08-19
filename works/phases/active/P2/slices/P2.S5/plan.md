# Plan: P2.S5 — deterministic validation gates (layer 2) + per-field reason codes

_Mode: auto. Plan written inline by the orchestrator._

## Context

S4 stored 304 extraction rows with deterministically located citation spans and reserved `gate_*` columns on `Extraction`. This slice is the product's trust claim: every extracted field passes its named deterministic gate or is recorded with a reason code and **never exposed**. Zero LLM calls in this slice; zero OpenDART requests should be needed (everything runs off stored snapshots + extractions).

S3/S4 handed over a concrete worklist that is now countdown-critical:
- **철회 detector (O-9, N39):** two exposable ① events (썸에이지 `20260805000454`, 제이알글로벌리츠 `20260205000605`) are withdrawn; the label layer can't see it. Deterministic signal: a `정정사항` row with 항목/정정 전 `유상증자 결정` → 정정 후 `유상증자 철회` (bodydoc already parses these rows). Do NOT use a raw-text `"철회"` keyword test — S4 measured it false-fires on 증권신고서/매수청구 boilerplate. Generalize carefully to ③ (합병 철회) via the same 정정사항-row mechanism if a case exists in the corpus; otherwise implement the row-pattern hook and note ③ untested.
- **`추후결정` rule (O-9, N40):** a third state — verified span, null dates. The gate result must distinguish `passed` / `failed(reason)` / `tbd` (schedule suspended); a `tbd` field is exposable AS "추후결정" but the countdown must never fall back to a superseded date.
- **`warrant_conflict` decision (O-8):** 제이알글로벌리츠 is 철회 anyway, but decide the general rule and record it: a `warrant_conflict` event is **not exposable** until resolved (본문 is the final test; conflicting evidence = no advertised 증서). Same conservative default for `detail_conflict` (3 events) and `hint_split_evidence` (9): flagged identity/detail = not exposable. These are all suppressed-from-exposure, not deleted.
- **1 span-unresolved value** (LB세미콘 `issue_price_formula`) must be blocked by the citation gate with its own reason code.

Read first: `works/phases/active/P2/phase.md` (N34–N40, O-8/O-9), `works/phases/active/P2/slices/P2.S4/result.md` (Extraction model, `is_citable`, span semantics), `docs/reference/dart/field-matrix.md` §7 (the gate column is the spec).

## Deliverables

1. **Gate module** (`src/mijual/gates/`): one named gate per §7 field, implemented as pure functions over (extraction row, label-layer values, API detail-snapshot values):
   - 1 매매기간: valid date order; window between 배정기준일 (label `8.`) and 청약일 (label `11.`).
   - 2 청약 취급처: per-대상자 청약일 consistency vs label `11.`.
   - 3 실권주 처리: enum membership (일반공모 / 주관사 인수 / 미발행 계열).
   - 4 초과청약: 0 < ratio ≤ 1 (+ arithmetic vs 배정주식수 where both present).
   - 5 발행가 산식: consistency vs label `6.` values where present (확정가 ≤ ceiling shape).
   - 6–8 (②): implement the gate functions per §7 (floor == API `act_mktprcfl_cvprc_lwtrsprc`; dates within 발행일~만기일; 해제일 ≥ 발행일) so S7 only runs them — mark unexercised until S7's corpus exists.
   - 9 반대의사: 기한 == API `mgsc_mgop_rcpd_bgd/_edd` (from stored detail snapshots).
   - 10 정정 해석: deterministic 정정사항 rows all parse; the interpretation's changes are subset-consistent (S4 already stores `deterministic_check` — gate on it).
   - **Citation gate on every field**: `span_status='resolved'` required (`span_verified` preferred; the 2 `trimmed` cases pass with a note); `unresolved` → blocked, reason `span_unresolved`.
   - Result per field: `passed | failed(reason_code) | tbd | not_evaluable(reason)` written to the reserved `gate_*` columns (short VARCHAR codes; additive columns via `ensure_columns` if more are needed). Gates re-derive on every run (S3's drop-and-rederive flag pattern); idempotent.
2. **철회 detector + event states**: deterministic scan of 정정사항 rows per event → event-level state (e.g. `withdrawn` review-flag or column). Withdrawn events: not exposable, and their extractions gate to `failed(withdrawn)` or an event-level block — your design, but the state must be visible to P3 as "이 유상증자는 철회되었습니다" (a demo asset, like the 소규모합병 suppression).
3. **Exposure contract**: a single derivation P3 will read — e.g. `Event.exposure` or a query/view: exposable iff not suppressed, not withdrawn, no unresolved identity/warrant/detail conflict flags; per-field: exposable iff gate `passed` (or `tbd` shown as 추후결정). Document it precisely in result.md + a Doc impact line — this is the durable boundary between P2 and P3.
4. **Deterministic calc module** (`src/mijual/calc/` or inside gates): the D-day and 금액-환산 primitives the product will use (D-day from a gated date vs a reference date; lapsed-value shape `주수 × 배정비율 × 증서가치` used by S8) — pure, LLM-free, unit-tested. Small: the high-value functions only.
5. **CLI + run**: `python -m mijual.gates run` (and a `summary`) over the whole extraction corpus; report per-field pass/fail/tbd counts and every reason code with its count; run twice → identical.

## Tests (terse)

LLM-free entirely. A few high-value cases per gate family (pass, fail, boundary), the 철회 detector on the real 썸에이지 rows (from the stored snapshot), 추후결정 → `tbd`, the LB세미콘 unresolved row → blocked, D-day/금액 calc edge cases (KST dates). Reuse stored corpus rows via session fixtures — no invented documents.

## Out of scope

Scheduling (S6), ② corpus (S7 — gates 6–8 land here but run there), estimation (S8), accuracy report (S9), any P3 rendering. No commits, no state transitions, no doc-new-version. Findings → N-notes from N41; durable truth → Doc impact one-liners; close O-8/O-9 in phase.md with the decisions taken.

## Verification

- `.venv/bin/python -m pytest` green (24 existing + new suite).
- `python -m mijual.gates run` ×2 identical; summary shows per-field outcomes incl.: 썸에이지 + 제이알글로벌리츠 `withdrawn`; 경남제약 + 에이전트AI 매매기간 `tbd`; LB세미콘 `issue_price_formula` blocked `span_unresolved`; ③ field-9 equality checks against stored API values reported.
- Exposure contract counts: how many ① / ③ events and fields are exposable today — stated plainly in result.md.
- 0 LLM calls, ~0 OpenDART requests (state any spent). `python3 scripts/workflow.py validate` passes.
