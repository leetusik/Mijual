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
 * ①'s 환산 블록 (R3 §Page anatomy 3 · §6-1, re-cut by **R10 §2**).
 *
 * > per-unit chain 예정/확정발행가 → 할인율 → (확정발행가 존재 시)
 * > `EstimateMarker` 증서 1주 이론가치 → 배정비율 printed to its full 10
 * > decimals. 확정발행가 null → chip `발행가 확정 전` + mono `확정 예정
 * > {final_price_date}`. Button "내 보유량으로 환산 →" routes to 조회 (R4); **no
 * > N주 input here**. Post-결과 events append the 청약 결과 inset.
 *
 * ## R10 deletes the arrows
 *
 * R3 drew `→` between the links. On a 390px column the cells stacked and left
 * **orphan arrows** hanging after 「발행가 확정 전」 and before 「배정비율」 (walk
 * finding 1), and on the desktop they claimed a derivation that is not there:
 * these are four values the filing states, not a chain that computes one from
 * the next (walk finding 7). R10 replaces them with hairline-ruled cells — a
 * vertical dashed rule on the desktop, a horizontal one at ≤767px where the
 * cells become label-left / value-right rows of at least 44px. There is no
 * relationship drawn, so there is no wrong relationship to draw.
 *
 * The 환산 button moves into the block's own footer rule and becomes **the
 * page's primary action** (walk finding 11): 담기 in the header is the secondary
 * text link, and this is a 44px hairline button (full width at ≤767px).
 *
 * ## Which cell carries a citation
 *
 * One rule: **the value that has a 본문 구절 behind it**. 확정발행가 and 할인율
 * cite when the payload carries a quote; 증서 1주 이론가치 is derived, so it
 * carries 「추정」 and no citation (there is no passage to point at); 배정비율 is
 * an API-tier fact and carries neither. A cell never wears 「추정」 and `[근거]`
 * at once.
 *
 * ## Why an unpriced offering shows no 예정발행가 either
 *
 * R3 writes the chain's first link as "예정/확정발행가", and the payload does
 * carry `planned_price`. It is not rendered, because the rule that governs it is
 * stated in three places and is absolute: **money never appears before
 * 확정발행가** — `docs/current/frontend.md`'s trust rules, the presentation
 * contract ("`확정발행가 null` ⇒ **no money number at all**, anywhere, including
 * mail"), and R3's own state for this case, which R10 keeps: the first cell
 * carries the `발행가 확정 전` chip and the date the price is due, **and no
 * label** — a label on a cell with no value would say a value exists.
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

  // The cells in R3's order, without the arrows R10 retired.
  const cells: ReactNode[] = [];

  if (priced && offering.confirmed_price) {
    cells.push(
      <Cell label={CONFIRMED_PRICE_KO} figure={offering.confirmed_price}>
        {won(offering.confirmed_price.value)}
      </Cell>,
    );
  } else {
    cells.push(
      <div className={styles.cell}>
        <p className={styles.cval}>
          <span className={styles.pend}>{PRICE_PENDING_KO}</span>
          {offering.final_price_date ? (
            <span className={styles.pendingDate}>
              {finalPriceDateKo(offering.final_price_date)}
            </span>
          ) : null}
        </p>
      </div>,
    );
  }

  if (offering.discount_rate) {
    cells.push(
      <Cell label={DISCOUNT_RATE_KO} figure={offering.discount_rate}>
        {percent(offering.discount_rate.value)}
      </Cell>,
    );
  }

  if (priced && offering.unit_value) {
    // Derived, so it wears 「추정」 and never a citation: there is no passage in
    // the filing that states this number.
    cells.push(
      <Cell label={UNIT_VALUE_KO} figure={offering.unit_value} cite={false}>
        {won(offering.unit_value.value)}
      </Cell>,
    );
  }

  if (offering.allotment_ratio) {
    // 배정비율 keeps all ten decimals: `mijual.calc.allotted_shares` floors
    // ⌊N × 배정비율⌋ (단수주 절사) and R4 does that multiplication, so a rounded
    // ratio here would be a different number there. R10 (Q16) confirms the value
    // and sets only its presentation — one step down in size, one mono token.
    cells.push(
      <Cell label={ALLOTMENT_RATIO_KO} figure={offering.allotment_ratio} ratio cite={false}>
        {String(offering.allotment_ratio.value)}
      </Cell>,
    );
  }

  return (
    <div className={styles.chainwrap}>
      <div className={styles.chain}>
        {cells.map((cell, index) => (
          <Fragment key={index}>{cell}</Fragment>
        ))}
      </div>
      <div className={styles.chainfoot}>
        <Link className={styles.convert} href={stockPath(corpCode)}>
          {CONVERT_CTA_KO}
        </Link>
      </div>
    </div>
  );
}

/** One cell of the block: label, value, and — where R10's rule allows one — the
 * value's own citation. A figure with neither `quote` nor `parts` renders **no
 * chip at all** either way: `Citation` returns nothing rather than promising
 * evidence it does not have. */
function Cell({
  label,
  figure,
  children,
  ratio = false,
  cite = true,
}: {
  label: string;
  figure: Figure;
  children: ReactNode;
  /** 배정비율's own presentation (R10 §2 / Q16): one step down, one mono token. */
  ratio?: boolean;
  /** R10 §2: 이론가치 (derived — it wears 「추정」) and 배정비율 (API tier) carry
   * no chip; the panel's provenance line answers for them. */
  cite?: boolean;
}) {
  return (
    <div className={styles.cell}>
      <p className={styles.clab}>{label}</p>
      <p className={styles.cval}>
        <EstimateMarker estimated={figure.estimated}>
          <span className={ratio ? `mono ${styles.ratio}` : "mono"}>{children}</span>
        </EstimateMarker>
        {cite ? (
          <Citation
            rceptNo={figure.rcept_no}
            quote={figure.quote}
            span={figure.span}
            parts={figure.parts}
            label={label}
          />
        ) : null}
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
          {LAPSE_VALUE_KO}{" "}
          <EstimateMarker estimated={lapse.value.estimated}>
            <span className="mono">{won(lapse.value.value)}</span>
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
      <span>{label}</span>
      <EstimateMarker estimated={figure.estimated}>
        <span className={`mono ${styles.insetNum}`}>
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
            <p className={styles.clab}>
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
