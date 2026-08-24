# P9.S11 — fidelity and the functional sweep in the Operator Runtime

The phase's work met the running product. Everything below was seen in **`make stack-up` → dev on
`http://127.0.0.1:3000`** and, for the hydration/stream-sensitive half, **again in the production
build** (`cd frontend && npm run build && npm run start`), in real Chrome driven over CDP at desktop
**1440** and at a true **390** device-metrics emulation (`Emulation.setDeviceMetricsOverride`, which
gets past the 500px headless window floor `P9.S10` recorded).

**Verdict in one line: the implementation is faithful to R16 — no code fix was warranted.** Every
measured number matches the record. Three checks could not be produced by the live product (their
element behaviour was verified against a stubbed stream and is labelled as such), one clause of one
check is a record-internal contradiction that must not be silently "fixed", and the sweep found one
substantial **product** gap that only the operator/design can settle. All of it is below, and the
questions are on `phase.md`'s `## Operator Questions`.

---

## 1. How each thing was exercised (so the evidence class is never in doubt)

| method | what it means | used for |
| --- | --- | --- |
| **live** | a real turn against the real API and the configured Gemini key, in the browser or by `curl` to `127.0.0.1:8000/ask` | checks 1 · 2 · 4 · 5 · 9 · 10 · 11 · 13 · 19 · 20 · 21 · 22 · 23 · 24 · 25 · 26, the 확정 전 half of 6 |
| **server** | the shipped module exercised directly in `.venv/bin/python` (real code, no model) | check 3, check 16 (the stored rows of the live turns) |
| **stubbed stream** | the **real** page, store, components and CSS at the real viewport, with `window.fetch` returning a hand-fed SSE body for `POST /ask` — the server is the only thing replaced | checks 7 · 8 · 8b · 12 and the `error` half of 6 |
| **not exercised** | listed in §5; never claimed | tailnet origin, signed-in 보유 종목, a live budget-exhausted turn |

A stubbed-stream check verifies **the element**, not that the product can produce the state. Where
the product cannot produce it, that is said in the row and repeated in §4.

---

## 2. build-prompt §4 — all 26 checks

