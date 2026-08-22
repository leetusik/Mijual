"use client";

import { useId, useState } from "react";
import { dartUrl } from "@/lib/api";
import type { AskChip } from "@/lib/ask";
import { API_TIER_KO, dartSourceLabel } from "./copy";
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
 * - a chip with no quote is the **API-tier** citation (R3 rule): the block says
 *   「DART 공시 API 수치 — 원문 스팬 없음, 접수번호가 인용 핸들」 in the signed
 *   words and links out. That is a citation, not a missing one — unlike the
 *   primitive's third state, which renders no chip at all.
 *
 * `span` is carried on the payload and deliberately **not rendered**: an offset
 * is internal, exactly as the primitive records.
 */
export function InlineCitation({ chip }: { chip: AskChip }) {
  const panelId = useId();
  const [open, setOpen] = useState(false);

  return (
    <span>
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
            {chip.quote === undefined ? (
              <span className={styles.apiTier}>{API_TIER_KO}</span>
            ) : (
              // The filing's own words: never paraphrased, corrected or
              // re-punctuated, so the whitespace it was filed with survives too.
              <span className={styles.quote}>{chip.quote}</span>
            )}
            <a
              className={styles.quoteLink}
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
