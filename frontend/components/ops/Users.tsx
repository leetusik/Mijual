import Link from "next/link";
import type { OpsUsers } from "@/lib/types";
import { conversationsForSession } from "./routes";
import {
  ANONYMOUS_PROMISE_KO,
  ANON_SESSIONS_KO,
  COUNT_UNIT_KO,
  DEFAULT_KO,
  EMAIL_KO,
  HOLDINGS_COUNT_KO,
  JOINED_KO,
  MINIMAL_READ_KO,
  NOTIFICATIONS_KO,
  NO_SIGNUPS_KO,
  READER_ACCOUNTS_KO,
  REFUSAL_SIGNAL_KO,
  SAMPLE_LOADED_KO,
  STORED_KO,
  TO_LOG_KO,
} from "./copy";
import { SESSION_COLUMNS, cellText, extraKeys } from "./log";
import { Code, Panel, Stamp } from "./atoms";
import styles from "./Ops.module.css";

/**
 * 사용자 — two tables, and the space between them is the point.
 *
 * > 계정↔대화 연결 컴럼·조인·추정 매칭 금지 — **스키마 수준 부재가 약속의 구현**.
 *
 * `/ops/users` is two independent reads in one response and there is no key in
 * either block that could be matched against the other; P5 stores no
 * conversation at all, so the promise is trivially structural here. Nothing on
 * this screen offers to relate a row on the left to a row on the right, and the
 * 「대화 로그 →」 link goes from a *session* to that session's own log — never
 * from an account to anything.
 *
 * **최소 열람** is what the payload allows and no more: an email, a join date, a
 * portfolio **count** (never its contents) and the 알림 설정. The password is not
 * mentioned, not even as "a hash exists".
 *
 * ## 샘플 로드 여부
 *
 * R7's fifth 독자 계정 column has **no backing fact in this build**: R5's sample
 * is anonymous end to end, `P5.S8` built no anonymous write endpoint, and a
 * 샘플→계정 이전 arrives as ordinary authenticated holdings — so nothing
 * server-side ever learns the sample was loaded, and `P5.S9` serves **no
 * `sample_loaded` key** rather than an invented `false`.
 *
 * The column is therefore **data-driven rather than dropped**: it renders as soon
 * as a served row carries the fact, and until then the table renders around the
 * hole the way `states-and-trust.md` §4 requires (absent, never a dash, never a
 * placeholder standing where a value would be). Recorded as an open question for
 * the review — building the backing means a holding-provenance column and a new
 * behavioural fact about a reader, which is an operator decision, not this
 * slice's.
 */
export function Users({ data }: { data: OpsUsers }) {
  const { accounts, sessions } = data;
  const showsSample = accounts.rows.some((row) => row.sample_loaded !== undefined);
  const extra = extraKeys(sessions.rows, SESSION_COLUMNS);

  return (
    <>
      <Panel note={ANONYMOUS_PROMISE_KO}>
        <div className={styles.panelNote}>{REFUSAL_SIGNAL_KO}</div>
      </Panel>

      <Panel title={READER_ACCOUNTS_KO} note={`${accounts.count}${COUNT_UNIT_KO} · ${MINIMAL_READ_KO}`}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{EMAIL_KO}</th>
              <th>{JOINED_KO}</th>
              <th className={styles.num}>{HOLDINGS_COUNT_KO}</th>
              <th>{NOTIFICATIONS_KO}</th>
              {showsSample ? <th>{SAMPLE_LOADED_KO}</th> : null}
            </tr>
          </thead>
          <tbody>
            {accounts.rows.map((row) => (
              <tr key={row.id}>
                <td>
                  <Code>{row.email}</Code>
                </td>
                <td>
                  <Stamp instant={row.created_at} />
                </td>
                {/* A count only — the portfolio's contents are never opened. */}
                <td className={styles.num}>{row.holdings}</td>
                <td>
                  <Code>{row.notifications.lead_days.join(" · ")}</Code>{" "}
                  {/* An absent preference row means the 7일+1일 default, not
                      "off" — the payload says which of the two it is. */}
                  <span className={styles.faint}>
                    {row.notifications.stored ? STORED_KO : DEFAULT_KO}
                  </span>
                </td>
                {showsSample ? (
                  <td>
                    <Code>{String(row.sample_loaded)}</Code>
                  </td>
                ) : null}
              </tr>
            ))}
          </tbody>
        </table>

        {/* R7's own line for this table's empty state, and it is true: nothing
            is deployed, so 0 is a measurement rather than a placeholder. */}
        {accounts.count === 0 ? <p className={styles.panelNote}>{NO_SIGNUPS_KO}</p> : null}
      </Panel>

      <Panel title={ANON_SESSIONS_KO} note={`${sessions.count}${COUNT_UNIT_KO}`}>
        <table className={styles.table}>
          <thead>
            <tr>
              {SESSION_COLUMNS.map((column) => (
                <th key={column.key}>{column.label}</th>
              ))}
              {extra.map((key) => (
                <th key={key}>{key}</th>
              ))}
              <th />
            </tr>
          </thead>
          <tbody>
            {sessions.rows.map((row, index) => {
              const hash = cellText(row.session_hash);
              return (
                <tr key={hash + index}>
                  {SESSION_COLUMNS.map((column) => (
                    <td key={column.key} className={styles.codeWrap}>
                      {cellText(row[column.key])}
                    </td>
                  ))}
                  {extra.map((key) => (
                    <td key={key} className={styles.codeWrap}>
                      {cellText(row[key])}
                    </td>
                  ))}
                  <td>
                    {/* The signed cross-link: it filters the log to this session
                        — the other half of the two-way wiring the log's own
                        session hash provides. */}
                    <Link className={styles.link} href={conversationsForSession(hash)}>
                      {TO_LOG_KO}
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {sessions.rows.length === 0 ? (
          <p className={styles.panelNote}>
            {sessions.count}
            {COUNT_UNIT_KO}
          </p>
        ) : null}
      </Panel>
    </>
  );
}
