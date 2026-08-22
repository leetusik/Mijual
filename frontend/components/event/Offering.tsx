import Link from "next/link";
import { Fragment, type ReactNode } from "react";
import { Citation, CraftPanel, EstimateMarker, StateBadge } from "@/components";
import { count, percent, won } from "@/lib/format";
import { stockPath } from "@/lib/routes";
import type { Disagreement, EventDetail, Figure, LapseResult, OfferingInputs } from "@/lib/types";
import {
  ALLOTMENT_RATIO_KO,
  CONFIRMED_PRICE_KO,
  CONVERT_CTA_KO,
  DISCOUNT_RATE_KO,
  LAPSE_FLOOR_KO,
  LAPSE_RESULT_KO,
  LAPSE_VALUE_KO,
  MISMATCH_DERIVED_KO,
  MISMATCH_FOOTER_KO,
  MISMATCH_HEADER_KO,
  PRICE_PENDING_KO,
  SHARES_UNIT_KO,
  UNIT_VALUE_KO,
  WARRANTS_EXERCISED_KO,
  WARRANTS_ISSUED_KO,
  WARRANTS_LAPSED_KO,
  finalPriceDateKo,
} from "./copy";
import styles from "./Event.module.css";

/**
 * ①'s 환산 블록 (R3 §Page anatomy 3, session decision §6-1).
 *
 * > per-unit chain 예정/확정발행가 → 할인율 → (확정발행가 존재 시)
 * > `EstimateMarker` 증서 1주 이론가치 → 배정비율 printed to its full 10
 * > decimals. 확정발행가 null → chip `발행가 확정 전` + mono `확정 예정
 * > {final_price_date}`. Button "내 보유량으로 환산 →" routes to 조회 (R4); **no
 * > N주 input here**. Post-결과 events append the 청약 결과 inset.
 *
 * ## Why an unpriced offering shows no 예정발행가 either
 *
 * R3 writes the chain's first link as "예정/확정발행가", and the payload does
 * carry `planned_price`. It is not rendered, because the rule that governs it is
 * stated in three places and is absolute: **money never appears before
 * 확정발행가** — `docs/current/frontend.md`'s trust rules, the presentation
 * contract ("`확정발행가 null` ⇒ **no money number at all**, anywhere, including
 * mail"), and R3's own state for this case, which replaces the money with the
 * `발행가 확정 전` chip and the date the price is due. A 예정발행가 printed
 * beside that chip would be exactly the number the chip exists to withhold.
 * 할인율 and 배정비율 are ratios, not money, and they render in both states.
 *
 * The N주 math stays in 조회 (R4 owns the single multiplication site, `P5.S8`
 * note 1), so this block links out and computes nothing.
 */
export function Offering({ detail }: { detail: EventDetail }) {
  const offering = detail.offering;
  const lapse = detail.lapse_result;
  const disagreement = detail.issuer_disagreement;
  if (!offering && !lapse && !disagreement) return null;

  return (
    <section className={styles.offering}>
      {offering ? <Chain offering={offering} corpCode={detail.corp_code} /> : null}
      {lapse ? <LapseInset lapse={lapse} /> : null}
      {disagreement ? <Mismatch disagreement={disagreement} /> : null}
    </section>
  );
}

function Chain({ offering, corpCode }: { offering: OfferingInputs; corpCode: string }) {
  const priced = offering.price_confirmed && offering.confirmed_price !== undefined;

  // The links in R3's order. The arrows between them are drawn as their own
  // items so a chain that wraps — four links do not fit a 390px column — breaks
  // where the layout breaks, instead of leaving a marker hanging off an edge.
  const links: ReactNode[] = [];

  if (priced && offering.confirmed_price) {
    links.push(
      <ChainStep label={CONFIRMED_PRICE_KO} figure={offering.confirmed_price}>
        {won(offering.confirmed_price.value)}
      </ChainStep>,
    );
  } else {
    links.push(
      <div className={styles.chainStep}>
        <span className={styles.pending}>{PRICE_PENDING_KO}</span>
        {offering.final_price_date ? (
          <span className={`mono ${styles.pendingDate}`}>
            {finalPriceDateKo(offering.final_price_date)}
          </span>
        ) : null}
      </div>,
    );
  }

  if (offering.discount_rate) {
    links.push(
      <ChainStep label={DISCOUNT_RATE_KO} figure={offering.discount_rate}>
        {percent(offering.discount_rate.value)}
      </ChainStep>,
    );
  }

  if (priced && offering.unit_value) {
    links.push(
      <ChainStep label={UNIT_VALUE_KO} figure={offering.unit_value}>
        {won(offering.unit_value.value)}
      </ChainStep>,
    );
  }

  if (offering.allotment_ratio) {
    // 배정비율 keeps all ten decimals: `mijual.calc.allotted_shares` floors
    // ⌊N × 배정비율⌋ (단수주 절사) and R4 does that multiplication, so a rounded
    // ratio here would be a different number there.
    links.push(
      <ChainStep label={ALLOTMENT_RATIO_KO} figure={offering.allotment_ratio}>
        {String(offering.allotment_ratio.value)}
      </ChainStep>,
    );
  }

  return (
    <>
      <div className={styles.chain}>
        {links.map((link, index) => (
          <Fragment key={index}>
            {index > 0 ? (
              <span aria-hidden="true" className={styles.chainArrow}>
                →
              </span>
            ) : null}
            {link}
          </Fragment>
        ))}
      </div>

      <Link className={styles.convert} href={stockPath(corpCode)}>
        {CONVERT_CTA_KO}
      </Link>
    </>
  );
}

