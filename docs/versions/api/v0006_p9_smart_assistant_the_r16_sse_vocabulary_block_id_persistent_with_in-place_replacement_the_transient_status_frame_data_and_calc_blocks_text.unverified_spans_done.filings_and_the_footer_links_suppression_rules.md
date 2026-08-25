---
doc_id: api
version: v0006
created_at: 2026-08-25T08:52:44+09:00
source: P9.REVIEW
summary: P9 smart assistant — the R16 SSE vocabulary: block_id/persistent with in-place replacement, the transient status frame, data and calc blocks, text.unverified spans, done.filings, and the footer/links suppression rules
previous: v0005_p8_design_polish_pass_post_feedback_write-only_outward_and_next_lapse.tie_count_on_get_board_summary
---

# API

## Status

The service exists. P5 built the whole HTTP surface over the P2 exposure contract:
FastAPI (`mijual.web`), no prefix on reader routes, `/ops` for the operator panel.
**P6 added `POST /ask`** — the API's first streaming endpoint — and filled the conversation port, so
the three ops conversation tabs serve real rows with no route change. **P7 added one read-only route,
`GET /stocks/suggest`** — the only contract change of that fix pass. **P8 (디자인 폴리시 패스)
added two things and nothing else: `POST /feedback` — the service's first *outward write* — and
`next_lapse.tie_count` on `GET /board/summary`.** **P9 (스마트 어시스턴트) added no route at all**:
it extended the `POST /ask` event vocabulary, additively — every pre-R16 frame is byte-identical to
what it was, and the new fields ride only when non-empty. Every contract below is
implemented and live-verified against the corpus. Deployment and the D-day mail channel are **not**
here (P4).

## Documentation Rules

- Only document a contract as stable when it is implemented or explicitly accepted.
- Mark experimental surfaces as draft.
- Record breaking changes once external consumers exist.
- Keep public contract changes synchronized with product, experience, frontend, backend, data, and security docs when boundaries change.
- Update this doc by creating a new version under `docs/versions/api/`, not by patching old versions.

## Contract-wide rules

These hold on every route and are enforced in code, not by convention.

- **The error envelope is the only error shape.**
  `{"error": {"code", "message", "message_ko"?, "fields"?}}`. `code` is a stable English
  `snake_case` token; `message` is English and **developer-facing — never rendered to a
  user**; `fields` is 422-only. **`message_ko` appears only where the product already owns
  that Korean string** (e.g. `WITHDRAWN_NOTICE_KO`) and is **omitted, not null**, otherwise.
  The signed design writes no HTTP-error copy at all — it writes *state* copy, which arrives
  in a normal 200 payload — so inventing Korean error copy would be a design change. Handlers
  cover `ApiError`, `HTTPException`, validation and bare `Exception`; there is no path back to
  FastAPI's `{"detail": …}`. The 500 handler logs the traceback and returns only the code.
- **Absent means the key is absent, never `null`.** A blocked, missing or unconstructable
  value is omitted. `null` appears only where the server genuinely has a null to state.
- **Every value carries `estimated`.** A `Figure` with no `estimated`, or a quote on an
  estimate, is unconstructable (`present.Figure` raises). An estimate can therefore never
  render untagged and a fact can never carry the mark.
- **Serialization.** Money and every ratio are **exact decimal strings**, never rounded and
  never floats (배정비율 keeps all ten decimals); counts are `int`; calendar dates are bare
  `YYYY-MM-DD` with **no offset** (청약일 / 매매기간 / 전환청구 개시일 are calendar days);
  instants are absolute **`+09:00`** second-precision KST strings. D-days are computed
  upstream in KST — the browser only diffs.
- **Keys are English `snake_case`; Korean appears only as content** (`label_ko`,
  `korean_name`, `notice_ko`). Scripts are never mixed inside one JSON contract.
