"use client";

import { useEffect } from "react";

import { REDUCED_MOTION_QUERY } from "@/lib/motion";

/**
 * Hands the 240 star twinkles from CSS to the Web Animations API on mount, at
 * the phase they had reached (`P4.F11`). It renders nothing and it changes
 * nothing about the picture: same values, same easing, same per-star duration
 * and delay, same first paint.
 *
 * ## Why the twinkle cannot stay a CSS animation
 *
 * `P4.F7` proved these animations already run on the compositor — blocking the
 * renderer's main thread for 2.5s does not stop them. What costs is that the
 * landing produces a main-thread frame on EVERY display frame, and Blink
 * re-resolves every running animation's style inside each one. Two things force
 * those frames; `P4.F11` removes both. The Hero orbiter's uncompositable
 * `offset-distance` is one (`Hero.module.css`). The other is these twinkles
 * themselves: 240 CSS animations with all-distinct durations end an iteration
 * ~56 times a second, and **React registers a delegated `animationiteration`
 * listener on the hydration root**, so Blink must create and dispatch every one
 * of those events — one main-thread frame each. A WAAPI animation fires no CSS
 * animation events at all, so the events stop existing.
 *
 * ## Two mechanisms were measured; this is the one that works
 *
 * Moving the field into a **declarative shadow tree** does NOT help, and the
 * measurement is worth keeping because the reasoning sounds right: CSS
 * animation events are not composed, so they never reach React's listener —
 * but Blink gates *creating* the event on a **document-level** listener flag,
 * which any listener in the document sets, shadow boundary or not. Measured
 * side by side over 8s idle windows at 1280 (240 stars, one document-level
 * `animationiteration` listener): light DOM **467** `UpdateLayoutTree` / 376
 * dispatches, shadow tree **469** / 370 (the events fired *inside* the shadow
 * tree instead of reaching the document — same cost), no listener at all
 * **131** / 0, this WAAPI handover **134** / 0.
 *
 * ## What the handover must not break
 *
 * - **First paint.** The CSS animation still paints and animates the field from
 *   the server-rendered HTML; this only takes over afterwards. That is the whole
 *   reason a `<canvas>` field was declined — it cannot paint before hydration.
 * - **Phase.** Each WAAPI animation starts at its CSS animation's own
 *   `currentTime`, so no star jumps at the handover.
 * - **Reduced motion.** Under `prefers-reduced-motion: reduce` nothing is handed
 *   over and `Cosmos.module.css`'s own freeze stays in force; the media query is
 *   watched, so flipping the preference either way still freezes and unfreezes.
 * - **The `<=480px` field cut.** Only rendered stars are handed over. A CSS
 *   animation on a `display: none` element does not run; a WAAPI one does, and
 *   Chrome cannot composite it — handing over the hidden 80 put the forced 60Hz
 *   frame straight back (480 `UpdateLayoutTree` per 8s at 390 against 8).
 * - **Anything unexpected.** Every failure path leaves the CSS animation exactly
 *   as it is: a browser without `Element.animate`, without pseudo-element
 *   targets, or a star whose computed duration cannot be read.
 */

/** The literals from `@keyframes twinkle`. `ease-in-out` is per SEGMENT in CSS,
 *  so it belongs on the keyframes and never on the effect's own `easing`. */
const TWINKLE: Keyframe[] = [
  { opacity: 1, easing: "ease-in-out" },
  { opacity: 0.28, easing: "ease-in-out" },
  { opacity: 1 },
];

export function StarTwinkle() {
  useEffect(() => {
    const field = document.querySelector<HTMLElement>("[data-starfield]");
    if (!field || typeof field.animate !== "function") return;

    /** Only the stars that are actually RENDERED are handed over. The `<=480px`
     *  rule hides the last 80, and a CSS animation on a `display: none` element
     *  does not run at all — but a WAAPI animation on one does, and Chrome
     *  cannot composite it, which puts the forced 60Hz main-thread frame
     *  straight back (measured: 480 `UpdateLayoutTree` per 8s at 390 with the
     *  hidden 80 handed over, 8 without them). */
    const handed = new Map<HTMLElement, Animation>();
    let broken = false;

    const clear = () => {
      handed.forEach((animation) => animation.cancel());
      handed.clear();
      delete field.dataset.twinkle;
    };

    const sync = () => {
      if (broken) return;
      if (window.matchMedia(REDUCED_MOTION_QUERY).matches) {
        // The stylesheet's own freeze is the reduced-motion behaviour; hand
        // everything back so flipping the preference still stops the twinkle.
        clear();
        return;
      }
      for (const star of Array.from(field.children) as HTMLElement[]) {
        const shown = window.getComputedStyle(star).display !== "none";
        const already = handed.get(star);
        if (!shown) {
          if (already) {
            already.cancel();
            handed.delete(star);
          }
          continue;
        }
        if (already) continue;
        const paint = window.getComputedStyle(star, "::before");
        const duration = Number.parseFloat(paint.animationDuration) * 1000;
        const delay = Number.parseFloat(paint.animationDelay) * 1000;
        if (!Number.isFinite(duration) || duration <= 0 || !Number.isFinite(delay)) {
          broken = true;
          clear();
          return;
        }
        // Read the phase BEFORE creating the replacement: once both exist,
        // `getAnimations()` returns them in composite order and [0] would be a
        // promise about sort order rather than about which animation this is.
        // A star that first appears on a resize has no CSS animation left to
        // read (the attribute below has already switched them off) and starts
        // at zero, exactly as a re-applied CSS animation would.
        const reached = star.getAnimations({ subtree: true })[0]?.currentTime;
        let animation: Animation;
        try {
          animation = star.animate(TWINKLE, {
            duration,
            delay,
            iterations: Number.POSITIVE_INFINITY,
            easing: "linear",
            pseudoElement: "::before",
          });
        } catch {
          // No pseudo-element target in this engine: keep the CSS twinkle.
          broken = true;
          clear();
          return;
        }
        if (reached != null) animation.currentTime = reached;
        handed.set(star, animation);
      }
      // Only now: while both exist the WAAPI animation already wins the cascade,
      // so switching the CSS one off cannot show a frame of the wrong opacity.
      if (handed.size) field.dataset.twinkle = "waapi";
      else delete field.dataset.twinkle;
    };

    const query = window.matchMedia(REDUCED_MOTION_QUERY);
    // A resize can cross the `<=480px` field cut in either direction; re-syncing
    // adds and cancels only what changed, so every other star keeps its phase.
    let pending = 0;
    const onResize = () => {
      window.clearTimeout(pending);
      pending = window.setTimeout(sync, 250);
    };
    sync();
    query.addEventListener("change", sync);
    window.addEventListener("resize", onResize);
    return () => {
      window.clearTimeout(pending);
      query.removeEventListener("change", sync);
      window.removeEventListener("resize", onResize);
      clear();
    };
  }, []);

  return null;
}
