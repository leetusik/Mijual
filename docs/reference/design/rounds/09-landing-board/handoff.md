# Design Handoff — Round 9: Polish — Landing 관제 현황판 + Board

- Round: **R9** (P8 polish pass, surface 2 of 8) · slice `P8.S4` · written 2026-08-23
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main branch, pushed at handoff commit)
- Builds on: **R2/R2.1 (landing + chrome), R3 §board strip (추후결정), R4 (SearchRow / typeahead
  as re-used on the hero, P7), R8 (chrome, just applied)** as signed, plus the P7 operator
  overrides in `docs/reference/design/SIGNOFF.md` / `docs/current/frontend.md`. Those rounds are
  **locked context** except where this handoff explicitly opens them; R9 is a **polish round — no
  new features** except the one the operator ordered at the gate (board auto-refresh, §2) — and,
  per `SIGNOFF.md` precedence, what R9 signs supersedes the parts of R2/R3 it touches.

## 1. Product context

미주알's landing `/` is the 관제 현황판: hero (H1 「내 종목 조회」 + subtitle + the shared search row
+ a mono stat line) over the cosmos, two anchor cards (retrospective 소멸 가치 · countdown + four
stats), the 소멸주의보 strip, and the board panel 「소멸 카운트다운」 — freshness chip, four tabs,
ranked rows in a 30-row window with 펼치기, then the 진행 중 and 추후결정 strips. R8 just removed the
sample link under the board and re-cut the chrome around it.

The operator walked the landing on 2026-08-23 (13 findings in `works/phases/active/P8/phase.md`
§"R9 walk — surface 2", screenshots in the session record) and answered at the gate. Their
answers below are **direction** (what to fix) and **REFERENCE — data, not a proposal** for how.
Claude Design + the operator decide how it looks.

## 2. Scope checklist — what this round must cover

Operator decisions (2026-08-23, `P8.S4` gate 1). Everything numbered is a walk finding the
operator accepted as "fix — Claude Design decides how" (their words: *"default ok"* by way of
answering only the exceptions):

- [ ] **Board window = 15 rows.** Operator on P7 Q3: *"q3: 15"*. The ranked list shows **15**
      rows per window and 펼치기 discloses the next 15 (today 30 / +30, `WINDOW_STEP` in
      `Board.tsx`). Design the board for a 15-row first screen.
- [ ] **Board data auto-refreshes while the page is open.** Operator on P7 Q5: *"q5: refresh"*.
      Read as **automatic** refresh on an interval (not a manual control) — the orchestrator's
      stated assumption, unchallenged. The session decides what the reader *sees*: how the
      freshness chip 「기준 … KST」 reflects a refresh, whether rows that change are marked, what
      happens to an open 펼치기 window / tab / expanded strip across a refresh, and the
      reduced-motion rule. Interval and fetch mechanics are the apply slice's; **no spinner** (R1).
- [ ] **1 · Whole-row click target + row hover.** Today only the corp name (`a.corp`) and `↗` are
      links; the row is inert with no hover rule. The row becomes the event's click target, with a
      hover/focus state; `↗` stays the DART 원문 link (R2 anatomy otherwise locked: RightsChip ·
      corp · ↗ · key date · 청약/발행가 cell · StateBadge · DDay).
- [ ] **2 / 3 · The board explains its numbers.** Tab counts are whole-board (전체 488 · 유증 50 ·
      CB 422 · 매수청구 16, R3) while the rows are the countdown subset (356 today) and the footer
      「356건 펼치기」 is a *remaining* count that shrinks as you expand. Make shown / remaining /
      total legible — what the tab number means, how many rows are on screen, how many are left.
      Copy for these labels is **in play** (none exists).
