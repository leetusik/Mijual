# Intent — P2

- Captured at: 2026-08-19T17:41:27+09:00
- Origin: operator

## Original Input (verbatim)

> ---
> - insepect the .zip file.
> - create phases for the 2026 ai challenge.
> - think, conversation with english, only the product will be have korean only surface.

## Confirmed Intent (refined + clarified)

Second phase of the 미주알 challenge project: build the data backbone the web service runs on, driven by the field matrix P1 produced.

1. **Collection pipeline**: DART OpenAPI ingestion for the confirmed MVP rights types, with scheduled jobs (Celery-beat-style), covering new filings and 정정공시 (기재정정) updates.
2. **Schema-based LLM extraction** (handoff §3.6 layer 1) for the fields the P1 matrix marked as unstructured — 증서 매매기간, 청약 취급 증권사, 실권주 처리, 리픽싱/콜풋/보호예수, 매수청구 통지 방법·기한, etc. — plus 정정공시 diff + interpretation.
3. **Deterministic validation gates** (layer 2): arithmetic consistency, date ordering, citation-span existence; per-field reason codes; failed fields are never exposed. All 금액/D-day computation is deterministic and unit-tested, LLM-free.
4. **"2026 소멸 신주인수권 가치 총액" estimation pipeline** (item 3): collect the year's 유상증자 filings, estimate lapsed-warrant value — the presentation-opening / landing-headline number.
5. **Extraction-accuracy evalset** (item 3-b): ~100 hand-labeled filings, per-field precision + gate-block-rate report, reusing the estimation pipeline's collected corpus.

**Shared working rules (all phases):** think/converse/document in English; product surface Korean-only. Honor handoff §7: evidence-tagged facts, no inflation, small scope/production polish, no chat-UI default, AI reads & speaks / determinism calculates, no fine-tuning/PyTorch/HF framing. Context: `docs/reference/challenge/00_HANDOFF.md`, `01_문제정의.md`.

## Clarifications Resolved

- Q: 4-phase structure (spike → pipeline → web → ship & submit)? — A: **Yes, 4 phases.**
- Q: Web service phase — one mixed design+build phase or two-phase design/apply split? — A: **One mixed phase (P3).**
- Q: MVP rights-type 3종 — confirm ① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권 now? — A: **All 3 tentatively confirmed**, finalized after the P1 spike.

## Notes

- Stack preference from the handoff §6 item 5: reuse the operator's existing stack (FastAPI or Django + Celery + Postgres); final architecture choice happens at decomposition/planning, not here.
