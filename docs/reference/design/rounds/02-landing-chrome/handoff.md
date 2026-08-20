# Design Handoff — Round 2: Landing 관제 현황판 + Global Chrome + vocky

- Round: **R2 of 7** · slice `P3.S3` · written 2026-08-20
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main branch, pushed at handoff commit)
- Builds on: **R1 signed design** (`docs/reference/design/rounds/01-brand-foundations/output/`,
  and the live `foundations/` + `components/` in this design project) — R1 is **locked
  context** this round: compose the tokens and trust primitives; changing them is a new
  superseding round, not an R2 edit.

## 1. Product context

미주알's landing is the product's opening argument: a **비로그인 market-wide 관제 현황판**
that makes a judge feel the size of the problem in 3 seconds — "지금 소멸 카운트다운 중인
신주인수권 N건 · 추정 가치 ▷X억원" — before any personalization exists. Positioning:
"시장 전체의 소멸 임박 권리를 감시하는 관제 서비스 + 내 종목 연결". The presentation's
opening number and the landing are the same thing. Judges arrive cold, desktop and mobile.

This round also sets the **global chrome** every later surface lives in (nav, footer,
mobile navigation, page shell) and places the **vocky feedback widget trigger**.

## 2. Scope checklist — what this round must cover

- [ ] **Hero headline** — the live counts + ▷ value framing from
      `grounding/headline-numbers.md`, with the fact/estimate distinction exactly per R1
      (`EstimateMarker`; facts never carry ▷). How the two headline layers (live board
      now vs. the 2026 retrospective total) relate is an open question below.
- [ ] **소멸주의보 strip** — where the R1 sub-brand element (`brand/Subbrand.html`) lives
      on the landing and what feeds it.
- [ ] **Live event board** — all three rights types in one board (① 50 / ② 422 / ③ 16
      exposable today — the type imbalance is real and the design must survive it):
      row anatomy (RightsChip, corp, key date, DDay, value-when-known), sort/filter,
      urgency ordering, and how a row with **no money number yet** reads (확정발행가
      publishes ~D-1 before 청약 — the most urgent ① rows often have no ▷ value; "아직
      확정 전" is a first-class state, see phase finding).
- [ ] **Live countdown** — the ticking component composed per R1 Motion (colon blink,
      reduced-motion freeze).
- [ ] **Data freshness** — the board is architecturally **stale-never-dark** (no API/LLM
      call in the request path; a dead worker leaves data stale, not missing). Staleness
      must be *visible*: the "측정/기준 시각" treatment, and what the page looks like when
      data is hours old.
- [ ] **Above-the-fold composition** — desktop and mobile: headline → board → the "내
      종목 연결" bridge to the (future) 검색/2층 surfaces.
- [ ] **Global nav** — R1 wordmark usage (charcoal, English alone), destinations for the
      surfaces the phase designs (검색/조회기, 2층, 해설 — naming from `copy-inventory.md`
      / `product.md` terminology; do not invent new Korean feature names, pose naming
      gaps back), login entry (2층 exists but is second-class to the anonymous
      experience).
- [ ] **Footer** — data provenance line (DART-derived, ▷ estimates marked), disclaimers
      per `product.md` trust claim, and whatever else the session decides belongs.
- [ ] **Mobile navigation** pattern.
- [ ] **vocky feedback trigger** — vocky is the operator's feedback service embedding as
      a **script widget with its own UI**; this round decides where its trigger sits in
      the chrome (placement + trigger styling to fit the system). The widget's internals
      are vocky's, not designable here; the admin-side observation of feedback is R7's,
      not this round's.

Cross-cutting (every round): Korean-only surface, copy locked to
`grounding/copy-inventory.md`, mobile-first responsive, a11y/reduced-motion floor.

## 3. Locked vs. in play

**Locked:** everything R1 signed (tokens, type, spacing, motion, trust primitives, state
vocabulary, urgency=color-never-size, square/hairline system, light theme only); Korean-only
surface; UI copy per `copy-inventory.md`; data contracts (`EventExposure`/`FieldView` —
a board row can only know what the samples show); stale-never-dark architecture; the
positioning sentence; a11y floor. vocky's widget internals (external product).

**In play:** all landing/chrome layout and composition, board anatomy and density,
sort/filter expression, headline hierarchy, countdown presentation, freshness treatment,
nav/footer content-arrangement and mobile pattern, vocky trigger placement/styling —
and whatever the session decides the landing needs that this list missed (log it as a
departure).

## 4. Where to look — real content, never lorem

- `docs/reference/design/grounding/board-snapshot.md` — real board counts, urgency
  distribution, the most-urgent live rows per type (use these rows in the cards).
- `docs/reference/design/grounding/headline-numbers.md` — headline figures + exact ▷ framing.
- `docs/reference/design/grounding/samples/*.json` — row-level truth (`r1-`/`r2-`/`r3-` =
  rights types ①②③). `r1-live-healthy.json` (citations), `r1-money-chain.json` (full ▷
  value chain), `r2-option-schedule.json` (why ② rows show fewer fields).
- `docs/reference/design/grounding/copy-inventory.md`, `states-and-trust.md`, `ui-traps.md`.
- `docs/current/product.md` — terminology, trust claim, non-goals.
- R1 landed record: `docs/reference/design/rounds/01-brand-foundations/output/`.

Missing real content → ask for it; do not invent it.

## 5. Required outputs (a round is incomplete without all three)

1. **The card set** — line-1 `@dsCard` markers, review-time groups `⏳ P3.S3 · Landing`
   and `⏳ P3.S3 · Chrome`. Required card paths (split further if useful; never merge into
   a monolith):

   - `landing/Headline.html`
   - `landing/Board.html`
   - `landing/Landing.html` (desktop composition)
   - `landing/LandingMobile.html` (mobile composition)
   - `chrome/Nav.html`
   - `chrome/Footer.html`
   - `chrome/Feedback.html` (vocky trigger in context)

2. **A record of what was designed** with every departure logged — refresh
   `handoff-output/result.md` for this round (R1's copy is already landed in the repo).

3. **An implementation contract** complete enough to build from without inventing
   anything — refresh `handoff-output/build-prompt.md` likewise. Token delta: if this
   round adds tokens to `foundations/tokens.css`, list them explicitly in the record.

**Definition of done: the cards appear in the Design System pane** under the
`⏳ P3.S3 · …` groups, and the refreshed record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. Retrospective vs. live: does the 2026 소멸 총액 story (▷718.1억원) share the landing
   with the live board, or get its own page linked from it? (Carried from `product` v0002.)
2. What is the board's default ordering — pure urgency, or type-weighted (② dominates by
   count but ① carries the money story)?
3. Does the landing surface the ② calendar (전환청구 개시/보호예수 해제) inline on the
   board, or defer it to event detail (R3's subject)?
4. Where does the vocky trigger live — chrome-level (persistent) or footer-level (quiet)?

## 7. Operator setup + definition of done

Same project ("Mijual Design System"), Connect GitHub already in place — pull latest
`main` in the session so it sees this handoff and the landed R1 record. When the cards
are up and the record/contract refreshed, tell the orchestrator to resume; read-back,
landing, signoff, and the regroup follow. Approval must be literal.
