# Plan — P3.S4: Design round R3 — event detail, three rights types + trust states (co-work)

## Shape

`co-work` slice, inline on the main thread, same two-leg shape as P3.S2/S3:
**handoff leg** — write `docs/reference/design/rounds/03-event-detail/handoff.md`, commit,
push `main` (the slice's one push), `set-slice-status P3.S4 pending`, STOP.
**Read-back leg** — DesignSync `list_files` → verify card paths → concreteness check →
land under `rounds/03-event-detail/output/` → phase.md spec append → operator signoff →
SIGNOFF append → pure regroup (`⏳ P3.S4 · …` off) → `finish-slice` → commit.

## Round scope (inventory item 4 + R2 deferrals)

- Event detail per rights type: ① 유증 (증서 매매기간, 청약일, 발행가 산식, 초과청약, 실권주
  처리, 발행가 확정 전 state), ② CB (전환청구기간, 전환가액, 오버행 비율, 리픽싱,
  `option_schedule` — render the `detail` string, never the two dates as a 기간, 보호예수
  해제; the full ② calendar deferred here from R2), ③ 매수청구 (반대의사 통지 방법·기한,
  2단계 절차).
- Citation display in context: per-field [근거] → verbatim quote + span + `rcept_no` → 원문.
- Trust states as card states: 철회, 추후결정 (no date), 발행사 기재 불일치, blocked-field
  absence, and the 정정공시 "your D-day moved" story (version history;
  `r3-version-split.json` + the correction-deleted-passage case `r3-field-absent.json`).
- Corp identity display (master vs 본문 header vs pair — grounding finding 4).
- Where 추후결정-countdown rows (4 today) surface — deferred from R2.
- Cosmos theme (R2.1) governs; estimate mark = 「추정」 tag everywhere (operator decision at
  the R2 gate) — this round also re-cuts `EstimateMarker` to the tag form.

## Notes

- Required cards (named in handoff): detail/EventR1, detail/EventR2, detail/EventR3,
  detail/EventStates, detail/CorrectionStory, detail/EventMobile; group `⏳ P3.S4 · Detail`.
  EstimateMarker re-cut updates the existing `components/EstimateMarker.*` (already-clean
  group, no new address needed).
- Open questions posed back: corp identity source; holding-conversion block on detail vs
  link-out to 조회 (R4); how much of the ② option_schedule renders; 추후결정 rows' surface.
- D1 (② wrong-사채 pairing) triggers at the apply phase's ② rendering, not at design —
  the pinned samples are correct; note it in the handoff as a data caveat, not a task.
