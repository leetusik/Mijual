import type { ElementType, HTMLAttributes, ReactNode } from "react";
import styles from "./CraftPanel.module.css";

/**
 * The craft panel (R2.1) — the shell every cosmos surface is built out of.
 *
 * > **Craft panel** = translucent dark card: `--surface-card`, 1px
 * > `--border-strong`, top-edge glow `box-shadow: var(--panel-glow)`, and 9px
 * > corner brackets (2px L-shapes, `--panel-bracket`) at all four corners. Used
 * > for: value card, countdown/stats card, 소멸주의보, board.
 *
 * There is deliberately **no ornament-free variant here**. R7's ops idiom strips
 * exactly what this component adds (no glow, no brackets, opaque flat `#0e1a15`)
 * — it is a different panel, not a mode of this one, and it belongs to `P5.S17`.
 */
export type CraftPanelProps = {
  /** `alert` swaps the hairline for `--alert` — 소멸주의보 and 기재 불일치 only. */
  tone?: "default" | "alert";
  /** The element to render. Panels are usually sections; the board is one too. */
  as?: ElementType;
  children: ReactNode;
} & HTMLAttributes<HTMLElement>;

export function CraftPanel({
  tone = "default",
  as: Tag = "section",
  className,
  children,
  ...rest
}: CraftPanelProps) {
  const classes = [styles.panel, tone === "alert" ? styles.alert : null, className]
    .filter(Boolean)
    .join(" ");

  return (
    <Tag className={classes} {...rest}>
      {children}
      <span aria-hidden="true" className={`${styles.bracket} ${styles.tl}`} />
      <span aria-hidden="true" className={`${styles.bracket} ${styles.tr}`} />
      <span aria-hidden="true" className={`${styles.bracket} ${styles.bl}`} />
      <span aria-hidden="true" className={`${styles.bracket} ${styles.br}`} />
    </Tag>
  );
}
