/**
 * `/stocks` — **내 종목 조회**, as a bare page shell. `P5.S14` builds the surface.
 *
 * The nav's first slot needs a destination, and R4's surface is a slice of its
 * own: search + the 보유량 strip with sessionStorage memory + 진행 중인 권리 +
 * the 2026 놓친 돈 breakdown + the empty states + the disclaimer footnote, all
 * composed from `/stocks?q=…`'s factors (the N주 math is the client's, with one
 * implementation shared with 내 포트폴리오).
 *
 * Same rule as `/ask`: **nothing is drawn here** rather than a placeholder or an
 * invented Korean line. The route exists so the signed nav slot resolves and its
 * active state works; `P5.S14` replaces this file.
 */
export default function StocksPage() {
  return <main className="content" />;
}
