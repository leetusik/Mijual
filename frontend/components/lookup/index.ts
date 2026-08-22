/**
 * 내 종목 조회 (R4) — the surface's own components.
 *
 * `LookupHeader` is the page frame (title · subline · crumb · the GET search
 * row) and works on every state, including the two where there is no stock:
 * the bare landing and a 검색 불일치. `StockView` is everything a resolved stock
 * adds, and it is a client component because the 보유량 count it owns drives
 * both sections.
 *
 * The N주 arithmetic is **not** here: it is `lib/holding.ts`, the product's one
 * multiplication site, shared with 내 포트폴리오 (`P5.S16`).
 */
export { LookupHeader } from "./LookupHeader";
export { StockView } from "./StockView";
