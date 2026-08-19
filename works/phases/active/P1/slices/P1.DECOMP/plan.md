# Plan — P1.DECOMP (decompose Phase P1)

## Goal

Decompose Phase P1 "Foundation Spike & Confirmations" into its middle slices and seed `phase.md` with the breakdown, rationale, and working notes. Create bare slice folders only (`new-slice`) — never pre-fill any slice's `plan.md`.

## Context to read first

- `works/phases/active/P1/intent.md` — confirmed operator intent (the source of truth).
- `works/phases/active/P1/phase.md` — the phase notebook you will seed.
- `docs/reference/challenge/00_HANDOFF.md` — full project context; §6 items 1, 2, 6 are this phase; §3.6 lists the service-critical fields the matrix must classify; §7 working principles.
- `docs/reference/challenge/01_문제정의.md` — problem definition (skim for grounding).

## Fixed facts (do not re-derive)

- A working OpenDART API key is already saved at repo root `.env` as `DART_API_KEY=...` (verified live: `status 000` on `company.json`). `.env` is gitignored; never move or commit the key.
- Operator decision (2026-08-19): the MVP rights-scope confirmation must **pause for the operator's decision** — the tentative 3종 (① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권) is NOT auto-confirmed; when the field matrix is ready, a confirmation step goes `pending` with a recommendation and the operator decides.
- P1 touches no product visual design → single-pass decomposition (no co-work slice, no DECOMP2).
- Working language: English for thinking/docs; Korean terms for domain artifacts (공시 field names etc.) are fine.

## Expected slice breakdown (steer toward this; refine only with recorded rationale)

Create with `python3 scripts/workflow.py new-slice --phase P1 --slice <id> --name "..." --kind <kind> --risk <risk> --order <n>`:

1. **P1.S1 — DART OpenAPI spike & field matrix** (`--kind spike` or `implementation`, `--risk high`, order before S2): using the key in `.env`, exercise the 주요사항보고서 APIs for the 3 rights types — 유상증자 결정 (piicDecsn), 전환사채권 발행결정 (cvbdIsDecsn), 교환사채 발행결정 if available (exbdIsDecsn), 회사합병 결정 (cmpMgDecsn) — against real 2026 filings; pull ≥5 기재정정 (정정공시) samples; produce the **event-type × field × {structured API / LLM extraction needed} matrix**, explicitly covering the §3.6 layer-1 fields (신주인수권증서 상장 매매기간, 청약 취급 증권사, 실권주 처리, 초과청약 조건, CB 리픽싱·콜풋·보호예수 해제, 매수청구 반대의사 통지 방법·기한) and the diff-target fields from the 정정 samples. Spike code stays small (a script or two under `scripts/spike/` or similar); matrix lands as a durable markdown artifact + a Doc impact note in `phase.md`.
2. **P1.S2 — MVP rights-scope recommendation & operator confirmation** (`--risk high`, depends on S1): analyze the matrix for extraction feasibility within the 19-day deadline, write a keep/demote recommendation per rights type, then hand off to the operator (the executor returns `needs_operator`; the orchestrator sets the slice `pending`). This is the planned mid-phase stop.
3. **P1.S3 — Recon: daker.ai submission requirements + mijual domain availability** (`--risk high` — it needs WebSearch/WebFetch, which only the high executor tier has): daker.ai submission format (데모 URL·영상·기획서 양식), individual-vs-team rules, 본선/발표 schedule vs the operator's 9/1 employment availability; mijual.ai (1st choice) / mijual.kr / mijual.com availability. Consider ordering it BEFORE the S2 pending stop (e.g. between S1 and S2, or first) so recon isn't blocked behind the operator gate — your call; record the ordering rationale.

Do NOT create build/service slices — P2..P4 own those. Do not touch the REVIEW slice.

## Also seed `phase.md`

Fill in: Decomposition (slice list + one-line rationale each + ordering/risk rationale), Context (key facts above: key location, scope-gate decision, deadline 2026-09-07), Findings & Notes (anything learned while decomposing, e.g. which DART endpoints exist for the 3 event types — a quick doc check of opendart.fss.or.kr API docs is in scope), Constraints (§7 principles: evidence-tagged facts, no inflation, AI reads/speaks while calculation is deterministic, no fine-tuning framing), and Open Questions.

## Validation

- `python3 scripts/workflow.py validate` passes.
- Backlog shows the new middle slices in the intended order.
- No middle slice folder contains anything beyond `slice.json`.
