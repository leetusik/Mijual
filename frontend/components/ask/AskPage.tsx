"use client";

import { useEffect, useRef, useState } from "react";
import { CraftPanel } from "@/components";
import { getEvent } from "@/lib/api";
import type { AskScope } from "@/lib/ask";
import { Answer } from "./Answer";
import { Composer, type ComposerState } from "./Composer";
import {
  AGENT_INTRO_KO,
  ANONYMITY_KO,
  ASK_LABEL_KO,
  CLOSE_GLYPH,
  VERIFIED_ONLY_KO,
  scopeLabel,
} from "./copy";
import { presetsFor, type AskPreset } from "./presets";
import { QuestionStrip } from "./QuestionStrip";
import { useAskState, useAskStore } from "./useAsk";
import ask from "./Ask.module.css";
import styles from "./AskPage.module.css";

/**
 * 전용 페이지 — the second view over the one conversation, and the whole surface
 * on a phone.
 *
 * > **전용 페이지의 챗 표면은 프레임 없음** — 패널·브래킷 없이 페이지에 직접,
 * > 우측 340 레일만 패널 (R6 §Surfaces, 개정 ④). 페이지에는 런처 렌더 금지
 * > (중복 표면 금지). 위젯이 열려 있으면 닫고 리다이렉트 — 대화·범위 그대로.
 * >
 * > **모바일 (≤480px)**: 위젯·런처 없음 — AI 질문 = 전폭 페이지 하나. 프리셋 =
 * > 가로 스크롤 한 줄 (타깃 ≥44px), 인용 블록 전폭 (180px 캡 + 스크롤), 입력 바
 * > 하단 sticky (44px), 도구 행 유지. (R6 §Mobile)
 *
 * Four things follow, and all four are decisions rather than layout:
 *
 * 1. **No frame.** The chat is `<main>`'s own children — no `CraftPanel`, no
 *    corner brackets, no border. The single panel on this page is the 340 rail,
 *    and it *is* a `CraftPanel`, because the record contrasts 「패널·브래킷 없이」
 *    with 「레일만 패널」 and this product's panel is the craft panel (R2.1).
 * 2. **A second view, never a second store.** Everything here reads
 *    `useAskState()` and calls the same `lib/ask.ts` the widget calls, so arriving
 *    mid-stream simply renders the snapshot as it grows — the fetch belongs to the
 *    store, which outlives both surfaces (`P6.S5` note 22).
 * 3. **Arriving closes the widget.** 「위젯이 열려 있으면 닫고 리다이렉트」: the
 *    header's external-link already does it, and this does it for every other way
 *    in (the nav slot, the footer link, a typed URL) — `close()` touches the
 *    thread not at all, so 「대화·범위 그대로」 holds. `AskSurface` additionally
 *    renders neither launcher nor widget on this route (`P6.S5`).
 * 4. **The rail's contents are the nearest signed strings, and that is flagged.**
 *    R6 fixes the rail's width and its panel-ness and writes nothing about what is
 *    in it (there are no R6 cards in this repository — phase note, §Context). So
 *    it carries the four things the design does write for this surface: the 범위
 *    chip 「범위: {종목} · {rcept_no}」 with its × (R6 §범위 모델 — the widget puts
 *    it in a header this page does not have), the panel promise 「검증된 필드만
 *    근거로 답합니다 — 모든 답에 원문 인용」, the agent intro, and the 세션·저장
 *    line. ⚠ `P6.S7`/`P6.REVIEW` confirm this against the record's own Page card.
 */
export function AskPage() {
  const store = useAskStore();
  const state = useAskState();
  const input = useRef<HTMLInputElement>(null);
  const presets = useScopePresets(state.scope);

  useEffect(() => {
    store.close();
  }, [store]);

  const last = state.turns[state.turns.length - 1];
  const composer: ComposerState =
    last?.status === "pending" ? "pending" : last?.status === "streaming" ? "streaming" : "idle";

  return (
    <main className={`content ${styles.page}`} aria-label={ASK_LABEL_KO}>
      <div className={styles.columns}>
        {/* 우측 340 레일 — the page's only panel. It leads in the DOM so the
            surface reads 범위 → 약속 → 인트로 → 대화 in every layout, which is
            also the order the widget's thread opens with. */}
        <CraftPanel as="aside" className={styles.rail}>
          <p className={ask.scope}>
            <span className={ask.scopeText}>{scopeLabel(state.scope)}</span>
            {state.scope ? (
              <button type="button" className={ask.scopeClear} onClick={store.clearScope}>
                {CLOSE_GLYPH}
              </button>
            ) : null}
          </p>
          <p className={styles.promise}>{VERIFIED_ONLY_KO}</p>
          <p className={ask.introText}>{AGENT_INTRO_KO}</p>
          <p className={ask.anonymity}>{ANONYMITY_KO}</p>
        </CraftPanel>

        <div className={styles.chat}>
          {/* The conversation, directly on the page. No auto-scroll: the widget
              scrolls its own 620px thread box, but scrolling the document under a
              reader as prose grows is ambient motion R1 keeps off data surfaces —
              the sticky bar below keeps the input reachable instead. */}
          {state.turns.map((turn) => (
            <div key={turn.id} className={ask.turn}>
              <p className={ask.question}>{turn.question}</p>
              {turn.blocks.length > 0 || turn.status === "aborted" || turn.status === "error" ? (
                <Answer
                  turn={turn}
                  onRetry={() => store.retry(turn.id)}
                  onReask={() => input.current?.focus()}
                />
              ) : null}
            </div>
          ))}

          {/* 프리셋 — the same 질문 스트립 as the detail page's, generated from the
              same gate-passing fields, shown while the 범위 is an event. 자유 입력
              is not one step behind here: the composer is the next element. */}
          {state.scope && presets.length > 0 ? (
            <QuestionStrip scope={state.scope} presets={presets} freeInput={false} />
          ) : null}

          {/* 「입력 바 하단 sticky (44px)」 — `position: sticky`, so nothing on this
              page is newly `position: fixed`. */}
          <div className={styles.bar}>
            <Composer state={composer} inputRef={input} onAsk={store.ask} onStop={store.stop} />
          </div>
        </div>
      </div>
    </main>
  );
}

/**
 * The 범위 event's gate-passing fields, read the same way the detail page reads
 * them — so a preset chip on this page and the one on `/events/{rcept_no}` are
 * generated from one payload by one rule (`presets.ts`).
 *
 * `GET /events/{rcept_no}` is the page's own contract call, anonymous and
 * read-only, and its `fields` map already holds **only** what the gate passed. A
 * failure or an abort yields **no chips** rather than a message: R6 writes no copy
 * for a preset row that could not be built, and the composer below is the surface
 * either way. A 철회 event yields none either — 「답할 수 없는 질문은 프리셋으로
 * 제안하지 않음」, and 철회 is the refusal family the agent would answer with.
 */
function useScopePresets(scope: AskScope | null): AskPreset[] {
  const [presets, setPresets] = useState<AskPreset[]>([]);
  const rceptNo = scope?.rcept_no ?? null;

  useEffect(() => {
    setPresets([]);
    if (!rceptNo) return;
    const controller = new AbortController();
    getEvent(rceptNo, { signal: controller.signal })
      .then((detail) => {
        if (controller.signal.aborted) return;
        setPresets(detail.state === "withdrawn" ? [] : presetsFor(detail.fields));
      })
      .catch(() => undefined);
    return () => controller.abort();
  }, [rceptNo]);

  return presets;
}
