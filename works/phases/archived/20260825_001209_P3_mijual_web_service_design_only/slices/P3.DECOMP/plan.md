# Plan — P3.DECOMP (decompose P3 as a DESIGN-ONLY phase)

## Context

P3 was created as a mixed design+build phase, but at this gate the operator re-scoped it
(2026-08-20, verbatim): **"make this phase design only. one by one. we have nothing to
hurry. vocky will be added as feedback inception, admin panel required, auth related
required."** Follow-ups resolved: **vocky = the operator's existing feedback-collection
service** — Mijual embeds its widget/touchpoint, and the design rounds include it; stack
confirmed **FastAPI + Next.js** (SSE only for 해설 streaming).

Consequences (per the `design-cowork` skill's design-only shape):
- Single-pass decomposition: `DECOMP` → design round slices → `REVIEW`. **No `P3.DECOMP2`,
  no build slices, no implementation code anywhere in P3.**
- Build moves to a separate **apply phase**, created later via `create-phase` (after P3's
  signed design), sized from the rounds' `build-prompt.md` contracts. Deferred jobs D1–D4
  keep their triggers but now fire at that apply phase, not P3.
- Multiple small rounds ("one by one"), each its own `co-work` slice with its own
  `handoff.md` and `pending` gate. No deadline pressure on round count.

Repo facts the decomposition builds on (from today's survey):
- P2 provides the full data substrate: `src/mijual/gates/exposure.py` (`EventExposure` /
  `FieldView` — the exposure contract, effectively the future API), `src/mijual/calc.py`
  (all displayed arithmetic: `d_day`, `lapsed_warrant_value`, etc.), CB calendar, the
  소멸가치 estimation report (headline ▷718.1억원 / 32 offerings), Korean state copy
  (`notice_ko`, `gates reasons`), and 488 exposable events (① 50 / ② 422 / ③ 16) as of
  2026-08-20.
- **No HTTP or frontend code exists**; `frontend.md` / `experience.md` / `api.md` /
  `security.md` are bootstrap stubs; `docs/reference/design/` does not exist yet (the
  design slices create it round by round).
- Product truth for handoffs: `docs/current/product.md` (v0002 — three product states,
  trust claim, terminology, open questions), handoff §3.5–3.7 (surfaces, AI-role
  architecture, brand context: MIJUAL 대문자 + 한글 '미주알' 병기).

## What the DECOMP executor does (slice-executor-high)

1. **Read** `phase.md`, `intent.md`, `docs/reference/challenge/00_HANDOFF.md` §3.5–3.7,
   `docs/current/product.md`, and skim `gates/exposure.py` + `calc.py` enough to write an
   accurate design inventory.

2. **Record the re-scope** so intent stays consultable:
   - Append to `intent.md` → *Clarifications Resolved* (verbatim original stays untouched):
     - Q: mixed one-phase vs design/apply split? — A (2026-08-20, supersedes the earlier
       "one mixed phase" answer; operator verbatim): "make this phase design only. one by
       one. we have nothing to hurry. vocky will be added as feedback inception, admin
       panel required, auth related required."
     - Q: vocky? — A: operator's existing feedback-collection service; embed its
       widget/touchpoint; design rounds include it.
     - Q: stack? — A: FastAPI + Next.js confirmed.
   - Update `phase.md` *Objective*/*Context* to the design-only scope (build → later apply
     phase) and note **no DECOMP2** in this phase.

3. **Write the design inventory in `phase.md`** (the source for every round's scope
   checklist — what to design, not how): brand identity (MIJUAL logo + 미주알 병기,
   palette, type, tokens); landing 관제 현황판 (headline number, event board, live
   countdowns) + global nav/footer; 종목 검색 + 보유량 슬라이더; event detail pages
   (per-type, incl. 철회/추후결정/"발행사 기재 불일치" states); 놓친 돈 조회기;
   personalization 2층 — auth surfaces (가입/로그인/세션), portfolio 등록, D-day list,
   sample-portfolio one-click; grounded 해설 panel (citation-forced, SSE); **admin panel**
   (operator-facing); **vocky feedback touchpoint**; Korean-only copy sourced from
   `notice_ko`/reason codes; mobile-first responsive (결격 requirement: web reachable
   unattended 09-07→09-11 shapes the later apply phase, not the design).

4. **Create the middle slices** (bare folders only — never pre-fill any `plan.md`):
   - `P3.S1` — design grounding pack, `--kind feature --risk high`, order 1: export real
     content for the design sessions into `docs/reference/design/grounding/` (dated real
     board counts, headline numbers, per-type sample `EventExposure`/`FieldView` JSON,
     Korean state notices + reason-code copy, terminology, the three product states, UI
     traps: `option_schedule` date conventions, issuer-table mismatch rendering, the wrong
     `corp_name` display case). 0 DART / 0 LLM cost; Claude Design reads it via the repo
     connection. Never lorem.
   - **Design round slices**, each `--kind co-work --risk high`, sequential orders after
     S1 — **executor finalizes the round packing and count (~5–7)** and records the
     rationale in `phase.md`. Required coverage = the whole inventory above; guidance:
     small reviewable clusters, one theme per round, brand/foundations first, e.g.:
     R1 brand + foundations → R2 landing 현황판 + nav + vocky touchpoint → R3 검색+슬라이더
     + event detail → R4 놓친 돈 조회기 → R5 2층 (auth + portfolio + D-day + sample load)
     → R6 해설 panel + admin panel. Repacking is the executor's call; count is fixed here
     per the skill.
   - No other slices. `P3.REVIEW` already exists.

5. **Findings & notes in `phase.md`**: stack decision (FastAPI + Next.js, SSE for 해설
   only) with a one-line **Doc impact** note (decisions doc); D1–D4 trigger handover to
   the apply phase; pointer that the apply phase is created by `create-phase` after P3
   passes; numbers drift — grounding pack must be dated.

6. **Validate**: `python3 scripts/workflow.py validate`; confirm the created slices'
   kind/risk/order via `works/backlog.md` regeneration.

Carve-outs: as a decomposition slice the executor may run `new-slice`; it still never
commits or transitions status. It writes `result.md` when done.

## Orchestrator follow-through (after the executor returns `done`)

`finish-slice P3.DECOMP` → `validate` → commit (`feat(p3): decompose design-only phase —
grounding pack + N design rounds`). Then the loop continues to `P3.S1`. Expected stop
later: the first `co-work` slice ends the run at its `pending` gate — that is the design
session handoff, not a failure.

## Verification

- `python3 scripts/workflow.py validate` passes; `next` points at `P3.S1`.
- `works/backlog.md` shows the new slices with `co-work`/`high` on every design round.
- `phase.md` carries the inventory + round rationale; `intent.md` carries the re-scope.
