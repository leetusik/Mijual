/**
 * 운영 관제's own route map — deliberately **not** in `lib/routes.ts`.
 *
 * R7's first rule for this surface is that it is "**reader chrome 어디에서도
 * 링크 금지** (nav·푸터·계정 메뉴·sitemap)", and the cheapest way to keep a rule
 * like that true is to make it structural: the reader's route module is what the
 * nav, the footer and the account menu import, so an ops path put there is one
 * autocomplete away from becoming a link. It lives here instead, beside the only
 * components allowed to use it.
 *
 * The one place outside `app/ops/**` that needs `OPS_ROOT` is `SiteChrome`, and
 * it needs it in order to render **nothing** — the reader chrome must not wrap
 * this surface (R7: 인증 전 표면은 ops 크롬 없음, and the authenticated tabs carry
 * the ops chrome instead).
 *
 * Six sections, six routes. R7 forbids 컴포넌트 단편 화면 — 모든 섹션은 ops
 * 크롬을 갖춘 완전한 페이지 — so each tab is a page of its own rather than a
 * client-side panel switch, which is also what makes 「로그인 후 있던 탭 복원」
 * mechanical: the door renders **in place** at the tab's own URL, so the path
 * never moves and there is nothing to restore.
 */

/** The panel's root. `docs/current/frontend.md` leaves the final path to the
 * deployment and names `/ops` as the example; it is the local choice `P5.S9`
 * already documents. */
export const OPS_ROOT = "/ops";

export const OPS_ROUTES = {
  overview: OPS_ROOT,
  gates: `${OPS_ROOT}/gates`,
  accuracy: `${OPS_ROOT}/accuracy`,
  conversations: `${OPS_ROOT}/conversations`,
  users: `${OPS_ROOT}/users`,
  feedback: `${OPS_ROOT}/feedback`,
} as const;

export type OpsRouteKey = keyof typeof OPS_ROUTES;

/** Is this request inside 운영 관제? `SiteChrome` asks, and so does the tab bar. */
export function isOpsPath(pathname: string): boolean {
  return pathname === OPS_ROOT || pathname.startsWith(`${OPS_ROOT}/`);
}

/**
 * The 대화 로그 tab, filtered to one anonymous session.
 *
 * R7 wires this **both ways**: 익명 세션's 「대화 로그 →」 comes here, and a
 * session hash in the log table goes back to the 사용자 tab. `session` is the
 * page's own query name; the API's filter is `session_hash` (`P5.S9`'s port
 * signature), and the page translates between the two.
 */
export function conversationsForSession(sessionHash: string): string {
  return `${OPS_ROUTES.conversations}?session=${encodeURIComponent(sessionHash)}`;
}
