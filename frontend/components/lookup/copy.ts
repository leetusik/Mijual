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
  APPRAISAL_EXERCISE_KO,
  CONFIRMED_PRICE_KO,
  CONVERSION_OPEN_KO,
  CONVERSION_PRICE_KO,
  CONVERTED_SHARES_KO,
  DISSENT_NOTICE_KO,
  FACT_SOURCE_KO,
  FIELD_ABSENT_KO,
  LAPSE_FLOOR_KO,
  MISMATCH_DERIVED_KO,
  MISMATCH_FOOTER_KO,
  MISMATCH_HEADER_KO,
  OVERHANG_KO,
  PAST_STEP_KO,
  PRICE_PENDING_KO,
  SHARES_UNIT_KO,
  STEP_DEPENDENCY_KO,
  STEP_ONE_KO,
  STEP_TWO_KO,
  UNIT_VALUE_KO,
  WARRANTS_EXERCISED_KO,
  WARRANTS_ISSUED_KO,
  WARRANTS_LAPSED_KO,
} from "@/components/event/copy";

/** The event-surface constants R11 **composes with** rather than only passing
 * through — a re-export does not put a name in this module's own scope, and the
 * derived strings below (the open-window phrase, the 추후결정 tail, the ② source
 * row) are built from these exact definitions so there is one of each. */
