# Result — P1.S2: MVP rights-scope recommendation & operator confirmation

**Status: `needs_operator` — by design, not by obstruction.** The slice's whole job was to produce a decision-ready package and stop on the operator; it did. Nothing was decided, nothing was purchased, no scope was confirmed on the operator's behalf.

Durable deliverable: **`works/phases/active/P1/slices/P1.S2/recommendation.md`**.

## TL;DR of the recommendation

**Keep all three types. Cut depth, not breadth.**

- **① 유증 신주인수권 — KEEP, make it the hero.** The matrix demoted nothing: ① turned out *mixed* (deterministic 본문 skeleton + ~5 prose fields, ~32 events/year) rather than LLM-heavy. It is the only type whose MVP actually exercises the §3.6 AI-reading layer, and the only killer user story.
- **② CB 오버행 — KEEP, with one condition.** Largest universe (263 CB reports) and the board's density, but a new measurement says **0 of 267 cached 2026-filed CB events have a 전환청구 개시일 before 2027-01-15**. Without a backfill to ≥ 2025-06 (▷ ~300–600 requests, ~half a day) ② is a 2027 calendar with no urgency. **EB (20 events) demoted out of the MVP.**
- **③ 매수청구권 — KEEP.** The plan expected this to be the demotion candidate ("may show zero live events at judging time"). Measured: **4 live events inside 9/7–9/11**, 14 of 19 매수청구권-bearing events still have a deadline on/after 9/7, near-total structured coverage, near-free on ②'s rails. **분할합병·주식교환 stay out** (deferred).
- **Filter-outs:** 제3자배정 유증 (252 reports, no 증서), 소규모합병 (65 reports, no 매수청구권).
- **Drop order under time pressure:** EB → ②'s backfill → ③ → ②. ① is the last thing to drop, not the first.
- **One non-scope recommendation the demo depends on:** the board must render from persisted snapshots, with **no OpenDART call in the request path** — F19's 9/7 11:00→9/11 23:59 window is 결격-grade and F15 measured transient upstream 503s.

## The new measurement this slice added

The plan asked whether any ① event would actually be *live* during the judging week. Answered with a read-only scan of the `P1.S1` response cache (no network call, key never read into output):

| type | live during 2026-09-07 → 09-11 | strongest evidence |
|---|---|---|
| ① | **YES** — 휴림에이텍 **신주배정기준일 = 9/9 (D-0, inside the window)**; 이렘 **신주인수권증서 매매기간 9/21~9/29 → D-12 counting down all week**. Both carry live 정정 stories. | 본문 `20260804000486`, `20260811000481` |
| ② | Dense but slow — 264 countdowns, **earliest 전환청구 개시일 2027-01-15**; only 4–6 near-term 청약/납입 items in-window | `20260107000643`; cache scan of 267 CB events |
| ③ | **YES, and more than expected** — 휴맥스홀딩스 (6,839원) / 휴맥스 (6,591원) 매수청구 행사기간 8/28~9/17 open all week; 에코볼트 (1,968원) / 알에프텍 (9,325원) 반대의사 접수 opens **9/8**, inside the window | `20260811000452`, `20260811000467`, `20260804000288`, `20260804000294` |

Plus a correctness demo that falls out for free: **6 소규모합병 filings have 반대의사 windows overlapping the same days and must be suppressed** (금호석유화학 `20260810000482`, 한국카본 ×4, HLB글로벌 `20260807000649`).

Everything above is already on the public record as of 2026-08-18, so the demo board is guaranteed non-empty without any new filing arriving. Honest limit: the scan's frame **is** the spike's frame (KOSPI+KOSDAQ, 2026-01-01~08-18), so §1.1 of the recommendation is a **floor, not a forecast**.

A second finding fell out of the same scan and is recorded in `phase.md` F24 because it binds P2: **`estkRs` schedules are version-stale in practice, not only in theory** — 휴림에이텍's `estkRs` still reads 청약 9/4~9/7 while its current 본문 reads 10/19~10/20. Any ① schedule claim not read from the 주요사항보고서 본문 is marked ▷ throughout the recommendation.

## The exact question set for the operator

Five questions, one round-trip. Q2–Q5 are `P1.S3`'s prepared bullets relayed verbatim; §5 of `recommendation.md` carries them in full.

