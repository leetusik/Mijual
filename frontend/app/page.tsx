import { connection } from "next/server";
import { SampleEntry } from "@/components/auth";
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
      <main>
        <Hero summary={summary} />
        <div className={`content ${styles.stack}`}>
          <RetrospectiveAnchor summary={summary} />
          <LapseNotice summary={summary} />
          <Board board={board} />
          {/* R5-4's second sample entry — "진입: 로그인 페이지 하단 + 랜딩 푸터".
              It lands at the foot of the landing *page*: R5 leaves the global
              footer unchanged ("Footer 불변"), so the sample entry is a landing
              element rather than chrome (`P5.S11` note 11). */}
          <SampleEntry variant="landing" />
        </div>
      </main>
    </>
  );
}
