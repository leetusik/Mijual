# Backlog

> Generated dashboard. Do not put detailed task context here; edit phase/slice/deferred folders instead.
> Status box: `[x]` done · `[~]` pending — waiting on operator · `[r]` ready — plan approved, awaiting execution · `[ ]` open/in progress.

## Pointer

- Current phase: `P8`
- Current slice: `P8.REVIEW`
- Next slice: `none`
- Waiting on operator: `none`
- Open deferred jobs: `4`
- Rebuilt at: `2026-08-24T23:15:16+09:00`

## Active Phases

| Phase | Status | Review | Name | Current Slice | Path |
|---|---|---|---|---|---|
| [x] `P1` | `done` | `pass` | Foundation Spike & Confirmations | `none` | `works/phases/active/P1` |
| [x] `P2` | `done` | `pass` | Data & Extraction Pipeline | `none` | `works/phases/active/P2` |
| [x] `P3` | `done` | `pass` | Mijual Web Service (design only) | `none` | `works/phases/active/P3` |
| [x] `P5` | `done` | `pass` | Apply — build the signed design | `none` | `works/phases/active/P5` |
| [x] `P7` | `done` | `pass` | 실서비스 정상화 fix pass | `none` | `works/phases/active/P7` |
| [x] `P6` | `done` | `pass` | Apply — AI 질문 agent | `none` | `works/phases/active/P6` |
| [ ] `P8` | `planned` | `pending` | Design polish pass — audit & polish every surface | `P8.REVIEW` | `works/phases/active/P8` |
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
| [x] `P5.S8` | `done` | Portfolio backend: holdings, D-day list, 챙긴 돈, 알림 preferences, sample portfolio | `implementation` | `works/phases/active/P5/slices/P5.S8` |
| [x] `P5.S9` | `done` | Admin backend: operator door + read-only ops endpoints + pipeline run log | `implementation` | `works/phases/active/P5/slices/P5.S9` |
| [x] `P5.S10` | `done` | Next.js foundation: scaffold, tokens/fonts/assets, cosmos shell, trust primitives, API client | `implementation` | `works/phases/active/P5/slices/P5.S10` |
| [x] `P5.S11` | `done` | Global chrome: nav, footer, mobile sheet, vocky triggers | `implementation` | `works/phases/active/P5/slices/P5.S11` |
| [x] `P5.S12` | `done` | Landing 관제 현황판: hero, 회고 anchor panels, countdown, 소멸주의보, board | `implementation` | `works/phases/active/P5/slices/P5.S12` |
| [x] `P5.S13` | `done` | Event detail ①②③: header, 환산 블록, field rows, trust states, CorrectionStory | `implementation` | `works/phases/active/P5/slices/P5.S13` |
| [x] `P5.S14` | `done` | 내 종목 조회 surface: search, 보유량, 진행 중인 권리, 놓친 돈 breakdown, empty states | `implementation` | `works/phases/active/P5/slices/P5.S14` |
| [x] `P5.S15` | `done` | Auth surfaces + conversion offers + sample entry | `implementation` | `works/phases/active/P5/slices/P5.S15` |
| [x] `P5.S16` | `done` | 내 포트폴리오: holdings, D-day list, 챙긴 돈, 알림 설정, sample mode, account menu | `implementation` | `works/phases/active/P5/slices/P5.S16` |
| [x] `P5.S17` | `done` | 운영 관제 admin panel: door + six sections | `implementation` | `works/phases/active/P5/slices/P5.S17` |
| [x] `P5.S18` | `done` | vocky integration: observation API shape decision + admin vocky view | `implementation` | `works/phases/active/P5/slices/P5.S18` |
| [x] `P5.S19` | `done` | Design-fidelity verification in a real browser (RESPECT THE DESIGN) | `implementation` | `works/phases/active/P5/slices/P5.S19` |
| [x] `P5.REVIEW` | `done` | phase review | `review` | `works/phases/active/P5/slices/P5.REVIEW` |

