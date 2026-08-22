import Link from "next/link";
import { CraftPanel, DDay, EstimateMarker, RightsChip, StateBadge } from "@/components";
import { count, won } from "@/lib/format";
import { eventPath } from "@/lib/routes";
import type { ConvertibleView, RightsRow, StockPage } from "@/lib/types";
import { Conversion } from "./Conversion";
import {
  CONVERSION_OPEN_KO,
  CONVERSION_PRICE_KO,
  CONVERTED_SHARES_KO,
  DETAIL_LINK_KO,
  OVERHANG_KO,
  RCEPT_NO_KO,
  RIGHTS_SECTION_KO,
  SHARES_UNIT_KO,
  STEP_DEPENDENCY_KO,
  subscriptionClosedKo,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * 진행 중인 권리 — N건 (R4 §Page anatomy 4).
 *
 * > One panel per live event, most urgent first. Each: RightsChip + 종목/건
 * > title + "상세 보기 →" (event detail) + rcept_no meta; right: governing label
 * > + upstream DDay + window line (live green when open).
 *
 * **The order is the server's** (`_live_rank`, `P5.S4` note 4): upcoming D-day
 * ascending → ② 진행 중 (opened, not closed) most-recently-opened first → 일정
 * 추후결정, unranked and last. A deadline you can still act on outranks an open
 * window with nothing to exercise (R4-4), and past ①/③ are absent — a past ①
 * reappears below with its 소멸 계산, the only honest place for it.
 *
 * Nothing here computes a date: `dday`, `days`, `date` and `window` are all
 * served, computed upstream in KST (D-10).
 */
export function RightsSection({ page, shares }: { page: StockPage; shares: number | null }) {
  const rows = page.rights.rows;
  const stockName = page.stock.corp_name ?? page.stock.corp_code;

  return (
    <section className={styles.section}>
      <h2 className={styles.eyebrow}>
        {`// ${RIGHTS_SECTION_KO} — ${count(page.rights.count)}건`}
      </h2>

      {rows.length === 0 ? (
        // 0건 is a fact, not an absence to apologise for. Where the stock's
        // offering has simply closed, the card states that ("청약 2026-07-23
        // 종료", `lookup/LookupMobile.html`) instead of leaving the section bare.
        <div className={styles.closedLines}>
          {page.lapse.rows
            .map((row) => row.lapse.subscription_end)
            .filter((end): end is string => Boolean(end))
            .map((end) => (
              <p key={end} className={styles.closedLine}>
                {subscriptionClosedKo(end)}
              </p>
            ))}
        </div>
      ) : (
        <ul className={styles.panels}>
          {rows.map((row) => (
            <RightsPanel
              key={row.event_id}
              row={row}
              stockName={row.corp_name ?? stockName}
              shares={shares}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

function RightsPanel({
  row,
  stockName,
  shares,
}: {
  row: RightsRow;
  stockName: string;
  shares: number | null;
}) {
  const countdown = row.countdown;
  const [windowStart, windowEnd] = countdown.window;
  const open = countdown.window_state === "open";

  return (
    <CraftPanel as="li" className={styles.panel}>
      <div className={styles.panelHead}>
        <div className={styles.panelIdentity}>
          <RightsChip rightsType={row.rights_type} />
          <p className={styles.panelTitle}>{stockName}</p>
          {row.rcept_no ? (
            <p className={`mono ${styles.panelMeta}`}>
              {RCEPT_NO_KO} {row.rcept_no}
            </p>
          ) : null}
        </div>

        <div className={styles.panelWhen}>
          <p className={styles.whenLabel}>{countdown.label_ko}</p>
          {countdown.dday !== null && countdown.days !== null ? (
            <DDay
              className={styles.panelDDay}
              dday={countdown.dday}
              days={countdown.days}
              date={countdown.date}
            />
          ) : (
            // 추후결정 means *no date* — never a dash, never the date it replaced.
            <StateBadge kind="tbd" />
          )}
          {windowStart && windowEnd ? (
            <p className={`mono ${styles.windowLine} ${open ? styles.live : ""}`}>
              {windowStart} ~ {windowEnd}
              {/* A past ② opening is 진행 중, never 종료 (`ui-traps.md` #5). */}
              {open && row.rights_type === "R2" ? ` · ${CONVERSION_OPEN_KO}` : ""}
            </p>
          ) : null}
        </div>
      </div>

      {row.rights_type === "R1" && row.offering ? (
        <Conversion
          factors={row.offering}
          shares={shares}
          finalPriceDate={row.offering.final_price_date}
          confirmedPrice={row.offering.confirmed_price}
        />
      ) : null}

      {row.rights_type === "R2" && row.convertible ? (
        <Dilution view={row.convertible} />
      ) : null}

      {/* ③: the 2단계 dependency line, and nothing a holder could mistake for a
          payout. 매수예정가 is R3's detail-page field and is deliberately not on
          this surface's contract (R4 §②/③; `P5.S8` note 6 records the same
          boundary for 내 포트폴리오). */}
      {row.rights_type === "R3" ? <p className={styles.dependency}>{STEP_DEPENDENCY_KO}</p> : null}

      {row.rcept_no ? (
        <Link className={styles.detailLink} href={eventPath(row.rcept_no)}>
          {DETAIL_LINK_KO}
        </Link>
      ) : null}
    </CraftPanel>
  );
}

/**
 * ②'s dilution context (R4 §②/③, decision R4-4).
 *
 * > **②**: RightsChip + 전환청구 개시 DDay (past opening = "진행 중", never
 * > 종료) + dilution context from API-tier facts (오버행 %, 전환 시 주식수,
 * > 전환가액). No per-holding math — there is nothing a holder exercises.
 *
 * Exactly those three of the strip's six: the round names them, and "Both link
 * out to detail for everything else". Every one is a **fact** from the
 * `cvbdIsDecsn` API row, so none carries the estimate mark and none carries a
 * `[근거]` chip — an API row has no character offsets, and its citation is the
 * filing number the panel already prints (`P5.S3` note 7).
 *
 * 전환가액 is a disclosed per-share price, which is why it survives R4's
 * "②/③ rows never carry a won amount": that rule is about the **per-holding**
 * conversion, and R5 later restates this very strip as ②'s substitute for it
 * ("금액 = R4 계약 그대로", `P5.S8` note 6). No holding is multiplied here.
 */
export function Dilution({ view }: { view: ConvertibleView }) {
  const cells: Array<{ label: string; value: string; estimated: boolean }> = [];

  if (view.overhang_pct) {
    cells.push({
      label: OVERHANG_KO,
      value: `${view.overhang_pct.value}%`,
      estimated: view.overhang_pct.estimated,
    });
  }
  if (view.shares) {
    cells.push({
      label: CONVERTED_SHARES_KO,
      value: `${count(view.shares.value)}${SHARES_UNIT_KO}`,
      estimated: view.shares.estimated,
    });
  }
  if (view.conversion_price) {
    cells.push({
      label: CONVERSION_PRICE_KO,
      value: won(view.conversion_price.value),
      estimated: view.conversion_price.estimated,
    });
  }

  if (cells.length === 0) return null;

  return (
    <div className={styles.dilution}>
      {cells.map((cell) => (
        <p key={cell.label} className={styles.factor}>
          <span className={styles.factorLabel}>{cell.label}</span>
          <EstimateMarker estimated={cell.estimated}>
            <span className="mono">{cell.value}</span>
          </EstimateMarker>
        </p>
      ))}
    </div>
  );
}
