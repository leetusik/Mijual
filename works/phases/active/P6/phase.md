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

20. **`P6.S3` landed the agent core — the entry point, the event vocabulary, the gate rule,
    and two live-measured SDK facts `P6.S4` must not rediscover.**
    New modules in `src/mijual/agent/`: **`loop.py`** (the turn) · **`client.py`** (the agent's
    own Gemini client + the neutral message/chunk types) · **`citations.py`** (the gate) ·
    **`events.py`** (the typed stream) · **`instructions.py`** (the system instruction).
    `copy.py` gained the five signed refusal sentences. Suite 126 → **130 passed**.
    - **Entry point:** `run_turn(ctx, question, history=(), *, client=None, budget=None,
      now=None) -> Iterator[AgentEvent]` (`mijual.agent.loop`, re-exported from
      `mijual.agent`). A **sync generator**; `P6.S4` adapts it to SSE and the reader's
      「중지」 is simply the consumer closing it (nothing is retracted, nothing is emitted).
      `history` is `Sequence[HistoryTurn(question, answer)]` — plain prose, because chip
      numbering is per answer (R6-4). `budget` is `TurnBudget(max_rounds=6,
      max_tool_calls=10, max_model_calls=8)`.
    - **Event vocabulary** (`mijual.agent.events`, every one a frozen dataclass with
      `payload()` and `frame()` → `{"event", "data"}`): `tool_row` `{tool,row,ok}` ·
      `citation` `{number,rcept_no,api_tier,quote?,span?,field_key?}` · `text`
      `{text,citations:[번호]}` · `refusal` `{family,text}` · `links` `{links:[…]}` ·
      `footer` `{count,evidence,generated_at,links}` · and the **terminal**.
      **Ordering rule S5 depends on:** a `citation` event is a *definition* emitted
      immediately **before** the `text` event that names its number, so the chip is painted
      with its sentence (R6: 칩은 주장과 동시에 도착; 자리표시·후행 부착 없음). A number is
      defined once per answer — same 근거 = same 번호.
    - **Terminal shape:** one class `TurnEnd` with `status ∈ {done, aborted, error}` (its
      `event` name *is* the status). Fields: `kind` (`answer`|`refusal`) · `answer` (the
      released prose, joined) · `refusal_category` · `scope` · `evidence` · `quotes` ·
      `blocked` · `rounds` · `tool_calls` · `reason` · `usage`. **`P6.S4` calls `record_turn`
      from this object alone** — the five middle fields are literally its arguments, so the
      log can never disagree with what the reader saw. `evidence`/`quotes` are **the chips
      the reader saw**, not the union of tool results (note 19 suggested the union; R7's
      column is 「인용 칩 원문」, so the log replays the answer, not the research).
      `footer` and `links` are emitted **only on `done`** — 중단/오류 has its own signed
      inset row and 재시도, and a footer under a half-answer would read as a finished one.
    - **Citation-gate rule chosen — drop-not-fail, with a verified-string escape.** A
      sentence is released only if (a) every `[[cite:cN]]` id resolves to a citation a tool
      returned, (b) it has at least one such id **or** is verbatim a string a tool payload
      carried, (c) every numeric token appears among the tools' own values (never-compute),
      and (d) every 「…」/"…" span occurs verbatim in tool output. A failing sentence is
      **dropped** — never emitted, never marked — and the count rides `TurnEnd.blocked`. If a
      turn releases **nothing**, the loop states the 검증 미통과 폴백 family itself. A
      budget/error abort is deliberately **not** turned into 폴백 (that sentence would be a
      false claim about the data); it ends `aborted`/`error` with the partial answer intact.
      A tool result naming exactly one filing **lends its citation** to a verbatim string of
      its own, which is what puts a 근거 칩 on 「이 유상증자는 철회되었습니다」 (R6: 거절도
      인용 강제) while leaving the 0건 sentence honestly chip-less.
      **Two id spaces:** the model cites `c7` (assigned when the tool ran, closed set — there
      is no id for a filing no tool returned); the reader sees chip `1` (assigned on first
      use). Honest limit, recorded: the number check is *membership*, not semantics — a small
      integer or a year is effectively always allowed. What it catches is a value that exists
      **nowhere upstream**, which is the shape of every computed or invented figure.
    - **Refusal families are recognised, not generated.** `copy.REFUSAL_SENTENCES` holds the
      five signed sentences verbatim, keyed by the exact `REFUSAL_FAMILIES` strings the R7
      filter sends; the gate cuts a family sentence out of the stream and emits it as a
      `refusal` event. A paraphrase is therefore not a softer refusal — it is uncited prose
      and gets dropped. `copy.family_of()` is exact-match only.
    - **Client + ledger location: `mijual.agent.client`, per turn.** `AgentGeminiClient`
      (model `gemini-3.7-flash`, lazy `google.genai` import, key resolved on first *use*,
      **AFC disabled** so the loop is ours). Budget: `max_calls` raises `CallBudgetExceeded`
      **before** the call. Ledger: `UsageLedger.payload()` rides `TurnEnd.usage` (calls ·
      tokens · `thinking_levels` · `cost_usd_estimate`) and `.render()` gives the ▷ line for
      `P6.S4`'s log. Nothing was lifted into a neutral module and `mijual.extract` is not
      imported — the two clients diverged immediately (JSON vs. streamed tool calls).
      **Errors carry the exception type name only** (`GeminiError("ClientError")`), never a
      message that could contain a URL.
    - **Thinking level: `LOW`, and it is a decision.** D-4's rule for an unlisted task, and
      three reasons to stay: the surface is free and unlimited (R6-5) so per-turn cost is the
      product's cost; SSE's first token is reader-visible latency and thinking precedes it;
      and 인용 강제 / never-compute / 거절 가족 are enforced **structurally**, so a cheaper
      level cannot produce an unverified claim, only a blocked one. **Measured:** five live
      turns at LOW, `blocked == 0` on every one — the marker protocol held. Raise it on
      `AgentGeminiClient(thinking_level=…)` if a measurement says tool choice suffers; the
      level is recorded per call either way.
    - **⚠ Two live-measured SDK facts.** (1) **Gemini 3.x requires `thought_signature`**: the
      opaque bytes on a function-call part must be echoed back in the conversation history or
      the *second* round dies with `400 INVALID_ARGUMENT`. `ModelCall.thought_signature`
      carries it; never inspect, log or store it. (2) The live model writes
      `…입니다.[[cite:c2]]` with **no space** after the full stop — a sentence splitter that
      requires whitespace glues a whole answer into one sentence carrying every chip at once.
      Both are fixed here; both would have been invisible to a chain-shaped implementation.
    - **Live smoke, 2026-08-22 (▷ $0.0942 total, 28 calls, ~103k tokens, all LOW):** the model
      chose a different tool path in every turn and, on a 0건 search, **re-searched with a
      corrected query on its own**. 확정 전 came out exactly as R6-7 signs it (cited known
      facts, then 금액만 거절); 철회 produced the signed 3-part refusal with a 근거 칩; 계산
      요청 produced the fixed redirect with **zero** tool calls forced.
    - **Open copy point for `P6.S7`/`P6.REVIEW`:** the live 확정 전 answer stated
      「예정발행가액은 3,200원입니다」 (1차 발행가액 반영) before refusing the amount. That is
      a gate-passing field the event page itself renders, so it is a *published planned*
      figure rather than a 확정 전 금액 claim — but it is worth confirming against R6's
      「확정 전 금액 — 금지」 with a real browser beside the detail page.
    - **Nit found, deliberately not fixed here:** `copy.BOARD_POINTER_HREF = "/board"` (landed
      in `P6.S2`) is a **dead route** — `frontend/lib/routes.ts` has `ROUTES.board = "/"` and
      there is no `frontend/app/board/`. `P6.S3` serves link *kinds* (`{"kind":"board"}`) and
      no hrefs at all, so nothing in this slice depends on it. **`P6.S5`/`P6.S7` should map
      the pointer through `ROUTES`** rather than render that string.

