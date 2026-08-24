/**
 * Every Korean string the landing 관제 현황판 renders, and where each one comes
 * from.
 *
 * Same rule and same shape as `lib/copy.ts` (the primitives') and
 * `components/chrome/copy.ts` (the chrome's): **nothing here is invented**.
 * Inventing a Korean string is a design change, not an implementation detail, so
 * every entry below is transcribed from the landed record — R2's build prompt and
 * its `result.md` copy list (signed at the R2 gate: "the round's new chrome copy
 * (발행가 확정 전 · … · stale notice · … · 소멸 카운트다운 · ② strip copy …)"),
 * R3's 추후결정 board-strip decision, R4's route/naming section, and the
 * pipeline's own 발표용 문장 block in `grounding/headline-numbers.md`, which
 * `mijual.estimate.__main__` generates.
 *
 * The two sentences that carry live numbers (the value card's fact line and the
 * 소멸주의보 body) are **templates over the pipeline's own wording**, not
 * paraphrases: the words are the report's, and only the figures move — which is
 * what "발표용 문장 N with live numbers" asks for.
 */

// ---------------------------------------------------------------------------
// Hero (R2 §Hero — "내 종목 연결, search-first")
// ---------------------------------------------------------------------------

/**
 * The hero's H1.
 *
 * R2's literal is **내 종목 연결**, and R2 says of this block "This IS the 내 종목
 * 연결 surface — no separate bridge panel; submit goes to R4's 조회". R4 then
 * **named that surface**: its signoff records "the surface name 내 종목 조회"
 * and its build prompt opens "Surface name **내 종목 조회** (session decision
 * R4-5) … The landing hero submits here". `docs/current/frontend.md`'s
 * supersession table carries the same row (R2 내 종목 연결 → R4 내 종목 조회).
 *
 * So the H1 renders the **superseded name**: it is a name for a destination
 * surface, not locked prose, and rendering R2's literal would print two names
 * for one surface on a page whose nav — one line above — already says 내 종목
 * 조회 (`P5.S11` renders the superseded nav label for exactly this reason).
 * The one place the retired wording survives is the footer's **locked
 * positioning sentence**, which `P5.S11` transcribed verbatim because locked
 * operator copy is not a label. Recorded for `P5.S19`/`P5.REVIEW`.
 */
export const HERO_TITLE_KO = "내 종목 조회";

/** R2 §Hero, verbatim: the 17px sub line under the H1. R4 §1 reuses it as its
 * own header subline ("subline (hero copy)"), so it is one sentence on two
 * surfaces. */
export const HERO_SUB_KO = "종목명 하나로 놓친 권리와 진행 중인 권리를 조회합니다";

/** R4 §2, which calls it the **hero placeholder** — the same console field on
 * both surfaces. R2 gives the input's colours and not its placeholder text. */
export const SEARCH_PLACEHOLDER_KO = "종목명 또는 종목코드 — 예: 계양전기";

/** R2 §Hero / §Cosmos: the solid `--live-solid` action beside the input. */
export const SEARCH_SUBMIT_KO = "조회";

/** The hero's mono stat line, R2 §Hero verbatim:
 * "2026년 소멸한 신주인수권 가치 718.1억원「추정」 · 감시 중 488건 · 30일 이내
 * 마감 34건". The three labels below are its three segments; the numbers are
 * live from `/board/summary`. */
export const HERO_STAT_VALUE_KO = "2026년 소멸한 신주인수권 가치";
export const HERO_STAT_WATCHING_KO = "감시 중";
export const HERO_STAT_WITHIN_30D_KO = "30일 이내 마감";

// ---------------------------------------------------------------------------
// Retrospective anchor (R2 §Retrospective anchor)
// ---------------------------------------------------------------------------

/** Value card eyebrow — mono 11 `--ink-3`, R2 verbatim. */
export const VALUE_EYEBROW_KO = "2026년에 소멸한 신주인수권 가치";

/** The band line under the headline figure, R2 verbatim:
 * "밴드 하한 548.7억원「추정」 (권리락 조정 가정)". */
export const BAND_FLOOR_KO = "밴드 하한";
export const BAND_ASSUMPTION_KO = "(권리락 조정 가정)";

/**
 * The value card's fact sentence — **발표용 문장 2**, whose wording is the
 * pipeline's own (`mijual.estimate.__main__`):
 *
 * > 주주에게 배정된 신주인수권증서 {issued:,}주 가운데 {rate:.1%}가 청약도
 * > 매도도 되지 않고 사라졌습니다.
 *
 * Both numbers are **facts** (발행 증서 and 소멸/발행), so neither carries the
 * estimate mark. R2 puts it at 15px, full card width, one line.
 */
export const factSentence = {
  before: "주주에게 배정된 신주인수권증서 ",
  between: " 가운데 ",
  after: "가 청약도 매도도 되지 않고 사라졌습니다.",
} as const;

