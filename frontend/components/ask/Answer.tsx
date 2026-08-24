"use client";

import { Fragment } from "react";
import Link from "next/link";
import type { AskChip, AskTurn } from "@/lib/ask";
import { KST_KO } from "@/lib/copy";
import { kstStamp } from "@/lib/format";
import { CalcBlock } from "./CalcBlock";
import { DataBlock } from "./DataBlock";
import { InlineCitation } from "./InlineCitation";
import { resolveLinks } from "./links";
import { StatusLine } from "./StatusLine";
import { ToolTrace } from "./ToolTrace";
import { ValueMarker } from "./ValueMarker";
import { answerParts, exhausted, proseSegments } from "./render";
import {
  DISCONNECTED_KO,
  FEEDBACK_SAVED_KO,
  FEEDBACK_TOOL,
  REASK_KO,
  RETRY_KO,
  evidenceCount,
} from "./copy";
import styles from "./Ask.module.css";

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
 *
 * R16 keeps that reading and makes it *visible*: a 데이터 행 or a 계산 입력 wears
 * the same numbered chip as the prose (같은 근거 = 같은 번호), so a turn whose
 * rows carry chips the sentences never cite now shows exactly as many chips as
 * the footer counts (`P9.S3` note 7 — the transitional mismatch closes here). A
 * calculation's **result** is never counted (§2.4).
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
 * One answer — R16 §2.8's child order, drawn the same way in **both** views.
 *
 * > 답변 상자의 자식 순서: **도구 흐름 → 구조화 블록(서버 순서 그대로) → 프로즈 →
 * > 링크 → 진행 표시 / 끝맺음 → 푸터.** 간격은 `.aa`의 `gap 12px` 하나. 블록은
 * > 항상 전폭이며 나란히 놓이지 않는다. 폭이 바꾸는 것은 값 칸 스크롤 여부와
 * > ≤767의 `margin-inline: -12px`뿐. (§2.8 — 두 시야 공통, **포크 금지**)
 *
 * The widget and `/ask` are two views over one store, so this is the only place
 * that decides what an answer looks like. The store keeps blocks in **arrival**
 * order and `render.ts` sorts them into the four regions above; nothing here
 * re-orders the server's own sequence within a region.
 *
 * What each region is:
 *
 * - **도구 흐름** — every 도구 행 of the turn as one `ToolTrace`, flat at ≤3 rows
 *   or while the turn is being painted, folded to 「도구 N번 · 공시 M건 읽음」 +
 *   자세히 once a ≥4-row turn settles (§2.2). R6 drew each row where it arrived;
 *   a trace that can fold has to be one element.
 * - **구조화 블록** — 공시에서 읽은 값 and 계산, in the server's order, always full
 *   width and never side by side (§2.3/§2.4).
 * - **프로즈** — one growing paragraph (R14 Q-E), refusals included: 「렌더: 일반
 *   답변과 같은 프로즈 (alert 색·아이콘 금지)」. A 미확인 span inside a sentence is
 *   drawn by `ValueMarker`, and the sentence stands either way (§2.5,
 *   strip-don't-drop).
 * - **링크 → 진행 표시 / 끝맺음 → 푸터** — R6-7's ③ 갈 곳 under the refusal it
 *   belongs to, then the one transient status line **or** the ending row, then
 *   the footer.
 *
 * ## 소진 vs 연결 끊김 — the one thing `status` alone cannot tell you
 *
 * Both are `aborted`, and R16 draws them differently: 「**inset 없음 · 버튼 없음 ·
 * 신규 문자열 없음.** 소진의 표식은 감쇠된 프로즈와 접힌 도구 흐름뿐이다」 (§2.7),
 * while R14's 「연결이 끊겼습니다」 inset + 재시도 stays for the disconnect state
 * alone. `turn.reason` is what separates them (`P9.S8` note 5); a budget reason
 * therefore draws **nothing extra** — the dimming and the folded trace, which
 * this component already does for every stopped turn, are the whole signal.
 *
 * ## The four SSE states, unchanged (R6 §SSE: 스피너·타이핑 점·버블 슬라이드 금지)
 *
 * `pending` — nothing painted yet, and from R16 the first frame is a 진행 표시
 * line rather than an empty box · `streaming` — the prose grows and the 7×15
 * caret blinks at its end · `done` — the footer fades in · `aborted`/`error` —
 * the partial answer **stays**, dimmed to `--ink-2`.
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
  const { tools, blocks, prose, status } = answerParts(turn.blocks);
  const live = turn.status === "pending" || turn.status === "streaming";
  const streaming = turn.status === "streaming";
  const stopped = turn.status === "aborted" || turn.status === "error";
  // 소진: dimmed prose + a folded trace and **nothing else** (§2.7). Only a
  // disconnect keeps R14's inset row and its 재시도.
  const disconnected = stopped && !exhausted(turn.reason);
  const byNumber = new Map<number, AskChip>(turn.chips.map((chip) => [chip.number, chip]));

  // 의견: 자동 저장 + 확인 한 줄. The confirmation is the **surface's** to print
  // (`mijual.agent.tools.save_feedback`: "the tool writes no Korean sentence
  // about it, because R6 signs the confirmation copy and the surface renders
  // it"), and it rests on the tool's own `ok` rather than on model prose. R6 put
  // it under the 의견 저장 행; the rows now live in a trace that may fold, so it
  // follows the trace instead — the nearest place it stays visible.
  const feedbackSaved = tools.some((block) => block.tool === FEEDBACK_TOOL && block.ok);

  // ③ 갈 곳 링크 belong to the refusal, right under its sentence — R6-7's three
  // parts are ① 상태 사실 ② 가족 문장 ③ 갈 곳, in that order. An answer has no
  // `links` event and takes its context links in the footer instead. The server
  // puts the same list on both frames, so exactly one of the two rows draws it.
  const refusalLinks = resolveLinks(turn.links);
  const footerLinks =
    refusalLinks.length > 0 || !turn.footer ? [] : resolveLinks(turn.footer.links);

  return (
    <div className={styles.answer} data-dim={stopped ? "true" : "false"}>
      {tools.length > 0 ? (
        <ToolTrace rows={tools} filings={turn.filings} live={live} />
      ) : null}

      {feedbackSaved ? <p className={styles.prose}>{FEEDBACK_SAVED_KO}</p> : null}

      {blocks.map((block, index) =>
        block.kind === "calc" ? (
          <CalcBlock
            key={block.block_id ?? index}
            mode={block.mode}
            name={block.name}
            inputs={block.inputs}
            state={block.state}
            expr={block.expr}
            result={block.result}
            why={block.why}
            chips={byNumber}
          />
        ) : (
          <DataBlock
            key={block.block_id ?? index}
            rows={block.rows}
            title={block.title}
            chips={byNumber}
          />
        ),
      )}

      {prose.length > 0 ? (
        <p className={styles.prose}>
          {prose.map((block, index) => (
            <span key={index} className={styles.sentence}>
              {block.kind === "text"
                ? proseSegments(block.text, block.unverified).map((segment, at) =>
                    segment.unverified ? (
                      // 「미확인」 — a 공시 figure no tool returned. The sentence
                      // lives and only the number is marked (§2.5, Q-B).
                      <ValueMarker key={at} kind="unverified">
                        {segment.text}
                      </ValueMarker>
                    ) : (
                      <Fragment key={at}>{segment.text}</Fragment>
                    ),
                  )
                : block.text}
              {/* 칩은 문장의 **마침표 뒤**에 온다 (§2.6) — the chip follows the
                  sentence it belongs to, which the server already released whole. */}
              {block.kind === "text"
                ? block.citations.map((number) => {
                    const chip = byNumber.get(number);
                    return chip ? <InlineCitation key={number} chip={chip} /> : null;
                  })
                : null}
            </span>
          ))}
          {streaming ? <span className={styles.caret} data-motion="tick" /> : null}
        </p>
      ) : null}

      {/* The caret belongs to growing prose. Before the first sentence the 진행
          표시 line is the turn's own account of itself, so the two never appear
          together; a stream with neither (a pre-R16 server, or a turn whose only
          blocks are tool rows) keeps R14's bare caret. */}
      {streaming && prose.length === 0 && status === null ? (
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

      {status ? <StatusLine text={status.text} /> : null}

      {disconnected ? (
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
