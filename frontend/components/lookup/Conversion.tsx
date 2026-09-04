import type { ReactNode } from "react";
import { Citation, EstimateMarker } from "@/components";
import { count, percent, won } from "@/lib/format";
import { convert, type ConversionFactors } from "@/lib/holding";
import type { Figure } from "@/lib/types";
import {
  ALLOTMENT_RATIO_CELL_KO,
  ALLOTMENT_RATIO_KO,
  ALLOTTED_SHARES_KO,
  CONFIRMED_PRICE_KO,
  CONVERTED_VALUE_KO,
  EXCESS_LIMIT_KO,
  EXCESS_RATIO_KO,
  HOLDING_CELL_KO,
  LAPSE_FLOOR_KO,
  PRICE_PENDING_KO,
  SHARES_UNIT_KO,
  allotmentCaptionKo,
  excessLimitKo,
  pricePendingLineKo,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * The N주 conversion, on a live ① row (R4 §The N주 conversion).
 *
 * > Client composes upstream numbers ONLY — every factor comes from the
 * > persisted contract (`offering_inputs` / `lapse_result`); nothing else is
 * > computed.
 * >
 * > - 배정 신주 = `allotted_shares(n, 배정비율)` … Show the factor to its full
 * >   10 decimals in the caption ("= {n}주 × 0.2465120994 · 1주 미만 버림").
 * > - 초과청약 한도 = ⌊배정 신주 × excess ratio⌋, shown as "+{k}주" where the
 * >   field passed.
 * > - **확정발행가 exists** → 환산액 = 배정 신주 × `unit_value` →
 * >   `EstimateMarker`; 하한 = 배정 신주 × `unit_value_floor`. Facts (주수,
 * >   확정발행가) never tagged; won amounts always.
 * > - **확정발행가 null** → chip `발행가 확정 전` + "확정 예정 {final_price_date}
 * >   — 확정 후 증서 이론가치와 금액을 환산합니다". **No money number at all.**
 * >   Share counts still shown.
 *
 * The arithmetic is `lib/holding.ts`'s and only its — the same call 내 포트폴리오
 * makes, so the two surfaces cannot print two readouts of one number
 * (`P5.S8` note 1). The no-money branch is that module's return value, not a
 * condition remembered here: with no `unit_value` there is no string to render.
 *
 * **Before a holding is entered nothing is derived.** An empty field is not a
 * zero: the row states its factors (배정비율, and the price or the chip that
 * stands in for it) and the derived rows appear the moment there is a number.
 */
export function Conversion({
  factors,
  shares,
  finalPriceDate,
  confirmedPrice,
}: {
  factors: ConversionFactors;
  shares: number | null;
  finalPriceDate?: string;
  confirmedPrice?: Figure;
}) {
  const conversion = convert(factors, shares);
  const ratio = factors.allotment_ratio;
  // Belt and braces with the seam's own gate: the price renders only where the
  // contract says it is fixed, so a stale `confirmed_price` beside
  // `price_confirmed: false` could never reach the page as a won amount.
  const price = factors.price_confirmed === false ? undefined : confirmedPrice;

  return (
    <div className={styles.conversion}>
      {/* The price state, first — it is what decides whether money exists at
          all. A confirmed price is a fact and carries no mark; an unconfirmed
          one is a chip and its due date, and never a 예정발행가 (the number the
          chip exists to withhold). */}
      {price ? (
        <p className={styles.factor}>
          <span className={styles.factorLabel}>{CONFIRMED_PRICE_KO}</span>
          <EstimateMarker estimated={price.estimated}>
            <span className="mono">{won(price.value)}</span>
          </EstimateMarker>
          <Citation
            className={styles.factorCite}
            rceptNo={price.rcept_no}
            quote={price.quote}
            span={price.span}
            parts={price.parts}
            label={CONFIRMED_PRICE_KO}
          />
        </p>
      ) : (
        <p className={styles.factor}>
          <span className={styles.pending}>{PRICE_PENDING_KO}</span>
          {finalPriceDate ? (
            <span className={styles.pendingLine}>{pricePendingLineKo(finalPriceDate)}</span>
          ) : null}
        </p>
      )}

      {shares === null ? (
        // No holding yet: the factor the conversion will use, stated as served.
        ratio ? (
          <p className={styles.factor}>
            <span className={styles.factorLabel}>{ALLOTMENT_RATIO_KO}</span>
            <span className="mono">{String(ratio.value)}</span>
            <Citation
              className={styles.factorCite}
              rceptNo={ratio.rcept_no}
              quote={ratio.quote}
              span={ratio.span}
              parts={ratio.parts}
              label={ALLOTMENT_RATIO_KO}
            />
          </p>
        ) : null
      ) : (
        <>
          {conversion.allotted !== null ? (
            <div className={styles.derived}>
              <p className={styles.factor}>
                <span className={styles.factorLabel}>{ALLOTTED_SHARES_KO}</span>
                {/* A share count is a fact about the ratio, not a derivation of
                    an estimate — it carries no mark, exactly as R4 states. */}
                <span className={`mono ${styles.derivedValue}`}>
                  {count(conversion.allotted)}
                  {SHARES_UNIT_KO}
                </span>
                {conversion.excess !== null ? (
                  <span className={styles.excess}>
                    {EXCESS_LIMIT_KO}{" "}
                    <span className="mono">{excessLimitKo(count(conversion.excess))}</span>
                  </span>
                ) : null}
              </p>
              {ratio ? (
                <p className={styles.caption}>
                  {allotmentCaptionKo(count(shares), String(ratio.value))}
                </p>
              ) : null}
            </div>
          ) : null}

          {conversion.value !== null ? (
            <p className={styles.factor}>
              <span className={styles.factorLabel}>{CONVERTED_VALUE_KO}</span>
              <EstimateMarker estimated={conversion.valueEstimated}>
                <span className={`mono ${styles.derivedValue}`}>{won(conversion.value)}</span>
              </EstimateMarker>
              {conversion.valueFloor !== null ? (
                <span className={styles.floor}>
                  {LAPSE_FLOOR_KO}{" "}
                  <EstimateMarker estimated={conversion.floorEstimated}>
                    <span className="mono">{won(conversion.valueFloor)}</span>
                  </EstimateMarker>
                </span>
              ) : null}
            </p>
          ) : null}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// R11 §4 — the same factors as instrument cells
// ---------------------------------------------------------------------------

/**
 * ①'s 환산 block on 내 종목 조회, **R11 §4**.
 *
 * The arithmetic is unchanged and still `lib/holding.ts`'s — this is the same
 * `convert()` the component above calls, so 조회 and 보유 종목 cannot print two
 * readouts of one number. What R11 re-cut is the **shape**: R10 §2's instrument
 * cells (a hairline row of label-over-value cells, dashed rules between them,
 * column-flow on desktop and 44px label/value rows at ≤767px) instead of R4's
 * stacked factor lines.
 *
 * Two states, and the reason for each:
 *
 * - **With a holding** — 보유 · 배정비율 (1주당) · 배정 신주 (carrying its own
 *   `= {n}주 × {ratio} · 1주 미만 버림` under it) · 초과청약 한도. Four cells, and
 *   the caption sits in the cell whose number it explains.
 * - **Without one** — exactly **two** cells, 배정비율 (1주당) and 초과청약 비율,
 *   both of them things the filing itself said. R4 left 배정비율 hanging alone on
 *   a line (finding 15); a pair reads as a row. Where the filing serves no
 *   `excess_ratio` there is one cell, because the alternative is inventing the
 *   second.
 *
 * The foot carries the **price state** on the left — 확정발행가 exists → R4's
 * 환산액 line (a won amount, always tagged, with its 하한); it does not → the
 * 발행가 확정 전 chip and its due date, and **no money number at all**, not even a
 * 예정발행가 (the very number the chip exists to withhold) — and the R11 §6
 * **prompt** on the right, while there is no holding to convert.
 */
export function ConversionChain({
  factors,
  shares,
  finalPriceDate,
  confirmedPrice,
  prompt,
}: {
  factors: ConversionFactors;
  shares: number | null;
  finalPriceDate?: string;
  confirmedPrice?: Figure;
  /** R11 §6's control, rendered once per page and owned by `StockView`. */
  prompt?: ReactNode;
}) {
  const conversion = convert(factors, shares);
  const ratio = factors.allotment_ratio;
  const excessRatio = factors.excess_ratio;
  // Belt and braces with the seam's own gate: the price renders only where the
  // contract says it is fixed, so a stale `confirmed_price` beside
  // `price_confirmed: false` could never reach the page as a won amount.
  const priced = factors.price_confirmed === false ? undefined : confirmedPrice;

  // ------------------------------------------------------------------
  // The pre-hydration reservation (`P12.F4`) — two facts the **server**
  // already holds, handed to `Lookup.module.css` so it can hold this row's
  // with-holding geometry before the browser's own `sessionStorage` has been
  // read. Neither is a number the browser knows: how many cells a holding will
  // draw follows from the served factors alone, and so does whether the foot's
  // note is the same in both states. See `components/chrome/PreHydration.tsx`.
  // ------------------------------------------------------------------

  /** How many cells this row draws **once a holding exists**: 보유 always, 배정비율
   * and 배정 신주 wherever a 배정비율 was served, 초과청약 한도 where an
   * 초과청약비율 was too. 4, 3 or 1 — and the reserved height differs per count,
   * because 3 cells are wider than 4 and the 배정 신주 caption then wraps less. */
  const reservedCells = 1 + (ratio ? 2 : 0) + (ratio && excessRatio ? 1 : 0);

  /** Whether `.chainfoot` carries the **same** note with and without a holding.
   * It does unless a money line is coming (which needs a confirmed price, a
   * `unit_value` and a 배정비율 all at once) — and where it does, hiding the
   * prompt pre-paint lands the foot at exactly its filled height. Where a money
   * line *is* coming, the foot's own height is a number no one has measured
   * (this product has served no priced ① yet), so the reservation says nothing
   * about it and the prompt stays: today's behaviour, not a guess. */
  const footSteady = !(priced && factors.unit_value !== undefined && ratio !== undefined);

  const cells: CellSpec[] =
    shares !== null
      ? [
          { label: HOLDING_CELL_KO, value: `${count(shares)}${SHARES_UNIT_KO}` },
          ...(ratio
            ? [{ label: ALLOTMENT_RATIO_CELL_KO, value: String(ratio.value), ratio: true }]
            : []),
          ...(conversion.allotted !== null
            ? [
                {
                  label: ALLOTTED_SHARES_KO,
                  value: `${count(conversion.allotted)}${SHARES_UNIT_KO}`,
                  sub: ratio
                    ? allotmentCaptionKo(count(shares), String(ratio.value))
                    : undefined,
                },
              ]
            : []),
          ...(conversion.excess !== null
            ? [{ label: EXCESS_LIMIT_KO, value: excessLimitKo(count(conversion.excess)) }]
            : []),
        ]
      : [
          ...(ratio
            ? [{ label: ALLOTMENT_RATIO_CELL_KO, value: String(ratio.value), ratio: true }]
            : []),
          ...(excessRatio
            ? [{ label: EXCESS_RATIO_KO, value: excessPercent(String(excessRatio.value)) }]
            : []),
        ];

  if (cells.length === 0 && !priced && !finalPriceDate && !prompt) return null;

  return (
    <div className={styles.chainwrap} data-mj-foot={footSteady ? "steady" : undefined}>
      {cells.length > 0 ? (
        <div className={styles.chain} data-mj-cells={reservedCells}>
          {cells.map((cell) => (
            <div key={cell.label} className={styles.cell}>
              <p className={styles.clab}>{cell.label}</p>
              <p className={styles.cval}>
                <span className={cell.ratio ? `${styles.v} ${styles.ratio}` : styles.v}>{cell.value}</span>
              </p>
              {cell.sub ? <p className={styles.clab}>{cell.sub}</p> : null}
            </div>
          ))}
        </div>
      ) : null}

      <div className={styles.chainfoot}>
        {priced && conversion.value !== null ? (
          <p className={styles.chainnote}>
            <span className={styles.factorLabel}>{CONVERTED_VALUE_KO}</span>
            <EstimateMarker estimated={conversion.valueEstimated}>
              <span className={`mono ${styles.derivedValue}`}>{won(conversion.value)}</span>
            </EstimateMarker>
            {conversion.valueFloor !== null ? (
              <span className={styles.floor}>
                {LAPSE_FLOOR_KO}{" "}
                <EstimateMarker estimated={conversion.floorEstimated}>
                  <span className="mono">{won(conversion.valueFloor)}</span>
                </EstimateMarker>
              </span>
            ) : null}
          </p>
        ) : priced ? null : (
          <p className={styles.chainnote}>
            <span className={styles.pending}>{PRICE_PENDING_KO}</span>
            {finalPriceDate ? <span>{pricePendingLineKo(finalPriceDate)}</span> : null}
          </p>
        )}

        {prompt}
      </div>
    </div>
  );
}

type CellSpec = { label: string; value: string; sub?: string; ratio?: boolean };

/** The card prints 「20%」, not 「20.0%」: the product's one percentage formatter at
 * its default precision, with a bare trailing `.0` dropped. A ratio that is not a
 * whole percent keeps its decimal — a disclosed factor is never rounded away. */
function excessPercent(value: string): string {
  return percent(value, 1).replace(/\.0%$/, "%");
}
