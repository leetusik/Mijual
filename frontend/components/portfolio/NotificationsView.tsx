"use client";

import { useState } from "react";
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
 * 알림 설정 (R5-5, R5-7) — the account menu's second destination.
 *
 * > 설정: 수신 주소(변경) · 마감 임박 시점 칩 다중선택 (7일/3일/1일/당일; 기본
 * > 7일+1일) · **KakaoTalk 행 = 라벨 + 「예정」 칩, 인터랙티브 컨트롤 렌더 금지** ·
 * > 로그아웃 · 계정 삭제 (이메일 즉시 삭제).
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
 * takes none either (`P5.S7`'s precedent). `P5.S8` note 10 records the
 * consequence and the phase carries it as an operator/design question; adding a
 * field here would be inventing a control the round does not have.
 *
 * **No 확인 다이얼로그, anywhere.** 로그아웃 is immediate (R5-1). 계정 삭제 is
 * immediate too, and its confirm is the round's own interaction vocabulary rather
 * than a modal: the control **arms in place** — the action column becomes
 * 계정 삭제 · 취소, exactly the horizontal swap 개정 ④ signs for a row edit — and
 * the second press deletes. No new copy, no overlay, and no irreversible act on a
 * single stray click. The signed sentence sits under the row permanently, as the
 * Notify card draws it.
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
        // Only R5's signed lines are ever shown; an unmapped code renders none
        // (`components/auth/copy.ts`'s `authErrorKo`).
        setError(failure instanceof ApiError ? authErrorKo(failure.code) : null);
      })
      .finally(() => setBusy(false));
  };

  // 로그아웃 and 계정 삭제 both leave through a fresh document load, for the
  // reason `components/chrome/AccountSlot.tsx` records: the session is gone, so
  // every gated payload the client router has cached is stale, and a Back press
  // must not restore a portfolio nobody is signed into any more.
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
    <div className={styles.surface}>
      <CraftPanel className={styles.notify}>
        <h2 className={styles.notifyTitle}>{NOTIFY_TITLE_KO}</h2>

        {/* 수신 주소 = the account email itself (`P5.S8` note 10). */}
        <div className={styles.notifyRow}>
          <span className={styles.notifyLabel}>{ADDRESS_LABEL_KO}</span>
          {editing ? (
            <>
              <input
                className={`mono ${styles.emailInput}`}
                type="email"
                value={draft}
                autoComplete="email"
                disabled={busy}
                onChange={(event) => setDraft(event.target.value)}
              />
              <span className={styles.actions}>
                <button
                  type="button"
                  className={styles.action}
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
        </div>
        {error ? <p className={styles.error}>{error}</p> : null}

        {/* 마감 임박 시점 칩 — multiselect, and an empty selection is a setting. */}
        <div className={styles.chips}>
          {LEAD_DAY_LABELS_KO.map((chip) => (
            <button
              key={chip.days}
              type="button"
              className={
                leadDays.includes(chip.days) ? `${styles.chip} ${styles.chipOn}` : styles.chip
              }
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
          <span className={styles.plannedChip}>{PLANNED_CHIP_KO}</span>
          <span className={styles.notifyNote}>{KAKAO_NOTE_KO}</span>
        </div>

        <div className={styles.notifyRow}>
          <button type="button" className={styles.action} disabled={busy} onClick={signOut}>
            {LOGOUT_KO}
          </button>
        </div>

        <div className={styles.notifyRow}>
          <span className={styles.actions}>
            <button
              type="button"
              className={armed ? `${styles.action} ${styles.armed}` : styles.action}
              disabled={busy}
              onClick={removeAccount}
            >
              {DELETE_ACCOUNT_KO}
            </button>
            {armed ? (
              <button type="button" className={styles.action} onClick={() => setArmed(false)}>
                {CANCEL_KO}
              </button>
            ) : null}
          </span>
        </div>
        <p className={styles.caption}>{DELETE_ACCOUNT_NOTE_KO}</p>
      </CraftPanel>
    </div>
  );
}
