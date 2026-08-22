/**
 * The order the detail page reads its 본문 fields in, and the one field that is
 * not a row — as plain data, so the page and the 질문 스트립 cannot disagree.
 *
 * Both constants were `Fields.tsx`'s (`P5.S13`); `P6.S6` moved them here
 * unchanged because the strip's preset chips are generated from **the same
 * gate-passing fields the page renders** (R6-2), and a chip order that differed
 * from the row order would be a second reading of one payload. No React, no CSS
 * and no copy lives here, so a client component may import it without pulling the
 * detail surface into its bundle.
 */

/** Rendered by the 정정 strip and the CorrectionStory, never as a field row.
 *
 * `correction_interpretation` is a served field like any other, but its value is
 * the 정정 story itself (`field_moves` + `interpretation`) — R3 gives it §5's
 * strip and the CorrectionStory view, and printing its nested record in a 220px
 * row would be neither the design nor readable. */
export const STORY_FIELD = "correction_interpretation";

/** Row order = **the filing's own §7 numbering** (`copy-inventory.md` §Field keys
 * and their Korean names), which is also the order R3's ① card reads in;
 * `appraisal_price` is the label-tier 11th field (`P5.S6`) and has no §7 number,
 * so it follows. A field this list does not know keeps its served position. */
export const FIELD_ORDER = [
  "warrant_trading_period",
  "subscription_agents",
  "forfeited_share_method",
  "excess_subscription",
  "issue_price_formula",
  "refixing_terms",
  "option_schedule",
  "lockup_release",
  "dissent_notice_procedure",
  "appraisal_price",
];

/** A field's place in the reading order; an unknown key sorts after all of them. */
export function fieldRank(key: string): number {
  const index = FIELD_ORDER.indexOf(key);
  return index === -1 ? FIELD_ORDER.length : index;
}