## Phase P7: 실서비스 정상화 fix pass

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [x] `P7.DECOMP` | `done` | decompose phase | `decomposition` | `works/phases/active/P7/slices/P7.DECOMP` |
| [x] `P7.S1` | `done` | dev origin unblock: hydration on 127.0.0.1/Tailscale — closes the dead 펼치기, static countdown, state-stomping reload, dead AI 질문 send and missing widget | `fix` | `works/phases/active/P7/slices/P7.S1` |
| [x] `P7.S2` | `done` | login reachable: the chrome account slot answers in dev (StrictMode double-effect in useAccount) | `fix` | `works/phases/active/P7/slices/P7.S2` |
| [x] `P7.S3` | `done` | board: a limited firm list at a time, with the signed 펼치기 disclosures working | `fix` | `works/phases/active/P7/slices/P7.S3` |
| [x] `P7.S4` | `done` | 내 종목 조회 typeahead: candidate suggestions before submit (API route + search UI) | `fix` | `works/phases/active/P7/slices/P7.S4` |
| [x] `P7.S5` | `done` | focus treatment: the clipped blue ring off the inputs, keyboard focus kept | `fix` | `works/phases/active/P7/slices/P7.S5` |
| [x] `P7.S6` | `done` | nav: drop the 내 종목 조회 slot (operator override of the signed three-slot nav) | `fix` | `works/phases/active/P7/slices/P7.S6` |
| [x] `P7.S7` | `done` | copy sweep: remove self-narrating implementation copy across the reader surfaces | `fix` | `works/phases/active/P7/slices/P7.S7` |
| [x] `P7.S8` | `done` | 포트폴리오: tidy the sample layout and make 청약·매도로 챙겼습니다 visibly move the 놓친 돈 | `fix` | `works/phases/active/P7/slices/P7.S8` |
| [x] `P7.S9` | `done` | fidelity sweep: all 11 items in a real browser, dev and production build, on the operator's own origins | `fix` | `works/phases/active/P7/slices/P7.S9` |
| [x] `P7.REVIEW` | `done` | phase review | `review` | `works/phases/active/P7/slices/P7.REVIEW` |

## Phase P6: Apply — AI 질문 agent

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [x] `P6.DECOMP` | `done` | decompose phase | `decomposition` | `works/phases/active/P6/slices/P6.DECOMP` |
| [x] `P6.S1` | `done` | 익명 대화 저장소 + Conversations 포트 구현: schema, session hash, cursor reads, ops tabs live | `implementation` | `works/phases/active/P6/slices/P6.S1` |
| [x] `P6.S2` | `done` | The five agent tools: search_events / get_event / get_portfolio / save_feedback / get_contact | `implementation` | `works/phases/active/P6/slices/P6.S2` |
| [x] `P6.S3` | `done` | Agent core: the autonomous Gemini function-calling loop, citation forcing, refusal families, never-compute | `implementation` | `works/phases/active/P6/slices/P6.S3` |
| [x] `P6.S4` | `done` | SSE 엔드포인트 + turn persistence + rate limiting + the request-path model boundary | `implementation` | `works/phases/active/P6/slices/P6.S4` |
| [x] `P6.S5` | `done` | 런처 + 위젯: the whole desktop AI 질문 surface (bubbles, tool rows, 인용, SSE states, 거절, scope, sessionStorage) | `implementation` | `works/phases/active/P6/slices/P6.S5` |
| [x] `P6.S6` | `done` | 전용 /ask 페이지 + 모바일 전폭 페이지 + 상세 질문 스트립 + 진입점 continuity | `implementation` | `works/phases/active/P6/slices/P6.S6` |
| [x] `P6.S7` | `done` | Design-fidelity verification in a real browser (RESPECT THE DESIGN) | `implementation` | `works/phases/active/P6/slices/P6.S7` |
| [x] `P6.F1` | `done` | Thousands-grouped numerals in agent prose (3,200원) | `fix` | `works/phases/active/P6/slices/P6.F1` |
| [x] `P6.REVIEW` | `done` | phase review | `review` | `works/phases/active/P6/slices/P6.REVIEW` |

