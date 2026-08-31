---
doc_id: product
version: v0011
created_at: 2026-08-31T11:15:15+09:00
source: P10.REVIEW
summary: P10 round 3: the favicon-scale mark entry now describes the shipped tile — transparent, one #2b8e6c ink at 75%
previous: v0010_p10_round_2_the_favicon-scale_symbol_gap_open_since_r1_is_closed_the_operator_supplied_a_square_symbol_export_so_the_mark_ships_at_16_32_180_with_nothing_cropped_or_invented
---

# Product

## Status

P2 produced the product's evidence; **P3 designed its interface and the operator signed it, round by
round; P5 built it; P6 added the AI 질문 agent.** The numbers below are still real and regenerable
from the corpus at zero spend, and they are now what the running product serves. **Every signed
surface now exists** — deployment is P4's, and one signed footer link is an open operator decision
(see *Open Questions*). Facts carry a command or an
`rcept_no`; estimates are marked `▷` **in documents and pipeline output — in the product's own UI the
estimate mark is the 「추정」 tag** (P3 R2 gate ruling).

**Working language rule:** the team thinks, converses and documents in **English**; the product's
user-facing surface is **Korean only**.

**P10 (리브랜드) renamed the product 주주의관제탑 and replaced the wordmark with the operator's own
mark.** The name is uniformly the unspaced **주주의관제탑**; the English `MIJUAL` wordmark and the
`MIJUAL OPS` bar mark are **retired with no romanized replacement**. Nothing about what the product
does changed. Code identifiers (`src/mijual/`, every `MIJUAL_*`, `X-Mijual-CSRF`) are deliberately
untouched, so the repository still spells the old name wherever a *user* cannot see it.

**P8 (디자인 폴리시 패스) polished every reader surface — seven more signed rounds, no new features.**
The product claims below are unchanged in substance; what moved is stated inline and marked **(P8)**,
and collected in *What P8 changed* near the end of this section. Surface 8 (운영 관제) was cancelled by
operator decision and ships in its R7 + P5/P7 state.

## Summary

**주주의관제탑** watches Korean disclosure (DART) for *shareholder rights with a deadline* — rights that
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

- **Six surfaces, two of them in the nav since P7.** Nav = **관제 현황판 · AI 질문**. R2 signed
  three (내 종목 조회 · 관제 현황판 · AI 질문); an explicit operator override in P7 removed the
  내 종목 조회 slot, because that surface is what the landing hero's own search *is* — it stays
  reachable at `/stocks`, from the hero, from an event detail's 「내 보유량으로 환산 →」 and from the
  agent's link row. Plus event detail (reached from the board), **내 포트폴리오** (behind the account
  menu) and the operator-facing **운영 관제** panel.
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
- ~~**A judge or a reader can end the sample from anywhere** — the 「샘플」 chip and 샘플 종료 outrank
  both other account-slot renderings, because a loaded sample is a browser fact.~~ — **no longer true
  (P8).** R8 retired both the chip and the control (the account slot has two states, and 로그인 여부
  is the state), and R13 officially **withdrew R5-4's 종료 clause**: no sample reset exists and none
  is coming. `clearSample()` runs only on 계정 이전, and a row deleted from a sample does not come
  back in that browser. The sample is now reached by **보유 종목 without a session** (and still by
  `?sample=1`).
- **The product's only alert colour means one thing.** `--alert` is expiring/lost; an auth failure, a
  budget shortfall and a stale board all render in body ink or a reported style. The one alert on the
  operator console is 「실행 기록 없음」 — *did not run*, nothing else.
- ~~**The AI 질문 slot ships as a signed frame with no content.**~~ — **filled by P6.** The nav slot
  and the footer link now open a real surface, `/ask` is a real page, and the event detail page has
  its 질문 스트립. See below.

### What P7 changed: the product as the operator actually runs it

P7 was a fix pass, not a feature phase — eleven things the operator found broken or rough in the
shipped P5/P6 product. **Six of the eleven were one bug and it was not in the product**: `next dev`
refuses to serve two client chunks and its HMR socket to any origin but `localhost`, so on the
operator's own `http://127.0.0.1:3000` the page rendered and **never hydrated** — nothing was
interactive and the tab reloaded itself while they typed. Three durable product facts came out of the
five that were real changes (the rest are in `experience` and `frontend`):

- **The nav is two slots** (above).
- **The board is read 15 rows at a time (P8 — was 30 in P7).** The 관제 현황판's ranked list shows 15
  and discloses the next 15 through the panel's own footer control. It is a **display window, never a filter** — the
  tab counts stay whole-board (전체 = 488), the order is untouched, and the whole list is still
  reachable. The design paginates nothing, so the number is an operator-confirmable default
  (`decisions`, D-24), not a signed one.
