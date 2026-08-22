import type { OpsOverview, OpsRun } from "@/lib/types";
import { timeline } from "@/lib/opsRuns";
import {
  BEAT_KO,
  LOCK_KO,
  LOCK_HELD_SINCE_KO,
  NO_RUN_RECORD_KO,
  PENDING_KO,
  RUNS_KO,
  TILE_EVENTS_KO,
  TILE_MEASURED_KO,
  TILE_RENDERABLE_KO,
  TILE_VERDICTS_KO,
} from "./copy";
import { Absent, Code, Num, Panel, Quoted, Stamp } from "./atoms";
import styles from "./Ops.module.css";

/**
 * 개요 — the pipeline and its beat.
 *
 * Everything on this tab is `gates summary`, the beat declaration, the run log
 * and the decisions document, re-read. The one thing the client *derives* is the
 * one R7 asks it to:
 *
 * > **스케줄된 beat가 안 돌았으면 「실행 기록 없음」 행을 alert 잉크로 렌더** —
 * > 예정 시각으로부터 파생, 침묵 금지.
 *
 * `P5.S9` serves both halves and mints no row for a gap (`beat.entries[].due` —
 * every instant an entry was due in the served window — and `runs.rows`), so the
 * join is here and is the only arithmetic on the page.
 *
 * And its converse, from the same paragraph: **예산 소진은 보고된 상태로 (실패
 * 스타일 금지 — alert는 미실행에만).** A run that hit a budget reports it in its
 * own stage lines and notes, in ordinary ink; the alert colour appears on this
 * surface only on a 실행 기록 없음 row.
 */

function StageLine({ run }: { run: OpsRun }) {
  if (!run.stages.length) return <Absent />;
  return (
    <span className={styles.codeWrap}>
      {run.stages
        .map((stage) => {
          const counts = `${stage.requests ?? 0}req ${stage.calls ?? 0}calls`;
          return `${stage.name} ${stage.status} · ${counts}${stage.summary ? ` · ${stage.summary}` : ""}`;
        })
        .join("\n")}
    </span>
  );
}

