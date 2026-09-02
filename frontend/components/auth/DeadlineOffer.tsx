"use client";

import Link from "next/link";
import { ROUTES, portfolioAddPath } from "@/lib/routes";
import { useAuthState } from "./useAuthState";
import { DEADLINE_OFFER_KO, PORTFOLIO_ADD_KO } from "./copy";
import styles from "./Auth.module.css";

/**
 * 전환 제안 ② — the one-line link under a detail page's D-day (R5-2).
 *
 * > ② 상세 D-day 아래 한 줄 링크 "이 마감 알림 받기 →". … 상세 D-day 아래 한 줄
 * > 링크 (로그인 시 "내 포트폴리오에 담기 →"로 교체).
 *
 * One line, two states, and it gates nothing in either: anonymous it is a link to
 * the 로그인 panel, logged in it is a link to 내 포트폴리오 with this issuer named
 * (`?add=`, which `P5.S16` reads to preselect it in R5's own 종목 추가 panel).
 * **Following a link writes nothing** — a 담기 needs a 보유량 this page never asks
 * for, and there is no anonymous write endpoint to guess one into.
 *
 * ## Two readings this component makes, both recorded for `P5.S19`
 *
 * **Nothing renders until the session is known.** The two states say different
 * things about the reader, so showing one and then the other would tell a logged-in
 * reader for a moment that they have no account. The probe is `GET /auth/me`,
 * which answers `{authenticated: false}` rather than 401 for a visitor, and it is
 * the only request this surface adds.
 *
 * **On the event page that reading is now honoured by the SERVER** (`P4.F10`).
 * `/events/{rcept_no}` resolves the session from the request's own cookie while it
 * fetches the event, and hands the answer down as `initialAuthenticated` — so the
 * correct one of the two states is in the first painted HTML, the probe never
 * fires there, and the line stops being inserted 2.4s into the load (a **0.0325**
 * mobile CLS on the one route P4 had left above its 0.01 target). Nothing about
 * the reading changed: neither state is shown before the session is known — it is
 * simply known earlier, and by the half of the app that can know it first. Every
 * other host passes nothing, keeps the probe, and behaves exactly as before.
 *
 * **The line needs a deadline that is still ahead**, which is the caller's gate:
 * "이 마감 알림 받기" on an anchor already behind the reference day would promise
 * an alert that can never be sent (the 시점 칩 are 7일/3일/1일/당일 *before* a
 * deadline), and a promise nothing can keep is the failure class this product
 * exists to avoid. R5-2 places the line "상세 D-day 아래" without qualifying it,
 * so the gate is a reading rather than a rule — see `Header.tsx`.
 */
export function DeadlineOffer({
  corpCode,
  className,
  initialAuthenticated,
}: {
  corpCode?: string | null;
  /** The host surface's own class for the line. R10 gives it the detail header's
   * geometry (`.offer`: an underlined secondary text link, 32px desktop / 44px
   * ≤767px, and its own place in the 390px stack) — the placement is the
   * surface's, the line is R5-2's. */
  className?: string;
  /** The session as the **server** already resolved it for this request, when the
   * host surface can (the event page does — `P4.F10`). Defined means "known
   * before first paint": this renders that state immediately and asks nobody.
   * `undefined` means no host resolved it, and the client probe runs exactly as it
   * always has — the two hosts differ in *when* the answer exists, never in what
   * is rendered from it. */
  initialAuthenticated?: boolean;
}) {
  // The probe is switched off, not merely ignored, when the server already
  // answered: `useAuthState(false)` fires no request and returns `null`.
  const probed = useAuthState(initialAuthenticated === undefined);
  const authenticated = initialAuthenticated ?? (probed === null ? null : probed.authenticated);

  if (authenticated === null) return null;
  const classes = className ? `${styles.deadlineOffer} ${className}` : styles.deadlineOffer;

  if (authenticated) {
    return (
      <Link className={classes} href={corpCode ? portfolioAddPath(corpCode) : ROUTES.portfolio}>
        {PORTFOLIO_ADD_KO}
      </Link>
    );
  }

  return (
    <Link className={classes} href={ROUTES.login}>
      {DEADLINE_OFFER_KO}
    </Link>
  );
}
