# P8.S15 — R14 applied: AI 질문 (런처 · 위젯 · `/ask` · 질문 스트립 · 인용)

The signed R14 round is built. **17 files changed, one added, none deleted.** The surface now lives
on the product's single 767 boundary — above it a launcher and a 440×620 widget, below it the
full-width page and nothing else — the composer says 「보내기」, a preset chip reads its served label
and sends a signed sentence, an answer grows as **one paragraph** whose 근거 N건 equals the numbers
on the screen, a 접수번호 never breaks mid-number, and a span-less citation is its DART link alone.

Everything below was **measured in the operator's runtime**, not inferred: `make stack-up` /
`next dev` at **`http://127.0.0.1:3000`** and at the tailnet origin **`http://100.77.164.42:3000`**,
and again against a **production build** (`next build && next start -H 0.0.0.0 -p 3100`) served from
a scratch copy, at 1440 / 1280 / 1024 / 900 / 768 / 767 / 600 / 390. The browser is Chrome driven
headless over CDP from an **isolated profile** (never the operator's session); every number here is a
`getBoundingClientRect()` or a `getComputedStyle()` from that browser, and every answer quoted is a
**real turn through the agent** (anonymous, as the surface is).

**No departures from the design record.** Three things the record and the running product disagree
about are catalogued as **Q56–Q58** in `phase.md` rather than resolved here.

---

## 1. What changed, file by file

**`frontend/components/ask/useAsk.ts`** — `DESKTOP_QUERY` is `"(min-width: 768px)"`. Its docstring
now says what the line *is* on this surface: not layout but **existence**, which is why the rule is a
render decision in `AskSurface` and not a media query (a launcher merely unpainted at 600px would
still be in the tab order and would still open a widget).

**`frontend/components/ask/AskSurface.tsx`** — same rule, restated at the render site; the vocky
sentence in its docstring is corrected, because **R8 deleted every `data-vocky-trigger`** (§4 below).

**`frontend/components/ask/Ask.module.css`** — ported from the round's geometry canon
(`output/ask/r14-ask.css`) declaration by declaration: the widget's `max-width` guard **deleted**
(`max-height` stays); the thread and the quote get the thin product scrollbar (`scrollbar-width:
thin` + `--border-strong` thumb + transparent track, with the three `::-webkit-` rules); the 도구 행
loses `word-break: break-all` for `white-space: nowrap; overflow-x: auto; overscroll-behavior-x:
contain` with its scrollbar hidden; `.prose` gains `text-wrap: pretty`; `.chip` gains its hover
(`border-color: var(--live)`) and its open fill (`background: var(--live-tint)` on
`[aria-expanded="true"]`); `.apiTier` is **deleted** and `.quoteLinkSolo { margin-top: 0 }` takes its
place; `.send` gains `transition: border-color`, a hover that moves **only** the border to `--live`,
and a `:disabled` that is the **ghost tier** (`background: none` · `--border-soft` · `--ink-3`,
`opacity: .72` gone) with its hover explicitly neutralised; the media query is `max-width: 767px` and
now also carries R6 §Mobile's 「인용 블록 전폭」 (§3, item 15).

**`frontend/components/ask/AskPage.module.css`** — `min-width: 768px`, and inside it f9's rhythm:
`grid-template-columns: minmax(0, 760px) 340px`, `max-width: 1124px; margin-inline: auto`, and the
rail `position: sticky; top: var(--space-6)`.

**`frontend/components/ask/copy.ts`** — **`SEND_KO = "보내기"`** added with the round's signature
(2026-08-24, Q-C, operator-specified in that session); **`API_TIER_KO` deleted** (finding 10, closing
P7 Q7①); `ASK_SUBMIT_KO`'s docstring records that R14 sent it back to the strip's free chip alone,
and the file header's `P6.S7` reuse flag is now **one** string, not two (the question field's
accessible name `ASK_LABEL_KO` stays flagged). `FORFEITED_QUESTION_KO`'s docstring no longer claims
that every other chip sends its label.

**`frontend/components/ask/Composer.tsx`** — the idle text is `SEND_KO`; `ASK_SUBMIT_KO` is no longer
imported here.

