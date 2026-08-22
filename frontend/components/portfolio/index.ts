/**
 * 내 포트폴리오 (R5-3 … R5-8) — the product's only gated surface, and its
 * anonymous 샘플 mode.
 *
 * `Portfolio` is the layer itself (holdings · the two D-day sections · 챙긴 돈 ·
 * the two carry offers · 종목 추가) and `NotificationsView` is 알림 설정, the
 * account menu's second destination. Both are client components over a
 * server-loaded payload: the pages under `app/portfolio/` do the gating and the
 * cookie-forwarded read, and nothing here re-composes a row — the sections, the
 * order and every D-day are `GET /portfolio`'s.
 *
 * The N주 arithmetic is **not** here either: it is `lib/holding.ts`, the product's
 * one multiplication site, and ①'s and ②'s blocks are literally 조회's components
 * (`components/lookup`), so "내 종목 조회와 수치 불일치 금지" holds by
 * construction rather than by care.
 */
export { Portfolio } from "./Portfolio";
export { NotificationsView } from "./NotificationsView";
