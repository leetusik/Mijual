import type { ReactNode } from "react";
import { EstimateMarker } from "@/components";
import styles from "./EstimateValue.module.css";

/**
 * A landing value with its 「추정」 tag at the size **R2 asks for on this page**.
 *
 * R2 §Cosmos: "Estimate mark (landing surfaces): a bordered sans **10px** 「추정」
 * tag beside the value". R3's system-wide re-cut states the same tag as
 * **0.56em of its context**, and R1's law is that a primitive never sets its own
 * size — 0.56 × ~17.9px is 10px, which is how one rule satisfies both readings
 * (`EstimateMarker.module.css` says so in as many words).
 *
 * So the surface supplies the context rather than the primitive: this wrapper
 * puts the marker in a `--text-lg` (17px) context — the closest token to R2's
 * own ~17.9px, giving a 9.5px tag — and the **value keeps its own size** through
 * `valueClassName`, which is 46px on the value card and the line's own size in
 * the hero and band lines. Nothing about the primitive is restyled: it is
 * composed, which is what an em-sized component is for.
 *
 * (The footer's tag renders 6.72px for the opposite reason — `P5.S11` left its
 * 12px sentence as the context and flagged it. Both readings are `P5.S19`'s to
 * check against the cards; neither slice touched `EstimateMarker`.)
 */
export function EstimateValue({
  estimated,
  valueClassName,
  children,
}: {
  /** Straight from the payload's `estimated` — never a literal (`P5.S10` note 9). */
  estimated: boolean;
  valueClassName?: string;
  children: ReactNode;
}) {
  return (
    <EstimateMarker className={styles.context} estimated={estimated}>
      <span className={valueClassName}>{children}</span>
    </EstimateMarker>
  );
}
