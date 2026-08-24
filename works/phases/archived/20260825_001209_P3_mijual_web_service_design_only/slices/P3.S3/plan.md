# Plan — P3.S3: Design round R2 — landing 관제 현황판 + global chrome + vocky (co-work)

## Shape

`co-work` slice, run inline by the orchestrator (never dispatched), same two-leg shape as
P3.S2: **handoff leg** — write
`docs/reference/design/rounds/02-landing-chrome/handoff.md`, commit
(`feat(design): P3.S3 handoff — landing + chrome round`), push `main` (the one push this
slice authorizes), `set-slice-status P3.S3 pending`, STOP. **Read-back leg** (after the
operator clears `pending`): DesignSync `list_files` → verify named card paths →
concreteness check → land the returned record read-only under
`rounds/02-landing-chrome/output/` → append the landed spec to `phase.md` → operator
signoff → append to `SIGNOFF.md` → pure regroup retiring `⏳ P3.S3 · …` →
`finish-slice` → commit (`feat(design): P3.S3 read-back — …`).

## Round scope (inventory items 2 + 3)

- **Landing 관제 현황판**: hero headline (grounding `headline-numbers.md` framing — "소멸
  카운트다운 중인 신주인수권 N건 · 추정 가치 ▷X억원"), the live event board (all three
  rights types, sort/filter, urgency ordering, RightsChip + DDay composition), live
  countdown, 소멸주의보 strip placement (R1 sub-brand), "market-wide 관제 + 내 종목 연결"
  above the fold, data-freshness/"측정 기준" treatment (the board is stale-never-dark by
  architecture — staleness must be visible, not hidden).
- **Global chrome**: nav (wordmark usage per R1 lockup), footer, mobile navigation, page
  shell; desktop + mobile compositions.
- **vocky feedback touchpoint**: vocky embeds as a **script widget** (its own UI) —
  this round decides where its trigger lives in the chrome and how it is styled to fit
  the design system. (vocky's observation API concerns R7/admin, not this round.)
- Open question posed back (from `product` v0002): does the retrospective (소멸 총액)
  story share the landing with the live board, or get its own page?

R1's signed design is **locked context**: tokens, type, trust primitives, state
vocabulary — compose them, don't redesign them (a change = a new superseding round).

## Notes

- Session output: ask Claude Design to refresh `handoff-output/result.md` +
  `build-prompt.md` for this round (R1's copies are already landed in the repo).
- Required card paths (named in the handoff): landing/Headline, landing/Board,
  landing/Landing (desktop composition), landing/LandingMobile, chrome/Nav,
  chrome/Footer, chrome/Feedback. Groups `⏳ P3.S3 · Landing` / `⏳ P3.S3 · Chrome`.
- Real content only: board rows and counts from `grounding/board-snapshot.md` and
  `samples/*.json`; copy locked per `copy-inventory.md`.
