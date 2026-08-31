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
 * the bottom (ink rows **195–370** of 371, flush to the bottom), and **30 empty
 * rows** separate them. So box-centring the image sits the *legible* part below
 * whatever it stands next to, and a height-constrained placement gets a mark
 * whose readable half is 47.44% of the declared height.
 *
 * **nav h27 / footer h24** are R17's, unchanged: at h27 the glyph band is
 * 12.81px against the 13.5px link type (0.95×, where R2's signed h19 gave 0.72×
 * and the retired ring gave 1.07×), and h27 is the ceiling the 52px bar allows.
 *
 * **The offset is text-referenced, and that supersedes R17.** R17 derived
 * `INK_OFFSET 0.2628 × H` from the *image alone* — the band's geometric centre
 * is at 76.28% of box height — and so aligned the band to the optical centre of
 * **the row**, never to the type beside it. The operator rejected that at the
 * P10 round-3 acceptance gate («로고 글자가 옆 nav 링크 글자보다 아래로 내려가
 * 있다 … 텍스트 기준 수평 정렬로 바꿀 것»), and `P10.F3` replaced the law with a
 * measured relationship between two rendered ink boxes:
 *
 * > **the mark's glyph band sits on the same baseline as the Hangul standing
 * > next to it** — band ink bottom on the neighbour's Hangul ink bottom.
 *
 * For Hangul beside Hangul that *is* the shared baseline the eye reads: the
 * *alphabetic* baseline is not it, because the rendered type carries real ink
 * below it (measured: 1.05px at 400 / 1.16px at 600 for 13.5px Noto Sans KR,
 * 1.02px at 12px), so aligning to the alphabetic baseline paints the mark ~1px
 * **high**. The rejected alternative the operator also named, a shared optical
 * *centre* line, is not adopted: the band (12.81px at h27) is taller than the
 * label ink (11.73–12.32px), so that law lands between 7.38 and 7.69 depending
 * on which label you pick — it cannot decide, and against the pure-Hangul labels
 * it reproduces the very placement the operator rejected.
 *
 * Measured in the running product (dev and a production build, 1280 and 390,
 * two independent methods — canvas `TextMetrics` on the element's own computed
 * font vs. an 8× pixel scan — agreeing to 0.04px):
 *
 * | surface | neighbour | its Hangul ink bottom | required offset | ships |
 * |---|---|---|---|---|
 * | nav h27 | `.link` 보유 종목 400 | 31.083 | 7.917 | **8** |
 * | nav h27 | `.link` 보유 종목 600 | 31.189 | 7.811 | **8** |
 * | nav h27 | `.link` AI 질문 400/600 | 30.947 / 31.091 | 8.053 / 7.909 | **8** |
 * | footer h24 | `.source` 12px | row-relative | 6.281 | **6** |
 *
 * Every label and weight rounds to the same integer, which is why one number
 * per height still serves. Whole pixels, per R17's own rounding rule (the PNG
 * resamples to a fractional height anyway). Rendered at h27 that puts the band
 * bottom at **31.00px** against the labels' **31.08–31.19px** — one line — with
 * the box top at **4.00px** under the bar's top edge. The footer's number does
 * not move: at h24 the band bottom was already within **0.28px** of `.source`'s
 * Hangul bottom, so the same law re-derives the shipped `-6`.
 *
 * **The component carries the offset itself**, deliberately: it is not a value a
 * caller can be trusted to remember, and a call site that forgot it would render
 * a mark that is merely slightly low rather than visibly wrong.
 *
 * There is no viewport branch — h27 at 390px too (R17 §1). At 390 the bar's
 * links are gone and the mark's neighbour is the 메뉴 button, whose Hangul ink
 * bottom is 30.875: the same `-8` lands the band at 31.00, 0.13px off it (it was
 * 1.13px off under R17's law), so one number still serves both viewports.
 */
export type WordmarkProps = {
  /** 27 in the nav, 24 in the footer — R17's two numbers (R2's 19/17 retired). */
  height: 27 | 24;
  className?: string;
};

/** Text-referenced, per height: the offset that puts the mark's glyph-band ink
 * bottom on the neighbouring Hangul's ink bottom, rounded to whole pixels
 * (`P10.F3`, superseding R17's image-only `0.2628 × H`). */
const INK_OFFSET_PX: Record<WordmarkProps["height"], number> = { 27: 8, 24: 6 };

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