/**
 * The countdown/stats card's live stats, R2 verbatim: "감시 중 이벤트 488건 ·
 * 30일 이내 마감 34건 · 소멸 앞둔 신주인수권 15건 · 읽은 실적보고서 69건".
 *
 * **R9 cut the card to three** (`rounds/09-landing-board/output/build-prompt.md`
 * §6, operator answer 9 at the R9 gate: "9. drop."): `STAT_REPORTS_KO`
 * (읽은 실적보고서) is deleted and `summary.performance_reports` is no longer
 * rendered — the contract field stays, the screen loses the row. The remaining
 * three are label-left / value-right rows, not a 2×2 grid.
 */
export const STAT_WATCHING_KO = "감시 중 이벤트";
export const STAT_WITHIN_30D_KO = "30일 이내 마감";
export const STAT_LAPSE_PENDING_KO = "소멸 앞둔 신주인수권";

// ---------------------------------------------------------------------------
// 소멸주의보 (R2 §소멸주의보 strip — "발표용 문장 4 with live numbers")
// ---------------------------------------------------------------------------

/**
 * 발표용 문장 4, again in the pipeline's own words:
 *
 * > 지금도 {n}건의 신주인수권이 소멸을 앞두고 있습니다 (가장 빠른 청약 마감
 * > {date}, {corp}).
 *
 * The numbers are live from the **same** `/board/summary` object the stats card
 * reads, so the strip and the card can never disagree. The landed R2 card shows
 * 계양전기; the live tie-break names 퓨쳐켐 (three offerings share 청약 마감
 * 2026-09-04 and the API orders by 접수번호 — `P5.S3` note 9). Live data
 * governs: the round asks for live numbers by contract.
 *
 * **R9 supersedes the `{corp}` slot** (build-prompt §6, walk finding 8): naming
 * one of three tied offerings made the strip and the board's first row disagree
 * one screen apart, so a tie prints `tieCountKo(n)` — 「3개 종목」 — instead of a
 * name. The template itself is unchanged; only what fills the slot moved.
 */
export const lapseSentence = {
  before: "지금도 ",
  middle: "의 신주인수권이 소멸을 앞두고 있습니다 (가장 빠른 청약 마감 ",
  join: ", ",
  after: ").",
} as const;

// ---------------------------------------------------------------------------
// Board (R2 §Board 소멸 카운트다운, R3 §추후결정 board strip)
// ---------------------------------------------------------------------------

/** R2 §Copy lists "board title 소멸 카운트다운" among the round's signed copy. */
export const BOARD_TITLE_KO = "소멸 카운트다운";

/** The freshness chip: mono 11 `기준 YYYY-MM-DD HH:MM KST` (R2 §Board). */
export const FRESHNESS_PREFIX_KO = "기준";
export const FRESHNESS_TZ_KO = "KST";

/** The stale chip's suffix — R2 §Board: "+ suffix `· N시간 전 데이터`". */
export const staleSuffixKo = (hours: number) => `· ${hours}시간 전 데이터`;

/** The stale inset notice above the tabs, R2's `result.md` §Freshness verbatim
 * (signed at the gate as part of the round's new chrome copy). The board itself
 * never dims: this notice is the whole staleness treatment besides the chip. */
export const STALE_NOTICE_KO =
  "데이터가 갱신되지 않고 있습니다. 아래 값은 기준 시각의 공시 기준이며, 그 이후의 정정공시는 반영 전일 수 있습니다.";

/** The 전체 tab. The other three take their labels from `lib/copy.ts`'s
 * `RIGHTS_LABEL_KO` / `RIGHTS_LABEL_COMPACT_KO`, which are R2's own tab strings
 * (유상증자 신주인수권 · 전환사채 오버행 · 주식매수청구권) and R1's compact forms
 * (유증 / CB / 매수청구) that R2 reuses on mobile. */
export const TAB_ALL_KO = "전체";

/** The ① extras cell: `청약 YYYY-MM-DD` + the `발행가 확정 전` chip.
 *
 * The chip is R2 §Copy's own new string, and its `result.md` states the rule it
 * carries: "a known-later fact, not a TBD schedule … Never a dash, never an
 * empty value cell". Which end of the 구주주 청약 window the date names is this
 * slice's decision (`P5.S3` note 10): the **마감** (`subscription_end`) — every
 * other 청약 date this product prints is the closing one (발표용 문장 4's "가장
 * 빠른 청약 마감", the report's 청약종료 column, `next_lapse.date`), and the
 * 소멸주의보 strip on this very page prints it for the same offerings. */
export const SUBSCRIPTION_PREFIX_KO = "청약";
export const PRICE_PENDING_KO = "발행가 확정 전";

