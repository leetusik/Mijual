import type { Metadata } from "next";
import { cookies } from "next/headers";
import { Portfolio, SampleRemovedRules } from "@/components/portfolio";
import type { ResolvedStock } from "@/components/portfolio/AddHolding";
import { ApiError, getPortfolio, getSamplePortfolio, getStock } from "@/lib/api";
import { PORTFOLIO_TITLE_KO } from "@/lib/seo";
import { readAuthState } from "@/lib/session.server";
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
/**
 * **`noindex, nofollow`** — this surface is not part of the product's public,
 * indexable face. `app/robots.ts` disallows the same prefix, so a well-behaved
 * crawler never fetches this page at all; this tag is what a crawler that fetches
 * anyway reads, and it is the only one of the two that can get an already-indexed
 * URL *removed*.
 */
export const metadata: Metadata = {
  title: PORTFOLIO_TITLE_KO,
  robots: { index: false, follow: false },
};

export default async function PortfolioPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const sample = params.sample === "1";
  const add = typeof params.add === "string" ? params.add : undefined;

  if (sample) {
    // `?sample=1` is the one entry a **signed-in** reader can take into 샘플 mode
    // (R5-4), so anonymity is a question here rather than a given — and it is the
    // server's to answer, not a probe's (`P12.F3`). `readAuthState()` is
    // request-memoised, so this costs the root layout's read and nothing more.
    const [payload, auth] = await Promise.all([getSamplePortfolio(), readAuthState()]);
    return (
      <main className={`content ${styles.page}`}>
        {/* Before the surface, so the parser holds the rules before it reaches
            the rows they hide (`P12.F10`). */}
        <SampleRemovedRules payload={payload} />
        <Portfolio
          payload={payload}
          mode="sample"
          preselect={null}
          anonymous={!auth.authenticated}
        />
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
        {/* The 401 **is** the answer: a request whose session the API refused is
            anonymous, so the 전환 제안 band's audience is known here with no extra
            read at all, and it is server-rendered rather than inserted 53 ms —
            2.2 s on a cold mobile load — after first paint (`P12.F3`). */}
        <SampleRemovedRules payload={example} />
        <Portfolio payload={example} mode="sample" preselect={null} anonymous />
      </main>
    );
  }

  // 계정 이전 (R5-4) is offered to a signed-in reader whose **browser** holds a
  // sample, and until `P12.F3` this client fetched today's served composition
  // itself, after mount — which is why the band could only ever be inserted into a
  // painted page (215.28 px of push, `P12.R1`'s worst measured shift). The server
  // cannot know whether this browser holds a sample (and must not be told — see
  // `security.md`), but the composition is anonymous, cheap and exactly what it
  // already fetches for 샘플 mode, so it is read **here**: the client then has the
  // rows and the names at hydration, and the pre-hydration mirror can size the
  // band's slot from the same composition before anything paints.
  //
  // A failure is `null`, and `null` is a state: `Portfolio` falls back to the
  // client-side read it always did, and the band simply lands the old way.
  const [preselect, sampleServed] = await Promise.all([
    add
      ? getStock(add, { headers })
          .then((page) => page.stock)
          .catch(() => null)
      : Promise.resolve(null),
    getSamplePortfolio()
      .then((page) => page.holdings)
      .catch(() => null),
  ]);

  return (
    <main className={`content ${styles.page}`}>
      <Portfolio
        payload={payload}
        mode="account"
        preselect={preselect as ResolvedStock | null}
        sampleServed={sampleServed}
      />
    </main>
  );
}
