import { EstimateMarker } from "@/components";
import { dartUrl } from "@/lib/api";
import { count, won } from "@/lib/format";
import type { ConvertibleView } from "@/lib/types";
import {
  CONVERSION_PRICE_KO,
  CONVERTED_SHARES_KO,
  FACE_AMOUNT_KO,
  ISSUE_METHOD_KO,
  MATURITY_KO,
  OVERHANG_KO,
  SHARES_UNIT_KO,
} from "./copy";
import styles from "./Event.module.css";

/**
 * ②'s API fact strip (R3 §Type-specific rules).
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
 * into a document. Its citation is the filing number, which is why the strip ends
 * with the 접수번호 as a DART link (`P5.S3` note 7). ② is also the type whose card
 * can be complete with **zero** 본문 fields — 239 of the 422 exposable ② events
 * have no readable 본문 at all — which is why this strip is above them rather
 * than beside them.
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
    <section className={styles.strip}>
      <div className={styles.stripCells}>
        {cells.map((cell) => (
          <div key={cell.label} className={styles.stripCell}>
            <p className={styles.chainLabel}>{cell.label}</p>
            <p className={styles.stripValue}>
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
        <a
          className={`mono ${styles.stripCite}`}
          href={dartUrl(view.rcept_no)}
          target="_blank"
          rel="noreferrer"
        >
          {view.rcept_no} ↗
        </a>
      ) : null}
    </section>
  );
}
