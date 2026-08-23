/**
 * Every Korean string the event detail surface renders, and where each one comes
 * from.
 *
 * Same rule and same shape as `lib/copy.ts` (the primitives'),
 * `components/chrome/copy.ts` (the chrome's) and `components/landing/copy.ts`
 * (the landing's): **nothing here is invented.** Inventing a Korean string is a
 * design change, not an implementation detail, so every entry below is
 * transcribed — almost all of them from R3's own build prompt
 * (`docs/reference/design/rounds/03-event-detail/output/build-prompt.md`), whose
 * connective chrome copy the R3 gate explicitly signed off ("정정 반영 strip
 * framing, '정정 이력' button, absence line '현재 버전 공시에 없음', sparse-②
 * closing line, 기재 불일치 sentences").
 *
 * Everything that is *not* here comes off the wire: field labels are the served
 * `korean_name`, values are the filing's own words, and the 철회 notice is the
 * payload's own `notice_ko`. The frontend keeps **no field-name table of its
 * own** — a label this file does not hold is a label the server owns.
 */

export { BOARD_LABEL_KO } from "@/components/chrome/copy";

// ---------------------------------------------------------------------------
// Header panel (R3 §Page anatomy 1–2)
// ---------------------------------------------------------------------------

/** R3 §2: "corp name (text-2xl bold) + **DART 원문 ↗** (mono link …)". The `↗`
 * is rendered beside it, the same mark R2's board row uses.
 *
 * Re-exported rather than transcribed again: R10 gives the same two words to the
 * citation popover's foot and to every section's `.secsrc` line, so the string
 * moved into `lib/copy.ts` where the primitive that renders it lives. */
export { DART_LINK_KO, dartSourceLabelKo } from "@/lib/copy";

/** The header's mono meta line — R3 §2: "mono meta line (접수번호 · 최초 공시
 * `original_rcept_dt` · 정정 반영 when versions > 1)". */
export const RCEPT_NO_KO = "접수번호";
export const FIRST_FILED_KO = "최초 공시";
export const CORRECTED_KO = "정정 반영";

/** The identity line, R3 §2 verbatim — rendered **iff**
 * `corp_name_agrees_with_body === false`. The card always shows the DART master
 * `corp_name`; the 본문's own spelling is *stated*, never silently corrected
 * (`ui-traps.md` #3), so the tap through to the 원문 survives the difference. */
export const identityLineKo = (nameInBody: string) =>
  `공시 본문 표기: ${nameInBody} — 원문에는 이 이름으로 기재되어 있습니다`;

/** R3 §2, the two `countdown.date === null` cases — and they are different
 * statements about the filing:
 *
 * - **추후결정** — the governing field is served and says 추후결정, so the badge
 *   answers with `StateBadge tbd` and this line. Never a date beside it.
 * - **field-absent** (R3's ③ 아시아나 case) — the governing field is not in the
 *   payload at all, so the line states a fact about *the filing*, never about
 *   the gate (`states-and-trust.md` §4). */
export const NO_COUNTDOWN_KO = "카운트다운 없음 — 일정이 공시상 미정";
export const FIELD_ABSENT_KO = "현재 버전 공시에 없음";

/** ①'s open 매매기간, R3 §Type-specific rules: "Window open → live-green
 * '거래 가능 · 마감 D-n'". The D-day is the served `countdown.dday`. */
export const tradingOpenKo = (dday: string) => `거래 가능 · 마감 ${dday}`;

/** ②'s already-open 전환청구기간, R3 §Type-specific rules: "past opening =
 * '진행 중', never 종료" — the trap `ui-traps.md` #5 exists to prevent. */
export const CONVERSION_OPEN_KO = "진행 중";

// ---------------------------------------------------------------------------
// ① 환산 블록 (R3 §Page anatomy 3, session decision §6-1)
// ---------------------------------------------------------------------------

/** The per-unit chain's four links, R3 §3 verbatim: "per-unit chain
 * 예정/확정발행가 → 할인율 → (확정발행가 존재 시) `EstimateMarker` 증서 1주
 * 이론가치 → 배정비율 printed to its full 10 decimals". */
export const CONFIRMED_PRICE_KO = "확정발행가";
export const DISCOUNT_RATE_KO = "할인율";
export const UNIT_VALUE_KO = "증서 1주 이론가치";
export const ALLOTMENT_RATIO_KO = "배정비율";

