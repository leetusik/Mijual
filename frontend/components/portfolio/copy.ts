/**
 * Every Korean string 내 포트폴리오 renders, and where each one comes from.
 *
 * Same rule and same shape as `lib/copy.ts` (the primitives'),
 * `components/chrome/copy.ts`, `components/landing/copy.ts`,
 * `components/event/copy.ts`, `components/lookup/copy.ts` and
 * `components/auth/copy.ts`: **nothing here is invented.** Inventing a Korean
 * string is a design change, not an implementation detail, so every entry below
 * is transcribed from the landed R5 record —
 * `docs/reference/design/rounds/05-account/output/build-prompt.md` (§Portfolio,
 * §D-day 목록, §알림, §샘플 포트폴리오, §Chrome, §Mobile) and its `result.md`
 * (§Proposed copy, §Departures & notes, incl. the post-gate **R5-8**), whose whole
 * copy list the R5 gate signed off.
 *
 * Where a sentence already belongs to another signed surface it is
 * **re-exported rather than re-typed** — R5 says the 보유량 input is "R4 서명
 * 프리미티브 재사용" with only its caption swapped, and "금액 = R4 계약 그대로",
 * so this surface speaks R4's own vocabulary for anything it shares with 조회.
 *
 * ## The one label the record does not write
 *
 * R5 signs the sample→계정 migration as an *offer* ("로그인 시 계정 이전
 * 제안(자동 이전 금지)", "로그인 시 이전 제안 → conversion offer") and writes no
 * sentence for it. `MIGRATE_LABEL_KO` therefore composes the round's own noun
 * (계정 이전) rather than writing one, the same class of move
 * `components/chrome/copy.ts` made for `© 미주알` and `components/auth/copy.ts`
 * made for 비밀번호 재설정 — and it is flagged the same way for `P5.S19`. The
 * offer's two controls are R5-3's own 담기 / 담지 않기, and what it lists is data
 * (종목명 + 주수), not copy.
 */

// ---------------------------------------------------------------------------
// Shared with 내 종목 조회 — R4's primitives, re-exported (build-prompt §Portfolio:
// "입력은 R4 서명 프리미티브 재사용", §D-day 목록: "금액 = R4 계약 그대로")
// ---------------------------------------------------------------------------

export {
  /** "label 보유 주식 수 · mono right-aligned integer input · suffix 주" (R4 §3). */
  HOLDING_LABEL_KO,
  /** "프리셋 칩 100/500/1,000주" — R5 names the same three. */
  PRESET_SHARES,
  /** 진행 중인 권리 — R4 §4's section title, and the holding row's summary cell
   * ("진행 중인 권리 요약", R5 §Portfolio). */
  RIGHTS_SECTION_KO,
  /** "지나간 행: inset 칩 `기간 지남 · D+n`" — R5 restates R4's own chip, so it is
   * the same string on both surfaces. */
  pastPeriodChipKo,
  /** The 종목 추가 panel resolves through `GET /stocks?q=`, the product's one
   * resolver, so a miss states R4's own signed line. */
  noMatchKo,
  SEARCH_PLACEHOLDER_KO,
  SEARCH_SUBMIT_KO,
} from "@/components/lookup/copy";

export { SHARES_UNIT_KO, STEP_DEPENDENCY_KO } from "@/components/event/copy";

/** The account destinations (R5 §Chrome) — the layer's own name, the 알림
 * surface's name and 로그아웃. They are chrome labels, transcribed beside the rest
 * of the chrome's copy, and this surface re-uses them rather than spelling the
 * same words twice.
 *
 * **R8 retired R5-4's 「샘플」 chip and 샘플 종료** (SIGNOFF), which used to be
 * re-exported here too: the chrome says nothing about the sample any more, so the
 * only thing that does is this surface's own `SampleBanner`.
 *
 * **R13 §4b — the layer's name on a reader surface is 「보유 종목」**, so the label
 * this module re-exports is R8's own `HOLDINGS_LABEL_KO` (the nav slot's word) and
 * no longer R5's `PORTFOLIO_LABEL_KO` (「내 포트폴리오」), which the chrome already
 * renders nowhere. 알림 설정's rail composes `← ` + that label — the same
 * composition `AuthRail` and `LookupRail` make, and no new Korean. R5's constant
 * stays exported from the chrome for the record; this surface simply never says
 * 포트폴리오. */