21. **`P6.S4` put the agent on the wire — the endpoint contract `P6.S5`/`P6.S6` build against,
    and five decisions that are cheaper to read than to rediscover.**
    New modules: **`src/mijual/web/ask.py`** (the decisions) + **`src/mijual/web/routers/ask.py`**
    (the route), the `mijual.web.portfolio` / `routers/portfolio.py` split this codebase already
    uses. Suite 130 → **136 passed**.
    - **The contract.** `POST /ask`, CSRF header required (service-wide guard, no exception),
      body `{question, scope_rcept_no?, session?, history?}` → `text/event-stream; charset=utf-8`
      with `Cache-Control: no-store` and `X-Accel-Buffering: no`.
      **Frame one is always `event: session`** carrying `{"session_hash", "scope"?}` — the browser
      keeps it in `sessionStorage` (R6-5/6) and sends it back as `session` on the next turn; it is
      **never a cookie**, because the thread is tab-scoped by design and a cookie is exactly the
      identifier the schema refuses. Then the agent's own events by their `frame()` —
      `tool_row` · `citation` · `text` · `refusal` · `links` · `footer` — then **exactly one**
      terminal, `done` | `aborted` | `error`. The transport reorders nothing and invents no field.
      `history` is oldest-first prose, capped at the newest **8** turns × 8 000 chars (dropped, not
      refused, so a long-lived tab keeps working). Pre-stream failures are the ordinary envelope
      with **no Korean**: `invalid_question` · `invalid_scope` (a 범위 that is not 14 digits is
      refused, never silently ignored — that would answer a different question) · `csrf_required` ·
      `rate_limited` · `invalid_request` (422). **Once streaming, the only failure is the typed
      `error` terminal** — never a half-frame. **⚠ There is no signed Korean copy for a pre-stream
      envelope**; `P6.S5` decides what the widget shows for one, and the nearest signed thing is
      R6's 중단 inset + 「재시도」.
    - **No stop endpoint** (the `DECOMP` table's "ask · stop" is superseded, deliberately). 중지 =
      the reader aborts the fetch = the consumer stops pulling = `run_turn`'s generator is closed.
      A stop route would need a server-side registry of *running* turns whose only job is to cancel
      what the socket already cancels. Nothing is retracted; released text stands.
    - **⚠ A streaming response cannot use `WriteSession` — or any `yield` dependency.** FastAPI
      tears a `yield` dependency down when the **handler returns**, which for a `StreamingResponse`
      is *before the first frame*. So `ask.py` opens its own session inside the body iterator and
      commits it from the response's **`BackgroundTask`** — the one hook Starlette runs on **both**
      exits (stream finished **and** client disconnected; measured, not assumed). Do not "simplify"
      this back onto `deps.WriteSession`. The transport owns the transaction, so the tools'
      `save_feedback` flush becomes real on the same commit.
    - **⚠ Absorb an event *after* yielding its frame, never before.** Measured 2026-08-22: with the
      obvious ordering, a turn cut mid-answer stored **one sentence more than `curl` had been
      sent** — the sentence was produced, absorbed, and then lost to the cancelled send. Being
      resumed past a `yield` is proof the consumer took the previous frame. Any later change to
      `AskTurn.frames()` must keep that order.
    - **Abort-persistence policy, decided.** `done`/`aborted`/`error` all persist **from `TurnEnd`
      alone** (note 20's rule, unchanged). A **disconnect has no terminal**, so the row is built
      from the frames actually written (`_Released`) — the same released strings in the same order,
      asserted equal to the terminal's fields by test. A 중지 **before the first sentence** stores
      nothing (no 답변 to replay, no 거절 to categorise; the row would be noise in a log whose
      purpose is 품질 점검). **The row records what the reader saw and nothing about the
      mechanism**: R7 signs the columns and there is no status bit, so `aborted` vs `error` lives in
      the server log — **no new column was added** (note 18's rule held). A `record_turn` failure
      rolls the **whole** transaction back, feedback included: a 대기열 row whose 원 대화 링크 points
      at a turn that was never written is worse than no row.
    - **Rate limiting (Open Question 3), decided — ship the cheap honest thing.**
      `ask.TurnLimiter` on `app.state.ask_limiter`, in process, **persisting nothing and holding no
      address**: (a) `max_concurrent=6` — an integer, unevadable, and the ceiling that actually
      bounds money and latency; (b) 30 turns / 300 s **per session handle** — bounds a runaway tab
      and is *trivially evaded* by minting a fresh handle, which is stated rather than hidden. No
      IP/UA counter even in memory: it would put the forbidden identifier in the process on the
      strength of "it's only in memory". A refused turn is `429 rate_limited` in the plain envelope
      with **no `message_ko` and zero UI copy anywhere** (R6-5: 질문 수 무제한 — a limit that is not
      shown must not be implied). An in-flight slot has a 600 s TTL so a lost one self-heals instead
      of wedging the endpoint. **Per process** — P4 owns cross-process state, same parking as login
      rate limiting.
    - **Injection seam: `create_app(agent_client=…)` — a *factory*, not a client** (`Callable[[],
      ModelClient] | None`), because the call budget and the ▷ ledger are per turn. `None` → each
      turn builds its own live `AgentGeminiClient`. Tests and the SSE smoke pass
      `lambda: ScriptedModel(...)`, so the suite spends nothing and **`GEMINI_API_KEY` is required
      neither to import nor to `create_app`** (verified: with it unset, `create_app(Settings())`
      builds and `google` is absent from `sys.modules`). Tests fill `app.state.session_factory`
      directly — the endpoint opens its own session, so there is **no dependency to override**.
    - **▷ ledger: server log only** (Finding 14). `TurnEnd.usage` is rebuilt into a `UsageLedger`
      and rendered by its own `.render()`, so there is one renderer and one rate card:
      `agent turn done · answer · rounds 3 · tools 2 · blocked 0 · calls 3 (0 failed) · tokens … ·
      thinking LOW · ▷ $0.0027 estimated (…, not billed)`. A disconnect logs
      `agent turn disconnected · … ▷ $0.0000`. No signed ops panel gained a row.
    - **The boundary re-aim (Finding 1), landed honestly.** The sentence is now three clauses, each
      with its own scan: **no OpenDART call in any request path** (`test_web_smoke`, unchanged
      target, re-aimed docstring) · **the model is reached only through `mijual.agent`** — new scan
      `test_the_model_is_reached_only_through_the_agent_package`, banning `google`/`openai`/
      `anthropic` under `src/mijual/web/**` · **`mijual.web` itself speaks HTTP in exactly one
      file** (`test_web_vocky`, docstring made precise) · plus S2's third scan keeping spending
      modules out of `mijual.agent`. The old absolute wording was also corrected in
      `mijual/web/__init__.py`, `mijual/web/app.py`'s **OpenAPI `DESCRIPTION`** (an outward
      surface) and `mijual/agent/__init__.py`. `docs/current/*` untouched — see *Doc impact*.
    - **SSE buffering (Open Question 4) — measured, four ways, all unbuffered.** `curl -N` with
      per-line timestamps against uvicorn directly, and through the Next `/api` rewrite on **both**
      `next dev` 16.3.2 (Turbopack) and a production `next build && next start`: six distinct
      arrival times across 6.5 s, proxy timings within ~30 ms of direct, and `cache-control` /
      `x-accel-buffering` / `transfer-encoding: chunked` all travelling through untouched. So
      **`P6.S5` can rely on incremental SSE through the rewrite locally.** Two honest limits: P4's
      *deployed* topology (edge route / CDN / nginx) is still unmeasured — `X-Accel-Buffering: no`
      is set for the nginx case — and **there is no heartbeat**, so a proxy idle timeout could cut a
      long tool round (the turn is sync and blocking, so a keep-alive comment needs a timer; not
      built, recorded for P4/`P6.S7`).
    - **Two facts for whoever runs the product locally.** `MIJUAL_API_ORIGIN` is read by
      `next.config.ts` at **build** time, so `next start` serves whatever origin was set during
      `npm run build` (a `next start` against the default `:8000` was the first failure hit — a real
      P4 deploy note). And the operator's dev Postgres does **not** yet have `conversation_turn` /
      `conversation_feedback`: P2 has no migrations and `create_all` runs from the
      collect/gates/pipeline entry points, so a local end-to-end run needs the tables created first.
      **No live model call was made from the endpoint in this slice** — S3 proved the client live,
      and `P6.S5`/`P6.S7` exercise the whole wire in a browser.

22. **`P6.S5` landed the desktop surface — the store API `P6.S6` builds on, the
    sessionStorage keys, the rendering decisions, and three contract pinches.**
    New: **`frontend/lib/ask.ts`** (the store) · **`frontend/components/ask/`**
    (copy · links · hooks · provider · surface · launcher · widget · answer ·
    citation · composer + two CSS modules) · `lib/api.ts` gained `ASK_PATH` /
    `streamAsk()` / `decodeSse()` · `lib/ask.test.ts` (4 cases). Edited: only
    `components/chrome/SiteChrome.tsx`. **No backend file changed** (pytest still
    **136 passed**); `frontend/app/ask/page.tsx` is still P5's bare shell.
    - **The store is module-scoped, and that is the architecture.** R6's
      「스트리밍 중 이동/전환에도 끊김 없음」 rules out owning the fetch in a page,
      so the thread lives in `lib/ask.ts` (no React import) and `AskProvider`,
      mounted once in `SiteChrome` (the client half of the persistent root
      layout), only hands it out through context. The provider holds **no state**,
      so a frame mid-stream re-renders the subscribed views and never the pages.
      **`P6.S6`'s page is a second view over the same store — do not build a
      second one, and do not lift state into the page.**
    - **The store API, verbatim** (`AskStore` in `lib/ask.ts`): `subscribe` ·
      `getSnapshot` · `getServerSnapshot` · `hydrate()` · `open()` · `close()` ·
      `toggle()` · **`setPageScope(scope|null)`** (a page's ambient 범위, applied
      **at open** and never over a 범위 the reader chose) · **`setScope(scope)`**
      (what the 질문 스트립 calls) · `clearScope()` · **`ask(question)`** ·
      **`stop()`** (= abort; there is no stop endpoint) · **`retry(turnId)`**.
      Hooks: `useAskState()` (a `useSyncExternalStore` snapshot), `useAskStore()`,
      `useDesktop()` (`min-width: 481px`, false until mount). State shape:
      `{open, hydrated, scope, scopeChosen, sessionHash, turns}` where a `turn` is
      `{id, question, scope, blocks, chips, links, footer, status, answer}` and
      `status ∈ pending|streaming|done|aborted|error`. A `scope` is
      `{rcept_no, name}` — **the 종목 name is required**, because the signed chip is
      `범위: {종목} · {rcept_no}`, so S6's strip must pass it.
    - **sessionStorage: one key, `mijual.ask.thread`** (`THREAD_KEY`), `{v: 1,
      scope, scopeChosen, sessionHash, turns}`. **`open` is deliberately not
      persisted** (a widget that reopened itself on reload is unsigned behaviour);
      a restored `pending`/`streaming` turn is settled to **`aborted`**, because
      the fetch died with the page and that *is* 「연결이 끊겼습니다」. Never
      `localStorage`, never a cookie. **S6 reads this key through the store and
      writes nothing of its own.**
    - **Pre-stream failure rendering, decided (S4's open point).** A `429
      rate_limited` / `invalid_question` / dead-service failure ends the turn with
      **no blocks** and shows R6's one 중단 inset row 「연결이 끊겼습니다 — 답변이
      여기서 중단되었습니다.」 + 「재시도」. No code, no English, no invented
      sentence — and **no quota copy anywhere**, so a limit that is not shown is
      never implied. The same state renders a reader's 중지, a stream cut without a
      terminal, and a typed `error` terminal: R6 writes exactly one sentence for
      「중단/오류」.
    - **의견 확인 — the surface prints it, not the agent** (the plan assumed
      otherwise). `save_feedback` returns `{"saved": true}` + the row 「의견 저장 →
      운영자 검토 대기열」 and its docstring assigns the confirmation to the surface;
      so `Answer.tsx` prints 「의견을 저장했습니다 — 운영자가 확인합니다.」 after a
      **successful** `save_feedback` row, off the tool's own `ok`. A failed save
      adds nothing — the row already **is** 「의견 저장 → 재시도」.
    - **⚠ Three contract pinches for `P6.S6`/`P6.S7` (no backend was patched).**
      (1) **필드로 이동** is a signed footer context link with **no link kind on the
      wire** (`_links` serves `dart` · `event` · `board` · `stocks` only) and no
      field anchor on the detail page — not rendered, not invented. (2) A footer
      can carry **up to 8 links** (3 filings × dart+event, + board, + stocks): the
      answer turn measured here rendered 5, which is a busy row for a signed
      `근거 N건 · {rcept_no} · {시각}` footer — a fidelity call for S7. (3) The
      footer's signed format names **one** `{rcept_no}`; several 근거 are printed
      with the format's own `·` separator rather than dropping any.
    - **Two strings R6 does not write, reused and flagged** (phase rule: reuse the
      nearest signed one): the composer's idle button = R6-2's 「직접 질문 입력 →」,
      and the question field's + the panel's accessible name = 「AI 질문」.
      `P6.S7`/`P6.REVIEW` should confirm both against the record. Everything else
      is transcribed with provenance in `components/ask/copy.ts`; the agent's own
      words (도구 행, the five refusal sentences) are rendered **verbatim from the
      wire** and never restated on this side.
    - **Launcher fidelity notes.** The two half-rings share one `ringdrift` with
      the DOM order the fix requires (top half → planet → bottom half); the band
      and both rings carry `data-motion="tick"` so `shell.css` freezes them, and
      the module adds its own reduced-motion block for the **transitions and the
      hover scale**, which that convention cannot express. **The 열림 상태 exists**
      (mark fades, 16px × appears, `inert`) and sits *behind* the opaque widget,
      which covers that corner exactly — that is how both 「런처는 열리면 숨음」 and
      §런처 마크's open state are honoured at once. Offsets are
      `right/bottom: var(--space-6)` for both the launcher and the widget (the
      record fixes the corner, not the inset).
    - **Verified against the real wire, spend-free.** S4's
      `create_app(agent_client=lambda: ScriptedModel(…))` produced the actual SSE
      bytes for an answer turn and a 철회 refusal; feeding them through the client
      **in 3-byte chunks** (splitting frames *and* multi-byte Korean) reproduced
      the chips, the 도구 행, ①②③, the API-tier citation and the footer exactly.
      `decodeSse` is a pure buffer-in/buffer-out function for this reason.
    - **Nothing new is `position: fixed`** except the launcher + widget
      (`app/shell.css`'s `.backdrop` is P5's), and both are `right/bottom`-anchored
      so neither can widen the document. Real-browser fidelity is `P6.S7`'s.

23. **`P6.S6` finished the surfaces — the page, the mobile page, the 질문 스트립 and
    every entry point, measured in a browser against a spend-free scripted agent.**
    New: **`frontend/components/ask/`** `AskPage.tsx` + `AskPage.module.css` ·
    `QuestionStrip.tsx` + `Strip.module.css` · `presets.ts` · `AskPageScope.tsx`,
    and **`frontend/components/event/fieldOrder.ts`**. Edited: `app/ask/page.tsx`
    (P5's shell replaced whole), `ask/copy.ts` (+3 signed strings), `ask/index.ts`,
    `ask/Ask.module.css` (one ≤480px block), `event/EventDetail.tsx`,
    `event/Fields.tsx`. **The store gained nothing** — `lib/ask.ts`, `lib/api.ts`
    and every S5 component are byte-unchanged, and **no backend file** was touched
    (pytest still **136 passed**; `build` · `typecheck` · `smoke 15/15` green).
    - **The page is S5's second view, and `close()` is how it arrives.**
      `AskPage` reads `useAskState()` and calls the same store; on mount it calls
      **`store.close()`**, which is 「위젯이 열려 있으면 닫고 리다이렉트」 for the
      nav slot, the footer link and a typed URL too — the widget header's
      external-link was only one of the ways in. `close()` touches no turn, so a
      mid-stream arrival renders the growing snapshot (「대화·범위 그대로」).
      `AskSurface` already renders neither launcher nor widget on `/ask`.
    - **The 340 rail's contents are a decision, and they are flagged.** R6 fixes
      the width and 「레일만 패널」 and writes **nothing** about what is in it (no
      R6 cards exist in this repo — §Context). The rail is a **`CraftPanel`**
      (R2.1's own — the record contrasts 「패널·브래킷 없이」 with 「레일만 패널」)
      carrying the four signed things this surface has: the 범위 chip
      `범위: {종목} · {rcept_no}` **+ its ×** (the widget puts it in a header the
      frameless page does not have), 「검증된 필드만 근거로 답합니다 — 모든 답에
      원문 인용」 (R6-2 패널 copy, newly transcribed as `VERIFIED_ONLY_KO`), the
      agent intro and the 세션·저장 line. The page's thread renders **no** intro
      block, so nothing is said twice. ⚠ `P6.S7`/`P6.REVIEW` confirm against the
      record's Page card.
    - **Preset generation rule (`components/ask/presets.ts`), verbatim in one
      sentence:** every served field except `correction_interpretation`, in the
      **page's own reading order**, chip text = the served **`korean_name`**, and
      the chip's text **is** the question sent. The one exception is the question
      R6 itself wrote — `forfeited_share_method` → 「실권주는 어떻게 처리되나요?」
      (result.md §Composition examples). **No sentence template was invented**: a
      「{label}은 어떻게 되나요?」 generator would be invented copy *and* wrong
      Korean for most labels. Gate-blocked fields need no filtering — the contract
      never serves them. A **철회** event yields no presets (the page renders no
      fields and 철회 is the family the agent would answer with), a field with no
      `korean_name` yields no chip, and the strip is capped by nothing: it is one
      horizontally-scrolling line. **`FIELD_ORDER`/`STORY_FIELD` moved out of
      `event/Fields.tsx` into `event/fieldOrder.ts`** so the row order and the chip
      order are one list, not two.
    - **Chip press = `setScope` + `ask` + the reader's surface**, in that order:
      desktop `open()` (the widget), ≤480px `router.push('/ask')`, and on `/ask`
      nothing to open. `setScope` (not `setPageScope`) because pressing a chip
      **is** the reader choosing a 범위. The strip renders no answer and holds no
      state; its last chip is R6-2's 「직접 질문 입력 →」, which opens the surface in
      the event's 범위 and sends nothing (`freeInput={false}` on the page, where
      the composer is the next element).
    - **Ambient-scope lifecycle, decided:** `AskPageScope` (renders `null`) is
      mounted by the event detail page **only** — set on mount, **cleared in the
      effect's cleanup**, keyed by `{rcept_no, name}` values rather than object
      identity. React runs a removed subtree's cleanup before the new subtree's
      effects, so event A → event B lands on B; a lost race would leave `null`
      (= 전체 공시), never someone else's event. Everywhere else the ambient scope
      is null by construction. A **withdrawn** event keeps the ambient scope (R6's
      own Refusal card is a 철회 conversation) while offering no presets.
      Measured live: launcher on detail opens at `범위: 계양전기 · 20260724000546`,
      `×` → `범위: 전체 공시`, and reopening keeps 전체 공시 — the reader's choice
      is never overridden.
    - **Mobile shape.** ≤480px the rail's contents stack **above** the chat (a 340
      rail cannot sit beside a 390 viewport), so the DOM order is rail → chat and
      the desktop layout places the rail into column 2 by grid. The input bar is
      **`position: sticky; bottom: 0`** with `--paper` behind it — nothing new is
      `position: fixed` anywhere. The 44px controls are a **≤480px-only** block in
      `Ask.module.css`: the widget never renders there, so its signed 36px
      composer is untouched. **No auto-scroll on the page** (the widget scrolls its
      own 620px box; scrolling the document under a reader is the ambient motion
      R1 keeps off data surfaces).
    - **`/ask` shows presets when its 범위 is an event**, generated by the same
      rule from a client `GET /events/{rcept_no}`; a failed read or a 철회 event
      yields no chips and **no message** (R6 writes none).
    - **⚠ The one place the record contradicts itself, left unresolved on purpose.**
      R6 §Mobile writes 「메뉴 첫 행 ≥44px」 while §Surfaces writes 「nav 세번째 자리
      「AI 질문」」 — and the mobile sheet mirrors the nav list. P5's shipped order was
      **kept** (AI 질문 = third row, rows 48px, 메뉴 button 44px, both ≥44) rather
      than silently reordering signed chrome. `P6.S7`/`P6.REVIEW` decide; it is one
      line in `chrome/Nav.tsx` if the other reading wins.
    - **Measured, not asserted (headless Chrome over CDP, `next build && next
      start` + uvicorn).** 0 px horizontal overflow at **390** on `/ask`, the ①
      detail page with the strip, the 철회 page and the landing; strip chips 44px
      with the row scrolling (1009 > 358) instead of widening the document; `/ask`
      at 1440 has the rail at **exactly 340px**, a chat column with **no border and
      no background** (프레임 없음) and **zero** `position: fixed` (no launcher);
      the in-place citation block renders **full width with `max-height: 180px` +
      `overflow-y: auto`** at 390. Entry points: nav third slot, footer bottom row
      and sheet row all `AI 질문 → /ask`; the widget's external-link lands on the
      page with the same thread; 뒤로가기 from the page returns to the detail page
      with the conversation intact; `sessionStorage` holds **only**
      `mijual.ask.thread` at every step.
    - **Spend-free end to end.** Everything that would have called a model ran
      against `create_app(Settings(), agent_client=lambda: ScriptedModel(...))`
      (S4's seam) over `tests/test_agent_tools._corpus` in SQLite, served on :8000
      behind the same `/api` rewrite. **No live model call was made in this
      slice** — the answer rendered on the mobile page (도구 행, chip 1, 인용 블록,
      `근거 1건 · … · KST` footer) is the scripted turn. Two facts for whoever runs
      it again: `MIJUAL_API_ORIGIN` is baked at **build** time (note 21), and the
      dev Postgres still has no `conversation_turn` table, which is why the
      scripted app used SQLite rather than writing to it.

24. **`P6.S7` ran the fidelity pass live — three fixes, and what `P6.REVIEW` can
    trust as measured rather than asserted.** Full table, ▷ ledger and the
    consolidated operator questions in `slices/P6.S7/result.md`.
    - **What actually ran.** uvicorn over the operator's **dev Postgres** + a
      **live** `AgentGeminiClient` + `npm run build && npm run start` + headless
      Chrome over CDP: 41 stages / ~120 scripted checks at **1440 · 768 · 481 ·
      480 · 390**, **25 live turns** (24 stored), 27 stored quotes and every
      numeral in 24 stored answers verified against the served payloads.
      ▷ **$0.0743 estimated measured exactly on 8 turns** (18 calls, 87,908
      tokens, thinking **LOW** throughout) → **▷ ≈ $0.23 for the pass**, never
      billed.
    - **⚠ Fix 1 — R6's 스트리밍 state was not reaching a real browser, and the
      cause is a header.** Next's router gzips whatever it proxies (`compress`
      defaults to on) including `text/event-stream`, and a gzip encoder holds the
      stream until it has a block: every frame of a turn — 도구 행, sentences,
      chips, footer — painted **in one burst under 10 ms** after a multi-second
      「답변 준비 중…」. `P6.S4`'s measurement was right for what it measured:
      **`curl` sends no `Accept-Encoding`, a browser sends `gzip`**. The fix is
      one directive in `mijual.web.ask.SSE_HEADERS`: `Cache-Control: no-store,
      **no-transform**` — the standard's own "do not re-encode" (RFC 9111
      §5.2.2.6), which `compression`'s `shouldTransform` honours, and so do nginx
      and the CDNs **P4** will meet. Measured after: tool row 1 at 5.5 s, tool row
      2 at 8.7 s, first sentence at 11.0 s — prose grows and 중지 is pressable.
      **Longest observed inter-frame gap with the live agent: 6.0 s** (first
      model round) — and **there is still no heartbeat**, so a proxy idle timeout
      under ~10 s would cut a legitimate turn. *Do not "simplify" that header
      back to `no-store`.*
    - **⚠ Fix 2 — a saved 의견 ended in a refusal that contradicted it.** The
      reader saw 「의견을 저장했습니다 — 운영자가 확인합니다.」 and 「이 데이터는
      검증을 통과하지 못했습니다.」 in the same bubble. Structural, not a model
      slip: nothing about a feedback save is citable, so every sentence was
      dropped at the gate and `loop._finish` selected the 폴백 family because
      nothing had been released. Now `_feedback_only(results)` (all results are a
      **successful `save_feedback`**) skips the fallback, emits **no event** —
      the confirmation is already on screen from the surface — and records the
      signed sentence as the turn's `answer` so the 대화 로그 replays what the
      reader read. Deliberately narrow: a turn that *also* read an event and then
      said nothing verifiable has genuinely failed to verify something and keeps
      the 폴백.
    - **Fix 3 — the dead `/board` route left the agent's reach.**
      `copy.BOARD_POINTER_HREF` was **removed**, not corrected: the frontend owns
      every route, the surface builds the pointer from the `{"kind":"board"}`
      link, and a path string in a tool payload is a string the gate's
      verbatim-string rule would let the model *say*. 0 of 24 stored answers ever
      contained it.
    - **Measured, not asserted, for `P6.REVIEW`.** The **ring reading test
      passes** — a 27-point hit grid over the paused mark shows the planet's band
      on top where the ring's upper half crosses it and `ringFront` on top where
      the lower half does, with the ring visible outside the planet on both sides
      (one ring, through a sphere — not the flat sticker the round paid for).
      Launcher 68×50 + 22×22 mark + 40×13 half-rings + 11×11 tail, hover mark-only
      1.35 with the frame fixed, active 1.15, open 16px × with ±45° 1.5px bars,
      **reduced motion stops band · drift · transitions · hover scale**, and the
      motion exception appears on **no** data surface (`/stocks` `/events` `/portfolio`
      carry the launcher's three animations and nothing else; `/ask` carries none).
      Widget **440×620** opaque `#0e1a15`, fixed, **no backdrop and no dim**, 28px
      header icons, **landing layout byte-identical before and after opening it**.
      Caret **7×15 `--live` `caretblink 1s steps(1)`**; footer fade =
      `--dur-base`; 중단 keeps the partial at **`--ink-2`** on a `--surface-inset`
      row with 재시도 and **no footer**; `--alert` appears nowhere. Chips mono
      **10px** `--live` with the `rgba(95,208,165,.4)` border, blocks open to
      `--surface-inset` + left 2px `--live` and **re-tap closes**. **27/27 stored
      quotes byte-identical** to a served payload value; **0 numerals missing**
      across 24 stored answers. All five refusal families exercised live. `/ask`
      rail exactly **340px**, chat frameless, **zero `position: fixed`**; the
      **480/481 boundary is exact**; **0 px horizontal overflow** on every touched
      page at 390 including one with a rendered answer and an open citation block;
      the corner is the launcher's alone on six pages and **no vocky element
      exists**. The ops loop closes: 24 real rows, both filters working with the
      five signed Korean names as values, the 대기열 holding the saved 의견,
      nothing mutable.
    - **Deployment, not schema (P4 inherits it).** The `P6.S1` tables were created
      in the dev Postgres with `mijual.db.session.create_all` — additive and
      idempotent, **16 → 18 tables**, no existing table touched, still zero
      foreign keys. **P4 must run this before the first `POST /ask`**: P2 has no
      migrations and `create_all` otherwise runs only from the
      collect/gates/pipeline entry points.
    - **⚠ The ▷ ledger is invisible under a default `uvicorn`.** It is `log.info`
      on `mijual.web.ask`, and uvicorn configures only its own loggers, so the
      root stays at `WARNING` and **agent spend is recorded nowhere**. Verified
      both ways (0 lines plain; the line appears with `logging.basicConfig`).
      Left unchanged — logging configuration is P4's — and raised as an operator
      question.
    - **Judged, not changed** (each with its reasoning in `result.md` §4):
      the mobile menu keeps **AI 질문 in the third slot** (§Surfaces states a
      position with an ordinal and the sheet mirrors the nav; §Mobile's
      「메뉴 첫 행 ≥44px」 carries a touch-target floor that is met — rows 48px,
      button 44px), the 확정 전 「3,200원」 is a **published planned figure the
      detail page itself renders** (「예정발행가액(4,985원 -> 3,200원)」 in the
      gate-passing 정정 해석) so the answer refused the *amount* exactly as R6-7
      asks, and 필드로 이동 · the 7-link footer · raw numerals in prose · the ops
      ISO timestamps · 철회-by-name · a 푸터 under a refusal · Korean glyphs inside
      the mono 도구 행 are all **catalogued** rather than "improved".
    - **Two method gotchas worth more than they look.** (a) A `Response.clone()`
      tee installed to capture raw SSE bytes **buffers**: it reported one
      2,096-byte chunk where the wire had seven spread frames, which would have
      hidden fix 1's before/after. Time the **wire** with `curl` and the
      **reader** with a `MutationObserver`, never the tee. (b) P5.S19's
      re-measure rule held again — five FAILs were probe artifacts
      (`span:nth-child(3)` matching a ring instead of the close glyph, a
      transparent `.close` overlay winning `elementsFromPoint`, an `active`
      transform read mid-transition, the sticky bar measured on the `<form>`
      instead of its `.bar` wrapper, and **`/ops/feedback` being the vocky 관찰
      뷰 while the `save_feedback` 대기열 lives on the Conversations tab**).

25. **`P6.REVIEW` — verdict `pass`. What was verified independently, and the one thing left open.**
    Full record in `slices/P6.REVIEW/result.md`. Validation re-run fresh: **pytest 137 passed**
    (and **again after the `decisions` rewrite**, because the ops 개요 tab reads that doc),
    frontend `build` · `typecheck` · `smoke 15/15` green, `workflow validate` green.
    - **The keystone was checked in the code, not accepted from the notes.** `call_tool` is invoked
      from **exactly one place in the whole codebase** (`loop.py:213`), dispatching on the name the
      model supplied; `run_turn`'s only caller is `web/ask.py:480`; `messages` starts as history +
      question with **nothing prefetched**; the turn ends at `if not calls: break`. The one place a
      forced call could have hidden — a scoped turn — deliberately does **not** hide one:
      `instructions.scope_line` uses a plain `resolve_event` read precisely so 범위 costs no tool
      call, and says so. **Agent, not chain: met structurally.**
    - **`docs/reference/design/` is byte-untouched across every P6 commit** (`git diff 0f0bb23..HEAD
      -- docs/reference/` empty), and so is `docs/` overall — so no slice versioned a doc, which is
      the correct per-phase rule. **No `/ops` route or component changed** either; the three tabs
      came alive purely through `create_app`'s new default.
    - **The five refusal sentences in `agent/copy.py` are byte-identical to R6 `result.md`
      §Proposed copy**, as are the SSE strings, the 의견 confirmation, the 세션 line and the two
      패널 lines. Copy fidelity was checked at the source, not via summary.
    - **⚠ The one shortfall against the record: 「필드로 이동」** — R6 signs three footer context
      links and two ship. Judged **non-blocking** and escalated rather than fixed, because building
      it faithfully is impossible without invention: the link kinds are a closed set, the detail
      page has no per-field anchor, and the record never says *which* field an answer citing several
      should point at. It is entangled with the footer's link density. **A `P6.F1` only makes sense
      after the operator decides "draw it or strike it"** — and it is now the one still-open reading
      in `decisions`, so it surfaces on the ops 가동 전 미결 panel rather than living only here.
    - **Every other catalogued item was re-judged and confirmed correctly catalogued**: 철회-by-name
      is the exposure contract working as designed (not P6's to re-decide), raw numerals are R6's own
      instruction plus never-compute (改 would have been the violation), the refusal 푸터 and the
      mobile-menu row are record ambiguities, and the ops timestamp/cross-link items are P5 surfaces
      P6 was constrained not to touch.
    - **11 doc versions** consolidated: `architecture` v0004 · `backend` v0003 · `api` v0003 ·
      `data` v0005 · `security` v0004 · `product` v0005 · `experience` v0004 · `frontend` v0004 ·
      `operations` v0006 · `qa` v0004 · `decisions` v0006 (**D-20** agent-not-chain, operator
      verbatim and dated 2026-08-22 · **D-21** the boundary re-aimed not relaxed · **D-22** the
      contact honest-unset; **D-4** gained the `agent_turn` LOW row, **D-10**'s SSE clause landed).
    - **⚠ Ops 개요 open-bullet re-check (P5.REVIEW note 8), done by rendering not by assuming:**
      **1 → 3** bullets, each with a sensible decision label and verbatim body. The two new ones are
      deliberately only the items **the operator alone can close** (the 연락처 string; 「필드로
      이동」). P4's engineering to-dos — create the conversation tables before the first `POST /ask`,
      preserve `no-transform` + `X-Accel-Buffering` through every hop with idle timeouts above ~10 s,
      install a root logging config — were kept **off** that panel and put in `operations`: they are
      미완, not 미결.
    - **Hygiene note for the orchestrator** (not a defect): `phase.json` still reads
      `status: "planned"` while every slice is `done`; `review-phase P6 --verdict pass` transitions it.

26. **`P6.F1` made the agent speak the product's numerals — the mechanism, and what it
    deliberately does not reach.** Review finding 4, operator disposition 2026-08-23
    (verbatim: 「make it 3,200원. dk how」). Suite **137 → 138 passed**. Full record in
    `slices/P6.F1/result.md`.
    - **New module `src/mijual/agent/figures.py` is the whole mechanism**, and it is
      **presentation, never computation** — twice over, so the never-compute rule is
      untouched.
      (1) **The tool contract serves the reader's form.**
      `ToolResult.__post_init__` runs `figures.with_display(payload)`, putting a
      **`value_display`** string beside every *figure*'s exact `value`
      (`"3200"` → `"3,200"`). One line in the system instruction's NEVER COMPUTE block
      tells the model to write a figure the way `value_display` writes it.
      (2) **The gate guarantees it.** `CitationGate.learn` builds a `{raw: grouped}`
      table from the same nodes and `_release` respells the sentence **after** every
      check passes.
    - **⚠ What counts as a figure is the contract's own predicate, not a key list**: a
      node carrying **both `value` and `estimated`** — exactly what
      `present.values.Figure.payload()` and `present.event.FieldPayload.payload()`
      emit. So `rcept_no` (its own key), `countdown.days`/`dday`, `span`, `event_id`,
      `window` and every date are structurally *not* figures and can never be grouped.
      `grouped()` also refuses < 1000 and a **14-digit bare integer** (that shape is a
      접수번호 here). **The key is `value_display`, not `display`** — `FieldPayload`
      already uses `display` for its render mode (`"value"` / `"추후결정"`).
    - **Verbatim stays verbatim, structurally.** `regroup` skips every 「…」/"…" span,
      and `citations._QUOTED` is now `figures.QUOTED_SPAN` — **one pattern**, so the
      spans the gate verifies are exactly the spans the grouping refuses to touch. A
      sentence released because it *is* a tool's own string (a locked `notice_ko`,
      `none_found_ko`) is copy and is never respelled. `TurnEnd.quotes` and the
      citation events come from `Citation`s and were not touched at all. The token
      pattern's lookarounds encode the rest of the rule: not part of a longer number
      (`15.22`, an already-grouped `3,200`), not `2026-08-26`, not `2026년`, not the
      `3` of `D-3`.
    - **Membership already normalized separators** (`_decimal` strips commas on both
      sides) — that is now *stated* rather than incidental, and the check still runs on
      what the model wrote, **before** the respelling, so an invented figure is blocked
      in its raw form. Grouping can neither add a number to the traceable set nor take
      one out.
    - **The log needs no extra step**: the respelled string is what `gate.released`
      appends, so `TurnEnd.answer` → `record_turn` carries `3,200원` by construction
      (note 20's rule, unchanged). **No signed format changed** — fact rows and the
      footer carry counts and 접수번호 only, and neither goes through any of this. No
      frontend file was touched.
    - **Live smoke, 2026-08-23 (▷ $0.0107 estimated, 4 calls, 12,287 tokens, LOW):**
      two scoped turns produced 「예정발행가액은 **3,200원**입니다」, 「전환가액은
      **1,591원**입니다」, 「권면총액은 **26,900,000,000원**입니다」, `blocked 0`, dates
      ungrouped. **All five released sentences arrived already grouped** — every
      `regroup` call was a no-op. The model reads `value_display` and writes it, so in
      practice the payload is the mechanism and the release-time rewrite is the
      guarantee. Both are kept: the fallback is what makes the property testable
      without a model and true regardless of one.
    - **Honest limit worth knowing:** grouping reaches **contract figures only**. A
      bare integer that is a genuine quantity but not a `Figure` — `holdings[].shares`
      in the portfolio payload — is still spoken ungrouped (the sample's holdings are
      500/300/500/100, so nothing is visible today; a real account holding ≥1000 shares
      would read `1500주`). Widening the predicate means naming keys by hand, which is
      the drift this seam exists to avoid.

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
- ~~**Is there a rate limit at all, and where does its state live?**~~ **Answered by `P6.S4`
  (note 21):** yes, two in-process ceilings holding no identity and persisting nothing — a
  concurrency cap (unevadable, bounds spend) and a per-session-handle window (evadable, bounds one
  tab) — refusing with `429 rate_limited` and **zero UI copy**. Per process; **P4 still owns
  cross-process state**, alongside login rate limiting.
- ~~**Does the SSE stream survive the Next rewrite proxy unbuffered?**~~ **Answered by `P6.S4`
  (note 21) for every local topology:** unbuffered straight at uvicorn, through `next dev`, and
  through a production `next build && next start`, with the SSE headers travelling untouched.
  **Still open for P4:** the *deployed* topology (edge route / CDN / nginx — `X-Accel-Buffering: no`
  is set for the last), and the absence of a heartbeat during a long tool round.
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
- (`P6.S3`) **`architecture`** · **`backend`** (+ lines in **`security`**, **`operations`**,
  **`qa`**, and a **`decisions`** candidate): `mijual.agent` now **reaches the model** —
  `run_turn()` is an autonomous Gemini function-calling loop (the model chooses the tools, the
  order, the rounds and the moment to answer; a structural round/call budget bounds it) with its
  own streaming client (`gemini-3.7-flash`, thinking **LOW** recorded per call, ▷ ledger per
  turn, `mijual.extract` copied-not-imported), **인용 강제 as a generation-boundary gate** (an
  uncited or untraceable-number or non-verbatim-quote sentence cannot enter the stream; blocked
  count is reported), the five signed refusal families selected by their signed sentences, and a
  typed event stream whose terminal carries `record_turn`'s arguments verbatim. Still no HTTP, no
  SSE, no persistence (`P6.S4`). Suite 126 → **130 passed**. **Decision candidate:** the
  agent-not-chain architecture + the model-in-request-path boundary, and D-4's per-task thinking
  level gaining an `agent_turn` row at `LOW`.
- (`P6.S4`) **`architecture`** · **`backend`** · **`api`** · **`security`** · **`operations`**
  (+ a line in **`qa`**): the **request-path boundary sentence changes** — "No OpenDART call *and no
  LLM call* happens in a request path" becomes *no OpenDART call in any request path; the model is
  reached **only** through `mijual.agent`; `mijual.web` itself speaks HTTP in exactly one file*,
  now carried by four AST scans (the new one bans a model SDK anywhere under `src/mijual/web/**`)
  and corrected in the OpenAPI `DESCRIPTION` too; **`POST /ask` is the API's first streaming
  endpoint** (`text/event-stream`, CSRF-guarded, `session` frame first with the anonymous handle for
  `sessionStorage`, the typed agent events, exactly one `done`/`aborted`/`error` terminal, no stop
  endpoint — 중지 is a client disconnect); **every turn is persisted anonymously**, `aborted` and
  `error` and mid-stream 중지 included, so 「대화는 익명으로 저장됩니다 (품질 점검용)」 is now true of
  the broken turns as well; **rate limiting exists and says nothing** — in-process, no IP/UA/account
  even transiently, `429` in the plain envelope, zero UI copy, cross-process state parked for P4;
  agent spend is logged as a **▷ server-log line only** (no signed ops panel row); and
  `create_app(agent_client=…)` is the new seam (a per-turn factory), with `GEMINI_API_KEY` still
  required neither to import nor to build an app. Suite 130 → **136 passed**.
- (`P6.S5`) **`frontend`** · **`experience`** (+ a line in **`product`**): the desktop AI 질문
  surface exists — a bottom-right 68×50 launcher (the product's **one sanctioned motion
  exception**) opening a fixed 440×620 opaque widget that streams `POST /ask` over a
  **module-scoped conversation store** (`frontend/lib/ask.ts`, provided once in `SiteChrome` so a
  turn survives 위젯↔페이지 navigation; sessionStorage key `mijual.ask.thread`, never
  localStorage, never a cookie), rendering 도구 행 verbatim, numbered inline citation chips with
  in-place quote blocks (including the API-tier variant), the 답변 푸터, refusals as ordinary
  prose in the signed 3-part order, and R6's four SSE states as **text replacement plus one
  7×15 caret** — no spinner, no typing dots, no quota copy, no history UI; `lib/api.ts` gains the
  API's first streaming client (`streamAsk` + `decodeSse`, CSRF-guarded, `session` frame first,
  중지 = abort). Nothing renders at ≤480px, on `/ask`, or under `/ops`. Backend untouched
  (pytest **136 passed**); frontend `build` · `typecheck` · `smoke` green (smoke 11 → **15**).
- (`P6.S6`) **`frontend`** · **`experience`** (+ a line in **`product`**): the AI 질문 surfaces are
  complete — **`/ask` is a real page** (P5's bare shell replaced): a frameless chat directly on the
  page with a single **340px right rail** panel (범위 chip + the signed 검증/인트로/세션 lines) and
  **no launcher**, arriving by nav slot · footer link · the widget's external-link and closing the
  widget on the way in with the thread intact; **≤480px it is the whole surface** — full width, no
  widget, no launcher, a `position: sticky` 44px input bar, 44px targets, 도구 행 kept and in-place
  citation blocks full width with the 180px cap; **event detail gained the 질문 스트립** (preset
  chips generated from that event's gate-passing fields, in the page's own field order, opening the
  widget — mobile: the page — in that event's 범위 with the question sent, plus R6-2's 「직접 질문
  입력 →」), and an **ambient 범위** bound per event page that never overrides a reader's own choice.
  Second view, not second state: `lib/ask.ts` and every `P6.S5` component are unchanged, the one
  sessionStorage key is unchanged, and **no backend file changed** (pytest **136 passed**; frontend
  `build` · `typecheck` · `smoke 15/15` green; 0 px horizontal overflow at 390 on every touched
  page, verified in a browser against a spend-free scripted agent).
- (`P6.S7`) **`qa`** · **`api`** · **`operations`** (+ lines in **`backend`** and **`architecture`**;
  **no** `frontend`/`experience` change — the pass touched no frontend file): the AI 질문 feature has
  a **measured** baseline — the whole product run live (dev Postgres · live `gemini-3.7-flash` agent ·
  `next build && next start` · headless Chrome) against R6's own contract, 41 stages / ~120 checks at
  1440·768·481·480·390, **25 live turns** covering all five refusal families, **27/27 stored quotes
  byte-identical** to the served payload and **0 numerals unaccounted for** in 24 stored answers, ▷
  ≈ **$0.23 estimated** (thinking LOW, never billed); suite **136 → 137 passed**. Three durable-truth
  changes came out of it: **(1) `POST /ask` now sends `Cache-Control: no-store, no-transform`** —
  without it the production Next proxy gzips the stream and the reader sees no incremental output at
  all, so the header is part of the streaming contract (`api`), and the deployed topology must
  preserve it (`operations`, alongside `X-Accel-Buffering: no`; longest observed inter-frame gap
  **6.0 s** and **still no heartbeat**); **(2) a turn whose only work is a successful `save_feedback`
  ends as an answer carrying the signed confirmation, never as a 검증 미통과 폴백 refusal**
  (`backend`); **(3) the agent carries no route string at all** — `BOARD_POINTER_HREF` removed, the
  frontend owns every path (`architecture`/`backend`). Two operations facts P4 inherits: the
  **conversation tables must be created in the deploy database** before the first `POST /ask`
  (`create_all`; P2 has no migrations), and the **▷ ledger line needs a root logging configuration**
  or agent spend is recorded nowhere.
- (`P6.REVIEW`) **consolidated — the list above is closed.** Eleven versions created on the passing
  review, one per doc the phase moved: **`architecture` v0004** · **`backend` v0003** ·
  **`api` v0003** · **`data` v0005** · **`security` v0004** · **`product` v0005** ·
  **`experience` v0004** · **`frontend` v0004** · **`operations` v0006** · **`qa` v0004** ·
  **`decisions` v0006**. `docs/current/*` was regenerated by `rebuild-docs`, never hand-edited, and
  `pytest` was re-run afterwards (**137 passed**) because the ops 개요 tab parses
  `docs/current/decisions.md`. Open-bullet count **1 → 3**, verified by rendering the panel's own
  reader. Nothing in this phase's diff changed durable truth without a line above.
- (`P6.F1`) **after the consolidation above — the list reopened, one line for the re-review.**
  **`backend`** (+ a line in **`api`** and **`experience`**): the agent's tool payloads
  now carry a **`value_display`** string beside each figure's exact `value` — the same
  number in the product's own thousands grouping (`"3200"` → `"3,200"`) — and the
  citation gate respells a released sentence's raw figures with it, so **agent prose
  prints 3,200원 like every other surface** (`mijual.agent.figures`; new module). A
  *figure* is the contract's own predicate (a node carrying both `value` and
  `estimated`), so 접수번호, dates, years, spans and D-days are structurally excluded;
  verbatim 「…」 spans, locked Korean strings and `TurnEnd.quotes` are byte-unchanged;
  the never-compute membership check is unchanged and still runs before the respelling
  (separators were already normalized on both sides); and no signed format, no schema
  and no frontend file changed. The stored 대화 로그 answer carries the reader's form by
  construction. Suite 137 → **138 passed**.
