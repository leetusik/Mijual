import { CraftPanel } from "@/components";
import { count, percent, won } from "@/lib/format";
import type { BoardSummary } from "@/lib/types";
import { Countdown } from "./Countdown";
import { EstimateValue } from "./EstimateValue";
import {
  BAND_ASSUMPTION_KO,
  BAND_FLOOR_KO,
  STAT_LAPSE_PENDING_KO,
  STAT_REPORTS_KO,
  STAT_WATCHING_KO,
  STAT_WITHIN_30D_KO,
  VALUE_EYEBROW_KO,
  factSentence,
} from "./copy";
import styles from "./Anchor.module.css";

/**
 * The retrospective anchor (R2 §Retrospective anchor) — two craft panels,
 * `1fr / 340px`, 20px gap, stacked on mobile (value card first).
 *
 * > **Value card**: mono 11 `--ink-3` eyebrow "2026년에 소멸한 신주인수권 가치" →
 * > 46px/700 718.1억원 + 「추정」 tag → band line mono 13.5 (밴드 하한
 * > 548.7억원「추정」 (권리락 조정 가정)) → fact sentence 15px, full card width,
 * > one line (no max-width cap). **The gate-cost line does NOT appear here
 * > (operator) — footer only.**
 * >
 * > **Countdown/stats card**: countdown + 2×2 live stats (감시 중 이벤트 · 30일
 * > 이내 마감 · 소멸 앞둔 신주인수권 · 읽은 실적보고서) — fed live from the same
 * > summary the board uses.
 *
 * Every number on both cards comes from **one** `/board/summary` object, which is
 * the point of that shape: the two cards, the hero's stat line and the 소멸주의보
 * strip cannot disagree with each other because there is nothing for them to
 * disagree with.
 *
 * A figure the summary does not carry produces **no phrase** — not a zero and not
 * a dash. The contract omits a key rather than sending an empty value, and the
 * surface omits the line rather than inventing one.
 */
export function RetrospectiveAnchor({ summary }: { summary: BoardSummary }) {
  const value = summary.lapsed_value;
  const floor = summary.lapsed_value_floor;
  const issued = summary.issued_warrants;
  const rate = summary.lapse_rate;
  const target = summary.next_lapse?.target;

  return (
    <section className={styles.anchor}>
      <CraftPanel className={styles.card}>
        <p className={styles.eyebrow}>{VALUE_EYEBROW_KO}</p>

        {value ? (
          <p className={styles.headline}>
            <EstimateValue estimated={value.estimated} valueClassName={styles.headlineValue}>
              <span className="mono">{won(value.value)}</span>
            </EstimateValue>
          </p>
        ) : null}

        {floor ? (
          <p className={styles.band}>
            {BAND_FLOOR_KO}{" "}
            <EstimateValue estimated={floor.estimated} valueClassName={styles.bandValue}>
              {won(floor.value)}
            </EstimateValue>{" "}
            {BAND_ASSUMPTION_KO}
          </p>
        ) : null}

        {issued && rate ? (
          <p className={styles.fact}>
            {factSentence.before}
            <span className="mono">{count(issued.value)}주</span>
            {factSentence.between}
            <span className="mono">{percent(rate.value)}</span>
            {factSentence.after}
          </p>
        ) : null}
      </CraftPanel>

      <CraftPanel className={styles.card}>
        {/* No served instant, no countdown: R2 fixes the target as an absolute
            KST instant from the backend, and a fabricated one would be the
            browser deriving a date. */}
        {target ? <Countdown target={target} /> : null}

        <dl className={styles.stats}>
          <Stat label={STAT_WATCHING_KO} value={summary.watching} />
          <Stat label={STAT_WITHIN_30D_KO} value={summary.within_30d} />
          <Stat label={STAT_LAPSE_PENDING_KO} value={summary.lapse_pending} />
          <Stat label={STAT_REPORTS_KO} value={summary.performance_reports} />
        </dl>
      </CraftPanel>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className={styles.stat}>
      <dt className={styles.statLabel}>{label}</dt>
      <dd className={styles.statValue}>
        <span className="mono">{count(value)}건</span>
      </dd>
    </div>
  );
}
