"use client";

import { useState } from "react";
import Link from "next/link";
import { CraftPanel } from "@/components";
import { authErrorKo } from "@/components/auth/copy";
import { setAccountState } from "@/components/chrome/useAccount";
import { ApiError, changeEmail, deleteAccount, logout, saveNotifications } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import { writeFlash } from "@/lib/session";
import type { Notifications } from "@/lib/types";
import {
  ADDRESS_LABEL_KO,
  CANCEL_KO,
  CHANGE_KO,
  DELETE_ACCOUNT_KO,
  DELETE_ACCOUNT_NOTE_KO,
  HOLDINGS_LABEL_KO,
  KAKAO_LABEL_KO,
  KAKAO_NOTE_KO,
  LEAD_DAY_LABELS_KO,
  LOGOUT_KO,
  NOTIFY_TITLE_KO,
  PLANNED_CHIP_KO,
  SAVE_KO,
} from "./copy";
import styles from "./Portfolio.module.css";

/**
 * 알림 설정 (R5-5, R5-7 — framed by **R13 §3**) — the account menu's second
 * destination.
 *
 * > 설정: 수신 주소(변경) · 마감 임박 시점 칩 다중선택 (7일/3일/1일/당일; 기본
 * > 7일+1일) · **KakaoTalk 행 = 라벨 + 「예정」 칩, 인터랙티브 컨트롤 렌더 금지** ·
 * > 로그아웃 · 계정 삭제 (이메일 즉시 삭제).
 *
 * ## finding 12 — the page had no frame
 *
 * It carried no `h1` and no way out but the nav. R13 fixes both **without new
 * copy**: 「마감 임박 이메일」 was already this page's title, so the `h2` is
 * promoted to the page's one `h1`; and the column's first row is a rail — the
 * same `← ` every other crumb in this product uses plus the signed layer name
 * `HOLDINGS_LABEL_KO` (「보유 종목」, R8's nav word; R13 §4b is explicit that a
 * reader surface never says 「포트폴리오」). It is the column's first row, not a
 * full-width bar, exactly as R12 gave the auth column one.
 *
 * The rows are the canon's three tracks (`104px minmax(0,1fr) auto`), so 변경 ·
 * 로그아웃 · 계정 삭제 share one right edge, and the three single actions share
 * one box size (`.wide`, 104px floor) because they must not read as three
 * different weights.
 *
 * ## What this surface does not have, and why each absence is the design
 *
 * **No KakaoTalk control.** R5-5: "행은 보이되 컨트롤 없음 … 동작하지 않는 스위치
 * 없음", and it is structural rather than remembered: `P5.S8` note 12 built **no
 * server field** for it, so there is nothing a switch could store.
 *
 * **No sending.** The preferences persist and nothing mails: the channel, the
 * schedule and the body are P4's (`P5.DECOMP` note 6). Deselecting every chip is
 * a valid setting that means no mail — R5's own mail footer promises "알림
 * 설정에서 끌 수 있습니다" and this is the only off switch the signed surface has,
 * so `[]` is saved rather than falling back to the default.
 *
 * **No password re-entry on 수신 주소 변경.** R5's Notify row is an address with a
 * 변경 affordance and nothing else, and 계정 삭제 — strictly more destructive —
 * takes none either (`P5.S7`'s precedent). A malformed address now answers with
 * R12's inherited `invalid_email` line (finding 13: the bite is **intended** — it
 * used to fail silently), rendered as one line of body ink that does not tint the
 * field's border, because `--alert` means 소멸·임박 on this product and nothing
 * else.
 *
 * **No 확인 다이얼로그, anywhere.** 로그아웃 is immediate (R5-1). 계정 삭제 is
 * immediate too, and its confirm is the round's own interaction vocabulary rather
 * than a modal: the control **arms in place** — the action column becomes
 * 계정 삭제 · 취소, exactly the horizontal swap 개정 ④ signs for a row edit — and
 * the second press deletes. **R13 revises where the signed sentence stands**: it
 * renders only while the control is armed. A reader with no intention of deleting
 * has no reason to read what deleting does on every visit; the reader who armed
 * it reads it *before* the irreversible press.
 */
