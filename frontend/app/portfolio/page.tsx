import { cookies } from "next/headers";
import { Portfolio } from "@/components/portfolio";
import type { ResolvedStock } from "@/components/portfolio/AddHolding";
import { ApiError, getPortfolio, getSamplePortfolio, getStock } from "@/lib/api";
import type { Portfolio as PortfolioPayload } from "@/lib/types";
import styles from "@/components/portfolio/Portfolio.module.css";

/**
 * `/portfolio` — 내 포트폴리오 (R5), 보유 종목 as the nav now names the slot (R8),
 * and `?sample=1` — 샘플 포트폴리오 (R5-4).
 *
 * ## What R8 changed: **an anonymous visit is the sample, not a redirect**
 *
 * R5 made this the product's one gated surface ("내 포트폴리오 → 로그인 게이트
 * (유일하게 게이트되는 표면)"), and a session-less visit bounced to 로그인. R8 puts
 * the route in the bar under one label for both states and says what each state
 * answers with:
 *
 * > `보유 종목`은 로그인 여부와 무관하게 같은 라벨·같은 라우트. 익명이면 표면이
 * > 샘플 모드로 응답 (`SampleBanner` + `lib/sample.ts` 기존 동작) — nav는 아무
 * > 배지도 붙이지 않는다.
 *
 * So a nav slot never leads to a login wall: signed in, the reader's own rows;
 * signed out, the same surface in the sample mode it already had. **The gate
 * itself is unchanged** — it is still the API's own answer (`GET /portfolio` with
 * the request's cookie forwarded; `401 unauthenticated` means no session), and
 * `GET /portfolio/sample` was always anonymous. What changed is what this page
 * does with that 401: it renders the sample instead of redirecting, and the
 * account's rows are still reachable by nobody but the account.
 *
 * `?sample=1` keeps working for the signed-in reader who follows R5-4's entry
 * from the 로그인 page, which is the one case where the mode must outrank a
 * session.
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
  // No session → the sample (R8 §1), same surface, same banner, no redirect.
  if (payload === null) {
    const example = await getSamplePortfolio();
    return (
      <main className={`content ${styles.page}`}>
        <Portfolio payload={example} mode="sample" preselect={null} />
      </main>
    );
  }

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
