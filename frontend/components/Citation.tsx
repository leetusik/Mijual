"use client";

import { useId, useState } from "react";
import { CITATION_CHIP_KO } from "@/lib/copy";
import { dartUrl } from "@/lib/api";
import type { QuotePart } from "@/lib/types";
import styles from "./Citation.module.css";

/**
 * The citation affordance: `[근거]` → the filing's own words.
 *
 * `states-and-trust.md` §2 — every rendered field carries a verbatim `quote`, a
 * `span` and the `rcept_no` it came from, and that triple is what makes "where
 * did this number come from" answerable in one tap. The affordance is **per
 * field, not per card** (one grounding sample carries six independent citations
 * on one event), and the quote is never paraphrased, corrected or re-punctuated.
 *
 * ## Three payload states, and no fourth (`P5.S20`)
 *
 * A served value carries **either** `quote` + `span` (one cell) **or** `parts`
 * (≥ 2 addends, each `{quote, span}`, summing exactly to the value) **or**
 * neither. `mijual.present.Figure` refuses every other combination, so this
 * component only has to honour them:
 *
 * - one quote → one panel;
 * - parts → **every part rendered verbatim and separately**. The sum is printed
 *   in the filing *nowhere*, so joining the addends into one quote string would
 *   fabricate a sentence, and showing one addend would be a false citation —
 *   which is the defect D4 existed to close;
 * - neither → **no chip at all**. The value is uncitable; `rcept_no` still opens
 *   the filing on DART, but through the row's own link, not through this
 *   primitive. Rendering an empty chip would promise evidence that is not there.
 */
export type CitationProps = {
  /** The filing this quote was read from — the DART link's `rcpNo`. */
  rceptNo?: string | null;
  /** The one verbatim passage, when the value has a single cell. */
  quote?: string | null;
  /** The quote's character offsets in the stored document. Accepted so a call
   * site can pass the payload's citation triple whole, and deliberately **not
   * rendered**: an offset is internal, like a gate reason code. */
  span?: readonly number[] | null;
  /** Every addend, when the filer printed the value as a sum of table rows. */
  parts?: readonly QuotePart[];
  /** Accessible context for the chip, e.g. the field's Korean row label. */
  label?: string;
  className?: string;
};

export function Citation({ rceptNo, quote, parts, label, className }: CitationProps) {
  // `span` is intentionally unread — see the prop's doc comment.
  const panelId = useId();
  const [open, setOpen] = useState(false);

  const passages: readonly QuotePart[] =
    parts && parts.length > 0 ? parts : quote ? [{ quote }] : [];

  // Uncitable: no chip, no panel, no placeholder.
  if (passages.length === 0) {
    return null;
  }

  return (
    <span className={className}>
      <button
        type="button"
        className={styles.chip}
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={label ? `${label} ${CITATION_CHIP_KO}` : undefined}
        onClick={() => setOpen((was) => !was)}
      >
        {CITATION_CHIP_KO}
      </button>
      <span
        id={panelId}
        className={`${styles.wrap} ${open ? styles.open : ""}`}
        // Collapsed, not merely invisible: an assistive reader should not meet a
        // quote the reader has not opened, and the DART link inside must not be
        // reachable by keyboard while the panel is shut.
        inert={!open}
      >
        <span className={styles.clip}>
          <span className={styles.panel}>
            {passages.map((part, index) => (
              <span
                // The addends of one figure have no id of their own; their order
                // is the filing's and is stable for a given payload.
                key={`${index}-${part.quote.slice(0, 24)}`}
                className={`${styles.quote} ${styles.part}`}
              >
                {part.quote}
              </span>
            ))}
            {rceptNo ? (
              <a
                className={styles.link}
                href={dartUrl(rceptNo)}
                target="_blank"
                rel="noopener noreferrer"
              >
                {rceptNo}
              </a>
            ) : null}
          </span>
        </span>
      </span>
    </span>
  );
}
