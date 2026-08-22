"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { CraftPanel } from "@/components";
import { ApiError, confirmPasswordReset } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import {
  ERR_PASSWORD_TOO_SHORT_KO,
  MIN_PASSWORD_LENGTH,
  PASSWORD_LABEL_KO,
  PENDING_KO,
  RESET_LINK_KO,
} from "./copy";
import { PiiInset } from "./PiiInset";
import styles from "./Auth.module.css";

/**
 * The surface the emailed 재설정 link lands on (`/auth/reset?token=…`).
 *
 * R5-1 signs the *flow* — "재설정 = 이메일 링크(가입 여부 비노출)" — and the
 * round's copy list gives the request's answer ("재설정 링크를 보냈습니다 —
 * 메일함을 확인해 주세요.") and the 8자 line. It writes **no dedicated copy for
 * this page**, so the page is composed only from strings the round already
 * signed: the field label 비밀번호, the composed 비밀번호 재설정 verb the request
 * trigger also uses, 확인 중…, and the 8자 미만 line. Nothing else is written.
 *
 * ## What this page is, structurally
 *
 * The link is a **credential** and the token is the whole of it (`P5.S7`: 256
 * bits, single-use, 1 hour, superseding — the latest mail is the one that works).
 * So this page collects one field and posts it with the token:
 * `POST /auth/reset/confirm` sets the password, **revokes every existing
 * session**, and issues a fresh one — the reader just proved mailbox control and
 * chose the password, so bouncing them back to the login panel would be ceremony.
 * A success therefore lands on 내 포트폴리오 exactly as a 로그인 does.
 *
 * ## ⚠ The one state with no signed line
 *
 * An expired or already-spent link answers `invalid_reset_token`, and R5 signs no
 * sentence for it (its three error cases are 불일치 / 중복 가입 / 8자 미만). The
 * panel therefore returns to idle and renders **no line** rather than inventing
 * Korean: a reader can request a new link from the login panel, and the missing
 * sentence is recorded for `P5.S19`/the operator as a design gap, not patched
 * here. `password_too_short` on this page *does* have its line, and gets it.
 */
export function ResetConfirmPanel({ token }: { token: string }) {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(ERR_PASSWORD_TOO_SHORT_KO);
      return;
    }

    setPending(true);
    try {
      await confirmPasswordReset(token, password);
      router.push(ROUTES.portfolio);
      router.refresh();
    } catch (failure) {
      // `password_too_short` has a signed line; `invalid_reset_token` has none,
      // and none is written (see the header).
      setError(
        failure instanceof ApiError && failure.code === "password_too_short"
          ? ERR_PASSWORD_TOO_SHORT_KO
          : null,
      );
      setPending(false);
    }
  }

  return (
    <main className={`content ${styles.page}`}>
      <CraftPanel className={styles.panel}>
        <h1 className={styles.title}>{RESET_LINK_KO}</h1>

        <form className={styles.form} onSubmit={onSubmit}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="reset-password">
              {PASSWORD_LABEL_KO}
            </label>
            <input
              id="reset-password"
              className={styles.input}
              type="password"
              autoComplete="new-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>

          <button className={styles.submit} type="submit" disabled={pending}>
            {pending ? PENDING_KO : RESET_LINK_KO}
          </button>
        </form>

        {error ? <p className={styles.error}>{error}</p> : null}

        {/* The PII statement is a permanent element of the auth screen
            (`security`), and this is one of its two pages. */}
        <PiiInset />
      </CraftPanel>
    </main>
  );
}