import {
  CONVERSION_PRICE_KO,
  CONVERTED_SHARES_KO,
  FACT_SOURCE_KO,
  NO_COUNTDOWN_KO,
  OVERHANG_KO,
  tradingOpenKo,
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
  `‘${query}’${josa(query)} 일치하는 종목이 없습니다 — 종목명 또는 종목코드로 다시 검색해 주세요.`;

/**
 * The particle in front of that sentence, **R11 §7 / walk finding 10**.
 *
 * > 조사: ‘{q}’ 뒤는 한글이면 `(code−0xAC00) % 28 !== 0 ? '과' : '와'`,
 * > **한글이 아니면 `와/과` 병기**.
 *
 * Korean picks 와/과 by the **final consonant** of the preceding syllable, and
 * a Hangul syllable block carries it in its own code point: the 28 jongseong of
 * `U+AC00`–`U+D7A3` cycle every 28 code points, so `(code − 0xAC00) % 28` is 0
 * exactly when the syllable ends in a vowel. That is arithmetic on the query, not
 * a new sentence — R11 `result.md` §4 calls it "서명된 문장의 기계적 굴절"
 * and the sentence body stays locked.
 *
 * A **non-Hangul** query (`012320`, `KOSPI`) prints both forms rather than
 * guessing a Latin word's or a numeral's reading aloud — build-prompt §7's own
 * rule, and the reason the round refuses to inflect what it cannot pronounce.
 */
function josa(query: string): string {
  const last = query.charCodeAt(query.length - 1);
  const hangul = last >= 0xac00 && last <= 0xd7a3;
  if (!hangul) return "와/과";
  return (last - 0xac00) % 28 !== 0 ? "과" : "와";
}

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
 * record's own `−` (U+2212), the same one R3's 발행 − 청약 reading uses.
 *
 * **R11 §5 unfolds this into the two readings it composes** — 「발행 {n}주 −
 * 청약 {n}주」 over 「= 소멸 {k}주 ({rate})」 — so the breakdown shows the counts
 * the 실적보고서 actually attests instead of only their difference. The words and
 * the operators are this constant's; only the arrangement moved, and the sentence
 * is kept here as the one definition of both. */
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

// ---------------------------------------------------------------------------
// R11 (`rounds/11-lookup`, signed 2026-08-24) — 내 종목 조회 polish
//
// R11 is a polish round: it adds **one** sentence (the prompt, its own dated
// copy exception) and one caption the gate signed as landed (P8 Q28 = a). What
// follows besides those two are the round's **cell and column labels**, written
// into `build-prompt.md` §2/§4/§5 — the contract the SIGNOFF names as governing
// — and drawn in the six cards. They are registered here rather than typed at a
// call site, and listed in `copy-inventory.md`'s R11 tail beside their citation.
// Everything else this surface says is still R4's, verbatim, above.
// ---------------------------------------------------------------------------

/**
 * The round's **one new string** (R11 `result.md` §4, dated exception
 * 2026-08-24, Q-E; `build-prompt.md` §6).
 *
 * > `보유 주식 수를 입력하면 내 보유량 기준으로 환산합니다`
 *
 * It is a **control, not a caption**: a 44px dashed button that focuses the
 * 보유량 input, rendered **once per page** — in the ① 환산 block's `.chainfoot`
 * when there is a live ① on the page, otherwise in 놓친 돈's head — and gone the
 * moment a holding exists. Its vocabulary is entirely borrowed from strings this
 * surface already signed: 「보유 주식 수」 (R4 §3's label), 「…와 금액을
 * 환산합니다」 (R4's 발행가 확정 전 line) and 「보유량 환산」 (the provenance
 * sentence). The round's own reason: 놓친 돈 opened with no number and nothing on
 * screen said why it was empty or what would fill it.
 */
export const MISSED_PROMPT_KO = "보유 주식 수를 입력하면 내 보유량 기준으로 환산합니다";

/** The boundary panel's own heading (R11 §1/§8, walk finding 12). The noun is
 * already inside `coverageCaptionKo`'s signed caption 「집계 범위 2026-01-01 ~
 * 오늘 (KST)」 — R11 `result.md` §4 states it is that noun promoted to a title,
 * not a new string. */
export const COVERAGE_SECTION_KO = "집계 범위";

/** The identity panel's mono meta (R11 §2). 종목코드 comes **first when the API
 * serves one** (계양전기 `012200`), 고유번호 follows; the separator is the CSS
 * `::before` of the span that follows, never a character in either string. */
export const STOCK_CODE_KO = "종목코드";
export const CORP_CODE_KO = "고유번호";

/** 「{공시일} 공시」 in a rights panel's meta line, and the ② table's first
 * column header (R11 §4). The word is the head of R3's own 「최초 공시」
 * (`event/copy.ts#FIRST_FILED_KO`) — the lookup panel prints the served
 * `original_rcept_dt`, so the qualifier 최초 belongs to the detail header that
 * distinguishes versions, and this surface names the act. */
export const FILED_SUFFIX_KO = "공시";

/** ①'s instrument cells (R11 §4, `lookup/Result.html`'s `Chain`).
 *
 * - 「보유」 restates the reader's own input beside the numbers it drives — the
 *   head of R4 §3's `HOLDING_LABEL_KO` 「보유 주식 수」, which the strip carries in
 *   full one panel above.
 * - 「배정비율 (1주당)」 is R3's `ALLOTMENT_RATIO_KO` with the round's own
 *   qualifier: the cell prints the ratio *per one held share*, which is what
 *   makes the 배정 신주 cell beside it readable.
 * - 「초과청약 비율」 is the filing's own field name for `excess_ratio`
 *   (`copy-inventory.md` §Field keys), and it renders **only** the served ratio —
 *   never the 한도 it becomes once a holding exists. */
export const HOLDING_CELL_KO = "보유";
export const ALLOTMENT_RATIO_CELL_KO = "배정비율 (1주당)";
export const EXCESS_RATIO_KO = "초과청약 비율";

/** ①'s open-window phrase, R11 §4's 「열림이면 `--live` 문구」 (`lookup/Rights.html`
 * renders 「거래 가능」).
 *
 * Derived from the detail header's own `tradingOpenKo` 「거래 가능 · 마감 D-n」
 * rather than re-typed, so the two surfaces cannot drift: on this surface the
 * D-day is already on the row, in the `DDay` directly above the window line, and
 * the card prints the phrase without it. One source, one wording. */
export const TRADING_OPEN_KO = tradingOpenKo("").split("·")[0].trim();

/** The line under a 추후결정 badge (R11 §4: 「일정이 공시상 미정」).
 *
 * The **tail** of R3's locked 「카운트다운 없음 — 일정이 공시상 미정」: the head
 * half is the detail page's own framing of an empty countdown slot, and this
 * surface's slot already shows the badge. Derived from the one constant, so the
 * locked literal has exactly one definition (`phase.md` §"R11 landed spec"). */
export const NO_SCHEDULE_KO = NO_COUNTDOWN_KO.split(" — ")[1] ?? NO_COUNTDOWN_KO;

/**
 * 놓친 돈's caption (R11 §5, **signed as landed** — P8 Q28 = (a)).
 *
 * > 유상증자 {n}건 · 집계 범위 {start} ~ 오늘 (KST) · 시장 가격 미사용 — 소멸된
 * > 증서의 이론가치 환산
 *
 * Composed, not re-typed: the count uses R4's own column noun 유상증자, the
 * middle is `coverageCaptionKo` unchanged, and only the tail below is new — the
 * caption's own answer to 「이 금액은 시세인가?」, which the provenance line makes
 * once for the page and this section now makes where the money is.
 */
export const MISSED_CAPTION_TAIL_KO = "시장 가격 미사용 — 소멸된 증서의 이론가치 환산";
export const missedCaptionKo = (offerings: string, start: string) =>
  `${COL_OFFERING_KO} ${offerings}건 · ${coverageCaptionKo(start)} · ${MISSED_CAPTION_TAIL_KO}`;

/** The breakdown's 소멸 계산 column, qualified by R11 §5's own head row: the
 * calculation in it is the **market's**, not the reader's, and the last column is
 * the one that depends on a holding. `COL_LAPSE_KO` alone still names the fact. */
export const COL_LAPSE_MARKET_KO = `${COL_LAPSE_KO} (시장 전체)`;

/** The ② table's source row (R11 §4), composed from the three facts R4-4 named
 * and the API tier they come from — the same 「DART 공시 API」 the detail page's ②
 * strip closes with, and the same one-line-per-section rule R10 §3 set. */
export const CONVERTIBLE_SOURCE_KO = `${FACT_SOURCE_KO} — ${CONVERSION_PRICE_KO} · ${CONVERTED_SHARES_KO} · ${OVERHANG_KO}`;

/** 「⋯」 — R11 §4's mark for a value the filing's API row does not carry. It is a
 * **typographic absence**, not a word: never a 0, never a dash sentence and never
 * a reason (D-14). */
export const MISSING_VALUE = "⋯";

/**
 * Two signed one-slot sentences, split around their **own** value.
 *
 * R11 renders the date inside 「청약 {date} 종료」 and 「… 청약 종료({date}) …」 in
 * mono (`lookup/Rights.html`'s `.closed .v`, `r11-parts.jsx`'s `Zero`), which a
 * call site can only do if it holds the sentence in halves. Splitting the signed
 * builder around a placeholder keeps **one** definition of each sentence — a
 * second transcription is exactly how a locked literal drifts.
 */
const splitAround = (build: (value: string) => string) => {
  const mark = "\u0000";
  const [before, after = ""] = build(mark).split(mark);
  return { before, after } as const;
};

export const subscriptionClosedParts = splitAround(subscriptionClosedKo);
export const pendingLapseParts = splitAround(pendingLapseKo);
