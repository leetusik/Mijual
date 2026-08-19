# Intent — P4

- Captured at: 2026-08-19T17:41:27+09:00
- Origin: operator

## Original Input (verbatim)

> ---
> - insepect the .zip file.
> - create phases for the 2026 ai challenge.
> - think, conversation with english, only the product will be have korean only surface.

## Confirmed Intent (refined + clarified)

Final phase of the 미주알 challenge project: make it real and submit before **2026-09-07 10:00**.

1. **Notifications**: D-day alert channel — email first, 카톡 as roadmap (handoff §6 item 4).
2. **Production deploy** to the operator's dev server (`ssh h`), with a public demo URL.
3. **Production polish**: smoke tests, honest-incompleteness notes, operational checks — the operator's "small scope, production-grade" standard.
4. **Presentation deck**: 주최사별 효용 매핑 (KB증권/카카오뱅크: missing retail feature; 금보원/금융위: investor protection + "숫자는 AI가 만들지 않는다" AI-trust principle; roadmap: 권리 데이터 MCP server → AI-agent policy agenda), AI-role architecture (§3.6) as the #1 expected Q&A, the P2 소멸 총액 number as the opening, extraction-accuracy report as evidence.
5. **Demo video + daker.ai submission** per the requirements P1 confirmed.

**Shared working rules (all phases):** think/converse/document in English; product surface (and submission-facing materials where the contest expects Korean) in Korean. Honor handoff §7: evidence-tagged facts, no inflation, small scope/production polish, AI reads & speaks / determinism calculates, no fine-tuning/PyTorch/HF framing. Context: `docs/reference/challenge/00_HANDOFF.md`, `01_문제정의.md`.

## Clarifications Resolved

- Q: 4-phase structure (spike → pipeline → web → ship & submit)? — A: **Yes, 4 phases** (deploy/polish and submission share this phase rather than splitting into five).
- Q: Web service phase — one mixed design+build phase or two-phase split? — A: **One mixed phase (P3).**
- Q: MVP rights-type 3종 — confirm ① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권 now? — A: **All 3 tentatively confirmed**, finalized after the P1 spike.

## Notes

- Operator schedule constraints (handoff §2): 창플 contract ends 8/31, job-application deadlines in parallel, 본선 발표 9–10월 — submission-package work must not assume full-time availability at the end.