/** R2 §Copy's own signed chip (the landing's board row carries it too), and R3
 * §3's state for an offering whose price is not fixed yet: "확정발행가 null →
 * chip `발행가 확정 전` + mono `확정 예정 {final_price_date}`". */
export const PRICE_PENDING_KO = "발행가 확정 전";
export const finalPriceDateKo = (date: string) => `확정 예정 ${date}`;

/** R3 §3's link-out, confirmed as-is by R4 ("R3's link-out '내 보유량으로 환산 →'
 * is confirmed as-is (no longer provisional)" — R4 signoff). The N주 input stays
 * in 조회: detail shows nothing R4's math could later contradict. */
export const CONVERT_CTA_KO = "내 보유량으로 환산 →";

// ---------------------------------------------------------------------------
// 청약 결과 inset (R3 §3) and 발행사 기재 불일치 (R3 §State pages)
// ---------------------------------------------------------------------------

/** R3 §3: "Post-결과 events append the **청약 결과** inset (발행·청약·소멸 shares
 * + `EstimateMarker` 소멸가치 + 하한)". The four labels are that sentence's. */
export const LAPSE_RESULT_KO = "청약 결과";
export const WARRANTS_ISSUED_KO = "발행";
export const WARRANTS_EXERCISED_KO = "청약";
export const WARRANTS_LAPSED_KO = "소멸";
export const LAPSE_VALUE_KO = "소멸가치";
/** R2's own band wording for the lower edge ("밴드 하한"), and R3 §3's "하한". */
export const LAPSE_FLOOR_KO = "하한";

/** The 발행사 기재 불일치 sentences, R3 §State pages verbatim. The badge itself is
 * `StateBadge kind="mismatch"`, whose literal lives in `lib/copy.ts`.
 *
 * The footer is transcribed **as far as the record states it** — the build
 * prompt writes it `"소멸가치 합산에는 발행 − 청약 값을 사용합니다…"`, and the
 * ellipsis is the record's own truncation of a sentence that continues on a card
 * this repo does not hold. Completing it would be inventing copy, so the
 * transcription stops where the record does (`P5.S19` checks it against the
 * card). */
export const MISMATCH_HEADER_KO =
  "발행사의 공시가 실권주에 대해 서로 다른 두 값을 제시합니다 — 미주알은 어느 쪽도 고르지 않고 둘 다 보여드립니다";
export const MISMATCH_FOOTER_KO = "소멸가치 합산에는 발행 − 청약 값을 사용합니다";
/** The derived reading's own name, from that same footer sentence. The stated
 * reading carries the server's own `label` (신주인수권증서 청약 실권주). */
export const MISMATCH_DERIVED_KO = "발행 − 청약";

// ---------------------------------------------------------------------------
// ② fact strip (R3 §Type-specific rules)
// ---------------------------------------------------------------------------

/** The six values R3 names, in its own order: "(전환가액, 오버행 %, 전환 시
 * 주식수, 권면총액, 발행방법·만기) in a fact strip ABOVE 본문 fields". Every one
 * is a **fact** — an API row has no character offsets, so its citation is the
 * filing number (`P5.S3` note 7), which is why the strip carries a 접수번호 link
 * and no `[근거]` chip. */
export const CONVERSION_PRICE_KO = "전환가액";
export const OVERHANG_KO = "오버행";
export const CONVERTED_SHARES_KO = "전환 시 주식수";
export const FACE_AMOUNT_KO = "권면총액";
export const ISSUE_METHOD_KO = "발행방법";
export const MATURITY_KO = "만기";

/** The ② fact strip's own source row (R10 §3 / result.md §2-8): the strip is
 * **API tier** — an API row has no character offsets, so it can carry no
 * `[근거]` — and the row states that tier once, under the frame, beside the
 * filing number. Not new copy: the words are the sparse-② closing line's own
 * ("위 값은 **DART 공시 API** 기준입니다"), which is why R10's copy list carries
 * four strings and not five. */
export const FACT_SOURCE_KO = "DART 공시 API";

/** The sparse-② closing line, R3 §Type-specific rules verbatim: an ② with zero
 * 본문 fields closes with one factual line and **no placeholders**. */
export const SPARSE_CLOSING_KO =
  "공시 본문에서 확인된 추가 조건이 없습니다 — 위 값은 DART 공시 API 기준입니다";

