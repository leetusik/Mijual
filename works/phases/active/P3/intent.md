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

**This is a mixed design+build phase under the `design-cowork` skill**: the first DECOMP creates only groundwork slices, the design co-work round slice(s) (count decided at DECOMP), and `P3.DECOMP2`, plus a **build inventory** in `phase.md`; build slices are cut by DECOMP2 only after the operator-signed design. Brand identity (MIJUAL logo + 한글 미주알 병기, palette, type) is part of the design rounds — never invented by the orchestrator or executors. RESPECT THE DESIGN applies to all build slices.

**Shared working rules (all phases):** think/converse/document in English; **product surface Korean-only** (all UI copy, alerts, explanations in Korean). Honor handoff §7: evidence-tagged facts, no inflation, small scope/production polish, no chat-UI default, AI reads & speaks / determinism calculates, no fine-tuning/PyTorch/HF framing. Context: `docs/reference/challenge/00_HANDOFF.md` (§3.5–3.7), `01_문제정의.md`.

## Clarifications Resolved

- Q: 4-phase structure (spike → pipeline → web → ship & submit)? — A: **Yes, 4 phases.**
- Q: One mixed design+build phase or a design/apply two-phase split, per design-cowork? — A: **One mixed phase** — DECOMP → design round(s) → DECOMP2 → build; leaner for the 19-day deadline.
- Q: MVP rights-type 3종 — confirm ① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권 now? — A: **All 3 tentatively confirmed**, finalized after the P1 spike.

## Notes

- Frontend preference from the handoff: Next.js, SSE only for 해설 streaming. Final choices at decomposition/planning.
- Service name **미주알 / mijual** is operator-confirmed (handoff §3.7) — not in play at the design gate unless the operator reopens it.
