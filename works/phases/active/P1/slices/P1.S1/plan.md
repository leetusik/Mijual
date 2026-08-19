# Plan — P1.S1: DART OpenAPI spike & field matrix

## Goal

Produce the phase's load-bearing artifact: the **event-type × field × {structured API / LLM extraction needed} matrix** for the 3 MVP rights types, grounded in real 2026 filings, including ≥5 paired 기재정정 samples and the resulting diff-target field list. This matrix fixes the extraction-target list for the AI reading layer (handoff §3.6 layer 1) and is the main input to the P1.S2 scope decision and P2's pipeline design.

## Context (read first)

- `works/phases/active/P1/phase.md` — especially **Findings F1–F7** (live-probe intel: endpoints exist; `piicDecsn` is thin — 19 constant fields, no 배정기준일/발행가/청약일/증서 매매기간; `estkRs` carries much of what `piicDecsn` lacks incl. `asstd` and 인수인 `actnmn`; CB/EB/합병 are structurally rich; 정정 pairing is unsolved; 3-month window cap without `corp_code`), **Open Questions Q1–Q3**, and **Constraints** (binding).
- `docs/reference/challenge/00_HANDOFF.md` §3.6 (the service-critical field list) and §6 item 1.
- API key: parse repo-root `.env` (`DART_API_KEY`) in-process. Never echo/print/log the key or keyed URLs; never write it into artifacts.

## Work

1. **Spike scripts** under `scripts/spike/` (throwaway-grade, 1–3 small Python files, stdlib + `urllib`/`requests` only; no framework, no package scaffolding). Suggested shape: a tiny DART client helper + a collector that pulls samples per event type + a probe for 정정 pairing. Cache raw JSON responses under `scripts/spike/samples/` (key stripped from any stored URL) so runs are re-checkable.
2. **Systematic field survey per rights type** — for each, list every service-relevant field and classify {structured (endpoint + field id, with a real `rcept_no` as evidence) / LLM-needed (본문 only)}:
   - **① 유증 신주인수권**: `piicDecsn` + `estkRs`. Answer **Q1**: does `estkRs.asstd` populate for **주주배정** filings (find real 주주배정 samples — 3-month windows, page through; use `corp_code` for longer history where helpful)? Does *any* structured field expose 신주인수권증서 상장·매매기간, 실권주 처리, 초과청약? Expected LLM-heavy; prove it rather than assume it.
   - **② CB·EB 오버행**: `cvbdIsDecsn`, `exbdIsDecsn` (+ `bdRs` where a 증권신고서 exists). Verify 전환가액/청구기간/리픽싱 coverage; identify what remains 본문-only (리픽싱 세부 조건, 콜·풋 세부, 보호예수 해제 스케줄).
   - **③ 매수청구권**: `cmpMgDecsn` (+ `mgRs`). Verify 예정가격/행사기간/기준일 coverage; expected 본문-only: 반대의사 통지 방법·절차.
3. **정정공시 diff targets** — answer **Q2**: implement a pairing heuristic (same `corp_code` + same 보고서 subtype + nearest earlier `rcept_dt`, original flagged `rm="정"`; check whether the 정정 document header names the superseded `rcept_no`). Pair **≥5 `[기재정정]` 주요사항보고서** samples across the 3 event types (skip `[첨부정정]`), diff their structured records old-vs-new, and list **which fields actually changed** (dates? price? ratio?) → the diff-target field list.
4. **본문 feasibility check** — answer **Q3**: fetch the `document` API ZIP for 2–3 filings, confirm the XML is parseable enough to feed schema-based LLM extraction (encoding, structure, where the §3.6 fields visually live), note an HTML-viewer fallback if not.
5. **Durable artifact**: write the matrix to `docs/reference/dart/field-matrix.md` — per event type: field, service meaning, source {endpoint.field | LLM(본문 section)}, evidence `rcept_no`, notes; plus sections for the 정정 pairing method + diff-target list, `document` parseability verdict, and API constraints (F6 + anything new). Evidence-tagged throughout; estimates marked `▷`; honest gaps stated as gaps.
6. **Wrap up**: append Findings (answers to Q1–Q3, surprises) and a one-line **Doc impact** note against `data` to `phase.md`; write `result.md` with a crisp summary + per-rights-type feasibility signal for S2 (which types are mostly deterministic vs LLM-heavy).

## Boundaries

- Do NOT build the P2 pipeline, the 총액 estimation, or the labeled evalset. No DB, no scheduler, no LLM calls at all in this slice — the matrix says where LLM extraction *will be needed*, it does not perform it.
- Sample volume: enough to be honest (a handful per event type, ≥5 정정 pairs), not exhaustive. Record counts truthfully.
- If something sprawls, note it as a candidate deferred job in `result.md` instead of absorbing it.

## Validation

- Spike scripts run end-to-end from a clean shell (`python3 scripts/spike/<...>.py`) using `.env`, without printing the key.
- `docs/reference/dart/field-matrix.md` exists, covers all 3 rights types + 정정 section, and every "structured" claim carries an evidence `rcept_no`.
- ≥5 기재정정 pairs actually paired and diffed (list them).
- `python3 scripts/workflow.py validate` passes.
