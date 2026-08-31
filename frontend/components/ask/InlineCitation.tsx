"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { dartUrl } from "@/lib/api";
import type { AskChip } from "@/lib/ask";
import { dartSourceLabel } from "./copy";
import styles from "./Ask.module.css";

/**
 * 인라인 인용 (R6-4) — the numbered chip and the quote it opens under itself.
 *
 * > 번호 칩: mono 10px, `--live` 잉크, 1px rgba(95,208,165,.4) 테두리, 같은 근거 =
 * > 같은 번호. 탭 → 제자리 인용 블록: 좌측 2px `--live`, verbatim quote +
 * > `DART 원문 {rcept_no} ↗`. 닫기 = 칩 재탭. **Citation 프리미티브의 인라인형 —
 * > 블록형과 스타일 공유.**
 *
 * ## The anatomy, after `P11.S1`
 *
 * 「블록형과 스타일 공유」 is now literal: this is `components/Citation.tsx`'s
 * **R10 anatomy** with R6-4's numbered chip in place of the `[근거]` one — a
 * **conditionally mounted, absolutely positioned popover**, fitted to the box
 * that would clip it by `fit()` in the ref callback that mounts it, closed by
 * the chip again, by a press outside, or by Esc (which gives the keyboard its
 * place back). Every element is phrasing content, because the chip sits inside
 * `<p class=prose>` and a `<div>` would be reparented out of the paragraph by
 * the HTML parser and break hydration — the same rule `Citation.tsx` states for
 * its own row.
 *
 * **What this replaced, and why.** Until `P11` the quote was an always-mounted
 * `display: grid` panel that animated its own height open and was held shut with
 * `inert`. A block-level box inside a paragraph's inline formatting context
 * splits that paragraph into anonymous block boxes, so **every chip forced a
 * line break**: a sentence resting on three 근거 rendered as `…입니다.[1]` ⏎
 * `[2]` ⏎ `[3]`, and `.sentence + .sentence`'s `.25em` gap — which assumes
 * inline siblings — was defeated with it. An overlay has no such effect on the
 * flow it hangs off, so the chips now sit side by side after the sentence's
 * period, which is what R16 §2.6 draws. `inert` retires with the panel it held
 * shut: an unmounted popover's DART link is unreachable by construction.
 *
 * **The ground is opaque, and that is a deliberate deviation from R16.** The
 * round signed the 인용 블록 as `--surface-inset` + a 2px `--live` left edge, and
 * that was an *in-flow* panel with nothing behind it. As an overlay it sits on
 * top of the prose, and `--surface-inset` is `rgba(255,255,255,.08)` — the
 * sentence would read straight through the reader's evidence. So the panel keeps
 * the 2px `--live` left edge and the 180px quote cap R16 signed, and takes the
 * opaque ground this product already uses for everything that floats over
 * something else: `#0e1a15` + 1px `--border-strong` + `--panel-glow`, the
 * widget's own surface and `Citation.module.css`'s. One property changed, and
 * only the one the overlay makes impossible to keep. (`P11.S1`; the CSS says it
 * again beside the rule.)
 *
 * **Closes, all three of them.** 닫기 = **칩 재탭** is R6-4's and survives
 * untouched; the press outside and Esc-with-focus-return come from R10 §6 with
 * the anatomy. The primitive's fourth close, its `×`, is **not** adopted: it
 * lives in a flex head beside the quote and is a 28/44px control, and R6-4 draws
 * no head and no second control on a 10px chip's block — inventing one inside a
 * 440px widget would be a design decision, not a port. Three closes is a whole
 * model, not half of one: every pointer close and every keyboard close is there.
 *
 * Two things that are still not the primitive's, both because the payload
 * differs:
 *
 * - the chip's text is the **number**, and the same 근거 keeps it for the whole
 *   answer (the server assigns it once, on first use);
 * - a chip with no quote is the **API-tier** citation (R3 rule), and **R14
 *   finding 10 re-cut what its block holds**: the `DART 원문 {rcept_no} ↗` link,
 *   alone (`.quoteLinkSolo`, so nothing sits above it to need a top margin). R3's
 *   explanatory sentence `API_TIER_KO` is retired — 원문 스팬 and 인용 핸들 are our
 *   contract's vocabulary, and the link's existence already is what the sentence
 *   said. It is still a citation, not a missing one — unlike the primitive's third
 *   state, which renders no chip at all. Closes P7 Q7①.
 *
 * `span` is carried on the payload and deliberately **not rendered**: an offset
 * is internal, exactly as the primitive records.
 *
 * ## R16 §2.6 — the same chip, in two more **places**
 *
 * 「**변경 없음** … 새로운 것은 칩이 붙는 **자리**뿐이다: 프로즈 + 데이터 행 값 +
 * 계산 입력.」 So the chip is unchanged and one prop says which place it is in,
 * because the two places anchor the popover differently:
 *
 * - `"prose"` (default) — the wrap is `position: relative; display: inline-block`
 *   (`Citation.module.css` `.wrap`) and the popover opens under the chip, 380px
 *   wide (340 at ≤767), slid back inside whatever would clip it;
 * - `"row"` — the fixed **셋째 칸** of a 데이터 행 / 계산 입력 (§2.3), whose width
 *   *is* the chip's and which never scrolls away with the value. The wrap stays
 *   `display: contents` so the chip is a grid item of the row itself, and the
 *   popover anchors to `.row` (`Blocks.module.css`, which takes `position:
 *   relative` for it) and opens **under the row, across the block** — R16 §2.6's
 *   「행 아래, 블록 전폭」, and the row-scale reading of R6 §Mobile's 「인용 블록
 *   전폭」. The collapse that made the old placement necessary — a quote's
 *   max-content sizing the `auto` track and squeezing the value column to zero —
 *   is now **structurally impossible**: an absolutely positioned box sizes no
 *   grid track.
 */
