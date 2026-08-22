/**
 * `/ask` — **AI 질문**, as a bare page shell. The surface is **P6's**.
 *
 * The nav's third slot is signed (R6 finalized 내 종목 조회 · 관제 현황판 · AI
 * 질문, and its build prompt puts the dedicated page behind that slot), and
 * RESPECT THE DESIGN forbids dropping an approved element — so P5 renders the
 * slot and the route. Everything R6 designs *behind* it is the agent: the widget,
 * the launcher, presets, tool fact rows, numbered citation chips, refusals,
 * streaming and anonymous server-side storage. All of that is P6's phase, by the
 * split this phase was created under (`P5.DECOMP` note 7).
 *
 * So this page renders **nothing**: no invented copy, no fake chat, no
 * placeholder, no 「준비 중」 string — the same honesty rule the ops panel's empty
 * tabs follow (`P5.DECOMP` note 5a: an honest 0건 rather than an invented
 * string). A reader who arrives sees the chrome and an empty page, which is what
 * this build truthfully has. **P6 replaces this file.**
 */
export default function AskPage() {
  return <main className="content" />;
}
