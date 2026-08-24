# Intent — P1

- Captured at: 2026-08-19T17:41:20+09:00
- Origin: operator

## Original Input (verbatim)

> ---
> - insepect the .zip file.
> - create phases for the 2026 ai challenge.
> - think, conversation with english, only the product will be have korean only surface.

## Confirmed Intent (refined + clarified)

First phase of the 2026 금융 AI Challenge project (**미주알 / mijual** — deadline-bound stock-rights protection service; submission deadline 2026-09-07 10:00). This phase de-risks everything downstream:

1. **DART OpenAPI validation spike** (handoff §6 item 1, top priority): with a real OpenDART key, run the 유상증자/CB·EB/합병 결정 APIs and produce the **event-type × field × {structured API / LLM extraction needed} matrix** — including ≥5 정정공시 (기재정정) samples to identify diff-target fields. This matrix fixes the extraction-target list for the AI "reading" layer (handoff §3.6 layer 1).
2. **Finalize the MVP rights-type scope with the operator** (item 2), starting from the tentatively confirmed list below.
3. **Recon**: daker.ai submission requirements (format, demo URL/video/기획서, team rules, 본선 schedule conflicts — item 6) and mijual domain availability (mijual.ai first choice, .kr/.com backups — from item 4).

**Shared working rules (all phases):** think/converse/document in English; the product surface (UI copy, user-facing text) is **Korean-only**. Honor handoff §7 principles: evidence-tagged facts vs. estimates, no inflation, small scope with production-grade polish, no chat-UI default, AI does reading & speaking while all calculation is deterministic behind validation gates, and never use fine-tuning/PyTorch/HF framing (금지선). Context source of truth: `docs/reference/challenge/00_HANDOFF.md` and `01_문제정의.md`.

## Clarifications Resolved

- Q: Does the 4-phase structure (P1 spike/confirm → P2 data pipeline → P3 web service → P4 ship & submit) match how you want the work organized? — A: **Yes, 4 phases.**
- Q: Should the web service phase be one mixed design+build phase or a design/apply two-phase split (design-cowork)? — A: **One mixed phase (P3)**, two-pass decomposition, leaner for the 19-day deadline.
- Q: Confirm the MVP rights-type 3종 candidates now — ① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권? — A: **Confirm all 3 tentatively**; the P1 spike's field matrix may still demote one if extraction proves too hard within the deadline.

## Notes

- The handoff zip was inspected and its two documents landed at `docs/reference/challenge/`.
