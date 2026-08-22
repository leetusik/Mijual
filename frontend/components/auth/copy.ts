/**
 * Every Korean string R5's auth surfaces and conversion touchpoints render, and
 * where each one comes from.
 *
 * Same rule and same shape as `lib/copy.ts` (the primitives'),
 * `components/chrome/copy.ts`, `components/landing/copy.ts`,
 * `components/event/copy.ts` and `components/lookup/copy.ts`: **nothing here is
 * invented.** Inventing a Korean string is a design change, not an implementation
 * detail, so every entry below is transcribed from the landed R5 record.
 *
 * ## The source is the round record, not the copy inventory — deliberately
 *
 * `grounding/copy-inventory.md` is generated from the code that emits Korean, and
 * P5 emitted none of this: R5's own record says so in the heading of its copy
 * list — "**Proposed copy (all new — copy-inventory에 auth 계열 없음)**" — and the
 * R5 signoff records the operator closing the round over that list. So the two
 * landed R5 files *are* the source of truth for every string here:
 *
 * - `docs/reference/design/rounds/05-account/output/build-prompt.md` (§Auth,
 *   §Conversion, §샘플 포트폴리오) — the implementation contract;
 * - `docs/reference/design/rounds/05-account/output/result.md` §Proposed copy —
 *   the sentences themselves, verbatim.
 *
 * ## Three strings the record does not write, and what happens instead
 *
 * 1. **A trigger label for 재설정.** The record names the mechanism ("재설정 =
 *    이메일 링크(가입 여부 비노출)") and its answer, never the control's label.
 *    `RESET_LINK_KO` composes the round's own two nouns (비밀번호 · 재설정) rather
 *    than writing a sentence — the same class of move `components/chrome/copy.ts`
 *    made for `© 미주알`, and flagged the same way for `P5.S19`.
 * 2. **A failure line for anything but the three signed cases.** `authErrorKo`
 *    maps 불일치 / 중복 가입 / 8자 미만 and returns `null` for every other
 *    structural code (`invalid_email`, `invalid_reset_token`, `csrf_required`, a
 *    network failure). A surface renders **no line** rather than a phrase nobody
 *    signed. See `authErrorKo` for what the panels do to keep those codes
 *    unreachable, and `P5.S15`'s `result.md` for the two that are not.
 * 3. **A third PII row.** R5's copy list says "PII 패널 3행" while R5-1 quotes
 *    two sentences and no more; the third row is on the card, which stays in the
 *    Claude Design project. Two signed lines render; nothing is invented to make
 *    up a count. `P5.S19` checks it against the card.
 */

// ---------------------------------------------------------------------------
// The one panel and its two modes (R5-1)
// ---------------------------------------------------------------------------

/** build-prompt §Auth: "로그인/계정 만들기는 한 패널 + 전환 링크". The two mode
 * names are the panel's title, its submit verb **and** the 전환 링크's label —
 * one word per mode, which is why the switch link needs no copy of its own. */
export const LOGIN_KO = "로그인";
export const SIGNUP_KO = "계정 만들기";

/** result.md §Proposed copy, Auth — the body line under each mode's title:
 * "가입한 이메일과 비밀번호로 로그인합니다." · "이메일과 비밀번호만으로 만듭니다 —
 * 만들어지면 바로 로그인됩니다." */
export const LOGIN_INTRO_KO = "가입한 이메일과 비밀번호로 로그인합니다.";
export const SIGNUP_INTRO_KO =
  "이메일과 비밀번호만으로 만듭니다 — 만들어지면 바로 로그인됩니다.";

/** The two field labels. R5-1 (개정) names exactly what the panel collects —
 * "가입/로그인 = **이메일+비밀번호**", restated in the PII line below — so these
 * are the round's own nouns for its own two fields, not new copy. */
export const EMAIL_LABEL_KO = "이메일";
export const PASSWORD_LABEL_KO = "비밀번호";

