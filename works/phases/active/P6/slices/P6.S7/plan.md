# Plan — P6.S7: design-fidelity verification in a real browser (RESPECT THE DESIGN)

## Goal

Run the whole product live — real Postgres corpus, real Gemini agent, production
frontend build, headless browser — and check every R6 element against the signed
contract, the way `P5.S19` did for P5. Fix faithful-implementation nits **in
code** (never in the landed record), give every flagged item from this phase a
disposition (*verified as described* / *fixed* / *catalogued for the operator*),
and leave `P6.REVIEW` a measured, not asserted, picture.

## Method (the `P5.S19` precedent — see its section in `works/phases/active/P5/phase.md`)

- Stack: uvicorn over the operator's dev Postgres (**first**: the `P6.S1`
  conversation tables do not exist there yet — S4 recorded this; create them
  with the schema layer's own `create_all` path, additive and idempotent, and
  record that P4 inherits this as a deploy step), a **live** agent client
  (`GEMINI_API_KEY` from `.env` — no `agent_client` override), and
  `npm run build && npm run start`. Headless Chrome over CDP; screenshots into
  the session scratchpad.
- Check against **the round's own contract**: R6's `build-prompt.md` +
  `result.md`, clause by clause. Keep a check table in `result.md`
  (`P5.S19`-style: stage · checks · result), widths **1440 / 768 / 481 / 480 /
  390** at minimum (the 480/481 boundary is signed: widget+launcher exist at
  481, none at 480).
- **Live agent spend is authorized but bounded**: on the order of a dozen
  turns, chosen to cover the families below; record the ▷ ledger total in
  `result.md` (D-4 reporting — calls · tokens · thinking level · ▷ estimated,
  never billed).

## Read first

`works/phases/active/P6/phase.md` end to end — the Constraints are the
acceptance criteria, and **notes 20–23 carry the accumulated flags this slice
must disposition** (listed below so none is lost), plus
`docs/reference/design/rounds/06-explain/output/build-prompt.md` +
`result.md` (READ-ONLY), and `works/phases/active/P5/phase.md` §`P5.S19` for
the method and the standing P5 rules (`.mono` split rule, overflow rules).

## The live conversation set (cover all of these, one turn can cover several)

1. Scoped question from an event detail (질문 스트립 press) — scope chip,
   tool rows, chips-with-sentences, footer, 완료 fade.
2. 전체 공시 search question (multi-candidate) — search fact row format.
3. 철회 event question — the 3-part refusal **with a 근거 칩** on the status
   fact, no alert color.
4. 확정 전 금액 question — known facts cited, amount refused; **note 20's
   open copy point**: the live answer once stated 「예정발행가액은
   3,200원입니다」 — judge it beside the detail page (the field is
   gate-passing and page-rendered, so it is a published planned figure, not a
   확정 전 금액 claim — confirm or catalogue).
5. 계산 요청 — fixed redirect sentence, zero forced tool calls.
6. 0건 search — signed 찾지 못했습니다 + 관제 현황판 link, no guess.
7. 포트폴리오 question anonymous — sample, labelled 구성 예시.
8. 의견 (feedback) — tool row, surface confirmation copy, then the row in
   the ops 피드백 tab.
