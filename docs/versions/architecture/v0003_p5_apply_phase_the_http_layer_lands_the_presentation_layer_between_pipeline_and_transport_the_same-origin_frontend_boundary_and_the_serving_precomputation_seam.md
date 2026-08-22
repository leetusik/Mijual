---
doc_id: architecture
version: v0003
created_at: 2026-08-22T18:04:19+09:00
source: P5.REVIEW
summary: P5 apply phase: the HTTP layer lands, the presentation layer between pipeline and transport, the same-origin frontend boundary, and the serving precomputation seam
previous: v0002_data_backbone_landed_package_postgres_schema_celery_beat_topology_and_the_p2_to_p3_exposure_boundary
---

# Architecture

## Status

P2 built the data backbone: a plain Python package that collects, parses, extracts, gates and
estimates, persisting everything to Postgres and running on Celery beat. **P5 added the HTTP layer
and the frontend**: a FastAPI service (`mijual.web`) over a new pure derivation layer
(`mijual.present`), and a Next.js app that reaches it through a same-origin proxy. The system is now
four layers — pipeline → presentation → transport → browser — and the request path reads persisted
rows only. Facts below carry a command or a measured count; estimates are marked `▷`.

## Stack

| layer | choice | notes |
|---|---|---|
| language / packaging | Python (`pyproject`), one package `src/mijual`, run from a repo-local `.venv` | no framework in P2 |
| persistence | **Postgres** via **SQLAlchemy 2 + psycopg3** | local docker, host port **5433** |
| scheduling | **Celery beat + worker** with **Redis** as broker, result backend and lock store | local docker, host port **6380**, compose profile `scheduling` |
| upstream | OpenDART REST (`mijual.dart`), ported from the P1 spike | retry/backoff, `null`-param dropping, `group[]` handling, key-safe on-disk cache |
| reading model | `gemini-3.7-flash` (operator credential) — **schema extraction only** | 213 calls stored to date; see `decisions` D-4 |
| HTTP layer | **FastAPI + uvicorn** (`mijual.web`), landed in P5 | reads persisted rows only; never calls OpenDART or a model in a request path — enforced by an AST import scan |
| frontend | **Next.js 16.3.2** (App Router, Turbopack) on React 19.2.8 + TypeScript 5.9.3 | no UI library, no CSS framework, no test framework — the design system is the vendored `tokens.css` |
| frontend → API | **same-origin rewrite** (`next.config.ts` proxies `/api/*` → `MIJUAL_API_ORIGIN`) | so the service configures **no CORS** and grants no preflight |

## Repo Shape

- `src/mijual/` — the package (see the module map below)
- `frontend/` — the Next.js app (`app/` routes · `components/` · `lib/` · `public/foundations/`
  with the byte-verbatim vendored `tokens.css` / `fonts.css` · `public/assets/` with the delivered
  binary design assets)
- `tests/` — terse pytest suite, **118 tests**, `.venv/bin/python -m pytest` (~2.6 s, no network,
  no model, no DB); the frontend's own check is `npm run build && npm run typecheck && npm run smoke`
  (**11** `node:test` cases, no jest/vitest/jsdom)
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
| `mijual.extract` | §3.6 **layer 1**, now in **two halves**: the paid schema reader (`runner`) for the 10 prose targets + 정정 re-extraction/diff, and the free deterministic `본문-label` reader (`labelfields`) | LLM calls (paid half only) |
| `mijual.gates` | §3.6 **layer 2**: one named gate per field + citation gate; writes the exposure contract | nothing |
| `mijual.calc` | all displayed arithmetic — 금액, D-day (KST), 단수주, lockup 해제일 | nothing |
| `mijual.cb` | ② CB-specific collection helpers and backfill | requests |
| `mijual.estimate` | 증권발행실적보고서 census + the 소멸 신주인수권 가치 총액 report | requests (adoption only) |
| `mijual.evalset` | frozen accuracy sample, labels with provenance, accuracy report | nothing |
| `mijual.scheduler` | Celery beat/worker wiring + the broker-free `once` runner | delegates to the stages |
| `mijual.db` | SQLAlchemy models, session factory, additive `schema_sync.ensure_columns`, and `repository` (version selection: `readable_versions` · `document_of` · `current_version(s)`) | nothing |
| `mijual.present` | **P5, layer 3**: the pure derivation layer every surface reads — tagged `Figure`s, countdowns, field payloads, ① money factors, 소멸 outcomes, 기재 불일치, the board summary | nothing |
| `mijual.web` | **P5, layer 4**: the FastAPI app — factory, session dependencies, error envelope, KST clock, CSRF, auth, portfolio, ops, the batched `reads`, the vocky client, `routers/` | nothing (except the one outbound vocky read) |
| `mijual.beat` | **P5**: the stdlib-only declaration of the beat schedule, windows and run-lock key, read by *both* the Celery app and the ops panel | nothing |
| `mijual.mail` | **P5**: the mailer seam — `Message(to, kind, data)` carries data, not rendered copy; `ConsoleMailer` is the dev transport | nothing |

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
`superseded_by_pairing`, **`foreign_correction_head`**, …), so a suppression is auditable and
reversible.

