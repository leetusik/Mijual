# Plan: P2.S7 — ② CB collection + backfill to ≥ 2025-06 (quota-gated → gate now open)

_Mode: auto. Plan written inline by the orchestrator._

## Context

② CB 오버행 is near-fully structured (N6: 전환가액/전환비율/전환청구기간/오버행 수량·비율 47/47, refixing floor 36/47 — all API tier; `cvbdIsDecsn` is the only source, `bdRs` is not one, N5). D-1 funds it on one condition: **backfill to ≥ 2025-06**, because 0 of 267 cached 2026-filed CB events open 전환청구 before 2027-01-15 — the 2025-H2 vintage is what makes the 오버행 캘린더 urgent during judging week. The quota gate that guarded this backfill is **open**: 20,000 requests/day confirmed (O-1 closed); keep structural ceilings anyway. **EB is OUT** (D-1). This is the phase's droppable slice — keep it tight, defer sprawl.

Read first: `works/phases/active/P2/phase.md` (whole Findings list — N52–N56 are new since S6), `src/mijual/collect/targets.py` (how ①/③ targets are declared), `src/mijual/gates/` (gates 6–8 exist, unexercised; exposure contract in `exposure.py`), `src/mijual/extract/` (`TASKS['r2_prose']` wired, never run), `src/mijual/scheduler/` (the beat schedule ② must ride).

## Deliverables

1. **② target in the collector**: `전환사채권발행결정` → `cvbdIsDecsn`, `rights_type R2`, riding the existing discover → pair → detail → snapshot path (정정 pairing included — ② corrections are numerous: 373 in 2026). No 증서/매수청구-style correctness filter exists for ②; define ②'s exposure semantics conservatively in `exposure.py`'s R2 arm: exposable iff not suppressed/withdrawn/flag-blocked **and** the countdown-critical API fields are present on the current version (전환가액, 전환청구기간, 오버행 수량·비율). 해외/USD issues (`ovis_*`, e.g. HD한국조선해양) — decide and record a rule (simplest honest: exposable only if the KRW fields parse).
2. **철회 for ②**: extend the withdrawal detector's row-shape to the ② subtype (`전환사채권 발행결정` → `…철회`), measure it over the collected ② corpus, report count (N55 says expect more than you think).
3. **2026 YTD collection**: the standard windows (2026-01-01 → today), both markets. Offline-first against the P1 cache (267 CB events' list/detail rows largely cached), then live top-up.
4. **The backfill**: 2025-06-01 → 2025-12-31 discovery (3-month chunks × 2 markets) + detail + pairing. Budget for the whole slice: **≤ 2,500 OpenDART requests** via `max_requests` (expected ~300–600 per P1's estimate; the ceiling is a guard, not a target). 본문 fetches prioritized: events whose 전환청구기간 opens ≤ 2026-12-31 (the urgency set), then corrections needed for pairing hints.
5. **Prose extraction (fields 6–8) — bounded, deferrable**: run `r2_prose` + the ② 정정 pass only for the **urgency set** (전환청구 개시일 ≤ 2026-12-31, exposable), **cap ≈ 80 LLM calls**; run gates afterward (`mijual.gates run`) — first real exercise of gates 6–8 (floor == API `act_mktprcfl_cvprc_lwtrsprc`; option dates within 발행일~만기일; 해제일 ≥ 발행일). Report per-gate outcomes. If the cap forces triage, structured-only is an acceptable floor for ② (D-1) — extract the soonest-opening events first and state what was left.
6. **Beat registration**: add ② to the scheduled collect targets (the daily pipeline picks it up); the backfill itself is a one-off CLI (`python -m mijual.collect --backfill-cb …` or a scheduler `once --stages …` variant — your call), never a beat entry.
7. **오버행 캘린더 evidence**: from the final corpus, report — total ② events (2025-H2 + 2026), how many open 전환청구 within 30/90/180 days of 2026-09-07 (judging week), the largest 오버행 비율 among them, and densities vs P1's measured 263/7.5mo. This is S8/P3's raw material and the D-1 condition's proof.

## Tests (terse)

② target/report_nm parsing (incl. `[기재정정]`), the R2 exposure arm (present/absent API fields), the ② withdrawal row-shape, backfill window chunking over 2025-06→12. Offline against cached rows; no invented JSON.

## Out of scope

EB entirely; estimation (S8); evalset (S9); any UI. Extraction beyond the capped urgency set. No commits, no state transitions, no doc-new-version. Findings → N-notes from N57; Doc impact one-liners (② semantics + backfill result are durable `data` truth).

## Verification

- `.venv/bin/python -m pytest` green (37 existing + new).
- Collection + backfill run reports: events/versions/snapshots before → after, request spend vs ceiling, pairing outcomes, withdrawal count.
- Gates 6–8 exercised: per-gate pass/fail/not_evaluable counts on the extracted subset.
- The 오버행 캘린더 evidence table (deliverable 7) in result.md.
- Re-run idempotence (0 new rows), `python -m mijual.scheduler once --offline` still green with ② in targets, `python3 scripts/workflow.py validate` passes.
