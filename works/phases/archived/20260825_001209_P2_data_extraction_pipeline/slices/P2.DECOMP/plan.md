# Plan: P2.DECOMP — decompose Phase P2 (Data & Extraction Pipeline)

## Context

P2 builds the data backbone of 미주알: DART OpenAPI collection with scheduled jobs, schema-based LLM extraction (handoff §3.6 layer 1) for the 10 prose fields P1 identified, deterministic validation gates (layer 2), the "2026 소멸 신주인수권 가치 총액" estimation, and the ~100-filing labeled evalset + accuracy report. P1 closed with `data`/`operations`/`decisions` docs at v0002, a 295-line field matrix (`docs/reference/dart/field-matrix.md`), reusable stdlib spike code (`scripts/spike/dart.py`, `survey.py`, `corrections.py`), and a 1,002-request offline cache on disk for offline development.

This slice is the decomposition only: dispatch `slice-executor-high` to create the middle slices (bare folders via `new-slice`) and seed `phase.md` with the breakdown, findings, constraints, and open questions. No implementation code, no pre-filled `plan.md`s. P2 has no visual design → single pass (no `DECOMP2`, no `co-work`).

## Operator decisions folded in (resolved at this gate)

- **Stack: FastAPI + SQLAlchemy + Postgres.** P2 builds a plain Python package (collector / parser / extractor / gates / estimation) with Postgres persistence via SQLAlchemy; FastAPI endpoints come in P3, reading snapshots only. Record in `phase.md` + a Doc impact note (architecture/backend durable truth, consolidated at review).
- **Scheduling: Celery beat** (+ worker, Redis broker) per the handoff preference.

## Instructions for the executor (goes into plan.md)

Read `phase.md`, `intent.md`, `docs/current/{data,operations,decisions}.md`, and `docs/reference/dart/field-matrix.md` before cutting slices. Then:

1. **Create middle slices** with `python3 scripts/workflow.py new-slice --phase P2 --slice P2.Sn --name ... --kind ... --risk ... --order n` — bare folders only. Recommended breakdown (executor may refine, staying ordered along the D-1 drop order — ① first, ② backfill last):
   - **S1 — Package scaffold + storage schema** (`kind: feature, risk: high`): pyproject-based package; SQLAlchemy models for the event/version/snapshot design — event key `(corp_code, report_subtype, original_rcept_dt)`, every `rcept_no` a version, every version snapshotted at collection time; port `scripts/spike/dart.py` into the package as the DART client (keep retry/backoff, key-safe caching); Postgres locally + offline-cache fixture path.
   - **S2 — Collector for ①③ (new filings + 정정)** (`high`): `list.json` polling (3-month window, paging), detail fetch, snapshot persistence; 정정 discovery must poll `[기재정정]` rows and re-window on the original date (a naive "yesterday" poll misses 100% of corrections); correctness filters as requirements: exclude 제3자배정/일반공모 유증 (check 본문 `18.`, don't trust `ic_mthn` alone), suppress 소규모합병.
   - **S3 — 본문 deterministic parse layer** (`high`): document.xml ZIP handling, labeled-row table parse (lift from `corrections.py`), the 10/10 stable ① labels, `<CORRECTION>` 정정사항 parse, citation-span offsets; 증권신고서 sliced by `<TITLE>` only, never fed whole.
   - **S4 — LLM extraction (layer 1)** (`high`): Gemini schema extraction for the 10 target fields + 정정 prose re-extraction/diff; per-field citation spans. **Blocking dependency: the Gemini "changple5" credential is not in the repo — this slice starts with a `pending` operator handoff to supply it (gitignored beside `DART_API_KEY`, never echoed) and to confirm the exact model id.**
   - **S5 — Validation gates (layer 2)** (`high`): the named gate per field (arithmetic, date-order, citation-span existence, API cross-checks), per-field reason codes, failed-fields-never-exposed; all 금액/D-day math deterministic with LLM-free unit tests (small, high-value suite per the workspace test rule).
   - **S6 — Celery beat jobs + ② CB collection & backfill** (`high`): schedule collect/extract/gate tasks; CB structured fields (zero-LLM per P1); backfill to ≥ 2025-06 (~300–600 requests) — **measure/confirm the daily quota before running the backfill**, and note ② can ship structured-only.
   - **S7 — 소멸 신주인수권 가치 총액 estimation** (`high`): year's 유증 corpus → lapsed-warrant value estimate (청약률·증서 시세), the presentation/landing headline number, evidence-tagged vs `▷` estimates per handoff §7.
   - **S8 — Evalset + accuracy report** (`high`): ~100 filings from the estimation corpus, hand-label workflow (operator co-work → expect a `pending` gate), per-field precision + gate-block-rate report.
   - Risk: everything here writes real cross-file code → all `high`; use `low` only if the executor carves out a genuinely few-line/docs slice.
2. **Seed `phase.md`**: breakdown + rationale, the stack decision (+ Doc impact note), P1 constraint carry-overs (snapshot-only request path; API quirks table; version-staleness of `estkRs` — 본문 wins for schedules; `bdRs` is not a CB source), and open questions (daily quota ▷ unmeasured; Gemini credential/model id pending; KONEX unmeasured).
3. **Do not** pre-fill any middle slice's `plan.md`, implement code, or run `doc-new-version`.

## Orchestrator steps (this slice's lifecycle)

1. `start-slice P2.DECOMP` → copy this approved plan to `works/phases/active/P2/slices/P2.DECOMP/plan.md`.
2. Dispatch `slice-executor-high` (background Agent) with the plan.
3. On `done`: read `result.md`, run `python3 scripts/workflow.py validate`, `finish-slice P2.DECOMP`, commit (`feat(scope): decompose P2 into pipeline slices` or similar `docs(scope)` type).
4. Continue the phase loop into P2.S1 (gated: plan mode again for the next slice since the operator invoked the gated flow).

## Verification

- `python3 scripts/workflow.py validate` passes; `next` points at the first middle slice.
- `works/backlog.md` regenerated with the new P2 slice table; every new slice folder holds only `slice.json`.
- `phase.md` Decomposition/Findings/Constraints/Open Questions sections filled.