**P5 added two serving tables and one column** (all additive, still no Alembic):
**`offering_input`** — one row per ① event, carrying the whole `EventInputs.as_json()` plus
`price_confirmed` / `subscription_start` / `subscription_end` / `decision_rcept_no` as columns so
the 소멸 앞둔 count and the 발행가 확정 전 state are SQL — and the additive column
**`performance_report.lapse`**, one `LapseRow.as_json()` per 실적보고서. Both are written by an
offline worker (`estimate reparse` → `estimate snapshot`), never by a request path.

**P5 also added the reader and operator tables**, disjoint from the corpus chain:
`account` · `auth_session` · `password_reset` · `holding` · `notification_pref` · `lapse_claim` ·
`ops_session` · `pipeline_run`. **`ops_session` has no relation to any other table** and no
conversation table exists at all — the schema-level 계정↔대화 no-join promise is trivially intact
because there is nothing to join (P6 owns that storage).

Corpus size today (2026-08-22): **1,359 events / 3,990 filing versions / 7,076 snapshots / 69
performance reports / 710 extraction rows / 545 offering inputs**, of which **488 events are
exposable** (50 ① / 422 ② / 16 ③).

**Migrations: none, on purpose.** P2 runs without Alembic — all data is re-collectable, so schema
changes are `create_all` plus, for additive nullable columns, `mijual.db.schema_sync.ensure_columns`
(add-only, idempotent, refuses anything else) instead of a corpus-destroying reset.

## Pipeline Topology

```
collect  →  bodydoc  →  extract  →  gates  →  reparse  →  snapshot
(API rows)  (본문+spans) (labels,     (verdicts   (re-read      (serving
                         then prose)  + exposure)  실적보고서)   precomputation)
```

Fixed order: each stage consumes what the previous one persisted. Exposed as
`mijual.daily_pipeline` plus one Celery task per stage, and as the broker-free
`python -m mijual.scheduler once [--offline]` (same code path). Schedule, budgets and the lock are in
`operations`.

**P5 added the last two stages, and both are offline** (0 requests, 0 model calls). They exist
because the request path may not import `mijual.estimate`: `reparse` rewrites the parse-derived
columns of every stored 실적보고서, `snapshot` builds the `offering_input` rows and
`performance_report.lapse` the API reads. The order is a data dependency — `snapshot` builds from
what `reparse` wrote. Inside `extract`, the **free label pass runs first and outside
`extract_max_calls`**: budgeting a pass that spends nothing could only starve it.

**Every run now writes itself down** (`pipeline_run`, opened before the first stage and closed
after the last), so an in-flight or crashed run is visible as a row with no `finished_at`, while a
*skipped* run writes none.

## Boundaries

- **Pipeline → presentation → transport.** `mijual.present` is the single derivation layer and
  **no endpoint re-derives a number**, which is what stops two surfaces showing two readouts of the
  same figure. The direction is **`web → present`, never the reverse** — `present` restates the
  instant-serialization policy rather than importing it back, and a test pins the two byte-for-byte.
- **The exposure contract (P2 → everything above).** The serving layers never re-implement exposure. An **event** is exposable iff
  it is not suppressed, not withdrawn and carries no blocking flag (`warrant_conflict`,
  `detail_conflict`, `event_key_collision`, `hint_split_evidence`); a **field** is renderable iff its
  gate verdict is `passed` or `tbd`. Both are persisted (`Event.exposure_state/_reason/_note/
  _checked_at`, `Extraction.gate_status/_reason_code/_note`) so the board filters in SQL.
