---
doc_id: architecture
version: v0008
created_at: 2026-08-25T08:53:37+09:00
source: P9.REVIEW
summary: P9 smart assistant — structured-block storage on the conversation row, the calculator and the security guard as the agent's sixth and seventh tools, ceilings 20/30/22, a static cache prefix
previous: v0007_p8_design_polish_pass_mijual.web_s_outbound_row_is_one_vocky_read_plus_one_vocky_capture_still_in_the_single_module_the_ast_scan_allows_suite_baseline_142
---

# Architecture

## Status

P2 built the data backbone: a plain Python package that collects, parses, extracts, gates and
estimates, persisting everything to Postgres and running on Celery beat. **P5 added the HTTP layer
and the frontend**: a FastAPI service (`mijual.web`) over a new pure derivation layer
(`mijual.present`), and a Next.js app that reaches it through a same-origin proxy. **P6 added the
agent**: a new top-level package `mijual.agent` that runs an autonomous tool-calling loop over
`gemini-3.7-flash`, reached from exactly one streaming endpoint. The system is now
pipeline → presentation → transport → browser, with the agent hanging off transport as a fifth
package the request path may reach and nothing else may. The request path still reads persisted
rows only — the agent's five tools read them too. Facts below carry a command or a measured count;
estimates are marked `▷`.

