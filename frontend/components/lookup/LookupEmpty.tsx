import { CraftPanel, RightsChip } from "@/components";
import { count } from "@/lib/format";
import type { BoardSummary, StockPage } from "@/lib/types";
import {
  COVERAGE_BOUNDARY_KO,
  HERO_STAT_WATCHING_KO,
  NO_RIGHTS_KO,
  WATCH_TARGETS_KO,
  coverageFromKo,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * The no-event stock (R4 §Empty states, `lookup/LookupEmpty.html`).
 *
 * > no-event stock ("이 종목에는 진행 중이거나 2026년에 소멸된 권리가 없습니다"
 * > + 감시 대상 3종 + 감시 중 count)
 *
 * A resolved stock with nothing to show is **structurally different from a
 * search that found nothing** (`P5.S4` note 3): `found: true` with
 * `rights.count === 0`, `totals {offerings: 0, valued: 0}` and **no money key at
 * all**. So this states what the product watches and how much of it, rather than
 * apologising or printing a zero amount.
 *
 * The 감시 중 count is the landing's own number, read from `/board/summary` —
 * the one object every aggregate on this product comes from, so 조회 and the
 * board cannot disagree about how many events are being watched. If the summary
 * is unavailable the line is simply absent: a count nobody served is not a count.
 */
export function NoRights({ summary }: { summary?: BoardSummary | null }) {
  return (
    <CraftPanel className={styles.empty}>
      <p className={styles.emptyLine}>{NO_RIGHTS_KO}</p>

      <div className={styles.watchTargets}>
        <span className={styles.factorLabel}>{WATCH_TARGETS_KO}</span>
        <RightsChip rightsType="R1" />
        <RightsChip rightsType="R2" />
        <RightsChip rightsType="R3" />
      </div>

      {summary ? (
        <p className={styles.caption}>
          {HERO_STAT_WATCHING_KO} <span className="mono">{count(summary.watching)}</span>건
        </p>
      ) : null}
    </CraftPanel>
  );
}

/**
 * The coverage boundary, stated factually (R4 decision R4-3, `LookupEmpty`).
 *
 * > the boundary panel states ① 2026-01-01부터 · ② 2025-06부터. Outside coverage
 * > is *unstated*, never counted as 0.
 *
 * Both dates come off the wire (`lapse.coverage`), because they are the corpus's
 * own collection windows and not a constant this surface may assert. The record
 * writes the two boundaries against ①/② — internal shorthand that **R1's
 * revision removed from the UI** — so they render as the rights types' own
 * chips, the same reading `components/event/copy.ts` records for ③'s 1단계/2단계.
 */
export function CoveragePanel({ coverage }: { coverage: StockPage["lapse"]["coverage"] }) {
  return (
    <section className={styles.coverage}>
      <div className={styles.coverageRows}>
        <p className={styles.coverageRow}>
          <RightsChip rightsType="R1" compact />
          <span className="mono">{coverageFromKo(coverage.start)}</span>
        </p>
        <p className={styles.coverageRow}>
          <RightsChip rightsType="R2" compact />
          <span className="mono">{coverageFromKo(coverage.convertible_start)}</span>
        </p>
      </div>
      <p className={styles.caption}>{COVERAGE_BOUNDARY_KO}</p>
    </section>
  );
}
