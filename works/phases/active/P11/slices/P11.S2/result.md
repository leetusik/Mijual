# Result — P11.S2 (Rebuild the /ask start cards to demonstrate every agent capability)

- **status:** `done`
- **summary:** Replaced the four hard-coded `START_CHIPS_KO` cards — three of which are now dead
  questions in the live corpus — with six, one per agent capability
  (`search_events` · `get_event` · `calculate` · `get_portfolio` · `save_feedback` · `get_contact`).
  Every card was pressed live at `http://127.0.0.1:3010/ask` in the manifest runtime, in **dev and
  in the production build**, and each one fired its intended tool row and returned a real answer on
  the **first** sentence written — no card needed rewriting.
- **files_changed:**
  - `frontend/components/ask/copy.ts` — the six sentences + the rewritten D11 「넷이다」 provenance block
  - `frontend/components/ask/AskPage.module.css` — the stale 「Four cards, no 메타 card.」 comment
  - `frontend/components/ask/AskPage.tsx` — a doc comment that also said 「**four** question cards」 (see *Deviations*)
  - `works/phases/active/P11/phase.md` — notebook edit
- **validation:**
  | command | result |
  |---|---|
  | `npm run typecheck` (frontend) | **pass** |
  | `npm run build` (frontend) | **pass** — 19 routes, `/ask` static |
  | `npm run smoke` (frontend) | **pass** — 22/22 |
  | `python3 scripts/workflow.py validate` | **pass** |
  | six-card live sweep, dev `http://127.0.0.1:3010/ask`, 1280×800@2 | **pass** — §2 |
  | six-card live sweep, **production** `npm run build && npm run start`, same origin, 1280×800@2 | **pass** — §2 |
  | card grid measured at 1280 and 390, dev and production | **pass** — §4 |
  | card press at 390×844@3 with touch emulation, production | **pass** — §4 |
- **deviations:** one — a third file (`AskPage.tsx`) took a **comment-only** edit; see §6.
- **doc_impact:**
  - `experience.md`: the `/ask` start-card set is now **six cards, one per agent capability**
    (`search_events` HLB ② · `get_event` 로젠 ③ by 접수번호 · `calculate` 에코프로비엠 ① with a
    reader-supplied 1,000주 · `get_portfolio` 샘플/구성 예시 · `save_feedback` a first-person
    opinion that files a real queue row · `get_contact` honest-unset), replacing R16 D11's four
    read-a-filing questions by operator instruction. **The same section's stale P9 lines go in the
    same version:** L205 lists five tools where the agent has seven, and L206 still says the agent
    never calculates, which R16's auditable calculator superseded. (P11.S2)
  - `qa.md` `## Regression Checklist`: L403's 「질문 카드 4장」 → **6장**, and the check gains its
    capability claim — pressing the six one at a time fires 검색 · 이벤트 읽기 · 계산 · 포트폴리오 ·
    의견 저장 · 연락처, six distinct 도구 행. (P11.S2)
- **instrument:** **not Aside** — `aside` is not installed on this machine (`which aside` → `aside
  not found`, no `/Applications` entry), the same finding `P11.S1` recorded. The documented fallback
  applies: the same sweep, at the same viewports, in the same manifest runtime, driven through the
  real **Google Chrome** this machine has over CDP (`--headless=new`, `Emulation.setDeviceMetrics
  Override`, `Emulation.setTouchEmulationEnabled` at 390). Every measurement below was read out of
  that live DOM; nothing here is inferred from source.
- **`conversation_feedback` rows this verification left: 3.** Baseline was **3** (ids 1–3, from
  2026-08-22); the table now holds **6**. Ids 4, 5 and 6 are this slice's — one from the API-level
  routing probe, one from the dev browser press, one from the production browser press — all three
  carrying the card's sentence verbatim. §5 says what the operator may want to do about them.

---

## 1. What shipped

`frontend/components/ask/copy.ts`:

```
1  "HLB 전환사채 공시가 몇 건이나 있나요?"                                  → search_events
2  "접수번호 20260730000215 공시에는 무슨 내용이 있나요?"                    → get_event
3  "에코프로비엠 유상증자, 1,000주 보유 시 배정 신주는 몇 주인가요?"          → calculate
4  "내 포트폴리오에서 가장 급한 일정은 무엇인가요?"                          → get_portfolio
5  "공시를 원문으로 확인할 수 있어 좋았어요. 어려운 용어에 설명도 붙으면 좋겠습니다."  → save_feedback
6  "운영자에게 직접 연락하려면 어디로 하면 되나요?"                          → get_contact
```

