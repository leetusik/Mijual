"use client";

import { useEffect, useState } from "react";

/**
 * The JS half of the reduced-motion floor.
 *
 * `app/shell.css` handles the CSS half: fades become cuts, `data-motion="tick"`
 * animations freeze, `data-motion="ambient"` layers hide. What CSS cannot do is
 * stop a *tick* — R2's countdown re-renders every second, and
 * `prefers-reduced-motion: reduce` requires "no animation, static value", which
 * means the interval must not run at all rather than merely not animate.
 *
 * Server-rendered as `false` and corrected on mount: the media query is a client
 * fact, and rendering the reduced form on the server would flash the wrong one
 * for every reader who has not asked for it.
 */
export const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const query = window.matchMedia(REDUCED_MOTION_QUERY);
    const sync = () => setReduced(query.matches);
    sync();
    query.addEventListener("change", sync);
    return () => query.removeEventListener("change", sync);
  }, []);

  return reduced;
}
