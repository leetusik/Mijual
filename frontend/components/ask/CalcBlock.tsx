import type { AskCalcMode, AskCalcState, AskChip, AskDataRow } from "@/lib/ask";
import { CALC_EXPR, CALC_RESULT, CALC_RUNNING, CALC_VERIFIED, calcError } from "./copy";
import { DataRowLine } from "./DataBlock";
import { ValueMarker } from "./ValueMarker";
import styles from "./Blocks.module.css";

/**
 * 계산 블록 — 입력 · 식 · 결과, this round's headline element (R16 §2.4).
 *
 * > 블록: 1px **`--border-strong`** (데이터 행보다 한 단 무겁다). 머리말: mono 11px
 * > — `--live` 색 단어(`검증된 계산` | `식 계산`) + ink-3 이름. 입력 행: DataRow와
 * > **같은 행 스키마·같은 CSS**. 독자가 준 값 = 「입력」 마커(칩 없음), 공시에서 온
 * > 값 = 인용 칩. 식 줄: mono `--text-sm` ink-2, `nowrap` + 가로 스크롤.
 * > `state=error`면 그리지 않는다. 상태 (같은 `block_id`에서 제자리 교체, 블록이
 * > 뛰지 않게 결과 행과 진행 줄의 **자리는 하나**): `pending` → 「계산 중」 한 줄
 * > (mono 11px ink-3) · `done` → 결과 행: 배경 `--live-tint`, 왼쪽 「결과」(12px
 * > ink-2), 오른쪽 값 = **`--text-md` mono 600 `--live` + 「계산」 마커** · `error`
 * > → `calcError(why)` 문장 (sans `--text-sm` ink-2). **alert 색·아이콘 금지.**
 * > 블록은 도구 호출 시점에 **입력만이라도** 먼저 나타난다 (감사 가능성의 절반).
 * > 계산 결과는 **푸터의 「근거 N건」에 세지 않는다**.
 *
 * Three of those are settled before this file draws anything, and it must not
 * re-derive them:
 *
 * - **the two headings are never the same word.** `mode` decides it, and
 *   rendering 검증된 계산 and 식 계산 identically would launder arithmetic into
 *   the product's own verified money math (result.md §3-7). A verified
 *   calculation's `name` is the **server's** — the operation that actually ran
 *   (`P9.S5` note 5) — and only 식 계산 lets the model name it.
 * - **the slot is one.** `pending`, `done` and `error` are mutually exclusive
 *   renderings of the same last child, replaced in place on the same `block_id`
 *   (§4 check 5: 블록이 뛰지 않는다).
 * - **the result is not a 근거.** Nothing here touches the chip numbering; a
 *   calculation carries no citation of its own (`P9.S5` note 11), and only its
 *   *inputs* wear chips.
 *
 * The error line has **no alert colour and no icon**: a calculation that could
 * not run is guidance, not an alarm — the same rule R6 states for a refusal.
 * `why` is the server's data (the input that stopped it, in its own label and
 * display) and `calcError` is the signed sentence around it; neither is composed
 * here.
 */
export function CalcBlock({
  mode,
  name,
  inputs,
  state,
  expr,
  result,
  why,
  chips,
}: {
  mode: AskCalcMode;
  name: string;
  inputs: readonly AskDataRow[];
  state: AskCalcState;
  expr?: string;
  result?: string;
  why?: string;
  chips: Map<number, AskChip>;
}) {
  return (
    <div className={styles.calc}>
      <p className={styles.calcHeading}>
        <span className={styles.calcKind}>{mode === "expr" ? CALC_EXPR : CALC_VERIFIED}</span>
        {name ? <span>{name}</span> : null}
      </p>

      {inputs.map((row, index) => (
        <DataRowLine key={index} row={row} chips={chips} />
      ))}

      {expr !== undefined && state !== "error" ? (
        <p className={styles.calcExpr}>{expr}</p>
      ) : null}

      {/* 자리는 하나 — exactly one of the three, always last. */}
      {state === "pending" ? <p className={styles.calcPending}>{CALC_RUNNING}</p> : null}
      {state === "error" && why !== undefined ? (
        <p className={styles.calcError}>{calcError(why)}</p>
      ) : null}
      {state === "done" && result !== undefined ? (
        <p className={styles.calcResult}>
          <span className={styles.calcResultLabel}>{CALC_RESULT}</span>
          <span className={styles.calcResultValue}>
            <ValueMarker kind="calc">{result}</ValueMarker>
          </span>
        </p>
      ) : null}
    </div>
  );
}
