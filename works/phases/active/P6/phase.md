# Phase P6: Apply — AI 질문 agent

_Intent: see [intent.md](intent.md)._

## Objective

Implement the AI 질문 feature per R6's signed build prompt, after P5 lands the rest: the citation-forced agent backend (SSE, tools search_events/get_event/get_portfolio/save_feedback/get_contact, refusal families, server-side anonymous conversation storage) and its widget + dedicated page surfaces. RESPECT THE DESIGN.

## Context

P6 is the **apply phase of a two-phase split** (P5 built everything else), so this is a
**single-pass** decomposition: the design landed and was signed in P3's R6 round. There are no
design slices and no `DECOMP2`.

Read order for every slice in this phase:

1. `works/phases/active/P6/intent.md` — the confirmed intent **including the mid-phase Operator
   Addition (2026-08-22): "we need to build a agent not just llm chain."**
2. `docs/reference/design/rounds/06-explain/output/build-prompt.md` — the binding implementation
   contract, and `.../output/result.md` — the round record (refusal families, copy, revisions).
   **READ-ONLY.** No P6 slice edits a file under `docs/reference/design/`.
3. `docs/reference/design/rounds/07-admin/output/build-prompt.md` §대화 로그 · §사용자 ·
   §save_feedback 대기열 — R7 signs the **conversation schema** P6 implements, column by column.
4. `docs/reference/design/grounding/ui-traps.md` + `states-and-trust.md` — binding rules.
5. `works/phases/active/P5/phase.md` — the P5→P6 boundary (DECOMP note 5, `P5.S9` note 9,
   `P5.S11` notes, `P5.S13` note 8, `P5.S16` note 7, `P5.REVIEW` note 9).
6. `docs/current/` — `api`, `backend`, `architecture`, `data`, `security`, `frontend`,
   `experience`, `operations`, `qa`, and **`decisions` D-4** (Gemini 3.7 Flash, per-task thinking
   level, ▷ cost estimates).

There are **no R6 HTML cards in this repository** — `docs/reference/design/rounds/*/output/`
holds `build-prompt.md` + `result.md` only (verified: `find … -name "*.html"` returns nothing).
The build prompt *is* the card set for implementation purposes; where it gives a pixel spec
(런처 마크, 440×620, 68×50, 7×15 캐럿, 28px 헤더 아이콘, 340 레일) that spec is literal.

## Decomposition

Backend first, then the design implementation, fidelity last — the ordering the confirmed intent
fixes and the one P5 proved. **Seven middle slices, every one `risk: high`**: each writes real
code across more than one file, which is the tier rule. `depends_on` is advisory and here it is
also the true build order.

| Slice | Order | Covers |
|---|---|---|
| `P6.S1` | 1 | **익명 대화 저장소 + `Conversations` 포트 구현** — the conversation/turn/feedback schema R7 signs (세션 해시 · 시각 KST · 범위 · 질문 · 답변/거절 · 거절 카테고리 · 근거 rcept_no 목록 · 인용 칩 원문), the anonymous session-hash derivation, newest-first opaque-cursor reads, and a `DbConversations` implementing P5's `mijual.web.conversations.Conversations` protocol, wired through `create_app(conversations=…)`. **No route changes** (`P5.S9` note 9). The three ops tabs go from honest zeros to real rows. Schema-level anonymity (**no account/email/IP/UA column anywhere**) is proven by a test, not by discipline. |
| `P6.S2` | 2 | **The five agent tools** — `search_events(query)` · `get_event(rcept_no)` · `get_portfolio()` · `save_feedback(text, email?)` · `get_contact()` as server-side callables in the new `mijual.agent` package, each returning **verified-contract values only** (via `mijual.present` / `mijual.web.reads`), each with its Gemini `FunctionDeclaration` schema and its signed **fact-row** string (`이벤트 검색 「{q}」 → {n}건 · {유형} · {rcept_no}`). Search-0건 returns the signed "찾지 못했습니다" fact, never a guess. `save_feedback` writes through `P6.S1`; `get_contact` reads deploy config and is honest when unset. **No tool computes a number.** |
| `P6.S3` | 3 | **Agent core — the autonomous Gemini function-calling loop.** The model decides *which* tools to call, *in what order*, *across as many rounds as it needs*, and *when it is ready to answer*; the loop is `generate → (function_call? → execute → feed result back) → repeat → answer`, with a structural round/call budget (the `CallBudgetExceeded` pattern from `mijual.extract.client`), never a scripted retrieve→prompt→answer chain. Also: the system instruction, the per-call thinking level + ▷ ledger (D-4), **citation forcing at the generation boundary** (a claim with no verified verbatim span cannot enter the stream), the never-compute rule, refusal-family selection (the five signed families only), scope handling (event ↔ 전체 공시), and the typed event stream the transport serializes. |
| `P6.S4` | 4 | **SSE transport + persistence + the request-path boundary.** The FastAPI streaming endpoint(s) under `mijual.web` (ask · stop), the frames that carry the signed states, the anonymous session handle, per-turn persistence into `P6.S1` (answer *or* refusal, with 거절 카테고리 · 근거 rcept_no · 인용 원문 — R7: 거절도 저장 시 인용 동반), server-side rate limiting with **zero UI copy**, and the honest re-statement of the architecture boundary: `mijual.web` now reaches a model, through `mijual.agent` and nowhere else. The two AST scan tests are **re-aimed, not deleted** (Finding 1). |
| `P6.S5` | 5 | **런처 + 위젯 — the whole desktop AI 질문 surface.** The 68×50 launcher with the two-half-ring 22px Saturn mark (the one sanctioned motion exception) and its hover/open/reduced-motion states; the 440×620 opaque `#0e1a15` widget (fixed 우하단, no backdrop/dim, header `external-link` + × at 28px); message bubbles; mono tool fact rows with the 2px hairline; numbered inline citation chips → in-place quote blocks + the API-tier variant; the 답변 푸터 (`근거 N건 · {rcept_no} · {생성시각 KST}` + context links); refusal rendering as ordinary prose in the signed 3-part structure; the four SSE states (답변 준비 중 → 스트리밍 with the 7×15 caret → 완료 fade → 중단/오류 keeping partial output); the sessionStorage thread + scope model with its 범위 chip. **One signed surface, complete** — nothing here ships half-rendered. |
| `P6.S6` | 6 | **전용 페이지 + 모바일 + 질문 스트립 + 진입점.** The frameless `/ask` page (chat directly on the page, 340 rail as the only panel, **no launcher rendered there**) replacing P5's bare shell; the ≤480px full-width page with **no widget and no launcher** (sticky 44px input bar, full-width citation blocks with the 180px cap, tool rows kept, ≥44px targets, back-navigation returning to where the reader was with the conversation intact); the 질문 스트립 preset chips on event detail, generated from that event's **gate-passing** fields and opening the widget (mobile: the page) in event scope with the question sent; widget↔page continuity over the same sessionStorage thread; the nav slot and the footer bottom-row link behaving as R6 signs. |
| `P6.S7` | 7 | **Design-fidelity verification in a real browser (RESPECT THE DESIGN)** — run the product end to end and check every R6 element against the signed contract, the way `P5.S19` did. Nits found in earlier slices are fixed **here**, never by editing the landed record. Includes the launcher-mark reading test (a ring that reads as a flat sticker is the recorded bug), the corner-collision check against vocky, reduced-motion, 390px overflow, and a live agent conversation exercised in the browser. |

