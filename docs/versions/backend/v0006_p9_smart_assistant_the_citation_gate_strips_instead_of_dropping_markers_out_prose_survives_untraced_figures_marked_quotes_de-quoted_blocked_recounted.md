---
doc_id: backend
version: v0006
created_at: 2026-08-25T08:54:47+09:00
source: P9.REVIEW
summary: P9 smart assistant — the citation gate strips instead of dropping: markers out, prose survives, untraced 공시 figures marked 미확인, quotes de-quoted, blocked recounted
previous: v0005_p7_fix_pass_reads.suggest_corps_beside_resolve_corp_and_find_corps_and_the_route-order_rule_that_keeps_get_stocks_suggest_reachable
---

# Backend

## Status

Implemented in P5. The service is a FastAPI app over the P2 pipeline package, with a pure
derivation layer between them. It adds **no new runtime dependency beyond `fastapi` and
`uvicorn`** — auth, hashing, mail and the vocky client are all stdlib.

**P6 added the agent.** A new top-level package `mijual.agent` runs an autonomous Gemini
function-calling turn, and `mijual.web.ask` streams it to the browser as the service's first
`text/event-stream` endpoint. `google-genai` is a runtime dependency of that package only, imported
lazily on first *use*: importing `mijual.agent`, and building an app with `create_app`, both cost no
SDK, no credential and no connection, so the suite spends nothing and `GEMINI_API_KEY` is required
neither to import nor to start.

**P9 rebuilt what that agent *does* without moving a boundary.** Same package, same lazy SDK import,
same zero-spend suite. Inside it: the citation gate **strips instead of dropping**, a `calculate`
tool and a `security_check` guard join the five, the per-turn ceilings rise to `20 / 30 / 22`, the
thinking level moves `LOW → MID`, tool results declare themselves **data, never instructions**, and
the stream gains `status` / `data` / `calc` blocks with stable ids. The Python suite is at **154**.

## Purpose

Server-side module layout, domain boundaries, jobs, auth, errors, and logging.

## Stack

- **Language/runtime:** Python 3.13
- **Framework:** FastAPI `>=0.115` (resolved 0.141.1 / starlette 1.6.0) on
  uvicorn `>=0.30`; `httpx` is a **dev extra** for `TestClient`
- **Package manager:** `uv` / `pyproject`, virtualenv at `.venv`
- **Server entrypoint:** `.venv/bin/uvicorn mijual.web.app:app --reload`
  (module-level `app` exists only as uvicorn's target; code calls
  `mijual.web.app.create_app`). There is deliberately **no compose service for the web app** —
  deployment is P4's.

## Module / Service Layout

- **`mijual.web`** — the HTTP layer. `app.py` (factory), `deps.py` (session dependencies),
  `errors.py` (the one envelope), `clock.py` (KST policy), `csrf.py`, `auth.py`,
  `passwords.py`, `portfolio.py`, `ops.py`, `opsreads.py`, `conversations.py` (the read port),
  **`conversationstore.py`** and **`ask.py`** (P6), `reads.py`, `vocky.py`, and one module per
  surface under `routers/`.