9. 중지 mid-stream — partial kept dimmed, inset row + 재시도; and a retry.
10. Widget → `/ask` mid-stream (external-link) — streaming survives the
    navigation (R6's 끊김 없음 — the store owns the fetch; measure it).

## The static/behavioral sweep

- **Launcher**: 68×50 + tail geometry, the **ring reading test** (two half
  rings read as one ring passing in front of and behind the planet — a flat
  sticker is the recorded bug), band loop, hover (mark-only 1.35, frame
  border/bg change incl. tail), active 1.15, open state behind the widget,
  **reduced-motion stops band + drift + transitions + hover scale**, and the
  motion exception leaks onto no data surface.
- **Widget**: 440×620, opaque `#0e1a15` (nothing bleeds through over the
  cosmos), fixed bottom-right, no backdrop, page layout unchanged beneath,
  header external-link + × both 28px, launcher hidden while open.
- **SSE states**: 답변 준비 중 button-text swap (no spinner/dots anywhere),
  streaming caret 7×15 `--live` 1s steps(1) (stops under reduced-motion),
  완료 footer fades in `--dur-base`, 중단 keeps partial at `--ink-2`.
- **Citations**: chip style (mono 10px, `--live` ink, the rgba border), same
  근거 = same 번호, tap → in-place block (`--surface-inset`, left 2px
  `--live`, verbatim quote + `DART 원문 {rcept_no} ↗`), re-tap closes,
  API-tier sentence for no-span facts. **Verbatim check**: pick two quotes
  and match them byte-for-byte against the detail page / DART payload.
- **Never-compute spot check**: every numeral in two live answers exists on
  the event detail page or portfolio payload; derived values show 「추정」.
- **Page**: frameless chat (no panel/bracket), single 340 rail, no launcher,
  nav third slot + footer bottom link land with thread intact.
- **Mobile 390/480**: full-width page only, sticky 44px input bar, one-line
  preset scroll ≥44px targets, 180px-capped full-width citation blocks, tool
  rows kept, 뒤로가기 keeps the conversation, **0px horizontal overflow** on
  every touched page; 481px boundary flips correctly.
- **Ops loop closes**: after the live turns, 대화 로그 shows the turns as the
  reader saw them (kind, 거절 카테고리 filter works with the five Korean
  names), 익명 세션 aggregates, 피드백 holds the saved row — all read-only.
- **Copy audit**: no quota/남은 질문 string anywhere, the 익명 저장 session
  line present, no 「저장 이력 없음」/「탭 닫으면 사라집니다」, no invented
  Korean (grep the new copy files against their provenance comments).
- **Corner**: no vocky collision (vocky is footer-only — confirm nothing
  else occupies the corner on any reader page).

## Flags to disposition (from notes 20–23 — every one gets a line in `result.md`)

- 확정 전 「예정발행가액 3,200원」 copy point (note 20).
- `BOARD_POINTER_HREF` dead route — confirm nothing renders it (S5's
  `links.ts` maps kinds through `ROUTES`).
- 필드로 이동 footer link: signed but no wire kind / no field anchors —
  catalogue for the operator (or fix if a faithful cheap path exists —
  adding an anchor is frontend-only; judge it).
- Footer with up to 8 links / multi-rcept_no `·` separator — fidelity call
  beside the signed format.
- Reused strings: 「직접 질문 입력 →」 send button, 「AI 질문」 accessible
  names (note 22); preset chip text = served `korean_name` verbatim +
  R6's 실권주 sentence (note 23) — confirm against the record.
- Mobile menu row order: §Mobile 「메뉴 첫 행」 vs §Surfaces nav-third
  (note 23) — judge which reading the record as a whole supports; it is a
  one-line change if you conclude 첫 행, otherwise catalogue the
  contradiction for the operator.
- SSE through a production `next start` proxy with the **live** agent (S4
  measured scripted turns; confirm nothing buffers with real tool-round
  gaps; no heartbeat exists — note the longest observed gap for P4).

## Boundaries

- Fix **code only**, and only toward the signed design — no restyling, no
  improvements, no new Korean copy, no token edits, no
  `docs/reference/design/` change, no backend behavior change beyond a
  faithful-implementation fix (record any backend touch explicitly).
- Keep the suites green after any fix: `pytest` (136), `npm run build` ·
  `typecheck` · `smoke`.
- No new ops surface, no schema change (creating the already-defined tables
  in the dev DB is deployment, not schema change).

## Deliverables

- `result.md`: the check table, the live ▷ ledger, every fix with its
  before/after, the disposition table for every flag above, operator
  questions consolidated in one section.
- `phase.md`: findings + fixes appended (durable notes), Doc impact line(s)
  (`qa` — the method + new baseline; `experience`/`frontend` if fixes moved
  anything; `operations` — the dev-DB table creation step P4 inherits).
- `python3 scripts/workflow.py validate` passes. No commits, no status
  transitions.
