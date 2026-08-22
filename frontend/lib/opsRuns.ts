import type { OpsBeat, OpsBeatEntry, OpsRun } from "./types";

/**
 * The 개요 tab's one derivation: which scheduled beats have no run.
 *
 * > **스케줄된 beat가 안 돌았으면 「실행 기록 없음」 행을 alert 잉크로 렌더** —
 * > 예정 시각으로부터 파생, 침묵 금지. (R7 §개요)
 *
 * `P5.S9` serves both halves and fabricates neither: `beat.entries[].due` is
 * every instant an entry was due inside the served window, and `runs.rows` is
 * what actually ran. A gap is the join of two truthful lists — never a row the
 * backend minted — so the join lives here, in the browser's own arithmetic, and
 * it is the **only** number this panel computes.
 *
 * ## What counts as "it ran"
 *
 * A due instant is covered when a run **triggered by the beat** and carrying that
 * entry's own label started at or after it and before the entry's *next* due
 * instant. The bound comes from the schedule itself, so no tolerance constant is
 * invented: a 07:30 entry is covered by anything that started between 07:30 and
 * tomorrow's 07:30, and the newest due instant is bounded by the schedule's own
 * `as_of` instead. A **manual** run never covers a scheduled beat — it is a
 * different fact, and treating it as cover would hide exactly the failure this
 * row exists to show.
 *
 * Instants are compared as strings, which is exact here and nowhere near a
 * `Date`: every one of them is an absolute second-precision `+09:00` stamp from
 * the same server, so lexicographic order *is* chronological order and no
 * timezone is ever applied.
 */
export type OpsTimelineRow =
  | { kind: "run"; at: string; run: OpsRun }
  | { kind: "missing"; at: string; entry: OpsBeatEntry };

/** The beat entry's own label, which is what the run log records. */
function labelOf(entry: OpsBeatEntry): string {
  return typeof entry.kwargs.label === "string" ? entry.kwargs.label : entry.name;
}

export function timeline(beat: OpsBeat, runs: OpsRun[]): OpsTimelineRow[] {
  const rows: OpsTimelineRow[] = runs.map((run) => ({
    kind: "run",
    at: run.started_at,
    run,
  }));

  for (const entry of beat.entries) {
    const label = labelOf(entry);
    for (let index = 0; index < entry.due.length; index += 1) {
      const due = entry.due[index];
      const until = entry.due[index + 1] ?? beat.as_of;
      const ran = runs.some(
        (run) =>
          run.trigger === "beat" &&
          run.label === label &&
          run.started_at >= due &&
          run.started_at < until,
      );
      if (!ran) rows.push({ kind: "missing", at: due, entry });
    }
  }

  // Newest first — the order the run log itself is served in.
  return rows.sort((a, b) => (a.at < b.at ? 1 : a.at > b.at ? -1 : 0));
}
