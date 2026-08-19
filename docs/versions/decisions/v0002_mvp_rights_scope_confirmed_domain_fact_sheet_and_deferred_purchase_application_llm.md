---
doc_id: decisions
version: v0002
created_at: 2026-08-19T20:58:29+09:00
source: P1.REVIEW
summary: MVP rights scope confirmed, domain fact sheet and deferred purchase, application LLM
previous: v0001_bootstrap
---

# Decisions

## Status

Four operator decisions from the P1 scope gate (2026-08-19) are accepted and binding, plus the
domain fact sheet they were decided against. Later phases follow these, not the alternatives that
were weighed.

## Decision Log

### D-1 — MVP rights scope: keep all three types

- **Date:** 2026-08-19
- **Status:** accepted (operator, verbatim: "keep all")
- **Context:** The three candidate types were tentatively confirmed at phase creation, explicitly
  subject to demotion if the DART field survey showed extraction was too hard for the deadline. The
  survey demoted nothing: ① turned out *mixed* (deterministic 본문 skeleton + ~5 prose fields) rather
  than LLM-heavy, and both ② and ③ can ship with **zero** LLM extraction.
- **Decision:** the MVP ships **① 유증 신주인수권 (the hero) + ② CB 오버행 + ③ 매수청구권**, with the
  recommended exclusions standing:
  - **EB (교환사채) — out** (20 events/year; its corrections are mostly free text, and one sampled EB
    correction was a full 발행결정 철회, which needs an event-invalidation path nothing else needs).
  - **분할합병 · 주식교환·이전 — out** (same field shape as ③, would roughly double its universe
    cheaply, but that is a scope-sizing win for later, not a 19-day win).
  - **제3자배정 유증 — filtered out** (252 of 299 2026 유상증자 reports, and none issues a 신주인수권증서).
  - **소규모합병 — suppressed** (65 of 83 합병 reports; they grant no 매수청구권, so publishing them
    would be a correctness bug).
- **Condition attached and funded:** ② needs a **CB backfill to ≥ 2025-06** (▷ ~300–600 requests,
  ~half a day). Without it ② has density but no urgency — 0 of 267 cached 2026-filed CB events have a
  전환청구 개시일 before 2027-01-15.
- **Alternatives considered:** ② only (min risk, but no killer story and almost no answer to the
  template's "생성형 AI 역할" question); ① + ③ (sharpest story, board density collapses); ① + ②
  (loses the most money-specific card type and the suppression demo); all three + EB + siblings
  (rejected at D-19).
- **Consequences:** **drop order under deadline pressure is EB → ②'s backfill → ③ → ②, with ① last**,
  because ① is the only type that exercises the AI-reading layer at all. ② and ③ degrade the board
  rather than empty it if ① slips.
- **Source:** `works/phases/active/P1/slices/P1.S2/recommendation.md` (full reasoning, incl. the
  judging-week live-event scan) and phase P1's finding F25.

### D-2 — Custom domain: deferred, nothing purchased

- **Date:** 2026-08-19
- **Status:** accepted (operator, verbatim: "I'll get you a domain later.")
- **Context:** A custom domain is a **branding choice, not a submission requirement** — the rules
  demand only "실행 가능한 링크", so a platform hostname qualifies. What makes it time-critical is the
  URL freeze (see `operations`).
- **Decision:** no domain was bought; the operator will supply one later.
- **Consequences:** **plan for a platform hostname and treat a branded URL as a late swap.** Any
  operator-supplied domain must arrive and be **wired before the deployment freeze** — after the
  submitted URL is frozen it cannot change.
- **Source:** phase P1 finding F25-2. Fact sheet below.

### D-3 — Challenge registration: done

- **Date:** 2026-08-19
- **Status:** accepted (operator, verbatim: "I registered")
- **Decision:** 참가 신청 (which requires a `dacon.io` account and closes 2026-09-07 10:00, the same
  instant as submission) is complete. "Register" drops off the ship checklist; only the 제출 steps
  remain — and uploading is not 최종 제출.
- **Consequences:** ▷ not verifiable from this workspace (the 제출 탭 is login-gated); taken on the
  operator's word.
- **Source:** phase P1 finding F25-3.

### D-4 — Application LLM: Gemini 3.7 Flash (high thinking), operator's "changple5" credential

- **Date:** 2026-08-19
- **Status:** accepted (operator, verbatim: "I'll use gemini 3.7 flash high for the application. use
  changple5 credential.")
- **Decision:** the reading (schema-based extraction) and speaking (grounded generation) layers run on
  Gemini 3.7 Flash at high thinking, via the operator's "changple5" credential.
- **Consequences:** the architecture is **unchanged** — the AI reads and speaks, **all calculation
  stays deterministic**, and extracted fields still pass the arithmetic / date-order / citation-span
  gates before exposure. Commercial LLM APIs are explicitly permitted by the organizer at the
  entrant's cost. **The credential is not in this repo and must not be committed** — it is obtained
  from the operator and stored gitignored beside `DART_API_KEY`, read in-process, never echoed.
  ▷ The exact API model id is confirmed at integration time; model naming is the operator's call.
- **Source:** phase P1 finding F25-5.

### D-5 — Schedule management is operator-owned

- **Date:** 2026-08-19
- **Status:** accepted (operator, verbatim: "you don't need to worry about the schedule. I'll handle
  it. only focus on building")
- **Decision:** the calendar conflicts surfaced during recon (the decisive build week overlapping a
  possible employment start; the weekday offline 발표 심사) are the operator's to manage and **must not
  be re-raised or planned around** by later work.
- **Consequences:** this does **not** relax the 결격 uptime window — that is a property of the service,
  not of anyone's calendar, so monitoring, a rollback path, and snapshot-backed rendering with no
  upstream call in the request path all remain requirements (see `operations`, `data`).
- **Source:** phase P1 finding F25-4.

## Reference — mijual domain fact sheet (verified 2026-08-19)

Verified by direct registry whois; re-checked at the P1 review.

| Domain | Status | Price |
|---|---|---|
| `mijual.ai` | **AVAILABLE** (`whois.nic.ai` → `Domain not found.`) | ~**$82.70**/yr but with a **2-year minimum term** → **~$165 upfront**; the registry moved to $160 per 2-year term on 2026-03-05. ▷ Checkout total unverified — nothing was purchased; ▷ registrar spread ~$75–112/yr |
| `mijual.kr` | **AVAILABLE** (`whois.kr`) | **22,000원/yr + VAT** (도레지); ▷ 가비아·후이즈·카페24 comparable (~19,000–29,000원) |
| `mijual.co.kr` | **AVAILABLE** | same tier as `.kr` |
| `mijual.io` | **AVAILABLE** (`whois.nic.io`) | — |
| `mijual.com` | **REGISTERED — struck from the options** | GoDaddy, created 2018-08-28, Registry Expiry 2026-08-28. It **actively forwards to `https://blog.naver.com/tou2me`** (a live blog, so the owner looks like a renewer), and even on a zero-day grace the ICANN lifecycle (≤45d renewal grace → 30d redemption → 5d pendingDelete) puts its earliest possible drop at **2026-10-02**, weeks after the submission deadline. Waiting on it is not an option |

No account was created and nothing was purchased in reaching these facts.

## Superseded Decisions

- The rights-type 3종 was previously **tentative** ("confirm all 3 tentatively; the spike may demote
  one"). D-1 supersedes that with a measured, operator-confirmed keep-all — plus exclusions the
  tentative list did not name.
- `mijual.com` as a fallback domain, and any "watch it lapse" plan, is **withdrawn** (see the fact sheet).