export function InlineCitation({
  chip,
  place = "prose",
}: {
  chip: AskChip;
  place?: "prose" | "row";
}) {
  const panelId = useId();
  const [open, setOpen] = useState(false);
  const wrap = useRef<HTMLSpanElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const pop = useRef<HTMLSpanElement | null>(null);

  // The popover is drawn where the record puts it and only **slid back inside**
  // when the surface would clip it. Nothing approved moves: width, colour,
  // border, padding and the 6px drop are the record's, and only the offsets
  // change — far enough to make the quote readable, which is the whole point of
  // the affordance.
  //
  // Two directions, because this surface clips in both. Horizontally, a 380px
  // popover hung off a chip that ends a line runs past the viewport edge (the
  // primitive measured the same thing at 390px); the row's popover is the block's
  // own width and needs no clamp at all. Vertically, the widget thread is a
  // 620px `overflow-y: auto` box, so a chip in the **last** answer opens its
  // evidence below the fold — the popover flips above the chip when there is
  // more room there. `nearestClip` is what makes that a scroll-container
  // question rather than a viewport one.
  const fit = useCallback(
    (panel: HTMLSpanElement | null) => {
      if (!panel) return;
      panel.style.transform = "";
      panel.removeAttribute("data-flip");
      const gutter = 8;

      const clip = nearestClip(panel);

      if (place === "prose") {
        const box = panel.getBoundingClientRect();
        let dx = 0;
        if (box.left < clip.left + gutter) dx = clip.left + gutter - box.left;
        else if (box.right > clip.right - gutter) dx = clip.right - gutter - box.right;
        if (dx) panel.style.transform = `translateX(${Math.round(dx)}px)`;
      }

      // `offsetParent` is the element the popover is positioned against — the
      // wrap in prose, the row in a data block.
      const anchor = (panel.offsetParent as HTMLElement | null)?.getBoundingClientRect();
      if (!anchor) return;
      const box = panel.getBoundingClientRect();
      const below = clip.bottom - anchor.bottom;
      const above = anchor.top - clip.top;
      if (box.bottom > clip.bottom - gutter && above > below) panel.setAttribute("data-flip", "up");
    },
    [place],
  );

  // A ref callback rather than a layout effect: it runs in the same commit that
  // mounts the popover, so the fitted position is the first one painted.
  const holdPop = useCallback(
    (node: HTMLSpanElement | null) => {
      pop.current = node;
      fit(node);
    },
    [fit],
  );

  // R6-4's 칩 재탭 is the button's own `onClick`. These are R10 §6's other two,
  // document-level and therefore only listened for while the popover is open —
  // an answer carries one of these per 근거.
  useEffect(() => {
    if (!open) return;
    const away = (event: MouseEvent) => {
      if (wrap.current && !wrap.current.contains(event.target as Node)) setOpen(false);
    };
    const key = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setOpen(false);
      // Esc is a keyboard close, so the keyboard gets its place back. A pointer
      // close moves nothing, because nothing was taken.
      trigger.current?.focus();
    };
    const refit = () => fit(pop.current);
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", key);
    window.addEventListener("resize", refit);
    return () => {
      document.removeEventListener("mousedown", away);
      document.removeEventListener("keydown", key);
      window.removeEventListener("resize", refit);
    };
  }, [fit, open]);

  return (
    <span ref={wrap} className={place === "row" ? styles.citationRow : styles.citationWrap}>
      <button
        ref={trigger}
        type="button"
        className={styles.chip}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((was) => !was)}
      >
        {chip.number}
      </button>

      {open ? (
        <span ref={holdPop} id={panelId} className={styles.quotePop}>
          {chip.quote === undefined ? null : (
            // The filing's own words: never paraphrased, corrected or
            // re-punctuated, so the whitespace it was filed with survives too.
            <span className={styles.quote}>{chip.quote}</span>
          )}
          <a
            className={
              chip.quote === undefined
                ? `${styles.quoteLink} ${styles.quoteLinkSolo}`
                : styles.quoteLink
            }
            href={dartUrl(chip.rcept_no)}
            target="_blank"
            rel="noopener noreferrer"
          >
            {dartSourceLabel(chip.rcept_no)}
          </a>
        </span>
      ) : null}
    </span>
  );
}

/** The box that would actually clip this popover: every scrolling or hidden
 * ancestor, intersected with the viewport. On `/ask` there is none, so this is
 * the viewport and the clamp is the primitive's own; inside the widget it is the
 * thread (`.thread`, `overflow-y: auto` inside 620px), which is why the evidence
 * stays inside the panel the reader opened rather than hanging off its edge or
 * being cut by it. */
function nearestClip(node: HTMLElement): {
  top: number;
  bottom: number;
  left: number;
  right: number;
} {
  let top = 0;
  let bottom = window.innerHeight;
  let left = 0;
  let right = window.innerWidth;
  let walk = node.parentElement;
  while (walk) {
    const style = getComputedStyle(walk);
    if (scrolls(style.overflowY) || scrolls(style.overflowX)) {
      const box = walk.getBoundingClientRect();
      top = Math.max(top, box.top);
      bottom = Math.min(bottom, box.bottom);
      left = Math.max(left, box.left);
      right = Math.min(right, box.right);
    }
    walk = walk.parentElement;
  }
  return { top, bottom, left, right };
}

function scrolls(overflow: string): boolean {
  return overflow === "auto" || overflow === "scroll" || overflow === "hidden";
}
