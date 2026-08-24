"use client";

import { Fragment } from "react";
import Link from "next/link";
import type { AskBlock, AskChip, AskTurn } from "@/lib/ask";
import { KST_KO } from "@/lib/copy";
import { kstStamp } from "@/lib/format";
import { InlineCitation } from "./InlineCitation";
import { resolveLinks } from "./links";
import {
  DISCONNECTED_KO,
  FEEDBACK_SAVED_KO,
  FEEDBACK_TOOL,
  REASK_KO,
  RETRY_KO,
  evidenceCount,
} from "./copy";
import styles from "./Ask.module.css";

type ProseBlock = Extract<AskBlock, { kind: "text" } | { kind: "refusal" }>;
type Group =
  | { kind: "tool"; tool: string; row: string; ok: boolean }
  | { kind: "prose"; blocks: ProseBlock[] };

/**
 * Consecutive prose runs as one paragraph; a 도구 행 breaks it.
 *
 * The stream arrives sentence by sentence (the citation gate releases one
 * verified sentence at a time), and R6's 스트리밍 state is 「프로즈 자람」 — prose
 * growing, not a list of lines. A refusal joins the same paragraph on purpose:
 * 「렌더: 일반 답변과 같은 프로즈 (alert 색·아이콘 금지)」, and R6-7's three parts
 * (① 상태 사실 ② 가족 문장 ③ 갈 곳 링크) are exactly ①② prose then ③ links.
 */
function group(blocks: readonly AskBlock[]): Group[] {
  const groups: Group[] = [];
  for (const block of blocks) {
    if (block.kind === "tool") {
      groups.push({ kind: "tool", tool: block.tool, row: block.row, ok: block.ok });
      continue;
    }
    const last = groups[groups.length - 1];
    if (last && last.kind === "prose") last.blocks.push(block);
    else groups.push({ kind: "prose", blocks: [block] });
  }
  return groups;
}

/**
 * 「근거 N건 · {rcept_no} · {생성시각 KST}」 — the format's own `·`, and every
 * 근거 the answer rests on rather than only the first. The instant is sliced,
 * never re-parsed into a `Date`: the server emits `+09:00` and the browser
 * derives no time (`lib/format.ts`).
 *
 * **N is the number of chips on the screen** (R14 Q-B — 하나의 근거 = 하나의 칩,
 * the operator's own sentence). The server's `footer.count` counts distinct
 * **filings**, which the rcept_no list right beside it already says: an answer
 * resting on five numbered chips from one filing printed 「근거 1건」 directly
 * under [1][2][3][4][5], and to a first-time reader that is a contradiction. So
 * the count is taken from `turn.chips` and the evidence list stays the server's.
 * The wire is unchanged — this is a **client-side** reading of the same frame, and
 * the divergence is deliberate and recorded (`P8.S15`, phase note).
 */
function footerFacts(count: number, evidence: readonly string[], instant: string): string {
  const stamp = instant ? kstStamp(instant) : null;
  return [
    evidenceCount(count),
    ...evidence,
    ...(stamp ? [`${stamp.date} ${stamp.time} ${KST_KO}`] : []),
  ].join(" · ");
}

/**
 * One answer — 도구 행, 인용 붙은 프로즈, 푸터, 그리고 중단/오류 행.
 *
 * The four SSE states are **text replacement only** (R6 §SSE: 스피너·타이핑 점·
 * 버블 슬라이드 금지). What that leaves on this side is:
 *
 * - `pending` — nothing here at all; the composer's button says 답변 준비 중…, so
 *   an empty answer bubble is not even mounted (a placeholder is a fake state);
 * - `streaming` — the prose grows and the 7×15 caret blinks at its end;
 * - `done` — the footer fades in over `--dur-base`;
 * - `aborted` / `error` — the partial answer **stays**, dimmed to `--ink-2`, with
 *   the signed inset row and 재시도 under it. R6 writes one sentence for that
 *   state, so a 중지, a cut stream, a typed `error` terminal and a pre-stream
 *   refusal all show it — none of them may invent a second one.
 */
