import { BRAND_ALT_KO, WORDMARK_NATURAL, WORDMARK_WHITE } from "./copy";

/**
 * The white 주주의관제탑 wordmark, rendered at a constrained height.
 *
 * R2 §Page shell put a white wordmark in both chrome surfaces, and R2.1 re-cut
 * the chrome cards "on cosmos", which is why the white variant is what this dark
 * chrome uses. **R17 supersedes R2's two heights and its box-centred placement**
 * (`docs/reference/design/rounds/17-brand-mark-launcher/`, signed 2026-08-31).
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
 * - **Height-constrained rendering only.** The intrinsic 1247×371 (3.3612:1)
 *   travels as the `width`/`height` attributes so the browser knows the ratio and
 *   reserves the right box before the PNG arrives (no layout shift in a 52px
 *   bar); CSS then sets the height and lets the width follow. **R18 re-derived
 *   the file from 1292×371 to 1247×371** by cutting the quarter-em space between
 *   「의」 and 「관」; only the width changed, so the rendered mark is 90.75px at
 *   h27 and 80.67px at h24 (was 94.03 / 83.58). No layout consequence — `.brand`
 *   is `flex:none` with no fixed width.
 *
 * ## The two heights, and the offset that comes with them
 *
 * The box is **not** filled evenly: the sparkle cluster sits alone in the top
 * (222×165, flush to the box's top and right), the Korean glyph band occupies
 * the bottom (1087×176, flush to the bottom), and **30 empty rows** separate
 * them. So box-centring the image sits the *legible* part below the optical
 * centre of whatever row it is in, and a height-constrained placement gets a
 * mark whose readable half is 47.44% of the declared height.
 *
 * R17 answers both halves of that (result.md §Q1/§Q2, `r17-mark.css` is the
 * geometry canon):
 *
 * - **nav h27 / footer h24** — at h27 the glyph band is 12.81px against the
 *   13.5px link type (0.95×, where R2's signed h19 gave 0.72× and the retired
 *   ring gave 1.07×). h27 is also the ceiling the 52px bar allows under ink
 *   alignment: h30 leaves only 3.0px above the box and the sparkle touches the
 *   hairline.
 * - **ink alignment, not box centring** — the band's geometric centre is at
 *   76.28% of box height, i.e. `0.2628 × H` below the box centre, so the image
 *   is lifted by that much, rounded to whole pixels: `translateY(-7px)` at h27,
 *   `-6px` at h24. Rendered, that puts the h27 band centre at **26.10px** in a
 *   52px bar whose optical centre is 26px.
 *
 * **The component carries the offset itself**, deliberately: it is not a value a
 * caller can be trusted to remember, and a call site that forgot it would render
 * a mark that is merely slightly low rather than visibly wrong.
 *
 * There is no viewport branch — h27 at 390px too (R17 §1).
 */
export type WordmarkProps = {
  /** 27 in the nav, 24 in the footer — R17's two numbers (R2's 19/17 retired). */
  height: 27 | 24;
  className?: string;
};

/** `0.2628 × H` rounded to whole pixels — R17's `INK_OFFSET`, per height. */
const INK_OFFSET_PX: Record<WordmarkProps["height"], number> = { 27: 7, 24: 6 };

export function Wordmark({ height, className }: WordmarkProps) {
  return (
    <img
      src={WORDMARK_WHITE}
      alt={BRAND_ALT_KO}
      width={WORDMARK_NATURAL.width}
      height={WORDMARK_NATURAL.height}
      className={className}
      style={{
        height: `${height}px`,
        width: "auto",
        transform: `translateY(-${INK_OFFSET_PX[height]}px)`,
      }}
    />
  );
}