- [ ] **4 · Strip toggles read their state** — 펼치기 ↔ 접기 (or the session's equivalent) for the
      진행 중 and 추후결정 strips; a way back without switching tabs.
- [ ] **5 · Expanded strip rows align with the board columns** (today ~14px right of the board's
      chip/corp/label columns); the 추후결정 row's **empty date slot** after 「신주인수권증서 매매 마감」
      reads as a missing value — decide how a dateless row shows its key-date cell.
- [ ] **6 · CB row anatomy** — 422 of 488 rows have no 청약/발행가 cell and leave ~450px of empty row
      between the key date and the D-day at 1512px. Re-cut the row so the board isn't mostly
      whitespace on desktop (column plan, what fills or collapses) — within the locked anatomy.
- [ ] **7 · D-day tiers** — today three unexplained colour tiers (alert red ≤ D-6 · white · dim
      ≥ D-37). A legend, a simpler rule, or a visible threshold — design's call; the alert hue stays
      reserved for 소멸·기한 (R1).
- [ ] **8 · 소멸주의보 and the board agree** — the strip names 퓨쳐켐 as 「가장 빠른 청약 마감 2026-09-04」
      while the board's first D-2 row is 계양전기 (three rows tie on 09-04). Same ordering rule in
      both, or the strip names the tie.
- [ ] **9 · Drop 「읽은 실적보고서 69건」 from the countdown card.** Operator: *"9. drop."* The card
      keeps 감시 중 이벤트 · 30일 이내 마감 · 소멸 앞둔 신주인수권; re-cut the 2×2 grid to three stats
      (the session decides the arrangement). The hero's mono stat line is unaffected.
- [ ] **10 · Mobile 390 line breaks** — hero subtitle orphan (「…조회합니 / 다」), the 소멸주의보 mono date
      split across lines (「2026-09- / 04」), the 진행 중 strip's 펼치기 dropping alone under its
      sentence. Unbreakable dates; balanced wraps; where the strip's button sits at 390.
- [ ] **11 · Hero plain-Enter vs typeahead** — typing 「삼성」 offers 삼성에스디에스 / 삼성제약, plain Enter
      lands on `/stocks?q=삼성` → 「'삼성'와 일치하는 종목이 없습니다」. Decide the hero-side rule (plain
      Enter on a prefix takes the first candidate? opens the candidates on `/stocks`? …). The `/stocks`
      page itself and its copy (incl. the wrong particle 와→과) belong to **R11 / surface 4** — note
      it, don't design it here.
- [ ] **13 · Board tabs hover** (P7 Q9) — operator: *"q9-11: idk"* → **left to the session**: give
      the four tabs a hover state or rule that they have none; same for P7 Q10 (focused hairline vs
      candidate panel edge) and Q11 (the 481px boundary between SearchRow 44px and Board 32px
      controls) — decide or explicitly leave, and log which.
- [ ] **Cards refreshed for everything above, desktop (1512/1280) and 390px mobile.**

**Explicitly NOT in this round (operator decisions at the same gate):** the hero H1 「내 종목 조회」
stays — *"q6 #12: its intended."*; the gate-cost + disclaimer sentences R8 removed from the footer
are **dropped, not relocated** — *"p8 q5: drop."* (no new placement on the landing; the apply slice
deletes the constants); finding 12 (typeahead panel over the stat line) — leave; `/stocks` page
fixes → R11.

Cross-cutting (every round): Korean-only surface; mobile-first; a11y/reduced-motion floor; no new
features beyond the operator-ordered auto-refresh.

## 3. Locked vs. in play

**Locked:** R1 tokens/type/spacing/motion/square-hairline system and the `.cosmos` scope (R2.1);
Pretendard for Korean prose, IBM Plex Mono for numerals/dates only; the hero composition (H1 —
by operator decision — subtitle, shared search row, mono stat line, cosmos + orbits with the P7
ring clip); the two anchor cards' existence and the retrospective card's content; the 소멸주의보
strip's existence and alert hue; the board panel's title, freshness chip and the four tabs with
whole-board counts; R2's row anatomy elements (what is in a row — not their column plan); the R3
strips' existence; R8 chrome; the P7 focus split; all product copy except the strings §2 names in
play.

**In play:** everything in §2 — the board's column plan and row geometry (desktop + mobile), the
15-row window's footer / count labels (**Korean copy in play — the dated exception of this round,
2026-08-23**: count/shown/remaining labels, 접기, any refresh-state label), row hover/focus, strip
toggles and alignment, the dateless row, D-day tiers, the countdown card at three stats, the
auto-refresh's visible behaviour, the 390px wraps, the hero plain-Enter rule, and tabs hover /
P7 Q10–Q11 (decide or leave, log it). A token change, if any, is a **new `foundations/tokens.css`
from the session** — the repo's copy is re-vendored from the landed file, never hand-edited.

## 4. Where to look — real paths, real data shapes

- **Landing as built:** `frontend/app/page.tsx` (fetches `/board/summary` + `/board` at request
  time, `connection()`), `frontend/components/landing/` — `Hero.tsx`, `Cosmos.tsx`, `Anchor.tsx`
  (`RetrospectiveAnchor`), `Countdown.tsx` (ticking; reduced motion stops the interval),
  `EstimateValue.tsx`, `LapseNotice.tsx` (소멸주의보), `Board.tsx` (`WINDOW_STEP = 30`, tabs as
  `<button aria-pressed>`, the two strips), `BoardRow.tsx` (row anatomy, `a.corp` + `↗`),
  `copy.ts` (every landing string with its citation — `STAT_REPORTS_KO = "읽은 실적보고서"` is the
  one to drop), the `.module.css` files beside them.
