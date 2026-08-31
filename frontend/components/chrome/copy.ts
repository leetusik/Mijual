/**
 * Every Korean string the global chrome renders, and where each one comes from.
 *
 * Same rule and same shape as `lib/copy.ts`, which holds only what the trust
 * primitives need and says so: *surface* copy belongs to the slice that renders
 * the surface, transcribed with a citation. This is the chrome's — the nav, the
 * mobile sheet and the footer (R2 §Page shell, signed at the R2 gate: the
 * signoff record explicitly covers "the round's new chrome copy … and the footer
 * provenance re-cut").
 *
 * **Nothing here is invented.** Inventing a Korean string is a design change, not
 * an implementation detail; a string with no citation does not belong in this
 * file. Where a later round superseded a label, the *superseded* label is what
 * renders — `docs/current/frontend.md`'s supersession table governs a landed
 * record, and R2's record is immutable history that still spells the old ones.
 */

import { ROUTES } from "@/lib/routes";

/** The wordmark the cosmos chrome uses.
 *
 * R2 §Page shell set the *placement* and R2.1 re-cut the chrome cards on cosmos
 * with the white mark. **R17 supersedes R2's two heights** — nav h27 / footer
 * h24, ink-aligned rather than box-centred — and `Wordmark.tsx` carries both
 * numbers and the offset. What R2's own asset was — `mijual-logo-ring-white.png`,
 * the latin MIJUAL wordmark with its orbital ring — is **retired** by the
 * 주주의관제탑 rebrand (P10); there is no ring in the new mark, so no name or
 * comment here says "ring".
 *
 * The file is `juju2-wordmark-white.png`: an alpha-preserving black→white recolor
 * of the operator's own delivered PNG, generated **in this repo** and recorded
 * with its exact command in `public/assets/README.md`. It supersedes the thin
 * first mark (`juju-wordmark-white.png`, 1213×319, landed by `P10.S1` and
 * retired at the gate — "previous one was so thin"): the replacement carries
 * **2.4× the ink** in its glyph band, which is why the fix was a new source file
 * and not a larger placement.
 *
 * **There is no black sibling any more.** The first mark had one for light
 * surfaces; nothing ever referenced it, R17 names no such variant, and the
 * symbol — the one mark that does need to change colour — is painted with a CSS
 * `mask` instead. See the assets README.
 *
 * It is still **never re-encoded** — the reason is now provenance rather than
 * byte-for-byte design-project output: the README proves this file by pixel
 * signature, and any re-compression breaks that proof. Which is why the consumer
 * is a plain `<img>` and not `next/image` (that would ship a re-compressed
 * derivative). */
export const WORDMARK_WHITE = "/assets/juju2-wordmark-white.png";
/** The file's intrinsic box. **1292 was the pre-R18 value** — the artwork carried
 * a quarter-em space between 「의」 and 「관」, and the derivation command now cuts
 * those **45 dead columns** (`x=530..574`, inside a 70-column, full-height
 * transparent band) before writing the PNG, so the box is 1247×371. `P10.review`
 * (R18 §①). Nothing vertical moved: see `Wordmark.tsx` for the offset. */
export const WORDMARK_NATURAL = { width: 1247, height: 371 } as const;

/** The wordmark's text equivalent — the product's own name in Korean, unspaced
 * (`docs/current/product.md`). Not a new string: it is the name of the thing,
 * and it is what the mark itself spells. P10 replaced the retired 미주알 here
 * when it replaced the mark; both are the same claim, so they change together. */
export const BRAND_ALT_KO = "주주의관제탑";

