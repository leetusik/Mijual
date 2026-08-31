"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { useReducedMotion } from "@/lib/motion";
import { lockBodyScroll } from "@/lib/scrollLock";
import { ROUTES, isActiveRoute } from "@/lib/routes";
import { AccountSlotDesktop, AccountSlotSheet } from "./AccountSlot";
import { CLOSE_GLYPH, MENU_KO, NAV_LINKS, VOCKY_ROW_KO } from "./copy";
import { FeedbackDialog } from "./Feedback";
import { Wordmark } from "./Wordmark";
import styles from "./Nav.module.css";

/**
 * The global nav — R2 §Page shell, **re-cut by R8** on both sides of the 480px
 * breakpoint (build-prompt §1 and §3; SIGNOFF: R8 supersedes R2's nav
 * destinations, utility slot and mobile sheet behaviour).
 *
 * What R2 signed and R8 keeps: the 52px transparent bar with its
 * `rgba(255,255,255,.12)` bottom hairline, the white ring wordmark at h19, links
 * at 13.5px with the 2px #fff active underline, hover as a colour change, P7's
 * focus split, and the 200ms fade.
 *
 * What R8 changes:
 *
 * 1. **Two destinations — AI 질문 · 보유 종목.** The 관제 현황판 *link* is gone,
 *    because "현황판은 랜딩이고 링 워드마크(→ `ROUTES.board`)가 이미 그 목적지다.
 *    같은 목적지를 바에서 두 번 말하지 않는다." On the landing there is therefore
 *    **no active link and no underline**, and `aria-current` is not moved onto
 *    the wordmark — the mark is the identity, not a nav item.
 * 2. **The `[의견]` chip is gone.** 의견 has two entry points now, the footer and
 *    the mobile sheet, and both open 미주알's own surface (`Feedback.tsx`).
 * 3. **The sheet is an overlay with a backdrop.** It used to push the page down;
 *    now it hangs from the bar over the content, the bar button turns into ×
 *    while it is open (the label stays 메뉴 — `aria-expanded` carries the state,
 *    and no 닫기 string was invented), the backdrop closes it on a tap, and the
 *    body cannot scroll underneath it.
 */

/** R2: "Sheet close = 200ms fade" — the same 200ms as `--dur-base`, which is what
 * the stylesheet uses. The JS half only has to unmount when the fade is over. */
const SHEET_FADE_MS = 200;

export function SiteNav() {
  const pathname = usePathname();
  const reducedMotion = useReducedMotion();
  const [sheetOpen, setSheetOpen] = useState(false);
  const [sheetClosing, setSheetClosing] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const menuButton = useRef<HTMLButtonElement>(null);

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

  // 「시트 열림 동안 `document.body` 스크롤 잠금」 (R8 §3). An overlay that lets the
  // page scroll behind it is the half-open state the walk found. The lock is
  // counted (`lib/scrollLock.ts`) because the 의견 sheet takes one too and the
  // two overlap by design.
  useEffect(() => {
    if (!sheetOpen) return;
    return lockBodyScroll();
  }, [sheetOpen]);

  return (
    <header className={styles.bar}>
      <div className={`content ${styles.inner}`}>
        {/* The mark is 관제 현황판's only entry from the chrome now (R8 §1), which
            is why the round removed the link that said the same thing twice. */}
        <Link href={ROUTES.board} className={styles.brand}>
          <Wordmark height={27} />
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
                data-label={link.label}
              >
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className={styles.utility}>
          <AccountSlotDesktop />
        </div>

        <button
          type="button"
          ref={menuButton}
          className={styles.menuButton}
          aria-label={MENU_KO}
          aria-expanded={sheetOpen}
          aria-controls="chrome-sheet"
          onClick={() => (sheetOpen ? closeSheet() : setSheetOpen(true))}
        >
          {sheetOpen ? (
            <span className={styles.menuGlyph}>{CLOSE_GLYPH}</span>
          ) : (
            MENU_KO
          )}
        </button>
      </div>

      {/* The backdrop belongs to the sheet and closes it on a tap. It is a
          sibling rather than a wrapper, so a tap on a row is never a tap on it. */}
      {sheetOpen ? (
        <div
          className={[styles.backdrop, sheetClosing ? styles.backdropClosing : null]
            .filter(Boolean)
            .join(" ")}
          onClick={closeSheet}
          aria-hidden="true"
        />
      ) : null}

      {/* The sheet stays in the document and is hidden with `display: none` (so
          it is out of the tab order and out of the accessibility tree) rather
          than mounted on open: the desktop bar must never show it at all, and
          keeping one element means the fade has something to fade. */}
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

        {/* 구분선 → 계정 영역 → 구분선 → 의견 보내기 (R8 §3). */}
        <div className={styles.sheetDivider} />
        <AccountSlotSheet />
        <div className={styles.sheetDivider} />
        <button
          type="button"
          className={styles.sheetAction}
          aria-haspopup="dialog"
          aria-expanded={feedbackOpen}
          onClick={() => {
            setFeedbackOpen(true);
            closeSheet();
          }}
        >
          {VOCKY_ROW_KO}
        </button>
      </nav>

      {/* Outside the sheet on purpose: opening 의견 closes the menu, and the
          sheet is `display: none` when closed — a dialog inside it would vanish
          with it. Focus returns to the bar button, which is the control the
          reader can actually see once the sheet is gone. */}
      {feedbackOpen ? (
        <FeedbackDialog
          channel="mobile"
          variant="sheet"
          onClose={() => setFeedbackOpen(false)}
          returnFocusTo={menuButton}
        />
      ) : null}
    </header>
  );
}
