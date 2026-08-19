# Plan: P2.S8 — "2026 소멸 신주인수권 가치 총액" estimation pipeline

_Mode: auto. Plan written inline by the orchestrator._

## Context

The presentation's opening number and the landing headline: how much warrant value lapsed unexercised in 2026. This is a *reporting* pipeline over the collected corpus, not part of the serving path. Handoff §7 discipline is load-bearing: every input evidence-tagged (`rcept_no`), every estimate `▷`, no inflation, honest gaps recorded as gaps, and the committed numbers regenerable from the final state (N8 — build a `report`/`summary` command, never a scratch script).

Hard constraint on method: **DART is the only data source** (data.md). There is no 증서 시세 feed and no stock-price feed in this repo. So the value proxy must come from the filings themselves — e.g. the filing's own 발행가 산정 data (기준주가, 할인율, 확정발행가 from label `6.`/prose field 5) gives a deterministic theoretical 증서 가치 ≈ max(기준주가 − 확정발행가, 0) × 배정비율-scaled units. Whatever method you choose: implement it in `mijual.calc` (deterministic, unit-tested), state its assumptions explicitly in the report, and tag it `▷`. Do not silently pull any external source.

The missing ingredient is **청약 결과 (실권)**: how many shares went unsubscribed → those warrants lapsed. P1 never surveyed this. The likely source is the **증권발행실적보고서** (pblntf_ty=C) filed after the 청약 completes — survey it cheaply first: discovery via `list.json` for the corps of ① events whose 청약일 has passed, then check whether a structured endpoint exists (probably not) and whether the 본문 carries 청약률/실권 as labeled tables (bodydoc) or prose. Expect and record the honest fallbacks: an event with no 실적보고서 yet → excluded from the realized sum, listed as pending; a 실권주 일반공모 that resold the shares still means the *warrant holders'* unexercised value lapsed — think the semantics through and write them down.

Read first: `works/phases/active/P2/phase.md` (full Findings — N57+ are new), `src/mijual/calc.py` (소멸가치 primitives from S5), `src/mijual/cb/` (S7's calendar/report patterns to mirror), field-matrix §1 (labels 6/8/9/11), `src/mijual/bodydoc/` + `src/mijual/extract/` (if 실적보고서 prose needs reading).

## Deliverables

1. **실적보고서 survey + collection** (`src/mijual/estimate/` — layout yours): discovery + fetch of 증권발행실적보고서 (or equivalent 청약-결과 disclosure) for the completed 2026 ① warrant-bearing events; snapshot them through the normal storage (new `report_subtype`, non-event-key-bearing attachment to the existing events — design it, additive columns fine). Budget: **≤ 500 OpenDART requests**.
2. **청약 결과 reading**: deterministic first (bodydoc labels/tables); if genuinely prose, a bounded LLM pass — **LOW thinking (D-4 as amended in S7), cap ≈ 40 calls**, same quote→span→gate discipline (register the field(s) in the §7-style registry with a named gate, e.g. 청약률 ∈ [0,1+초과청약], 실권주수 ≤ 배정주수 arithmetic).
3. **The estimation** (`mijual.calc` + `python -m mijual.estimate report`): per event — 실권/미행사 warrant units, value proxy with stated assumptions, realized (청약 완료) vs pending split; the headline total with its `▷` tag and a per-event evidence table (corp, rcept_no, 배정기준일, 청약률, 실권, value). Include a sensitivity note (e.g. value under 확정발행가-대비-기준주가 vs any alternative proxy you considered) — one honest paragraph, not a research annex.
4. **Judging-week framing**: alongside the 2026 YTD total, the number(s) P3's landing will actually show — phrase-ready Korean line(s) (product surface is Korean-only) with the calculation trace behind each.
5. **Regenerable report**: `report` command prints the whole table + totals from the DB at 0 requests; the committed result.md quotes only numbers that command reproduces (N8). If you commit a machine-readable summary, regenerate it from the final run.

## Tests (terse)

Calc functions (lapse arithmetic, edge: 청약률 > 1 with 초과청약, zero-실권, missing 확정가), 실적보고서 discovery parsing, one end-to-end offline case from cached/stored data. No invented filings.

## Out of scope

Evalset/accuracy (S9 — but your corpus and any new extractions are its sample frame), UI (P3), EB/②/③ lapse analogs (① only — the headline is about 신주인수권증서). No commits, no state transitions, no doc-new-version. Findings → N-notes continuing from where S7 left off; Doc impact one-liners (the estimation method + its assumptions are durable `data`/`product` truth).

## Verification

- `.venv/bin/python -m pytest` green (44 existing + new).
- `python -m mijual.estimate report` ×2 → identical, 0 requests; headline total + per-event table with evidence rcept_no per row.
- Spend reported: OpenDART requests ≤ 500, LLM calls ≤ 40 (LOW thinking confirmed in the ledger), ▷ cost.
- Honest-gaps section: events excluded and why (no 실적보고서 yet, 철회, 추후결정...).
- `python3 scripts/workflow.py validate` passes.