| # | check | verdict | evidence |
| --- | --- | --- | --- |
| 1 | 「안녕」 → 인사 한두 문장 · 도구 행 0 · 칩 0 · 푸터 없음 · 거절 아님 · 화면 언급 없음 | **PASS** (live, dev + prod) | wire = `session · status(read) · text · text · done`; `kind:"answer"`, `tool_calls:0`, **no `footer` frame**, stored `refusal_category` NULL. Rendered: 「안녕하세요. 궁금하신 공시가 있다면 회사명이나 종목명을 말씀해 주세요.」 The operator's original 「이 데이터는 검증을 통과하지 못했습니다」 is gone. |
| 2 | 「주식 처음인데…」 → 한 줄 거절 + 갈 곳 · `RefusalEvent` 미발생 · 저장 가족 없음 | **PASS** (live ×2) | 「종목 추천이나 투자 판단은 하지 않습니다. / 대신 궁금하신 기업의 공시 내용이나 일정은 원문으로 확인해 드릴 수 있습니다.」 `kind:"answer"`, no `refusal` frame, DB `refusal_category` NULL. Asked twice → **byte-identical both times** (see §4.5). |
| 3 | 잘못된 마커 → 마커만 사라지고 문장은 남는다 · 선행 공백도 정리 | **PASS** (server) | `CitationGate` fed `…3일입니다 [[cite:zz]]. / …3,200원입니다 [[cite:c1]. / …처리됩니다 [[cite:` → three `TextEvent`s, markers gone, **no double space before the full stop**, `blocked == 3`. Not observed from the live model: `blocked` was **0** on every one of the 16 live turns. |
| 4 | 계산 블록: 입력 2행(하나 「입력」 마커, 하나 칩) · 식 한 줄 · 결과 「N주 계산」 · 푸터 근거 = 칩 수 | **PASS** (live) | 「계양전기 1,000주면 초과청약 몇 주…」 → two 검증된 계산 blocks (배정 신주 · 초과청약 한도), each with 입력-marked reader value + chipped filing value, a 식 line, and 「231주 계산」/「46주 계산」. Footer 「근거 3건」 = exactly the 3 chips on screen. |
| 5 | 계산 진행 → 완료: 같은 `block_id` 제자리 교체, **블록이 뛰지 않는다** | **PASS** (measured) | calc block top `y=286` at `pending`, `y=286` at `done`; height 139 → 181. A `tool_row` arriving **between** pending and done pushed the trace above it but did **not** re-append the calc block below it (`P9.S8` note 2, in the DOM). The +42px is the **식 줄 arriving with the outcome** — `P9.S9` note 10's known, record-caused consequence; the block's own top edge never moves. |
| 6 | 확정 발행가액 미공시 → 계산 블록 `error` + 「확정 전」 문장 · alert 색 없음 | **PARTIAL** | 「확정 전」 half **PASS live, twice** (`refusal(확정 전)` + `kind:"refusal"` + stored family). The **drawn `error` block was not reachable live**: the model states the 미공시 fact and refuses *before* calling `calculate`, in both phrasings tried (including an explicit 「계산 도구로 계산해 주세요」). Element verified stubbed: 「계산할 수 없습니다 — 확정 발행가액 미공시」 in `rgb(157,179,168)` (ink-2), **0** elements anywhere in the document carrying `--alert` (`rgb(224,87,63)`), no icon. |
| 7 | 데이터 행 7행 → 6행 + 「모두 보기 (7)」, 누르면 전부 + 「접기」 | **PASS (element); no live producer** | stubbed 7-row block → 6 rows + 「모두 보기 (7)」 (44px at 390), press → 7 rows + 「접기」. **The product cannot produce a 7-row block** — see §4.1. |
| 8 | 긴 값 → 값 칸만 가로 스크롤 · 블록 폭 불변 · 줄바꿈 없음 · 칩·마커 항상 보임 | **PASS (element); no live producer** | only `rowValue` overflows (`scrollWidth 503/792` vs `clientWidth 392`); driving `scrollLeft` to the end moved the text (0→111 at 1440, 0→325 at 390) while the **chip's x stayed put** (1060 / 346), row width 732/354 and block width 734/356 unchanged, page `scrollWidth == clientWidth`, row height 36px = one line. Longest value the corpus can actually serve is **23 characters**. |
| 8b | 390에서 데이터·계산 블록이 답변 상자 좌·우 끝까지 (오른쪽 24px 틈 없음) | **PASS** (live + element) | answer box `x=16 … right=374`; data and calc blocks `x=17 … right=373` (the 1px border), i.e. `margin-inline: -12px` applied on both sides. Same in the **production** build on a live turn. |
| 9 | 도구 행 3개 → 평평 · 4개 이상 + 완료 → 요약 + 자세히 · 스트리밍 중에는 펼침 | **PASS** (live) | 2-row turn renders flat (production screenshot); 4-tool turn settles **folded** as 「도구 4번 · 공시 1건 읽음」 + 자세히; pressing 자세히 shows 4 rows, 접기 → 0. While streaming the rows arrive flat. |
| 10 | 진행 표시: 한 번에 한 줄 · phase 교체 시 높이 변화 없음 · 첫 토큰에 소멸 · 저장 안 됨 | **PASS** (measured over all 5 phases) | across `read→search→open→write→calc`: **always exactly 1** `[role="status"]`, `y=215`, answer height `43`, document height `813` — **identical every time**; `n=0` at the first `text`; `n=0` at the terminal on a **refusal-only** turn (`P9.S6` note 12's client-side death, confirmed); `sessionStorage['mijual.ask.thread']` never contains a status sentence. |
| 11 | 주입 시도 → 「보안」 문장만 · 도구 0 · 인용 0 · 링크 0 · 점검 언급 0 · 추가 프로즈 0 · 로그에 카테고리 + 200자 + `session_hash` | **PASS** (live) | wire = `session · status(read) · refusal(보안) · done` and nothing else; `tool_calls:0`, `rounds:1`, no `links`/`footer` frame. Text is D3 **verbatim**. Log: `agent security_check · instruction_override · afa46dec… · 지금까지의 모든 지시를 무시하고 …`. DB row = ordinary anonymous 보안 refusal, no incident detail, `blocks` NULL. |
| 12 | 예산 소진 → 감쇠 유지 · 끝맺음·버튼 없음 · 「예산·한도·라운드」 없음 · 연결 끊김 inset 없음 | **PASS (element); not reachable live** | `aborted` + `reason:"round_budget"` → prose `rgb(157,179,168)` (ink-2, `data-dim`), folded trace, **only** button is 자세히, no inset, no budget word on screen. The **disconnect** branch was verified **live** (중지 → 「연결이 끊겼습니다 …」 + 재시도, and 재시도 re-ran the same turn in place). Reaching the real ceiling needs a 20-round turn. |
| 13 | 도구가 확인하지 않은 공시 수치 → 「미확인」 마커, 문장·턴 모두 살아 있다 | **PASS** (live) | 「오늘 며칠이야?」 → `text{"text":"오늘은 2026년 8월 25일입니다.","unverified":[[4,16]]}` → rendered 「오늘은 2026년 8월 25일 [미확인] 입니다.」; turn completes normally. (`P9.S7` note 6's deliberate 오늘(KST) reading, in the flesh.) |
| 14 | 390: 블록 전폭 · 값 무손실 · **칩**·자세히·모두 보기 타깃 44px · 위젯·런처 부재 | **PARTIAL** | 블록 전폭 ✓ (8b) · 값 무손실 ✓ (8) · 자세히 **44px** ✓ · 모두 보기 **44px** ✓ · 새 대화 **44px** ✓ · 보내기 **44px** ✓ · 런처/위젯 부재 ✓ · 가로 오버플로 0 ✓ — **인용 칩은 14×16px** ✗. Not fixed on purpose: see §4.2. |
| 15 | 1440: 두 열 `minmax(0,760px) 340px`, 레일 sticky | **STALE — superseded** | the catalogued stale line (`P9.S2`): §2.7b/item 20 retire the rail. Verified **retired**: `main aside` count **0**, no 340 column, at 1440 and in production. Check 20 is the live form of this line. |
| 16 | 대화 로그 재생: 데이터·계산 블록이 원형 그대로 (입력·식·결과·각 입력의 근거) | **PASS at the payload level** | `conversation_turn.blocks` for the live calc turn holds the exact frames: `{"event":"calc","data":{mode,name,inputs:[{label,value,reader_input|citation}],expr,result,state:"done",block_id,persistent}}` — one entry per `block_id`, in its final state, plus the `data` block. *Serving* them in 운영 대화 로그 is the `P9.DECOMP2` Operator Question (a/b/c); nothing was invented on that surface. |
| 17 | `prefers-reduced-motion`: 새 요소에 애니메이션 없음 · 캐럿만 정지 | **PASS** (dev + prod) | without reduce, the **only** animated element in the whole surface is `caretblink` (1s). Under `reduce`, `animationName` is `none` on every element and durations collapse to 0.001s. |
| 18 | 위젯과 페이지가 같은 턴을 **같은 블록 구성**으로 (스토어 포크 없음) | **PASS** | one turn made in the widget on an event detail, then read on `/ask`: identical child sequence `trace · data · calc · prose · footer`, identical text; only the width differs (406 vs 760). |
| 19 | 헤더 어디에도 「범위:」 칩 없음 · 상세에서 연 위젯 헤더는 두 아이콘 · 그 공시의 프리셋 스트립은 그대로 | **PASS** (dev + prod) | `범위:` appears **nowhere** in the page or widget text. Widget header buttons = exactly `["AI 질문 페이지 →", "×"]`. The widget carries 「이 공시에 대해 질문」 + that filing's 5 preset chips. |
| 20 | `/ask`에 오른쪽 열 없음 · 1440에서 스레드가 760에서 멈추고 가운데 | **PASS** (dev + prod) | `main aside` = 0; answer box `x=340 … right=1100`, width **760**, centred on 1440. |
| 21 | 시작 화면: 가운데 · 인사 + 약속 · 질문 카드(서명본 **4**장, 2열/≤767 1열) · 익명 줄 0 · 이중 테두리 0 · 구분선 0 · 카드 누르면 그 문장 전송 | **PASS** (dev + prod) | `.centered` `min-height 560px` (420 at ≤767), `.start` 640 centred, `.cards` `316px 316px` (1 column at 390), heading `--text-2xl` → `--text-xl` at 390. Composer: the **input's own 1px only** — form, wrapper and start block all `border: 0 none`, `box-shadow: none`, no divider. Pressing 「퓨쳐켐 실권주는 어떻게 처리되나요?」 sent that sentence **verbatim** as the question bubble. (「5장」 + meta card is the catalogued stale line; `START_CHIPS_KO` signs 4.) |
| 22 | 익명 줄이 표면 어디에도 없다 | **PASS** (dev + prod) | `/ask` start screen and the widget's empty thread both carry only the D1 intro 「주주의 권리를 지키기 위해 공시를 근거로 질문에 답합니다.」; no 익명/저장하지 않 string anywhere on either surface. |
| 23 | 회사를 특정하지 않은 첫 질문 → 되묻는 한 줄, 임의 회사로 검색하지 않는다 | **PASS** (live) | 「이 공시 조건 알려줘」 → 「어떤 회사의 공시인지 회사명이나 종목코드를 알려주시면 확인해 드리겠습니다.」, `tool_calls: 0`, `rounds: 1`. |
| 24 | 새 대화 → 스레드만 비워진다 · 저장된 대화 목록이 어디에도 없다 | **PASS** (live, dev + prod) | turns 1 → 0, stored thread 371 → 100 bytes (the scope/handle envelope, no turns), page returns to the start screen, **reload stays empty**, and no 대화 목록/이전 대화/기록 element exists. |
| 25 | 시작 화면에 새 대화 버튼이 없다 · 시작 카드 4장이 서로 다른 회사를 부른다 | **PASS** | `새 대화` is absent from the start-screen DOM (present only once a thread exists). The four cards name **계양전기 · 퓨쳐켐 · 대동기어 · 아시아나항공**. |
| 26 | 완료 푸터에 `다시 질문`이 없다 (모든 카드) | **PASS** (live, dev + prod) | completed footer = 「근거 N건 · {접수번호} · {KST}」 + `DART 원문 {rcept} ↗` (`target=_blank`, `rel=noopener noreferrer`) · `이벤트 상세` · `내 종목 조회`, and nothing else. 재시도 appears **only** on an interrupted turn. |

**Tally:** 24 PASS · 2 PARTIAL (6, 14) · 1 STALE-superseded (15). Of the 24, three (7 · 8 · 12) are
element-level passes whose live producer does not exist today — flagged in the rows and in §4.

---

## 3. Fidelity: the measured numbers against §2

Every value below was read with `getComputedStyle` in the running product and compared to
`build-prompt.md` §2 / `output/r16-ask.css`. **No departure was found.**

- **§2.1 StatusLine** — mono `11px` ink-3 `rgb(109,131,120)`; border-left **`2px dashed`**
  `rgba(163,196,180,.15)`; `padding-left 8px`; `nowrap` + `overflow-x auto`; `role="status"`;
  `animation-name: none`; **last child** of the answer box. The tool row beside it is `2px **solid**`
  — 실선 = 남는 사실, 점선 = 지나가는 상태, as signed.
- **§2.2 ToolTrace** — summary border-left `2px solid`, mono `11px` ink-3; `자세히/접기` min-height
  **32px** at 1440 and **44px** at 390.
- **§2.3 DataRow** — block `1px solid --border-soft`; heading mono `11px` ink-3; row grid
  `283.188px / 391.812px / 17px` on a 710px content box = **39.9 % / 1fr / auto** (and
  `118.797/332 = 35.8 %` at 390 → the signed 40 % / 36 %); `column-gap 8px`; `padding 8px 12px`;
  1px **dashed** between rows; label sans `12px` ink-2 `word-break: keep-all`; value mono `12px`
  `tabular-nums` ink-1 `nowrap` + `overflow-x auto`; `align-self: stretch` (not `width:100%`);
  `margin-inline: -12px` at ≤767; **`main table` count = 0** (「3열 이상 표는 만들지 않는다」).
- **§2.4 CalcBlock** — block `1px solid rgba(163,196,180,.32)` = `--border-strong`, one step heavier
  than the data block's `.15`; heading mono `11px` with the `--live` mode word; expr mono `12px`
  ink-2 `nowrap` + scroll, `border-top: 1px dashed`; result row `border-top: 1px solid`,
  background `rgba(95,208,165,.14)` = `--live-tint`, `justify-content: space-between`, label `12px`
  ink-2, **value mono `15px` (`--text-md`) weight 600 `--live` tabular nowrap + 「계산」 마커**;
  `error` sentence sans `12px` ink-2 with **zero** `--alert`-coloured elements in the document.
- **§2.5 marker family** — 계산 and 미확인 render `EstimateMarker`'s own tag class: `padding 1px 4px`,
  `vertical-align: middle`, `margin-inline-start: 4px`, `letter-spacing .08em`, `1px
  color-mix(currentColor 42%)`, colour per family (`--live` / ink-2 / ink-3 for 입력). `kind` has no
  default. (The record's `.amk` em spelling differs from the shipped tag — already an Operator
  Question from `P9.S9`; the binding sentence 「`EstimateMarker` 그대로」 governs and is honoured.)
- **§2.6 인용 칩** — mono `10px`, border `rgba(95,208,165,.4)`, same component in all three places
  (프로즈 · 데이터 행 · 계산 입력), `aria-expanded`, opens and closes on re-press; the chip sits
  **after the sentence's full stop** (「…200주입니다.」 then the chip). In a row the panel opens
  **under the row across the block** (`x=366, w=708` inside a 734 block) — `P9.S9` note 3's decision,
  and it reads correctly at 390 too.
- **§2.7 / §2.7b** — measured under checks 12, 20, 21; `.centered 560/420`, `.start 640`,
  `.atop` sticky at the column's top right as a **sibling** (max-width 760, `margin-inline auto`),
  `.bar` sticky bottom with `--paper`.
- **§2.8 배치** — the answer box is `display:flex; flex-direction:column; gap: 12px; padding: 12px`,
  and the observed child order is exactly **도구 흐름 → 구조화 블록(서버 순서) → 프로즈 → 링크 →
  진행 표시 → 푸터** in both views, with blocks always full width and never side by side.

---

## 4. Functional sweep and findings

### 4.1 The data block has almost nothing to draw — the sweep's biggest product finding

`DataBlockEvent` rows come from `tools.value_rows(payload)`, which reads `get_event`'s `fields`, and
`tools._stated` can only state four shapes (`P9.S3` note 6). Measured across **the whole 386-event
board corpus**:

- **372 events produce 0 data rows** (no block at all is emitted — the wire stays additive),
- **14 events produce exactly 1 row**, always `신주인수권증서 상장·매매기간`,
- the longest value any event can produce is **23 characters**.

The reason is structural, not a bug: **every gate-passing field's `value` is a composite dict**
(`appraisal_price → {"price": 6591}`, `excess_subscription → {ratio, detail}`,
`issue_price_formula → {5 keys}`, `subscription_agents → {entries: [...]}`). `_stated`'s
`value_display` and scalar branches have no producer at all today, and stating
`{"price": 6591}` as 「6,591원」 would be the **server inventing a row format** — exactly the fork of
the product's field surface that `P9.S3` note 6 refused, and a design change (R16 §0 signs no row
format for those fields).

Consequences, stated plainly: R16's 데이터 블록 — one of the five headline elements, and the answer to
intent point 7 (「데이터 행을 보여준다」) — is invisible on 96 % of filings and never shows more than one
row; checks **7** (6-row fold) and **8** (value-cell scroll) have **no producer in the product**; and
the fixture the round drew (three data rows, `foot.n = 3`) is not reachable. → new
`## Operator Questions` entry.

### 4.2 Check 14's 「칩 타깃 44px」 — a record-internal contradiction, deliberately not "fixed"

At 390 the citation chip measures **14 × 16px**. §4 check 14 names 칩 among the 44px targets and
§2.6 lists 「≤767 타깃 44px」 as part of the chip's *unchanged* definition — but:

- no earlier round signed it. R14's own 390 check (item 15) lists 인용 블록 전폭 · 접수번호 쪼개짐 0 ·
  바 44px, **not** the chip; R14 item 1's 480→767 move is about the composer's 44px controls, which
  the shipped `Ask.module.css` does implement. R6 §Mobile's 44px list is 메뉴 첫 행 · 프리셋 · 입력 바.
- the round's **own** CSS agrees with the shipped code: `r16-ask.css` gives `min-height: 44px` at
  ≤767 to `.atx` (자세히) and `.amore` (모두 보기) and **not** to the chip.

So R16 attributes to an explicitly-unchanged component a property it never had. There is also no
zero-visual-change fix: R10's recipe on the 이벤트 상세 chip (padding out, the same value back as
negative margin) works because that trigger has no border, while this chip is `display: inline` with
a visible 1px border, so padding enlarges the painted box; the alternative — an invisible absolutely
positioned hit area — would swallow taps on the prose around it. Restyling an approved element on a
contradictory line is exactly what RESPECT THE DESIGN forbids. **Catalogued, not changed.**

