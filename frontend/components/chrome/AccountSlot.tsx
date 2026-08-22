"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { abbreviateEmail } from "@/lib/account";
import { logout as logoutRequest } from "@/lib/api";
import { ROUTES, samplePath } from "@/lib/routes";
import { clearSample, useSampleActive } from "@/lib/sample";
import { writeFlash } from "@/lib/session";
import {
  LOGIN_KO,
  LOGOUT_KO,
  NOTIFICATIONS_LABEL_KO,
  PORTFOLIO_LABEL_KO,
  SAMPLE_CHIP_KO,
  SAMPLE_EXIT_KO,
} from "./copy";
import { useAccount } from "./useAccount";
import styles from "./AccountSlot.module.css";

/**
 * The chrome's account slot — **the one place R5 changes the chrome.**
 *
 * The signoff records the round as extending "R2's chrome with the logged-in
 * account menu (**extension, not restyle**; footer unchanged)", and the build
 * prompt spells the extension out:
 *
 * > Desktop: links 불변(R2 삼분할) · 로그인 링크 → 축약 이메일 메뉴(mono, 앞 4자 +
 * > … + 도메인 끝): 내 포트폴리오 / 알림 설정 / 로그아웃. 그 외 R2 서명 불변
 * > (52px, underline, 의견 슬롯).
 * > Mobile 시트: 구분선 + 내 포트폴리오(이메일 병기) / 알림 설정 / 로그아웃 —
 * > 계정 메뉴 영역. Footer 불변.
 *
 * plus R5-4's third state, which occupies the same slot:
 *
 * > 로드 상태: … nav 「샘플」 칩 + 샘플 종료 (**로그인 슬롯 대체** — 메뉴 자리).
 *
 * So this slot has exactly three renderings — 로그인 (R2's, untouched), the
 * 축약 이메일 menu, and the 샘플 pair — and nothing else in `Nav.tsx`,
 * `Footer.tsx` or their stylesheets moved: the three destinations, the 52px bar,
 * the active underline, the 의견 slot and the whole footer are signed as they are.
 *
 * ## Three decisions this file makes, recorded for the review
 *
 * 1. **The slot renders nothing until the probe answers.** `useAccount()`'s
 *    `null` is "not answered yet", distinct from anonymous (the convention
 *    `components/auth/useAuthState.ts` set). Rendering 로그인 in the meantime
 *    would tell a logged-in reader for a frame that they have no account, which
 *    is the wrong half of R5's own 가짜 사용자 정체성 rule.
 * 2. **The 샘플 pair outranks both.** A loaded sample is a browser fact, and
 *    R5-4 says it *replaces* the 로그인 slot; the mode survives a revisit, so the
 *    reader must be able to see and end it from wherever they are, not only from
 *    the 2층 surface. The chip is inert (it names the state and links back to the
 *    mode's own address); 샘플 종료 wipes the browser's sample and returns to the
 *    landing — the anonymous home a reader was on before loading it.
 * 3. **로그아웃 is immediate and dialog-free** (R5-1: "로그아웃 즉시, 확인
 *    다이얼로그 없음, '로그아웃되었습니다' 1회 표시"). The message travels as a
 *    *kind* through `lib/session.ts`'s flash channel and the auth panel — the
 *    anonymous surface this lands on — shows it once (`P5.S15` note 1e).
 */

/**
 * 로그아웃 — immediate, dialog-free, and it leaves through a **fresh document
 * load** rather than a client-side push.
 *
 * Two reasons, one of them measured. (a) The session row is gone the moment the
 * `POST` returns (`P5.S7` note 1), so every gated payload the App Router has
 * cached client-side is stale in a way no re-render fixes — a full load drops the
 * lot, and a reader who presses Back after 로그아웃 cannot be shown their old
 * 포트폴리오 out of a cache. (b) A `router.push()` from this control is **dropped**
 * in a real browser: the slot swaps back to 로그인 in the same commit, and React
 * discards a navigation started by a component that unmounts (measured — the push
 * simply never happened, with or without a tick of delay).
 *
 * The one-time "로그아웃되었습니다" survives the load because the flash channel is
 * `sessionStorage` (`lib/session.ts`), and the 로그인 panel reads and clears it.
 */