**Rationale for the cut**

- **Storage first, because two later slices write into it and one existing surface is waiting.**
  `save_feedback` (S2) and turn persistence (S4) both need a schema, and R7's three ops tabs are
  already built against the port and serving honest zeros. Landing the schema first turns those
  tabs on early, which makes every later backend slice observable through a surface the operator
  already has — and it puts the **schema-level anonymity promise in place before anything writes**,
  which is the order that makes the promise structural rather than retrofitted.
- **Tools before the agent, because the agent is defined by what it can call.** The tool layer is
  ordinary, testable, deterministic code over `mijual.present` — it can be measured against the
  live corpus with no model and no key. Building it first means S3's loop is exercised against
  real return contracts instead of stubs, and it keeps the two hardest-to-review things (money
  spent per call, and a non-deterministic loop) out of the slice that establishes what a tool
  returns.
- **The agent core is its own slice because the operator addition makes it the phase's keystone.**
  "Agent not chain" is an architectural property, not a feature: it lives or dies in the loop's
  control flow. Isolating it means the review can read one module and answer *does the model
  choose?* — rather than hunting for the decision inside an HTTP handler.
- **Transport is separated from the loop** for the reason `P5.S2`/`P5.S3` were separated: a
  generator of typed events is unit-testable with no HTTP, and an SSE handler that also owned the
  agent's control flow would make every streaming bug a reasoning bug too. It is also where the
  **architecture boundary changes**, and that change deserves to be visible in one slice's diff.
- **One slice per signed surface, and each one complete.** The widget is one surface (S5) and the
  page + mobile + entry points are the other (S6); S6 reuses S5's components rather than
  reimplementing them. Splitting the widget into "chrome" and "answers" was considered and
  rejected: it would leave a chat that renders prose without citations across a slice boundary,
  and a half-rendered answer surface is exactly the thing RESPECT THE DESIGN and P5's
  no-fake-chat rule refuse.
- **Fidelity is its own slice**, per `design-cowork` and the `P5.S19` precedent: implementing and
  verifying against the record are different jobs, and the second one needs a running browser.
- **Seven, not nineteen.** P5 was seven signed rounds' worth of surfaces; P6 is one round with a
  deep backend. The cut follows the seams the record itself draws (§Agent · §SSE · §거절 ·
  §세션+저장 · §Mobile · §런처 마크), not an arbitrary size target.

## Findings & Notes

