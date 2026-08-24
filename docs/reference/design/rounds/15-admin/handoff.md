# R15 handoff — Polish: 운영 관제 admin `/ops` (surface 8 of 8 — the last round)

- Round **R15** · slice `P8.S16` (co-work) · apply slice `P8.S17`
- Claude Design project: **"Mijual Design System"** (reads this repository via GitHub)
- Review group for new cards: **`⏳ P8.S16 · Admin`** (R7's originals live under `admin/`)
- **Token freeze**: `foundations/tokens.css` is signed (R8). This round changes no token. The ops
  idiom's one literal stays `#0e1a15` (R7 §6.6).
- Common rules: R10 §0 **except the breakpoint** — this surface is **desktop-only by explicit
  operator decision** (R7: no media queries, `min-width: 1180px`, a narrow window scrolls). That
  decision is not re-opened here unless the operator re-opens it. keep-all / nowrap-mono /
  tabular-nums / hit floors still apply.

**Walk provenance (read this first):** the Chrome bridge disconnected mid-session, and the
authenticated tabs sit behind the ops door's **separate operator credentials, which the
orchestrator does not hold and may not type**. So this walk is (a) the **live SSR of the door**
at `http://127.0.0.1:3000/ops` (renders the signed Access surface: MIJUAL OPS mark · 운영자 ID ·
비밀번호 · 로그인 · the four rule lines), (b) the **complete module source** (`components/ops/*`,
`app/ops/*` — every tab, the chrome, the CSS canon, `copy.ts`'s provenance comments), and (c) the
**R7 landed record** (`rounds/07-admin/output/` + the 7 `admin/*.html` cards in the project).
The authenticated tabs were **not seen rendered with live data** — the operator sees them in the
design session (Claude Design reads this repo) and walks them at the phase acceptance gate;
`P8.S17` verifies in the real runtime. If you want a live-data walk folded in before the session,
log into `/ops` in your Chrome with the extension connected and say so.

## 1. Product context

Routes: `/ops` + five sub-tabs (`gates` · `accuracy` · `conversations` · `users` · `feedback`),
each a complete page inside the ops chrome (MIJUAL OPS bar: 6 tabs · lock chip · KST clock ·
로그아웃 / status footer 운영자 전용 · 순수 관찰 · as-of stamp). Unauthenticated → the door **in
place** (no redirect, no `?next=` — the path never moves). Designed by **R7** (2026-08-21, seven
cards, §6.1–§6.6 all operator-signed): read-only everywhere, raw-English codes/identifiers in
mono, Korean chrome labels, no ornament (no starfield/brackets/glow — 장식의 부재가 표시), alert
ink **only** on 「실행 기록 없음」, judged_by above any accuracy number, rates never without their
decomposition, schema-level anonymity (no account↔conversation join), vocky observation view =
피드백 section (shape decided `P5.S18`, allowlist fields, keyset cursor, GET-only proxy).

**What changed under R7's feet since it was signed — the reason this round exists:**
- **P6 shipped the agent.** 대화 로그 / 익명 세션 / `save_feedback` queue were drawn with
  composition examples and honest `0건` empty states; the product now **stores real
  conversations** (this phase's own walks created several). The tabs render live rows R7 never
  saw drawn.
- **vocky is wired.** `MIJUAL_VOCKY_API_BASE`/`_KEY` are configured in this deployment, so the
  피드백 view's live state is `ok` with real rows — the signed skeleton + 「API shape 확정 대기」
  is now the *unconfigured* state only (and its literal lags its own surface: what an
  unconfigured deployment waits for is the credential, not the shape — flagged in `copy.ts`,
  carried since `P5.S18`).
- **P7/P8 polish** landed product-wide conventions (R10 §0, hover one-rule on reader surfaces,
  R12 auth focus treatment) that this surface predates.

## 2. The walk — 13 findings (code + SSR + record; live-tab items marked ◪)

1. **The live-data era is undrawn (the headline).** ◪ 대화 로그's expanded-row replay (native
   `<details>`, mono detail block), 익명 세션 aggregates, and the `save_feedback` queue were
   designed against composition examples; real turns now exist (multi-sentence cited answers,
   refusals with quotes, scoped turns). Nothing was ever drawn for: a long answer inside the
   mono `.detail` block, citation-quote lists per turn, or a session with dozens of turns. The
   round should draw the replay against real-shaped rows.
2. **The 로그→사용자 cross-link is not the signed 양방향.** R7: 「로그 표의 세션 해시 클릭 →
   사용자 탭의 **그 행**」. `Conversations.tsx` links the session hash to the bare users tab —
   no session parameter, no row targeting, no highlight. The other direction (users → filtered
   log) is wired. Sign what "그 행" means concretely (filter? anchor? highlight?).
3. **「API shape 확정 대기」 lags reality** (carried, flagged in code): the unconfigured state
   waits for a `vk_` credential, not a shape. Rewriting a signed line is a design change — this
   is the round where it can be re-signed (or kept, with the raw `state` code doing the work).
4. **Users 샘플 로드 여부 has no backing fact** (carried from P5, an operator decision): the
   column is data-driven and currently never renders; building the backing means a
   holding-provenance column — a new behavioural fact about readers. Decide: build, drop from
   the drawing, or keep data-driven.
5. **Focus treatment predates R12.** The door inputs and every ops filter/pager control rely on
   default browser focus; the reader product signed explicit `:focus-visible` treatment (R12).
   One rule for ops keyboard focus is this round's to sign — or explicitly not.
6. **Hover coverage is partial**: tabs/links/logout/expand brighten; `.pageButton` and filter
   controls have no hover; the lock chip none (it is not interactive — fine). One rule per R14
   f11's precedent, adapted to ops.
7. **The ops bar at 1180 is one row of eight things** (mark · 6 tabs · chip · clock · 로그아웃)
   — at the min-width it is tight but holds (code reading; no overflow guard beyond nowrap).
   ◪ Worth one measured look at 1180 and 1440 in the session's cards.
8. **Alert-ink honesty check**: with beat never deployed locally, Overview's 최근 실행 interleaves
   *every* scheduled due-instant as an alert 「실행 기록 없음」 row — correct per R7 (침묵 금지),
   but ◪ the live table is *mostly alert rows*, which reads as a wall of red. R7 anticipated
   single missing rows; decide whether a long unbroken run of them collapses (e.g. count line)
   or stays row-per-miss (the honest default — a design gap to sign either way).
9. **`Conversations` empty-state vs live rows**: the tab prints `{count}건` under an empty table
   (signed: the count and unit are the honest rendering of nothing) — with live rows this line
   still renders below a *non-empty* table as `N건` note only when rows.length is 0; fine. But
   the **filters row renders even with zero stored conversations** — harmless; noted only.
10. **`Accuracy`'s correction-recall tile prints its whole payload** (`recall` appears both as
    the tile value and again in the key-value lines) — a small doubled fact; the record's card
    drew四 tiles cleanly. Cosmetic; sign the intended line set.
11. **Door duplication in `<title>`**: the tab title is `MIJUAL OPS` and the door mark is
    `MIJUAL OPS` — SSR shows the pair; correct per R7 (metadata + mark), noted as not-a-bug.
12. **`favicon.ico` 404** (carried from R14 §7 — chrome-wide, and this is the chrome round it
    was parked for): every route 404s the favicon; the browser tab shows the default globe on an
    operator console titled MIJUAL OPS. Decide: ship a favicon this round (an asset decision —
    the wordmark exists in `assets/`), or explicitly defer past P8.
13. **Decisions panel coupling** (carried): 가동 전 미결 parses `docs/current/decisions.md` for
    `- **Open…` bullets — versioning that doc reshapes the panel. Known, structural, not this
    round's to change; listed so the cards don't redraw it away.

## 2b. Questions for the operator (answer in the design session)

- **Q-A (Finding 1)** — should R15 re-draw 대화 로그/사용자/피드백 against **live-shaped data**
  (real replay anatomy, long answers, citation lists), or keep R7's composition-example drawings
  and only sign the deltas below?
- **Q-B (Finding 2)** — 로그 → 사용자 "그 행": what does the signed 양방향 mean concretely?
- **Q-C (Finding 3)** — re-sign the unconfigured-state line or keep 「API shape 확정 대기」?
- **Q-D (Finding 4)** — 샘플 로드 여부: build the backing fact, drop the column from the
  drawing, or keep it data-driven-and-absent?
- **Q-E (Findings 5–6)** — sign one ops focus+hover rule (R12/R14 precedent), or leave ops on
  browser defaults as part of its "counter-back" idiom?
- **Q-F (Finding 8)** — a long run of 「실행 기록 없음」 rows: row-per-miss stays, or a signed
  collapse? **Q-G (Finding 12)** — favicon: this round or explicitly deferred?

## 3. What to design (required cards, group `⏳ P8.S16 · Admin`)

Draw only what this round changes — R7's cards stand for everything else (RESPECT THE DESIGN;
R15 supersedes only what it explicitly re-signs):