/** The surfaces the chrome names, and R8's two nav destinations.
 *
 * R2 landed 내 종목 연결 · 관제 현황판 · 해설 as a three-slot nav and posed the
 * labels back as provisional. Both were then settled by later signed rounds and
 * both are in the supersession table: R4 named the surface **내 종목 조회**
 * ("Naming consequences: nav label 내 종목 연결 → 내 종목 조회"), and R6 "retires
 * the provisional 해설 nav label in favor of 「AI 질문」". P7 item 1 then removed
 * the 내 종목 조회 slot itself (an operator override, not a relabelling).
 *
 * **R8 re-cuts the bar to two destinations — AI 질문 · 보유 종목, in that order**
 * (build-prompt §1):
 *
 * > 「관제 현황판」 링크는 제거한다 — 현황판은 랜딩이고 링 워드마크(→
 * > `ROUTES.board`)가 이미 그 목적지다. 같은 목적지를 바에서 두 번 말하지 않는다.
 * > `BOARD_LABEL_KO`는 표면 제목 용도로만 남기고 크롬에서는 미사용.
 *
 * So `BOARD_LABEL_KO` and `STOCKS_LABEL_KO` stay exported as **surface names**
 * (조회's own header, the detail page's ← crumb, the AI 질문 link rows) and the
 * chrome renders neither. */
export const STOCKS_LABEL_KO = "내 종목 조회";
export const BOARD_LABEL_KO = "관제 현황판";
/** Also the footer's action link, where R2 landed the retired 해설. */
export const ASK_LABEL_KO = "AI 질문";

/** R8's new destination slot (build-prompt §1 / §7 — the round's own new
 * constant): the 2층 surface, under one label whether or not the reader has an
 * account.
 *
 * > `보유 종목`은 로그인 여부와 무관하게 같은 라벨·같은 라우트. 익명이면 표면이
 * > 샘플 모드로 응답 (`SampleBanner` + `lib/sample.ts` 기존 동작) — nav는 아무
 * > 배지도 붙이지 않는다.
 *
 * The round's own reason for the word (result.md §1): 보유 종목 is a plain noun
 * phrase whose object is distinct from the hero's 내 종목 **조회** (an act of
 * looking up), and 내 포트폴리오 is the loanword the operator questioned. */
export const HOLDINGS_LABEL_KO = "보유 종목";

export const NAV_LINKS = [
  { label: ASK_LABEL_KO, href: ROUTES.ask },
  { label: HOLDINGS_LABEL_KO, href: ROUTES.portfolio },
] as const;

/** The nav's right-hand 2층 entry (R2 §Page shell: "Right: 로그인 (quiet …)").
 * R5 keeps it and swaps it, logged in, for the 축약 이메일 계정 메뉴 — that is
 * `P5.S16`'s, and `AccountSlot.tsx` is the one place it happens. */
export const LOGIN_KO = "로그인";

/**
 * The logged-in slot R5 puts in 로그인's place (§Chrome, 개정 ⑤).
 *
 * > Desktop: links 불변(R2 삼분할) · 로그인 링크 → 축약 이메일 메뉴(mono, 앞 4자 +
 * > … + 도메인 끝): **내 포트폴리오 / 알림 설정 / 로그아웃**.
 * > Mobile 시트: 구분선 + 내 포트폴리오(이메일 병기) / 알림 설정 / 로그아웃.
 *
 * 내 포트폴리오 is the layer's own name (R5-6 개정, which also withdrew the fourth
 * nav link: "내 포트폴리오는 links가 아니라 계정 메뉴(스택 리스트) 첫 행"), and
 * 알림 설정 is the 알림 surface's — the round's own two menu rows. 로그아웃 is
 * R5-1's ("로그아웃 즉시, 확인 다이얼로그 없음"). The three destinations are
 * chrome labels, so they are transcribed here and the surfaces re-use them.
 */
export const PORTFOLIO_LABEL_KO = "내 포트폴리오";
export const NOTIFICATIONS_LABEL_KO = "알림 설정";
export const LOGOUT_KO = "로그아웃";

/* ⚠ **R8 supersedes R5 §Chrome 개정 ⑤ here.** The account menu is now two rows —
 * 알림 설정 / 로그아웃 — and the 내 포트폴리오 row is deleted, because the same
 * destination moved up into the bar as 보유 종목 (build-prompt §2:
 * "`내 포트폴리오` 행 삭제 — `PORTFOLIO_LABEL_KO`는 계정 표면 자체 제목 용도로만
 * 남기고 크롬에서는 미사용"). The constant stays exported as the 2층 surface's own
 * name (`components/portfolio/copy.ts` re-exports it); the chrome renders it
 * nowhere. */

