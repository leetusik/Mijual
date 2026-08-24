# R14 handoff — Polish: AI 질문 (surface 7 of 8)

- Round **R14** · slice `P8.S14` (co-work) · apply slice `P8.S15`
- Claude Design project: **"Mijual Design System"** (reads this repository via GitHub)
- Review group for new cards: **`⏳ P8.S14 · Ask`**
- **Token freeze**: `foundations/tokens.css` is signed (R8). This round changes no token.
- Common rules: **R10 §0 adopted as-is** (keep-all, nowrap mono, tabular-nums, border-box, single
  767px breakpoint, hit floors 32px desktop / 44px ≤767) — R11/R12/R13 already build on it.
  **Note:** this surface is the one place the single-767 rule collides with a signed R6 behavior
  boundary (480) — that collision is Finding 1 / Q-A, not something to resolve silently.

**Walk provenance (read this first):** walked **live in Chrome** on the operator runtime
(`http://127.0.0.1:3000`, dev mode) — launcher → widget, three real questions asked through the
agent (전체 공시 scope and event scope), 중지 caught mid-stream, 재시도 exercised, citation chips
opened, reload-restore verified, `/ask` desktop and the event-detail strip walked, and **390px via
a same-live-origin iframe harness** (event detail + `/ask`, real app, real store). Hover states
were read from CSS (the bridge has no mouse-move); the production build was not walked — `P8.S15`
verifies there per the runtime manifest. Screenshots referenced below live in the session record;
every claim is re-checkable in the runtime in one minute.

## 1. Product context

Routes and mounts: `/ask` (dedicated page; frameless chat + right 340 rail); chrome-mounted
**launcher + widget** on every reader route except `/ask`, `/ops`, and ≤480px (not hidden — not
rendered); the event detail's **질문 스트립** (entry point, renders no answer); the same strip on
`/ask` itself when the 범위 is an event. Components: `frontend/components/ask/` — `AskSurface`,
`AskLauncher` (68×50 chat box + 22px Saturn mark), `AskWidget` (440×620 opaque `#0e1a15`),
`AskPage` (+ `AskPageScope`), `QuestionStrip`, `Composer` (one button, three texts), `Answer`,
`InlineCitation`, `presets.ts`, `links.ts`, `copy.ts`; store `frontend/lib/ask.ts` (module scope,
sessionStorage, survives widget↔page and navigation mid-stream).

Designed by **R6** (`rounds/06-explain/output/build-prompt.md` — the binding contract: surfaces +
routes, agent tool rows, 인라인 인용 R6-4, SSE four states text-replacement-only, 거절 R6-7,
세션+저장 R6-5·6 개정, Mobile ≤480, 런처 마크 개정 ⑤). `P8.S1` already fixed the `t1` duplicate-key
bug (turn ids now `t<tag>-N`; verified live: restored ids `t3b341f2d-1..3`, no console warnings).

**What works, verified live (not findings — the baseline to respect):** launcher opens the widget
in place (no layout shift); pending = button text 답변 준비 중… disabled, no bubble, no spinner;
tool rows print verbatim (`이벤트 검색 「계양전기」 → 1건 · ① 유상증자 · 20260724000546`);
citations arrive with their sentences; chip tap opens the in-place quote block (API-tier block for
span-less facts) and re-tap closes; refusal renders as plain prose with a citation and the three
갈 곳 links, no alert color; 중지 keeps the partial turn, dims it, prints exactly one signed inset
sentence 「연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.」 + 재시도; 재시도 re-runs the same
turn in place; footer fades in with 근거 · rcept_no · KST stamp + 다시 질문; external-link closes
the widget and lands `/ask` with the conversation and 범위 intact; reload restores the thread;
scope chip × releases to 전체 공시 without touching existing answers; strip chip at 390 routes to
`/ask` with scope set and the question sent; same-근거 sentences share one chip number.

## 2. The walk — 16 findings

