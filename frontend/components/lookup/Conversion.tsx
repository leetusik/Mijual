import { Citation, EstimateMarker } from "@/components";
import { count, won } from "@/lib/format";
import { convert, type ConversionFactors } from "@/lib/holding";
import type { Figure } from "@/lib/types";
import {
  ALLOTMENT_RATIO_KO,
  ALLOTTED_SHARES_KO,
  CONFIRMED_PRICE_KO,
  CONVERTED_VALUE_KO,
  EXCESS_LIMIT_KO,
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
