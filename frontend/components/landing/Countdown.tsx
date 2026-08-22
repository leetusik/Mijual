"use client";

import { useEffect, useState } from "react";
import { useReducedMotion } from "@/lib/motion";
import styles from "./Countdown.module.css";

/**
 * The 소멸 countdown (R2 §Countdown).
 *
 * > Mono 28px/600 `--alert`: `{d}일 HH:MM:SS`, colons `animation: blink 1s
 * > step-end infinite`; `prefers-reduced-motion: reduce` → **no animation, static
 * > value**. Target = earliest 소멸 instant … The instant arrives from the
 * > backend as an absolute KST timestamp; **the browser only diffs against it —
 * > it never derives dates.**
 *
 * That last rule is the whole design of this component. `target` is
 * `/board/summary`'s `next_lapse.target`, an absolute `+09:00` instant the server
 * computed (end of the 청약 day, behind `MIJUAL_COUNTDOWN_CUTOFF_TIME` —
 * `P5.S3`'s decision 1). This file subtracts two instants and formats the
 * remainder; it parses no calendar, applies no timezone and would render the
 * same difference in Seoul and in Los Angeles.
 *
 * **Reduced motion stops the interval, not just the animation.** CSS can freeze
 * the colon blink (`data-motion="tick"`), but "static value" means the seconds
 * must not advance either, and CSS cannot stop a `setInterval` — which is why
 * `useReducedMotion()` exists (`P5.S10` note 6).
 *
 * The first render happens on the server and the first client render happens a
 * moment later, so their seconds differ by construction: `suppressHydrationWarning`
 * marks the text nodes where that is expected rather than a bug.
 */
export function Countdown({ target }: { target: string }) {
  const reduced = useReducedMotion();
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (reduced) {
      // One correction to the reader's own clock, then nothing moves again.
      setNow(Date.now());
      return;
    }
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [reduced]);

  const remaining = Math.max(0, Date.parse(target) - now);
  const seconds = Math.floor(remaining / 1000);
  const days = Math.floor(seconds / 86400);
  const head = `${days}일 ${pad(Math.floor(seconds / 3600) % 24)}`;
  const minutes = pad(Math.floor(seconds / 60) % 60);

  return (
    <p className={styles.countdown}>
      <span suppressHydrationWarning>{head}</span>
      <span aria-hidden="true" className={styles.colon} data-motion="tick">
        :
      </span>
      <span suppressHydrationWarning>{minutes}</span>
      <span aria-hidden="true" className={styles.colon} data-motion="tick">
        :
      </span>
      <span suppressHydrationWarning>{pad(seconds % 60)}</span>
    </p>
  );
}

function pad(value: number): string {
  return String(value).padStart(2, "0");
}
