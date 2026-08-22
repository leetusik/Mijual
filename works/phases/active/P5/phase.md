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

### `P5.S5` — the pairing is identity-scoped now; the rule, the numbers, and what it did *not* fix

D1 is **closed**. The 본문 `<CORRECTION>` 최초제출일 is now an identity check as well as evidence, and
the whole repair was offline: **0 OpenDART requests, 0 model calls**, `var/preP5S5.dump` is the
pre-run corpus.

**The rule** (`mijual.bodydoc.backfill._apply_hint`; the three constants are named and commented
there). When the hint names no event of this corp+subtype:

1. **Self-evidence wins.** The hint matches a filing the event already holds (`rcept_no[:8]` **or**
   `rcept_dt`), or is within **`HINT_SKEW_DAYS = 7`** of the event's key → nothing moves, the version
   stays `mismatch`. This is what keeps N31's ±7-day skew — and every ① row — untouched.
2. **Only on a *rendered* event** (`exposure_state in {exposable, withdrawn}`): a **unique** other
   event within **`HINT_NEAR_DAYS = 1`** → **reattach** there; nothing at all → **split** onto
   `ensure_event(corp, subtype, hint)`, suppressed **`foreign_correction_head`**, flagged
   `hint_foreign_split`, `hint_status='split'` (sticky, and `pairing_is_resolved`).
3. Everything else is P2.S3's behaviour unchanged.

