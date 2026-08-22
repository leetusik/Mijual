import type { OpsGateQueue, OpsGateRows } from "@/lib/types";
import {
  BASIS_KO,
  BLOCKED_FIELDS_KO,
  BLOCKED_KO,
  BLOCKING_FLAGS_KO,
  EVENT_STATE_KO,
  OBSERVATION_ONLY_KO,
  REASON_COUNTS_KO,
  SUPPRESSION_KO,
  WITHDRAWN_KO,
  WITHDRAWN_UNRENDERED_KO,
} from "./copy";
import { RowInspect, type RowFilterValues } from "./RowInspect";
import { Absent, Code, Panel, Rcept } from "./atoms";
import styles from "./Ops.module.css";

/**
 * 게이트 대기열 — §6.5 순수 관찰.
 *
 * This is the one surface in the product where a gate-blocked field is visible
 * *with its reason*, and `states-and-trust.md` §4 says why it may be: the reason
 * a field failed is internal, actionable only by re-running the pipeline, and
 * showing it to a reader would teach distrust in exchange for nothing. So it is
 * here, and only here.
 *
 * Four prohibitions this tab keeps:
 *
 * - **No action of any kind.** 검토/해제/승인/재실행 버튼 금지 — the only way an
 *   exposure changes is a pipeline run, and there is no status bit to set.
 * - **Every rate carries its denominator.** Counts are over stored rows, rates
 *   over distinct `(rcept_no, field_key)`, and the served `basis` prints both
 *   with the number of duplicates between them.
 * - **Codes are raw English, unknown ones included** (§6.1). `reason_ko` is
 *   rendered when the *code* owns that Korean and simply absent otherwise —
 *   there is no fallback phrase and no rendering function.
 * - **A blocked row's missing evidence is 「없음」, a state — never a
 *   placeholder** where a value would be.
 */
export function GateQueue({
  queue,
  rows,
  filters,
}: {
  queue: OpsGateQueue;
  rows: OpsGateRows;
  filters: RowFilterValues;
}) {
  const { basis, events } = queue;
  const codes = [...new Set(queue.reasons.map((r) => r.code).filter(Boolean))];
  const statuses = [...new Set(queue.reasons.map((r) => r.gate_status ?? "").filter(Boolean))];

  return (
    <>
      <Panel note={OBSERVATION_ONLY_KO}>
        <table className={styles.table}>
          <tbody>
            <tr>
              <td className={styles.ko}>{BASIS_KO}</td>
              <td>
                <Code>
                  {basis.distinct_rows} distinct {basis.key} / {basis.stored_rows} stored ·{" "}
                  {basis.duplicates} duplicates
                </Code>
              </td>
            </tr>
          </tbody>
        </table>
      </Panel>

      <Panel title={REASON_COUNTS_KO} note={`rate = n / ${basis.distinct_rows}`}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>reason_code</th>
              <th>reason_ko</th>
              <th>gate_status</th>
              <th className={styles.num}>count</th>
              <th className={styles.num}>distinct</th>
              <th className={styles.num}>rate</th>
            </tr>
          </thead>
          <tbody>
            {queue.reasons.map((reason) => (
              <tr key={`${reason.gate_status}-${reason.code}`}>
                <td>{reason.code ? <Code>{reason.code}</Code> : <Absent />}</td>
                {/* Present only where the gate layer owns that Korean (§6.1). */}
                <td className={styles.ko}>{reason.reason_ko ?? ""}</td>
                <td>
                  <Code>{reason.gate_status}</Code>
                </td>
                <td className={styles.num}>{reason.count}</td>
                <td className={styles.num}>{reason.distinct_count}</td>
                <td className={styles.num}>{reason.rate ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>

      <RowInspect rows={rows} filters={filters} codes={codes} statuses={statuses} />

      <div className={styles.columns}>
        <Panel
          title={EVENT_STATE_KO}
          note={`${events.exposable} / ${events.considered} · suppressed ${events.suppressed}`}
        >
          <table className={styles.table}>
            <tbody>
              {Object.entries(events.by_state).map(([key, value]) => (
                <tr key={key}>
                  <td>
                    <Code>{key}</Code>
                  </td>
                  <td className={styles.num}>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className={styles.panelHead} style={{ marginTop: "16px" }}>
            <span className={styles.panelNote}>{BLOCKED_KO}</span>
          </div>
          <table className={styles.table}>
            <tbody>
              {events.blocked.map((reason) => (
                <tr key={reason.code}>
                  <td>
                    <Code>{reason.code}</Code>
                  </td>
                  <td className={styles.ko}>{reason.reason_ko ?? ""}</td>
                  <td className={styles.num}>{reason.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>

        <div>
          {/* The four blocking flags with the Korean the **code** carries. */}
          <Panel title={BLOCKING_FLAGS_KO} note={`${events.blocking_flags.length}`}>
            <table className={styles.table}>
              <tbody>
                {events.blocking_flags.map((flag) => (
                  <tr key={flag.code}>
                    <td>
                      <Code>{flag.code}</Code>
                    </td>
                    <td className={styles.ko}>{flag.reason_ko}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>

          {/* Raw English, unknown codes included — no Korean, no fallback. */}
          <Panel title={SUPPRESSION_KO} note={`${events.suppressed}`}>
            <table className={styles.table}>
              <tbody>
                {events.suppressed_reasons.map((reason) => (
                  <tr key={reason.code}>
                    <td>
                      <Code>{reason.code}</Code>
                    </td>
                    <td className={styles.num}>{reason.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        </div>
      </div>

      {/* 철회 검사: notice + note verbatim, the gate-passing count that will never
          render, and the blocked field list. */}
      <Panel title={WITHDRAWN_KO} note={`${queue.withdrawn.count}`}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>rcept_no</th>
              <th>corp</th>
              <th>rights</th>
              <th>notice_ko · note</th>
              <th className={styles.num}>{WITHDRAWN_UNRENDERED_KO}</th>
              <th>{BLOCKED_FIELDS_KO}</th>
            </tr>
          </thead>
          <tbody>
            {queue.withdrawn.rows.map((row) => (
              <tr key={row.event_id}>
                <td>
                  <Rcept rceptNo={row.rcept_no} url={row.dart_url} />
                </td>
                <td className={styles.ko}>
                  {row.corp_name ?? <Code>{row.corp_code}</Code>}
                </td>
                <td>
                  <Code>{row.rights_type}</Code>
                </td>
                <td>
                  <div className={styles.ko}>{row.notice_ko ?? ""}</div>
                  {row.note ? <div className={styles.codeWrap}>{row.note}</div> : null}
                </td>
                <td className={styles.num}>{row.gate_passed_unrendered}</td>
                <td className={styles.codeWrap}>
                  {row.blocked.length
                    ? row.blocked
                        .map((field) => `${field.field_key} ${field.reason_code ?? field.gate_status}`)
                        .join("\n")
                    : ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </>
  );
}
