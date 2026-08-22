import Link from "next/link";
import type { OpsPage } from "@/lib/types";
import { OPS_ROUTES, conversationsForSession } from "./routes";
import {
  COUNT_UNIT_KO,
  FEEDBACK_EMPTY_KO,
  FEEDBACK_READ_ONLY_KO,
  NO_VOCKY_MERGE_KO,
  TO_LOG_KO,
} from "./copy";
import { FEEDBACK_COLUMNS, cellText, extraKeys } from "./log";
import { Panel } from "./atoms";
import styles from "./Ops.module.css";

/**
 * 피드백 — the `save_feedback(text, email?)` queue.
 *
 * > 빈 상태: 「대기 0건 — save_feedback 호출이 아직 없습니다」.
 *
 * Which is what this build actually holds: `save_feedback` is the AI 질문
 * agent's tool and the agent is **P6**, so nothing has ever called it. The line
 * is R7's own, so it is rendered as signed rather than replaced by a sentence
 * about being unfinished.
 *
 * Three rules ride with it: **읽기 전용 — 처리 상태 비트 없음** (there is no
 * "handled" checkbox to add later without a new signed decision; 회신 happens in
 * a mail client, outside the panel), the 답장 이메일 column carries a value only
 * where the reader volunteered one, and **vocky 수집분과 병합 금지 — 상호 링크만**.
 *
 * The vocky observation view itself is **not on this tab yet**: §6.3 delegates
 * its return shape to the build against vocky's real API and `P5.S18` owns that
 * decision, so shipping a frame with invented column names is precisely what the
 * round forbids. It lands beside this queue, unmerged, when the shape is known.
 */
export function Feedback({ page }: { page: OpsPage }) {
  const extra = extraKeys(page.rows, FEEDBACK_COLUMNS);

  return (
    <Panel note={`${FEEDBACK_READ_ONLY_KO} · ${NO_VOCKY_MERGE_KO}`}>
      <table className={styles.table}>
        <thead>
          <tr>
            {FEEDBACK_COLUMNS.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
            {extra.map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {page.rows.map((row, index) => {
            const hash = cellText(row.session_hash);
            return (
              <tr key={hash + index}>
                {FEEDBACK_COLUMNS.map((column) => (
                  <td key={column.key} className={styles.codeWrap}>
                    {column.key === "session_hash" && hash ? (
                      <Link className={styles.link} href={conversationsForSession(hash)}>
                        {TO_LOG_KO}
                      </Link>
                    ) : (
                      cellText(row[column.key])
                    )}
                  </td>
                ))}
                {extra.map((key) => (
                  <td key={key} className={styles.codeWrap}>
                    {cellText(row[key])}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>

      {page.count === 0 ? (
        <p className={styles.panelNote}>{FEEDBACK_EMPTY_KO}</p>
      ) : (
        <p className={styles.panelNote}>
          {page.count}
          {COUNT_UNIT_KO}
        </p>
      )}

      {page.next_cursor ? (
        <div className={styles.pager}>
          <Link
            className={styles.pageButton}
            href={`${OPS_ROUTES.feedback}?cursor=${encodeURIComponent(page.next_cursor)}`}
          >
            →
          </Link>
        </div>
      ) : null}
    </Panel>
  );
}
