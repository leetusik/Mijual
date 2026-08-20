# R3 Implementation Contract — Event Detail (`P3.S4`)

For the Next.js build. Renders the persisted `EventExposure`/`FieldView` contract — P3 never
re-decides exposure, never computes D-days in the browser, never re-punctuates a quote.
Reference cards: `detail/*.html` in the design project; tokens unchanged from R2.

## Token delta

None. Use `foundations/tokens.css` as landed in R2 (`.cosmos` scope on the page root).

## Page anatomy (all three types)

1. **Crumb** — "← 관제 현황판" (mono, text-sm).
2. **Header panel** (craft panel: `--surface-card` + `--border-strong` + `--panel-glow` +
   corner brackets):
   - left: `RightsChip type` → corp name (text-2xl bold) + "DART 원문 ↗" (mono link to
     `https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}`) → mono meta line
     (접수번호 · 최초 공시 `original_rcept_dt` · 정정 반영 when versions > 1).
   - **Identity**: show DART master `corp_name` only. Iff `corp_name_agrees_with_body ===
     false`, add one line under the name: `공시 본문 표기: {corp_name_in_body} — 원문에는 이
     이름으로 기재되어 있습니다`. Never for suffix-only differences (upstream already
     ignores them).
   - right: governing label (`countdown.label_ko`) → `DDay` (upstream-computed label +
     date) → mono window/state line. When `countdown.date === null`: 추후결정 →
     `StateBadge tbd` + "카운트다운 없음 — 일정이 공시상 미정"; field-absent (③ 아시아나
     case) → factual line "현재 버전 공시에 없음". Never a dash, never a stale date.
3. **환산 블록** (① only, decision §6-1): per-unit chain 예정/확정발행가 → 할인율 →
   (확정발행가 존재 시) `EstimateMarker` 증서 1주 이론가치 → 배정비율 printed to its full
   10 decimals. 확정발행가 null → chip `발행가 확정 전` + mono `확정 예정 {final_price_date}`.
   Button "내 보유량으로 환산 →" routes to 조회 (R4); no N주 input here. Post-결과 events
   append the 청약 결과 inset (발행·청약·소멸 shares + `EstimateMarker` 소멸가치 + 하한).
4. **Field sections** — section eyebrow `// {name}` (mono, tracked); rows = 220px label
   column (Korean `korean_name` from copy-inventory) + value + `Citation` per field
   (`quote` verbatim, `rcept_no`). Only fields with `exposable: true` exist in the DOM;
   `display: "추후결정"` renders `StateBadge tbd` (+ any non-date facts the value carries,
   e.g. 취급처 확정·청약일만 미정). Blocked fields: **no row, no marker.**
5. **정정 strip** (footer, `--surface-raised`): "정정공시 반영 — 최근: {interpretation.summary
   key figures} · {schedule_impact}" + "정정 이력" button → CorrectionStory view.
6. **Provenance line** (mono 10px): "모든 값은 DART 공시에서만 나왔습니다 · 각 항목의
   [근거]가 원문 구절과 접수번호로 연결됩니다".

## Type-specific rules

- **①**: governing = 매매 마감. Window open → live-green "거래 가능 · 마감 D-n". Past →
  faint D+, history. 청약 취급처 renders as a target/agent/date table (구주주 rows bolded).
- **②**: API-tier facts (전환가액, 오버행 %, 전환 시 주식수, 권면총액, 발행방법·만기) in a
  fact strip ABOVE 본문 fields; governing = 전환청구 **개시**, past opening = "진행 중",
  never 종료. `option_schedule`: render each option's `detail` string as the value; the
  stored `start_date ~ end_date` appear ONLY as a caption "청구 가능 구간 … — 연속 기간
  아님 · 행사 가능일은 위 조건이 정함". Never a plain 기간, never a bar. Sparse ② (본문
  fields = 0): fact strip + closing line "공시 본문에서 확인된 추가 조건이 없습니다 — 위
  값은 DART 공시 API 기준입니다". No placeholders.
- **③**: governing = 통지 마감 (the earlier step). 2단계 절차 as numbered structure:
  ① 반대의사 통지 (window) ② 매수청구 행사 (window), with the dependency sentence
  "1단계에서 반대의사를 통지한 주주만 행사 가능". Past steps: chip "기한 지남", faint.
  매수예정가: NOT in the contract — do not render (posed back).

## State pages

- **철회** (`state: withdrawn`): `StateBadge withdrawn-r{n}` replaces the body (locked
  notice per type). Below it only: one sentence naming the 정정사항-table evidence + a
  `Citation` with the withdrawal quote. No fields, no countdown, no old dates.
- **발행사 기재 불일치**: two readings side by side, each with its own `Citation`; header
  sentence "발행사의 공시가 실권주에 대해 서로 다른 두 값을 제시합니다 — 미주알은 어느
  쪽도 고르지 않고 둘 다 보여드립니다"; footer "소멸가치 합산에는 발행 − 청약 값을
  사용합니다…". The badge text is the locked literal.

## CorrectionStory view (opened by "정정 이력")

- Version rail: chronological rows (date · correction_kind · rcept_no ↗); only
  `is_current_readable` gets the filled marker + live badge "현재 읽는 버전"; superseded
  rows may carry the locked reason string as a grey annotation. Verdicts never cross
  versions — a countdown must never fall back to a superseded version's values.
- Field moves: 정정 전 / → / 정정 후 columns from `field_moves` verbatim; `new: null`
  renders "(정정 후 본문에서 삭제됨)" — the deleted-passage story lives HERE; the detail
  card itself stays silent. Summary = `interpretation.summary` verbatim + bolded
  `schedule_impact`.

## Mobile (≤480px)

Single column: 52px top bar (crumb + ring wordmark) → header stack → countdown box →
DART link (44px full-width) → 환산 블록 → all field rows vertically stacked (label row
carries the [근거] chip right-aligned) — **no accordions**. Hit targets ≥44px.

## 추후결정 board strip (decision §6-4)

On the 관제 현황판, below the ② 진행 중 strip, same pattern: "일정 추후결정 — 카운트다운
없이 감시 중인 이벤트 N건" + 펼치기; expanded rows link to detail. Not ranked.

## Estimate mark

`EstimateMarker` is the ONLY estimate mark: value + bordered 「추정」 tag (sans, 0.56em of
context, letter-spacing .08em, border currentColor @42%). ▷ must not appear in any UI
surface. Facts never carry the tag.

## Hard rules (unchanged, restated)

An estimate without 「추정」 or a tag on a fact — never. A date next to 추후결정 — never.
A placeholder where a gate-blocked field would be — never. Paraphrased quotes — never.
Browser-computed or non-KST D-days — never. A past ② date labeled 종료 — never.
