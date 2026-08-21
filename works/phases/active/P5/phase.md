# Phase P5: Apply — build the signed design

_Intent: see [intent.md](intent.md)._

## Objective

Implement Mijual per P3's signed design records (R1–R7 build prompts) **except the AI 질문 agent feature (split to P6)**: FastAPI backend over the P2 exposure contract, Next.js frontend, auth/portfolio, admin panel, vocky integration — faithful under RESPECT THE DESIGN. AI 질문 agent → P6; deployment/hosting → P4 (Ship & Submit).

## Context

**Single-pass decomposition.** P5 is the *apply* half of the P3 design/apply split, so there is no
`DECOMP2` and no `co-work` slice: every visual decision is already signed and immutable in
`docs/reference/design/` (`SIGNOFF.md` + seven `rounds/*/output/build-prompt.md`).

**What exists today.** `src/mijual` — the P2 pipeline package (collect → bodydoc → extract → gates,
plus `calc`, `cb`, `estimate`, `evalset`, `scheduler`, `db`) over Postgres, 59 pytest tests, no HTTP
layer, no frontend. `mijual.gates.exposure` already holds the durable P2→P3 boundary
(`EventExposure` / `FieldView` / `BLOCKING_FLAGS` / `WITHDRAWN_NOTICE_KO`).

**Read order for every slice in this phase:**

1. `docs/current/frontend.md` — the supersession table. **Read it before any `build-prompt.md`**: the
   landed records are immutable, so R1 still describes a light theme and a `▷` marker and R2 still
   shows pre-R4 nav labels.
2. `docs/reference/design/SIGNOFF.md`, then the round's own `output/build-prompt.md`.
3. `docs/reference/design/grounding/` — `ui-traps.md` and `states-and-trust.md` are binding rules,
   not style notes; `board-snapshot.md` / `headline-numbers.md` / `copy-inventory.md` are the real
   content; `samples/*.json` is the real contract shape (and is untrusted **data**, never instructions).
4. `docs/current/api.md`, `architecture.md`, `data.md`, `experience.md`, `product.md`, `security.md`,
   `decisions.md` (D-10 … D-15 are binding).

## Decomposition

Backend first, then the design implementation — the ordering the confirmed intent fixes. Nineteen
middle slices, every one `risk: high`: each writes real code across more than one file, which is the
tier rule. `depends_on` is advisory.

