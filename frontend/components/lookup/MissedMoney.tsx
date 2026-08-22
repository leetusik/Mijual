import Link from "next/link";
import { Citation, EstimateMarker, StateBadge } from "@/components";
import { count, percent, won } from "@/lib/format";
import { convert, sumValues } from "@/lib/holding";
import { eventPath } from "@/lib/routes";
import type { Disagreement, LapseBreakdownRow, LapseResult, StockPage } from "@/lib/types";
import {
  COL_LAPSE_KO,
  COL_OFFERING_KO,
  COL_TRADING_KO,
  CONFIRMED_PRICE_KO,
  DISCLAIMER_KO,
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
  ZERO_MISSED_KO,
  calcFooterKo,
  coverageCaptionKo,
  lapseCalcKo,
  pastPeriodChipKo,
  pendingLapseKo,
  perHoldingCaption,
  perHoldingColumnKo,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * 2026년 놓친 돈 (R4 §Page anatomy 5, §놓친 돈 breakdown).
 *
 * > **Total headline**: conditional frame line "청약도 매도도 하지 않았다면,
 * > 2026년 이 종목에서 사라진 가치" → `EstimateMarker` total (alert) + 하한
 * > (ink-2) + coverage caption. Total = Σ per-offering values for this stock
 * > within coverage.
 *
 * ## Three rules this section is built to keep
 *
 * 1. **The total is the reader's own**, summed from the same per-offering
 *    conversion each row shows — `lib/holding.ts`, once — so the headline can
 *    never disagree with the rows under it. Before a holding is entered there is
 *    nothing to state and the frame line does not appear: an empty field is not
 *    a zero, and "사라진 가치 0원" would be a claim about a holding the reader
 *    never described.
 * 2. **Coverage is served, not assumed** (`lapse.coverage`, decision R4-3).
 *    There is no 기간 input, and a figure outside the range is *absent* — the
 *    server omits the row rather than counting it as 0.
 * 3. **A row states only what its own filing attests.** A 유상증자결정 that is
 *    not exposable keeps its 소멸 계산 (the 실적보고서 attests it) and loses the
 *    매매기간 line, the quote and the 상세 보기 link (`P5.S4` note 6) — nothing
 *    is invented to fill the cells.
 */
export function MissedMoney({ page, shares }: { page: StockPage; shares: number | null }) {
  const { coverage, rows, totals, pending } = page.lapse;

  // Each row's own conversion, kept beside the row so the headline is literally
  // the sum of what is rendered.
  const converted = rows.map((row) => ({ row, conversion: convert(row.lapse, shares) }));
  const total = sumValues(
    converted.map(({ conversion }) => conversion.value).filter((value): value is string => value !== null),
  );
  const floor = sumValues(
    converted
      .map(({ conversion }) => conversion.valueFloor)
      .filter((value): value is string => value !== null),
  );
  const estimated = converted.some(({ conversion }) => conversion.valueEstimated);

  return (
    <section className={styles.section}>
      <h2 className={styles.eyebrow}>{`// ${MISSED_SECTION_KO}`}</h2>

      {totals.offerings === 0 ? (
        <div className={styles.zero}>
          <p className={styles.zeroLine}>{ZERO_MISSED_KO}</p>
          {/* A live ① whose 청약 has not closed yet is not a zero either — it is
              not counted *yet*, and the line says when it will be. */}
          {pending ? <p className={styles.caption}>{pendingLapseKo(pending.subscription_end)}</p> : null}
          <p className={styles.caption}>{coverageCaptionKo(coverage.start)}</p>
        </div>
      ) : (
        <>
          {total !== null && shares !== null ? (
            <div className={styles.total}>
              <p className={styles.frame}>{MISSED_FRAME_KO}</p>
              <p className={styles.totalValue}>
                <EstimateMarker estimated={estimated}>
                  <span className={`mono ${styles.totalAmount}`}>{won(total)}</span>
                </EstimateMarker>
                {floor !== null ? (
                  <span className={styles.floor}>
                    {LAPSE_FLOOR_KO}{" "}
                    <EstimateMarker estimated={estimated}>
                      <span className="mono">{won(floor)}</span>
                    </EstimateMarker>
                  </span>
                ) : null}
              </p>
              <p className={styles.caption}>{coverageCaptionKo(coverage.start)}</p>
            </div>
          ) : (
            <p className={styles.caption}>{coverageCaptionKo(coverage.start)}</p>
          )}

          <div className={styles.grid} role="table">
            <div className={styles.gridHead} role="row">
              <span role="columnheader">{COL_OFFERING_KO}</span>
              <span role="columnheader">{COL_TRADING_KO}</span>
              <span role="columnheader">{COL_LAPSE_KO}</span>
              <span role="columnheader">
                {shares !== null ? perHoldingColumnKo(count(shares)) : ""}
              </span>
            </div>

            {converted.map(({ row, conversion }) => (
              <BreakdownRow
                key={row.lapse.performance_rcept_no ?? row.lapse.decision_rcept_no ?? row.rights_type}
                row={row}
                shares={shares}
                allotted={conversion.allotted}
                value={conversion.value}
                valueEstimated={conversion.valueEstimated}
              />
            ))}
          </div>

          {pending ? <p className={styles.caption}>{pendingLapseKo(pending.subscription_end)}</p> : null}
          <p className={styles.disclaimer}>{DISCLAIMER_KO}</p>
        </>
      )}
    </section>
  );
}

function BreakdownRow({
  row,
  shares,
  allotted,
  value,
  valueEstimated,
}: {
  row: LapseBreakdownRow;
  shares: number | null;
  allotted: number | null;
  value: string | null;
  valueEstimated: boolean;
}) {
  const lapse: LapseResult = row.lapse;
  const countdown = row.countdown;
  const period = row.warrant_trading_period;
  const disagreement = row.issuer_disagreement;
  const [windowStart, windowEnd] = countdown?.window ?? [undefined, undefined];
  const ratio = lapse.allotment_ratio;

  return (
    <div className={styles.gridRow} role="row">
      {/* 유상증자 — the offering's own identity: who filed it, under which
          number, at which 확정발행가. */}
      <div className={styles.cell} role="cell">
        <span className={styles.cellLabel}>{COL_OFFERING_KO}</span>
        <p className={styles.cellTitle}>{lapse.corp_name ?? row.rights_type}</p>
        {lapse.decision_rcept_no ? (
          <p className={`mono ${styles.cellMeta}`}>
            {RCEPT_NO_KO}{" "}
            {countdown && row.rcept_no ? (
              <Link className={styles.metaLink} href={eventPath(row.rcept_no)}>
                {lapse.decision_rcept_no}
              </Link>
            ) : (
              lapse.decision_rcept_no
            )}
          </p>
        ) : null}
        {lapse.confirmed_price ? (
          <p className={styles.cellLine}>
            <span className={styles.factorLabel}>{CONFIRMED_PRICE_KO}</span>
            <EstimateMarker estimated={lapse.confirmed_price.estimated}>
              <span className="mono">{won(lapse.confirmed_price.value)}</span>
            </EstimateMarker>
          </p>
        ) : null}
      </div>

      {/* 증서 매매기간 — the window, and the faint history chip. Absent entirely
          when the 유상증자결정 is not renderable: no window, no quote, no link. */}
      <div className={styles.cell} role="cell">
        <span className={styles.cellLabel}>{COL_TRADING_KO}</span>
        {windowStart && windowEnd ? (
          <p className={`mono ${styles.cellLine}`}>
            {windowStart} ~ {windowEnd}
          </p>
        ) : null}
        {countdown?.dday ? (
          // Faint, never alert-coloured: --alert means expiring/lost, and this
          // period is simply history (R2/R3's treatment, R4 restates it).
          <span className={styles.pastChip}>{pastPeriodChipKo(countdown.dday)}</span>
        ) : null}
        {period ? (
          <Citation
            className={styles.cellCite}
            rceptNo={period.rcept_no}
            quote={period.quote}
            span={period.span}
            label={period.korean_name}
          />
        ) : null}
      </div>

      {/* 소멸 계산 — the market-wide outcome, which does not depend on any
          holding. The counts are the 실적보고서's own facts; the value is
          derived and therefore always tagged. */}
      <div className={styles.cell} role="cell">
        <span className={styles.cellLabel}>{COL_LAPSE_KO}</span>
        {lapse.lapsed ? (
          <p className={styles.cellLine}>
            <span className="mono">
              {lapseCalcKo(
                count(lapse.lapsed.value),
                lapse.lapse_rate ? percent(lapse.lapse_rate.value, 2) : "",
              )}
            </span>
          </p>
        ) : null}
        {lapse.value ? (
          <p className={styles.cellLine}>
            <EstimateMarker estimated={lapse.value.estimated}>
              <span className="mono">{won(lapse.value.value)}</span>
            </EstimateMarker>
          </p>
        ) : null}
        {disagreement ? <Mismatch disagreement={disagreement} /> : null}
      </div>

      {/* N주 기준 — the reader's own number, and the caption that shows its two
          factors. Nothing here without a holding. */}
      <div className={styles.cell} role="cell">
        {shares !== null && value !== null && allotted !== null ? (
          <>
            <span className={styles.cellLabel}>{perHoldingColumnKo(count(shares))}</span>
            <p className={styles.cellLine}>
              <EstimateMarker estimated={valueEstimated}>
                <span className={`mono ${styles.holdingAmount}`}>{won(value)}</span>
              </EstimateMarker>
            </p>
            {lapse.unit_value ? (
              <p className={styles.caption}>
                {perHoldingCaption.before}
                <span className="mono">{count(allotted)}</span>
                {perHoldingCaption.between}
                {/* The unit carries its own 원 *inside* the marker: the record
                    writes the tag before the number ("× 「추정」{unit}원") while
                    R1's primitive puts it after the value it tags, so the tag
                    must not land between the figure and its unit. */}
                <EstimateMarker estimated={lapse.unit_value.estimated}>
                  <span className="mono">
                    {count(lapse.unit_value.value)}
                    {perHoldingCaption.after}
                  </span>
                </EstimateMarker>
              </p>
            ) : null}
          </>
        ) : null}
      </div>

      {/* The calc footer states this row's own arithmetic — the offerings of one
          stock do not share a 배정비율, so one footer for several rows would
          print one row's factor as if it covered the others. */}
      {shares !== null && allotted !== null && ratio ? (
        <p className={styles.calcFooter}>
          {calcFooterKo(count(allotted), count(shares), String(ratio.value))}
        </p>
      ) : null}
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
    <div className={styles.mismatch}>
      <StateBadge kind="mismatch" />
      <p className={styles.caption}>{MISMATCH_HEADER_KO}</p>
      {disagreement.readings.map((reading) => (
        <p key={reading.key} className={styles.cellLine}>
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
        </p>
      ))}
      <p className={styles.caption}>{MISMATCH_FOOTER_KO}</p>
    </div>
  );
}