- **Citations are three states and no fourth.** A value carries **either** `quote` + `span`
  (one cell) **or** `parts` (≥ 2, each `{quote, span}`, summing exactly to `value`) **or**
  neither (no chip; `rcept_no` still links to DART). Every other combination is
  unconstructable, so a one-addend quote posing as a whole number cannot be served.
- **A reader payload carries no gate reason code and no report `reason` string.** Why a field
  is missing is operator truth (D-14); only the `/ops` surfaces read it.
- **Every unsafe request must carry `X-Mijual-CSRF`** (any non-empty value) or it is refused
  `403 csrf_required` before the route runs.
- **Anonymous is a result, not a 401** — `GET /auth/me` answers `{"authenticated": false}`,
  the same shape a search miss uses.
- **No OpenDART call happens in any request path; the model is reached only through
  `mijual.agent`; `mijual.web` itself speaks HTTP in exactly one file.** P6's AI 질문 agent is an
  LLM call in a request path **by design** — SSE cannot be anything else — so the old absolute
  sentence was re-aimed into these three clauses, each carried by its own AST import scan in the
  test suite (a fourth scan keeps spending modules out of `mijual.agent` too). The OpenAPI
  `DESCRIPTION` states the corrected sentence, because it is an outward surface.
- **Exactly one endpoint streams, and only it may.** Every other route returns a complete JSON body.

## The presentation contract

`mijual.present` is the single derivation layer; **no endpoint re-derives a number**, so two
surfaces cannot disagree about the same figure. The named shapes:

- **`countdown`** — `{label_ko, date, dday, days, window, window_state, reference, source}`,
  one governing anchor per rights type: ① 증서 매매 마감 · ② 전환청구 **개시** · ③ 반대의사 통지
  마감. A past ② opening is **진행 중**, never 종료.
- **`corp_name_in_body` / `corp_name_agrees_with_body`** — display shows the DART master
  `corp_name`; a 본문 disagreement is a **stated fact**, never a silent correction.
- **`offering_inputs`** (①) — 예정/확정발행가, 할인율, 배정비율 to its full ten decimals,
  초과청약 비율, `final_price_date`, `unit_value`, `unit_value_floor`. **`확정발행가 null` ⇒ no
  money number at all, anywhere.**
- **`lapse_result`** — 발행 증서 / 증서 청약 / 소멸 주수 / 소멸률 / per-offering 소멸가치 + 하한.
- **Field payloads** — `{value, display ("value"|"추후결정"), quote, span, rcept_no,
  korean_name}`. A gate-blocked field is **absent from the payload**, not a null; a `추후결정`
  field never carries a date.
- **발행사 기재 불일치** — two readings side by side, each with its own citation, **never
  reconciled**; the footer states only which reading the totals use.
- **Board/landing aggregates** — one `BoardSummary` so the landing's cards can never disagree.

## Contracts

### Health

- `GET /health` — liveness only. **Deliberately does not touch Postgres**: a probe that flaps
  with the database turns one outage into two. Data freshness is a separate corpus fact served
  by `/board/summary`.

### Board and events (reader, anonymous)

- `GET /board/summary` — every landing number in one object: 감시 중 · 30일 이내 · 소멸 앞둔 ·
  읽은 실적보고서 · the 「추정」 headline + band floor · 소멸/발행 증서 · 소멸률 ·
  `next_lapse{date, corp_name, target, tie_count}` · `freshness{as_of, stale, age_hours,
  stale_after_hours}`. **`tie_count`** (P8) is how many ① offerings share that earliest 청약 마감 — `1`
  when only the named one does, `3` on the corpus as it stands. It is derived from the same ordered
  `lapse_pending` list the strip and the board already read, so the two can never disagree, and the
  key is present **only when `next_lapse` is**. It exists because the 소멸주의보 headline says
  「N개 종목」 on a tie rather than picking one company out of a tied set.
