# Phase P3: Mijual Web Service (design only)

_Intent: see [intent.md](intent.md)._

## Objective

**Design** the Korean-only 미주알 web service with Claude Design under operator gates — brand identity,
the 비로그인 landing 관제 현황판, 종목 검색 + 보유량 슬라이더, 놓친 돈 조회기, event detail for the three
rights types, the 개인화 2층 (auth + portfolio + D-day + sample load), the grounded 해설 panel, the
operator-facing **admin panel**, and the **vocky** feedback touchpoint. **Design only** — P3 ends at the
signed design plus its implementation contracts. No implementation code is written in this phase.

Re-scoped by the operator on 2026-08-20 from the original mixed design+build shape (verbatim wording and
the superseded answer are in `intent.md`). Under `design-cowork` a design-only phase keeps the **single
decomposition pass**: `DECOMP` → design rounds → `REVIEW`. **There is no `P3.DECOMP2` in this phase.**

## Context

- **Where the build goes.** The build is a separate **apply phase**, created later with `create-phase`
  once P3's design is signed, and sized from each round's landed implementation contract
  (`build-prompt.md`). Its own `DECOMP` runs after the design landed, so it too is single-pass.
- **Stack (decided here, locked at the design gate as system structure):** **FastAPI + Next.js**,
  SSE only for 해설 streaming — the handoff §5 preference, and consistent with the P2 Python package
  and Postgres/Celery backbone that already exist. Not a visual decision, so it is *locked* in every
  handoff, never in play.
- **What P2 already provides** (the design has real content to sit on — never lorem):
  - `src/mijual/gates/exposure.py` — `EventExposure` / `FieldView`, the persisted P2 → P3 contract and
    effectively the future API shape. P3 renders what it says and never re-decides exposure.
  - `src/mijual/calc.py` — every displayed number: `d_day` / `DDay.label` (`D-3` / `D-DAY` / `D+2`),
    `window_state`, `allotted_shares`, `excess_subscription_cap`, `lapsed_warrant_value`,
    `lapsed_warrants`, `warrant_intrinsic_value(_floor)`, `lockup_release_date`. All LLM-free.
  - Live board measured 2026-08-20: **488 exposable events — ① 50 / ② 422 / ③ 16**, 409 renderable
    field instances; headline **▷ 718.1억원 / 32 offerings**; ② urgency 33 events within 30 days of
    2026-09-07.
  - Korean state copy that is product, not error handling: `WITHDRAWN_NOTICE_KO` (철회), `추후결정`
    (`TBD_DISPLAY_KO`, **no date shown at all**), `BLOCKING_FLAGS` reasons, 소규모합병 suppression.
- **What does not exist yet:** no HTTP layer, no frontend code. `frontend.md` / `experience.md` /
  `api.md` / `security.md` are bootstrap stubs. `docs/reference/design/` does not exist — the design
  slices create it round by round (`rounds/<NN>-<slug>/handoff.md` + read-only `output/`, `SIGNOFF.md`).
- **Brand context:** logo is **MIJUAL 대문자 + 한글 '미주알' 병기** (handoff §3.7); name and romanization
  are operator-confirmed and not in play unless the operator reopens them. 소멸주의보 exists as a
  possible sub-brand.
- **Working rule:** think/converse/document in English; the **product surface is Korean only**.

## Design Inventory

The source every round's scope checklist is written from — **what to design, not how**. Coverage below is
required across the rounds; Claude Design + the operator decide everything about how it looks.

1. **Brand identity & foundations** — MIJUAL + 미주알 lockup, palette, type scale (Korean text and
   tabular numerals for 금액/카운트다운), spacing, radius, elevation, motion + reduced-motion floor,
   mobile-first breakpoints, `tokens.css`, and the primitives that carry the trust story: the fact vs.
   **▷ 추정** marker, the citation affordance, and the state vocabulary (정상 / 임박 / 철회 / 추후결정 /
   비노출).
