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
 * R2 §Page shell: "white ring wordmark PNG (h 19px)" in the nav, "(h 17)" in the
 * footer; R2.1: "Chrome cards (Nav/Footer/Feedback) re-cut on cosmos with the
 * white ring wordmark". The ring assets are R2's own addition (they close R1's
 * missing-symbol-mark gap — supersession table), and the delivered file is
 * `mijual-logo-ring-white.png` (2178×346, the MIJUAL wordmark with its orbital
 * ring). The charcoal pair is for light surfaces and never substitutes for it.
 *
 * The file is operator-exported design output: rendered at a constrained height
 * and **never re-encoded**, which is also why it is a plain `<img>` rather than
 * `next/image` (that would ship a re-compressed derivative). */
export const RING_WORDMARK_WHITE = "/assets/mijual-logo-ring-white.png";
export const RING_WORDMARK_NATURAL = { width: 2178, height: 346 } as const;

/** The wordmark's text equivalent. The mark reads "MIJUAL"; the product's own
 * name in Korean is 미주알 (`docs/current/product.md`, and the disclaimer below
 * spells it). Not a new string — the name of the thing. */
export const BRAND_ALT_KO = "미주알";

/** The three signed nav destinations, in R6's finalized order:
 * **내 종목 조회 · 관제 현황판 · AI 질문**.
 *
 * R2 landed 내 종목 연결 · 관제 현황판 · 해설 and posed the labels back as
 * provisional. Both were then settled by later signed rounds and both are in the
 * supersession table: R4 named the surface **내 종목 조회** ("Naming
 * consequences: nav label 내 종목 연결 → 내 종목 조회"), and R6 "retires the
 * provisional 해설 nav label in favor of 「AI 질문」" — its build prompt puts
 * 「AI 질문」 in "nav 세번째 자리". Rendering R2's literals would be rendering a
 * superseded decision. */
export const STOCKS_LABEL_KO = "내 종목 조회";
export const BOARD_LABEL_KO = "관제 현황판";
/** Also the footer's bottom-row link, where R2 landed the retired 해설. */
export const ASK_LABEL_KO = "AI 질문";

export const NAV_LINKS = [
  { label: STOCKS_LABEL_KO, href: ROUTES.stocks },
  { label: BOARD_LABEL_KO, href: ROUTES.board },
  { label: ASK_LABEL_KO, href: ROUTES.ask },
] as const;

/** The nav's right-hand 2층 entry (R2 §Page shell: "Right: 로그인 (quiet …)").
 * R5 keeps it and swaps it, logged in, for the 축약 이메일 계정 메뉴 — that is
 * `P5.S16`'s, and `AccountSlot.tsx` is the one place it happens. */
export const LOGIN_KO = "로그인";

/** The mobile top bar's menu button (R2 §Page shell — "메뉴 button, mono, 44px
 * hit"). It keeps this label while the sheet is open; the open/closed state is
 * carried by `aria-expanded`, because a 닫기 label is copy nobody signed. */
export const MENU_KO = "메뉴";

/** The nav's vocky trigger, brackets included — R2 writes it `[의견]` every
 * time, exactly as it writes `[근거]` (whose brackets `lib/copy.ts` also keeps).
 * R2 §Copy lists "의견 / 의견 보내기 (vocky trigger)" as signed chrome copy. */
export const VOCKY_NAV_KO = "[의견]";

/** The same trigger where it is a row or a quiet link — the mobile sheet and the
 * footer's bottom row (R2 §vocky: "nav `[의견]` button, mobile sheet 의견 보내기
 * row, footer 의견 보내기 link"). */
export const VOCKY_ROW_KO = "의견 보내기";

/** The footer's left-column positioning line (R2 §Page shell: "positioning line
 * (mono 11, `rgba(255,255,255,.45)`)").
 *
 * The sentence itself is **locked context**, not R2's to write: R2's handoff §3
 * lists "the positioning sentence" among the locked items and §1 states it —
 * "Positioning: 시장 전체의 소멸 임박 권리를 감시하는 관제 서비스 + 내 종목
 * 연결" — as does R1's handoff §1 and the operator's own brief
 * (`docs/reference/challenge/00_HANDOFF.md`).
 *
 * ⚠ It contains the words 내 종목 연결, and R4 superseded that as **a nav
 * label**. The supersession table's row is about the label; this is the
 * operator's positioning sentence, locked before any surface had a name, so it
 * is transcribed verbatim rather than re-written — rewriting locked copy is a
 * design change. Recorded for `P5.S19`/`P5.REVIEW` as a fidelity question. */
export const POSITIONING_KO =
  "시장 전체의 소멸 임박 권리를 감시하는 관제 서비스 + 내 종목 연결";

/** Footer sentence ① — the provenance line, quoted verbatim in R2's build prompt
 * and signed at the gate ("the footer provenance re-cut").
 *
 * `[추정]` here is **prose describing the mark**, not the mark itself: R2.1 note
 * 5 re-cut the sentence when the estimate mark became the bordered tag. So it is
 * rendered as characters, and the tag primitive is not used on it. */
export const PROVENANCE_KO =
  "모든 수치는 DART 공시에서만 나왔고, 추정치는 [추정] 표시로 구분했습니다.";

/** Footer sentence ② — the gate-cost line, and **the footer is its only
 * remaining placement**: R2.1 note 4 removed it from the value card, and R2's
 * build prompt says so again ("its only remaining placement").
 *
 * R2 §Copy landed it re-cut as "▷ 49.2억원은 할인율 인용이 게이트를 통과하지
 * 못해 총액에서 제외했습니다". The `▷` is retired from every UI surface (R2's
 * gate ruling, executed in R3 — supersession table), and the build prompt states
 * the replacement in the same breath: the value is **추정-tagged**. So the
 * sentence renders with `EstimateMarker` on 49.2억원 and no `▷`; the words are
 * otherwise untouched, including the missing full stop.
 *
 * The figure is `grounding/headline-numbers.md`'s "▷ 게이트가 포기한 금액
 * 49.2억원" (= 767.3억 upper bound − 718.1억 total, the three offerings whose
 * 할인율 failed its citation gate). It is a **dated pack number**: the
 * presentation contract serves no gate-cost figure, so unlike the landing's
 * headline this one cannot be live today — see `P5.S11`'s note in `phase.md`. */
export const GATE_COST_VALUE_KO = "49.2억원";
export const GATE_COST_TAIL_KO =
  "은 할인율 인용이 게이트를 통과하지 못해 총액에서 제외했습니다";

/** Footer sentence ③ — the disclaimer, R2 §Copy verbatim, signed at the gate. */
export const DISCLAIMER_KO =
  "미주알은 투자 자문·권유를 제공하지 않습니다. 모든 정보는 DART 공시 원문 확인을 전제로 제공됩니다.";

/** The bottom hairline row (R2 §Page shell: "© · 자료: 금융감독원 DART 전자공시
 * | 의견 보내기 · 해설 (mono 11)", with 해설 → AI 질문 per R6).
 *
 * The record writes the symbol and no more, and the card that showed the line is
 * in the Claude Design project. `© 미주알` composes R2's own symbol with the
 * product's own name and invents no sentence and **no year** (a year would be a
 * fact nobody stated). Flagged for `P5.S19` to check against the card. */
export const COPYRIGHT_KO = "© 미주알";

/** The source line in the same row — R2's literal, and the product's one
 * provenance claim in the smallest possible form. */
export const SOURCE_KO = "자료: 금융감독원 DART 전자공시";