/** One link of the chain: label, value, and the value's own citation. A figure
 * with neither `quote` nor `parts` renders **no chip at all** — `Citation`
 * returns nothing rather than promising evidence it does not have. */
function ChainStep({
  label,
  figure,
  children,
}: {
  label: string;
  figure: Figure;
  children: ReactNode;
}) {
  return (
    <div className={styles.chainStep}>
      <p className={styles.chainLabel}>{label}</p>
      <p className={styles.chainValue}>
        <EstimateMarker estimated={figure.estimated}>
          <span className="mono">{children}</span>
        </EstimateMarker>
        <Citation
          className={styles.chainCite}
          rceptNo={figure.rcept_no}
          quote={figure.quote}
          span={figure.span}
          parts={figure.parts}
          label={label}
        />
      </p>
    </div>
  );
}

/**
 * The 청약 결과 inset — 발행 · 청약 · 소멸 shares, then the 소멸가치 and its 하한.
 *
 * The counts are facts read from the 증권발행실적보고서; the two won figures are
 * derived and therefore always tagged. `warrants_exercised` is the corpus's
 * multi-part case (`P5.S20`): the filer states the 청약 on two rows — 한국예탁결제원
 * and 직접청약 — and the number the report means is printed on neither, so its
 * citation carries **one span per addend** and `Citation` renders every one of
 * them. Never one addend, and never the two joined into a sentence the filing
 * does not contain.
 */
function LapseInset({ lapse }: { lapse: LapseResult }) {
  if (!lapse.warrants_issued && !lapse.lapsed && !lapse.value) return null;
  return (
    <div className={styles.inset}>
      <p className={styles.insetTitle}>{LAPSE_RESULT_KO}</p>

      <div className={styles.insetRow}>
        <Shares label={WARRANTS_ISSUED_KO} figure={lapse.warrants_issued} />
        <Shares label={WARRANTS_EXERCISED_KO} figure={lapse.warrants_exercised} />
        <Shares
          label={WARRANTS_LAPSED_KO}
          figure={lapse.lapsed}
          suffix={lapse.lapse_rate ? ` (${percent(lapse.lapse_rate.value, 2)})` : undefined}
        />
      </div>

      {lapse.value ? (
        <p className={styles.insetValue}>
          <span className={styles.chainLabel}>{LAPSE_VALUE_KO}</span>
          <EstimateMarker estimated={lapse.value.estimated}>
            <span className={`mono ${styles.insetAmount}`}>{won(lapse.value.value)}</span>
          </EstimateMarker>
          {lapse.value_floor ? (
            <span className={styles.floor}>
              {LAPSE_FLOOR_KO}{" "}
              <EstimateMarker estimated={lapse.value_floor.estimated}>
                <span className="mono">{won(lapse.value_floor.value)}</span>
              </EstimateMarker>
            </span>
          ) : null}
        </p>
      ) : null}
    </div>
  );
}

function Shares({
  label,
  figure,
  suffix,
}: {
  label: string;
  figure?: Figure;
  suffix?: string;
}) {
  if (!figure) return null;
  return (
    <span className={styles.shares}>
      <span className={styles.chainLabel}>{label}</span>
      <EstimateMarker estimated={figure.estimated}>
        <span className="mono">
          {count(figure.value)}
          {SHARES_UNIT_KO}
          {suffix ?? ""}
        </span>
      </EstimateMarker>
      <Citation
        rceptNo={figure.rcept_no}
        quote={figure.quote}
        span={figure.span}
        parts={figure.parts}
        label={label}
      />
    </span>
  );
}

/**
 * 발행사 기재 불일치 — two readings side by side, each with its own citation.
 *
 * `ui-traps.md` #2: the issuer's own 실권주 cell disagrees with the issuer's own
 * table, and both numbers are cited into the same document. The product does not
 * pick a winner, average them or hide the clash — it shows that **the filing
 * contradicts itself**, phrased so the reader never thinks 미주알 made the
 * mistake. The footer states which reading the totals use, and that is the only
 * statement made about the two.
 *
 * The derived reading has no quote of its own (it is 발행 − 청약), so its evidence
 * is its two inputs, each rendered with its own count and its own citation. They
 * are deliberately **not** passed as `Citation`'s `parts`: parts are addends that
 * sum to the value, and these two are a difference.
 */
function Mismatch({ disagreement }: { disagreement: Disagreement }) {
  return (
    <CraftPanel tone="alert" className={styles.mismatch}>
      <StateBadge kind="mismatch" className={styles.mismatchBadge} />
      <p className={styles.mismatchHead}>{MISMATCH_HEADER_KO}</p>

      <div className={styles.readings}>
        {disagreement.readings.map((reading) => (
          <div key={reading.key} className={styles.reading}>
            <p className={styles.chainLabel}>
              {reading.label ?? (reading.inputs ? MISMATCH_DERIVED_KO : null)}
            </p>
            <p className={styles.readingValue}>
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
            </p>
            {reading.inputs ? (
              <div className={styles.readingInputs}>
                {reading.inputs.map((input, index) => (
                  <Shares
                    key={`${reading.key}-${index}`}
                    label={index === 0 ? WARRANTS_ISSUED_KO : WARRANTS_EXERCISED_KO}
                    figure={input}
                  />
                ))}
              </div>
            ) : null}
          </div>
        ))}
      </div>

      <p className={styles.mismatchFoot}>{MISMATCH_FOOTER_KO}</p>
    </CraftPanel>
  );
}
