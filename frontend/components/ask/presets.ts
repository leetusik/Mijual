/**
 * 프리셋 칩 — generated from **that event's gate-passing fields**, and from
 * nothing else.
 *
 * > **R6-2 · Presets-first** — 프리셋은 그 이벤트의 게이트 통과 필드에서 생성
 * > (답할 수 없는 질문은 프리셋으로 제안하지 않음), 자유 입력은 한 단계 뒤
 * > ("직접 질문 입력 →").
 *
 * The generation rule, in full, because it is the part of the 질문 스트립 that is
 * a *decision* rather than a layout:
 *
 * 1. **The input is the served `fields` map**, which by contract holds only
 *    gate-passing fields — 「a gate-blocked field has no key here at all」
 *    (`lib/types.ts`, `states-and-trust.md` §4). So "generated from the
 *    gate-passing fields" is literally `Object.values(fields)`, and there is no
 *    filter this module could get wrong: a field the gate failed never arrives.
 * 2. **`correction_interpretation` is dropped**, the same exclusion the page's
 *    own field sections make: its value is the 정정 story, not a field row, and
 *    R3 renders it in the 정정 strip instead (`components/event/fieldOrder.ts`).
 * 3. **Order = the page's reading order** (`FIELD_ORDER`), so the chips arrive in
 *    the order the rows below them do.
 * 4. **A chip shows the served label and sends a signed question** — see below.
 *
 * ## R14 Q-D — what a chip *sends* is no longer what it *reads*
 *
 * R6-2 left the chip's text and its question as one string, so a noun-phrase
 * `korean_name` (신주인수권증서 상장·매매기간) became the reader's own question
 * bubble verbatim: the thread showed noun phrases where the reader had asked
 * something. R14's walk found it (finding 6) and the round decided **labels shown,
 * sentences sent**:
 *
 * - the **label** stays the served `korean_name` — the same words the field row
 *   below the strip prints, off the wire, so this file still holds no field-name
 *   table and never renames a field;
 * - the **question** is a sentence **R14 signed by hand**, one per key of
 *   `FIELD_ORDER` (result.md §Copy, R14-D1…D9, 2026-08-24). `forfeited_share_method`
 *   keeps **R6's own** sentence, which the record wrote first and R14 did not
 *   re-sign.
 *
 * **A key that is not in the table produces no chip.** That is the round's own
 * rule and the reason the table below is exhaustive rather than a lookup with a
 * default: a fallback that sent the label would quietly restore the behaviour Q-D
 * removed, one new field key at a time. A field with no `korean_name` yields no
 * chip either (the label is the server's — `components/event/copy.ts`'s rule), so
 * a chip exists only where **both** halves are known.
 *
 * **Why no sentence template.** Turning every label into 「{label}은 어떻게
 * 되나요?」 would be inventing Korean copy, which this phase treats as a design
 * change (note 17), and it would be *wrong* Korean for most of the labels
 * (신주인수권증서 상장·매매기간 is not something that 처리된다). The nine sentences
 * below are not composed from the labels — they were written and signed in the
 * round, each with its own reason in `result.md` §Copy (e.g. `excess_subscription`
 * asks 「어떤 조건으로」 rather than 「얼마까지」 because a limit exists only against
 * a holding, and `issue_price_formula` asks how the price is *calculated* because
 * a 확정 전 금액 is never explained on this surface).
 */

import { STORY_FIELD, fieldRank } from "@/components/event/fieldOrder";
import type { FieldPayload } from "@/lib/types";
import { FORFEITED_FIELD, FORFEITED_QUESTION_KO } from "./copy";

export type AskPreset = {
  /** The field key it was generated from — a React key, never rendered. */
  key: string;
  /** What the chip reads: the served `korean_name`, verbatim. */
  label: string;
  /** What is sent as the question: the round's signed sentence for that key. */
  question: string;
};

/**
 * 필드 키 → 서명된 질문 (R14 §3 · result.md §Copy, all dated 2026-08-24).
 *
 * The keys are `FIELD_ORDER`'s ten, and the order here is that order — this is
 * the table the round signed, not a re-derivation of it. Every sentence carries
 * the signature the record gave it; nothing may be added to this table outside a
 * design round.
 */
const PRESET_QUESTIONS: Record<string, string> = {
  /** R14-D1 — 매매기간 is a 「언제부터 언제까지」 fact, so the question asks for both ends. */
  warrant_trading_period: "신주인수권증서는 언제부터 언제까지 매매할 수 있나요?",
  /** R14-D2 — the served value is 대상자별 증권사 + 청약일, so the question asks 어디서·언제. */
  subscription_agents: "청약은 어느 증권사에서 언제 받나요?",
  /** R6 — the one preset sentence the record wrote first (result.md §Composition
   * examples). R14 kept it as it was rather than signing a second version. */
  [FORFEITED_FIELD]: FORFEITED_QUESTION_KO,
  /** R14-D3 — 「어떤 조건으로」, not 「얼마까지」: a limit exists only against a holding. */
  excess_subscription: "초과청약은 어떤 조건으로 할 수 있나요?",
  /** R14-D4 — how the price is *calculated*; a 확정 전 금액 is never asked for. */
  issue_price_formula: "발행가액은 어떻게 산정되나요?",
  /** R14-D5 */
  refixing_terms: "리픽싱 조건은 어떻게 되나요?",
  /** R14-D6 — ui-traps §1: 스케줄, not 기간. */
  option_schedule: "콜옵션과 풋옵션 스케줄은 어떻게 되나요?",
  /** R14-D7 */
  lockup_release: "보호예수는 언제 해제되나요?",
  /** R14-D8 */
  dissent_notice_procedure: "반대의사는 어떻게 통지하나요?",
  /** R14-D9 — a served figure, and not a 확정 전 금액. */
  appraisal_price: "주식매수청구 가격은 얼마인가요?",
};

export function presetsFor(fields: Record<string, FieldPayload> | undefined): AskPreset[] {
  if (!fields) return [];
  return Object.values(fields)
    .filter((field) => field.field_key !== STORY_FIELD)
    .sort((a, b) => fieldRank(a.field_key) - fieldRank(b.field_key))
    .flatMap((field) => {
      const question = PRESET_QUESTIONS[field.field_key];
      // Both halves or no chip: an unsigned key would otherwise fall back to
      // sending its label, and a field with no `korean_name` has nothing to read.
      return question && field.korean_name
        ? [{ key: field.field_key, label: field.korean_name, question }]
        : [];
    });
}