- **The search suggests, and the resolver still never guesses.** 내 종목 조회 offers up to eight
  candidates while the reader types, each carrying its 종목코드, and a chosen one opens that company
  by its exact handle. The product rule this looks like it contradicts is intact and is worth
  restating precisely: what this product may never do is let **the system** silently open a different
  company's 놓친 돈. A reader choosing from a list is the opposite of that, and a bare submit still
  resolves unique-or-decline.

### What P6 added: the AI 질문 agent

- **It is an agent, not a scripted answer pipeline** — the operator's own binding requirement. The
  model decides which of its five tools to call, in what order, over as many rounds as it needs, and
  when it is ready to answer. Nothing is fetched before it speaks, no tool fires because a question
  matched a pattern, and a question that needs no data (「계산해 주세요」) reaches the answer with
  **zero** tool calls. Observed live: on a search that found nothing, the model corrected its own
  query and searched again, unprompted.
- **It cannot make an uncited claim, and it cannot compute.** A sentence reaches the reader only if
  it rests on a verified verbatim span (or is itself a value a tool returned), every number in it
  came from a tool's own payload, and every quoted span is byte-exact. Anything else is **dropped
  before it is ever streamed** — not flagged, not shown with a caveat. Measured over a live pass:
  **27 of 27 stored quotes byte-identical** to the served payload, and **0 numerals unaccounted for**
  across 24 stored answers. That is the trust claim below, made mechanical.
- **Refusing is a first-class answer, not an error.** Five categories and no more — 철회 · 확정 전 ·
  공시에 없음 · 검증 미통과 폴백 · 계산 요청 — each with one fixed sentence, rendered in ordinary
  prose with **no alert colour and no icon**, and structured as ① the verified status fact (**with
  its own citation** — a refusal is citation-forced too) ② the family sentence ③ where to go instead.
  It never explains *why* more specifically than the family, because the reader-facing data carries
  no reason code and inventing one would be a claim with no source. A 확정 전 금액 question gets every
  known fact, cited, and a refusal of **the amount only**.
- **Unlimited and anonymous, and the copy says so.** No quota, no 「남은 질문 N회」, no exhausted
  state on any surface; the same behaviour signed-in or not; and the reader is told plainly that the
  conversation is stored anonymously for quality checks rather than being told it disappears.
- **The reader always sees what it read.** Each tool call prints a one-line fact row (「이벤트 검색
  「대동기어」 → 2건 · …」) as it happens — *what was read is part of the evidence* — and the answer
  ends with 근거 N건 · the filing number · the generation time in KST.
- **It reaches the reader in three places**: a corner launcher opening a fixed widget on desktop, a
  dedicated 「AI 질문」 page in the nav, and preset question chips on each event's detail page that
  open the conversation already scoped to that filing. On a phone the page *is* the surface — no
  widget and no launcher. The conversation follows the reader between them.
- **It costs about a cent a turn.** ▷ $0.0093 per turn estimated over a measured live sample
  (`gemini-3.7-flash`, low thinking) — never a billed figure. The surface being free and unlimited is
  what makes per-turn cost the product's cost rather than the reader's, which is why the model runs
  at the cheap setting: the guarantees are structural, so a cheaper setting cannot produce an
  unverified claim, only a blocked one.

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
- No trading, no brokerage integration, no purchase or exercise flow — 주주의관제탑 informs; the user acts
  in their own MTS.
- No price feed and no market data vendor: every number is derived from disclosure documents.
- No EB, no 분할합병 / 주식교환·이전 in the MVP (D-1).
- No model training of any kind — the story is about *use*, never training.

### What P8 changed: the polish pass, as durable product truth

Seven surfaces, one signed round each, and no new capability. What a reader can now do — or can no
longer do — that this doc previously stated otherwise:

- **The layer is called 보유 종목, not 포트폴리오,** on every reader surface (measured: 「포트폴리오」
  0건 on `/portfolio` and `/portfolio/notifications`). Routes, paths and component names are unchanged.
  Two R12-signed strings on the 로그인 page are the only reader-visible survivors of the old word, and
  they are an open operator decision.
- **`/portfolio` is no longer the product's only login-gated *route*.** Signed out it renders the
  sample instead of redirecting to 로그인. The gate itself is unchanged — the *account's rows* are
  still gated by the API's 401 — but the route answers anonymously.
- **The 관제 현황판 keeps itself current while a reader watches it,** without asking them to reload:
  every 60 s it re-reads the board and, when the served 기준시각 has moved, says so in the chip and
  marks the changed rows. When it has not moved, nothing on the screen changes at all.
- **The 소멸주의보 headline names a count, not a company,** when several offerings close on the same
  day (「3개 종목」 today) — the product does not pick one out of a tied set.
- **The last English screen a Korean-only reader could reach is gone.** A non-exposable filing, a
  mistyped address and an unmatched path all render the product's own Korean not-found, which **still says
  no reason why**. The last English string inside a *form* is gone too: the browser's own validation
  bubble no longer speaks for this product.
- **An absence is a fact about the filing.** On a ③ page whose 반대의사 통지 절차 is not in the current
  version, the product states the absence in a field row (the same dashed chip the countdown slot
  wears) instead of quietly dropping the section.