/* **R5-4's 「샘플」 chip and 샘플 종료 button are retired by R8** (SIGNOFF: "R5-4
 * (샘플 chip + 샘플 종료)" superseded), so their two constants are gone from this
 * file. The account slot has exactly two states now — anonymous and signed-in —
 * and the only surface that says a portfolio is a sample is the portfolio itself
 * (`SampleBanner`). 로그아웃 여부가 곧 상태: 보유 종목 opens the sample when
 * nobody is signed in, so there is nothing to "end". */

/** The mobile top bar's menu button (R2 §Page shell — "메뉴 button, mono, 44px
 * hit"). It keeps this label while the sheet is open; the open/closed state is
 * carried by `aria-expanded`, because a 닫기 label is copy nobody signed. */
export const MENU_KO = "메뉴";

/* **R2's nav `[의견]` chip is removed by R8** (build-prompt §1: "`VockyTrigger
 * surface="nav"` 제거 (`VOCKY_NAV_KO` 상수도 삭제)"), so that constant is gone.
 * The 의견 진입점 is the footer button and the mobile sheet row — two places, and
 * neither is a floating corner button (R2 §6-4, which R8 strengthens). */

/** The 의견 보내기 entry point's label, in both remaining placements (R2 §vocky,
 * kept by R8 build-prompt §7: "기존 `VOCKY_ROW_KO`(「의견 보내기」)는 진입점
 * 라벨로 재사용"). It is also the surface's own title — see
 * `FEEDBACK_TITLE_KO`, which the round lists separately in its copy table. */
export const VOCKY_ROW_KO = "의견 보내기";

/* ---------------------------------------------------------------------------
   The four footer sentences R8 removed from the surface (build-prompt §4) —
   **and the constants R9 deleted with them.**

   R8 took the markup out and left the five strings transcribed here, because its
   own record made deleting them conditional on an operator decision (result.md
   §6-1: the footer was the gate-cost sentence's *last* placement and the
   면책 sentence's only one, so the session proposed relocating both). That
   decision came back at the R9 gate — **P8 Operator Question Q5: "p8 q5: drop."**
   — and R9's build-prompt §9 executes it: 「삭제: … 푸터에서 R8이 뺀 게이트
   비용/면책 상수 (P8 Q5: 폐기, 재배치 없음 — 랜딩 어디에도 두지 않는다)」.

   So `POSITIONING_KO`, `PROVENANCE_KO`, `GATE_COST_VALUE_KO`,
   `GATE_COST_TAIL_KO` and `DISCLAIMER_KO` are **gone from this module**
   (`P8.S5`) — exactly the five R8's build-prompt §4 named for deletion, none of
   them rendered anywhere since `P8.S3`, and none of them imported by anything.

   Two same-named constants elsewhere are **different surfaces' own strings and
   are untouched**: `lookup/copy.ts`'s `DISCLAIMER_KO` + `PROVENANCE_KO` (the
   놓친 돈 card and the /stocks pages render them) and `event/copy.ts`'s
   `PROVENANCE_KO` (the detail page's). The sentences themselves also survive in
   the design record — R2's build prompt, `grounding/copy-inventory.md` and the
   operator's own brief — so nothing was lost, only unshipped.
   --------------------------------------------------------------------------- */

/** The identity line's © (R2 §Page shell: "© · 자료: 금융감독원 DART 전자공시
 * | 의견 보내기 · 해설 (mono 11)", with 해설 → AI 질문 per R6).
 *
 * R8 keeps both halves of that row and re-cuts everything around them: one
 * hairline, one row, and **Pretendard rather than mono** — "mono는 숫자
 * 전용(R1)이고 남은 줄에는 숫자가 없다" (result.md §2-14). The words are
 * untouched.
 *
 * The record writes the symbol and no more, and the card that showed the line is
 * in the Claude Design project. The line composes R2's own symbol with the
 * product's own name and invents no sentence and **no year** (a year would be a
 * fact nobody stated). P10 swapped the name only — the record's `© 미주알`
 * became `© 주주의관제탑`, same shape, same symbol. */
export const COPYRIGHT_KO = "© 주주의관제탑";

/** The source line in the same row — R2's literal, and the product's one
 * provenance claim in the smallest possible form. */
export const SOURCE_KO = "자료: 금융감독원 DART 전자공시";

