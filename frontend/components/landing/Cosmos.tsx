import type { CSSProperties } from "react";
import styles from "./Cosmos.module.css";

/**
 * The cosmos backdrop (R2.1) — one continuous full-page starfield, the root-level
 * green glows, and the shooting stars.
 *
 * > The landing is a **dark cosmos page**: body `#0a1310`; ONE continuous
 * > full-page starfield behind all sections (≈240 stars desktop / 160 mobile,
 * > twinkle 2.5–6.5s, 80s drift), root-level radial green glows (strong at ~12%
 * > height, faint echo at the bottom), shooting stars staggered down the whole
 * > page (~5 desktop / 3 mobile, 9–18s cycles).
 *
 * It fills the `.backdrop` slot `app/shell.css` reserves: `position: fixed;
 * inset: 0; z-index: -1`, no pointer events. That fixed layer is what makes the
 * starfield *one* field rather than a per-section decoration — which is why the
 * shell, the chrome frame and this file all keep `transform`, `filter` and
 * `contain` off every ancestor (`P5.S10` note 7, `P5.S11` note 8): any of them
 * would turn `position: fixed` into a containing-block position.
 *
 * ## The stars are generated once, deterministically, and never with `Math.random`
 *
 * A random field would differ between the server render and the client's
 * hydration, which is a hydration mismatch on every page load. `mulberry32` with
 * a fixed seed is the whole fix: the same 240 stars, in the same order, in every
 * process — module scope, computed once per process rather than once per render.
 *
 * ## Reduced motion
 *
 * The convention `app/shell.css` fixes: `data-motion="tick"` **freezes** (the
 * 80s drift), `data-motion="ambient"` **hides** (the shooting stars). The
 * per-star twinkle and the orbiter are frozen by this file's own
 * `prefers-reduced-motion` block, because the shell's attribute rule reaches an
 * element and its pseudo-elements, not 240 children.
 */

/** R2: ≈240 stars desktop / 160 mobile. The field is rendered once and the tail
 * hides at ≤480px, so both counts come out of one deterministic list. */
const STAR_COUNT = 240;
export const MOBILE_STAR_COUNT = 160;

/** R2: ~5 shooting stars desktop / 3 mobile, staggered down the whole page. */
const SHOOTER_COUNT = 5;
export const MOBILE_SHOOTER_COUNT = 3;

/** A small, fast, seedable PRNG. Any deterministic source would do; what matters
 * is that it is not `Math.random()`. */
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

type Star = {
  x: number;
  y: number;
  size: number;
  opacity: number;
  duration: number;
  delay: number;
};

type Shooter = {
  x: number;
  y: number;
  length: number;
  duration: number;
  delay: number;
};

const random = mulberry32(0x6d696a75); // "miju" — a constant, and only a constant

const STARS: Star[] = Array.from({ length: STAR_COUNT }, () => ({
  x: round(random() * 100),
  y: round(random() * 100),
  size: round(0.8 + random() * 1.4),
  opacity: round(0.2 + random() * 0.65),
  // R2: twinkle 2.5–6.5s.
  duration: round(2.5 + random() * 4),
  delay: round(random() * 6.5),
}));

const SHOOTERS: Shooter[] = Array.from({ length: SHOOTER_COUNT }, (_, index) => ({
  x: round(random() * 70),
  // Staggered down the whole page, one per horizontal band.
  y: round((index * 100) / SHOOTER_COUNT + random() * 12),
  length: round(90 + random() * 90),
  // R2: 9–18s cycles.
  duration: round(9 + random() * 9),
  delay: round(random() * 14),
}));

function round(value: number): number {
  return Math.round(value * 1000) / 1000;
}

export function Cosmos() {
  return (
    <div className="backdrop" aria-hidden="true">
      <div className={styles.glow} />

      <div className={styles.field} data-motion="tick">
        {STARS.map((star, index) => (
          <span
            key={index}
            className={styles.star}
            style={
              {
                left: `${star.x}%`,
                top: `${star.y}%`,
                width: `${star.size}px`,
                height: `${star.size}px`,
                animationDuration: `${star.duration}s`,
                animationDelay: `${star.delay}s`,
                "--star-opacity": star.opacity,
              } as CSSProperties
            }
          />
        ))}
      </div>

      <div className={styles.shooters} data-motion="ambient">
        {SHOOTERS.map((shooter, index) => (
          <span
            key={index}
            className={styles.shooter}
            style={{ left: `${shooter.x}%`, top: `${shooter.y}%` }}
          >
            <span
              className={styles.streak}
              style={{
                width: `${shooter.length}px`,
                animationDuration: `${shooter.duration}s`,
                animationDelay: `${shooter.delay}s`,
              }}
            />
          </span>
        ))}
      </div>
    </div>
  );
}
