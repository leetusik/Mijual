# Plan — P5.S13: Event detail ①②③ (R3)

## Context

Read `works/phases/active/P5/phase.md` in full — binding here: S3 (the
`/events/{rcept_no}` and `/corrections` payloads, notes 5–7: 404-not-explained,
철회-is-a-surface, the ② fact strip's six values), S5 (the three repaired ② pages
worth spot-checking), S6 (③ `appraisal_price` is now in the contract), S20 (multi-
part citations), S10 (primitives — `Citation` parts, `StateBadge`, `DDay`;
`lib/copy` rule), S11 (chrome/routes — `/events/[rcept_no]` per `eventPath`), S12
(shared board-row anatomy, `lib/format.won()`), and DECOMP notes 4 (D4 landed —
never re-attach a one-addend quote; the contract's three-state citation governs)
and 8 (**no 질문 스트립** — the R6 preset-chip strip on detail is P6's; its absence
here is a phase boundary, not a dropped element — restate that in your notes).
Design chain: `frontend.md` supersessions → `SIGNOFF.md` (R3) → R3 `build-prompt.md`
in full → `grounding/` (`ui-traps.md`, `states-and-trust.md`, `sample-events.md`,
`copy-inventory.md` for the `korean_name` labels and locked state copy).
**RESPECT THE DESIGN.**

## Deliverables — `app/events/[rcept_no]/page.tsx` + components

1. **Common anatomy** (all three types, per R3 §Page anatomy): crumb "← 관제
   현황판" (mono, text-sm) → craft-panel header (RightsChip → corp text-2xl bold +
   "DART 원문 ↗" mono link → mono meta line: 접수번호 · 최초 공시 date · 정정 반영
   when versions > 1; right side: governing label → `DDay` (upstream values) → mono
   window/state line) → type body → field sections (`// {name}` mono eyebrow; rows =
   220px label col from the served `korean_name` + value + per-field `Citation` —
   only served fields exist in the DOM; `display: "추후결정"` → `StateBadge tbd` plus
   any non-date facts; blocked fields have **no row, no marker**) → 정정 strip
   (`--surface-raised`: "정정공시 반영 — 최근: …" from the corrections teaser + "정정
   이력" button — **label open question**: the phase carries "정정 이력" as
   unresolved; render the R3 literal `정정 이력` and flag it for `P5.S19`/the
   operator, record that) → provenance line (mono 10px, the locked sentence).
   **Identity rule**: DART master `corp_name` only; iff
   `corp_name_agrees_with_body === false`, the one-line 본문 표기 sentence (locked
   copy) under the name.
2. **① body** — the 환산 블록 (§6-1): per-unit chain 예정/확정발행가 → 할인율 →
   (확정 시) 증서 1주 이론가치 with the estimate tag → 배정비율 at its full 10
   decimals; 확정발행가 null → `발행가 확정 전` chip + mono `확정 예정
   {final_price_date}` and **no money number**. "내 보유량으로 환산 →" routes to
   `/stocks` with the stock preselected (record the query-param convention — S14
   consumes it). No N주 input here. Post-결과 events: the 청약 결과 inset (발행 ·
   청약 · 소멸 shares + tagged 소멸가치 + 하한) — citations per the served
   three-state contract (a `parts` citation renders every addend, S10 note 10).
   발행사 기재 불일치 (when served): two readings side by side, each with its own
   `Citation`, the locked header/footer sentences, never reconciled. ① governing =
   매매 마감; open window → live-green "거래 가능 · 마감 D-n"; past → faint D+.
   청약 취급처 as the target/agent/date table (구주주 rows bolded).
3. **② body** — the API fact strip ABOVE 본문 fields with exactly the six served
   values (전환가액 · 오버행 % · 전환 시 주식수 · 권면총액 · 발행방법 · 만기 — facts,
   no quote chips; the citation is the filing number). Governing = 전환청구 개시;
   past opening = "진행 중", never 종료. `option_schedule`: each option's `detail`
   string as the value; the stored range **only** as the locked caption — never a
   plain 기간, never a bar. Sparse ② (0 본문 fields): fact strip + the locked
   closing line, no placeholders.
4. **③ body** — governing = 통지 마감. The 2단계 numbered structure (① 반대의사
   통지 window ② 매수청구 행사 window) + the locked dependency sentence; past steps
   faint with `기한 지남` chip. **매수예정가**: S6 put `appraisal_price` in the
   contract, superseding R3's "not rendered" line (D-15's exact mechanism — build
   the backing, then it renders). Render it as a standard field row through the
   generic field-section anatomy (served `korean_name`, value, its verified
   `Citation`) — no invented layout beyond the signed row anatomy; record this
   reading for `P5.S19`.
5. **State pages** — 철회 (`state: withdrawn`): `StateBadge` full-width locked
   notice replacing the body; below it only the 정정사항-evidence sentence + a
   `Citation` with the served withdrawal quote; no fields, no countdown, no old
   dates. Countdown-less exposable states per R3: 추후결정 → `StateBadge tbd` +
   "카운트다운 없음 — 일정이 공시상 미정"; field-absent ③ → the factual "현재 버전
   공시에 없음" line. Unknown/non-renderable `rcept_no` → the 404 experience
   (decide what a not-found renders inside the chrome — no invented Korean beyond
   what exists; record it).
6. **CorrectionStory view** — opened by 정정 이력 (decide: route or in-page view;
   record): the version rail from `/events/{rcept_no}/corrections` (chronological
   rows date · correction_kind · rcept_no ↗; only `is_current_readable` filled +
   live badge "현재 읽는 버전"; superseded rows may carry the locked grey reason
   annotation), field moves as 정정 전 / → / 정정 후 columns verbatim (`new: null`
   → "(정정 후 본문에서 삭제됨)"), summary = `interpretation.summary` verbatim +
   bolded `schedule_impact`. Verdicts never cross versions.
7. **Mobile ≤480px** — single column per R3: top bar (crumb + ring wordmark) →
   header stack → countdown box → 44px full-width DART link → 환산 블록 → field
   rows stacked, label row carrying the `[근거]` chip right-aligned; no accordions;
   ≥44px hits.

## Constraints

- All copy verbatim with citations; labels from served `korean_name` — the
  frontend maintains no field-name table of its own.
- Board-row/strip components from S12 reused where they fit; primitives/tokens/
  chrome untouched; no new dependencies.
- Estimates tagged only via `figure.estimated`; facts never tagged (매수예정가,
  전환가액 etc. are facts).

## Validation

- `npm run build` + `typecheck` + `smoke`; Python 113 untouched.
- Dev + headless-Chrome pass over real pages (localhost): a priced ① with 청약
  결과 (한화솔루션 `20260720000067` — the multi-part citation renders both
  addends), an unpriced ① (`발행가 확정 전`, no money), 대한광통신's 불일치 two
  readings, a rich ② and a sparse ②, one of S5's three repaired ② pages serving
  its own bond, a ③ with 매수예정가 (and one of the 4 without — row absent), a 철회
  page (notice + evidence only), a multi-version CorrectionStory, a 404. Verify no
  `▷`, no invented strings, mobile at 390×844. Screenshots. Stop everything.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (the 환산→조회 param convention for S14;
the 매수예정가 and 정정-이력-label readings for S19; component map) and *Doc impact*
(`frontend`, `experience`, `qa`). Structured verdict. No commits, no status
transitions.
