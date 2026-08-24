"use client";

import { useId, useState } from "react";
import { dartUrl } from "@/lib/api";
import type { AskChip } from "@/lib/ask";
import { dartSourceLabel } from "./copy";
import styles from "./Ask.module.css";

/**
 * 인라인 인용 (R6-4) — the numbered chip and the quote block it opens in place.
 *
 * > 번호 칩: mono 10px, `--live` 잉크, 1px rgba(95,208,165,.4) 테두리, 같은 근거 =
 * > 같은 번호. 탭 → 제자리 인용 블록: `--surface-inset` + 좌측 2px `--live`,
 * > verbatim quote + `DART 원문 {rcept_no} ↗`. 닫기 = 칩 재탭. **Citation
 * > 프리미티브의 인라인형 — 블록형과 스타일 공유.**
 *
 * So this is `components/Citation.tsx`'s anatomy with R6-4's chip in place of the
 * `[근거]` one: the same grid height animation (opening to the panel's own height
 * rather than a guessed one), the same 180px quote scroll floor, the same
 * `inert` collapse so a shut panel's DART link is unreachable, and the same rule
 * that **every element is phrasing content** — a `<div>` in here would be
 * reparented out of the paragraph by the HTML parser and break hydration.
 *
 * Two things it does *not* share, both because the payload differs:
 *
 * - the chip's text is the **number**, and the same 근거 keeps it for the whole
 *   answer (the server assigns it once, on first use);
 * - a chip with no quote is the **API-tier** citation (R3 rule), and **R14
 *   finding 10 re-cut what its block holds**: the `DART 원문 {rcept_no} ↗` link,
 *   alone (`.quoteLinkSolo`, so nothing sits above it to need a top margin). R3's
 *   explanatory sentence `API_TIER_KO` is retired — 원문 스팬 and 인용 핸들 are our
 *   contract's vocabulary, and the link's existence already is what the sentence
 *   said. It is still a citation, not a missing one — unlike the primitive's third
 *   state, which renders no chip at all. Closes P7 Q7①.
 *
 * `span` is carried on the payload and deliberately **not rendered**: an offset
 * is internal, exactly as the primitive records.
 *
 * ## R16 §2.6 — the same chip, in two more **places**
 *
 * 「**변경 없음** … 새로운 것은 칩이 붙는 **자리**뿐이다: 프로즈 + 데이터 행 값 +
 * 계산 입력.」 So this component is unchanged and gains one prop that says which
 * place it is in, because the two places lay their contents out differently:
 *
 * - `"prose"` (default) — inside the sentence, where the 인용 블록 opens under it
 *   across the paragraph, exactly as R6-4 signed it;
 * - `"row"` — the fixed **셋째 칸** of a 데이터 행 / 계산 입력 (§2.3), whose width
 *   *is* the chip's and which never scrolls away with the value. The panel cannot
 *   be measured inside that column: a `grid-template-columns: minmax(0,40%)
 *   minmax(0,1fr) auto` track sized by a quote's max-content squeezes the value
 *   column to **zero** (measured in Chrome before this prop existed — the value
 *   simply vanished). So in a row the two halves are grid items of the row
 *   itself: the chip stays in the third column and the block opens **under the
 *   row, across the block** — the same 제자리 relationship the prose has to its
 *   sentence, and R6 §Mobile's 「인용 블록 전폭」 read at row scale. `Ask.module.css`
 *   holds the three placement rules; nothing about the chip or the panel changes.
 */
export function InlineCitation({
  chip,
  place = "prose",
}: {
  chip: AskChip;
  place?: "prose" | "row";
}) {
  const panelId = useId();
  const [open, setOpen] = useState(false);

  return (
    <span className={place === "row" ? styles.citationRow : undefined}>
      <button
        type="button"
        className={styles.chip}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((was) => !was)}
      >
        {chip.number}
      </button>
      <span
        id={panelId}
        className={`${styles.quoteWrap} ${open ? styles.quoteOpen : ""}`}
        inert={!open}
      >
        <span className={styles.quoteClip}>
          <span className={styles.quotePanel}>
            {chip.quote === undefined ? null : (
              // The filing's own words: never paraphrased, corrected or
              // re-punctuated, so the whitespace it was filed with survives too.
              <span className={styles.quote}>{chip.quote}</span>
            )}
            <a
              className={
                chip.quote === undefined
                  ? `${styles.quoteLink} ${styles.quoteLinkSolo}`
                  : styles.quoteLink
              }
              href={dartUrl(chip.rcept_no)}
              target="_blank"
              rel="noopener noreferrer"
            >
              {dartSourceLabel(chip.rcept_no)}
            </a>
          </span>
        </span>
      </span>
    </span>
  );
}
