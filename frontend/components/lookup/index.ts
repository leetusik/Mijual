/**
 * 내 종목 조회 (R4) — the surface's own components.
 *
 * **R11** split the page frame in two, because the two states owe a reader
 * different things: `LookupHeader` is the *entry* page's (title · subline · the
 * 48px GET search row · the 검색 불일치 line), `LookupIdentity` is a *result*'s
 * (the 종목명 as `h1`, the two codes, a search row echoing the name, and the
 * 보유량 strip as its bottom rail), and `LookupRail` is the crumb both share.
 * `StockView` is everything a resolved stock adds, and it is a client component
 * because the 보유량 count it owns drives both sections and the identity panel.
 *
 * The N주 arithmetic is **not** here: it is `lib/holding.ts`, the product's one
 * multiplication site, shared with 내 포트폴리오 (`P5.S16`).
 */
export { LookupHeader, LookupIdentity, LookupRail } from "./LookupHeader";
/** The search row itself (`P7.S4`) — the landing hero renders the same one, so
 * the two surfaces cannot drift into two behaviours. */
export { SearchRow } from "./SearchRow";
export { StockView } from "./StockView";

/** The two blocks the **entry** page composes for itself (R11 §1, Q-A = b): the
 * 감시 대상 context panel — the same one a no-rights stock shows, so an empty
 * entry and an empty result say the same thing — and the 집계 범위 boundary under
 * its own `h2`. `StockView` renders the coverage panel on a result. */
export { CoveragePanel, WatchPanel } from "./LookupEmpty";

/**
 * The two type blocks R5 hands to 내 포트폴리오 as-is: "금액 = **R4 계약 그대로**
 * … 내 종목 조회와 수치 불일치 금지 (같은 contract 소스)".
 *
 * `P5.S16` renders ① rows with `Conversion` and ② rows with `Dilution` rather
 * than drawing its own — one composition on the server (`reads._rights_row`), one
 * multiplication site in the browser (`lib/holding.ts`) and one rendering, so the
 * two surfaces cannot disagree about a number or about how it is labelled. Making
 * them public is the whole change: neither component moved and neither took a
 * portfolio-shaped prop.
 */
export { Conversion } from "./Conversion";
export { Dilution } from "./RightsSection";
