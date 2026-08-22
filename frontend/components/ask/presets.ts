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
 * 4. **A chip's text is its question, and both come off the wire**: the served
 *    `korean_name`, the same label the field row prints. The one exception is the
 *    question R6 itself wrote — 「실권주는 어떻게 처리되나요?」 for
 *    `forfeited_share_method` (result.md §Composition examples) — rendered
 *    verbatim in that field's place.
 *
 * **Why no sentence template.** Turning every label into 「{label}은 어떻게
 * 되나요?」 would be inventing Korean copy, which this phase treats as a design
 * change (note 17), and it would be *wrong* Korean for most of the labels
 * (신주인수권증서 상장·매매기간 is not something that 처리된다). A served field
 * name **is** a question in the 범위 the chip sets — the agent receives it with
 * `scope_rcept_no` — so the honest chip is the label itself. ⚠ **Flagged for
 * `P6.S7`/`P6.REVIEW`**: R6 draws preset chips and writes exactly one preset
 * sentence, so whether the other chips should read as sentences is a question for
 * the record's own reader, not for this module.
 *
 * A field with no `korean_name` yields **no chip** (the label is the server's and
 * this file keeps no field-name table — `components/event/copy.ts`'s rule).
 */

import { STORY_FIELD, fieldRank } from "@/components/event/fieldOrder";
import type { FieldPayload } from "@/lib/types";
import { FORFEITED_FIELD, FORFEITED_QUESTION_KO } from "./copy";

export type AskPreset = {
  /** The field key it was generated from — a React key, never rendered. */
  key: string;
  /** What the chip reads. */
  label: string;
  /** What is sent as the question. Identical to `label` by construction. */
  question: string;
};

export function presetsFor(fields: Record<string, FieldPayload> | undefined): AskPreset[] {
  if (!fields) return [];
  return Object.values(fields)
    .filter((field) => field.field_key !== STORY_FIELD)
    .sort((a, b) => fieldRank(a.field_key) - fieldRank(b.field_key))
    .flatMap((field) => {
      const text =
        field.field_key === FORFEITED_FIELD ? FORFEITED_QUESTION_KO : field.korean_name;
      return text ? [{ key: field.field_key, label: text, question: text }] : [];
    });
}
