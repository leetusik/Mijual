/**
 * Every Korean string 내 종목 조회 renders, and where each one comes from.
 *
 * Same rule and same shape as `lib/copy.ts` (the primitives'),
 * `components/chrome/copy.ts`, `components/landing/copy.ts` and
 * `components/event/copy.ts`: **nothing here is invented.** Inventing a Korean
 * string is a design change, not an implementation detail, so every entry below
 * is transcribed from the landed R4 record —
 * `docs/reference/design/rounds/04-lookup/output/build-prompt.md` and its
 * `result.md` §Proposed chrome copy, whose whole list the R4 gate signed off
 * ("the round's proposed chrome copy including the disclaimer footnote").
 *
 * Where a sentence already belongs to another signed surface it is **re-exported
 * rather than re-typed** — R4 §1 says the header's subline *is* the hero copy and
 * §2 says the input carries the *hero placeholder*, so those two are one sentence
 * on two surfaces, and a second transcription could drift from the first.
 */

/** The crumb's destination and this surface's own name (R2 §Page shell with R4's
 * supersession — the nav renders the same two labels). */
export { BOARD_LABEL_KO, STOCKS_LABEL_KO } from "@/components/chrome/copy";

/** R4 §1 "subline (hero copy)" · §2 "input (hero placeholder …) + 조회 button". */
export {
  HERO_SUB_KO,
  SEARCH_PLACEHOLDER_KO,
  SEARCH_SUBMIT_KO,
  /** The empty state's 감시 중 context number (R2's own stat-line label). */
  HERO_STAT_WATCHING_KO,
} from "@/components/landing/copy";

/**
 * Labels this surface shares with the event detail page, transcribed there.
 *
 * R4 composes R1–R3 as locked, so these are the *same* labels R3 signed —
 * ①'s 확정발행가/할인율/배정비율 chain, ②'s three dilution facts, ③'s 2단계
 * dependency line, the 하한/발행/청약/소멸 vocabulary of a 소멸 계산, and the
 * 발행사 기재 불일치 sentences — `ui-traps.md` #2 is a **payload** rule
 * (`P5.S4` note 9), so a breakdown row states the contradiction in exactly the
 * words R3 signed for the detail page rather than in new ones.
 */
export {
  ALLOTMENT_RATIO_KO,
  CONFIRMED_PRICE_KO,
  CONVERSION_OPEN_KO,
  CONVERSION_PRICE_KO,
  CONVERTED_SHARES_KO,
  DISSENT_NOTICE_KO,
  LAPSE_FLOOR_KO,
  MISMATCH_DERIVED_KO,
  MISMATCH_FOOTER_KO,
  MISMATCH_HEADER_KO,
  OVERHANG_KO,
  PAST_STEP_KO,
  PRICE_PENDING_KO,
  SHARES_UNIT_KO,
  STEP_DEPENDENCY_KO,
  UNIT_VALUE_KO,
  WARRANTS_EXERCISED_KO,
  WARRANTS_ISSUED_KO,
  WARRANTS_LAPSED_KO,
} from "@/components/event/copy";

// ---------------------------------------------------------------------------
// Search row (R4 §2)
// ---------------------------------------------------------------------------

/**
 * The 검색 불일치 line, R4 §2 verbatim:
 *
 * > No match → "‘{query}’와 일치하는 종목이 없습니다 — 종목명 또는 종목코드로
 * > 다시 검색해 주세요."
 *
 * It is rendered on **`found: false`**, which is a `200` result and not an error
 * (`P5.S4` note 1: "A search miss is a result; a bad link is an error"). It names
 * no reason, no candidate and no near-miss, because the contract serves none.
 * The typographic quotes are the record's own.
 */
export const noMatchKo = (query: string) =>
  `‘${query}’와 일치하는 종목이 없습니다 — 종목명 또는 종목코드로 다시 검색해 주세요.`;

// ---------------------------------------------------------------------------
// 보유량 strip (R4 §3, decision R4-2 / R4-6)
// ---------------------------------------------------------------------------

/** R4 §3: "label 보유 주식 수 · mono right-aligned integer input · suffix 주". */
export const HOLDING_LABEL_KO = "보유 주식 수";

/** R4 §3 / decision R4-2: "preset chips 100/500/1,000주". No slider — holdings
 * are exact integers. */
export const PRESET_SHARES = [100, 500, 1000] as const;

/** R4 §3's caption, **trimmed by P7 (item 10) to its promise half**. The round's
 * literal is "브라우저 세션에만 저장 · 서버 전송 없음"; the mechanism clause is a
 * storage word the reader gains nothing from, so it goes and the promise stays
 * verbatim — a **P7 operator override** of a signed literal, listed for the
 * review. What is left is still true by construction, and it is the half the
 * anonymous boundary leans on: `lib/holding.ts` writes to sessionStorage and the
 * API accepts no holding count on any path (`P5.S4`: factors, never products;
 * `routers/stocks.py` has no `n` parameter for exactly this reason). */
