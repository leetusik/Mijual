/**
 * The answer's layout arithmetic — three cases, no framework.
 *
 * Run by `npm run smoke` (`node --test "lib/*.test.ts"`), which is why a test for
 * `components/ask/render.ts` lives here: the glob is the qa contract, and that
 * module is pure functions over the store's block union with no React import, so
 * it loads unchanged (the same arrangement `lib/auth.test.ts` uses).
 *
 * What is worth pinning is what a browser pass cannot show cheaply: that R16
 * §2.8's child order is produced from **arrival** order rather than assumed, that
 * a 「미확인」 span cuts a sentence without ever eating it (§2.5 — the sentence goes
 * out either way), and that 소진 and 연결 끊김 are told apart by `reason` and not
 * by `status`, which is the one distinction §2.7 rests on. The drawing itself is
 * `next build` plus `P9.S11`'s browser sweep.
 */

import assert from "node:assert/strict";
import test from "node:test";
import type { AskBlock } from "./ask.ts";
import { answerParts, exhausted, foldable, proseSegments } from "../components/ask/render.ts";

const BLOCKS: AskBlock[] = [
  { kind: "status", phase: "read", text: "질문을 읽고 있습니다", block_id: "status", persistent: false },
  { kind: "tool", tool: "search_events", row: "이벤트 검색 「계양전기」 → 1건", ok: true },
  { kind: "data", rows: [{ label: "초과청약 비율", value: "배정 신주 1주당 0.2주", citation: 2 }] },
  { kind: "calc", mode: "verified", name: "초과청약 한도", inputs: [], state: "pending", block_id: "calc-1" },
  { kind: "tool", tool: "calculate", row: "계산 → 초과청약 한도 · 1,000주 × 0.2 = 200주", ok: true },
  { kind: "text", text: "1,000주 기준이면 200주까지입니다.", citations: [2] },
];

test("§2.8's regions come out of arrival order, each in the server's own order", () => {
  const parts = answerParts(BLOCKS);
  // 도구 흐름 is every row hoisted into one trace, still in the order it arrived.
  assert.deepEqual(
    parts.tools.map((block) => block.tool),
    ["search_events", "calculate"],
  );
  // 구조화 블록(서버 순서 그대로) — the calculation arrived after the data block
  // and stays after it, even though a tool row landed between them.
  assert.deepEqual(
    parts.blocks.map((block) => block.kind),
    ["data", "calc"],
  );
  assert.equal(parts.prose.length, 1);
  assert.equal(parts.status?.text, "질문을 읽고 있습니다");
  // 진행 표시 없는 턴 (a refusal-only turn, or one restored from storage).
  assert.equal(answerParts(BLOCKS.slice(1)).status, null);
});

test("「미확인」 cuts the sentence and never eats it", () => {
  const text = "1차 발행가액은 8,000원 수준으로 언급됩니다.";
  const start = text.indexOf("8,000원");
  assert.deepEqual(proseSegments(text, [[start, start + "8,000원".length]]), [
    { text: "1차 발행가액은 ", unverified: false },
    { text: "8,000원", unverified: true },
    { text: " 수준으로 언급됩니다.", unverified: false },
  ]);
  // No spans, and a span the server could not state honestly (inverted, out of
  // range, overlapping): the marker is dropped, the sentence goes out whole.
  for (const spans of [undefined, [], [[9, 4]], [[2, 900]], [[0, 5], [3, 8]]]) {
    assert.equal(
      proseSegments(text, spans)
        .map((segment) => segment.text)
        .join(""),
      text,
    );
  }
});

test("소진 vs 연결 끊김, and when a trace folds", () => {
  // Both are `aborted`; only `reason` says which (§2.7 draws them differently).
  assert.equal(exhausted("round_budget"), true);
  assert.equal(exhausted("tool_budget"), true);
  assert.equal(exhausted("call_budget"), true);
  assert.equal(exhausted(null), false); // 중지 / a cut stream → R14's inset stays
  assert.equal(exhausted("error"), false);
  // ≤3 flat · ≥4 flat while it is still arriving · ≥4 folded once it settles.
  assert.equal(foldable(3, false), false);
  assert.equal(foldable(4, true), false);
  assert.equal(foldable(4, false), true);
});
