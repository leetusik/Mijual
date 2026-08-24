"use client";

import { ASK_LABEL_KO } from "./copy";
import styles from "./Launcher.module.css";

/**
 * 우하단 고정 런처 — a 68×50 chat-message box with a 22px Saturn inside it.
 *
 * The whole specification is R6 §Surfaces 「런처 (클릭 전)」 + §런처 마크 and it is
 * literal; `Launcher.module.css` carries the numbers and the reasons. What this
 * component owns is only the DOM order the mark depends on, which is not a style
 * choice but the fix the round paid for (개정 ⑧):
 *
 * 1. the ring's **top** half, clipped — painted *behind* the planet, so it is
 *    first in the DOM;
 * 2. the planet, with its rotation band;
 * 3. the ring's **bottom** half, clipped — painted *in front*, so it is last.
 *
 * Two halves sharing one `ringdrift` read as a single ring the planet passes
 * through. One ring on one side reads as a flat sticker.
 *
 * ## Where it renders, and where it must not
 *
 * `AskSurface` decides: desktop only (≤767px renders **nothing** — 위젯·런처 없음,
 * R14 Q-A's boundary),
 * never on `/ask` (전용 페이지에는 런처 렌더 금지 — 중복 표면 금지), and never
 * inside the ops chrome (which `SiteChrome` never wraps in the reader tree at
 * all). The corner is R2's deliberately empty one and vocky's trigger is chrome-
 * level, so 「런처·위젯은 vocky 트리거와 모서리 충돌 금지」 holds by construction.
 */
export function AskLauncher({ open, onOpen }: { open: boolean; onOpen: () => void }) {
  return (
    <button
      type="button"
      className={styles.launcher}
      data-open={open ? "true" : "false"}
      // 「런처는 열리면 숨음」: the widget is opaque and covers this exact corner,
      // and the launcher stops taking focus or clicks while it is up.
      inert={open}
      aria-label={ASK_LABEL_KO}
      aria-expanded={open}
      onClick={onOpen}
    >
      <span className={styles.tail} />
      <span className={styles.mark}>
        <span className={`${styles.ring} ${styles.ringBehind}`} data-motion="tick" />
        <span className={styles.planet}>
          <span className={styles.band} data-motion="tick" />
        </span>
        <span className={`${styles.ring} ${styles.ringFront}`} data-motion="tick" />
      </span>
      <span className={styles.close} />
    </button>
  );
}