export function NotificationsView({ notifications }: { notifications: Notifications }) {
  const [leadDays, setLeadDays] = useState<number[]>(notifications.lead_days);
  const [address, setAddress] = useState(notifications.address);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(notifications.address);
  const [error, setError] = useState<string | null>(null);
  const [armed, setArmed] = useState(false);
  const [busy, setBusy] = useState(false);

  const toggle = (days: number) => {
    const next = leadDays.includes(days)
      ? leadDays.filter((value) => value !== days)
      : [...leadDays, days];
    setLeadDays(next);
    setBusy(true);
    void saveNotifications(next)
      .then((saved) => setLeadDays(saved.lead_days))
      .catch(() => setLeadDays(leadDays))
      .finally(() => setBusy(false));
  };

  const saveAddress = () => {
    const email = draft.trim();
    if (email === "" || email === address) {
      setEditing(false);
      return;
    }
    setBusy(true);
    setError(null);
    void changeEmail(email)
      .then((result) => {
        setAddress(result.account.email);
        setEditing(false);
        setAccountState({ authenticated: true, account: result.account });
      })
      .catch((failure) => {
        // Only signed lines are ever shown; an unmapped code renders none
        // (`components/auth/copy.ts`'s `authErrorKo`).
        setError(failure instanceof ApiError ? authErrorKo(failure.code) : null);
      })
      .finally(() => setBusy(false));
  };

  // 로그아웃 and 계정 삭제 both leave through a fresh document load, for the
  // reason `components/chrome/AccountSlot.tsx` records: the session is gone, so
  // every gated payload the client router has cached is stale, and a Back press
  // must not restore a 보유 종목 nobody is signed into any more.
  const signOut = () => {
    setBusy(true);
    void logout()
      .catch(() => undefined)
      .finally(() => {
        writeFlash("logout");
        window.location.assign(ROUTES.login);
      });
  };

  const removeAccount = () => {
    if (!armed) {
      setArmed(true);
      return;
    }
    setBusy(true);
    void deleteAccount()
      .catch(() => undefined)
      .finally(() => {
        // The account is gone; the landing is the anonymous home it leaves the
        // reader on. No 로그아웃 message: nothing was logged out of.
        window.location.assign(ROUTES.board);
      });
  };

  return (
    <div className={styles.notifyColumn}>
      {/* finding 12 — the way back, and the only one this page had was the nav. */}
      <nav className={styles.rail}>
        <Link className={styles.crumb} href={ROUTES.portfolio}>
          ← {HOLDINGS_LABEL_KO}
        </Link>
      </nav>

      <CraftPanel className={styles.notify}>
        <h1 className={styles.notifyTitle}>{NOTIFY_TITLE_KO}</h1>

        {/* 수신 주소 = the account email itself (`P5.S8` note 10). */}
        <div className={styles.notifyRow}>
          <span className={styles.notifyLabel}>{ADDRESS_LABEL_KO}</span>
          {editing ? (
            <>
              <input
                className={styles.emailInput}
                type="email"
                value={draft}
                autoComplete="email"
                disabled={busy}
                onChange={(event) => setDraft(event.target.value)}
              />
              <span className={styles.actions}>
                <button
                  type="button"
                  className={`${styles.action} ${styles.actionPrimary}`}
                  disabled={busy}
                  onClick={saveAddress}
                >
                  {SAVE_KO}
                </button>
                <button
                  type="button"
                  className={styles.action}
                  onClick={() => {
                    setEditing(false);
                    setError(null);
                    setDraft(address);
                  }}
                >
                  {CANCEL_KO}
                </button>
              </span>
            </>
          ) : (
            <>
              <span className={`mono ${styles.notifyValue}`}>{address}</span>
              <button
                type="button"
                className={styles.action}
                onClick={() => {
                  setDraft(address);
                  setEditing(true);
                }}
              >
                {CHANGE_KO}
              </button>
            </>
          )}
          {/* The error belongs to the row it is about — one line of body ink
              across the row's own tracks, never a red field. */}
          {error ? (
            <p className={styles.error} role="status">
              {error}
            </p>
          ) : null}
        </div>

        {/* 마감 임박 시점 칩 — multiselect, and an empty selection is a setting. */}
        <div className={styles.chips}>
          {LEAD_DAY_LABELS_KO.map((chip) => (
            <button
              key={chip.days}
              type="button"
              className={styles.chip}
              aria-pressed={leadDays.includes(chip.days)}
              disabled={busy}
              onClick={() => toggle(chip.days)}
            >
              {chip.label}
            </button>
          ))}
        </div>

        {/* KakaoTalk — a row, a 「예정」 chip, a sentence, and no control at all. */}
        <div className={styles.notifyRow}>
          <span className={styles.notifyLabel}>{KAKAO_LABEL_KO}</span>
          <span className={styles.notifyNote}>{KAKAO_NOTE_KO}</span>
          <span className={styles.plannedChip}>{PLANNED_CHIP_KO}</span>
        </div>

        <div className={styles.notifyRow}>
          <span className={styles.notifyLabel} />
          <span />
          <button
            type="button"
            className={`${styles.action} ${styles.wide}`}
            disabled={busy}
            onClick={signOut}
          >
            {LOGOUT_KO}
          </button>
        </div>

        <div className={styles.notifyRow}>
          <span className={styles.notifyLabel} />
          <span />
          <span className={styles.actions}>
            <button
              type="button"
              className={
                armed
                  ? `${styles.action} ${styles.wide} ${styles.armed}`
                  : `${styles.action} ${styles.wide}`
              }
              disabled={busy}
              onClick={removeAccount}
            >
              {DELETE_ACCOUNT_KO}
            </button>
            {armed ? (
              <button
                type="button"
                className={`${styles.action} ${styles.wide}`}
                onClick={() => setArmed(false)}
              >
                {CANCEL_KO}
              </button>
            ) : null}
          </span>
        </div>

        {/* 삭제가 무엇을 하는지는 무장된 다음에만 말한다 (R13 session revision,
            withdrawing R5's 상시 placement). */}
        {armed ? <p className={styles.notifyFoot}>{DELETE_ACCOUNT_NOTE_KO}</p> : null}
      </CraftPanel>
    </div>
  );
}
