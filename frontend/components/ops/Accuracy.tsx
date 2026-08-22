import type { OpsAccuracy, OpsBucket } from "@/lib/types";
import { count, percent } from "@/lib/format";
import {
  BASIS_LABEL_KO,
  BY_FIELD_KO,
  CORPUS_BLOCK_KO,
  CORRECTION_RECALL_KO,
  DART_SPEND_KO,
  HARD_CASES_KO,
  IMPORTED_AT_KO,
  JUDGED_BY_KO,
  JUDGE_KO,
  LLM_SPEND_KO,
  OVER_BLOCK_KO,
  QUOTA_KO,
  QUOTA_PER_DAY_KO,
  REPORT_OUTPUT_KO,
  SAMPLE_KO,
  SHOWN_PRECISION_KO,
} from "./copy";
import { Absent, Code, Panel, Rcept, Stamp } from "./atoms";
import styles from "./Ops.module.css";

/**
 * 정확도·비용.
 *
 * Two hard rules shape this tab and both are about **what may not be quoted
 * alone**:
 *
 * - **판정 출처(judged_by) 블록을 숫자 위에** — 98.6%를 judged_by 없이 렌더 —
 *   금지. The block is read off the artifact itself, so a re-judging updates it
 *   with no code change; if it is missing, the headline is not rendered at all.
 * - **분해 없이 단독 인용되는 레이아웃 금지 (분해가 같은 패널 안).** Every rate
 *   here carries its n, its interval and its corpus denominator inside the same
 *   panel: strict beside `correct/judged` and `partial`, 과차단 beside `19/19`,
 *   a field's block rate beside `corpus_blocked/corpus_total` and its reasons.
 *
 * The report is a **frozen artifact** — two JSON files, no database — so its
 * sentences describe the reading they were made on and are rendered as served,
 * including `mijual.evalset report`'s own markdown at the foot of the tab. The
 * spend half is live: `extraction_call` aggregates (labelled **cumulative**) and
 * the run log's own per-day OpenDART requests (labelled **daily**), because R7
 * forbids showing one as the other. ▷ stays ▷ (경계 = 출처).
 */

/** `"0.9861"` → `98.6% (213/216)`, with its interval — never the rate alone. */
function Rate({ bucket, label }: { bucket: OpsBucket; label: string }) {
  if (bucket.strict === undefined) return null;
  return (
    <div>
      <div className={styles.tileLabel}>{label}</div>
      <div className={styles.tileValue}>{percent(bucket.strict)}</div>
      <div className={styles.tileLines}>
        <div>
          {bucket.correct}/{bucket.judged}
          {bucket.interval
            ? ` · CI [${percent(bucket.interval[0], 0)}–${percent(bucket.interval[1], 0)}]`
            : ""}
        </div>
        <div>
          partial {bucket.partial} · wrong {bucket.wrong}
          {bucket.lenient ? ` · lenient ${percent(bucket.lenient)}` : ""}
        </div>
      </div>
    </div>
  );
}