function useLogout(): { pending: boolean; run: () => void } {
  const [pending, setPending] = useState(false);

  const run = () => {
    if (pending) return;
    setPending(true);
    void logoutRequest()
      .catch(() => undefined)
      .finally(() => {
        writeFlash("logout");
        window.location.assign(ROUTES.login);
      });
  };

  return { pending, run };
}

/** 샘플 종료 — "샘플·브라우저 저장분 삭제 후 **로드 전 상태 복귀**": the store goes
 * and the app reloads anonymous on the landing, for the same two reasons 로그아웃
 * has (a cached sample surface must not survive the mode, and a push from this
 * control is dropped when the control unmounts). */
function useSampleExit(): () => void {
  return () => {
    clearSample();
    window.location.assign(ROUTES.board);
  };
}

export function AccountSlotDesktop() {
  const sample = useSampleActive();
  const account = useAccount();
  const logout = useLogout();
  const exitSample = useSampleExit();
  const [open, setOpen] = useState(false);
  const slot = useRef<HTMLDivElement>(null);

  // An open menu closes on Escape and on a click outside it — an overlay floor,
  // the same one `Nav.tsx` gives the mobile sheet.
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    const onPointerDown = (event: MouseEvent) => {
      if (slot.current && !slot.current.contains(event.target as Node)) setOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("mousedown", onPointerDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("mousedown", onPointerDown);
    };
  }, [open]);

  if (sample) {
    return (
      <div className={styles.slot}>
        <Link className={styles.sampleChip} href={samplePath()}>
          {SAMPLE_CHIP_KO}
        </Link>
        <button type="button" className={styles.sampleExit} onClick={exitSample}>
          {SAMPLE_EXIT_KO}
        </button>
      </div>
    );
  }

  if (account === null) return <div className={styles.slot} />;

  if (!account.authenticated) {
    return (
      <Link href={ROUTES.login} className={styles.login}>
        {LOGIN_KO}
      </Link>
    );
  }

  return (
    <div className={styles.slot} ref={slot}>
      <button
        type="button"
        className={`mono ${styles.account}`}
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((value) => !value)}
      >
        {abbreviateEmail(account.account.email)}
      </button>

      {/* 스택 리스트 (R5-6): three rows, the layer's own entry first. */}
      {open ? (
        <div className={styles.menu} role="menu">
          <Link className={styles.menuRow} role="menuitem" href={ROUTES.portfolio}>
            {PORTFOLIO_LABEL_KO}
          </Link>
          <Link className={styles.menuRow} role="menuitem" href={ROUTES.notifications}>
            {NOTIFICATIONS_LABEL_KO}
          </Link>
          <button
            type="button"
            role="menuitem"
            className={styles.menuRow}
            disabled={logout.pending}
            onClick={logout.run}
          >
            {LOGOUT_KO}
          </button>
        </div>
      ) : null}
    </div>
  );
}

export function AccountSlotSheet() {
  const sample = useSampleActive();
  const account = useAccount();
  const logout = useLogout();
  const exitSample = useSampleExit();

  if (sample) {
    return (
      <>
        <Link className={styles.loginRow} href={samplePath()}>
          <span className={styles.sampleChip}>{SAMPLE_CHIP_KO}</span>
        </Link>
        <button type="button" className={styles.sheetAction} onClick={exitSample}>
          {SAMPLE_EXIT_KO}
        </button>
      </>
    );
  }

  if (account === null) return null;

  if (!account.authenticated) {
    return (
      <Link href={ROUTES.login} className={styles.loginRow}>
        {LOGIN_KO}
      </Link>
    );
  }

  return (
    <>
      {/* 내 포트폴리오(이메일 병기) — the sheet has room the 52px bar does not, so
          the address rides beside the row rather than replacing it. */}
      <Link className={styles.loginRow} href={ROUTES.portfolio}>
        {PORTFOLIO_LABEL_KO}
        <span className={`mono ${styles.sheetEmail}`}>{account.account.email}</span>
      </Link>
      <Link className={styles.loginRow} href={ROUTES.notifications}>
        {NOTIFICATIONS_LABEL_KO}
      </Link>
      <button
        type="button"
        className={styles.sheetAction}
        disabled={logout.pending}
        onClick={logout.run}
      >
        {LOGOUT_KO}
      </button>
    </>
  );
}
