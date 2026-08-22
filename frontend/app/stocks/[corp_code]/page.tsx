import { notFound } from "next/navigation";
import { connection } from "next/server";
import { LookupHeader, StockView } from "@/components/lookup";
import { ApiError, getBoardSummary, getStock } from "@/lib/api";
import { PROVENANCE_KO } from "@/components/lookup/copy";
import type { BoardSummary } from "@/lib/types";
import styles from "@/components/lookup/Lookup.module.css";

/**
 * `/stocks/{corp_code}` — one issuer's 내 종목 조회 page (R4).
 *
 * The `corp_code` path segment is the product's stable handle for a stock:
 * `GET /stocks/{corp_code}` is the API's own link-out for R3's "내 보유량으로
 * 환산 →" (`P5.S4`'s route map), `lib/routes.ts`'s `stockPath()` states it once,
 * and `isActiveRoute` already keeps 내 종목 조회 underlined here. A query is the
 * *search's* vocabulary and lives on `/stocks?q=`, which redirects onto this
 * page when it resolves.
 *
 * **An unknown code is a 404** — "a search miss is a result; a bad link is an
 * error" (`P5.S4` note 1) — and, like every other 404 in this product, it
 * explains nothing: the copy inventory holds no Korean not-found sentence and
 * writing one would be inventing signed copy (`P5.S13` note 4 carries the same
 * open question).
 *
 * `/board/summary` is fetched **only** for the no-event empty state, which is
 * the one place this surface states a number it does not otherwise hold (감시 중
 * N건). A stock with rights or a 소멸 row never pays for that request, and a
 * summary that fails costs the line rather than the page.
 */
export default async function StockPage({
  params,
}: {
  params: Promise<{ corp_code: string }>;
}) {
  await connection();
  const { corp_code: corpCode } = await params;

  let page;
  try {
    page = await getStock(corpCode);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  const empty = page.rights.count === 0 && page.lapse.totals.offerings === 0;
  const summary: BoardSummary | null = empty
    ? await getBoardSummary().catch(() => null)
    : null;

  return (
    <main className={`content ${styles.page}`}>
      <LookupHeader />
      {/* Keyed by the issuer: a different stock is a different holding, and its
          session memory must be read fresh rather than inherited. */}
      <StockView key={page.stock.corp_code} page={page} summary={summary} />
      <p className={styles.provenance}>{PROVENANCE_KO}</p>
    </main>
  );
}
