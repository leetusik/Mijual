import Link from "next/link";
import type { OpsVocky } from "@/lib/types";
import { OPS_ROUTES } from "./routes";
import {
  API_SHAPE_PENDING_KO,
  COUNT_UNIT_KO,
  TO_LOG_KO,
  VOCKY_CONTRACT_KO,
  VOCKY_VIEW_KO,
} from "./copy";
import { cellText, extraKeys } from "./log";
import { Code, Panel, Stamp } from "./atoms";
import styles from "./Ops.module.css";

/**
 * vocky 관찰 뷰 — the 피드백 section (R7 §6.3).
 *
 * ## Why this section, and not a seventh tab
 *
 * R7's record maps its seven cards onto the six signed tabs in order, and the
 * mapping is explicit: "**Feedback** — vocky 관찰 뷰 프레임 (§6.3)", while the
 * `save_feedback` 대기열 is drawn on the **Conversations** card ("… save_feedback
 * 대기열 — 대기 0건 …"). The round's own handoff says the same
 * (`admin/Feedback.html` — "the vocky observation view"; `admin/Conversations.html`
 * — "the anonymous 해설 log viewer **+ agent feedback queue**"). So 피드백 *is*
 * this view, a seventh tab would break the signed 6-tab nav, and `P5.S18` moved
 * the queue to where the record draws it.
 *
 * It is also what the round's reasoning asks for: "vocky 뷰와 agent 대기열은
 * **분리** … 병합하면 '익명 대화 로그'와 '자발 이메일 동반 의견'의 서로 다른
 * 프라이버시 계약이 섞임." The queue's privacy contract is the conversation log's;
 * vocky's is a different collection path entirely. Two sections, 상호 링크만.
 *
 * ## The columns are vocky's own field names
 *
 * §6.3 forbade inventing them and delegated the real shape to this build; the
 * card's `?` headers were proposals. `P5.S18` read vocky's running product and
 * `mijual.web.vocky` now serves the decided set in `fields` — so the headers are
 * raw English identifiers, which is exactly what §6.1/§6.2 sign for this surface,
 * and this file names not one of them. A key a row carries beyond that set is
 * still rendered (`extraKeys`), the convention `log.ts` established.
 *
 * ## Three states, and none of them invents a row
 *
 * `unconfigured` is 연결 전 — the signed 「API shape 확정 대기」 line over the
 * skeleton, which now carries the **decided** column names instead of `?`.
 * `unreachable` prints the raw English reason (and the HTTP status when there was
 * one), the same way the lock chip reports a Redis that is down. Only `ok` has
 * rows, and they are vocky's, unaltered but for the KST timestamps.
 */
export function Vocky({ page }: { page: OpsVocky }) {
  const columns = page.fields.map((key) => ({ key, label: key }));
  const extra = extraKeys(page.rows, columns);
  const connected = page.state === "ok";

  return (
    <Panel title={VOCKY_VIEW_KO} note={VOCKY_CONTRACT_KO.join(" · ")}>
      <p className={styles.panelNote}>
        <Code>{page.state}</Code>{" "}
        {page.source.base ? <Code>{page.source.base}</Code> : null}
        <Code>{page.source.endpoint}</Code>
        {page.reason ? (
          <>
            {" "}
            <Code>{page.status ? `${page.reason} ${page.status}` : page.reason}</Code>
          </>
        ) : null}
      </p>

      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} className={styles.code}>
                {column.label}
              </th>
            ))}
            {extra.map((key) => (
              <th key={key} className={styles.code}>
                {key}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {connected
            ? page.rows.map((row, index) => (
                <tr key={cellText(row.id) + index}>
                  {columns.map((column) => (
                    <td key={column.key} className={styles.codeWrap}>
                      {column.key === "ingested_at" ? (
                        <Stamp instant={cellText(row[column.key]) || null} />
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
              ))
            : /* 스켈레톤 — the table's shape with no value in it. Not a
                 placeholder glyph: R7 forbids one where a value would be. */
              [0, 1, 2].map((row) => (
                <tr key={row}>
                  {columns.map((column) => (
                    <td key={column.key}>
                      <span className={styles.skeleton} />
                    </td>
                  ))}
                </tr>
              ))}
        </tbody>
      </table>

      <p className={styles.panelNote}>
        {connected ? (
          <>
            {page.count}
            {COUNT_UNIT_KO}
          </>
        ) : (
          API_SHAPE_PENDING_KO
        )}
      </p>

      {/* 상호 링크만 — the queue this view is never merged with lives beside the
          대화 로그 it belongs to, and 「대화 로그 →」 is the round's own link. */}
      <p className={styles.panelNote}>
        <Link className={styles.link} href={OPS_ROUTES.conversations}>
          {TO_LOG_KO}
        </Link>
      </p>

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