export const HOLDING_CAPTION_KO = "서버 전송 없음";

/** R4 §3 / decision R4-6: "on a new stock with a remembered value, offer a
 * restore chip '이전 입력 {n}주' — never auto-fill silently, never persist
 * server-side". The chip is an offer; the reader presses it. */
export const restoreChipKo = (shares: string) => `이전 입력 ${shares}주`;

// ---------------------------------------------------------------------------
// 진행 중인 권리 (R4 §4)
// ---------------------------------------------------------------------------

/** R4 §4's section title; the count is per-stock and live, not a board count
 * (R4 `result.md`: "진행 중 카운트: … per-stock facts from the pinned samples,
 * not board counts"). */
export const RIGHTS_SECTION_KO = "진행 중인 권리";

/** R4 §4: each panel carries "상세 보기 →" to the event detail page. */
export const DETAIL_LINK_KO = "상세 보기 →";

/** The panel's mono meta line names the filing, the same way R3's header does. */
export const RCEPT_NO_KO = "접수번호";

/**
 * The factual line an offering whose 청약 has closed leaves behind on this
 * section (`lookup/LookupMobile.html`, R4 `result.md`: "진행 중 0건 (factual
 * line: 청약 2026-07-23 종료)" — the 한화솔루션 composition).
 */
export const subscriptionClosedKo = (date: string) => `청약 ${date} 종료`;

// ---------------------------------------------------------------------------
// The N주 conversion (R4 §The N주 conversion)
// ---------------------------------------------------------------------------

/** "배정 신주 = `allotted_shares(n, 배정비율)`" and "초과청약 한도 = ⌊배정 신주 ×
 * excess ratio⌋, shown as '+{k}주' where the field passed". */
export const ALLOTTED_SHARES_KO = "배정 신주";
export const EXCESS_LIMIT_KO = "초과청약 한도";
export const excessLimitKo = (shares: string) => `+${shares}주`;

/** "확정발행가 exists → **환산액** = 배정 신주 × `unit_value`". */
export const CONVERTED_VALUE_KO = "환산액";

/** R4's own caption under 배정 신주: "= {n}주 × 0.2465120994 · 1주 미만 버림".
 * The ratio prints to its full ten decimals — it is what the multiplication
 * used, and a rounded one would not reproduce the number above it. */
export const allotmentCaptionKo = (shares: string, ratio: string) =>
  `= ${shares}주 × ${ratio} · 1주 미만 버림`;

/** R4: "확정발행가 null → chip `발행가 확정 전` + '확정 예정 {final_price_date} —
 * 확정 후 증서 이론가치와 금액을 환산합니다'. **No money number at all.**" */
export const pricePendingLineKo = (date: string) =>
  `확정 예정 ${date} — 확정 후 증서 이론가치와 금액을 환산합니다`;

// ---------------------------------------------------------------------------
// 2026년 놓친 돈 (R4 §5, §놓친 돈 breakdown)
// ---------------------------------------------------------------------------

/** R4 §5's section title. The year is the record's literal, and the served
 * coverage still starts 2026-01-01 (`reads.LAPSE_COVERAGE_START`). */
export const MISSED_SECTION_KO = "2026년 놓친 돈";

/** The conditional frame, R4 §놓친 돈 breakdown verbatim. It is a condition, not
 * a claim that the reader lost the money — which is why the disclaimer footnote
 * below sits under the same block (R4 `result.md` §Departures). */
export const MISSED_FRAME_KO = "청약도 매도도 하지 않았다면, 2026년 이 종목에서 사라진 가치";

/**
 * The coverage caption, R4 decision R4-3 verbatim: "집계 범위 2026-01-01 ~ 오늘
 * (KST)". There is **no 기간 picker** — "a picker with one valid value is a
 * trap" — and outside the range a figure is *unstated*, never counted as 0.
 *
 * The start comes off the wire (`lapse.coverage.start`, the corpus's own
 * collection window) so the sentence cannot outlive the boundary it describes;
 * `오늘` is the record's own word for the end, and it is exactly what the served
 * `coverage.end` is — today in KST.
 */
export const coverageCaptionKo = (start: string) => `집계 범위 ${start} ~ 오늘 (KST)`;

/** The breakdown grid's four columns, R4 §놓친 돈 breakdown: "grid 유상증자 /
 * 증서 매매기간 / 소멸 계산 / N주 기준". The last one names the reader's own
 * holding (the card's own "500주 기준"). */
