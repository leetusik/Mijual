# Plan — P1.S2: MVP rights-scope recommendation & operator confirmation

## Goal

Turn P1's evidence (S1's field matrix + S3's submission recon) into a **single decision-ready recommendation package** for the operator: keep/demote per rights type with measured rationale, plus the domain-purchase question and any schedule flags — one consolidated operator round-trip. This slice does **not** decide; it recommends and stops on the operator (`needs_operator`).

## Context (read first)

- `works/phases/active/P1/phase.md` — full Findings list (F1–F23), especially F8–F16 (matrix results) and F17–F23 (submission rules, domain facts); Constraints; Open Question Q4.
- `works/phases/active/P1/slices/P1.S1/result.md` — the per-rights-type feasibility table (universe / structured coverage / verdict) and the 정정 diff evidence.
- `works/phases/active/P1/slices/P1.S3/result.md` — contains the **verbatim operator-facing bullet list** prepared for this slice; incorporate it as-is (it covers domain options and deadline/uptime constraints).
- `docs/reference/dart/field-matrix.md` — cite it, don't restate it.
- `works/phases/active/P1/intent.md` — the tentative 3종 (① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권) and the standing rule: the operator decides; nothing auto-confirms.

## Fixed decision frame (from the operator, 2026-08-19)

The tentative 3종 is confirmed **only tentatively**; the matrix may demote a type if extraction proves too hard within the deadline (submission 2026-09-07 10:00, URL freeze + unattended uptime through 9/11). The operator explicitly chose to pause and decide personally.

## Work

1. **Write the recommendation** as `works/phases/active/P1/slices/P1.S2/recommendation.md` (this slice's durable deliverable; result.md summarizes it). Structure:
   - **Per rights type**: measured universe (S1), structured/LLM split (matrix), demo strength (does it feed the landing 관제 현황판 with live countdown data during 9/7–9/11 judging week?), build cost within the remaining ~18 days, and a **keep / demote / keep-with-condition** recommendation with 1-paragraph rationale. Consider explicitly: ②'s volume (263 CB) is what makes the landing board data-dense during judging week; ①'s 증서 매도 D-day is the killer user story but only ▷~4–5 events/month — check (from S1 data or a quick re-run of the cached spike scripts if needed) whether any ① event will actually be *live* during 9/7–9/11; ③ is near-free to build but needs the 소규모합병 filter and may show zero live events at judging time.
   - **Interaction with the demo**: which combination guarantees a non-empty, countdown-active board during the judged window — the judge sees the service unattended (F: 기능명세서 §5 requires stranger-executable verification).
   - **A recommended package** (your single best call, stated plainly) + what each alternative would cost/gain.
   - **The operator round-trip bullets**: incorporate S3's verbatim operator-facing list (domain choice: .ai ~$165/2yr vs .kr ~22,000원/yr, both available, must be wired before the deploy freeze; schedule facts: 발표 심사 10/13 offline, 최종 제출 10/8 — vs 9/1 employment availability, flag only, no advice on personal matters).
2. **Do not** touch the spike scripts' committed outputs, the matrix, or any P2/P3 concern beyond what the recommendation needs. Re-running cached spike scripts read-only for a "live during judging week" check is allowed (they hit the cache; the key stays unprinted).
3. **Wrap up**: append a short finding (the recommendation summary, one paragraph) to `phase.md` — do NOT append a Doc impact note yet (the `decisions` doc note lands only after the operator actually decides; note this explicitly in result.md so the confirmation step knows to add it). Write `result.md` with: the recommendation TL;DR, the exact question set for the operator, and what must happen after the operator answers (record decision in phase.md + Doc impact `decisions` note + slice back to in_progress → done).
4. **Return `needs_operator`** — not `done`. Your verdict's summary must contain the operator-facing question set so the orchestrator can relay it directly.

## Boundaries

- No purchases, no scope decision on the operator's behalf, no P2 planning.
- Honest numbers only; every claim sourced to a finding/matrix section or marked ▷.

## Validation

- `recommendation.md` exists, covers all 3 types + package recommendation + operator question set.
- `python3 scripts/workflow.py validate` passes.