- **`mijual.agent`** — P6's agent package, the only place in the system that reaches a model from a
  request path:
  - `loop.py` — `run_turn(ctx, question, history, *, client, budget, now) -> Iterator[AgentEvent]`,
    a **sync generator**. The turn *is* the control flow (see *Domain Boundaries*).
  - `tools.py` — the **seven** server-side callables (`search_events` · `get_event` ·
    `get_portfolio` · `save_feedback` · `get_contact` · **`calculate`** · **`security_check`**)
    over `mijual.present` / `mijual.web.reads`, each returning a
    `ToolResult` of `fact_row` (the signed mono 도구 행, already composed) + `payload`
    (verified-contract values, fed back as the function response) + `citations` + `ok`. A result's
    `.evidence` / `.quotes` are literally `record_turn`'s 근거 rcept_no 목록 and 인용 칩 원문.
    **No tool computes a number and no tool writes prose**; `ok=False` exists only where the design
    signs a failure answer, so a 0건 search is `ok=True` carrying the signed sentence as a *fact*.
    Every result leaves **display-ready**: `ToolResult.__post_init__` runs `figures.with_display`
    over the payload, so the exact contract `value` travels with a `value_display` string beside it.
  - `citations.py` — the generation boundary (a **stripper** since P9, not a dropper).
  - `figures.py` — thousands grouping, and **presentation only**. `grouped()` turns a figure into
    the string a reader reads (`"3200"` → `"3,200"`), inserting commas into the integer part and
    moving nothing else — `frontend/lib/format.ts`'s own rule. **What counts as a figure is the
    contract's own predicate, not a key list:** a node carrying **both** `value` and `estimated`,
    which is exactly what `present.values.Figure.payload()` and `present.event.FieldPayload.payload()`
    emit — so `rcept_no`, `countdown.days`/`dday`, `window`, `span`, `event_id` and every date are
    structurally *not* figures and can never be grouped. `grouped()` additionally refuses a value
    below 1000 and a **14-digit bare integer** (that shape is a 접수번호 here; leaving one
    hypothetical 10조 amount ungrouped is cheaper than grouping one filing number). The module also
    owns `QUOTED_SPAN`, the one 「…」/"…" pattern `citations.py` verifies against — so the spans the
    gate checks are exactly the spans the grouping refuses to touch.
  - `client.py` — `AgentGeminiClient` (model `gemini-3.7-flash`, lazy import, key resolved on first
    use, **automatic function calling disabled** so the loop is ours), `CallBudgetExceeded` raised
    **before** a call, and `UsageLedger` (calls · tokens · thinking level · ▷ estimate).
  - `events.py` — the typed stream: `tool_row` · `citation` · `text` · `refusal` · `links` ·
    `footer` and exactly one terminal `TurnEnd(status ∈ done|aborted|error)`. A `citation` event is a
    *definition* emitted immediately **before** the `text` event that names its number, so a chip is
    painted with its sentence; a number is defined once per answer.
  - `instructions.py` · `copy.py` — the system instruction, and the signed Korean strings with their
    provenance (the tool row formats, the 0건 sentence, the five refusal sentences).
  - `context.py` — `ToolContext`, the frozen per-request server half: `session` · `today` (a KST day
    fixed once for the whole turn) · `session_hash` · `account` · `scope_rcept_no` · `settings`.
    **No tool takes an identity** — the model's declared arguments are only `query` / `rcept_no` /
    `text` / `email`, and `get_portfolio()` takes nothing at all, asserted by a signature test. That
    is what makes "no client-supplied holdings" structural rather than a review habit.
- **`mijual.web.conversationstore`** — P6's anonymous storage. Write API off the port (the port stays
  read-only): `record_turn(...)` and `record_feedback(...)`, both taking the caller's own session,
  both `flush` but never `commit` — the transport owns the transaction. `new_session_hash()` is
  `secrets.token_hex(16)`: **random, never derived** from IP/UA/account/email, and
  `session_hash_or_new()` **replaces** a missing or malformed client token rather than trusting it,
  which is also what keeps an address out of the column. Pagination is an opaque keyset cursor,
  newest first; an unreadable cursor is `invalid_cursor` (400), never a silent page 1. `DbConversations`
  is now `create_app`'s **default** (over the app's own lazy engine, the mailer's seam shape), so the
  three ops tabs went from honest zeros to real rows **with no route change**. 익명 세션 is *derived*
  (`GROUP BY session_hash`), never materialized, so a session cannot drift from its turns.
- **`mijual.web.ask`** — the SSE transport: the turn's decisions, framing, persistence and the
  limiter. `routers/ask.py` is the thin route over it, the same split as
  `portfolio.py` / `routers/portfolio.py`.
- **`mijual.present`** — the pure derivation layer (`values` · `event` · `money` · `summary`).
  **Every surface reads it; no endpoint re-derives a number.** Its constructors *refuse* to
  build what the design forbids: a blocked field, a date beside 추후결정, an untagged estimate,
  a won amount before 확정발행가 and a one-addend quote on a summed figure are
  **unconstructable**, not merely discouraged.
