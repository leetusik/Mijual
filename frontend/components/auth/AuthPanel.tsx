"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { CraftPanel } from "@/components";
import { clearMirror } from "@/components/chrome";
import {
  ApiError,
  login,
  requestPasswordReset,
  resendVerification,
  signup,
  verifySignup,
} from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import { readFlashOnce } from "@/lib/session";
import {
  EMAIL_LABEL_KO,
  ERR_CODE_FORMAT_KO,
  ERR_FIELDS_REQUIRED_KO,
  ERR_INVALID_EMAIL_KO,
  ERR_PASSWORD_TOO_SHORT_KO,
  LOGIN_INTRO_KO,
  LOGIN_KO,
  LOGOUT_DONE_KO,
  MIN_PASSWORD_LENGTH,
  PASSWORD_LABEL_KO,
  PASSWORD_RULE_KO,
  PENDING_KO,
  RESEND_KO,
  RESET_LINK_KO,
  RESET_SENT_KO,
  SIGNUP_INTRO_KO,
  SIGNUP_KO,
  VERIFY_CODE_LABEL_KO,
  VERIFY_CODE_STILL_VALID_KO,
  VERIFY_KO,
  VERIFY_RESENT_KO,
  VERIFY_SUBMIT_KO,
  authErrorKo,
  verifyIntroKo,
} from "./copy";
import { AuthRail } from "./AuthRail";
import { SampleEntry } from "./SampleEntry";
import styles from "./Auth.module.css";

