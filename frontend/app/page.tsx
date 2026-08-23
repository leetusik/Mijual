import { connection } from "next/server";
import { Board, Cosmos, Hero, LapseNotice, RetrospectiveAnchor } from "@/components/landing";
import { getBoard, getBoardSummary } from "@/lib/api";
import styles from "./page.module.css";

/**
 * 관제 현황판 — the landing (R2/R2.1, with R3's 추후결정 board strip).
 *
 * The round composes one page: cosmos backdrop → hero (search-first) →
 * retrospective anchor (value card + countdown/stats card) → 소멸주의보 →
 * the board. The nav and the footer around it are `P5.S11`'s chrome, applied by
 * the root layout.
 *
 * ## Two requests, one corpus reading
 *
 * `/board/summary` and `/board` are fetched together at request time.
 * `/board/summary` is deliberately **one object for every landing number** so the
 * hero's stat line, the value card, the stats card and the 소멸주의보 strip cannot
 * disagree; `/board` carries the ranked rows, the whole-board tab counts and the
 * two pinned strips. Nothing on this page is computed from anything else: no
 * D-day, no date, no staleness and no total is derived in the browser.
 *
 * `connection()` is what keeps that true. It marks the page as request-time
 * rendering (Next 16's replacement for the old `dynamic` segment config), so the
 * board is never a build-time snapshot served hours later — and so `next build`
 * needs no API to build against.
 */
export default async function BoardLanding() {
  await connection();

  const [summary, board] = await Promise.all([getBoardSummary(), getBoard()]);

  return (
    <>
      <Cosmos />
      <main className={styles.landing}>
        <Hero summary={summary} />
        <div className={`content ${styles.stack}`}>
          <RetrospectiveAnchor summary={summary} />
          <LapseNotice summary={summary} />
          <Board board={board} />
          {/* R5-4's landing sample entry stood here. **R8 removed it** (build-prompt
              §1: "랜딩의 「내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →」 링크와
              그 빈 밴드 제거"), because the nav's 보유 종목 slot now opens the same
              sample for a reader with no session — one destination instead of a
              line at the foot of the page. The 로그인 page's entry (R5-4's other
              placement) is untouched. */}
        </div>
      </main>
    </>
  );
}
