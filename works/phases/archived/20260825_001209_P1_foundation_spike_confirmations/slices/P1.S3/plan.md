# Plan — P1.S3: Recon — daker.ai submission requirements + mijual domain availability

## Goal

Turn the challenge's submission requirements and the mijual domain situation into **verified, durably recorded facts** (phase.md findings + Doc impact), so the operator can decide scope (P1.S2) and buy a domain with everything on the table, and so P4 (Ship & Submit) can be planned against the real rules.

## Context (read first)

- `works/phases/active/P1/phase.md` — Open Questions **Q5, Q6**; Constraints (evidence tags, no inflation).
- `works/phases/active/P1/intent.md` — recon scope: submission format, team rules, 본선 schedule vs the operator's 9/1 employment availability, domain availability.

## Advisory input (orchestrator's read-only probe, 2026-08-19 — verify, then record; treat as leads, not conclusions)

A prior probe found the daker.ai brief fully public via the unauthenticated JSON endpoint `https://daker.ai/api/hackathons/2026-finance-ai-challenge` (the HTML page is a JS SPA that renders empty to plain fetch). Its claims to verify:

- Deliverables, 2 stages: ① 공모전 기획서 PDF (from template) — due 9/7(월) 10:00, [제출 탭]; ② MVP 산출물 = 기능명세서 PDF + **웹서비스 URL** — due 9/7 10:00; ③ 최종 (발표 진출자만) = 발표자료 PDF + 소스코드 ZIP — due 10/8 23:59, via dacon@dacon.io. **No video required.**
- Templates: two .hwpx files publicly downloadable from `cfiles.dacon.co.kr` ((첨부1) 기획서, (첨부2) 기능명세서) — must be converted to PDF.
- **Uptime clause (결격):** submitted web URL must be reachable 9/7 11:00 ~ 9/11 23:59; inaccessibility = disqualification.
- Team: 1–4인, anyone eligible, no dual registration; 팀빌딩 needs 팀장's '팀으로 전환' before submitting. Registering/submitting needs a **dacon.io account**.
- Judging: 본선 = internal closed-panel review of all pre-screened submissions (100%), top ~11 teams (~1.5x) advance; 발표 심사 offline **2026-10-13(화)**, PT 15min + Q&A 5min, PDF only (PPT banned). Venue/details announced later to finalists.
- IP: no copyright transfer demanded; winners grant 금보원 a 5-year non-exclusive internal-use license. Reuse bans: no recycled entries from other competitions; winning entry can't be reused elsewhere afterward.
- No dataset provided by the organizers.
- Domains (whois): **mijual.ai AVAILABLE** (`Domain not found` from whois.nic.ai), **mijual.kr AVAILABLE**, **mijual.com REGISTERED** (GoDaddy, created 2018-08-28, **registry expiry 2026-08-28** — nine days out; may or may not drop).

## Work

1. **Verify** the advisory claims against the live sources (the API endpoint, the template URLs, whois). Where a claim checks out, record it as fact with the source; where it doesn't, record what you actually found. Do not re-derive everything from scratch — this is verification plus gap-filling.
2. **Fill the gaps the probe flagged:**
   - The 게시판/공지사항 (the stated official Q&A channel) — check for amendments, FAQ answers, or clarifications that modify the rules (accessible portions only; note if login-gated).
   - Download the two .hwpx templates into `docs/reference/challenge/submission/` (they are the required 양식 — small files, keep them) and note anything about their required structure that's visible (if .hwpx content is unreadable in this environment, record that honestly; conversion/reading can be a P4 concern).
   - Schedule-conflict check (Q5): lay out the timeline (9/7 submit → 9/7–9/11 uptime window → ~late Sep 본선 → 10/13 발표, 10/8 최종 제출) against the operator's constraints (employment availability 9/1, contract ends 8/31). Flag concrete conflicts as facts; the operator weighs them in S2.
3. **Domain facts (Q6):** confirm the three whois results yourself; add price-tier context for .ai (registry norms — .ai runs ~$70–90/yr at common registrars; mark as `▷` estimate unless verified) and .kr. Note the mijual.com expiry-watch option (expiry 2026-08-28; drop-catch timing uncertain). **Do not purchase anything** — purchasing is operator-only; your output is the decision-ready fact sheet.
4. **Record durably:**
   - Append findings to `phase.md` (new F-numbered entries) answering Q5 and Q6, including the uptime-결격 clause and the reuse-ban clauses (both shape P4 and the pitch).
   - Append Doc impact note(s): expect one against `operations` (submission requirements, uptime window, deliverable formats — this is ship/submit truth) and one against `decisions` (domain options fact sheet; the actual purchase decision lands in S2's operator round-trip).
   - Write `result.md`: crisp summary + the exact operator-facing bullet list S2 should relay (domain choice + any schedule-conflict flag).

## Boundaries

- Read-only against the outside world: no account creation, no registration, no purchases, no form submissions.
- Do not draft the 기획서/기능명세서 content (P4 work). Do not touch spike code or the matrix.
- Keep new repo files to the two templates under `docs/reference/challenge/submission/` (plus optional tiny notes file there if needed).

## Validation

- Every recorded fact carries its source (URL or command); estimates marked `▷`.
- Q5 and Q6 have explicit answers (or explicit "could not determine" with reason) in `phase.md`.
- `python3 scripts/workflow.py validate` passes.
