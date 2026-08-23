/**
 * The global chrome (R2 §Page shell, re-cut by R8) — the nav, the mobile sheet,
 * the footer and the 의견 보내기 surface.
 *
 * Separate from `components/index.ts`, which is the R1/R2 **trust primitives**
 * every surface composes. These are chrome: a page never renders one, the root
 * layout does. The one seam later slices touch is named in its own file —
 * `AccountSlot.tsx` (the 로그인 slot, `P5.S16`, re-cut by R8).
 *
 * **R8 deleted vocky's script seam** (`VockyScript.tsx`, `NEXT_PUBLIC_VOCKY_SRC`)
 * and the three `data-vocky-trigger` elements (`VockyTrigger.tsx`): vocky ships
 * no embeddable widget, so 미주알 owns the screen and the browser talks only to
 * this app's own `POST /api/feedback` (`Feedback.tsx`).
 */
export { SiteChrome } from "./SiteChrome";
export { SiteNav } from "./Nav";
export { SiteFooter } from "./Footer";
export { FeedbackDialog, FeedbackEntry, type FeedbackDialogProps } from "./Feedback";
export { Wordmark, type WordmarkProps } from "./Wordmark";