export function Overview({ data }: { data: OpsOverview }) {
  const { gates, beat, runs, lock, decisions } = data;
  const rows = timeline(beat, runs.rows);
  const byState = Object.entries(gates.events.by_state);
  const verdicts = Object.entries(gates.fields.verdicts);

  return (
    <>
      {/* 상태 타일 4 — `gates summary` 값 그대로. */}
      <div className={styles.tiles}>
        <section className={styles.panel}>
          <div className={styles.tileLabel}>{TILE_EVENTS_KO}</div>
          <div className={styles.tileValue}>
            {gates.events.exposable}
            <span className={styles.tileUnit}> / {gates.events.considered}</span>
          </div>
          <div className={styles.tileLines}>
            {byState
              .filter(([key]) => key.endsWith(":exposable"))
              .map(([key, count]) => (
                <div key={key}>
                  {key.split(":")[0]} {count}
                </div>
              ))}
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.tileLabel}>{TILE_VERDICTS_KO}</div>
          <div className={styles.tileValue}>{gates.fields.stored_rows}</div>
          <div className={styles.tileLines}>
            {verdicts.map(([key, count]) => (
              <div key={key}>
                {key} {count}
              </div>
            ))}
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.tileLabel}>{TILE_RENDERABLE_KO}</div>
          <div className={styles.tileValue}>{gates.fields.renderable.total}</div>
          <div className={styles.tileLines}>
            {gates.fields.renderable.by_field.map((field) => (
              <div key={field.field_key}>
                {field.field_key} {field.count}
                {field.tbd ? ` (tbd ${field.tbd})` : ""}
              </div>
            ))}
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.tileLabel}>{TILE_MEASURED_KO}</div>
          <div className={styles.tileValue}>
            <Stamp instant={gates.measured_at} />
          </div>
        </section>
      </div>

      {/* beat 스케줄 — 설정에서 렌더, 하드코딩 금지. */}
      <Panel
        title={BEAT_KO}
        note={`${beat.timezone} · due since ${beat.due_since.slice(0, 10)} ${beat.due_since.slice(11, 16)}`}
      >
        <table className={styles.table}>
          <thead>
            <tr>
              <th>name</th>
              <th>task</th>
              <th>spec</th>
              <th>kwargs</th>
              <th className={styles.num}>due</th>
            </tr>
          </thead>
          <tbody>
            {beat.entries.map((entry) => (
              <tr key={entry.name}>
                <td>
                  <Code>{entry.name}</Code>
                </td>
                <td>
                  <Code>{entry.task}</Code>
                </td>
                <td>
                  <Code>{entry.spec}</Code>
                </td>
                <td className={styles.codeWrap}>
                  {Object.entries(entry.kwargs)
                    .map(([key, value]) => `${key}=${String(value)}`)
                    .join(" · ")}
                </td>
                <td className={styles.num}>{entry.due.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>

      {/* 최근 실행 표 + the derived 실행 기록 없음 rows, interleaved by time. */}
      <Panel title={RUNS_KO} note={`${runs.rows.length} / ${runs.count} rows`}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>시각</th>
              <th>trigger</th>
              <th>label</th>
              <th>stages</th>
              <th className={styles.num}>req</th>
              <th className={styles.num}>calls</th>
              <th>spend</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) =>
              row.kind === "run" ? (
                <tr key={`run-${row.run.id}`}>
                  <td>
                    <Stamp instant={row.run.started_at} seconds suffix={false} />
                  </td>
                  <td>
                    <Code>{row.run.trigger}</Code>
                  </td>
                  <td>
                    <Code>{row.run.label}</Code>
                  </td>
                  <td>
                    <StageLine run={row.run} />
                    {row.run.notes?.length ? (
                      <div className={styles.codeWrap}>{row.run.notes.join("\n")}</div>
                    ) : null}
                    {row.run.config ? <div className={styles.codeWrap}>{row.run.config}</div> : null}
                  </td>
                  <td className={styles.num}>{row.run.requests}</td>
                  <td className={styles.num}>{row.run.calls}</td>
                  <td>
                    {/* ▷ verbatim: it is the pipeline's own sentence, and this is
                        the one surface where the estimate mark stays ▷ (경계 =
                        출처). A run still in flight has no line yet. */}
                    {row.run.spend_line ? (
                      <span className={styles.codeWrap}>{row.run.spend_line}</span>
                    ) : (
                      <Absent />
                    )}
                  </td>
                </tr>
              ) : (
                <tr key={`missing-${row.entry.name}-${row.at}`}>
                  <td>
                    <Stamp instant={row.at} seconds suffix={false} />
                  </td>
                  <td>
                    <Code>beat</Code>
                  </td>
                  <td>
                    <Code>{row.entry.name}</Code>
                  </td>
                  <td className={styles.alert} colSpan={4}>
                    {NO_RUN_RECORD_KO} <span className={styles.code}>{row.entry.spec}</span>
                  </td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      </Panel>

      <div className={styles.columns}>
        {/* lock 칩's detail — the bar carries the chip, this is what it holds. */}
        <Panel title={LOCK_KO} note={lock.key}>
          <table className={styles.table}>
            <tbody>
              <tr>
                <td className={styles.ko}>state</td>
                <td>
                  <Code>{lock.state}</Code>
                  {lock.reason ? <span className={styles.faint}> {lock.reason}</span> : null}
                </td>
              </tr>
              <tr>
                <td className={styles.ko}>source</td>
                <td>
                  <Code>{lock.source}</Code>
                </td>
              </tr>
              {lock.holder ? (
                <tr>
                  <td className={styles.ko}>holder</td>
                  <td>
                    <Code>{lock.holder}</Code>
                  </td>
                </tr>
              ) : null}
              {lock.ttl_seconds !== undefined ? (
                <tr>
                  <td className={styles.ko}>ttl</td>
                  <td>
                    <Num value={lock.ttl_seconds} />
                  </td>
                </tr>
              ) : null}
              {lock.since ? (
                <tr>
                  <td className={styles.ko}>{LOCK_HELD_SINCE_KO}</td>
                  <td>
                    <Stamp instant={lock.since} seconds />
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </Panel>

        {/* 가동 전 미결 — quoted from the decisions document, never written here. */}
        <Panel
          title={PENDING_KO}
          note={
            decisions.available
              ? `${decisions.path} ${decisions.version ?? ""}`.trim()
              : decisions.reason
          }
        >
          {decisions.available && decisions.items?.length ? (
            <table className={styles.table}>
              <tbody>
                {decisions.items.map((item) => (
                  <tr key={`${item.decision}-${item.text.slice(0, 24)}`}>
                    <td>
                      <Code>{item.decision}</Code>
                    </td>
                    <td className={styles.ko}>
                      <Quoted text={item.text} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <Absent />
          )}
        </Panel>
      </div>
    </>
  );
}
