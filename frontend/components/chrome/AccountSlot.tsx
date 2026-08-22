import Link from "next/link";
import { ROUTES } from "@/lib/routes";
import { LOGIN_KO } from "./copy";
import styles from "./AccountSlot.module.css";

/**
 * The chrome's account slot — **the one place `P5.S16` changes.**
 *
 * Today it is R2's signed 로그인 entry: "Right: 로그인 (quiet,
 * `rgba(255,255,255,.68)`)" in the desktop bar, and a row in the mobile sheet.
 *
 * ## The seam, stated so S16 does not have to redesign the chrome
 *
 * R5 extends this slot and nothing else — the signoff records it as "extends
 * R2's chrome with the logged-in account menu (**extension, not restyle**;
 * footer unchanged)", and its build prompt spells the extension out:
 *
 * > Desktop: links 불변(R2 삼분할) · 로그인 링크 → 축약 이메일 메뉴(mono, 앞 4자
 * > + … + 도메인 끝): 내 포트폴리오 / 알림 설정 / 로그아웃. 그 외 R2 서명 불변
 * > (52px, underline, 의견 슬롯).
 * > Mobile 시트: 구분선 + 내 포트폴리오(이메일 병기) / 알림 설정 / 로그아웃 —
 * > 계정 메뉴 영역. Footer 불변.
 *
 * So `P5.S16` replaces the bodies of these two components (and adds the sample
 * mode's 「샘플」 chip + 샘플 종료, which R5-4 puts in the same slot). Nothing
 * else in `Nav.tsx` or `Footer.tsx` moves: the nav's three destinations, the 52px
 * bar, the active underline and the 의견 slot are signed as they are, and the
 * footer is explicitly unchanged.
 *
 * Two things this file deliberately does **not** do, both of which S16 owns:
 * it calls no API (`GET /auth/me` answers `{authenticated: false}` for a
 * visitor — anonymous is a result, not a 401 — but a fetch on every page load of
 * every surface is a decision for the slice that renders the logged-in chrome),
 * and it renders no email. The 축약 form (앞 4자 + … + 도메인 끝) is R5's, over
 * the full address `/auth/me` serves.
 *
 * ⚠ `ROUTES.login` has **no page until `P5.S15`** — see `lib/routes.ts`.
 */
export function AccountSlotDesktop() {
  return (
    <Link href={ROUTES.login} className={styles.login}>
      {LOGIN_KO}
    </Link>
  );
}

export function AccountSlotSheet() {
  return (
    <Link href={ROUTES.login} className={styles.loginRow}>
      {LOGIN_KO}
    </Link>
  );
}
