import { BRAND_ALT_KO, RING_WORDMARK_NATURAL, RING_WORDMARK_WHITE } from "./copy";

/**
 * The white ring wordmark, rendered at a constrained height.
 *
 * R2 §Page shell puts it in both chrome surfaces at two sizes — nav **h 19px**,
 * footer **h 17px** — and R2.1 re-cut the chrome cards "on cosmos with the white
 * ring wordmark", which is why the white pair is what this dark chrome uses.
 *
 * Two rules the design record imposes on the file itself:
 *
 * - **Never re-encoded.** The five binaries are the design project's own output,
 *   copied in byte-for-byte and checksummed (`public/assets/README.md`);
 *   replacing one means a new export, never a local edit. So this is a plain
 *   `<img>`: `next/image` would serve a re-compressed derivative of a delivered
 *   asset, which is exactly the edit that rule forbids.
 * - **Height-constrained rendering only.** The intrinsic 2178×346 travels as the
 *   `width`/`height` attributes so the browser knows the ratio and reserves the
 *   right box before the PNG arrives (no layout shift in a 52px bar); CSS then
 *   sets the height and lets the width follow.
 */
export type WordmarkProps = {
  /** 19 in the nav, 17 in the footer — R2's two numbers. */
  height: 19 | 17;
  className?: string;
};

export function Wordmark({ height, className }: WordmarkProps) {
  return (
    <img
      src={RING_WORDMARK_WHITE}
      alt={BRAND_ALT_KO}
      width={RING_WORDMARK_NATURAL.width}
      height={RING_WORDMARK_NATURAL.height}
      className={className}
      style={{ height: `${height}px`, width: "auto" }}
    />
  );
}
