---
doc_id: product
version: v0002
created_at: 2026-08-20T05:10:14+09:00
source: P2.REVIEW
summary: 미주알 product truth after P2: the lapsed-warrant headline, the live rights board and the measured price of the trust gate
previous: v0001_bootstrap
---

# Product

## Status

P2 produced the product's evidence, not its interface: the numbers below are real, regenerable from
the corpus at zero spend, and ready for P3 to render. **No page exists yet.** Facts carry a command or
an `rcept_no`; estimates are marked `▷`.

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

- No chat UI as the default surface.
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

## Open Questions

- Everything about the interface: page structure, the board's default sort, how a 정정 is shown in
  place, and the Korean copy — all P3 (design-bearing).
- Whether the retrospective (소멸 총액) and the live board share one page or two.
- The 증권사 MTS 권리 메뉴 coverage matrix ("미발견 ≠ 부존재") is still unwritten differentiation
  evidence for the 기획서.
