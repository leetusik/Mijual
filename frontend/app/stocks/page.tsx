import { redirect } from "next/navigation";
import { connection } from "next/server";
import { CoveragePanel, LookupHeader, LookupRail, WatchPanel } from "@/components/lookup";
import { getBoardSummary, lookupStock } from "@/lib/api";
import { stockPath } from "@/lib/routes";
import { PROVENANCE_KO } from "@/components/lookup/copy";
import type { BoardSummary } from "@/lib/types";
import styles from "@/components/lookup/Lookup.module.css";

/**
 * `/stocks` — **내 종목 조회** (R4): the search state, and where a query lands.
 *
 * ## Two routes, one surface, and which is which
 *
 * - **`/stocks`** is the search: with no `?q=` it is the entry page the hero and
 *   the nav point at; with one it resolves the query server-side.
 * - **`/stocks/{corp_code}`** is a resolved stock — the product's **stable
 *   handle** for an issuer, which R3's "내 보유량으로 환산 →" already links by
 *   (`P5.S13` note 1, `lib/routes.ts`'s `stockPath`).
 *
 * A hit therefore **redirects onto the handle**: a `corp_code` names one issuer
 * by construction while a query is only resolvable, so the page a reader can
 * bookmark, share or reload should be the former. The two entry points — typing a
 * name here and arriving from a detail page — then reach byte-identical pages
 * instead of two routes that must be kept saying the same thing.
 *
 * A **miss is not an error**: `?q=` that resolves nothing is `200 {found:
 * false}` (`P5.S4` note 1), so this stays on the search page and renders R4's own
 * 검색 불일치 sentence with the query still in the box. The contract names no
 * reason, offers no candidate and suggests no near-miss, and neither does this.
 *
 * ## What R11 gave this page (Q-A = b)
 *
 * With no query it used to be a title, a search row and a void. **Not a redirect**
 * — the landing hero already sends readers *here*, so bouncing them back would be
 * a loop — and **no new copy**: the page states the two things it can honestly say
 * before a stock is named, out of elements other surfaces already signed. 감시
 * 대상 3종 + 감시 중 {n}건 (`WatchPanel`, the same block the no-rights stock
 * shows) and the 집계 범위 boundary, now under its own `h2`.
 *
 * `/board/summary` is fetched for that count and **costs the page nothing when it
 * fails**: the line is absent, never a placeholder.
 *
 * `connection()` marks the page request-time, so `next build` needs no API and no
 * D-day is a build-time snapshot served hours later.
 */
export default async function StocksPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string | string[] }>;
}) {
  await connection();
  const params = await searchParams;
  const raw = Array.isArray(params.q) ? params.q[0] : params.q;
  const query = raw?.trim() ?? "";

  if (query !== "") {
    const result = await lookupStock(query);
    if (result.found) redirect(stockPath(result.stock.corp_code));
  }

  const summary: BoardSummary | null = await getBoardSummary().catch(() => null);

  return (
    <main className={`content ${styles.page} ${styles.narrow}`}>
      <LookupRail />
      <LookupHeader query={query === "" ? undefined : query} missed={query !== ""} />
      <WatchPanel summary={summary} />
      {/* The two coverage dates are served on `GET /stocks/{corp_code}` only, so
          with no stock this states the **boundary** without dating it rather than
          asserting a date this page was never given (`P8.S9` `result.md`). */}
      <CoveragePanel />
      <p className={styles.provenance}>{PROVENANCE_KO}</p>
    </main>
  );
}
