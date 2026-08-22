import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { Portfolio } from "@/components/portfolio";
import type { ResolvedStock } from "@/components/portfolio/AddHolding";
import { ApiError, getPortfolio, getSamplePortfolio, getStock } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import type { Portfolio as PortfolioPayload } from "@/lib/types";
import styles from "@/components/portfolio/Portfolio.module.css";

/**
 * `/portfolio` — 내 포트폴리오 (R5), and `?sample=1` — 샘플 포트폴리오 (R5-4).
 *
 * ## The gate, and the fact that it is the only one
 *
 * > 내 포트폴리오 → 로그인 게이트 (**유일하게 게이트되는 표면**); 그 외 전부 익명
 * > 동작 유지.
 *
 * The gate is the API's own answer rather than a second rule: this page asks for
 * `GET /portfolio` with the request's own cookie forwarded (`P5.S10` note 13 —
 * `credentials` is a browser concept and does nothing in Node) and a
 * `401 unauthenticated` sends the reader to the 로그인 panel, which on a
 * successful login sends them back here (`P5.S15`). One request, one authority,
 * and no way for the page's idea of "logged in" to differ from the service's.
 *
 * Nothing else in the product gained a gate: every other route still answers 200
 * without a cookie, and this file is the only `redirect` to 로그인 in the app.
 *
 * ## The sample is a mode of this route, not a surface of its own
 *
 * `?sample=1` (`lib/routes.ts`'s `samplePath()`, which both signed entries use)
 * loads the anonymous `GET /portfolio/sample` — no cookie, no account, no write.
 * R5-4 draws it as a **loaded state of the 2층**: an inset banner here, a
 * 「샘플」 chip and 샘플 종료 in the nav slot, and the reader's own edits in
 * `localStorage`. A reader with a session who follows a sample link gets the
 * sample: it carries no account fact either way, and the banner says what it is.
 *
 * ## `?add={corp_code}` preselects, and writes nothing
 *
 * R5-2's logged-in one-liner navigates here with an issuer named
 * (`portfolioAddPath`), so the code is resolved server-side through 조회's own
 * `GET /stocks/{corp_code}` and handed to the 종목 추가 panel already named. A
 * code that resolves to nothing is simply dropped — the panel opens empty, and no
 * Korean is invented for a link that went stale.
 */
export default async function PortfolioPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const sample = params.sample === "1";
  const add = typeof params.add === "string" ? params.add : undefined;

  if (sample) {
    const payload = await getSamplePortfolio();
    return (
      <main className={`content ${styles.page}`}>
        <Portfolio payload={payload} mode="sample" preselect={null} />
      </main>
    );
  }

  const cookie = (await cookies()).toString();
  const headers = cookie ? { cookie } : undefined;

  let payload: PortfolioPayload | null = null;
  try {
    payload = await getPortfolio({ headers });
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error;
  }
  if (payload === null) redirect(ROUTES.login);

  const preselect: ResolvedStock | null = add
    ? await getStock(add, { headers })
        .then((page) => page.stock)
        .catch(() => null)
    : null;

  return (
    <main className={`content ${styles.page}`}>
      <Portfolio payload={payload} mode="account" preselect={preselect} />
    </main>
  );
}
