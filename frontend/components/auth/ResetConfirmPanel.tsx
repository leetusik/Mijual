"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { CraftPanel } from "@/components";
import { ApiError, confirmPasswordReset } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import {
  ERR_PASSWORD_TOO_SHORT_KO,
  LOGIN_KO,
  MIN_PASSWORD_LENGTH,
  PASSWORD_LABEL_KO,
  PASSWORD_RULE_KO,
  PENDING_KO,
  RESET_LINK_KO,
  authErrorKo,
} from "./copy";
import { AuthRail } from "./AuthRail";
import styles from "./Auth.module.css";

/**
 * The surface the emailed 재설정 link lands on (`/auth/reset?token=…`).
 *
 * R5-1 signs the *flow* — "재설정 = 이메일 링크(가입 여부 비노출)" — and **R12 §3**
 * gives this page its own contract: the login panel's column, rail, panel and
 * four states, **one** field, and the rule stated on its label row.
 *
 * ## What it collects, and what it deliberately does not
 *
 * The link is a **credential** and the token is the whole of it (`P5.S7`: 256
 * bits, single-use, 1 hour, superseding — the latest mail is the one that works).
 * So this page collects one field and posts it with the token. There is **no
 * 이메일 field**: asking for the address again would imply the reset could be for
 * a different one, and drawing it would put a reader's address back on a screen
 * that does not need it. There is **no sample entry** either — R5-4 fixed that to
 * the 로그인 page, and this page belongs to a reader who already has an account.
 *
 * It also never states the link's remaining validity, and never says a link *is*
 * valid at render: the token's state is knowable only at submit.
 *
 * ## The state that used to answer nothing (R12 finding 3)
 *
 * An expired or already-spent link answers `invalid_reset_token`, and until R12
 * no round had signed a sentence for it, so the panel returned to idle in
 * silence. It now renders `ERR_RESET_TOKEN_KO` — which does **not** say which of
 * the two happened, because not distinguishing 만료 from 사용됨 is the token state
 * staying unexposed — and, **in that state only**, one quiet 「로그인」 back to the
 * panel where a fresh link is requested.
 *
 * ## Success is not a screen
 *
 * `POST /auth/reset/confirm` sets the password, **revokes every existing
 * session**, and issues a fresh one — the reader just proved mailbox control and
 * chose the password, so bouncing them back to the login panel would be ceremony
 * and a 「완료되었습니다」 screen would be a fake state. A success lands on 보유
 * 종목 exactly as a 로그인 does.
 */
export function ResetConfirmPanel({ token }: { token: string }) {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  /** The last answer, line **and** way out in one value: 「로그인」 belongs to the
   * expired/spent state and to no other, so the two cannot be left disagreeing —
   * a later 8자 미만 replaces both at once. */
  const [answer, setAnswer] = useState<{ line: string | null; expired: boolean }>({
    line: null,
    expired: false,
  });

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    // The rule was already on the label row; this is the same signed line, one
    // round trip sooner (R12 §3).
    if (password.length < MIN_PASSWORD_LENGTH) {
      setAnswer({ line: ERR_PASSWORD_TOO_SHORT_KO, expired: false });
      return;
    }

    setAnswer({ line: null, expired: false });
    setPending(true);
    try {
      await confirmPasswordReset(token, password);
      router.push(ROUTES.portfolio);
      router.refresh();
    } catch (failure) {
      const code = failure instanceof ApiError ? failure.code : null;
      setAnswer({
        line: code === null ? null : authErrorKo(code),
        expired: code === "invalid_reset_token",
      });
      setPending(false);
    }
  }

  return (
    <main className={`content ${styles.page}`}>
      <AuthRail />

      <CraftPanel className={styles.panel}>
        <div className={styles.head}>
          <h1 className={styles.title}>{RESET_LINK_KO}</h1>
        </div>

        <form className={styles.form} noValidate onSubmit={onSubmit}>
          <div className={styles.field}>
            <div className={styles.labelRow}>
              <label className={styles.label} htmlFor="reset-password">
                {PASSWORD_LABEL_KO}
              </label>
              <span className={styles.rule}>{PASSWORD_RULE_KO}</span>
            </div>
            <input
              id="reset-password"
              className={styles.input}
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setAnswer({ line: null, expired: false });
              }}
            />
          </div>

          <button className={styles.submit} type="submit" disabled={pending}>
            {pending ? PENDING_KO : RESET_LINK_KO}
          </button>
        </form>

        {answer.line ? (
          <p className={styles.line} role="status">
            {answer.line}
          </p>
        ) : null}

        {/* The way back, drawn only where it is the answer. It navigates, so it
            is a link wearing the quiet row's own treatment — the login panel's
            two controls are buttons precisely because neither of them does. */}
        {answer.expired ? (
          <div className={styles.quietRow}>
            <Link className={styles.quiet} href={ROUTES.login}>
              {LOGIN_KO}
            </Link>
          </div>
        ) : null}
      </CraftPanel>
    </main>
  );
}
