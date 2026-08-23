import { EstimateMarker } from "@/components";
import { dartUrl } from "@/lib/api";
import { count, won } from "@/lib/format";
import type { ConvertibleView } from "@/lib/types";
import {
  CONVERSION_PRICE_KO,
  CONVERTED_SHARES_KO,
  FACE_AMOUNT_KO,
  FACT_SOURCE_KO,
  ISSUE_METHOD_KO,
  MATURITY_KO,
  OVERHANG_KO,
  SHARES_UNIT_KO,
} from "./copy";
import styles from "./Event.module.css";

/**
 * ②'s API fact strip (R3 §Type-specific rules, re-cut by **R10 §3**).
 *
 * > **②**: API-tier facts (전환가액, 오버행 %, 전환 시 주식수, 권면총액,
 * > 발행방법·만기) in a fact strip **ABOVE** 본문 fields.
 *
 * Exactly those six, because that is what the round names and what the contract
 * serves (`present.convertible_view`) — 리픽싱 floor and 전환비율 are deliberately
 * not in the payload, and a seventh cell here would be a value nobody signed.
 *
 * **Every one of them is a fact**, so none carries the estimate mark; and none
 * carries a `[근거]` chip either, because an API row has no character offsets
 * into a document. ② is also the type whose card can be complete with **zero**
 * 본문 fields — 239 of the 422 exposable ② events have no readable 본문 at all —
 * which is why this strip is above them rather than beside them.
 *
 * ## R10 makes the provenance *tier* visible
 *
 * R3 closed the strip with a bare 접수번호 link, which read as "why is this the
 * only place with no evidence?" (walk finding 8). R10 gives the strip its own
 * frame and its own **source row**: 「DART 공시 API」 on the left — the sparse-②
 * closing line's own words, not a new sentence — and the filing number on the
 * right. The 본문 rows below it cite per row. Two surfaces, two provenance
 * grammars, and the difference between them is now legible instead of looking
 * like an omission.
 *
 * The grid is **fixed at 3 × 2** (1 × 6 at ≤767px) rather than `auto-fit`, which
 * used to break into four and five columns at widths in between, and 「전환 시
 * 주식수」 is its own cell rather than a sub-line of 오버행 — the API serves it
 * separately, so it is a value, not a gloss.
 */
export function ConvertibleStrip({ view }: { view: ConvertibleView }) {
  const cells: Array<{ label: string; value: string }> = [];

  if (view.conversion_price) {
    cells.push({ label: CONVERSION_PRICE_KO, value: won(view.conversion_price.value) });
  }
  if (view.overhang_pct) {
    // A served percentage, printed as served: the contract already carries it in
    // percent units, so re-scaling or re-rounding it would publish a different
    // number than `/board`'s own.
    cells.push({ label: OVERHANG_KO, value: `${view.overhang_pct.value}%` });
  }
  if (view.shares) {
    cells.push({ label: CONVERTED_SHARES_KO, value: `${count(view.shares.value)}${SHARES_UNIT_KO}` });
  }
  if (view.face_amount) {
    cells.push({ label: FACE_AMOUNT_KO, value: won(view.face_amount.value) });
  }
  if (view.issue_method) {
    cells.push({ label: ISSUE_METHOD_KO, value: view.issue_method });
  }
  if (view.maturity_date) {
    cells.push({ label: MATURITY_KO, value: view.maturity_date });
  }

  if (cells.length === 0) return null;

  return (
    <section className={styles.facts}>
      <div className={styles.fgrid}>
        {cells.map((cell) => (
          <div key={cell.label} className={styles.fcell}>
            <p className={styles.clab}>{cell.label}</p>
            <p className={styles.cval}>
              {/* Facts, all six — the marker is passed the payload's own flag
                  rather than a literal, and it renders nothing for a fact. */}
              <EstimateMarker estimated={false}>
                <span className="mono">{cell.value}</span>
              </EstimateMarker>
            </p>
          </div>
        ))}
      </div>

      {view.rcept_no ? (
        <p className={styles.fsrc}>
          <span>{FACT_SOURCE_KO}</span>
          <a href={dartUrl(view.rcept_no)} target="_blank" rel="noreferrer">
            {view.rcept_no} ↗
          </a>
        </p>
      ) : null}
    </section>
  );
}
