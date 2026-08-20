# Design Handoff — Round 3: Event Detail — 3 Rights Types + Trust States

- Round: **R3 of 7** · slice `P3.S4` · written 2026-08-21
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main, pushed at handoff commit)
- Builds on: **R1 + R2 signed designs** (locked context): the cosmos-dark theme and craft
  panels (R2.1 governs), tokens incl. the `.cosmos` scope, trust primitives, chrome. A
  change to any of them is a new superseding round, not an R3 edit.
- **Estimate mark ruling (operator, R2 gate): the bordered 「추정」 tag is the system-wide
  estimate mark — ▷ retires from the UI.** This round designs with the tag only, and
  re-cuts the `EstimateMarker` component/card to the tag form (see §5).

## 1. Product context

The event detail page is where a board row opens up: one rights event, all its verified
fields, every field citable back to the filing, and the states that make the trust story
visible. It is also where the 정정공시 narrative lives — "the schedule moved, here is what
changed and what it does to your D-day". Judges will click into 계양전기 from the board and
this page has to hold up. Reached from: the landing board (R2), search/조회 results (R4,
future), and the personal D-day list (R5, future).

## 2. Scope checklist — what this round must cover

- [ ] **Detail page shell** — cosmos page under the R2 chrome: header block (corp identity,
      RightsChip, governing D-day/countdown, DART 원문 link), field sections, provenance.
      Desktop + mobile.
- [ ] **① 유증 신주인수권 detail** — the hero type, richest fields (~5.3 renderable per
      event): 신주배정기준일, 증서 매매기간 (매매 마감 = governing date), 청약일, 발행가
      산식/확정발행가 (or `발행가 확정 전`), 초과청약 조건, 실권주 처리, 청약 취급 증권사;
      per-holding money chain where 확정발행가 exists (`r1-money-chain.json` — ▷206.4억원
      한화솔루션 becomes 「추정」-tagged).
- [ ] **② CB 오버행 detail** — API-tier fields (~0.29 renderable per event — the design
      must survive sparse cards): 전환청구기간 (개시 = governing date; past opening = 진행
      중, never 종료), 전환가액, 오버행 비율, 리픽싱 조건, 콜·풋 `option_schedule` — **render
      the `detail` string, never the two stored dates as a 기간** (ui-traps §1: recurring-
      claim brackets, e.g. 대동기어 "30개월이 되는 날 및 이후 매 3개월"), 보호예수 해제.
      The fuller ② calendar view was deferred from R2 to here — decide how much of it the
      detail page carries.
- [ ] **③ 매수청구권 detail** — 반대의사 통지 방법·기한, 매수청구 행사기간, the 2단계 절차
      explained structurally (통지 → 행사), 매수예정가.
- [ ] **Citation in context** — the R1 Citation primitive composed at density: a field row
      with [근거], the expanded quote panel, the DART link. One event can carry six.
- [ ] **Trust states as page states** (grounding `samples/`):
      - 철회 (`r1-withdrawn.json`) — notice replaces the body,
      - 추후결정 (`r1-tbd-schedule.json`) — structurally no date,
      - 발행사 기재 불일치 (`r1-lapse-mismatch.json`) — alert chip, never reconciled,
      - blocked/absent fields (`r3-field-absent.json`) — absent, no placeholder,
      - sparse-but-healthy ② (`r2-incomplete-api.json`).
- [ ] **정정공시 story** — "your D-day moved": version history of the event, what the
      correction changed (old → new), including the correction-deleted-passage case
      (`r3-field-absent.json` — absence with a history) and the ③ version split
      (`r3-version-split.json` — figures shown must carry the version scoping).
- [ ] **Corp identity display** — decide the shown identity (DART master `corp_name` vs
      본문 header vs both): routine legal-suffix differences (한화솔루션 vs 한화솔루션(주))
      and the one genuine mismatch (`r2-corpname-trap.json`, 풍전약품/에스씨엠생명과학) must
      both survive the tap through to 원문.
- [ ] **추후결정-countdown rows** (4 today) — where they surface, given R2 excluded them
      from the board ranking.
- [ ] **`EstimateMarker` re-cut** — update the component + its card to the 「추정」 tag form
      (the R2 gate ruling), so the system has one estimate mark again.

