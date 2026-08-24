"use client";

import { useState } from "react";
import { DETAIL, FOLD, trace } from "./copy";
import { foldable, type ToolBlock } from "./render";
import ask from "./Ask.module.css";
import styles from "./Blocks.module.css";

/**
 * 도구 흐름 — every 도구 행 of the turn, flat or folded (R16 §2.2).
 *
 * > 행은 `ToolRowEvent` verbatim, 오늘의 도구 행 스타일 그대로(한 줄 + 가로
 * > 스크롤, 접수번호 줄바꿈 금지). `rows.length <= 3` **또는** 스트리밍 중 → 전부
 * > 평평하게 펼침. `rows.length >= 4` **그리고** 턴 완료 → 한 줄 요약
 * > (`trace(tools, events)`) + `자세히`. 펼치면 각 행 앞에 mono 순서 번호(ink-3,
 * > `margin-right 8px`). 접힘/펼침은 표면 상태이며 저장되지 않는다. 저장은 언제나
 * > 전체 행. 요약 줄 왼쪽 테두리 2px solid(도구 행과 동일). `자세히/접기` 타깃
 * > 32/44px.
 *
 * The rows themselves are untouched R14 (`Ask.module.css`'s `.toolRow`): one
 * nowrap line that scrolls, so a 접수번호 never breaks mid-number. What is new is
 * that they are **one thing** — R6 drew a row wherever it arrived, and a trace
 * that can fold has to be a single element in the answer's child order (§2.8).
 *
 * ## The fold is a default, not a memory
 *
 * `chosen` holds only the **reader's** press. While the turn streams the trace is
 * not collapsible at all (the arriving rows *are* the progress), and the moment
 * it settles a ≥4-row trace presents itself folded — which is what §4 check 9
 * asks for and what a state initialised once at mount could not do. Nothing is
 * persisted: 「저장은 언제나 전체 행」, and the store keeps every row regardless.
 *
 * `events` in the summary is `AskTurn.filings` — the turn's **distinct 접수번호**
 * count, server-known and never parsed back out of these strings (R16 §1).
 */
export function ToolTrace({
  rows,
  filings,
  live,
}: {
  rows: readonly ToolBlock[];
  filings: number;
  /** The turn is still being painted (pending or streaming). */
  live: boolean;
}) {
  const [chosen, setChosen] = useState<boolean | null>(null);
  const collapsible = foldable(rows.length, live);
  const open = !collapsible || chosen === true;

  return (
    <div className={styles.trace}>
      {collapsible ? (
        <p className={styles.traceSummary}>
          <span>{trace(rows.length, filings)}</span>
          <button
            type="button"
            className={styles.traceToggle}
            aria-expanded={open}
            onClick={() => setChosen(!open)}
          >
            {open ? FOLD : DETAIL}
          </button>
        </p>
      ) : null}

      {open
        ? rows.map((block, index) => (
            // 도구 행 — printed **verbatim** from the tool's own signed string.
            // `ok` is carried and deliberately given no colour of its own (R6:
            // a failed 의견 저장's own row already says 재시도).
            <p key={index} className={ask.toolRow} data-ok={block.ok ? "true" : "false"}>
              {collapsible ? <span className={styles.traceNumber}>{index + 1}</span> : null}
              {block.row}
            </p>
          ))
        : null}
    </div>
  );
}