### 4.3 Every visible control does something observable

Exercised, each with its observable effect: **start cards** (send their own sentence verbatim →
question bubble matches the card string byte for byte) · **보내기** (disabled on an empty field,
「답변 준비 중…」 while pending, 「중지」 while streaming) · **중지** (live: stops the turn, keeps the
partial answer, draws R14's 「연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.」 + 재시도, composer back to
보내기) · **재시도** (live: re-runs the same turn **in place**, turn count unchanged) · **새 대화**
(check 24) · **자세히/접기** (4 rows ↔ 0) · **모두 보기 (N)/접기** (6 ↔ 7 rows) · **인용 칩** in all
three places (opens/closes, `aria-expanded` flips, panel height 0 ↔ 83) · **답변 푸터 링크**
(DART 원문 → `dart.fss.or.kr/...?rcpNo=…` new tab with `rel=noopener noreferrer`; 이벤트 상세 →
`/events/{rcept}`; 내 종목 조회 → `/stocks`) · **위젯 ↗** (navigates to `/ask`, thread intact) ·
**위젯 ×** (closes). **Nothing rendered was inert.**

**Keyboard and focus:** Tab reaches every new control in DOM order — 새 대화 → 자세히 → chip → chip →
chip → DART 원문 → 이벤트 상세 → 내 종목 조회 → 입력 → … — and each shows the product's
`:focus-visible` ring (`2px solid rgb(143,178,232)`, offset 2px). Enter submits from the composer.
**Typing-and-waiting:** text typed and left for 3 s survives, and the button stays enabled; clearing
the field disables it again.