1. **⚠ The architecture's loudest invariant changes here, and it must change honestly.**
   `docs/current/api.md`, `architecture.md` and `backend.md` all state **"No OpenDART call and no
   LLM call happens in a request path,"** and it is enforced by
   `tests/test_web_smoke.py::test_no_request_path_module_imports_a_spending_module` (an AST scan
   over `src/mijual/web/**.py` for `mijual.dart` / `mijual.collect` / `mijual.extract`) plus
   `tests/test_web_vocky.py::test_only_the_vocky_module_may_speak_http` (the same scan for
   `urllib` / `http.client` / `socket` / `requests` / `httpx`, `vocky.py` excepted). **P6's agent
   is an LLM call in a request path by design** — SSE streaming cannot be anything else.
   - Both scans walk `src/mijual/web/` only, so putting the agent in a **new top-level package
     `mijual.agent`** keeps them literally green — *and that is not good enough on its own.*
     The slice that lands the endpoint (`P6.S4`) must **re-aim** the invariant rather than let it
     quietly become false: `web/` still imports no spending module and still speaks HTTP in one
     file; the model is reached **only** through `mijual.agent`; and a **new scan over
     `src/mijual/agent/`** must keep `mijual.dart` / `mijual.collect` / `mijual.extract` out of
     the agent too (the agent reads persisted rows, it never collects or extracts).
   - Do **not** import `mijual.extract.client` from the agent, however tempting the `GeminiClient`
     wrapper is: it lives inside a package the request path is forbidden to reach. Copy the two
     ideas that matter (structural call budget, recorded thinking level + ▷ ledger) into the
     agent's own client, or lift the shared piece into a neutral module — a decision `P6.S3`
     makes and records here.
   - Doc impact when it lands: `architecture` (module map + the boundary sentence), `backend`,
     `api`, `security`, `operations`, `qa`. Note it in *Doc impact* below; `P6.REVIEW` versions it.
2. **The conversation schema is signed by R7, not free.** R7 §대화 로그 fixes the columns —
   *세션 = 익명 해시 · 시각 KST · 범위 (이벤트 rcept_no 또는 전체) · 질문 · 답변/거절 ·
   거절 카테고리 (가족 5종) · 근거 rcept_no 목록 · 인용 칩 원문* — and states
   **"계정·이메일·IP·UA 컬럼은 저장하지 않음 — 표시 정책이 아니라 스키마."** 익명 세션 is
   *"대화 로그의 집계면"*: 세션 해시 · 최근 활동 KST · 질문 수 · 거절 수 · 마지막 범위, with a
   two-way cross-link to the log. `save_feedback` 대기열: 시각 KST · 의견 텍스트 · 답장 이메일
   (선택, 자발 입력한 경우에만) · 원 대화 링크 (세션 해시로). Read-only everywhere: 삭제·편집·
   태깅 없음, 처리 상태 비트 없음.
3. **The exact row keys the built ops panel already reads** (`frontend/components/ops/log.ts`,
   `P5.S16` note 7's three-tier convention) — serve these and the tables render with no frontend
   change:
   - 대화 로그 row: `session_hash` · `at` · `scope` · `question` · `kind` (`answer`|`refusal`) ·
     `refusal_category`; expanded row: `answer` · `evidence` · `quotes`.
   - 익명 세션 row: `session_hash` · `last_activity` · `questions` · `refusals` · `last_scope`.
   - 피드백 row: `at` · `text` · `email` · `session_hash`.
   - Filters already wired: `/ops/conversations?kind=&refusal_category=&session_hash=&cursor=&limit=`.
     The 거절 카테고리 filter sends the **five signed Korean family names** —
     `철회` · `확정 전` · `공시에 없음` · `검증 미통과 폴백` · `계산 요청` — so those strings are the
     stored vocabulary; do not invent English tokens for them. `kind` sends `answer`/`refusal`.
   - Any key P6 serves that `log.ts` does not name is rendered **raw** rather than dropped, so a
     mismatch shows up as a visible raw key — but matching the list above is the intended path.
4. **The port's three rules are inherited, not re-decided** (`P5.S9` note 9): every method returns
   `Page(rows, total, next_cursor)`; **no method takes an account, email, IP or UA filter**;
   nothing writes; pagination is an opaque cursor, newest first. `EmptyConversations` is replaced
   by wiring a real implementation into `create_app(conversations=…)` — the same seam shape as the
   mailer. **P6 changes no `/ops` route.** `next_cursor` is omitted, never `null`.
5. **`get_portfolio()` has no anonymous server-side portfolio to read, and that is by design.**
   P5 made it structural: *"Anonymous state never reaches the server … there is no anonymous write
   endpoint at all"*; 보유량 and the 샘플 live in the browser. So the tool resolves **only the
   caller's own session/account** (`security` §Rate Limits/Abuse), and for an anonymous caller the
   designed answer is **the sample portfolio, labelled** — R6-3 combines portfolio questions with
   the R5 sample, R6's own fact row reads `내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)`,
   and the answer must carry 「구성 예시」 with the 샘플 배너 규칙. `GET /portfolio/sample` already
   exists and is anonymous + read-only. **Do not add an anonymous write path, and do not accept a
   client-supplied holdings payload** to make this look richer.
6. **The agent never computes a number, and the tools are where that is enforced.** D-day, 환산,
   금액, 소멸률 all arrive from `mijual.present` (§3.6 layer 3 / `api` §The presentation contract);
   the model receives them as values it may quote, never as inputs to arithmetic. Derived values
   keep 「추정」 in prose too (R6 hard rules). A won amount before 확정발행가 is *unconstructable*
   upstream, so 확정 전 금액 refusals are backed by an absent value, not by a prompt instruction.
7. **Citation forcing is a generation-boundary property, not a post-processing step.** R6:
   *"인용 없는 주장은 생성 단계에서 차단 (스트림에 나올 수 없음)"* and *"인용 칩은 해당 주장과
   동시에 도착 — 자리표시 칩·후행 부착 금지."* Practically: a factual sentence is emitted only
   together with the verified verbatim span it rests on, and quotes are **never reconstructed or
   summarised**. The verified spans come from the tools' verified-contract payloads (quote + span +
   rcept_no); API-tier facts have no quote and use `rcept_no` as the citation handle (R3 rule), and
   the citation block says so in the signed words. `P6.S3` owns the mechanism and `P6.S5` renders it.