2. **Landing 관제 현황판** — the opening headline number ("소멸 카운트다운 중인 신주인수권 N건 · 추정
   가치 X억"), the live event board (all three rights types, sort/filter, urgency), the live countdown
   component, and the "market-wide 관제 + 내 종목 연결" positioning above the fold.
3. **Global chrome** — nav, footer, mobile navigation, page shell, and the **vocky feedback touchpoint**
   (the operator's existing feedback service, embedded as the in-product feedback inception point).
4. **Event detail, per rights type** — ① 유증 신주인수권 (증서 매매기간, 청약일, 발행가 산식, 초과청약,
   실권주 처리), ② CB 오버행 (전환청구기간, 전환가액, 오버행 비율, 리픽싱, 콜·풋 `option_schedule`,
   보호예수 해제), ③ 매수청구권 (반대의사 통지 방법·기한, 2단계 절차) — plus the **citation display**
   (quote + span + `rcept_no` → 원문) and the non-happy states that are product features: **철회**,
   **추후결정** (no date at all), **발행사 기재 불일치**, gate-blocked fields simply absent, and the
   정정공시 "your D-day moved" story.
5. **종목 검색 + 보유량 슬라이더** — anonymous, no-login instant conversion ("500주 보유였다면 83만 원 ·
   증서 매도 마감 D-3"): search entry, ticker resolution, holding input, result readout, no-event state.
6. **놓친 돈 조회기** — retroactive missed-rights value (종목 + 보유량 + 기간 → 소급 계산), per-offering
   breakdown, ▷ estimate framing, zero-result state, the "poke your own stock" hook.
7. **개인화 2층 — auth** — 가입 / 로그인 / 세션 / 로그아웃, minimal-PII framing, and the conversion moment
   from the anonymous experience.
8. **개인화 2층 — portfolio & D-day** — manual holding registration and editing, the personal D-day list
   ordered by urgency, notification settings (email first, KakaoTalk later), and the **judge-facing
   sample-portfolio one-click load**.
9. **Grounded 해설 panel** — the citation-forced explanation layer (§3.6 layer 3) over verified data:
   entry point (**not a chat UI as the default surface**), question affordance, SSE streaming /
   complete / error states, inline citations back to the filing, and the refusal state when the data is
   not gate-passing.
10. **Admin panel (operator-facing)** — pipeline run and beat status, the gate-blocked field / reason-code
    review queue, event state inspection (suppressed / withdrawn / flagged), the accuracy & evalset
    report view, and quota/cost visibility.
11. **Korean-only copy** — every string sourced from or consistent with `notice_ko`, reason codes and the
    P2 terminology (신주인수권증서 / 소멸 / 오버행 / 매수청구권 / 정정공시). Copy is *locked* by default;
    any exception must be named and dated in the round's handoff.
12. **Mobile-first responsive behaviour** across all of the above. (The 결격-grade "reachable unattended
    2026-09-07 → 09-11" deploy requirement shapes the **apply** phase, not the design.)

## Decomposition

Single pass — grounding pack, then **seven design rounds**, then the existing `P3.REVIEW`.

| Slice | Kind | Risk | Order | Covers |
|---|---|---|---|---|
| `P3.S1` | feature | high | 1 | Design grounding pack — real content export for the sessions |
| `P3.S2` | co-work | high | 2 | **R1** brand identity + foundations (inventory 1) |
| `P3.S3` | co-work | high | 3 | **R2** landing 관제 현황판 + global chrome + vocky touchpoint (2, 3) |
| `P3.S4` | co-work | high | 4 | **R3** event detail, 3 rights types + citation + 철회/추후결정/불일치 states (4) |
| `P3.S5` | co-work | high | 5 | **R4** 종목 검색 + 보유량 슬라이더 + 놓친 돈 조회기 (5, 6) |
| `P3.S6` | co-work | high | 6 | **R5** 개인화 2층 — auth + portfolio + D-day + sample load (7, 8) |
| `P3.S7` | co-work | high | 7 | **R6** grounded 해설 panel (9) |
| `P3.S8` | co-work | high | 8 | **R7** admin panel (10) |
| `P3.REVIEW` | review | high | 9999 | phase review (already existed) |

Inventory items 11 (Korean copy) and 12 (responsive) are **cross-cutting** — every round's handoff carries
them, no round owns them.

### Round-packing rationale

- **Seven rounds, one theme each.** The operator asked for "one by one … we have nothing to hurry", so the
  packing favours small reviewable clusters over throughput. Each round is its own `co-work` slice with
  its own `handoff.md`, `pending` gate, card set and implementation contract; the run stops at each gate.
- **R1 first because everything links `tokens.css`.** Palette, type and the trust primitives (fact vs
  ▷ 추정, citation affordance, state vocabulary) are what later rounds compose; designing a surface before
  the foundations exist guarantees rework.
- **R2 packs global chrome and the vocky touchpoint with the landing** — nav/footer/page shell and the
  feedback entry point are decided *by* placing them on the first real surface, and vocky is a global
  affordance rather than a screen of its own. Splitting it out would ask the operator to review a widget
  with no page around it.
- **R3 is the heaviest round and stays whole.** The three rights types share one card anatomy, and 철회 /
  추후결정 / 발행사 기재 불일치 / blocked-field absence are *states of that card* — they are the trust
  claim made visible and cannot be designed apart from it.
- **R4 merges 검색 + 슬라이더 with 놓친 돈 조회기** because both are the same family: anonymous, no login,
  holding quantity → 금액 환산. They share the holding-input primitive and the money readout; designing
  them separately is the reliable way to end up with two divergent readouts for the same number.
- **R5 keeps auth with portfolio/D-day/sample-load.** Auth exists only to serve the 2층, and the design
  question that matters is the conversion moment from anonymous use — that is one flow, not two.
- **R6 and R7 are separate rounds although the example packing joined them.** 해설 is an end-user,
  streaming, citation-bearing panel; the admin panel is operator-facing, dense and ops-shaped. Different
  audience, different density, and both are explicit operator requirements — packing them together would
  make one of them the tail end of a round about the other.
- **Count is fixed here**, per `design-cowork` (the number of design slices is knowable from the inventory
  and is decided at the first `DECOMP`). Expect the read-backs to re-shape what comes *after* the design;
  in a design-only phase that means new slices at fractional orders, never a `DECOMP2`.
- **Slice folders are bare.** No round's `plan.md` is pre-filled — each is planned by the orchestrator at
  its own turn, and the `co-work` rounds are run **inline by the orchestrator, never dispatched** (an
  executor has no `DesignSync`).

## Findings & Notes

- **`P3.S1` is the phase's only non-design slice** and it exists so no session ever sees lorem: it exports
  dated real content into `docs/reference/design/grounding/` — board counts by rights type, the headline
  numbers, per-type sample `EventExposure` / `FieldView` JSON, the Korean state notices and reason-code
  copy, terminology, the three product states, and the UI traps. **0 DART requests, 0 LLM calls.** Claude
  Design reads it through the repo connection (Connect GitHub, or a local-dir connection).
- **UI traps the grounding pack must state explicitly** (all from P2, `data` v0003): `option_schedule`
  dates need a `date_basis` marker before they can be rendered as a date; the five `lapse_mismatch`
  filings are **issuer table errors** and the exposed contract is the literal string "발행사 기재 불일치",
  never a silent reconciliation; `rcept_no 20250930000508` stores `corp_name` 풍전약품 while its 본문
  header says 에스씨엠생명과학 — a DART master artifact that affects **display only**.
- **Numbers drift.** 488 / ▷718.1억원 / 33-within-30-days are measurements of 2026-08-20. Every grounding
  artifact must carry its measurement date and the command that regenerates it, so a later round can tell
  a stale figure from a changed one.
- **Stack decided: FastAPI + Next.js**, SSE confined to 해설 streaming. Reuses the operator's existing
  stack and the P2 Python package; the exposure contract is read-only in the request path (no OpenDART
  call there, per `exposure.py`).
- **Deferred jobs D1–D4 keep their triggers, but the triggers now fire at the apply phase, not P3** —
  they are all rendering-time or data-depth concerns (D1 ② pairing before ② event detail *renders*, D2
  duplicate/collided keys, D3 pre-2026 ① depth for retrospective views, D4 multi-span citations for
  실적보고서 figures). A design round may *surface* one of them as a design question; none of them blocks
  a design round.
- **The apply phase is created by `create-phase`, after P3 passes review** — not from inside this phase
  (a `DECOMP` executor may not run `new-phase`), and not before the design is signed.
- **`co-work` slices never get implementation work** and end at the landed design + SIGNOFF; the first one
  will stop the run at its `pending` gate — that is the design session handoff, not a failure.

## Doc impact

- `decisions` — P3 stack decision: **FastAPI + Next.js**, SSE used only for 해설 streaming; and P3
  re-scoped to design-only with the build moved to a later apply phase.

## Constraints

- **Design only.** No implementation code, no HTTP layer, no frontend scaffolding anywhere in P3.
- **The orchestrator and its executors never design.** Claude Design + the operator make every visual
  decision; a handoff says what to cover and poses questions back, and never proposes a palette, a type
  scale or a layout.
- **Every `co-work` round is main-thread only** (`--risk high`, never dispatched — executors have no
  `DesignSync`), produces a reviewable **card set** with `@dsCard` markers plus a `tokens.css`, and closes
  only on the operator's literal signoff.
- **Ground in real content, never lorem** — `P3.S1`'s pack is what makes that possible; if something a
  round needs is missing, ask for it rather than invent it.
- The returned design record under `docs/reference/design/` is **read-only** once landed.
- Product surface Korean-only; team language English.

## Open Questions

- Whether the retrospective (소멸 총액) and the live board share one page or two — a design question for
  R2, posed back, never answered by us (carried over from `product` v0002).
- The admin panel's audience boundary: operator-only, or also a judge-visible "how the gate works" view?
  Posed at R7.
- vocky's embed shape (script widget vs. link-out) — an integration fact the operator supplies before R2's
  handoff; it constrains where the touchpoint can live.
