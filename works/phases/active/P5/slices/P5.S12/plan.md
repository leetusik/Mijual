# Plan — P5.S12: Landing 관제 현황판 (R2/R2.1 + R3's board strip)

## Context

Read `works/phases/active/P5/phase.md` in full — S10 (primitives, `.backdrop` slot,
reduced-motion convention, `lib/copy` rule), S11 (chrome, route map, the
localhost-not-127.0.0.1 gotcha), S3 (the `/board` + `/board/summary` payloads, notes
8–11), and DECOMP note 2 (the D2 duplicate-row check). Design chain:
`docs/current/frontend.md` supersessions → `SIGNOFF.md` (R2/R2.1) → R2 `build-prompt.md`
(the whole file — cosmos, hero, anchor panels, countdown, 소멸주의보, board, all
signed) → R3 `build-prompt.md` §추후결정 board strip → `grounding/`
(`board-snapshot.md`, `headline-numbers.md`, `copy-inventory.md`, `ui-traps.md`).
**RESPECT THE DESIGN** — the R2 record is unusually precise (px values, rgba values,
counts); those are contract.

This slice replaces `app/page.tsx` (S10's foundation proof) with the real landing.
All data is live from `/board/summary` and `/board`; the dated-pack numbers on the
current page disappear with it.

## Deliverables

1. **Cosmos backdrop** — into S10's `.backdrop` slot: one continuous full-page
   starfield (~240 desktop / 160 mobile, twinkle 2.5–6.5s, 80s drift), root-level
   radial green glows (strong ~12% height + faint bottom echo), staggered shooting
   stars (~5 desktop / 3 mobile, 9–18s). Hero-only orbit ellipses (980×280 +
   1200×360, rotate −14°, orbiting star 26s) fully clear of nav and first panel
   (110/160px hero padding desktop); never shrink the rings. Reduced motion:
   twinkle/orbit freeze (`data-motion="tick"`), shooting stars hide
   (`data-motion="ambient"`). Deterministic star generation (no `Math.random` per
   render producing hydration mismatches — seed or generate once; record how).
2. **Hero** — centered: H1 52px/700 "내 종목 조회" — **wait: the R2 literal is
   "내 종목 연결" and R4-5 superseded the surface name to 내 종목 조회; the
   supersession table + SIGNOFF govern which the H1 renders — check them and record
   the reading** (the sub line and search-row copy come verbatim from the record) →
   sub 17px → search row (console input + 조회 button, 52px/560px, submits to the
   `/stocks` route with the query) → the mono stat line with live numbers from
   `/board/summary` (718.1억원 + 추정 tag · 감시 중 N건 · 30일 이내 마감 N건;
   number+건 spans nowrap). Mobile: H1 34px, 48px controls.
3. **Retrospective anchor** — two craft panels (1fr/340px, 20px gap; mobile
   stacked): the value card (eyebrow → 46px/700 headline + 추정 tag → band line →
   fact sentence full-width one line; **no gate-cost line here** — footer only) and
   the countdown/stats card (countdown + 2×2 live stats: 감시 중 · 30일 이내 마감 ·
   소멸 앞둔 · 읽은 실적보고서 — same summary object as everything else).
4. **Countdown** — mono 28px/600 `--alert`, `{d}일 HH:MM:SS`, colon blink 1s
   step-end; target = `next_lapse.target` (the served absolute KST instant — the
   browser only diffs); reduced motion → interval stopped, static value
   (`useReducedMotion`, S10 note 6). If `next_lapse.target` is absent, no countdown
   fabricated — render what the record's own states allow and note it.
5. **소멸주의보 strip** — craft panel, `--alert` border + 10px hazard stripe left
   (repeating −45°, 5px on/off), filled badge, body = 발표용 문장 4 from
   `copy-inventory` with the **live** numbers (`next_lapse` count/date/corp — S3
   note 9: the live tie-break names 퓨쳐켐 where the landed card showed 계양전기;
   live data governs, record it).
6. **Board** — craft panel: header (title 17px/700 + freshness chip). Freshness per
   R2: mono `기준 YYYY-MM-DD HH:MM KST`; stale → alert treatment + `· N시간 전
   데이터` suffix + inset notice above tabs (all served fields — `freshness.stale`,
   `age_hours`; no client staleness math). Content never dims. Tabs with whole-board
   counts (전체/유증/CB/매수청구 compact on mobile, x-scroll, ≥44px hits, active
   underline). Rows: desktop grid `86px 1fr 300px 230px 96px`, 9px v-pad, dashed
   separators — RightsChip compact | corp 600 + `↗` DART link (mono 11) | countdown
   label + date | extras | DDay right-aligned (showDate=false). Extras: ① `청약
   YYYY-MM-DD` + `발행가 확정 전` chip when unpriced (S3 note 10: the payload
   carries the whole 구주주 window — decide which end renders as 청약 and record
   it); ②/③ genuinely empty. Sort: served order (D-day ascending, upcoming only).
   Mobile two-line rows, 11px v-pad.
7. **The two pinned strips under the rows** — ② 진행 중 (`open_now`): the signed
   sentence with the live count, 펼치기 expanding to the same row anatomy with
   D+N DDay; never 종료 language. And R3's 추후결정 strip (`tbd`): "일정 추후결정 —
   카운트다운 없이 감시 중인 이벤트 N건" + 펼치기, rows link to detail, not ranked.
8. **D2 check (DECOMP note 2)** — while verifying against live data, look at the
   board for a visibly duplicated row (two rows sharing an `rcept_no` — 코이즈/
   사토시홀딩스 were the known pair). Report what you see in `result.md`; do not fix
   or `DISTINCT` anything — the orchestrator promotes D2 if the trigger fired.

## Constraints

- Copy verbatim with citations (`components/.../copy.ts` pattern); event-detail
  links use S11's route map (`/events/[rcept_no]` — the detail *page* is S13's; a
  link to a not-yet-built route is correct here, record it, don't stub the page).
- Primitives/tokens/chrome untouched; no new dependencies; numerals mono.
- Estimates: only `figure.estimated` drives the tag (S10 note 9).

## Validation

- `npm run build` + `typecheck` + `smoke`; Python suite untouched (113).
- Dev server (uvicorn 8000 + `npm run dev`, localhost) + headless-Chrome pass:
  hero stat line matches `/board/summary` exactly; the two anchor cards agree with
  each other; countdown ticking against the served target and static under reduced
  motion; board counts match tabs; a ① unpriced row shows the chip and **no money
  anywhere on the page for it**; ② strip count matches `open_now.count`; 추후결정
  strip matches `tbd.count`; freshness chip renders the served 기준시각; screenshot
  desktop + 390×844. Stop everything.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md` (include the D2 observation); `phase.md` *Findings & Notes* (what S13/
S14 inherit: the board-row component if reusable, the H1 naming reading, the ①
extras decision) and *Doc impact* (`frontend`, `experience`; `qa`). Structured
verdict. No commits, no status transitions.
