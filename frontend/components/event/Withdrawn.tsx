import { Citation, StateBadge } from "@/components";
import type { EventDetail } from "@/lib/types";
import { CORRECTION_TABLE_KO } from "./copy";
import styles from "./Event.module.css";

/**
 * The 철회 page (R3 §State pages).
 *
 * > **철회** (`state: withdrawn`): `StateBadge withdrawn-r{n}` replaces the body
 * > (locked notice per type). Below it only: one sentence naming the 정정사항-table
 * > evidence + a `Citation` with the withdrawal quote. **No fields, no
 * > countdown, no old dates.**
 *
 * That rule is already a *payload* rule, not only a rendering one: a withdrawn
 * event comes back with no fields, no 환산 블록, no ② strip and no 정정 teaser
 * (`P5.S3` note 6), so there is nothing here to suppress — the surface renders
 * what it is given and the given is the notice plus its evidence.
 *
 * The evidence is the filing's own `3. 정정사항` row — 항목 · 정정 전 → 정정 후 —
 * re-read from the stored bytes so the citation has parts to point at. The
 * quote is the 정정 후 cell itself, at the span it was read from, which is what
 * makes 「이 유상증자는 철회되었습니다」 a cited statement rather than an
 * assertion. The evidence line is composed of served strings only: the card's
 * own sentence is not in the landed record (`P5.S19` checks it against the
 * card), and writing one here would be inventing product copy.
 */
export function Withdrawn({ detail }: { detail: EventDetail }) {
  const withdrawal = detail.withdrawal;

  return (
    <section className={styles.withdrawn}>
      <StateBadge
        kind="withdrawn"
        rightsType={detail.rights_type}
        noticeKo={detail.notice_ko}
        className={styles.notice}
      />

      {withdrawal ? (
        <div className={styles.evidence}>
          <p className={styles.evidenceLine}>
            <span className={styles.chainLabel}>{CORRECTION_TABLE_KO}</span>
            {withdrawal.item ? <span>{withdrawal.item}</span> : null}
            {withdrawal.before && withdrawal.after ? (
              <span className={styles.evidenceMove}>
                {withdrawal.before} → {withdrawal.after}
              </span>
            ) : null}
          </p>
          <Citation
            rceptNo={withdrawal.rcept_no}
            quote={withdrawal.after}
            span={withdrawal.span}
            label={CORRECTION_TABLE_KO}
          />
        </div>
      ) : null}
    </section>
  );
}
