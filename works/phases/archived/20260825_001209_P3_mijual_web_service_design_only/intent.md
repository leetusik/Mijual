# Intent — P3

- Captured at: 2026-08-19T17:41:27+09:00
- Origin: operator

## Original Input (verbatim)

> ---
> - insepect the .zip file.
> - create phases for the 2026 ai challenge.
> - think, conversation with english, only the product will be have korean only surface.

## Confirmed Intent (refined + clarified)

Third phase of the 미주알 challenge project: the **Korean-only web service**, designed with Claude Design and built on the P2 pipeline. Surfaces from the confirmed 겉면 설계 (handoff §3.5):

1. **비로그인 landing = 전 시장 권리 관제 현황판** — live countdowns, "소멸 카운트다운 중인 신주인수권 N건 · 추정 가치 X억" headline (the P2 estimation number), event board.
2. **종목 검색 + 보유량 슬라이더** — instant per-holding conversion without login ("500주 보유였다면 83만 원 · 증서 매도 마감 D-3").
3. **놓친 돈 조회기** — retroactive missed-rights value for a stock/holding/period.
4. **개인화 2층** — portfolio registration, D-day list, sample-portfolio one-click load for judges.
5. **Grounded 해설 panel** — citation-forced explanation layer (§3.6 layer 3) on top of verified data.

**Re-scoped 2026-08-20 (see Clarifications Resolved): this is a DESIGN-ONLY phase under the `design-cowork` skill** — single-pass decomposition, DECOMP → design round slices (one round at a time, each with its own handoff and `pending` gate) → REVIEW. No `DECOMP2` and no build slices here; the build is a later **apply phase**. Scope additions from the same re-scope: the **vocky feedback touchpoint**, an **admin panel**, and **auth surfaces** are all designed in P3. Brand identity (MIJUAL logo + 한글 미주알 병기, palette, type) is part of the design rounds — never invented by the orchestrator or executors. RESPECT THE DESIGN applies to every apply-phase build slice.

**Shared working rules (all phases):** think/converse/document in English; **product surface Korean-only** (all UI copy, alerts, explanations in Korean). Honor handoff §7: evidence-tagged facts, no inflation, small scope/production polish, no chat-UI default, AI reads & speaks / determinism calculates, no fine-tuning/PyTorch/HF framing. Context: `docs/reference/challenge/00_HANDOFF.md` (§3.5–3.7), `01_문제정의.md`.

## Clarifications Resolved

- Q: 4-phase structure (spike → pipeline → web → ship & submit)? — A: **Yes, 4 phases.**
- Q: One mixed design+build phase or a design/apply two-phase split, per design-cowork? — A: **One mixed phase** — DECOMP → design round(s) → DECOMP2 → build; leaner for the 19-day deadline.
  - **A' (2026-08-20, supersedes the answer above; operator verbatim):** "make this phase design only. one by one. we have nothing to hurry. vocky will be added as feedback inception, admin panel required, auth related required." → **P3 is design-only**: DECOMP → design round slices → REVIEW. **No `P3.DECOMP2`, no build slices, no implementation code in P3.** Build moves to a separate **apply phase**, created later with `create-phase` after P3's signed design and sized from each round's implementation contract (`build-prompt.md`).
- Q: What is "vocky"? — A: the operator's **existing feedback-collection service**. Mijual embeds its widget/touchpoint as the in-product feedback inception point; the design rounds cover where and how it appears.
- Q: Stack? — A: **FastAPI + Next.js confirmed** (SSE only for 해설 streaming). Locked as system structure at the design gate, not in play as a visual decision.
- Q: Admin panel and auth? — A: **both required** and in scope for the design rounds — an operator-facing admin panel, and the auth surfaces (가입/로그인/세션) the 개인화 2층 needs.
- Q: MVP rights-type 3종 — confirm ① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권 now? — A: **All 3 tentatively confirmed**, finalized after the P1 spike.

## Notes

- Frontend preference from the handoff: Next.js, SSE only for 해설 streaming. Final choices at decomposition/planning.
- Service name **미주알 / mijual** is operator-confirmed (handoff §3.7) — not in play at the design gate unless the operator reopens it.