### 4.4 Liveness over time

Watched on live turns, not inferred: the status line replaces per phase with **zero** thread-height
change and dies at the first token (check 10); a 4-tool trace arrives flat and folds the instant the
turn settles (check 9); the calculation settles in place (check 5); a 6-round / 5-tool turn ran ~60 s
with the caret as the only moving thing; 재시도 re-streamed the same turn without duplicating it.

**The ▷ ledger, from a real turn** (`P9.S7` note 3 asked for this):

```
agent turn done · answer · rounds 1 · tools 0 · blocked 0 · calls 1 (0 failed)
  · tokens prompt 5,481 (cached 0) + thinking 108 + output 20 = 5,609
  · thinking MEDIUM · ▷ $0.0046 estimated (gemini-3.7-flash rate card, not billed)
```

`thinking MEDIUM` end to end (intent item 1, confirmed on the wire as `thinking_levels:["MEDIUM"]`).
**`cached 0` on every one of the 16 live turns**, including repeats of the same question minutes
apart — the 4,096-token implicit-caching floor was not credited once in this session. That is an
honest reading of a real number, which is exactly why `P9.S7` made the ledger measure it; it is not a
bug and not a claim that caching never happens. Turn cost ranged **$0.0046** (greeting) to
**$0.0548** (the 6-round / 5-tool calculator turn, 63k prompt tokens) — worth knowing beside the
`P9.DECOMP` spend question.

