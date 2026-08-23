"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { CITATION_CHIP_KO, CLOSE_GLYPH, CLOSE_KO, dartSourceLabelKo } from "@/lib/copy";
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
 * ## The R10 re-cut (`P8.S7`)
 *
 * R10 keeps the word — the provenance line names it (「각 항목의 [근거]가 …」) —
 * and changes the target and the opening:
 *
 * - the trigger is a **real target**: 32px desktop, 44px ≤767px, made with
 *   padding and given back with an equal negative margin so the row does not
 *   move;
 * - the quote opens as an **overlay popover** rather than an inline panel, so
 *   the values around it keep their places while a reader reads. Close = the
 *   popover's `×`, a click outside, or Esc — and the trigger itself, which now
 *   carries the open state (`--live-tint` + `aria-expanded="true"`).
 *
 * The re-cut reaches every surface that renders this primitive (event detail and
 * 조회); the ask surface's numbered `InlineCitation` is R6-4's own component and
 * is not this one.
 *
 * **Where a `[근거]` is placed is the surface's decision, not this component's**
 * — R10's density rule (a chip only where the on-screen value differs from the
 * filing's words) lives in `components/event/fieldOrder.ts`.
 *
 * ## Three payload states, and no fourth (`P5.S20`)
 *
 * A served value carries **either** `quote` + `span` (one cell) **or** `parts`
 * (≥ 2 addends, each `{quote, span}`, summing exactly to the value) **or**
 * neither. `mijual.present.Figure` refuses every other combination, so this
 * component only has to honour them:
 *
 * - one quote → one passage;
 * - parts → **every part rendered verbatim and separately**, inside the popover.
 *   The sum is printed in the filing *nowhere*, so joining the addends into one
 *   quote string would fabricate a sentence, and showing one addend would be a
 *   false citation — which is the defect D4 existed to close;
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
  const wrap = useRef<HTMLSpanElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const pop = useRef<HTMLSpanElement | null>(null);

  // R10 anchors the popover to the trigger — `left:0` desktop, `right:0` ≤767px.
  // On the round's card that is always in view, because a card frame is drawn
  // inside a wide canvas; on a real page a chip sits wherever its value ends,
  // and the same declarations then carry part of the verbatim quote past the
  // viewport edge (measured at 390px: a mid-row chip opened a 340px popover
  // starting at −90px, clipping the first characters of every line).
  //
  // So the anchor is kept exactly as drawn and only **slid back inside** when it
  // would be clipped. Nothing approved changes — width, colour, border, padding
  // and the 6px drop are the record's; only the horizontal offset moves, and
  // only far enough to make the quote readable, which is the whole point of the
  // affordance.
  const fit = useCallback((panel: HTMLSpanElement | null) => {
    if (!panel) return;
    panel.style.transform = "";
    const box = panel.getBoundingClientRect();
    const gutter = 8;
    let dx = 0;
    if (box.left < gutter) dx = gutter - box.left;
    else if (box.right > window.innerWidth - gutter) dx = window.innerWidth - gutter - box.right;
    if (dx) panel.style.transform = `translateX(${Math.round(dx)}px)`;
  }, []);

  // A ref callback rather than a layout effect: it runs in the same commit that
  // mounts the popover, so the clamped position is the first one painted.
  const holdPop = useCallback(
    (node: HTMLSpanElement | null) => {
      pop.current = node;
      fit(node);
    },
    [fit],
  );

  // R10 §6's three closes. A pointer press outside the affordance and Esc are
  // document-level, so they are only listened for while the popover is open —
  // there is one of these on nearly every row of a detail page.
  useEffect(() => {
    if (!open) return;
    const away = (event: MouseEvent) => {
      if (wrap.current && !wrap.current.contains(event.target as Node)) setOpen(false);
    };
    const key = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setOpen(false);
      // Esc is a keyboard close, so the keyboard gets its place back. A pointer
      // close moves nothing, because nothing was taken.
      trigger.current?.focus();
    };
    const refit = () => fit(pop.current);
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", key);
    window.addEventListener("resize", refit);
    return () => {
      document.removeEventListener("mousedown", away);
      document.removeEventListener("keydown", key);
      window.removeEventListener("resize", refit);
    };
  }, [fit, open]);

  const passages: readonly QuotePart[] =
    parts && parts.length > 0 ? parts : quote ? [{ quote }] : [];

  // Uncitable: no chip, no panel, no placeholder.
  if (passages.length === 0) {
    return null;
  }

  const name = label ? `${label} ${CITATION_CHIP_KO}` : CITATION_CHIP_KO;

  return (
    // Every element in here is phrasing content: a Citation sits inline inside a
    // field row's <p>, and a <div> would be reparented by the HTML parser and
    // break hydration.
    <span ref={wrap} className={className ? `${styles.wrap} ${className}` : styles.wrap}>
      <button
        ref={trigger}
        type="button"
        className={styles.chip}
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={label ? name : undefined}
        onClick={() => setOpen((was) => !was)}
      >
        {CITATION_CHIP_KO}
      </button>

      {open ? (
        <span ref={holdPop} id={panelId} role="dialog" aria-label={name} className={styles.pop}>
          <span className={styles.head}>
            <span className={styles.quotes}>
              {passages.map((part, index) => (
                <span
                  // The addends of one figure have no id of their own; their
                  // order is the filing's and is stable for a given payload.
                  key={`${index}-${part.quote.slice(0, 24)}`}
                  className={`${styles.quote} ${styles.part}`}
                >
                  {part.quote}
                </span>
              ))}
            </span>
            <button
              type="button"
              className={styles.close}
              aria-label={CLOSE_KO}
              onClick={() => {
                setOpen(false);
                trigger.current?.focus();
              }}
            >
              {CLOSE_GLYPH}
            </button>
          </span>

          {rceptNo ? (
            <a
              className={styles.link}
              href={dartUrl(rceptNo)}
              target="_blank"
              rel="noopener noreferrer"
            >
              {dartSourceLabelKo(rceptNo)}
            </a>
          ) : null}
        </span>
      ) : null}
    </span>
  );
}