Cross-cutting: Korean-only, copy locked to `copy-inventory.md` (state strings are exact:
`추후결정`, "발행사 기재 불일치", `WITHDRAWN_NOTICE_KO` per type), mobile-first, a11y floor,
urgency = color-never-size, gate-blocked = absent.

## 3. Locked vs. in play

**Locked:** R1+R2 signed systems (tokens/`.cosmos`, type, motion, craft panels, chrome,
trust primitives' semantics); 「추정」 as the estimate mark; data contracts — a detail page
can only know `EventExposure`/`FieldView` + the version/correction records the samples
show; state copy per `copy-inventory.md`; the option_schedule render rule (detail string,
never a derived 기간); "blocked fields are absent"; Korean-only surface.

**In play:** the whole detail-page composition — field grouping and order, section
anatomy, density, header design, citation placement at density, how the correction story
is told visually, how sparse ② cards keep dignity, the ② calendar depth, corp identity
presentation, 추후결정-row surfacing, mobile pattern, EstimateMarker's tag-form design.

## 4. Where to look — real content, never lorem

- `docs/reference/design/grounding/sample-events.md` + `samples/*.json` — the 11 pinned
  real events with annotations; `r1-`/`r2-`/`r3-` prefixes = rights types ①②③.
- `docs/reference/design/grounding/ui-traps.md` — §1 option_schedule, §2 issuer mismatch,
  §3 corp_name, §5 지남 language per type.
- `docs/reference/design/grounding/copy-inventory.md`, `states-and-trust.md`.
- R2 landed record: `docs/reference/design/rounds/02-landing-chrome/output/` (board row →
  detail continuity: RightsChip, DDay, governing-date labels).
- Data caveat: a small number of ② events carry a 정정 paired to the wrong 사채 (deferred
  job D1, fixed at the apply phase). The pinned samples are verified correct — design from
  them; do not chase the pairing issue in this round.

Missing real content → ask; never invent.

## 5. Required outputs (a round is incomplete without all three)

1. **Card set** — line-1 `@dsCard` markers, review-time group `⏳ P3.S4 · Detail`:

   - `detail/EventR1.html` — ① full detail (계양전기 or 한화솔루션 with money chain)
   - `detail/EventR2.html` — ② detail incl. option_schedule + sparse-card treatment
   - `detail/EventR3.html` — ③ detail with the 2단계 절차
   - `detail/EventStates.html` — 철회 / 추후결정 / 기재 불일치 / absence, in page context
   - `detail/CorrectionStory.html` — the 정정 "D-day moved" narrative + version history
   - `detail/EventMobile.html` — one representative detail at 390px

   Splitting further is fine; merging into a monolith is not. Additionally, **re-cut the
   existing `components/EstimateMarker.html` card** (and its `.jsx`/`.prompt.md` reference
   implementation) to the 「추정」 tag form — it keeps its path and its already-clean
   `Components` group.

2. **Record of what was designed** with departures — refresh `handoff-output/result.md`
   (R1/R2 copies are landed in the repo).

3. **Implementation contract** — refresh `handoff-output/build-prompt.md`; list any token
   delta explicitly.

**Definition of done: the cards appear in the pane** under `⏳ P3.S4 · Detail`, the
EstimateMarker card shows the tag form, and the refreshed record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. Does the detail page carry a holding-conversion block ("N주 보유 시 …" — R4's math), or
   only a prominent link into 조회? (Both must not disagree with R4 later.)
2. How deep does the ② calendar go on detail — full option_schedule + 보호예수 schedule
   table, or governing dates + a 더보기?
3. Corp identity: master `corp_name`, 본문 header, or a pairing — and what happens visually
   in the one genuine-mismatch case?
4. Where do 추후결정-countdown events live (not ranked on the board per R2) — a section on
   detail-adjacent lists, a board footnote, or 조회-only?

## 7. Operator setup + definition of done

Same project ("Mijual Design System"); pull latest `main` in the session so it sees this
handoff and the landed R1/R2 records. When done, tell the orchestrator to resume;
read-back, landing, signoff, and the regroup follow. Approval must be literal.
