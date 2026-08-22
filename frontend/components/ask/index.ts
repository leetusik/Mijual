/**
 * AI 질문 (R6) — the launcher, the widget, and the shared conversation store.
 *
 * `SiteChrome` mounts exactly two of these: `AskProvider` around the reader tree
 * and `AskSurface` inside it. Everything else is a piece of the widget, exported
 * because **`P6.S6` composes the same pieces into the dedicated page** rather
 * than writing a second answer renderer — one surface, two views.
 *
 * The thread itself is not here: it lives in `lib/ask.ts` (framework-free, module
 * scope) so that a turn keeps streaming while the reader navigates.
 */
export { AskProvider } from "./AskProvider";
export { AskSurface } from "./AskSurface";
export { AskWidget } from "./AskWidget";
export { AskLauncher } from "./AskLauncher";
export { Answer } from "./Answer";
export { Composer, type ComposerState } from "./Composer";
export { InlineCitation } from "./InlineCitation";
export { resolveLink, resolveLinks, type ResolvedLink } from "./links";
export { AskContext, useAskState, useAskStore, useDesktop, DESKTOP_QUERY } from "./useAsk";
