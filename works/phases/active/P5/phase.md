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

## Open Questions

- **The countdown cut-off instant.** R2 assumed 2026-09-04 24:00 KST for 계양전기; the real 접수 마감
  시각 is TBC and the backend must serve an absolute KST timestamp. Operator input, needed by `P5.S3`.
- **The stale threshold in hours** — R2 carried it open; needed by `P5.S3` (freshness chip) and
  `P5.S12`. Operator or a stated default recorded as a decision.
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