8. **Refusals are five families, are not error states, and are themselves citation-forced.**
   Structure is 3-part (① 상태 사실 — 잠긴 카피 우선 · ② the family sentence · ③ 갈 곳 링크), in
   ordinary prose ink with **no alert colour and no icon**; 철회 등 검증된 상태 사실 carries its own
   근거 칩. **Do not generate per-reason-code wording** — the reader-facing payload carries no gate
   reason code at all (`api`: *"A reader payload carries no gate reason code"*), so a family is the
   most specific thing the surface may say. 확정 전 금액: say the known facts (확정 예정일 etc.)
   with citations and refuse **only** the amount. The five signed sentences are in R6's
   `result.md` §Proposed copy — transcribe them, never paraphrase.
9. **`get_contact` is a deploy config value: 미정, operator-provided, never invented.** Build it to
   read config (a `Settings` field alongside `ops_id` / `vocky_api_key` in `mijual.config`) and to
   answer honestly when unset — the tool says it has no contact string rather than inventing an
   address or a 「준비 중」 line. The real string lands at P4/deploy; `security` already records it as
   *"the one operator-identifying string the product will publish. **P6's.**"* This is a **phase
   note, not a blocker** — do not stop a slice on it.
10. **What P5 deliberately left for this phase, ready and waiting** (`P5.REVIEW` note 9):
    `/ask` is a bare shell (`frontend/app/ask/page.tsx` renders `<main className="content" />`) —
    **replace the file**, do not decorate it; the nav's third slot and the footer bottom-row link
    already point at it and already render the superseded label **AI 질문**; the event detail page
    has **no 질문 스트립** on purpose (`P5.S13` note 8 — "do not restore it in review", it is
    `P6.S6`'s); and the bottom-right corner is clear on **every** reader surface (measured: zero
    `position: fixed` elements) for the launcher. `ROUTES.ask = "/ask"` is deliberately not
    `/explain`.
11. **The launcher is the one sanctioned motion exception and it has a recorded bug history.**
    22×22 Saturn: planet = 22px circle `#dfe9e4` with a `repeating-linear-gradient` band looping
    −14px over 4.5s; **the ring is two half-boxes sharing one `ringdrift` 14s animation**, one
    clipped to the bottom half in front of the planet and one to the top half behind it. A single
    ring laid on one side reads as a flat sticker — that is the bug the round already paid for.
    hover scales **only the mark** (1.35) while the frame holds; open state fades the mark out for a
    16px ×. `prefers-reduced-motion` stops the band, the drift, the transitions **and** the hover
    scale. **This motion must not leak onto data surfaces** — R1's no-spinner/no-ambient-motion rule
    is intact everywhere else, and the SSE states use text replacement plus the blinking caret only.
12. **sessionStorage, not localStorage — and never described as deletion.** R6-5/6: screen
    persistence is session-scoped (survives 위젯↔페이지 and navigation, disappears from the screen
    when the tab closes), while the server keeps an anonymous log. The required copy is
    「완전 익명 — 로그인도, 질문 수 제한도 없습니다 · 대화는 익명으로 저장됩니다 (품질 점검용)」;
    「저장 이력 없음」 and 「탭을 닫으면 사라집니다」 are **forbidden** (`security`). Note the trap:
    R5's 포트폴리오 uses different storage rules — do not copy that helper blindly.
13. **No quota, anywhere.** R6-5 revision: 질문 수 무제한, and therefore **no 「남은 질문 N회」, no
    소진 상태, no quota bar on any surface**. Server-side rate limiting is an operations matter with
    **zero UI copy** (`security` §Rate Limits) — if `P6.S4` adds one, it adds no string.
14. **Agent spend is a server fact, not a new ops surface element.** R7 signs 정확도·비용's LLM
    spend as **`extraction_call` 집계** specifically, and its quota bar as the extraction budget.
    Recording agent calls (calls · tokens · thinking level · ▷ cost, per D-4) is prudent and
    allowed; **adding an agent row to the signed 비용 panel is a design change** and is not P6's to
    make. Record the numbers, leave the panel alone, and raise it as an operator question if it
    matters.