export {
  HOLDINGS_LABEL_KO,
  LOGOUT_KO,
  NOTIFICATIONS_LABEL_KO,
} from "@/components/chrome/copy";

// ---------------------------------------------------------------------------
// 보유 종목 (build-prompt §Portfolio)
// ---------------------------------------------------------------------------

/**
 * The holding row's cells, named by the round itself:
 *
 * > 행: **종목** / **보유량**(인라인 편집 …) / **진행 중인 권리 요약**(RightsChip +
 * > governing label + `D-n · date`) / **수정·삭제**.
 *
 * The same class of enumeration R4's breakdown grid columns came from
 * (`COL_OFFERING_KO` …), rendered as the grid's column headers.
 */
export const COL_STOCK_KO = "종목";
export const COL_SHARES_KO = "보유량";

/** The action column, before and after the row-edit confirm — 개정 ④: "행 편집
 * 확정 = 액션 열 저장/취소 **가로 배치**", build-prompt: "확정은 우측 액션 열이
 * 수정·삭제 → 저장·취소로 교체, 가로 배치". */
export const EDIT_KO = "수정";
export const DELETE_KO = "삭제";
export const SAVE_KO = "저장";
export const CANCEL_KO = "취소";

/** "삭제 = 즉시 + **8초 되돌리기**, 모달 없음" (build-prompt §Portfolio, and
 * result.md §Departures: "삭제 = 즉시 + 8초 되돌리기 (모달 없음)"). The window is
 * the record's own number. */
export const UNDO_KO = "되돌리기";
export const UNDO_SECONDS = 8;

/** The one caption R5 swaps on the reused R4 input: "저장 위치 캡션만 교체:
 * **'계정에 저장 · 마감 알림의 기준'**". It states both facts the account mode
 * adds — the count leaves the browser, and it is what a D-day alert is measured
 * against (the sending itself is P4's). */
export const HOLDING_CAPTION_KO = "계정에 저장 · 마감 알림의 기준";

/** R5 §Mobile: "**종목 추가**는 하단 패널" — the panel's own name, and the round's
 * own words for it. */
export const ADD_SECTION_KO = "종목 추가";

/** R5-3's two controls, on the 세션 이월 row: "inset 행 … + **담기/담지 않기**".
 * 담기 is also R5-2's own verb for the same act ("내 포트폴리오에 담기 →"), which
 * is why the 종목 추가 panel's submit carries it too. */
export const KEEP_KO = "담기";
export const DISCARD_KO = "담지 않기";

// ---------------------------------------------------------------------------
// 빈 상태 + 세션 이월 제안 (R5-3)
// ---------------------------------------------------------------------------

/** result.md §Proposed copy, Portfolio: "포트폴리오가 비어 있습니다" · "종목과
 * 보유량을 등록하면, 진행 중인 권리와 마감을 여기서 지켜보고 이메일로 알립니다."
 *
 * **The title is the operator's R13 revision of that R5 string** (2026-08-24,
 * build-prompt §4b): 독자 표면에서 「포트폴리오」를 쓰지 않는다 — 층 이름은
 * **보유 종목** (R8's nav slot word). Same sentence, the layer's own name in it;
 * the body is untouched, and the route, the paths and the component names are
 * unchanged. */
export const EMPTY_TITLE_KO = "보유 종목이 비어 있습니다";
export const EMPTY_BODY_KO =
  "종목과 보유량을 등록하면, 진행 중인 권리와 마감을 여기서 지켜보고 이메일로 알립니다.";

/**
 * R5-3 verbatim, with the round's own example filled from live data:
 *
 * > 빈 포트폴리오에 inset 행 "조회에서 입력한 계양전기 500주가 이 세션에 남아
 * > 있습니다" + 담기/담지 않기. **자동 저장 없음** (R4-6 restore-chip 패턴 재사용).
 *
 * The value it names is 조회's own sessionStorage entry (`lib/holding.ts`'s
 * `SESSION_KEY`), which never left the browser and never will unless the reader
 * presses 담기 — at which point it becomes an ordinary authenticated write.
 */