- **Search row (hero + surface 4):** `frontend/components/lookup/SearchRow.tsx` + `.module.css`
  (P7 typeahead: debounce, ↑/↓, Enter-on-highlight, Esc); the `/stocks` page it submits to is
  `frontend/app/stocks/page.tsx` (R11's, not this round's).
- **Backend shapes:** `src/mijual/web/routers/board.py` (`/board`, `/board/summary` — the stat
  numbers incl. 읽은 실적보고서, 소멸주의보 pick, freshness 기준시각), `frontend/lib/api.ts`.
- **Landed records:** `docs/reference/design/rounds/02-landing-chrome/output/` (R2 hero, anchors,
  board, rows; R2.1 cosmos re-cut), `rounds/03-event-detail/output/` (§board strip 추후결정),
  `rounds/04-lookup/output/` (SearchRow), `rounds/08-foundations-chrome/output/` (R8 chrome the
  landing now wears). P7 overrides: `docs/reference/design/SIGNOFF.md` (30-row window, typeahead
  on the hero, ring clip).
- **Walk findings + operator answers:** `works/phases/active/P8/phase.md` §"R9 walk — surface 2"
  and §"R9 interview — operator answers".
- **Terminology / product truth:** `docs/current/product.md`, `docs/current/frontend.md`
  (supersession table), `docs/reference/design/SIGNOFF.md`.

Missing real content → ask for it; do not invent it.

## 5. Required outputs (a round is incomplete without all three)

1. **The card set** — line-1 `@dsCard` markers, review-time groups **`⏳ P8.S4 · Landing`** and
   **`⏳ P8.S4 · Components`**, one card per reviewable unit (never a monolith). Required card
   paths (split further if useful; paths are stable across the post-approval regroup):

   - `landing/Board.html` — the panel at 15 rows: tabs (+ hover rule), count/shown/remaining
     labels, 펼치기, desktop column plan incl. CB rows, row hover/focus, D-day tiers (+ legend if
     any), freshness chip with the refresh state
   - `landing/BoardRow.html` — row anatomy variants: 유증 (청약 + 발행가 cell), CB, 매수청구,
     진행 중 (D+n), 추후결정 (dateless), each at desktop + 390px, idle / hover / focus
   - `landing/BoardStrips.html` — 진행 중 + 추후결정 strips collapsed/expanded with aligned rows and
     stateful toggles, desktop + 390px
   - `landing/Anchors.html` — countdown card at three stats + the retrospective card beside it,
     desktop + 390px; 소멸주의보 strip with the unbreakable date and the tie rule
   - `landing/HeroSearch.html` — the hero at 390px (subtitle wrap) and the plain-Enter rule for a
     prefix (what the reader sees)
   - `landing/Refresh.html` — what a refresh looks like over time (before / during / after, rows
     that changed, window/tab/strip persistence, reduced motion)
   - `foundations/tokens.css` — **only if tokens change**; then the full file, linked by the cards

2. **A record of what was designed** with every departure logged — `result.md` for this round
   (what changed vs R2/R3, the count-label copy with each string listed, the D-day rule, the
   CB row plan, what was left for tabs hover / P7 Q10–Q11).

3. **An implementation contract** complete enough to build from without inventing anything —
   `build-prompt.md` (column plan + geometry, tokens, states, copy table, the refresh's visible
   contract, mobile rules, the hero Enter rule). If the session produces Claude Design's own
   handoff bundle, that **is** the record and the contract — land as-is.

**Definition of done: the cards appear in the Design System pane** under the `⏳ P8.S4 · …`
groups, and the record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. **What a reader should see when the board refreshes** — silent swap with a chip update, a
   one-line 「갱신됨」 notice, row-level change marks — and what survives (window, tab, strips).
2. **The CB row's column plan** — collapse the 청약/발행가 column when a tab has none, fill it with
   something the row already knows (e.g. the conversion window), or narrow the board.
3. **D-day tiers** — keep three tiers with a legend, or reduce to alert-vs-normal.
4. **The hero's plain-Enter rule for a prefix** with candidates visible.
5. **Count labels' wording** — the reader needs shown / remaining / total without three numbers
   in a row; REFERENCE data only: today's strings are 「N건」 + 「펼치기」.

## 7. Operator setup + definition of done

Same project ("Mijual Design System"), Connect GitHub already in place — pull latest `main` in
the session so it sees this handoff, the walk findings and the landed R1–R8 records. When the
cards are up and the record + contract exist, tell the orchestrator to resume; read-back, landing,
SIGNOFF, and the regroup (retiring the `⏳ P8.S4 ·` address) follow. Approval must be literal.
Then `P8.S5` applies R9 from the landed `build-prompt.md`.
