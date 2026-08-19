# Backlog

> Generated dashboard. Do not put detailed task context here; edit phase/slice/deferred folders instead.
> Status box: `[x]` done · `[~]` pending — waiting on operator · `[r]` ready — plan approved, awaiting execution · `[ ]` open/in progress.

## Pointer

- Current phase: `P2`
- Current slice: `P2.F4`
- Next slice: `P2.REVIEW`
- Waiting on operator: `none`
- Open deferred jobs: `4`
- Rebuilt at: `2026-08-20T04:40:58+09:00`

## Active Phases

| Phase | Status | Review | Name | Current Slice | Path |
|---|---|---|---|---|---|
| [x] `P1` | `done` | `pass` | Foundation Spike & Confirmations | `none` | `works/phases/active/P1` |
| [ ] `P2` | `in_progress` | `changes_requested` | Data & Extraction Pipeline | `P2.F4` | `works/phases/active/P2` |
| [ ] `P3` | `planned` | `pending` | Mijual Web Service (design + build) | `P3.DECOMP` | `works/phases/active/P3` |
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
| [ ] `P2.F4` | `todo` | Fix check_against_items matcher and re-freeze the 정정 recall proxy | `fix` | `works/phases/active/P2/slices/P2.F4` |
| [ ] `P2.REVIEW` | `changes_requested` | phase review | `review` | `works/phases/active/P2/slices/P2.REVIEW` |

## Phase P3: Mijual Web Service (design + build)

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [ ] `P3.DECOMP` | `todo` | decompose phase | `decomposition` | `works/phases/active/P3/slices/P3.DECOMP` |
| [ ] `P3.REVIEW` | `todo` | phase review | `review` | `works/phases/active/P3/slices/P3.REVIEW` |

## Phase P4: Ship & Submit

| Slice | Status | Name | Kind | Path |
|---|---|---|---|---|
| [ ] `P4.DECOMP` | `todo` | decompose phase | `decomposition` | `works/phases/active/P4/slices/P4.DECOMP` |
| [ ] `P4.REVIEW` | `todo` | phase review | `review` | `works/phases/active/P4/slices/P4.REVIEW` |
