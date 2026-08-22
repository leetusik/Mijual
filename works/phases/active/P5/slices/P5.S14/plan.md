# Plan — P5.S14: 내 종목 조회 (R4)

## Context

Read `works/phases/active/P5/phase.md` in full — binding here: S4 (the `/stocks`
endpoints and their two flagged findings: **no live ① in the corpus has a
확정발행가**, so the 환산액 path can't be exercised against live data — build it
faithfully anyway and prove it with the served factors' shape; and the
closed-청약-but-no-실적보고서 gap (코이즈/센서뷰/클로봇) that R4 has no signed state
for — see *Decision to record* below), S13 (**the stable handle is the path:
`/stocks/{corp_code}` via `stockPath()`** — the detail 환산 CTA already links to it;
this slice must serve it), S12 (hero search submits to `/stocks` with a query),
S10/S11 (primitives, chrome, copy convention), DECOMP note 2 (the second D2 check:
a per-stock 놓친 돈 double-count) and note 4 (D4 landed — three-state citations).
Design chain: `frontend.md` supersessions → `SIGNOFF.md` (R4) → R4 `build-prompt.md`
in full → `grounding/` (`copy-inventory.md`, `ui-traps.md`). **RESPECT THE DESIGN.**

## Deliverables — replace S11's bare `/stocks` shell

1. **Routes** — `/stocks` (search/landing state; accepts the hero's query — decide
   the param name with S12's hero form and record it) and `/stocks/{corp_code}` (a
   resolved stock — the handle S13 links). A successful search navigates to the
   path; direct path hits resolve server-side.
2. **Header + search row** — title 내 종목 조회 + the hero subline + crumb "← 관제
   현황판"; input with the locked placeholder ("종목명 또는 종목코드 — 예: 계양전기")
   + 조회 (`--live-solid`). Resolution is S4's endpoint; no-match renders the locked
   "'{query}'와 일치하는 종목이 없습니다 …" line (structural `found: false` → this
   copy, cited).
3. **보유량 strip** — craft panel: label 보유 주식 수 · mono right-aligned integer
   input (`inputMode="numeric"`, comma-grouped) · suffix 주 · preset chips
   100/500/1,000주 · the locked caption ("브라우저 세션에만 저장 · 서버 전송 없음").
   **sessionStorage only** (decision R4-6): remembered per corp? — R4 says on a new
   stock with a remembered value offer the restore chip "이전 입력 {n}주", never
   auto-fill, never server-side. Record the storage key convention (S16's 세션 이월
   제안 reads it later).
4. **진행 중인 권리 — N건** — one panel per live event, most urgent first (the
   served order): RightsChip + title + "상세 보기 →" (`eventPath`) + rcept_no meta;
   right: governing label + upstream DDay + window line (live green when open).
   ②/③ rows per R4 §②/③: deadline + context (② dilution facts from the served
   `convertible`; ③ the 2단계 dependency line), **never a won amount, no
   매수예정가**.
5. **The N주 conversion (① rows)** — client composes **served factors only**, one
   implementation (extend/reuse the shared math seam — S10 note 12: 조회 and
   포트폴리오 must share it; put it in `lib/` and record it for S16): 배정 신주 =
   ⌊n × 배정비율⌋ with the full-10-decimals caption; 초과청약 한도 as "+{k}주" where
   served; 확정발행가 exists → 환산액 = 배정 신주 × `unit_value` (tagged) + 하한;
   확정발행가 null → chip + "확정 예정 {final_price_date} …" and **no money**,
   shares still shown. Recompute on input, no debounce.
6. **2026년 놓친 돈** — total headline (conditional frame line → tagged total
   (alert) + 하한 (ink-2) + coverage caption "집계 범위 2026-01-01 ~ 오늘 (KST)" —
   the **served** boundary, no 기간 input, outside coverage unstated) and the
   per-offering grid rows (유상증자 / 증서 매매기간 / 소멸 계산 / N주 기준): title +
   rcept_no + 확정발행가; 매매기간 + faint `기간 지남 · D+{n}` chip; "발행 − 청약 =
   소멸 {k}주 ({rate}%)" + tagged market value; right column per-holding tagged
   value + the "배정 {k}주 × 추정 {unit}원" caption; **one `Citation` per row**
   (the served warrant-period quote); the calc footer and the disclaimer footnote
   (both locked copy). Zero state and the pending-① "청약 종료({subscription_end})
   후 집계됩니다" line where served.
7. **Decision to record — the S4 gap** (closed 청약, no 실적보고서 yet): those
   events are in **neither** section by the served payload. Render what the
   contract serves — nothing invented for them — and record explicitly in
   `result.md`/`phase.md` that the gap remains a design question for
   `P5.S19`/operator (do not invent a Korean state line for it).
8. **Empty states** — per R4 §Empty states / `LookupEmpty`: 검색 불일치; no-event
   stock (the locked line + 감시 대상 3종 + 감시 중 count from the summary);
   coverage boundary panel (① 2026-01-01부터 · ② 2025-06부터 — served values).
9. **Mobile ≤480px** — single column: top bar → search → 보유량 panel (44px input,
   full-width chips) → sections stacked; breakdown as label/value lines; 44px
   full-width 상세 보기 links. No accordions.
10. **D2 second check** — with live data, check a stock whose corp has the known
    shared-`rcept_no` pairs (코이즈): does the 놓친 돈 total double-count one
    offering? Report the observation; fix nothing.

## Constraints

- All copy verbatim + cited; the provenance line and every sentence above are R4
  literals. No invented Korean (the plan's quoted strings are from the record —
  verify against `build-prompt.md`/`copy-inventory.md` when transcribing).
- Money/ratios stay strings until the one shared math implementation (Decimal-safe
  — record how you multiply exact strings in TS without float drift; `won()` +
  integer-share flooring already exist in `lib/format.ts`).
- Holding count never in a request; primitives/tokens/chrome untouched; no new
  dependencies.

## Validation

- `npm run build` + `typecheck` + `smoke` (add a terse `node:test` case for the
  shared N주 math: flooring, the null-확정발행가 no-money branch); Python 113
  untouched.
- Dev + headless-Chrome pass (localhost, live API): resolve 계양전기 by name and
  code; unpriced ① shows shares + chip + **no 원**; 한화솔루션 breakdown reproduces
  S8's 679,575원 at 500주 client-side (the one true cross-check of the shared
  math); 대한광통신 두 readings; the restore chip flow (set a value on stock A,
  visit stock B); no-match and no-event states; ③ row without 매수예정가; 코이즈
  D2 observation; mobile 390×844. Screenshots. Stop everything.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md` (incl. the D2 and gap observations); `phase.md` *Findings & Notes*
(the sessionStorage key + shared-math module for S16; param conventions) and *Doc
impact* (`frontend`, `experience`, `qa`). Structured verdict. No commits, no
status transitions.