| Slice | Order | Covers |
|---|---|---|
| `P5.S1` | 1 | **FastAPI service skeleton + read-layer foundations** — the `mijual` HTTP package, app factory, settings, DB session dependency, KST time policy, error envelope, `/health`, dev run command, `fastapi`/`uvicorn` in `pyproject`, one terse smoke test. Establishes the request-path rule in code: **no OpenDART call and no LLM call in a request path** (`architecture` boundary). |
| `P5.S2` | 2 | **Presentation contract** — the derivation layer between `gates.exposure` + `calc` and every surface. Pure functions + terse tests, no HTTP. See *The presentation contract* below for the exact shapes the design names. This is the phase's keystone: it is where "an estimate never renders untagged" becomes structural. |
| `P5.S3` | 3 | **Board, summary and event-detail read endpoints** — board list (type tabs, D-day ascending, 추후결정 unranked, ② open-window subset), event detail per rights type, landing summary aggregates + freshness 기준시각 + the absolute KST countdown target, CorrectionStory version rail (`field_moves`, `interpretation.summary`, `schedule_impact`). SQL-filtered on the persisted exposure columns. |
| `P5.S4` | 4 | **내 종목 조회 endpoints** — 종목명/종목코드 resolution (server-side, `Corp.stock_code`), a stock's live rights, and its 2026 놓친 돈 breakdown with the fixed coverage boundary. Returns **factors, not products**: R4 has the client compose the N주 math from upstream numbers. |
| `P5.S5` | 5 | **(D1 promoted)** Identity-scope the API-backed gates — re-pair 정정 filings joined to the wrong 사채. Its trigger fires here: P5 renders ② detail pages. |
| `P5.S6` | 6 | **③ 매수예정가 backing (D-15)** — extend extraction/exposure so 매수예정가 enters the contract. R3 ships ③ without it until this lands. |
| `P5.S7` | 7 | **Reader auth backend** — accounts (email + password hash, *nothing else*), hashing, session cookie, login/가입/logout, reset-token flow behind a mailer seam. |
| `P5.S8` | 8 | **Portfolio backend** — holdings CRUD, the D-day list composition (per-type governing anchor), 챙긴 돈 marks (user claims, never mixed into disclosure data or aggregates), notification **preferences**, sample-portfolio load. |
| `P5.S9` | 9 | **Admin backend** — the separate operator door (uniform constant-time failure, differently-named httpOnly/secure cookie) plus the read-only ops endpoints, **and the pipeline run log the 개요 tab needs** (see *Backing work the design implies*). Zero mutation endpoints anywhere. |
| `P5.S10` | 10 | **Next.js foundation** — scaffold, `tokens.css`/`fonts.css` vendored from the landed record, the binary assets, the `.cosmos` page shell, the R1 trust primitives (`EstimateMarker` 「추정」 · `Citation` · `StateBadge` · `DDay` · `RightsChip` · 소멸주의보 strip · craft panel), typed API client. |
| `P5.S11` | 11 | **Global chrome (R2)** — 52px nav with the signed three slots, footer (provenance · gate-cost · disclaimer · bottom hairline row), mobile top bar + sheet menu, vocky script load + the three `data-vocky-trigger` elements. |
| `P5.S12` | 12 | **Landing 관제 현황판 (R2/R2.1 + R3's board strip)** — cosmos starfield/glow/shooting stars, hero, retrospective value card + countdown/stats card, 소멸주의보 strip, the board (tabs, rows, freshness, ② 진행 중 strip, 추후결정 strip). |
| `P5.S13` | 13 | **Event detail ①②③ (R3)** — crumb, craft header + identity rule, ① 환산 블록, field sections with per-field `Citation`, type-specific rules, 철회 / 추후결정 / 발행사 기재 불일치 state pages, 정정 strip → CorrectionStory. |
| `P5.S14` | 14 | **내 종목 조회 (R4)** — search, 보유량 strip with sessionStorage memory, 진행 중인 권리, 2026 놓친 돈 breakdown, empty states, the disclaimer footnote. |
| `P5.S15` | 15 | **Auth surfaces (R5-1/R5-2)** — one panel with the 전환 link, the permanent PII inset, error/idle/확인 중 states, conversion offers that never gate, the sample entry link. |
| `P5.S16` | 16 | **내 포트폴리오 (R5-3…R5-8)** — holding rows with horizontal row-edit, 세션 이월 제안, D-day list (다가오는/지나간), 챙긴 돈 체크, 알림 설정 (KakaoTalk 「예정」 row with no control), sample mode banner/칩/종료, the logged-in account menu. |
| `P5.S17` | 17 | **운영 관제 (R7)** — the door plus six complete pages (개요 · 게이트 대기열 · 정확도·비용 · 대화 로그 · 사용자 · 피드백) in the ornament-free ops idiom, desktop-only, read-only. |
| `P5.S18` | 18 | **vocky integration** — decide the observation API's return shape against vocky's real API (R7 §6.3 delegates this to the build), **record the decided shape in that build-prompt section**, and build the admin vocky view behind it. |
| `P5.S19` | 19 | **Design-fidelity verification in a real browser** — run the product and check every surface against its signed contract, per `design-cowork` (fidelity is its own slice). Nits found earlier are fixed here, never by editing the landed record. |

**Rationale for the cut**

- **Backend before frontend, by intent.** The confirmed intent fixes it, and it is also the only
  order that works: the design contracts name a *presentation* contract (`countdown.label_ko`,
  `offering_inputs`, `lapse_result`, `corp_name_agrees_with_body`) that P2 does not persist. Building
  a page against a contract that does not exist yet is how invented numbers get in.
- **S2 is separated from S3/S4 on purpose.** The derivation layer is where the trust rules become
  structural (estimate-vs-fact tagging, upstream-only D-days, no browser-computed dates). Splitting it
  from transport keeps it unit-testable with no HTTP and stops each endpoint from re-deriving its own
  version of the same number — the failure mode R4 names explicitly ("two divergent readouts for the
  same number").
- **One slice per signed surface, plus a chrome slice.** R2 packed the landing with global chrome, but
  they are separable deliverables and the chrome is what every later page sits inside; landing them
  together would make one very large slice whose review cannot isolate a chrome regression.
- **Auth is split from portfolio (R5 is one round, two deliverables).** R5 covers auth + portfolio +
  D-day + 알림 + sample; that is four surfaces' worth of work. The seam is the login boundary.
- **vocky is its own slice, after admin.** §6.3 delegates a real decision (the observation API's
  shape) to this build against an external system — the one slice most likely to need operator input
  or a credential. Isolating it keeps that risk out of the admin panel slice.
- **Fidelity verification is a separate slice** (`design-cowork` invariant), and it is last because it
  is the only slice that can see the whole product running.
- **All nineteen are `risk: high`.** None of them is a one-line edit or docs; every one writes real
  code across several files, so `low` (the `mid` tier) would be a misroute.

### The presentation contract (what `P5.S2` owes every later slice)

The signed build prompts name these shapes. **None of them exists in `src/mijual` today** — grep
confirms `offering_inputs`, `lapse_result`, `countdown`, `label_ko`, `corp_name_agrees_with_body`
appear nowhere in the package. They are P5's to derive, on top of `gates.exposure` + `calc`:

- `countdown` — `{label_ko, date, dday, window_state}`, per-type governing anchor: ① 증서 매매 마감 ·
  ② 전환청구 **개시** · ③ 반대의사 통지 마감. **Computed upstream in KST and delivered as an absolute
  timestamp**; the browser only diffs. A past ② opening is 진행 중, never 종료 (`ui-traps` #5).
- `corp_name_agrees_with_body` / `corp_name_in_body` — R3's identity line. Display shows the DART
  master `corp_name`; the 본문 disagreement is a stated fact, never a silent correction
  (`ui-traps` #3, and `rcept_no 20250930000508` is the live case).
- `offering_inputs` (①) — 예정/확정발행가, 할인율, 배정비율 **to its full 10 decimals**, 초과청약 비율,
  `final_price_date`, `unit_value`, `unit_value_floor`. `확정발행가 null` ⇒ **no money number at all**,
  anywhere, including mail.
- `lapse_result` — 발행 증서 / 증서 청약 / 소멸 주수 / 소멸률 / per-offering 소멸가치 + 하한, from
  `mijual.estimate`'s report over the 증권발행실적보고서 family.
- Field payloads — value + `display` (`value` | `추후결정`) + verbatim `quote` + `span` + `rcept_no`.
  A blocked field is **absent from the payload**, not a null: `ui-traps` and R3 both forbid a
  placeholder where a gate-blocked field would be.
- **An explicit estimated/fact flag on every value.** The 「추정」 tag must not depend on a frontend
  author remembering; the contract says which values are derived and the primitive tags them.
- 발행사 기재 불일치 — **two readings side by side, each with its own citation**; never reconciled
  (`ui-traps` #2, N68's five `lapse_mismatch` filings).
- Board/landing aggregates — 감시 중 N건, 30일 이내 N건, 소멸 앞둔 N건, 읽은 실적보고서 N건, the
  freshness 기준시각, and the 718.1억원 / 548.7억원 headline pair, all from the same summary so the
  landing's two cards can never disagree.

### Backing work the design implies (build it, never quietly drop the feature)

- **③ 매수예정가** (`P5.S6`) — D-15's worked example: R3 does not render it because it is not in the
  exposure contract; the apply phase extends extraction/exposure and then it renders.
- **A pipeline run log** (`P5.S9`) — R7's 개요 tab requires a 최근 실행 표 with per-stage counts and
  spend, and "**스케줄된 beat가 안 돌았으면 「실행 기록 없음」 행을 alert 잉크로**". There is no run
  table in `mijual.db.models` today (Corp · Event · FilingVersion · Snapshot · ExtractionCall ·
  Extraction · PerformanceReport). Persisting runs is backing work, not a rendering choice — and it
  must be additive (`schema_sync.ensure_columns` / new table; **no Alembic, by design**).
- **The vocky observation API** (`P5.S18`) — §6.3 delegates the shape to this build.

## Findings & Notes

### Decisions this decomposition made

1. **D1 → promoted into `P5.S5`.** Its trigger is "before P3 renders ② event detail pages", and P5
   renders them (`P5.S13`). The four remaining ② gate failures are 정정 filings paired to the wrong
   사채; mis-pairing does not merely block four fields, it can put the wrong version's 전환가액 /
   전환청구기간 on a detail page. A wrong number on a rendered page is the one defect class this
   product cannot ship. Ordered before the ② surface lands.
2. **D2 → stays deferred.** Judged against the design records rather than the flag list: the 9
   collided keys (`event_key_collision` / `hint_split_evidence`) are **blocking flags**, so the
   exposure contract already keeps them off every page — no rendered surface trips on them. The
   residual product-visible case is `hint_duplicate`: **2 of 488 events share an `rcept_no` with
   another exposable event** (코이즈 `20260122000058`, 사토시홀딩스 `20251219000402` — `qa` v0002).
   That renders two *truthful* board rows, not a wrong number, and the fix is a corpus-mutating
   merge/split. **Carried as an explicit check for `P5.S12`/`P5.S14`/`P5.S19`:** if the board shows a
   visibly duplicated row, or a per-stock 놓친 돈 total double-counts one offering, the trigger has
   fired — promote D2 as a fix slice then. Do not paper over it with a display-level `DISTINCT`.
3. **D3 → stays deferred.** The signed design removed the need: R4-3 fixed the coverage line at
   "집계 범위 2026-01-01 ~ 오늘 (KST)" with **no 기간 picker**, and "outside coverage is *unstated*,
   never counted as 0". Pre-2026 ① depth would change no rendered figure; there is no retrospective
   surface that reaches past the stated boundary.
4. **D4 → stays deferred, conditionally.** Its trigger is "when P3 renders 실적보고서 figures **with
   citations**". Read against the contracts, the signed surfaces attach citations to *본문 extraction
   fields*, and R4's 놓친 돈 row carries "**One `Citation` per row (warrant-period quote verbatim)**"
   — a single-span 증서 매매기간 quote, not the summed 발행/청약 figures. **Condition for `P5.S13`
   (청약 결과 inset) and `P5.S14` (놓친 돈 breakdown):** if a slice attaches a `[근거]` chip to a
   실적보고서 figure that is a sum of two table rows (SKC and 에스에너지 are the two live cases, and
   에스에너지 is in the 2026 놓친 돈 table), the trigger has fired — promote D4 rather than shipping a
   one-addend quote as if it backed the whole number.
5. **Admin 대화 로그 / 익명 세션 → framed now in P5, filled by P6.** R7's ops chrome is **six signed
   tabs** and "컴포넌트 단편 화면 — 금지 (모든 섹션은 ops 크롬을 갖춘 완전한 페이지)"; dropping two of
   them would break the signed chrome, and the 사용자 tab is *half* P5 data (독자 계정) and half P6
   data (익명 세션). So `P5.S17` builds all six tabs complete, with 대화 로그 and the 익명 세션 table
   reading through a **thin storage-agnostic port that P5 implements as an empty source**. P5 creates
   **no conversation tables** — the storage and its schema are P6's, by P6's intent — and P6
   implements the port plus the two-way session-hash cross-links. Two consequences worth stating:
   (a) the tabs render an honest **0건** rather than an invented 「준비 중」 string — no Korean is
   invented; (b) the schema-level 계정↔대화 no-join promise is trivially intact in P5, because there
   is nothing to join, and `P5.S7` must not add any column that would later enable one.
6. **Notification boundary: settings here, sending in P4.** R5's 알림 설정 is a signed surface inside
   내 포트폴리오, so `P5.S8`/`P5.S16` build the preferences (수신 주소, 시점 칩 7일/3일/1일/당일 with
   the 7일+1일 default, the KakaoTalk 「예정」 row that renders **no working control**, 로그아웃,
   계정 삭제). The **D-day alert channel itself** — provider, scheduled send, the mail body — is P4's
   item 1 (`works/phases/active/P4/intent.md`). `P5.S7`'s password reset therefore goes behind a
   **mailer seam with a dev/console transport**, so P5 has no deploy dependency and P4 plugs in the
   real transport.
7. **The AI 질문 slot stays in the chrome; the surface is P6's.** The signed nav is three slots
   (내 종목 조회 · 관제 현황판 · **AI 질문**) and RESPECT THE DESIGN forbids dropping an approved
   element, so `P5.S11` renders all three. The `AI 질문` route ships as a **bare page shell with no
   invented copy and no fake chat**, owned and replaced by P6. Likewise the footer's bottom-row link:
   R2 landed it as 해설, and R6 superseded that label to **AI 질문** (`frontend` supersession table) —
   render the superseded label, not R2's literal.
8. **P5's event-detail pages ship without the 질문 스트립.** The preset-chip strip on detail
   (R6) is an agent entry point and belongs to P6. This is a **phase boundary, not a dropped design
   element** — recorded here so the phase review does not read it as a RESPECT-THE-DESIGN violation.

### What reading the design records changed about the plan's suggested shape

- **R6 contains no non-agent 해설 component.** The plan left room for one ("insofar as R6 describes
  non-agent 해설"). It does not: R6 is the AI 질문 agent end to end — widget, dedicated page, launcher,
  tools, SSE, refusals, server-side anonymous storage. Everything R6 designs is P6's. P5's only R6
  touchpoints are the nav/footer slot (note 7), the detail preset strip's absence (note 8), the admin
  대화 로그 frame (note 5), and one layout constraint: **the launcher/widget must not collide with the
  vocky trigger corner** — so `P5.S11` should keep the bottom-right corner clear for P6.
- **The plan's suggested "final fidelity slice" is kept, and it is the only slice that runs the whole
  product in a browser.** Per `design-cowork`, faithful implementation and real-browser fidelity are
  separate slices; `P5.S19` is the latter.

### `P5.S1` — the HTTP layer now exists; what every later slice inherits

The skeleton is `src/mijual/web/`. Import paths, so no slice has to go looking:

| you need | import |
|---|---|
| an app | `from mijual.web.app import create_app` (module-level `app` is only uvicorn's target) |
| a DB session in an endpoint | `from mijual.web.deps import DbSession` → `def board(db: DbSession)` |
| to fail a request | `from mijual.web.errors import ApiError, NotFound` |
| any timestamp or date in a payload | `from mijual.web import clock` → `clock.iso(dt)` / `clock.iso_date(d)` / `clock.now()` |
| a new surface | a module under `mijual.web.routers/`, included in `create_app` |

Run it: `.venv/bin/uvicorn mijual.web.app:app --reload` (also in `compose.yaml`'s header). There is
**no compose service for the web app** — deployment is P4's.

1. **The error envelope is decided and it is the only error shape.**
   `{"error": {"code", "message", "message_ko"?, "fields"?}}`. `code` is a stable English
   `snake_case` token, `message` is English and **developer-facing — never rendered to a user**,
   `fields` is 422-only. **`message_ko` is present only when the product already owns that Korean
   string** (e.g. `WITHDRAWN_NOTICE_KO`) and is **omitted, not null**, otherwise. Reasoning, so a
   later slice does not "fix" it: the signed design writes **no HTTP-error copy at all** — it writes
   *state* copy (철회 / 추후결정 / 발행사 기재 불일치), which reaches the user in a normal 200 payload.
   Inventing Korean error copy would be a design change. **A slice that needs user-visible Korean for
   a failure raises `ApiError(..., message_ko=<an existing string>)` or leaves it to the surface.**
   Handlers cover `ApiError`, `HTTPException` (404/405), validation and bare `Exception`, so there is
   no path back to FastAPI's `{"detail": …}`. The 500 handler logs the traceback and returns only the
   code — **do not add exception text to an error body.**
2. **`clock.py`, not `time.py`** (the plan said "or similar"; `mijual.web.time` reads as a stdlib
   trap). `KST` is **re-exported from `mijual.calc`, never redefined** — the pipeline and the API must
   agree on what "today" is. `clock.iso()` emits second-precision `+09:00`; `clock.iso_date()` emits a
   bare `YYYY-MM-DD` **with no offset**, because 청약일 / 매매기간 / 전환청구 개시일 are calendar days
   and pinning one to midnight+09:00 invites a client to shift it into the previous day. Both are
   `None`-in-`None`-out and overloaded, so a non-optional call type-checks.
3. **`/health` does not touch the database, and that is a rule, not an omission.** A liveness check
   that flaps with Postgres turns one outage into two. Freshness (the landing 기준시각) is a fact
   about the *corpus* and is **`P5.S3`'s summary endpoint**, not this probe. Do not "improve" health
   by adding a DB ping.
4. **The engine is lazy and sessions are rollback-only.** One engine per app, built on the **first
   request that needs a row** (verified: `app.state.engine is None` until then) and cached on
   `app.state`; `get_session` rolls back on the way out of *successful* requests too. This is
   deliberately **not** `db.session.session_scope`, which commits — that is the pipeline's wrapper.
   **P5's HTTP layer never writes through `DbSession`.** `P5.S7`/`P5.S8` introduce the first real
   writes (accounts, holdings): they must add their own committing dependency rather than relaxing
   this one, so a GET can never write.
5. **The request-path rule is now enforced by the suite.** `tests/test_web_smoke.py` walks every
   `.py` under `src/mijual/web/` with `ast` and fails if one imports `mijual.dart`, `mijual.collect`
   or `mijual.extract`. If a slice trips it, the answer is never to relax the test. **Known
   near-miss for `P5.S3`:** `mijual.gates.exposure.current_version` does a *function-local* import of
   `mijual.extract.runner`, so importing `mijual.gates.exposure` from a router is fine by the scan
   (the import is not in `web/`) but does pull the extractor's module tree in at call time. It makes
   no LLM call, but S3 should check what `mijual.extract.runner` drags in at import before putting
   `event_exposure()` on a hot request path — the SQL-filtered read over the persisted exposure
   columns that S3 is specified to do avoids the question entirely.
6. **Dependency facts.** `fastapi>=0.115` + `uvicorn>=0.30` are runtime deps; `httpx>=0.27` is a dev
   extra for `TestClient`. Resolved today: fastapi 0.141.1 / **starlette 1.6.0** / uvicorn 0.52.4.
   Starlette 1.6 emits one `StarletteDeprecationWarning` — "Using `httpx` with
   `starlette.testclient` is deprecated; install `httpx2` instead". **Left as-is on purpose:** it is
   the only warning in the suite, and swapping a test transport to a brand-new package for a cosmetic
   line is a worse trade than carrying it. Revisit at `P5.S19`/P4 if it becomes an error.
7. **Nothing speculative was added.** No CORS, no compression, no request-id middleware, no auth.
   `P5.S10` owns the CORS/origin question (it creates the frontend that has an origin); `P5.S7` owns
   the session cookie. Pool sizing / `pool_pre_ping` / read-replica routing are noted in `deps.py` as
   **P4** deploy decisions.

### `P5.S2` — the presentation contract exists; do not re-derive any of it

`src/mijual/present/` is the derivation layer. **Every surface reads it; no endpoint
re-derives a number.** Import map, so no slice goes looking:

| you need | import |
|---|---|
| a tagged value | `from mijual.present import Figure` → `Figure.fact(v, quote=…, span=…, rcept_no=…)` / `Figure.estimate(v)` |
| one event for a board row or a detail page | `event_view(exposure, facts=…, corp_name_in_body=…, today=…)` → `EventView` |
| just the countdown / identity / fields | `countdown_of` · `identity_of` · `field_payloads` · `field_value` |
| ①'s money factors | `offering_inputs(exposure, event_inputs_result)` → `OfferingInputs` |
| an offering's 소멸 outcome | `lapse_result(row_or_stored_json, facts=perf_facts)` → `LapseResult` |
| 발행사 기재 불일치 | `issuer_disagreement(perf_facts_mapping)` → `Disagreement | None` |
| the landing/board aggregates | `board_summary(views, as_of=…, …)` → `BoardSummary` |
| JSON | every shape's **`payload()`** — never `dataclasses.asdict` (it emits the nulls the contract exists to prevent) |

1. **Serialization is decided.** Money and every ratio are **exact decimal strings**
   (`decimal_str`, never rounded, never a float — 배정비율 keeps all ten decimals);
   counts are `int`; calendar dates are **bare** `YYYY-MM-DD` (`iso_day`); instants are
   `datetime` in the dataclass and `+09:00` second-precision strings in `payload()`
   (`present.values.instant`). **Absent means the key is absent**, never `null` — the
   same rule `mijual.web.errors` already uses for `message_ko`.
2. **Keys are English `snake_case`; Korean appears only as content** (`label_ko`,
   `korean_name`, `notice_ko`). The grounding samples' `offering_inputs` shows Korean
   keys — that is the exporter script's shape, not the product's; `lapse_result`'s
   English keys are product code and the build prompts name `unit_value`,
   `unit_value_floor`, `final_price_date` in code position. **Do not re-litigate this**,
   and do not mix scripts in one JSON contract.
3. **The plan's key name `dday` governs**, holding what the grounding samples call
   `d_day_label` (`"D-5"`); `days` carries the signed integer beside it.
4. **What raises, on purpose** (each one is a rule the design states as a prohibition):
   a `Figure` with no `estimated`, or with a quote on an estimate; an `OfferingInputs` /
   `LapseResult` carrying money with no `confirmed_price`; a `FieldPayload` with a value
   beside `추후결정`; a `Disagreement` with fewer than two readings or with none/two
   marked `used`; `countdown_of` on an **exposable ②** with no `facts=` (a silently
   dateless board row looks like data, not like a bug).
5. **A non-exposable event has no countdown and no fields.** `EventView.renderable` is
   `state in {"exposable", "withdrawn"}`; 철회 *is* a surface (the notice replaces the
   body), everything else — suppressed / flagged / `no_document` / `no_detail` /
   `incomplete_api_row` — has no board row and no detail page, so **`P5.S3` answers 404
   rather than rendering a page that explains why an event is not exposed**. This is
   stricter than `scripts/export_design_grounding.py`, which emits a countdown for the
   flagged sample; that is a designer's debug convenience, not the contract.
6. **The reader payload carries no gate reason code and no report `reason` string.** Why
   a field is missing is internal (`states-and-trust.md` §4, D-14) — `P5.S9`/`P5.S17`
   read `EventExposure` / the report directly, and they are the only surfaces that do.
7. **⚠ `P5.S3`/`P5.S4` blocker, measured here: `mijual.estimate` imports `mijual.dart`,
   `mijual.collect` **and** `mijual.extract` at module level.** A router therefore cannot
   call `build_report` or `event_inputs` — `tests/test_web_smoke.py`'s AST scan would
   fail on a direct import, and the module tree comes along regardless. So the 놓친 돈 /
   소멸가치 numbers must reach the request path from **persisted** state: either the
   `PerformanceReport.facts` JSON already stored (which is why `lapse_result` also accepts
   a `LapseRow.as_json()` mapping and `issuer_disagreement` takes the stored mapping), or
   an additive persisted precomputation written by the worker (`schema_sync.ensure_columns`
   / a new table — **no Alembic**), the same shape of backing work as `P5.S9`'s run log.
   Note that `event_inputs`' 확정발행가 / 할인율 / 배정비율 are **not** in the exposure
   columns today; decide this in `P5.S3` and record it, do not smuggle an extractor import
   into a router. (`mijual.cb` and `mijual.gates.exposure` are both clean — verified.)
8. **`mijual.present` itself imports only `mijual.calc` + `mijual.gates.exposure`** at
   runtime; `mijual.estimate` / `mijual.cb` types are `TYPE_CHECKING`-only and the
   functions read attributes. `tests/test_present.py` enforces it with the same AST scan
   `web` uses (TYPE_CHECKING blocks excluded). **`web → present`, never the reverse** —
   which is why `present.values.instant` restates `mijual.web.clock.iso`'s policy instead
   of importing it; a test pins the two together byte-for-byte.
9. **No Korean was invented.** `COUNTDOWN_LABELS_KO` (신주인수권증서 매매 마감 · 전환청구
   개시 · 반대의사 통지 마감) are the strings the grounding pack was exported with and R3
   names as `countdown.label_ko`; `MISMATCH_LABEL_KO` is ui-traps #2's locked literal;
   `FIELD_NAMES_KO` is copied verbatim from `mijual.extract.fields.FIELDS` (importing it
   would drag the extractor tree) and **pinned to it by a test**, so a label change in
   `fields.py` fails the suite. The three countdown labels are also duplicated in
   `scripts/export_design_grounding.py`'s `key_date()`; the script was deliberately left
   untouched (it regenerates a landed, dated pack) — **if a later slice ever edits it,
   import them from `mijual.present` instead of re-typing them.**
10. **`board_summary` definitions**, so a SQL-side count in `P5.S3` matches: 감시 중 =
    `state == "exposable"`; 30일 이내 = `0 <= days <= 30` **inclusive** (the definition
    `board-snapshot.md` measured 34 with); 추후결정 = exposable with **no** countdown date;
    ② 진행 중 = `window_state == "open"` **and** the anchor is past. That last one is
    deliberately narrower than the snapshot's `지남` column (56, which is only `days < 0`):
    an ② whose 전환청구기간 has fully closed is not "지금 전환할 수 있는". If the live count
    differs from 56, that is why — it is not a regression.
11. **The landing countdown instant is still open.** `BoardSummary.countdown_target` is
    `None` and the contract will not invent one; R2's assumed 2026-09-04 24:00 KST is not
    in the code. `next_lapse_date` / `next_lapse_corp_name` feed the 소멸주의보 strip's
    live numbers (15건 / 2026-09-04 / 계양전기) from the *same* object as the stats card,
    which is the whole point of one summary shape.
12. **Cross-checked against the landed pack.** All 11 grounding samples were replayed
    through the layer: countdown, identity, exposable-field set, `lapse_result` values
    (한화솔루션 20,635,460,625원 = ▷206.4억원) and the 대한광통신 두 readings all reproduce,
    with only the flagged-event divergence in note 5. Worth re-running as a scratch script
    (never as a committed test — the pack is dated) if a later slice changes a derivation.

### `P5.S3` — the read endpoints exist; the route map, and two stated defaults

**The endpoint map** (no prefix, matching `/health` — `P5.S10`'s client should hard-code these):

| route | what it serves |
|---|---|
| `GET /board/summary` | every landing number in **one** `BoardSummary` payload — 감시 중 · 30일 이내 · 소멸 앞둔 · 읽은 실적보고서 · 「추정」 headline + band edge · 소멸 증서/발행 증서/소멸률 · `next_lapse{date, corp_name, target}` · `freshness{as_of, stale, age_hours, stale_after_hours}` |
| `GET /board?rights=R1\|R2\|R3` | `counts` (tabs, **always whole-board**) · `rows` (D-day ascending, `days >= 0` only) · `open_now{count,total,rows}` (② 진행 중) · `tbd{…}` (일정 추후결정, unranked) · `reference` · `freshness` |
| `GET /events/{rcept_no}` | the detail card: `EventView.payload()` + `corrections` teaser + ① `offering`/`lapse_result`/`issuer_disagreement` + ② `convertible` + 철회 `withdrawal` |
| `GET /events/{rcept_no}/corrections` | the CorrectionStory: version rail (`is_current_readable` on exactly one row) + `field_moves` + `interpretation` verbatim |

**Route key = `rcept_no`, resolved against *every* `FilingVersion`** (recorded choice): it is what the
design links by, and `rcept_no` mutates to the newest version (N2), so yesterday's link must still
open the page — it renders today's readable version regardless. `event_id` travels in every payload
for a client that wants a stable handle. **840 stored `rcept_no` values sit under two event keys**
(N21 pairing residue, far more than D2's 2 `hint_duplicate` pairs), so resolution orders
**renderable first** (`exposable` → `withdrawn` → rest), then newest 최초 접수일. Without that,
계양전기 `20260724000546` opens its `superseded_by_pairing` twin and 404s a row the board is showing —
found by the live curl pass, not by reasoning.

**Decision 1 — the countdown instant.** Served as `next_lapse.target`, an absolute KST instant =
`next_lapse_date + 1 day at 00:00 KST`, i.e. **end of the 청약 day** — exactly R2's stated assumption
(2026-09-04 24:00 KST). Behind `MIJUAL_COUNTDOWN_CUTOFF_TIME` (`"24:00"` default, or `"HH:MM"`), so
the operator's real 접수 마감 시각 lands **without a code change**. The policy lives in
`mijual.web.reads.countdown_target`; `mijual.present` still refuses to invent one and only carries
what it is handed. **The open question stays the operator's.**

**Decision 2 — the stale threshold: 18 hours** (`present.DEFAULT_STALE_AFTER_HOURS`, overridable with
`MIJUAL_STALE_AFTER_HOURS`). Derived from the beat schedule, not from taste: the pipeline runs 07:30
and 19:30 KST, so the widest *healthy* gap is 12 h and a **missed** beat reaches ~24 h. 18 h is the
smallest threshold that cannot fire on a healthy schedule and still fires on the first miss.
**기준시각 is `max(Event.last_seen_at)`** — a corpus fact ("when did we last look at DART"), never the
request time; a dead worker therefore makes the board *stale*, never fresh and never dark. `stale`
and the `N시간 전` `age_hours` (floored, never rounded up) are **served**, so no client computes
staleness against its own clock.

**What `P5.S4`/`P5.S9`/`P5.S10+` inherit**

| you need | use |
|---|---|
| rows/summary/detail loading | `mijual.web.reads` — `load_board` · `load_summary` · `resolve_event` + `load_detail` · `corpus_as_of` · `countdown_target` |
| an exposure from rows you already loaded | `mijual.gates.exposure.exposure_of(event, version=…, rows=…, facts=…)` — pure; `event_exposure` is now just its loading half |
| the newest readable version | `mijual.db.repository` — `readable_versions` · `document_of` · `current_document` (one decode, gives the 본문 back) · `current_version` · `current_versions` (batched) |
| ① money inputs / 소멸 결과 in a request path | the **persisted** `OfferingInput.inputs` / `PerformanceReport.lapse` mappings → `present.offering_inputs` / `present.lapse_result` (both now read an object *or* its stored JSON) |
| a board row / ② fact strip / 정정 rail / freshness / totals | `present.board_row` · `present.convertible_view` · `present.correction_story` · `present.freshness` · `present.lapse_totals` |

1. **The version-selection near-miss (S1 note 5) is closed by moving, not forking.**
   `readable_versions` / `document_of` now live in **`mijual.db.repository`**; `mijual.extract.runner`
   re-exports them, so every existing caller is untouched and the suite stayed green at 75. The gates,
   the exposure contract and the 철회 detector import them at module level now — no function-local
   `import mijual.extract.runner`, so **importing `mijual.gates.exposure` no longer drags the extractor
   tree (model client included) onto a request path**. Verified: importing `mijual.web.app` loads
   none of `mijual.dart` / `collect` / `extract` / `estimate`. What a *detail* request still pulls at
   call time is `mijual.dart`'s module (stdlib-only) inside `BodyDocument.from_bytes` — a ZIP decode,
   not a request. `tests/test_web_smoke.py`'s AST scan covers `web/` only, so that remains a fact to
   keep in mind rather than one the suite catches.
2. **`current_versions` is the same rule, batched without decoding** (a board must not decode ~500
   ZIPs). It can only differ from `current_version` for a stored body that fails to decode; **measured
   over all 488 exposable events: 0 differences**, and the difference would be conservative anyway (an
   undecodable body has no gate-passing rows, so the row loses its date rather than inheriting a
   superseded version's). Re-measure with `scripts/` if the corpus grows a corrupt snapshot.
3. **The board loads one field per event, on purpose** (`reads.COUNTDOWN_FIELDS`): a row renders no
   field values, so shipping all 409 gate-passing fields (some with 600-character quotes) would be
   payload nobody renders. `exposure_of` accepts a subset of rows exactly for this.
4. **The estimate-import blocker is closed by a persisted precomputation** (S2 note 7's sanctioned
   route, additive, no Alembic):
   - **new table `offering_input`** — one row per ① event: `inputs` (the whole
     `EventInputs.as_json()`), plus `price_confirmed` / `subscription_start` / `subscription_end` /
     `decision_rcept_no` as **columns** so the 소멸 앞둔 count and the 발행가 확정 전 state are SQL;
   - **additive column `performance_report.lapse`** — one `LapseRow.as_json()` per 실적보고서;
   - written by **`python3 -m mijual.estimate snapshot`** (`mijual.estimate.snapshot`, 0 requests, 0
     LLM calls, idempotent, ~2 s over the corpus). `EventInputs.as_json()` is new and its keys **are**
     the attribute names, so `present.offering_inputs` reads an object and the stored mapping
     identically (pinned by a test).
   - ⚠ **The snapshot is not yet wired into the beat schedule.** Adding a 5th stage changes
     `PipelineConfig.stages`' default and would edit `tests/test_scheduler.py` — out of this slice's
     scope. **`P5.S9` (it already touches the scheduler for the run log) or P4 must wire it**; until
     then it is run by hand after a `collect`, or the ① extras and the headline age silently while
     기준시각 says the corpus is fresh.
5. **D4's trigger has fired, and it is wider than the deferred note assumed.** Measured over the 32
   parsed 실적보고서: **7 figures in 4 companies** carry a citation cell that does not state the number
   it backs — SKC, 에스에너지, **루닛** and **한화솔루션** (the landing's own headline example): 청약
   38,430,497 against a cell reading `38,427,609`, because 청약 is a **sum of two table rows** while
   `raw`/`span` point at one addend. The note named SKC + 에스에너지 only. Interim, landed here:
   `present.money._cited_count` attaches `quote`/`span` **only when the cell's text parses to exactly
   that number**; otherwise the value keeps its `rcept_no` (the DART link still resolves) and carries
   no verbatim chip. **Promote D4** as a fix slice to make those figures properly citable (a span per
   addend); `P5.S13`/`P5.S14` must not re-attach a one-addend quote.
6. **The 철회 page carries its notice and its evidence and nothing else.** `state: withdrawn` returns
   early: no `offering`, no `convertible`, no 정정 teaser — R3's "no fields, no countdown, no old
   dates" is a payload rule, not only a rendering one. `withdrawal{rcept_no,item,before,after,span}`
   comes from re-running `detect_withdrawal` (stored bytes only; 11 events corpus-wide) because the
   stored `exposure_note` is one prose line for an operator and a `Citation` needs the parts.
7. **The ② fact strip is exactly R3's six values** (`present.convertible_view`): 전환가액 · 오버행 % ·
   전환 시 주식수 · 권면총액 · 발행방법 · 만기, all facts, none with a quote/span (an API row has no
   character offsets — its citation is the filing number). 리픽싱 floor and 전환비율 are deliberately
   **not** in the payload: the countdown already carries 전환청구기간 and the design names six.
8. **Live numbers, measured 2026-08-22 against the pack's 2026-08-20** — shapes match, counts drift as
   expected: 488 exposable (50/422/16 ✓) · **389 ranked rows** (upcoming) · **57 ② 진행 중** (the pack's
   `지남` was 56; two days of openings, and S2 note 10's narrower definition currently excludes nobody —
   **0** ② in the corpus has a fully-closed 전환청구 window) · **4 추후결정** ✓ · 38 past ①/③ off the
   landing (389+57+4+38 = 488 ✓) · within_30d 33 (pack 34) · 소멸 앞둔 **15** ✓ · 실적보고서 **69** ✓ ·
   headline **71,812,971,649원 = 718.1억원** ✓ with floor 548.7억원 ✓ · 소멸/발행 51,253,956 /
   365,527,824 ✓ · 소멸률 **0.1402** ✓ · 한화솔루션 소멸가치 **20,635,460,625원 = 206.4억원** ✓ ·
   증서 1주 5,525원 ✓ · 대한광통신's two readings both cited ✓ · `20250930000508` 풍전약품 vs
   본문 에스씨엠생명과학 → `corp_name_agrees_with_body: false` ✓.
9. **`next_lapse` tie-break, and it is visible on the landing.** Three offerings share 청약 마감
   2026-09-04 (계양전기 · SG · 퓨쳐켐). The pipeline's `min()` picked whichever row the DB returned
   (the R2 card shows **계양전기**); the API orders `(마감일, 접수번호)` and names **퓨쳐켐** — earliest
   filed, stable across databases and locales (a 회사명 sort depends on the DB's Korean collation).
   The strip's numbers are live by contract ("발표용 문장 4 with live numbers"), so this is data, not a
   design deviation — but `P5.S12`/`P5.S19` will see a different company than the landed card.
10. **The ① extras cell needs one decision from `P5.S12`.** R2 says `청약 YYYY-MM-DD`; the row carries
    the whole 구주주 window (`subscription_start` / `subscription_end`) because the design does not say
    which end that date is (the 소멸주의보 sentence uses the **마감**). Pick one when rendering and note
    it; the payload does not choose for you.
11. **Payload sizes / timings** (local Postgres, warm): `/board` **160 KB in ~54 ms** (all 389 rows,
    no paging — `?rights=` cuts it to ~8 KB for ①), `/board/summary` ~98 ms, a detail 6–15 ms. If
    `P5.S12` wants paging, add it there; the design paginates nothing today.
12. **The contract outranks the persisted column.** `load_board` skips a row whose `exposure_of`
    verdict is not `exposable` even though `Event.exposure_state` said it was (a gate run that has not
    landed). The API renders what `gates.exposure` says — never its own reading.

### `P5.S4` — 내 종목 조회 serves **factors, not products**; the route map and six decisions

**The endpoint map** (no prefix, like the rest):

| route | what it serves |
|---|---|
| `GET /stocks?q=<종목명\|종목코드>` | resolution **and**, on a hit, the whole page in one response: `{query, found, stock{corp_code,corp_name,stock_code}, reference, rights, lapse}`. A miss is **`200 {"query": …, "found": false}`** — nothing else, no reason code |
| `GET /stocks/{corp_code}` | the same page by stable handle (R3's "내 보유량으로 환산 →" link-out). Unknown code → **404 envelope** |

`rights` = `{count, rows[]}`, each row `EventView.payload()` + `offering` (①, the **full**
`OfferingInputs`) + `convertible` (②, R3's six-value strip). `lapse` = `{coverage, totals, rows[],
pending?}`, each row `{rights_type, lapse}` + the event-derived block when the 유상증자결정 is
exposable (`event_id`, `rcept_no`, `countdown`, `warrant_trading_period`, `offering`) +
`issuer_disagreement` when the filing contradicts itself.

**`P5.S14` (and `P5.S10`'s client) inherit these:**

| you need | use |
|---|---|
| 종목명/종목코드 → issuer | `mijual.web.reads.resolve_corp` (never guesses; see below) · `stock_by_code` |
| the whole 종목 page | `reads.load_stock(session, corp, today=…)` — one load, both sections |
| a subset total (Σ over *some* offerings) | `present.LapseTotals.payload()` — same fact/estimate split as `BoardSummary` |
| "the same company, written differently" | `present.bare_name` (was private `_bare_name`) |
| the coverage boundary | `reads.LAPSE_COVERAGE_START` / `CONVERTIBLE_COVERAGE_START` — **served**, never assumed client-side |

1. **A search miss is a result; a bad link is an error.** `?q=` that resolves nothing returns
   `200 {"query", "found": false}` — R4 renders its own locked 검색 불일치 sentence on the same
   page, and a 404 envelope would carry an English `code` the surface would translate anyway. An
   unknown `corp_code` on the second route **is** a 404. Neither says *why*: no candidate list, no
   near-miss, no reason (404-not-explained).
2. **Matching semantics — four tiers, each unique-or-decline:** 종목코드 exact (all digits,
   zero-padded to 6) → 회사명 verbatim → 회사명 normalized (`bare_name` + casefold) → **unique**
   normalized prefix. Ambiguity resolves to **nothing**. Measured 2026-08-22: 0/614 normalized-name
   collisions, and **13 names are a strict prefix of another's** (금양/금양그린파워,
   디와이/디와이디·씨·에이, 한창/한창제지 …) — which is precisely why the exact-normalized tier runs
   before the prefix tier. `계양`, `계양 전기(주)`, `계양전기`, `012200` all reach 계양전기; `삼성전`
   reaches neither 삼성전자 nor 삼성전기.
3. **Unknown stock ≠ stock with no rights, structurally.** `found: false` vs `found: true` with
   `rights.count == 0` and `totals {offerings: 0, valued: 0}` and **no money key at all**. Every
   `Corp` row resolves: measured **614/614 corps have events** (`ensure_corp` only runs while
   creating one), so "resolvable" and "in the corpus" coincide today; if that ever diverges the
   reader gets the honest no-event empty state rather than 검색 불일치. Live example of the
   empty state: 고려아연 (226 of 614 corps have nothing renderable today). The 감시 중 count that
   empty state also wants stays in `/board/summary` — it is not duplicated here.
4. **Live-rights ranking (recorded):** upcoming (`days >= 0`) D-day ascending → **② 진행 중**
   (opened, not closed) most-recently-opened first → **일정 추후결정** unranked, last. A deadline
   still ahead outranks an open window with nothing to exercise (R4-4). Past ①/③ are absent — the
   past ① reappears in 놓친 돈 with its 소멸 계산, the only honest place for it. Verified live on
   유티아이: D-91 · D-280 · D-327 · **D+46 open last**.
5. **The lookup ① row carries the detail-grade `offering`, not the board's slim extras cell.** R4
   owns the N주 conversion (R3 shows per-unit only), so the row needs 배정비율 to ten decimals,
   초과청약 비율, `unit_value` + floor and `final_price_date`. `price_confirmed` is on both shapes,
   so a client reading only that key works against either. ⚠ **`P5.S14`: no live ① in today's
   corpus has a 확정발행가** (33 priced offerings, all with 청약 already closed) — every live ① row
   currently renders the `발행가 확정 전` state, and the 환산액 path is only exercisable against the
   놓친 돈 rows until a new offering confirms its price.
6. **A 놓친 돈 row's event-derived block is gated on `state == "exposable"`.** `event_id`,
   `rcept_no`, `countdown` (the 매매기간 **D+n**, computed upstream) and the 매매기간 `Citation`
   appear only when the 유상증자결정 is renderable. Two corpus rows (한솔테크닉스, 트리니티항공) hang
   off *flagged* events: they keep their 소멸 계산 — a lapse is a fact the 실적보고서 attests — and
   lose the 기간 line, the quote and a "상세 보기" link that would 404. `lapse` still carries
   배정비율 + `unit_value`, so the N주 math survives the degraded row. This is stricter than the
   plan's wording and follows "the exposure contract is not re-decidable".
7. **Coverage is served, not assumed:** `{start: "2026-01-01", end: <today KST>,
   convertible_start: "2025-06-01"}` — the corpus's own collection windows (`estimate collect
   --bgn 20260101`, `collect --bgn 20250601`), which is what R4-3's line states. Membership is the
   offering's **청약 종료일** (fallback: the 실적보고서's 접수일 — a guard, not a path: all 32 stored
   `lapse` rows carry one, 2026-01-23 … 2026-08-06). Outside it a row is **absent**, never 0.
8. **`pending` is the same definition the landing counts 15건 with** — `_pending_lapses` now takes
   `corp_code=` rather than growing a second query. It answers R4's "…청약 종료({date}) 후
   집계됩니다" line: `{count, subscription_end}` for the soonest. ⚠ **Known gap, no signed state:**
   an ① whose 청약 has *closed* but whose 증권발행실적보고서 has not been filed yet (코이즈, 센서뷰,
   클로봇 — the report's "청약 종료 — 증권발행실적보고서 미제출" bucket) is in **neither** section
   and gets no line: `pending` would render the wrong copy (its 청약 is over) and a 놓친 돈 row
   would be an invented figure. `P5.S14`/`P5.S19` should look at it; it is a design gap, not a bug.
9. **D4 was not re-triggered.** Verified live that SKC's and 한화솔루션's 청약 counts come back with
   `rcept_no` and **no quote** (S3's `_cited_count` guard), while 대한광통신's two counts do carry
   quotes and its row carries `issuer_disagreement` with both readings and both spans —
   `ui-traps` #2 is a payload rule, not a detail-page rule, so it rides on the breakdown row too.
10. **Live cross-check (2026-08-22, local Postgres).** 한화솔루션 3,734,925주 · 22,100원 · 증서
    **5,525원** · **20,635,460,625원 = 206.4억원** ✓ (배정비율 `0.2465120994` — R4's own caption
    example); 에스에너지 1,990,157주 · 14.22% · 7.2억원 ✓; 대한광통신 2,083,302주 · 16.2억원 ✓;
    계양전기 pending 2026-09-04 ✓. Payloads **1.1–5.7 KB in 8–24 ms**.
11. **Two additions outside `mijual.web`**, both to keep "all numbers through `present`" true:
    `LapseTotals.payload()` (a per-stock total is still a presentation shape, and it emits **no
    zero** — a stock with no 소멸 has no `value` key) and `bare_name` made public. Also
    `_countdown_rows` → **`_field_rows(session, ids, fields)`**: the stock page loads four field
    keys (`STOCK_FIELDS` = the two countdown fields + `issue_price_formula` + `excess_subscription`)
    instead of all of them, the same "load what the surface renders" rule the board follows.

### Constraints and gotchas the later slices must not rediscover

- **The cards never left the Claude Design project.** `build-prompt.md` + `docs/current/frontend.md`
  + the grounding pack are the *whole* source of truth an executor gets. Do not go looking for
  `landing/*.html` in this repo — it is not here, and its absence is not permission to improvise.
- **Binary assets are outside the repo** (`frontend` v0002 Open Questions): the wordmark PNGs, the
  ring logo (`mijual-logo-ring-{charcoal,white}.png`) and `PretendardVariable.woff2` live in the design
  project. `fonts.css` self-hosts Pretendard from `../assets/fonts/PretendardVariable.woff2` and pulls
  IBM Plex Mono from the Google Fonts CDN. **`P5.S10` cannot invent a wordmark** — expect an operator
  co-work (`pending`) hand-off to export those files into the repo. There is **no SVG wordmark**.
- **The exposure contract is not re-decidable.** `mijual.gates.exposure.event_exposure` is the single
  derivation; the API renders what it says. Event exposable iff not suppressed, not withdrawn, no
  blocking flag; field renderable iff `passed` or `tbd`.
- **`추후결정` means *no date*, not *unknown date*** (`ui-traps` #4) — `StateBadge tbd`, never a date
  beside it, never the superseded date it replaced.
- **`option_schedule` dates are not a period** (`ui-traps` #1) — render each option's `detail` string;
  the stored range appears only as the caption, never as a plain 기간 and never as a bar.
- **Numbers drift, rules do not.** The grounding pack is dated 2026-08-20 and the exporter re-dates
  every D-day when re-run. Never overwrite the landed pack to "refresh" it — export to a scratch dir
  with `--out` and diff (P3.REVIEW note 3).
- **Suppression reason codes render as raw English** (§6.1 / D-14) — no Korean render function, no
  fallback string for an unknown code. The real 소규모합병 code is `no_appraisal_right`; R7's
  `GateQueue` card shows an invented `small_scale_merger …` chip that the build-prompt correctly
  overrides (see SIGNOFF R7).
- **Gate-queue rates are computed over distinct `(rcept_no, field_key)` = 633**, not over the 649
  stored rows (16 duplicates).
- **`▷` in admin output is verbatim pipeline output** and must **not** be swapped for 「추정」 — the
  boundary is the source. Everywhere else in the product, 「추정」 is the only estimate mark.
- **Tests stay terse** (repo rule + `qa`): minimal high-value cases, no fixture sprawl. Today's
  baseline is `.venv/bin/python -m pytest` → 59 passed, ~1 s, no network, no model. Keep it that way.
- **No Alembic.** Additive columns go through `mijual.db.schema_sync.ensure_columns`; new tables via
  `create_all`. The corpus is re-collectable but must not be reset casually.

## Constraints

- **RESPECT THE DESIGN.** Nothing approved is dropped, simplified, restyled or "improved". Where a
  design implies data that does not exist, **build the backing** (D-15's rule) — never quietly drop
  the feature. A nit in a landed record is an apply-time to-do, **never an edit to the record**.
- **Read `SIGNOFF.md` before any `build-prompt.md`**; the supersession chain (`frontend` v0002) is
  binding: cosmos-dark over "light theme only" · 「추정」 over `▷` · 내 종목 조회 over 내 종목 연결 ·
  AI 질문 over 해설 · widget 440×620 over 380×560.
- **Korean-only product surface; English for work, notes and commits.** Copy is locked by default and
  comes from `grounding/copy-inventory.md`, which is generated from the code that emits it. **Inventing
  a Korean string is a design change**, not an implementation detail.
- **No OpenDART call and no LLM call in a request path** (`architecture` boundary). A dead worker
  leaves the board **stale, never dark**.
- **The AI 질문 agent, its conversation storage and its surfaces are P6.** Deployment, hosting, the
  D-day mail channel and the 결격-grade unattended window are **P4**.
- **The admin panel has no mutation endpoints at all** (§6.5 / D-14) — no click may override a gate
  verdict. Desktop-only, linked from nowhere in the reader chrome.
- **Stored reader PII is exactly email + password hash.** Anonymous state never reaches the server:
  조회 holdings in sessionStorage, anonymous/sample portfolio edits in localStorage, migration
  **offered, never automatic**.
- **Estimates and facts:** an estimate never renders untagged, a fact never carries the mark, money
  never appears before 확정발행가 (mail included), ②/③ rows never carry a won amount, and D-days are
  computed upstream in KST — never in the browser.
- Docs are versioned **once, at `P5.REVIEW`**. Every slice that changes durable truth appends a
  one-line note to *Doc impact* below instead.

## Doc impact

_One line per durable-truth change; `P5.REVIEW` consolidates these into doc versions._

- (`P5.DECOMP`) none — decomposition only; no durable truth changed. Expect this list to grow
  substantially: `api` is still the bootstrap v0001 stub and `backend` is still the bootstrap v0001
  stub, and both become real at this phase, alongside `architecture` (the HTTP layer it explicitly
  defers to "P3"), `frontend`, `experience`, `security`, `operations` and `decisions`.
- (`P5.S1`) **`architecture`** — the HTTP layer it deferred to "P3" now exists: `mijual.web`
  (app factory · lazy one-engine/rollback-only session dependency · error envelope · KST time
  policy · `routers/`), added to the module map and the stack table; the "no OpenDART/LLM call in a
  request path" boundary is now **enforced by a test** (`tests/test_web_smoke.py` AST import scan),
  not just structurally true. **`backend`** — first real content over the v0001 stub: the package
  layout, `create_app`, `.venv/bin/uvicorn mijual.web.app:app --reload`, the read-only session
  contract (P5's HTTP layer never commits), and `fastapi`/`uvicorn`/`httpx` in `pyproject`.
  **`api`** — the service-wide **error envelope** `{"error": {code, message, message_ko?, fields?}}`
  with `message_ko` present only where the product already owns the Korean string, plus the
  **absolute-KST timestamp / bare-calendar-date serialization policy**, plus `GET /health`
  (DB-independent by design). **`qa`** — suite baseline 59 → **62 tests**, still ~1 s, no network/
  model/DB. **`operations`** — `/health` is a liveness probe that deliberately does not touch
  Postgres ("stale, never dark"); data freshness is a separate corpus fact served by `P5.S3`.
- (`P5.S2`) **`api`** — the **presentation contract** every surface reads is now a named,
  versionable shape set: `countdown` (`label_ko` · `date` · `dday` · `days` · `window` ·
  `window_state` · `reference` · `source`, one governing anchor per rights type),
  `corp_name_in_body` / `corp_name_agrees_with_body`, `offering_inputs`, `lapse_result`, the
  per-field payload (`display` · `value` · `quote` · `span` · `rcept_no` · `korean_name`), the
  발행사 기재 불일치 two-reading shape, and the single board/landing summary — plus three
  contract-wide serialization rules (**every value carries `estimated`**; money and ratios are
  exact decimal **strings**, counts are ints, calendar dates are bare `YYYY-MM-DD` and instants
  are absolute `+09:00`; an absent value means an **absent key**, never `null`) and the
  English-`snake_case`-keys / Korean-only-as-content convention. **`backend`** — the new pure
  derivation package `mijual.present` (`values` · `event` · `money` · `summary`) and what its
  constructors *refuse* to build: a blocked field, a date beside 추후결정, an untagged estimate
  and a won amount before 확정발행가 are now **unconstructable**, not merely forbidden.
  **`architecture`** — a layer between the pipeline and the HTTP layer, with two boundary rules:
  **`web → present`, never the reverse** (so instant serialization is restated rather than
  imported back), and `present` imports nothing that can spend an OpenDART request or a model
  call — enforced by an AST scan in `tests/test_present.py`, as `web` already is. Measured
  consequence worth recording: **`mijual.estimate` pulls `mijual.dart` + `mijual.collect` +
  `mijual.extract` at module level**, so the retrospective 소멸가치 numbers must reach a request
  path from persisted state, never from `build_report`. **`qa`** — suite baseline 62 → **75
  tests**, still ~1 s, no network/model/DB; the derivation was additionally cross-checked
  against all 11 landed grounding samples out-of-suite (a dated pack is not a fixture).
- (`P5.S3`) **`api`** — the four read endpoints are now a contract: `GET /board/summary` (one object
  for every landing number, incl. `next_lapse{date,corp_name,target}` and
  `freshness{as_of,stale,age_hours,stale_after_hours}`), `GET /board?rights=` (whole-board tab
  `counts` + ranked `rows` + the `open_now` / `tbd` strips with `count` vs `total`),
  `GET /events/{rcept_no}` and `GET /events/{rcept_no}/corrections`; **the route key is `rcept_no`,
  resolved against every stored version and renderable-event-first**; a non-renderable event is a
  **404 envelope**, never a page explaining itself; a 철회 page carries its notice + withdrawal
  evidence and nothing else. **`backend`** — `mijual.web.reads` (the batched read layer), the
  `present` additions (`board_row` · `convertible_view` · `correction_story` · `freshness` ·
  `lapse_totals`), `gates.exposure.exposure_of` as the pure derivation behind `event_exposure`, and
  the two new settings `MIJUAL_COUNTDOWN_CUTOFF_TIME` / `MIJUAL_STALE_AFTER_HOURS`.
  **`architecture`** — `readable_versions` / `document_of` / `current_version` moved to
  `mijual.db.repository` (a neutral home; `mijual.extract.runner` re-exports them), so the exposure
  contract no longer reaches the extractor through a function-local import and **no request path
  imports a spending module even at call time**; the serving precomputation seam is now explicit
  (worker computes → request path reads). **`data`** — new table **`offering_input`** (one row per ①
  event: `inputs` JSON + `price_confirmed` / `subscription_start` / `subscription_end` /
  `decision_rcept_no` columns) and additive column **`performance_report.lapse`**, both written by
  `python3 -m mijual.estimate snapshot`, both additive (`create_all` + `ensure_columns`, no Alembic).
  **`operations`** — **기준시각 = `max(Event.last_seen_at)`** (a corpus fact, not the request time) and
  the **18-hour stale threshold** derived from the 07:30/19:30 KST beat schedule; the snapshot worker
  must run after each pipeline run and is **not yet a beat stage**. **`decisions`** — two stated
  defaults: the landing countdown ticks to **end of the 청약 day (KST)**, overridable per deployment;
  **stale after 18 h**, overridable. **`qa`** — suite baseline 75 → **83 tests**, still ~1 s, no
  network/model/DB; the endpoints were additionally curl-verified against the live corpus
  (718.1억원 / 548.7억원 / 51,253,956 / 365,527,824 / 14.02% / 15건 / 69건 all reproduce).
- (`P5.S4`) **`api`** — 내 종목 조회 is now a contract: `GET /stocks?q=<종목명|종목코드>` (resolution
  **plus** the whole page on a hit; a miss is `200 {"query", "found": false}` — a search that finds
  nothing is a **result**, not an error, and names no reason) and `GET /stocks/{corp_code}` (the
  stable-handle link-out; unknown code → 404 envelope). The page shape is
  `{stock, reference, rights{count,rows}, lapse{coverage,totals,rows,pending?}}`, where a rights row
  is the event view plus **the detail-grade `offering`** on ① (R4 does the N주 conversion, so the row
  carries 배정비율 to ten decimals · 초과청약 비율 · `unit_value` + floor · `final_price_date`) and
  R3's six-value `convertible` strip on ②; a 놓친 돈 row is `lapse_result` plus the 매매기간
  countdown/citation/factors **only when the 유상증자결정 is exposable**, plus `issuer_disagreement`
  where the filing contradicts itself. Two contract-wide statements: these endpoints serve
  **factors, never products** — no holding count is accepted on any path and no per-holding number
  appears in any payload — and the **coverage boundary is served**
  (`{start: 2026-01-01, end: <today KST>, convertible_start: 2025-06-01}`), with anything outside it
  **absent rather than zero**. **`backend`** — `mijual.web.routers.stocks` + `reads.resolve_corp`
  (four unique-or-decline tiers: 종목코드 → 회사명 → normalized 회사명 → unique normalized prefix;
  ambiguity resolves to nothing) · `reads.load_stock` (one load, both sections) ·
  `reads.STOCK_FIELDS` / `LAPSE_COVERAGE_START` / `CONVERTIBLE_COVERAGE_START`; `present` gains
  `LapseTotals.payload()` (a **subset** total, emitting no zero) and the now-public `bare_name` —
  one definition of "the same company, written differently", shared by 종목 resolution and the 본문
  identity check. **`qa`** — suite baseline 83 → **87 tests**, still ~1 s, no network/model/DB; the
  endpoints were additionally curl-verified against the live corpus (한화솔루션 206.4억원 / 증서
  5,525원 / 배정비율 0.2465120994, 에스에너지 7.2억원, 대한광통신 16.2억원 + 발행사 기재 불일치,
  계양전기 청약 마감 2026-09-04, 1.1–5.7 KB in 8–24 ms).

## Open Questions

- **The countdown cut-off instant** — *stated default landed, still the operator's call*: `P5.S3`
  serves R2's own assumption (end of the 청약 day, 00:00 KST of the next day) behind
  `MIJUAL_COUNTDOWN_CUTOFF_TIME`, so the real 접수 마감 시각 replaces it with no code change.
- **The stale threshold in hours** — *stated default landed*: **18 h**
  (`present.DEFAULT_STALE_AFTER_HOURS`, override `MIJUAL_STALE_AFTER_HOURS`), derived from the
  07:30/19:30 KST beat schedule. Operator may still choose another number.
- **The "정정 이력" button label** — exited P3 unresolved and is carried here (`experience` v0002,
  `product` v0003); `P5.S13` needs it.
- **Binary design assets** — who exports the wordmark/ring PNGs and `PretendardVariable.woff2` out of
  the Claude Design project into the repo (`P5.S10`). Almost certainly an operator co-work step.
- **The concrete admin route** (`/ops` is the example, not the decision) and how the operator
  credential is issued — `security` calls these **deploy** decisions (P4); `P5.S9`/`P5.S17` need a
  working local value in the meantime.
- **vocky's real observation API** — its shape, and whether reaching it needs a credential the
  operator must supply (`P5.S18`).
- Not P5's: the **운영자 연락처 string** for `get_contact` (P6, operator-provided, never invented).
