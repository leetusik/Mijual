# Result — P6.S7: design-fidelity verification in a real browser (RESPECT THE DESIGN)

The whole product ran end to end — the operator's dev Postgres, a **live** Gemini
agent (`GEMINI_API_KEY` from `.env`, no `agent_client` override), a production
`next build && next start`, and headless Chrome over CDP — and every R6 element
was checked against **R6's own contract**, clause by clause. **Three
faithful-implementation fixes landed in code**; nothing under
`docs/reference/design/` was touched, no token was edited, no Korean was invented
and nothing signed was restyled.

**One of the three fixes is the pass's headline**: R6's signed 스트리밍 state was
not reaching a real browser at all. Everything else the record signs was already
there.

---

## 0. What ran, and how

| | |
|---|---|
| API | `uvicorn mijual.web.app:app` on `127.0.0.1:8000`, the operator's dev Postgres (`:5433`), **live** `AgentGeminiClient` (`gemini-3.7-flash`, thinking `LOW`) |
| Frontend | `npm run build && npm run start` on `:3000`, same-origin `/api` rewrite (`MIJUAL_API_ORIGIN` default `:8000`) |
| Browser | headless Chrome (`--headless=new`) over CDP, widths **1440 / 768 / 481 / 480 / 390**, `prefers-reduced-motion` emulated through `Emulation.setEmulatedMedia` |
| Corpus | live, `reference 2026-08-22` — 계양전기 `20260724000546` (①, 확정 전), 썸에이지 `20260805000454` (철회), 대동기어 `20251016000315` + `20260715000369` |
| Evidence | 24 stored conversation turns, 3 feedback rows, 16 screenshots, per-frame arrival timings, DOM measurements |

**Deploy step P4 inherits (done here as deployment, not as a schema change).**
The `P6.S1` tables did not exist in the dev Postgres (`P6.S4` note 21 recorded
it). They were created with the schema layer's own path —
`mijual.db.session.create_all(make_engine())` — which is additive and idempotent:
**16 tables → 18**, `conversation_turn` + `conversation_feedback` created, no
existing table touched, no foreign key on either (asserted again after
creation). **P4 must run this (or its migration equivalent) before the first
`POST /ask`**, because P2 has no migrations and `create_all` otherwise runs only
from the collect/gates/pipeline entry points.

---

## 1. Check table

Stage · what was checked · result. Every "measured" number below came out of the
running browser or the running service, not out of the source.