/** build-prompt §Auth: "idle → **확인 중**(버튼 텍스트 교체 + disabled, 스피너
 * 없음)", and result.md's copy list gives the literal with its ellipsis. The
 * button's own label is replaced by this while a request is in flight — there is
 * no spinner anywhere on this surface. */
export const PENDING_KO = "확인 중…";

/** R5-1: "로그아웃 즉시, 확인 다이얼로그 없음, "로그아웃되었습니다" 1회 표시."
 * The message belongs to whoever triggered the 로그아웃 (`P5.S16`'s account
 * menu); the channel that carries it one hop is `lib/session.ts`'s flash. */
export const LOGOUT_DONE_KO = "로그아웃되었습니다";

// ---------------------------------------------------------------------------
// The three signed failure lines (R5-1: "오류(본문 한 줄: 불일치/중복 가입/8자 미만)")
// ---------------------------------------------------------------------------

/** 불일치. R5-1: "로그인 오류는 **필드 특정 없음**" — and `P5.S7` made that
 * structural on the server too: a wrong password and an address with no account
 * are one `invalid_credentials`, at one cost. */
export const ERR_INVALID_CREDENTIALS_KO = "이메일 또는 비밀번호가 일치하지 않습니다.";

/** 중복 가입 — `email_taken`. */
export const ERR_EMAIL_TAKEN_KO = "이미 가입된 이메일입니다 — 로그인해 주세요.";

/** 8자 미만 — `password_too_short`. The rule is R5-1's "비밀번호 8자 이상(다른
 * 규칙 없음)"; `mijual.web.passwords.MIN_LENGTH` enforces it. */
export const ERR_PASSWORD_TOO_SHORT_KO = "비밀번호는 8자 이상이어야 합니다.";

/** The rule's own number, so the panel can state the signed line before spending
 * a round trip on a password it already knows is too short. It is the *server's*
 * rule (`mijual.web.passwords.MIN_LENGTH = 8`); this constant only lets the
 * client say the same thing sooner, and never lets it say anything else. */
export const MIN_PASSWORD_LENGTH = 8;

/**
 * `mijual.web` structural code → the signed body line, and **nothing else**.
 *
 * The API writes no failure copy by design (`P5.S1` note 1: the signed design
 * writes *state* copy, not error copy), so the Korean for a failure is this
 * surface's — which means the mapping is exactly as wide as the round's three
 * cases and no wider. An unmapped code returns `null` and the panel shows no
 * line, because the alternative is inventing a sentence.
 *
 * The two unmapped codes a reader could otherwise meet are held off structurally
 * instead of verbally: `invalid_email` by the field's own `type="email"` +
 * `pattern` (the browser refuses in **its** copy, not ours, exactly as the
 * framework's 404 does — `P5.S13` note 4), and `csrf_required` by
 * `lib/api.ts` setting the header on every mutation. `invalid_reset_token`
 * remains reachable — an expired or spent link — and is a recorded gap for
 * `P5.S19`/the operator, not a licence to write Korean for it.
 */
export function authErrorKo(code: string): string | null {
  switch (code) {
    case "invalid_credentials":
      return ERR_INVALID_CREDENTIALS_KO;
    case "email_taken":
      return ERR_EMAIL_TAKEN_KO;
    case "password_too_short":
      return ERR_PASSWORD_TOO_SHORT_KO;
    default:
      return null;
  }
}

// ---------------------------------------------------------------------------
// 재설정 (R5-1: "재설정 = 이메일 링크(가입 여부 비노출)")
// ---------------------------------------------------------------------------

/** The trigger's label — composed from the round's own two nouns, not written.
 * See this module's header, note 1. */
export const RESET_LINK_KO = "비밀번호 재설정";

/** result.md §Proposed copy, Auth. The answer is the **same** whether or not the
 * address has an account (R5-1: 가입 여부 비노출), which `P5.S7` already made
 * structural: `POST /auth/reset/request` answers `{"requested": true}` either
 * way and the link travels only through the mailer. */
