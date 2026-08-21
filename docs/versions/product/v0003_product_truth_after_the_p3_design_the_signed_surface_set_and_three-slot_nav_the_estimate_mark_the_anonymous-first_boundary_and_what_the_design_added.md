---
doc_id: product
version: v0003
created_at: 2026-08-21T23:49:14+09:00
source: P3.REVIEW
summary: Product truth after the P3 design: the signed surface set and three-slot nav, the 「추정」 estimate mark, the anonymous-first boundary and what the design added
previous: v0002_product_truth_after_p2_the_lapsed-warrant_headline_the_live_rights_board_and_the_measured_price_of_the_trust_gate
---

# Product

## Status

P2 produced the product's evidence; **P3 designed its interface and the operator signed it, round by
round**. The numbers below are still real and regenerable from the corpus at zero spend. **No page is
built yet** — the build is the apply phase (P5 for everything except the AI 질문 agent, P6 for the
agent). Facts carry a command or an `rcept_no`; estimates are marked `▷` **in documents and pipeline
output — in the product's own UI the estimate mark is the 「추정」 tag** (P3 R2 gate ruling).

**Working language rule:** the team thinks, converses and documents in **English**; the product's
user-facing surface is **Korean only**.

## Summary

**미주알** watches Korean disclosure (DART) for *shareholder rights with a deadline* — rights that
expire quietly if nobody acts — and shows an individual investor what is happening to their shares,
when it expires, and where the statement came from in the original filing.

Three rights types ship in the MVP:

| | type | what expires | reading cost |
|---|---|---|---|
| ① | **유상증자 신주인수권** (the hero) | the 증서 lapses if it is neither exercised nor sold | mixed — the only type that needs the AI reading layer |
| ② | **전환사채 오버행** | the 전환청구 window opens and the dilution lands | zero LLM — all `API` |
| ③ | **주식매수청구권** | the 반대의사 통지 deadline passes | zero LLM — all `API` |

## The Opening Number

**▷ 718.1억원 of 신주인수권 value lapsed unexercised in 2026 YTD**, across **32** 주주배정 유상증자.

- **51,253,956 of 365,527,824 배정 증서 (14.02 %)** were neither subscribed nor sold.
- Per-offering 소멸률 **2.51 %–49.09 %**, median 11.60 %; largest single loss **▷ 206.4억원**
  (한화솔루션).
- ▷ Band lower edge **548.7억원** under the conservative 권리락 adjustment assumption.
- Method: ▷ 증서 이론가치 derived by inverting each filing's **own** 발행가 산식 (DART-only — there is
  no price feed); 소멸 증서 = **발행 증서 − 증서 청약**; framed on the **증권발행실적보고서**, the
  document that reports the actual 청약 result.
- Regenerate: `.venv/bin/python -m mijual.estimate report --today YYYYMMDD [--korean]` —
  **0 OpenDART requests, 0 LLM calls**, byte-identical across runs.

The retrospective number and the live board are **the same pipeline**: of the 32 offerings, **23 are
still open and 15 have a 청약 date ahead of them**.

## The Live Board (what P3 renders)

Measured 2026-08-20 (`.venv/bin/python -m mijual.gates run`):

- **488 exposable events — ① 50, ② 422, ③ 16** — and **409 renderable field instances**.
- ② urgency, the reason the CB backfill was funded: **33 events open 전환청구 within 30 days of
  2026-09-07**, 82 within 90, 152 within 180; max 오버행 **67.8 %**.
- Every rendered field carries a **citation span into the original filing**, and every countdown is
  computed deterministically in KST.

Three states that are product features, not error handling:

- **철회** — a withdrawn 유상증자 renders **"이 유상증자는 철회되었습니다"** instead of a live
  countdown (detected deterministically from the 정정 table; 15 withdrawal filings in the corpus).
- **추후결정** — a suspended schedule renders as 추후결정 with **no date shown at all**; the superseded
  date is structurally unable to leak.
- **소규모합병 suppression** — mergers that grant no 매수청구권 are never published as a live right.

## The Trust Claim, and Its Measured Price

The product's core promise is that **a field that fails its deterministic gate is never shown** — it
is recorded with a reason code instead. That promise costs something, and the cost is measured rather
than assumed:

- **▷ 49.2억원 — 6.4 % of the headline — is deliberately left on the table.** Three offerings with a
  citable 실권 count are excluded from the total because their 할인율 extraction failed its citation
  gate (▷ upper bound if they were priced at the corpus median 할인율: 767.3억원).
- **Verified on the live corpus, not just by test:** 409 renderable field instances, **0** of them
  outside `passed`/`tbd`; **0** `tbd` fields leaking a value; **0** exposable events in a
  non-exposable state.
- **Accuracy of what the product would show: 98.6 % strict** (213/216 random picks, 95 % Wilson
  [96–100 %]), 100 % counting partials. **These labels are cross-model judgements — Claude judging
  Gemini extractions, at the operator's direction — and explicitly not human ground truth.** Any
  public use of the number must say so (see `qa`, `decisions` D-7).

## The Product P3 Designed

