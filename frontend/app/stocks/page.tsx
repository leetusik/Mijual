import { redirect } from "next/navigation";
import { connection } from "next/server";
import { LookupHeader } from "@/components/lookup";
import { lookupStock } from "@/lib/api";
import { stockPath } from "@/lib/routes";
import { PROVENANCE_KO } from "@/components/lookup/copy";
import styles from "@/components/lookup/Lookup.module.css";

/**
 * `/stocks` — **내 종목 조회** (R4): the search state, and where a query lands.
 *
 * ## Two routes, one surface, and which is which
 *
 * - **`/stocks`** is the search: with no `?q=` it is the empty console the hero
 *   and the nav point at; with one it resolves the query server-side.
 * - **`/stocks/{corp_code}`** is a resolved stock — the product's **stable
 *   handle** for an issuer, which R3's "내 보유량으로 환산 →" already links by
 *   (`P5.S13` note 1, `lib/routes.ts`'s `stockPath`).
 *
 * A hit therefore **redirects onto the handle**: a `corp_code` names one issuer
 * by construction while a query is only resolvable, so the page a reader can
 * bookmark, share or reload should be the former. The two entry points — typing
 * a name here and arriving from a detail page — then reach byte-identical pages
 * instead of two routes that must be kept saying the same thing.
 *
 * A **miss is not an error**: `?q=` that resolves nothing is `200 {found:
 * false}` (`P5.S4` note 1), so this stays on the search page and renders R4's
 * own 검색 불일치 sentence with the query still in the box. The contract names no
 * reason, offers no candidate and suggests no near-miss, and neither does this.
 *
 * `connection()` marks the page request-time, so `next build` needs no API and
 * no D-day is a build-time snapshot served hours later.
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

    return (
      <main className={`content ${styles.page}`}>
        <LookupHeader query={query} missed />
        <p className={styles.provenance}>{PROVENANCE_KO}</p>
      </main>
    );
  }

  return (
    <main className={`content ${styles.page}`}>
      <LookupHeader />
      <p className={styles.provenance}>{PROVENANCE_KO}</p>
    </main>
  );
}
