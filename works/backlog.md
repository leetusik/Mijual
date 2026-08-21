# Backlog

> Generated dashboard. Do not put detailed task context here; edit phase/slice/deferred folders instead.
> Status box: `[x]` done · `[~]` pending — waiting on operator · `[r]` ready — plan approved, awaiting execution · `[ ]` open/in progress.

## Pointer

- Current phase: `P5`
- Current slice: `P5.S8`
- Next slice: `P5.S9`
- Waiting on operator: `none`
- Open deferred jobs: `2`
- Rebuilt at: `2026-08-22T03:29:31+09:00`

## Active Phases

| Phase | Status | Review | Name | Current Slice | Path |
|---|---|---|---|---|---|
| [x] `P1` | `done` | `pass` | Foundation Spike & Confirmations | `none` | `works/phases/active/P1` |
| [x] `P2` | `done` | `pass` | Data & Extraction Pipeline | `none` | `works/phases/active/P2` |
| [x] `P3` | `done` | `pass` | Mijual Web Service (design only) | `none` | `works/phases/active/P3` |
| [ ] `P5` | `planned` | `pending` | Apply — build the signed design | `P5.S8` | `works/phases/active/P5` |
| [ ] `P6` | `planned` | `pending` | Apply — AI 질문 agent | `P6.DECOMP` | `works/phases/active/P6` |
| [ ] `P4` | `planned` | `pending` | Ship & Submit | `P4.DECOMP` | `works/phases/active/P4` |

## Phase P1: Foundation Spike & Confirmations

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [x] `P1.DECOMP` | `done` | decompose phase | `decomposition` | `works/phases/active/P1/slices/P1.DECOMP` |
| [x] `P1.S1` | `done` | DART OpenAPI spike & field matrix (event-type x field x structured/LLM) | `spike` | `works/phases/active/P1/slices/P1.S1` |
| [x] `P1.S3` | `done` | Recon: daker.ai submission requirements + mijual domain availability | `research` | `works/phases/active/P1/slices/P1.S3` |
| [x] `P1.S2` | `done` | MVP rights-scope recommendation & operator confirmation | `decision` | `works/phases/active/P1/slices/P1.S2` |
| [x] `P1.REVIEW` | `done` | phase review | `review` | `works/phases/active/P1/slices/P1.REVIEW` |

## Phase P2: Data & Extraction Pipeline

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [x] `P2.DECOMP` | `done` | decompose phase | `decomposition` | `works/phases/active/P2/slices/P2.DECOMP` |
| [x] `P2.S1` | `done` | Package scaffold, storage schema (event/version/snapshot) & DART client port | `feature` | `works/phases/active/P2/slices/P2.S1` |
| [x] `P2.S2` | `done` | Collector: 유증(①) + 매수청구(③) new filings and 정정 discovery | `feature` | `works/phases/active/P2/slices/P2.S2` |
| [x] `P2.S3` | `done` | 본문 XML parse layer: labeled rows, CORRECTION block, citation spans | `feature` | `works/phases/active/P2/slices/P2.S3` |
| [x] `P2.S4` | `done` | LLM extraction (layer 1): Gemini schema extraction for the 10 fields + 정정 re-extraction | `feature` | `works/phases/active/P2/slices/P2.S4` |
| [x] `P2.S5` | `done` | Deterministic validation gates (layer 2) + per-field reason codes | `feature` | `works/phases/active/P2/slices/P2.S5` |
| [x] `P2.S6` | `done` | Celery beat scheduling: collect / extract / gate tasks | `feature` | `works/phases/active/P2/slices/P2.S6` |
| [x] `P2.S7` | `done` | ② CB collection + backfill to 2025-06 (quota-gated) | `feature` | `works/phases/active/P2/slices/P2.S7` |
| [x] `P2.S8` | `done` | 2026 소멸 신주인수권 가치 총액 estimation pipeline | `analysis` | `works/phases/active/P2/slices/P2.S8` |
| [x] `P2.F1` | `done` | Full-2026 discovery re-run + reconcile (run gap + pifricDecsn pickup) | `fix` | `works/phases/active/P2/slices/P2.F1` |
| [x] `P2.S9` | `done` | ~100-filing labeled evalset + extraction-accuracy report | `eval` | `works/phases/active/P2/slices/P2.S9` |
| [x] `P2.F2` | `done` | Reword evalset docstrings judge-neutrally (provenance honesty) | `fix` | `works/phases/active/P2/slices/P2.F2` |
| [x] `P2.F3` | `done` | Stamp judged_by provenance into labels.json + report | `fix` | `works/phases/active/P2/slices/P2.F3` |
| [x] `P2.F4` | `done` | Fix check_against_items matcher and re-freeze the 정정 recall proxy | `fix` | `works/phases/active/P2/slices/P2.F4` |
| [x] `P2.REVIEW` | `done` | phase review | `review` | `works/phases/active/P2/slices/P2.REVIEW` |

