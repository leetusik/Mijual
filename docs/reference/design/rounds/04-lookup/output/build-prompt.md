# R4 Implementation Contract — 종목 조회 (`P3.S5`)

For the Next.js build. The surface owns ALL N주 math display (R3: detail shows per-unit
only). Reference cards: `lookup/*.html`; tokens unchanged.

## Token delta

None. `foundations/tokens.css` as landed in R2 (`.cosmos` scope on the page root).

## Route + naming

- Surface name **내 종목 조회** (session decision R4-5). Nav label 내 종목 연결 → 내 종목
  조회; R3 detail link-out stays "내 보유량으로 환산 →" and routes here with the stock
  preselected. The landing hero submits here. Anonymous, no login.

## Page anatomy (one page, two sections — decision R4-1)

1. **Header**: title 내 종목 조회 + subline (hero copy) + crumb "← 관제 현황판".
2. **Search row**: input (hero placeholder "종목명 또는 종목코드 — 예: 계양전기") + 조회
   button (`--live-solid`). Name/ticker resolution server-side. No match →
   "‘{query}’와 일치하는 종목이 없습니다 — 종목명 또는 종목코드로 다시 검색해 주세요."
3. **보유량 strip** (craft panel): label 보유 주식 수 · mono right-aligned integer input
   (`inputMode="numeric"`, comma-grouped) · suffix 주 · preset chips 100/500/1,000주 ·
   caption "브라우저 세션에만 저장 · 서버 전송 없음". **Session memory (decision R4-6):**
   sessionStorage only; on a new stock with a remembered value, offer a restore chip
   "이전 입력 {n}주" — never auto-fill silently, never persist server-side.
4. **진행 중인 권리 — N건** (`// ` mono eyebrow): one panel per live event, most urgent
   first. Each: RightsChip + 종목/건 title + "상세 보기 →" (event detail) + rcept_no meta;
   right: governing label + upstream DDay + window line (live green when open).
5. **2026년 놓친 돈** (`// ` eyebrow): total + breakdown (below). Zero state: "이 종목은
   2026년 집계 범위에서 놓친 권리가 없습니다" (+ if a live ① is pending: "진행 중인 건의
   소멸 여부는 청약 종료({subscription_end}) 후 집계됩니다").
6. **Provenance line** (mono 10px): "모든 값은 DART 공시에서만 나왔습니다 · 보유량 환산은
   공시된 배정비율과의 곱셈이며, 시장 가격을 사용하지 않습니다".

## The N주 conversion (① rows)

Client composes upstream numbers ONLY — every factor comes from the persisted contract
(`offering_inputs` / `lapse_result`); nothing else is computed:

- 배정 신주 = `allotted_shares(n, 배정비율)` — display assumes ⌊n × ratio⌋; **the
  mijual.calc rule governs**, mirror it exactly. Show the factor to its full 10 decimals
  in the caption ("= {n}주 × 0.2465120994 · 1주 미만 버림").
- 초과청약 한도 = ⌊배정 신주 × excess ratio⌋, shown as "+{k}주" where the field passed.
- **확정발행가 exists** → 환산액 = 배정 신주 × `unit_value` → `EstimateMarker`; 하한 =
  배정 신주 × `unit_value_floor`. Facts (주수, 확정발행가) never tagged; won amounts always.
- **확정발행가 null** → chip `발행가 확정 전` + "확정 예정 {final_price_date} — 확정 후
  증서 이론가치와 금액을 환산합니다". **No money number at all.** Share counts still shown.
- Recompute instantly on input (no debounce needed — pure multiplication).

## ②/③ rows (decision R4-4)

Deadline rows with context, visually separated from ① money rows; **never a won amount**:

- **②**: RightsChip + 전환청구 개시 DDay (past opening = "진행 중", never 종료) + dilution
  context from API-tier facts (오버행 %, 전환 시 주식수, 전환가액). No per-holding math —
  there is nothing a holder exercises.
- **③**: RightsChip + 반대의사 통지 마감 DDay + the 2단계 dependency line. 매수예정가 is
  not in the contract — not rendered.
- Both link out to detail for everything else.

## 놓친 돈 breakdown

- **Total headline**: conditional frame line "청약도 매도도 하지 않았다면, 2026년 이
  종목에서 사라진 가치" → `EstimateMarker` total (alert) + 하한 (ink-2) + coverage caption.
  Total = Σ per-offering values for this stock within coverage.
- **Per-offering row** (grid 유상증자 / 증서 매매기간 / 소멸 계산 / N주 기준): offering
  title + rcept_no + 확정발행가; 매매기간 + faint chip "기간 지남 · D+{n}" (history styling
  per R2/R3 — never alert-colored); 소멸 계산 "발행 − 청약 = 소멸 {k}주 ({rate}%)" +
  market-wide `EstimateMarker`; right column per-holding `EstimateMarker` + caption
  "배정 {k}주 × 「추정」{unit}원". One `Citation` per row (warrant-period quote verbatim).
- Calc footer: "배정 {k}주 = {n}주 × 배정비율 {ratio} (1주 미만 버림) · 증서 1주 이론가치
  = 확정발행가 × 할인율 ÷ (1 − 할인율)".
- Disclaimer footnote (proposed copy): "실제 손익은 개별 청약·매도 행동에 따라 다릅니다 —
  이 값은 소멸된 증서의 이론가치를 보유량 기준으로 환산한 것입니다".
- **기간 input: none (decision R4-3).** Fixed factual coverage line "집계 범위 2026-01-01 ~
  오늘 (KST)"; the boundary panel states ① 2026-01-01부터 · ② 2025-06부터. Outside
  coverage is *unstated*, never counted as 0.

## Empty states

Per `lookup/LookupEmpty.html`: 검색 불일치 / no-event stock ("이 종목에는 진행 중이거나
2026년에 소멸된 권리가 없습니다" + 감시 대상 3종 + 감시 중 count) / coverage boundary.
No placeholders, no invented dates or amounts anywhere.

## Mobile (≤480px)

Single column per `lookup/LookupMobile.html`: 52px top bar → search → 보유량 panel (44px
input + full-width chips) → sections stacked; breakdown as label/value lines; "상세 보기 →"
as a 44px full-width link. No accordions.

## Hard rules (restated)

An estimate without 「추정」 or a tag on a fact — never. Money before 확정발행가 — never.
A date or amount outside coverage — never (state the range instead). ②/③ rows with won
amounts — never. D-day computed in the browser or non-KST — never (compose upstream
labels). A past ② opening labeled 종료 — never. Holding value sent to a server — never.