- **`mijual.web.reads`** — the batched read layer (`load_board` · `load_summary` ·
  `resolve_event` + `load_detail` · `load_stock` · `load_portfolio` · `corpus_as_of` ·
  `countdown_target` · `resolve_corp` · **`suggest_corps`**). It loads only the fields a surface
  renders. **P6 added three loaders and moved one assembly here; P7 added a fourth loader:**
  - **`event_payload(session, detail)`** — the event detail card's single assembly, lifted out of
    `routers/events.py` (which became one line over it) and now shared with the agent's `get_event`.
    So the agent can quote nothing the page would not show, **down to the key**, and
    `GET /events/{rcept_no}` is unchanged byte for byte.
  - **`find_corps(session, q, limit=5)`** — issuer lookup with the same normalization and tier order
    as `resolve_corp` (종목코드 → 회사명 verbatim → normalized → prefix → substring, first matching
    tier wins) but returning **several** hits instead of declining on ambiguity, because R6's search
    tool returns 이벤트 목록/단건 while R4's resolution is unique-or-decline. Two different contracts,
    deliberately.
  - **`load_corp_events(session, codes, today=)`** — every **exposable** event of those issuers as
    views, gated twice (persisted verdict **and** derived contract), keeping past events because a
    lapsed ① is the subject of a 놓친 돈 question. Ordering only — no number is derived.
  - **`suggest_corps(session, q, limit=8)`** (**P7**) — the 내 종목 조회 typeahead's candidate list.
    All-digit `q` → `stock_code` **prefix** plus the zero-padded exact; otherwise normalized-name
    **prefix, then substring**, with the tiers **unioned** and alphabetical inside each group. That
    union is why it could not reuse `find_corps` (first matching tier wins, limit 5, exact ticker
    only) and it is the invariant worth keeping: **every tier `resolve_corp` can hit is a *prefix*
    hit here**, so the row a bare submit would land on is always at the top of the list. It changes
    no resolution rule — `GET /stocks?q=` still declines on ambiguity — because candidates are the
    reader's choice, made before the submit, and a chosen one travels as the exact `corp_code`.
    Route-order rule for `routers/stocks.py`: **`GET /stocks/suggest` must stay declared before
    `GET /stocks/{corp_code}`**, or the handle route swallows `suggest` as a `corp_code`.
- **`mijual.db.repository`** — `readable_versions` · `document_of` · `current_version` ·
  `current_versions` (batched, no decode). Moved here from `mijual.extract.runner`, which
  re-exports them, so the exposure contract no longer reaches the extractor.
- **`mijual.beat`** — stdlib-only declaration of the beat schedule, window constants and the
  run-lock key, read by **both** the Celery app and the ops panel, so the panel can never
  render a schedule the worker is not running.
- **`mijual.mail`** — the mailer seam. `Message(to, kind, data)` carries **data, not rendered
  copy**; a `ConsoleMailer` dev transport prints and sends nothing.
- **`mijual.extract.labelfields`** — the free deterministic `본문-label` reader beside the paid
  schema-based one. It writes the same `Extraction` rows, so it is invisible to the gate layer,
  the exposure contract and the presentation contract. A second label field is a registry entry
  plus a gate, nothing more.

## Domain Boundaries

- **`web → present`, never the reverse.** `present` restates the instant-serialization policy
  rather than importing it back; a test pins the two together byte-for-byte.
- **No request-path module may import a spending module.** An AST import scan over
  `src/mijual/web/` fails the suite if one imports `mijual.dart`, `mijual.collect` or
  `mijual.extract`; `tests/test_present.py` applies the same scan to the derivation layer, and
  `tests/test_agent_tools.py` applies it to **`mijual.agent`** as well — the agent reads persisted
  rows, it never collects or extracts. Measured consequence: **`mijual.estimate` pulls `dart` +
  `collect` + `extract` at module level**, so retrospective 소멸가치 numbers reach a request path only
  from **persisted** state (`offering_input.inputs`, `performance_report.lapse`), written by an
  offline worker. Verified: `import mijual.web.app` pulls none of
  `dart`/`collect`/`extract`/`estimate`/`scheduler`/`evalset`, and no Celery.
