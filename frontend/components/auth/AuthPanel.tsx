"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { CraftPanel } from "@/components";
import { ApiError, login, requestPasswordReset, signup } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import { readFlashOnce } from "@/lib/session";
import {
  EMAIL_LABEL_KO,
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
  RESET_LINK_KO,
  RESET_SENT_KO,
  SIGNUP_INTRO_KO,
  SIGNUP_KO,
  authErrorKo,
} from "./copy";
import { AuthRail } from "./AuthRail";
import { SampleEntry } from "./SampleEntry";
import styles from "./Auth.module.css";

/**
 * 로그인 / 계정 만들기 — **one panel, two modes** (R5-1, re-cut by **R12**).
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

export function AuthPanel() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [line, setLine] = useState<Line>(null);
  const [flash, setFlash] = useState(false);
  const emailRef = useRef<HTMLInputElement>(null);

  // "로그아웃되었습니다" — 1회 표시. The click happened on another surface
  // (`P5.S16`'s account menu); this reads the one-hop channel and clears it, so a
  // reload never shows it twice.
  useEffect(() => {
    if (readFlashOnce() === "logout") setFlash(true);
  }, []);

  const signingUp = mode === "signup";
  const submitLabel = signingUp ? SIGNUP_KO : LOGIN_KO;

  /** Every entry into the slot goes through here, and every one of them also
   * retires the logout band: the reader has acted since. */
  function say(text: string | null, soft = false) {
    setFlash(false);
    setLine(text === null ? null : { text, soft });
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

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
      if (signingUp) {
        await signup(email, password);
      } else {
        await login(email, password);
      }
      // 로그인됨 = 보유 종목. `refresh()` re-runs the server components that read
      // the session, so the chrome and any gated page see the new cookie. Every
      // login lands here, and the origin is not carried (R12 Q-B).
      router.push(ROUTES.portfolio);
      router.refresh();
    } catch (failure) {
      say(failure instanceof ApiError ? authErrorKo(failure.code) : null);
      setPending(false);
    }
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
        {/* 이전 행동의 영수증 — 제목 위 자기 밴드, 타이머 없음 (R12 finding 10). */}
        {flash ? (
          <p className={styles.flash} role="status">
            {LOGOUT_DONE_KO}
          </p>
        ) : null}

        <div className={styles.head}>
          <h1 className={styles.title}>{submitLabel}</h1>
          <p className={styles.intro}>{signingUp ? SIGNUP_INTRO_KO : LOGIN_INTRO_KO}</p>
        </div>

        {/* noValidate: the browser says nothing, the slot below says it in Korean. */}
        <form className={styles.form} noValidate onSubmit={onSubmit}>
          <div className={styles.field}>
            <div className={styles.labelRow}>
              <label className={styles.label} htmlFor="auth-email">
                {EMAIL_LABEL_KO}
              </label>
            </div>
            <input
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
        </div>
      </CraftPanel>

      {/* 하단 고정 (R5-1's own words for this page's sample entry). */}
      <SampleEntry />
    </main>
  );
}
