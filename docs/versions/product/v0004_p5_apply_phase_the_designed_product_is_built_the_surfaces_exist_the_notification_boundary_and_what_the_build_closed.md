---
doc_id: product
version: v0004
created_at: 2026-08-22T18:19:40+09:00
source: P5.REVIEW
summary: P5 apply phase: the designed product is built — the surfaces exist, the notification boundary, and what the build closed
previous: v0003_product_truth_after_the_p3_design_the_signed_surface_set_and_three-slot_nav_the_estimate_mark_the_anonymous-first_boundary_and_what_the_design_added
---

# Product

## Status

P2 produced the product's evidence; **P3 designed its interface and the operator signed it, round by
round; P5 built it.** The numbers below are still real and regenerable from the corpus at zero spend,
and they are now what the running product serves. **Every surface except the AI 질문 agent exists**
(the agent, its storage and its surfaces are P6; deployment is P4). Facts carry a command or an
`rcept_no`; estimates are marked `▷` **in documents and pipeline output — in the product's own UI the
estimate mark is the 「추정」 tag** (P3 R2 gate ruling).

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

## The Product P3 Designed — and P5 Built

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
- **② past-opening is 진행 중, never 종료.** **57 events today** have an open 전환청구 window — the
  dilution is live, and a single "종료" label across rights types would be backwards for all of them.
  The served definition is deliberately narrower than "the anchor is past": an ② whose 전환청구기간 has
  **fully closed** is not 지금 전환할 수 있는, and it moves to the 지나간 section. (Today no ② in the
  corpus has a fully-closed window, so the two populations coincide.)
- **챙긴 돈** — the user may mark a lapsed ① as claimed. It is the user's own claim, never mixed into
  disclosure data or aggregates.
- **A judge-facing sample portfolio** loads four real pinned events in one click, labeled as a sample,
  with no fake identity.
- **The admin panel is pure observation.** No action in it can change what the product exposes; that
  happens only through the pipeline CLI.
- ~~**Deferred by design, with a home:** 매수예정가 (③)~~ — **built and rendering.** The apply phase
  extended extraction/exposure and ③ detail now shows 매수예정가격 with a verbatim citation on 12 of
  the 16 exposable ③ events; the other 4 (소규모합병 and three 스팩 합병, whose filings state no price)
  render **no row at all** rather than a placeholder. Nothing was quietly dropped — and the backing
  cost 0 model calls, because the value turned out to be deterministic in two independent places.

### What the build added to product truth

- **The notification boundary: settings here, sending in P4.** 알림 설정 persists the 시점 칩
  (7 / 3 / 1 / 당일, default **7일 + 1일**) and the 수신 주소 (which *is* the account email — there is
  no second address). **An empty selection is a valid setting meaning "no mail"**, because the mail
  footer promises an off switch and deselecting every chip is the only one the signed surface offers;
  and **an absent preference row means the default, not "off"**. The KakaoTalk row renders a 「예정」
  chip and **no working control**, which is structural — no server field for it exists. **Nothing
  sends yet**: the channel, the schedule and the mail body are P4's.
- **The sample portfolio loads five D-day rows for its four pinned disclosures**, because one of them
  (대동기어) also holds an exposable ① that lapsed. The signed subline says 4건 and describes the
  *composition*, which is still four filings; the build prompt says "실제 corpus 이벤트를 그대로
  로드", so this is live data, not a deviation, and it must not be filtered out.
- **A judge or a reader can end the sample from anywhere** — the 「샘플」 chip and 샘플 종료 outrank
  both other account-slot renderings, because a loaded sample is a browser fact.
- **The product's only alert colour means one thing.** `--alert` is expiring/lost; an auth failure, a
  budget shortfall and a stale board all render in body ink or a reported style. The one alert on the
  operator console is 「실행 기록 없음」 — *did not run*, nothing else.
- **The AI 질문 slot ships as a signed frame with no content.** The nav's third slot and the footer's
  bottom-row link render **AI 질문** (R6's superseded label), and `/ask` is a bare shell — no invented
  copy, no fake chat. The event detail page ships **without** R6's 질문 스트립. Both are the P5/P6
  phase boundary, not dropped design elements.

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
- Still open after the build: the **"정정 이력" button label** (the detail page renders R3's literal
  and is now its second site), and the **운영자 연락처** string the AI 질문 agent hands out
  (operator-provided, never invented — **P6's**).
- ~~The real countdown cut-off instant~~ — a **stated default landed** (end of the 청약 day, KST),
  behind an environment variable, so the operator's real 접수 마감 시각 replaces it with no code
  change. Same shape for the 18-hour freshness threshold.
- ~~The vocky observation API shape~~ — **decided and recorded** in the R7 record's own §6.3 section.
  What remains is a **product** question, not a shape one: **vocky ships no embeddable widget script**,
  so the three signed feedback triggers have nothing to bind to and the observation view will observe
  an empty list until the operator wires a server-to-server capture path. Their product, their call.
- **The footer's gate-cost figure (49.2억원) is a dated-pack number beside live landing numbers.**
  The signed sentence is transcribed verbatim, but the presentation contract serves no gate-cost
  figure and deriving one needs the corpus-median 할인율 from a module the request path may not
  import. Making it live is **backing work** — a persisted precomputation plus a summary key — so it
  is a deferred job or a later fix slice, not a rendering change.
- **Two product states the design never drew**, both left honestly blank rather than filled with
  invented copy: an ① whose 청약 has closed but whose 증권발행실적보고서 has not been filed (it appears
  in neither 조회 section), and R7's 샘플 로드 여부 column (no server-side fact exists, because the
  sample is anonymous end to end).
- The 증권사 MTS 권리 메뉴 coverage matrix ("미발견 ≠ 부존재") is still unwritten differentiation
  evidence for the 기획서.