export function Accuracy({ data }: { data: OpsAccuracy }) {
  const { evalset, spend } = data;
  const today = spend.dart.days[0];
  const usedShare = today
    ? Math.min(100, (today.requests / spend.dart.quota.requests_per_day) * 100)
    : 0;

  return (
    <>
      {evalset.available ? (
        <>
          {/* 판정 출처 — above the numbers, always. */}
          {evalset.judged_by ? (
            <Panel title={JUDGED_BY_KO}>
              <table className={styles.table}>
                <tbody>
                  <tr>
                    <td className={styles.ko}>{JUDGE_KO}</td>
                    <td className={styles.ko}>{evalset.judged_by.judge}</td>
                  </tr>
                  <tr>
                    <td className={styles.ko}>{BASIS_LABEL_KO}</td>
                    <td className={styles.ko}>{evalset.judged_by.basis}</td>
                  </tr>
                  <tr>
                    <td className={styles.ko}>{IMPORTED_AT_KO}</td>
                    <td>
                      <Stamp instant={evalset.judged_by.imported_at} seconds />
                    </td>
                  </tr>
                  <tr>
                    <td className={styles.ko}>{SAMPLE_KO}</td>
                    <td className={styles.codeWrap}>
                      {evalset.sample.units} units · {evalset.sample.rows} rows · labelled{" "}
                      {evalset.sample.labelled} · seed {evalset.sample.seed} ·{" "}
                      {Object.entries(evalset.sample.coverage)
                        .map(([key, value]) => `${key} ${value}`)
                        .join(" · ")}
                    </td>
                  </tr>
                </tbody>
              </table>
            </Panel>
          ) : null}

          {/* The rates, each with its decomposition in the same panel. The
              headline renders only when the artifact is stamped. */}
          {evalset.judged_by ? (
            <Panel>
              <div className={styles.tiles}>
                <Rate bucket={evalset.shown} label={SHOWN_PRECISION_KO} />
                <div>
                  <div className={styles.tileLabel}>{OVER_BLOCK_KO}</div>
                  <div className={styles.tileValue}>
                    {evalset.blocked.over_block_rate ? (
                      percent(evalset.blocked.over_block_rate)
                    ) : (
                      <Absent />
                    )}
                  </div>
                  <div className={styles.tileLines}>
                    <div>
                      {evalset.blocked.correct}/{evalset.blocked.judged}
                      {evalset.blocked.interval
                        ? ` · CI [${percent(evalset.blocked.interval[0], 0)}–${percent(
                            evalset.blocked.interval[1],
                            0,
                          )}]`
                        : ""}
                    </div>
                    {evalset.blocked.over_blocked_estimate ? (
                      <div>▷ {evalset.blocked.over_blocked_estimate}</div>
                    ) : null}
                  </div>
                </div>
                <div>
                  <div className={styles.tileLabel}>{CORRECTION_RECALL_KO}</div>
                  <div className={styles.tileValue}>
                    {percent(String(evalset.correction_recall.recall ?? 0))}
                  </div>
                  <div className={styles.tileLines}>
                    {Object.entries(evalset.correction_recall).map(([key, value]) => (
                      <div key={key}>
                        {key} {value}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Panel>
          ) : null}

          <Panel title={BY_FIELD_KO}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>field</th>
                  <th className={styles.num}>노출 n</th>
                  <th className={styles.num}>strict</th>
                  <th className={styles.num}>CI</th>
                  <th className={styles.num}>차단 n</th>
                  <th className={styles.num}>{OVER_BLOCK_KO}</th>
                  <th className={styles.num}>{CORPUS_BLOCK_KO}</th>
                  <th>reason</th>
                </tr>
              </thead>
              <tbody>
                {evalset.fields.map((field) => (
                  <tr key={field.field_key}>
                    <td>
                      <Code>{field.field_key}</Code>
                      <div className={styles.ko}>{field.korean_name}</div>
                    </td>
                    <td className={styles.num}>{field.shown.judged}</td>
                    <td className={styles.num}>
                      {field.shown.strict ? percent(field.shown.strict) : ""}
                      <div className={styles.faint}>
                        {field.shown.correct}/{field.shown.judged}
                      </div>
                    </td>
                    <td className={styles.num}>
                      {field.shown.interval
                        ? `[${percent(field.shown.interval[0], 0)}–${percent(
                            field.shown.interval[1],
                            0,
                          )}]`
                        : ""}
                    </td>
                    <td className={styles.num}>{field.blocked.judged}</td>
                    <td className={styles.num}>
                      {field.blocked.over_block_rate ? percent(field.blocked.over_block_rate) : ""}
                      {field.blocked.over_blocked_estimate ? (
                        <div className={styles.faint}>▷ {field.blocked.over_blocked_estimate}</div>
                      ) : null}
                    </td>
                    <td className={styles.num}>
                      {field.block_rate ? percent(field.block_rate) : ""}
                      <div className={styles.faint}>
                        {field.corpus_blocked}/{field.corpus_total}
                      </div>
                    </td>
                    <td className={styles.codeWrap}>
                      {field.corpus_reasons
                        .map((reason) => `${reason.code} × ${reason.count}`)
                        .join("\n")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>

          <Panel title={HARD_CASES_KO} note={`${evalset.hard_cases.length}`}>
            <table className={styles.table}>
              <tbody>
                {evalset.hard_cases.map((row) => (
                  <tr key={`${row.hard_case}-${row.rcept_no}-${row.field_ko}`}>
                    <td>
                      <Code>{row.hard_case}</Code>
                    </td>
                    <td className={styles.ko}>{row.corp_name}</td>
                    <td className={styles.ko}>{row.field_ko}</td>
                    <td>
                      <Code>{row.label}</Code>
                    </td>
                    <td>
                      <Rcept rceptNo={row.rcept_no} url={row.dart_url} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>

          {/* The command's own output, so the tab and the CLI cannot disagree. */}
          <Panel title={REPORT_OUTPUT_KO} note="mijual.evalset report">
            <pre className={styles.detail}>{evalset.markdown}</pre>
          </Panel>
        </>
      ) : (
        <Panel title={REPORT_OUTPUT_KO} note={evalset.reason}>
          <Absent />
        </Panel>
      )}

      <div className={styles.columns}>
        <Panel title={LLM_SPEND_KO} note={spend.llm.window}>
          <table className={styles.table}>
            <tbody>
              <tr>
                <td className={styles.ko}>calls</td>
                <td className={styles.num}>{spend.llm.calls}</td>
              </tr>
              <tr>
                <td className={styles.ko}>tokens</td>
                <td className={styles.num}>{count(spend.llm.tokens)}</td>
              </tr>
              <tr>
                <td className={styles.ko}>cost</td>
                <td className={styles.num}>
                  {/* ▷ verbatim — the pipeline's own mark on its own figure. */}
                  <Code>{spend.llm.cost_line}</Code>
                </td>
              </tr>
              <tr>
                <td className={styles.ko}>failures</td>
                <td className={styles.num}>{spend.llm.failures}</td>
              </tr>
              <tr>
                <td className={styles.ko}>window</td>
                <td>
                  <Code>{spend.llm.window}</Code>{" "}
                  {spend.llm.since ? (
                    <>
                      <Stamp instant={spend.llm.since} suffix={false} /> –{" "}
                      <Stamp instant={spend.llm.until} />
                    </>
                  ) : null}
                </td>
              </tr>
              {spend.llm.by_model.map((model) => (
                <tr key={model.model}>
                  <td>
                    <Code>{model.model}</Code>
                  </td>
                  <td className={styles.num}>
                    {model.calls} calls · {count(model.tokens)} tokens
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>

        <Panel title={`${QUOTA_KO} · ${DART_SPEND_KO}`} note={spend.dart.window}>
          {/* The bar is a **daily** measure against a **daily** quota, and both
              say so: R7 forbids a cumulative figure drawn as if it were a day's.
              The denominator is an operator statement, served with that
              provenance because this service cannot measure it. */}
          <div className={styles.tileLabel}>
            {QUOTA_PER_DAY_KO} · <Code>{spend.dart.quota.source}</Code>
          </div>
          <div className={styles.bar2}>
            <div className={styles.bar2Fill} style={{ width: `${usedShare}%` }} />
          </div>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>date</th>
                <th className={styles.num}>requests</th>
                <th className={styles.num}>calls</th>
                <th className={styles.num}>runs</th>
              </tr>
            </thead>
            <tbody>
              {spend.dart.days.map((day) => (
                <tr key={day.date}>
                  <td>
                    <Code>{day.date}</Code>
                  </td>
                  <td className={styles.num}>{day.requests}</td>
                  <td className={styles.num}>{day.calls}</td>
                  <td className={styles.num}>{day.runs}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={styles.panelNote}>measured_from {spend.dart.measured_from}</div>
        </Panel>
      </div>
    </>
  );
}