## Phase P3: Mijual Web Service (design only)

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [x] `P3.DECOMP` | `done` | decompose phase | `decomposition` | `works/phases/active/P3/slices/P3.DECOMP` |
| [x] `P3.S1` | `done` | Design grounding pack: dated real content export for the design sessions | `feature` | `works/phases/active/P3/slices/P3.S1` |
| [x] `P3.S2` | `done` | Design R1: brand identity + foundations (logo lockup, palette, type, tokens) | `co-work` | `works/phases/active/P3/slices/P3.S2` |
| [x] `P3.S3` | `done` | Design R2: landing 관제 현황판 + global chrome + vocky feedback touchpoint | `co-work` | `works/phases/active/P3/slices/P3.S3` |
| [x] `P3.S4` | `done` | Design R3: event detail for ①②③ + citation display + 철회/추후결정/불일치 states | `co-work` | `works/phases/active/P3/slices/P3.S4` |
| [x] `P3.S5` | `done` | Design R4: 종목 검색 + 보유량 슬라이더 + 놓친 돈 조회기 (anonymous 금액 환산) | `co-work` | `works/phases/active/P3/slices/P3.S5` |
| [x] `P3.S6` | `done` | Design R5: 개인화 2층 — auth surfaces + portfolio 등록 + D-day list + sample load | `co-work` | `works/phases/active/P3/slices/P3.S6` |
| [x] `P3.S7` | `done` | Design R6: grounded 해설 panel (citation-forced, SSE streaming states) | `co-work` | `works/phases/active/P3/slices/P3.S7` |
| [x] `P3.S8` | `done` | Design R7: admin panel (operator-facing pipeline, gate queue, accuracy, quota) | `co-work` | `works/phases/active/P3/slices/P3.S8` |
| [x] `P3.REVIEW` | `done` | phase review | `review` | `works/phases/active/P3/slices/P3.REVIEW` |