- **A resolved stock page names its stock,** and `/stocks` with no query states what the product
  watches (3종 · 감시 중 N건 · the 집계 범위 boundary) instead of being a void.
- **481–767 no longer has a widget or a launcher.** Every window below 768 gets the same full-width
  AI 질문 page a phone gets, and a 질문 스트립 chip there routes to the page. A preset chip shows the
  served field name and **sends a signed question**; a field key with no signed sentence produces no
  chip at all. The completed answer's 「근거 N건」 counts the numbers on the screen, not the filings —
  a deliberate client/server divergence (the rcept_no list beside it already says which filings).
- **The anonymous sample surface now carries the product's one conversion offer** (after 지나간 마감,
  without the session-loss lead line, which is false there because sample edits persist). So "the
  offer lives only under 조회 results" is no longer true.
- **계정 삭제 states its consequence only while armed**, and 주주의관제탑 owns its 의견 screen — a reader's
  message goes out with no contact field, no email and no account, and the surface says so.

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
  and is now its second site), and the **운영자 연락처** string the AI 질문 agent hands out. P6 built
  the honest behaviour — unset, the agent says it has no contact string rather than inventing one or
  promising one — so **only the value itself is outstanding, at P4/deploy**.
- **One signed element of the AI 질문 answer footer is not built: 「필드로 이동」.** The record lists
  three context links and the product renders two. Pointing at *one field* needs a new link kind, a
  per-field anchor on the detail page, and — the part the record does not write — a rule for which
  field, when an answer cites several across several filings. It was **not invented**, and it is
  entangled with the next item. **Draw it or strike it: an operator decision, and the one thing this
  phase leaves short of the record.**
- **The answer footer's link row is denser than the signed line suggests.** With three filings read
  it carries up to seven links on three lines and repeats 「이벤트 상세」, one of them for a filing that
  is not among the 근거 — because the links come from what the turn *read* while the footer's facts
  name what the answer *cited*. Limiting, capping or per-filing labelling are all design calls;
  nothing was dropped or relabelled unilaterally.
- **One more agent-surface call left to the operator**, honest as shipped: a completed refusal
  currently carries a footer (`근거 0건 · 시각`), which the record neither signs nor forbids.
  (The second item on this list — the agent printing raw contract numerals — was **dispositioned by
  the operator on 2026-08-23 and is closed**: agent prose now reads `3,200원` like every other
  surface. Nothing about never-compute moved; the tool contract hands over the reader's spelling of
  the exact value, and the respelling happens only after a sentence has passed the citation,
  never-compute and verbatim-quote checks.)
- **A withdrawn filing is answerable by number but not findable by name.** Asking 「썸에이지 유상증자
  어떻게 되나요?」 gets 공시에 없음, while the same event by filing number gets the signed 철회 refusal.
  That is the exposure contract working as designed — a withdrawn event is not exposable, so it is
  not a search result — but the record's own refusal example is a 철회 conversation reached by name.
  Changing it means changing the exposure contract, which this phase may not re-decide.
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
- ~~**There is still no favicon-scale symbol mark**~~ — **closed 2026-08-31 (P10 round 2)**, the
  oldest open item in this list. R1 disclosed the gap, R2 closed it with the ring logo, P10's first
  round retired those assets and re-opened it, and the operator closed it the only way the assets
  README allows: **they supplied a square symbol export**. Nothing was cropped out of the wordmark
  and nothing was generated, so the rule (*no image is substituted, generated or placeheld*) is
  **satisfied, not relaxed**. The sparkle cluster is now a **first-class symbol mark** — painted in
  the UI by CSS `mask` + `currentColor` from one asset, and composited at **16 / 32 / 180** for the
  favicon and the apple-touch icon. **Re-cut 2026-08-31 (P10 round 3, design round R18):** the tiles
  are now **transparent**, carrying a single `#2b8e6c` ink at **75 %** of the box instead of white ink
  on an opaque `#0a1310` square — the background existed only to hold contrast for an ink pinned to
  white, and `#2b8e6c` reads on a light tab (4.05) and a dark one (3.98) alike. **The launcher keeps
  the 84 % ink width**; one artwork, and now two placement rules for two different surfaces, recorded
  as a deliberate divergence. Verified served in dev and in a production build, on every reader and
  `/ops` route, with the served bytes hashed against the files on disk. **Two limitations are
  disclosed rather than fixed:** at 16px the five small dots are ~1.2px each and read soft (the fix —
  a second crop showing one star — is still explicitly *not* adopted, because one artwork with one
  rule beats two that disagree); and **no one has yet seen a tile inside a real OS tab strip**, since
  the machine running these passes has no Screen Recording permission and CDP captures page content
  only. That is the first thing the acceptance walkthrough asks the operator to look at.
- The 증권사 MTS 권리 메뉴 coverage matrix ("미발견 ≠ 부존재") is still unwritten differentiation
  evidence for the 기획서.
