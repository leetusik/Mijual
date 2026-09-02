import type { Metadata } from "next";
import { connection } from "next/server";
import { Board, Cosmos, Hero, LapseNotice, RetrospectiveAnchor } from "@/components/landing";
import { getBoard, getBoardSummary } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import { routeMetadata, SITE_DESCRIPTION_KO, TITLE_DEFAULT } from "@/lib/seo";
import type {
  BoardResponse,
  BoardRow,
  BoardStrip,
  LandingBoard,
  LandingRow,
  LandingStrip,
} from "@/lib/types";
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
/**
 * The home page's own canonical, and the one place the site title is **not**
 * templated.
 *
 * `routeMetadata` gives every indexable route the same field set — title,
 * description, canonical, the whole Open Graph block (which Next replaces rather
 * than merges per segment) and the Twitter card. The canonical lives here rather
 * than in the root layout on purpose: `alternates` **is** inherited as a whole,
 * so a canonical in the layout would make every route claim this page.
 *
 * `title.absolute` because the template is `%s | 주주의관제탑` and this route's
 * own title *is* 주주의관제탑 — templated it would read 「주주의관제탑 |
 * 주주의관제탑」. Every other route wants the template and gets it.
 */
export const metadata: Metadata = {
  ...routeMetadata({
    title: TITLE_DEFAULT,
    description: SITE_DESCRIPTION_KO,
    path: ROUTES.board,
  }),
  title: { absolute: TITLE_DEFAULT },
};

/**
 * Project `/board` down to what the landing actually renders, on the server,
 * once (`P4.F6`).
 *
 * `<Board>` is a client component, so **everything handed to it is serialised
 * into this document a second time** as the RSC flight — the props React needs
 * to hydrate with. `P4.R1` measured the landing at 354,266 B, of which 277,870 B
 * (78 %) is that flight, i.e. the whole board twice: once as 15 rendered rows and
 * once as 445 rows of props. All the rows have to be there (the tabs filter in
 * the browser by design, and the 60 s refresh diffs previous against next), so
 * the only lever is **field width**.
 *
 * Four `countdown` fields are read by nobody on this page. `BoardRow` renders
 * `label_ko`, `date`, `dday` and `days`; `Board`'s `diff()` compares those same
 * three printed values plus `offering`. `window`, `window_state`, `reference` and
 * `source` are the event page's, the 종목 lookup's and 보유 종목's — ~135 B of a
 * 378 B row, ~35 % of it — and they were being parsed and hydrated by every
 * reader of the landing for nothing.
 *
 * Three things this deliberately does **not** do:
 *
 * - **It does not touch `/board`.** The endpoint, its contract and `BoardResponse`
 *   are unchanged; this is one surface declining bytes it does not read, not a
 *   second API. `lib/types.ts`'s `Landing*` shapes are `Pick`/`Omit` over the
 *   real ones for the same reason.
 * - **It does not narrow the refresh.** `Board` keeps calling `getBoard()` and
 *   feeding the full response to `apply()` — a `BoardResponse` is structurally a
 *   `LandingBoard`, and a value fetched in the browser is never serialised into
 *   a document, so there is nothing there to save.
 * - **It does not introduce `undefined`.** Rows are rebuilt by rest-spread rather
 *   than by naming every kept key, because an explicitly-`undefined` optional
 *   (`offering` on ②/③) would be encoded in the flight as `$undefined` — bytes
 *   spent to say a key is missing — and because a field added to `BoardRow`
 *   should reach the landing without an edit here.
 */
const landingRow = ({ countdown, ...rest }: BoardRow): LandingRow => ({
  ...rest,
  countdown: {
    label_ko: countdown.label_ko,
    date: countdown.date,
    dday: countdown.dday,
    days: countdown.days,
  },
});

const landingStrip = ({ rows, ...rest }: BoardStrip): LandingStrip => ({
  ...rest,
  rows: rows.map(landingRow),
});

const landingBoard = (board: BoardResponse): LandingBoard => ({
  ...board,
  rows: board.rows.map(landingRow),
  open_now: landingStrip(board.open_now),
  tbd: landingStrip(board.tbd),
});

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
          <Board board={landingBoard(board)} />
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