- **The model is reached only through `mijual.agent`** (P6's re-aim of the old "no LLM call in a
  request path"). A fourth scan bans `google` / `openai` / `anthropic` anywhere under
  `src/mijual/web/**`, so no handler can talk to the model API itself and bypass the call budget, the
  citation gate or the ▷ ledger. `mijual.extract.client` is **not** imported by the agent even though
  its `GeminiClient` wrapper is tempting: it sits inside a package the request path may not reach.
  The two ideas worth keeping (a structural call budget, a recorded thinking level + ▷ ledger) were
  copied into `agent/client.py`, and the two clients diverged immediately anyway — JSON extraction
  versus streamed tool calls.
- **The agent decides; the loop enforces.** `run_turn`'s shape is
  `generate → (function_call? → execute → feed the result back) → repeat → answer`, and **no tool
  name appears in its control flow**: nothing is fetched before the model speaks or after it, no tool
  fires because a question matched a pattern, and no ordering is imposed on the calls it asks for.
  `call_tool` is invoked from exactly one place in the codebase, dispatching on the name the model
  supplied, and the turn ends when the model emits a round with no function calls. Even the reader's
  범위 is resolved with a plain row read into the system instruction rather than through a tool, so a
  scoped turn makes no call mandatory; the tool notes in the instruction say *advice, not
  instructions — you decide*. What the loop keeps is what must not be left to a model: the fact rows,
  the citation gate, the five signed refusal families, the links and footer composed from tool
  results **as data** (so the model never writes a URL — the agent carries no route string at all),
  the structural budget, and the ledger.
- **Strip, don't drop — the generation boundary stays, its judgement is gone (P9 / R16).** The
  model's prose still reaches `CitationGate` sentence by sentence as it streams, but the gate no
  longer decides whether a sentence may exist. Per rule, in one line each: **markers are removed**
  (a resolvable one becomes a numbered chip, and the whitespace that introduced it goes with it); an
  **uncited sentence ships**; an **untraceable 공시 figure becomes a `TextEvent.unverified` span** the
  surface marks 「미확인」; and a **「…」 quote occurring verbatim in nothing a tool returned loses its
  quotation marks** while the words survive as the assistant's own prose (인용문 재구성 금지 was not
  superseded — what must not reach the reader is the *claim of being 원문*, so the claim is what is
  removed). **Nothing is dropped and no turn is replaced.** `TurnEnd.blocked` now counts **markers the
  gate could not honour** — an id no tool returned, a malformed marker, half of one left by a dying
  stream — not sentences. The loop selects **no refusal family** at the end of a turn any more:
  `REFUSAL_FALLBACK` and its 「이 데이터는 검증을 통과하지 못했습니다」 sentence are deleted, which is
  the single change that stops a greeting being refused.

  **What was kept, deliberately:** the **closed citation space** (`learn()` — a `c7` exists only
  because a tool returned it, so an invalid citation is *unconstructable* rather than filtered),
  `_number_for` (같은 근거 = 같은 번호, now shared across 프로즈 · 데이터 행 · 계산 입력 through one
  public `cite()`/`cite_ref()` door), chip-arrives-with-its-claim, the sentence cut itself (so
  `TextEvent.citations` stays per sentence — a deliberate compatibility choice with the renderer,
  **not** where the event is heading), and a tool's own signed string reaching the reader byte for
  byte. **Two id spaces** are unchanged: the model cites `c7`, the reader sees chip `1`. Recorded
  honest limits: the number check is still *membership*, not semantics; a figure the **reader** typed
  is not a tool value and is therefore marked until it goes through the calculator, which returns it;
  and 오늘(KST) is handed to the model by the instruction rather than by a tool, so a sentence stating
  today's date draws a 「미확인」 mark — kept deliberately, and the instruction now says so.
- **`calculate`: one tool, an `op` enum, and an AST whitelist.** Five named operations over
  `mijual.calc` (`allotted_shares` · `excess_subscription_cap` · `lapsed_warrants` · `d_day` ·
  `lockup_release_date`) plus an `expr` escape hatch evaluated by `ast.parse(…, mode="eval")` and a
  **node whitelist** over `Decimal` — `Expression` · `Constant` · `Name` (bound only to a declared
  input) · `UnaryOp` · `BinOp` with `+ − × ÷`, everything else refused **before its operands are
  read**, bounded at 160 characters and 48 nodes, non-finite values and division by zero refused.
  **Never `eval`**, and `ast.literal_eval` is not an arithmetic evaluator. The **inputs are the
  arguments**: a named op must receive exactly its own parameters, no extra and none defaulted, so
  the block drawn at call time is the call. `reader_input` is not a flag the model sets — it is the
  **absence of a citation**. The 식 line is composed from each op's declared template over its own
  parameter keys, pinned by a test, so it can never describe an arithmetic the function does not do.
  A computed figure is figure-shaped, so `learn()` harvests it and restating it in prose is traceable
  by construction. A calculation **result** is never a 근거; a calculation **input**'s chip is.