1. **The surface lives on the retired 480px breakpoint.** `Ask.module.css:421`
   (`max-width: 480px`), `AskPage.module.css:64` (`min-width: 481px`), and `useAsk.ts`'s
   `DESKTOP_QUERY = (min-width: 481px)` all draw R1's old 480 line; R10 §0 (adopted R10–R13)
   standardized the product on a **single 767px breakpoint**, and R13 just deleted the last 480
   blocks from portfolio. Here the line is not only CSS: it decides **where the widget/launcher
   exist at all** (a 600px window today gets the launcher and a squeezed widget). Q-A.
2. **Footer says 근거 1건 under five numbered chips.** The count counts distinct filings (the
   evidence list is rcept_nos), while the answer above it numbers chips 1–5. To a first-time
   user 「근거 1건」 directly under [1][2][3][4][5] reads as a contradiction. Q-B.
3. **Prose renders one sentence per line, with a leading space on continuation lines.** R6 signs
   스트리밍 as 「프로즈 자람」 — a growing paragraph — but the live render breaks after every
   sentence (widget and page, all three answers walked), and sentences 2+ carry a visible leading
   indent from the stream's own whitespace. Either the paragraph flow or the line-list is the
   design — it should be decided, not accidental. Q-E.
4. **At 390 the vocky ⓝ trigger overlaps the sticky composer bar on `/ask`.** The chrome-level
   bottom-left trigger sits on top of the input's left edge (harness screenshot). R6's hard rule
   kept the launcher/widget out of vocky's corners; the mobile page's 44px sticky bar now collides
   with it. Q-F.
5. **Tool-row rcept_no wraps mid-number at 390** (`2026072400054⏎6` in 이벤트 검색 rows on both
   iframes). R10 §0: numerals never wrap (nowrap mono). The row itself may scroll or truncate —
   design's call — but a receipt number split across lines misreads.
6. **Preset chips send their noun label as the question.** Four of five chips are noun phrases
   (신주인수권증서 상장·매매기간, 청약 취급처 …, 초과청약 조건 (비율), 발행가액 산정방법 …) and
   exactly one is a sentence (실권주는 어떻게 처리되나요? — the signed FORFEITED exception). The
   pressed label becomes the reader's question bubble verbatim, so the thread shows noun-phrase
   "questions". Register is mixed on the strip and in the thread. Q-D.
7. **The composer's idle button is 「직접 질문 입력 →」 acting as the send button.** The string is
   R6-2's free-input *chip* label, reused as the button's idle text; once the reader has typed a
   question, the control that submits it still says "enter a question directly". The three-text
   machine (idle → 답변 준비 중… → 중지) is signed; the idle text's fitness as *send* is not. Q-C.
8. **Empty-thread widget is mostly dead space.** 440×620 with only the intro + anonymity lines at
   top and the composer at bottom leaves ~380px of empty middle on first open. R6 writes no empty
   state beyond the intro. A polish candidate (e.g. the scope's presets, or nothing — design's
   call; no new Korean without a signed string).
9. **`/ask` desktop: the right column is empty below the rail.** The 340 rail's four items occupy
   ~250px; the rest of the column is blank for the whole page height, and at 1564×963 the page
   under a short thread is largely empty with the composer mid-screen. The frameless chat is
   signed (개정 ④); the proportion/rhythm of the two columns is this round's to polish.
10. **API-tier citation block speaks developer.** 「DART 공시 API 수치 — 원문 스팬 없음, 접수번호가
    인용 핸들」 (P7 Q7① — carried, still open). It is the signed R3 wording, shown verbatim to a
    first-time reader inside a quote block; 스팬 and 인용 핸들 are vocabulary from our own
    contracts. If it changes, the change is this round's to sign.
11. **Hover coverage is inconsistent on the strip/composer group** (P7 Q9 — carried): strip chips
    brighten on hover (border-strong), the send button has no hover state at all, header icons and
    scope × brighten. One rule should cover the surface's affordances.
12. **The scoped answer and the 전체-공시 answer segment citations differently** — the same
    실권주 question got chips 1,2,2 unscoped and 1,2,3 scoped (the server assigns numbers per
    근거; both are correct under 같은 근거 = 같은 번호). Not a bug; noted so the cards draw the
    numbering rule as it actually behaves.
13. **Send button disabled state is only opacity .72 on the solid `--live` fill** — with an empty
    input it still reads pressable (it correctly does nothing). The 32px/44px hit floors are met
    (36px desktop controls, 44px at ≤480).