| # | Stage | Checks | Result |
|---|---|---|---|
| 1 | **런처 geometry** (§Surfaces 「런처 (클릭 전)」) | 68×50 frame · `#0e1a15` · 1px `--border-strong` · `--panel-glow` · radius 0 · `position: fixed` right/bottom 24 · 22×22 mark · tail 11×11 rotate(45°) right 12 / bottom −6 carrying the frame's fill + its two outer borders | **PASS** — every literal exact |
| 2 | **런처 마크 · the ring reading test** (개정 ⑧) | two half-boxes, layout **40×13**, authored `border: 1.5px solid rgba(95,208,165,.9)`, `border-radius: 50%`, `left:-9px top:5px`; **one shared** `ringdrift 14s ease-in-out infinite`; clips `polygon(… 49% …)` top vs bottom; DOM order ringBehind → planet → ringFront | **PASS** |
| 3 | **the ring actually passes in front *and* behind** | 27-point hit grid over the paused mark: over the planet at y−5 the topmost paint is the planet's **band** (ring behind); at y+5 it is **ringFront** (ring in front); outside the planet on both sides the ring is visible | **PASS** — reads as one ring through a sphere, **not** a flat sticker |
| 4 | **밴드 + drift really move** | band `repeating-linear-gradient(90deg, rgba(30,52,42,.34) 0 2px, transparent 2px 7px)`, `background-size: 14px 100%`, `bandspin 4.5s linear infinite`; sampled twice 1.4 s apart: `−4.12px → −8.50px`, ring `rotate` matrix changed | **PASS** |
| 5 | **hover / active** (real CDP mouse) | hover: **mark only** `scale(1.35)`, frame stays **68×50**, frame bg `#122219` + border `rgba(95,208,165,.7)`, **tail follows**; active: `scale(1.15)` exactly (measured after the transition settles) | **PASS** |
| 6 | **열림 상태** | mark `opacity: 0`, **16×16** ×, bars **16px × 1.5px** at **+45° / −45°**, `#dfe9e4`; launcher `inert` + `aria-expanded="true"`; widget rect **covers the launcher rect exactly** (z 40 over 30) — 「런처는 열리면 숨음」 and §런처 마크's open state honoured at once | **PASS** |
| 7 | **reduced motion** | band `animation: none`, both rings `none`, launcher/tail/mark/close `transition-property: none`, **hover scale → `none`**; zero infinite animations anywhere on the page | **PASS** — 「밴드·드리프트·전환·hover 확대 전부 정지」 |
| 8 | **the motion exception does not leak** | infinite animations per page: `/stocks` `/events/…` `/portfolio` = **only** `ringdrift · bandspin · ringdrift`; `/ask` = **none**; landing additionally has P5's own signed R2 cosmos (`twinkle`/`shoot`/`orbit`/`drift`/`blink`), which predates P6 | **PASS** |
| 9 | **위젯 spec** (개정 ①·②·⑥) | **440×620** · opaque `#0e1a15` `opacity: 1` · fixed right/bottom 24 · radius 0 + `--panel-glow` · **no backdrop, no dim, no `backdrop-filter`** (the only other `position: fixed` node is P5's `.backdrop` cosmos slot at `z-index: -1`, `pointer-events: none`, fully transparent) | **PASS** |
| 10 | **페이지 레이아웃 불변** | landing `main` 1440 × 17567.70 px and `document.scrollWidth` 1440 / `body.scrollHeight` 17863 — **identical before and after opening the widget** | **PASS** |
| 11 | **헤더** | two icons, **28×28** each; first = inlined Lucide `external-link` svg with accessible name 「AI 질문 페이지 →」; second = 「×」; 범위 칩 mono 11px | **PASS** |
| 12 | **인트로 + 세션·저장 카피** | exactly the two signed lines, verbatim: 에이전트 인트로 and 「완전 익명 — 로그인도, 질문 수 제한도 없습니다 · 대화는 익명으로 저장됩니다 (품질 점검용)」 | **PASS** |
| 13 | **SSE 상태 (R6 §SSE)** | measured as a millisecond timeline via `MutationObserver`: `직접 질문 입력 →` → **`답변 준비 중…` + `disabled`** → **`중지`** (not disabled) + caret → idle. **Zero** spinner/dots elements. Caret **7×15px**, `background: var(--live)` = `rgb(95,208,165)`, `caretblink 1s steps(1)`, `data-motion="tick"` | **PASS** (after fix 1 the 스트리밍 state is real — see §2) |
| 14 | **완료 → 푸터 페이드** | `askfade 0.2s cubic-bezier(.2,0,.2,1)` = `--dur-base` (200 ms), opacity observed `0 → 1` | **PASS** |
| 15 | **중단/오류** | 중지 pressed mid-answer: partial answer **kept** (1 sentence + its chip), `data-dim="true"` → prose renders `rgb(157,179,168)` = **`--ink-2`**; inset row on `rgba(255,255,255,.08)` = **`--surface-inset`** carrying 「연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.」 + 「재시도」; **no footer**; `--alert` (`#e0573f`) appears nowhere | **PASS** |
| 16 | **재시도** | replaces the turn and re-runs it live; the retried turn completed with 7 sentences, 6 chips and a footer | **PASS** |
| 17 | **인라인 인용 칩** (R6-4) | mono **10px**, colour `rgb(95,208,165)` = `--live`, border **`1px rgba(95,208,165,.4)`**, transparent bg, inline; same 근거 → same 번호 (`1,2,2` / `1,1,2` observed) | **PASS** |
| 18 | **제자리 인용 블록** | closed height **0** → tap → **103.77 px**, `--surface-inset` bg + **left 2px `--live`**, verbatim quote + 「DART 원문 20260724000546 ↗」 → `dart.fss.or.kr/…rcpNo=…`; **re-tap closes** (height back to 0, opacity 0) | **PASS** |
| 19 | **API-tier variant** | the 철회 turn's chip opened to 「DART 공시 API 수치 — 원문 스팬 없음, 접수번호가 인용 핸들」 + the DART link, verbatim | **PASS** |
| 20 | **인용문 verbatim** | **27/27** stored 인용 칩 원문, across every live turn, are **byte-identical** to a value the served `GET /events/{rcept_no}` payload carries; the rendered block text equals the wire quote | **PASS** — no reconstruction, no summary |
| 21 | **never-compute** | every numeral in **all 24** stored answers checked against that turn's own event payload(s) + `/portfolio/sample`: **0 missing** across 20 answered turns (up to 12 numerals in one). D-day (`D-3`, `D-63`) arrives from the payload's own `countdown`; 「추정」 was never attached to a non-derived value | **PASS** |
| 22 | **거절 = 5 families, 3 parts, no alert colour** | all five exercised live and stored: 철회 1 · 확정 전 3 · 공시에 없음 3 · 계산 요청 1 · 검증 미통과 폴백 1. 철회: ① 「이 유상증자는 철회되었습니다.」 **with a 근거 칩** ② 「철회된 공시는 해설하지 않습니다.」 ③ DART 원문 · 이벤트 상세 · 내 종목 조회. Body ink throughout | **PASS** |
| 23 | **계산 요청** | 「15552 곱하기 643004 계산해 주세요」 → **zero tool calls**, the fixed sentence 「해설은 계산하지 않습니다 — 계산은 검증된 수치로 내 종목 조회가 합니다.」 + 내 종목 조회 | **PASS** |
| 24 | **0건 search** | 「삼성전」 → the model searched, corrected itself, searched again, then 「「삼성전」에 해당하는 공시를 찾지 못했습니다」 + **관제 현황판 → `/`** + 내 종목 조회. No guess, no invented company | **PASS** |
| 25 | **포트폴리오 anonymous** | 「내 마감 뭐가 급한가요?」 → row 「내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)」 and the answer opens 「포트폴리오 **구성 예시** 기준으로 …」 | **PASS** |
| 26 | **의견** | row 「의견 저장 → 운영자 검토 대기열」 + 「의견을 저장했습니다 — 운영자가 확인합니다.」, and the row lands in the ops 대기열 | **PASS** after fix 2 (§2) |
| 27 | **끊김 없음 mid-stream** | the reader pressed the header external-link **after the first 도구 행**: `/ask`, widget gone, launcher absent, `중지` still showing — and the **same turn finished on the page** (2 tool rows, 4 sentences, `근거 1건 · 20260724000546 · 2026-08-22 22:20 KST`, no 중단 row) | **PASS** — 「스트리밍 중 이동/전환에도 끊김 없음」, measured |
| 28 | **전용 페이지 (개정 ④)** | `/ask` at 1440: **zero** `position: fixed` elements (no launcher, no widget), rail **exactly 340px** and it *is* a `CraftPanel`, chat column `border: 0px none` + transparent bg (프레임 없음), 0 px horizontal overflow | **PASS** |
| 29 | **레일 카피** | 범위 칩 · 「검증된 필드만 근거로 답합니다 — 모든 답에 원문 인용」 · 인트로 · 세션·저장 — the four signed things, nothing else | **PASS** (the rail's *contents* remain S6's flagged reading — §4) |
| 30 | **480 / 481 boundary** | 481 px: widget **and** launcher present. 480 px and 390 px: **neither**. Horizontal overflow 0 px at all three | **PASS** — the signed boundary is exact |
| 31 | **모바일 페이지** | 390 px: input bar is `position: sticky; bottom: 0` on `--paper` (`#0a1310`), input and button **44 px**; rail contents stack **above** the chat (railTop 76 < chatTop 326.5); no auto-scroll | **PASS** |
| 32 | **모바일 도구 행 · 인용 블록** | 도구 행 kept: IBM Plex Mono, 11px, `--ink-3`, left 2px hairline. Citation block full width (332 of 358 px), **`max-height: 180px` + `overflow-y: auto`**, rendered height 83.7 px | **PASS** |
| 33 | **질문 스트립** | one horizontally-scrolling line (scrollWidth 1009 > clientWidth 358), every chip **44 px**, document overflow **0 px**; heading 「이 공시에 대해 질문」; press → mobile lands on `/ask` in `범위: 계양전기 · 20260724000546` with the question already sent | **PASS** |
| 34 | **뒤로가기** | `/ask` → back → `/events/20260724000546` with its strip; returning to `/ask` shows the same turn, same 범위, and `sessionStorage` holds **only** `mijual.ask.thread` (`localStorage` empty) | **PASS** |
| 35 | **0 px horizontal overflow at 390** | `/` · `/stocks` · `/events/20260724000546` · `/ask` (empty **and** with a rendered answer + open citation block) · `/portfolio` | **PASS** — 0 px everywhere |
| 36 | **corner / vocky** | at `(vw−40, vh−40)` on `/` `/stocks` `/events/…` `/portfolio` `/ask` `/auth/login`: the only `position: fixed` node is the launcher (none on `/ask`); **no vocky element anywhere** (`NEXT_PUBLIC_VOCKY_SRC` unset, so no third-party script loaded) | **PASS** — 「런처·위젯은 vocky 트리거와 모서리 충돌 금지」 |
| 37 | **ops loop closes** | 대화 로그 shows **21→24 real rows** (세션 · 시각 · 범위 · 질문 · 답변/거절 · 거절 카테고리); expanded row replays 답변/거절 + 근거 + 인용 verbatim; both filters work with the **five signed Korean names sent as the values** (확정 전 → 3, 계산 요청 → 1, `kind=refusal` → 8, `kind=answer` → 13); 익명 세션 aggregates 13 sessions with 질문 수 · 거절 수 · 마지막 범위; save_feedback 대기열 holds the saved 의견 under 「시각 · 의견 텍스트 · 답장 이메일 (선택) · 원 대화」. **No 삭제/편집/태깅/처리 control anywhere** | **PASS** |
| 38 | **copy audit** | no 「남은 질문」, no quota bar, no 소진 state on any surface; the signed 익명 저장 line present in the widget, the rail and the ops panel; 「저장 이력 없음」 and 「탭을 닫으면 사라집니다」 absent from every rendered reader surface (the one 「탭을 닫으면」 in the tree is P5's **보유량** conversion line, a different R5 rule, correctly untouched); no history UI | **PASS** |
| 39 | **copy provenance** | preset chips = the served `korean_name` **verbatim** (5/5 matched against `GET /events/…`), plus R6's own 「실권주는 어떻게 처리되나요?」 and R6-2's 「직접 질문 입력 →」 — **nothing unaccounted for**; a 철회 event yields **no presets** (only the free-input chip) | **PASS** |
| 40 | **type** | Korean prose in the widget draws in **Pretendard Variable** (`CSS.getPlatformFontsForNode`, not a computed-style guess); **no `.mono`-classed element exists inside the ask surfaces**, so P5.S19's cascade defect cannot recur here | **PASS** |
| 41 | **anonymity, re-asserted on the real DB** | `conversation_turn` and `conversation_feedback` in the dev Postgres: no account/email/IP/UA column, **zero foreign keys** on either | **PASS** |

---

## 2. The three fixes (code only, before → after)

### Fix 1 — ⚠ the signed 스트리밍 state was never reaching the browser

**`src/mijual/web/ask.py` · `SSE_HEADERS`** (+ its test)

```
- "Cache-Control": "no-store",
+ "Cache-Control": "no-store, no-transform",
```

**What was wrong.** R6 §SSE signs four states, and the middle one is
「**스트리밍** (프로즈 자람 + 캐럿 …)」 with the 도구 행 arriving as the agent
reads (「도구 호출은 숨기지 않고 사실 행으로 표시 — 무엇을 읽었는지가 근거의
일부」). In a production `next start`, the reader saw **none of it**: 「답변 준비
중…」 for the whole turn, then the entire answer — every tool row, every sentence,
every chip and the footer — painted in **one burst under 10 ms**. Measured across
eight consecutive live turns.

**Why.** Next's router runs the `compression` middleware whenever `compress !==
false` (the default), and it compresses `text/event-stream` like anything else. A
gzip encoder holds bytes until it has a block, so the whole stream was released at
the end. `P6.S4` measured the proxy as unbuffered and was right *for what it
measured*: `curl` sends no `Accept-Encoding` by default, a browser sends
`gzip, deflate, br, zstd`.

**Measured, three ways, same question shape:**

| through the `next start` proxy | frame arrival |
|---|---|
| plain `curl -N` (no `Accept-Encoding`) | session `74.08` → tool_row `75.47` → citation `76.52` → text `76.58` → text `76.63` → footer `76.68` → done `76.73` (spread over **2.6 s**) |
| `curl --compressed` (what a browser gets) — **before** | response header **`Content-Encoding: gzip`**; all seven frames inside a **450 ms** window at the very end of a 2.8 s turn |
| `curl --compressed` — **after** | **no `Content-Encoding`**; session `572.81` → tool_row `578.80` → citation `581.51` → text `581.62` → text `581.70` → footer/done (spread over **9 s**) |

**Why `no-transform` and not `compress: false`.** It is the standard's own way to
say *do not re-encode this payload* (RFC 9111 §5.2.2.6); `compression`'s
`shouldTransform` honours it, and so do nginx and the CDNs P4 will meet — so the
one header covers the deployed topology too, beside the `X-Accel-Buffering: no`
already there. `compress: false` would have de-optimised every HTML and JS
response to fix one endpoint.

**After the fix, in the browser** (reader-visible timeline, `MutationObserver`):
tool row 1 at `5542 ms`, tool row 2 at `8683 ms`, first sentence at `11024 ms` —
prose grows, the caret blinks for **5.5 s**, and 중지 is now pressable mid-stream
(it is how check 15 was measured at all).

**For P4:** longest observed gap between frames with the live agent is **6.0 s**
(request → first 도구 행, i.e. the model's first round), and **3.1 s** between two
tool rounds. There is still **no heartbeat**, so a proxy idle timeout below ~10 s
would cut a legitimate turn.

### Fix 2 — ⚠ a saved 의견 ended in a refusal that contradicted it

**`src/mijual/agent/loop.py` · `_finish` + new `_feedback_only`** (+ one terse test)

**Before** (live, verbatim, one bubble):

```
의견 저장 → 운영자 검토 대기열
의견을 저장했습니다 — 운영자가 확인합니다.
이 데이터는 검증을 통과하지 못했습니다. 검증되지 않은 내용은 해설하지 않습니다.
```

R6 §의견 signs 「자유 텍스트 → 자동 저장, 확인 "의견을 저장했습니다 — 운영자가
확인합니다." … **실패 시에만** 재시도 행」 — a confirmation, and no refusal. The
폴백 family is a claim about **data that failed verification**; a feedback turn has
no data. The cause is structural, not a model slip: nothing about a feedback save
is citable, so every sentence the model wrote was dropped at the gate
(`blocked: 2`), and `_finish` selected the fallback because nothing was released.

**After:** when a turn's **only** work was a successful `save_feedback`, the
fallback is not selected. **No event is emitted** — the confirmation is already on
the screen, printed by the surface under the tool's own row (the split
`mijual.agent.copy` and `save_feedback`'s docstring both fix) — and the signed
sentence is recorded as the turn's `answer`, so the 대화 로그 replays what the
reader read (`P6.S4`'s rule). The guard is deliberately narrow: a turn that also
read an event and then said nothing verifiable **has** failed to verify something
and keeps the 폴백.

Verified live after the fix: row + confirmation, **no refusal**, `kind=answer`,
and the 대기열 row present.

### Fix 3 — the dead `/board` route left the agent's reach

**`src/mijual/agent/copy.py` · `tools.py`** (+ its test)

`copy.BOARD_POINTER_HREF = "/board"` was a dead route (`ROUTES.board` is `"/"`,
there is no `app/board/`) served inside the 0건 and event-miss tool payloads.
`P6.S3` recorded it as a nit and `P6.S5`'s `links.ts` correctly refuses to render
it. **It was removed rather than corrected**, because the agent should not carry a
route at all: `frontend/lib/routes.ts` owns every path, the surface builds the
pointer from the `{"kind": "board"}` link the turn already serves — and a path
string in a tool payload is a string the citation gate's verbatim-string rule
would let the model **say**.

Confirmed: **0 of 24** stored answers contain `/board` or any URL, and the 0건
turn still renders 「관제 현황판」 → `/` after the change.

**Backend touches, stated explicitly** (per the plan's boundary): fixes 1–3 are
all backend. Fix 1 adds one cache directive; fix 2 narrows one refusal selection;
fix 3 deletes one dead constant. **No frontend file was changed in this slice.**

---

## 3. The live conversation set — ▷ ledger

**25 live turns** (24 stored — a 중지 before the first sentence stores nothing by
design), covering every family the plan lists:

| # | Family | Turn | Outcome |
|---|---|---|---|
| 1 | scoped (질문 스트립) | 실권주는 어떻게 처리되나요? · 계양전기 | 범위 칩, 1 도구 행, 2 근거, chips `1,1,2`, footer, 완료 fade |
| 2 | 전체 공시 search | 대동기어 공시 알려주세요 | `이벤트 검색 「대동기어」 → 2건 · ② 전환사채 · 20251016000315 · ① 유상증자 · 20260715000369` + two `get_event` rows |
| 3 | 철회 (by filing number) | 20260805000454 | 3-part refusal **with a 근거 칩**, body ink, no alert colour |
| 3b | 철회 (by company name) | 썸에이지 유상증자 어떻게 되나요? | 「찾지 못했습니다」 + 공시에 없음 — the recorded search contract, catalogued in §4 |
| 4 | 확정 전 금액 | 계양전기 500주 청약하려면 얼마? | known facts cited (배정비율 · 예정발행가액 · 확정 예정일 09-01 · 청약기간), **amount refused** |
| 5 | 계산 요청 | 15552 × 643004 | fixed redirect sentence, **zero** tool calls |
| 6 | 0건 | 삼성전 공시 있나요? | model re-searched on its own, then the signed sentence + 관제 현황판 |
| 7 | 포트폴리오 (anonymous) | 내 마감 뭐가 급한가요? | 샘플 4종목, 「구성 예시」 in the answer |
| 8 | 의견 | (×3) | tool row + surface confirmation + 대기열 row |
| 9 | 중지 mid-stream | 계양전기 전체 설명 | partial kept, dimmed, inset row + 재시도 |
| 9b | 재시도 | same | full 7-sentence answer |
| 10 | mid-stream navigation | 위젯 → `/ask` after the first 도구 행 | the turn finished on the page — 끊김 없음 |

**▷ ledger (D-4 — estimated, never billed).** Exactly measured on 8 turns
(7 from captured `done` frames + 1 verbatim server-log line):
**18 model calls · 87,908 tokens (prompt 85,106 + thinking 1,717 + output 1,085) ·
thinking `LOW` on every call · ▷ $0.0743 estimated**. That is **$0.0093 per
turn**, so the whole pass is **▷ ≈ $0.23 estimated** over 25 turns
(`gemini-3.7-flash` rate card, **not billed**). One line verbatim from the server:

```
agent turn done · answer · rounds 2 · tools 1 · blocked 0 · calls 2 (0 failed) ·
tokens prompt 10,734 + thinking 77 + output 188 = 10,999 · thinking LOW ·
▷ $0.0090 estimated (gemini-3.7-flash rate card, not billed)
```

`blocked == 0` on every turn but the pre-fix feedback one (`blocked: 2`) — the
citation gate dropped nothing a reader should have seen.

---

## 4. Disposition of every flag

*verified as described* / *fixed* / *catalogued for the operator*.

| # | Flag (source) | Disposition |
|---|---|---|
| 1 | 확정 전 「예정발행가액은 3,200원입니다」 (note 20) | **Verified as described.** The event page itself renders 「정정공시 반영 — 최근: 1차 발행가액 확정에 따라 **예정발행가액(4,985원 -> 3,200원)** …」 inside the gate-passing 정정 해석 field. It is a **published planned figure the product prints**, not a 확정 전 금액 claim — and in the same turn the agent cited 「최종 발행가액은 2026년 09월 01일에 공시될 예정입니다」 and then refused the amount, which is R6-7's own instruction verbatim. Catalogued sub-point: the agent writes `3200원` where the page writes `3,200원` (→ #10). |
| 2 | `BOARD_POINTER_HREF` dead route (note 20) | **Fixed** (fix 3). Also verified: `links.ts` maps kinds through `ROUTES`, the live 0건 turn renders 관제 현황판 → `/`, and 0/24 stored answers contain the string. |
| 3 | 필드로 이동 footer link (note 22 pinch 1) | **Catalogued.** Confirmed not rendered and not invented. There is no cheap faithful path: the wire's link kinds are a closed set (`dart · event · board · stocks`), so an anchor alone would not produce the link — it needs a new server-side kind *and* per-field anchors on the detail page, i.e. a new link vocabulary. Operator question §5-A. |
| 4 | Footer with up to 8 links · multi-`rcept_no` `·` (note 22 pinches 2·3) | **Catalogued with the measurement.** Worst case observed: **7 links** (3 filings × dart+event, + 내 종목 조회) + 다시 질문, wrapping to 3 lines / 51 px. `_links` is composed from every filing the tools **read** (capped at 3), while the footer's facts name the filings the answer **cited** — so one 이벤트 상세 can point at a filing that is not among the 근거, and up to three links carry the **identical** label 「이벤트 상세」. Not changed: dropping links would drop signed destinations and relabelling would invent copy. Operator question §5-B. |
| 5 | Reused strings 「직접 질문 입력 →」 · 「AI 질문」 (note 22) | **Verified as described.** Both are the record's own words — 「직접 질문 입력 →」 is in result.md §Proposed copy (패널) and R6-2; 「AI 질문」 is the nav label and the launcher's own name (§Surfaces, R6-1). Only the *slots* (idle send button, field accessible name) are unsigned, and reuse beats invention. Rendered and measured on both surfaces. |
| 6 | Preset chip text = served `korean_name` + R6's 실권주 sentence (note 23) | **Verified as described.** All 5 field chips matched the served `korean_name` byte for byte; the 실권주 chip is R6's own sentence; the trailing chip is 「직접 질문 입력 →」; nothing unaccounted for; a 철회 event yields no presets. |
| 7 | Mobile menu row order — §Mobile 「메뉴 첫 행」 vs §Surfaces nav-third (note 23) | **Judged: keep the third slot; catalogue the contradiction.** §Surfaces states a *position* with an ordinal (「nav 세번째 자리 「AI 질문」」) and the mobile sheet mirrors the nav list; §Mobile's 「메뉴 첫 행 ≥44px」 is inside a list of **touch-target/behaviour** constraints, and the constraint it actually carries is satisfied (**rows 48 px, 메뉴 button 44 px**, measured). Moving the row would break the only clause that is unambiguously about position, or else make the sheet disagree with the nav — a new inconsistency the record never asks for. Operator question §5-C. |
| 8 | SSE through a production `next start` proxy with the **live** agent (note 21 / Open Question 4) | **Fixed** (fix 1) — this is where the gzip buffering was found. Longest observed inter-frame gap **6.0 s**; **no heartbeat exists** — recorded for P4. |
| 9 | 의견 turn ended in a 폴백 refusal (**new**) | **Fixed** (fix 2). |
| 10 | Raw numerals in agent prose (**new**) | **Catalogued.** The agent prints contract values as-is — `3200원`, `5767800주`, `0.2314082845주`, `15552원` — which is literally R6 §Agent's 「모든 수치는 도구가 돌려준 검증 계약 값 그대로」, while every *rendered* surface in the product prints `3,200원`. Formatting inside prose would be the agent transforming a number, so it was not done. Operator question §5-D. |
| 11 | ▷ ledger invisible under a default `uvicorn` (**new**) | **Catalogued for P4.** The line is `log.info` on the `mijual.web.ask` logger; uvicorn configures only its own loggers, so the root stays at `WARNING` and **the spend record is never printed**. Verified: 0 ledger lines under `uvicorn mijual.web.app:app`, and the line above appears the moment `logging.basicConfig(level=INFO)` runs. Nothing was changed here — logging configuration is P4's, and adding `basicConfig` to the app would pre-empt it. Operator question §5-E. |
| 12 | 철회 event is not *searchable* by company name (**new**) | **Catalogued.** 「썸에이지 유상증자 어떻게 되나요?」 → `이벤트 검색 「썸에이지」 → 0건` → 공시에 없음, while the same event asked by **filing number** produces R6's signed 철회 refusal. This is the recorded contract working as designed (a withdrawn event is not exposable, so it is not a search result — `P6.S2` note 19; and 「exposure is not re-decidable」), but R6's own Refusal card is a 썸에이지 철회 conversation. Operator question §5-F. |
| 13 | Refusal turns render a 푸터 (**new**) | **Catalogued.** A completed refusal shows 「근거 0건 · {시각} KST」 + 다시 질문 under R6-7's three parts. R6 signs the 푸터 for 답변 and gives 거절 its own anatomy; the line is honest (0건 really is 0건) and the ③ 갈 곳 links correctly render **once** (the footer's link row is suppressed when the refusal already drew them). Operator question §5-G. |
| 14 | Ops 대화 로그 / 익명 세션 timestamps render raw ISO (**new**) | **Catalogued, not changed.** 「시각」 shows `2026-08-22T22:25:38+09:00` while the sibling 독자 계정 table on the same tab shows `2026-08-22 17:16 KST`. The value **is** KST, and `components/ops/log.ts`'s `cellText` states the rule deliberately — 「Nothing is reformatted: this panel quotes its source」 (P5.S16's three-tier convention). Changing it means overriding a P5-landed decision or making the API serve display strings; both are wider than a fidelity fix. Operator question §5-H. |
| 15 | Korean glyphs inside the mono 도구 행 (P5.S19 §6's class) | **Catalogued, unchanged** — same disposition as P5.S19: the 도구 행 is an element **R6 itself draws in mono** (「mono `--text-xs` `--ink-3`」), and R1's rule is 「Korean **prose** never mono」, which holds (measured: prose = Pretendard Variable; the mono row falls to Apple SD Gothic Neo for its Korean). A cross-platform fix means editing the landed `tokens.css` — a design change. |
| 16 | 대화 로그 session cross-link → `/ops/users` unfiltered (**new, P5's surface**) | **Catalogued, out of P6's scope.** R7 signs a two-way cross-link; the log→sessions direction lands on the tab without a session filter. `P6` changed no `/ops` route or component (a phase constraint), so this is `P5.S16`'s panel. |

---

## 5. Operator questions, consolidated

None of these is an implementation defect: each needs a **new decision** — a visual
one, a copy one, or an operations one.

- **A. 필드로 이동.** R6's footer signs three context links and the product renders
  two. Giving the reader the third needs a new server-side link kind and a field
  anchor on the detail page. Draw it, or strike it from the footer's list?
- **B. The footer link row.** With three filings read, the row carries 7 links on
  3 lines and repeats 「이벤트 상세」 three times, one of them for a filing that is
  not among the 근거. Should the row be limited to the answer's own 근거, capped at
  one filing, or labelled per filing (new copy)?
- **C. R6's internal contradiction on the mobile menu.** §Mobile writes 「메뉴 첫
  행」, §Surfaces writes 「nav 세번째 자리」. Shipped as third in both nav and sheet.
  One line either way — the operator owns the record.
- **D. Numerals inside agent prose.** `3200원` (agent) vs `3,200원` (page). R6 says
  the agent quotes the contract value as-is; the product's own type rules format
  every rendered numeral. Should the *tool contract* hand the agent
  presentation-formatted values (it already owns presentation elsewhere), or does
  raw stay?
- **E. The ▷ ledger needs a logging configuration at deploy (P4).** Without one,
  agent spend is recorded nowhere. The turn already computes it; only the handler
  is missing.
- **F. 철회 by name.** R6's Refusal card is a 썸에이지 철회 conversation, but a
  withdrawn event is not exposable and therefore not searchable, so asking by
  company name gives 「공시에 없음」 instead. A fix would mean telling the search
  tool about non-exposable events — a change to the exposure contract, which this
  phase may not re-decide.
- **G. Does a refusal get a 푸터?** It currently does (`근거 0건 · {시각}` + 다시
  질문). R6 signs the footer under 답변 and gives 거절 its own three-part anatomy.
- **H. Ops timestamp format.** Two tables on one tab print instants two ways,
  because `log.ts` quotes its source by design. Decide which convention the 대화
  로그 · 익명 세션 · 대기열 columns follow.
- **I. Carried, still not P6's to invent** — the 운영자 연락처 string is unset
  (`get_contact` answers 미정, honestly), plus P5's standing four (English 404,
  the locked 내 종목 연결 line, the dated 49.2억원 figure, 「샘플 로드 여부」).

---

## 6. Validation

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest` | **137 passed** (136 → 137: one terse case for fix 2), 1 pre-existing httpx deprecation warning, ~3.5 s, no network, no model |
| `npm run build` (frontend) | **PASS** — compiled in 358 ms, 15/15 static pages |
| `npm run typecheck` | **PASS** |
| `npm run smoke` | **PASS** — 15/15 |
| `python3 scripts/workflow.py validate` | **PASS** |
| Live browser pass | 41 stages, ~120 scripted checks at 1440 / 768 / 481 / 480 / 390, 16 screenshots |

**Re-measure before believing a failure** (P5.S19 gotcha 9b held again): five
"FAIL" lines in this pass were probe artifacts — `span:nth-child(3)` matching the
ring instead of the close glyph; `elementsFromPoint` returning the transparent
`.close` overlay; an `active` transform read mid-transition; the sticky bar
measured on the `<form>` instead of its `.bar` wrapper; and `/ops/feedback`
being the **vocky** 관찰 뷰 while the save_feedback 대기열 lives on the
Conversations tab. Each was re-measured with a scoped selector and passed.

**One measurement tool distorted its own subject**, worth recording: a
`Response.clone()` tee installed to capture raw SSE bytes **buffers** — it showed
one 2,096-byte chunk where the wire had seven spread frames. Every timing claim
above therefore comes from `curl` (the wire) or a `MutationObserver` timeline (the
reader), never from the tee.

## 7. Hygiene

- Both servers were stopped afterwards; the headless Chrome profiles were
  temporary and removed.
- Ops credentials were passed as **process environment variables for this run
  only** (`MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` / `MIJUAL_SESSION_SECRET`); the
  operator's `.env` was read only by the app itself and never opened or edited.
- `NEXT_PUBLIC_VOCKY_SRC` stayed unset, so no third-party script loaded.
- **24 conversation turns and 3 feedback rows now sit in the dev Postgres.** They
  are the product's own anonymous log (no account/email/IP/UA column, no foreign
  key) and they are what makes the three ops tabs demonstrably alive; delete them
  with an ordinary `DELETE` if a clean dev log is wanted.
- No commit, no workflow status transition, and nothing under
  `docs/reference/design/` was read-write.