/** The DART 원문 link's accessible name. The mark itself is R2's `↗`; the words
 * are R3's own link label ("DART 원문 ↗"), so the screen-reader name is signed
 * copy rather than a new sentence. */
export const DART_LINK_KO = "DART 원문";

/**
 * The ② open-window strip, R2 §Board verbatim:
 *
 * > "전환청구 **진행 중** — 개시일이 지나 지금 전환할 수 있는 전환사채 **56건**"
 * > (진행 중 in `--live` 600, count mono 600) + 펼치기
 *
 * The count is live (57 today). **Never 종료/마감** for these rows: a past ②
 * opening means the window is open right now (`ui-traps.md` #5).
 */
export const openNowSentence = {
  before: "전환청구 ",
  emphasis: "진행 중",
  middle: " — 개시일이 지나 지금 전환할 수 있는 전환사채 ",
  after: "",
} as const;

/** R3 §추후결정 board strip: "일정 추후결정 — 카운트다운 없이 감시 중인 이벤트
 * N건" + 펼치기, below the ② strip, same pattern, **not ranked**. */
export const tbdSentence = {
  before: "일정 추후결정 — 카운트다운 없이 감시 중인 이벤트 ",
  after: "",
} as const;

/**
 * The strips' disclosure button (R2 §Board, R3 §추후결정 board strip), now the
 * **closed** half of a pair.
 *
 * R2 kept this one label open or closed because "a 접기 label is copy nobody
 * signed". **R9 signed it** (build-prompt §5: "라벨이 상태를 읽는다 — 닫힘
 * `펼치기` / 열림 `접기`", and `result.md` §3-4: "이번 라운드에 카피가 열렸으므로
 * 「서명되지 않은 라벨」이라는 R2의 근거가 사라졌다"), so the toggle now says
 * what it does and `aria-expanded` agrees with the label instead of standing in
 * for it. The board's own window footer follows the same rule
 * (`collapseToFirstKo`).
 */
export const EXPAND_KO = "펼치기";

// ---------------------------------------------------------------------------
// R9 — 관제 현황판 폴리시 (round `09-landing-board`, signed 2026-08-23)
//
// R9 is a **dated copy exception**: its handoff opened count / shown / remaining
// labels, 접기, and the refresh-state label for this one surface and nothing
// else. The fourteen constants below are `build-prompt.md` §9's own table,
// transcribed verbatim ("아래 신규 상수 14개가 전부이며, 그 밖의 제품 문구는
// 잠긴 상태 그대로다"), and all fourteen are registered in
// `docs/reference/design/grounding/copy-inventory.md`.
// ---------------------------------------------------------------------------

// R9's meta line — `TAB_NOTE_KO` ("탭 숫자는 감시 중 전체 건수입니다") and
// `shownLine` ("아래 목록은 카운트다운 {ranked}건 중 {shown}건") — is **removed**
// by operator decision, along with the D-day legend below. Both existed to
// explain a tab count that counted events the board could not show; the count
// now counts what it renders (`board_bucket`), so the explanation went with the
// gap it explained. Six of R9's fourteen constants are retired with it — these
// two and the four legend labels — and `copy-inventory.md` still registers all
// fourteen, because a signed round is a record of what was signed.

/** The window footer's button — **what one click adds**, not what is left
 * (`build-prompt.md` §4/§9). */
export const moreKo = (step: string | number) => `${step}건 더 보기`;

/** The window footer's remainder, separated from the button so the two numbers
 * stop being read as one (`build-prompt.md` §4/§9, walk finding 3). */
export const remainingKo = (remaining: string | number) => `남은 ${remaining}건`;

/** The way back out of an expanded window (`build-prompt.md` §4/§9) — shown once
 * the window is past its first step. */
export const collapseToFirstKo = (step: string | number) => `처음 ${step}건으로 접기`;

/** The strips' disclosure button, **open** (`build-prompt.md` §5/§9). Pairs with
 * `EXPAND_KO`. */
export const COLLAPSE_KO = "접기";

/**
 * The auto-refresh's whole visible vocabulary (`build-prompt.md` §7/§9): it sits
 * beside a **new** 기준시각 and stays until the next refresh that brings one.
 *
 * There is no other refresh copy — no spinner, no button, no 새로고침, no failure
 * sentence. An 기준시각 that stops moving is how a failing refresh says so.
 */
export const REFRESHED_KO = "갱신됨";

/**
 * 동시 마감 (`build-prompt.md` §6/§9, walk finding 8).
 *
 * When several ① offerings share the earliest 청약 마감, the 소멸주의보 sentence's
 * `{corp}` slot says how many there are instead of naming one of them — the
 * sentence's shape and words are otherwise untouched. With a single offering it
 * still names the company. The count is served (`next_lapse.tie_count`); the
 * screen never guesses it.
 */
export const tieCountKo = (count: string | number) => `${count}개 종목`;
