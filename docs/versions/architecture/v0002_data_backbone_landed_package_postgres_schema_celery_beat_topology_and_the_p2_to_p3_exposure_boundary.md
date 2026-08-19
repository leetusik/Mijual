---
doc_id: architecture
version: v0002
created_at: 2026-08-20T05:05:25+09:00
source: P2.REVIEW
summary: Data backbone landed: package, Postgres schema, Celery beat topology and the P2 to P3 exposure boundary
previous: v0001_bootstrap
---

# Architecture

## Status

P2 built the data backbone: a plain Python package that collects, parses, extracts, gates and
estimates, persisting everything to Postgres and running on Celery beat. **There is no HTTP layer
yet** — FastAPI is P3's, and it reads persisted rows only. Facts below carry a command or a measured
count; estimates are marked `▷`.

## Stack

| layer | choice | notes |
|---|---|---|
| language / packaging | Python (`pyproject`), one package `src/mijual`, run from a repo-local `.venv` | no framework in P2 |
| persistence | **Postgres** via **SQLAlchemy 2 + psycopg3** | local docker, host port **5433** |
| scheduling | **Celery beat + worker** with **Redis** as broker, result backend and lock store | local docker, host port **6380**, compose profile `scheduling` |
| upstream | OpenDART REST (`mijual.dart`), ported from the P1 spike | retry/backoff, `null`-param dropping, `group[]` handling, key-safe on-disk cache |
| reading model | `gemini-3.7-flash` (operator credential) — **schema extraction only** | 213 calls stored to date; see `decisions` D-4 |
| HTTP layer | **deferred to P3 (FastAPI)** | reads persisted snapshots; never calls OpenDART or a model in a request path |

## Repo Shape

- `src/mijual/` — the package (see the module map below)
- `tests/` — terse pytest suite, **59 tests**, `.venv/bin/python -m pytest`
- `evalset/` — the frozen accuracy artifacts (`sample.json`, `sheet.csv`, `labels.json`, `LABELING.md`)
- `docs/current/`, `docs/versions/`, `docs/index.json` — durable docs (generated snapshots + immutable versions)
- `docs/reference/` — P1 artifacts (`dart/field-matrix.md`, the challenge handoff and 양식)
- `scripts/spike/` — P1's throwaway spike, kept as the source of the ported client and as an offline response cache (gitignored)
- `scripts/workflow.py`, `works/` — the workspace engine and its state
- `.claude/` — Claude Code entry points (skills, subagents, settings)

## Module Map

| module | job | spends |
|---|---|---|
| `mijual.dart` | OpenDART client with an explicit `max_requests` ceiling (`RequestBudgetExceeded`) | requests |
| `mijual.collect` | discovery (`list.json`) + detail fetch + snapshot persistence, originals and 정정 | requests |
| `mijual.bodydoc` | ZIP → single UTF-8 XML, labeled-row tables, `<CORRECTION>` blocks, **character spans** | requests (documents) |
| `mijual.extract` | §3.6 **layer 1**: schema extraction of the 10 prose targets + 정정 re-extraction/diff | LLM calls |
| `mijual.gates` | §3.6 **layer 2**: one named gate per field + citation gate; writes the exposure contract | nothing |
| `mijual.calc` | all displayed arithmetic — 금액, D-day (KST), 단수주, lockup 해제일 | nothing |
| `mijual.cb` | ② CB-specific collection helpers and backfill | requests |
| `mijual.estimate` | 증권발행실적보고서 census + the 소멸 신주인수권 가치 총액 report | requests (adoption only) |
| `mijual.evalset` | frozen accuracy sample, labels with provenance, accuracy report | nothing |
| `mijual.scheduler` | Celery beat/worker wiring + the broker-free `once` runner | delegates to the stages |
| `mijual.db` | SQLAlchemy models, session factory, additive `schema_sync.ensure_columns` | nothing |

## Storage Schema

Core chain — **`corp → event → filing_version → snapshot`**:

- **`event`** is keyed `(corp_code, report_subtype, original_rcept_dt)`. **The key is not injective**
  (~8 % of 2026 events collide: same-day double filings, concurrent events of one corp), so a
  collision detector flags `event_key_collision` and *no event is ever suppressed because its detail
  rows disagree*.