export const COL_OFFERING_KO = "유상증자";
export const COL_TRADING_KO = "증서 매매기간";
export const COL_LAPSE_KO = "소멸 계산";
export const perHoldingColumnKo = (shares: string) => `${shares}주 기준`;

/** R4: "매매기간 + faint chip '기간 지남 · D+{n}' (history styling per R2/R3 —
 * **never alert-colored**)". The D+n is the served `countdown.dday`. */
export const pastPeriodChipKo = (dday: string) => `기간 지남 · ${dday}`;

/** R4: 소멸 계산 "발행 − 청약 = 소멸 {k}주 ({rate}%)". The minus sign is the
 * record's own `−` (U+2212), the same one R3's 발행 − 청약 reading uses. */
export const lapseCalcKo = (lapsed: string, rate: string) =>
  `발행 − 청약 = 소멸 ${lapsed}주 (${rate})`;

/** R4: the right column's caption "배정 {k}주 × 「추정」{unit}원". The 「추정」 is
 * the `EstimateMarker` tag itself (`P5.S10` note 4a: the border is the
 * enclosure), so the caption is composed around the primitive rather than
 * spelling the brackets. */
export const perHoldingCaption = {
  before: "배정 ",
  between: "주 × ",
  after: "원",
} as const;

/** The calc footer, R4 verbatim: "배정 {k}주 = {n}주 × 배정비율 {ratio} (1주 미만
 * 버림) · 증서 1주 이론가치 = 확정발행가 × 할인율 ÷ (1 − 할인율)". */
export const calcFooterKo = (allotted: string, shares: string, ratio: string) =>
  `배정 ${allotted}주 = ${shares}주 × 배정비율 ${ratio} (1주 미만 버림) · 증서 1주 이론가치 = 확정발행가 × 할인율 ÷ (1 − 할인율)`;

/** The disclaimer footnote — R4's signoff names it explicitly as signed copy. */
export const DISCLAIMER_KO =
  "실제 손익은 개별 청약·매도 행동에 따라 다릅니다 — 이 값은 소멸된 증서의 이론가치를 보유량 기준으로 환산한 것입니다";

/** R4 §5's zero state, and the pending line beside it: "Zero state: '이 종목은
 * 2026년 집계 범위에서 놓친 권리가 없습니다' (+ if a live ① is pending: '진행
 * 중인 건의 소멸 여부는 청약 종료({subscription_end}) 후 집계됩니다')". */
export const ZERO_MISSED_KO = "이 종목은 2026년 집계 범위에서 놓친 권리가 없습니다";
export const pendingLapseKo = (subscriptionEnd: string) =>
  `진행 중인 건의 소멸 여부는 청약 종료(${subscriptionEnd}) 후 집계됩니다`;

// ---------------------------------------------------------------------------
// Empty states (R4 §Empty states, `lookup/LookupEmpty.html`)
// ---------------------------------------------------------------------------

/** The no-event stock, R4 §Empty states verbatim. */
export const NO_RIGHTS_KO = "이 종목에는 진행 중이거나 2026년에 소멸된 권리가 없습니다";

/** The three things this product watches, named on that same card ("감시 대상
 * 3종 + 감시 중 count"). The 3종 themselves are `RightsChip`'s labels, so the
 * list is the primitive's and only this lead-in is copy. */
export const WATCH_TARGETS_KO = "감시 대상";

/**
 * The coverage boundary panel, R4 `result.md` §LookupEmpty: "집계 범위 경계
 * stated factually (① 2026-01-01부터 · ② 2025-06부터 · '2026년 이전의 유상증자
 * 기록은 집계에 없습니다') — no apology, no zero-counting outside coverage",
 * and its `result.md` copy list's own sentence.
 *
 * The record writes the two boundaries against ①/② — this product's internal
 * shorthand for the rights types, which **R1's revision removed from the UI**
 * ("no ①②③ numbering in UI"; `components/event/copy.ts` records the same reading
 * for ③'s 1단계/2단계). So they render as the rights types' own labels, and both
 * dates come off the wire (`lapse.coverage.start` / `.convertible_start`).
 */
export const COVERAGE_BOUNDARY_KO =
  "놓친 돈은 집계 범위 안에서만 계산됩니다 · 2026년 이전의 유상증자 기록은 집계에 없습니다";
export const coverageFromKo = (date: string) => `${date}부터`;

// ---------------------------------------------------------------------------
// Provenance (R4 §6)
// ---------------------------------------------------------------------------

/** R4 §6, mono 10px and verbatim. It is the sentence this whole surface has to
 * keep true: every factor is served, and the only arithmetic is the reader's own
 * holding times a disclosed ratio. */
export const PROVENANCE_KO =
  "모든 값은 DART 공시에서만 나왔습니다 · 보유량 환산은 공시된 배정비율과의 곱셈이며, 시장 가격을 사용하지 않습니다";
