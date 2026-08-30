"use client";

import { ASK_LABEL_KO } from "./copy";
import styles from "./Launcher.module.css";

/**
 * 우하단 고정 런처 — a 68×50 chat-message box with the 32×32 브랜드 스파클 inside it.
 *
 * The frame, the tail and the states are R6's, **the mark and the motion are
 * R17's** (§3, signed 2026-08-31). `Launcher.module.css` carries every number and
 * every reason; what this component owns is only the DOM.
 *
 * And the DOM is now almost nothing. R6's mark needed four nested spans in a
 * load-bearing order — the ring's top half behind the planet, the planet with its
 * rotation band, the ring's bottom half in front — because two clipped halves
 * sharing one drift were what made a flat sticker read as a ring the planet
 * passes through. R17 deletes the Saturn outright, so **the mark is one span**,
 * painted by a CSS `mask` over `currentColor`, and the three `data-motion="tick"`
 * hooks are gone with the animations they froze.
 *
 * ## Where it renders, and where it must not
 *
 * `AskSurface` decides: desktop only (≤767px renders **nothing** — 위젯·런처 없음,
 * R14 Q-A's boundary),
 * never on `/ask` (전용 페이지에는 런처 렌더 금지 — 중복 표면 금지), and never
 * inside the ops chrome (which `SiteChrome` never wraps in the reader tree at
 * all). That boundary is untouched by R17. The corner is R2's deliberately empty
 * one and vocky's trigger is chrome-level, so 「런처·위젯은 vocky 트리거와 모서리
 * 충돌 금지」 holds by construction — and R17 additionally reserves the footer's
 * own right corner (`chrome/Footer.module.css`), because this launcher was
 * covering the 의견 보내기 button underneath it.
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
      <span className={styles.mark} />
      <span className={styles.close} />
    </button>
  );
}
