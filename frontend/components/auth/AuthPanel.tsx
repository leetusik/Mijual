"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CraftPanel } from "@/components";
import { ApiError, login, requestPasswordReset, signup } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import { readFlashOnce } from "@/lib/session";
import {
  EMAIL_LABEL_KO,
  ERR_PASSWORD_TOO_SHORT_KO,
  LOGIN_INTRO_KO,
  LOGIN_KO,
  LOGOUT_DONE_KO,
  MIN_PASSWORD_LENGTH,
  PASSWORD_LABEL_KO,
  PENDING_KO,
  RESET_LINK_KO,
  RESET_SENT_KO,
  SIGNUP_INTRO_KO,
  SIGNUP_KO,
  authErrorKo,
} from "./copy";
import { PiiInset } from "./PiiInset";
import { SampleEntry } from "./SampleEntry";
import styles from "./Auth.module.css";

/**
 * 로그인 / 계정 만들기 — **one panel, two modes** (R5-1).
 *
 * > 이메일+비밀번호 (개정). 로그인/계정 만들기는 한 패널 + 전환 링크; 비밀번호 8자
 * > 이상(다른 규칙 없음); 재설정 = 이메일 링크(가입 여부 비노출). 저장 PII =
 * > 이메일 + 비밀번호 해시.
 * >
 * > States: idle → 확인 중(버튼 텍스트 교체 + disabled, 스피너 없음) → 오류(본문
 * > 한 줄: 불일치/중복 가입/8자 미만 — 로그인 오류는 필드 특정 없음) → 로그인됨.
 * >
 * > PII 패널은 로그인 화면 상시 요소 (inset), 샘플 진입 링크는 하단 고정.
 *
 * ## The four states, and what each one is made of
 *
 * **idle** is the panel as rendered. **확인 중** is the submit button's own label
 * replaced and the button disabled — there is no spinner on this surface and no
 * overlay anywhere, because the state *is* the text. **오류** is one body line
 * under the form, mapped from the API's structural code by `authErrorKo` and
 * never naming a field on a login (`P5.S7` made that structural too: a wrong
 * password and an address with no account are one code, at one cost).
 * **로그인됨** is not a state of this panel at all — it is 내 포트폴리오, so a
 * success navigates there and the button stays disabled until it does.
 *
 * ## Why the 8자 rule is checked here as well as on the server
 *
 * `mijual.web.passwords.MIN_LENGTH` is the rule and this is not a second copy of
 * it: the client states the **same signed line** the server's
 * `password_too_short` maps to, one round trip sooner, and only on 계정 만들기.
 * On 로그인 a short password is not a rule violation — it is a wrong password,
 * and the server answers 불일치 exactly as the round requires.
 *
 * ## What this panel refuses to do
 *
 * It renders no line for a code the round did not sign (`authErrorKo` returns
 * `null`), it stores nothing, and it sends nothing anywhere but the four
 * `/auth/*` endpoints. The email field's `type` + `pattern` mirror the server's
 * own acceptance rule, so `invalid_email` — which has no signed Korean — is
 * refused by the browser in the browser's own words instead.
 */
export function AuthPanel() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // "로그아웃되었습니다" — 1회 표시. The click happened on another surface
  // (`P5.S16`'s account menu); this reads the one-hop channel and clears it, so a
  // reload never shows it twice.
  useEffect(() => {
    if (readFlashOnce() === "logout") setNotice(LOGOUT_DONE_KO);
  }, []);

  const signingUp = mode === "signup";
  const submitLabel = signingUp ? SIGNUP_KO : LOGIN_KO;

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setNotice(null);

    // 8자 미만 — 계정 만들기 only. On 로그인 a short password is simply wrong,
    // and the round's own line for that is 불일치.
    if (signingUp && password.length < MIN_PASSWORD_LENGTH) {
      setError(ERR_PASSWORD_TOO_SHORT_KO);
      return;
    }

    setPending(true);
    try {
      if (signingUp) {
        await signup(email, password);
      } else {
        await login(email, password);
      }
      // 로그인됨 = 내 포트폴리오. `refresh()` re-runs the server components that
      // read the session, so the chrome and any gated page see the new cookie.
      router.push(ROUTES.portfolio);
      router.refresh();
    } catch (failure) {
      setError(failure instanceof ApiError ? authErrorKo(failure.code) : null);
      setPending(false);
    }
  }

  async function onReset() {
    setError(null);
    setNotice(null);
    setPending(true);
    try {
      await requestPasswordReset(email);
    } catch {
      // 가입 여부 비노출: the endpoint answers identically for a known and an
      // unknown address, so the reader is told the same thing either way — and a
      // transport failure must not become a hint about the address.
    }
    setPending(false);
    setNotice(RESET_SENT_KO);
  }

  return (
    <main className={`content ${styles.page}`}>
      <CraftPanel className={styles.panel}>
        <h1 className={styles.title}>{submitLabel}</h1>
        <p className={styles.intro}>{signingUp ? SIGNUP_INTRO_KO : LOGIN_INTRO_KO}</p>

        <form className={styles.form} onSubmit={onSubmit}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="auth-email">
              {EMAIL_LABEL_KO}
            </label>
            <input
              id="auth-email"
              className={styles.input}
              type="email"
              // `mijual.web.auth._EMAIL_RE`, so a value the service would refuse
              // cannot be submitted: `invalid_email` has no signed Korean, and
              // the browser's own refusal is the browser's copy, not ours.
              pattern="[^@\s]+@[^@\s]+\.[^@\s]+"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="auth-password">
              {PASSWORD_LABEL_KO}
            </label>
            <input
              id="auth-password"
              className={styles.input}
              type="password"
              autoComplete={signingUp ? "new-password" : "current-password"}
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>

          <button className={styles.submit} type="submit" disabled={pending}>
            {pending ? PENDING_KO : submitLabel}
          </button>
        </form>

        {/* One line, under the form, never beside a field (R5-1). */}
        {error ? <p className={styles.error}>{error}</p> : null}
        {notice ? <p className={styles.notice}>{notice}</p> : null}

        <div className={styles.quietRow}>
          {/* The 전환 링크: its label is the other mode's own name, so switching
              needs no copy of its own. */}
          <button
            className={styles.quiet}
            type="button"
            onClick={() => {
              setMode(signingUp ? "login" : "signup");
              setError(null);
              setNotice(null);
            }}
          >
            {signingUp ? LOGIN_KO : SIGNUP_KO}
          </button>

          {/* 재설정 is a 로그인 affordance: there is nothing to reset from the
              계정 만들기 side. Disabled without an address, because the endpoint
              answers 보냈습니다 for anything and would say it about nothing. */}
          {signingUp ? null : (
            <button
              className={styles.quiet}
              type="button"
              disabled={pending || email.trim() === ""}
              onClick={onReset}
            >
              {RESET_LINK_KO}
            </button>
          )}
        </div>

        {/* 상시 요소 — both modes, always. */}
        <PiiInset />
      </CraftPanel>

      {/* 하단 고정 (R5-1's own words for this page's sample entry). */}
      <SampleEntry />
    </main>
  );
}