- `GET /board?rights=R1|R2|R3` — `counts` (tabs, **always whole-board**) · `rows` (D-day
  ascending, `days >= 0`) · `open_now{count,total,rows}` (② 진행 중) · `tbd{…}` (일정 추후결정,
  unranked) · `reference` · `freshness`. Nothing is paged.
- `GET /events/{rcept_no}` — the detail card: the event view + `corrections` teaser + ①
  `offering` / `lapse_result` / `issuer_disagreement` + ② `convertible` (R3's six values) +
  철회 `withdrawal`.
- `GET /events/{rcept_no}/corrections` — the CorrectionStory: version rail
  (`is_current_readable` on at most one row) + `field_moves` + `interpretation` verbatim.

**The route key is `rcept_no`, resolved against every stored `FilingVersion`,
renderable-first** (`exposable` → `withdrawn` → rest, then newest 최초 접수일): `rcept_no`
mutates to the newest version, so yesterday's link must still open the page. `event_id`
travels in every payload as a stable handle. **A non-renderable event is a 404 envelope** —
the API never renders a page explaining why an event is not exposed. A 철회 event returns its
notice and its withdrawal evidence and **nothing else**: no fields, no countdown, no old dates.

Two stated defaults, both overridable without a code change:
`next_lapse.target` = end of the 청약 day (00:00 KST of the next day, R2's own assumption)
behind `MIJUAL_COUNTDOWN_CUTOFF_TIME`; **stale after 18 hours** behind
`MIJUAL_STALE_AFTER_HOURS`, derived from the 07:30/19:30 KST beat schedule.
**기준시각 is `max(Event.last_seen_at)`** — a corpus fact, never the request time — and
`stale` / `age_hours` are **served**, so no client times staleness against its own clock.

### 내 종목 조회 (reader, anonymous)

- `GET /stocks?q=<종목명|종목코드>` — resolution **and**, on a hit, the whole page:
  `{query, found, stock, reference, rights, lapse}`. **A miss is `200 {"query", "found": false}`**
  — a search that finds nothing is a *result*, not an error, and it names no reason, candidate
  or near-miss.
- `GET /stocks/suggest?q=<종목명|종목코드>` (**P7**) — the reader's own candidate list, *before* the
  submit: `{query, candidates: [{corp_code, corp_name, stock_code}, …]}`, **at most 8**, and `200`
  with an **empty list** when nothing matches (never a 404). `q` is its **only** parameter, so the
  "no holding count is ever received here" promise below holds unchanged. Matching is
  `reads.suggest_corps`: all-digit → `stock_code` prefix + the zero-padded exact; otherwise
  normalized-name **prefix then substring**, tiers **unioned** (unlike the agent's `find_corps`,
  where the first matching tier wins), alphabetical inside each group. **It must stay declared
  before `GET /stocks/{corp_code}`** in `routers/stocks.py`, or the handle route swallows
  `suggest` as a `corp_code`.
- `GET /stocks/{corp_code}` — the same page by stable handle. An unknown code **is** a 404.

Resolution is four unique-or-decline tiers (종목코드 exact → 회사명 verbatim → 회사명 normalized →
unique normalized prefix); **ambiguity resolves to nothing**. **The rule that ambiguity is never
guessed at is unchanged by `suggest`** — and the distinction is the whole reason the route was
allowed: the defect class the rule guards against is *the system* silently opening a different
company's 놓친 돈, while a candidate list is the **reader's own choice**. So: the submit path still
declines on ambiguity and the miss payload still names no reason, candidate or near-miss; candidates
exist only on their own route, before the submit; and a chosen candidate travels as the **exact
handle** `/stocks/{corp_code}`, never as a second fuzzy resolve. `rights` rows carry the
detail-grade `offering` on ① and the six-value `convertible` strip on ②. `lapse` =
`{coverage, totals, rows, pending?}`, each row's event-derived block gated on the 유상증자결정
being exposable.

**These endpoints serve factors, never products.** No holding count is accepted on any path
and no per-holding number appears in any payload — so the product has exactly one
multiplication site and 조회 and 포트폴리오 cannot disagree. **The coverage boundary is served**
(`{start: 2026-01-01, end: <today KST>, convertible_start: 2025-06-01}`), and anything outside
it is **absent rather than zero**.

### Auth (reader)

`POST /auth/signup` (201) · `POST /auth/login` · `POST /auth/logout` · `GET /auth/me` ·
`POST /auth/reset/request` · `POST /auth/reset/confirm` · `DELETE /auth/account` ·
`PATCH /auth/account` (수신 주소 변경).

Structural codes, **none carrying Korean** — the single body line is the client's:
`email_taken` 409 · `invalid_credentials` 401 · `password_too_short` 400 · `invalid_email` 400 ·
`invalid_reset_token` 400 · `unauthenticated` 401 · `csrf_required` 403. The account payload is
`{email, created_at}` and nothing else. A login failure is **one code for both causes** and the
miss path burns a scrypt verification so the timing matches. A reset request answers
`{"requested": true}` for a known and an unknown address alike, and the link travels only
through the mailer.

### 내 포트폴리오 (reader, the product's **only** gated surface)

`GET /portfolio` (one read: `holdings` with each one's 진행 중인 권리 요약, plus **`upcoming`**
and **`past`** and the KST `reference` day) · `POST /portfolio/holdings` (201) ·
`PATCH|DELETE /portfolio/holdings/{id}` · `PUT|DELETE /portfolio/claims/{rcept_no}` ·
`GET|PUT /portfolio/notifications` · **`GET /portfolio/sample` (anonymous, read-only)**.

New codes: `holding_exists` 409 · `invalid_shares` 400 · `invalid_lead_days` 400.
Statements worth their own lines: **a ②/③ portfolio row carries no won amount at all**;
**an open ② is in `upcoming`, never in `past`**, because "지나간" is the 종료 label the design
forbids; **`claimed` is absent, never `false`, when there is no account**; **a stranger's row
is a 404, not a 403**; and **there is no anonymous write endpoint at all** — 세션 이월 and
샘플 이전 are client offers that produce ordinary authenticated writes.

### AI 질문 (reader, anonymous, **streaming**)

**`POST /ask`** — the API's first and only `text/event-stream` endpoint, and the only place a model
call happens in a request path.

- **Request.** CSRF header required (the service-wide guard, no exception). Body
  `{question, scope_rcept_no?, session?, history?}`. `session` is the anonymous handle the browser
  got back from a previous turn; `history` is oldest-first plain prose, capped at the newest few
  turns and a per-turn character ceiling — **dropped, not refused**, so a long-lived tab keeps
  working. `scope_rcept_no` must be 14 digits: a malformed 범위 is **refused, never silently
  ignored**, because ignoring it would answer a different question than the one asked.
- **Response headers.** `text/event-stream; charset=utf-8`, `Cache-Control: no-store,
  **no-transform**`, `X-Accel-Buffering: no`. **The `no-transform` is load-bearing, not decoration**:
  the Next router (and nginx, and CDNs) will otherwise gzip the stream, and a gzip encoder holds
  bytes until it has a block — measured, the whole answer then painted in one burst under 10 ms
  after a multi-second wait, which is R6's 스트리밍 state not happening at all. It is RFC 9111
  §5.2.2.6's own "do not re-encode this". A `curl` without `Accept-Encoding` will not reproduce the
  bug; a browser will.
- **Frame one is always `event: session`**, carrying `{"session_hash", "scope"?}`. The browser keeps
  it in `sessionStorage` and sends it back as `session` next turn. **It is never a cookie** — the
  thread is tab-scoped by design, and a cookie is exactly the identifier the conversation schema
  refuses. A missing or malformed handle is **replaced, not trusted**.
- **Then the agent's typed events, in the order they happen:** `tool_row` `{tool,row,ok}` ·
  `citation` `{number,rcept_no,api_tier,quote?,span?,field_key?}` · `status` `{phase,text}` ·
  `data` `{title?,rows:[…]}` · `calc` `{mode,name,inputs:[…],expr?,result?,state,why?}` ·
  `text` `{text,citations:[번호],unverified?}` · `refusal` `{family,text}` · `links` `{links:[…]}` ·
  `footer` `{count,evidence,generated_at,links}`.
  **Ordering the client depends on:** a `citation` is a *definition* emitted immediately **before**
  the `text` **or the block** that names its number, so the chip arrives with its claim — never a
  placeholder chip and never a trailing attachment. A number is defined once per answer; the same
  근거 keeps the same number, across 프로즈 · 데이터 행 · 계산 입력 alike. `links` and `footer` are
  emitted **only** on a completed turn. The transport reorders nothing and invents no field.
- **Every event may carry `block_id` and `persistent` (R16, P9), and they ride only when
  `block_id` is set** — which is what keeps every pre-R16 frame byte-identical. A second event
  wearing a `block_id` already on screen is an **in-place replacement, not an append**; an event
  with no `block_id` appends, exactly as before. `persistent: false` marks a block that belongs to
  the turn's *progress*, not to its record: the client never writes it to `sessionStorage` and the
  server never stores it.
- **`status` is the one transient frame** — `phase ∈ read | search | open | calc | write`, carrying
  **its own signed Korean sentence** (composed server-side in `mijual.agent.copy`, rendered verbatim
  like a 도구 행; the surface holds no status strings). Its `block_id` is the constant `"status"`, so
  「exactly one alive at a time」 is produced by the keyed reduce rather than by a rule the client has
  to remember. It dies at the first `text`/`refusal` block **and at every terminal** — a refusal-only
  turn has no prose to kill it.
- **`data` is a label/value block** — `rows: [{label, value, citation?, reader_input?}]`, `title`
  absent meaning 「use the signed heading」. A row carries its own citation number, allocated from the
  same numbering the prose uses. An empty block is never emitted.
- **`calc` is drawn at call time and settled in place** — it arrives with `state: "pending"` and its
  `inputs` **already filled** (that is half of the audit path), then the same `block_id` returns as
  `done` (with `result`) or `error` (with `why`). `mode: verified | expr` separates a number the
  product's own money math computed from one an arithmetic expression produced; they are never
  rendered identically. A calculation's **result is not a 근거** and is never counted in 근거 N건 —
  a calculation **input**'s chip is, because it is a filing value the reader saw.
- **`text.unverified` carries character offsets within that sentence** (unit included, absent when
  empty): a 공시 figure no tool returned. The sentence and the turn both survive — the span is a
  claim-level mark, never a turn-replacing gate.
- **`done` carries `filings`** — the count of distinct 접수번호 whose contract a tool actually read
  (server-known, **never** parsed back out of a 도구 행 string) — and `blocked`, which after P9 counts
  **markers the gate could not honour**, not sentences it dropped. Nothing is dropped any more.
- **A turn that called no tool emits no `footer` frame**, and a `보안` refusal carries **neither
  `links` nor `footer`** — its signed sentence already contains its 갈 곳. Footer suppression is the
  server's guarantee; the client does not re-derive it.
- **Then exactly one terminal:** `done` | `aborted` | `error`. Once streaming has started, the only
  failure is the typed `error` terminal — never a half-frame.
- **`links` carry a destination *kind*, never a URL** (`dart` · `event` · `board` · `stocks`, each
  with an `rcept_no` where it has one). The frontend owns every route, so the agent cannot point at a
  page that does not exist — and a path string in a payload is a string the citation gate would let
  the model *say*. An unrecognised kind is dropped by the client rather than rendered.
- **Pre-stream failures are the ordinary envelope, with no Korean:** `invalid_question` ·
  `invalid_scope` · `csrf_required` · `rate_limited` (429) · `invalid_request` (422). The design
  writes no copy for a pre-stream failure, so none is invented; the client renders the signed
  중단 row instead.
- **`rate_limited` says nothing to the reader.** Rate limiting is in-process, holds no address and
  persists nothing; the refusal carries **no `message_ko` and produces zero UI copy anywhere**,
  because 질문 수 무제한 is signed and a limit that is not shown must not be implied.
- **There is no stop endpoint.** 중지 is the client aborting the fetch; the server's turn ends when
  the consumer stops pulling. Nothing is retracted and released text stands.
- **Every turn is persisted anonymously** — `done`, `aborted`, `error` and a mid-stream disconnect
  alike — so 「대화는 익명으로 저장됩니다 (품질 점검용)」 is true of the broken turns as well. The
  stored row is **what the reader saw**: the released prose, its 거절 카테고리, its 근거 rcept_no
  목록, its 인용 칩 원문 and — since P9 — its **structured blocks, verbatim as the frames the reader
  received** (`conversation_turn.blocks`, one entry per `block_id`, in its final state; a
  `pending → done` pair stores one block). Prose cannot carry a calculation's inputs, expression and
  per-input 근거, so the audit path *is* the payload. The transient `status` line is never stored. A
  중지 before the first sentence stores nothing. Nothing about the
  mechanism is stored — there is no status column, and none was added.
- **거절 카테고리 is a six-value vocabulary** (`철회 · 확정 전 · 공시에 없음 · 보안 · 계산 요청 ·
  검증 미통과 폴백`), mirrored value-for-value in the ops filter. **Two of the six are read-only**:
  `계산 요청` and `검증 미통과 폴백` retired with P9 and have no producer left, but past rows must
  stay findable, so the whitelist keeps them.

### 운영 관제 (operator only)

**Thirteen `/ops` routes, of which eleven are `GET`.** The only unsafe methods on the whole
surface are `POST /ops/login` and `POST /ops/logout`, both touching only the operator's own
session row — asserted over the documented OpenAPI paths by a test. `GET /ops/session` ·
`overview` (+ a `decisions` block) · `gates` · `gates/rows` · `accuracy` · `conversations` ·
`sessions` · `feedback` · `users` · `lock` · `vocky`. Expiry answers **401
`ops_unauthenticated`** so the client returns to the door and restores the tab.

Contract statements: **every number is re-read from the source that already owns it** (the
개요 tiles reproduce `gates summary` byte for byte; 정확도 ships `evalset report`'s **exact
markdown** beside a structured mirror of the same object); **a reason/suppression code travels
raw English** and carries `reason_ko` only where the gate layer owns that Korean — never a
fallback phrase; **`▷` is served verbatim inside this panel and never becomes 「추정」** (the
boundary is the source); **every rate ships its own denominator** (gate-queue counts are over
stored rows, rates over distinct `(rcept_no, field_key)`, both served with `basis`); and spend
windows are labelled with their provenance. A blocked gate row omits `quote`/`span` entirely.

**`POST /feedback` (reader, anonymous, write-only, outward — P8).** The 의견 보내기 surface's
endpoint, and the second call in this service that leaves it. Body `{message, channel?: "web" |
"mobile", session_id?}`; **202 `{request_id, accepted_at}`** on vocky's own 202. Errors:
`400 feedback_empty`, `502 feedback_rejected` (`retryable: false`), `503 feedback_unavailable`
(`retryable: true`) and `503 feedback_unconfigured`. It **stores nothing on this side** — no row, no
table — and it is deliberately **not** merged with the agent's `save_feedback` queue: one is a reader
pressing a button, the other is the agent's own tool, and joining them would put a reader's free text
on the anonymous conversation path. The only correlation handle forwarded is the anonymous AI 질문
tab id, and only when one already exists; no email, no account, no IP.

`GET /ops/vocky?limit=&cursor=` is **no longer** the one read that leaves this service — there are now
one read and one write, both in `mijual/web/vocky.py`, which is still the single module the AST scan
allows to import an HTTP client. The read: a server-side proxy
of vocky's `GET /api/project/feedback`, serving `{as_of, state, source, fields[], count, rows[],
next_cursor?, reason?, status?}` — one feedback event per row, newest-first keyset cursor
(limit default 50, **max 100 = vocky's own ceiling**), `next_cursor` absent-not-null, and **no
total, because vocky returns none**. The sixteen served fields are vocky's own English key
names, carried in `fields` so the client names none of them. `state` is
`ok | unconfigured | unreachable` — the whole degradation contract; it never 500s and never
fabricates a row.

**P6 filled the conversation port and changed no route.** The 대화 로그 / 익명 세션 / 피드백 queue
tabs read the same storage-agnostic port; P5's implementation returned empty pages, and P6's real one
returns rows. So the three tabs went from an honest `{"count": 0, "rows": []}` to live data with no
change to `/ops/conversations`, `/ops/sessions` or `/ops/feedback`, and no frontend change either.

The port's rules are unchanged and inherited: every method returns `{count, rows, next_cursor?}`;
**no method takes an account, email, IP or UA filter**; nothing writes; pagination is an opaque
keyset cursor, newest first, with `next_cursor` **omitted at the end, never null**. An unreadable
cursor is `invalid_cursor` (400) — never a silent page 1. The served row keys are the ones the panel
already names: 대화 로그 `session_hash · at · scope · question · kind · refusal_category` (expanded:
`answer · evidence · quotes`); 익명 세션 `session_hash · last_activity · questions · refusals ·
last_scope`; 피드백 `at · text · email · session_hash`. **The 거절 카테고리 filter's values are the
five signed Korean family names** (`철회` · `확정 전` · `공시에 없음` · `검증 미통과 폴백` ·
`계산 요청`) — those strings are the stored vocabulary, and no English token stands in for them;
`kind` is `answer`/`refusal`. 익명 세션 is **derived** from the turn table, never materialized, so a
session can never drift from its turns.

## Open Questions

- **「API shape 확정 대기」 now reads half a step behind its surface** — the vocky shape is
  decided; what the view waits for is the `vk_` credential. Rewriting a signed line is a design
  change, so it renders as signed with the raw English `state` code beside it.
- **A closed 청약 with no 증권발행실적보고서 yet has no signed state** — such an ① is in neither
  section of 조회. Nothing was invented for it; drawing a state is a design call.
- **The 답변 푸터's third context link, 「필드로 이동」, is signed but not served.** The link kinds are
  a closed set (`dart · event · board · stocks`), and pointing at one field would need a new kind
  *and* per-field anchors on the detail page — plus a rule for which field, when an answer cites
  several across several filings, which the record does not write. It is **not rendered and not
  invented**; drawing it (or striking it) is an operator decision, and it is entangled with the
  footer's link density below.
- **The footer's link row can carry up to eight links.** `links` is composed from every filing the
  turn **read** (capped at three), while the footer's facts name the filings the answer **cited** —
  so one 이벤트 상세 can point at a filing that is not among the 근거, and several links can share the
  identical label. Dropping links would drop signed destinations and relabelling would invent copy,
  so it ships as measured and the shape is an operator question.
- **A completed refusal currently gets a footer** (`근거 0건 · {시각}` + 다시 질문). The line is
  honest, and the ③ 갈 곳 links render once rather than twice — but the record signs the footer under
  답변 and gives 거절 its own three-part anatomy, so whether it belongs there is an operator call.
- **The deployed streaming topology is unmeasured** (edge route / CDN / nginx), and there is **no
  heartbeat**: longest observed inter-frame gap with the live agent is **6.0 s**, so a proxy idle
  timeout below ~10 s would cut a legitimate turn. **P4**'s.