export const RESET_SENT_KO = "재설정 링크를 보냈습니다 — 메일함을 확인해 주세요.";

// ---------------------------------------------------------------------------
// The PII inset (R5-1 개정, build-prompt §Auth: "PII 패널은 로그인 화면 상시 요소")
// ---------------------------------------------------------------------------

/** R5-1 verbatim: PII 패널 유지: "미주알이 받는 것: 이메일 주소와 비밀번호" +
 * "저장하지 않는 것은 유출되지 않습니다". Both lines are true by construction —
 * `security` fixes stored reader PII at email + password hash, and `P5.S7`'s
 * `account` table carries nothing else. */
export const PII_RECEIVES_KO = "미주알이 받는 것: 이메일 주소와 비밀번호";
export const PII_NOT_STORED_KO = "저장하지 않는 것은 유출되지 않습니다";

// ---------------------------------------------------------------------------
// 전환 제안 (R5-2)
// ---------------------------------------------------------------------------

/** result.md §Proposed copy, Convert — the offer panel's four lines, in the
 * order the round lists them. The first is R4's own constraint stated back to the
 * reader (조회 holdings live in `sessionStorage`, `lib/holding.ts`); the last is
 * the promise that the offer gates nothing. */
export const CONVERT_SESSION_KO = "이 보유량은 탭을 닫으면 사라집니다";
export const CONVERT_BODY_KO =
  "계정에 저장하면 마감이 다가올 때 이메일로 알립니다 — 계정은 이메일과 비밀번호뿐입니다.";
export const CONVERT_CTA_KO = "저장하고 알림 받기";
export const CONVERT_STAY_KO = "지금처럼 로그인 없이 계속 쓸 수 있습니다";

/** build-prompt §Conversion: "세션스토리지 플래그로 세션당 1회, **닫기 가능**,
 * 결과를 가리지 않음". The control's label is the round's own word. */
export const DISMISS_KO = "닫기";

/** R5-2's second placement: "상세 D-day 아래 한 줄 링크 (로그인 시 "내
 * 포트폴리오에 담기 →"로 교체)", with the anonymous literal in result.md's copy
 * list. One line, two states, and it gates nothing either way. */
export const DEADLINE_OFFER_KO = "이 마감 알림 받기 →";
export const PORTFOLIO_ADD_KO = "내 포트폴리오에 담기 →";

// ---------------------------------------------------------------------------
// 샘플 포트폴리오 (R5-4)
// ---------------------------------------------------------------------------

/** result.md §Proposed copy, Sample — the 로그인 page's entry and its subline.
 * build-prompt §Auth pins the placement: "샘플 진입 링크는 **하단 고정**".
 *
 * ⚠ The subline says **4건** and R5's own composition table pins four filings;
 * the live surface renders **five rows**, because 대동기어 also holds an
 * exposable ① that lapsed (`P5.S8` note 14 — live data, not a design deviation).
 * The sentence describes the composition, which is still four disclosures, and it
 * is signed copy either way: transcribed verbatim, flagged for `P5.S16`/`P5.S19`. */
export const SAMPLE_ENTRY_KO = "샘플 포트폴리오로 둘러보기";
export const SAMPLE_ENTRY_SUB_KO =
  "가입 없이, 실제 공시 4건으로 구성된 예시 포트폴리오를 엽니다 — 클릭 한 번.";

/** The other signed placement — R5-4: "진입: 로그인 페이지 하단 + **랜딩 푸터**",
 * with result.md's literal line. It lands at the foot of the landing *page*, not
 * in the global footer: R5's chrome section says "Footer 불변" and its signoff
 * records the round as extending only the account slot, so the sample entry is a
 * landing/sample element (`P5.S11` note 11). */
export const SAMPLE_LANDING_KO = "내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →";