/**
 * 로그인 / 계정 만들기 — **one panel, two modes** (R5-1, re-cut by **R12**), plus
 * the 이메일 인증 state both of them can end in (**P13**).
 *
 * > 이메일+비밀번호 (개정). 로그인/계정 만들기는 한 패널 + 전환 링크; 비밀번호 8자
 * > 이상(다른 규칙 없음); 재설정 = 이메일 링크(가입 여부 비노출). 저장 PII =
 * > 이메일 + 비밀번호 해시.
 * >
 * > States: idle → 확인 중(버튼 텍스트 교체 + disabled, 스피너 없음) → 오류(본문
 * > 한 줄: 불일치/중복 가입/8자 미만 — 로그인 오류는 필드 특정 없음) → 로그인됨.
 *
 * ## The four states, and what each one is made of
 *
 * **idle** is the panel as rendered. **확인 중** is the submit button's own label
 * replaced and the button disabled — there is no spinner on this surface and no
 * overlay anywhere, because the state *is* the text; the quiet row is disabled
 * with it, because neither of its two actions can be taken while one is in
 * flight. **오류** and **알림** share one `p role="status"` slot under the form,
 * separated by weight rather than by hue (`--ink-1` / `--ink-2`) — `--alert`
 * never appears on this layer, and a login error never names a field (`P5.S7`
 * made that structural too: a wrong password and an address with no account are
 * one code, at one cost). **로그인됨** is not a state of this panel at all — it is
 * 보유 종목, so a success navigates there and the button stays disabled until it
 * does.
 *
 * ## R12: the browser stopped speaking English here (Q-A = b)
 *
 * The inputs used to carry `required` + `pattern` so the *browser* refused a bad
 * value in its own copy — which on a Korean-only product meant an English bubble,
 * and on 계정 만들기 an empty address that reached `invalid_email`, a code with no
 * signed Korean, so the submit answered nothing at all. The form now carries
 * `noValidate`, the two attributes are gone (`type` and `autoComplete` stay), and
 * the gating runs **in the round's order** before any request:
 *
 * 1. either field empty → `ERR_FIELDS_REQUIRED_KO`;
 * 2. the address fails `EMAIL_RE` → `ERR_INVALID_EMAIL_KO`;
 * 3. 계정 만들기 with a password under 8 → `ERR_PASSWORD_TOO_SHORT_KO`;
 * 4. otherwise POST, and an `ApiError` renders `authErrorKo(code)`.
 *
 * `EMAIL_RE` is the round's own expression and mirrors the server's
 * `mijual.web.auth._EMAIL_RE`: the client states the same rule one round trip
 * sooner and never states a different one. Same reading as the 8자 rule, which is
 * `mijual.web.passwords.MIN_LENGTH` and is checked here **only** on 계정 만들기 —
 * on 로그인 a short password is not a rule violation but a wrong password, and the
 * server answers 불일치 exactly as the round requires.
 *
 * ## 재설정 is never a dead control (R12 finding 1)
 *
 * It used to be `disabled` whenever the address was empty — a grey label that did
 * nothing for the one reader who needed it most. Pressing it with no address now
 * **focuses the email field** and sends nothing: R11's own grammar (a prompt that
 * points at the input it needs) rather than a new sentence. `disabled` exists
 * only while a request is in flight.
 *
 * ## 로그아웃되었습니다 is a band above the title (R12 finding 10)
 *
 * The line under the form is where *this* form's answers stand, so a receipt for
 * an action taken on another surface would read there as the response to a submit
 * that never happened. It renders above the `h1`, with no timer, and is cleared by
 * the first change of either field, by a submit, or by navigating away (the flash
 * channel already guarantees it shows once).
 *
 * **It no longer lands after the page has painted (`P12.F5`).** Whether that band
 * exists is a fact only the browser holds — `sessionStorage["mijual.auth.flash"]`,
 * written by 로그아웃 on another surface — so it used to be *inserted* by this
 * component's mount effect, +27 ms after first paint, pushing the form and the
 * sample entry down **56.6 px** (`P12.R1` F4). The pre-hydration mirror
 * (`components/chrome/PreHydration.tsx`) now reads that key in the `<head>` and
 * stamps `data-mj-auth-flash="logout"` on `<html>` before the body is parsed, and
 * `Auth.module.css` holds the band's exact height in an **empty slot** until this
 * effect fills it. The line is therefore *filled into* a box that is already the
 * right size instead of being inserted into a painted page — same copy, same
 * style, same `role`, nothing moves.
 *
 * The channel itself is untouched: the `<head>` script only *reads* the key, and
 * `readFlashOnce()` below is still the one consumer, still clearing at the same
 * moment. `flashResolved` exists so the stamp is released after the commit that
 * settles the band either way — a reservation left standing would become a
 * permanent gap the moment the reader types and the band leaves.
 *
 * ## P13: 이메일 인증 is a third mode, not a fourth page
 *
 * The mailbox gate gave 가입 an ending it did not have: `POST /auth/signup` now
 * creates the account, mails a 6자리 인증번호 and **opens no session at all**
 * (`P13.S1`), so the reader is one number short of being logged in. 로그인 with the
 * correct password on an unverified account answers the identical `verification`
 * block instead of a cookie, so **both** ways in end in the same place — which is
 * why this is one state and not two.
 *
 * **It is a state of this panel, not a route.** There is no `/auth/verify` page,
 * no modal and no overlay: the reader is mid-가입 on the surface they started on,
 * and navigating would put a URL in their history that answers nothing when
 * reloaded (the state is held in this component and nowhere else — a reload
 * legitimately returns to 로그인, from which the correct password brings the code
 * step straight back). R5-1's own rule stands: 로그인됨 is 보유 종목, and only a
 * *session* is worth a navigation.
 *
 * **What the state is made of.** The title 이메일 인증; one body line naming the
 * **normalized** address the API returned and the 10분 window; one field
 * (`inputMode="numeric"`, `autoComplete="one-time-code"`, `maxLength=6`, and a
 * **string** value so 「012345」 survives — the code keeps its leading zeros from
 * `new_code` all the way to this comparison); the submit 확인, which swaps to
 * `PENDING_KO` and disables exactly as the other two modes do; and the quiet row
 * carrying 인증번호 재전송 beside the way back, whose label is the origin mode's
 * own name. The line slot below the form is the same one slot, with the same two
 * weights: 불일치 and 만료·시도 초과 are 오류, 재전송됨 and 「아직 유효합니다」 are
 * 알림, and `--alert` still never appears on this layer.
 *
 * **The password travels with the code**, which is why `email` and `password`
 * stay in state through the transition instead of being cleared. `POST
 * /auth/verify` checks the password **first** and only then the code (`P13.S1`),
 * and that ordering is load-bearing: 가입 on an address that is still unverified
 * *replaces* the stored password hash, so without it a stranger could sit on a
 * half-finished signup and be logged in by the code the mailbox's owner types.
 * The one who verifies is the one who chose the password. It also means
 * `invalid_credentials` is reachable from this state — the panel answers it with
 * the round's own 불일치 line, since `authErrorKo` maps it already.
 *
 * **Two live behaviours the state is built around** (`P13.S1`): the **fifth**
 * wrong number answers `verification_code_expired`, not `..._invalid`, because
 * the attempt that reaches the cap kills the grant — so that reader is pointed at
 * 재전송; and `resent: false` is the 60-second cooldown rather than a failure, so
 * it takes a 알림 line saying the number already mailed still works, with no timer
 * drawn for it. A malformed code costs one of the five attempts on the server,
 * which is why an empty or short value is answered **here**, before any request.
 *
 * ## What this panel refuses to do
 *
 * It renders no line for a code no round has signed (`authErrorKo` returns
 * `null`), it stores nothing, and it sends nothing anywhere but the four
 * `/auth/*` endpoints. The PII inset R5-1 made a 상시 요소 of this screen was
 * **withdrawn by the operator in the R12 session** and is gone from both auth
 * pages.
 */