- **No OpenDART call and no LLM call in a request path — now enforced, not merely observed.** An AST
  import scan (`tests/test_web_smoke.py`) walks every module under `src/mijual/web/` and fails if one
  imports `mijual.dart`, `mijual.collect` or `mijual.extract`; `tests/test_present.py` applies the
  same scan to the derivation layer. Two near-misses were closed **by moving, not forking**: version
  selection moved into `mijual.db.repository` (so importing `gates.exposure` no longer drags the
  extractor tree), and the beat/lock declaration moved into stdlib-only `mijual.beat` (so the ops
  panel can read the schedule without importing `mijual.scheduler`). Measured: `import
  mijual.web.app` pulls **none** of `dart`/`collect`/`extract`/`estimate`/`scheduler`/`evalset`, and
  no Celery. A dead worker leaves the board **stale, never dark** — what the 결격 uptime window
  requires (see `operations`).
- **The serving precomputation seam: the worker computes, the request path reads.** Because
  `mijual.estimate` imports `dart` + `collect` + `extract` at module level, a router can never call
  `build_report` or `event_inputs`. Anything derived from those reaches a surface only through
  persisted state — the same shape of backing work as the pipeline run log. This is the general
  answer whenever a design implies data the request path cannot compute.
- **The frontend/API boundary is a same-origin rewrite, so there is no cross origin.** The browser
  talks only to the Next origin; `next.config.ts` proxies `/api/*` to `MIJUAL_API_ORIGIN`. The
  service therefore configures **no CORS middleware and grants no preflight** — which is exactly what
  the CSRF design rests on — and the session cookie needs no `SameSite=None`. **Do not add CORS to
  this service.** P4 repoints the proxy with an env var, not a code change.
- **Only one module may hold an HTTP client.** `mijual.web.vocky` is the single outbound reader
  (stdlib `urllib`, 3 s timeout, no retries, redirects refused because `urllib` re-sends
  `Authorization` to the target). A test asserts no other request-path module imports one.
- **The model reads; it never computes and never locates.** The extractor asks for a value **plus a
  verbatim quote**, and *this package* finds the quote's character span in the stored snapshot; a span
  is never taken from the model, and an unlocatable quote is stored `span_unresolved` and blocked.
- **Deterministic first.** `API` and `본문-label` fields never reach the extractor (a test asserts the
  two registries stay disjoint); all 금액/D-day arithmetic lives in `mijual.calc`, LLM-free and
  unit-tested. P5 made this concrete: the `본문-label` tier gained its **first stored field**
  (③ 매수예정가격) through `extract.labelfields`, writing the same `Extraction` row shape as an LLM
  field with `call_id`/`model` **NULL** — so a report can tell a free reading from a paid one, and
  the gate layer, the exposure contract and the presentation contract needed no change at all. The
  lesson generalizes: **when a design implies missing data, measure which tier the value lives in
  before assuming it needs a model** — this one turned out deterministic in two independent places
  and cost ▷ $0.0000.

## Cross-Cutting Constraints

- Handoff §3.6: the AI reads and speaks, **calculation is deterministic**, and a field that fails its
  gate is recorded with a reason code and never shown.
- Every outward-spending entry point carries an explicit ceiling: `DartClient(max_requests=…)` and
  `GeminiClient(max_calls=…)` refuse past it and report a budget-exhausted status rather than failing.
- Secrets (`DART_API_KEY`, the Gemini credential) live in the gitignored repo-root `.env`, are read
  in-process, and never reach a log, a cached filename, a recorded URL or an exception.
- **금지선:** no fine-tuning / PyTorch / HF framing anywhere. Model *training* is out of the story.

## Open Questions

- Where the worker runs in production, and the per-task thinking level it should use unattended
  (the 정정 해석 task still inherits the project preset — see `decisions` D-4).
- **Caching.** Nothing is cached and nothing is paged today; `/board` is 160 KB in ~54 ms and the
  design paginates nothing. If a surface ever needs paging or a cache, it is that surface's
  decision, not a transport-wide one.
- **Deployment topology (P4).** Neither the API nor the frontend is a compose service; pool sizing,
  `pool_pre_ping`, read-replica routing and where the schema is created before first serve are all
  P4's.
