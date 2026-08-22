/**
 * The product's route map — one module, so a path is stated once.
 *
 * `docs/current/frontend.md` §Open Questions leaves the concrete paths to the
 * build ("only the admin surface is constrained: a separate path, e.g. `/ops`,
 * linked from nowhere in the reader chrome"), so `P5.S11` decides them here
 * because the chrome is what links to them. Later slices **add** entries; they
 * do not restate a path at a call site.
 *
 * The three nav slots are signed (R2 §Page shell, with R4's and R6's label
 * supersessions): 내 종목 조회 · 관제 현황판 · AI 질문. Their paths:
 *
 * - `/` — 관제 현황판. R2's landing *is* the root surface: it is the product's
 *   opening argument, and the round composes hero + anchor + board on one page.
 *   `app/page.tsx` is still `P5.S10`'s foundation proof; `P5.S12` replaces it.
 * - `/stocks` — 내 종목 조회 (R4). The noun the API already uses for this
 *   surface (`GET /stocks?q=…`, `GET /stocks/{corp_code}`), so the page path and
 *   the contract path read as one thing rather than two vocabularies. `P5.S14`
 *   builds it over `P5.S11`'s bare shell; a per-issuer route lives under it.
 * - `/ask` — AI 질문 (R6). **P6 owns and replaces the surface**; P5 ships the
 *   nav slot and a bare page shell (P5.DECOMP note 7), because RESPECT THE
 *   DESIGN forbids dropping a signed element and honesty forbids a fake chat.
 *   Deliberately not `/explain`: 해설 is the label R6 retired.
 *
 * `login` is the 2층 entry the nav's right-hand slot points at. `/auth/…` is not
 * a free choice — `mijual.web.auth.RESET_PATH` already fixes `/auth/reset` as the
 * password-reset page's path on this app, so its siblings live beside it.
 * **`P5.S15` builds the panel; until it lands this link has no page.** That is
 * deliberate: an empty stand-in for a signed surface would read as a dropped
 * design element, while a missing page is honest and one slice away.
 */
export const ROUTES = {
  /** 관제 현황판 — the landing (R2/R2.1). */
  board: "/",
  /** 내 종목 조회 — R4's surface (`P5.S14`). */
  stocks: "/stocks",
  /** AI 질문 — R6's surface; the body is **P6**'s (`P5.DECOMP` note 7). */
  ask: "/ask",
  /** 로그인 — R5's auth panel (`P5.S15`), beside the backend's `/auth/reset`. */
  login: "/auth/login",
} as const;

export type RouteKey = keyof typeof ROUTES;

/**
 * An event's detail page (R3), keyed by `rcept_no` — the same key the API
 * resolves against every stored version, so yesterday's link still opens the page
 * after a 정정 mutates the number (`P5.S3`'s recorded choice).
 *
 * **`P5.S13` builds the page.** Until it lands the board links to a route that
 * 404s, which is the same deliberate choice `login` above records: an empty
 * stand-in for a signed surface would read as a dropped design element, while a
 * missing page is honest and one slice away.
 */
export function eventPath(rceptNo: string): string {
  return `/events/${rceptNo}`;
}

/**
 * One issuer's 내 종목 조회 page, keyed by the stable `corp_code`.
 *
 * This is where R3's "내 보유량으로 환산 →" goes: the API's own link-out for it is
 * `GET /stocks/{corp_code}` (`P5.S4`'s recorded map — "the stable-handle link-out
 * (R3's '내 보유량으로 환산 →')"), and `isActiveRoute` above was already written
 * for `/stocks/00162461` keeping 내 종목 조회 underlined. A `?q=` link would have
 * to carry a *name* — the search's own vocabulary, resolvable but not exact —
 * while a `corp_code` names one issuer by construction, which is what
 * "preselected" has to mean for a link a reader did not type.
 *
 * **`P5.S14` builds the page.** Until it lands this link has no page, the same
 * deliberate choice `login` and `eventPath` record.
 */
export function stockPath(corpCode: string): string {
  return `${ROUTES.stocks}/${corpCode}`;
}

/**
 * Is `pathname` inside `route`? The nav's active state (R2: "active = 600 + 2px
 * #fff underline") must survive a nested path — `/stocks/00162461` is still the
 * 내 종목 조회 surface — while `/` stays exact, or it would match everything.
 */
export function isActiveRoute(pathname: string, route: string): boolean {
  if (route === "/") return pathname === "/";
  return pathname === route || pathname.startsWith(`${route}/`);
}