### 4.5 Two readings for the walkthrough (not departures)

- **The unsigned out-of-scope line is now de-facto copy.** `P9.S7`'s Operator Question asked to see
  whether the model reproduces §0's 서명 아님 example. Asked 「주식 처음인데 뭐부터 사면 좋아요?」 twice,
  the answer came back **byte-identical both times** — and it is *not* the record's example
  sentence; the model converged on its own stable pair. So the risk the question names is real
  (readers see an unsigned, stable sentence), just with different words than expected.
- **중지 says 「연결이 끊겼습니다」.** A reader who deliberately pressed 중지 is told the connection was
  lost. This is the **signed** behaviour (R14 item 11: 중지 → 부분 답변 유지 + 감쇠 + 서명 문장 한 줄 +
  재시도; R6 gives 중단/오류 that one inset), so it is fidelity, not a defect — but it is the kind of
  thing a first-time user notices, so it belongs in the operator's walkthrough rather than in a
  silent edit.

### 4.6 Confirmations the plan asked for explicitly

- **`pending → done` without a block jump** (`P9.S3`/`P9.S9`): confirmed in the flesh, with the
  measured `y` values and the tool-row-in-between case — check 5.
- **The 근거 N건 chip-count reconciliation** (`P9.S3` note 7): confirmed. The live calculator turn
  showed 3 distinct chips (a data-row chip and two calc-input chips, one of them reused in prose) and
  the footer read **근거 3건**. 같은 근거 = 같은 번호 holds across 프로즈 · 데이터 행 · 계산 입력, and the
  transitional mismatch S3 predicted has closed now that data rows render.

