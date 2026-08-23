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
 * 3. **A third PII row.** Moot since **R12**: the PII inset itself is gone (the
 *    operator struck both of its lines in the R12 session, 2026-08-24), so the
 *    count R5's copy list wrote has nothing left to describe. See the note where
 *    the two constants used to stand.
 *
 * ## R12 (2026-08-24) — four new strings, three deletions, one shortened body
 *
 * The auth surfaces' polish round is the first to add copy here since R5. Its
 * four new constants are the round's own dated exceptions (`build-prompt.md` §5,
 * `account/r12-parts.jsx`): the field rule 「8자 이상」 and three lines that fill
 * **recorded blanks** — a submit that used to answer nothing (empty fields,
 * a malformed address) and an expired reset link that used to answer nothing.
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
 * "가입/로그인 = **이메일+비밀번호**" — so these are the round's own nouns for its
 * own two fields, not new copy. (The PII inset that used to restate the same pair
 * on screen was withdrawn by R12; see below.) */
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

/** The same rule, stated **before** the reader spends a submit on it (R12 Q-C =
 * yes; `build-prompt.md` §5, card `account/Auth.html`). One token, mono, on the
 * 비밀번호 label row — R5-1's own rule text ("비밀번호 8자 이상(다른 규칙 없음)")
 * and not a sentence. It renders on 계정 만들기 and the 재설정 page only: on
 * 로그인 a short password is not a rule violation but a wrong password, and a
 * rule stated there would claim a check that screen does not run. */
export const PASSWORD_RULE_KO = "8자 이상";

/** R12 Q-A = (b) — the form now carries `noValidate`, so the browser's English
 * bubble is gone and these two lines answer in the slot the round already owns.
 * The handoff's default (c) — "let the existing Korean API errors answer" — was
 * rejected in session for a measured reason: on 계정 만들기 an empty address maps
 * to `invalid_email`, which had no signed Korean, so the reader met a submit that
 * did nothing at all. 빈 입력 and 형식 오류 are different facts, so they are two
 * lines. (`build-prompt.md` §2/§5.) */
export const ERR_FIELDS_REQUIRED_KO = "이메일과 비밀번호를 입력해 주세요.";
export const ERR_INVALID_EMAIL_KO = "이메일 주소 형식이 올바르지 않습니다.";

/** The line for `invalid_reset_token` — an expired or already-spent link, which
 * until R12 answered with **no line at all** (see `authErrorKo`'s note below and
 * `ResetConfirmPanel`'s header). It does not say *which* of the two happened:
 * not distinguishing 만료 from 사용됨 is the token state staying unexposed, the
 * same rule the 가입 여부 비노출 answer keeps. (R12 finding 3, `build-prompt.md`
 * §3/§5, card `account/Reset.html`.) */
export const ERR_RESET_TOKEN_KO =
  "이 재설정 링크는 만료되었거나 이미 사용되었습니다 — 새 링크를 요청해 주세요.";

/**
 * `mijual.web` structural code → the signed body line, and **nothing else**.
 *
 * The API writes no failure copy by design (`P5.S1` note 1: the signed design
 * writes *state* copy, not error copy), so the Korean for a failure is this
 * surface's — which means the mapping is exactly as wide as what a round has
 * signed and no wider. An unmapped code returns `null` and the panel shows no
 * line, because the alternative is inventing a sentence.
 *
 * **R12 closed two of the three recorded gaps.** `invalid_email` used to be held
 * off structurally, by the field's own `type="email"` + `pattern` (the browser
 * refusing in **its** copy, not ours) — R12 Q-A retired that trade: the inputs
 * carry `noValidate` and no `pattern`, and the code has a signed Korean line.
 * `invalid_reset_token` used to be reachable with no line at all; it now has one,
 * and the reset page additionally offers the way back to where a fresh link is
 * requested.
 *
 * **Two stay unmapped, by design.** `csrf_required` is held off by `lib/api.ts`
 * setting the header on every mutation — a reader who meets it is in a state no
 * sentence of ours can improve — and a transport failure is not a structural code
 * at all (no `ApiError`, so nothing to map). Neither is a licence to write Korean
 * for it.
 */