- **`filing_version`** — every observed `rcept_no` is a version (`original` / `기재정정` / `첨부정정`),
  carrying `pairing_method`, `hint_status` and a `pairing_note` audit line.
- **`snapshot`** — every version snapshotted at collection time with its raw body (JSONB for API
  responses, BYTEA for 본문 ZIPs) and a `content_sha1` that makes re-collection idempotent.
- **`extraction_call`** (one row per LLM call: model, prompt/schema version, input scope, tokens,
  ▷ cost, thinking level, raw payload) and **`extraction`** (one row per field, keyed
  `(filing_version_id, field_key, schema_version)`, with the `gate_*` verdict columns).
- **`performance_report`** — 증권발행실적보고서, a **sibling of `filing_version`, never a version of an
  event** (a 실적보고서 must not become an event's `latest_version`); keeps the same evidence contract
  (raw ZIP + `content_sha1`) plus a `facts` JSONB in which every figure carries its char span.

Excluded events are **retained** with a `suppressed_reason`, never deleted
(`no_warrant_class`, `no_appraisal_right`, `no_warrant_bodymun`, `unpaired_correction`,
`superseded_by_pairing`, …), so a suppression is auditable and reversible.

Corpus size today (`mijual.gates run`, 2026-08-20): **1,345 events / 3,990 filing versions / 7,076
snapshots / 69 performance reports**.

**Migrations: none, on purpose.** P2 runs without Alembic — all data is re-collectable, so schema
changes are `create_all` plus, for additive nullable columns, `mijual.db.schema_sync.ensure_columns`
(add-only, idempotent, refuses anything else) instead of a corpus-destroying reset.

## Pipeline Topology

```
collect  →  bodydoc  →  extract  →  gates
(API rows)  (본문+spans) (10 prose)  (verdicts + exposure)
```

Fixed order: each stage consumes what the previous one persisted. Exposed as
`mijual.daily_pipeline` plus one Celery task per stage, and as the broker-free
`python -m mijual.scheduler once [--offline]` (same code path). Schedule, budgets and the lock are in
`operations`.

## Boundaries

- **P2 → P3 (the exposure contract).** P3 never re-implements exposure. An **event** is exposable iff
  it is not suppressed, not withdrawn and carries no blocking flag (`warrant_conflict`,
  `detail_conflict`, `event_key_collision`, `hint_split_evidence`); a **field** is renderable iff its
  gate verdict is `passed` or `tbd`. Both are persisted (`Event.exposure_state/_reason/_note/
  _checked_at`, `Extraction.gate_status/_reason_code/_note`) so the board filters in SQL.
- **No OpenDART call and no LLM call in a request path.** Structurally true today: nothing under
  `mijual.gates`, `mijual.calc` or `mijual.db` imports the DART client. A dead worker leaves the board
  **stale, never dark** — which is what the 결격 uptime window requires (see `operations`).
- **The model reads; it never computes and never locates.** The extractor asks for a value **plus a
  verbatim quote**, and *this package* finds the quote's character span in the stored snapshot; a span
  is never taken from the model, and an unlocatable quote is stored `span_unresolved` and blocked.
- **Deterministic first.** `API` and `본문-label` fields never reach the extractor (a test asserts the
  two registries stay disjoint); all 금액/D-day arithmetic lives in `mijual.calc`, LLM-free and
  unit-tested.

## Cross-Cutting Constraints

- Handoff §3.6: the AI reads and speaks, **calculation is deterministic**, and a field that fails its
  gate is recorded with a reason code and never shown.
- Every outward-spending entry point carries an explicit ceiling: `DartClient(max_requests=…)` and
  `GeminiClient(max_calls=…)` refuse past it and report a budget-exhausted status rather than failing.
- Secrets (`DART_API_KEY`, the Gemini credential) live in the gitignored repo-root `.env`, are read
  in-process, and never reach a log, a cached filename, a recorded URL or an exception.
- **금지선:** no fine-tuning / PyTorch / HF framing anywhere. Model *training* is out of the story.

## Open Questions

- P3's HTTP shape (FastAPI routers, rendering, caching) — deferred by design.
- Where the worker runs in production, and the per-task thinking level it should use unattended
  (the 정정 해석 task still inherits the project preset — see `decisions` D-4).
- Whether `backend` needs its own doc once P3 exists; today the backend *is* this package.
