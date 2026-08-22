# Result — P6.DECOMP

**Status: done.** P6 is decomposed into **seven middle slices** (`P6.S1` … `P6.S7`), all
`kind: implementation`, all `risk: high`, ordered 1–7 between `P6.DECOMP` (order 0) and
`P6.REVIEW` (order 9999). Every folder is **bare — `slice.json` only**; no `plan.md` was
pre-filled anywhere. Single pass, as the plan specifies: P6 is the apply half of a two-phase
split, the design was signed in P3's R6 round, so there are no `co-work` slices and no `DECOMP2`.

## The cut

| Slice | Order | Risk | Covers |
|---|---|---|---|
| `P6.S1` | 1 | high | 익명 대화 저장소 + `Conversations` 포트 구현 — schema, session hash, cursor reads, the three ops tabs go live |
| `P6.S2` | 2 | high | The five agent tools (`search_events` / `get_event` / `get_portfolio` / `save_feedback` / `get_contact`) |
| `P6.S3` | 3 | high | Agent core — the autonomous Gemini function-calling loop, citation forcing, refusal families, never-compute |
| `P6.S4` | 4 | high | SSE 엔드포인트 + turn persistence + rate limiting + the request-path model boundary |
| `P6.S5` | 5 | high | 런처 + 위젯 — the whole desktop AI 질문 surface |
| `P6.S6` | 6 | high | 전용 `/ask` 페이지 + 모바일 전폭 페이지 + 상세 질문 스트립 + 진입점 continuity |
| `P6.S7` | 7 | high | Design-fidelity verification in a real browser (RESPECT THE DESIGN) |

`depends_on` is a chain (S1 ← S2 ← S3 ← S4 ← S5 ← S6 ← S7); it is advisory, and here it is also
the true build order. Backend (S1–S4) precedes design implementation (S5–S6); fidelity is last.

Full breakdown, rationale, findings, constraints and open questions are in
`works/phases/active/P6/phase.md` — this file only summarises.

## Why seven, and why these seams

