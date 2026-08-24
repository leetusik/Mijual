"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/lib/routes";
import { Answer } from "./Answer";
import { Composer, type ComposerState } from "./Composer";
import { AGENT_INTRO_KO, ASK_LABEL_KO, ASK_PAGE_LINK_KO, CLOSE_GLYPH } from "./copy";
import { QuestionStrip } from "./QuestionStrip";
import { useAskState, useAskStore } from "./useAsk";
import { useScopePresets } from "./useScopePresets";
import styles from "./Ask.module.css";

/**
 * 위젯 챗룸 — 제자리 위젯 **440×620**, 불투명 `#0e1a15`, 우하단 고정.
 *
 * > `position:fixed` 우하단 (본문 오버레이; 백드롭·dim 없음; 런처는 열리면 숨음,
 * > ×로 닫고 복귀). … 헤더 우측: Lucide `external-link` (= 전용 페이지 리다이렉트)
 * > + ×, 각 28px 정사각. 답변은 메시지 버블. **랜딩 포함 모든 페이지 레이아웃
 * > 불변.** (R6 §Surfaces, 개정 ①·②·⑥)
 *
 * It is a **view over `lib/ask.ts`**, not an owner: the thread, the 범위 and the
 * SSE fetch live in the store at the persistent-layout level, so closing this
 * panel — or walking to `/ask` — interrupts nothing (「스트리밍 중 이동/전환에도
 * 끊김 없음」). `P6.S6`'s page is the second view over the same store.
 *
 * **R14 moved two things here.** The widget now exists only above **767px**
 * (Q-A — `AskSurface` decides it, and the panel's `max-width` guard went with the
 * boundary: the narrowest window that renders one fits 440 exactly). And an empty
 * thread whose 범위 is an event fills its middle with the **질문 스트립** under the
 * intro (finding 8) — the same chips the detail page shows, without the free-input
 * chip, because the composer is right below. A 전체 공시 widget's empty middle
 * stays empty: that **is** the state, and the round minted no empty-state copy.
 *
 * **R16 took two things out of this panel and added none** (§0 폐기, `P9.S10`).
 * The header's 범위 chip and its × are gone — 「`AskWidget` 헤더에는 ↗·× 두
 * 아이콘만 남는다」 — and so is the 익명 줄 under the intro, because R6-5 is kept
 * **as a property** (no login, no history, no quota) rather than declared as a
 * sentence. The 범위 *state* is untouched: a widget opened from an event detail
 * still asks in that filing's 범위 and still shows its 질문 스트립 (회귀 19), it
 * simply no longer says so on screen. Everything else here is R14's, unchanged.
 */
export function AskWidget() {
  const store = useAskStore();
  const state = useAskState();
  const router = useRouter();
  const thread = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLInputElement>(null);

  const presets = useScopePresets(state.turns.length === 0 ? state.scope : null);

  const last = state.turns[state.turns.length - 1];
  const composer: ComposerState =
    last?.status === "pending" ? "pending" : last?.status === "streaming" ? "streaming" : "idle";

  // Keep the newest line in view as the answer grows. An instant scroll, never a
  // smooth one: R6 allows fades and nothing else, and a scroll animation is
  // exactly the ambient motion R1 keeps off data surfaces.
  const painted = `${state.turns.length}:${last?.blocks.length ?? 0}:${last?.status ?? ""}`;
  useEffect(() => {
    const element = thread.current;
    if (element) element.scrollTop = element.scrollHeight;
  }, [painted]);

  return (
    // The panel's accessible name is the surface's own signed one — no new copy,
    // and nothing rendered that the design does not draw.
    <section className={styles.widget} aria-label={ASK_LABEL_KO}>
      {/* R16 §0 폐기 ①: 「범위: …」 칩과 그 ×는 헤더에서 제거되고 **↗·× 두
          아이콘만 남는다**. 범위 자체는 스토어에 그대로 있고(이벤트 상세에서 연
          위젯은 여전히 그 공시를 범위로 묻는다 — 회귀 19) 표면에 그리지 않을 뿐이다. */}
      <header className={styles.header}>
        <span className={styles.actions}>
          <button
            type="button"
            className={styles.icon}
            aria-label={ASK_PAGE_LINK_KO}
            onClick={() => {
              // 「위젯이 열려 있으면 닫고 리다이렉트 — 대화·범위 그대로」: the store
              // outlives both surfaces, so the thread simply reappears there.
              store.close();
              router.push(ROUTES.ask);
            }}
          >
            <ExternalLinkIcon />
          </button>
          <button type="button" className={styles.icon} onClick={store.close}>
            <span className={styles.iconGlyph}>{CLOSE_GLYPH}</span>
          </button>
        </span>
      </header>

      <div className={styles.thread} ref={thread}>
        {/* 빈 스레드의 인트로 = D1 한 줄. 익명 줄은 폐기 ⓐ로 사라졌다 — R6-5는
            기능으로 지켜지므로(로그인·이력·quota 없음) 표면이 선언하지 않는다. */}
        <div className={styles.intro}>
          <p className={styles.introText}>{AGENT_INTRO_KO}</p>
        </div>

        {/* finding 8 — 빈 스레드 · 범위 = 이벤트: the preset row is what the middle
            of this panel is for. It disappears the moment there is a turn to
            read, and it never appears in 전체 공시 범위, where there is no event
            to generate chips from. `freeInput={false}`: the composer below is the
            free input, and a chip pointing at it would be a second one. */}
        {state.turns.length === 0 && state.scope ? (
          <QuestionStrip scope={state.scope} presets={presets} freeInput={false} />
        ) : null}

        {state.turns.map((turn) => (
          <div key={turn.id} className={styles.turn}>
            <p className={styles.question}>{turn.question}</p>
            {/* A `pending` turn mounts no answer bubble at all: the button already
                says 답변 준비 중…, and an empty bubble would be a placeholder for a
                state that has produced nothing. */}
            {turn.blocks.length > 0 || turn.status === "aborted" || turn.status === "error" ? (
              <Answer turn={turn} onRetry={() => store.retry(turn.id)} />
            ) : null}
          </div>
        ))}
      </div>

      <Composer
        state={composer}
        inputRef={input}
        onAsk={store.ask}
        onStop={store.stop}
      />
    </section>
  );
}

/**
 * Lucide `external-link`, inlined.
 *
 * R6 names the icon set (「Lucide `external-link`」) and this is that icon's own
 * path data (lucide, ISC): three strokes at 24×24, `currentColor`, 2px round
 * caps. It is inlined rather than installed because it is the **one** icon this
 * product draws — every other affordance in the signed design is text, a hairline
 * or a token — and a dependency for one 16px glyph would be a build cost with no
 * second call site.
 */
function ExternalLinkIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M15 3h6v6" />
      <path d="M10 14 21 3" />
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h6" />
    </svg>
  );
}