## Phase P5: Apply — build the signed design

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [x] `P5.DECOMP` | `done` | decompose phase | `decomposition` | `works/phases/active/P5/slices/P5.DECOMP` |
| [x] `P5.S1` | `done` | FastAPI service skeleton + read-layer foundations | `implementation` | `works/phases/active/P5/slices/P5.S1` |
| [x] `P5.S2` | `done` | Presentation contract: countdowns, 환산 chain, lapse results, citations, 「추정」 tagging | `implementation` | `works/phases/active/P5/slices/P5.S2` |
| [x] `P5.S3` | `done` | Board, summary and event-detail read endpoints (+ CorrectionStory version rail) | `implementation` | `works/phases/active/P5/slices/P5.S3` |
| [x] `P5.S4` | `done` | 내 종목 조회 endpoints: stock resolution, live rights, 2026 놓친 돈 breakdown | `implementation` | `works/phases/active/P5/slices/P5.S4` |
| [x] `P5.S5` | `done` | Identity-scope the API-backed gates: re-pair 정정 filings joined to the wrong 사채 | `implementation` | `works/phases/active/P5/slices/P5.S5` |
| [x] `P5.S6` | `done` | ③ 매수예정가 backing (D-15): extraction target, gate, exposure | `implementation` | `works/phases/active/P5/slices/P5.S6` |
| [x] `P5.S20` | `done` | Multi-span citations for multi-addend 실적보고서 figures | `implementation` | `works/phases/active/P5/slices/P5.S20` |
| [x] `P5.S7` | `done` | Reader auth backend: accounts, password hashing, sessions, reset flow | `implementation` | `works/phases/active/P5/slices/P5.S7` |
| [ ] `P5.S8` | `todo` | Portfolio backend: holdings, D-day list, 챙긴 돈, 알림 preferences, sample portfolio | `implementation` | `works/phases/active/P5/slices/P5.S8` |
| [ ] `P5.S9` | `todo` | Admin backend: operator door + read-only ops endpoints + pipeline run log | `implementation` | `works/phases/active/P5/slices/P5.S9` |
| [ ] `P5.S10` | `todo` | Next.js foundation: scaffold, tokens/fonts/assets, cosmos shell, trust primitives, API client | `implementation` | `works/phases/active/P5/slices/P5.S10` |
| [ ] `P5.S11` | `todo` | Global chrome: nav, footer, mobile sheet, vocky triggers | `implementation` | `works/phases/active/P5/slices/P5.S11` |
| [ ] `P5.S12` | `todo` | Landing 관제 현황판: hero, 회고 anchor panels, countdown, 소멸주의보, board | `implementation` | `works/phases/active/P5/slices/P5.S12` |
| [ ] `P5.S13` | `todo` | Event detail ①②③: header, 환산 블록, field rows, trust states, CorrectionStory | `implementation` | `works/phases/active/P5/slices/P5.S13` |
| [ ] `P5.S14` | `todo` | 내 종목 조회 surface: search, 보유량, 진행 중인 권리, 놓친 돈 breakdown, empty states | `implementation` | `works/phases/active/P5/slices/P5.S14` |
| [ ] `P5.S15` | `todo` | Auth surfaces + conversion offers + sample entry | `implementation` | `works/phases/active/P5/slices/P5.S15` |
| [ ] `P5.S16` | `todo` | 내 포트폴리오: holdings, D-day list, 챙긴 돈, 알림 설정, sample mode, account menu | `implementation` | `works/phases/active/P5/slices/P5.S16` |
| [ ] `P5.S17` | `todo` | 운영 관제 admin panel: door + six sections | `implementation` | `works/phases/active/P5/slices/P5.S17` |
| [ ] `P5.S18` | `todo` | vocky integration: observation API shape decision + admin vocky view | `implementation` | `works/phases/active/P5/slices/P5.S18` |
| [ ] `P5.S19` | `todo` | Design-fidelity verification in a real browser (RESPECT THE DESIGN) | `implementation` | `works/phases/active/P5/slices/P5.S19` |
| [ ] `P5.REVIEW` | `todo` | phase review | `review` | `works/phases/active/P5/slices/P5.REVIEW` |

## Phase P6: Apply — AI 질문 agent

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [ ] `P6.DECOMP` | `todo` | decompose phase | `decomposition` | `works/phases/active/P6/slices/P6.DECOMP` |
| [ ] `P6.REVIEW` | `todo` | phase review | `review` | `works/phases/active/P6/slices/P6.REVIEW` |

## Phase P4: Ship & Submit

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [ ] `P4.DECOMP` | `todo` | decompose phase | `decomposition` | `works/phases/active/P4/slices/P4.DECOMP` |
| [ ] `P4.REVIEW` | `todo` | phase review | `review` | `works/phases/active/P4/slices/P4.REVIEW` |
