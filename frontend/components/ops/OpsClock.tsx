"use client";

import { useEffect, useState } from "react";
import { KST } from "./copy";
import styles from "./Ops.module.css";

/**
 * The ops bar's KST clock.
 *
 * It is the **operator's own wall clock**, not a product number: every date and
 * D-day this product publishes is computed upstream in KST and delivered as an
 * absolute instant (`frontend` v0002), and nothing on this surface is derived
 * from this readout. It is formatted in `Asia/Seoul` explicitly, so an operator
 * working from another timezone still reads the schedule's own hours.
 *
 * Two notes for the fidelity pass:
 *
 * - The first render is computed the same way on the server and in the browser,
 *   so `suppressHydrationWarning` covers only the second that may elapse between
 *   them — the pattern `P5.S12`'s countdown established.
 * - **The tick is not stopped under `prefers-reduced-motion`.** The shell's
 *   convention freezes *animation*, and R2 asked for a static countdown in so
 *   many words; R7 asks for a 시계, and a clock that silently stops is a wrong
 *   number on a panel whose whole rule is that numbers are real.
 */
const FORMATTER = new Intl.DateTimeFormat("sv-SE", {
  timeZone: "Asia/Seoul",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

function nowKst(): string {
  // `sv-SE` formats as `YYYY-MM-DD HH:MM:SS` — ISO-shaped, and the same shape
  // every stamp on this surface uses.
  return FORMATTER.format(new Date());
}

export function OpsClock() {
  const [now, setNow] = useState(nowKst);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(nowKst()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <span className={styles.clock} suppressHydrationWarning>
      {now} {KST}
    </span>
  );
}
