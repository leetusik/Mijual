import assert from "node:assert/strict";
import test from "node:test";
import { timeline } from "./opsRuns.ts";
import type { OpsBeat, OpsRun } from "./types.ts";

/** The morning beat, due three mornings running, as `/ops/overview` serves it. */
const beat: OpsBeat = {
  timezone: "Asia/Seoul",
  as_of: "2026-08-22T15:00:00+09:00",
  due_since: "2026-08-19T15:00:00+09:00",
  entries: [
    {
      name: "daily-pipeline-morning",
      task: "mijual.daily_pipeline",
      spec: "07:30 daily",
      hour: 7,
      minute: 30,
      day_of_week: null,
      kwargs: { label: "daily-morning", trigger: "beat" },
      due: ["2026-08-20T07:30:00+09:00", "2026-08-21T07:30:00+09:00", "2026-08-22T07:30:00+09:00"],
    },
  ],
};

function run(partial: Partial<OpsRun>): OpsRun {
  return {
    id: 1,
    label: "daily-morning",
    trigger: "beat",
    started_at: "2026-08-22T07:30:12+09:00",
    window: [null, null],
    lock: "redis",
    requests: 0,
    calls: 0,
    stages: [],
    ...partial,
  };
}

test("a beat that ran covers its own due instant, and only that one", () => {
  const rows = timeline(beat, [run({})]);
  const missing = rows.filter((row) => row.kind === "missing").map((row) => row.at);
  // Today's 07:30 is covered by the run that started at 07:30:12; the two
  // earlier mornings are still unaccounted for and must be said out loud.
  assert.deepEqual(missing, ["2026-08-21T07:30:00+09:00", "2026-08-20T07:30:00+09:00"]);
  // Newest first, runs and gaps interleaved by time.
  assert.equal(rows[0].kind, "run");
});

test("a manual run is not cover for a scheduled beat — silence is what R7 forbids", () => {
  const rows = timeline(beat, [run({ trigger: "manual" })]);
  assert.equal(rows.filter((row) => row.kind === "missing").length, 3);
  // …and neither is a beat run of a *different* entry.
  const other = timeline(beat, [run({ label: "weekly-resync" })]);
  assert.equal(other.filter((row) => row.kind === "missing").length, 3);
});