/** `option_schedule`'s caption, R3 verbatim: the stored `start_date ~ end_date`
 * appear ONLY here — "Never a plain 기간, never a bar" (`ui-traps.md` #1: those
 * two dates bracket a *recurring* claim right, and the value that states the
 * convention is the filer's own `detail` string). */
export const optionWindowCaptionKo = {
  before: "청구 가능 구간 ",
  range: (start: string, end: string) => `${start} ~ ${end}`,
  after: " — 연속 기간 아님 · 행사 가능일은 위 조건이 정함",
} as const;

/** 콜·풋 — the two option kinds, spelled as the served field's own `korean_name`
 * spells them (`콜·풋 세부 스케줄`) and as R3's record names the blocks
 * ("option_schedule as 풋/콜 blocks"). The payload's `kind` is the English token
 * `put` / `call`, which is internal and never reaches a reader surface. */
export const OPTION_KIND_KO: Record<string, string> = { put: "풋", call: "콜" };

// ---------------------------------------------------------------------------
// ③ 2단계 절차 (R3 §Type-specific rules)
// ---------------------------------------------------------------------------

/** R3: "2단계 절차 as numbered structure: ① 반대의사 통지 (window) ② 매수청구
 * 행사 (window), with the dependency sentence '1단계에서 반대의사를 통지한 주주만
 * 행사 가능'. Past steps: chip '기한 지남', faint."
 *
 * The step ordinals render as **1단계 / 2단계**, the words the dependency
 * sentence itself uses, rather than the record's ①② glyphs — those glyphs are
 * this product's shorthand for the three *rights types* and R1's revision
 * removed them from the UI, so re-introducing them here would print the ① of
 * 유상증자 beside a 매수청구 event. */
/** The ③ 절차 block's section heading (R10 §5 · `detail/Procedure.html`:
 * `<h2 className="eyebrow">2단계 절차</h2>`). R3 names the structure with these
 * words too ("2단계 절차 as numbered structure", and `experience.md` repeats
 * them), so this is a transcription of the record's own name for the block, not
 * a new sentence: R10 gives the block an `h2` of its own because the two steps
 * are `h3`s under it and a page outline cannot start at h3. */
export const SECTION_PROCEDURE_KO = "2단계 절차";

export const STEP_ONE_KO = "1단계";
export const STEP_TWO_KO = "2단계";
export const DISSENT_NOTICE_KO = "반대의사 통지";
export const APPRAISAL_EXERCISE_KO = "매수청구 행사";
export const STEP_DEPENDENCY_KO = "1단계에서 반대의사를 통지한 주주만 행사 가능";
export const PAST_STEP_KO = "기한 지남";

/** ③'s two sub-rows, R3's record: "통지 방법/접수처 rows" (the served field's own
 * `method` and `recipient` values). */
/** The window row's label on a ③ page whose `dissent_notice_procedure` is **not
 * in the current version** of the filing (R10 §10 box 6 · `detail/Procedure.html`
 * draws the 아시아나 case as `<Row label="반대의사 통지 접수기간">` + the dashed
 * absence chip). Nothing is minted here: the string is the signed round's own,
 * and it is used only to say that the field is missing — never as a heading over
 * a value. */
export const NOTICE_WINDOW_KO = "반대의사 통지 접수기간";

export const NOTICE_METHOD_KO = "통지 방법";
export const NOTICE_RECIPIENT_KO = "접수처";

// ---------------------------------------------------------------------------
// Field sections (R3 §Page anatomy 4)
// ---------------------------------------------------------------------------

/** The section eyebrows, `// {name}`. R3's landed record names the ① card's two
 * sections — "field sections **일정/발행 조건** with per-field [근거]" — and names
 * none for ②/③; the anatomy itself is stated for all three types. So these two
 * are the whole vocabulary: a field that states *when* goes under 일정, a field
 * that states the filing's terms goes under 발행 조건. Inventing a third name
 * would be a design change (`P5.S19` checks the ②/③ cards). */
export const SECTION_SCHEDULE_KO = "일정";
export const SECTION_TERMS_KO = "발행 조건";

/** `issue_price_formula`'s three sub-rows. The names are the served
 * `korean_name`'s own parenthetical — `발행가액 산정방법 (1·2차·확정 산식)` — so
 * the row labels come off the wire like every other one. */
export const FORMULA_FIRST_KO = "1차";
export const FORMULA_SECOND_KO = "2차";
export const FORMULA_FINAL_KO = "확정";

