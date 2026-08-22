---
doc_id: api
version: v0002
created_at: 2026-08-22T18:05:00+09:00
source: P5.REVIEW
summary: P5 apply phase: the whole HTTP contract — error envelope, presentation contract, board/event/stock reads, auth, portfolio, and the thirteen read-only ops routes
previous: v0001_bootstrap
---

# API

## Status

The service exists. P5 built the whole HTTP surface over the P2 exposure contract:
FastAPI (`mijual.web`), no prefix on reader routes, `/ops` for the operator panel.
Every contract below is implemented and live-verified against the corpus. Deployment,
the D-day mail channel and the AI 질문 agent surfaces are **not** here (P4 / P6).

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
- **No OpenDART call and no LLM call happens in a request path.** Enforced by an AST import
  scan over `src/mijual/web/` in the test suite.

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
  `next_lapse{date, corp_name, target}` · `freshness{as_of, stale, age_hours, stale_after_hours}`.
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
- `GET /stocks/{corp_code}` — the same page by stable handle. An unknown code **is** a 404.

Resolution is four unique-or-decline tiers (종목코드 exact → 회사명 verbatim → 회사명 normalized →
unique normalized prefix); **ambiguity resolves to nothing**. `rights` rows carry the
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

`GET /ops/vocky?limit=&cursor=` is the one read that leaves this service: a server-side proxy
of vocky's `GET /api/project/feedback`, serving `{as_of, state, source, fields[], count, rows[],
next_cursor?, reason?, status?}` — one feedback event per row, newest-first keyset cursor
(limit default 50, **max 100 = vocky's own ceiling**), `next_cursor` absent-not-null, and **no
total, because vocky returns none**. The sixteen served fields are vocky's own English key
names, carried in `fields` so the client names none of them. `state` is
`ok | unconfigured | unreachable` — the whole degradation contract; it never 500s and never
fabricates a row.

**P5 creates no conversation storage.** The 대화 로그 / 익명 세션 / 피드백 queue tabs read a
storage-agnostic port whose P5 implementation returns empty pages, so they serve an honest
`{"count": 0, "rows": []}` rather than an invented 「준비 중」 string. P6 implements the port and
changes no route.

## Open Questions

- **「API shape 확정 대기」 now reads half a step behind its surface** — the vocky shape is
  decided; what the view waits for is the `vk_` credential. Rewriting a signed line is a design
  change, so it renders as signed with the raw English `state` code beside it.
- **A closed 청약 with no 증권발행실적보고서 yet has no signed state** — such an ① is in neither
  section of 조회. Nothing was invented for it; drawing a state is a design call.
