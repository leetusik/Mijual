import Link from "next/link";
import type { OpsPage } from "@/lib/types";
import { OPS_ROUTES, conversationsForSession } from "./routes";
import {
  COUNT_UNIT_KO,
  FEEDBACK_EMPTY_KO,
  FEEDBACK_READ_ONLY_KO,
  FEEDBACK_SECTION_KO,
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
 * ## Where this queue lives, and why it moved
 *
 * R7 draws it on the **Conversations** card ("… save_feedback 대기열 — 대기 0건
 * (미배포 실제값) …"), not on the Feedback card, which is the vocky 관찰 뷰
 * (`Vocky.tsx` has the full mapping). `P5.S17` had it on the 피드백 tab because
 * the vocky view had no decided shape yet; `P5.S18` decided the shape and put
 * both where the record draws them. The round's reasoning is the same one: the
 * queue's privacy contract is the 익명 대화 로그's, so it belongs beside the log.
 *
 * The link to the vocky view is the 상호 링크 the no-merge line allows — nothing
 * on this tab reads a vocky row, and nothing there reads one of these.
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

      {/* 상호 링크만 — the other collection, never merged into this table. */}
      <p className={styles.panelNote}>
        <Link className={styles.link} href={OPS_ROUTES.feedback}>
          {FEEDBACK_SECTION_KO}
        </Link>
      </p>

      {page.next_cursor ? (
        <div className={styles.pager}>
          <Link
            className={styles.pageButton}
            /* Its own cursor name: the 대화 로그 on the same page owns `cursor`,
               and two tables paging one query parameter would move together. */
            href={`${OPS_ROUTES.conversations}?feedback_cursor=${encodeURIComponent(page.next_cursor)}`}
          >
            →
          </Link>
        </div>
      ) : null}
    </Panel>
  );
}