export function Answer({
  turn,
  onRetry,
  onReask,
}: {
  turn: AskTurn;
  onRetry: () => void;
  onReask: () => void;
}) {
  const groups = group(turn.blocks);
  const streaming = turn.status === "streaming";
  const stopped = turn.status === "aborted" || turn.status === "error";
  const byNumber = new Map<number, AskChip>(turn.chips.map((chip) => [chip.number, chip]));
  const lastGroup = groups[groups.length - 1];
  const caretInProse = streaming && lastGroup?.kind === "prose";

  // ③ 갈 곳 링크 belong to the refusal, right under its sentence — R6-7's three
  // parts are ① 상태 사실 ② 가족 문장 ③ 갈 곳, in that order. An answer has no
  // `links` event and takes its context links in the footer instead. The server
  // puts the same list on both frames, so exactly one of the two rows draws it.
  const refusalLinks = resolveLinks(turn.links);
  const footerLinks =
    refusalLinks.length > 0 || !turn.footer ? [] : resolveLinks(turn.footer.links);

  return (
    <div className={styles.answer} data-dim={stopped ? "true" : "false"}>
      {groups.map((item, index) =>
        item.kind === "tool" ? (
          // 도구 행 — printed **verbatim** from the tool's own signed string, so
          // what the agent read is part of the evidence. `ok` is carried for
          // `P6.S7` to inspect and deliberately given no colour of its own: R6
          // signs a 재시도 row for a failed 의견 저장 (「실패 시에만 재시도 행」), and
          // the row's own words already are that retry.
          <Fragment key={index}>
            <p className={styles.toolRow} data-ok={item.ok ? "true" : "false"}>
              {item.row}
            </p>
            {/* 의견: 자동 저장 + 확인 한 줄. The confirmation is the **surface's**
                to print (`mijual.agent.tools.save_feedback`: "the tool writes no
                Korean sentence about it, because R6 signs the confirmation copy
                and the surface renders it"), so it follows the row it is about
                and rests on the tool's own `ok` rather than on model prose. */}
            {item.tool === FEEDBACK_TOOL && item.ok ? (
              <p className={styles.prose}>{FEEDBACK_SAVED_KO}</p>
            ) : null}
          </Fragment>
        ) : (
          <p key={index} className={styles.prose}>
            {item.blocks.map((block, position) => (
              <span key={position} className={styles.sentence}>
                {block.text}
                {block.kind === "text"
                  ? block.citations.map((number) => {
                      const chip = byNumber.get(number);
                      return chip ? <InlineCitation key={number} chip={chip} /> : null;
                    })
                  : null}
              </span>
            ))}
            {caretInProse && index === groups.length - 1 ? (
              <span className={styles.caret} data-motion="tick" />
            ) : null}
          </p>
        ),
      )}

      {streaming && !caretInProse ? (
        <p className={styles.prose}>
          <span className={styles.caret} data-motion="tick" />
        </p>
      ) : null}

      {refusalLinks.length > 0 ? (
        <p className={styles.links}>
          {refusalLinks.map((link) => (
            <LinkOut key={link.key} href={link.href} external={link.external} label={link.label} />
          ))}
        </p>
      ) : null}

      {stopped ? (
        <p className={styles.stopped}>
          <span className={styles.stoppedText}>{DISCONNECTED_KO}</span>
          <button type="button" className={styles.reask} onClick={onRetry}>
            {RETRY_KO}
          </button>
        </p>
      ) : null}

      {turn.footer ? (
        <p className={styles.footer}>
          <span className={styles.footerFacts}>
            {footerFacts(turn.chips.length, turn.footer.evidence, turn.footer.generated_at)}
          </span>
          <span className={styles.links}>
            {footerLinks.map((link) => (
              <LinkOut
                key={link.key}
                href={link.href}
                external={link.external}
                label={link.label}
              />
            ))}
          </span>
          <button type="button" className={styles.reask} onClick={onReask}>
            {REASK_KO}
          </button>
        </p>
      ) : null}
    </div>
  );
}

/** DART is another site and opens in a new tab; every other destination is this
 * app's own route and goes through `next/link`. */
function LinkOut({
  href,
  label,
  external,
}: {
  href: string;
  label: string;
  external: boolean;
}) {
  if (external) {
    return (
      <a className={styles.link} href={href} target="_blank" rel="noopener noreferrer">
        {label}
      </a>
    );
  }
  return (
    <Link className={styles.link} href={href}>
      {label}
    </Link>
  );
}
