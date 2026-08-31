"use client";

import { useEffect, useRef } from "react";
import { Answer } from "./Answer";
import { Composer, type ComposerState } from "./Composer";
import {
  AGENT_INTRO_KO,
  ASK_LABEL_KO,
  NEW_CHAT_KO,
  START_CHIPS_KO,
  START_HEADING_KO,
} from "./copy";
import { useAskState, useAskStore } from "./useAsk";
import ask from "./Ask.module.css";
import styles from "./AskPage.module.css";

/**
 * 전용 페이지 — the second view over the one conversation, and the whole surface
 * on a phone.
 *
 * **R16 re-cut this page whole** (§2.7b, `P9.S10`). The two-column grid and the
 * 340 rail it held are **retired** (§0 폐기 ②), and what is left is one column:
 *
 * > 열 하나: `max-width 760px`, `margin-inline auto`. 오른쪽 열 없음, sticky
 * > aside 없음. … **빈 상태:** 페이지 세로 가운데(`min-height 560px`, ≤767 420px)에
 * > 폭 640 블록 — `START_HEADING_KO` → `AGENT_INTRO_KO` → **컴포저** → 시작용
 * > **질문 카드**. **익명 줄 없음** … **대화 상태:** 스레드가 열을 채우고 컴포저는
 * > 하단 sticky. (§2.7b)
 *
 * So the page has exactly two states, and the thread is what tells them apart:
 *
 * 1. **시작 화면** — no turn yet. The composer stands in the middle of the screen
 *    with the greeting and D1's promise above it and **six** question cards
 *    below — R16 D11 signed four, and P11's operator instruction freed the count
 *    so that one card demonstrates one agent capability; the landed
 *    build-prompt's 「5장」 and its 제품 메타 카드 remain two of the three stale
 *    lines the signed copy overrides (`copy.ts::START_CHIPS_KO` carries both
 *    citations). The array's length is the only thing that changed: this
 *    component just maps it.
 *    Pressing a card **sends the card's own sentence**: 「카드의 문장이 곧 보내는
 *    질문이다」, which is why R14's label≠question convention (`presets.ts`) is
 *    explicitly *not* applied here.
 * 2. **대화 상태** — the thread fills the column and the composer is
 *    bottom-sticky. 「새 대화」 appears **only here** (「시작 화면에는 그리지
 *    않는다 — 비울 것이 없다」), sticky at the column's top right, and it empties
 *    the thread and nothing else: no history list, no titles, no restore (R6's
 *    ban stands).
 *
 * The four things the rail used to carry are settled rather than moved: the 범위
 * chip and the 익명 줄 are retired outright (폐기 ⓐ·①), the promise line went with
 * the rail (폐기 ②), and the intro is now the start screen's own second line.
 *
 * What did **not** change:
 *
 * - **No frame.** The chat is `<main>`'s own children — 「챗 표면 프레임 없음:
 *   패널·브래킷 없이 페이지에 직접」. The page's one panel was the rail, and the
 *   rail is gone, so this surface now has no `CraftPanel` at all.
 * - **A second view, never a second store.** Everything here reads
 *   `useAskState()` and calls the same `lib/ask.ts` the widget calls, so arriving
 *   mid-stream simply renders the snapshot as it grows.
 * - **Arriving closes the widget.** 「위젯이 열려 있으면 닫고 리다이렉트」 —
 *   `close()` touches the thread not at all, so 「대화·범위 그대로」 holds.
 * - **No auto-scroll.** The widget scrolls its own 620px thread box; scrolling the
 *   document under a reader as prose grows is ambient motion R1 keeps off data
 *   surfaces, and the sticky bar is what keeps the input reachable instead.
 */
export function AskPage() {
  const store = useAskStore();
  const state = useAskState();
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    store.close();
  }, [store]);

  const last = state.turns[state.turns.length - 1];
  const composer: ComposerState =
    last?.status === "pending" ? "pending" : last?.status === "streaming" ? "streaming" : "idle";
  const thread = state.turns.length > 0;

  // One composer, two placements. The page's is `plain`: 입력창 자신의 1px만,
  // 구분선 없음 (§2.7b) — the widget's R14 geometry is untouched.
  const composerBox = (
    <Composer plain state={composer} inputRef={input} onAsk={store.ask} onStop={store.stop} />
  );

  return (
    <main className={`content ${styles.page}`} aria-label={ASK_LABEL_KO}>
      {thread ? (
        <>
          {/* 「새 대화」 — 스레드가 있을 때만 존재한다. Sticky at the top of the
              column so a long thread never scrolls it away, and its only action is
              to empty the thread (`store.newChat`). */}
          <div className={styles.top}>
            <button type="button" className={styles.new} onClick={store.newChat}>
              {NEW_CHAT_KO}
            </button>
          </div>

          <div className={styles.column}>
            {state.turns.map((turn) => (
              <div key={turn.id} className={ask.turn}>
                <p className={ask.question}>{turn.question}</p>
                {turn.blocks.length > 0 || turn.status === "aborted" || turn.status === "error" ? (
                  <Answer turn={turn} onRetry={() => store.retry(turn.id)} />
                ) : null}
              </div>
            ))}

            {/* 「입력 바 하단 sticky (44px)」 — `position: sticky`, so nothing on
                this page is newly `position: fixed`. */}
            <div className={styles.bar}>{composerBox}</div>
          </div>
        </>
      ) : (
        // 빈 상태 — 페이지 세로 가운데. The block is centre-aligned; only the typed
        // question and the questions inside the cards are left-aligned.
        <div className={styles.centered}>
          <div className={styles.start}>
            <h1 className={styles.heading}>{START_HEADING_KO}</h1>
            <p className={styles.intro}>{AGENT_INTRO_KO}</p>
            <div className={styles.startComposer}>{composerBox}</div>
            <div className={styles.cards}>
              {START_CHIPS_KO.map((question) => (
                <button
                  key={question}
                  type="button"
                  className={styles.card}
                  onClick={() => store.ask(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
