import type { ReactNode } from "react";
import { ESTIMATE_TAG_KO } from "@/lib/copy";
import styles from "./EstimateMarker.module.css";

/**
 * The one estimate mark in this product.
 *
 * R2's gate ruling and R3's re-cut make the bordered 「추정」 tag system-wide and
 * **retire `▷` from every UI surface** (`docs/current/frontend.md`'s supersession
 * table; `▷` survives only in pipeline output and the ops panel, where the
 * boundary is the source). R1's law still governs the shape: the tag inherits its
 * scale and never sets its own size, because urgency and estimate emphasis are
 * colour-only, never size.
 *
 * ## Why `estimated` is required and has no default
 *
 * `states-and-trust.md` §1: *an estimate never renders untagged; a fact never
 * carries the mark.* On the server that rule is structural —
 * `mijual.present.Figure.estimated` has no default, so a value that forgets to
 * say which kind it is does not construct. This prop is the same rule on this
 * side of the wire: the type makes it impossible to render a value through this
 * primitive without answering the question, and the runtime guard below catches
 * a payload whose `estimated` key went missing in transit rather than letting a
 * derived number reach a reader looking like a fact.
 *
 * ```tsx
 * <EstimateMarker estimated={figure.estimated}>
 *   <span className="mono">718.1억원</span>
 * </EstimateMarker>
 * ```
 */
export type EstimateMarkerProps = {
  /** Straight from the payload's `estimated`. No default, on purpose. */
  estimated: boolean;
  /** The already-formatted value. Numerals are the caller's `.mono` span. */
  children: ReactNode;
  className?: string;
};

export function EstimateMarker({ estimated, children, className }: EstimateMarkerProps) {
  if (typeof estimated !== "boolean") {
    throw new Error(
      "EstimateMarker: `estimated` must be a boolean read from the payload. " +
        "Every value in the contract carries it; a missing flag means the value " +
        "was built somewhere it should not have been, and rendering it untagged " +
        "would break the product's one trust claim.",
    );
  }

  return (
    <span className={className ? `${styles.marker} ${className}` : styles.marker}>
      {children}
      {estimated ? <span className={styles.tag}>{ESTIMATE_TAG_KO}</span> : null}
    </span>
  );
}
