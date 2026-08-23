import { CraftPanel, RightsChip } from "@/components";
import { count } from "@/lib/format";
import type { BoardSummary, StockPage } from "@/lib/types";
import {
  COVERAGE_BOUNDARY_KO,
  COVERAGE_SECTION_KO,
  HERO_STAT_WATCHING_KO,
  NO_RIGHTS_KO,
  WATCH_TARGETS_KO,
  coverageFromKo,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * 감시 대상 — the entry page's context (R11 §1, **Q-A = (b)**).
 *
 * With no query the page used to be a title, a search row and a void. R11's
 * answer is not a redirect and not new copy: it is the two things this page can
 * honestly say before a reader has named a stock — **what it watches** (the three
 * rights types, as their own chips) and **how much of it** (감시 중 {n}건, the
 * landing's own stat, read from `/board/summary`). Both elements were already
 * signed, on the no-rights card below, so the empty entry and an empty result now
 * say the same thing.
 *
 * If the summary is unavailable the line is simply absent: a count nobody served
 * is not a count, and a placeholder would be worse than silence.
 */
export function WatchPanel({ summary }: { summary?: BoardSummary | null }) {
  return (
    <CraftPanel>
      <div className={styles.empty}>
        <WatchTargets />
        {summary ? (
          <p className={styles.cap}>
            {HERO_STAT_WATCHING_KO} <span className="mono">{count(summary.watching)}</span>건
          </p>
        ) : null}
      </div>
    </CraftPanel>
  );
}

/**
 * The no-event stock (R4 §Empty states, `lookup/LookupEmpty.html`; R11 §1's
 * `Empty` card keeps its words).
 *
 * > no-event stock ("이 종목에는 진행 중이거나 2026년에 소멸된 권리가 없습니다"
 * > + 감시 대상 3종 + 감시 중 count)
 *
 * A resolved stock with nothing to show is **structurally different from a search
 * that found nothing** (`P5.S4` note 3): `found: true` with `rights.count === 0`,
 * `totals {offerings: 0, valued: 0}` and **no money key at all**. So this states
 * what the product watches and how much of it, rather than apologising or
 * printing a zero amount.
 *
 * **Q-D, decided at the R11 gate: a past ②/③ leaves no trace here.** 세기상사's
 * 주식매수청구권 windows have passed, and this page still says the sentence above,
 * because 놓친 돈 is ①-only (R4-4) and a ③ is never money — attaching 「소멸」 to a
 * past ③ would give the word two meanings on one surface. The ① that leaves
 * 「청약 {date} 종료」 does so because the money it leads to is further down the
 * same page; a ③ has no such bridge. The whole story of a past ③ is the event
 * detail's (R10), and the way there is a link, not this page.
 *
 * The 감시 중 count is the landing's own number, from the one object every
 * aggregate on this product comes from, so 조회 and the board cannot disagree.
 */
export function NoRights({ summary }: { summary?: BoardSummary | null }) {
  return (
    <CraftPanel>
      <div className={styles.empty}>
        <p className={styles.emptylead}>{NO_RIGHTS_KO}</p>
        <WatchTargets />
        {summary ? (
          <p className={styles.cap}>
            {HERO_STAT_WATCHING_KO} <span className="mono">{count(summary.watching)}</span>건
          </p>
        ) : null}
      </div>
    </CraftPanel>
  );
}

/** The three things this product watches. The 3종 themselves are `RightsChip`'s
 * labels, so the list is the primitive's and only the lead-in is copy. */
function WatchTargets() {
  return (
    <div className={styles.watch}>
      <span className={styles.watchlab}>{WATCH_TARGETS_KO}</span>
      <RightsChip rightsType="R1" />
      <RightsChip rightsType="R2" />
      <RightsChip rightsType="R3" />
    </div>
  );
}

/**
 * 집계 범위 — the coverage boundary, stated factually (R4-3, **given its own `h2`
 * by R11 §8**).
 *
 * > the boundary panel states ① 2026-01-01부터 · ② 2025-06부터. Outside coverage
 * > is *unstated*, never counted as 0.
 *
 * R11's finding 12: this panel and the 보유량 strip were the two blocks on the
 * surface with no heading, so a screen-reader outline jumped from 놓친 돈 to the
 * provenance line with an unnamed panel in between. The heading reuses the noun
 * already inside the signed caption 「집계 범위 2026-01-01 ~ 오늘 (KST)」.
 *
 * Both dates come off the wire (`lapse.coverage`), because they are the corpus's
 * own collection windows and not a constant this surface may assert. The record
 * writes the two boundaries against ①/② — internal shorthand that **R1's revision
 * removed from the UI** — so they render as the rights types' own chips.
 *
 * **On the entry page there is no stock, and therefore no served coverage**: the
 * contract carries the two dates on `GET /stocks/{corp_code}` only, and no other
 * served object holds them. So `/stocks` renders the boundary **sentence** with no
 * dated rows rather than a date this surface invented (`P8.S9` `result.md`).
 */
export function CoveragePanel({ coverage }: { coverage?: StockPage["lapse"]["coverage"] }) {
  return (
    <section className={styles.section}>
      <h2 className={styles.eyebrow} aria-label={COVERAGE_SECTION_KO}>
        {COVERAGE_SECTION_KO}
      </h2>
      <CraftPanel>
        <div className={styles.cvg}>
          {coverage ? (
            <div className={styles.cvgrows}>
              <p className={styles.cvgrow}>
                <RightsChip rightsType="R1" compact />
                {coverageFromKo(coverage.start)}
              </p>
              <p className={styles.cvgrow}>
                <RightsChip rightsType="R2" compact />
                {coverageFromKo(coverage.convertible_start)}
              </p>
            </div>
          ) : null}
          <p className={styles.cap}>{COVERAGE_BOUNDARY_KO}</p>
        </div>
      </CraftPanel>
    </section>
  );
}