Seven signed design rounds (R1–R7) turned the evidence above into a product. The full surface map,
journeys and states are in `experience`; the design system is in `frontend`; the record itself is
`docs/reference/design/` (contracts in `rounds/<NN>/output/build-prompt.md`, approvals in `SIGNOFF.md`).
What is durable **product** truth:

- **Six surfaces, three of them in the nav.** Nav = **내 종목 조회 · 관제 현황판 · AI 질문**. Plus
  event detail (reached from the board), **내 포트폴리오** (behind the account menu) and the
  operator-facing **운영 관제** panel.
- **Anonymous-first is a product boundary, not a default.** Everything except 내 포트폴리오 works with
  no account: the board, per-holding 환산, 놓친 돈, event detail, and AI 질문 (**unlimited, anonymous,
  no quota display anywhere**). Login is offered after value is delivered — never as a gate.
- **The landing is one page.** The retrospective 소멸 총액 and the live board share the 관제 현황판;
  the hero is search-first (내 종목 연결 → submits to 내 종목 조회). *This closes the open question
  carried by v0002.*
- **「추정」 replaces ▷ in the UI.** A bordered 「추정」 tag marks every estimate on every surface; a
  fact carries no mark. `▷` remains the internal/document marker.
- **The 소멸주의보 sub-brand is confirmed** as a named element — a hazard-striped strip on the landing.
- **Per-holding conversion is a number input, not a slider** (direct integer + preset chips
  100·500·1,000주), and it is **session-memory only** — never stored server-side for an anonymous user.
- **"아직 확정 전" is a product state.** A live ① usually has no 확정발행가 yet (published ~1 business
  day before 청약), so the most urgent events show share counts and a `발행가 확정 전` chip instead of
  money. The product never invents an amount to fill the space.
- **② past-opening is 진행 중, never 종료.** 56 events today have an open 전환청구 window — the dilution
  is live, and a single "종료" label across rights types would be backwards for all of them.
- **챙긴 돈** — the user may mark a lapsed ① as claimed. It is the user's own claim, never mixed into
  disclosure data or aggregates.
- **A judge-facing sample portfolio** loads four real pinned events in one click, labeled as a sample,
  with no fake identity.
- **The admin panel is pure observation.** No action in it can change what the product exposes; that
  happens only through the pipeline CLI.
- **Deferred by design, with a home:** 매수예정가 (③) is not rendered because it is not in the exposure
  contract — the apply phase builds the extraction/exposure backing first, then a design-fidelity slice
  adds it. Nothing was quietly dropped.

## Differentiators That Are Facts, Not Claims

- **Real filings, not dummy data.** The organizer permits 더미 데이터 with disclosure; running on live
  DART is a free differentiator.
- **정정공시 is a first-class story.** A correction that moves 납입일 by a month moves the user's D-day
  by a month, and the pipeline stores every version and snapshot so the change can be shown — not just
  the latest state.
- **The AI reads; determinism calculates.** The model extracts a value **and a verbatim quote**; the
  package itself locates the quote in the stored document. All 금액/D-day arithmetic is LLM-free and
  unit-tested. This is the direct answer to the 기획서's "생성형 AI 모델의 역할" question.

## Non-Goals for Now

- **No chat UI as the default surface** — still binding, and honored by the signed design: the product
  opens on the 관제 현황판 board, and AI 질문 is a deliberate affordance (a corner launcher, a nav slot,
  and presets generated from gate-passing fields) that never occupies the default surface. The operator
  authored this shape in the R6 session with the constraint stated in the handoff.
- No trading, no brokerage integration, no purchase or exercise flow — 미주알 informs; the user acts
  in their own MTS.
- No price feed and no market data vendor: every number is derived from disclosure documents.
- No EB, no 분할합병 / 주식교환·이전 in the MVP (D-1).
- No model training of any kind — the story is about *use*, never training.

## Terminology

- **신주인수권증서** — the tradable right issued in a 주주배정 유상증자; it lapses if neither exercised
  nor sold.
- **소멸(가치)** — the value of 증서 that expired unexercised and unsold.
- **오버행** — shares a CB can convert into, as a ratio of outstanding stock.
- **매수청구권** — a dissenting shareholder's right to have shares bought back around a merger.
- **정정공시** — an amended filing; the `3. 정정사항` table is the authoritative what-changed list.
- **exposable / renderable** — the persisted P2 → P3 contract: an *event* is exposable, a *field* is
  renderable (see `data`).
- **「추정」** — the product's estimate mark: a bordered tag beside any derived value. An estimate never
  renders untagged; a fact never carries the mark.

## Open Questions

- ~~Everything about the interface~~ **Closed by P3's signed design** (see `experience` / `frontend`).
  What remains is implementation, not product definition.
- ~~Whether the retrospective (소멸 총액) and the live board share one page or two~~ **Closed: one page**
  (R2, operator-signed).
- Still open, all carried to the apply phase: the **"정정 이력" button label**; the real countdown
  cut-off instant (assumed 2026-09-04 24:00 KST); the **운영자 연락처** string the AI 질문 agent hands
  out (operator-provided, never invented); and the vocky observation API shape.
- The 증권사 MTS 권리 메뉴 coverage matrix ("미발견 ≠ 부존재") is still unwritten differentiation
  evidence for the 기획서.
