import Link from "next/link";
import type { OpsPage } from "@/lib/types";
import { OPS_ROUTES } from "./routes";
import {
  ANONYMOUS_PROMISE_KO,
  ANSWER_KO,
  COUNT_UNIT_KO,
  FILTER_KIND_KO,
  FILTER_REFUSAL_KO,
  KIND_VALUES,
  LOG_SESSION_KO,
  REFUSAL_KO,
  REFUSAL_CATEGORIES_KO,
} from "./copy";
import { LOG_COLUMNS, LOG_DETAIL_COLUMNS, cellText, extraKeys } from "./log";
import { Code, Panel } from "./atoms";
import styles from "./Ops.module.css";

export type LogFilters = {
  kind?: string;
  refusal_category?: string;
  session?: string;
  cursor?: string;
};

function href(filters: LogFilters, cursor?: string): string {
  const search = new URLSearchParams();
  if (filters.kind) search.set("kind", filters.kind);
  if (filters.refusal_category) search.set("refusal_category", filters.refusal_category);
  if (filters.session) search.set("session", filters.session);
  if (cursor) search.set("cursor", cursor);
  const text = search.toString();
  return text ? `${OPS_ROUTES.conversations}?${text}` : OPS_ROUTES.conversations;
}

/**
 * 대화 로그 — the internal face of 「대화는 익명으로 저장됩니다 (품질 점검용)」.
 *
 * The promise is kept **at the schema level, not by this screen**: there is no
 * account, email, IP or user-agent column anywhere in the port
 * (`mijual.web.conversations`), and P5 creates no conversation table at all — so
 * what this tab shows today is an honest `0건`. Not 「준비 중」 (a Korean string
 * nobody signed), not a 404 (the section is signed and complete), and not an
 * example row (a fabricated conversation on the screen that exists to prove
 * conversations are real would be the worst of both).
 *
 * Everything else is here and wired: the two signed filters (유형 답변/거절 and
 * the five R6-7 refusal families), 시간 역순 커서 페이지네이션, the session
 * cross-link the 사용자 tab links into, and the expanded row's replay anatomy —
 * a native `<details>`, so the disclosure needs no JavaScript and no state.
 *
 * **Read-only** — 삭제·편집·태깅 없음, and no processed-state bit (§6.5).
 */
export function Conversations({ page, filters }: { page: OpsPage; filters: LogFilters }) {
  const extra = extraKeys(page.rows, [...LOG_COLUMNS, ...LOG_DETAIL_COLUMNS]);

  return (
    <>
      <Panel note={ANONYMOUS_PROMISE_KO}>
        <form className={styles.filters} method="get" action={OPS_ROUTES.conversations}>
          <label className={styles.field}>
            <span className={styles.fieldLabel}>{FILTER_KIND_KO}</span>
            <select className={styles.select} name="kind" defaultValue={filters.kind ?? ""}>
              <option value="" />
              <option value={KIND_VALUES.answer}>{ANSWER_KO}</option>
              <option value={KIND_VALUES.refusal}>{REFUSAL_KO}</option>
            </select>
          </label>
          <label className={styles.field}>
            <span className={styles.fieldLabel}>{FILTER_REFUSAL_KO}</span>
            {/* The five families are R6's own names, and they travel as the
                filter's value too: inventing an English token for each would be
                pre-implementing a vocabulary P6 owns. */}
            <select
              className={styles.select}
              name="refusal_category"
              defaultValue={filters.refusal_category ?? ""}
            >
              <option value="" />
              {REFUSAL_CATEGORIES_KO.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </label>
          {filters.session ? (
            <label className={styles.field}>
              <span className={styles.fieldLabel}>{LOG_SESSION_KO}</span>
              <input
                className={styles.input}
                name="session"
                defaultValue={filters.session}
                readOnly
              />
            </label>
          ) : null}
          <button type="submit" className={styles.pageButton}>
            →
          </button>
        </form>
      </Panel>

      <Panel note={`${page.count}${COUNT_UNIT_KO}`}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th />
              {LOG_COLUMNS.map((column) => (
                <th key={column.key}>{column.label}</th>
              ))}
              {extra.map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {page.rows.map((row, index) => (
              <tr key={cellText(row.session_hash) + index}>
                <td>
                  {/* 펼친 행 = 대화 재생: 저장분 그대로. */}
                  <details>
                    <summary className={styles.expand}>+</summary>
                    <div className={styles.detail}>
                      {LOG_DETAIL_COLUMNS.map((column) => (
                        <div key={column.key}>
                          <span className={styles.faint}>{column.label}</span>{" "}
                          {cellText(row[column.key])}
                        </div>
                      ))}
                    </div>
                  </details>
                </td>
                {LOG_COLUMNS.map((column) => (
                  <td key={column.key} className={styles.codeWrap}>
                    {column.key === "session_hash" ? (
                      <Link className={styles.link} href={OPS_ROUTES.users}>
                        <Code>{cellText(row[column.key])}</Code>
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
            ))}
          </tbody>
        </table>

        {/* The empty state is the served count and its unit — no sentence was
            written for this table, so none is printed. */}
        {page.rows.length === 0 ? (
          <p className={styles.panelNote}>
            {page.count}
            {COUNT_UNIT_KO}
          </p>
        ) : null}

        {page.next_cursor ? (
          <div className={styles.pager}>
            <Link className={styles.pageButton} href={href(filters, page.next_cursor)}>
              →
            </Link>
          </div>
        ) : null}
      </Panel>
    </>
  );
}
