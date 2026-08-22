# Plan — P6.S2: the five agent tools (`mijual.agent` package)

## Goal

Create the new top-level package `src/mijual/agent/` and implement the five
server-side tools the AI 질문 agent will call — `search_events(query)` ·
`get_event(rcept_no)` · `get_portfolio()` · `save_feedback(text, email?)` ·
`get_contact()` — each returning **verified-contract values only**, each with
its Gemini `FunctionDeclaration` schema and its signed fact-row string. This is
deterministic, model-free code: no LLM call, no SSE, no loop (S3/S4 own those).
Everything here is testable against the live corpus with zero spend.

## Read first

- `works/phases/active/P6/phase.md` — Findings 1 (package boundary), 5
  (get_portfolio), 6 (never compute), 7 (citation payloads), 9 (get_contact),
  15 (search_events contract), 17 (copy discipline), Constraints, and **note 18
  (S1's landed write API)**: `record_turn` / `record_feedback` /
  `session_hash_or_new` in `mijual.web.conversationstore`.
- `docs/reference/design/rounds/06-explain/output/build-prompt.md` §Agent —
  the tool list, the fact-row format
  `이벤트 검색 「{q}」 → {n}건 · {유형} · {rcept_no}`, search-0건 copy, and the
  hard rules. `.../output/result.md` (~line 49) has the signed fact-row
  examples, including `내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)`
  and the 의견 저장 row. READ-ONLY; transcribe strings, never paraphrase.
- `src/mijual/web/reads.py` — the public loaders to build on: `resolve_corp` ·
  `resolve_event` · `load_detail` · `load_stock` · `load_portfolio` ·
  `load_board` · `corpus_as_of`. Prefer these over private helpers; if a
  genuinely new query is needed (search returning *multiple* candidates —
  Finding 15), write it against the same exposure rules the loaders use, never
  a fresh derivation of numbers or exposure.
- `src/mijual/present/values.py` — `Figure` / `QuotePart`: the citation shapes
  (quote + span + rcept_no; API-tier = no quote, rcept_no as handle).
- `src/mijual/config.py` — Settings conventions, for the new contact field.
- `src/mijual/web/portfolio.py` + `GET /portfolio/sample` — how the sample
  portfolio and an account portfolio are served today.
- `docs/current/api.md` §presentation contract — what "the agent never
  computes" means concretely (D-day, 환산, 금액 all upstream).

## Package boundary (Finding 1 — structural)

- `mijual.agent` must **never** import `mijual.dart`, `mijual.collect`, or
  `mijual.extract` (not even for the `GeminiClient` — S3 builds the agent's own
  client). It reads persisted rows through `mijual.web.reads` /
  `mijual.present` / `mijual.web.conversationstore` and speaks no HTTP.
- Lazy-import `google.genai.types` inside the declaration builders (the
  convention `mijual.extract.client` uses), so the package imports cleanly
  without the SDK in play.

## What to build

1. **`ToolContext`** — a small dataclass the transport (S4) will construct per
   request: the DB session, `today`/clock, the caller's `session_hash`, the
   authenticated account (or `None`), and the event scope (`rcept_no` or None,
   from the widget's 범위 model). Tools take context + their declared args and
   nothing else — **no tool accepts an account id, email, or client-supplied
   holdings payload** (Finding 5).
2. **The five tools**, each returning a structured result carrying:
   - the payload (verified-contract values straight from the loaders — pass
     `Figure`/citation data through untouched, 「추정」 tags intact);
   - the signed **fact-row string** for the UI (`이벤트 검색 「{q}」 → {n}건 ·
     {유형} · {rcept_no}` — for multi-hit searches render count + the listed
     items the way the format implies; keep one obvious helper so S5 renders
     verbatim);
   - machine-readable fields S3 needs for citation forcing (the spans/quotes
     with their rcept_no).
   Specifics:
   - `search_events(query)`: corpus search over **exposable events only**;
     multiple candidates are legitimate (Finding 15 — unlike R4's
     unique-or-decline); 0건 returns the signed 「「{q}」에 해당하는 공시를 찾지
     못했습니다」 fact + 관제 현황판 pointer, never a guess. Scope-aware: when
     the context carries an event scope, that event is the natural first
     candidate but the tool still searches honestly.
   - `get_event(rcept_no)`: the verification contract for one event —
     exposable fields with quote/span/rcept_no via `resolve_event` +
     `load_detail`. Non-exposable/unknown → an honest not-found result (S3
     turns it into the right refusal family; the tool itself never refuses in
     prose).
   - `get_portfolio()`: authenticated account → its portfolio via
     `load_portfolio` (upstream D-day/금액 as served); anonymous → the **sample
     portfolio, labelled** (구성 예시 / 샘플 배너 rule; the signed fact row
     names it). Never an anonymous write, never client-supplied holdings.
   - `save_feedback(text, email?)`: writes through
     `mijual.web.conversationstore.record_feedback` with the context's
     session_hash; returns the fact for the signed confirmation copy
     (「의견을 저장했습니다 — 운영자가 확인합니다.」 rendering is S5's; the tool
     returns success/failure honestly — failure maps to the retry row).
   - `get_contact()`: reads the new Settings field (name it alongside
     `ops_id`/`vocky_api_key` conventions; default unset). Unset → an honest
     "no contact string configured" result — **never invent an address or a
     「준비 중」 line** (Finding 9).
3. **Gemini `FunctionDeclaration`s** — one per tool, names matching exactly,
   parameter schemas minimal and typed, descriptions written for the model
   (English is fine internally; user-facing strings stay Korean and signed).
   Export a `declarations()` (or similar) the S3 loop will hand to the SDK.
4. **Tests (terse)**: seed a couple of events the way existing web tests do;
   assert search finds/declines honestly, get_event returns citation-bearing
   contract values, anonymous get_portfolio serves the labelled sample,
   save_feedback lands a row, get_contact is honest when unset; and one
   boundary test asserting `mijual.agent` imports none of
   `mijual.dart`/`mijual.collect`/`mijual.extract` (the S4 re-aim will extend
   the scans; a simple import-walk here is cheap insurance). Keep the suite
   green: baseline **121 passed**.

## Boundaries

- No number computed anywhere — values pass through from `mijual.present` /
  `reads`. No re-derivation of exposure. No HTTP, no model call, no SSE, no
  frontend change, no `/ops` change.
- Korean strings only from the signed record (transcribe; the fact-row and
  0건 formats are copy). Inventing a Korean sentence is a design change.
- Do not modify `mijual.web.conversations` (port), `mijual.extract`, or the
  AST-scan tests (S4 re-aims them).

## Deliverables

- `src/mijual/agent/` with tools + declarations + `ToolContext`, the Settings
  contact field, tests. Full `pytest` green.
- `result.md` in this slice folder.
- `phase.md` notes: the tool result shape S3 will consume (payload/fact-row/
  citation fields), the ToolContext contract S4 must construct, the Settings
  field name, and any search-ranking decision. One-line **Doc impact** note
  (`backend`, `api`, `architecture` move here).
- `python3 scripts/workflow.py validate` passes. No commits, no status
  transitions.
