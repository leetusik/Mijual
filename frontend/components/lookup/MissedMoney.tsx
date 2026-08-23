import type { ReactNode } from "react";
import Link from "next/link";
import { Citation, CraftPanel, EstimateMarker, RightsChip, StateBadge } from "@/components";
import { count, percent, won } from "@/lib/format";
import { convert, sumValues } from "@/lib/holding";
import { eventPath } from "@/lib/routes";
import type { Disagreement, LapseBreakdownRow, LapseResult, StockPage } from "@/lib/types";
import {
  COL_LAPSE_MARKET_KO,
  COL_OFFERING_KO,
  COL_TRADING_KO,
  CONFIRMED_PRICE_KO,
  DETAIL_LINK_KO,
  DISCLAIMER_KO,
  HOLDING_LABEL_KO,
  LAPSE_FLOOR_KO,
  MISMATCH_DERIVED_KO,
  MISMATCH_FOOTER_KO,
  MISMATCH_HEADER_KO,
  MISSED_FRAME_KO,
  MISSED_SECTION_KO,
  RCEPT_NO_KO,
  SHARES_UNIT_KO,
  WARRANTS_EXERCISED_KO,
  WARRANTS_ISSUED_KO,
  WARRANTS_LAPSED_KO,
  ZERO_MISSED_KO,
  calcFooterKo,
  missedCaptionKo,
  pastPeriodChipKo,
  pendingLapseParts,
  perHoldingCaption,
  perHoldingColumnKo,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * 2026년 놓친 돈 (R4 §5, **re-cut by R11 §5**).
 *
 * ## Three rules this section was built to keep, and still keeps
 *
 * 1. **The figures are the reader's own**, from the same per-offering conversion
 *    each row shows — `lib/holding.ts`, once — so nothing here can disagree with
 *    anything else on the page.
 * 2. **Coverage is served, not assumed** (`lapse.coverage`, R4-3). There is no
 *    기간 input, and a figure outside the range is *absent*: the server omits the
 *    row rather than counting it as 0.
 * 3. **A row states only what its own filing attests.** A 유상증자결정 that is not
 *    exposable keeps its 소멸 계산 (the 실적보고서 attests it) and loses the
 *    매매기간, the quote and the 상세 보기 link (`P5.S4` note 6).
 *
 * ## What R11 changed
 *
 * **The same won amount is never printed twice** (finding 4). R4 drew a headline
 * *and* a per-holding column, so 한화솔루션 at 500주 said 679,575원 in both. The
 * rule now: **the total is drawn only when there is more than one row to sum**.
 * On a single-offering stock that row's own cell *is* the headline — `text-2xl`,
 * alert, tagged, with its 하한 and its 배정 caption beneath it.
 *
 * **Before a holding, the section says why it is empty and what fills it.** R4
 * opened it with a coverage caption and a three-column table and nothing else; a
 * reader had no way to know a number was missing rather than zero. R11 puts the
 * frame sentence first, the **prompt** (a control, R11 §6) under it, 「보유 주식
 * 수」 as the last column's header, and a **dashed empty slot** in the cell —
 * never 0원, never a dash.
 *
 * **One way to the event**: 「상세 보기 →」 under the offering's name. The mono
 * 접수번호 stops being a link; it is an identifier, and the way to the filing is
 * the detail page and the `[근거]` popover.
 *
 * **`[근거]` sits inside the cell it cites** — the quote is the 신주인수권증서
 * 상장예정기간, so it belongs under the 증서 매매기간 window, not on a citation
 * line spanning the row.
 */
export function MissedMoney({
  page,
  shares,
  prompt,
}: {
  page: StockPage;
  shares: number | null;
  /** R11 §6's control, when no live ① block on this page carries it. */
  prompt?: ReactNode;
}) {
  const { coverage, rows, totals, pending } = page.lapse;

  // Each row's own conversion, kept beside the row so a headline is literally the
  // sum of what is rendered under it.
  const converted = rows.map((row) => ({ row, conversion: convert(row.lapse, shares) }));
  const total = sumValues(
    converted
      .map(({ conversion }) => conversion.value)
      .filter((value): value is string => value !== null),
  );
  const floor = sumValues(
    converted
      .map(({ conversion }) => conversion.valueFloor)
      .filter((value): value is string => value !== null),
  );
  const estimated = converted.some(({ conversion }) => conversion.valueEstimated);
  // R11 §5's total rule: a sum exists only where there is more than one thing to
  // sum. With one offering the row carries the headline instead.
  const single = rows.length === 1;
  const showTotal = rows.length >= 2 && shares !== null && total !== null;

  return (
    <section className={styles.section}>
      <h2 className={styles.eyebrow} aria-label={MISSED_SECTION_KO}>
        {MISSED_SECTION_KO}
      </h2>

      {totals.offerings === 0 ? (
        <CraftPanel>
          <div className={styles.zero}>
            <p className={styles.zerolead}>{ZERO_MISSED_KO}</p>
            {/* A live ① whose 청약 has not closed yet is not a zero either — it is
                not counted *yet*, and the line says when it will be. */}
            {pending ? (
              <p className={styles.zerosub}>
                {pendingLapseParts.before}
                <span className={styles.v}>{pending.subscription_end}</span>
                {pendingLapseParts.after}
              </p>
            ) : null}
          </div>
        </CraftPanel>
      ) : (
        <CraftPanel>
          <div className={styles.mmhead}>
            <p className={styles.frame}>{MISSED_FRAME_KO}</p>

            {showTotal ? (
              <p className={styles.total}>
                <EstimateMarker estimated={estimated}>
                  <span className={`mono ${styles.totalAmount}`}>{won(total)}</span>
                </EstimateMarker>
                {floor !== null ? (
                  <span className={styles.totalFloor}>
                    {LAPSE_FLOOR_KO}{" "}
                    <EstimateMarker estimated={estimated}>
                      <span className="mono">{won(floor)}</span>
                    </EstimateMarker>
                  </span>
                ) : null}
              </p>
            ) : null}

            {shares === null ? prompt : null}

            <p className={styles.mmcap}>
              {missedCaptionKo(count(rows.length), coverage.start)}
            </p>

            {/* A live ① whose 청약 has not closed is **not** in these figures yet,
                and R4's own line says when it will be. R11's card has no sample
                that is both lapsed and pending, so the line keeps R4's words and
                takes the caption tier beside the coverage it qualifies. */}
            {pending ? (
              <p className={styles.mmcap}>
                {pendingLapseParts.before}
                {pending.subscription_end}
                {pendingLapseParts.after}
              </p>
            ) : null}
          </div>

          <div className={styles.bkd}>
            <div className={`${styles.brow} ${styles.bhead}`}>
              <span>{COL_OFFERING_KO}</span>
              <span>{COL_TRADING_KO}</span>
              <span>{COL_LAPSE_MARKET_KO}</span>
              <span className={styles.r}>
                {shares !== null ? perHoldingColumnKo(count(shares)) : HOLDING_LABEL_KO}
              </span>
            </div>

            {converted.map(({ row, conversion }) => (
              <BreakdownRow
                key={rowKey(row)}
                row={row}
                shares={shares}
                single={single}
                allotted={conversion.allotted}
                value={conversion.value}
                valueFloor={conversion.valueFloor}
                valueEstimated={conversion.valueEstimated}
                floorEstimated={conversion.floorEstimated}
              />
            ))}
          </div>

          {/* The calc footer states a row's own arithmetic. The offerings of one
              stock do not share a 배정비율, so **one** footer for several rows
              would print one row's factor as if it covered the others — hence one
              band per row, which on a single-offering stock (the shape the round
              draws) is exactly the card's single foot. */}
          {shares !== null
            ? converted.map(({ row, conversion }) =>
                conversion.allotted !== null && row.lapse.allotment_ratio ? (
                  <p key={`foot-${rowKey(row)}`} className={styles.calcfoot}>
                    {calcFooterKo(
                      count(conversion.allotted),
                      count(shares),
                      String(row.lapse.allotment_ratio.value),
                    )}
                  </p>
                ) : null,
              )
            : null}

          <p className={styles.disc}>{DISCLAIMER_KO}</p>
        </CraftPanel>
      )}
    </section>
  );
}

function rowKey(row: LapseBreakdownRow): string {
  return row.lapse.performance_rcept_no ?? row.lapse.decision_rcept_no ?? row.rights_type;
}

function BreakdownRow({
  row,
  shares,
  single,
  allotted,
  value,
  valueFloor,
  valueEstimated,
  floorEstimated,
}: {
  row: LapseBreakdownRow;
  shares: number | null;
  single: boolean;
  allotted: number | null;
  value: string | null;
  valueFloor: string | null;
  valueEstimated: boolean;
  floorEstimated: boolean;
}) {
  const lapse: LapseResult = row.lapse;
  const countdown = row.countdown;
  const period = row.warrant_trading_period;
  const disagreement = row.issuer_disagreement;
  const [windowStart, windowEnd] = countdown?.window ?? [undefined, undefined];

  return (
    <div className={styles.brow}>
      {/* 유상증자 — what this row is, under which filing, at which 확정발행가. The
          corp name is the page's `h1` and is not repeated (R11 §4); the round's
          card titles the row by the offering's own 결의일, which this route does
          not serve, so the row is named by its kind (see `result.md`). */}
      <span className={styles.boff}>
        <RightsChip rightsType="R1" compact />
        <p className={styles.bofftitle}>{COL_OFFERING_KO}</p>
        <p className={styles.bmeta}>
          {lapse.decision_rcept_no ? (
            <>
              {RCEPT_NO_KO} {lapse.decision_rcept_no}
            </>
          ) : null}
          {lapse.decision_rcept_no && lapse.confirmed_price ? <br /> : null}
          {lapse.confirmed_price ? (
            <>
              {CONFIRMED_PRICE_KO} {won(lapse.confirmed_price.value)}
            </>
          ) : null}
        </p>
        {countdown && row.rcept_no ? (
          <Link className={styles.golink} href={eventPath(row.rcept_no)}>
            {DETAIL_LINK_KO}
          </Link>
        ) : null}
      </span>

      {/* 증서 매매기간 — the window, its faint history chip, and **this row's
          `[근거]`, inside the cell whose value it quotes**. Absent entirely when
          the 유상증자결정 is not renderable: no window, no quote, no link. */}
      <span className={styles.bwin}>
        {windowStart && windowEnd ? (
          <span className={styles.dates}>
            {windowStart} ~ {windowEnd}
          </span>
        ) : null}
        {countdown?.dday ? (
          // Faint, never alert-coloured: --alert means expiring/lost, and this
          // period is simply history (R2/R3's treatment, R4 and R11 restate it).
          <span className={styles.past}>{pastPeriodChipKo(countdown.dday)}</span>
        ) : null}
        {period ? (
          <Citation
            className={styles.bcite}
            rceptNo={period.rcept_no}
            quote={period.quote}
            span={period.span}
            label={period.korean_name}
          />
        ) : null}
      </span>

      {/* 소멸 계산 (시장 전체) — the outcome, which does not depend on any holding.
          The counts are the 실적보고서's own facts; the value is derived and
          therefore always tagged. */}
      <span className={styles.bcalc}>
        {lapse.warrants_issued && lapse.warrants_exercised ? (
          <span>
            {WARRANTS_ISSUED_KO}{" "}
            <span className={styles.v}>
              {count(lapse.warrants_issued.value)}
              {SHARES_UNIT_KO}
            </span>{" "}
            {/* R4's own operators, the same two `calcFooterKo` writes. */}−{" "}
            {WARRANTS_EXERCISED_KO}{" "}
            <span className={styles.v}>
              {count(lapse.warrants_exercised.value)}
              {SHARES_UNIT_KO}
            </span>
          </span>
        ) : null}
        {lapse.lapsed ? (
          <span>
            = {WARRANTS_LAPSED_KO}{" "}
            <span className={`${styles.v} ${styles.lapsed}`}>
              {count(lapse.lapsed.value)}
              {SHARES_UNIT_KO}
              {lapse.lapse_rate ? ` (${percent(lapse.lapse_rate.value, 2)})` : ""}
            </span>
            {lapse.value ? (
              <>
                {" · "}
                <EstimateMarker estimated={lapse.value.estimated}>
                  <span className="mono">{won(lapse.value.value)}</span>
                </EstimateMarker>
              </>
            ) : null}
          </span>
        ) : null}
        {disagreement ? <Mismatch disagreement={disagreement} /> : null}
      </span>

      {/* 내 기준 — the reader's own number, or the dashed slot that says there is
          not one yet. Never a 0원 and never a dash: a holding nobody described
          has no value, and saying "0" would be a claim about it. */}
      <span className={styles.bmine}>
        {shares !== null && value !== null && allotted !== null ? (
          <>
            <span className={single ? `${styles.v} ${styles.big}` : styles.v}>
              <EstimateMarker estimated={valueEstimated}>{won(value)}</EstimateMarker>
            </span>
            {single && valueFloor !== null ? (
              <p className={styles.floorline}>
                {LAPSE_FLOOR_KO}{" "}
                <EstimateMarker estimated={floorEstimated}>
                  <span className="mono">{won(valueFloor)}</span>
                </EstimateMarker>
              </p>
            ) : null}
            {lapse.unit_value ? (
              <p className={styles.cap}>
                {perHoldingCaption.before}
                {count(allotted)}
                {perHoldingCaption.between}
                {/* The unit carries its own 원 *inside* the marker: the record
                    writes the tag before the number ("× 「추정」{unit}원") while
                    R1's primitive puts it after the value it tags, so the tag
                    must not land between the figure and its unit. */}
                <EstimateMarker estimated={lapse.unit_value.estimated}>
                  {count(lapse.unit_value.value)}
                  {perHoldingCaption.after}
                </EstimateMarker>
              </p>
            ) : null}
          </>
        ) : (
          <span className={styles.bslot} aria-hidden="true" />
        )}
      </span>
    </div>
  );
}

/**
 * 발행사 기재 불일치, on a breakdown row (`ui-traps.md` #2).
 *
 * The rule is a **payload** rule, not a detail-page one (`P5.S4` note 9), so it
 * rides here too: both readings, each cited into the same filing, never
 * reconciled. The two counts render as they are served — a derived reading's
 * evidence is its own inputs (발행 − 청약 is a difference, not a sum), which is
 * why they are not passed as `Citation`'s `parts`.
 */
function Mismatch({ disagreement }: { disagreement: Disagreement }) {
  return (
    <span className={styles.mismatch}>
      <StateBadge kind="mismatch" />
      <span className={styles.cap}>{MISMATCH_HEADER_KO}</span>
      {disagreement.readings.map((reading) => (
        <span key={reading.key} className={styles.cellLine}>
          {/* The derived reading's own name is the footer sentence's own words —
              the same fallback R3's block uses, so one number is not left
              unlabelled beside a labelled one. */}
          <span className={styles.factorLabel}>
            {reading.label ?? (reading.inputs ? MISMATCH_DERIVED_KO : null)}
          </span>
          <EstimateMarker estimated={reading.estimated}>
            <span className="mono">
              {count(reading.value)}
              {SHARES_UNIT_KO}
            </span>
          </EstimateMarker>
          <Citation
            rceptNo={reading.rcept_no}
            quote={reading.quote}
            span={reading.span}
            parts={reading.parts}
            label={reading.label}
          />
          {reading.inputs ? (
            <span className={styles.mismatchInputs}>
              {reading.inputs.map((input, index) => (
                <span key={`${reading.key}-${index}`} className={styles.mismatchInput}>
                  <span className={styles.factorLabel}>
                    {index === 0 ? WARRANTS_ISSUED_KO : WARRANTS_EXERCISED_KO}
                  </span>
                  <span className="mono">
                    {count(input.value)}
                    {SHARES_UNIT_KO}
                  </span>
                  <Citation
                    rceptNo={input.rcept_no}
                    quote={input.quote}
                    span={input.span}
                    parts={input.parts}
                    label={index === 0 ? WARRANTS_ISSUED_KO : WARRANTS_EXERCISED_KO}
                  />
                </span>
              ))}
            </span>
          ) : null}
        </span>
      ))}
      <span className={styles.cap}>{MISMATCH_FOOTER_KO}</span>
    </span>
  );
}
