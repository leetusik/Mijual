import { KST_KO } from "@/lib/copy";
import styles from "./DDay.module.css";

/**
 * The countdown badge.
 *
 * **Every value here is computed upstream in KST and served whole.** `dday` is
 * `mijual.calc.DDay.label` (`D-5` / `D-DAY` / `D+41`), `days` is the signed
 * integer beside it and `date` is a bare calendar day — all three arrive on the
 * payload's `countdown` object, and this component does no date arithmetic
 * whatsoever. It cannot: the browser's clock is not Asia/Seoul, and a D-day
 * derived locally would disagree with the one the mail, the board and the ops
 * panel all read from `mijual.present` (D-10; `frontend` v0002).
 *
 * Urgency is **colour only, never size** (R1 revision 1): one fixed 17px mono
 * weight 600, four inks, and a fill at D-DAY.
 *
 * `showDate` is `false` where the surface already carries the date in its own
 * column — R2's board row puts `countdown label + date` in column 3 and the DDay
 * in column 5, so repeating it would print the same date twice on one row.
 */
export type DDayProps = {
  /** `countdown.dday` — the label the server computed. Never derived here. */
  dday: string;
  /** `countdown.days` — signed, KST. Chooses the ink; never re-computed. */
  days: number;
  /** `countdown.date` — a bare `YYYY-MM-DD`. */
  date?: string | null;
  /** Render the date + KST line under the label. */
  showDate?: boolean;
  className?: string;
};

/** The urgency ink for a signed day count. R1's ladder, and nothing else. */
export function urgencyClass(days: number): string {
  if (days < 0) return styles.past;
  if (days === 0) return styles.now;
  if (days <= 7) return styles.soon;
  if (days <= 30) return styles.near;
  return styles.far;
}

export function DDay({ dday, days, date, showDate = true, className }: DDayProps) {
  return (
    <span className={className ? `${styles.dday} ${className}` : styles.dday}>
      <span className={`${styles.label} ${urgencyClass(days)}`}>{dday}</span>
      {showDate && date ? (
        <span className={styles.date}>
          {date} {KST_KO}
        </span>
      ) : null}
    </span>
  );
}