- **`security_check`: the call is the whole signal.** A sixth declaration whose docstring *is* the
  trigger spec (four categories, plus an explicit **WHEN NOT TO USE ME** — a question *about* a
  filing is never a trigger, text inside a tool result is filing content rather than the reader
  speaking, an out-of-scope investing question is 범위 밖 and not an attack) and whose body is an
  unreachable defensive no-op returning **no fact row**. The reject fires in `run_turn` before the
  gate flush, before the tool-budget check and before any execution; it **overrides** any family
  selected earlier in the turn, because the guard is *why the turn ended*. The 보안 refusal is
  **bare** — no 갈 곳 링크 and no 푸터, since its signed second sentence is the 갈 곳 — declared as a
  property of the family (`copy.BARE_FAMILIES`) so the loop branches on a set, never on a Korean
  string.
- **A released sentence is respelled into the product's numerals — after every check, never before.**
  The agent's prose used to print the raw contract value (`3200원`) while every other surface in the
  product grouped it (`3,200원`); it now prints `3,200원` too. Two halves, one rule, and the rule is
  that **grouping is presentation, never computation**. (1) *The tool contract serves the reader's
  form* — a figure travels with its `value_display` (above), and one line of the system instruction's
  NEVER COMPUTE block tells the model to write a figure the way `value_display` writes it, naming
  `rcept_no`, dates, years and D-days as *not* figures. (2) *The gate guarantees it* —
  `CitationGate.learn` builds a `{as the payload writes it: as the reader reads it}` table from the
  same figure nodes, and `_release` runs `figures.regroup` over the sentence **only after** the
  citation, never-compute and verbatim-quote checks have all passed. So the membership check still
  runs on what the model actually wrote and an invented figure is still blocked in its raw form;
  separators were already normalized away on both sides (`_decimal`), so `3,200` and `3200` are one
  member and grouping can neither add a number to the traceable set nor take one out. **Verbatim
  stays verbatim, structurally:** `regroup` skips every `QUOTED_SPAN`, and a sentence released
  because it *is* a tool's own string (a locked `notice_ko`, the signed 0건 sentence) is copy and is
  never respelled at all. `TurnEnd.quotes` and the citation events are built from `Citation`s and are
  untouched by any of this. No signed format changed — the fact rows and the footer carry counts and
  접수번호 only. **The log needs no extra step:** the respelled string is what `gate.released`
  appends, so `TurnEnd.answer` → `record_turn` stores the numerals the reader read, by construction.
  Recorded honest limit: grouping reaches **contract figures only**, so a bare integer that is a
  genuine quantity but not a `Figure` — `holdings[].shares` in the portfolio payload — is still
  spoken ungrouped (the sample's holdings are 500/300/500/100, so nothing is visible today; a real
  account holding ≥1000 shares would read `1500주`). Widening the predicate means naming keys by
  hand, which is the drift this seam exists to avoid.
- **Refusal families are recognised, not generated — and after P9 only four are recognisable.**
  The signed sentences live verbatim in `agent/copy.py`, keyed by the exact family names the ops
  filter sends; the gate cuts a family sentence out of the stream and emits it as a `refusal` event.
  Matching is **exact string match in three places** (`copy.family_of`, `citations._family_at_head`,
  `citations._is_family_prefix`), which is why retiring a family is a code change rather than a copy
  edit. P9 split the producer side from the stored vocabulary: `copy.RETIRED_FAMILIES` holds
  `계산 요청` and `검증 미통과 폴백`, and every recogniser reads the **live** mapping, so a model that
  happens to type a retired sentence now writes prose rather than a stored row of a family nobody may
  newly record. The stored whitelist keeps **all six** (`철회 · 확정 전 · 공시에 없음 · 보안 · 계산
  요청 · 검증 미통과 폴백`) because past rows must stay findable, and it is mirrored value-for-value in
  the ops filter. 「보안」 is recognised like any other live family, deliberately: a model that types
  the signed sentence itself has refused in the record's own words, and the honest record is a 보안
  row the operator can filter for. `_feedback_only` survives, narrowed: it no longer avoids a
  fallback (there is none) — it exists so a save turn whose model says nothing at all still stores the
  signed confirmation.
- **The exposure contract is not re-decidable.** `gates.exposure.exposure_of` is the single
  derivation and the API renders what it says — `load_board` skips a row whose live verdict
  disagrees with the persisted column.
- **Only `web/vocky.py` may import an HTTP client** (`urllib`/`http.client`/`socket`/
  `requests`/`httpx`), asserted by a test, so a later slice cannot quietly put a second
  external dependency on a request path.

