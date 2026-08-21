import type { ReactNode } from "react";
import { LAPSE_ALERT_KO } from "@/lib/copy";
import { CraftPanel } from "./CraftPanel";
import styles from "./LapseAlert.module.css";

/**
 * 소멸주의보 — R1's confirmed sub-brand element, in R2's craft/hazard form.
 *
 * R1 fixed it as a named element (operator decision 2): a card with the `--alert`
 * border, a 4px left rule and a filled mono tag. R2 re-cut it for the cosmos
 * landing as a **craft panel with a 10px hazard stripe** on the left edge
 * (repeating −45° `--alert` stripes, 5px on / 5px off) and the filled 소멸주의보
 * badge, sitting full content-width between the anchor panels and the board.
 * Both forms are here; `craft` is what the app renders.
 *
 * The body is the caller's — R2 fills it with 발표용 문장 4 carrying **live**
 * numbers from the same `/board/summary` the stats card reads, so the strip and
 * the card can never disagree. That copy and those numbers are `P5.S12`'s; this
 * component owns the placard, the badge and the stripe, and invents no sentence.
 *
 * Numerals inside the body go in `<span className={`mono ${lapseNumeralClass}`}>`
 * so they render mono 600 in `--alert` as R1 specifies.
 */
export type LapseAlertProps = {
  variant?: "craft" | "plain";
  children: ReactNode;
  className?: string;
};

/** The mono-600-in-`--alert` treatment R1 gives the strip's live numbers. */
export const lapseNumeralClass: string = styles.num;

export function LapseAlert({ variant = "craft", children, className }: LapseAlertProps) {
  const classes = [styles.strip, variant === "craft" ? styles.craft : styles.plain, className]
    .filter(Boolean)
    .join(" ");

  const body = (
    <>
      <span className={styles.badge}>{LAPSE_ALERT_KO}</span>
      <span className={styles.body}>{children}</span>
    </>
  );

  // R2's form is a craft panel (translucent card, brackets, top-edge glow) with
  // the alert hairline; R1's is the bare card with the 4px rule.
  return variant === "craft" ? (
    <CraftPanel tone="alert" as="aside" className={classes}>
      {body}
    </CraftPanel>
  ) : (
    <aside className={`${classes} ${styles.plainCard}`}>{body}</aside>
  );
}
