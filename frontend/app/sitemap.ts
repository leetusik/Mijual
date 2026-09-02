import type { MetadataRoute } from "next";
import { getBoard } from "@/lib/api";
import { eventPath, ROUTES, stockPath } from "@/lib/routes";
import { SITE_URL } from "@/lib/seo";
import type { BoardRow } from "@/lib/types";

/**
 * `/sitemap.xml` (Next file convention) — the static reader routes plus every
 * event and every issuer the board currently exposes.
 *
 * ## Dynamic on purpose, and it degrades instead of 500-ing
 *
 * `force-dynamic` + `revalidate = 0`: the corpus moves twice a day (beat's 07:30
 * and 19:30 KST runs), and a sitemap baked at build time would name yesterday's
 * events until the next deploy. The **one** `getBoard()` call is wrapped in
 * `try/catch` with a timeout, so an API outage costs the dynamic half and leaves
 * the static half served — a 500 here would tell a crawler the whole site's map
 * is broken, which is a much larger claim than "the API is down right now".
 *
 * ## What is listed, and what is structurally absent
 *
 * The static half is `lib/routes.ts`'s three **reader** routes — `/`, `/stocks`,
 * `/ask`. `/auth/login`, `/auth/reset`, `/portfolio` and `/portfolio/notifications`
 * are in that same map and are **not** listed: they are gated or credential-bearing
 * surfaces, disallowed in `robots.ts` and `noindex` on their own segments.
 *
 * **`/ops` is not in this file and cannot be**: R7's first rule names the sitemap
 * explicitly (「reader chrome 어디에서도 링크 금지 — nav·푸터·계정 메뉴·sitemap」),
 * and the ops paths live in `components/ops/routes.ts` precisely so that a module
 * like this one cannot reach them by accident.
 *
 * **`/stocks` is crawler-orphaned by design** — the R8 nav has two slots and 내
 * 종목 조회 is not one of them (`components/chrome/copy.ts`: the constant stays a
 * *surface* name, the chrome renders it nowhere). This file is therefore the only
 * path by which a crawler reaches it, which is the reason the sitemap matters
 * here beyond hygiene. Adding a nav link instead would be a design change.
 *
 * ## `lastModified` is the board's own reference day, and nothing else
 *
 * `BoardResponse.reference` is the KST calendar day the whole board was computed
 * against — the one date this payload actually holds. A row carries no
 * modification timestamp (`BoardRow` has `countdown`, not a `updated_at`), and
 * `original_rcept_dt` is the *filing* date, which a 정정 makes a lie about the
 * content's age. So every dynamic URL gets the board's reference and the static
 * routes get none: an honest coarse date beats a precise invented one. On an API
 * failure there is no reference either, and the static half carries no date.
 */
export const dynamic = "force-dynamic";
export const revalidate = 0;

/** The board is chrome for this route: the crawler gets its map whether or not
 * the API answers. Same reasoning (and roughly the same budget) as the root
 * layout's 운영자 연락처 read. */
const BOARD_TIMEOUT_MS = 4000;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const board = await getBoard(undefined, {
    cache: "no-store",
    signal: AbortSignal.timeout(BOARD_TIMEOUT_MS),
  }).catch(() => null);

  const staticUrls: MetadataRoute.Sitemap = [
    { url: `${SITE_URL}${ROUTES.board}`, changeFrequency: "daily", priority: 1 },
    { url: `${SITE_URL}${ROUTES.stocks}`, changeFrequency: "daily", priority: 0.8 },
    { url: `${SITE_URL}${ROUTES.ask}`, changeFrequency: "monthly", priority: 0.5 },
  ];

  if (!board) return staticUrls;

  // The unpaged board plus its two pinned strips. `rows` is the ranked list;
  // `open_now` (② 진행 중) and `tbd` (일정 추후결정) are served beside it rather
  // than inside it, so a crawler that only saw `rows` would miss whole classes of
  // event page. Deduplicated below — an event may legitimately appear twice.
  const rows: BoardRow[] = [...board.rows, ...board.open_now.rows, ...board.tbd.rows];
  const lastModified = board.reference;

  const events = new Set<string>();
  const issuers = new Set<string>();
  for (const row of rows) {
    // Only a renderable event has a page: everything else is a 404 from the API
    // (`app/events/[rcept_no]/page.tsx`), and a sitemap full of 404s is a crawl
    // budget spent on nothing. `withdrawn` *does* render — 철회 is a surface —
    // but it is a closed matter with no deadline left, so it is not advertised.
    if (row.state === "exposable" && row.rcept_no) events.add(row.rcept_no);
    if (row.corp_code) issuers.add(row.corp_code);
  }

  return [
    ...staticUrls,
    ...[...events].map((rceptNo) => ({
      url: `${SITE_URL}${eventPath(rceptNo)}`,
      lastModified,
      changeFrequency: "daily" as const,
      priority: 0.7,
    })),
    ...[...issuers].map((corpCode) => ({
      url: `${SITE_URL}${stockPath(corpCode)}`,
      lastModified,
      changeFrequency: "daily" as const,
      priority: 0.6,
    })),
  ];
}