**`frontend/components/ask/presets.ts`** — rewritten around the round's **field key → signed
question** table (`PRESET_QUESTIONS`, the ten `FIELD_ORDER` keys, each row carrying its own R14-D#
signature; `forfeited_share_method` keeps R6's sentence and was not re-signed). `AskPreset.question`
is no longer `label` by construction: the label is the served `korean_name`, the question is the
signed sentence, and **a key outside the table produces no chip** — no label-sending fallback, which
is the rule that keeps Q-D from unwinding one new field key at a time. Order, the
`correction_interpretation` exclusion, the gate-passing input and the 철회 zero-chip case are
untouched.

**`frontend/components/ask/QuestionStrip.tsx`** — a chip carries `title` **and** `aria-label` = the
sentence it sends (build-prompt §3: 「칩의 `title`/접근명은 보내는 문장이다」); the free chip is
unchanged; the docstring's mobile branch is stated at the new boundary.

**`frontend/components/ask/InlineCitation.tsx`** — the API-tier branch is now 「quote → quote block;
no quote → link only」, with `.quoteLinkSolo` when the link stands alone.

**`frontend/components/ask/Answer.tsx`** — `footerFacts` is fed `turn.chips.length` instead of
`turn.footer.count` (Q-B). The rcept_no list and the KST stamp are the server's, unchanged.

**`frontend/lib/ask.ts`** — one new function, `leading()`, applied to `text` and `refusal` blocks as
they enter the store: `String(text ?? "").replace(/^\s+/, "")`. Leading only — a trailing space may
be a sentence's own, and `.question`'s `pre-wrap` is untouched (독자가 친 것은 독자가 친 그대로다).

**`frontend/components/ask/AskWidget.tsx`** — an empty thread whose 범위 is an event renders the
질문 스트립 under the intro (`freeInput={false}`); 전체 공시 renders nothing there, which **is** the
state (finding 8 — no empty-state copy was minted).

**`frontend/components/ask/useScopePresets.ts`** (new) — the hook `AskPage` already had, moved out
whole so the widget and the page generate a chip from one payload by one rule. `AskPage.tsx` imports
it and lost its local copy.

**`frontend/components/ask/AskLauncher.tsx` · `Strip.module.css` · `AskPage.tsx`** — comment-only:
the boundary is stated at 767, and the R6 §Mobile block quote in `AskPage.tsx` is kept **verbatim**
with the supersession marked beneath it (it is the only `480` left in the surface — item 3).

**`docs/reference/design/grounding/copy-inventory.md`** — the R14 tail, hand-registered: 신규 10건
(「보내기」 + R14-D1…D9, dated and reasoned), 회수 2건 (`API_TIER_KO`; `ASK_SUBMIT_KO`'s composer
use), labels stay server-owned, and the superseded R6/R3 clauses listed as 경계·배치 rather than copy.

---

## 2. build-prompt §6 — items 1–20, verbatim, with the measurement

Dev = `127.0.0.1:3000` and the tailnet `100.77.164.42:3000` (identical on every structural item);
prod = the scratch production build on `:3100`.

| # | item | outcome |
|---|---|---|
| 1 | 런처 → 위젯 제자리, 시프트 0 (1440·1024·**768**) | **pass.** `<main>` rect and `documentElement.scrollWidth` before/after the click: `dx=dy=dw=0`, `dScrollW=0` at all three widths, dev · tailnet · prod. |
| 2 | 767/768 존재 경계 | **pass.** launcher/widget present at 768·1024·1280·1440, **absent** at 767·600·390; `/ask` is one column ≤767. Widget at 768 = **440×620 exactly**, `max-width: none`, 24px from both edges. |
| 3 | 480 잔재 0건 | **pass with one documented hit**: `AskPage.tsx:29`, the **verbatim R6 §Mobile quote**, with the supersession stated in the paragraph beneath it. No CSS, no query, no logic mentions 480/481 anywhere in `components/ask` or `lib/ask.ts`. |
| 4 | pending: 답변 준비 중… + 고스트 disabled, 버블·스피너 없음 | **pass.** Caught mid-flight at 390: text 「답변 준비 중…」, `disabled=true`, `background: rgba(0,0,0,0)`, border `--border-soft`, colour `--ink-3`, `opacity: 1`; **no answer element mounted**, 0 spinner/dots nodes. |
| 5 | streaming: 도구 행 verbatim · 프로즈 한 단락 · 캐럿 7×15 1s step · 버튼 중지 | **pass.** Tool row printed verbatim on one line; **one** `<p class=prose>`, `<br>` count **0**, every sentence `display: inline`; caret 7×15 with `1s steps(1) infinite`; button 「중지」. |
| 6 | 빈 입력 = 고스트 disabled → 입력 시 솔리드 보내기 → 전송 | **pass.** Empty: ghost as in item 4. Typed: `background rgb(15,107,80)` (`--live-solid`), border same, ink `rgb(234,242,237)`, enabled; clicking sends. |
| 7 | 인용 칩 탭 → 제자리 인용문 (180px 캡) · 재탭 닫힘 · 같은 근거 = 같은 번호 | **pass.** Open: `aria-expanded=true`, panel 96px, `inert` off, quote `max-height: 180px`. Re-tap: `aria-expanded=false`, clip height **0**, `inert` back. Two sentences citing 근거 1 both print chip **1**. |
| 8 | API-tier 칩 → 블록에 링크만, 새 탭 | **pass.** The span-less chip's panel has exactly one child — `A.quoteLink` with `margin-top: 0px`, `target="_blank"`, text 「DART 원문 20260724000546 ↗」. The three quoted chips render `SPAN.quote` + the link at `margin-top: 12px`. |
| 9 | 푸터 근거 N건 = 화면의 칩 번호 개수 · 접수번호 · KST · 다시 질문 포커스 | **pass, on three real answers**: chips `[1,1,2,3]` → 「근거 3건 · 20260724000546 · 2026-08-24 22:37 KST」; `[1,2,2,2,2]` → 「근거 2건 …」; `[1,1,1,1]` → 「근거 1건 …」. 「다시 질문」 → `document.activeElement` **is** the question field. |
| 10 | 거절: 프로즈 경로 + 인용 + 갈 곳 3링크, alert 색 없음 | **pass** (prod, 「…받을 수 있는 돈이 얼마인가요?」). One prose paragraph in `--ink-1`, three numbered chips, links = DART(`_blank`) · 이벤트 상세 · 내 종목 조회; **0** alert-family colours, **0** icons. |
| 11 | 중지: 부분 답변 유지 + ink-2 감쇠 + 서명 문장 + 재시도 제자리 | **pass.** After 중지: `data-dim="true"`, prose `rgb(157,179,168)` = `--ink-2`, 4 sentences kept, inset row 「연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.」 + 재시도. 재시도 → **same** turn (`turns` stays 1), finishes with its own footer, stopped row gone. |
| 12 | external-link → 위젯 닫힘 + `/ask` 대화·범위 유지; reload → 복원, 콘솔 경고 0 | **pass.** ↗ → `/ask`, widget gone, launcher not rendered, turn intact, rail sticky. Reload → 1 turn restored **with its footer**; console clean of app messages (the only line is Next's own dev preload notice for `app_not-found_module_*.css`, pre-existing and route-independent). |
| 13 | 범위 칩 × → 전체 공시, 기존 답변 불변 | **pass.** Chip 「범위: 전체 공시」, × gone, `turns` unchanged, the existing answer's `innerHTML.length` **identical** (4267 → 4267). |
| 14 | 스트립 칩: 라벨이 보이고 문장이 전송된다 (1440·390) | **pass.** 1440: pressing 「실권주 처리 방식」 puts 「실권주는 어떻게 처리되나요?」 in the thread. 390: pressing 「신주인수권증서 상장·매매기간」 routes to `/ask` with 「범위: 계양전기 · 20260724000546」 and the bubble 「신주인수권증서는 언제부터 언제까지 매매할 수 있나요?」. All ten chips carry `title` = `aria-label` = their sentence. |
| 15 | 390: 인용 블록 전폭 · 접수번호 쪼개짐 0 · 바 44px sticky · vocky ⓝ 없음 · 오버플로 0 | **pass** (dev **and** prod). Quote panel `x=17 w=356` inside answer `x=16 w=358` → bleeds to the box edge, text inset 12px, 180px cap. Tool rows `white-space: nowrap`, **1 line**, no mid-number break. Bar `position: sticky; bottom: 0`, controls `min-height: 44px`, not inset beyond the page's own gutters (`x=16 w=358`). **0** `position: fixed` elements on the route. `scrollWidth − clientWidth = 0`. |
| 16 | `/ask` 1564: 챗 열 ≤760 · 묶음 가운데 · 레일 sticky · 짧은 스레드에서 바가 마지막 요소 아래 | **pass, with a measured note (Q57).** 1564: chat **708px** (≤760 ✓), bundle centred (`x=246`, right gap 246), rail 340 `sticky` at `top: 24px`, bar directly under the last element. The bundle measures **1072**, not 1124, because `main.content` (R2's shell, `--bp-lg` 1120 + 2×24) binds first — the canon's `max-width: 1124px` is in the file and simply never the tighter constraint. |
| 17 | 768–1024 `/ask` 바의 좌하단이 chrome 코너에 닿는지 **실측** | **measured — and the corner is empty.** With a real thread and a 520px-tall viewport, the sticky bar **does** reach the viewport bottom mid-scroll at 768 / 900 / 1024 (`bottomGap = 0`, bar `left = 24`). The app renders **0** fixed elements on `/ask` at every width, so nothing of ours is in that corner: R8 (`P8.S3`) deleted every `data-vocky-trigger`. What the R14 walk photographed at 390 is **Next's dev-tools badge** (`nextjs-portal` shadow root, 36×36 at x 20–56, bottom-left), which the bar's box does intersect **in `next dev` only** — the production build has no `nextjs-portal` at all. Nothing to apply: Q-F's ≤767 rule ("don't render the trigger") is already true everywhere. → **Q56**. |
| 18 | 스레드·인용문 스크롤바 얇은 제품 스타일 | **pass.** Thread: `scrollbar-width: thin`, `scrollbar-color: rgba(163,196,180,.32) transparent`, `::-webkit-scrollbar{width:6px}` + thumb/track rules; quote: same. |
| 19 | 신규 카피 등재 · `API_TIER_KO` 삭제 · `ASK_SUBMIT_KO`는 스트립 자유 칩에만 | **pass.** `SEND_KO` defined in `copy.ts` and used **only** by `Composer.tsx`; `ASK_SUBMIT_KO` used **only** by `QuestionStrip.tsx`'s free chip; `API_TIER_KO` exists nowhere but in three retirement comments; the ten questions live in `presets.ts` with their R14-D# signatures; the copy inventory carries the R14 tail. |
| 20 | 하드룰 재확인 | **pass.** No claim without a citation (every sentence carrying a fact shows its chip); quotes rendered verbatim from the payload; no arithmetic in the browser; no pre-확정 amount (the refusal turn is the proof); **0** spinners/typing dots; refusal in body ink; no 지난 대화 UI; no quota copy. Greps for 「남은 질문」·「저장 이력 없음」·「탭을 닫으면」·`localStorage` in the ask surface: **0** rendered strings (only the prohibitions in docstrings). |

---

## 3. Two judgment calls worth stating plainly

**The canon's `.m390` mirror is read as ≤767 product rules only where the rule is R6's own.** The
block exists because a 390 box inside a card is not a viewport (the round says so, R13's convention).
Of its declarations, 「인용 블록 전폭」 (`.aqp` margin-inline bleed) **is** a product rule — R6 §Mobile
writes it and §6 item 15 checks it — so it is now in `Ask.module.css`'s `max-width: 767px` block, and
it is what item 15 measured. The mirror's `padding-block`/`padding-inline` on `.apage`, by contrast,
is the card harness standing in for the app's own `content` shell; the product keeps R6's page
padding. Nothing else in the mirror was product-bound.

**The footer's count now diverges from the wire, deliberately.** The build-prompt allows either side
(「또는 서버를 칩 수로 맞춘다 — 둘 중 하나이며 화면과 어긋나면 안 된다」) and this slice's plan chose
the client: `turn.footer.count` (distinct filings) is ignored, `turn.chips.length` is printed. No
backend file was touched, the SSE contract is unchanged, and the recorded phase note says so, so the
review sees a divergence that was decided rather than one that drifted.

---

## 4. What the walk called 「vocky ⓝ」 is Next's dev badge — and why nothing was built for it

`build-prompt` §5 asks the chrome not to render the vocky trigger on `/ask` at ≤767. There is no such
element to not-render: **R8 (`P8.S3`) deleted `VockyTrigger.tsx`, `VockyScript.tsx` and all three
`data-vocky-trigger` elements**, and the reader chrome has been free of fixed corner controls since.
Measured on this surface: `0` `position: fixed` nodes on `/ask` at 390 / 768 / 1024 in dev **and**
prod. The 36×36 ⓝ in the walk's 390 screenshot is `nextjs-portal`'s dev-tools button, present only
under `next dev` (absent at `:3100`). Writing a route-conditional render rule for a component that
does not exist would have been inventing an element to hide, so the slice built nothing and the
question goes to the operator as **Q56** (accept the dev badge, or move/disable `devIndicators`).

---

## 5. Gates

| gate | result |
|---|---|
| `cd frontend && npm run typecheck` | clean |
| `cd frontend && npm run smoke` | **16/16** |
| `npm run build` (scratch copy at `…/scratchpad/s15/prod`, `next-env.d.ts` untouched) | green — 16 routes, twice (before and after the item-15 CSS addition) |
| `.venv/bin/python -m pytest` | **142 passed** (unchanged; no backend file touched) |
| `python3 scripts/workflow.py validate` | passed |
| console errors, all three origins, every width | **0 app errors.** The only error line anywhere is the pre-existing `favicon.ico` 404 (chrome-wide, R15's scope — dev and prod both 404); the only warning is Next's dev preload notice. |
| `scrollWidth − clientWidth` at 1564/1440/1280/1024/768/767/600/390, `/ask` · 상세, dev · tailnet · prod | **0** everywhere |

---

## 6. Doc impact appended to `phase.md`

- `frontend` — the ask surface's single 767 existence boundary (`DESKTOP_QUERY`, both modules), the
  retired widget `max-width` guard, the desktop `minmax(0,760px) 340px` bundle + sticky rail, the
  ghost disabled send, the nowrap scrolling tool row, thin thread/quote scrollbars, the ≤767
  full-width quote block, `presets.ts`'s signed-question table with its no-fallback rule, the store's
  leading-whitespace normalization, and the new `useScopePresets` hook shared by the widget and page.
- `product` — 481–767 no longer has a widget or a launcher: it gets the same full-width `/ask` a
  phone gets; a preset chip now sends a full question while showing the served field label; an empty
  scoped widget offers that event's presets, an unscoped one offers nothing.
- `experience` — 「보내기」 is the composer's idle word; a disabled send is a ghost, not a dimmed
  solid; an answer is one growing paragraph; 근거 N건 counts the numbers on the screen; a span-less
  citation is its DART link alone (P7 Q7① closed); one hover rule per control (P7 Q9 closed here).
- `qa` — the `## Regression Checklist` gains this surface's lines (the review appends them);
  build-prompt §6 items 1–20 are the surface's own regression list, all run above.
- `copy` (`docs/reference/design/grounding/copy-inventory.md`, edited in place) — R14 tail: 신규 10건,
  회수 2건, labels server-owned, superseded clauses listed.

## 7. New operator questions

**Q56 · Q57 · Q58** are appended to `phase.md`'s `## Operator Questions`: the 「vocky ⓝ」 that is
actually Next's dev badge (with item 17's measurement); the `/ask` bundle that cannot reach the
signed 1124/760 inside R2's 1120 page shell (1072/708 measured); and the preset chip whose accessible
name is now the sentence while its visible label is a noun phrase (the record signs it; WCAG 2.5.3
「Label in Name」 does not hold for it). None of them was decided inside this slice.
