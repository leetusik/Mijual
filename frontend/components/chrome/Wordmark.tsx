import { BRAND_ALT_KO, WORDMARK_NATURAL, WORDMARK_WHITE } from "./copy";

/**
 * The white 주주의관제탑 wordmark, rendered at a constrained height.
 *
 * R2 §Page shell puts a white wordmark in both chrome surfaces at two sizes —
 * nav **h 19px**, footer **h 17px** — and R2.1 re-cut the chrome cards "on
 * cosmos", which is why the white variant is what this dark chrome uses. The
 * placement is R2's; the artwork is P10's (the ring mark is retired).
 *
 * Two rules still govern the file, and only one of them has the same reason it
 * used to:
 *
 * - **Never re-encoded.** This binary is *not* a design-project export copied in
 *   byte-for-byte — that was true of the retired `mijual-*` set. It is a
 *   repo-generated derivative of the operator's delivered PNG (class C in
 *   `public/assets/README.md`), and the README proves it by **pixel signature**,
 *   not by file hash. Re-compressing it therefore breaks the one proof that
 *   links it to the operator's file. So this stays a plain `<img>`: `next/image`
 *   would serve a re-compressed derivative, which is exactly what that proof
 *   forbids.
 * - **Height-constrained rendering only.** The intrinsic 1213×319 travels as the
 *   `width`/`height` attributes so the browser knows the ratio and reserves the
 *   right box before the PNG arrives (no layout shift in a 52px bar); CSS then
 *   sets the height and lets the width follow.
 *
 * One thing the new artwork changes that the numbers do not show: the mark is
 * 3.80:1 where the ring was 6.29:1, and only its **bottom half** is the Korean
 * wordmark (sparkle cluster above, 22-row gap between — see the README's
 * geometry table). At h19 that is a 72×19 box carrying a 9.7px glyph band, where
 * the ring put 14.4px of ink into the same 19px. The heights below are the
 * signed ones and stay signed; whether they are still the right ones is an open
 * question for the operator, filed in the P10 notebook.
 */
export type WordmarkProps = {
  /** 19 in the nav, 17 in the footer — R2's two numbers. */
  height: 19 | 17;
  className?: string;
};

export function Wordmark({ height, className }: WordmarkProps) {
  return (
    <img
      src={WORDMARK_WHITE}
      alt={BRAND_ALT_KO}
      width={WORDMARK_NATURAL.width}
      height={WORDMARK_NATURAL.height}
      className={className}
      style={{ height: `${height}px`, width: "auto" }}
    />
  );
}
