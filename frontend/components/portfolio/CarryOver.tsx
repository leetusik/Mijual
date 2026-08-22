"use client";

import { count } from "@/lib/format";
import { DISCARD_KO, KEEP_KO, MIGRATE_LABEL_KO, SHARES_UNIT_KO, carryOverKo } from "./copy";
import styles from "./Portfolio.module.css";

/** One thing that could be carried into the account: an issuer and a count. */
export type CarryEntry = { corp_code: string; corp_name?: string | null; shares: number };

/**
 * 세션 이월 제안 (R5-3) and the 샘플 → 계정 이전 offer (R5-4) — **offers, never
 * transfers**.
 *
 * > **R5-3 · 세션 보유량 이월** — 제안으로만: 빈 포트폴리오에 inset 행 "조회에서
 * > 입력한 계양전기 500주가 이 세션에 남아 있습니다" + 담기/담지 않기. **자동 저장
 * > 없음** (R4-6 restore-chip 패턴 재사용). … 담지 않기 → 세션 값 유지.
 * > **R5-4** — 편집 가능 + localStorage 저장 …; 로그인 시 **이전 제안** →
 * > conversion offer.
 *
 * Both are the same shape and the same promise: the browser holds a number the
 * server has never seen (조회's `sessionStorage`, or a sample's `localStorage`),
 * the surface *says so* and offers to keep it, and nothing moves unless the
 * reader presses 담기 — at which point it becomes an ordinary authenticated
 * `POST /portfolio/holdings`. There is no anonymous write endpoint to do it any
 * other way, and `security` requires exactly this ("Anonymous state never reaches
 * the server … Migration into an account is offered, never automatic").
 *
 * 담지 않기 dismisses the offer and **keeps the browser's value** — the round says
 * so for the session case, and it is the same courtesy for the sample: declining
 * to copy something is not deleting it.
 *
 * The `migrate` variant carries no sentence, because R5 signs none for it: it
 * renders the round's own noun as a label (`MIGRATE_LABEL_KO`), the data (종목명 +
 * 주수) and the two signed controls. See `copy.ts`'s header.
 */
export function CarryOver({
  variant,
  entries,
  busy,
  onKeep,
  onDiscard,
}: {
  variant: "session" | "migrate";
  entries: CarryEntry[];
  busy: boolean;
  onKeep: (entries: CarryEntry[]) => void;
  onDiscard: () => void;
}) {
  if (entries.length === 0) return null;

  return (
    <div className={styles.carry}>
      {variant === "migrate" ? <p className={styles.carryLabel}>{MIGRATE_LABEL_KO}</p> : null}

      <ul className={styles.carryList}>
        {entries.map((entry) => (
          <li key={entry.corp_code} className={styles.carryRow}>
            {variant === "session" ? (
              carryOverKo(entry.corp_name ?? entry.corp_code, count(entry.shares))
            ) : (
              <>
                {entry.corp_name ?? entry.corp_code}{" "}
                <span className="mono">{count(entry.shares)}</span>
                {SHARES_UNIT_KO}
              </>
            )}
          </li>
        ))}
      </ul>

      <div className={styles.carryActions}>
        <button
          type="button"
          className={styles.action}
          disabled={busy}
          onClick={() => onKeep(entries)}
        >
          {KEEP_KO}
        </button>
        <button type="button" className={styles.action} onClick={onDiscard}>
          {DISCARD_KO}
        </button>
      </div>
    </div>
  );
}