## Auth and Session Logic

- **The session is a row, not a signed cookie.** `auth_session` holds a **digest** of the
  token, never the token; 로그아웃 deletes the row and 계정 삭제 cascades. A stateless cookie
  would have needed a revocation list — i.e. this table — and saved no query.
- **`MIJUAL_SESSION_SECRET` peppers, it does not sign** (HMAC-SHA256 over the token), so a
  database dump holds nothing replayable and rotating the key logs everyone out. Unset is a
  development state: unkeyed SHA-256 plus one log warning.
- **scrypt from the stdlib**, `n=2**14, r=8, p=1` — ~25 ms/hash and the largest `n` that fits
  OpenSSL's **default `maxmem`**. Hashes carry their own parameters, so an upgrade bumps
  `passwords.CURRENT` and `needs_rehash` re-hashes each account at its next successful login.
- **CSRF is service-wide middleware, not a per-route dependency.** Every unsafe method must
  carry `X-Mijual-CSRF` or it is refused before the route runs. A cross-origin page cannot set
  a custom header without a preflight this service does not grant, so nothing is minted,
  stored or rotated.
- **Two session dependencies, and a GET can never write.** `DbSession` is rollback-only (it
  rolls back on the way out of *successful* requests too); `WriteSession` commits on success,
  rolls back on any exception, and **refuses a safe HTTP method outright**. **A streaming response
  can use neither** — see the next section.
- **The operator door is a credential with no row.** `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD`
  from the environment; no operator account, no admin flag, no signup, no reset. `ops_session`
  carries **no `account_id`, no FK and no operator identifier at all**.

## Streaming (`POST /ask`, P6)

The service's first `text/event-stream` endpoint, and it broke three assumptions worth writing down.

- **⚠ A streaming response cannot use `WriteSession` — or any `yield` dependency.** FastAPI tears a
  `yield` dependency down when the **handler returns**, which for a `StreamingResponse` is *before
  the first frame*. So `ask.py` opens its own session inside the body iterator and commits it from
  the response's **`BackgroundTask`** — the one hook Starlette runs on **both** exits, stream
  finished and client disconnected (measured, not assumed). The transport owning the transaction is
  also what makes the tools' `save_feedback` flush become real. **Do not "simplify" this back onto
  `deps.WriteSession`.** Tests fill `app.state.session_factory` directly for the same reason: the
  endpoint opens its own session, so there is no dependency to override.
- **⚠ Absorb an event *after* yielding its frame, never before.** Measured: with the obvious
  ordering, a turn cut mid-answer stored **one sentence more than the client had been sent** — the
  sentence was produced, absorbed, then lost to the cancelled send. Being resumed past a `yield` is
  the proof that the consumer took the previous frame. Any later change to the frame generator must
  keep that order.
- **Persistence covers the broken turns too.** `done` / `aborted` / `error` all persist from the
  terminal event alone, whose fields *are* `record_turn`'s arguments — so the log can never disagree
  with what the reader saw. A **disconnect has no terminal**, so the row is rebuilt from the frames
  actually written, asserted equal to the terminal's fields by test. A 중지 **before the first
  sentence** stores nothing: there is no 답변 to replay and no 거절 to categorise, and the row would be
  noise in a log whose purpose is 품질 점검. The row records **what the reader saw and nothing about
  the mechanism** — `aborted` versus `error` lives in the server log, because the signed columns
  carry no status bit and none was added. A `record_turn` failure rolls the **whole** transaction
  back, feedback included: a 대기열 row pointing at a turn that was never written is worse than no row.
- **There is no stop endpoint, deliberately.** 중지 is the reader aborting the fetch, which stops the
  consumer pulling, which closes the generator. A stop route would need a server-side registry of
  running turns whose only job is to cancel what the socket already cancels. Nothing is retracted;
  released text stands.
- **Rate limiting exists and says nothing.** `ask.TurnLimiter` on `app.state.ask_limiter`, in
  process, **persisting nothing and holding no address**: a `max_concurrent` ceiling (an integer,
  unevadable, and the thing that actually bounds money and latency) plus a per-session-handle window
  (which bounds a runaway tab and is *trivially evaded* by minting a fresh handle — stated rather
  than hidden). **No IP or UA counter even in memory**: that would put the forbidden identifier in
  the process on the strength of "it's only in memory". A refused turn is `429 rate_limited` in the
  plain envelope with **no `message_ko` and zero UI copy anywhere**, because a limit that is not
  shown must not be implied. An in-flight slot carries a TTL so a lost one self-heals instead of
  wedging the endpoint. **Per process** — cross-process state is P4's, same parking as login rate
  limiting.