1. **Conversations (live era)** — the log table + one expanded replay with a real-shaped cited
   answer and a refusal; the save_feedback queue with a real-shaped row; the 그 행 cross-link
   resolved per Q-B.
2. **Users (live era)** — reader accounts (real columns incl. the Q-D outcome) + 익명 세션 rows
   with live-shaped aggregates.
3. **Feedback (`ok` state)** — the vocky view with real rows (allowlist columns), plus the
   re-signed (or kept) unconfigured state per Q-C.
4. **Overview** — only if Q-F changes the missing-run rendering; otherwise reference R7's card.
5. **Focus/hover spec** — one small card or a §-block in the build-prompt per Q-E (no new
   tokens).
6. **Door** — only if Q-G ships a favicon or Q-E touches its focus treatment; otherwise R7's
   Access card stands.

With the cards, land in this round's `output/`: `result.md` (decisions Q-A…Q-G + any session
revisions) and `build-prompt.md` (binding contract for `P8.S17`, with a numbered §6 regression
checklist — including the R7 hard rules re-verified: read-only everywhere, raw codes, judged_by
above numbers, alert only on missing runs, no ornament, schema-level anonymity, desktop-only).

## 4. Hard rules (restated, unchanged)

R7 §6.1–§6.6 all stand: 게이트 판정을 바꾸는 액션 금지 · suppression 한국어 발명 금지 · vocky
필드명 선구현 금지 · PII 저장 금지 (스키마 수준) · 발명 수치 금지 · 미실행 beat 침묵 금지 ·
98.6% judged_by 없이 렌더 금지 · 모바일 대응 없음 (명시적) · 장식 금지 · 계정↔대화 조인 금지 ·
컴포넌트 단편 화면 금지. Tokens frozen (R8); `#0e1a15` stays the one sanctioned literal. All new
Korean = dated, signed exceptions in `result.md`; codes and identifiers stay raw English mono.
