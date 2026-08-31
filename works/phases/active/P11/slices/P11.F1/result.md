# Result — P11.F1 (Serve the start cards from the live corpus and drop two cards)

- **status:** `done`
- **summary:** The `/ask` start screen is four cards again, and the two 공시 cards no longer name a
  fixed company: a new read (`GET /ask/start-cards` → `reads.load_start_cards`) picks, on every
  render, an issuer with live 전환사채 filings and an ① that still exposes a 신주배정비율 before its
  deadline, so a card can never become a question the product cannot answer. All four cards were
  pressed live in dev **and** in the production build, and the fallback was exercised four ways for
  real — API stopped, dead origin, 12-second-slow origin, and a `null` slot.
- **files_changed:**
  - `src/mijual/web/reads.py` — `load_start_cards` + its two card pickers (the read layer)
  - `src/mijual/web/routers/ask.py` — `GET /ask/start-cards`, and the module docstring's 「one route」
  - `tests/test_web_ask_cards.py` — **new**, two cases
  - `frontend/app/ask/page.tsx` — the route becomes the start screen's data boundary
  - `frontend/components/ask/copy.ts` — the two templates, the static fallback, `startChips()`
  - `frontend/components/ask/AskPage.tsx` — `cards` prop (default = fallback) + the 「six cards」 doc
  - `frontend/components/ask/AskPage.module.css` — the 「Six cards / three rows」 comment
  - `frontend/lib/api.ts` · `frontend/lib/types.ts` — the client seam for the new path (see §7)
  - `works/phases/active/P11/phase.md` — notebook edit
- **validation:**
  | command | result |
  |---|---|
  | `.venv/bin/python -m pytest` | **pass** — 156 passed (154 before; the two new cases) |
  | `npm run typecheck` (frontend) | **pass** |
  | `npm run build` (frontend) | **pass** — 19 routes, **`/ask` is now `ƒ (Dynamic)`**, was `○ (Static)` |
  | `npm run smoke` (frontend) | **pass** — 22/22 |
  | `python3 scripts/workflow.py validate` | **pass** |
  | four-card press sweep, **dev** `http://127.0.0.1:3010/ask`, 1280×800@2 | **pass** — §3 |
  | four-card press sweep, **production** (`npm run build && npm run start`), same origin | **pass** — §3 |
  | grid measured at 1280 and 390×844@3 (touch), dev and production | **pass** — §5 |
  | derivation is live — shifted `today`, narrowed corpus, two different stub answers | **pass** — §4 |
  | fallback exercised: API stopped · dead origin · slow origin · `null` slot · one-slot `null` | **pass** — §6 |
- **deviations:** two files outside the plan's literal scope list, both the seam the plan's own
  "+ whatever read helper it legitimately needs" implies — see §7. Nothing else.
- **doc_impact:** three lines appended to `phase.md` `## Doc impact` —
  - `experience.md`: the start-card set is **four**, the two 공시 cards name a company **resolved per
    request** from the live corpus, `get_event` is demonstrated inside the 계산 card's chain, and
    **`save_feedback` is no longer shown on the start screen**; P11.S2's six-card lines in that same
    section are now stale and go in the same version.
  - `frontend.md`: `app/ask/page.tsx` **loads data** (`connection()` + `cache: "no-store"` + a 2.5s
    timeout), `AskPage` takes the sentences as a prop, and the **fallback contract** is durable —
    per-card fallback to `copy.ts`'s static four, so the empty state never shows a spinner or a hole.
    `/ask` is now a dynamic route.
  - `qa.md` `## Regression Checklist` **L403**: 「질문 카드 6장」 → **4장** (two even rows), the
    capability claim drops 의견 저장 and the bare-접수번호 row, and it gains this fix's two checks.
- **instrument:** **not Aside.** `which aside` → not found and there is no `/Applications` entry —
  the same finding `P11.S1` and `P11.S2` recorded. The documented fallback applies: the same sweep,
  at the same viewports, in the same manifest runtime, driven through the real **Google Chrome** this
  machine has, over CDP (`--headless=new`, `Emulation.setDeviceMetricsOverride`,
  `Emulation.setTouchEmulationEnabled` at 390). Every number and every answer quoted below was read
  out of that live DOM or off the wire; nothing here is inferred from source.

---

## 1. The four cards

| # | shape | company | tool(s) the press fires |
|---|---|---|---|
| 1 | `{회사} 전환사채 공시가 몇 건이나 있나요?` | **served, multi-hit** | `search_events` |
| 2 | `{회사} 유상증자, 1,000주 보유 시 배정 신주는 몇 주인가요?` | **served, R1** | 검색 → 이벤트 → `calculate` |
| 3 | 내 포트폴리오에서 가장 급한 일정은 무엇인가요? | none (static) | `get_portfolio` |
| 4 | 운영자에게 직접 연락하려면 어디로 하면 되나요? | none (static) | `get_contact` |

Dropped, per the operator: the bare 접수번호 `get_event` card and the 의견 `save_feedback` card.
`get_event` survives inside card 2's chain (measured below); `save_feedback` is undemonstrated by
their decision.