15. **`search_events` is a new read with a different contract from `/stocks?q=`.** R4's resolution
    is four *unique-or-decline* tiers where **ambiguity resolves to nothing**; R6's tool returns
    *이벤트 목록/단건*, so it may legitimately return several candidates. It must still obey the
    exposure contract (a non-exposable event is not a search result — `_exposable_events` /
    `gates.exposure` is the single derivation, never re-decided), and 0건 returns the signed
    「「{q}」에 해당하는 공시를 찾지 못했습니다」 + 관제 현황판 링크 rather than a guess. Useful
    starting points in `mijual.web.reads`: `resolve_corp` · `resolve_event` · `load_detail` ·
    `load_stock` · `load_portfolio` · `load_board` · `corpus_as_of`.
16. **Frontend facts worth not rediscovering.** Next.js **16.3.2** + React 19 (`frontend/`), and
    `frontend/AGENTS.md` warns it is not the Next.js in training data — read
    `node_modules/next/dist/docs/` before writing app-router code. The API seam is a **same-origin
    rewrite** (`/api/:path*` → `MIJUAL_API_ORIGIN`), which is what makes the CSRF design work; every
    unsafe call needs `X-Mijual-CSRF` and `lib/api.ts` sets it once for all call sites — **add the
    ask endpoints there**, hard-coded, like every other path. Validation commands:
    `npm run build` · `npm run typecheck` · `npm run smoke` (`node --test "lib/*.test.ts"`), and
    `pytest` at the repo root (P5 left it at **118 passed**). SSE over the rewrite proxy needs an
    explicit check — buffering is the classic failure, and `P6.S4`/`P6.S5` should measure it rather
    than assume it.
17. **Korean-only product surface, and every string in this phase is already written.** R6's
    `result.md` §Proposed copy holds the intro, the SSE strings (「답변 준비 중…」 · 「중지」 ·
    「연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.」 · 「재시도」), the feedback confirmation
    (「의견을 저장했습니다 — 운영자가 확인합니다.」), the five refusal families and the session line.
    Transcribe them into a `copy.ts` with citations, the convention `lib/copy.ts` and
    `components/chrome/copy.ts` already use. **Inventing a Korean sentence is a design change** —
    P5 shipped an English framework 404 rather than invent one.

