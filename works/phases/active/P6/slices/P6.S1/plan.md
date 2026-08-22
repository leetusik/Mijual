# Plan — P6.S1: 익명 대화 저장소 + `Conversations` 포트 구현

## Goal

Land the server-side anonymous conversation storage (R6-6) and replace P5's
`EmptyConversations` with a real DB-backed implementation of the
`mijual.web.conversations.Conversations` protocol, so the three ops tabs
(대화 로그 · 익명 세션 · 피드백) go from honest zeros to real rows — **with no
`/ops` route change and no frontend change**. Schema-level anonymity is the
slice's core deliverable, proven by a test.

## Read first

- `works/phases/active/P6/phase.md` — Findings 1–4, 12, Constraints, and Open
  Question 1 (its stated default is binding for this slice: store the turn as the
  reader saw it; never add a portfolio/holdings column; never store the tool's
  structured portfolio payload).
- `docs/reference/design/rounds/07-admin/output/build-prompt.md` — §대화 로그
  (line ~67), §사용자 (~78), §save_feedback 대기열 (~91). This signs the column
  set. READ-ONLY.
- `src/mijual/web/conversations.py` — the port. Its docstring carries the three
  inherited rules (no account/email/IP/UA anywhere; read-only port; opaque-cursor
  newest-first pagination). Do not change the protocol or `Page`.
- `src/mijual/db/models.py` — table conventions (Account section ~line 728 shows
  the anonymity commentary style and the FK/cascade conventions), and
  `schema_sync.py` / `__init__.py` for how tables come into being
  (`create_all`-based; additive columns via `ensure_columns`).
- `src/mijual/web/app.py` (~line 76–90) — the `create_app(conversations=…)` seam,
  and wherever the serving entrypoint builds the real app (find the production
  wiring the way the mailer is wired; wire `DbConversations` there).
- `src/mijual/web/routers/ops.py` (~line 72) and `src/mijual/web/opsreads.py` —
  how the three tabs call the port and how existing ops rows format values
  (match the KST display convention already in use).
- `frontend/components/ops/log.ts` — the exact row keys the built panel reads
  (phase.md Finding 3 lists them; serve exactly those).

## What to build

1. **Tables** (in `src/mijual/db/models.py`, following its section-comment and
   docstring conventions):
   - **Conversation turn** (the 대화 로그 row): `session_hash` · created-at
     (UTC stored, KST rendered like the rest of ops) · `scope` (이벤트 rcept_no
     or 전체) · `question` · `kind` (`answer` | `refusal`) · answer/refusal
     prose · `refusal_category` (nullable; one of the five signed Korean family
     names — `철회`·`확정 전`·`공시에 없음`·`검증 미통과 폴백`·`계산 요청`) ·
     근거 rcept_no 목록 · 인용 칩 원문 (verbatim quotes). List-shaped values may
     be JSON columns — pick what the existing models already do for list data.
   - **Feedback** (the `save_feedback` 대기열 row): created-at · `text` ·
     `email` (nullable — present **only** when the user volunteered it; this is
     the one signed exception to "no email column", it lives with the feedback
     row and joins to nothing) · `session_hash` (원 대화 링크).
   - **익명 세션 is "대화 로그의 집계면"** (R7's words) — prefer deriving the
     sessions page by aggregation over the turn table (세션 해시 · 최근 활동 ·
     질문 수 · 거절 수 · 마지막 범위) rather than a third table; if you find a
     concrete reason to materialize it, record the reason in `phase.md`.
   - **No account/email/IP/UA column in any of this** (feedback's voluntary
     reply email excepted, as signed). No FK to `account` or any auth table.
     No portfolio/holdings column, no structured tool-payload column.
2. **Session handle**: a small helper that mints the anonymous session
   identity. Guardrails: it must be **random/opaque, minted server-side or
   accepted as an opaque client token — never derived from IP, user-agent,
   account, or email** (hashing PII would smuggle the join back in). The client
   (P6.S4/S5) will hold it in sessionStorage next to the thread; storage only
   ever sees the hash string. Keep the mint/validate helper in the new storage
   module so S4 can import it.
3. **`DbConversations`** — implement the three port methods over the tables:
   newest-first, opaque cursor (encode e.g. the last row id/timestamp; the port
   layer never interprets it), `Page(rows, total, next_cursor)` with
   `next_cursor` omitted at the end. Row mappings must use exactly the keys the
   panel reads (Finding 3): conversations → `session_hash`/`at`/`scope`/
   `question`/`kind`/`refusal_category` (+ expanded `answer`/`evidence`/
   `quotes`); sessions → `session_hash`/`last_activity`/`questions`/`refusals`/
   `last_scope`; feedback → `at`/`text`/`email`/`session_hash`. Honor the
   signed filters (`kind`, `refusal_category` — the five Korean strings —
   `session_hash`).
4. **Write API for later slices** (not on the port — the port stays read-only):
   module-level functions or methods on the storage class, e.g.
   `record_turn(...)` and `record_feedback(...)`, used by S2 (`save_feedback`)
   and S4 (per-turn persistence). Terse, typed, documented. No HTTP endpoint in
   this slice.
5. **Wiring**: pass `DbConversations` where the real app is composed, exactly
   like the mailer seam. `EmptyConversations` stays for tests that want it.
6. **Tests (terse, high-value)**:
   - the schema-level anonymity proof: walk the new tables' columns and assert
     no `account`/`email`/`ip`/`user_agent`-shaped column exists (feedback's
     `email` the sole, explicitly signed exception) and no FK reaches `account`;
   - a round-trip: record turns + feedback, read back through the port with
     filters and cursor, assert row keys and newest-first order;
   - the five refusal-family strings accepted; an unknown category rejected (or
     stored raw — pick one, record which in `phase.md`).
   - Run the whole suite: `pytest` (P5 baseline 118 passed — keep it green).

## Boundaries

- **No `/ops` route or response-shape change; no frontend change.** If a served
  key renders raw in the panel, the key is wrong — fix the key, not `log.ts`.
- Do not touch `mijual.agent` (doesn't exist yet — S2's job), the SSE transport
  (S4), or any surface code.
- No mutation on the port; the write API is separate and unexported to HTTP.
- Never invent Korean copy; strings that render in the panel come from the data
  itself, and empty states already exist in P5.
- RESPECT THE DESIGN: R7's column set is the schema, column by column — nothing
  dropped, nothing extra that changes the promise.

## Deliverables

- New tables + storage module + `DbConversations` + wiring + tests, all green.
- `result.md` in this slice folder (free-form, from scratch).
- Append durable cross-slice notes to `phase.md` (at minimum: the storage
  module path and write-API signatures S2/S4 will import; the session-handle
  scheme; the cursor encoding; any decision taken on Open Question 1's default
  or the unknown-category behavior). Add a one-line **Doc impact** note
  (`data`, `security`, `backend` move here).
- `python3 scripts/workflow.py validate` passes. No commits, no status
  transitions.
