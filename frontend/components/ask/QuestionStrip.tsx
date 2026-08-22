"use client";

import { useId } from "react";
import { usePathname, useRouter } from "next/navigation";
import { ROUTES, isActiveRoute } from "@/lib/routes";
import type { AskScope } from "@/lib/ask";
import { ASK_ABOUT_KO, ASK_SUBMIT_KO } from "./copy";
import type { AskPreset } from "./presets";
import { useAskStore, useDesktop } from "./useAsk";
import styles from "./Strip.module.css";

/**
 * 질문 스트립 — the event detail page's preset chips, and the mobile page's row.
 *
 * > 상세의 질문 스트립(프리셋 칩 — 그 이벤트의 게이트 통과 필드에서 생성)은 위젯
 * > (모바일: 페이지)을 이벤트 범위로 열며 질문 전송 — **스트립 자체는 답변을
 * > 렌더하지 않음.** (R6 §Surfaces)
 * >
 * > 프리셋 = 가로 스크롤 한 줄 (타깃 ≥44px) (R6 §Mobile)
 *
 * So the strip is an **entry point, not a surface**: it holds no state, subscribes
 * to nothing, and renders no answer. One press does three things in this order —
 * `setScope` (the reader's own choice, which is what a chip press is), `ask`, and
 * then whichever surface is the reader's:
 *
 * - **desktop** → `open()`, the widget (「위젯을 이벤트 범위로 열며 질문 전송」);
 * - **≤480px** → `/ask`, the whole surface there (「모바일: 페이지」). Going back
 *   returns the reader to this page with the conversation intact, because the
 *   thread lives in `lib/ask.ts` rather than in either view;
 * - **already on `/ask`** → nothing to open; the question simply starts.
 *
 * `setScope` rather than `setPageScope`: the page's *ambient* 범위 is bound by
 * `AskPageScope` and yields to a 범위 the reader chose, while pressing a chip **is**
 * that choice (`lib/ask.ts`'s two entry points, `P6.S5` note 22). A `scope` carries
 * `{rcept_no, name}` because the signed chip prints 「범위: {종목} · {rcept_no}」.
 *
 * The last chip is R6-2's 「직접 질문 입력 →」 — presets first, free input one step
 * behind: it opens the same surface in the same 범위 and sends **nothing**.
 */
export function QuestionStrip({
  scope,
  presets,
  freeInput = true,
}: {
  scope: AskScope;
  presets: readonly AskPreset[];
  /** The 직접 질문 입력 → chip. Off on `/ask`, where the composer is already the
   * next thing on the page and a chip pointing at it would be a second one. */
  freeInput?: boolean;
}) {
  const store = useAskStore();
  const desktop = useDesktop();
  const router = useRouter();
  const pathname = usePathname() ?? "";
  const onPage = isActiveRoute(pathname, ROUTES.ask);
  const headingId = useId();

  if (presets.length === 0 && !freeInput) return null;

  function press(question?: string) {
    store.setScope(scope);
    if (question) store.ask(question);
    if (onPage) return;
    if (desktop) store.open();
    else router.push(ROUTES.ask);
  }

  return (
    // The region takes its name from the label it already shows, rather than
    // repeating the string as an `aria-label` a screen reader would read twice.
    <section className={styles.strip} aria-labelledby={headingId}>
      <p id={headingId} className={`mono ${styles.heading}`}>
        {ASK_ABOUT_KO}
      </p>
      <div className={styles.row}>
        {presets.map((preset) => (
          <button
            key={preset.key}
            type="button"
            className={styles.chip}
            onClick={() => press(preset.question)}
          >
            {preset.label}
          </button>
        ))}
        {freeInput ? (
          <button
            type="button"
            className={`${styles.chip} ${styles.free}`}
            onClick={() => press()}
          >
            {ASK_SUBMIT_KO}
          </button>
        ) : null}
      </div>
    </section>
  );
}
