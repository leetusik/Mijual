"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Identicon } from "@/components";
import { logout as logoutRequest } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import { writeFlash } from "@/lib/session";
import { LOGIN_KO, LOGOUT_KO, NOTIFICATIONS_LABEL_KO, VOCKY_ROW_KO } from "./copy";
import { FeedbackDialog } from "./Feedback";
import { useAccount } from "./useAccount";
import styles from "./AccountSlot.module.css";

/**
 * The chrome's account slot — R5 built it, **R8 re-cut it** (SIGNOFF: R8
 * supersedes "R5 §Chrome 개정 ⑤ (축약 이메일 메뉴 → full email + identicon +
 * frame, menu rows)" and "R5-4 (샘플 chip + 샘플 종료)").
 *
 * ```
 * <button class=frame aria-haspopup="menu" aria-expanded title={email}>
 *   <Identicon seed={email} size={20} />
 *   <span class="mono email">{email}</span>
 *   <span aria-hidden>▾</span>
 * </button>
 * ```
 *
 * Three deletions and one addition, all signed (build-prompt §2, result.md §2):
 *
 * 1. **축약 이메일 → the full address.** R5's abbreviation (앞 4자 + … + 도메인 끝)
 *    is retired — the walk found "swan…com" unreadable as an identity — so the
 *    frame renders the whole address, `max-width: 280px` with an ellipsis and the
 *    full text in `title`. `lib/account.ts` went with it.
 * 2. **A hairline frame + ▾.** "조용한 텍스트 링크였던 R5의 형태는 클릭 가능성을
 *    말하지 못했다": the affordance is the frame, the caret and the hover.
 * 3. **The menu is two rows** — 알림 설정 / 로그아웃. 내 포트폴리오 left the menu
 *    because the same destination is now a nav slot (보유 종목), and the menu is
 *    aligned to the frame's right edge and **opaque** so the cosmos cannot read
 *    through a list of destinations. **R9's session added a third row**, 의견
 *    보내기, between them (build-prompt §12, card `chrome/AccountSlot.html`):
 *    「메뉴는 `알림 설정 / 의견 보내기 / 로그아웃` 세 행이 된다 … R8이 만든 미주알
 *    소유 의견 표면을 여는 세 번째 진입점이며 … 새 표면도 새 카피도 없다」 — the
 *    label is the existing `VOCKY_ROW_KO`, the behaviour is the footer's.
 * 4. **The 샘플 state is gone.** R5-4's chip and 샘플 종료 are retired: the slot
 *    has exactly two states, anonymous and signed-in, and 「샘플임을 말하는 자리」
 *    is the portfolio surface's own banner. `lib/sample.ts` still runs the mode —
 *    the chrome simply says nothing about it.
 *
 * What R5 decided and R8 leaves alone: the slot renders **nothing** until the
 * probe answers (`useAccount()`'s `null` is "not answered yet", never anonymous),
 * and 로그아웃 is immediate and dialog-free (R5-1).
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

/** 열림 시 ▴ — a glyph pair, not copy (the same reading `CLOSE_GLYPH` records). */
const CARET_CLOSED = "▾";
const CARET_OPEN = "▴";

export function AccountSlotDesktop() {
  const account = useAccount();
  const logout = useLogout();
  const [open, setOpen] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const slot = useRef<HTMLDivElement>(null);
  const frame = useRef<HTMLButtonElement>(null);

  // ≤480 the whole desktop slot is `display: none` (`Nav.module.css` `.utility`)
  // and the 의견 row's job passes to the sheet's own row — so an open panel would
  // go invisible **with its ancestor** while `FeedbackDialog`'s mobile branch
  // still holds the counted body-scroll lock. Measured before this effect
  // existed: at 400px the dialog was in the DOM with `offsetParent === null`,
  // a zero-size rect and `body { overflow: hidden }`, i.e. exactly the lock
  // `P8.S3` note 3 warns about, with nothing on screen to close. Closing at the
  // breakpoint is the honest end of that panel: its entry point is gone.
  useEffect(() => {
    if (!feedbackOpen) return;
    const media = window.matchMedia("(max-width: 480px)");
    const sync = () => {
      if (media.matches) setFeedbackOpen(false);
    };
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, [feedbackOpen]);

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

  if (account === null) return <div className={styles.slot} />;

  if (!account.authenticated) {
    return (
      <Link href={ROUTES.login} className={styles.login}>
        {LOGIN_KO}
      </Link>
    );
  }

  const email = account.account.email;

  return (
    <div className={styles.slot} ref={slot}>
      <button
        type="button"
        ref={frame}
        className={styles.frame}
        aria-expanded={open}
        aria-haspopup="menu"
        title={email}
        onClick={() => setOpen((value) => !value)}
      >
        <Identicon seed={email} size={20} />
        <span className={`mono ${styles.email}`}>{email}</span>
        <span aria-hidden="true" className={styles.caret}>
          {open ? CARET_OPEN : CARET_CLOSED}
        </span>
      </button>

      {open ? (
        <div className={styles.menu} role="menu">
          <Link className={styles.menuRow} role="menuitem" href={ROUTES.notifications}>
            {NOTIFICATIONS_LABEL_KO}
          </Link>
          {/* 의견 보내기 — the third entry point to the surface 미주알 already
              owns (R9 §12). 메뉴를 먼저 닫고 다이얼로그를 연다, in that order and
              for the reason `Nav.tsx` gives its sheet row: the menu closes on an
              outside click, so a dialog living inside it would be closed by its
              own first click. */}
          <button
            type="button"
            role="menuitem"
            className={styles.menuRow}
            aria-haspopup="dialog"
            aria-expanded={feedbackOpen}
            onClick={() => {
              setOpen(false);
              setFeedbackOpen(true);
            }}
          >
            {VOCKY_ROW_KO}
          </button>
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

      {/* Outside the menu and inside the slot: the menu is unmounted by the time
          this opens, and `.slot` is the `position: relative` box the anchored
          panel hangs off — `placement="below"`, because this entry point is in
          the top bar. Focus returns to the frame, the control still on screen. */}
      {feedbackOpen ? (
        <FeedbackDialog
          channel="web"
          variant="anchored"
          placement="below"
          onClose={() => setFeedbackOpen(false)}
          returnFocusTo={frame}
        />
      ) : null}
    </div>
  );
}

/**
 * The same account, in the mobile sheet (build-prompt §3).
 *
 * > 로그인 시 `[아이디콘 28 + 전체 이메일]` 표기 행(비인터랙티브, `padding:
 * > var(--space-3) var(--space-4)`) + `알림 설정` + `로그아웃`; 익명이면 `로그인`
 * > 한 행.
 *
 * The identity row is **표기, 탭 대상 아님** — it says whose account this is and
 * goes nowhere, which is why it is a `div` rather than the link R5 had here (the
 * destination it used to carry, 내 포트폴리오, is a sheet row of its own now:
 * 보유 종목).
 */
export function AccountSlotSheet() {
  const account = useAccount();
  const logout = useLogout();

  if (account === null) return null;

  if (!account.authenticated) {
    return (
      <Link href={ROUTES.login} className={styles.loginRow}>
        {LOGIN_KO}
      </Link>
    );
  }

  const email = account.account.email;

  return (
    <>
      <div className={styles.identityRow}>
        <Identicon seed={email} size={28} />
        <span className={`mono ${styles.sheetEmail}`}>{email}</span>
      </div>
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
