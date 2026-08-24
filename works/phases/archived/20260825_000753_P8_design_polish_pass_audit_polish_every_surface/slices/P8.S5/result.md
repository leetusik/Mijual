# Result — P8.S5: Apply R9 — landing 관제 현황판 + board

R9 is built as signed and verified in the operator's runtime on **both origins in `next dev` and in a
production build**, desktop (1512 / 1280 / 1119 / 1024 / 802 / 768) and 390. Every box of
`build-prompt.md` §11 passes. No design gap had to be invented; one design element the contract does
not carry (the countdown card's caption) is catalogued as a question rather than minted — §6 below.

## 1. What changed (10 items, in the build-prompt's own order)

| # | §  | change |
|---|----|--------|
| 1 | §9 | **`components/landing/copy.ts`** — the **14 new constants verbatim** (`TAB_NOTE_KO`, `shownLine.{before,middle,after}`, `moreKo`, `remainingKo`, `collapseToFirstKo`, `COLLAPSE_KO`, `REFRESHED_KO`, `LEGEND_{DDAY,SOON,NEAR,FAR}_KO`, `tieCountKo`), each cited to R9 §4–§9; `EXPAND_KO`'s comment rewritten (R2's "a 접기 label is copy nobody signed" is **superseded** — R9 signed it); **`STAT_REPORTS_KO` deleted**. In `components/chrome/copy.ts`, **P8 Q5 "drop." executed**: `POSITIONING_KO`, `PROVENANCE_KO`, `GATE_COST_VALUE_KO`, `GATE_COST_TAIL_KO`, `DISCLAIMER_KO` deleted (grepped first — nothing imported any of them; the same-named constants in `lookup/copy.ts` and `event/copy.ts` are those surfaces' own and are untouched). All 14 registered in `grounding/copy-inventory.md` §"R9 additions" with the same "a regeneration drops this — re-append it" note R8's section carries. |
| 2 | §2–§5 | **`Board.module.css`** — rewritten around `landing/r9-board.css` (ported, not re-derived): row grid `76 · minmax(180,1fr) · 240 · 190 · 96` with `[data-extras="none"]` → `76 · 1fr · 300 · 96` + `.extras{display:none}`; gap 12, `min-height:44px`, `align-items:center`, padding 8×12 on `margin-inline:-12px`, dashed separators; ≤1119 `72 · 1fr · 200 · 170 · 96` / `72 · 1fr · 240 · 96`; ≤767 the two-line row (`minmax(0,1fr) auto`, D-day right on line 1, `.rmeta` spanning, `extras:not(:empty)::before{content:"·"}`). Row states: hover raised + corp underline, `:focus-within` raised + `outline:2px --focus-ring` at `-1px`, `:active` inset, `.changed` `inset 2px 0 0 --live` + a `--dur-base` fade on the changed values only. Stretched link (`a.corp::after`), `.dart{position:relative;z-index:1}`. Tabs hover/focus-visible. Meta line + legend (`lg0..lg3`). Footer `.more` / `.btn` **36px ≥768 · 44px ≤767** (the 32px rule and the 481px seam retired) / `.rest` / `.flat`. Strips bled to the panel edge (`margin-inline:-24px`) with `.sbody` putting expanded rows on the board's 24px start line. |
| 3 | §2–§3 | **`BoardRow.tsx`** — R2's DOM order kept, now inside R9's two wrappers (`.top` = chip + corpCell, `.rmeta` = when + extras, `.rail` = D-day); `data-event-id` on the `li` (the refresh's identity in the DOM); `changed?: RowChange` marks the row and flags which of the three values fade; a row with no `rcept_no` keeps its `span` (no stretched target — nothing to open); a dateless row renders **the label only** (already true, kept) with `StateBadge tbd` in the rail. |
| 4 | §1·§4·§5 | **`Board.tsx`** — `WINDOW_STEP` **30 → 15** (doc comment rewritten: the operator's "q3: 15" at the R9 gate, P7 Q3 closed); `data-extras` computed **per panel** (the tab's ranked rows + both strips) and passed to the strips so one panel never runs two column systems; the meta line (`TAB_NOTE_KO · shownLine`, `{ranked}` = `rows.length`, `{shown}` = `min(shown, rows.length)`, both mono) + the four-step legend; the footer's three controls (`moreKo(15)` + `remainingKo(hidden)` while `hidden > 0`, `collapseToFirstKo(15)` while `shown > 15`, nothing when neither); strip toggle `open ? COLLAPSE_KO : EXPAND_KO` with `aria-expanded`. Tab switch still resets the window; a refresh does not. |
| 5 | §7 | **Auto-refresh** — `REFRESH_INTERVAL_MS = 60_000` (one constant, cited to Q10), `getBoard()` from the browser through the same-origin rewrite; paused while `document.hidden` and read once immediately on `visibilitychange` → visible; a **new `as_of`** swaps rows/counts/strips, shows `REFRESHED_KO` beside the chip until the next such refresh, and edges the changed rows (`event_id` + a `countdown.dday` / `countdown.date` / `label_ko` / `offering` diff, or newly inside the window) for one cycle; an **unchanged `as_of`** does nothing at all; a failure is silent and retries next tick; tab / window (clamped to the new list, floor 15) / open strips / scroll / focus survive, and a focused row that vanished hands focus to its list. `page.tsx` keeps its server fetch, so the hero and countdown never remount. |
| 6 | §6 | **`Anchor.tsx` / `.module.css`** — the stats card is **three rows** (label left / value right, `padding:9px 0`, dashed separators, none under the last, value mono 17/600 `nowrap`) under a dashed hairline; the 2×2 grid is gone and `performance_reports` is no longer rendered (the contract field stays). |
| 7 | §6 | **`LapseNotice.tsx`** — `tie_count > 1` → `tieCountKo(n)` in the `{corp}` slot, else `corp_name`; the tie phrase `nowrap` (new one-rule `LapseNotice.module.css`) and `LapseAlert`'s `.num` gains `white-space: nowrap` so the mono date stops splitting at 390. The sentence template is unchanged. |
| 8 | §6/Q11 | **Backend `next_lapse.tie_count`** — `reads.py` `load_summary` counts the entries of the ordered `pending` list that share `soonest[1]`; `present/summary.py` carries `next_lapse_tie_count` through `board_summary(...)` and adds the key **only when `next_lapse` exists**; `lib/types.ts` gains `tie_count?: number`. One assertion added to the existing summary test (fixture has one pending offering → `tie_count == 1`). Live: `{"date": "2026-09-04", "corp_name": "퓨쳐켐", "tie_count": 3}`. |
| 9 | §8 | **`lookup/SearchRow.tsx`** — the four-step Enter rule (no candidates → plain GET submit; a highlight → go; an exact 종목명/종목코드 match → go on the first Enter; otherwise **select the first candidate**, no navigation). It lives in the one shared row, so the hero and R4's header cannot fork; the `/stocks` page and its copy are untouched (R11). |
| 10 | §8·§10 | **390 line breaks** — `word-break: keep-all` on the landing's `<main>` (`app/page.module.css` `.landing`, scoped there rather than `app/shell.css` so the surfaces R9 did not design are left to their own rounds), `text-wrap: balance` on the hero subtitle, and `nowrap` on every landing mono value (row date, 청약 date, 발행가 확정 전 chip, strip counts, stats values, 소멸주의보 date + tie phrase). |

Untouched, deliberately: `AccountSlot.tsx` / the chrome (Q12 is a later slice), the `/stocks` page (R11), the hero H1 · stat line · orbits, the retrospective card, `Countdown.tsx`, `DDay` / `StateBadge` / `RightsChip`, and everything under `rounds/*/output/`.

## 2. Validation

| command | result |
|---|---|
| `.venv/bin/python -m pytest` | **142 passed** |
| `cd frontend && npm run typecheck` | clean |
| `cd frontend && npm run smoke` | **16/16** |
| `cd frontend && npm run build` | ✓ (15/15 pages; `next-env.d.ts` rewritten by the build and restored with `git checkout --` both times) |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

## 3. Build-prompt §11 완료 확인 — every box

Harness: `P7.S9`'s `cdp.mjs` (headless Chrome over raw CDP, fresh profile per run), reused verbatim as
`P8.S1`/`P8.S3` did. **dev** = `next dev` on `127.0.0.1:3000` **and** `100.77.164.42:3000` (tailnet);
**prod** = `npm run build` + `next start -p 3100` with `MIJUAL_API_ORIGIN=http://127.0.0.1:8000`.

| §11 box | measurement | dev 127 | tailnet | prod |
|---|---|---|---|---|
| 15행 + 「15건 더 보기」 + 「남은 N건」 → click → 30 + 「처음 15건으로 접기」 | 15 → footer `15건 더 보기 · 남은 371건` → click → **30** + `남은 356건` + `처음 15건으로 접기` → click → back to 15 | ✓ | ✓ | ✓ |
| 탭 숫자(488) ≠ 메타 줄의 랭킹 수(386), 둘 다 설명된 채로 | 「탭 숫자는 감시 중 전체 건수입니다 · 아래 목록은 카운트다운 **386**건 중 **15**건」 under a 전체 **488** tab | ✓ | ✓ | ✓ |
| CB 탭: 키 날짜↔D-day 사이 빈 구간 없음, D-day가 패널 우변에 | `data-extras="none"`, key date **859–1159** (300), rail **1236–1267**; panel content right edge = 1268 → flush. R9's own departure 6 (the CB lane stays wide) holds: the slack is inside the widened key-date column, not between the columns | ✓ | ✓ | ✓ |
| 보드 행과 펼친 스트립 행의 열 x좌표 일치 | board / 진행 중 / 추후결정 rows all `chip 245‑280 · corp 333‑705 · when 717‑957 · extras 969‑1159 · rail →1267`; **`railRight` unique count = 1 at every width** (1512/1280/1119/1024/802/768/767/481/390) | ✓ | ✓ | ✓ |
| 행 ≥44px, 값 수직 중앙, D-day 줄바꿈 없음 | every row exactly **44px** (min = max), `align-items:center`, D-day `nowrap`, 0 document overflow at all nine widths | ✓ | ✓ | ✓ |
| 행 아무 곳이나 클릭 → 상세 · `↗` → DART · Tab → 행 둘레 링 | click at 62 % of the row width (the extras area) → `/events/20260724000546`; `elementFromPoint` there = the stretched `A`; the `↗` hit-tests as **itself** (`z-index:1`, `rel=noreferrer`, `aria-label 계양전기 DART 원문`); focus in the row → row `outline 2px #8fb2e8 / -1px` + raised bg; hover → raised + underline; press → `--surface-inset` | ✓ | ✓ | ✓ |
| 스트립 펼침 → 「접기」, 행 정렬 | both toggles flip 펼치기 ↔ **접기** with `aria-expanded` agreeing; expanded rows share the board's x-coordinates (above) | ✓ | ✓ | ✓ |
| 추후결정 행 = 라벨만 + 레일의 「추후결정」 | all four tbd rows: `when` has **1 child** (the label; no date span, no dash), rail = 「추후결정」 | ✓ | ✓ | ✓ |
| D-day 범례 4단, 색이 R1 사다리와 일치 | `D-DAY` #fff on `--alert` · `D-7 이내` `--urgency-soon` · `D-30 이내` `--urgency-near` · `30일 초과` `--urgency-far` | ✓ | ✓ | ✓ |
| 지표 3개, 「읽은 실적보고서」 DOM에 없음 | `감시 중 이벤트 488건 / 30일 이내 마감 32건 / 소멸 앞둔 신주인수권 15건`; the string is absent from `document.body.innerText` | ✓ | ✓ | ✓ |
| 소멸주의보 ↔ 캡션 같은 날짜, 동시 마감이면 「N개 종목」 | 「… 가장 빠른 청약 마감 **2026-09-04**, **3개 종목**).」 — the served `tie_count: 3`, the three-way tie the walk found. **The countdown card has no caption to compare** — see §6 | ✓ | ✓ | ✓ |
| 열어 두면 기준시각 갱신, 스피너 없음, 탭·창·스트립·스크롤 유지 | see §4 | ✓ | — | ✓ |
| 갱신 중/후 카운트다운 리마운트 없음 | the node keeps a `data-mark` set before the refresh and the seconds run monotonically (02:43:19 → 02:42:14 → 02:41:09 over two 65 s intervals; prod 02:25:05 → 02:23:55 over 70 s) | ✓ | — | ✓ |
| 390: 부제 안 끊김, mono 날짜 안 넘어감, 스트립 버튼 전폭 44px | subtitle = 2 balanced lines (174 / 189 px, `keep-all` + `balance`) with no orphan; **0** of the visible dates wrap; strip button **324 × 44** full width under the sentence; 더 보기 44px; tabs 44px; 0 overflow | ✓ | — | ✓ |
| 히어로 「삼성」 + Enter → 첫 후보 선택, 다시 Enter → 이동 | Enter ① stays on `/`, sets `aria-activedescendant`, first option `aria-selected=true`; Enter ② → `/stocks/00126186`. Also: 「계양전기」 (exact) → goes on the **first** Enter (`/stocks/00102618`); a query with no candidates → `GET /stocks?q=…` | ✓ | ✓ | ✓ |
| `prefers-reduced-motion`: 페이드 정지, 갱신 계속, 엣지 표시 | fade `animation-duration` **0.001s** (the shell's global floor) vs **0.2s** normally; the `--live` edge is painted either way; the refresh still runs and 갱신됨 still appears; the countdown's colon `animation: none` and its interval stops (R2 rule, unchanged) | ✓ | — | ✓ |

## 4. The refresh, measured

**Two real 60 s intervals, dev, page left open** (`refresh-real.mjs`): exactly **2** `/api/board`
requests in 130 s, both 200; the corpus did not move, so `as_of` stayed `2026-08-23 16:25` and
**nothing on the screen changed** — no 갱신됨, no edged rows, window still 30, the expanded strip still
open, `scrollY` still 1400, the countdown ticking through both cycles. Production: **1** request in
70 s, same result. That is the "unchanged 기준시각 → 아무 표시도 하지 않는다" half of §7 proven against
the real interval.

The other half needs a corpus that moves, which this one does not, so the visible contract was driven
by **intercepting the browser's own `/api/board` response** (CDP `Fetch`, response stage) and handing
back a mutated payload — and, for that run only, `REFRESH_INTERVAL_MS` was **temporarily set to 3 s in
dev** so a cycle took seconds instead of a minute. It was restored to `60_000` before the final
build, typecheck, smoke and all production measurements (`grep TEMP-P8S5` → nothing).

| case | result |
|---|---|
| same `as_of` | stamp, rows, window, strips, scroll, focus — **all identical**; no 갱신됨, no edge |
| new `as_of`, two rows mutated (계양전기's 발행가 확정, SG's D-day/date) | stamp swaps, **갱신됨** appears (mono 11, `#5fd0a5` on `rgba(95,208,165,.14)`, 2×8) and stays; **exactly those two rows** carry `inset 2px 0 0 --live`; **only the three changed values** carry the 0.2 s fade; tab 전체, window 30, open strip, scroll all survive (`scrollY` 1200 → 1202 — the 2 px the 갱신됨 badge adds to the header, the one geometry change a refresh makes); **0 elements with an infinite animation inside the board panel** (no spinner) |
| next refresh with a new `as_of` | the previous edges are cleared and replaced by the new diff — "다음 갱신에서 엣지 제거", read as *the next refresh that brings a new 기준시각*, because clearing on a no-op tick would be a visible change on a tick the round says must show nothing |
| a row disappears while focused | focus moves to that row's `<ol>` (`tabIndex={-1}`); rows that stay keep their focus and position (`event_id` keys) |
| refresh fails (`ConnectionFailed`) | stamp, rows and everything else unchanged; **no** 실패/오류/다시 시도/새로고침 text anywhere in the panel; the next tick retries |
| result is `stale` | chip → `--alert` on `--alert-tint` + 4×10 + 「· 32시간 전 데이터」, the inset notice above the tabs, **rows at opacity 1** and unchanged (R2's handling, unchanged) |
| `document.hidden` | **0** requests across 2+ intervals; on becoming visible again, a read fires immediately (0 → 2 requests within 600 ms) |

## 5. Functional sweep — every visible control does something

Inventoried and exercised at 1512 and 390: hero input + 조회 submit + the typeahead's four Enter paths
+ ↑/↓/Esc; the four tabs (click, hover `--ink-1` + 2px `--border-strong`, `:focus-visible` 2px ring) —
전체 15 rows/`extras=yes`, 유증 14 rows/`extras=yes`/**no footer** (14 < 15, so none of the three
controls), CB 15/`none`, 매수청구 10/`none`/no footer; a tab switch resets the window (30 → 15) and
keeps the scroll; 15 corp links → `/events/<rcept_no>` and 15 `↗` → DART; 더 보기 / 처음 15건으로 접기;
both strip toggles and their rows. The R8 chrome around it still works: two nav destinations + 로그인,
the 메뉴 sheet button, the footer's 의견 보내기 (opens the dialog, focus lands in the textarea), the
AI 질문 launcher; `[data-vocky-trigger]` count **0**, no 샘플 chip. Console on every run: **only** the
pre-existing `GET /favicon.ico` 404 (deferred D5), 0 page exceptions, 0 React warnings.

## 6. Departures, readings, and one thing deliberately not built

1. **The countdown card's caption was not built.** R9's `Anchors.html` card draws a label
   (「가장 빠른 소멸까지」) and a caption (「청약 마감 2026-09-04 (KST) · 3개 종목」) around the countdown;
   `build-prompt.md` §6 says 「카운트다운 자체 불변」 and its §9 says the fourteen constants 「전부이며,
   그 밖의 제품 문구는 잠긴 상태 그대로다」. The product's `Countdown.tsx` has never had either string,
   and both would be **new Korean** outside §9's list. So the tie rule is applied where a corp is
   actually printed (소멸주의보), exactly as `plan.md` instructs, and the caption is catalogued as
   **Operator Question Q14** rather than minted. Nothing else in §11's caption box is affected: the
   strip and the card read the same `/board/summary`, so they cannot disagree about the date.
2. **`minmax(0, N)` on the value tracks instead of a bare `N`.** R9's own numbers (240/190, 300,
   200/170, 240), but with a shrink floor — `P5.S19` measured 41 px of document overflow at 768 px with
   bare fixed widths, and R9's five widths + four gaps (706 px) exceed the padded panel below ~802 px.
   Measured: full R9 widths from 802 px up, an equal squeeze (198/198 at 802, 167/167 at 768) below it,
   **identical tracks for every row of a panel at every width**, and 0 overflow everywhere. This is not
   the `auto` R9 forbids — `auto` is per-row content sizing, which is the misalignment walk 5 reported.
3. **The 소멸주의보 sentence keeps R2's shape**, `(가장 빠른 청약 마감 {date}, {corp})`, with only the
   `{corp}` slot swapped — build-prompt §6's 「문장 형태·낱말 불변」. R9's card draws the same sentence
   with an em-dash and parentheses around the tie phrase; the contract's words win over the card's
   punctuation.
4. **`word-break: keep-all` is scoped to the landing's `<main>`**, not `app/shell.css`. R9 says
   「랜딩 산문에 전역으로 (`app/shell.css` 또는 각 모듈)」 and its geometry file puts it on `body`;
   putting it on `.cosmos` would restyle five surfaces other rounds own (R10–R14).
5. **The board panel's bottom padding is now 0** so the last strip ends at the panel's bottom hairline,
   as `r9-board.css` has it (`.panel{padding:18px 24px 0}` + `.strip{margin-inline:-24px}`); a
   `:not(:has(.strip))` rule puts the padding back for a panel with no strip at all (no tab has that
   today, and 유증/CB/매수청구 each still have one).
6. **The Enter rule lands in the shared `SearchRow`**, which `/stocks` also renders — that is where
   build-prompt §8 puts it (「`SearchRow`의 Enter 규칙」) and the two surfaces cannot fork. No file under
   `app/stocks/` was touched; what the `/stocks` **page** says on a miss is still R11's.
7. **The API needed a restart** to serve `tie_count` (uvicorn runs without `--reload`): api pid
   65992 → **3182**, web pid 13009 untouched. The temporary `:3100` production server is stopped.

## 7. State of the machine

Dev stack up and answering exactly as the manifest describes (postgres healthy, api `127.0.0.1:8000`
pid 3182, web `0.0.0.0:3000` pid 13009, tailnet `100.77.164.42:3000`). Database untouched — this slice
created no account and wrote no row. `frontend/next-env.d.ts` restored after both builds. Session
scratch (scripts, screenshots, gate/estimate/scheduler output):
`…/scratchpad/p8s5/` — `cdp.mjs`, `board.mjs`, `columns.mjs`, `interact.mjs`, `states.mjs`,
`tabhover.mjs`, `mobile.mjs`, `widths.mjs`, `refresh-real.mjs`, `refresh-mock.mjs`, `reduced3.mjs`,
`refresh-prod.mjs`, `sweep.mjs`, `clean-shots.mjs`, `shots/*.png`.

One unrelated untracked path appeared in the worktree while this slice ran and is **not this slice's**:
`docs/reference/design/rounds/10-event-detail/handoff.md`.

## 8. Regression checklist (the whole cumulative list, re-run)

| line | result |
|---|---|
| `pytest` green + `workflow validate` clean | ✓ **142** (the doc still says 139 — already on the Doc impact list from `P8.S3`) |
| `build && typecheck && smoke` | ✓ **16/16** (doc says 15/15 — same Doc impact line) |
| `gates run` twice byte-identical, split unchanged over 710 rows | ✓ identical; **710** field rows, exposable **50/422/16 = 488** |
| the four AST import scans + anonymity + tool signatures + ops read-only | ✓ (in the suite; this slice added no import and no module) |
| no reader-facing quota / storage-denial copy; no `localStorage` in the ask surfaces | ✓ (only the 보유량 offer's 「탭을 닫으면 사라집니다」, a different signed rule; `localStorage` appears only in comments) |
| the agent's own two numbers | n/a — no live agent pass in this slice |
| exposure invariant re-derived read-only | ✓ **488** exposable, **0 / 0 / 0** |
| `estimate report` twice byte-identical, headline unchanged | ✓ 718.1억원 |
| `scheduler once --offline` six stages | ✓ 0 requests, 0 LLM calls, ▷ $0.0000 |
| corpus change → re-measure | n/a — corpus untouched; the rendered numbers were still read off the served payload (488 / 386 / 32 / 15 / 3) |
| `extract recheck` / `evalset refresh-recall` write nothing on a second run | ✓ `rewritten 0`, `sample: unchanged` |
| no secret value in a tracked file or generated artifact | ✓ (and `vk_` absent from `.next/static`) |
| evalset labels never described as human ground truth | ✓ untouched |
| regenerated summary artifacts from the final run | n/a |