// ---------------------------------------------------------------------------
// 정정 strip + CorrectionStory (R3 §Page anatomy 5, §CorrectionStory view)
// ---------------------------------------------------------------------------

/** R3 §5: "정정공시 반영 — 최근: {interpretation.summary key figures} ·
 * {schedule_impact}" — the connective framing signed at the R3 gate, over the
 * server's own verbatim `summary` / `schedule_impact`.
 *
 * Split at the em dash because the clause after it introduces a summary: a
 * corrected filing whose interpretation carries none still states that it was
 * corrected, and "최근:" opening onto nothing would be a sentence the page
 * cannot finish. */
export const correctionStripKo = {
  title: "정정공시 반영",
  recent: "— 최근: ",
  join: " · ",
} as const;

/** The button that opens the CorrectionStory (R3 §5).
 *
 * ⚠ **This label is an open question, carried since R3 and still unresolved**
 * (`SIGNOFF.md` R3/R4/R5 "Carried open items: '정정 이력' button label";
 * `docs/current/experience.md` v0002, `product.md` v0003, and P5's own Open
 * Questions). R3's literal is what renders until the operator settles it. */
export const CORRECTION_HISTORY_KO = "정정 이력";

/** The **open** label of that button (R10 §7): 「정정 이력」 ↔ **「접기」** + `×`.
 * R9 signed 접기 for the board's own strips and R10 re-uses that word here, so
 * `Corrections.tsx`'s R3-era note — "a 접기 label is copy nobody signed" — is
 * superseded: the label now reads the state and `aria-expanded` agrees with it
 * instead of standing in for it. Re-exported from the round that signed it. */
export { COLLAPSE_KO } from "@/components/landing/copy";

/** The version rail's live badge, R3 §CorrectionStory verbatim: "only
 * `is_current_readable` gets the filled marker + live badge '현재 읽는 버전'". */
export const CURRENT_VERSION_KO = "현재 읽는 버전";

/** The field-move columns, R3 §CorrectionStory verbatim: "정정 전 / → / 정정 후
 * columns from `field_moves` verbatim; `new: null` renders '(정정 후 본문에서
 * 삭제됨)' — the deleted-passage story lives HERE". */
export const MOVE_BEFORE_KO = "정정 전";
export const MOVE_AFTER_KO = "정정 후";
export const MOVE_DELETED_KO = "(정정 후 본문에서 삭제됨)";

// ---------------------------------------------------------------------------
// 철회 evidence + provenance (R3 §State pages, §Page anatomy 6)
// ---------------------------------------------------------------------------

/** The 정정사항 table the withdrawal was read from — the filing's own section
 * name (`copy-inventory.md` §Product terminology: "정정공시 … `3. 정정사항` 표가
 * 무엇이 바뀌었는지의 근거다"), and the label R3's 철회 page uses to name the
 * evidence. The row's own words (항목 · 정정 전 → 정정 후) are served. */
export const CORRECTION_TABLE_KO = "정정사항";

/** R3 §6, the provenance line, mono 10px and verbatim. */
export const PROVENANCE_KO =
  "모든 값은 DART 공시에서만 나왔습니다 · 각 항목의 [근거]가 원문 구절과 접수번호로 연결됩니다";

/** The unit every share count in this product carries. */
export const SHARES_UNIT_KO = "주";

// ---------------------------------------------------------------------------
// 404 (R10 §8) — the one screen in this product that used to be English
// ---------------------------------------------------------------------------

/** R10's three new Korean strings, its dated copy exception (2026-08-23,
 * `result.md` §4 · SIGNOFF R10), rendered by `app/not-found.tsx`.
 *
 * They live in this surface's module because R10 — the event-detail round —
 * designed the page, and it is `/events/{rcept_no}`'s `notFound()` that a reader
 * reaches it through. **The page says no reason**: flagged, incomplete, a
 * 실적보고서 rcept and a typo all get this screen, and the gate's reason exists
 * only on the operator's surface (`states-and-trust.md` §4, D-14). The requested
 * path is echoed in mono with **no label** — an address is a fact; why it has no
 * page is not one this product tells. */
export const NOT_FOUND_TITLE_KO = "이 주소에 해당하는 공시가 없습니다";
export const NOT_FOUND_LINE_KO = "관제 현황판에서 감시 중인 공시를 확인하실 수 있습니다.";
export const NOT_FOUND_BACK_KO = "관제 현황판으로 →";