## 2. How the picking works

`GET /ask/start-cards` → `mijual.web.reads.load_start_cards(session, today=…)`, read off
`_board_views` — the board's own reading of the corpus, so a card can only name a company the board
would show, gated by the persisted verdict *and* the derived contract like every other surface. No
new query layer: the whole selector is a ranking over that one batched read.

**검색 slot.** Rank issuers by (multi-hit first) → (whole exposable set is that 권리 가족, so the 도구
행's 건수 and the card's own question count the same thing) → (most filings) → `corp_code`. Requires
at least one filing still on the board.

**계산 slot.** Candidates are exposable ① views whose `OfferingInput.inputs` carries an
`allotment_ratio` (the value the answer must cite) with `countdown.days >= 0`. Rank by D-day tier
(**D-20…D-60 first**, then further out, then D-7…D-19, then under a week) → (the issuer's only ①, so
the read cannot land on a sibling filing) → most headroom inside the tier → `rcept_no`. Then it
avoids the 검색 card's issuer when the corpus offers another.

**Both names must be findable by the agent's own search.** The card's sentence travels to
`search_events` → `find_corps` (not `resolve_corp` — the tool's contract is a list), so a candidate
is rejected unless `find_corps(name)` returns exactly that one issuer. A name that reached two
companies would make the card's own 건수 a claim about somebody else's filings. The check is bounded
to the first 8 ranked candidates per slot.

No Korean is in the payload: `{"reference", "search_events": {corp_name, corp_code, filings} | null,
"calculate": {corp_name, corp_code, rcept_no, dday, days} | null}`. Today it answers
`빛과전자 / 5건` and `아이에이 / 20260818000250 / D-45`.

## 3. The sweep — all four cards, dev and production

Each press is a fresh load of `/ask`, one click, a wait for the 푸터 frame, and a read of the
rendered DOM. **Dev** = `make stack-up` (`next dev`, `http://127.0.0.1:3010`). **Production** =
`npm run build && npm run start` on the same origin with the same env the Makefile uses (no
`MIJUAL_API_ORIGIN` override — the manifest's own recipe).

| # | 도구 행 that appeared (dev) | intended row | answer real? |
|---|---|---|---|
| 1 | `이벤트 검색 「빛과전자」 → 5건 · ② 전환사채 ×5 (20251219000568 … 20260729000387)` | **yes, only that one** | 「빛과전자의 전환사채 관련 공시는 총 5건이 확인됩니다.」 + chips `1 2 3 4 5` inline |
| 2 | `이벤트 검색 「아이에이」 → 2건` → `이벤트 읽기 → 아이에이 · ① 유상증자 · 20260818000250` → `계산 → 배정 신주 · 1,000주 × 0.507594018주 = 507주` | **yes** (the three-row chain) | 배정비율 cited `[2]`, 「배정 신주는 507주입니다」 |
| 3 | `내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)` | **yes, only that one** | 「포트폴리오(**구성 예시**)에서 … 대동기어 전환청구 개시일 … 2026-10-24, D-54」 |
| 4 | `운영자 연락처 → 미정` | **yes, only that one** | 「현재 등록된 운영자 연락처가 없습니다.」 — nothing invented |

**Production repeats every line of that table** (wording differs turn to turn — it is a live agent —
routing does not). The two confirmations the plan asked for, in both runtimes:

- **Card 2 shows exactly one 「입력」 marker beside exactly one cited chip.** The 검증된 계산 block
  reads `보유 주식 수 1,000주 [입력] | 1주당 신주배정비율 0.507594018주 [2] | 1,000주 × 0.507594018주
  = 507주 | 결과 507주`. The reader's own number carries no cite; the filing's ratio carries the chip.
- **Card 3's answer says 구성 예시** — in the sentence *and* in the 도구 행.

Card 1 also happens to be the cleanest live demonstration of P11.S1's chip fix: five 근거 on one
sentence, chips side by side after the period, no line break.

## 4. Proving the derivation is live (not a fixed pair with extra steps)

Three independent runs, because this is the thing the operator actually rejected:

1. **Shifted `today`, real corpus** (direct calls to the selector): 2026-08-31 → 아이에이 (D-45);
   +20d → 케이이엠텍 (D-43); +40d → 케이이엠텍 (D-23); +90d → **`null`** (no answerable ① left —
   the fallback path); −60d → 퓨쳐켐 (D-54). Same code, five different answers.
2. **Narrowed corpus, real database, never committed** (events set `suppressed` inside a transaction
   that was rolled back — re-reading afterwards returns the original pick): hiding 빛과전자 moves the
   검색 card to **HLB** (4건); hiding the next two four-hit issuers keeps HLB, as the `corp_code`
   tie-break says it should.
3. **Two different answers to one running production server** (a stub upstream toggled between
   requests, no restart): `/ask` rendered 「에이회사 …」 then 「씨회사 …」. That is the property Next
   would silently break by statically rendering the page — and it holds in the **production** build,
   where the route table now prints `ƒ /ask`.

**Nothing in this slice hard-codes today's answers.** 빛과전자 and 아이에이 appear in exactly one
place, `copy.ts`'s static fallback array, which is documented there as *the screen-must-not-be-empty
set*, not as the specification.

## 5. The grid, measured

Read out of the live DOM (`getBoundingClientRect` + `getComputedStyle`) — identical in dev and
production:

| viewport | grid | cards | rows |
|---|---|---|---|
| **1280×800@2** | `316px 316px`, gap 8px | 2 × **316 × 63 px** (the two long 공시 sentences), 2 × **316 × 56 px** | **two even rows**, y = 372 / 443 — no orphan |
| **390×844@3, touch** | `358px`, gap 8px | all four **358 × 56 px** | four single-column rows, y = 242 … 434 |

No clipping on any card at either viewport (`scrollHeight ≤ clientHeight`, `scrollWidth ≤
clientWidth`), and no horizontal overflow at 390 (`documentElement.scrollWidth === innerWidth ===
390`). Four cards fill two rows exactly, which is what the CSS comment now says.

## 6. The fallback, exercised (not read)

The plan calls this load-bearing, so it was broken on purpose five ways:

| what I did | result |
|---|---|
| **Stopped the API** (`kill` the `make stack-up` api pid), dev | `/ask` → 200 in **74 ms**, four static cards; confirmed in the browser too (4 cards, two rows, no spinner) |
| **Dead origin** (production pointed at a killed stub) | 200 in **30 ms**, four static cards, browser-confirmed |
| **Slow origin** (stub sleeping 12 s) | 200 in **2.52 s** — the 2.5 s timeout fires and the static four render; the page does not wait 12 s |
| **Both slots `null`** (corpus offers nobody) | four static cards, no hole |
| **One slot `null`** (`search_events: null`, `calculate` served) | card 1 falls back, **card 2 keeps today's company** — the fallback is per card, not all-or-nothing |

The empty-corpus case is also a unit test (`test_a_corpus_with_nothing_to_offer_answers_nulls_not_an_error`):
two issuers with no exposable filing answer `200 {search_events: null, calculate: null}`, never an
error, because this is the product's first screen.

## 7. Deviations, and what I rejected

**Deviation — two files past the plan's literal scope list, both a seam it implies.**
`frontend/lib/api.ts` and `frontend/lib/types.ts`. `api.ts` states its own rule in its header — 「Every
route path is hard-coded here … Adding a surface means adding a function here, with the response type
from `./types`」 — so a `fetch` written inline in the route would have been the deviation. The edits
are purely additive: one exported function, two exported types. `src/mijual/web/reads.py` is the
plan's own 「+ whatever read helper it legitimately needs」.

**Not touched, deliberately:** the footer, `get_contact`, `config.py` and `.env` (`P11.F2`'s files —
`git status` shows none of them), the chip work from `P11.S1`, `presets.ts`, and the agent package.

Rejected along the way:

- **A client-side fetch for the cards.** The start screen is the one surface that must never look
  empty; a client fetch means it starts empty every time. The route renders them server-side.
- **Korean in the API payload.** The endpoint returns companies, not sentences — `copy.ts` stays the
  single home of every Korean string this product renders, and the templates carry their citations.
- **A company-free wording for the fallback** (which would never go stale). R16 D11's surviving rule
  is that a 공시 question carries a 회사; a generic card would break the rule the phase kept. The
  fallback names companies and is documented as ageing — and it only ever renders when the same
  service's `/ask` is down too, so no sentence would have answered anyway.
- **`resolve_corp` as the findability check.** The card's sentence goes to `search_events`, which uses
  `find_corps`; checking the other resolver would have proved the wrong thing.

## 8. What I ran

```
.venv/bin/python           — corpus probes (R2 counts per issuer, R1 candidates with 배정비율 and
                             D-day), the selector at five reference days, the rolled-back
                             narrowed-corpus run
pytest / typecheck / build / smoke / workflow validate
curl                       — /ask/start-cards direct (8010) and through the Next rewrite (3010)
Chrome over CDP            — /ask press sweep ×4 (dev), ×4 (production), grid measurement at 1280
                             and 390 in both runtimes, and the fallback renders
a stub upstream on :8099   — per-request proof + the null / half / slow / dead fallback paths
```

The dev stack was stopped and restarted around the production run and is **back up**
(`make stack-status`: api pid 32687, web pid 32553, `http://127.0.0.1:3010`; `/api/ask/start-cards`
answers 빛과전자 / 아이에이). Every probe and the stub lived in the session scratchpad and are gone;
nothing was added to the repo but the files listed above. **Note for the concurrent `P11.F2`:** this
slice restarted the shared dev stack twice and ran a production server on 3010 for a while — if F2
saw a moment of 3010 serving a production build, that was this slice.

The notebook edits (the superseding card decisions, the three `## Doc impact` lines and the two notes
for `P11.REVIEW`) are in [`works/phases/active/P11/phase.md`](../../phase.md) and are not restated
here.