14. **The widget's thread scrollbar is the browser default** on the opaque `#0e1a15` panel —
    every other panel surface in the product styles none; a visible grey bar sits inside the
    right edge while streaming. Minor; design's call whether to keep it.
15. **`get_contact`'s 연락처 string is still the deploy placeholder** (R6: 미정, 운영자 지정 —
    carried from P6, not this round's to invent; listed so it is not read as forgotten).
16. **`GET /favicon.ico` 404s on every route** (carried from P8.S1's walk; chrome-wide, belongs
    with surface 8 / R15's chrome scope — listed here only because the console shows it on this
    surface too).

## 2b. Questions for the operator (answer in the design session)

- **Q-A (Finding 1)** — the ask surface's breakpoint: **(a)** migrate to the product-wide 767
  (launcher/widget exist only >767; 481–767 gets the full-width page like a phone), or **(b)**
  keep 480 as a documented R6 exception (the widget fits a 481–767 window today only via
  max-width guards). This changes *where a surface exists*, so it is the operator's product call
  before it is a layout call.
- **Q-B (Finding 2)** — 근거 N건: **(a)** keep counting filings but say so (e.g. count the word
  differently — needs a signed string), **(b)** count the chips, or **(c)** leave as-is.
- **Q-C (Finding 7)** — the composer idle/send label: keep 「직접 질문 입력 →」 on both surfaces,
  or sign a distinct send text for the button (new Korean = this round mints and signs it).
- **Q-D (Finding 6)** — presets: keep noun labels as sent questions, or send full question
  sentences behind the labels (sentences exist in the filings' own vocabulary; any new ones must
  be signed in this round).
- **Q-E (Finding 3)** — answer prose: one growing paragraph (R6's 프로즈 자람 literally) or the
  current line-per-sentence list — which is the design?
- **Q-F (Finding 4)** — 390 `/ask`: vocky ⓝ vs the sticky bar — move/hide the trigger on `/ask`
  mobile, inset the bar, or accept the overlap.

## 3. What to design (required cards, group `⏳ P8.S14 · Ask`)

Draw the surface as it should be after this round — reviewable `@dsCard` cards, states drawn
from the walked truth above, **token freeze respected, no invented Korean** (new strings appear
only as signed decisions in `result.md`):

1. **Widget** — empty (post-Q-8 decision), streaming (tool rows + growing prose + caret + 중지),
   done (citations + footer), aborted (dim + signed inset + 재시도), refusal. 440×620 unless Q-A
   changes its world.
2. **`/ask` desktop (1440)** — frameless chat + 340 rail, short-thread and long-thread rhythm
   (Finding 9), on-page strip when scoped.
3. **`/ask` mobile (390)** — stacked opening, sticky 44px bar (Q-F resolved), full-bleed
   citation blocks, strip row.
4. **질문 스트립** (event detail, both widths) — chip register per Q-D, heading, free chip.
5. **Citation chips + quote blocks** — numbered chip, verbatim-quote block, API-tier block
   (Q-B/Finding 10 wording as decided), footer line.
6. **Launcher** — as landed (mark + ring halves + open ×); include only if a finding above moves
   it, otherwise reference it as signed truth (R6 개정 ⑤ + P3 session fix).

With the cards, land in this round's `output/`: `result.md` (decisions Q-A…Q-F + session
revisions, measurements for anything geometric) and `build-prompt.md` (the binding contract for
`P8.S15`, with a numbered §6 regression checklist covering every state in §1's baseline list).

## 4. Hard rules (restated, unchanged)

R6's hard rules stand: 인용 없는 주장 금지 · 인용문 재구성 금지 · 에이전트/브라우저 계산 금지 ·
「추정」 없는 파생값 금지 · 확정 전 금액 금지 · 익명 경로 차단 금지 · 게이트 실패 데이터로 답변
금지 · 이력 UI 금지 · quota 표기 금지 · 스피너·타이핑 점 금지 · 거절에 alert 색 금지. The
launcher's Saturn stays the one sanctioned motion exception; nothing from it spreads to data
surfaces. Tokens frozen (R8). All reader-visible copy Korean; every new Korean string is a dated,
signed exception recorded in `result.md`.