1. **Rights scope (the gate).** Approve the recommended package (① + ② CB with backfill + ③; EB / 분할합병·주식교환 / 제3자배정 유증 out), or cut something specific along the stated drop order, or pick a different package from §3 of the recommendation.
2. **Domain.** `mijual.ai` available at ~$82.70/yr but with a **2-year minimum → ~$165 upfront**; `mijual.kr` / `.co.kr` available at 22,000원/yr + VAT; `mijual.io` available; **`mijual.com` is struck** (actively forwarding to a live Naver blog; earliest possible drop 2026-10-02, 25 days past the deadline). A custom domain is a branding choice, not a submission requirement — but the URL is frozen at submission, so it must be bought and wired **before the deploy freeze**. Buying is the operator's alone; nothing was purchased.
3. **Registration.** 참가 신청 closes **2026-09-07 10:00 KST**, the same instant as the submission deadline, and needs a **`dacon.io` account**. Do it now, not on 9/7. Solo entry carries no penalty.
4. **Schedule flags** (flags only, no advice on personal matters): the decisive build week 9/1→9/7 is exactly the week employment could start; 9/7 11:00→9/11 23:59 is a five-business-day unattended uptime window where failure is **결격**; 10/13 (화) 10:00–16:00 is an offline PT with no 대리인 possible; 9/23→10/8 is a low-friction packaging window.
5. **Two rules to acknowledge:** web-only (mobile-first responsive explicitly fine), and commercial LLM APIs explicitly allowed at our own cost — with real DART data being a free differentiator.

## What must happen after the operator answers

1. Record the decision in `phase.md` (a short "Q4 ANSWERED" note naming the confirmed package and any cuts).
2. **Then** append the Doc impact note against **`decisions`** — confirmed MVP rights scope, the exclusions, the drop order, and the domain outcome. *This slice deliberately filed no Doc impact note*, because until the operator decides there is no durable decision to record. `P1.REVIEW` consolidates it afterwards.
3. If the operator buys a domain, that fact also belongs in the same `decisions` note.
4. Move `P1.S2` back to `in_progress` and then `done` (orchestrator-owned; not this executor's to do).

## Validation

| check | outcome |
|---|---|
| `recommendation.md` exists and covers all 3 types + the recommended package + the operator question set | **PASS** — §2 per type, §0/§3 package + alternatives, §5 the five-question round-trip |
| `python3 scripts/workflow.py validate` | **PASS** — `VALIDATE OK` |
| Judging-week scan made no network call and printed no key material | **PASS** — cache-only reads under `scripts/spike/samples/`; scripts ran under `env -i`; no `crtfc_key` and no key value in any output or artifact |
| Committed spike outputs, the field matrix, and `_summary/*.json` unmodified | **PASS** — `git status` shows only `works/phases/active/P1/phase.md` and this slice's two new files as changed/untracked |
| Every claim sourced to a finding / matrix section / `rcept_no`, estimates marked `▷` | **PASS** — ▷ used for all inferred rates, costs and unverified items; §6 of the recommendation states the gaps |

## Deviations from `plan.md`

1. **The plan's premise for ① was inverted by measurement, in the good direction.** It asked me to "check whether any ① event will actually be *live* during 9/7–9/11", implying the answer might be no. It is yes — and better than the plan's framing, since the 배정기준일 lands on 9/9 and the 증서 매도 D-day counts down all week. Reported as measured rather than as the plan anticipated.
2. **③ was not demoted.** The plan flagged it as likely to "show zero live events at judging time". The scan found the opposite, so the recommendation keeps it. This is a factual correction to a plan assumption, not a scope change.
3. **Two exclusions the plan did not name** — EB out of the MVP, and 제3자배정 유증 filtered out — are recommended inside the three types rather than as new types. They are depth cuts within the plan's decision frame, not new decisions; both are stated as recommendations for the operator to accept or reject.
4. **One recommendation outside pure scope** (§4: snapshot-backed rendering, no OpenDART in the request path). It is included because the scope decision's demo value is only real if the board survives the unattended 결격 window; it is flagged as a P2/P3 requirement, and no P2 planning was done.
5. **The scan scripts were written to session scratch space and are not committed.** They read only the existing cache; the plan permitted re-running the cached spike scripts, and writing a throwaway reader was the smaller-footprint way to do it. Nothing under `scripts/spike/` was touched.

Boundaries held: no purchase, no account, no registration; no scope decided; no P2 planning; no commit; no status transition; **no Doc impact note** (deliberate, see above).
