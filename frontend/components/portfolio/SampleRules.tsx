import { SAMPLE_REMOVED_ATTR } from "@/components/chrome/PreHydration";
import type { Portfolio as PortfolioPayload } from "@/lib/types";

/**
 * 샘플 모드's half of the **pre-hydration mirror**'s third use (`P12.F10`) — the
 * rules that hide the rows this browser removed, before they can paint.
 *
 * ## The shift this closes
 *
 * The anonymous 보유 종목 surface renders **the served composition**
 * (`GET /portfolio/sample`, chosen per request since `P4.F1`) and the browser
 * keeps only what the reader *did* to it (`lib/sample.ts` § v2). `useSample()` is
 * a `useSyncExternalStore` whose **server snapshot is `null`**, which is the only
 * value that lets the client's first render match the server's — so every served
 * row hydrates, and the first post-hydration render then drops the rows whose
 * issuer this browser removed. A reader who had deleted one issuer therefore
 * watched the list re-flow after paint: `P12.F3` measured it at 1280 with
 * `removed: ["00102618"]` — **CLS 0.05206**.
 *
 * ## The mechanism, and why it is CSS
 *
 * The server may not be told which issuers this browser dropped
 * (`security.md`: 「anonymous state never reaches the server」, and `P12.F3`
 * rejected a cookie on exactly that rule), and React may not render a different
 * list than the server did. What is left is the seam: the `<head>` script stamps
 * the removals on `<html>` as `data-mj-sample-removed="<code> <code> …"` before
 * anything paints, every removable row carries `data-corp`, and **this** file
 * emits one static rule per **served** code —
 * `html[data-mj-sample-removed~="c"] [data-corp="c"] { display: none }` — so the
 * hidden row has no box from the first frame and the post-hydration unmount
 * removes an element that never had one. `~=` is what makes a static per-code
 * rule work against a list the server cannot know.
 *
 * Three rule shapes, all generated from the composition this render serves:
 *
 * 1. **the row** — one per served code, above;
 * 2. **the container**, per D-day section and for the block as a whole: a section
 *    whose every row is removed is *unmounted* by `Deadlines` (its title with it),
 *    so it must be hidden too — expressed as one rule whose `html` selector
 *    carries every code of that section at once;
 * 3. **the first row's rule**: `.row:first-child` drops its `border-top`, and
 *    `:first-child` counts a `display: none` element. So for each row after the
 *    first, "everything before me is removed **and** I am not" — an `html[…][…]`
 *    chain with a `:not()` — restores the 1 px the unmount would have taken.
 *
 * ## What it deliberately does not do
 *
 * A sample whose **holdings are all removed** swaps the whole list panel for the
 * 「없습니다」 empty panel, which is a different element rather than a hidden one;
 * that swap is left as it is today (measured and recorded in `P12.F10`'s
 * `result.md`). Hiding the list would only trade one shift for another, and
 * rendering both panels would be exactly the hydration mismatch this seam exists
 * to avoid.
 *
 * Codes are validated as digit strings before they enter a selector — a served
 * code that is not one is left un-ruled (its row behaves as it does today) rather
 * than interpolated.
 */
export function SampleRemovedRules({ payload }: { payload: PortfolioPayload }) {
  const css = sampleRemovedCss(payload);
  if (css === "") return null;
  // Rendered **before** the surface, so the parser has the rules in hand before
  // it reaches the rows they hide. `<style>` is `display: none` per the UA sheet,
  // so it is not a flex item of `.page` and takes no gap.
  return <style dangerouslySetInnerHTML={{ __html: css }} />;
}

/** A served row's issuer, if it can safely be one word of a CSS attribute match. */
function codesOf(rows: ReadonlyArray<{ corp_code: string }>): string[] {
  return rows.map((row) => row.corp_code).filter((code) => /^[0-9]+$/.test(code));
}

function unique(codes: readonly string[]): string[] {
  return [...new Set(codes)];
}

/** `html` + one attribute match per code: "this browser removed all of these". */
function removed(codes: readonly string[]): string {
  return `html${codes.map((code) => `[${SAMPLE_REMOVED_ATTR}~="${code}"]`).join("")}`;
}

export function sampleRemovedCss(payload: PortfolioPayload): string {
  const sections = [
    { group: "upcoming", codes: codesOf(payload.upcoming) },
    { group: "past", codes: codesOf(payload.past) },
  ];
  const rules: string[] = [];

  for (const code of unique([...codesOf(payload.holdings), ...sections.flatMap((s) => s.codes)])) {
    rules.push(`${removed([code])} [data-corp="${code}"]{display:none}`);
  }

  for (const { group, codes } of sections) {
    if (codes.length === 0) continue;
    rules.push(`${removed(unique(codes))} [data-corp-group="${group}"]{display:none}`);
    codes.forEach((code, index) => {
      const before = unique(codes.slice(0, index));
      // The first row needs no rule, and a repeated issuer's later row can never
      // be the first visible one (its earlier row would have to be both removed
      // and not removed), so that rule would be dead weight.
      if (before.length === 0 || before.includes(code)) return;
      rules.push(
        `${removed(before)}:not([${SAMPLE_REMOVED_ATTR}~="${code}"])` +
          ` [data-corp-group="${group}"] [data-corp="${code}"]{border-top:0}`,
      );
    });
  }

  const deadlines = unique(sections.flatMap((s) => s.codes));
  if (deadlines.length > 0) {
    rules.push(`${removed(deadlines)} [data-corp-group="deadlines"]{display:none}`);
  }

  return rules.join("");
}
