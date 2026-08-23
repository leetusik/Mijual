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

/**
 * R10 §5 — **which rows carry a `[근거]`**, as data rather than as a decision
 * scattered through the markup.
 *
 * The operator's rule, given inside the R10 session: a citation chip belongs
 * where **the value on the screen differs from the filing's words** — a date, a
 * figure or a ratio *extracted* from prose, or an input a derived value was
 * built from. Where the value **is** the filer's sentence, printed 1:1, the
 * quote panel would only re-print what the reader is already looking at; those
 * rows carry no chip, and the section closes with one mono `DART 원문 {rcept} ↗`
 * line instead (`.secsrc`). Provenance does not shrink — every value is still
 * one tap from the 원문 — but the number of chips on a page stops tracking the
 * number of rows.
 *
 * The two lists below are R10's own, mapped onto the payload's field keys:
 *
 * | R10 names | key | chip |
 * |---|---|---|
 * | 매매기간 | `warrant_trading_period` | yes |
 * | 초과청약 비율 | `excess_subscription` | yes |
 * | 보호예수 해제일 | `lockup_release` | yes |
 * | 발행가액 산정방법 | `issue_price_formula` | no |
 * | 청약 취급처 표 | `subscription_agents` | no |
 * | 리픽싱 조건 | `refixing_terms` | no |
 * | 콜·풋 스케줄 | `option_schedule` | no |
 * | 통지 방법 · 접수처 | `dissent_notice_procedure` | no |
 *
 * 확정발행가 · 할인율 · 청약 결과 수치 · 정정 요약 · 철회 근거 are the rule's
 * other half and are not rows: they are `Figure`s in the 환산 chain, the 청약
 * 결과 inset, the 정정 story and the 철회 evidence, each of which cites its own
 * value where the payload carries a quote (`P8.S7`: the live 확정발행가 carries
 * none, so it renders no chip — `Citation` refuses to promise evidence it does
 * not have).
 *
 * A key in **neither** list falls to the reading below: chip when the payload
 * carries a quote at all. Two live keys are in that position and both are
 * genuinely the first kind — `forfeited_share_method` renders a normalised
 * sentence while its quote is a different passage of the filing, and
 * `appraisal_price` renders a number extracted from one.
 */
const VERBATIM_FIELDS = new Set([
  "issue_price_formula",
  "subscription_agents",
  "refixing_terms",
  "option_schedule",
  "dissent_notice_procedure",
]);

/** Does this field's row carry a `[근거]`? `hasQuote` is the payload's answer to
 * "is there anything to cite at all" — a field with no quote never had a chip. */
export function fieldCites(fieldKey: string, hasQuote: boolean): boolean {
  return hasQuote && !VERBATIM_FIELDS.has(fieldKey);
}
