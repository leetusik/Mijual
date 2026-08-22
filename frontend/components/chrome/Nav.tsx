"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { useReducedMotion } from "@/lib/motion";
import { ROUTES, isActiveRoute } from "@/lib/routes";
import { AccountSlotDesktop, AccountSlotSheet } from "./AccountSlot";
import { MENU_KO, NAV_LINKS, VOCKY_NAV_KO, VOCKY_ROW_KO } from "./copy";
import { VockyTrigger } from "./VockyTrigger";
import { Wordmark } from "./Wordmark";
import styles from "./Nav.module.css";

/**
 * The global nav — R2 §Page shell, on both sides of the 480px breakpoint.
 *
 * > **Nav** 52px, transparent over the cosmos, 1px `rgba(255,255,255,.12)`
 * > bottom. Left: white ring wordmark PNG (h 19px) + links 내 종목 연결 · 관제
 * > 현황판 · 해설 (13.5px; active = 600 + 2px #fff underline; labels
 * > provisional). Right: 로그인 (quiet, `rgba(255,255,255,.68)`) + vocky trigger
 * > `[의견]` (mono, hairline `rgba(255,255,255,.3)`).
 * >
 * > **Mobile**: top bar 52px (white ring wordmark + `메뉴` button, mono, 44px
 * > hit) + sheet menu: rows ≥48px. Sheet close = 200ms fade.
 *
 * The two provisional labels are **not** rendered as R2 spells them: R2 posed
 * them back and both were settled by later signed rounds, which is what the
 * supersession table in `docs/current/frontend.md` is for — 내 종목 연결 → **내
 * 종목 조회** (R4) and 해설 → **AI 질문** (R6, which also states the final
 * three-slot nav). The labels and their sources live in `./copy.ts`.
 *
 * One bar renders both forms: the destinations and the utility slots are the
 * desktop content, the 메뉴 button is the mobile one, and the 480px media query
 * in `Nav.module.css` decides which is visible — the round describes one 52px
 * bar, not two components.
 */

/** R2: "Sheet close = 200ms fade" — the same 200ms as `--dur-base`, which is what
 * the stylesheet uses. The JS half only has to unmount when the fade is over. */
const SHEET_FADE_MS = 200;

export function SiteNav() {
  const pathname = usePathname();
  const reducedMotion = useReducedMotion();
  const [sheetOpen, setSheetOpen] = useState(false);
  const [sheetClosing, setSheetClosing] = useState(false);

  /* The close is the animated half. Under `prefers-reduced-motion: reduce` a
   * fade becomes a **cut** — `app/shell.css`'s convention, and the JS half of it
   * is here: unmount immediately rather than wait out a transition that the
   * stylesheet has already reduced to 1ms. */
  const closeSheet = useCallback(() => {
    if (reducedMotion) {
      setSheetClosing(false);
      setSheetOpen(false);
      return;
    }
    setSheetClosing(true);
  }, [reducedMotion]);

  useEffect(() => {
    if (!sheetClosing) return;
    const timer = window.setTimeout(() => {
      setSheetClosing(false);
      setSheetOpen(false);
    }, SHEET_FADE_MS);
    return () => window.clearTimeout(timer);
  }, [sheetClosing]);

  // A destination replaces the surface underneath, so the sheet goes with it —
  // and it goes at once, because the page it belonged to is gone.
  useEffect(() => {
    setSheetClosing(false);
    setSheetOpen(false);
  }, [pathname]);

  // Escape closes an open overlay. An a11y floor (R1/`frontend` v0002:
  // "reduced motion is a floor, not an option"; the focus ring is the shell's),
  // not a visual decision.
  useEffect(() => {
    if (!sheetOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeSheet();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [sheetOpen, closeSheet]);

  return (
    <header className={styles.bar}>
      <div className={`content ${styles.inner}`}>
        {/* The mark leads to 관제 현황판, which is also a destination in the
            list — chrome behaviour, not a visual decision: R2 draws the mark and
            the three links, and says nothing about what the mark does. */}
        <Link href={ROUTES.board} className={styles.brand}>
          <Wordmark height={19} />
        </Link>

        <nav className={styles.links}>
          {NAV_LINKS.map((link) => {
            const active = isActiveRoute(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={active ? `${styles.link} ${styles.active}` : styles.link}
                aria-current={active ? "page" : undefined}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className={styles.utility}>
          <AccountSlotDesktop />
          <VockyTrigger surface="nav">{VOCKY_NAV_KO}</VockyTrigger>
        </div>

        <button
          type="button"
          className={styles.menuButton}
          aria-expanded={sheetOpen}
          aria-controls="chrome-sheet"
          onClick={() => (sheetOpen ? closeSheet() : setSheetOpen(true))}
        >
          {MENU_KO}
        </button>
      </div>

      {/* The sheet stays in the document and is hidden with `display: none` (so
          it is out of the tab order and out of the accessibility tree) rather
          than mounted on open. Two reasons: the desktop bar must never show it
          at all, and **vocky's script binds `[data-vocky-trigger]` on its own
          terms** — an external script that binds once at load would never see a
          trigger React creates later, so all three triggers exist from the first
          paint, which is also what R2 §vocky describes. */}
      <nav
        id="chrome-sheet"
        aria-label={MENU_KO}
        className={[styles.sheet, sheetOpen ? styles.sheetOpen : null, sheetClosing ? styles.sheetClosing : null]
          .filter(Boolean)
          .join(" ")}
      >
        {NAV_LINKS.map((link) => {
          const active = isActiveRoute(pathname, link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={active ? `${styles.sheetRow} ${styles.sheetActive}` : styles.sheetRow}
              aria-current={active ? "page" : undefined}
            >
              {link.label}
            </Link>
          );
        })}

        {/* R5's sheet keeps the destinations and adds a 구분선 before the
            account area; the utility rows (로그인, and the 의견 보내기 trigger
            R2 §vocky puts here) sit below it. */}
        <div className={styles.sheetDivider} />
        <AccountSlotSheet />
        <VockyTrigger surface="sheet">{VOCKY_ROW_KO}</VockyTrigger>
      </nav>
    </header>
  );
}
