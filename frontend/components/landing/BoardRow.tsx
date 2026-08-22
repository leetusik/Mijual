import Link from "next/link";
import { DDay, RightsChip, StateBadge } from "@/components";
import { dartUrl } from "@/lib/api";
import { eventPath } from "@/lib/routes";
import type { BoardRow as Row } from "@/lib/types";
import { DART_LINK_KO, PRICE_PENDING_KO, SUBSCRIPTION_PREFIX_KO } from "./copy";
import styles from "./Board.module.css";

/**
 * One board row (R2 §Board), and the same anatomy the two pinned strips expand
 * into.
 *
 * > **Row** (desktop grid `86px 1fr 300px 230px 96px`, 9px v-pad, dashed
 * > `--border-soft` separators): RightsChip compact | corp 600 + `↗` link to
 * > DART (mono 11 `--ink-3`) | countdown label + date (label 12px `--ink-2`, date
 * > mono `--ink-1`) | per-type extras | DDay right-aligned (showDate=false; date
 * > lives in col 3).
 * >
 * > **Extras col**: ① pre-fixing = `청약 YYYY-MM-DD` (mono) + chip `발행가 확정
 * > 전` (sans 11, `--surface-inset`, 2×8). ②/③ = empty — **absence is the design,
 * > no dash.**
 *
 * Three readings this file carries out, each recorded in `phase.md`:
 *
 * 1. **The 청약 date is the window's 마감** (`subscription_end`). The payload
 *    carries the whole 구주주 window because the record does not say which end it
 *    means (`P5.S3` note 10); every other 청약 date this product prints is the
 *    closing one, and the 소멸주의보 strip on this same page prints it for these
 *    same offerings — two different 청약 dates for 계양전기 on one page would be
 *    the page contradicting itself.
 * 2. **The corp name links to the event's detail page.** R2 gives the row the
 *    `↗` DART link and no other href, but R3's detail page opens with the crumb
 *    "← 관제 현황판" and its 추후결정 strip says "expanded rows link to detail" —
 *    the board is where a reader comes from. The `↗` keeps its own job (the 원문
 *    on DART) and the name keeps its weight; only the href is new.
 * 3. **A row with no countdown date renders `StateBadge tbd`**, never a dash and
 *    never a date: 추후결정 means *no date* (`ui-traps.md` #4).
 */
export function BoardRow({ row }: { row: Row }) {
  const countdown = row.countdown;
  const name = row.corp_name ?? row.corp_code;
  const offering = row.offering;
  const subscription = offering?.subscription_end ?? offering?.subscription_start;

  return (
    <li className={styles.row}>
      <RightsChip rightsType={row.rights_type} compact className={styles.chip} />

      <div className={styles.corpCell}>
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
      </div>

      <div className={styles.meta}>
        <div className={styles.when}>
          <span className={styles.whenLabel}>{countdown.label_ko}</span>
          {countdown.date ? <span className={`mono ${styles.whenDate}`}>{countdown.date}</span> : null}
        </div>

        {/* ②/③ carry no `offering` at all, so this cell renders empty — the
            absence is the design. */}
        <div className={styles.extras}>
          {subscription ? (
            <span className={`mono ${styles.subscription}`}>
              {SUBSCRIPTION_PREFIX_KO} {subscription}
            </span>
          ) : null}
          {offering && offering.price_confirmed === false ? (
            <span className={styles.pricePending}>{PRICE_PENDING_KO}</span>
          ) : null}
        </div>
      </div>

      <div className={styles.ddayCell}>
        {countdown.dday !== null && countdown.days !== null ? (
          <DDay dday={countdown.dday} days={countdown.days} showDate={false} />
        ) : (
          <StateBadge kind="tbd" />
        )}
      </div>
    </li>
  );
}