- **Storage first.** Two later slices write into it (`save_feedback` in S2, turn persistence in
  S4) and one *already built* surface is waiting on it (R7's 대화 로그 · 익명 세션 · 피드백 tabs,
  serving honest zeros through P5's port). Landing it first also puts the schema-level anonymity
  promise in place **before** anything writes, which is what makes it structural.
- **Tools before the agent.** The tool layer is deterministic code over `mijual.present`,
  measurable against the live corpus with no model and no credential. It also keeps "what a tool
  returns" out of the slice that spends money in a non-deterministic loop.
- **The agent core is its own slice** because the operator's binding addition — *"we need to build
  a agent not just llm chain"* — is a property of control flow, not a feature. Isolated, the review
  can read one module and answer *does the model choose the tools, the order, the number of rounds
  and the moment to answer?*
- **Transport is split from the loop**, the same seam P5 drew between `present` (S2) and the
  endpoints (S3): a generator of typed events is unit-testable with no HTTP. It is also where the
  architecture boundary changes, and that change deserves to be one slice's diff.
- **One slice per signed surface, each complete.** Splitting the widget into "chrome" then
  "answers" was considered and rejected — it would leave a chat rendering prose without citation
  chips across a slice boundary, which is precisely the half-built surface RESPECT THE DESIGN and
  P5's no-fake-chat rule refuse.
- **Fidelity is its own slice** (`design-cowork`, the `P5.S19` precedent).

## Coverage check against R6's build prompt — nothing dropped

Walked the record section by section; each element has an owning slice:

- **Surfaces + routes**: 위젯 440×620 불투명 `#0e1a15`, 런처 68×50 + 꼬리, 헤더 external-link + × 28px,
  메시지 버블 → **S5**; 전용 프레임 없는 페이지 + 340 레일, 페이지에 런처 렌더 금지, 모바일 ≤480 전폭
  페이지 (위젯·런처 없음), 질문 스트립, 위젯↔페이지 continuity, nav/푸터 진입점 → **S6**;
  범위 모델 (이벤트 칩 ↔ 전체 공시, 새 질문부터 적용) and sessionStorage 스레드 → **S5**, reused by **S6**.
- **Agent**: five tools + 도구 행 형식 → **S2** (contract) / **S5** (render); 절대 계산하지 않음 →
  **S2**+**S3**; 인용 강제 (생성 단계 차단, verbatim만) → **S3**; 검색 0건 문구 → **S2**.
- **인라인 인용 (R6-4)**: 번호 칩 · 제자리 인용 블록 · API-tier 변형 · 답변 푸터 `근거 N건 · rcept_no ·
  생성시각 KST` + 컨텍스트 링크 → **S5** (mobile 전폭 인용 블록 180px 캡 → **S6**).
- **SSE**: idle → 답변 준비 중 → 스트리밍 (7×15 캐럿, 1s steps(1), reduced-motion 정지, 중지 버튼) →
  완료 푸터 페이드 → 중단/오류 partial 유지 + 재시도 → server frames **S4**, client states **S5**;
  인용 칩 동시 도착 → **S3**+**S4**+**S5**.
- **거절 (R6-7)**: 3단 구조, 프로즈 렌더, 근거 칩 동반, 가족 5종만, 계산 요청 리다이렉트 고정,
  확정 전 부분 답변 → selection **S3**, render **S5**, persistence of 카테고리 + 인용 → **S1**/**S4**.
- **세션 + 저장**: 무제한 (quota 표기 전무), 익명 유지, 서버 레이트 리밋 무카피 → **S4**;
  sessionStorage (localStorage 금지) → **S5**; 서버 익명 저장 + 운영 패널 열람 → **S1**;
  「대화는 익명으로 저장됩니다 (품질 점검용)」 카피 → **S5**.
- **의견 · 문의**: 자동 저장 + 확인 한 줄 + 선택 이메일 + 실패 시 재시도 행 → **S2** (write) /
  **S5** (surface); 운영자 연락처 = 배포 설정값, 발명 금지 → **S2**.
- **Mobile**: 메뉴 첫 행 ≥44px, 프리셋 가로 스크롤, 입력 바 sticky 44px, 도구 행 유지, 뒤로가기 복귀 →
  **S6**.
- **런처 마크**: 22px 토성, 밴드 4.5s, 두 반쪽 링 + `ringdrift` 14s, hover 마크만 1.35, 열림 상태 ×,
  reduced-motion 전면 정지, 데이터 표면 비확산 → **S5**, verified in **S7**.
- **Hard rules**: acceptance criteria for **S7** and for `P6.REVIEW`; restated in `phase.md`
  §Constraints.

Also covered because R7's admin round depends on it: the signed conversation/session/feedback
column sets and the two-way 세션 해시 cross-link → **S1**.

## The finding that most changes the shape of this phase

`docs/current/api.md`, `architecture.md` and `backend.md` all state **"No OpenDART call and no LLM
call happens in a request path,"** enforced by two AST scans over `src/mijual/web/`
(`tests/test_web_smoke.py::test_no_request_path_module_imports_a_spending_module`,
`tests/test_web_vocky.py::test_only_the_vocky_module_may_speak_http`). **P6's agent is an LLM call
in a request path by design** — SSE streaming cannot be anything else.

The decomposition answers it structurally rather than by exception: the agent lives in a **new
top-level package `mijual.agent`** (S2/S3), so `web/` keeps importing no spending module and keeps
speaking HTTP in exactly one file — and **S4 must re-aim the invariant honestly** (state the new
boundary in the tests and the docs, and add a scan over `src/mijual/agent/` that keeps
`mijual.dart` / `mijual.collect` / `mijual.extract` out of the agent too). It also forbids the
tempting shortcut of importing `mijual.extract.client` for its `GeminiClient` wrapper: that module
sits inside a package the request path may not reach. Recorded as Finding 1 in `phase.md`.

Sixteen further findings are recorded there, the load-bearing ones being: R7 signs the conversation
schema column by column (2); the exact row keys the built ops panel already reads (3); the port's
three inherited rules (4); `get_portfolio` has no anonymous server-side portfolio and must answer
with the labelled sample (5); citation forcing is a generation-boundary property (7); refusals are
five families and carry their own citations (8); `get_contact` is an unset deploy value and a note,
not a blocker (9); what P5 left ready (10); the launcher's recorded flat-sticker bug (11);
sessionStorage-not-localStorage and the forbidden deletion copy (12); no quota anywhere (13); agent
spend is a server fact and **not** a new element on R7's signed 비용 panel (14); `search_events`
returns candidates where `/stocks?q=` declines (15); and the frontend's Next 16.3.2 caveat plus the
same-origin rewrite that SSE has to survive (16).

## Validation

| command | outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **passed** — `Workflow validation passed.` |
| `ls works/phases/active/P6/slices/P6.S*/` | each new folder holds **`slice.json` only** — no `plan.md` pre-filled |

No source file was touched, no doc version was created, nothing was committed, and no slice or
phase status was transitioned. `new-slice` was the only workflow command run besides `validate`.

## Deviations from `plan.md`

- **Slice count: seven, at the top of the plan's "roughly 5–7" range**, and the shape differs from
  the candidate cut in two deliberate ways, both explained above and in `phase.md`:
  1. **Storage moved out of the transport slice and to the front** (candidate ③ → `P6.S1`),
     because `save_feedback` and turn persistence both need it and R7's three ops tabs are already
     built against the port.
  2. **The frontend is two surface slices, not two feature slices** — the widget lands complete
     (`P6.S5`) rather than being split into chrome and answer rendering.
- Otherwise the plan is followed exactly: implementation kind, `high` risk throughout, backend
  before design implementation, fidelity last, no fix slices created, `P6.REVIEW` untouched.
