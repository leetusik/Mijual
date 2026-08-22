import { count, won } from "@/lib/format";
import type { BoardSummary } from "@/lib/types";
import { SearchRow } from "@/components/lookup/SearchRow";
import { EstimateValue } from "./EstimateValue";
import {
  HERO_STAT_VALUE_KO,
  HERO_STAT_WATCHING_KO,
  HERO_STAT_WITHIN_30D_KO,
  HERO_SUB_KO,
  HERO_TITLE_KO,
} from "./copy";
import styles from "./Hero.module.css";

/**
 * The hero (R2 §Hero, as R2.1 recomposed it — search-first).
 *
 * > No logo or eyebrow in the hero body (the nav carries the mark). Centered: H1
 * > 52px/700 → sub 17px → search row (console input + 조회, 52px tall, 560px
 * > total) → mono stat line: 2026년 소멸한 신주인수권 가치 718.1억원「추정」 ·
 * > 감시 중 488건 · 30일 이내 마감 34건 (number+건 spans nowrap). Mobile: H1
 * > 34px, 48px controls. This IS the [내 종목 조회] surface — no separate bridge
 * > panel; submit goes to R4's 조회.
 *
 * Two things the round decides that this file only carries out:
 *
 * - **The orbit ellipses are the hero's alone** (980×280 + 1200×360, rotate −14°,
 *   orbiting star 26s), they must clear the nav line and the first panel, and
 *   they are **never shrunk** — the hero is given vertical room instead
 *   (110/160px desktop padding). On a narrow viewport they are clipped by the
 *   hero's own overflow, which is not the same thing as shrinking them.
 * - **The submit is a plain GET form** to `/stocks` with the API's own `q`
 *   parameter, so the hero works before any JavaScript does and the page path
 *   and the contract path stay one vocabulary (`P5.S11`'s route map). `P7.S4`
 *   moved that row into `lookup/SearchRow` — one component for this surface and
 *   R4's header, adding the typeahead to both at once and leaving the GET
 *   submit, the geometry and the classes exactly as the round signed them.
 *
 * The three stat numbers come from the **same** `/board/summary` object the
 * countdown/stats card reads, which is what stops one page from printing two
 * readouts of one number.
 */
export function Hero({ summary }: { summary: BoardSummary }) {
  const value = summary.lapsed_value;

  return (
    <section className={styles.hero}>
      {/* R2.1: the rings live in the hero only. Decoration, so it is hidden from
          the a11y tree and never intercepts a click. */}
      <div className={styles.orbits} aria-hidden="true">
        <div className={styles.stage}>
          <span className={styles.ellipseSmall} />
          <span className={styles.ellipseLarge} />
          <span className={styles.track}>
            <span className={styles.orbiter} data-motion="tick" />
          </span>
        </div>
      </div>

      <div className={`content ${styles.inner}`}>
        <h1 className={styles.title}>{HERO_TITLE_KO}</h1>
        <p className={styles.sub}>{HERO_SUB_KO}</p>

        {/* The row itself is `P7.S4`'s shared client component — the same one R4's
            header renders — so the two search rows cannot drift apart. It still
            renders this surface's own form/input/button classes, and it is still
            a plain GET to `/stocks`; the candidate list is the addition. The
            label is the surface's own signed name; the placeholder is R4's "hero
            placeholder", and a placeholder alone is not a label. */}
        <SearchRow
          label={HERO_TITLE_KO}
          variant="hero"
          classNames={{ form: styles.search, input: styles.input, submit: styles.submit }}
        />

        <p className={styles.stats}>
          {/* A figure the summary does not carry has no segment at all — the
              contract omits a key rather than sending a zero, and the surface
              omits the phrase rather than printing one. */}
          {value ? (
            <>
              <span className={styles.stat}>
                {HERO_STAT_VALUE_KO}{" "}
                <EstimateValue estimated={value.estimated} valueClassName={styles.statValue}>
                  {won(value.value)}
                </EstimateValue>
              </span>
              <span aria-hidden="true" className={styles.dot}>
                ·
              </span>
            </>
          ) : null}
          <span className={styles.stat}>
            {HERO_STAT_WATCHING_KO}{" "}
            <span className={styles.nowrap}>{count(summary.watching)}건</span>
          </span>
          <span aria-hidden="true" className={styles.dot}>
            ·
          </span>
          <span className={styles.stat}>
            {HERO_STAT_WITHIN_30D_KO}{" "}
            <span className={styles.nowrap}>{count(summary.within_30d)}건</span>
          </span>
        </p>
      </div>
    </section>
  );
}
