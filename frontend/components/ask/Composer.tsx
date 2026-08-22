"use client";

import { useState, type RefObject } from "react";
import { ASK_LABEL_KO, ASK_SUBMIT_KO, PREPARING_KO, STOP_KO } from "./copy";
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
 * The two strings R6 does not write are reused rather than invented and are
 * flagged in `phase.md`: the idle button takes R6-2's 「직접 질문 입력 →」 and the
 * field's accessible name is the surface's own 「AI 질문」.
 */
export function Composer({
  state,
  inputRef,
  onAsk,
  onStop,
}: {
  state: ComposerState;
  inputRef: RefObject<HTMLInputElement | null>;
  onAsk: (question: string) => void;
  onStop: () => void;
}) {
  const [text, setText] = useState("");
  const running = state !== "idle";

  return (
    <form
      className={styles.composer}
      onSubmit={(event) => {
        event.preventDefault();
        if (running || text.trim() === "") return;
        onAsk(text);
        setText("");
      }}
    >
      <input
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
          {state === "pending" ? PREPARING_KO : ASK_SUBMIT_KO}
        </button>
      )}
    </form>
  );
}