All six strings are distinct (`key={q}` in `AskPage.tsx` is the sentence itself). `AskPage.tsx`'s
`.map` needed no component change and `AskPage.module.css` needed no rule change — only the two
stale comments. `security_check` is not a card (`intent.md`).

**R16 D11's two set-level rules hold.** Every 공시 question carries a 회사 or a 접수번호. The three
공시 cards are different companies × different 권리 가족 × different question shapes: HLB ② 전환사채
(검색) · 로젠 ③ 주식매수청구권 (접수번호로 열기) · 에코프로비엠 ① 유상증자 (계산). Cards 4–6 are
not 공시 questions, carry no company, and their tools take no filing argument.

The provenance comment above the array was rewritten from the D11 「넷이다」 paragraph: it now cites
`intent.md` §2 (「Replace the set with cards chosen so that clicking them one at a time demonstrates
every agent capability」) and the resolved clarification (「**Copy + card count may change**, existing
visual style kept, no design round」) as the operator override that supersedes 「4장」, in the P7
override style the file already uses; it names `phase.md` `## Decisions` for the mapping, records the
measured corpus facts, and keeps R16's own stale-line history intact (the 2026-08-25 메타-card
retirement is untouched; the build-prompt's 「5장」 is still catalogued as stale).

## 2. The live sweep — every card pressed, one at a time

Each press is a fresh page load of `/ask`, a click on that card, a wait for the `footer` frame, and
a read of the rendered DOM. **Dev** = `make stack-up`'s `next dev` on `http://127.0.0.1:3010`.
**Production** = `npm run build && npm run start` on the same origin (the manifest's own production
recipe; `-p 3010` is in `package.json`, so the access path is identical).