export function authErrorKo(code: string): string | null {
  switch (code) {
    case "invalid_credentials":
      return ERR_INVALID_CREDENTIALS_KO;
    case "email_taken":
      return ERR_EMAIL_TAKEN_KO;
    case "password_too_short":
      return ERR_PASSWORD_TOO_SHORT_KO;
    case "invalid_email":
      return ERR_INVALID_EMAIL_KO;
    case "invalid_reset_token":
      return ERR_RESET_TOKEN_KO;
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

/* ---------------------------------------------------------------------------
   The PII inset — **withdrawn by R12** (operator instruction, 2026-08-24)
   ---------------------------------------------------------------------------

   R5-1 made the two-line PII panel a 상시 요소 of the login screen ("PII 패널은
   로그인 화면 상시 요소 (inset)"), and `security` restated it as a boundary
   rather than as copy. **That clause is withdrawn.** In the R12 session the
   operator struck both lines — 「미주알이 받는 것: 이메일 주소와 비밀번호」 and
   「저장하지 않는 것은 유출되지 않습니다」 — from both auth pages; `PiiInset.tsx`
   and its two constants are deleted with them (R12 `build-prompt.md` §1/§5, card
   `account/Auth.html` note 「PII inset 삭제」).

   What was true stays true — `P5.S7`'s `account` table is still
   `id · email · password_hash · created_at · updated_at` and nothing else — it is
   simply no longer asserted on the screen. The canon keeps the `.pii*` geometry
   unused so the tier does not have to be re-decided if the statement ever comes
   back; the product renders nothing for it.
   --------------------------------------------------------------------------- */

// ---------------------------------------------------------------------------
// 전환 제안 (R5-2)
// ---------------------------------------------------------------------------

/** result.md §Proposed copy, Convert — the offer's lines, in the order the round
 * lists them. The first is R4's own constraint stated back to the reader (조회
 * holdings live in `sessionStorage`, `lib/holding.ts`).
 *
 * ⚠ **R12 shortened this set** (operator instruction, 2026-08-24; `build-prompt`
 * §4/§5, card `account/Offers.html`). The closing reassurance 「지금처럼 로그인
 * 없이 계속 쓸 수 있습니다」 is **deleted**, and `CONVERT_BODY_KO` loses its
 * trailing clause 「— 계정은 이메일과 비밀번호뿐입니다.」. The reason the round
 * gives: that the offer is not a gate is said by what it *does* — 닫기, once per
 * session, every anonymous path unchanged — not by a sentence promising it. The
 * band is three things now: the session line, one body line and the CTA. */
export const CONVERT_SESSION_KO = "이 보유량은 탭을 닫으면 사라집니다";
export const CONVERT_BODY_KO = "계정에 저장하면 마감이 다가올 때 이메일로 알립니다.";
export const CONVERT_CTA_KO = "저장하고 알림 받기";

/** build-prompt §Conversion: "세션스토리지 플래그로 세션당 1회, **닫기 가능**,
 * 결과를 가리지 않음". The control's label is the round's own word. */
export const DISMISS_KO = "닫기";

/** R5-2's second placement: "상세 D-day 아래 한 줄 링크 (로그인 시 "내
 * 포트폴리오에 담기 →"로 교체)", with the anonymous literal in result.md's copy
 * list. One line, two states, and it gates nothing either way.
 *
 * ⚠ The signed-in label is **R10's**, and it supersedes R5-2's: 「보유 종목에
 * 담기 →」 (SIGNOFF R10, an in-session operator direction — 「포트폴리오」 was
 * retired by R8 and the line now matches the nav's own noun, 보유 종목). The
 * constant keeps its name because the destination did not change; only the words
 * did. The anonymous line is R5-2's, untouched. */
export const DEADLINE_OFFER_KO = "이 마감 알림 받기 →";
export const PORTFOLIO_ADD_KO = "보유 종목에 담기 →";

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

/* R5-4's second placement — the landing line 「내 포트폴리오는 어떻게 보이나 —
 * 샘플로 열어보기 →」 — is **retired by R8** (build-prompt §1: "랜딩의 … 링크와 그
 * 빈 밴드 제거"), so its constant is gone from this file. The destination did not
 * disappear with it: the nav's 보유 종목 slot opens the same sample for anyone
 * without a session, which is what made the line redundant. */