/* **The 운영자 연락처 joins that row at `P11.F2`, and adds no constant here.**
 *
 * The operator asked at P11's acceptance gate for their email and phone to be
 * published in the footer as well as in the agent's answer. What renders is the
 * **values themselves** — served from `MIJUAL_OPERATOR_CONTACT` through `GET
 * /site/contact`, split into an address and a number by the API — separated by
 * the same `·` the row already uses. They are *data*, not copy: an operator's own
 * address is not a string this file could transcribe from a record, and it
 * changes without a round.
 *
 * **And no label precedes them**, deliberately. 「문의」 or 「운영자 연락처」 here
 * would be an invented Korean string, which is a design change and not an
 * implementation detail (this file's own rule, first paragraph). The agent owns
 * the labelled form — `CONTACT_ROW` = 「운영자 연락처 → …」 in `mijual.agent.copy`
 * — and the footer owns the bare one.
 *
 * `Footer.tsx` carries the full override note, including why a numeral now sits
 * in a Pretendard row R8 typeset for having none. */

// ---------------------------------------------------------------------------
// 의견 보내기 — R8's new 미주알-owned surface (build-prompt §6, copy table §7)
// ---------------------------------------------------------------------------

/**
 * The fourteen strings R8 signs for the feedback surface, **verbatim from
 * build-prompt §7** ("카피 (신규 15 — 등재 필요)", of which `HOLDINGS_LABEL_KO`
 * above is the fifteenth). The round is the copy exception `handoff.md` §2
 * granted for this surface and this round only, dated 2026-08-23, and the
 * FeedbackStates card is the 정본.
 *
 * The set is deliberately small and it is the whole surface: a title, one guide
 * line, a placeholder, an empty-input hint, two fine-print sentences, the send
 * button in its two labels, the accepted line with its receipt label, the failure
 * line with its "your text is still here" reassurance, 다시 시도 and 닫기. There
 * is no contact field and therefore no contact copy — **the surface says out loud
 * that no reply is coming** (`FEEDBACK_FINE_KO`), which is the product's own
 * "거절하는 것을 소리 내어 말한다" rule rather than a new promise.
 *
 * Every string below is registered in
 * `docs/reference/design/grounding/copy-inventory.md` §R8 additions.
 */
export const FEEDBACK_TITLE_KO = "의견 보내기";
export const FEEDBACK_GUIDE_KO = "잘못된 수치나 바라는 점을 적어 주십시오.";
export const FEEDBACK_PLACEHOLDER_KO = "예: 계양전기 청약 기간이 공시와 다릅니다";
export const FEEDBACK_EMPTY_HINT_KO = "내용을 입력하면 보낼 수 있습니다.";
export const FEEDBACK_FINE_KO =
  "연락처를 받지 않으므로 답장은 드리지 못합니다. 이메일·계정 정보는 함께 보내지 않습니다.";
export const FEEDBACK_SEND_KO = "보내기";
export const FEEDBACK_SENDING_KO = "보내는 중입니다";
export const FEEDBACK_SENT_KO = "의견이 접수되었습니다.";
export const FEEDBACK_RECEIPT_LABEL_KO = "접수 번호";
export const FEEDBACK_RECEIPT_FINE_KO =
  "접수 번호는 문의 확인용 표기입니다. 답장은 드리지 못합니다.";
export const FEEDBACK_FAILED_KO = "의견을 보내지 못했습니다. 잠시 후 다시 시도해 주십시오.";
export const FEEDBACK_KEPT_KO = "입력한 내용은 그대로 남아 있습니다.";
export const FEEDBACK_RETRY_KO = "다시 시도";
export const FEEDBACK_CLOSE_KO = "닫기";

/** The close **glyph**, not a label — the same decision `components/ask/copy.ts`
 * records for the widget header ("the record writes the glyph itself and signs no
 * 닫기 label"). R8 uses it twice: the feedback header's 28×28 button, and the
 * mobile bar button while the sheet is open ("바 버튼: 닫힘 `메뉴`, 열림 **`×`**
 * … `aria-label`은 항상 `메뉴`"). result.md §6-3 logs it as a departure taken
 * *instead of* inventing Korean: "「닫기」 문구를 만들지 않기 위한 처리". */
export const CLOSE_GLYPH = "×";