| # | card | 도구 행 that appeared (dev) | intended row present | answer real? |
|---|---|---|---|---|
| 1 | HLB 전환사채… | `이벤트 검색 「HLB」 → 4건 · ② 전환사채 · 20250924000387 · … · 20250820000179` | **yes, and only that one** | 「HLB의 전환사채 공시는 총 4건이 등록되어 있습니다.」 + 4 chips |
| 2 | 접수번호 20260730000215… | `이벤트 읽기 → 로젠 · ③ 주식매수청구권 · 20260730000215` | **yes, and only that one — no 검색 row** | 3 sentences: 정정공시 성격, 통지/행사 기간, 「주식매수예정가격은 2,116원입니다.」 |
| 3 | 에코프로비엠 유상증자… | `이벤트 검색` → `이벤트 읽기` → **`계산 → 배정 신주 · 1,000주 × 0.0910905009 = 91주`** | **yes** (three rows, as the plan's finding 3 predicted is legitimate) | 배정비율 cited, 「배정 신주는 91주입니다」 |
| 4 | 내 포트폴리오… | `내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)` | **yes, and only that one** | 「현재 포트폴리오는 **구성 예시** 기준입니다.」 + 대동기어 전환청구 개시 2026-10-24 (D-54) |
| 5 | 공시를 원문으로… | `의견 저장 → 운영자 검토 대기열` | **yes, and only that one** | 감사 인사 2문장, 도구 행 0칩 — and a real row landed |
| 6 | 운영자에게 직접 연락… | `운영자 연락처 → 미정` | **yes, and only that one** | 「현재 등록된 운영자 연락처가 없습니다.」 — **no invented address** |

**Production repeats every line of that table.** Same six tool rows, same tools, same shapes; the
model's wording differs turn to turn (it is a live agent), the routing does not. Two production
readings worth quoting: card 2 produced 「매수예정가격은 2,116원입니다.」 and a two-근거 sentence
(chips `3` `4` side by side after the period — P11.S1's fix, visible on a card answer); card 5's
answer named the suggestion back (「공시 용어 해설에 대한 제안을 운영진 검토 목록에 전달했습니다.」).

**No card needed rewriting.** That was the finding this slice was most likely to produce and it did
not appear — because each sentence was shaped against the two known holes before it was written
(§3), and each was probed at the API level (`POST /ask`, SSE) before the browser sweep.

### The three specific confirmations the plan asked for

- **계산 card — one 「입력」 marker beside one cited chip.** The rendered 계산 블록 reads
  `검증된 계산 | 배정 신주 | 보유 주식수 1,000주 **[입력]** | 신주배정비율 0.0910905009 **[2]** |
  1,000주 × 0.0910905009 = 91주 | 결과 91주`. Exactly one `입력` marker (the reader's 1,000주, which
  carries no `cite`) and exactly one 인용 칩 (`[2]`, the filing's `allotment_ratio`). Measured in dev
  and in production, identically.
- **포트폴리오 answer says 구성 예시.** Yes, in both runtimes and in the 도구 행 itself
  (`샘플 포트폴리오 · 4종목 (구성 예시)`).
- **연락처 answer is the honest-unset line.** `MIJUAL_OPERATOR_CONTACT` is unset, the 도구 행 reads
  `운영자 연락처 → 미정`, and the answer is 「현재 등록된 운영자 연락처가 없습니다.」 — nothing
  invented, nothing promised.

**No 「미확인」 marker appeared on any of the twelve answers** (six dev + six production); the whole
page body was searched for the string on every read, not just the sentence spans.

## 3. What I measured, and where the research leads were wrong

The plan's leads were re-measured rather than trusted. Three held, one did not.

1. **Corpus (held).** Re-run at corpus 2026-08-31 through `.venv/bin/python` + SQLAlchemy against
   `mijual-postgres` (`psql` is indeed not on PATH): **488 exposable events — R1 50 / R2 422 /
   R3 16**, exactly the lead's numbers.
2. **The four current cards are three-quarters dead (held, and worse than stated).** Loading
   `reads.load_board` per rights family: **계양전기 has no live row at all** (its ① 매매 마감 was
   2026-08-25, D+6), **퓨쳐켐 has none**, and **아시아나항공's ③ is `tbd`** — no countdown, its
   deadline gone. Only 대동기어 (② D-54) still answers. So three of the four cards a reader meets
   today are questions the product can no longer answer well.
3. **Deadline safety (held).** HLB제약 is D-1 and 툴젠 D-7 — both would expire before 2026-09-07, and
   neither is used. The three companies shipped are **HLB** (4건, nearest D-32), **로젠** (D-46,
   2026-10-16) and **에코프로비엠** (D-32, 2026-10-02). None expires before the deadline.
4. **The R3 caveat was WRONG — this is the slice's substantive correction.** The lead said 알에프텍 /
   로젠 / the three 스팩 expose only `dissent_notice_procedure` on their *current* filing version and
   that `appraisal_price` survives only on 아시아나's. `get_event("20260730000215")` returns
   `appraisal_price = {"price": 2116}` with the quote 「매수예정가격 2,116」 **on the current
   version**, and the live card answer prints 2,116원 with a chip. 로젠 is therefore a fully usable
   ③ card and the phase did not have to reach for the expired 아시아나 filing.
5. **`calculate` (held).** `allotted_shares` is the only viable card op, for the reason given:
   `d_day` and `lockup_release_date` come back precomputed from the reading tools and `_CALCULATOR`
   forbids recomputing them. `allotment_ratio` is API-tier (no quote), so its chip resolves to the
   `DART 원문 ↗` link — **it reads acceptably**: in the 계산 블록 it is an ordinary `[2]` chip beside
   its input row, and after P11.S1 it opens as a popover like any other.
6. **`SAMPLE_HOLDINGS` overlap — avoided, not accepted.** The sample names 계양전기 · 대동기어 ·
   한화솔루션 · 세기상사, and the 포트폴리오 card's answer duly surfaces 대동기어. **None of the three
   공시 cards names any of those four**, so the reader sees seven distinct companies across the six
   cards instead of the same two twice. I chose difference over coherence: the point of the set is
   breadth of capability, and repeating 대동기어 in two cards would read as a thin corpus.

### The three questions the plan left open, and how I settled them

- **The get_event card: a bare 접수번호.** Measured, the two shapes route differently: a company +
  field question fires 검색 **then** 이벤트 (card 3 shows exactly that chain), while
  `접수번호 20260730000215 …` fires **`get_event` alone, no 검색 row** — in dev and in production.
  So the 접수번호 card is the only card that isolates `get_event`, it makes the two 공시-reading
  cards visibly different question shapes (D11's second rule), and it demonstrates a real product
  capability a reader arriving from DART actually needs: paste the number. D11 permits it. The cost
  is a 14-digit string on the start screen; at 316px it wraps to two lines like every other card and
  clips nothing (§4).
- **The search_events card: yes, a multi-hit company.** `search_events("HLB")` returns **4건**, all
  ② 전환사채, and the 도구 행 lists all four 접수번호. The answer then rests two sentences on four
  근거 apiece — so this card also happens to be the cleanest live demonstration of P11.S1's fix
  (chips `1 2 3 4` inline after the period, no line break).
- **Consent on the 의견 card.** The sentence is the reader's own first-person opinion **and** a
  concrete suggestion — 「공시를 원문으로 확인할 수 있어 좋았어요. 어려운 용어에 설명도 붙으면
  좋겠습니다.」 The first-person voice is what carries the consent (`phase.md` Decision Q2): the
  reader is not asking *about* feedback, they are saying a thing, and the card sends their sentence
  verbatim. A 용어 설명 is a genuine gap (there is no glossary anywhere in the product), so the
  suggestion is honest rather than decorative. **The gate walkthrough should say plainly that
  pressing this card writes a row to the 운영자 검토 대기열** — that is the capability working, and
  it is the one card with a side effect.

**On the meta-question hole (lead 2), which was the real risk:** `_FINALLY` gives 인사 · 짧은 확인 ·
제품 메타 질문 no tool call at all. Card 5 clears it by being an unmistakable first-person opinion +
suggestion rather than a bare compliment; card 6 clears it by being about reaching a **person**
(「운영자에게 직접 연락하려면」) rather than about the product. Both fired their tool on the first
try, in all three environments (API probe, dev browser, production browser).

## 4. The cards themselves, measured

Read out of the live DOM (`getBoundingClientRect` + `getComputedStyle`), dev and production —
**identical numbers in both**:

| viewport | grid | card box | rows |
|---|---|---|---|
| **1280×800@2** | `grid-template-columns: 316px 316px`, gap 8px, block 640px | all six **316 × 63 px**, `min-height: 56px` | three even rows at y = 333 / 404 / 475 — **no orphan** |
| **390×844@3, touch** | `grid-template-columns: 358px`, gap 8px | five at **358 × 56 px**, the 의견 card at **358 × 63 px** (two lines) | six single-column rows, y = 236 … 563 |

- **No clipping on any card, at either viewport:** `scrollHeight ≤ clientHeight` and
  `scrollWidth ≤ clientWidth` for all six, both runtimes.
- **No horizontal overflow at 390:** `document.documentElement.scrollWidth === window.innerWidth ===
  390`. `word-break: keep-all` + `text-wrap: pretty` are doing the work; the 14-digit 접수번호 does
  not push the grid.
- **Six is the better count for the grid, not merely a permitted one.** Four cards left the second
  row half-empty in the 2-column layout; six fills three rows exactly.
- A card was pressed at 390 with touch emulation in the production build (card 1) and the flow is
  the same as at 1280: card sentence sent verbatim, tool row, answer, chips.

## 5. The three feedback rows this slice wrote

`conversation_feedback` went from **3 → 6**. Ids 4 (API probe, 15:37 KST), 5 (dev browser press,
15:40) and 6 (production browser press, 15:44) all carry the card's sentence verbatim and are
anonymous queue rows exactly like ids 1–3 from P6's own verification. Nothing else was written: no
new endpoint, no new state, no email. The operator may want them cleared out of
`/ops/feedback` before the P4 demo — three identical rows in the review queue are noise rather than
signal — which is why it is on `phase.md`'s `## Operator Questions` for the review to route rather
than something I decided.

## 6. Deviations

**One, comment-only.** `frontend/components/ask/AskPage.tsx` L33 said the start screen carries
「**four** question cards」. The plan's scope names `copy.ts` and `AskPage.module.css`'s stale
comment; this is the same stale-comment category in a third file, and leaving it would have left the
component's own doc block contradicting the array it maps. The edit changes **no code** — the JSX,
the `.map` and every import are untouched, and `npm run typecheck` / `npm run build` both pass. It
now says six, cites the operator instruction, and keeps R16's stale-line history.

Nothing else departed from `plan.md`. No backend file, no agent instruction, no `presets.ts`, no
chip work, and no CSS rule was touched — and no card needed a scope-widening change to route.

## 7. What I ran

```
.venv/bin/python  — corpus counts, load_board per rights family, get_event / search_events /
                    get_portfolio / get_contact / calculate payload probes, conversation_feedback counts
POST /ask (SSE)   — API-level routing probe of all six sentences before touching the browser
Chrome over CDP   — /ask press sweep ×6 (dev), ×6 (production), layout measurement at 1280 and 390
                    in both runtimes, one 390 touch press
npm run typecheck / build / smoke ; python3 scripts/workflow.py validate
```

The dev stack was stopped and restarted around the production run and is back up (`make
stack-status`: api pid 5283, web pid 18059, `http://127.0.0.1:3010` → 200). All probe scripts lived
in the session scratchpad and are gone; nothing was added to the repo but the four files above.

The notebook edits (the card-set decision, the refined `## Doc impact` lines, the new operator
question and the note for `P11.REVIEW`) are in
[`works/phases/active/P11/phase.md`](../../phase.md) and are not restated here.
