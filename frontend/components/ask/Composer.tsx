"use client";

import { useState, type RefObject } from "react";
import { ASK_LABEL_KO, PREPARING_KO, SEND_KO, STOP_KO } from "./copy";
import styles from "./Ask.module.css";

/** Which of R6's SSE states the composer is in. `idle` covers 완료 and 중단 —
 * both leave the reader able to ask the next question. */
export type ComposerState = "idle" | "pending" | "streaming";

/**
 * The question field and **one** button whose text is replaced.
 *
 * > idle → **답변 준비 중** (버튼 텍스트 교체 + disabled — 스피너·점 금지) →
 * > 스트리밍 (… 중지 버튼) (R6 §SSE)
 *
 * That is the whole state machine on this side: no spinner, no typing dots, no
 * disabled-looking third control. 중지 is the same button again, and it stops the
 * turn by aborting the fetch — there is no stop endpoint to call (`P6.S4`).
 *
 * **R14 Q-C named the idle text 「보내기」** (`SEND_KO`, operator-specified in that
 * round's session), so the three texts are 보내기 → 답변 준비 중… → 중지 and
 * R6-2's 「직접 질문 입력 →」 went back to the strip's free-input chip. The field's
 * accessible name is still the surface's own 「AI 질문」 — the one reuse this
 * surface still carries, and still flagged in `copy.ts`.
 *
 * **Disabled is the ghost tier, not a dimmed solid** (R14 f13): an empty field and
 * a 답변 준비 중… both render the button with no fill, a soft hairline and
 * `--ink-3` — a control that cannot be pressed no longer looks pressable. The
 * geometry (36px, ≤767 44px) is unchanged, and so is the fact that `disabled` is a
 * real attribute rather than a look.
 *
 * **`plain` is `/ask`'s composer** (R16 §2.7b, `.apage .acom`): 「감싸는
 * 테두리·그림자 없음(입력창 자신의 1px만 — 이중 프레임 금지), `/ask`에서는
 * `border-top` 구분선도 없음. 위젯 컴포저의 R14 기하는 그대로.」 So the flag drops
 * the widget's divider and its inline padding and touches nothing else — one
 * component, two placements, no second composer.
 */
export function Composer({
  state,
  inputRef,
  onAsk,
  onStop,
  plain = false,
}: {
  state: ComposerState;
  inputRef: RefObject<HTMLInputElement | null>;
  onAsk: (question: string) => void;
  onStop: () => void;
  plain?: boolean;
}) {
  const [text, setText] = useState("");
  const running = state !== "idle";

  return (
    // Extensions and mobile autofill stamp their own attributes onto form
    // controls before React hydrates; `SearchRow.tsx` carries the full note.
    <form
      suppressHydrationWarning
      className={plain ? `${styles.composer} ${styles.composerPlain}` : styles.composer}
      onSubmit={(event) => {
        event.preventDefault();
        if (running || text.trim() === "") return;
        onAsk(text);
        setText("");
      }}
    >
      <input
        suppressHydrationWarning
        ref={inputRef}
        className={styles.input}
        type="text"
        value={text}
        aria-label={ASK_LABEL_KO}
        onChange={(event) => setText(event.target.value)}
      />
      {state === "streaming" ? (
        <button type="button" className={styles.send} onClick={onStop}>
          {STOP_KO}
        </button>
      ) : (
        <button
          type="submit"
          className={styles.send}
          disabled={state === "pending" || text.trim() === ""}
        >
          {state === "pending" ? PREPARING_KO : SEND_KO}
        </button>
      )}
    </form>
  );
}