18. **`P6.S1` landed the storage — what S2/S4 import, and the decisions taken.**
    Module: **`src/mijual/web/conversationstore.py`** (tables in
    `src/mijual/db/models.py`: `ConversationTurn` / `conversation_turn` and
    `ConversationFeedback` / `conversation_feedback`, at the bottom of the file).
    - **Write API** (not on the port — the port stays read-only; both take the
      caller's own session, `flush` but never `commit`):
      `record_turn(session, *, session_hash, question, kind, answer, scope_rcept_no=None,
      refusal_category=None, evidence=(), quotes=()) -> ConversationTurn` and
      `record_feedback(session, *, text, email=None, session_hash=None) -> ConversationFeedback`.
      `evidence` = 근거 rcept_no 목록, `quotes` = 인용 칩 원문 **verbatim** — both
      plain `Sequence[str]`, stored as JSON lists. There is deliberately **no
      quote↔rcept_no pairing column**: R7 signs two lists and that is what exists.
      If `P6.S4` needs the pairing, add a nullable JSON column additively
      (`ensure_columns`) rather than reshaping these — conversation rows, unlike
      every pipeline table (N16), are **not re-collectable**.
    - **Session handle**: `new_session_hash()` = `secrets.token_hex(16)` (32 lowercase
      hex chars), **random, never derived** from IP/UA/account/email.
      `is_session_hash(v)` accepts 16–64 lowercase hex; `session_hash_or_new(v)` is
      S4's entry point — a missing/malformed client token is **replaced, not
      trusted**, which is also what keeps an address out of the column. Both write
      functions raise `ValueError` on a non-handle, so nothing client-controlled
      reaches storage unchecked.
    - **Cursor**: opaque `base64url(f"{epoch_micros}\x1f{tiebreaker}")`, no padding.
      Keyset, newest first, `(created_at, id)` for the log and the queue,
      `(max(created_at), session_hash)` for the sessions aggregate. An unreadable
      cursor is `ApiError("invalid_cursor")` (400) — never a silent page 1.
      `next_cursor` is omitted at the end (`Page.payload()`'s rule, unchanged).
    - **Vocabulary**: `KIND_ANSWER`/`KIND_REFUSAL`, `REFUSAL_FAMILIES` (the five
      signed Korean names, the exact strings the panel's filter sends), and
      `SCOPE_ALL_KO = "전체 공시"` (R6 §범위 모델's own words). **Decision — an
      unknown refusal family is rejected at the write** (`ValueError`), as is a
      refusal without a family and a category on an answer: an invented family
      would be a row the signed filter can never find. `kind` is additionally a DB
      `CheckConstraint`; the five families are **not** in the schema, because copy
      can be re-signed and these rows cannot be re-collected — a re-signed family
      must not cost a destructive migration.
    - **Open Question 1 — taken as stated**: the turn is stored as the reader saw
      it; **no portfolio/holdings column, no structured tool payload**. Nothing
      changed about the promise, so nothing was raised to the operator.
    - **익명 세션 is derived, not materialized** (R7's 집계면): a `GROUP BY
      session_hash` over the turn table + one follow-up query for each page's
      마지막 범위. One place a session can be written, so nothing can drift.
    - **Wiring**: `create_app(conversations=…)`'s **default is now
      `DbConversations`** over the app's own lazy engine (`session_factory(app.state)`),
      exactly the mailer's seam shape; no route changed. `EmptyConversations`
      stays exported for a caller that wants an empty source. `DbConversations`
      takes a **session factory** (`Callable[[], Session]`), opens one session per
      read and rolls it back — `deps.get_session`'s rule, since the port's methods
      take no session. `tests/test_web_ops.py`'s fixture now passes
      `DbConversations(factory)` over its in-memory SQLite, so the three tabs are
      exercised against the real implementation.
    - **Anonymity is asserted, not remembered**:
      `tests/test_web_conversations.py::test_no_conversation_column_can_name_a_person_and_none_joins_an_account`
      walks both tables' columns and foreign keys. **Do not add a foreign key to
      either table** (in either direction) — the test fails on any.

19. **`P6.S2` landed the five tools — the shapes `P6.S3`/`P6.S4` build on, and the decisions taken.**
    Package: **`src/mijual/agent/`** — `context.py` (`ToolContext`) · `tools.py` (the five +
    `Citation`/`ToolResult`/`call_tool`) · `copy.py` (the Korean strings, with provenance) ·
    `declarations.py` (`TOOL_SPECS` + `declarations()`). Importing it costs **no SDK, no
    credential, no connection** (verified: `google` is absent from `sys.modules` after
    `import mijual.agent`, and google-genai is not even installed in this venv).
    - **`ToolResult` — what `P6.S3` consumes.** `tool` · `fact_row` (the signed mono 도구 행,
      already composed — S5 renders it verbatim) · `payload` (JSON-ready verified-contract
      values, fed back as the function response) · `citations: tuple[Citation, ...]` ·
      `ok`. Plus `.evidence` (unique rcept_no, reading order) and `.quotes` (verbatim, unique)
      — **exactly `record_turn`'s 근거 rcept_no 목록 and 인용 칩 원문**, so `P6.S4` persists a
      turn by unioning the turn's results, never by re-reading the prose. `.response()` packs
      `{ok, fact_row, result, citations}` if S3 wants one object. `Citation` =
      `rcept_no` + optional `quote`/`span`/`field_key`, with **`quote is None` meaning the
      API-tier citation** (R3: 접수번호 is the handle) — it is *a* citation, not a missing one.
      `citations_in(payload)` walks any contract payload for the `rcept_no`(+`quote`,`span`)
      convention, so a shape added later is cited automatically; multi-part figures (D4) yield
      one citation per addend under the parent's filing number. **`ok=False` exists only where
      the design signs a failure answer** (`save_feedback` → 재시도 행); 0건 is `ok=True`.
    - **`ToolContext` — what `P6.S4` must construct** (frozen dataclass, per request):
      `session` · `today` (KST day, fixed once for the whole turn) · `session_hash`
      (`session_hash_or_new`) · `account=None` · `scope_rcept_no=None` · `settings=None`
      (`.config()` loads on demand). **No tool takes an identity**: the model's declared
      arguments are `query` / `rcept_no` / `text` / `email`, and `get_portfolio()` takes
      *nothing* — asserted by a signature test, which is what makes "no client-supplied
      holdings" structural. **`session` must be a write session when the turn may call
      `save_feedback`**: `record_feedback` flushes and never commits, so the transport owns
      the transaction (a write failure rolls back inside the tool so the turn's later reads
      still work).
    - **Settings field: `operator_contact` / `MIJUAL_OPERATOR_CONTACT`** (`mijual.config`),
      no default and deliberately **no `require_` accessor** — nothing may fail for want of
      it and nothing may substitute for it. Unset → `{"configured": false}` + the row
      `운영자 연락처 → 미정`; the tool never emits an address or a 「준비 중」 line.
    - **Search contract (Finding 15), decided here.** New public loaders in
      `mijual.web.reads`: **`find_corps(session, q, limit=5)`** — the same normalization and
      tier order as `resolve_corp` (종목코드 → 회사명 verbatim → normalized → prefix →
      substring), first matching tier wins, but **several hits are returned** instead of
      declining; and **`load_corp_events(session, codes, today=)`** — every **exposable**
      event of those issuers as `EventView`s, batched through the same `_load_views` 조회 and
      포트폴리오 use, gated twice (persisted verdict **and** derived contract). Past events are
      kept (a lapsed ① is the subject of a 놓친 돈 question, unlike `load_stock`'s 진행 중인
      권리). A **14-digit query is a filing number** and resolves to that single event.
      Ranking = 범위 event first, then the board's own order (upcoming by D-day → open ② →
      추후결정 → past); ordering only, no number derived. Listing is capped at
      **`MAX_SEARCH_RESULTS = 8`** while the row states the true count, so a capped list is
      visible rather than silent.
    - **Decision — a 0건 filing-number search carries a machine `hint` (English, not copy)**
      telling the model to call `get_event` first: a 철회된 event is *readable* (page, locked
      notice, 정정사항 evidence) without being *searchable*, and answering 「찾지 못했습니다」
      about it would be the weaker of two true statements. **S3's system instruction should
      restate this**: a filing number → `get_event`. Note also that 0건 covers two situations —
      no such company, and a company with no exposable event — and the signed sentence is true
      of both because it speaks about 공시, not 회사.
    - **`get_event` returns the detail page's payload, not a copy of it.** The assembly moved
      from `routers/events.py` into **`mijual.web.reads.event_payload(session, detail)`**
      (with `_add_offering` / `_withdrawal`); the route is now one line over it. So the agent
      can quote nothing the page would not show, down to the key. A **withdrawn** event comes
      back as a surface (`state: "withdrawn"`, `notice_ko`, `withdrawal`) and `get_event`
      **prepends its 철회 citation explicitly** — the 정정 후 cell is the verbatim quote under
      the key `after`, the one citation shape the generic walk cannot see. Live-verified on
      썸에이지 `20260805000454`: quote `유상증자 철회`, span `[3445, 3461]`. Non-renderable →
      `found: false` + the signed sentence; **the tool never refuses in prose** (S3 picks the
      family).
    - **Copy provenance — read `mijual/agent/copy.py` before writing any tool row.** Signed
      and transcribed: the search format, the 0건 sentence, `내 포트폴리오 읽기 → 샘플
      포트폴리오 · {n}종목 (구성 예시)`, `의견 저장 → 운영자 검토 대기열`, `구성 예시`,
      `관제 현황판`. **Composed** (in the signed `{도구} → {결과}` grammar, from signed
      vocabulary only, and flagged for `P6.S7`/`P6.REVIEW` to confirm): `이벤트 읽기 →
      {회사} · {유형} · {rcept_no}`, `이벤트 읽기 → 0건`, `내 포트폴리오 읽기 → {n}종목`,
      `의견 저장 → 재시도` (R6: 「실패 시에만 재시도 행」), `운영자 연락처 → {값}/미정`.
      `RIGHTS_TOOL_LABEL_KO` = `① 유상증자` / **`② 전환사채`** (verbatim from R6's example) /
      `③ 주식매수청구권` — note the deliberate difference from the reader-facing chips, which
      carry **no ①②③ numbering** (R1 revision): this is the mono 도구 행 and R6's own example
      numbers it. **No tool writes prose, ever.**
    - **`declarations()` is the one untested path**: google-genai is not installed in this
      venv, so `TOOL_SPECS` (plain data, pinned to `TOOL_NAMES` by test) is exercised and the
      `types.Schema`/`FunctionDeclaration` construction is not. `P6.S3` verifies it on its
      first live call; if the SDK wants `parameters_json_schema` instead, `TOOL_SPECS`
      already holds JSON Schema and the change is one function.
    - **Live corpus, zero spend** (2026-08-22, 12–52 ms per call):
      `이벤트 검색 「대동기어」 → 2건 · ② 전환사채 · 20251016000315 · ① 유상증자 ·
      20260715000369` (R6's example says 1건 — 대동기어 has since filed an ①; the row is the
      corpus's own reading), `「계양」 → 1건` (unique prefix), `「삼성전」 → 0건` (ambiguous *and*
      nothing exposable), 계양전기 `20260724000546` → 3 verbatim quotes + 발행가 확정 전 with
      **no won amount anywhere**, sample 포트폴리오 → 4종목 / 15 quotes / 7 근거.
    - **Suite 121 → 126 passed.** `tests/test_agent_tools.py` also carries the third AST scan
      (`mijual.agent` imports no `mijual.dart`/`collect`/`extract`) — `P6.S4` extends the
      scans, this one is cheap insurance meanwhile.

## Constraints

- **RESPECT THE DESIGN.** Every element of R6's build prompt ships; nothing is dropped, simplified,
  restyled or "improved". `docs/reference/design/` is read-only in this phase — a nit found while
  implementing is fixed in the implementation (or in `P6.S7`), never by editing the record.
- **Agent, not chain** (binding operator addition). The backend runs an autonomous tool-calling
  loop on Gemini function calling: the model chooses the tools, the order, the number of rounds,
  and the moment to answer. A fixed retrieve→prompt→answer pipeline does not satisfy this phase's
  intent, however good its output looks.
- **D-4 is the model decision:** `gemini-3.7-flash`, `GEMINI_API_KEY` from the gitignored `.env`,
  thinking level chosen per task via `ThinkingConfig(thinking_level=…)` (omitting it inherits the
  project preset), every call recording the level it ran at, and every cost figure a ▷ estimate —
  never a billed claim.
- **No claim without a verified verbatim span; no reconstructed quote; no computed number; no
  untagged derived value; no 확정 전 금액; no answer from gate-failed data** (refuse with a family);
  **no fake Q&A history UI**; **no quota copy**; **no spinner or typing dots**; **no alert colour on
  a refusal**. R6 §Hard rules, restated because they are the phase's acceptance criteria.
- **Anonymity is schema-level:** no account, email, IP or user-agent column exists in any P6 table,
  and no join between an account and a conversation is possible. The reply email on `save_feedback`
  is optional and voluntary and lives with the feedback row, not with a conversation identity.
- **The exposure contract is not re-decidable** and **no endpoint re-derives a number** — the agent
  and its tools read `mijual.present` / `mijual.web.reads` like every other surface.
- **No `/ops` route changes** and **no mutation endpoint on the ops surface**; the panel stays
  read-only, and the three tabs come alive purely by the port returning real rows.
- **`mijual.web` and `mijual.agent` must not import `mijual.dart` / `mijual.collect` /
  `mijual.extract`.** The model is reached only through `mijual.agent`, and that seam is asserted
  by a test (Finding 1).
- **Never commit anything under `docs/reference/design/`**, and never invent Korean copy. The
  operator contact string stays unset until the operator supplies it.
- Keep tests terse (repo rule): a few high-value cases per slice, no fixture sprawl. Every slice
  runs `pytest` and, where it touches the frontend, `npm run build` + `typecheck` + `smoke`.

## Open Questions

- **Does a stored turn keep prose derived from a *real account's* holdings?** R7 signs the log's
  columns (질문 · 답변 · 인용) and R7's 사용자 tab shows portfolio **counts, never contents**; an
  anonymous log row whose `answer` names an authenticated reader's 종목 would sit awkwardly between
  the two, even though no join exists and no column identifies anyone. **Stated default for
  `P6.S1`/`P6.S4`:** store the turn as the reader saw it (the log's purpose is 품질 점검 and the row
  is unattributable), but **never add a portfolio/holdings column** and never store the tool's
  structured portfolio payload. If a slice takes a different line, record it here and let
  `P6.REVIEW` judge it. Raise to the operator if it feels like a promise change rather than an
  implementation detail.
- **The 운영자 연락처 string is unset** (Finding 9) — operator-provided at P4/deploy. Until then
  `get_contact` answers honestly. Not a blocker.
- **Is there a rate limit at all, and where does its state live?** `security` says it is an
  operations decision with no UI copy, and P5 already parked login rate limiting in P4 for needing
  cross-process state. `P6.S4` should ship the cheapest honest thing (or nothing) and record which.
- **Does the SSE stream survive the Next rewrite proxy unbuffered in the deployed topology?** P4
  may replace the rewrite with an edge route; if it does, streaming is a deploy concern too. Verify
  locally in `P6.S4`/`P6.S7` and hand P4 the measurement.
- **Carried from P5, unchanged and still not P6's to invent:** the English 404 sentence, the locked
  내 종목 연결 positioning line, the dated 49.2억원 footer figure, and 「샘플 로드 여부」's absent
  backing fact.

## Doc impact

_One line per durable-truth change; `P6.REVIEW` consolidates these into doc versions._

- (`P6.DECOMP`) none — decomposition only; no durable truth changed. Expect this list to grow:
  **`architecture`** and **`backend`** (the new `mijual.agent` package and the re-aimed
  request-path/model boundary), **`api`** (the SSE ask contract + the three ops tabs now serving
  real rows), **`data`** (the anonymous conversation/feedback tables), **`security`** (the
  schema-level anonymity promise moving from "trivially true, nothing stored" to "implemented"),
  **`product`** / **`experience`** / **`frontend`** (the AI 질문 surfaces), **`operations`** (agent
  spend, rate limiting, the `get_contact` deploy value), **`qa`** (suite baseline), and
  **`decisions`** if the phase takes a decision worth a D-number — the agent-not-chain architecture
  and the model-in-request-path boundary are both candidates. Note also `P5.REVIEW` note 8: the ops
  개요 tab **parses `docs/current/decisions.md` for `- **Open…` bullets**, so versioning that doc
  can move an operator surface — re-check the open-bullet count after any `decisions` rewrite.
- (`P6.S1`) **`data`** · **`security`** · **`backend`** (+ a line in **`api`**): two anonymous
  tables (`conversation_turn` · `conversation_feedback`) now exist with **no account/email/IP/UA
  column and no foreign key** (feedback's voluntary 답장 이메일 the one signed exception), a
  random-minted session handle, and `mijual.web.conversationstore.DbConversations` wired as
  `create_app`'s default — so 「대화는 익명으로 저장됩니다」 moves from "trivially true, nothing
  stored" to implemented-and-asserted, and `/ops/conversations` · `/ops/sessions` · `/ops/feedback`
  serve real rows with **no route change**. Suite 118 → **121 passed**.
- (`P6.S2`) **`architecture`** · **`backend`** (+ lines in **`api`**, **`operations`**,
  **`security`**): the new top-level package **`mijual.agent`** exists (tools + declarations +
  `ToolContext`) and reads persisted rows only — no spending module, no HTTP, no model call yet,
  asserted by a third AST scan; `mijual.web.reads` gains **`event_payload`** (the detail card's
  single assembly, now shared with the agent — `GET /events/{rcept_no}` is unchanged byte for
  byte), **`find_corps`** (multi-candidate issuer lookup, unlike `resolve_corp`'s
  unique-or-decline) and **`load_corp_events`** (exposable events as views); and
  `Settings.operator_contact` / `MIJUAL_OPERATOR_CONTACT` is the new deploy setting the product
  answers 미정 for until the operator supplies it. Suite 121 → **126 passed**.
