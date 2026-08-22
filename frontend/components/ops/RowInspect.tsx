import Link from "next/link";
import type { OpsGateRows } from "@/lib/types";
import { OPS_ROUTES } from "./routes";
import { NONE_KO, ROW_INSPECT_KO } from "./copy";
import { Absent, Code, Panel, Rcept } from "./atoms";
import styles from "./Ops.module.css";

/** The four filters R7 names, plus the page window. Every one of them is a
 * column the table renders — there is no query surface beyond what is shown. */
export type RowFilterValues = {
  field_key?: string;
  reason_code?: string;
  gate_status?: string;
  rcept_no?: string;
  limit: number;
  offset: number;
};

function href(values: RowFilterValues, offset: number): string {
  const search = new URLSearchParams();
  for (const key of ["field_key", "reason_code", "gate_status", "rcept_no"] as const) {
    if (values[key]) search.set(key, values[key] as string);
  }
  if (offset) search.set("offset", String(offset));
  const text = search.toString();
  return text ? `${OPS_ROUTES.gates}?${text}` : OPS_ROUTES.gates;
}

/**
 * 행 검사 — one page of stored gate verdicts, with their evidence or its absence.
 *
 * > 행 검사 (row inspect): field_key/한국어 이름 · gate_status · reason_code ·
 * > reason_ko · quote/span (차단 행은 대개 없음 — 「없음」을 상태로 렌더,
 * > 자리표시자 금지) · rcept_no verbatim + DART 링크.
 *
 * The filters are a **plain GET form** and the pager is two links, so the whole
 * panel is server-rendered and works with no JavaScript at all — the same choice
 * the landing's own search form makes. The filter labels are the API's own
 * parameter names in mono: §6.1/§6.2 sign raw English for identifiers, and a
 * Korean label for `reason_code` would be a string this build invented.
 */
export function RowInspect({
  rows,
  filters,
  codes,
  statuses,
}: {
  rows: OpsGateRows;
  filters: RowFilterValues;
  /** Filter options, taken from the served reason table — never a list of codes
   * this file knows. */
  codes: string[];
  statuses: string[];
}) {
  const from = rows.count === 0 ? 0 : rows.offset + 1;
  const to = Math.min(rows.offset + rows.limit, rows.count);

  return (
    <Panel title={ROW_INSPECT_KO} note={`${from}–${to} / ${rows.count}`}>
      <form className={styles.filters} method="get" action={OPS_ROUTES.gates}>
        <label className={styles.field}>
          <span className={styles.fieldLabel}>field_key</span>
          <input
            className={styles.input}
            name="field_key"
            defaultValue={filters.field_key ?? ""}
            autoComplete="off"
          />
        </label>
        <label className={styles.field}>
          <span className={styles.fieldLabel}>reason_code</span>
          <select className={styles.select} name="reason_code" defaultValue={filters.reason_code ?? ""}>
            <option value="" />
            {codes.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
        </label>
        <label className={styles.field}>
          <span className={styles.fieldLabel}>gate_status</span>
          <select className={styles.select} name="gate_status" defaultValue={filters.gate_status ?? ""}>
            <option value="" />
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
        <label className={styles.field}>
          <span className={styles.fieldLabel}>rcept_no</span>
          <input
            className={styles.input}
            name="rcept_no"
            defaultValue={filters.rcept_no ?? ""}
            autoComplete="off"
          />
        </label>
        {/* The arrow is the round's own mark (「대화 로그 →」); a Korean verb here
            would be a word nobody signed. */}
        <button type="submit" className={styles.pageButton}>
          →
        </button>
      </form>

      <table className={styles.table}>
        <thead>
          <tr>
            <th>field_key</th>
            <th>gate_status</th>
            <th>reason_code</th>
            <th>reason_ko</th>
            <th>quote / span</th>
            <th>rcept_no</th>
          </tr>
        </thead>
        <tbody>
          {rows.rows.map((row) => (
            <tr key={row.id}>
              <td>
                <Code>{row.field_key}</Code>
                {row.korean_name ? <div className={styles.ko}>{row.korean_name}</div> : null}
                <div className={styles.faint}>
                  {row.corp_name ?? row.corp_code} · {row.rights_type ?? ""}
                </div>
              </td>
              <td>
                <Code>{row.gate_status}</Code>
                {row.status ? <div className={styles.faint}>{row.status}</div> : null}
                {row.span_status ? <div className={styles.faint}>{row.span_status}</div> : null}
              </td>
              <td>
                {row.reason_code ? <Code>{row.reason_code}</Code> : <Absent />}
                {row.gate_note ? <div className={styles.codeWrap}>{row.gate_note}</div> : null}
              </td>
              {/* Absent unless the **code** owns that Korean (§6.1). */}
              <td className={styles.ko}>{row.reason_ko ?? ""}</td>
              <td>
                {row.quote ? (
                  <>
                    <div className={styles.quote}>{row.quote}</div>
                    {row.span ? (
                      <div className={styles.faint}>
                        span {row.span[0]}–{row.span[1]}
                      </div>
                    ) : null}
                  </>
                ) : (
                  /* 「없음」 as a state: a blocked row usually has no evidence, and
                     R7 forbids a placeholder standing where a value would be. */
                  <span className={styles.faint}>{NONE_KO}</span>
                )}
                {row.value_summary ? (
                  <div className={styles.codeWrap}>{row.value_summary}</div>
                ) : null}
              </td>
              <td>
                <Rcept rceptNo={row.rcept_no} url={row.dart_url} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className={styles.pager}>
        {rows.offset > 0 ? (
          <Link
            className={styles.pageButton}
            href={href(filters, Math.max(0, rows.offset - rows.limit))}
          >
            ←
          </Link>
        ) : (
          <button type="button" className={styles.pageButton} disabled>
            ←
          </button>
        )}
        <span>
          {from}–{to} / {rows.count}
        </span>
        {to < rows.count ? (
          <Link className={styles.pageButton} href={href(filters, rows.offset + rows.limit)}>
            →
          </Link>
        ) : (
          <button type="button" className={styles.pageButton} disabled>
            →
          </button>
        )}
      </div>
    </Panel>
  );
}