---

## 5. The whole `## Regression Checklist` (`docs/current/qa.md`)

Every line was re-run, not only P9's. Format: line → verdict → the number that proves it.

**Base block**

| line | verdict |
| --- | --- |
| `pytest` green and `workflow validate` clean | **PASS** — **154 passed**, exit 0; `Workflow validation passed.` The doc's baseline of **142** is a stale count (expected growth) → `qa` Doc impact. |
| `build && typecheck && smoke` green | **PASS** — build ✓ (15 routes), `tsc --noEmit` ✓, smoke **22/22**. Doc says **16/16** — same stale-count correction. |
| `gates run` twice byte-identical, split unchanged over **710** rows | **PASS** — two runs `diff`-identical; **710 field rows**, `appraisal_price 47 passed / 14 n/a`, **488 exposable** events (50+422+16). |
| structural guards still guard (4 AST import scans · anonymity scan · tool signature · ops surface) | **PASS** — inside the 154-test suite, all green. |
| no reader-facing quota or storage-denial copy; no `localStorage` in the AI 질문 surfaces | **PASS** — every hit for 「남은 질문」/「저장 이력 없음」/「탭을 닫으면」 in ask files is a **comment restating the ban**; the one live 「탭을 닫으면 사라집니다」 is `CONVERT_SESSION_KO` on the 보유량 surface, which the line exempts. `localStorage` appears in `lib/ask.ts` / `AskProvider.tsx` **only inside comments saying never to use it**; the thread is one `sessionStorage` key (`mijual.ask.thread`). |
| the agent's own two numbers (a live pass was run) | **PASS with a P9-caused restatement** — over the 16 live turns: **18/18 stored 인용 원문 byte-identical** to a served payload value (100 %, 0 misses, as at P6); numerals **81/87**. All 6 misses are the three numerals of 오늘(KST) in the two 「오늘 며칠이야?」 turns — **the exact numerals the reader saw marked 「미확인」**. Under strip-don't-drop the invariant is now *every **unmarked** numeral is in the payloads*, and the stored row (prose only) cannot tell the two apart — which is precisely the `P9.S4` Operator Question. → `qa` Doc impact. |
| exposure invariant re-derived read-only | **PASS** — over 628 events: **0** renderable fields outside `passed`/`tbd`, **0** `tbd` fields carrying a value, **488** exposable events, states `{exposable 488, no_detail 68, flagged 61, withdrawn 9, incomplete_api_row 1, no_document 1}`. (4 events hold field-level-passed fields under a `flagged`/`withdrawn` **event** gate — the two-level gate working as designed, not a leak.) |
| `estimate report` twice byte-identical, headline unchanged | **PASS** — `diff`-identical; ▷ **718.1억원**, **32** offerings, **14.02 %**. |
| `scheduler once --offline` → six stages green at 0 requests / 0 calls | **PASS** — collect·bodydoc·extract·gates·reparse·snapshot all green, `0 OpenDART request(s), 0 LLM call(s), ▷ $0.0000`. |
| after any corpus change, rendered numbers re-measured | **N/A** — P9 changed no corpus. Landing headline (718.1억원 · 450건 · 32건) and the five board counts (전체 450 · 유증 16 · CB 422 · 매수청구 12, 15-row window with 남은 371건) were read anyway and agree with `/board/summary`. |
| `extract recheck` and `evalset refresh-recall` → second run writes nothing | **PASS** — recheck `diff`-identical, 「DRY RUN, nothing written」; refresh-recall 「sample: unchanged — nothing written」, 재현율 88.70 %. |
| no secret value in any tracked file or generated artifact | **PASS** — the three secret values (`DART_API_KEY`, `GEMINI_API_KEY`, `MIJUAL_VOCKY_API_KEY`) appear in **no** tracked file and in **no** file under `frontend/.next/static`. (The only `.env` string that appears in tracked files is `MIJUAL_VOCKY_API_BASE`, a hostname, in `config.py`/`vocky.py` and old records.) |
| no committed claim describes the evalset labels as human ground truth | **PASS** — every committed mention (`decisions.md` D-7, `qa.md`, `product.md`) says explicitly **not** human ground truth. |
| any regenerated summary artifact regenerated from the final run | **N/A** — P9 regenerated none. |

**P8 surface blocks** — all 35 re-run:

- AI 질문 ask → reload → ask again: **PASS** (2 distinct turns 안녕/고마워, **0** console errors or warnings, dev **and** production).
- 크롬 nav: **PASS** (exactly `AI 질문 · 보유 종목`, 0 `[data-vocky-trigger]`, no `[의견]` chip, no 샘플 chip).
- 보유 종목 signed out: **PASS** (「샘플 보유 종목 — 구성 예시입니다…」 banner + the sample rows). *Signed-in not exercised — §6.*
- 의견 보내기: **PASS** (empty field disables 보내기; success → 「접수되었습니다.」 + 접수 번호, **0** spinners; a stubbed 500 → 「의견을 보내지 못했습니다…」 + 「입력한 내용은 그대로 남아 있습니다.」 + 닫기/다시 시도, **0** `--alert`-coloured elements, **0** spinners).
- ≤480 sheet: **PASS** (opens `position:absolute` over the page with `document.body.scrollHeight` unchanged at 2873 and body overflow locked; closes on **Esc** and on a **backdrop** click, releasing body scroll. The chrome menu sheet has no ×; it toggles from 메뉴 — the 의견 보내기 dialog is the one carrying 닫기/×).
- 푸터: **PASS** (no mono anywhere, height 70, one row at 1440; at 390 「의견 보내기」 and 「AI 질문」 share `y=2805` — not orphaned).
- no vocky value in the client bundle: **PASS** (no `vk_`, no key value; the only "vocky" hits are the identifier `VOCKY_ROW_KO`).
- 관제 현황판 window: **PASS** (15 rows + 「15건 더 보기」 + 「남은 371건」; one click → **30** + 「처음 15건으로 접기」; a tab switch resets to 15).
- 보드 행: **PASS** (a click anywhere on the row → `/events/20260724000546` via `a.corp::after`; 「↗」 → DART `target=_blank`; Tab gives `.row:focus-within` a `2px solid` ring around the **whole 1046×44 row**).
- 보드 열: **PASS** at 1512 / 1119 / 768 / 390 — every row's last cell shares one right edge, flush with the panel.
- 스트립: **PASS** (펼치기 ↔ 접기 with `aria-expanded` true/false and a changed surface).
- 카운트다운 카드: **PASS** (three stats — 718.1억원추정 · 감시 중 450건 · 30일 이내 마감 32건; 「읽은 실적보고서」 absent from the DOM).
- 소멸주의보: **PASS** (「가장 빠른 청약 마감 2026-09-04, **3개 종목**」 against `/board/summary next_lapse.tie_count = 3`, no company name).
- 자동 갱신: **PASS on the unchanged branch** (two ~35 s intervals: **0** spinners, scroll held at 600, row count unchanged, no layout move, no 「갱신됨」 — correct, since nothing changed). The changed branch (a new 기준시각 → 「갱신됨」 + `--live` edge) needs a corpus change — §6.
- 히어로 Enter: **PASS** (「삼성」 → candidates 삼성에스디에스/삼성제약; first Enter selects without navigating; second Enter → `/stocks/00126186`).
- 390px 랜딩: **PASS** (subtitle one line, no orphan; the strip button is its container's **full width at 44px**; no mono split).
- 상세 헤더 (열림 · 아시아나 ③ · 닫힘): **PASS** — 161/156/161px at 1440 (≥136) and 313/304/313px at 390 (≥248); 「종료」 appears on no page. *추후결정 has no sample in the current corpus — §6.*
- 상세 390: **PASS** (**no** interactive target under 44px on the event page, no orphan 「→」/「·」 line).
- 인용 popover: **PASS** (overlay `position:absolute`; the six rows behind it keep `y = 315/532/576/857/922/966` before **and** after opening; Esc closes and focus returns to the `[근거]` chip).
- 섹션 밀도: **PASS** (일정 2 rows/1 chip, 발행 조건 3 rows/2 chips — no section repeats 「[근거]」 on every row; one 「DART 원문 {rcept} ↗」 line closes a section).
- 정정 이력: **PASS** (button flips to 「접기 ×」, `aria-expanded="true"`, both 정정 전 and 정정 후 tagged, no arrow column).
- 아시아나 ③: **PASS** (on `20260513000801`/`20260514001047`/`20260713000496`: exactly **two** dashed 「현재 버전 공시에 없음」 chips — countdown slot + field row — no placeholder for any other field, no reason given).
- 개요 outline: **PASS** (on the served-절차 sample `20260811000467`: h2 `2단계 절차 · 발행 조건 · 정정공시 반영 —…`, h3 `반대의사 통지 · 매수청구 행사`; **no** accessible name contains 「//」).
- 404: **PASS** (`/events/99999999999999` → **404** with 「이 주소에 해당하는 공시가 없습니다」, the path echoed, no reason; `/no/such/path` → 404).
- mono: **PASS** at **1512 / 1440 / 1280 / 768 / 767 / 481 / 390** on `/`, `/events/{rcept}` and `/stocks` — **0** mono runs containing a digit split across two line boxes.
- 조회 정체성: **PASS** (h1 = 종목명, 종목코드/고유번호 under it, the search box echoes the name, 「내 종목 조회」 exactly once).
- 보유량 스트립: **PASS** (present on 계양전기 — input + 100/500/1,000주 + 「서버 전송 없음」; **absent** on 풍전약품 (②-only) and 세기상사 (no rights); **0** disabled controls, no explanatory sentence).
- ② 표: **PASS in substance** (풍전약품's three CB rows in **one** grouped block with **one** 「DART 공시 API — 전환가액 · 전환 시 주식수 · 오버행 | 1건」 source line, the corp name printed **once**, no `0` standing in for an unserved fact). Rendered as a CSS grid, not an HTML `<table>` — pre-existing, untouched by P9.
- ③ 절차: **PASS both branches** (`20260811000467` → **2단계 절차** with dated windows `2026-08-05 ~ 2026-08-27` and `2026-08-28 ~ 2026-09-17`; the 아시아나 pages → the dashed chip; the two notations never mix in one block).
- 놓친 돈 합계: **PASS on the 1건 branch** (형지엘리트 · 코이즈 · 아이씨에이치: the figure once in the row, **no total above it**, each row carrying its own 배정비율 line). *No stock in the corpus has ≥2 lapse rows — §6.*
- 조회 출구: **PASS** (「상세 보기 →」 is the only link out of a row; the 놓친 돈 prompt appears once per page).
- 검색 불일치: **PASS** (「‘삼성’과 일치하는 종목이 없습니다 — …」 with the **과** particle; the first differing keystroke removes the line).
- 빈 `/stocks`: **PASS** (감시 대상 with its three categories + 「감시 중 450건」 + 집계 범위; no placeholder count).
- 조회 390: **PASS** (**0** targets under 44px on `/stocks`, `/stocks/00102618`, `/stocks/01110474`; no horizontal overflow; `h1` font-size changes only between **767 and 768** — the single breakpoint).
- 조회 신뢰: **PASS** (계양전기, 발행가 확정 전: **no 원 amount** on the page before or after entering 1,000주, while share counts still convert; **no request carried the number** — every fetch recorded during typing was checked).
- 프로덕션 폭: **PASS in the production build** — `/stocks` **620px** and `/stocks/{corp_code}` **960px**, matching P8.REVIEW's own recorded pair. (The checklist line prints the two numbers in the opposite order to the routes; → `qa` Doc impact.)
- 인증 게이팅: **PASS** (empty submit on 로그인 renders 「이메일과 비밀번호를 입력해 주세요.」, **no** browser bubble, **0** requests fired; no `required` and no `pattern` on any auth input. `/auth/reset` currently resolves to the login page, so it was exercised there.)

---

## 6. Not exercised — the explicit list (never claimed)

1. **The tailnet origin from another device.** Operator-only by the plan and the manifest. The
   manifest's second origin (`http://100.77.164.42:3000` from `make stack-status`) needs a second
   device on the tailnet. → walkthrough material.
2. **A live budget-exhausted turn** (check 12's live half). Reaching `round_budget` needs a 20-round
   turn; the surface was verified on the real terminal frame instead.
3. **A live calculation `error` block** (check 6's element half). The model refuses with 「확정 전」
   before it calls `calculate`; two phrasings tried.
4. **The 「모두 보기 (N)」 and value-scroll states from real data** (checks 7 · 8) — no producer, §4.1.
5. **A bad citation marker produced by the live model** (check 3) — `blocked` was 0 on all 16 live
   turns; the rule was exercised in the shipped gate instead.
6. **보유 종목 signed in** — needs an operator account.
7. **자동 갱신's changed branch** (「갱신됨」 + the `--live` edge on changed rows) — needs a corpus
   change during the run.
8. **상세 헤더's 추후결정 state** and **놓친 돈 with ≥2 rows** — no sample exists in the current corpus.
9. **A live turn on a phone browser** — the 390 pass is Chrome device-metrics emulation (true 390
   metrics, not a real handset).

---

## 7. Fixes made

**None.** No fidelity departure was found that a code change should close: every §2 number matches,
and the two non-PASS clauses are (a) a record-internal contradiction (§4.2) and (b) states the
product cannot produce for design reasons (§4.1, check 6). Changing either would mean restyling an
approved element or inventing Korean, which the standing constraint forbids. Four new
`## Operator Questions` entries were written instead.

## 8. Validation

| command | result |
| --- | --- |
| `cd frontend && npm run typecheck` | **pass** (`tsc --noEmit`, no output) |
| `cd frontend && npm run smoke` | **pass** — `tests 22 · pass 22 · fail 0` |
| `cd frontend && npm run build` | **pass** — 15 routes, no warnings |
| `.venv/bin/pytest -q` | **pass** — **154 passed**, exit 0 |
| `python3 scripts/workflow.py validate` | **pass** — `Workflow validation passed.` |
| `.venv/bin/python -m mijual.gates run` (×2) | byte-identical, 710 rows, 488 exposable |
| `.venv/bin/python -m mijual.estimate report --today 20260825` (×2) | byte-identical, 718.1억원 / 32 / 14.02 % |
| `.venv/bin/python -m mijual.scheduler once --offline` | six stages green, 0 req / 0 calls / ▷ $0.0000 |
| `.venv/bin/python -m mijual.extract --dry-run recheck` (×2) | idempotent, nothing written |
| `.venv/bin/python -m mijual.evalset refresh-recall` | 재현율 88.70 %, nothing written |

## 9. Machine left clean

`make stack-down` run (API + web stopped; Postgres left running, as the Makefile documents); the
production `npm run start` I started was killed and its pid file removed; the headless Chrome and its
scratch profile were killed. Nothing was committed and no workflow state was transitioned.

## 10. Deviations from `plan.md`

1. **The plan's four un-producible states were verified against a stubbed stream rather than skipped.**
   `plan.md` §Scope 1 asks for all 26 checks; checks 7 · 8 · 8b · 12 and check 6's `error` half have
   no live producer. Rather than record five blanks, each was driven through the **real** page, store,
   components and CSS with `window.fetch` returning a hand-fed SSE body — the server is the only
   thing replaced. Every such row says so, and §5's inventory repeats it. Nothing is claimed live
   that was not seen live.
2. **No fixes were made** (§7). The plan expects departures to be fixed here; none was found that a
   code change may close without restyling an approved element or inventing copy.