- **The injection seam is `create_app(agent_client=…)` — a *factory*, not a client**
  (`Callable[[], ModelClient] | None`), because the call budget and the ▷ ledger are per turn.
  `None` means each turn builds its own live client. Tests and the SSE smoke pass a scripted model,
  which is why the whole suite spends nothing.

## Background Jobs / Workers

- **`python -m mijual.estimate snapshot`** — writes the serving precomputation
  (`offering_input` rows + `performance_report.lapse`). 0 requests, 0 LLM calls, idempotent.
- **`python -m mijual.estimate reparse`** — re-reads every stored 실적보고서 from its own
  `payload_bytes` and rewrites only the parse-derived columns. This is how *any* future
  `parse_performance` change reaches the corpus without spending a request.
- **`python -m mijual.extract labels`** — the free label-field pass. Runs **first inside
  `stage_extract` and outside `extract_max_calls`**: budgeting a pass that spends nothing could
  only starve it.
- The beat pipeline is now `collect → bodydoc → extract → gates → reparse → snapshot`, and
  every run writes a `pipeline_run` row (opened before the first stage, closed after the last).

## Error Handling and Logging

- One envelope, four handlers (`ApiError`, `HTTPException`, validation, bare `Exception`); the
  500 handler logs the traceback and returns **only** the code — no exception text in a body.
- The vocky client never logs its key, the response body or the exception text, and vocky's
  error text is never echoed onto the panel.
- **The agent's model errors carry the exception type name only** (`GeminiError("ClientError")`),
  never a message that could contain a URL or a credential. Once a stream has started the only
  failure mode is the typed `error` terminal — never a half-frame; everything refusable is refused
  **before** the first frame, in the ordinary envelope with no Korean.
- **The ▷ ledger is one server-log line per turn** (`agent turn done · answer · rounds N · tools N ·
  blocked N · calls N · tokens … · thinking LOW · ▷ $X estimated (rate card, not billed)`), rendered
  by the ledger's own `.render()` so there is one renderer and one rate card. Agent spend joins **no**
  signed ops panel: R7 signs 정확도·비용's LLM spend as extraction-call aggregation specifically, and
  adding an agent row there would be a design change this phase may not make.
- A run-log failure is swallowed into a run note: a log that can kill a pipeline is worse than
  no log.
- Redis is optional at request time — the lock chip degrades to `state: "unknown"` with a
  reason and the tab still answers 200.

## Open Questions

- The serving process creates no schema at startup (it must answer while Postgres is down), so
  tables land through a pipeline entry point's `create_all` + `ensure_columns`. **P4** must
  ensure they exist before the API serves a fresh database — and P6 made that concrete: the
  **`conversation_turn` / `conversation_feedback` tables must be created before the first
  `POST /ask`**, or every turn fails at persistence.
- Pool sizing, `pool_pre_ping` and read-replica routing are noted in `deps.py` as **P4** deploy
  decisions.
- Rate limiting on the two login endpoints needs cross-process state and stays **P4**'s — and so does
  the ask limiter's, for the same reason.
- **The ▷ ledger line needs a root logging configuration at deploy.** It is `log.info` on
  `mijual.web.ask`, and uvicorn configures only its own loggers, so under a default `uvicorn` the
  root stays at `WARNING` and **agent spend is recorded nowhere** (verified both ways). Nothing was
  added to the app, because putting `basicConfig` in a library pre-empts the deploy's own choice.
- **`Settings.operator_contact` / `MIJUAL_OPERATOR_CONTACT` has no default and deliberately no
  `require_` accessor**: nothing may fail for want of the operator's contact string and nothing may
  substitute for it. Unset, `get_contact` answers that it has no contact string — it never invents an
  address or a 「준비 중」 line. The real value is the operator's to supply at deploy.
- **There is no heartbeat on the stream.** The turn is sync and blocking, so a keep-alive comment
  needs a timer; the longest observed inter-frame gap with the live agent is **6.0 s**, so a proxy
  idle timeout below ~10 s would cut a legitimate turn. **P4**'s.