## Phase P8: Design polish pass — audit & polish every surface

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [x] `P8.DECOMP` | `done` | decompose phase | `decomposition` | `works/phases/active/P8/slices/P8.DECOMP` |
| [x] `P8.S1` | `done` | AskWidget t1 중복 키 — collision-free turn ids after a restored thread | `fix` | `works/phases/active/P8/slices/P8.S1` |
| [x] `P8.S2` | `done` | R8 폴리시 라운드 — foundations/tokens + global chrome (nav · footer · vocky) | `co-work` | `works/phases/active/P8/slices/P8.S2` |
| [x] `P8.S3` | `done` | Apply R8 — foundations/tokens + global chrome | `implementation` | `works/phases/active/P8/slices/P8.S3` |
| [x] `P8.S4` | `done` | R9 폴리시 라운드 — landing 관제 현황판 + board | `co-work` | `works/phases/active/P8/slices/P8.S4` |
| [x] `P8.S5` | `done` | Apply R9 — landing 관제 현황판 + board | `implementation` | `works/phases/active/P8/slices/P8.S5` |
| [x] `P8.S5.5` | `done` | Account-menu 「의견 보내기」 row (R9 session instruction, Q12) | `implementation` | `works/phases/active/P8/slices/P8.S5.5` |
| [x] `P8.S6` | `done` | R10 폴리시 라운드 — event detail ①②③ + trust states | `co-work` | `works/phases/active/P8/slices/P8.S6` |
| [x] `P8.S7` | `done` | Apply R10 — event detail ①②③ + trust states | `implementation` | `works/phases/active/P8/slices/P8.S7` |
| [x] `P8.S8` | `done` | R11 폴리시 라운드 — 내 종목 조회 + 놓친 돈 조회기 | `co-work` | `works/phases/active/P8/slices/P8.S8` |
| [x] `P8.S9` | `done` | Apply R11 — 내 종목 조회 + 놓친 돈 조회기 | `implementation` | `works/phases/active/P8/slices/P8.S9` |
| [x] `P8.S10` | `done` | R12 폴리시 라운드 — auth (로그인 · 비밀번호 재설정) | `co-work` | `works/phases/active/P8/slices/P8.S10` |
| [x] `P8.S11` | `done` | Apply R12 — auth (로그인 · 비밀번호 재설정) | `implementation` | `works/phases/active/P8/slices/P8.S11` |
| [x] `P8.S12` | `done` | R13 폴리시 라운드 — 내 포트폴리오 + 알림 설정 | `co-work` | `works/phases/active/P8/slices/P8.S12` |
| [x] `P8.S13` | `done` | Apply R13 — 내 포트폴리오 + 알림 설정 | `implementation` | `works/phases/active/P8/slices/P8.S13` |
| [x] `P8.S14` | `done` | R14 폴리시 라운드 — AI 질문 (런처 · 위젯 · /ask · 질문 스트립) | `co-work` | `works/phases/active/P8/slices/P8.S14` |
| [x] `P8.S15` | `done` | Apply R14 — AI 질문 (런처 · 위젯 · /ask · 질문 스트립) | `implementation` | `works/phases/active/P8/slices/P8.S15` |
| [x] `P8.S16` | `done` | R15 폴리시 라운드 — 운영 관제 admin /ops | `co-work` | `works/phases/active/P8/slices/P8.S16` |
| [x] `P8.S17` | `done` | Apply R15 — 운영 관제 admin /ops | `implementation` | `works/phases/active/P8/slices/P8.S17` |
| [ ] `P8.REVIEW` | `todo` | phase review | `review` | `works/phases/active/P8/slices/P8.REVIEW` |

## Phase P4: Ship & Submit

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [ ] `P4.DECOMP` | `todo` | decompose phase | `decomposition` | `works/phases/active/P4/slices/P4.DECOMP` |
| [ ] `P4.REVIEW` | `todo` | phase review | `review` | `works/phases/active/P4/slices/P4.REVIEW` |
