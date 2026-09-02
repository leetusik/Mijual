import Link from "next/link";
import { DDay, RightsChip, StateBadge } from "@/components";
import { dartUrl } from "@/lib/api";
import { eventPath } from "@/lib/routes";
import type { LandingRow as Row } from "@/lib/types";
import { DART_LINK_KO, PRICE_PENDING_KO, SUBSCRIPTION_PREFIX_KO } from "./copy";
import styles from "./Board.module.css";

/**
 * Which of a row's values a refresh replaced (R9 §7). Only these fade in; the
 * row's `--live` edge is `Board`'s.
 */
export type RowChange = {
  when: boolean;
  extras: boolean;
  dday: boolean;
};

/**
 * One board row (R2 §Board, re-cut by R9 §2–§3), and the same anatomy the two
 * pinned strips expand into.
 *
 * > **Row** (desktop grid `76px minmax(180px,1fr) 240px 190px 96px`, gap 12,
 * > `min-height:44px`, `align-items:center`, 8×12 padding on a −12 inline
 * > margin, dashed `--border-soft` separators): RightsChip compact | corp 600 +
 * > `↗` link to DART (mono 11 `--ink-3`) | countdown label + date (label 12px
 * > `--ink-2`, date mono `--ink-1`, `nowrap`) | per-type extras | DDay
 * > right-aligned in the row's last cell (`showDate=false`).
 * >
 * > **Extras col**: ① pre-fixing = `청약 YYYY-MM-DD` (mono) + chip `발행가 확정
 * > 전` (sans 11, `--surface-inset`, 2×8). ②/③ = empty — **absence is the design,
 * > no dash** — and when *no* row of the panel carries extras the column is not
 * > drawn at all (`Board`'s `data-extras`).
 *
 * The components and their order are R2's and are unchanged; R9 changed the
 * column widths, gave the row its states, and settled two things this file
 * carries out:
 *
 * 1. **The whole row is the event's click target** (walk finding 1). The corp
 *    anchor is stretched over the row in CSS (`a.corp::after`), so the row has
 *    exactly one link, its accessible name is still the company's, and the `↗`
 *    stays above it with its own job — the 원문 on DART. A row with **no filing
 *    number** keeps the plain `span`: there is no detail page to open, so there
 *    is nothing to stretch.
 * 2. **A row with no countdown date renders the label alone** — no empty date
 *    slot and no dash (walk finding 5) — and the rail answers 「언제」 with
 *    `StateBadge tbd`. 추후결정 means *no date* (`ui-traps.md` #4), while
 *    `발행가 확정 전` is a known-later fact and stays in the extras cell.
 *
 * The 청약 date is the window's **마감** (`subscription_end`): the payload carries
 * the whole 구주주 window because the record does not say which end it means
 * (`P5.S3` note 10), every other 청약 date this product prints is the closing one,
 * and the 소멸주의보 strip on this same page prints it for these same offerings.
 */
export function BoardRow({ row, changed }: { row: Row; changed?: RowChange }) {
  const countdown = row.countdown;
  const name = row.corp_name ?? row.corp_code;
  const offering = row.offering;
  const subscription = offering?.subscription_end ?? offering?.subscription_start;

  return (
    <li
      className={changed ? `${styles.row} ${styles.changed}` : styles.row}
      // The refresh replaces rows in place by `event_id` (R9 §7); this is the
      // same identity in the DOM, so a focused row that *vanished* can be told
      // apart from one that merely moved.
      data-event-id={row.event_id}
    >
      <span className={styles.top}>
        <RightsChip rightsType={row.rights_type} compact className={styles.chip} />

        <span className={styles.corpCell}>
          {row.rcept_no ? (
            <Link className={styles.corp} href={eventPath(row.rcept_no)}>
              {name}
            </Link>
          ) : (
            <span className={styles.corp}>{name}</span>
          )}
          {row.rcept_no ? (
            <a
              className={styles.dart}
              href={dartUrl(row.rcept_no)}
              target="_blank"
              rel="noreferrer"
              aria-label={`${name} ${DART_LINK_KO}`}
            >
              ↗
            </a>
          ) : null}
        </span>
      </span>

      <span className={styles.rmeta}>
        <span className={styles.when} data-changed={changed?.when ? "true" : undefined}>
          <span className={styles.whenLabel}>{countdown.label_ko}</span>
          {countdown.date ? <span className={`mono ${styles.whenDate}`}>{countdown.date}</span> : null}
        </span>

        {/* ②/③ carry no `offering` at all, so this cell renders empty — the
            absence is the design. On a panel where *nothing* carries extras the
            cell is removed by CSS instead, so no empty track survives. */}
        <span className={styles.extras} data-changed={changed?.extras ? "true" : undefined}>
          {subscription ? (
            <span className={`mono ${styles.subscription}`}>
              {SUBSCRIPTION_PREFIX_KO} {subscription}
            </span>
          ) : null}
          {offering && offering.price_confirmed === false ? (
            <span className={styles.pricePending}>{PRICE_PENDING_KO}</span>
          ) : null}
        </span>
      </span>

      <span className={styles.rail} data-changed={changed?.dday ? "true" : undefined}>
        {countdown.dday !== null && countdown.days !== null ? (
          <DDay dday={countdown.dday} days={countdown.days} showDate={false} />
        ) : (
          <StateBadge kind="tbd" />
        )}
      </span>
    </li>
  );
}