export const carryOverKo = (stock: string, shares: string) =>
  `조회에서 입력한 ${stock} ${shares}주가 이 세션에 남아 있습니다`;

/** The sample→계정 이전 offer's label — composed from the round's own noun
 * ("로그인 시 **계정 이전** 제안(자동 이전 금지)"), never written. See this
 * module's header. */
export const MIGRATE_LABEL_KO = "계정 이전";

// ---------------------------------------------------------------------------
// D-day 목록 (build-prompt §D-day 목록)
// ---------------------------------------------------------------------------

/** "섹션 2개: **다가오는 마감**(D-day 오름차순) · **지나간 마감**(최근순)". */
export const UPCOMING_SECTION_KO = "다가오는 마감";
export const PAST_SECTION_KO = "지나간 마감";

/** "앵커 날짜 명기 ('기준 YYYY-MM-DD (KST)'), 모든 D-day는 상류 계산값 — 브라우저
 * 계산 금지." The date is the served `reference`, which is the KST day every
 * `dday` in the payload was computed against (`P5.S8`). */
export const referenceKo = (date: string) => `기준 ${date} (KST)`;

/** The ③ half of "지나간 행: inset 칩 `기간 지남 · D+n` / **`통지 마감 지남 ·
 * D+n`** — alert 색 금지". The ① half is R4's own chip, re-exported above. */
export const pastNoticeChipKo = (dday: string) => `통지 마감 지남 · ${dday}`;

/** "① 소멸 행은 500주 기준 「추정」 금액 + **'놓친 돈 상세 →'** 링크(조회
 * breakdown으로)". The link goes to `/stocks/{corp_code}` — 조회's own stable
 * handle, where the same offering's breakdown row lives.
 *
 * **R13 Q-B (session revision) moved where it stands, not what it says**: it
 * renders **inside the 금액 줄**, right after the label and the basis, and a row
 * the reader has checked renders it **not at all** — that row is saying it is no
 * longer 놓친 돈, so a link calling 놓친 돈 has no place on it. Unchecking brings it
 * back. The line keeps the control's height either way (`Portfolio.module.css`
 * `.lapsedLine`), so the swap moves 0px. */
export const MISSED_DETAIL_KO = "놓친 돈 상세 →";

// ---------------------------------------------------------------------------
// 챙긴 돈 체크 (R5-8, post-gate operator addition)
// ---------------------------------------------------------------------------

/**
 * R5-8 verbatim:
 *
 * > 지나간 ① 소멸 행에 체크박스 "**청약·매도로 챙겼습니다**": 체크 시 라벨
 * > **놓친 돈 → 챙긴 돈**, 금액 동일(「추정」 유지), 색 alert → live, 캡션
 * > "**본인 표시 · 계정에 저장**". 공시 데이터가 아닌 사용자 주장 — 계정에만 저장.
 *
 * The two labels are the row's own, and they name the *same* number: the check
 * re-labels and re-colours, and changes no figure anywhere (`P5.S8` note 7 — the
 * mark stores no amount and the payload carries no total for it to reach).
 */
export const CLAIM_CHECK_KO = "청약·매도로 챙겼습니다";
export const MISSED_LABEL_KO = "놓친 돈";
export const CLAIMED_LABEL_KO = "챙긴 돈";

/** The caption, and its sample/anonymous half. R5-8 writes "본인 표시 · 계정에
 * 저장" and the build prompt states the other storage in the same sentence:
 * "계정에 저장, **샘플/익명에서는 이 브라우저(localStorage)에**".
 *
 * **P7 (item 10) trimmed the sample half back to R5-8's own 「본인 표시」** — the
 * operator named this exact caption as the copy to remove, and the storage clause
 * is the build prompt's mechanism, which a reader gains nothing from. The account
 * half keeps 계정에 저장: that one is the reader's own fact (the mark follows the
 * account), not narration. So the two captions no longer differ only in storage —
 * one names where the mark is kept, the other just names what it is. */
export const CLAIM_CAPTION_ACCOUNT_KO = "본인 표시 · 계정에 저장";
export const CLAIM_CAPTION_LOCAL_KO = "본인 표시";

