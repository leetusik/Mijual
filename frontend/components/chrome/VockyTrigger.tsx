import styles from "./VockyTrigger.module.css";

/**
 * A vocky trigger — one of exactly **three** in the product.
 *
 * > Triggers: nav `[의견]` button, mobile sheet 의견 보내기 row, footer 의견
 * > 보내기 link — each a plain element with `data-vocky-trigger`. Trigger
 * > styling: mono 12, 1px `--border-strong`, white bg, `--ink-2`; hover =
 * > `--surface-raised` + border `--ink-3`; focus = 2px `--focus-ring`. **Do not
 * > style the widget itself; do not add a floating button.** (R2 §vocky)
 *
 * The contract is the attribute: vocky's own script binds to
 * `[data-vocky-trigger]` and opens **its own UI**, which is an external product
 * and is never styled, wrapped or overridden here. That is also why this
 * component has no `onClick` — a handler would be this app deciding what the
 * widget does.
 *
 * ## Why the styling differs per surface, and where each variant comes from
 *
 * R2 §vocky's paragraph describes the trigger's **chip** form on the light
 * theme; R2.1 then re-cut the chrome on cosmos ("Chrome cards (Nav/Footer/
 * Feedback) re-cut on cosmos with the white ring wordmark") and R2.1 governs
 * where they conflict. What survives unchanged is everything token-based (mono
 * 12, `--ink-2`, hover `--surface-raised` + `--ink-3`, the 2px focus ring) —
 * those tokens remap themselves inside `.cosmos`. What R2.1 restates is the
 * nav's hairline (`rgba(255,255,255,.3)` in §Page shell) and, unavoidably, the
 * white background: a white chip on a transparent 52px bar over the starfield is
 * the one thing the dark re-cut cannot keep, so the chip is transparent and
 * carries the round's own hairline.
 *
 * The other two placements are not chips at all in the record — a sheet **row**
 * (rows ≥48px, beside the destinations) and a quiet footer **link** in the mono
 * 11 bottom row — so they take their surface's type and stay quiet, which is
 * decision §6-4's whole point: "chrome-level but not floating … quiet footer
 * link. No floating corner button — it would fight the control-room density."
 * P6's launcher owns the bottom-right corner (R6: 런처·위젯은 vocky 트리거와
 * 모서리 충돌 금지), and nothing here goes near it.
 */
export type VockyTriggerProps = {
  /** Which of the three placements this is. */
  surface: "nav" | "sheet" | "footer";
  /** The signed label — `[의견]` in the nav, 의견 보내기 elsewhere. */
  children: string;
  className?: string;
};

export function VockyTrigger({ surface, children, className }: VockyTriggerProps) {
  const classes = [styles.trigger, styles[surface], className].filter(Boolean).join(" ");

  return (
    <button type="button" data-vocky-trigger="" className={classes}>
      {children}
    </button>
  );
}