1. **Measured: the defect is wider than N62's 3 filings and far narrower than `hint_mismatch`.**
   653 mismatches, but **201 are a 1-day 접수일/제출일 skew** (DART accepts an after-hours 제출 the
   next day — 알파AI's original `20250731000550` is *dated* 2025-08-01), **111 name a filing the
   event already holds**, and only **46 sat on an event the product renders**. Of those 46, **22 were
   the corp's own earlier 사채 one 접수일 away** (알파AI 2025-05-07→2025-05-08, 차AI헬스케어
   2025-03-27→03-28, 아리바이오홀딩스 2025-04-29→04-30) — mis-*attachments*, not unknown originals.
   Splitting those (the plan's single shape) would have minted duplicate events, i.e. manufactured
   D2/N81's disease. Hence the two arms. **No hint anywhere in the corpus has two events within 3
   days of it**, so unique-or-decline never had to decline.
2. **Before → after, and the 488 is the same 488.** ② gate failures on exposable events **6 → 1**
   (the survivor is 에이럭스 `20250908000110` `span_unresolved` — a citation defect, not pairing);
   exposable **488 = 50/422/16 unchanged**; ranked rows 389 · ② 진행 중 57 · 추후결정 4 · 30일 이내 33 ·
   소멸 앞둔 15 · 실적보고서 69 · 718.1억/548.7억/0.1402 · 퓨쳐켐 2026-09-04 — **all identical**; ①
   gate rows **261 passed / 4 tbd / 4 failed unchanged** and ① renderable field instances unchanged
   (the plan's "42 passing + 2 tbd" is N63's P2-era ① board; today's equivalent is 48 + 2 = 50).
   Versions **3,990** and extractions **649** unchanged — **0 rows added, 0 removed, 49 re-parented**.
   New: **+14 events**, every one a suppressed chain head (12 ② + 2 ①). `hint_status`: mismatch
   653→593, reattached 76→98, duplicate 364→375, **split 27**.
3. **Two ② 철회 pages went away, and that is the finding.** 드래곤플라이 `cvbdIsDecsn/2025-03-20` and
   캔버스엔 `cvbdIsDecsn/2025-01-20` held **no original and no detail row of their own** — every
   version was another bond's 정정, so the 「이 사채 발행은 철회되었습니다」 they rendered was a
   different 사채's withdrawal. The versions (and the 철회 evidence, re-derived by `gates run`) now
   sit on the head events. `_retire_emptied` was widened to relabel any event whose every version
   left: an event with no version has no filing number and cannot be cited, so it must not render.
   `R2:withdrawn` 8 → 6 is exactly these two.
4. **The heads are suppressed on purpose, and they self-heal.** Keyed on the *declared* 접수일, so a
   later run that ever collects that original hits the same N2 key — `ensure_event` finds the head
   and `persist` clears the suppression. A distinct reason code (**not** `unpaired_correction`) is
   deliberate: `retire_superseded_unpaired` retires an `unpaired_correction` event as soon as *any*
   other event holds one of its `rcept_no`, and with N21's residue (840 of 3,024 `rcept_no` under 2+
   keys) that would have retired a head the moment it was minted. **`P5.S9`/`P5.S17`: the admin
   suppression list gains `foreign_correction_head`** — raw English, like every other reason code.
5. **The repair converges in two passes and is idempotent from the third.** Each minted head becomes
   an *exact* target for other versions naming the same date, so pass 2 moved one more version
   (케이이엠텍) and pass 3 moved none. **Re-run order after any collect:
   `bodydoc backfill` → `gates run` → `estimate snapshot`.**
6. **The collector can no longer undo it.** `collect.runner.persist` skips a `rcept_no` whose
   identity a hint has settled on another event (`_identity_owner`, reported as `identity :` in the
   run render) and writes that run's `list`/detail snapshot **onto the owning version instead** —
   evidence follows the filing, and this is the one path by which a split head can ever acquire the
   `cvbdIsDecsn` row that would let it render on its own. Without the guard, N78(a)'s proposed
   full-2026 re-collect would nearest-earlier-pair those filings back onto the wrong 사채, spend
   requests re-fetching their 본문, and then hit the head's unique constraint. **Any later
   re-collection must keep this.**
7. **What this rule cannot fix, by construction: D2.** The two `hint_duplicate` events
   (코이즈 `20260122000058`, 사토시홀딩스 `20251219000402`) still carry a version whose hint names a
   *different, existing* event — that is a duplicate record, not a foreign document, and the fix is
   still the corpus-mutating merge P5.DECOMP note 2 describes. Verified as an invariant after the
   run: those 2 are the **only** foreign-hint versions left on a renderable event, and **0**
   extraction rows on any of the 488 cite a filing their event does not hold.
8. **Scope knob, for whoever wants it later.** The literal "no collected original" test fires on
   **398** versions corpus-wide; 352 of them sit on suppressed placeholders and
   `superseded_by_pairing` residue that no surface reads. They are excluded on purpose —
   restructuring ~200 dead records buys nothing and could clear `hint_split_evidence` (a **blocking**
   flag) on events whose exposure has never been measured. Widening the scope is a correctness
   change, not a cleanup: measure the exposable count on both sides of it (N81's rule).
9. **Gotcha for any job that re-parents a version:** the move is a column write, so both events'
   loaded `versions` collections go stale — `_apply_hint` expires them explicitly and
   `backfill_corrections` calls `expire_all()` before the retire/split-evidence passes. A test caught
   this, not review.
10. **`P5.S13` note:** an exposable ② event can have **no readable version at all** (엑시큐어하이트론
    751 now does — its original carries only `list` + `cvbdIsDecsn`, no 본문). Its 정정 rail then marks
    **no** row `is_current_readable`. This is not new and not rare: **239 of the 422** exposable ②
    events have no 본문 anywhere, which is why ②'s arm of the exposure contract requires the API row
    and not a document (N6). The card renders from the API strip; the 본문 fields are absent, not null.
11. **Freshness caveat for `P5.S9`/P4:** `ensure_event` bumps `Event.last_seen_at`, so an **offline**
    maintenance run moves the landing's 기준시각 (`max(last_seen_at)`) to "just now" without a single
    OpenDART call. Harmless here (hours), but a freshness signal that a repair job can reset is worth
    knowing before it is used as an alert.

### `P5.S6` — ③ 매수예정가격 exists, and it cost nothing: the layer decision and the numbers

D-15 is **backed**. 12 of the 16 exposable ③ events now serve 매수예정가격 as a gated fact with a
verbatim citation; the other 4 serve **no key at all**. **0 LLM calls, 0 OpenDART requests, ▷ $0.0000.**

1. **The plan's shape moved one layer down, and the corpus is why.** `plan.md` specified a
   `FieldSpec` in `extract/fields.py` + a bounded Gemini run. Reading the ③ 본문 first (the step the
   plan asked for) showed the value is **not LLM-tier**: 매수예정가격 is a **본문 form cell** —
   `13. 주식매수청구권에 관한 사항` → qualifier `매수예정가격` — that `bodydoc.extract_labels`
   already parses with a real span, present in **95 of 95** stored ③ 본문 (70 a number, 25 `-`), and
   the ③ detail API row carries the same number in **`aprskh_plnprc`**, agreeing **17/17 with
   0 mismatches** over every comparable current version. Paying a model for it would have broken the
   phase's own anti-rule *and* `fields.py`'s registry rule ("a field that turns out to be
   label-readable belongs in `bodydoc`, not here"). So it was built as the **`본문-label` tier's first
   stored field**.
2. **The new layer, and where later work plugs into it.** `mijual/extract/labelfields.py` —
   `LABEL_SPECS` (declaration: key · Korean name · 본문 위치 · label block · qualifier · gate),
   `read_document(doc, spec)` (pure), `read_label_fields(factory, …)` (the corpus pass).
   **A second label field is now a registry entry plus a gate, nothing more.** Rows land in the
   *same* `Extraction` shape, so exposure / `present.field_payloads` / `/events/{rcept_no}` needed
   **no change at all** beyond `FIELD_NAMES_KO`.
   | you need | use |
   |---|---|
   | the label-tier registry | `from mijual.extract.labelfields import LABEL_SPECS` |
   | one document's reading | `read_document(doc, LABEL_SPECS["appraisal_price"])` |
   | the corpus pass | `python -m mijual.extract labels [--rights R3] [--current-only]` (0 calls) |
   | a rights type's label fields | `label_field_keys_for("R3")` |
3. **The citation is composed, and self-checked.** The quote is the document's own two adjacent
   cells (`매수예정가격 5,649`), located with the same `QuoteLocator` an LLM quote goes through and
   **accepted only if its span ends exactly where the label parser's own value cell ends**.
   Measured: **70/70** compose, resolve and verify; 0 fell back to the narrower label span, 0
   unresolved. **A label row relocates against the whole document, never a prompt-sized window** —
   the cell sits at char 65k of a 120k-char 합병 본문, so `relocate`'s default head window would have
   lost it (handled in `runner.relocate_spans`).
4. **The gate is two machine witnesses** (`gates.rules.gate_appraisal_price`): citation → positive 원
   → the value equals the number the citation prints → **value == API `aprskh_plnprc`**. An absent
   API value (`-`, or a superseded version, whose reference row belongs to a newer filing) is a
   **skip**, not a pass in disguise; the document's own number still stands, because unlike a prose
   reading there is no hallucination to defend against. Result over the corpus:
   **47 passed / 0 tbd / 0 failed / 14 not_evaluable**, and **no `appraisal_price_*` reason code
   fired anywhere**.
5. **An empty cell is `absent`, never 0 and never a null.** The 4 exposable ③ without a price:
   모다이노칩 (소규모합병 — the 본문 says the right is not granted) and 케이피항공산업 ·
   미래에셋비전스팩7호 · IBKS제25호스팩 (스팩 합병 — the price is deferred to the 증권신고서). All four
   print `-` in the cell *and* in the API row. **There is no `추후결정` case for this field**: none of
   those filings writes 추후결정 in that cell (they write "향후 … 결정하여 공시할 예정"), and N40's rule
   stands — only positive evidence earns a `tbd`. **`P5.S13`: a ③ page with no `appraisal_price` key
   renders no row at all.**
6. **Before → after: the diff is only the new field.** exposable **488 = 50/422/16 unchanged**;
   every event state unchanged; every other field's gate distribution **byte-identical**; extraction
   rows **649 → 710** (+61); renderable fields gain **`appraisal_price: 12`**; landing numbers
   (33 · 57 · 4 · 15 · 69 · 718.1억/548.7억 · 0.1402 · 퓨쳐켐 2026-09-04) all identical. All 16
   exposable ③ pages still answer **200**, and 12/12 served citations re-slice to their quote *and*
   to their value.
7. **Run order, and a trap inside it: `extract labels` → `gates run`, always.** `upsert_extraction`
   clears the gate verdict on **every** write (the existing contract — a re-read invalidates the
   previous verdict), so a label pass on its own leaves 61 rows with `gate_status = NULL` and the ③
   pages temporarily without the field. The pipeline's stage order does this correctly, and the free
   pass now runs **first inside `stage_extract`, outside `extract_max_calls`** — budgeting a pass
   that spends nothing could only starve it. Verified idempotent: two `labels` → `gates run` cycles
   reproduce a byte-identical measurement.
8. **The 정정 diff now covers label fields** (`run_corrections` diffs
   `prose_task.fields + label_field_keys_for(rights)`), so a 정정 that revises the 매수예정가격 shows
   up in the CorrectionStory's `field_moves` rather than changing a published number silently. It
   takes effect on the next 정정 run; stored interpretations were not re-run (and cost nothing today).
9. **Freshness caveat, wider than S5 note 11 — `P5.S9`/P4 should know.** `Event.last_seen_at` is
   `onupdate=utcnow`, and `gates run` writes `exposure_checked_at` on every event every run. So the
   landing's 기준시각 (`max(last_seen_at)`) is moved to "just now" by **any** gate run — not only by
   `ensure_event` during a collect. Measured live: `/board/summary.as_of` was 02:48 immediately after
   an offline gate run. **A freshness signal that an offline maintenance job resets cannot, by
   itself, be an alert that the collector stopped.**
10. **Evalset is untouched and structurally unaffected**: `evalset/sample.py` skips a row whose
    `field_key` is not in `FIELDS`, so the label field is outside its universe. Whether a
    deterministic two-witness field ever belongs in an *accuracy* evalset is a `P5.REVIEW` question,
    not a defect. Likewise `scripts/export_design_grounding.py` would now emit `appraisal_price` in ③
    samples — **the landed pack is dated and must not be regenerated** (P3.REVIEW note 3).

### `P5.S20` — D4 is closed: a citation states its number, in one part or in parts that sum

The 7 figures S3 measured (에스에너지 · 루닛 · SKC · 한화솔루션) now carry **one span per
addend**; **0 of the 269 stored 실적보고서 figures is uncitable** (was 7). Offline: **0
OpenDART requests, 0 LLM calls**, and every rendered number is byte-identical before → after
(718.1억/548.7억 · 51,253,956/365,527,824 · 0.1402 · 488 = 50/422/16 · 33 · 57 · 4 · 15 · 69 ·
퓨쳐켐 2026-09-04 · `estimate report` diff empty).

1. **The payload shape `P5.S13`/`P5.S14` render — three states, no fourth.** A `Figure`
   carries **either** `quote` + `span` (one cell) **or** `parts` (≥ 2 addends, each
   `{quote, span}`, and they sum to `value`) **or** neither (uncitable → render **no** chip;
   `rcept_no` still links to DART). The three are mutually exclusive *by construction* —
   `present.Figure` raises on `quote` beside `parts`, and on a one-element `parts`.
   ```json
   "warrants_exercised": {"value": 38430497, "estimated": false,
     "parts": [{"quote": "38,427,609", "span": [285071, 285081]},
               {"quote": "2,888", "span": [285911, 285916]}],
     "rcept_no": "20260730000366"}
   ```
   **Render every part verbatim.** Never one of them, and never joined into a single quote
   string: the sum is printed **nowhere** in the filing, so a joined quote would be a sentence
   the document does not contain. Live today on 4 figures (한화솔루션's 청약 is the landing's
   own example); `warrants_issued` and the other 58 served counts stay single-quote.
2. **Why the figures existed at all.** The filer splits the same 청약 by 경로 — 한국예탁결제원
   *and* 직접청약/실질주주 — so Ⅶ 청약내역 states 38,427,609 and 2,888 on two rows and the
   number the report means (38,430,497) on none. All 7 cases are exactly two rows; the missing
   term was small (866 · 10 · 2 · 239 · 41 · 2,888 · 149), which is why the defect read as a
   typo rather than a sum. `perf.py` summed correctly and kept only the first cell.
3. **Stored form: additive and byte-compatible.** `perf.Cited.as_json()` emits `"parts"`
   **only** on a real multi-addend sum, so the other 262 figures serialize exactly as before
   and every reader that knows only `raw`/`span` still works (it sees the first addend).
   `Cited.citations` normalizes both forms. `performance_report.lapse` did not change at all —
   `LapseRow` carries values, not citations.
4. **New offline command, and the run order grows a step.**
   **`python -m mijual.estimate reparse`** re-reads every stored 실적보고서 from its own
   `payload_bytes` and rewrites only the parse-derived columns (`facts` · `form` ·
   `parse_status` · `parse_note`) — never the event link, the bytes or the hash. **0 requests,
   0 model calls**, idempotent (second pass: `0 with changed facts`). This is how *any* future
   `parse_performance` change reaches the corpus: `facts` is otherwise only written by
   `estimate collect`, which needs a client to discover filings. **Order after any collect:
   `bodydoc backfill` → `gates run` → `estimate reparse` → `estimate snapshot`.**
5. **The guard was generalized, never relaxed.** `present.money._cited_count` now asks
   "does this text state this number — in one cell, or in parts that add up exactly?" A
   stored figure that answers no still loses its chip and keeps its `rcept_no`. The
   발행사 기재 불일치 rule is untouched: still 5 filings, both readings, both quotes,
   `used` on 발행 − 청약 (verified live on 대한광통신).
6. **Two readers of `facts` citations existed, not one.** `evalset/sample.py`'s 실적보고서
   rows showed the grader the first addend beside the summed value — the same false-citation
   shape, in the artifact that measures accuracy. Its `quote` column now prints every addend.
   Sampling is unaffected (the draw keys on `unit`/`stratum`/`hard_case`). **`P5.S17`'s
   정확도 tab reads this sheet — it inherits the fix, not a caveat.**
7. **Gotcha for anyone touching `perf.py` again:** the pattern to watch for is
   `x = x or cell` **beside an accumulating `+=`** — that is the shape that drops evidence.
   The three remaining `or` assignments (`lapse_stated` · `lapse_with_fractions` ·
   `fractional_shares`) are first-*header*-wins over one printed cell, not addends, and the
   corpus confirms it: all 262 single-cell figures state their own number exactly.

### `P5.S7` — reader auth exists; the decisions, the seams, and the first writes

`security`'s four open apply-phase questions (cookie name/flags, lifetime, session
mechanism, CSRF) are **answered in code**. **0 new dependencies** (`pyproject` untouched),
0 requests, 0 model calls, and **no existing route is gated** — every anonymous surface
still answers 200 without a cookie.

**Import map, so no slice goes looking:**

| you need | import |
|---|---|
| the reader's identity on a gated **read** | `from mijual.web.auth import ReadAccount` → `def holdings(account: ReadAccount)` |
| …on a gated **write** | `from mijual.web.auth import WriteAccount` (shares the request's write session) |
| "who is this, if anyone" | `auth.current_account(db, request)` → `Account | None`, never raises |
| a committing session | `from mijual.web.deps import WriteSession` |
| the CSRF header name | `from mijual.web.csrf import CSRF_HEADER` (`X-Mijual-CSRF`) |
| to send anything | `from mijual.mail import Mailer, Message` → `request.app.state.mailer` |
| the account payload a surface renders | `auth.account_payload(account)` → `{email, created_at}` |

**Endpoints** (no prefix, like the rest): `POST /auth/signup` (201) · `POST /auth/login` ·
`POST /auth/logout` · `GET /auth/me` · `POST /auth/reset/request` ·
`POST /auth/reset/confirm` · `DELETE /auth/account`. Structural codes only, no Korean:
`email_taken` 409 · `invalid_credentials` 401 · `password_too_short` 400 ·
`invalid_email` 400 · `invalid_reset_token` 400 · `unauthenticated` 401 ·
`csrf_required` 403. **`P5.S15` renders the single body line (불일치 / 중복 가입 /
8자 미만) from the code** — the API writes no failure copy, by S1 note 1's rule.

1. **The session is a row, and that is the whole answer to "immediate".** `AuthSession`
   holds a **digest** of the cookie token, never the token. 로그아웃 deletes the row;
   계정 삭제 deletes the account and the ORM cascade takes the sessions and reset grants
   with it. A signed stateless cookie would have needed a revocation list — i.e. this
   table — and would have saved no query, because an authenticated request loads the
   account anyway. **A cookie is worthless the instant its row is gone** (verified live).
2. **The cookie, decided:** `mj_session`, `HttpOnly`, `SameSite=Lax`, `Path=/`, `Secure`
   from `MIJUAL_COOKIE_SECURE` (**off** locally on purpose — a `Secure` cookie on plain
   http silently never arrives; **P4 must turn it on**), `Max-Age` 30 days. The ops door's
   cookie name is **reserved as `mj_ops`** (`auth.OPS_COOKIE`) so `P5.S9` cannot collide
   with the reader's — `security` requires it to be differently named.
3. **Lifetime is 30 days, absolute, and never extended on a read** — a sliding window
   would have to write during `GET /auth/me`, and a GET may not write. Renewal happens on
   the next login, which is already a write. If a reader-retention argument ever wants
   sliding sessions, it needs a `POST`-shaped refresh, not a quiet write on a probe.
4. **CSRF is service-wide middleware, not a per-route dependency**
   (`mijual.web.csrf.register_csrf_guard`): every `POST`/`PUT`/`PATCH`/`DELETE` must carry
   **`X-Mijual-CSRF`** (any non-empty value) or it is refused with `403 csrf_required`
   *before* the route runs. A cross-origin page cannot set a custom header without a CORS
   preflight this service does not grant (no CORS is configured — `P5.S10` owns that), so
   nothing has to be minted, stored or rotated. **`P5.S8`/`P5.S9`/`P5.S17` inherit this:
   every mutation, including the admin login POST, needs the header, and `P5.S10`'s client
   should set it once in the fetch wrapper.**
5. **The first committing dependency, and the GET rule got *stronger*.**
   `mijual.web.deps.WriteSession` commits on success and rolls back on any exception —
   and **refuses a safe HTTP method outright** (`RuntimeError`), so a `GET` cannot even
   acquire it. `DbSession` is untouched and still rollback-only. S1 note 4's guarantee is
   now enforced from both ends; a test pins both halves.
6. **scrypt, stdlib, and the parameter ceiling is the reason for the parameters.**
   `n=2**14, r=8, p=1` — ~25 ms/hash measured, and the largest `n` that fits OpenSSL's
   **default `maxmem`** (`n=2**15` raises "memory limit exceeded" unless a private knob is
   turned up — a login endpoint one deployment away from raising). Hashes carry their own
   parameters (`scrypt$n=16384,r=8,p=1$salt$key`), so an upgrade is: bump
   `passwords.CURRENT`, and `needs_rehash` re-hashes each account at its next successful
   **login** — never a mass reset, never a locked-out reader. Argon2id remains one branch
   in `verify` away if a dependency ever becomes acceptable.
7. **`MIJUAL_SESSION_SECRET` peppers, it does not sign** — HMAC-SHA256 over the token, so
   a stolen database dump holds nothing replayable as a cookie or a reset link, and
   rotating the key logs everyone out (the lever you want in that hour). Unset is a
   **development** state: unkeyed SHA-256 plus one log warning, so local dev needs no
   secret. `Settings.require_session_secret()` exists, unused in P5, for a **P4**
   deployment that would rather fail than start unkeyed. New settings, all three:
   `MIJUAL_SESSION_SECRET` · `MIJUAL_COOKIE_SECURE` · `MIJUAL_APP_BASE_URL`
   (default `http://localhost:3000`, the reset link's origin).
8. **The mailer seam carries data, not copy.** `mijual.mail.Message(to, kind, data)` — no
   subject, no body: writing a Korean subject line in P5 would be **inventing product
   copy**, and R5's signed mail spec is P4's item. `ConsoleMailer` prints
   `[mail:password_reset] to=… url=… expires_at=…` to the server's stderr and sends
   nothing. **P4 implements `Mailer.send` and passes it to `create_app(mailer=…)`; no
   route changes.** The reset link is `MIJUAL_APP_BASE_URL` + `/auth/reset?token=…`
   (`auth.RESET_PATH`) — **`P5.S15` owns that page**.
9. **Two prohibitions are structural, and were verified live.** A login failure is one
   code for a wrong password and for an address with no account, *and* the miss path burns
   a scrypt verification against a dummy hash so the two do not differ in timing. A reset
   request answers `{"requested": true}` for a known and an unknown address alike, and the
   link never appears in an HTTP response — only in the server's own log.
10. **The account table is deliberately barren, and `P5.S8`/`P5.S9` must keep it that
    way.** `account` = `id · email · password_hash · created_at · updated_at`. No name, no
    phone, **no admin flag** (R7's door is a separate credential), no activity trail, and
    **nothing that could ever join to a conversation** — DECOMP note 5(b)'s promise is
    trivially intact because there is nothing to join with. R7's 독자 계정 table wants
    이메일 (here), 가입일 (`created_at`), 포트폴리오 종목 개수 · 알림 설정 · **샘플 로드
    여부** — the last three belong on **`P5.S8`'s** tables, not on `account`.
11. **The FK seam `P5.S8` builds on:** hang holdings/preferences/챙긴 돈 off `account.id`
    with `ondelete="CASCADE"` **and** an ORM `cascade="all, delete-orphan"` relationship.
    Both halves are needed — SQLite (the test engine) does not enforce foreign keys by
    default, so relying on the DB alone would make 계정 삭제's completeness
    environment-dependent. Verified in Postgres: deleting an account took its outstanding
    reset grant with it.
12. **Email is stored in exactly one spelling:** NFKC + strip + case-fold, whole address
    (local part included — no consumer provider treats `A@x.kr` and `a@x.kr` as two
    people, and honouring the distinction would only make 중복 가입 depend on the shift
    key). Plus-tags are **kept** (`a+alerts@x.kr` is a deliverable address a reader may
    want for D-day mail). The typed spelling is not additionally stored.
13. **Anonymous is a result, not a 401.** `GET /auth/me` answers
    `{"authenticated": false}` for a visitor with no cookie — the same shape `P5.S4` uses
    for a search that found nothing, and the honest one for a product where every surface
    but 내 포트폴리오 is anonymous. The chrome can call it on every page load without
    filling a console with errors. It serves the **full** email; the 축약 (앞 4자 + … +
    도메인 끝) is `P5.S11`/`P5.S16`'s rendering.
14. **A password reset revokes every existing session** and then issues a fresh one (the
    reader just proved mailbox control and chose the password, so bouncing them to the
    login panel would be ceremony). A repeated 재설정 request **supersedes** the previous
    unused grant rather than adding a second live key to the mailbox — so the *latest*
    mail is the one that works.
15. **Schema landing, for P4.** The three tables come from `create_all` (no Alembic, per
    the phase rule). The **serving process creates no schema at startup** — it must answer
    while Postgres is down — so they land via any pipeline entry point (all of which run
    `create_all` + `ensure_columns`) or the explicit one-liner in this slice's
    `result.md`. Deploying the API alone against a fresh database would otherwise 500 on
    the first signup.

### `P5.S8` — 내 포트폴리오 exists; the endpoint map, and the decisions `P5.S15`/`P5.S16` inherit

The product's **only gated surface** is built: holdings, the two-section D-day list, 챙긴 돈,
알림 preferences and the anonymous sample. **0 requests, 0 model calls, 0 new dependencies.**

**Import map**

| you need | import |
|---|---|
| the reader's holdings as composition input | `from mijual.web.portfolio import entries_of` → `list[HoldingEntry]` |
| the fixed R5-4 sample composition | `portfolio.sample_entries()` / `portfolio.SAMPLE_HOLDINGS` |
| the whole home payload | `from mijual.web.reads import load_portfolio` (`entries`, `today=`, `claims=`) |
| this reader's 챙긴 돈 marks | `portfolio.claimed_reports(db, account)` → `frozenset[str]` |
| the 시점 칩 (defaults included) | `portfolio.lead_days_of` · `LEAD_DAY_CHOICES` · `DEFAULT_LEAD_DAYS` |
| to change the 수신 주소 | `from mijual.web.auth import change_email` |

**Endpoints** (no prefix, like the rest). Everything but the sample requires the owner:
`GET /portfolio` · `POST /portfolio/holdings` (201) · `PATCH|DELETE /portfolio/holdings/{id}` ·
`PUT|DELETE /portfolio/claims/{rcept_no}` · `GET|PUT /portfolio/notifications` ·
**`GET /portfolio/sample` (anonymous)** · and `PATCH /auth/account` (수신 주소 변경).
Structural codes, no Korean: `holding_exists` 409 · `invalid_shares` 400 ·
`invalid_lead_days` 400 · `not_found` 404 · `unauthenticated` 401 · `csrf_required` 403 ·
`email_taken` 409. **`P5.S16` renders R5's own copy from the code** — and note that R5 wrote
**no** line for "이미 담긴 종목" (see note 3): the client, which holds the whole list, should
route a repeat 담기 to the row's inline 수정 rather than need one.

1. **The portfolio serves factors, not products — the same rule `P5.S4` records, and here it was
   a real choice.** The server *does* know the holding count, so it could have pre-multiplied.
   It does not: pre-multiplying would put a **second multiplication site** in the product for
   one number (조회 composes client-side; 포트폴리오 would compose server-side), which is exactly
   the "두 divergent readouts for the same number" R4 names as the failure mode, and R5 restates
   as "내 종목 조회와 수치 불일치 금지 (같은 contract 소스)". Verified live: the 한화솔루션 row's
   `lapse` block is **byte-identical** to the block `/stocks/00162461` serves for the same
   offering, and `⌊500 × 0.2465120994⌋ = 123주 × 5,525원 =` **679,575원** — R5-4's own card
   figure — appears **nowhere** in the payload. **`P5.S10` must own exactly one implementation
   of ⌊N × 배정비율⌋ × 증서가치 and use it on both surfaces**; two would recreate the defect this
   decision avoids.
2. **One composition function, shared with 조회 at the row level.** A portfolio row *is*
   `reads._rights_row` — the same function `/stocks` uses — plus `shares` (a stored count, not a
   derived number), plus `lapse` on a past ①. `_load_views` / `_events_for_corps` were factored
   out of `load_stock` so both surfaces batch and derive identically. If a row ever needs
   something new, add it there, not in a portfolio-flavoured copy.
3. **A duplicate 담기 is refused, never merged or replaced** (`holding_exists` 409, unique
   `(account_id, corp_code)`). Merging invents a count the reader never typed; replacing
   discards one they did; R5 already ships the honest way to change a 보유량 — the row's inline
   수정. The 409 is a last-resort invariant (two tabs, one account), not a path a reader walks.
4. **`holding.corp_code` is deliberately not a FK to `corp`.** The corp table is pipeline data —
   re-collectable, reset outright when the schema changes (N16) — and a reader's portfolio must
   survive that. A FK would make a corpus rebuild either delete a reader's rows or fail on them.
   The reference is validated **on write** (`stock_by_code`), and a code that later resolves to
   nothing degrades to a holding with **no `corp_name` key** and zero rights, never a 500.
   `shares` is a `BigInteger` on purpose: Postgres `integer` tops out at 2.1 bn and 삼성전자 alone
   has ~5.97 bn shares outstanding. Upper bound `MAX_SHARES = 10_000_000_000`.
5. **The two sections, and where each population lands.** 다가오는 마감 = every dated deadline
   still ahead (D-day ascending), then **② 진행 중** (opened, not closed; most recently opened
   first), then **일정 추후결정** (unranked, no date near it). 지나간 마감 = every anchor already
   behind the reference day, most recent first — a passed ① 매매 마감, a passed ③ 통지 마감, and
   an ② whose window has **fully closed**. An *open* ② is never in 지나간: filing it there is the
   종료 label R5 forbids, spelled as a section heading. The ordering inside 다가오는 is `P5.S4`'s
   (`_live_rank`), because a deadline you can still act on outranks an open window with nothing
   to exercise (R4-4).
6. **`STOCK_FIELDS` is exactly the right subset here, and that is a rule, not a saving.** The
   portfolio loads the four 조회 field keys, so a ③ row carries `dissent_notice_procedure` and
   **not `appraisal_price`**. That is required: R5 says "②/③ → 금액 절대 없음" for this surface,
   and 매수예정가격 (`P5.S6`) is a won figure. R3's **detail page** renders it — a different
   surface with a different signed rule. **Do not "complete" the portfolio row by adding it.**
   Conversely ②'s `convertible` strip (전환가액 · 권면총액 …) **stays**: R5 says "금액 = R4 계약
   그대로" and names ②'s substitute as 희석 컨텍스트, which is that strip.
7. **The 챙긴 돈 key is the 증권발행실적보고서's own `rcept_no`, and the alternatives were worse.**
   The 유상증자결정's number *mutates* to its newest version (N2), so a mark keyed on it comes
   unstuck the day a 정정 lands; an `event.id` is an autoincrement a corpus rebuild does not
   preserve, and `P5.S5` re-parented 49 versions between events. The 실적보고서 is terminal, its
   `rcept_no` is unique, and it is what makes the row exist at all. It is also what the payload
   carries (`lapse.performance_rcept_no`), so the **localStorage** mark an anonymous/sample
   reader keeps addresses the identical row. The table stores account + filing number +
   timestamp — **no amount** — and **the payload has no total anywhere**, so R5-8's "집계·통계에
   미반영" is structural rather than careful. A mark is validated against a real report with a
   `lapse` (404 otherwise) but **not** against the caller's holdings: a reader may sell and their
   claim about a past offering stays true.
8. **`claimed` is absent — never `false` — when nobody is logged in.** The sample and any
   anonymous composition pass `claims=None` and no row carries the key, because a server-side
   `false` would be the product asserting something about a person it has no account for
   (R5: 가짜 사용자 정체성 금지). Verified: `claimed` and `@` appear nowhere in the sample body.
9. **알림 preferences default on **first read**, not at signup, and no row is written until the
   reader saves one.** Creating a row at 가입 would have meant editing `auth.create_account` to
   carry a preference it does not own, and would freeze today's default into every account ever
   created. So **an absent row means the default (7일 + 1일), not "off"** — `P5.S9`/`P5.S17`'s
   독자 계정 table must render it that way. **An empty list is a valid setting and means no mail**:
   R5's mail footer promises "알림 설정에서 끌 수 있습니다" and deselecting every chip is the only
   off switch the signed surface offers, so `[]` persists rather than falling back. Anything
   outside `(7, 3, 1, 0)` is refused — a lead time the UI cannot express is one nobody could
   turn off again. **No sending, no scheduler, no mail body: that is P4's item 1.**
10. **수신 주소 = the account email, and 변경 edits the account** (`PATCH /auth/account`).
    `security` fixes stored PII to email + password hash, so there is no second address column
    and no `notification_pref.address`. Decisions inside it: a duplicate is `email_taken` (two
    accounts cannot share a login identity); **outstanding unused reset grants are revoked**
    (a grant was issued *to an address* that is no longer this account's, and leaving it live
    keeps a working key in a mailbox the reader just moved away from); **sessions are not**
    (the reader is the one doing this); and **no password is re-entered**. That last one is
    worth stating out loud: R5's Notify row is a 수신 주소 with a 변경 affordance and nothing
    else, `P5.S7` already established the precedent — 계정 삭제, strictly more destructive, takes
    no password either — and adding a password field would be **inventing a control the signed
    round does not have**. The consequence is honest and belongs in the review's field of view:
    **a stolen live session can move the address**, i.e. escalate read access into a permanent
    takeover. If the operator wants re-auth here it is a *design* change (a new control on the
    Notify card), not an implementation detail — see the new Open Question.
11. **A stranger's row is a 404, not a 403.** Every holding lookup carries `account_id` in its
    `WHERE`, so a row that belongs to somebody else is indistinguishable from one that does not
    exist. A 403 would confirm that it does. Same shape as `P5.S4`'s "a bad link is an error,
    and it says nothing else".
12. **KakaoTalk has no server field at all** — R5 draws the row with a 「예정」 chip and no working
    control, so a stored flag for a channel that cannot be switched on would be exactly the
    non-functional switch the round forbids. **`P5.S16` renders the row from nothing.**
13. **No anonymous write exists, and that is the design.** `security`: "Anonymous state never
    reaches the server … Migration into an account is offered, never automatic." The 세션 이월
    (R5-3) and 샘플→계정 이전 (R5-4) flows are entirely the client's — when the reader accepts,
    the browser makes the ordinary authenticated `POST /portfolio/holdings` calls; when they
    decline, nothing is sent. **`P5.S16` must not ask for an anonymous endpoint; there is none
    and there must not be one.**
14. **Live sample composition, measured 2026-08-22 — all four pinned filings still resolve to
    the event R5-4 named**, and the surface shows **one row R5's card does not**:
    | R5 pin | resolves to | live row |
    |---|---|---|
    | 계양전기 `20260724000546` | ev3 `piicDecsn` 2026-05-08, exposable | ① **D-3 · 2026-08-25**, `price_confirmed: false` → **no money key** ✓ |
    | 대동기어 `20251016000315` | ev724 `cvbdIsDecsn`, exposable | ② 전환청구 개시 **D-63 · 2026-10-24**, 오버행 6.68% ✓ |
    | 한화솔루션 `20260720000067` | ev84 `piicDecsn`, exposable | ① 소멸 **D+43**, 20,635,460,625원 「추정」 ✓ |
    | 세기상사 `20260713000345` | ev54 `cmpMgDecsn`, exposable | ③ 통지 마감 **D+47 · 2026-07-06** ✓ |
    **New:** 대동기어 also holds an exposable ① (`pifricDecsn` 2026-04-22) that lapsed —
    **D+45, 3,344,138,940원** — so the sample renders **5 rows, not 4**. This is live data, the
    same class as `P5.S3` note 9's 퓨쳐켐 case: R5's card is a mockup of a composition, and the
    build prompt says "실제 corpus 이벤트를 그대로 로드". **`P5.S16`/`P5.S19` will see it; it is
    not a design deviation and must not be filtered out.** A pinned corp that ever stops
    resolving is **omitted** from the composition rather than 500-ing the anonymous entry point,
    and is never substituted with a different filing.
15. **Two boundaries measured, both no-ops today but worth knowing.** (a) A past ① row carries
    its 소멸 only when the 실적보고서 is inside **the same coverage window 조회 counts with**
    (`2026-01-01 … today`) — outside it the row keeps its 기간 지남 chip and states nothing
    (R4-3: unstated, never 0). Measured: **32 of 32** stored `lapse` rows are inside, so the
    filter changes nothing today. (b) A report whose `event_id` is `NULL` gets **no portfolio
    row** — 지나간 마감 is a list of deadlines and such a report has no 매매기간 to have passed;
    the figure still reaches the reader through 조회's breakdown, which is keyed on the issuer.
    Measured: **0** such rows today, but **2 of 32 hang off a *flagged* event** (한솔테크닉스
    `20260722000448`, 트리니티항공 `20260319000351`) and those are skipped by the same
    `state != "exposable"` gate `P5.S4` note 6 describes — a holder of either sees the 놓친 돈 in
    조회 and no 지나간 마감 row. Honest, and the inverse of S4's rule rather than a new one.
16. **Payload sizes / timings** (local Postgres, warm, 4 holdings): `GET /portfolio`
    **18.3 KB in 37 ms**, `GET /portfolio/sample` **18.2 KB in 25 ms**. Nothing is paged and the
    design pages nothing; a portfolio is a handful of issuers. 지나간 마감 grows without bound as
    a reader's holdings age — if that ever matters it is a `P5.S16` decision, not a payload one.

### `P5.S9` — 운영 관제's backend exists; the door, the endpoint map, the port, the run log

The panel's whole backend: a **separate** operator credential, eleven routes of which nine
are `GET`, the pipeline run log R7's 개요 tab requires, and the storage port that lets the
three P6 tabs serve honest zeros. **0 requests, 0 model calls, 0 new dependencies.** The
개요 tiles reproduce `python -m mijual.gates summary` byte for byte and the 정확도 markdown
reproduces `python -m mijual.evalset report` byte for byte — both verified live.

**Import map**

| you need | import |
|---|---|
| the operator gate on a read | `from mijual.web.ops import OpsGate` → `def tab(db: DbSession, _: OpsGate)` |
| "is this an operator", never raising | `ops.has_ops_session(db, request)` |
| the ops cookie's name | `mijual.web.auth.OPS_COOKIE` (`mj_ops`) — reserved by `P5.S7` |
| any ops number | `mijual.web.opsreads` — `gate_summary` · `beat_view` · `run_log` · `lock_state` · `gate_queue` · `gate_rows` · `accuracy` · `spend` · `reader_accounts` |
| the 대화/세션/피드백 source | `mijual.web.conversations.Conversations` (P6 implements; P5 wires `EmptyConversations`) |
| the beat schedule **or** the run-lock key from anywhere | `mijual.beat` — `BEAT_ENTRIES` · `TIMEZONE` · `lock_key()` · `DEFAULT_WINDOW_DAYS` |

**Endpoints** (prefix `/ops`, all behind the operator session):
`POST /ops/login` · `POST /ops/logout` · `GET /ops/session` ·
`GET /ops/overview` · `GET /ops/gates` · `GET /ops/gates/rows` · `GET /ops/accuracy` ·
`GET /ops/conversations` · `GET /ops/sessions` · `GET /ops/feedback` · `GET /ops/users`.
New structural codes: `invalid_credentials` 401 (the door) · `ops_unauthenticated` 401
(expiry → the client returns to the door and restores the tab). **No vocky route exists**
— `P5.S18` decides its shape and a stub with invented field names is what §6.3 forbids.

1. **The door is a credential with no row, and that is the no-join promise.**
   `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` in the environment; **no operator account, no
   admin flag, no signup, no reset**. `ops_session` has **no `account_id`, no FK and no
   operator identifier at all** — a row means "somebody proved they hold the credential",
   which is the whole fact. Cookie **`mj_ops`** (`HttpOnly` · `SameSite=Lax` · `Path=/` ·
   `Secure` from `MIJUAL_COOKIE_SECURE`), **12 hours absolute, never extended on a read** —
   a working day, deliberately not the reader's 30 days, because an operator console should
   not still be open tomorrow morning. Token digests are keyed with the same
   `MIJUAL_SESSION_SECRET`, so one rotation logs out readers *and* operators.
2. **One failure, one cost, and "unset" is one of the causes.** Unknown ID, wrong password
   and *no credential configured* return byte-identical 401 bodies (verified with `==` on
   the raw content). The configured password is hashed once per process and **every** path
   spends exactly one scrypt verification (the miss burns one against a dummy hash, S7's
   shape); the ID goes through `hmac.compare_digest` and **both checks are always
   evaluated** — a short-circuit would leak "the ID exists" in the timing the uniform body
   exists to hide. `P5.S17` renders 「자격증명이 올바르지 않습니다」 from the code; the API
   writes no Korean. **Attempt limiting is recorded, not built** (`security`: server
   concern, no UI copy) — it needs cross-process state, which is **P4**'s, exactly as
   `P5.S7` decided for the reader login.
3. **Two import boundaries were closed by moving, not forking — do not undo either.**
   (a) **`mijual/beat.py`** (new, stdlib-only) now holds `TIMEZONE`, the window constants,
   `BEAT_ENTRIES` and the **run-lock key**. `mijual.scheduler.app` builds `BEAT_SCHEDULE`
   from it, `mijual.scheduler.locks` re-exports `KEY_PREFIX` from it, and the ops panel
   reads it — so there is **one** statement of when the pipeline runs and one spelling of
   `mijual:lock:pipeline`. It had to move because `mijual.scheduler` pulls
   `collect`/`extract`/`dart` through `pipeline.py`, and R7 requires the schedule to be
   rendered *from the configuration* ("설정이 곧 진실"). (b) **`mijual/evalset/sample.py`'s
   two `mijual.extract` imports are now function-local** (they belong to the corpus-*draw*
   half; the *artifact* half — `EvalSample`/`load_sample` — is pure JSON and is what a
   request path reads). Measured after both: `import mijual.web.app` still pulls **none** of
   `dart`/`collect`/`extract`/`estimate`/`scheduler`/`evalset` and no Celery.
4. **The gate-queue denominator is now 691, not 633** — `710` stored rows, **19**
   duplicates (was 649/633/16). It moved because `P5.S6` added 61 `appraisal_price` label
   rows. **Both numbers are served** (`basis.stored_rows` / `basis.distinct_rows` /
   `basis.duplicates` / `basis.key`) and every reason carries `count` (stored) **and**
   `distinct_count` + `rate` (distinct basis), so no percentage's denominator is ever
   implicit. `method_not_enumerated` is the visible duplicate case: 4 stored, 2 distinct.
5. **The run log is opened at the start of a run and closed at the end.** `pipeline_run`:
   label · trigger (`beat` from the beat entries' own kwargs, else `manual`) · started/
   finished · seconds · window · config line · lock kind · ok · requests · calls · cost ·
   **`spend_line` verbatim** · `stages` (each `StageResult.as_dict()`, `detail` included) ·
   notes. Opening it early is why an in-flight or crashed run is visible **and** why the
   lock chip has an honest 시작 시각: the Redis lock value is an owner token with no start
   time, so deriving one from its TTL would be an invented number. **A skipped run writes
   no row** — it did nothing, and the lock chip is where contention shows. A run-log failure
   is swallowed into a run note: a log that can kill a pipeline is worse than no log.
6. **`▷` is stored and served verbatim.** `PipelineResult.spend_line` is now a property so
   `render()` and the stored row cannot drift; a test asserts the row carries `▷` and does
   **not** carry 「추정」. Same rule in `spend()`'s `cost_line`. Everywhere outside the ops
   panel, 「추정」 remains the only estimate mark — the boundary is the source.
7. **S3's deviation is closed: `reparse` + `snapshot` are beat stages now.**
   `STAGES = (collect, bodydoc, extract, gates, reparse, snapshot)`. Both are offline
   (0 requests, 0 calls) so scheduling them costs nothing, and until they ran on the
   schedule the ① extras and the landing headline could age silently while 기준시각 said the
   corpus was fresh. Order is a data dependency: `reparse` rewrites `facts`, `snapshot`
   builds `LapseRow` from them. `tests/test_scheduler.py` was updated deliberately and now
   pins the ordering, not just the membership. Measured on the live corpus: `reparse 69/69,
   **0 with changed facts**`, `snapshot ① inputs 545 / 소멸 rows 32`, and `/board/summary`
   **identical** before → after.
8. **⚠ R7's 사용자 tab asks for a column P5 has no fact for: 샘플 로드 여부.** R5's sample is
   anonymous end to end (`P5.S8` note 13 — there is no anonymous write endpoint, and a
   샘플→계정 이전 is the client making ordinary authenticated `POST /portfolio/holdings`
   calls), so **nothing server-side ever learns that a reader loaded it**. The payload
   therefore carries **no `sample_loaded` key** rather than an invented `false`, and
   `P5.S17` must render it as an honest absent. Building the backing would mean a new
   holding-provenance column plus a client-visible parameter — a change to `P5.S8`'s signed
   contract *and* a new behavioural fact about a reader, against `security`'s minimal
   disclosure. **New Open Question below; `P5.REVIEW`'s call.** The other four columns are
   real: 이메일 · 가입일 · 포트폴리오 종목 **개수** (count only — never contents) · 알림 설정
   with `stored: false` meaning the 7일+1일 default rather than "off" (`P5.S8` note 9).
9. **The conversation port's three rules are P6's to inherit, not to re-decide.**
   `Conversations` offers `conversations()` / `sessions()` / `feedback()`, each returning a
   `Page(rows, total, next_cursor)`; **no method takes an account, email, IP or UA filter**,
   nothing writes, and pagination is an opaque cursor, newest first. P5 wires
   `EmptyConversations` through `create_app(conversations=…)` — the same seam shape as
   `P5.S7`'s mailer, so **P6 changes no route**. The tabs serve `{"count": 0, "rows": []}`:
   honest, because this build genuinely stores no conversations, and **no 「준비 중」 string
   was invented**.
10. **`P5.S17` inherits three rendering obligations the payloads are shaped for.**
    (a) The 「실행 기록 없음」 alert row is the **client's join** of `beat.entries[].due`
    (every instant an entry was due in the last 3 days, computed from the declaration) with
    `runs.rows` — the backend serves both facts and fabricates no row. (b) A blocked gate row
    has **no `quote`/`span` key** (verified live on a `field_absent` row); render 「없음」 as a
    state, never a placeholder. (c) The 정확도 tab gets `evalset.markdown` (the CLI's exact
    output) *and* a structured mirror derived from the same object — quote from either, but
    never a rate without the decomposition sitting beside it (`over_blocked_estimate` now
    lives **inside** the `blocked` bucket for exactly that reason).
11. **Live measurements (2026-08-22, local Postgres + Redis).** 개요 5.8 KB / 67 ms ·
    게이트 대기열 10 KB / 189 ms · 정확도 29 KB / 35 ms · 행 검사 ~5 KB. The expensive one is
    `gate_summary`'s renderable-field count, which walks the 488 exposable events the same
    way `/board` does (batched `current_versions`, one extraction query). Redis pointed at a
    dead port: **200 in 0.13 s** with `lock.state = "unknown"` + the reason, and the rest of
    the tab intact — a broker that is down is a fact the operator wants, not a reason to
    fail the page.
12. **Local dev needs one operator step, and it was deliberately not taken for them.**
    Add `MIJUAL_OPS_ID=…` and `MIJUAL_OPS_PASSWORD=…` to the gitignored repo-root `.env`.
    Nothing was written into that file: choosing a credential in the operator's own
    environment is theirs. Until it is set the door never opens (and says so identically to
    a wrong password). **The deploy-time issuance/rotation stays P4's open question**, and
    so does the concrete route (`/ops` is the local choice, matching R7's own example).

### `P5.S10` — the frontend foundation exists; the layout, the primitives, the client

`frontend/` is a Next.js **16.3.2** app (App Router, Turbopack) on React **19.2.8** +
TypeScript **5.9.3** and **nothing else** — no UI library, no CSS framework, no test
framework, no linter. The design system is `tokens.css`; a framework theme would be a
second source of truth for decisions R1 already made. **0 new Python dependencies, the
Python suite untouched at 113.**

**Where things are, so no slice goes looking:**

| you need | use |
|---|---|
| a trust primitive | `import { DDay, Citation, … } from "@/components"` — the seven R1/R2 primitives |
| to call the API | `import { getBoard, getEvent, … } from "@/lib/api"` — one function per route, paths hard-coded |
| a payload type | `import type { EventView, Figure, … } from "@/lib/types"` |
| a Korean string a primitive renders | `@/lib/copy` — every entry carries its source; **nothing there is invented** |
| "is motion reduced" in JS | `import { useReducedMotion } from "@/lib/motion"` |
| the page shell / column / numeral class | `app/shell.css` — `.content`, `.mono`, `.backdrop` |
| the tokens | `public/foundations/tokens.css`, **vendored verbatim — do not edit** |
| to run it | `cd frontend && npm run dev` (also in `compose.yaml`'s header), with uvicorn up on 8000 |

1. **The CORS/origin question `P5.S1` note 7 left open is answered: there is no cross
   origin.** The browser only ever talks to the Next origin; `next.config.ts` rewrites
   `/api/*` → `MIJUAL_API_ORIGIN` (default `http://localhost:8000`). So the FastAPI service
   still configures **no CORS middleware and grants no preflight** — which is exactly what
   `P5.S7` note 4's CSRF design rests on — and `mj_session` (`SameSite=Lax`, `Path=/`) is
   stored and returned same-origin with no `SameSite=None` and no `Secure`-on-http trap.
   **Do not add CORS to this service.** Verified live: `/api/health` through the proxy
   returned the API's own body byte for byte. The rewrite is the same seam under
   `next start`; P4 repoints it with an env var, not a code change.
2. **The foundations are vendored verbatim and needed no path edit at all.**
   `public/foundations/tokens.css` = the landed R2 `tokens.css`, `public/foundations/fonts.css`
   = the landed R1 `fonts.css`, both diffed byte-identical with only a provenance header
   prepended. They are **served as static files, not bundled**, and the directory mirrors
   the design project's own `foundations/` + `assets/`, so `fonts.css`'s
   `url("../assets/fonts/PretendardVariable.woff2")` resolves correctly **unchanged**.
   Serving also kept the build green through the days the binary was missing (a bundled
   `url()` to a non-existent file fails the build; a served one 404s and `font-display: swap`
   falls through) — the font is in the repo now (note 17) and the file was never touched
   either way. **A change in either file is a design change.**
3. **One apply-time to-do against a landed nit, record untouched.** `fonts.css` puts its
   `@import url(…IBM+Plex+Mono…)` **after** the `@font-face` block, where CSS is invalid and
   every browser drops it — so the mono face the design puts on *every numeral* would never
   load. The same URL is linked from `app/layout.tsx` instead. Do not "fix" the vendored
   file.
4. **Two readings of the record `P5.S19` should check against the actual cards** (which stay
   in the Claude Design project and are unreadable from here). Both went the way three later
   rounds point:
   (a) **The estimate tag renders `추정`, not `「추정」`.** 「」 is the documents' own quoting
   notation — it also wraps 「예정」, 「진행 중」, 「실행 기록 없음」 and whole sentences that
   cannot contain it — and the mark is specified as a *bordered* tag, so the border is the
   enclosure. `[근거]` is the opposite case: written in square brackets every time, and it
   has only a dotted underline, so its brackets **are** rendered. R2's footer sentence
   spells the mark `[추정]` *in prose*; that is locked copy describing the mark and is
   `P5.S11`'s to render verbatim — it does not respell the tag.
   (b) **A past `D+n` is faint, never alert.** R1 only says "D+N stays unfilled", but R3
   ("faint D+, 기한 지남 — never 종료-colored"), R4 ("faint chip 기간 지남 · D+{n}") and R5
   ("지나간 행 … **alert 색 금지**") settle the colour. `DDay` maps `days < 0` to
   `--urgency-far`. This also protects `ui-traps` #5: an open ② is 진행 중, and painting its
   D+46 in the expiring/lost hue would say the opposite.
5. **Sizes reconcile, they do not conflict.** R2's 10px estimate tag *is* R3's `0.56em`
   (0.56 × ~17.9px), and the em form is what honours R1's "the component never sets its own
   size". Implemented as `0.56em`. Same discipline everywhere: the primitives set colour and
   weight, never a size that competes with the surface's.
6. **The reduced-motion convention is fixed here — do not invent a second one.**
   `data-motion="tick"` **freezes** (colon blink, twinkle, orbit); `data-motion="ambient"`
   **hides** (shooting stars); everything else is a fade and a fade becomes a cut. The JS
   half is `useReducedMotion()`, and `P5.S12` needs it: R2 requires "no animation, **static
   value**" for the countdown, which means the interval must not run — CSS cannot stop a
   `setInterval`.
7. **The shell guarantees the cosmos backdrop is possible and builds none of it.** `body`
   carries no `overflow`, `transform`, `filter` or `contain` — any of them would turn
   `position: fixed` into a containing-block position and break the one continuous
   starfield R2 requires. `.backdrop` (fixed, `inset: 0`, `z-index: -1`, no pointer events)
   is the slot `P5.S12` fills.
8. **`CraftPanel` has no ornament-free variant, on purpose.** R7's ops idiom strips exactly
   what this component adds (glow, brackets, translucency), so it is a *different* panel and
   `P5.S17` builds it — not a mode of this one. `tone="alert"` exists for 소멸주의보 and R3's
   기재 불일치 header, and that is the only variant.
9. **`EstimateMarker` refuses an untagged estimate the way `present.Figure` does.**
   `estimated` is a required prop with no default plus a runtime guard, mirroring
   `Figure.estimated` having no default on the server. `P5.S11`–`P5.S17`: pass
   `figure.estimated` straight through — never a literal, and never omit it.
10. **`Citation` handles exactly `P5.S20`'s three states and no fourth.** One `quote` →
    one panel; `parts` → **every addend rendered verbatim and separately** (never joined —
    the sum is printed in the filing nowhere, so a joined quote would fabricate a sentence);
    neither → **no chip at all**, and the `rcept_no` link belongs to the row, not to this
    primitive. It also accepts a `span` it deliberately does not render: offsets are
    internal, like reason codes.
11. **`lib/copy.ts` is the only place a Korean string enters the frontend, and every entry
    cites its source** (`exposure.py`'s `TBD_DISPLAY_KO` / `WITHDRAWN_NOTICE_KO`,
    `present.money.MISMATCH_LABEL_KO`, R1/R2/R3's build prompts, `copy-inventory.md`).
    Surface copy — the hero, the footer, the ② strip, R4's 검색 불일치 line — belongs to the
    slice that renders it, transcribed the same way. **A string with no citation does not
    belong in the frontend.**
12. **The typed client's shape rules, so a surface does not re-derive them.** Optional
    (`?:`) means the key can be **absent**; `| null` appears only where the server genuinely
    emits null (`countdown.date`/`dday`/`days`, `corp_name`, `rcept_no`, `freshness.as_of`,
    a version row's `rcept_dt`/`correction_kind`). Money and ratios are typed `string` and
    must never be `Number()`-parsed — 배정비율 keeps ten decimals and a ₩ total runs past
    10^10. Compose the N주 math from the served factors with **one** implementation shared by
    조회 and 포트폴리오 (`P5.S8` note 1); `⌊N × 배정비율⌋ × 증서 1주 이론가치` appears in no
    payload, by design.
13. **Server components get the client too**, and it bypasses the proxy: with no `window` it
    calls `MIJUAL_API_ORIGIN` directly. A gated read from a server component must forward the
    incoming `cookie` header itself — `credentials` is a browser concept and does nothing in
    Node. `P5.S16` will meet this first.
14. **The smoke check is two halves and stays that way.** `next build` prerenders
    `app/page.tsx` through the shell and every primitive, so a broken component fails the
    build; `node --test lib/*.test.ts` (3 cases, no framework, no fixtures) covers what a
    render cannot show — the CSRF header on a mutation and not on a read, `credentials:
    include`, and the envelope becoming an `ApiError`. Adding jest/vitest/jsdom here would be
    the fixture sprawl the repo rule forbids.
15. **`app/page.tsx` is `P5.S12`'s to replace.** It is the foundation proof, not a landing
    draft: every string on it is verbatim from the landed record (the quote + span from
    `grounding/samples/r1-live-healthy.json`, the figure from `headline-numbers.md`, the body
    from that file's 발표용 문장 4) and the numbers are the pack's **dated 2026-08-20**
    samples, not live data.
16. **Two housekeeping facts.** TypeScript is pinned to **5.9.3**, not npm's `latest` 7.0.2
    (which is the Go rewrite — a foundation nine slices inherit is the wrong place to be
    first); revisit at P4. And `next dev` writes **`frontend/AGENTS.md` + `frontend/CLAUDE.md`**
    itself (`node_modules/next/dist/server/lib/generate-agent-files.js`) warning that Next 16
    differs from training data and pointing at the docs bundled under
    `node_modules/next/dist/docs/` — deleting them only re-creates the change on the next
    `next dev`. **Read those bundled docs before writing Next code in S11–S17.**
17. **The binary design assets landed — the operator exported all five on 2026-08-22, and
    `P5.S11` is unblocked.** Copied in byte-for-byte (sha256 in
    `frontend/public/assets/README.md`; not re-encoded, resized, optimised or stripped),
    because they are the design project's own output and a diff here would be a design
    change — replacing one means a **new export**, never a local edit:

    | path | format |
    |---|---|
    | `frontend/public/assets/fonts/PretendardVariable.woff2` | WOFF2/TrueType, variable `wght 45–920`, 2,057,688 b |
    | `frontend/public/assets/mijual-wordmark-charcoal.png` | PNG 1788×324 RGBA, 42,403 b |
    | `frontend/public/assets/mijual-wordmark-white.png` | PNG 1788×324 RGBA, 37,242 b |
    | `frontend/public/assets/mijual-logo-ring-charcoal.png` | PNG 2178×346 RGBA, 76,558 b |
    | `frontend/public/assets/mijual-logo-ring-white.png` | PNG 2178×346 RGBA, 64,605 b |

    **The white wordmark's filename is `mijual-wordmark-white.png`** — the record described
    a reversed white version without naming its file, and this is the answer `P5.S11` wires;
    the white pair is what the cosmos-dark chrome uses, the charcoal pair is for light
    surfaces, and neither substitutes for the other. Nothing was substituted, generated or
    placeheld at any point. `fonts.css` needed **no edit**: its landed
    `url("../assets/fonts/PretendardVariable.woff2")` resolves as
    `/assets/fonts/PretendardVariable.woff2`, exactly as vendored. There is still **no SVG
    wordmark** and no favicon-scale mark beyond the ring logo.
18. **Pretendard is verified loading in a real browser, not just 200-ing** (headless Chrome
    over CDP, 2026-08-22): the face reports `status: "loaded"`,
    `document.fonts.check('400 16px "Pretendard Variable"')` is `true`, and
    `CSS.getPlatformFontsForNode` shows Blink drawing Korean prose with **Pretendard
    Variable** (`RightsChip` 유상증자 신주인수권 ×10 glyphs, the `Citation` quote ×48) instead
    of the `-apple-system` fallback. All five asset URLs return **200** with the exact byte
    counts, and the served `woff2` body is sha256-identical to the file on disk.
19. **⚠ Korean inside a `--font-mono` element does not reach Pretendard — a `P5.S19` check,
    not a bug to fix here.** Now that the real face is loaded this is visible: the token
    stack `--font-mono` is `"IBM Plex Mono","SF Mono",Consolas,monospace`, which has no
    Hangul, so the Korean glyphs in the three primitives that use it — `StateBadge` 추후결정,
    the `LapseAlert` 소멸주의보 badge, the `Citation` `[근거]` chip (brackets in Plex Mono,
    근거 not) — are drawn by the **OS** Korean face (macOS: Apple SD Gothic Neo), i.e. a
    different face per platform. Latin numerals are unaffected and Korean *prose* is
    correct. Both the token file and those components are as landed/approved, so this is a
    fidelity question for `P5.S19` against the real cards — **do not restyle a primitive or
    edit the vendored `tokens.css` to "fix" it**.

### `P5.S11` — the chrome exists; the route map, the two seams, the fidelity to-dos

`frontend/components/chrome/` is the R2 chrome, wrapped around every route by the root
layout. **0 new dependencies, no primitive or token touched, no Python file edited** (suite
still 113), and **no Korean invented** — every chrome string is transcribed with a citation
in `components/chrome/copy.ts`, the same convention `lib/copy.ts` uses for the primitives.

| you need | use |
|---|---|
| the chrome around a page | nothing — `app/layout.tsx` already wraps every route in `SiteChrome` |
| a route path | `import { ROUTES, isActiveRoute } from "@/lib/routes"` — **one module, one statement per path** |
| a chrome string | `components/chrome/copy.ts` (surface copy still belongs to the surface's own slice) |
| the 로그인 slot | `components/chrome/AccountSlot.tsx` — **`P5.S16`'s one swap point** |
| vocky's script URL | `NEXT_PUBLIC_VOCKY_SRC` (`components/chrome/VockyScript.tsx`) |

**The route map, decided here and inherited by S12–S17:** `/` 관제 현황판 (`P5.S12`) ·
`/stocks` 내 종목 조회 (`P5.S14`, the API's own noun so page path and contract path are one
vocabulary) · `/ask` **AI 질문 (P6's surface**, and deliberately not `/explain` — 해설 is the
label R6 retired) · `/auth/login` 로그인 (`P5.S15`; `mijual.web.auth.RESET_PATH` already fixes
`/auth/reset`, so the auth surfaces live under `/auth/`) · `/ops` 운영 관제 (`P5.S17`). Active
state is `isActiveRoute`: `/` exact, everything else prefix-with-boundary, so
`/stocks/00162461` keeps 내 종목 조회 underlined. **`/stocks` and `/ask` ship as bare shells**
— chrome only, no copy, no placeholder — and their owners replace the files.

1. **The superseded labels are what render, and the check is in the HTML.** 내 종목 조회 ·
   관제 현황판 · **AI 질문** in the bar (R4/R6 via the supersession table, and R6's own "nav
   finalized" line), and **AI 질문** in the footer's bottom row where R2 landed 해설
   (`P5.DECOMP` note 7). Verified against the served HTML: **해설 and `▷` appear nowhere**,
   and no 내 종목 연결 nav link exists.
2. **The gate-cost sentence keeps its words and loses its `▷`** — `▷ 49.2억원은 …` becomes
   49.2억원 + the 「추정」 tag + `은 할인율 인용이 게이트를 통과하지 못해 총액에서
   제외했습니다`, byte-identical otherwise (its missing full stop included). ⚠ **The figure
   is a dated-pack number, not a served one:** `grep` confirms the presentation contract has
   no gate-cost figure anywhere (`/board/summary` serves the 718.1억/548.7억 pair and no
   upper bound), and computing 49.2억 needs the corpus-median 할인율 from
   `mijual.estimate`'s report — a module a request path may not import (S2 note 7). So the
   footer states a 2026-08-20 figure on every page while the landing beside it states live
   ones. Making it live is **backing work** (a persisted precomputation like `offering_input`,
   plus a summary key), not a rendering fix: **`P5.REVIEW`'s call** whether that is a fix
   slice or a deferred job.
3. **The positioning line is locked copy and is transcribed verbatim — including 내 종목
   연결.** R2's handoff §3 lists "the positioning sentence" among the *locked* items and §1
   states it ("시장 전체의 소멸 임박 권리를 감시하는 관제 서비스 + 내 종목 연결"; also R1's
   handoff and the operator's own `docs/reference/challenge/00_HANDOFF.md`). R4's supersession
   is scoped to the **nav label**, and rewriting a locked sentence would be a design change,
   so the footer says 연결 while the nav says 조회. **Flagged for `P5.S19`/`P5.REVIEW`** — if
   the operator wants the sentence re-cut, that is a signed-copy change, not an edit.
4. **`© 미주알`** — R2's bottom row is written "© · 자료: …" and the card stays in the design
   project. The symbol is R2's, 미주알 is the product's own name (it is in the disclaimer on
   the same surface), **no year is invented**. `P5.S19` checks it against the card.
5. **The wordmark is `mijual-logo-ring-white.png` at h 19 (nav) / h 17 (footer), rendered by
   a plain `<img>`.** The ring file (2178×346) is the mark *with* its orbital ring, which is
   what R2 asks for; the wordmark pair (1788×324) has none and does not substitute. **`next/image`
   is not used and must not be**: it serves a re-compressed derivative, and a delivered asset
   is never re-encoded. Intrinsic dimensions travel as attributes so the 52px bar reserves the
   right box before the PNG arrives. Verified in a browser: `complete: true`, natural
   2178×346, rendered 119.59 × 19.
6. **vocky: one script, three triggers, and the URL is configuration.** R2 wants the script
   loaded "once, deferred, in the shell"; `next/script` in the root layout is exactly Next's
   documented once-per-app mechanism. The URL is in **no** record, so it is
   `NEXT_PUBLIC_VOCKY_SRC` — **unset ⇒ no script tag at all, triggers still render** (both
   directions measured; with it set there is exactly one tag, still one after a client-side
   navigation). `NEXT_PUBLIC_*` is inlined at **build** time, so setting it means rebuilding.
   `P5.S18`/P4 own the real value.
7. **The mobile sheet stays in the DOM, hidden with `display: none`.** An external script that
   binds `[data-vocky-trigger]` at load would never see a trigger React mounts later, so all
   three exist from the first paint; `display: none` keeps the closed sheet out of the tab
   order and the a11y tree, and the desktop bar never shows it. Its open rule is
   `.sheet.sheetOpen` — **specificity, not source order**, so a bundler moving a block cannot
   flip it.
8. **The bottom-right corner is clear and nothing in the chrome is `position: fixed`**
   (measured: zero fixed elements). R2 §6-4 forbids a floating button and R6's launcher lands
   in that corner — `P5.S12` should keep it that way too.
9. **⚠ Fidelity to-do for `P5.S19`: the 「추정」 tag in the footer renders at 6.72px.** The
   primitive is `0.56em` of its context (R3's system-wide re-cut, and R1's "the component
   never sets its own size"), and the footer sentence is 12px — while **R2's own landing spec
   writes the tag as 10px**. The two readings agree at ~17.9px context and diverge here. This
   slice did **not** touch the primitive (the plan forbids it) and did not resize the signed
   sentence. If the cards show a legible tag, the sanctioned fix is a **named prop on
   `EstimateMarker` with its citation** (`components/index.ts`'s own rule), never a local
   restyle. Worth deciding, because an estimate mark nobody can read is close to an untagged
   estimate.
10. **Two more `P5.S19` items in the same class.** (a) The positioning line and the bottom row
    are Korean **in mono** because R2 says mono 11 — so they hit S10 note 19's mono/Hangul
    gap and are drawn by the OS Korean face. (b) The 메뉴 button carries the chrome's own
    hairline (`rgba(255,255,255,.3)`, the value R2 gives the `[의견]` trigger); R2 specifies
    only "메뉴 button, mono, 44px hit", so its border is this build's reading of "button".
11. **R5-4's 샘플 포트폴리오 entry is *not* in this footer, on purpose.** R5 says "진입:
    로그인 페이지 하단 + **랜딩 푸터**" while its chrome section says "Footer 불변" and the
    signoff records the round as extending only the account slot. Read together, the sample
    entry is a **landing/sample** element, not global chrome: `P5.S15`/`P5.S16` (with
    `P5.S12` if it lands on the landing page) own it. Do not silently drop it — it is signed.
12. **Gotcha, and it cost this slice an hour: run browser checks against
    `http://localhost:3000`, never `http://127.0.0.1:3000`.** Next 16's dev-origin protection
    answers **403** for two `/_next/static/chunks/*.js` files when the browser's host is not
    the dev server's own (`curl` gets 200 for the same URLs, which makes it look fine), so
    **hydration never completes** and every interactive check quietly measures the
    un-hydrated page — a click changes nothing, and an `<a>` still navigates, so even a
    "client-side navigation worked" reading is misleading. The dev log says so explicitly
    (`allowedDevOrigins`). Everything in note 7 and the sheet's behaviour was re-verified
    over `localhost` **and** against `npm run build && npm run start`.

### `P5.S12` — the landing is live; the readings it had to make, and what S13/S14 reuse

`frontend/components/landing/` is the R2/R2.1 landing over live `/board/summary` + `/board`.
S10's foundation proof and its dated 2026-08-20 numbers are gone. **0 new dependencies, no
primitive/token/chrome file touched, Python suite untouched at 113, no Korean invented**
(every string cited in `components/landing/copy.ts`). The production build's browser console is
**empty** — no hydration warning, which is what the deterministic starfield exists for.

| you need | use |
|---|---|
| a won/count/ratio rendered | `@/lib/format` — `won` (mirrors `mijual.estimate.won`: 조원 2dp / 억원 1dp / 원 0dp, half-even) · `count` · `percent` (the pipeline's `:.1%`) · `kstStamp` |
| R2's board row anatomy | `components/landing/BoardRow` — shared by the board and both expanded strips |
| the 「추정」 tag at R2's landing size over a value of any size | `components/landing/EstimateValue` |
| a link to a detail page | `eventPath(rceptNo)` from `@/lib/routes` (the page itself is `P5.S13`'s) |

1. **The hero H1 renders 내 종목 조회, not R2's literal 내 종목 연결.** R2 says "This IS the
   내 종목 연결 surface … submit goes to R4's 조회", and R4 *named that surface* ("the surface
   name **내 종목 조회**", signoff + build prompt §Route, plus the supersession table). It is a
   name for a destination, not locked prose, and R2's literal would print two names for one
   surface on a page whose nav one line above says 내 종목 조회. The retired wording survives
   only in the footer's **locked positioning sentence** (`P5.S11` note 3), which is a different
   class of copy. **`P5.S19`/`P5.REVIEW` check both against the cards.**
2. **The ① extras date is the 청약 window's 마감** (`subscription_end`) — the decision `P5.S3`
   note 10 left open. Every other 청약 date the product prints is the closing one (발표용 문장
   4, the report's 청약종료 column, `next_lapse.date`), and the 소멸주의보 strip on the same
   page prints 2026-09-04 for the same offerings; two different 청약 dates for 계양전기 on one
   page would be the page contradicting itself. **`P5.S14` should print the same end.**
3. **The board row's corp name links to `/events/{rcept_no}`; the `↗` still goes to DART.** R2
   gives the row only the DART link, but R3's detail page opens with "← 관제 현황판" and its
   추후결정 strip says "expanded rows link to detail" — the board is the way in. Only an href
   was added. **The link 404s until `P5.S13` lands**, deliberately, like `/auth/login`.
4. **The hero needed a `min-height: 680px` (desktop) for the rings to clear.** R2.1's rule is
   an outcome — "never shrink them — give the hero vertical room instead, so rings clear the
   nav line and the panels below" — and 110/160px padding alone does not produce it: rotated
   −14° the outer ring occupies ≈640px against a 508px hero. Padding unchanged, content centred
   in the taller box; measured ring box **72 → 712** with the nav ending at 52 and the first
   panel starting at 732. Consequence for the review: the anchor panels now begin ~730px down,
   so base-R2 decision 1's "live layer above the fold" is tighter than it was (R2.1 governs the
   base record where they conflict, and the ring rule is what the build prompt states).
5. **The landing's 「추정」 tag renders 9.52px, from a 17px marker context** (`EstimateValue`).
   R2 asks for a 10px tag on landing surfaces; the primitive is `0.56em` of context and may not
   set its own size, so the **surface** supplies the context and the value keeps its own (46px
   on the value card, the line's size elsewhere). The primitive is untouched, so `P5.S11`'s
   6.72px footer tag stands as it was — the two readings are `P5.S19`'s to settle together.
6. **A strip states the count that is in view**, mirroring `/board`'s own `count` vs `total`: on
   전체/CB the ② strip reads 57건 = `open_now.count`; on 유증/매수청구 it has no rows and does
   not render at all (0건 would be a sentence about nothing). 펼치기 keeps its label while open
   and carries state in `aria-expanded` — a 접기 label is copy nobody signed (the chrome's 메뉴
   precedent).
7. **Tabs filter the served list in the browser.** `?rights=` exists, but the whole board is one
   160 KB request and `counts` is whole-board either way, so a tab costs no request and two tabs
   cannot show two corpora. 전체 reads **488** while **450** rows are on the page — the 38 past
   ①/③ are not on the landing by design; that is not a missing-rows bug.
8. **Stars are generated once, deterministically** (`mulberry32`, fixed seed, module scope): a
   `Math.random()` field is a hydration mismatch on every load. The mobile field is the first
   160 of the same 240 (`:nth-child(n+161)` hides the tail ≤480px). The glow/ring alphas are this
   build's reading — the record states geometry and counts, the *hue* is the `--live` token's.
9. **Reduced motion is fully wired and measured**: countdown identical after 3 s (the interval
   never runs — CSS cannot stop a `setInterval`), colon/twinkle/drift/orbit `animation: none`,
   shooting-star layer `display: none`. The per-star twinkle needed a rule in the module's own
   `prefers-reduced-motion` block, because the shell's `data-motion="tick"` rule reaches an
   element and its pseudo-elements, not 240 children.
10. **Live cross-check (2026-08-22, headless Chrome, dev *and* `npm run start`).** Hero stat line
    = `/board/summary` exactly (718.1억원「추정」 · 488 · 33); both anchor cards agree (488 · 33 ·
    15 · 69 · 548.7억원 · 365,527,824주 · 14.0%); the countdown's own diff against
    `next_lapse.target` is **0 s off**; tabs = `counts` (488/50/422/16) and filter to 365/14/389;
    ② strip 57건 = `open_now.count` with 삼성제약 **D+1** faint (never 종료); 추후결정 4건 with
    `StateBadge 추후결정` and **no date anywhere**; freshness `기준 2026-08-22 04:14 KST`; with
    `MIJUAL_STALE_AFTER_HOURS=1` the chip flips to alert + `· 7시간 전 데이터`, the inset notice
    appears **and the rows render identically** (content never dims); **no `원` amount anywhere on
    the page** — a ① before 확정발행가 shows the `발행가 확정 전` chip and no money; 390×844 gives
    H1 34px, 48px controls, 160 stars / 3 shooters, compact tabs, two-line rows, no horizontal
    overflow; exactly **one** `position: fixed` element (the backdrop), so P6's corner stays clear.
11. **D2's trigger has NOT fired on the board** (DECOMP note 2). Across all 450 rendered rows
    **no two share an `rcept_no`**. 코이즈 `20260122000058` sits on two exposable ① events
    (1195/1264) and **neither is on the landing** (past ①). 사토시홀딩스 `20251219000402` sits on
    events 941 (`reattached`) and 942 (`duplicate`) and **both are on the landing**, but they are
    different bonds by their own originals — 941: `20250623000222`, 개시 2026-07-21, in the ②
    strip at D+32; 942: `20251215000366`, 개시 2026-12-23, ranked at D-123 — so the shared 정정 is
    an internal pairing artifact, not a duplicated row. The pair that *looks* duplicated is
    **제이스코홀딩스 479/480** (same corp/type/date 2027-07-22) and it is two different filings
    (`20260714000457` / `20260714000466`) — two CB tranches filed the same day, two truthful rows.
    Nothing was de-duplicated. **`P5.S14`/`P5.S19` still carry the other half of the check** (a
    per-stock 놓친 돈 total that double-counts one offering).
12. **Two `P5.S19` fidelity items in `P5.S11` note 10's class.** (a) R2 asks for a **mono stat
    line** and a **mono 13.5 band line**, so Korean prose on them is drawn by the OS Korean face
    (S10 note 19) — as specified, not a defect to restyle. (b) On a 390px viewport an ① row's
    second line wraps once more (label + date, then `· 청약 … 발행가 확정 전`), because the
    content does not fit one line and truncating data is not an option.

### `P5.S13` — the event detail page is live; the conventions S14/S19 inherit, and eight readings

`frontend/components/event/` + `app/events/[rcept_no]/page.tsx` is R3 over live
`/events/{rcept_no}` (+ `/corrections`), all three rights types and every state the round draws.
**0 new dependencies, no primitive/token/chrome/landing file touched, Python suite untouched at
113, no Korean invented** (every string cited in `components/event/copy.ts`). Verified in real
headless Chrome over `npm run start` on **13 real pages × 2 viewports + 2 404s**.

| you need | use |
|---|---|
| the whole surface | `components/event` → `EventDetail` (the only export; the page is a thin route) |
| a link to 조회 for a stock | **`stockPath(corpCode)`** from `@/lib/routes` — `/stocks/{corp_code}` |
| one field rendered the way this surface renders it | `FieldValue({fieldKey, value, reference, moved})` from `components/event/Fields` (the CorrectionStory's diff columns already reuse it) |
| a Korean string this surface owns | `components/event/copy.ts` — one citation per entry, no exceptions |

1. **The 환산 CTA links to `/stocks/{corp_code}` — a path, not a query param.** The plan asked for
   a "query-param convention"; `P5.S4` had already made the **corp_code path segment** 조회's
   stable handle (`isActiveRoute` knows `/stocks/00162461`), and `?q=` is the *search* box the
   landing hero posts to — a `corp_code` is not a search term. `lib/routes.ts` now states it once
   as `stockPath()`. **`P5.S14` must serve that path**, and it is the only thing this page
   promises about 조회 (the N주 multiplication stays R4's single site, `P5.S8` note 1).
2. **매수예정가 renders as an ordinary field row under `// 발행 조건`** — served `korean_name`
   (매수예정가격), value, its own `Citation` — not as a highlighted figure. `P5.S6` put
   `appraisal_price` in the contract and thereby superseded R3's "not rendered" line; what R3
   signed is the *row anatomy*, so using it invents no layout. Verified on 세기상사
   `20260713000345` (**5,649원**, quote `매수예정가격 5,649`) and absent — no row — on
   미래에셋비전스팩7호 `20260512000669`. **`P5.S19` should confirm this reading against the cards.**
3. **The 정정 이력 label is still the phase's open question, and this surface is now its second
   site.** R3's literal `정정 이력` is what renders (button, `aria-expanded`, no 접기 label — the
   chrome's 메뉴 precedent). The question is unchanged, not resolved.
4. **A not-found `rcept_no` renders the framework's own 404 inside the chrome.** `P5.S3` note 5
   makes a non-renderable event a 404 that never explains itself, and the copy inventory holds
   **no Korean 404 sentence** — writing one is a design change, so none was written. The chrome
   around it is correct; only the sentence is English. **`P5.S19`/the operator decide** whether a
   Korean not-found line gets signed. Same shape for both `99999999999999` and the flagged
   `20260709000212`.
5. **The CorrectionStory is an in-place disclosure, not a route** — a route needs its own way
   back, and the product's only crumb ("← 관제 현황판") points at the board, not the event. It
   fetches `/corrections` on first open, so a card never pays for a rail nobody opened. Two rail
   readings: the **superseded-row grey annotation renders nothing** (the reader payload carries no
   gate reason at all — that is operator truth, D-14 — and R3 says "may carry"), and the
   **earliest row shows no `correction_kind`**, because that value is the English token `original`
   for a first filing and Korean (기재정정 · 첨부정정) for every other. An event with no readable
   본문 marks **no** row 현재 읽는 버전 — verified on HLB테라퓨틱스 `20260807000003`, whose three
   rows carry no current badge at all.
6. **The layout gotcha this surface cost a rebuild over: a collapsed `Citation` still occupies
   its quote's width.** The panel is a child of the same element, so `max-content` on a flex/grid
   line includes a 300-character 산식 quote. Consequences now baked into `Event.module.css`: a
   field row gives the citation **its own grid area** (desktop `"label value" / "label cite"` with
   a 220px label column; mobile `"label" / "cite" / "value"` with the chip lifted onto the label
   line by `margin-top: -1.45em`), and `.chainStep` carries `max-width: 340px; min-width: 0`.
   Without those, one row renders one character per line. The chain's arrows are **real flex
   items** (`.chainArrow`), not `::before` pseudo-elements — an absolutely positioned arrow lands
   outside the container the moment the chain wraps at 390px.
7. **Section eyebrows are the record's two, and `correction_interpretation` is never a row.**
   Only `// 일정` and `// 발행 조건` appear; the interpretation is the 정정 strip's own content, so
   rendering it as a field would print the same sentence twice.
8. **No 질문 스트립 on this page** (DECOMP note 8): R6's preset-chip strip on detail is **P6's**.
   Its absence is a phase boundary, not a dropped element — do not "restore" it in review.
9. **D4 holds on a real page.** 한화솔루션 `20260720000067`'s 청약 chip opens **both addends**
   (`38,427,609` + `2,888` = 38,430,497) against `20260730000366`. The 발행사 기재 불일치 block
   deliberately does *not* use `parts` for its derived reading: parts are addends that sum to the
   value, and 발행 − 청약 is a difference, so the two inputs render as their own cited counts.
10. **D2's trigger has not fired here either.** No page showed two rows for one bond; 알파AI
    `20250918000398` — one of `P5.S5`'s three repaired ② events — serves **its own** bond end to
    end (전환가액 2,000원 / 권면총액 55.0억원 / 만기 2028-09-22), so the identity-scoped pairing
    holds through the presentation layer.
11. **Live cross-check (2026-08-22, headless Chrome, `npm run start`).** Across 26 renders: no
    `▷`, no `[object Object]`, no `undefined`/`NaN`/`null`, **no stray English token**, **zero
    `position: fixed`** elements (P6's corner stays clear), **zero horizontal overflow at 390px**,
    and every named mobile target exactly 44px (crumb 79×44 · DART **308×44 full-width** · 환산
    149×44 · 정정 이력 71×44). A sparse ② (트리니티항공 `20250808000003`) shows the fact strip plus
    the locked closing line and **no placeholder**; a past-opening ② reads **진행 중**, never 종료;
    an unpriced ① (계양전기 `20260724000546`) shows **no 원 amount anywhere** while 할인율/배정비율
    still render; 추후결정 (경남제약 `20260623000409`) shows the badge with **no date near it**; the
    철회 page (썸에이지 `20260805000454`) renders **0 field rows and no countdown**; 대한광통신
    `20260223002079` shows both readings unreconciled (2,117,937주 vs 2,083,302주) with the locked
    footer. Dev console clean — no hydration warning.
12. **One `P5.S19` fidelity item.** On desktop the 할인율 link of the 환산 chain sits in a 340px
    box because of note 6's citation-panel width, so the gap before the next arrow is wider than
    the round's even spacing. Data is never truncated to close it; the cards decide whether the
    chain should instead cap the quote panel's width.

### `P5.S14` — 내 종목 조회 is live; the shared math seam, the session key, and two gaps

`frontend/components/lookup/` + `app/stocks/` is R4 over live `/stocks?q=…` and
`/stocks/{corp_code}`. **0 new dependencies, no primitive/token/chrome/landing/event file
touched, Python suite untouched at 113, no Korean invented** (every string cited in
`components/lookup/copy.ts` or re-exported from the surface that owns it). Verified in real
headless Chrome over `npm run start` — **43 checks, all pass**, 15 navigations across 9 issuers
× 2 viewports — plus a `next dev` second opinion.

| you need | use |
|---|---|
| **⌊N × 배정비율⌋ × 증서 1주 이론가치** | **`@/lib/holding`** → `convert(factors, shares)` — the product's **one** multiplication site (`P5.S8` note 1). `P5.S16` imports it; it does not write a second one |
| the pieces, if a surface needs them alone | `allottedShares` · `excessLimit` · `sharesValue` · `sumValues` · `parseShares` · `MAX_SHARES` |
| 조회's remembered holdings (R5-3's 세션 이월) | `holding.SESSION_KEY` (`mijual.lookup.holdings`) · `readSessionHoldings()` · `writeSessionHolding()` |
| a link to one issuer's 조회 page | `stockPath(corpCode)` from `@/lib/routes` — **now served** |
| the 놓친 돈 row's served shape | `LapseBreakdownRow` in `@/lib/types` |

1. **Two routes, and the search redirects onto the handle.** `/stocks` is the search
   (`?q=` resolves server-side; the param is **`q`**, the name `P5.S12`'s hero form and the API
   already use) and `/stocks/{corp_code}` is a resolved stock. A hit `redirect()`s onto the
   corp_code path, so the page a reader bookmarks is the stable handle `P5.S13`'s 환산 CTA links,
   and the two entry points reach byte-identical pages instead of two routes that must be kept
   saying the same thing. A **miss stays on the search page** and renders R4's locked 검색 불일치
   line with the query still in the box — `found: false` is a result, not an error.
2. **The math seam is `lib/holding.ts`, and its two rules are structural.** Arithmetic is
   `BigInt` over the digits with the scale tracked separately — **no `Number()` on money or a
   ratio, ever** — so 배정비율's ten decimals survive and the flooring is the multiplication's own
   step (`mijual.calc.allotted_shares` governs, as R4's signoff verified). And `convert()` returns
   **`value: null`** when the factors carry no `unit_value`: money before 확정발행가 is
   *unconstructable* rather than merely unrendered, mirroring `mijual.present`. `OfferingInputs`
   and `LapseResult` both satisfy `ConversionFactors` structurally, which is why one function
   serves the live ① rows, the 놓친 돈 rows **and** 내 포트폴리오's.
3. **sessionStorage convention, for `P5.S16`:** one key `mijual.lookup.holdings`, one object
   `{"v":1,"entries":{"<corp_code>":<shares>},"last":{"corp_code","shares"}}`. Per-issuer, so
   R5-3's 세션 이월 제안 reads the whole session in one go. Behaviour: a stock you already typed
   into restores **its own** count; a **different** stock is never filled in and gets the offer
   chip `이전 입력 {n}주` instead (R4-6's "never auto-fill silently"). Nothing is sent anywhere —
   the API accepts no holding count on any path and there is no anonymous write endpoint.
4. **No holding ⇒ no derived number.** An empty field is not a zero: an ① row states its factors
   (배정비율, and the price or the `발행가 확정 전` chip) and the 놓친 돈 headline — frame line +
   total — appears only once a count exists. `0원` under "청약도 매도도 하지 않았다면" would be a
   claim about a holding the reader never described. The per-offering 소멸 계산 (market-wide) does
   not depend on a holding and always renders.
5. **Three readings of the record, recorded for `P5.S19`.** (a) The coverage caption's start is
   **served** (`lapse.coverage.start`) while `오늘` is R4's own word — `coverage.end` *is* today
   KST. (b) The boundary panel renders **rights-type chips**, not the record's ①②, because R1's
   revision removed the numbering from the UI (the same reading `components/event/copy.ts` made for
   ③'s 1단계/2단계); both dates come off the wire, so it prints `2025-06-01부터` where the record
   writes "2025-06부터". (c) The calc footer is **per row** — offerings of one stock do not share a
   배정비율, so one footer for several rows would print one row's factor as if it covered the others.
6. **②'s 전환가액 stays, and that is not a violation of "②/③ rows never carry a won amount".**
   R4 §② names 오버행 % · 전환 시 주식수 · 전환가액 as the dilution context in the same document
   whose hard rules forbid won amounts on ②/③ rows; the rule is about the **per-holding**
   conversion, and R5 later calls this very strip ②'s substitute for it ("금액 = R4 계약 그대로",
   `P5.S8` note 6). Exactly those three of R3's six render — "Both link out to detail for
   everything else" — and ③ carries the 2단계 dependency line with **no 매수예정가** (it is not in
   `STOCK_FIELDS`, by `P5.S8` note 6's boundary).
7. **D4 is not re-triggered here.** R4 gives a breakdown row **one** `Citation` — the 매매기간
   quote — and the 소멸 계산 cell prints 발행/청약 as *words* with only the 소멸 count as a number.
   No summed 실적보고서 figure carries a chip on this surface. The 발행사 기재 불일치 block does
   ride along (`ui-traps` #2 is a payload rule, `P5.S4` note 9), rendered in R3's own signed words.
8. **⚠ D2's second check: the trigger has NOT fired.** 코이즈 has two exposable ① events
   (1195 · 1264) sharing version `20260122000058`, but only ev1195 carries a 증권발행실적보고서
   (`20260129000503`). The breakdown is keyed on the **실적보고서**, which is unique, so the page
   renders **one** offering row and `totals.offerings: 1` (1,000주 → 944,495원). Nothing was
   de-duplicated. `P5.S19` still holds the board half.
9. **⚠ `P5.S4` note 8's gap is now visible on a page, and it is a design question.** An ① whose
   청약 has closed but whose 실적보고서 has not been filed is in **neither** section, so its stock
   renders the *no-event* empty state ("이 종목에는 진행 중이거나 2026년에 소멸된 권리가 없습니다").
   Live today: **센서뷰 `01593668`** and **클로봇 `01784914`**, each with a 확정발행가-priced ①
   whose 청약 closed **2026-08-14**. Nothing was invented for them — `pending` would render the
   wrong copy (their 청약 is over) and a 놓친 돈 row would be a figure nobody filed. **`P5.S19`/the
   operator decide** whether a state gets signed for it.
10. **Two facts about the environment, neither this surface's.** (a) Next prefetches the chrome's
    로그인 link, so **every** page in this build logs a `/auth/login` 404 until `P5.S15` lands —
    measured identically on `/` and on an event detail page. (b) The shared `Citation` primitive's
    `[근거]` chip (14px) and its panel's DART link (17px) sit under the mobile 44px floor, exactly
    as on R3's detail page; the primitive was **not** touched (a variation belongs in it with a
    named prop and a citation, never as a local restyle). Both are `P5.S19` items.
11. **Live cross-check (2026-08-22, headless Chrome, `npm run start`).** 계양전기 by name **and**
    by `012200` → `/stocks/00102618`; unpriced ① → `발행가 확정 전` + 배정 신주 **115주** +
    **+23주** + `= 500주 × 0.2314082845 · 1주 미만 버림` and **no 원 in the page body**;
    한화솔루션 500주 reproduces R4's own card client-side — **679,575원** (하한 **545,181원**),
    배정 **123주 × 5,525원**, `발행 − 청약 = 소멸 3,734,925주 (8.86%)` + **206.4억원**, calc footer
    and disclaimer — and 1,000주 gives exactly 2× (246주 · 1,359,150원); 대한광통신 shows
    **2,117,937주** beside the derived **2,083,302주** with both inputs cited, unreconciled;
    유티아이's D+46 ② reads **진행 중** and the word 종료 appears nowhere; 휴맥스's ③ (D-5) has the
    dependency line and no won amount; 고려아연 gets the no-event state with 감시 중 **488건**;
    한솔테크닉스's flagged-event row keeps its 소멸 계산 and loses the 기간 line, the quote and the
    link; 390×844 has **no horizontal overflow**, every target ≥44px, and **zero `position: fixed`**
    elements (P6's corner stays clear).

### `P5.S15` — the auth surfaces exist; the routes S16 owns, the session seam, the copy floor

`frontend/components/auth/` + `app/auth/{login,reset}` is R5-1's one panel and R5-2's two
conversion touchpoints, over the `/auth/*` endpoints `P5.S7` built. **0 new dependencies, no
primitive / token / chrome file touched, Python suite untouched at 113, no Korean invented**
(every string cited in `components/auth/copy.ts`). Verified in real headless Chrome over
`npm run start` **and** `next dev` — 76 of 80 checks pass, and the four non-passes were
over-strict assertions, each re-measured in `result.md`.

| you need | use |
|---|---|
| "am I logged in", in a **client** component | `import { useAuthState } from "@/components/auth/useAuthState"` — lazy (`enabled`), and `null` until answered |
| …in a **server** component | `import { readAuthState } from "@/lib/session.server"` — forwards the request's own cookie |
| the raw probe / the 로그아웃 flash | `@/lib/session` — `fetchAuthState` · `writeFlash("logout")` · `readFlashOnce()` |
| a structural code → R5's signed body line | `authErrorKo(code)` from `@/components/auth/copy` — **three codes, `null` for everything else** |
| an R5 element on another surface | `@/components/auth` → `ConversionOffer` · `DeadlineOffer` · `SampleEntry` · `PiiInset` |

**The routes decided here, which `P5.S16` must honour** (`lib/routes.ts` states each once):
`/auth/login` · `/auth/reset?token=` (**the backend already fixed this** —
`mijual.web.auth.RESET_PATH` mails `{MIJUAL_APP_BASE_URL}/auth/reset?token=…`, so it is a query,
not a `[token]` segment) · **`/portfolio`** 내 포트폴리오 (the API's own noun; a successful
로그인 routes there and it **404s until S16**) · **`/portfolio?sample=1`** (`samplePath()`, both
signed sample entries) · **`/portfolio?add={corp_code}`** (`portfolioAddPath()`, the logged-in
담기 link — a navigation that writes nothing; S16 preselects the issuer in R5's own 종목 추가
panel).

1. **What `P5.S16` still owes, stated as a list because three of them are links this slice
   already renders.** (a) The 내 포트폴리오 page itself at `/portfolio`. (b) The **sample mode**
   behind `?sample=1` — banner, nav 「샘플」 칩, 샘플 종료, over the anonymous
   `GET /portfolio/sample` that already exists. (c) The **`?add=` preselection**. (d) The
   logged-in **account menu** in `AccountSlot.tsx` — untouched here, still R2's quiet 로그인 link
   (measured `rgba(255,255,255,.68)`, weight 400: R5-2's "nav 로그인 변경 금지" holds). (e) The
   **로그아웃 writer**: call `writeFlash("logout")` and send the reader to an anonymous surface;
   the auth panel already reads and clears it, so "로그아웃되었습니다 1회 표시" needs no second
   mechanism.
2. **An authenticated visit to `/auth/login` redirects to `/portfolio`, and that is a design
   reading.** R5's fourth auth state (로그인됨) *is* the 2층 — there is no signed logged-in
   variant of the auth screen — so rendering one would have meant inventing both a sentence and
   a control. Server-side, over the forwarded cookie.
3. **`authErrorKo` is the whole error vocabulary, and it is exactly three codes wide.**
   `invalid_credentials` → 불일치 · `email_taken` → 중복 가입 · `password_too_short` → 8자 미만;
   **everything else returns `null` and the surface shows no line.** Two otherwise-silent codes
   are held off structurally rather than verbally: `invalid_email` by the email input carrying
   **`mijual.web.auth._EMAIL_RE` as its `pattern`** (measured: `a@b` cannot be submitted at all
   and spends no request — the browser refuses in the UA's own words, the same class as the
   framework's English 404), and `csrf_required` by `lib/api.ts`. **`invalid_reset_token` stays
   reachable and stays silent — new Open Question below.**
4. **The 8자 rule is checked client-side on 계정 만들기 and the reset confirm, never on
   로그인.** On a login a short password is a *wrong* password and R5's line for that is 불일치;
   checking length there would contradict the round and leak a password-shape fact. Where it
   applies the client states the **same signed sentence** the server maps `password_too_short`
   to — measured to render without spending a request.
5. **An error line is body ink, never `--alert`.** `--alert` means expiring/lost and nothing
   else (`frontend.md`: "Red never encodes price movement"), and R5 says "오류(**본문** 한 줄)".
   A red auth error would spend the one hue reserved for a deadline. Later surfaces with their
   own failure copy (`P5.S17`'s door) should follow this, not invent a second treatment.
6. **확인 중 is the button's own text, measured.** Under 700 ms emulated latency the submit
   button reads `확인 중…` and is `disabled`; **no spinner element exists on the panel**, and
   nothing anywhere on these surfaces is a modal or an overlay.
7. **The 조회 offer's three conditions, and the one that is a reading.** Shown (a) only after
   `lib/holding.ts`'s own `convert()` produces a value — the same multiplication site the rows
   use, so no second arithmetic exists and an unpriced ① can never trigger it; (b) once per
   session, flag `sessionStorage["mijual.convert.offer"]`; (c) **only to an anonymous reader** —
   its body is "계정에 저장하면 …", and offering an account to someone who has one is the
   가짜 사용자 정체성 R5 forbids. R5-2 writes no logged-in variant of *this* panel (the swap it
   signs is the detail one-liner), so (c) is this build's reading — `P5.S19`'s to confirm.
   The panel is the **last block of the stock view, in normal flow** (`CraftPanel`'s own
   `position: relative`; the page still has **zero** fixed elements, so P6's corner stays clear).
8. **The detail one-liner is gated on `countdown.days >= 0`, and that is also a reading.**
   "이 마감 알림 받기" under an anchor already behind the reference day promises an alert nothing
   can send — the 시점 칩 are 7/3/1/0 days *before* a deadline — and a 추후결정 event has no
   마감 at all. Measured absent on a D+43 ①, a 추후결정 event and a 철회 page; present and
   under the D-day on 계양전기's D-3.
9. **⚠ Every event detail page now makes one `GET /auth/me`.** It is what renders the signed
   two-state line, it answers 200 either way (anonymous is a result, not a 401) and it gates
   nothing — but the element renders **nothing until the probe answers**, so a two-state line
   never flashes the wrong state. If `P5.S16` decides the chrome should probe once per page load
   for the account menu, that probe should **replace** this one rather than sit beside it; both
   read `lib/session.ts`.
10. **The PII inset renders two lines, not three.** R5's copy list says "PII 패널 3행" while
    R5-1 quotes exactly two sentences; the third is on the card, which stays in the design
    project. Nothing was invented to reach the count — `P5.S19` checks it against the card.
    The inset is on **both** auth pages, because `security` calls it "a permanent inset panel on
    the auth screen".
11. **Three labels are composed from the round's own nouns, never written.** `비밀번호 재설정`
    (the trigger, and the confirm page's title + verb — the record names the mechanism and never
    labels its control), `이메일` / `비밀번호` (R5-1's own "이메일+비밀번호"), and the 전환
    링크, whose label **is** the other mode's name. Same class as `P5.S11`'s `© 미주알`; all
    flagged for `P5.S19`.
12. **⚠ The sample subline says 4건 while the live sample renders 5 rows** (`P5.S8` note 14 —
    대동기어 also holds an exposable ① that lapsed). The sentence describes the *composition*,
    which is still four pinned disclosures, and it is signed copy, so it is transcribed verbatim.
    `P5.S16`/`P5.S19` will see the difference on the page; it is live data, not a deviation.
13. **The landing's sample line is a landing element, not chrome** (`P5.S11` note 11, honoured):
    one `<SampleEntry variant="landing" />` at the foot of `app/page.tsx`'s stack, asserted in
    the browser **not** to be inside `<footer>`. R5's "Footer 불변" holds — no chrome file was
    edited by this slice at all.
14. **Live cross-check (2026-08-22, headless Chrome, `npm run start` + `next dev`).** 가입 →
    확인 중 → `/portfolio` with a live cookie; wrong password and unknown address produce the
    **identical** string (compared with `==` in the browser); 중복 가입 and 8자 미만 their own;
    재설정 answers identically for a known and an unknown address and the link appeared **only**
    in the server log; the emailed link opens the confirm page (**token never rendered**), sets
    a password, lands logged in, and is **single-use**; 한화솔루션 500주 still reproduces
    **679,575원** with the offer beside it; 390×844 has **no horizontal overflow**, every target
    ≥44px and zero fixed elements. Test account and its reset grant deleted afterwards —
    `account/auth_session/password_reset/holding/lapse_claim/notification_pref` all back to 0.
15. **Gotcha for `P5.S16`, cost this slice a build:** `lib/session.server.ts` may not import a
    module whose graph contains a React hook (`next/headers` and `useState` cannot meet), which
    is why the hook lives in `components/auth/useAuthState.ts` and `lib/session.ts` imports no
    React at all. Keep that split.

### `P5.S16` — 내 포트폴리오 is live; the storage keys, the chrome seam, and the trap that froze the router

Files: `app/portfolio/{page.tsx,notifications/page.tsx}`, `components/portfolio/*` (11 files),
`lib/sample.ts`, `lib/account.ts`, `components/chrome/{AccountSlot.tsx,useAccount.ts}` +
`copy.ts`/`AccountSlot.module.css`, `lib/routes.ts`, `lib/session.ts`, and two exports added to
`components/lookup/`. Full detail in the slice's `result.md`.

1. **⚠ The trap that cost this slice hours — an inline `[]` will freeze the App Router.**
   `sampleCorpCodes: sample?.holdings ?? []` fed a `useMemo` that fed an effect's dependency
   list, and the effect called `setEntries([])`: two fresh identities per render, so
   render → effect → state → render, forever. **React warns nothing** (passive effects, not
   nested sync updates) and the page looks fine. What breaks is anything needing a React
   transition to finish: `router.refresh()` fetched the new payload and never committed it, and
   **every client navigation away from `/portfolio` did nothing** — nav links and the account
   menu alike, with the RSC response arriving and then `net::ERR_ABORTED` as the next render
   interrupted the transition. Measured `/portfolio → /` 0/4 before the fix, 4/4 after; the other
   routes were 12/12 throughout. Fix: shared frozen empties + an identity-preserving functional
   `setEntries`. **If a link or a refresh in this app ever "does nothing", look for an inline
   `[]`/`{}` reaching a dependency list of an effect that sets state — not at Next.**
2. **The write→re-read seam.** An account write is followed by this client's own
   `getPortfolio()`, and the whole served payload replaces the one in state — the same endpoint
   the page reads, so the rows, factors, placement and D-days are still composed once, on the
   server. Not `router.refresh()`: same one request, but Next 16 answers a refresh by
   re-prefetching every in-viewport `<Link>` too (vercel/next.js#93210). An edit is on screen
   ~0.1 s after the write, and navigating away and back re-renders from the server anyway.
3. **Storage keys, complete (S19 will inspect these).** localStorage: **`mijual.portfolio.sample`**
   = `{v:1, holdings:[{corp_code, shares}], claims:[rcept_no]}` (the sample's edits and marks).
   sessionStorage: **`mijual.portfolio.carry`** and **`mijual.portfolio.migrate`** = "this tab
   declined that offer" flags — dismissal is a flag, never a deletion, so declining keeps the
   browser's value and a new session may ask again. Plus S14's `mijual.lookup.holdings` (read)
   and S15's `mijual.auth.flash` (written on 로그아웃). Nothing anonymous reaches the server.
4. **`AccountSlot` is the whole chrome change, and it has exactly three renderings** — R2's
   로그인 link untouched, the 축약 이메일 menu (mono, `앞 4자 + … + 도메인 끝`; 내 포트폴리오 /
   알림 설정 / 로그아웃), and R5-4's 「샘플」 + 샘플 종료 pair, which **outranks both** (a loaded
   sample is a browser fact and must be endable from anywhere). The slot renders **nothing** until
   `GET /auth/me` answers — 로그인 for a frame to a signed-in reader is the wrong half of the
   가짜 사용자 정체성 rule. The probe is shared through a module store (`components/chrome/useAccount.ts`)
   and `lib/session.ts` now de-dupes in-flight probes. Nav links, the 52px bar, the underline, the
   의견 slot and the footer are untouched.
5. **로그아웃 · 계정 삭제 · 샘플 종료 leave through `window.location.assign`, deliberately.** The
   session (or the sample) is gone, so every gated payload the client router cached is stale and a
   Back press must not restore it — and a `router.push()` from these controls is dropped anyway,
   because the control unmounts in the same commit. The one-time "로그아웃되었습니다" survives the
   full load because S15's flash channel is `sessionStorage`; it rendered exactly once.
6. **A repeat 담기 opens that row's 수정** rather than surfacing S8's `holding_exists` 409 — R5
   wrote no "이미 담긴 종목" line and the client holds the whole list, so no Korean was invented.
   Works from both entrances (the panel's 조회 and the `?add=` link), and it does not touch the
   count. **`?add=` comes from the event detail one-liner** (S15's `DeadlineOffer`, rendered only
   where the deadline is still ahead), resolved **server-side** through `GET /stocks/{corp_code}`;
   an `add=` that resolves to nothing is simply absent.
7. **계정 삭제 arms in place.** R5 signs "즉시" and forbids gate screens and forced modals, so the
   confirm is the round's own vocabulary: the action column becomes 계정 삭제 · 취소 — 개정 ④'s
   horizontal swap — and the second press deletes. No new copy, no overlay.
8. **알림 설정 lives at `/portfolio/notifications`** behind the same gate. Deselecting every 시점
   칩 saves `[]` — the round's only off switch, so it must not fall back to the served default. The
   **KakaoTalk row renders no control at all** (label + 「예정」 + the signed sentence): structural,
   since S8 built no server field for it.
9. **조회 and 포트폴리오 render the same ②/③ components** — `Conversion`/`Dilution` are now exported
   from `components/lookup` — so "수치 불일치 금지" holds structurally. Verified live: 한화솔루션
   500주 → **679,575원** on both surfaces, 1,000주 → 1,359,150원. ②'s only 원 is 전환가액 15,552원,
   R4's signed **per-share** context — when testing "no money on ②/③", test for the 보유량-기준
   column (`놓친 돈`/`챙긴 돈`/`n주 기준`/`추정`), not for the character 원.
10. **샘플 모드 has no 종목 추가, on purpose.** R5-4 signs the sample as a fixed composition that is
    *editable* (보유량, 삭제, R5-8's mark) and endable; adding an arbitrary issuer would need the
    client to compose that issuer's rows and place them into 다가오는/지나간 itself — a second
    composition site for the rules S8 owns (a past ③ appears in no 조회 payload at all). The sample
    serves **five** D-day rows for four issuers (S8 note 14), as the live data says.
11. **Live pass (2026-08-22, headless Chrome over `npm run start` + uvicorn, plus a `next dev`
    smoke): 107 checks, 107 pass** — 샘플 23, 계정 A 29, 계정 B 22, 계정 C 33. Covered signup →
    empty state → 세션 이월 → 종목 추가 (name and 종목코드) → the D-day sections and the 조회
    cross-check → inline edit → 삭제 + 되돌리기 + the window closing itself at 8 s → 챙긴 돈
    (label/ink flip on the same figure, persists) → 알림 설정 (defaults, empty allowed, no Kakao
    control, 주소 변경) → 로그아웃 (message once) → the gate (only `/portfolio*` redirects) →
    re-login → 계정 삭제 → 샘플 모드 end to end → 계정 이전 → mobile 390×844 (0 px overflow, 0
    fixed elements, every target ≥44 px — the 챙긴 돈 checkbox is a 16 px box inside a 194×44
    **label**, which is what a tap activates). Test accounts deleted through the product's own
    계정 삭제; all six reader tables back to **0**.
12. **Test-assertion traps worth not repeating:** `document.body.innerText` in headless Chrome can
    include the inline flight `<script>` — scope "no 합계/총액" checks to `main` (the **footer**
    carries R4's market-wide "…총액에서 제외했습니다"); and measure a tap target on the enclosing
    `<label>`, not on the native checkbox.

### `P5.S17` — 운영 관제 is live; the ops idiom `P5.S18` imports, and eight readings

1. **The ops idiom is a module, not a style opinion — import it.** `frontend/components/ops/`
   owns the whole surface: `Ops.module.css` states the idiom **once**
   (`--ops-panel: #0e1a15` as a local custom property — the vendored token file stays read-only,
   1px `--border-strong`, zero ornament, `min-width: 1180px` and **not one media query**), and
   `atoms.tsx` exports the five primitives every tab is built from — `Panel` (title + mono note),
   `Code` (raw English identifiers), `Num` (tabular), `Stamp` (**slices an instant string; never
   `Date`-parses it** — the server already sends `+09:00`), `Absent` (「없음」 as a *state*), plus
   `Rcept` (rcept_no + DART link) and `Quoted`. `P5.S18`'s vocky tab should import these, add its
   route to `OPS_ROUTES` + `OPS_TABS` in `routes.ts`/`copy.ts`, and write **no new CSS idiom**.
   `S10` note 8 held: **no `CraftPanel` here**, and none was reached for.
2. **`components/ops/routes.ts` is deliberately not `lib/routes.ts`.** The ops path map lives
   inside the ops module so no reader-chrome module can import an `/ops` href by accident. Verified
   in a browser: six reader surfaces contain **no `/ops` href and no `/ops` substring at all**.
3. **The tab-restore mechanism is "the door renders in place", not `?next=`.** `app/ops/layout.tsx`
   probes `GET /ops/session`; unauthenticated it renders `<Door />` **at the requested URL** with no
   redirect, and a successful login calls `router.refresh()`, which re-runs that same route. Nothing
   is stored, no path travels in a query string, and an expiry mid-session returns the operator to
   the tab they were on. Any future ops route gets this free.
4. **Escaping the reader chrome cost exactly one reader-side edit.** `components/chrome/SiteChrome.tsx`
   is now a **client** component that returns `children` bare when `isOpsPath(pathname)`. The
   alternative — moving every reader route into a route group — would have changed which layout the
   framework's 404 renders inside, i.e. behaviour `P5.S13` measured. Re-verified: a not-found event
   still renders inside the reader chrome. The chrome markup itself is untouched.
5. **Two signed R7 elements had no backing, so the backing was built** (D-15's rule; the Python
   suite therefore moved **113 → 114**, which is a deliberate deviation from that slice's plan):
   - `opsreads.open_decisions()` reads `docs/current/decisions.md` and quotes its `- **Open…`
     bullets **verbatim** with the doc's own version (today: `v0004`, exactly one open item, D-4 —
     which is R7's own card example). A missing file yields `{available: false, reason}`; nothing is
     re-worded or summarised, because 가동 전 미결 is a quotation surface.
   - `GET /ops/lock` — the lock chip lives in the bar on **all six tabs** and polls every 15 s;
     `/ops/overview` walks 488 events, so polling it would have made the chip the most expensive
     thing on the surface. The chip's endpoint returns `lock_state` + `as_of` and nothing else.
     **`/ops` is now twelve routes**, all read-only, all behind the same `OpsGate`.
6. **The absent-fact rendering decision (샘플 로드 여부), now measured:** the column is
   **data-driven** — it renders iff a served row carries `sample_loaded`. No row does today, so
   there is **no column and no cell** (verified with a real account present: 0 placeheld cells on
   the tab). This is the one rendering that satisfies both R7 ("no placeholder where a value would
   be") and `states-and-trust` §4 (never assert a fact the system does not hold), and it means
   building the backing later needs **no frontend change**. The standing open question is unchanged.
7. **The vocabularies `P6` will own are marked, not invented.** 거절 카테고리 filters send the five
   **signed Korean** family names (철회 · 확정 전 · 공시에 없음 · 검증 미통과 폴백 · 계산 요청) —
   not invented English tokens; `유형` sends `answer`/`refusal`, which are the API's own parameter
   values. `log.ts` documents a **three-tier key convention**: keys the API already names
   (`session_hash`, `kind`, `refusal_category`) are read directly, a small set of expected keys is
   read defensively, and **any other served key renders raw** rather than being dropped. When P6
   ships real rows, mismatches show up as raw keys instead of silent blanks.
8. **Only one thing on this surface is derived client-side**, and it is the one R7 mandates:
   `lib/opsRuns.ts` joins `beat.entries[].due` with `runs.rows` and emits an alert-ink
   「실행 기록 없음」 row per uncovered due instant. It is a pure module so `npm run smoke` covers it
   (**9 → 11** `node:test` cases): a beat run covers only its **own** due instant, and a manual run
   or another entry's run is **not** cover. The KST clock is the only other client computation, and
   it is display-only.
9. **CSS gotcha, measured in a browser:** `.table td` (class **+** element) out-specifies a bare
   `.alert` class, so the alert row silently rendered in body ink. The rule is now stated twice
   (`.alert, .table td.alert`) and re-measured at `rgb(224, 87, 63)`. Any later ops cell colour must
   match `.table td`'s specificity or lose to it.
10. **The clock deliberately keeps ticking under `prefers-reduced-motion`.** It is a *readout of the
    current time*, not an animation; freezing it would make the panel state a wrong fact. Recorded
    because it is the one place on the product where a moving element is intentional.
11. **Test-assertion traps from this slice** (three of the four browser "failures" were the checks,
    not the product): a "no 가입/재설정" regex matched the door's own **rules panel** quoting
    「가입·재설정 UI 없음」 — assert the control set instead (`["로그인"]`); an em-dash regex matched
    signed copy 「가입 0건 — 미배포 상태의 실제값」 — count placeheld cells instead; and
    `header nav a` matches the **always-in-DOM mobile sheet** (S11 note 7), so scope reader-chrome
    nav assertions to the *first* `header nav` or you will count seven links.
12. **The browser pass, for the record:** 104 scripted checks, 104 pass, over
    `npm run build && npm run start` with the API launched as
    `MIJUAL_OPS_ID=… MIJUAL_OPS_PASSWORD=… .venv/bin/uvicorn …` — **the operator's `.env` was never
    opened**. Covered: the uniform door failure (wrong ID vs wrong password compared with `==`),
    deep-tab door + restore, 개요 tiles equal to `python3 -m mijual.gates summary` (488/628 · 710 ·
    418 · measured 2026-08-22 04:14 KST), six 실행-기록-없음 rows in alert ink, the 691 basis,
    `evalset report`'s markdown byte-identical to the served artifact, honest `0건` on three tabs, a
    live account row and its deletion, a **live held → free lock chip** (a real Redis key, set and
    removed), the reader cookie opening nothing, and six 1440-wide screenshots. No mobile pass —
    desktop-only is signed.

### `P5.S18` — vocky's shape is decided; the endpoint, the allowlist, and where the view lives

§6.3's delegation is closed. The shape was decided against **vocky's running product**
(the operator's own repo at `~/projects/personal/vocky`, read-only, plus a throwaway local
stack) and written back into `rounds/07-admin/output/build-prompt.md` §vocky 관찰 뷰 as a
dated subsection — **59 lines added, 0 changed** (`git diff` shows no `-` line in that file).
**0 new dependencies**; Python suite **114 → 118**, frontend smoke unchanged at 11.

| you need | use |
|---|---|
| the observation itself | `mijual.web.vocky` — `observe(settings, limit=, cursor=)` → `Observation.payload()` |
| the decided field set | `mijual.web.vocky.ROW_FIELDS`, **also served as `payload.fields`** |
| the route | `GET /ops/vocky?limit=&cursor=` (`/ops` is **thirteen** routes now, all read-only) |
| the settings | `MIJUAL_VOCKY_API_BASE` + `MIJUAL_VOCKY_API_KEY` (`Settings.vocky_api_base` / `.vocky_api_key`, `require_vocky_api_key()`) |
| the surface | `frontend/components/ops/Vocky.tsx`, rendered by `app/ops/feedback/page.tsx` |

1. **The endpoint is `GET {base}/api/project/feedback`** — vocky's **Project Feedback API
   v2**, whose own contract names this exact use ("an external service's own admin panel /
   operator page … reading and managing its project's feedback directly by API"), authed by
   `Authorization: Bearer vk_…` with the scope implicit in the key (there is no project
   parameter on that surface). The other three read surfaces were rejected on the record:
   `GET /api/feedback` is one product *user's* self-read (needs a `user_id`), `/app/feedback`
   wants a human session token, and `/api/project/usage` returns the org's **credentials** —
   key metadata a different product's panel must not render (최소 열람).
2. **Granularity = one feedback event per row; pagination = keyset cursor, newest first.**
   `limit` default 50, **max 100 — vocky's own ceiling** (`limit must be between 1 and 100`,
   measured), not this panel's usual 200. `next_cursor` is vocky's opaque string, passed
   through untouched and **absent, never null**, at the end. **There is no total**: vocky
   returns none, so `count` is *this page's* row count and no total is invented.
3. **The fields are an allowlist, and the client names none of them.** Sixteen keys, in the
   table's order, using **vocky's own English names** (§6.1/§6.2 sign raw English identifiers
   here): `ingested_at · message · feedback_value · trigger_type · trigger_message ·
   target_type · target_id · target_text · channel · recorded_by · source_product ·
   source_integration · comment · tags · id · project_id`(org keys only). Excluded on
   purpose: `user_id` · `session_id` · `conversation_id` (correlation handles — 사용자 추적
   용도 금지), `messages` · `used_context` · `source_metadata` · `attributes` ·
   `trigger_metadata` (free-form blobs), `target_role` · `event_at`. The set travels in
   `payload.fields` and the table renders **those** headers, so widening it later is a
   backend one-liner with **no frontend change** — and the card's `?` headers are gone.
4. **The 피드백 section *is* the vocky view — `P5.S17`'s placement was inverted, and this
   slice corrected it.** R7's seven cards map 1:1 onto the six signed tabs *in order*, and
   the record is explicit: `result.md` — "**Feedback** — vocky 관찰 뷰 프레임 (§6.3)", while
   the `save_feedback` 대기열 is drawn on the **Conversations** card; `handoff.md` §5 says
   the same (`admin/Feedback.html` = the vocky observation view; `admin/Conversations.html` =
   the log viewer **+ agent feedback queue**). So the queue moved to `/ops/conversations`
   (its own `?feedback_cursor=`, so the two tables page independently) and `/ops/feedback`
   became the vocky view. **A seventh tab was rejected** — it would break the signed 6-tab
   nav. The round's reasoning agrees: 병합하면 "익명 대화 로그"와 "자발 이메일 동반 의견"의
   서로 다른 프라이버시 계약이 섞임 — the queue's rows come out of the anonymous
   conversations, vocky's from a different collection path. **상호 링크만**: vocky →
   「대화 로그 →」, queue → 「피드백」, and neither table reads the other's rows.
5. **⚠ vocky ships no embeddable widget script — R2/S11's assumption does not hold.**
   `data-vocky-trigger` / `embed.js` / `widget.js` appear **nowhere** in the repository,
   `web/public/` holds only `install.sh` and `SKILL.md`, and vocky's README lists
   "Browser-direct unauthenticated ingestion" under **What The First MVP Will Not Do**; every
   "widget" mention there is an example of a *kind of surface* whose feedback you capture.
   So **`NEXT_PUBLIC_VOCKY_SRC` has no real value to set today**. Nothing is dropped: the
   three triggers and the seam stay exactly as `P5.S11` built them (unset ⇒ no script tag,
   triggers still render), and the rows this view observes will arrive from whatever capture
   path the operator wires — a server-to-server `POST /api/feedback`, not a browser widget.
   **Do not build one here** (R7: 위젯 UI는 vocky 소유).
6. **Read-only is structural, because vocky cannot make it a property of the key.** vocky has
   **no read-scoped credential** — "one `vk_` key does capture **and** full read+manage across
   its whole scope" — so the key Mijual holds could write. `mijual.web.vocky` therefore issues
   `GET` and has no code path that could issue another method, and a new test asserts that
   **only `web/vocky.py` may import an HTTP client** (`urllib`/`http.client`/`socket`/
   `requests`/`httpx`) so a later slice cannot quietly put a second external dependency on a
   request path. `tests/test_web_ops.py`'s "no vocky route is pre-implemented" guard
   (`P5.S9`'s, for the pre-decision period) was inverted deliberately: the route exists and
   reports 연결 전 when unwired.
7. **Transport decisions, each one a rule.** stdlib **`urllib.request`** (no dependency added;
   `httpx` is a dev extra) on a sync endpoint, so FastAPI's threadpool absorbs the block;
   **3 s timeout, no retries**; **redirects refused** — `urllib` re-sends `Authorization` to
   the redirect target, so a redirected base URL would hand the `vk_` key to whatever
   answered; a non-`http(s)` scheme refused for the same class of reason. The key is masked in
   `Settings.__repr__`, raises only on use, travels in a header, and **neither it, the
   response body, nor the exception text is ever logged** — vocky's error text is not echoed
   onto this panel.
8. **Degraded honestly, measured.** Three states (`ok` · `unconfigured` · `unreachable`), the
   `P5.S9` Redis precedent, **never a 500 and never a fabricated row**. Live: dead port →
   `URLError` in **12 ms**; wrong key against a live vocky → `HTTPError` + `status 401` in
   **33 ms**; blackholed host → **3.03 s**, i.e. the timeout bound holds and the tab cannot
   hang the panel. Unconfigured renders R7's signed 「API shape 확정 대기」 over **48 skeleton
   cells carrying the decided column names**.
9. **⚠ The 연결 전 literal is now half a step stale, and was left as signed.** The shape is
   confirmed, so what the view waits for is the **credential**, not the shape. Rewriting a
   signed line is a design change, so it renders as signed and the raw English `state` code
   beside it says which cause it is. **`P5.REVIEW`/operator call** whether 「API shape 확정
   대기」 gets re-cut — new Open Question below.
10. **The live pass, for the record (2026-08-22).** A throwaway vocky stack from its own repo
    under its **own compose project** (`-p mijual-s18-vocky`, ports 8010/55433/56380 — no
    collision with Mijual's 5433/6380), migrated **inside the container** so the local
    `uv.lock` was never touched, driven entirely over REST (no CLI install): account +
    `"default"` project + a project `vk_` key, **3 captured rows** with Mijual-shaped context,
    then `GET /ops/vocky` and the rendered tab — title, the three contract lines, `state ok`,
    the real headers, `2026-08-22 16:33 KST`, the Korean text, `3건`, the cross-link, and
    cursor page 2. 대화 로그 re-checked: the queue's signed empty state and **no vocky row or
    column on it**. Everything stopped, volumes and images removed;
    `git -C ~/projects/personal/vocky status` **clean before and after**, and
    **`vocky.hi2vi.com` was never contacted** — no account there, no request of any kind.
11. **What P4 must supply** (nothing else is needed to light this up):
    `MIJUAL_VOCKY_API_BASE=https://vocky.hi2vi.com` and `MIJUAL_VOCKY_API_KEY=vk_…` minted by
    the operator in their own vocky org (org- or project-scoped both work; a project key's
    rows carry no `project_id`, an org key's do). **https matters** — the key travels in a
    header. `NEXT_PUBLIC_VOCKY_SRC` stays **unset** until a widget script exists (note 5), and
    it is inlined at build time, so setting it will mean a rebuild (`P5.S11` note 6).

### `P5.S19` — the fidelity pass ran in a real browser; five fixes, and what `P5.REVIEW` can trust

1. **What was actually done.** `npm run build && npm run start` + uvicorn against the live corpus,
   driven in headless Chrome over CDP: **~230 scripted checks across 11 stages**, at 1440 / 768 /
   390 plus the intermediate widths (481/600/900/1024/1119/1120) the phase flagged, with 41
   screenshots kept. Every signed surface was checked against **its own round's contract**, not
   against a general sense of taste: R1 foundations swept across 12 pages, R2/R2.1 landing +
   chrome, R3 on **11 real events** covering every state (①unpriced · ①lapsed · ②sparse · ②past ·
   ③ · 추후결정 · 철회 · 기재 불일치 · 정정 이력), R4 with and without a holding count, R5 auth +
   portfolio + sample + the conversion touchpoints, R7 all six tabs behind the door, and the
   cross-cutting trust rules as their own stage. Full table in the slice's `result.md`.
2. **Five faithful-implementation fixes landed** (code only — **no landed record was touched**,
   no token file, no new value chosen anywhere):
   - **The global `.mono` rule was overriding every surface's own font-size.** `app/shell.css`'s
     `.mono {font-size: .95em}` and a CSS-module class are both specificity **(0,1,0)**, so source
     order decided — and the global won **everywhere**: **23 classes** collapsed to one flat
     **12.825px**, including R4's 놓친 돈 **총액 (should be 32px)**, 보유량 input and every
     per-holding 금액 (20), R3's 청약 결과 inset (20) and crumb (12), R2's tab counts (11), the
     meta/eyebrow lines (11). Fixed by splitting the rule: `.mono` keeps family + tabular-nums,
     **`:where(.mono) {font-size:.95em}`** makes R1's ratio a *zero-specificity default* a stated
     size beats. **Do not merge those two rules back together** — the comment in `shell.css` says
     so at the site.
   - **Footer 「추정」 was 6.72px** (`P5.S11` note 9): 0.56em of a 12px sentence against R2's own
     "bordered sans **10px** tag". Fixed through the sanctioned route — a **named prop** with its
     citation, `<EstimateMarker size="landing">` → 10px — not a local restyle. `P5.S12` note 5's
     two readings now settle together: footer = R2's 10px literal; landing = 0.56em of the
     surface's 17px context (9.52px).
   - **R3 §2's "mono window/state line" rendered half sans** — the dates were mono, the state
     phrase (`거래 가능 · 마감 D-3`, `진행 중`) inherited sans, so a **D-day numeral rendered
     outside R1's mono rule**. `font-family: var(--font-mono)` on `.windowLine`.
   - **41px of horizontal document overflow on the landing through the 768–830px band**: R2's
     board grid `86px 1fr 300px 230px 96px` + four 12px gaps = 760px inside a 720px content
     column. The two wide columns became `minmax(0, …)`: R2's widths wherever they fit, shrink
     instead of scroll below that. **0 overflow at every width now**, nothing truncated.
   - (the tab counts are the same defect as the first item; listed in `result.md` for completeness)
3. **What `P5.REVIEW` can trust as measured, not asserted.** No off-token colour on any reader
   surface (35 rendered colours, all tokens or R2 literals); **radius 0** except R2's own hero
   ellipses; the only box-shadow is `--panel-glow`; motion only R1's durations/eases and the
   named keyframes, with reduced-motion freezing the tick and hiding the ambient layer; **Korean
   prose verifiably draws in Pretendard Variable** (`CSS.getPlatformFontsForNode`, not a
   computed-style guess); every numeral mono after fix 3. **Trust rules all hold**: no untagged
   estimate and no tagged fact, **no money before 확정발행가 on any of the three surfaces**, no
   ②/③ per-holding won, **40 board D-days identical to the served `countdown.dday`** and the
   countdown 0 s off the served absolute instant, past ② reads 진행 중 and never 종료, 추후결정
   never beside a date, a gate-blocked field is **absent** and never placeheld, and 조회 and
   포트폴리오 agree to the won (한화솔루션 500주 = 679,575원 on both).
4. **`D2`'s trigger did not fire** (the decomposition's deferred duplicate-row/double-count
   watch): **no two of the 389 rendered board rows share an `rcept_no`**, and 코이즈 — the
   two-version case — serves `totals.offerings: 1` and renders one breakdown row.
5. **Every `S19` mention in this file was swept** and given a disposition; the table is in
   `result.md` §3. Nothing was left implicit: each item is either *verified as described*,
   *fixed*, or *catalogued for the operator*.
6. **The Korean-in-mono question is judged, not fixed.** Korean glyphs inside `--font-mono`
   elements fall to the OS Korean face (macOS: Apple SD Gothic Neo). Every such element is one
   the record **draws in mono** — `StateBadge 추후결정`, the 소멸주의보 badge, `[근거]`, R2's
   positioning/stat/band lines, the mono chrome — and R1's rule is *"Korean **prose** never mono"*,
   which holds. Making those glyphs a single cross-platform face means editing the landed
   `tokens.css`, i.e. **a design change**. Left as built, catalogued.
7. **19 operator questions are consolidated in `result.md` §4**, grouped as: copy the record does
   not contain (English 404 · silent `invalid_reset_token` · the half-stale 「API shape 확정 대기」 ·
   the 내 종목 연결 positioning line · five composed labels · the 4건 subline vs five live sample
   rows), states the design never drew (closed 청약 with no 실적보고서 · R7's 샘플 로드 여부), type
   and layout the cards must settle (the mono/Hangul face · `[근거]`+DART link under the 44px
   mobile floor · the 340px chain-step gap · the hero H1's name · the two-line PII inset · the
   메뉴 hairline · a three-line mobile ① row and the sans dates inside two signed R4 sentences),
   and product decisions already standing (the dated 49.2억원 · no vocky widget script · the two
   stated defaults · 수신 주소 변경 re-auth). **None is an implementation defect** — each needs a
   new visual or operator decision, so none was decided here.
8. **Deliberately not "fixed":** 조회's coverage caption and its `청약 {date} 종료` line render
   their dates in sans while the boundary panel renders its dates in mono. The record gives those
   as whole signed sentences, so splitting the type inside them is a typographic decision, not a
   correction.
9. **Two operational gotchas, worth more than they look.** (a) `npm run start` fails **silently
   into `next.log` with `EADDRINUSE`** if an older `next start` still holds :3000 — the stale
   server then serves a build manifest whose CSS chunks 500, which looks exactly like *"my fix did
   nothing"*. Kill the listener (`lsof -nP -iTCP:3000 -sTCP:LISTEN`; `pkill -f next-server` does
   **not** match it) and confirm a CSS chunk returns 200 before believing any measurement.
   (b) A flattened-`innerText` proximity check produces confident false failures — four of this
   pass's "FAIL" lines were probe artifacts (a verbatim 정정 요약 containing 원, a header date near
   the 추후결정 badge, a frame line checked before a count was typed, a wrong `corp_code` measuring
   a 404). Re-measure with a scoped selector before believing a failure.
10. **Client storage, inventoried** (`P5.S16` note 3's deferral): localStorage `mijual.portfolio.sample`;
    sessionStorage `mijual.lookup.holdings`, `mijual.convert.offer`, `mijual.auth.flash`. Nothing
    anonymous reaches the server. One cross-tab observation, not signed and not fixed: a tab whose
    chrome mounted before another tab loaded the sample can show the account slot while its body
    renders the sample; **single-tab behaviour is correct**, including that logging in with a sample
    loaded shows an **empty account portfolio + the 계정 이전 offer**, never the sample rows as the
    account's.
11. **Hygiene.** The four test accounts this pass created were deleted through the product's own
    계정 삭제 (`/auth/me` back to anonymous); ops credentials were passed as **process env vars for
    this run only** and the operator's `.env` was never opened; `NEXT_PUBLIC_VOCKY_SRC` stayed
    unset so no third-party script loaded; both servers were stopped afterwards.

### Constraints and gotchas the later slices must not rediscover

- **The cards never left the Claude Design project.** `build-prompt.md` + `docs/current/frontend.md`
  + the grounding pack are the *whole* source of truth an executor gets. Do not go looking for
  `landing/*.html` in this repo — it is not here, and its absence is not permission to improvise.
- **The binary assets are in the repo now, and they came from outside it** (`frontend` v0002 Open
  Questions, closed by the operator's 2026-08-22 export): `frontend/public/assets/` holds
  `mijual-wordmark-{charcoal,white}.png`, `mijual-logo-ring-{charcoal,white}.png` and
  `fonts/PretendardVariable.woff2`, copied byte-for-byte and checksummed in that directory's README.
  `fonts.css` self-hosts Pretendard from `../assets/fonts/PretendardVariable.woff2` and pulls IBM Plex
  Mono from the Google Fonts CDN. **No slice may invent, generate, re-encode or placehold one of
  these** — they are design-project output, so a replacement is a new export, never a local edit, and
  a slice needing an asset that is not here renders the real file or nothing. There is still **no SVG
  wordmark** and no favicon-scale mark beyond the ring logo.
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
- **Browser-check the frontend over `http://localhost:3000`, not `http://127.0.0.1:3000`** —
  Next 16's dev-origin protection 403s two client chunks for a foreign host, hydration never
  completes, and the check silently measures an un-hydrated page (`P5.S11` note 12). A
  `npm run build && npm run start` pass is the second opinion.
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
- (`P5.S5`) **`data`** — the 정정 pairing rule is now **identity-scoped**: a 본문 `<CORRECTION>`
  최초제출일 that names no event of the corp is read as skew (own filing's `rcept_no[:8]`/`rcept_dt`,
  or ±7 days of the event's key — nothing moves), as the corp's own event one 접수일 away (unique
  within ±1 day — the version is **reattached**), or as a foreign document (the version is **split**
  onto a chain head keyed on the declared date). New suppression reason
  **`foreign_correction_head`** + review flag `hint_foreign_split` + `hint_status` value **`split`**
  (sticky, counts as `pairing_is_resolved`); an event whose every version left is relabelled
  `superseded_by_pairing`; and `collect.persist` will not re-place a `rcept_no` whose identity a hint
  has settled elsewhere — it stores that run's snapshots on the owning version instead. Corpus effect: 49 versions re-parented (0 added, 0 removed), **+14 suppressed
  chain heads**, exposable **488 = 50/422/16 unchanged**, ② withdrawn 8 → 6.
  **`qa`** — the *Known Fragile Areas* row "② 정정 filings paired to the wrong 사채 → deferred **D1**"
  **closes**: ② gate failures on exposable events 6 → 1 (the survivor is 에이럭스
  `20250908000110` `span_unresolved`, a citation defect). New invariant worth stating there: **0**
  extraction rows on any of the 488 exposable events cite a filing their event does not hold. D2's
  row stays — its two `hint_duplicate` events are the only foreign-hint versions left on a renderable
  event, and that defect is a duplicate record, not a foreign document. Suite baseline 87 → **89
  tests**, still ~1.2 s, no network/model/DB. **`operations`** — the repair sequence after any
  collection is **`bodydoc backfill` → `gates run` → `estimate snapshot`**, all offline (0 requests,
  0 model calls); the backfill converges in two passes and is a no-op from the third. Caveat:
  `ensure_event` bumps `last_seen_at`, so an offline repair moves the landing's 기준시각
  (`max(last_seen_at)`) without any OpenDART call.
- (`P5.S6`) **`data`** — the field model gains its **11th field and its first stored `본문-label`
  field**: ③ **`appraisal_price` (매수예정가격)**, read deterministically from 본문
  `13. 주식매수청구권에 관한 사항 → 매수예정가격` (present in **95/95** stored ③ 본문; never twice, so
  there is no per-주식종류 split) and stored in the same `Extraction` row shape as an LLM field, with
  `call_id`/`model` **NULL** — which is how a report tells a free reading from a paid one. New
  registry `mijual.extract.labelfields.LABEL_SPECS` beside §7's `FIELDS`, and
  `bodydoc.LABEL_FIELDS` gains ③'s label block (`주식매수청구권에관한사항 → appraisal_rights`, eight
  qualified sub-rows). Its **gate** is a §7-shaped two-witness rule — 본문 cell **==** API
  `aprskh_plnprc`, measured agreeing **17/17, 0 mismatches** — with three new reason codes
  (`appraisal_price_mismatch` · `_quote_mismatch` · `_out_of_range`); an empty cell is **`absent`**,
  never 0 and never a null, and there is **no `추후결정` case** for this field. Corpus effect:
  extraction rows **649 → 710** (+61: 47 passed / 14 not_evaluable / 0 failed), exposable
  **488 = 50/422/16 unchanged**. **`api`** — a ③ detail payload now carries
  `fields.appraisal_price` = `{value: {price: <int 원>}, quote, span, rcept_no, korean_name:
  "매수예정가격", display: "value", estimated: false}` on **12 of the 16** exposable ③ events; the
  other 4 carry **no key** (a field the filing does not state is absent from the payload, the same
  contract-wide rule as every blocked field). The 정정 story's `field_moves` now covers label fields,
  so a revised 매수예정가격 is visible in the CorrectionStory. **`architecture`** — layer 1 now has
  **two halves**: the paid schema-based reader (`mijual.extract.runner`) and the free deterministic
  one (`mijual.extract.labelfields`), which writes the same rows and is therefore invisible to the
  gate layer, the exposure contract and the presentation contract. The free half runs **first in the
  `extract` pipeline stage and outside `extract_max_calls`** — a pass that spends nothing is never
  budgeted. **`operations`** — new command `python -m mijual.extract labels [--rights R3]` (0 calls,
  0 requests, ~1.4 s over ③, idempotent); the re-derivation order is **`extract labels` →
  `gates run`**, because `upsert_extraction` clears the gate verdict on every write. Caveat that
  **widens `P5.S5`'s**: `Event.last_seen_at` is `onupdate=utcnow` and `gates run` writes every event,
  so the landing's 기준시각 is reset to "now" by **any** gate run, not only by a collect — a freshness
  signal that an offline maintenance job resets cannot by itself alert that the collector stopped.
  **`decisions`** — **D-15's backing has landed**, and the worked example carries a second lesson
  worth recording beside it: the design implied data that did not exist, and building the backing
  meant **measuring which tier the value lives in first** — it turned out to be deterministic in two
  places, so the honest build cost **0 calls and ▷ $0.0000** rather than the re-extraction the plan
  assumed. **`qa`** — suite baseline 89 → **91 tests**, still ~1.3 s, no network/model/DB (one reader
  test, one gate test); new corpus invariants: **47/47** label citations resolve *and* verify (0
  unresolved, 0 fall-backs), **12/12** served ③ citations re-slice to their quote and their value,
  all **16/16** exposable ③ pages answer 200, and every pre-existing gate distribution and landing
  number is byte-identical before → after.

- (`P5.S20`) **`data`** — the stored citation model gains **multi-part evidence**:
  `estimate.perf.Cited` carries `parts` (one `{raw, span}` per contributing cell) for a figure
  the filer printed as a **sum of table rows**, and `performance_report.facts` therefore gains
  an optional `parts` list on such a figure. Additive and byte-compatible — the key appears
  only on a real sum, so every single-cell figure serializes exactly as before, and
  `performance_report.lapse` is unchanged (it carries values, not citations). Corpus effect:
  **7 figures in 4 filings** (에스에너지 · 루닛 · SKC · 한화솔루션 — each a
  한국예탁결제원 + 직접청약 two-row 청약), **0 of 269 stored figures now uncitable** (was 7),
  all 14 spans re-slice to their cells. **`api`** — the contract-wide citation rule is now
  stated and structural: a served value carries **either** `quote` + `span` (one cell)
  **or** `parts` (≥ 2, each `{quote, span}`, summing exactly to `value`) **or** neither
  (no chip; `rcept_no` still links to DART) — `present.Figure` refuses every other
  combination, so a one-addend quote posing as the whole number is unconstructable. Live on
  `lapse_result.warrants_exercised` for the four filers, the landing's own 한화솔루션 example
  included. **`backend`** — `perf.CitedPart` / `Cited.citations` / `_cited_sum` (the Ⅶ
  청약내역 branch keeps **all** contributing cells, not the first), `present.QuotePart`,
  `present.money._backing_parts`, and `estimate.runner.reparse_performance`. **`operations`**
  — new offline command **`python -m mijual.estimate reparse`** (0 requests, 0 model calls,
  idempotent, ~4 s over 69 reports) which re-reads every stored 실적보고서 from its own
  `payload_bytes` and rewrites only the parse-derived columns; the re-derivation order after
  any collection becomes **`bodydoc backfill` → `gates run` → `estimate reparse` →
  `estimate snapshot`**. It is the general answer to "a parser change must reach the corpus
  without spending a request". **`qa`** — the *Known Fragile Areas* row "값은 두 행의 합인데
  인용은 한 행 → deferred **D4**" **closes**: 7 → 0 uncitable 실적보고서 figures, 7 multi-part
  citations all verifying, and the evalset's 실적보고서 rows now show the grader every addend
  instead of the first one (sampling unaffected). Suite baseline 91 → **93 tests**, still
  ~1.2 s, no network/model/DB; the landing/board/stock numbers were re-measured after the
  re-derivation and are byte-identical (718.1억/548.7억 · 51,253,956/365,527,824 · 0.1402 ·
  488 = 50/422/16 · 33 · 57 · 4 · 15 · 69 · 퓨쳐켐 2026-09-04), with `estimate report`
  diffing empty line for line.

- (`P5.S7`) **`security`** — the R5 auth model is **implemented**, and the four
  apply-phase questions it left open are decided: session = a **server-side row**
  (`auth_session`) behind cookie **`mj_session`** (`HttpOnly` · `SameSite=Lax` · `Path=/`
  · `Secure` from `MIJUAL_COOKIE_SECURE`, **30 days absolute, never extended on a read**),
  ops cookie reserved as **`mj_ops`**; **CSRF = `SameSite=Lax` + a required
  `X-Mijual-CSRF` header on every unsafe method, enforced service-wide** (a cross-origin
  page cannot set it without a CORS preflight this service does not grant); password
  storage = **stdlib `hashlib.scrypt` `n=2**14,r=8,p=1`**, parameters carried inside the
  hash so an upgrade re-hashes at the next login; the "reader session signing key"
  (`MIJUAL_SESSION_SECRET`) **keys the stored token digest** rather than signing a cookie,
  so a database dump holds nothing replayable, and rotating it logs every reader out.
  Stored PII is exactly **email + password hash** (+ created/updated timestamps): no
  admin flag, no activity trail, and no column that could join an account to a
  conversation — the schema-level no-join promise is intact because there is nothing to
  join. A login failure is **one code for both causes** (and the miss path burns a scrypt
  verification so the timing matches); a reset request answers identically whether or not
  the address exists and the link travels **only** through the mailer. 계정 삭제 wipes the
  row immediately and the cascade takes sessions and reset grants with it. The checklist's
  "Implement: password hashing, session cookies, … the no-join schema" line is now half
  done (the constant-time admin failure is `P5.S9`'s). **`decisions`** — three stated
  decisions worth their own record: session-as-a-row (immediacy beats statelessness when
  the request path loads the account anyway), scrypt's parameters chosen at **OpenSSL's
  default `maxmem` ceiling** (a parameter that only works with a private knob turned up is
  a login endpoint one deployment away from raising), and **a 30-day absolute session
  because a sliding one would have to write on a `GET`**. **`api`** — seven auth
  endpoints (`POST /auth/signup` 201 · `/auth/login` · `/auth/logout` ·
  `GET /auth/me` · `POST /auth/reset/request` · `/auth/reset/confirm` ·
  `DELETE /auth/account`), their structural codes (`email_taken` 409 ·
  `invalid_credentials` 401 · `password_too_short` · `invalid_email` ·
  `invalid_reset_token` 400 · `unauthenticated` 401 · `csrf_required` 403, **none carrying
  Korean** — the single body line is the client's), the account payload
  `{email, created_at}`, and two contract-wide statements: **anonymous is a result, not a
  401** (`GET /auth/me` → `{"authenticated": false}`, the same shape as `P5.S4`'s search
  miss) and **every unsafe request must carry `X-Mijual-CSRF`**. **`backend`** — the HTTP
  layer gained its first writes: `mijual.web.deps.WriteSession` (commits on success, rolls
  back on any exception, and **refuses a safe method outright**, so "a GET never writes"
  is now enforced from both ends), `mijual.web.auth` (accounts · sessions · reset grants ·
  the `ReadAccount`/`WriteAccount` gates), `mijual.web.passwords` (scrypt, versioned
  parameters, `needs_rehash`), `mijual.web.csrf`, `mijual.web.routers.auth`, and
  **`mijual.mail`** — the mailer seam (`Message(to, kind, data)` carries **data, not
  rendered copy**, because a Korean subject line would be invented product copy) with a
  `ConsoleMailer` dev transport; `create_app(settings, mailer=…)` is where P4 plugs the
  real one in. **Still no new dependency** — `pyproject` is untouched. Three new settings:
  `MIJUAL_SESSION_SECRET` · `MIJUAL_COOKIE_SECURE` · `MIJUAL_APP_BASE_URL`. **`data`** —
  three new tables via `create_all` (no Alembic): **`account`** (`email` unique +
  NFKC/case-folded whole address, `password_hash`, `created_at` = 가입일, `updated_at`),
  **`auth_session`** (a **digest** of the cookie token, `expires_at`; no IP, no user
  agent, no last-used column — updating one would make an authenticated GET write) and
  **`password_reset`** (single-use `used_at`, 1-hour `expires_at`). Both hang off
  `account.id` with `ondelete="CASCADE"` **and** an ORM `cascade="all, delete-orphan"`,
  which is the seam `P5.S8`'s holdings use. **`operations`** — the serving process creates
  no schema at startup (it must answer while Postgres is down), so the auth tables land
  through any pipeline entry point's `create_all` + `ensure_columns`, or the explicit
  one-liner in `P5.S7`'s `result.md`; **P4 must set `MIJUAL_COOKIE_SECURE` and
  `MIJUAL_SESSION_SECRET`** (unset = unkeyed digests plus one log warning, a development
  state) and implement the real `Mailer`. No rate limiting was added: it needs shared
  state P4 owns and `security` already says it has no UI copy. **`qa`** — suite baseline
  93 → **99 tests**, ~1.6 s (scrypt is the extra 0.4 s), still no network/model/DB; the
  flow was additionally curl-verified against live Postgres end to end (CSRF refusal
  writes no row · identical 401 bodies for both login failures · identical reset-request
  responses with the link only in the server log · single-use token · cascade delete
  leaving `accounts/sessions/resets = 0/0/0`), and the anonymous surfaces
  (`/board`, `/board/summary`, `/stocks`) still answer 200 uncookied.

- (`P5.S8`) **`api`** — 내 포트폴리오 is now a contract, and it is the product's **only gated
  surface**: `GET /portfolio` (one read: `holdings` — each with its 진행 중인 권리 요약 —
  plus **`upcoming` / `past`**, the two sections R5 signs, and the KST `reference` day),
  `POST /portfolio/holdings` (201) · `PATCH|DELETE /portfolio/holdings/{id}` ·
  `PUT|DELETE /portfolio/claims/{rcept_no}` (챙긴 돈 check/uncheck) ·
  `GET|PUT /portfolio/notifications` · **`GET /portfolio/sample`, anonymous and read-only**,
  and `PATCH /auth/account` (수신 주소 = the account email). Contract-wide statements worth
  their own lines: **the portfolio serves factors, never products** — the server knows the
  holding count and still ships only 배정비율/증서 1주 이론가치/초과청약 비율, so there is exactly
  one multiplication site in the product and 조회 and 포트폴리오 cannot disagree (verified: the
  한화솔루션 `lapse` block is byte-identical to `/stocks`'s, and 500주 → 679,575원 exists
  nowhere in the payload); **a ②/③ portfolio row carries no won amount at all**, which is why
  the row loads `STOCK_FIELDS` and not `appraisal_price` (that is R3's detail-page field);
  **an open ② is in `upcoming`, never in `past`**, because "지나간" is the 종료 label
  `ui-traps` #5 forbids; **`claimed` is absent, never `false`, when there is no account**; and
  **a stranger's row is a 404, not a 403**. New structural codes: `holding_exists` 409 ·
  `invalid_shares` · `invalid_lead_days` 400. **`data`** — three new tables via `create_all`
  (no Alembic), all hanging off `account.id` with `ondelete="CASCADE"` **and** an ORM
  `cascade="all, delete-orphan"`: **`holding`** (`corp_code` + `shares` `BigInteger`, unique
  per account+corp, `shares > 0`; **deliberately no FK to `corp`** — the corp table is
  re-collectable pipeline data and a reader's portfolio must survive a rebuild, so the
  reference is validated on write instead), **`notification_pref`** (`lead_days` JSON only —
  **no address column**, because the 수신 주소 *is* the account email, and **no KakaoTalk
  column**, because that row renders a 「예정」 chip and no working control) and
  **`lapse_claim`** (`account_id` + the 증권발행실적보고서's `rcept_no`, **and no amount**).
  The claim key is the 실적보고서's number on purpose: a 유상증자결정's `rcept_no` mutates (N2)
  and an `event.id` does not survive a rebuild or a `P5.S5` re-parenting. **`security`** — the
  R5 personalization layer's boundaries are implemented: 내 포트폴리오 is the only gated surface
  and every other route still answers 200 uncookied (verified); **no anonymous write endpoint
  exists at all**, so "anonymous state never reaches the server / migration is offered, never
  automatic" is structural — the 세션 이월 and 샘플 이전 flows are client offers that produce
  ordinary authenticated writes; a 챙긴 돈 mark is a **user assertion** that stores no amount
  and reaches no aggregate (the payload has none); the **sample carries no account fact** —
  no address, no 알림 설정, no `claimed` key, no fake identity; 계정 삭제 now cascades holdings,
  claims and preferences too (verified 0/0/0/0/0/0 in Postgres). One nuance the checklist
  should carry: **수신 주소 변경 (`PATCH /auth/account`) takes the session and no password** —
  R5's Notify row has no re-auth control and `P5.S7`'s 계정 삭제 set the precedent, so a live
  stolen session can move the address; adding a password prompt would be a **design** change
  (see Open Questions). **`backend`** — `mijual.web.portfolio` (the decisions: holdings CRUD,
  claims, 시점 칩 validation, the sample composition) + `mijual.web.routers.portfolio`
  (transport) + `mijual.web.auth.change_email`; `reads` gains `HoldingEntry` /
  `load_portfolio` and the factored-out `_events_for_corps` / `_load_views`, which
  `load_stock` now shares — one batched reading and one derivation for both surfaces, so a
  portfolio row *is* the 조회 row plus `shares`. Still **no new dependency**. **`product`** —
  the 알림 boundary as built: preferences persist (시점 칩 7/3/1/0, default **7일+1일**, an
  **empty selection is a valid "no mail"** because R5's mail footer promises an off switch and
  deselecting every chip is the only one the signed surface has), and **nothing sends** — the
  channel, schedule and body are P4's. An absent preference row means the default, not "off".
  **`qa`** — suite baseline 99 → **104 tests**, 1.87 s, still no network/model/DB; the surface
  was additionally curl-verified against live Postgres (owner-scoping 404s · CSRF refusal
  before the route · the 한화솔루션 500주 basis reproducing R5-4's own 679,575원 from factors
  only · the anonymous sample at 18.2 KB/25 ms with no `@` in the body · cascade delete). New
  measured invariants: **32/32** stored `lapse` rows sit inside the 조회 coverage window (so the
  portfolio's 소멸 rows are exactly 조회's), **0** carry a `NULL` `event_id`, and **2 of 32**
  hang off a *flagged* event and therefore have no 지나간 마감 row (한솔테크닉스, 트리니티항공).
  All four R5-4 pinned filings still resolve to the events R5 named; the sample renders **5
  rows, not 4**, because 대동기어 also holds an exposable ① that lapsed (D+45, 33.4억원) — live
  data, not a design deviation.

- (`P5.S9`) **`security`** — the R7 §6.4 operator door is **implemented**, and its half of
  the checklist line "constant-time admin failure" closes: a **separate credential from the
  environment** (`MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD`, masked in `Settings.__repr__`),
  with **no operator account row, no admin flag, no signup and no reset** — and therefore
  nothing to join to a reader account. Session = its own **`ops_session`** row keyed by the
  same peppered digest as the reader's, carrying **no `account_id`, no FK and no operator
  identifier at all**, behind cookie **`mj_ops`** (`HttpOnly` · `SameSite=Lax` · `Path=/` ·
  `Secure` from `MIJUAL_COOKIE_SECURE`), **12 hours absolute, never extended on a read** —
  shorter than the reader's 30 days because an operator console should not still be open the
  next morning. **The failure is uniform in body *and* in cost for three causes, not two**:
  unknown ID, wrong password, and *no credential configured* return byte-identical 401
  bodies, the ID goes through `hmac.compare_digest`, both checks are always evaluated (no
  short-circuit, which would leak existence in the timing), and every path spends exactly one
  scrypt verification. Expiry answers **401 `ops_unauthenticated`** so the client returns to
  the door and restores the tab. Attempt limiting stays **P4**'s (cross-process state, no UI
  copy). The panel's read-only property is now structural: **nine of eleven ops routes are
  `GET`** and the two `POST`s touch only the operator's own session row — a test asserts the
  documented OpenAPI surface carries no other unsafe method under `/ops`, and that no reader
  payload mentions the path. The 계정↔대화 no-join promise is likewise structural in the
  serving layer: `/ops/users` is **two independent reads** and no query touches both. One
  honest gap worth the checklist: R7's **샘플 로드 여부** column has no server-side fact (see
  Open Questions) and is served as an **absent key**, never a `false`. **`operations`** — the
  scheduled pipeline gains **two offline stages, `reparse` and `snapshot`**
  (`STAGES = collect → bodydoc → extract → gates → reparse → snapshot`, 0 requests / 0 model
  calls), which closes `P5.S3`'s standing caveat that the serving precomputation was
  hand-run and could age silently while 기준시각 said the corpus was fresh; and **every run
  now writes itself down** (`pipeline_run`, opened before the first stage and closed after
  the last, so an in-flight or crashed run is visible as a row with no `finished_at`, while a
  **skipped** run writes none). The **beat schedule and the run-lock key now have exactly one
  declaration** (`mijual.beat`), read by both the Celery app and the ops panel, so the panel
  can never render a schedule the worker is not running. New CLI flags
  `--trigger` / `--no-run-log`; new dev settings `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD`
  (deploy-time issuance and the concrete route stay P4's). Redis is **optional at request
  time**: the lock chip degrades to `state: "unknown"` with a reason and the tab still
  answers 200. **`api`** — 운영 관제 is now a contract: eleven `/ops` routes (door ·
  개요 · 게이트 대기열 + 행 검사 · 정확도·비용 · 대화 로그 · 익명 세션 · 피드백 · 사용자),
  **operator-only**, and contract-wide statements worth their own lines: **every number is
  re-read from the source that already owns it** (the 개요 tiles reproduce `gates summary`
  byte for byte; the 정확도 block ships `mijual.evalset report`'s **exact markdown** beside a
  structured mirror derived from the same object); **a reason/suppression code travels raw
  English and carries `reason_ko` only when the gate layer itself owns that Korean** — never
  a fallback phrase; **`▷` is served verbatim and never becomes 「추정」** inside this panel
  (the boundary is the source); **every rate ships its own denominator** — gate-queue counts
  are over stored rows while rates are over **distinct `(rcept_no, field_key)`**, both served
  with `basis`, and each accuracy rate carries its n, interval and corpus denominator; and
  **spend windows are labelled** (LLM `cumulative` with `since`/`until`, OpenDART `daily`
  against the operator-stated 20,000/day). A blocked gate row omits `quote`/`span` entirely.
  **`data`** — two new tables via `create_all` (additive, no Alembic): **`ops_session`**
  (token digest + expiry, **no relation to any other table** — the no-join promise as schema)
  and **`pipeline_run`** (one row per run: label · trigger · started/finished · seconds ·
  window · config line · lock kind · ok · requests · calls · ▷ cost · the run's **verbatim**
  spend line · per-stage `StageResult` JSON · notes). **P5 creates no conversation table**:
  the 대화 로그 / 익명 세션 / 피드백 tabs read a storage-agnostic port whose P5 implementation
  returns empty pages, so the schema-level 계정↔대화 absence stays trivially intact and P6
  owns the storage. **`backend`** — `mijual.beat` (the Celery-free beat + lock-key
  declaration both the worker and the panel read), `mijual.web.ops` (the door),
  `mijual.web.opsreads` (every ops number), `mijual.web.conversations` (the P6 port, wired
  through `create_app(conversations=…)` exactly like the mailer seam),
  `mijual.web.routers.ops`; `mijual.scheduler.pipeline` gains `stage_reparse` /
  `stage_snapshot` / `open_run_row` / `close_run_row` and `PipelineResult.spend_line` (a
  property, so the printed line and the stored one cannot drift); `auth._new_token` became
  public `auth.new_token` (one definition of "unguessable" for both credentials). **Still no
  new dependency** — `pyproject` untouched. **`architecture`** — the request-path boundary
  held under a surface that legitimately needs pipeline configuration: rather than importing
  `mijual.scheduler` (which pulls `collect`/`extract`/`dart`) or `mijual.evalset` as it was
  (which pulled `extract`), both were fixed **by moving, not forking** — the beat/lock
  declaration moved down into a stdlib-only `mijual.beat`, and `evalset/sample.py`'s two
  extractor imports moved into the corpus-*draw* functions that own them, leaving the
  frozen-artifact half pure. Measured after: `import mijual.web.app` still pulls **none** of
  `dart`/`collect`/`extract`/`estimate`/`scheduler`/`evalset`, and no Celery. **`decisions`**
  — three worth recording: the ops session is **12 hours absolute** (a working day, not the
  reader's 30) because an operator console should not outlive the shift; the run log's
  **start-then-close** write is what makes a crashed run visible *and* gives the lock chip an
  honest 시작 시각 (the Redis lock holds an owner token and no start time, so deriving one
  from the TTL would be an invented number); and the OpenDART quota bar's denominator is
  served with its **provenance** (`operator (decisions O-1)`) because 20,000/day is an
  operator statement, not something this service can measure. **`qa`** — suite baseline 104 →
  **113 tests**, 2.49 s, still no network/model/DB; new cases cover the door's three-way
  uniform failure (byte-identical bodies), both cookie-rejection directions, the ops surface
  carrying no mutation route (asserted over the OpenAPI paths) and no reader payload
  mentioning it, the port's honest zeros, the distinct-basis rate arithmetic, the beat
  declaration's Celery-vs-Python weekday mapping, and a run-log round trip including the
  ▷ line and the skipped-run-writes-nothing rule. Live cross-checks: 개요 reproduces
  `gates summary` exactly (628 considered / 488 exposable / 418 renderable, 추후결정 2+2) and
  정확도's markdown equals `evalset report`'s output **byte for byte** (98.6% · 213/216 ·
  과차단 100% 19/19 · 재현율 88.7%, `judged_by` present). New measured constant: the
  gate-queue basis is now **710 stored rows / 691 distinct / 19 duplicates** (was 649/633/16
  — the 61 `appraisal_price` label rows from `P5.S6`).

- (`P5.S10`) **`frontend`** — the doc's own "**No frontend code exists yet**" opening is
  obsolete: `frontend/` is a Next.js **16.3.2** app (App Router, Turbopack) on React
  **19.2.8** + TypeScript **5.9.3** with **no UI library, no CSS framework and no test
  framework** — the design system is `tokens.css`, and a framework theme would be a second
  source of truth for R1's decisions. Durable additions: the app layout (`app/` ·
  `components/` · `lib/` · `public/foundations/`); **`tokens.css` and `fonts.css` are
  vendored byte-verbatim from the landed records into `public/foundations/`, served rather
  than bundled, and read-only** — the directory mirrors the design project's own
  `foundations/` + `assets/`, so `fonts.css`'s relative font path needed **no edit at all**;
  the `.cosmos` page shell (`<html lang="ko" class="cosmos">`, body `--paper`, the 1120px
  content column, 480/768/1120, the `.mono` numeral rule and the 2px focus ring); the
  **reduced-motion convention every later slice uses** (`data-motion="tick"` freezes,
  `data-motion="ambient"` hides, everything else cuts, plus `useReducedMotion()` for a tick
  that must stop re-rendering); and the **seven R1/R2 trust primitives** as faithful
  implementations — `EstimateMarker` (「추정」, `▷` retired), `Citation` (`[근거]` → inset
  panel, verbatim quote, **multi-part rendered part-by-part**, scroll > 180px, the DART
  link), `StateBadge` (추후결정 · 철회 per-type locked notice · 발행사 기재 불일치, **and no
  variant for a gate-blocked field**), `DDay` (mono 600 fixed 17px, colour-only urgency,
  upstream values only), `RightsChip`, the 소멸주의보 strip (R1 + R2's craft/hazard form) and
  the craft panel. Two readings of the record are now stated as durable truth: the estimate
  tag renders **추정** (the 「」 are the record's quoting notation; the border is the
  enclosure — unlike `[근거]`, whose brackets are literal), and a past **`D+n` is faint,
  never alert** (R3/R4/R5 all say so; R1 only said "unfilled"). The Open Question "binary
  assets live in the design project" is **closed**: the operator exported all five on
  **2026-08-22** and they are in the repo byte-for-byte under `frontend/public/assets/` —
  `fonts/PretendardVariable.woff2` (WOFF2, variable `wght 45–920`),
  `mijual-wordmark-{charcoal,white}.png` (1788×324 RGBA) and
  `mijual-logo-ring-{charcoal,white}.png` (2178×346 RGBA), checksummed in that directory's
  README; Pretendard is verified **loading and drawing** in a real headless Chrome, and
  nothing anywhere is substituted, generated or placeheld. The white wordmark's filename —
  described but never named in the landed record — is **`mijual-wordmark-white.png`**, and
  that is the name `P5.S11` wires. The doc's other two Open Questions narrow: **data fetching is a typed
  `fetch` wrapper** (`lib/api.ts`, no client library) and the **rendering strategy is per
  surface**, still open — but the API seam is decided (below). **`architecture`** — the
  frontend/API boundary is a **same-origin rewrite**: the browser talks only to the Next
  origin and `next.config.ts` proxies `/api/*` to `MIJUAL_API_ORIGIN`, so `P5.S1` note 7's
  CORS question is answered by **not having a cross origin** — the service keeps no CORS
  middleware and grants no preflight, which is what `P5.S7`'s CSRF rule depends on, and the
  session cookie needs no `SameSite=None`. **`api`** — nothing new on the wire; the contract
  now has a typed client-side mirror whose rules are structural (an absent key is an optional
  field, `| null` only where the server truly emits null, money/ratios stay **strings**, and
  `estimated` is required on every value — `EstimateMarker` refuses to render without it, as
  `present.Figure` refuses to construct). **`operations`** — `cd frontend && npm run dev`
  (http://127.0.0.1:3000) is documented in `compose.yaml`'s header beside the uvicorn line;
  like the API it is deliberately **not** a compose service, and P4 owns its deployment
  (repointing `MIJUAL_API_ORIGIN` is an env change, not a code change). Exporting the
  wordmark/ring PNGs and `PretendardVariable.woff2` out of the Claude Design project was an
  **operator step, and it is done** (2026-08-22) — the five files are checked in and
  checksummed; because they are the design project's own output, replacing one means a new
  export from there, never a local edit or a re-compression. **`decisions`** —
  three worth recording: the frontend reaches the API through a **same-origin proxy rather
  than CORS** (a cross-origin setup would have weakened a landed security decision to save a
  proxy line); the 「추정」 mark **renders 추정**; and a past `D+n` renders **faint, never in
  the expiring/lost hue**, which is also what keeps an open ② from reading as 종료. **`qa`** —
  the frontend has its own check and it is deliberately framework-free: `npm run build`
  (prerenders the proof page through the shell and every primitive, so a broken component
  fails the build) + `npm run typecheck` (`tsc --noEmit`) + `npm run smoke`
  (`node --test lib/*.test.ts`, **3 cases**, ~75 ms, no jest/vitest/jsdom, no fixtures) —
  covering the CSRF header on a mutation and not on a read, `credentials: include`, and the
  error envelope becoming an `ApiError`. The Python suite is **untouched at 113**; this slice
  edited no Python file and added no Python dependency.

- (`P5.S11`) **`frontend`** — the **global chrome** R2 designs is built and is durable
  frontend truth: `components/chrome/` (nav · mobile top bar + sheet · footer · vocky
  triggers · the script seam), wrapped around every route by the root layout, with the 52px
  transparent bar over the cosmos, the three **signed** slots rendering their *superseded*
  labels (내 종목 조회 · 관제 현황판 · **AI 질문**, R4/R6 over R2's provisional literals), the
  active state as 600 + a 2px #fff underline, the quiet 로그인 slot, the ≤480px sheet (rows
  ≥48px, R5's 구분선, a 200ms close that becomes a **cut** under reduced motion) and the
  white-on-dark footer (ring wordmark h 17 + the locked positioning line in mono 11, the three
  signed sentences, the mono 11 bottom hairline row). Three durable rules land with it: the
  **wordmark is the delivered `mijual-logo-ring-white.png` rendered height-constrained through
  a plain `<img>`** — never `next/image`, which would ship a re-compressed derivative of an
  asset that is never re-encoded; the **gate-cost sentence's `▷` is gone and its 49.2억원
  carries the 「추정」 tag**, the footer being its only placement; and **nothing in the chrome
  is `position: fixed`** — no floating button, bottom-right corner clear for P6's launcher.
  Two open fidelity readings for the record: the 「추정」 tag inside a 12px sentence renders
  **6.72px** (the primitive's `0.56em`) against R2's landing literal of 10px, and the
  positioning line/bottom row are Korean **in mono** by the round's own spec. The doc's Open
  Question "concrete route paths were left to the build" is **answered for the reader
  surfaces**: `/` 관제 현황판 · `/stocks` 내 종목 조회 · `/ask` AI 질문 (P6's surface, shipped
  as a bare shell) · `/auth/login` 로그인 (`/auth/reset` is already fixed by the backend) ·
  `/ops` unchanged; one module, `lib/routes.ts`, states each path once. **`api`** — nothing
  new on the wire; the chrome calls no endpoint at all (`GET /auth/me` stays `P5.S16`'s
  decision, so no surface pays for a session probe on every page load). **`operations`** —
  one new frontend setting, **`NEXT_PUBLIC_VOCKY_SRC`**: vocky's script URL is external and in
  no record, so it is configuration, loaded once through `next/script` in the shell, and
  **unset means no script tag while the three `data-vocky-trigger` elements still render**;
  `NEXT_PUBLIC_*` is inlined at build time, so P4 sets it *before* building. Also worth the
  runbook: browser checks must use `http://localhost:3000` — Next 16's dev-origin protection
  403s two client chunks for a foreign host and hydration silently never completes.
  **`qa`** — the frontend's framework-free check now covers four prerendered routes
  (`/`, `/_not-found`, `/ask`, `/stocks`); `npm run build` + `typecheck` + `smoke` (3 cases)
  all green, the Python suite **untouched at 113**, and the chrome was verified in a **real
  headless Chrome** on both sides of the 480px breakpoint (nav 52px/transparent/hairline, the
  three labels and their moving active state, the wordmark at natural 2178×346 rendered 19px
  high, the three footer sentences byte-identical, three triggers with **zero** vocky script
  tags when the env is unset and **exactly one** when it is set — still one after a
  client-side navigation, the sheet's 48px rows and its 200ms-fade/reduced-motion-cut close,
  and zero `position: fixed` elements).

- (`P5.S12`) **`frontend`** — the **landing 관제 현황판** is built and is durable frontend truth:
  `components/landing/` (cosmos backdrop · hero · retrospective anchor · countdown · 소멸주의보 ·
  board) rendered by `app/page.tsx` as a **request-time** page (`connection()`, Next 16's
  replacement for the removed `dynamic` segment config) over one `/board/summary` + one `/board`
  read, so no number on the page is derived from anything else. Durable rules that land with it:
  the **cosmos backdrop fills `.backdrop`** with a starfield generated **once, deterministically**
  (seeded PRNG at module scope — `Math.random()` would be a hydration mismatch on every load; the
  mobile field is the first 160 of the same 240), the glows/rings state the record's geometry with
  token hues; **the hero owns the orbit rings and is given a height floor (680px desktop) so the
  full-size rings clear the nav and the first panel** — R2.1's "never shrink them, give the hero
  vertical room" as an outcome rather than as its stated padding; the **landing 「추정」 tag gets its
  10px from the surface** (`EstimateValue` puts the marker in a `--text-lg` context and the value
  keeps its own size) because R1 forbids the primitive to set its own size, and the primitive is
  untouched; **R2's board row anatomy is one component** shared by the board and both expanded
  strips; and the live-tick pattern is SSR-first value + `suppressHydrationWarning` +
  `useReducedMotion()` to **stop the interval**, since CSS cannot. New shared module **`lib/format.ts`**
  — `won()` mirrors `mijual.estimate.won` branch for branch over **exact decimal strings** (no
  `Number()` on money or a ratio, ever), plus `count` / `percent` / `kstStamp` (an instant is
  **sliced, never `Date`-parsed**, so a reader's timezone cannot move a KST stamp). Two readings of
  the record are stated as truth: the hero H1 renders the **superseded surface name 내 종목 조회**
  (R4-5 named the surface; R2's 내 종목 연결 survives only inside the footer's locked positioning
  sentence), and a **board row's corp name links to the event detail page** while the `↗` keeps
  DART (R3's crumb and its 추후결정 strip make the board the way in). `lib/routes.ts` gains
  `eventPath(rceptNo)`. **`experience`** — the reader's first surface as built, and what it refuses
  to state: every landing number is **live from one summary object**, so the hero's stat line, the
  value card, the stats card and the 소멸주의보 placard cannot disagree; a figure the payload omits
  produces **no phrase at all** (no zero, no dash) and an absent countdown instant produces no
  countdown; **no won amount appears on any board row** and a ① before 확정발행가 shows only the
  `발행가 확정 전` chip beside its 청약 마감; **staleness is served, never timed client-side** — the
  chip flips to the alert treatment with `· N시간 전 데이터` and an inset notice appears above the
  tabs while **the rows render identically** (stale-never-dark, verified); a 추후결정 row renders
  `StateBadge 추후결정` with **no date anywhere near it**; a past ② is the pinned **진행 중** strip
  with a faint `D+n`, never 종료; the tabs' counts are **whole-board** (488) while the page ranks
  450 rows, because past ①/③ belong to 조회 and the retrospective; and the hero's search is a plain
  **GET form to `/stocks?q=`**, so the product's entry point works before any JavaScript does.
  **`qa`** — the frontend check now covers the landing: `npm run build` (the landing is `ƒ` and
  needs no API to build) + `typecheck` + `smoke` (3 cases) all green, **Python suite untouched at
  113**, and the surface was verified in a **real headless Chrome on both sides of 480px and in
  both `next dev` and `next start`**, with an **empty production console** (no hydration warning).
  Measured invariants worth keeping: the rendered stat line equals `/board/summary` exactly; the
  countdown's own diff against the served `next_lapse.target` is **0 s off**; tab counts equal
  `counts` and filtering reproduces the endpoint's own `?rights=` populations (365 / 14 / 389);
  the strips equal `open_now.count` / `tbd.count`; under `prefers-reduced-motion` the countdown is
  **identical after 3 s** and twinkle/drift/orbit/colon are `animation: none` with the shooting-star
  layer `display: none`; and exactly **one** `position: fixed` element exists on the page.
- (`P5.S13`) **`frontend`** — the **event detail surface** R3 designs is built and is durable
  frontend truth: `app/events/[rcept_no]/page.tsx` is a **request-time** page (`connection()`) over
  one `/events/{rcept_no}` read, with `components/event/` as its component set (`EventDetail`
  composition · `Header` · `Fields` · `Offering` · `Convertible` · `Withdrawn` · `Corrections` ·
  `copy.ts` · one CSS module). Durable rules that land with it: **field labels come from the served
  `korean_name`** and the frontend keeps **no field-name table of its own**, so a field the API
  does not serve has no row, no marker and no explanation; `FieldValue` is the **one** renderer for
  a field's value and the CorrectionStory's 정정 전/후 columns reuse it, so a value can never be
  drawn two ways on one page; the **three-state citation** is rendered as served — a `parts` figure
  shows **every addend** and a figure with neither `quote` nor `parts` shows **no chip at all**,
  while a *difference* (발행 − 청약) is rendered as its own cited inputs rather than as parts;
  **money is never printed before 확정발행가** even where the payload carries `planned_price`
  (the `발행가 확정 전` chip and the due date replace it), while ratios render in both states and
  배정비율 keeps **all ten decimals** because R4 multiplies by it; and a **collapsed `Citation`
  still contributes its quote's width**, which is why a field row gives the chip its own grid area
  and the 환산 chain caps a step at 340px with its arrows as real flex items — a layout constraint
  any later surface embedding a citation inherits. `lib/routes.ts` gains **`stockPath(corpCode)`**:
  the 환산 CTA links to **`/stocks/{corp_code}`**, making the corp_code path segment (not a query
  param) the product's stable handle for 조회. Two record readings are stated as truth: the
  **CorrectionStory is an in-place disclosure rather than a route** (the product's only crumb points
  at the board), and **매수예정가 renders as an ordinary field row** under 발행 조건 — `P5.S6`'s
  contract addition superseding R3's "not rendered" line, using the signed row anatomy rather than
  a new layout. **`experience`** — the reader's event surface as built, and what it refuses to
  state: a 철회 event is a **notice plus its evidence and nothing else** (no fields, no countdown,
  no old dates); 추후결정 produces `StateBadge 추후결정` + "카운트다운 없음" with **no date anywhere
  near it**; a field the current version dropped says "현재 버전 공시에 없음" as a fact, never as an
  error; a past ② opening reads **진행 중**, never 종료; an `option_schedule` range appears **only**
  as the locked "연속 기간 아님" caption, never as a period or a bar; the **발행사 기재 불일치 block
  shows both readings, cites each into the same filing, and never reconciles them**, with the footer
  stating only which reading the totals use; the identity rule prints the DART master name and adds
  the locked 본문 표기 line **only** when the API says the body disagrees; the version rail marks
  **no** current-readable row when the event has no readable 본문, shows no `correction_kind` on a
  first filing (the value is the English token `original`), and carries **no** superseded-row reason
  because why a value is missing is operator truth, never reader truth; a **non-renderable
  `rcept_no` renders a not-found page that does not explain itself** — and no Korean 404 sentence
  was invented, so the one English string on the surface is the framework's, pending an operator
  decision. **`qa`** — the frontend check now covers the detail surface: `npm run build` (the page
  is `ƒ`) + `typecheck` + `smoke` all green, **Python suite untouched at 113**, and the surface was
  verified in a **real headless Chrome on both sides of 480px over `npm run start`** across
  **13 real pages covering every ①②③ state plus two 404s**. Measured invariants worth keeping: no
  `▷`, no `[object Object]`, no `undefined`/`NaN`/`null` and **no stray English token** on any of
  the 26 renders; **zero `position: fixed`** elements and **zero horizontal overflow at 390px**;
  every named mobile target exactly **44px** (DART link 308×44 full-width); a multi-part citation
  opens **both** addends summing to the printed value; and an unpriced ① shows **no 원 amount
  anywhere on the page**.

- (`P5.S14`) **`frontend`** — **내 종목 조회** (R4) is built and is durable frontend truth:
  `components/lookup/` over two **request-time** routes (`connection()`) — `app/stocks/page.tsx`
  (the search: `?q=` resolves through `GET /stocks?q=`, a hit **redirects onto**
  `/stocks/{corp_code}`, a miss stays put and renders the locked 검색 불일치 line) and
  `app/stocks/[corp_code]/page.tsx` (a resolved stock; an unknown code is a 404 that explains
  nothing). The **corp_code path is the product's stable handle for an issuer** while a query is the
  search's own vocabulary — `?q=`'s name is `q`, one word shared by the hero form, the page and the
  contract. Durable rules that land with it: **`lib/holding.ts` is the product's one N주
  multiplication site** — `convert(factors, shares)`, exact `BigInt` decimal arithmetic with **no
  `Number()` on money or a ratio**, ⌊N × 배정비율⌋ floored on the digits (`mijual.calc` governs),
  and **`value: null` when the factors carry no `unit_value`**, so money before 확정발행가 is
  *unconstructable* rather than merely unrendered; `OfferingInputs` and `LapseResult` satisfy its
  input type structurally, so **`P5.S16` imports it instead of writing a second one** (`P5.S8`
  note 1's requirement, discharged). Holdings live in **sessionStorage only**, one key
  `mijual.lookup.holdings` = `{v, entries:{corp_code:shares}, last:{corp_code,shares}}` — per
  issuer, so R5-3's 세션 이월 제안 reads the session in one go — with **the same stock restoring its
  own count and a different stock only ever *offered* one** ("이전 입력 {n}주"), never auto-filled
  and never sent anywhere. Three readings of the record are stated as truth: the coverage caption's
  start is **served** while `오늘` is the round's own word; the boundary panel renders **rights-type
  chips rather than the record's ①②** (R1's revision removed the numbering from the UI) with both
  dates off the wire; and the calc footer is **per breakdown row**, because offerings of one stock
  do not share a 배정비율. `lib/types.ts` gains `LapseBreakdownRow` (the 놓친 돈 row's served shape,
  `warrant_trading_period` + `issuer_disagreement` included). **`experience`** — the reader's
  conversion surface as built, and what it refuses to state: **no holding means no derived number**
  (an empty field is not a zero — the ① row shows its factors, the 놓친 돈 headline appears only
  once a count exists, and "사라진 가치 0원" is never printed); an unpriced ① shows `발행가 확정 전`
  + the due date and **no money anywhere**, while 배정 신주 and 초과청약 한도 still compute; a
  **②/③ row carries no per-holding amount** — ② carries R4's three dilution facts (오버행 % ·
  전환 시 주식수 · 전환가액, the same strip R5 calls ②'s substitute) and ③ the 2단계 dependency line
  with **no 매수예정가** — while an already-open ② reads **진행 중** and the word 종료 appears
  nowhere; a breakdown row carries **exactly one `Citation`** (the 매매기간 quote) and prints
  발행/청약 as words, so no summed 실적보고서 figure ever carries a chip; a row hanging off a
  *flagged* event keeps its 소멸 계산 and silently loses its 기간 line, quote and link; 발행사 기재
  불일치 rides onto the breakdown row in R3's own signed words, both readings cited, never
  reconciled; a **search miss is a result** and names no reason, candidate or near-miss; and a
  resolved stock with nothing to show states the watched 3종 and the live 감시 중 count instead of a
  zero. **`qa`** — the frontend check now covers 조회: `npm run build` (both routes `ƒ`) +
  `typecheck` + `smoke` (**3 → 6 `node:test` cases**, ~79 ms, still no jest/vitest/jsdom) all green,
  **Python suite untouched at 113**, and the surface was verified in a **real headless Chrome over
  `npm run start` and again in `next dev`** — 43 checks across 9 issuers × 2 viewports. Measured
  invariants worth keeping: **한화솔루션 500주 reproduces R4's own card client-side from factors
  only — 679,575원, 하한 545,181원, 배정 123주 × 5,525원** (and 1,000주 is exactly 2×), 계양전기
  500주 → 115주 / +23주 with **no `원` in the page body**, 대한광통신's two readings both cited and
  unreconciled, 코이즈's 놓친 돈 total **not double-counted** (one row, `offerings: 1` — D2's second
  trigger did **not** fire), the restore-chip flow offering rather than filling, and 390×844 with no
  horizontal overflow, every target ≥44px and **zero `position: fixed`** elements. Two pre-existing
  conditions were measured and left alone: Next's `/auth/login` prefetch 404 on **every** page until
  `P5.S15` lands, and the shared `Citation` chip/link sitting under the mobile 44px floor exactly as
  on R3's detail page.

- (`P5.S15`) **`frontend`** — R5's **auth surfaces and its two conversion touchpoints** are built
  and are durable frontend truth: `components/auth/` over two request-time routes —
  `app/auth/login/page.tsx` (R5-1's **one panel with two modes**, its 전환 링크, the four states,
  the 재설정 request and the permanent PII inset) and `app/auth/reset/page.tsx` (the page the
  emailed link lands on; **`?token=` is the backend's own link shape, not a path segment**, and a
  visit with no token redirects rather than rendering a sentence nobody signed). Durable rules
  that land with it: **확인 중 is the submit button's own text replaced + disabled**, with no
  spinner and no modal anywhere on the layer; **a failure renders one body line in body ink,
  never `--alert`** (that hue means expiring/lost, so an auth error may not spend it), mapped
  from `P5.S7`'s structural code by **`authErrorKo` — exactly three codes wide
  (`invalid_credentials` · `email_taken` · `password_too_short`) and `null` for everything
  else**, so an unsigned failure is never given words; the **8자 rule is stated client-side on
  계정 만들기 and the reset confirm but never on 로그인**, where a short password is simply
  wrong and the round's line is 불일치; and **the email input carries the service's own regex as
  its `pattern`**, so `invalid_email` — which has no signed Korean — is refused by the browser in
  the browser's copy instead (verified: `a@b` cannot be submitted and spends no request). The
  route map gains **`/portfolio`** (내 포트폴리오, the API's own noun and where a successful
  로그인 goes), **`samplePath()` = `/portfolio?sample=1`** — R5-4's sample is a *mode* of the
  layer, not a second surface — and **`portfolioAddPath()` = `/portfolio?add={corp_code}`** for
  the logged-in 담기 link, which navigates and **writes nothing**. New shared seam
  **`lib/session.ts` + `lib/session.server.ts` + `components/auth/useAuthState.ts`**: a client
  probe, a server read that forwards the request's own cookie, and a hook whose `null` (*not
  answered yet*) is deliberately distinct from `{authenticated:false}` so a two-state element
  never flashes the wrong state — plus the one-time flash channel that carries the
  **로그아웃되었습니다** message as a *kind*, never a stored sentence. **`experience`** — the
  reader's account surfaces as built, and what they refuse to state: a **login error never names
  a field** and a wrong password and an unknown address produce the byte-identical line
  (measured in the browser with `==`); a **재설정 request answers the same sentence whether or
  not the address has an account**, and the link travels only through the mailer; an
  **authenticated visit to the 로그인 page redirects to 내 포트폴리오** rather than inventing a
  logged-in variant of a screen the round draws four states for; the **PII statement is
  permanent on both auth pages** and renders the round's two signed lines with **no invented
  third**; R5-2's **offer panel appears only after a per-holding value has rendered** (asked of
  `lib/holding.ts`, the one multiplication site), **once per session**, dismissible, as the last
  block of the page in normal flow — it never covers the results, never gates, leaves the nav's
  로그인 quiet, and is **not shown to a reader who already has an account** (offering an account
  to an account holder is the 가짜 사용자 정체성 the round forbids); and the **detail one-liner**
  swaps 이 마감 알림 받기 → / 내 포트폴리오에 담기 → under the D-day **only where the deadline is
  still ahead**, because an alert for a passed anchor is a promise nothing can keep. Both signed
  **샘플 entries** render — the 로그인 page's bottom pair and the landing page's own footer line,
  which is a **landing element rather than chrome** (R5's "Footer 불변" is untouched).
  **`security`** — the R5 reader-auth *surface* now matches the model the doc records: the panel
  collects **email + password and nothing else**, the PII inset states that permanently on the
  auth screen (not as a link to a policy page), 가입 여부 is never disclosed by the 재설정 flow,
  the login failure names no field, the **reset token is never rendered** and leaves the app only
  in the confirm request's body, and **no anonymous surface was gated** — the conversion offers
  are an inline panel and a one-line link, with no modal, no interstitial and no highlighted nav.
  One consequence worth the checklist: the auth pages are the product's first surfaces that
  branch on a session, and they do it through one seam that **degrades to anonymous** on any
  probe failure. **`qa`** — the frontend check now covers the auth layer: `npm run build`
  (8 routes; `/auth/login` and `/auth/reset` both `ƒ`) + `typecheck` + `smoke` (**6 → 8**
  `node:test` cases, ~85 ms, still no jest/vitest/jsdom — the two new ones pin each signed line
  to the code that produces it **and** that every other code produces none) all green, the
  **Python suite untouched at 113**, and the layer was verified in a **real headless Chrome over
  `npm run start` and again in `next dev`** — 76 of 80 checks, the four non-passes being
  over-strict assertions re-measured in the slice's `result.md`. Measured invariants worth
  keeping: 가입 → **확인 중 (text swap + disabled, no spinner element)** → `/portfolio` with a
  live cookie; the two login failures byte-identical; the 재설정 answer identical for a known and
  an unknown address with the link only in the server log; the emailed link **single-use**;
  the offer panel gone after 닫기 and not returning on another stock in the same session; **zero
  `position: fixed`** elements and **no horizontal overflow at 390×844** with every target ≥44px.
  Test data was removed afterwards (all six reader tables back to 0).
- (`P5.S16`) **`frontend`** — R5's **내 포트폴리오** is built: `/portfolio` (the product's only
  gated route; the gate is the API's own 401, and it is the only `redirect` to 로그인 in the app),
  its **샘플 모드** at `?sample=1`, the `?add={corp_code}` handshake resolved server-side, and
  **알림 설정** at `/portfolio/notifications`. The surface is one client orchestrator over the
  served payload — **no page 대제목** (개정 ③), rows with an in-place 보유량 edit whose confirm is
  the horizontal 수정·삭제 → 저장·취소 column swap (개정 ④), 삭제 = immediate + an 8-second
  in-place 되돌리기 with no modal, and the two D-day sections in the server's order under the
  served 기준 anchor. An account write is followed by a **re-read of the same endpoint** rather
  than a local recomposition, so ② and ③ render 조회's **own** components (`Conversion`/`Dilution`,
  now exported from `components/lookup`) and the two surfaces cannot disagree about a number.
  The chrome gains exactly one thing — the `AccountSlot` seam with its three renderings (R2's
  로그인, the 축약 이메일 menu, R5-4's 「샘플」 + 샘플 종료 pair) plus the mobile sheet's account
  rows; nav links, the 52px bar and the footer are untouched. **`experience`** — the 2층 now
  behaves as the round draws it: **offers are offers** (세션 이월 and 계정 이전 are inset rows with
  담기 / 담지 않기, never automatic, and declining keeps the browser's value as a per-tab flag);
  **챙긴 돈 (R5-8)** flips a past ① 소멸 row's label and ink 놓친 돈 → 챙긴 돈 on the *same* figure
  and reaches **no aggregate**; a repeat 담기 opens that row's 수정 instead of an error the round
  wrote no words for; 계정 삭제 confirms by **arming in place** (계정 삭제 · 취소), because "즉시"
  plus "게이트 화면·강제 모달 금지" leaves no room for a dialog; and 로그아웃 is immediate with the
  one-time message carried across a full document load. **`security`** — the gate and the sample
  are honest at the same time: exactly one surface is gated and every other route still answers
  anonymously; the sample is anonymous end to end (**no anonymous write endpoint is called or
  needed**), shows no email and no account fact, and its edits plus the reader's 챙긴 돈 marks live
  in **`localStorage` (`mijual.portfolio.sample`)** while the two "offer declined" flags live in
  `sessionStorage`; migration is **offered, never automatic**, and 계정 삭제 removes the address
  immediately (the cascade takes sessions, holdings, claims and preferences). Leaving a session —
  로그아웃, 계정 삭제, 샘플 종료 — goes through a **fresh document load** so no gated payload
  survives in a client cache and Back cannot restore a signed-in surface. **`qa`** — the frontend
  check now covers the gated layer: `npm run build` (**10 routes**; `/portfolio` and
  `/portfolio/notifications` both `ƒ`) + `typecheck` + `smoke` (**8 → 9** `node:test` cases, still
  no jest/vitest/jsdom) all green with the **Python suite untouched at 113**, and the surface was
  driven end to end in a real headless Chrome over `npm run start` **and** `next dev` —
  **107 scripted checks, all passing** across 샘플 모드, the account lifecycle (signup → 이월 →
  추가 → 편집 → 삭제/되돌리기 → 챙긴 돈 → 알림 → 로그아웃 → 재로그인 → 계정 삭제) and mobile
  390×844 (0 px overflow, zero `position: fixed`, every tap target ≥44 px). Test accounts were
  deleted through the product's own 계정 삭제 (all six reader tables back to 0). One durable
  engineering rule came out of it: **an inline `[]`/`{}` that reaches an effect's dependency list
  silently freezes the App Router** — refreshes stop committing and links stop navigating, with no
  warning — so shared frozen empties are the convention here.
- (`P5.S17`) **`frontend`** — R7's **운영 관제** is built and is durable frontend truth: the `/ops`
  route group (six request-time routes + a layout that is also the door), `components/ops/` and
  `lib/opsRuns.ts`. The **ops idiom** is now a stated module, not a per-page style: the cosmos token
  scope stays, **all ornament is removed** (no starfield, shooting star, radial glow, corner
  brackets or panel-glow), a panel is opaque `#0e1a15` + 1px `--border-strong` — the literal is a
  local custom property, never added to the read-only vendored token file — rows are mono 11–12px,
  and the surface is **desktop-only by explicit operator decision**: not one media query, a fixed
  `min-width: 1180px` instead. Chrome labels are Korean; codes, identifiers and stage output are
  raw English mono; `▷` stays `▷` here and 「추정」 appears nowhere. The primitives `P5.S18` imports
  are `Panel`/`Code`/`Num`/`Stamp`/`Absent`/`Rcept`/`Quoted` — and **`CraftPanel` is not used on
  this surface at all**. Two durable route rules land with it: the ops path map lives in
  `components/ops/routes.ts` and **not** in `lib/routes.ts`, so no reader-chrome module can import
  an `/ops` href; and `SiteChrome` is now a **client** component that returns `children` bare on an
  ops path — chosen over a route group because a route group would have changed which layout the
  framework's 404 renders inside (`P5.S13`'s measured behaviour). The **only** client-side
  derivation on the surface is the one R7 mandates — `lib/opsRuns.ts` joining the beat schedule with
  the run log to emit 「실행 기록 없음」 — plus the display-only KST clock, which deliberately keeps
  ticking under `prefers-reduced-motion` because it is a readout, not an animation.
  **`api`** — `/ops` is now **twelve** read-only routes: `GET /ops/lock` is new (the bar's lock chip
  polls every 15 s from all six tabs, and `/ops/overview` walks 488 events, so the chip got its own
  cheap endpoint), and `GET /ops/overview` gained a **`decisions`** block. **`backend`** —
  `mijual.web.opsreads.open_decisions()` reads `docs/current/decisions.md` and returns its still-open
  bullets **verbatim** with the document's own version (`v0004` today), or `{available: false,
  reason}` when the file is absent: 가동 전 미결 is a quotation surface, so nothing there is
  re-worded, summarised or authored. **`security`** — the operator surface behaves as the doc
  requires, measured rather than asserted: the door is an **empty page with one card** (no ops
  chrome, no reader chrome), takes 운영자 ID + 비밀번호 and **nothing else**, has **no 가입 and no
  재설정 affordance**, and answers a wrong ID and a wrong password with the **byte-identical** line
  「자격증명이 올바르지 않습니다」; the session is its **own `mj_ops` cookie** — a reader `mj_session`
  opens nothing — and expiry re-renders the door **in place at the same URL** (no `?next=`, nothing
  stored) so the operator returns to the tab they were on; a service outage leaves the door silent
  rather than claiming bad credentials. **The panel is linked from nowhere** — six reader surfaces
  contain no `/ops` href **and no `/ops` substring at all** — and it is **read-only end to end**: the
  only POSTs on the whole surface are login and logout, 행 검사 is a plain GET whose state lives in
  the URL, and no tab carries an action control (피드백's only button is 로그아웃). Reader disclosure
  stays minimal: 사용자 shows a **count** of portfolio holdings and never their contents, the two
  tables are **not joined**, and 샘플 로드 여부 renders as an **absent fact** (the column exists iff a
  served row carries `sample_loaded` — today no column, no placeheld cell) rather than asserting
  `false`. **`operations`** — the panel is now the operator's actual console: 개요 renders
  `gates summary` verbatim (488/628 exposable · 710 stored rows · 418 renderable · its measured-at
  stamp), the beat schedule **from the served config**, the run log with per-stage counts and the
  pipeline's own `▷` spend line, and — the one alert on the surface — an **alert-ink 「실행 기록
  없음」 row per scheduled beat instant with no run** (budget exhaustion stays in reported style;
  alert means *did not run*, nothing else). The **lock chip is live** (`free` / `held` + holder,
  ttl and held-since / an honest `unknown`), 게이트 대기열 prints its **691 distinct
  `(rcept_no, field_key)` / 710 stored · 19 duplicates** basis beside every rate, suppression codes
  render **raw English with no fallback**, and 정확도·비용 puts **판정 출처 above every number**,
  never shows a rate without its decomposition, renders `evalset report`'s markdown byte-identically,
  and labels both spend windows with the quota's `20,000/day · operator (decisions O-1)` provenance.
  **`qa`** — the frontend check now covers the operator surface: `npm run build` (**16 routes**; all
  six `/ops` routes `ƒ`) + `typecheck` + `smoke` (**9 → 11** `node:test` cases, still no
  jest/vitest/jsdom) all green, and the **Python suite moved 113 → 114** — one terse test for the two
  additions above. The surface was driven in a real headless Chrome over `npm run build && npm run
  start` with the API launched from **process env vars** (`MIJUAL_OPS_ID=… MIJUAL_OPS_PASSWORD=…
  .venv/bin/uvicorn …`; the operator's `.env` was never opened): **104 scripted checks, all
  passing**, including a live account row created and then deleted through the product's own
  endpoint and a **real Redis lock set and released** to exercise the chip's held state. Reader
  regression: all six reader surfaces and the 404-inside-chrome behaviour unchanged. No mobile pass
  — desktop-only is signed.
- (`P5.S18`) **`api`** — the panel gains its thirteenth route and the one read that leaves this
  service: `GET /ops/vocky?limit=&cursor=` proxies vocky's **`GET /api/project/feedback`**
  server-side and serves `{as_of, state, source{endpoint, base?}, fields[], count, rows[],
  next_cursor?, reason?, status?}` — **one feedback event per row**, newest-first **keyset cursor**
  (limit default 50, **max 100 = vocky's own ceiling**), `next_cursor` absent-not-null, and **no
  total, because vocky returns none**. The sixteen served fields are **vocky's own English key
  names**, carried in `fields` so a client names none of them, and `ingested_at` is converted to
  absolute KST like every other instant this API emits. `state` is `ok | unconfigured |
  unreachable` — the whole degradation contract, with `reason` a raw English exception name.
  **`security`** — the vocky auth model was an open unknown and is now settled: a `vk_`-prefixed
  key in `Authorization: Bearer`, project- or org-scoped, held **only** by the backend
  (`MIJUAL_VOCKY_API_KEY`, masked repr · raises only on use · never logged · never in a URL) and
  never by the browser. Three findings belong to this doc: vocky has **no read-scoped credential**
  (the same key can write), so read-only is enforced Mijual-side by issuing `GET` and nothing else
  and by a test that lets **only `web/vocky.py` import an HTTP client**; **redirects are refused**
  because `urllib` re-sends `Authorization` to the redirect target; and vocky's error body is never
  echoed onto the panel. **`operations`** — the observation view is live behind two settings
  (`MIJUAL_VOCKY_API_BASE` + `MIJUAL_VOCKY_API_KEY`), degrades in **3 s** with no retries and never
  takes the tab down (dead port 12 ms · wrong key `HTTPError 401` 33 ms · blackholed host 3.03 s),
  and P4's wiring list is exactly those two values over **https** — plus the finding that
  **vocky ships no embeddable widget script today**, so `NEXT_PUBLIC_VOCKY_SRC` stays unset and
  the three `data-vocky-trigger` elements stay as built. **`frontend`** — 피드백 **is** the vocky
  관찰 뷰 (R7's card→section mapping) and the `save_feedback` 대기열 now sits on 대화 로그 with its
  own `?feedback_cursor=`, the two linked and never merged; the table's headers are the served
  field names in mono (the card's `?` columns are gone), and the 연결 전 state renders the signed
  「API shape 확정 대기」 over a static skeleton carrying those same column names. **`decisions`** —
  §6.3's delegation is **closed**: the shape is recorded in the landed record's own section
  (2026-08-22, additive, nothing else in that file touched). **`qa`** — Python suite **114 → 118**
  (four terse cases: the 연결 전 path, the mapping of a **captured real** vocky payload, the
  degraded path, and the one-HTTP-client scan); frontend `build`/`typecheck`/`smoke` (11) green;
  live end-to-end pass against a throwaway local vocky stack with the repo left byte-identical and
  the hosted service never contacted.
- (`P5.S19`) **`frontend`** — the fidelity pass corrected four contract-level defects, one of them
  systemic: **`.mono`'s `font-size` is now `:where(.mono)`**, a zero-specificity default, because a
  global class rule and a CSS-module class rule are both **(0,1,0)** and source order was silently
  flattening **23 surface-stated sizes to one 12.825px** (R4's 32px 놓친 돈 총액, the 20px 금액 /
  청약 결과 inset, R3's 12px crumb, R2's 11px tab counts). The rule to record in the doc: **R1's
  "mono ≈0.95em of the surrounding sans" is a default relationship, and a size the record states
  for a surface governs over it.** Also: `EstimateMarker` gains a **named `size` prop**
  (`"inherit" | "landing"`) so the footer's 「추정」 renders R2's literal **10px** instead of 6.72px —
  the primitives are extended by named, record-cited props, never by a local restyle; R3's
  "mono window/state line" is now mono for the **whole** line, so no D-day numeral renders in sans;
  and the board's desktop grid uses `minmax(0, …)` for R2's two wide columns, which keeps R2's exact
  widths wherever they fit and removes **41px of horizontal document overflow in the 768–830px band**
  without truncating a value. **`experience`** — the whole signed product was verified against its
  rounds in a real browser and the **trust rules are now measured, not asserted**: no untagged
  estimate / no tagged fact, **no derived money before 확정발행가 on detail, 조회 or the portfolio**,
  no ②/③ per-holding won, **40 board D-days byte-identical to the served `countdown.dday`** and the
  countdown 0 s off the served instant, past ② reads 진행 중, 추후결정 never beside a date, a
  gate-blocked field is absent rather than placeheld, and 조회 ↔ 포트폴리오 agree to the won.
  Korean prose draws in Pretendard on every surface (measured via platform fonts, not computed
  style), and **Korean inside a mono element is the record's own choice of face** — a
  cross-platform Hangul mono would be a token edit, i.e. a design change. **`qa`** — the durable
  method: `build` + `start` + uvicorn driven over CDP, **~230 checks / 11 stages** at 1440/768/390
  plus 481–1120, screenshots per surface, and two traps that cost real time — a stale `next start`
  holding :3000 fails **silently** into the log with `EADDRINUSE` and then serves 500ing CSS chunks
  (looks exactly like a fix that did nothing), and flattened-`innerText` proximity checks yield
  confident false failures that must be re-measured with scoped selectors. Suite state unchanged
  and green: `pytest` **118 passed**, `smoke` **11/11**, `build` + `typecheck` clean.

## Open Questions

- **The consolidated operator catalogue lives in `slices/P5.S19/result.md` §4** — *new, `P5.S19`*:
  the fidelity pass swept every surface and every deferred `S19` item and produced **19 questions,
  none of them an implementation defect**. Many are the entries already below (the English 404, the
  silent `invalid_reset_token`, 「API shape 확정 대기」, 내 종목 연결, R7's 샘플 로드 여부, the closed
  청약 with no 실적보고서, the dated 49.2억원, the two stated defaults, 수신 주소 변경 re-auth, the
  vocky capture path, 계정 이전's composed heading). **New there and not repeated here:** Korean
  glyphs inside `--font-mono` elements fall to the OS Korean face — every one of those elements is
  drawn in mono *because the record says so*, and changing it means editing the landed `tokens.css`;
  `[근거]` (14px) and its DART link (17px) sit under the mobile **44px** hit floor inside a signed row
  anatomy; the ① 환산 chain's 할인율 step fills its 340px citation cap, widening the gap before the
  arrow; the hero H1 renders **내 종목 조회** where R2's literal says 내 종목 연결; the PII inset
  renders **2 lines** where R5's copy list says 3행; the 메뉴 button's hairline is this build's
  reading of "button"; the sample's signed **4건** subline sits above **five** live D-day rows; and
  two signed R4 sentences render their dates in **sans** while the boundary panel renders its dates
  in mono. Also noted, no decision needed: the app has **no favicon** (the ring PNG is 2178×346 and
  re-encoding a delivered asset is not an implementation call). **`P5.REVIEW` / operator call**, one
  pass over that section.
- **「API shape 확정 대기」 now reads half a step behind its own surface** — *new, `P5.S18`*:
  the line is signed copy for the vocky view's 연결 전 state, but §6.3's delegation is closed —
  the shape **is** confirmed, and what the view waits for is the `vk_` credential. Rewriting a
  signed line is a design change, so it renders **as signed** and the raw English `state` code
  (`unconfigured`) beside it says which cause it is. Re-cutting the sentence would be a new
  signoff item; leaving it is a small stale literal on an operator-only surface. **Operator /
  `P5.REVIEW` call**, the same shape as the other copy questions here.
- **Is there a capture path into vocky at all?** — *new, `P5.S18`*: vocky ships **no embeddable
  widget script** (its README puts "Browser-direct unauthenticated ingestion" under what the MVP
  will not do), so the three signed `data-vocky-trigger` elements have nothing to bind to and the
  observation view will observe an empty list until the operator wires a server-to-server capture
  call. Nothing was built for it here — R7 signs 위젯 UI는 vocky 소유, and inventing a capture
  endpoint would be this build deciding another product's surface. **Operator call** (their own
  product), with P4 as the natural place if the answer is "wire one".
- **The 계정 이전 offer has a body but no signed heading** — *new, `P5.S16`*: R5-4 writes the
  offer's own sentence and names the flow ("샘플 → 계정 이전 제안"), but no heading for the inset
  row, so the surface labels it **계정 이전** — composed from the round's own phrase rather than
  quoted from a signed line. The alternative was inventing a sentence or shipping an unlabelled
  row. Flagged for `P5.S19`'s copy inspection / the operator, alongside the same slice's reading
  that **샘플 모드 offers no 종목 추가** (R5-4 signs a fixed, editable composition; adding an
  arbitrary issuer would need a second row-composition site for the placement rules `P5.S8` owns).
- **An expired or spent 재설정 link has no signed sentence** — *new, `P5.S15`*: R5 signs three
  auth failure lines (불일치 / 중복 가입 / 8자 미만) and `invalid_reset_token` is not one of them,
  so the confirm page returns to idle and **states nothing**; the reader can request a fresh link
  from the panel. Writing "링크가 만료되었습니다" would be inventing signed copy, so nothing was
  written. **Operator/`P5.S19` call**, the same shape as the missing Korean 404 sentence.
- **R7's 샘플 로드 여부 column has no backing fact** — *new, `P5.S9`*: R5's sample portfolio
  is anonymous end to end and `P5.S8` deliberately built **no anonymous write endpoint**, so
  a 샘플→계정 이전 arrives as ordinary authenticated holdings and nothing server-side records
  that the sample was ever loaded. `/ops/users` therefore serves the other four 독자 계정
  columns and **omits this one** rather than asserting `false`. Building the backing means a
  holding-provenance column plus a client-visible parameter — a change to `P5.S8`'s signed
  contract and a new behavioural fact about a reader, which `security`'s minimal-disclosure
  rule argues against. **Operator/review call**, not an implementation one. *`P5.S17` renders it
  the only way both records allow — the column is **data-driven**, appearing iff a served row
  carries `sample_loaded`, so today there is no column and no placeheld cell, and building the
  backing later needs no frontend change.*
- **Re-authentication for 수신 주소 변경** — *new, `P5.S8`*: `PATCH /auth/account` accepts a live
  session as authority, matching R5's Notify card (a 변경 affordance, no password field) and
  `P5.S7`'s 계정 삭제 precedent. The consequence is that a stolen session can turn read access
  into a permanent takeover. Requiring the current password would need a control the signed
  round does not have, so it is an **operator/design** call, not an implementation one.
- **The countdown cut-off instant** — *stated default landed, still the operator's call*: `P5.S3`
  serves R2's own assumption (end of the 청약 day, 00:00 KST of the next day) behind
  `MIJUAL_COUNTDOWN_CUTOFF_TIME`, so the real 접수 마감 시각 replaces it with no code change.
- **The stale threshold in hours** — *stated default landed*: **18 h**
  (`present.DEFAULT_STALE_AFTER_HOURS`, override `MIJUAL_STALE_AFTER_HOURS`), derived from the
  07:30/19:30 KST beat schedule. Operator may still choose another number.
- **The "정정 이력" button label** — exited P3 unresolved and is carried here (`experience` v0002,
  `product` v0003); `P5.S13` needs it.
- **The footer's 49.2억원 is a dated-pack figure, not a served one** — *new, `P5.S11`*: the
  gate-cost sentence is signed and the footer is its only placement, but the presentation
  contract serves no gate-cost number and deriving it needs `mijual.estimate`'s corpus-median
  할인율, which a request path may not import (S2 note 7). It therefore states 2026-08-20's
  figure on every page beside live landing numbers. Making it live is **backing work** (a
  persisted precomputation + a summary key), so whether it becomes a fix slice, a deferred job
  or stays as transcribed copy is **`P5.REVIEW`'s call**.
- **The locked positioning sentence still says 내 종목 연결** — *new, `P5.S11`*: it is locked
  operator copy (R1/R2 handoffs; the challenge brief), and R4's supersession is scoped to the
  **nav label**, so the footer was transcribed verbatim rather than re-cut. If the operator
  wants the sentence to match the surface's final name, that is a signed-copy change — an
  operator/design call, not an implementation one.
- ~~**Binary design assets**~~ — **CLOSED 2026-08-22** by the operator's export (the co-work step
  `P5.S10` stopped for). All five files are in the repo byte-for-byte under
  `frontend/public/assets/` — `mijual-wordmark-{charcoal,white}.png` (1788×324),
  `mijual-logo-ring-{charcoal,white}.png` (2178×346), `fonts/PretendardVariable.woff2`
  (variable `wght 45–920`) — checksummed in that directory's README, with Pretendard verified
  loading and drawing Korean prose in a real headless Chrome. **Nothing was ever substituted,
  generated or placeheld.** The one detail that needed the operator's eye is answered: the white
  wordmark ships as **`mijual-wordmark-white.png`**, and that is the name `P5.S11` wires.
  `P5.S11` is unblocked.
- **The concrete admin route** (`/ops` is the example, not the decision) and how the operator
  credential is issued — `security` calls these **deploy** decisions (P4); `P5.S9`/`P5.S17` need a
  working local value in the meantime.
- **vocky's real observation API** — its shape, and whether reaching it needs a credential the
  operator must supply (`P5.S18`).
- **A closed 청약 with no 실적보고서 yet has no signed state** — *new, `P5.S14`* (raised as a gap by
  `P5.S4` note 8, now visible on a page): such an ① is in **neither** section of 내 종목 조회, so its
  stock renders the *no-event* empty state — "이 종목에는 진행 중이거나 2026년에 소멸된 권리가
  없습니다". Live today on **센서뷰 `01593668`** and **클로봇 `01784914`**, both with a
  확정발행가-priced ① whose 청약 closed **2026-08-14**. Nothing was invented for them: `pending`
  would render the wrong copy (their 청약 is over) and a 놓친 돈 row would be a figure nobody filed.
  R4 signs no state for the interval between 청약 종료 and the 증권발행실적보고서, so drawing one is a
  **design** call — `P5.S19`/the operator's, not an implementation one.
- **The not-found page has no Korean sentence** — *new, `P5.S13`*: a non-renderable `rcept_no`
  must 404 without explaining itself (`P5.S3` note 5), and the copy inventory holds **no 404
  string**, so `app/events/[rcept_no]/page.tsx` calls `notFound()` and the framework's English
  default renders inside the correct chrome. Writing a Korean line would be inventing signed copy.
  The operator (with `P5.S19`) decides whether a 404 sentence gets drawn; until then this is the
  one English string a reader can reach.
- Not P5's: the **운영자 연락처 string** for `get_contact` (P6, operator-provided, never invented).
