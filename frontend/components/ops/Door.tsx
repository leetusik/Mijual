"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ApiError, opsLogin } from "@/lib/api";
import {
  CREDENTIALS_INVALID_KO,
  LOGIN_KO,
  OPERATOR_ID_KO,
  OPS_MARK,
  PASSWORD_KO,
} from "./copy";
import styles from "./Ops.module.css";

/**
 * The door (R7's `Access` card, §6.4).
 *
 * > 인증 전 표면이므로 ops 크롬 없음 — 빈 페이지 가운데 문 하나 (Access 카드).
 * > 운영자 ID + 비밀번호, R5 계정 테이블과 완전 분리 … 가입·재설정 UI 없음.
 *
 * So: no ops chrome, no reader chrome (`SiteChrome` renders none under `/ops`),
 * no 가입, no 재설정, no "forgot", and nothing that names a reader account.
 *
 * **One failure, always the same one.** The service answers a single
 * `401 invalid_credentials` for a wrong password, an unknown 운영자 ID *and* a
 * credential that was never configured, spending the same scrypt verification on
 * each — so this renders the one signed line 「자격증명이 올바르지 않습니다」 and
 * never names a field. It is body ink, not `--alert`: that hue means
 * expiring/lost, the rule `P5.S15` follows on the reader's own login.
 *
 * ## 로그인 후 있던 탭 복원
 *
 * The door is rendered **in place** by `app/ops/layout.tsx` at whatever ops URL
 * the operator asked for, so a session that expires on 정확도·비용 puts the door
 * on `/ops/accuracy` and `router.refresh()` re-runs that same route with the new
 * cookie. There is no `?next=`, no redirect and nothing to restore — the path
 * never moved.
 */
export function Door() {
  const router = useRouter();
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [failed, setFailed] = useState(false);
  const [busy, setBusy] = useState(false);

  return (
    <div className={styles.door}>
      {/* Stamped by extensions before hydration — see `SearchRow.tsx`. */}
      <form
        suppressHydrationWarning
        className={styles.doorCard}
        onSubmit={(event) => {
          event.preventDefault();
          setBusy(true);
          setFailed(false);
          opsLogin(id, password)
            .then(() => {
              // The layout re-runs, sees the session, and renders this tab.
              router.refresh();
            })
            .catch((error: unknown) => {
              // The signed line states one thing — that the credential is wrong
              // — so it is rendered for exactly that answer. A service that is
              // unreachable is a different fact, and R7 writes no copy for it:
              // the door stays silent rather than blaming the operator's typing
              // (the shape `P5.S15` took for `invalid_reset_token`).
              setFailed(error instanceof ApiError && error.status === 401);
              setBusy(false);
            });
        }}
      >
        <div className={styles.doorMark}>{OPS_MARK}</div>

        <label className={styles.doorField}>
          <span className={styles.doorLabel}>{OPERATOR_ID_KO}</span>
          <input
            suppressHydrationWarning
            className={styles.doorInput}
            name="id"
            autoComplete="off"
            value={id}
            onChange={(event) => setId(event.target.value)}
          />
        </label>

        <label className={styles.doorField}>
          <span className={styles.doorLabel}>{PASSWORD_KO}</span>
          <input
            suppressHydrationWarning
            className={styles.doorInput}
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>

        {/* Disabled while the request is in flight, with its label unchanged:
            R5's 확인 중 is that round's signed copy for the reader's panel, and
            borrowing it here would be putting a word on a control R7 drew
            without one. */}
        <button type="submit" className={styles.doorSubmit} disabled={busy}>
          {LOGIN_KO}
        </button>

        {failed && <p className={styles.doorError}>{CREDENTIALS_INVALID_KO}</p>}
      </form>
    </div>
  );
}
