/**
 * 계정 아이디콘 — the deterministic mark R8 puts in front of the account email.
 *
 * The algorithm is the design record's, transcribed rather than chosen
 * (`docs/reference/design/rounds/08-foundations-chrome/output/Identicon.prompt.md`,
 * and build-prompt §5):
 *
 * > 1. `key = seed.trim().toLowerCase()`
 * > 2. `h = fnv1a32(key)` → `hue = [--r1, --r2, --r3, --live][h % 4]`
 * > 3. `bits = fnv1a32(key + ':cells')`
 * > 4. For each row `r` in 0..4, take bits `r*3 + 0..2` as the left half; row =
 * >    `[b0, b1, b2, b1, b0]` (column 2 is the mirror axis).
 * >
 * > `fnv1a32`: `h = 0x811c9dc5`; per char `h ^= code; h = (h * 0x01000193) >>> 0`
 * > (use `Math.imul`).
 *
 * It lives in `lib/` rather than inside the component for the reason every other
 * derivation in this app does: it is a **pure function of one string**, so it is
 * the testable half of the mark, and `components/Identicon.tsx` only paints what
 * it returns. The record's own reason for pinning the algorithm is that "the mark
 * must match across web and any later surface" — a re-derivation elsewhere has to
 * agree with this file byte for byte.
 *
 * The seed is a **data** decision the round left to the apply slice ("시드:
 * 이메일 문자열 또는 서버가 주는 per-account 시드 — 둘 중 무엇이든 이 함수의
 * 입력일 뿐"); today's caller passes the account email. Nothing here hashes for
 * secrecy — FNV-1a is a *dispersal* function, and the mark is decoration for
 * recognition, never data.
 */

/** The four **data** hues, in the record's order. `--alert` (red = 소멸/기한) and
 * `--brand` (the mark carries no data colour) are excluded by the round. */
export const IDENTICON_HUES = ["--r1", "--r2", "--r3", "--live"] as const;

export type IdenticonHue = (typeof IDENTICON_HUES)[number];

/** The record's own sizes — 20 (nav frame) · 28 (mobile sheet) · 40 (account
 * surface). Each divides by 5, so every cell lands on whole pixels. */
export const IDENTICON_SIZES = [20, 28, 40] as const;

export type IdenticonSize = (typeof IDENTICON_SIZES)[number];

/** The grid is 5×5 and column 2 is the mirror axis, so a row is decided by three
 * bits — 15 of the 32 the second hash produces. */
const GRID = 5;
const HALF = 3;

function fnv1a32(input: string): number {
  let hash = 0x811c9dc5;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash >>> 0;
}

export type IdenticonPattern = {
  /** The token name (`--r1` …), not a colour: the cosmos scope remaps it. */
  hue: IdenticonHue;
  /** Five rows of five, each vertically mirrored about column 2. */
  cells: boolean[][];
};

export function identicon(seed: string): IdenticonPattern {
  const key = seed.trim().toLowerCase();
  const hue = IDENTICON_HUES[fnv1a32(key) % IDENTICON_HUES.length];
  const bits = fnv1a32(`${key}:cells`);

  const cells: boolean[][] = [];
  for (let row = 0; row < GRID; row += 1) {
    const half: boolean[] = [];
    for (let column = 0; column < HALF; column += 1) {
      half.push(((bits >>> (row * HALF + column)) & 1) === 1);
    }
    cells.push([half[0], half[1], half[2], half[1], half[0]]);
  }
  return { hue, cells };
}