/** R12 §2's own expression, mirroring `mijual.web.auth._EMAIL_RE`. */
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

type Line = { text: string; soft: boolean } | null;

/** The 6자리 인증번호, stated once. The server's own shape (`new_code`: six
 * digits, leading zeros kept), checked here only so a slip never spends one of
 * the five attempts. */
const CODE_RE = /^[0-9]{6}$/;

export function AuthPanel() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup" | "verify">("login");
  /** Where the reader entered 이메일 인증 from — 가입, or 로그인 on an account
   * that never finished one. The state itself is identical either way; the origin
   * only decides which mode the way back returns to and which intro they left. */
  const [origin, setOrigin] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [pending, setPending] = useState(false);
  const [line, setLine] = useState<Line>(null);
  const [flash, setFlash] = useState(false);
  const [flashResolved, setFlashResolved] = useState(false);
  const emailRef = useRef<HTMLInputElement>(null);
  const codeRef = useRef<HTMLInputElement>(null);

  // "로그아웃되었습니다" — 1회 표시. The click happened on another surface
  // (`P5.S16`'s account menu); this reads the one-hop channel and clears it, so a
  // reload never shows it twice.
  //
  // `setFlash(true)` rather than `setFlash(read === "logout")` on purpose: Strict
  // Mode runs this effect twice in `next dev`, and the second run reads a channel
  // the first run already consumed — assigning the second answer would blank a
  // band the reader is meant to see. (`P12.F5`; the shape predates it and is kept.)
  useEffect(() => {
    if (readFlashOnce() === "logout") setFlash(true);
    setFlashResolved(true);
  }, []);

  // The reservation is a **pre-hydration** device, so it is released as soon as
  // this panel owns the answer — after the commit that renders the band, not
  // inside the effect that reads the key (`P12.F4`'s rule). Both `setState`s above
  // land in one commit, so by the time this runs the band is on screen if it is
  // coming at all; dropping the stamp then is what gives the box back when the
  // reader's first keystroke retires the band.
  useEffect(() => {
    if (flashResolved) clearMirror("auth-flash");
  }, [flashResolved]);

  const signingUp = mode === "signup";
  const verifying = mode === "verify";
  const modeLabel = signingUp ? SIGNUP_KO : LOGIN_KO;
  const title = verifying ? VERIFY_KO : modeLabel;
  const submitLabel = verifying ? VERIFY_SUBMIT_KO : modeLabel;

  // The one field of the 인증 state takes the caret, because it is the only thing
  // the reader can do here and they arrived by pressing a button elsewhere on the
  // panel. Focusing on the *transition* rather than in each handler keeps the two
  // routes in (가입, 로그인) from having to remember it separately.
  useEffect(() => {
    if (mode === "verify") codeRef.current?.focus();
  }, [mode]);

  /** Every entry into the slot goes through here, and every one of them also
   * retires the logout band: the reader has acted since. */
  function say(text: string | null, soft = false) {
    setFlash(false);
    setLine(text === null ? null : { text, soft });
  }

  /** 로그인됨 = 보유 종목. `refresh()` re-runs the server components that read the
   * session, so the chrome and any gated page see the new cookie. All three ways
   * to a session — 로그인, and 확인 from either origin — land here, and the origin
   * is not carried (R12 Q-B). `pending` is deliberately left standing: the button
   * stays disabled until the navigation happens. */
  function landSignedIn() {
    router.push(ROUTES.portfolio);
    router.refresh();
  }

  /** Enter 이메일 인증. The address becomes the **normalized** one the API just
   * returned (never the string that was typed), the password stays — `/auth/verify`
   * checks it before the code — and the number field starts empty. */
  function enterVerify(from: "login" | "signup", verifiedEmail: string) {
    setOrigin(from);
    setEmail(verifiedEmail);
    setCode("");
    setMode("verify");
    say(null);
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (verifying) {
      await submitCode();
      return;
    }

    // The round's order, before any request leaves (R12 §2).
    if (email.trim() === "" || password === "") {
      say(ERR_FIELDS_REQUIRED_KO);
      return;
    }
    if (!EMAIL_RE.test(email.trim())) {
      say(ERR_INVALID_EMAIL_KO);
      return;
    }
    // 8자 미만 — 계정 만들기 only. On 로그인 a short password is simply wrong,
    // and the round's own line for that is 불일치.
    if (signingUp && password.length < MIN_PASSWORD_LENGTH) {
      say(ERR_PASSWORD_TOO_SHORT_KO);
      return;
    }

    say(null);
    setPending(true);
    try {
      const result = signingUp ? await signup(email, password) : await login(email, password);
      // Which answer arrived is a question about the **key**, never the status:
      // 가입 is a 201 and an unverified 로그인 a plain 200, and both carry the
      // 인증 block instead of an account (`P13.S1`).
      if ("verification" in result) {
        enterVerify(signingUp ? "signup" : "login", result.verification.email);
        setPending(false);
        return;
      }
      landSignedIn();
    } catch (failure) {
      say(failure instanceof ApiError ? authErrorKo(failure.code) : null);
      setPending(false);
    }
  }

  /** 확인 — the 인증 state's own submit. */
  async function submitCode() {
    // Six digits or nothing, answered before the request: on the server a
    // malformed value is simply a wrong code and costs one of the five attempts
    // (`P13.S1`), so a slip of the finger must not reach it.
    if (!CODE_RE.test(code.trim())) {
      say(ERR_CODE_FORMAT_KO);
      return;
    }

    say(null);
    setPending(true);
    try {
      await verifySignup(email, password, code.trim());
      // 확인 opens the session itself (`/auth/verify` sets the cookie), so this is
      // the same landing 로그인 has and not a return to the panel.
      landSignedIn();
    } catch (failure) {
      // `invalid_credentials` is reachable here — a second 가입 elsewhere replaces
      // an unverified account's password hash — and `authErrorKo` already answers
      // it with the round's 불일치 line.
      say(failure instanceof ApiError ? authErrorKo(failure.code) : null);
      setPending(false);
    }
  }

  /** 인증번호 재전송. `resent: false` is the 60-second cooldown and not a failure,
   * so both answers are 알림 (soft): either a new number is on its way, or the one
   * already mailed is still the one to type. No timer is drawn for it. */
  async function onResend() {
    say(null);
    setPending(true);
    try {
      const { resent } = await resendVerification(email, password);
      setPending(false);
      say(resent ? VERIFY_RESENT_KO : VERIFY_CODE_STILL_VALID_KO, true);
    } catch (failure) {
      say(failure instanceof ApiError ? authErrorKo(failure.code) : null);
      setPending(false);
    }
  }

  /** The way back out of 인증, to the mode the reader came from. The two fields
   * are kept — the account exists and the password is the one that was just
   * accepted, so re-typing either would be ceremony — and the line is cleared,
   * because it answered a submit on a form that is no longer on screen. */
  function leaveVerify() {
    setMode(origin);
    say(null);
  }

  async function onReset() {
    // No address: point at what is needed instead of asking about nothing
    // (R12 finding 1). No request, no line.
    if (email.trim() === "") {
      emailRef.current?.focus();
      return;
    }

    say(null);
    setPending(true);
    try {
      await requestPasswordReset(email);
    } catch {
      // 가입 여부 비노출: the endpoint answers identically for a known and an
      // unknown address, so the reader is told the same thing either way — and a
      // transport failure must not become a hint about the address.
    }
    setPending(false);
    say(RESET_SENT_KO, true);
  }

  return (
    <main className={`content ${styles.page}`}>
      <AuthRail />

      <CraftPanel className={styles.panel}>
        {/* 이전 행동의 영수증 — 제목 위 자기 밴드, 타이머 없음 (R12 finding 10).
            The band's **slot** (`P12.F5`): `display: contents`, so a filled slot
            lays the `<p>` out as a direct `.panel` grid item exactly as an
            unwrapped one did, and an empty slot with no stamp is not a grid item
            at all and takes not even a gap — the login page of a reader who did
            not just log out is byte-identical. An empty slot **under the stamp**
            is the pre-hydration window, and `Auth.module.css` gives it the band's
            measured height there. */}
        <div className={styles.flashSlot}>
          {flash ? (
            <p className={styles.flash} role="status">
              {LOGOUT_DONE_KO}
            </p>
          ) : null}
        </div>

        <div className={styles.head}>
          <h1 className={styles.title}>{title}</h1>
          {/* 인증 상태의 본문 한 줄은 API가 돌려준 **정규화된** 주소를 말한다 (P13). */}
          <p className={styles.intro}>
            {verifying ? verifyIntroKo(email) : signingUp ? SIGNUP_INTRO_KO : LOGIN_INTRO_KO}
          </p>
        </div>

        {/* noValidate: the browser says nothing, the slot below says it in Korean. */}
        {/* Stamped by extensions before hydration — see `SearchRow.tsx`. */}
        <form className={styles.form} noValidate onSubmit={onSubmit} suppressHydrationWarning>
          {verifying ? (
            /* 인증 상태는 필드 하나다 — 주소도 비밀번호도 이미 있고, 다시 묻는
               것은 방금 한 일을 되묻는 것이다 (`ResetConfirmPanel`의 같은 판단).
               `type="text"` + `inputMode="numeric"`: number 필드는 스피너와
               스크롤 증감을 달고 오고 앞자리 0을 지우는데, 코드는 셈하는 값이
               아니라 여섯 글자다. */
            <div className={styles.field}>
              <div className={styles.labelRow}>
                <label className={styles.label} htmlFor="auth-code">
                  {VERIFY_CODE_LABEL_KO}
                </label>
              </div>
              <input
                suppressHydrationWarning
                id="auth-code"
                ref={codeRef}
                className={`${styles.input} ${styles.code}`}
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                value={code}
                onChange={(event) => {
                  setCode(event.target.value);
                  say(null);
                }}
              />
            </div>
          ) : (
            <>
              <div className={styles.field}>
                <div className={styles.labelRow}>
                  <label className={styles.label} htmlFor="auth-email">
                    {EMAIL_LABEL_KO}
                  </label>
                </div>
                <input
                  suppressHydrationWarning
                  id="auth-email"
                  ref={emailRef}
                  className={styles.input}
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => {
                    setEmail(event.target.value);
                    say(null);
                  }}
                />
              </div>

              <div className={styles.field}>
                <div className={styles.labelRow}>
                  <label className={styles.label} htmlFor="auth-password">
                    {PASSWORD_LABEL_KO}
                  </label>
                  {/* 규칙을 앞에 (R12 Q-C) — 계정 만들기에만. 로그인에서 길이는 규칙이
                      아니라 틀린 비밀번호다. */}
                  {signingUp ? <span className={styles.rule}>{PASSWORD_RULE_KO}</span> : null}
                </div>
                <input
                  suppressHydrationWarning
                  id="auth-password"
                  className={styles.input}
                  type="password"
                  autoComplete={signingUp ? "new-password" : "current-password"}
                  value={password}
                  onChange={(event) => {
                    setPassword(event.target.value);
                    say(null);
                  }}
                />
              </div>
            </>
          )}

          <button className={styles.submit} type="submit" disabled={pending}>
            {pending ? PENDING_KO : submitLabel}
          </button>
        </form>

        {/* One slot, one live region: 오류 ink-1 · 알림 ink-2 (R5-1, R12 §2). */}
        {line ? (
          <p
            className={line.soft ? `${styles.line} ${styles.soft}` : styles.line}
            role="status"
          >
            {line.text}
          </p>
        ) : null}

        <div className={styles.quietRow}>
          {verifying ? (
            <>
              {/* 인증번호 재전송 — 쿨다운 안이면 「아직 유효합니다」로 답한다. */}
              <button
                className={styles.quiet}
                type="button"
                disabled={pending}
                onClick={onResend}
              >
                {RESEND_KO}
              </button>

              {/* The way back wears the origin mode's **own name**, which is the
                  전환 링크's rule applied to a return instead of a switch — so the
                  state needs no 취소 copy of its own. */}
              <button
                className={styles.quiet}
                type="button"
                disabled={pending}
                onClick={leaveVerify}
              >
                {origin === "signup" ? SIGNUP_KO : LOGIN_KO}
              </button>
            </>
          ) : (
            <>
              {/* The 전환 링크: its label is the other mode's own name, so switching
                  needs no copy of its own. */}
              <button
                className={styles.quiet}
                type="button"
                disabled={pending}
                onClick={() => {
                  setMode(signingUp ? "login" : "signup");
                  say(null);
                }}
              >
                {signingUp ? LOGIN_KO : SIGNUP_KO}
              </button>

              {/* 재설정 is a 로그인 affordance: there is nothing to reset from the
                  계정 만들기 side. Alive without an address — pressing it then points
                  at the field it needs (R12 finding 1). */}
              {signingUp ? null : (
                <button
                  className={styles.quiet}
                  type="button"
                  disabled={pending}
                  onClick={onReset}
                >
                  {RESET_LINK_KO}
                </button>
              )}
            </>
          )}
        </div>
      </CraftPanel>

      {/* 하단 고정 (R5-1's own words for this page's sample entry). */}
      <SampleEntry />
    </main>
  );
}
