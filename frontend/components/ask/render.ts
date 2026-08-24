/**
 * The answer's layout arithmetic — **no React, no CSS, no Korean**.
 *
 * `Answer.tsx` draws R16 §2.8's child order (도구 흐름 → 구조화 블록 → 프로즈 →
 * 링크 → 진행 표시/끝맺음 → 푸터) over a store that keeps blocks in **arrival**
 * order (`P9.S8`: 「the store keeps arrival order, the renderer decides
 * placement」). Sorting one into the other is a pure function of the block list,
 * and so is cutting a sentence around its 「미확인」 spans — so both live here,
 * where `node --test` can see them (`lib/askRender.test.ts`, the same arrangement
 * `lib/auth.test.ts` uses for `components/auth/copy.ts`).
 *
 * Nothing here decides anything visual: the record does that, `Answer.tsx` and
 * `Blocks.module.css` carry it out, and this file only says *what goes where*.
 */

import type { AskBlock } from "@/lib/ask";

export type ToolBlock = Extract<AskBlock, { kind: "tool" }>;
export type StructuredBlock = Extract<AskBlock, { kind: "data" } | { kind: "calc" }>;
export type ProseBlock = Extract<AskBlock, { kind: "text" } | { kind: "refusal" }>;
export type StatusBlock = Extract<AskBlock, { kind: "status" }>;

/**
 * One answer, split into §2.8's four regions.
 *
 * `tools` is every 도구 행 of the turn **hoisted into one 도구 흐름**, which is
 * the change §2.2 makes to R6's interleaved rows: a trace is one thing that can
 * fold, not a row wherever it happened to arrive. `blocks` keeps the **server's**
 * order (「구조화 블록(서버 순서 그대로)」). `prose` is every released sentence and
 * refusal in arrival order — one growing paragraph (R14 Q-E), which is why they
 * are not grouped further. `status` is the one transient line, or `null`.
 */
export type AnswerParts = {
  tools: ToolBlock[];
  blocks: StructuredBlock[];
  prose: ProseBlock[];
  status: StatusBlock | null;
};

/** Split a turn's blocks into §2.8's regions, each in its own arrival order. */
export function answerParts(blocks: readonly AskBlock[]): AnswerParts {
  const parts: AnswerParts = { tools: [], blocks: [], prose: [], status: null };
  for (const block of blocks) {
    if (block.kind === "tool") parts.tools.push(block);
    else if (block.kind === "data" || block.kind === "calc") parts.blocks.push(block);
    else if (block.kind === "text" || block.kind === "refusal") parts.prose.push(block);
    // 「항상 1개」 — the store's keyed reduce already guarantees it (one
    // `block_id`, replaced in place), so the last one standing is the live one.
    else parts.status = block;
  }
  return parts;
}

/** A sentence cut into runs: `unverified` runs wear the 「미확인」 marker (§2.5). */
export type ProseSegment = { text: string; unverified: boolean };

/**
 * Cut a sentence around its `unverified` spans — 「문장은 살아남고 수치만
 * 표시된다」.
 *
 * Offsets are the server's, **within this sentence, unit included**
 * (`P9.S4` note 3: 「3,200원」 is one span, not a number and a unit). They arrive
 * sorted and disjoint from `CitationGate`; this still sorts, clamps and drops
 * anything overlapping or inverted, because a bad offset must cost a marker, not
 * the sentence — §2.5's rule is that the sentence goes out either way.
 *
 * Python counts code points and JavaScript counts UTF-16 units; every figure
 * shape the gate marks (digits, 원/주/%/배, dates) and the Korean around it are
 * BMP, where the two agree.
 */
export function proseSegments(
  text: string,
  spans: readonly (readonly number[])[] | undefined,
): ProseSegment[] {
  const marks = (spans ?? [])
    .map((span) => [span[0] ?? -1, span[1] ?? -1] as const)
    .filter(([start, end]) => Number.isInteger(start) && Number.isInteger(end))
    .filter(([start, end]) => start >= 0 && end > start && end <= text.length)
    .sort((a, b) => a[0] - b[0]);

  const segments: ProseSegment[] = [];
  let at = 0;
  for (const [start, end] of marks) {
    if (start < at) continue; // overlaps one already drawn — drop the marker, keep the text
    if (start > at) segments.push({ text: text.slice(at, start), unverified: false });
    segments.push({ text: text.slice(start, end), unverified: true });
    at = end;
  }
  if (at < text.length) segments.push({ text: text.slice(at), unverified: false });
  return segments;
}

/**
 * The three `TurnEnd.reason` values that mean **소진** (`mijual.agent.loop`).
 *
 * R16 §2.7 draws an exhausted turn as dimmed prose and a folded 도구 흐름 and
 * *nothing else* — 「inset 없음 · 버튼 없음 · 신규 문자열 없음」 — while R14's
 * 「연결이 끊겼습니다」 inset + 재시도 stays for the **연결 끊김** state alone. Both
 * are `aborted` on `turn.status`, so `reason` is the only thing that tells them
 * apart (`P9.S8` note 5, which is why the field exists).
 */
const BUDGET_REASONS = new Set(["round_budget", "tool_budget", "call_budget"]);

/** 소진 (a ceiling ended the turn) rather than 연결 끊김. */
export function exhausted(reason: string | null): boolean {
  return reason !== null && BUDGET_REASONS.has(reason);
}

/**
 * 「`rows.length <= 3` **또는** 스트리밍 중 → 전부 평평하게 펼침 / `>= 4`
 * **그리고** 턴 완료 → 한 줄 요약 + 자세히」 (§2.2).
 *
 * A turn still being painted counts as streaming: while the rows are arriving
 * they *are* the progress, so they stay flat and fold when the turn settles.
 */
export function foldable(rows: number, live: boolean): boolean {
  return rows >= 4 && !live;
}
