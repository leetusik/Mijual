# Result — P6.S1: 익명 대화 저장소 + `Conversations` 포트 구현

The seam P5 framed is filled. Two anonymous tables, a storage module with the
write API `P6.S2`/`P6.S4` will import, `DbConversations` over P5's protocol, and
`create_app`'s default flipped from `EmptyConversations` to the real thing — with
**no `/ops` route change and no frontend change**, which is what the seam was for.
The three ops tabs go from honest zeros to real rows.

## What landed

**Tables** (`src/mijual/db/models.py`, new section at the bottom):

- `ConversationTurn` / `conversation_turn` — `session_hash` · `created_at`
  (UTC stored, KST rendered) · `scope_rcept_no` (NULL = 전체 공시) · `question` ·
  `kind` (`answer`|`refusal`, DB `CheckConstraint`) · `answer` ·
  `refusal_category` · `evidence` (JSON list of rcept_no) · `quotes` (JSON list
  of verbatim spans). R7 §대화 로그's column list, transcribed column by column.
- `ConversationFeedback` / `conversation_feedback` — `created_at` · `text` ·
  `email` (nullable, the one signed exception) · `session_hash` (원 대화 링크).
- **No account/email/IP/UA column, and no foreign key at all** in either table —
  in either direction. 익명 세션 is derived (`GROUP BY session_hash`), not a third
  table, per R7's 「대화 로그의 집계면」.

**Storage module** `src/mijual/web/conversationstore.py`:

- `new_session_hash()` (`secrets.token_hex(16)`), `is_session_hash`,
  `session_hash_or_new` — random, never derived from IP/UA/account/email; a
  client token is accepted only if it has the minted shape.
- `record_turn(session, …)` / `record_feedback(session, …)` — the write API, off
  the port, flushing into the caller's transaction, reachable from no HTTP route
  in this slice.
- `DbConversations` — the three port reads: newest-first keyset pagination over
  an opaque `base64url(epoch_micros \x1f tiebreaker)` cursor, R7's three filters
  and no others, `next_cursor` omitted at the end.
- Constants `KIND_ANSWER`/`KIND_REFUSAL`, `REFUSAL_FAMILIES` (the five signed
  Korean names), `SCOPE_ALL_KO = "전체 공시"` (R6 §범위 모델's own words — no
  Korean was invented anywhere in this slice).

**Wiring**: `create_app`'s `conversations` default is now
`DbConversations(lambda: session_factory(app.state)())` — the mailer's seam shape,
built on the app's own lazy engine, so constructing an app still opens no
connection (verified). `EmptyConversations` stays exported and untouched.

**Row keys** are exactly the ones `frontend/components/ops/log.ts` names, so
`extraKeys()` finds nothing extra and the tables render with no frontend change:
log → `session_hash`/`at`/`scope`/`question`/`kind`/`refusal_category` (+ the
expanded `answer`/`evidence`/`quotes`, which `Conversations.tsx` reads from
`LOG_DETAIL_COLUMNS` and therefore does **not** turn into extra columns);
sessions → `session_hash`/`last_activity`/`questions`/`refusals`/`last_scope`;
feedback → `at`/`text`/`email`/`session_hash`.

## Decisions taken (recorded in `phase.md` note 18)

1. **An unknown refusal family is rejected at the write** (`ValueError`), as is a
   refusal without a family and a category on an answer. An invented family would
   be a row the signed filter can never find.
2. The five families are enforced **in the write API, not in the schema** —
   signed copy can be re-signed, and these rows (unlike every pipeline table,
   N16) are not re-collectable, so a re-signed family must not cost a destructive
   migration. `kind` *is* a DB constraint: two values, and they are the API's own.
3. **Open Question 1 taken as stated**: the turn is stored as the reader saw it;
   no portfolio/holdings column, no structured tool payload. No promise changed,
   so nothing was raised to the operator.
4. **`scope_rcept_no` NULL = 전체 공시**; the panel row says 「전체 공시」 (R6's
   signed words) rather than serving an empty cell that would read as missing.
5. **Two lists, no quote↔rcept_no pairing column** — R7 signs 근거 rcept_no 목록
   and 인용 칩 원문 as two lists. If `P6.S4` needs the pairing it adds a nullable
   column additively; the log's rows cannot be rebuilt.
6. **An unreadable cursor is a 400** (`ApiError("invalid_cursor")`), never a
   silent restart from page 1.

## Validation

| Command | Outcome |
|---|---|
| `.venv/bin/python -m pytest` | **121 passed** (P5 baseline 118 + 3 new) |
| `.venv/bin/python -m pytest tests/test_web_conversations.py` | 3 passed |
| `.venv/bin/python -m pytest tests/test_web_ops.py` | 8 passed |
| `python3 scripts/workflow.py validate` | OK |
| `create_app()` smoke | `DbConversations` wired, `isinstance(…, Conversations)` true, `app.state.engine is None` — construction still opens no connection |

The two AST scans that guard the request-path boundary
(`test_web_smoke.py`, `test_web_vocky.py`) are green untouched: the new module
imports no spending module and speaks no HTTP. Re-aiming them is `P6.S4`'s job
(phase Finding 1), and this slice did not disturb them.

**Tests added** (terse, three cases, `tests/test_web_conversations.py`):

1. the schema-level anonymity proof — walks both tables' columns for
   account/email/ip/user_agent/holding/portfolio names (feedback's `email` the
   sole allowed exception, spelled out so a second cannot arrive unnoticed) and
   asserts no foreign key crosses the conversation boundary in either direction;
2. the round trip — keys, newest-first order, the three filters, the cursor's
   page boundary, `next_cursor` omitted at the end, an unreadable cursor
   rejected, and the sessions aggregate's 질문 수/거절 수/마지막 범위;
3. the write API's vocabulary — the five families accepted, four kinds of bad
   input refused, and the handle guard.

**Test edited**: `tests/test_web_ops.py`'s fixture now passes
`DbConversations(factory)` (the panel is exercised against what it will actually
serve), and `test_the_conversation_port_serves_honest_zeros_and_no_join` gained a
closing block that records a turn + a comment and reads them back through the
three P5 endpoints — the proof that the tabs came alive with no route change. Its
docstring was updated from "P5 stores no conversations" to what is now true.

## Doc impact

Appended to `phase.md`'s running list (`P6.REVIEW` consolidates):
**`data`** · **`security`** · **`backend`** (+ a line in **`api`**) — the anonymous
conversation/feedback tables, the schema-level anonymity promise moving from
"trivially true, nothing stored" to implemented-and-asserted, the storage module
and its write API, and the three ops tabs now serving real rows. Suite baseline
118 → **121** (a **`qa`** line at review time).

## Deviations from `plan.md`

None in substance. Two things the plan left open and this slice chose:

- The plan said "find the production wiring the way the mailer is wired" — the
  mailer has no separate entrypoint wiring; its real transport *is* the
  `create_app` default. So `DbConversations` became the default there, and the
  module-level `app = create_app()` needed no change.
- The plan allowed "rejected **or** stored raw" for an unknown refusal category;
  rejection was chosen and recorded (decision 1 above).