**P8 (디자인 폴리시 패스) changed the topology in exactly one place**: `mijual.web`'s outbound row is
no longer "the one outbound vocky read" but **one outbound vocky read + one outbound vocky capture**
(`POST /feedback`, the reader's 의견 surface). Both live in the same single module the AST scan
allows to hold an HTTP client (`mijual/web/vocky.py`), both use stdlib `urllib`, and neither adds a
dependency or a layer. Nothing else moved: no new package, no new table, no new column.

**P9 (스마트 어시스턴트) changed the topology nowhere and `mijual.agent` everywhere inside itself.**
No new package, no new table, no new dependency, no new outbound call: the agent grew from **five
tools to seven** (`calculate` and `security_check`), the conversation row gained **one additive
nullable column** (`conversation_turn.blocks`, via `schema_sync.ensure_columns` — this repo still has
no Alembic), and the per-turn ceilings rose. Every invariant the AST scans hold still holds: no
OpenDART call and no LLM call outside the agent in a request path, the model reached **only** through
`mijual.agent`, and `mijual.agent` importing no spending module.

## Stack

| layer | choice | notes |
|---|---|---|
| language / packaging | Python (`pyproject`), one package `src/mijual`, run from a repo-local `.venv` | no framework in P2 |
| persistence | **Postgres** via **SQLAlchemy 2 + psycopg3** | local docker, host port **5433** |
| scheduling | **Celery beat + worker** with **Redis** as broker, result backend and lock store | local docker, host port **6380**, compose profile `scheduling` |
| upstream | OpenDART REST (`mijual.dart`), ported from the P1 spike | retry/backoff, `null`-param dropping, `group[]` handling, key-safe on-disk cache |
| reading model | `gemini-3.7-flash` (operator credential) — **two uses now**: offline schema extraction, and **P6's in-request agent turn** | 213 extraction calls stored to date; the agent runs at thinking `LOW` with a per-turn ▷ ledger. See `decisions` D-4 |
| HTTP layer | **FastAPI + uvicorn** (`mijual.web`), landed in P5 | reads persisted rows only; **never calls OpenDART** in a request path, and reaches a model **only** through `mijual.agent` — both enforced by AST import scans |
| agent | **`mijual.agent`** (P6): an autonomous Gemini function-calling loop with five server-side tools, a generation-boundary citation gate and a structural per-turn budget | streamed to the browser over SSE (`POST /ask`); imports no spending module; **derives no number** — the one formatting step it owns (`figures.py`, thousands grouping in released prose) is presentation over values the contract already served |
| frontend | **Next.js 16.3.2** (App Router, Turbopack) on React 19.2.8 + TypeScript 5.9.3 | no UI library, no CSS framework, no test framework — the design system is the vendored `tokens.css` |
| frontend → API | **same-origin rewrite** (`next.config.ts` proxies `/api/*` → `MIJUAL_API_ORIGIN`) | so the service configures **no CORS** and grants no preflight |

## Repo Shape

- `src/mijual/` — the package (see the module map below)
- `frontend/` — the Next.js app (`app/` routes · `components/` · `lib/` · `public/foundations/`
  with the byte-verbatim vendored `tokens.css` / `fonts.css` · `public/assets/` with the delivered
  binary design assets)
- `tests/` — terse pytest suite, **142 tests** (P7 added one over `GET /stocks/suggest`; P8 added three over `POST /feedback`), `.venv/bin/python -m pytest` (~3.5 s, no network,
  no model, no DB — the agent suite runs against a scripted model, so it spends nothing and needs no
  `GEMINI_API_KEY`); the frontend's own check is `npm run build && npm run typecheck && npm run smoke`
  (**15** `node:test` cases, no jest/vitest/jsdom)
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
| `mijual.web` | **P5, layer 4**: the FastAPI app — factory, session dependencies, error envelope, KST clock, CSRF, auth, portfolio, ops, the batched `reads`, the vocky client, `routers/`; **P6 added `ask` + `conversationstore`** (the SSE transport and the anonymous conversation storage); **P7 added one read-only route, `GET /stocks/suggest`**, over a new `reads.suggest_corps` — no new dependency and no new layer | nothing (except the outbound vocky **read and capture** — P8's `POST /feedback` joins `GET /ops/vocky` in the same module); **`ask` spends through `mijual.agent`** |
| `mijual.agent` | **P6**: the AI 질문 agent — `loop.run_turn` (the autonomous function-calling turn), `tools` (the server-side callables over `present`/`reads`), `citations` (the generation boundary), `client` (its own streaming Gemini client + ▷ ledger), `events` (the typed stream), `instructions`, `copy` (the signed Korean strings), `figures` (thousands grouping — **presentation only**, over values `present` already served). **P9 (R16) made it seven tools and a wider stream**: `calculate` (an `op` enum over five `mijual.calc` primitives plus an AST-whitelisted `expr` hatch) and `security_check` (a detector whose *call* is the whole signal), plus `status`/`data`/`calc` events, `block_id`/`persistent` on the event base, and `TurnEnd.filings` | **LLM calls** — the only in-request spend in the system |
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
`ops_session` · `pipeline_run`. **`ops_session` has no relation to any other table.**

**P6 added the two conversation tables** — `conversation_turn` and `conversation_feedback` — and
they are the schema-level shape of the anonymity promise rather than a display policy. Neither
carries an account, email, IP or user-agent column (the voluntary 답장 이메일 on a feedback row is
the one signed exception), **neither has a foreign key in either direction**, and no column on
`account` reaches them. That is asserted by a test that walks both tables' columns and every foreign
key in the metadata, not by discipline — so 「대화는 익명으로 저장됩니다」 moved from *trivially true,
nothing stored* to *implemented and checkable*. **Do not add a foreign key to either table**: the
test fails on any. Conversation rows are also the one class of row in this system that is **not
re-collectable**, so their schema changes additively (`ensure_columns`) or not at all.

**P9 added one column to `conversation_turn`: `blocks`, nullable and default-free** — the turn's
**structured blocks stored verbatim as the frames the reader received**, keyed by `block_id`, one
entry per block in its final state (a `pending → done` calculation stores one). It is stored because
prose cannot carry a calculation's inputs, its expression and each input's 근거: the audit path *is*
the payload. `NULL` means both "this turn had no blocks" and "written before R16" — the same reading,
honestly. The absorb path is **generic over any persistent block**, so a later structured element
needs no second storage change; the transient 진행 표시 line is never stored. The ops panel's row
shape is unchanged — the payload is stored, not yet served (an open operator question).

Corpus size today (2026-08-22): **1,359 events / 3,990 filing versions / 7,076 snapshots / 69
performance reports / 710 extraction rows / 545 offering inputs**, of which **488 events are
exposable** (50 ① / 422 ② / 16 ③). The dev database now holds **18 tables** (16 → 18 with the two
conversation tables, created additively with `mijual.db.session.create_all`, no existing table
touched).

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
- **The request-path boundary, re-aimed in P6 rather than quietly broken.** Through P5 the sentence
  was *"no OpenDART call **and no LLM call** happens in a request path"*. R6's AI 질문 agent is a
  model call in a request path **by design** — SSE streaming cannot be anything else — so the
  invariant was rewritten into the three clauses that are still absolutely true, each carried by its
  own AST import scan rather than by prose:
  1. **No OpenDART call happens in any request path.** `tests/test_web_smoke.py` walks every module
     under `src/mijual/web/` and fails if one imports `mijual.dart`, `mijual.collect` or
     `mijual.extract`; `tests/test_present.py` applies the same scan to the derivation layer.
  2. **The model is reached only through `mijual.agent`.**
     `tests/test_web_smoke.py::test_the_model_is_reached_only_through_the_agent_package` bans
     `google` / `openai` / `anthropic` anywhere under `src/mijual/web/**`, so the credential, the
     per-turn call budget, the citation gate and the ▷ ledger cannot be bypassed by a handler that
     talks to the model API itself. It is a **routing** rule, not an absence.
  3. **`mijual.web` itself speaks HTTP in exactly one file** (`vocky.py` — see below), and
     **`mijual.agent` imports no spending module either**
     (`tests/test_agent_tools.py::test_the_agent_package_imports_no_spending_module`): the agent
     reads persisted rows, it never collects or extracts.

  The old absolute wording was corrected everywhere it was published, including the OpenAPI
  `DESCRIPTION` — an outward surface. **`mijual.extract.client` is deliberately not imported by the
  agent**, however convenient its `GeminiClient` wrapper looks: it lives inside a package the request
  path is forbidden to reach. The agent has its own client; the two ideas worth sharing (a structural
  call budget, a recorded thinking level + ▷ ledger) were copied, and the two clients diverged
  immediately anyway (JSON extraction versus streamed tool calls).

  Two earlier near-misses were closed **by moving, not forking**: version selection moved into
  `mijual.db.repository` (so importing `gates.exposure` no longer drags the extractor tree), and the
  beat/lock declaration moved into stdlib-only `mijual.beat` (so the ops panel can read the schedule
  without importing `mijual.scheduler`). Measured: `import mijual.web.app` pulls **none** of
  `dart`/`collect`/`extract`/`estimate`/`scheduler`/`evalset`, and no Celery; importing
  `mijual.agent` costs **no SDK, no credential and no connection** (`google` is absent from
  `sys.modules` afterwards, and `GEMINI_API_KEY` is required neither to import nor to `create_app`).
  A dead worker still leaves the board **stale, never dark** — what the 결격 uptime window requires
  (see `operations`).
- **The agent decides; the loop enforces.** `mijual.agent.loop.run_turn` is the phase's keystone and
  its control flow is the architecture: `generate → (function_call? → execute → feed the result back)
  → repeat → answer`. **No tool name appears in the control flow** — nothing is fetched before the
  model speaks or after it, no tool fires because a question matched a pattern, and no ordering is
  imposed on the calls the model asks for. `call_tool` is invoked from exactly one place in the whole
  codebase, dispatching on the name the model supplied; a turn ends when the model emits a round with
  no function calls. Even the 범위 the reader opened on is resolved with a plain row read and put in
  the system instruction as *context*, precisely so that a scoped turn does not make one tool call
  mandatory. What the loop keeps for itself is everything that must not be left to a model: the
  visible tool fact rows, the citation gate, the signed refusal families, the 갈 곳 links and
  footer (composed from tool results as **data**, so the model never writes a URL), the structural
  budget, and the ▷ ledger.

  **P9 kept that property while adding two tools and a hard reject.** The loop still names no tool:
  it asks `tools.status_phase` / `value_rows` / `calc_plan` / `calc_outcome` / `security_incident`
  what a call *is*, so payload- and argument-shape knowledge stays beside the tools. The
  **security hard reject** sits exactly where the record puts it — right after `model.stream(...)`
  returns and `calls` have been collected, **before** the gate flush, **before** the tool-budget
  check and **before** any tool executes: no tool of that round runs, no `ModelMessage` is appended,
  the signed 보안 sentence is emitted, and the model gets **no second chance** to soften it. The
  detector's own body is an unreachable defensive no-op that returns **no fact row**, so the reader
  never learns a check happened. The incident is logged (category + a 200-character excerpt +
  `session_hash`) and **never stored in the database**.
- **The ceilings, and the one invariant that keeps an abort honest.** P9 raised the per-turn budget
  from `6 rounds / 10 tool calls / 8 model calls` to **`20 / 30 / 22`**, and the client's own default
  `max_calls` moved `8 → 22` with it. **`max_model_calls` must stay ≥ `max_rounds`**, pinned by a
  test: the client's ceiling fires *inside* a round, so a smaller model-call budget would abort with
  `call_budget` when what actually happened was `round_budget` — a ceiling that lies about which
  ceiling fired. The ceilings stay structural and are **never rendered as copy**. Zero-I/O tools
  (`calculate`, `security_check`) are **budget-exempt**, counted by a separate `billed` counter so
  the terminal still reports every tool that ran. Nothing bounds a turn in **time**: the 120 s
  timeout is per model call, so a pathological 20-round turn holds its slot for a long while — a
  known, recorded trade, not an oversight.
- **The system instruction is a static cache prefix, and that is a standing constraint.**
  `instructions._RULEBOOK` is assembled **once at import** from the static blocks and
  `system_instruction()` appends only the turn's two changing values (범위 · 오늘 KST) at the tail, so
  the prefix is byte-identical across turns — asserted by a test that splits on the `THIS TURN.`
  seam. **Any per-turn value placed above that prefix re-breaks it.** Whether the prefix is actually
  credited is now **measured, not assumed**: `Usage.cached_tokens` rides the ▷ ledger end to end
  (printed inside the prompt count, because it is a subset) and is priced at a cached rate. The
  measurement across P9's live passes is `cached 0` every time, with a ~5.5k-token prefix that should
  clear Gemini's 4,096-token floor — an honest reading of a real number, and an open operator
  question rather than a claim that caching never happens.
- **`mijual.calc` is still the LLM-free home of the product's money math.** The `calculate` tool is a
  *window* onto it, never a second implementation: an `op` enum over five existing primitives
  (배정 신주 · 초과청약 한도 · 소멸 증서 · D-day · 전매제한 해제일) whose 식 line is composed from each
  op's own declared template, plus a clearly-labelled `expr` escape hatch. The ▷ 추정 family is
  deliberately **not** exposed — a 추정 value returned as a 「계산」 result would silently lose its
  추정 mark. Every derived number still comes from an auditable tool; browser-side calculation stays
  banned.
- **The generation boundary stays; its *judgement* was retired in P9 (R16 strip-don't-drop).** The
  model's prose still does not reach the reader directly — it reaches
  `mijual.agent.citations.CitationGate` as the stream arrives — but the gate no longer **drops**.
  Markers are stripped (resolvable ones become numbered chips), an uncited sentence ships, a 공시
  figure no tool returned is **marked 「미확인」** instead of deleted, and a 「…」 span occurring
  verbatim in nothing a tool returned loses its **quotation marks** while the words survive as the
  assistant's own prose. `blocked` on the terminal is now a **count of markers the gate could not
  honour**, not of sentences it discarded. What was **kept** is the part that was always load-bearing:
  the **closed citation space** (a reference id exists only because a tool returned it, so an invalid
  citation is unconstructable rather than filtered), 같은 근거 = 같은 번호, chip-arrives-with-its-claim,
  and a tool's own signed string reaching the reader byte for byte. The honest limit is still recorded
  with the mechanism: the number check is *membership*, not semantics, so what it reliably catches is
  a value present nowhere upstream — which is the shape of every invented figure, and is now expressed
  as a visible 「미확인」 mark rather than as a silent deletion.
- **The serving precomputation seam: the worker computes, the request path reads.** Because
  `mijual.estimate` imports `dart` + `collect` + `extract` at module level, a router can never call
  `build_report` or `event_inputs`. Anything derived from those reaches a surface only through
  persisted state — the same shape of backing work as the pipeline run log. This is the general
  answer whenever a design implies data the request path cannot compute.
- **The frontend/API boundary is a same-origin rewrite, so there is no cross origin.** The browser
  talks only to the Next origin; `next.config.ts` proxies `/api/*` to `MIJUAL_API_ORIGIN`. The
  service therefore configures **no CORS middleware and grants no preflight** — which is exactly what
  the CSRF design rests on — and the session cookie needs no `SameSite=None`. **Do not add CORS to
  this service.** P4 repoints the proxy with an env var, not a code change. **P6 found the one thing
  this proxy does to a payload**: Next's router compresses whatever it forwards, `text/event-stream`
  included, and a gzip encoder holds the stream until it has a block — so the streaming endpoint
  sends `Cache-Control: no-store, **no-transform**` (RFC 9111 §5.2.2.6), the standard's own way to
  say *do not re-encode this*, which the Next `compression` middleware, nginx and the CDNs P4 will
  meet all honour. Without it a reader sees the whole answer arrive at once. Do not simplify that
  header back to `no-store`.
- **Only one module may hold an HTTP client.** `mijual.web.vocky` is the single outbound module —
  since P8 it holds **two** calls, a read (`GET /ops/vocky`) and a capture (`POST /feedback`) —
  (stdlib `urllib`, 3 s timeout, no retries, redirects refused because `urllib` re-sends
  `Authorization` to the target). A test asserts no other request-path module imports one.
  **Both calls must send a `User-Agent`** (`mijual.web.vocky.USER_AGENT`): vocky sits behind
  Cloudflare, which bans `Python-urllib/3.x` by browser signature — measured 403 `error 1010` without
  it and 200/202 with it, and it had been silently breaking the P5.S18 observation read.
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
- Every outward-spending entry point carries an explicit ceiling: `DartClient(max_requests=…)`,
  `GeminiClient(max_calls=…)` and — P6's — `AgentGeminiClient(max_calls=…)` plus the per-turn
  `TurnBudget(max_rounds, max_tool_calls, max_model_calls)` all refuse past it and report a
  budget-exhausted status rather than failing. Every cap maps to an honest terminal; a turn is never
  silently truncated, and no ceiling is ever rendered as reader-facing copy.
- Secrets (`DART_API_KEY`, the Gemini credential) live in the gitignored repo-root `.env`, are read
  in-process, and never reach a log, a cached filename, a recorded URL or an exception.
- **금지선:** no fine-tuning / PyTorch / HF framing anywhere. Model *training* is out of the story.

## Open Questions

- Where the worker runs in production, and the per-task thinking level it should use unattended
  (the 정정 해석 task still inherits the project preset — see `decisions` D-4).
- **Caching.** Nothing is cached and nothing is paged today; `/board` is 160 KB in ~54 ms and the
  design paginates nothing. If a surface ever needs paging or a cache, it is that surface's
  decision, not a transport-wide one. **The streaming endpoint is `no-store` and must stay that way.**
- **Deployment topology (P4).** Neither the API nor the frontend is a compose service; pool sizing,
  `pool_pre_ping`, read-replica routing and where the schema is created before first serve are all
  P4's — and P6 made the last one concrete: **the two conversation tables must exist in the deploy
  database before the first `POST /ask`**, because there are no migrations and `create_all` otherwise
  runs only from the collect/gates/pipeline entry points.
- **The deployed streaming topology (P4).** Unbuffered was measured straight at uvicorn, through
  `next dev`, and through a production `next build && next start`, browser-style `Accept-Encoding`
  included. An edge route / CDN / nginx in front of it is still unmeasured, and **there is no
  heartbeat** — the longest observed gap between frames with the live agent is **6.0 s** (the model's
  first round), so a proxy idle timeout below ~10 s would cut a legitimate turn.
- **Rate-limit state is per process.** P6's two ceilings live in memory on one worker, hold no
  identity and persist nothing; cross-process state is P4's, alongside login rate limiting.