// ---------------------------------------------------------------------------
// 알림 설정 (R5-5, R5-7)
// ---------------------------------------------------------------------------

/** result.md §Proposed copy, Notify — the surface's own title. */
export const NOTIFY_TITLE_KO = "마감 임박 이메일";

/** build-prompt §알림: "설정: **수신 주소(변경)** · 마감 임박 시점 칩 …". The
 * address *is* the account email (`P5.S8` note 10: `security` fixes stored PII at
 * email + password hash, so there is no second address), and 변경 edits the
 * account. */
export const ADDRESS_LABEL_KO = "수신 주소";
export const CHANGE_KO = "변경";

/** "마감 임박 시점 칩 다중선택 (7일/3일/1일/당일; 기본 7일+1일)", with result.md's
 * own chip labels: "시점 칩 **7일 전/3일 전/1일 전/당일**". The values are the
 * API's `lead_days` (`portfolio.LEAD_DAY_CHOICES = (7, 3, 1, 0)`), and the
 * default is served, never assumed here. */
export const LEAD_DAY_LABELS_KO: ReadonlyArray<{ days: number; label: string }> = [
  { days: 7, label: "7일 전" },
  { days: 3, label: "3일 전" },
  { days: 1, label: "1일 전" },
  { days: 0, label: "당일" },
];

/**
 * R5-5 verbatim: "행은 보이되 컨트롤 없음: **「예정」 칩** + '준비되면 이 자리에서
 * 켤 수 있습니다'. 동작하지 않는 스위치 없음."
 *
 * The chip renders **예정** and the border is its enclosure — `P5.S10` note 4a's
 * convention for exactly these brackets ("「」 is the documents' own quoting
 * notation — it also wraps 「예정」"). KakaoTalk is the round's own token for the
 * channel, and there is no server field behind this row at all (`P5.S8` note 12),
 * which is what makes "no working control" structural rather than remembered.
 */
export const KAKAO_LABEL_KO = "KakaoTalk";
export const PLANNED_CHIP_KO = "예정";
export const KAKAO_NOTE_KO = "준비되면 이 자리에서 켤 수 있습니다";

/** build-prompt §알림: "· 로그아웃 · **계정 삭제(이메일 즉시 삭제)**", with
 * result.md's sentence: "계정을 삭제하면 이메일 주소를 즉시 지웁니다 — 남는 것이
 * 없습니다." It is true by construction: `DELETE /auth/account` removes the row
 * and the cascade takes sessions, holdings, claims and preferences with it
 * (`P5.S7` note 11, `P5.S8`).
 *
 * **R13 (session revision) withdraws R5's 상시 placement of the sentence**: it is
 * rendered **only while the control is armed** — a reader with no intention of
 * deleting has no reason to read the consequence of deleting on every visit, and
 * the reader who armed it reads this *before* the irreversible second press. The
 * string itself is untouched. */
export const DELETE_ACCOUNT_KO = "계정 삭제";
export const DELETE_ACCOUNT_NOTE_KO =
  "계정을 삭제하면 이메일 주소를 즉시 지웁니다 — 남는 것이 없습니다.";

// ---------------------------------------------------------------------------
// 샘플 포트폴리오 (R5-4)
// ---------------------------------------------------------------------------

/** result.md §Proposed copy, Sample — the banner, verbatim: "샘플 포트폴리오 —
 * 구성 예시입니다. 종목·공시·마감은 실제, 계정·보유량은 예시입니다."
 *
 * **The first two words are the operator's R13 revision** (2026-08-24,
 * build-prompt §4b — the same revision `EMPTY_TITLE_KO` carries): 독자 표면에서
 * 「포트폴리오」를 쓰지 않는다, so the banner names the layer 보유 종목. Nothing
 * else about the sentence moves.
 *
 * It is exactly true of what is rendered: the rows are live corpus events for
 * four pinned filings and every number on them is the server's, while the
 * holdings themselves — the issuers and their 보유량 — are the card's example. */
export const SAMPLE_BANNER_KO =
  "샘플 보유 종목 — 구성 예시입니다. 종목·공시·마감은 실제, 계정·보유량은 예시입니다.";
