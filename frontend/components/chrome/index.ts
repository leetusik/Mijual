/**
 * The global chrome (R2 §Page shell) — the nav, the mobile sheet, the footer,
 * the vocky triggers and vocky's script seam.
 *
 * Separate from `components/index.ts`, which is the R1/R2 **trust primitives**
 * every surface composes. These are chrome: a page never renders one, the root
 * layout does. The two seams later slices touch are named in their own files —
 * `AccountSlot.tsx` (the 로그인 slot, `P5.S16`) and `VockyScript.tsx`
 * (`NEXT_PUBLIC_VOCKY_SRC`, `P5.S18`/P4).
 */
export { SiteChrome } from "./SiteChrome";
export { SiteNav } from "./Nav";
export { SiteFooter } from "./Footer";
export { VockyTrigger, type VockyTriggerProps } from "./VockyTrigger";
export { VockyScript } from "./VockyScript";
export { Wordmark, type WordmarkProps } from "./Wordmark";
