# Plan — P11.S2 (Rebuild the /ask start cards to demonstrate every agent capability)

Kind `implementation`, risk `high`, executed by `slice-executor-high`.

## The defect

`frontend/components/ask/copy.ts` L306–323 hard-codes four `START_CHIPS_KO` cards
(계양전기 · 퓨쳐켐 · 대동기어 · 아시아나항공), all read-a-filing questions. They
exercise `search_events` + `get_event` and nothing else, so the auditable
calculator, the portfolio D-day read, the feedback queue and the operator contact
are invisible from the first screen a reader meets — and from the P4 demo video.

Read `works/phases/active/P11/phase.md` in full first. Its `## Decisions` and the
`**(from P11.DECOMP, for P11.S2)**` note block are binding and are not repeated
here; consume that note block when you are done. `P11.S1` has landed, so the
chips in the answers your cards produce are the re-cut ones.

## What to build

**Six cards, one capability each** — `search_events` · `get_event` · `calculate` ·
`get_portfolio` · `get_contact` · `save_feedback`. The mapping is decided; the
final Korean sentences are yours. A 2-column grid gives three clean rows.
`security_check` is not a card (`intent.md` says why).

**The card's sentence is the question sent, verbatim.** `AskPage.tsx` L119–130 is
a bare `.map` and needs **no component change** for six.

## Findings from a prior research pass — verify, don't just trust

These were gathered by a read-only agent while `P11.S1` ran. Treat them as leads
that save you time, not as established fact: **re-measure anything you rely on.**

1. **`calculate`: `allotted_shares` is the only viable card op.** `d_day` and
   `lockup_release_date` are already computed upstream and returned by the reading
   tools (`20251016000315` comes back with `lockup_release.release_date` and
   `countdown.dday`), and both the tool declaration and `_CALCULATOR` in
   `src/mijual/agent/instructions.py` forbid recomputing a number another tool
   returned — so a 전매제한 해제일 or D-day card would answer correctly and **never
   call `calculate`**, failing the one thing it exists to demonstrate.
   `lapsed_warrants` needs two numbers the reader does not have;
   `excess_subscription_cap` needs a derived input and chains two calls. So: a
   company + 유상증자 + a **reader-supplied 보유 주식 수** → 배정 신주, which is also
   the shape that yields exactly one 「입력」 marker beside one cited chip.
   Note `allotment_ratio` is an API-tier fact (no quote), so its chip resolves to
   the `DART 원문 ↗` link rather than a 인용 스팬 — still a chip, and after S1 it
   opens as a popover. Confirm that reads acceptably.
2. **The meta-question hole is the real risk to the 의견 and 연락처 cards.**
   `_FINALLY` instructs the model that 인사 · 짧은 확인 · 제품 메타 질문 get **no
   tool call at all**. A bare compliment reads as 짧은 확인 and fires nothing. The
   의견 card must be an unmistakable **first-person opinion + a suggestion**; the
   연락처 card must be unmistakably about reaching a **person**, not about the
   product.
3. **You cannot force a card to fire exactly one tool** — the agent loop names no
   tool and no ordering; every call is the model's. Hold yourself to the standard
   the notebook actually sets: the **intended tool row appears** and the answer is
   real. A calculate card legitimately shows 검색 → 이벤트 → 계산.
4. **Corpus freshness decides which companies are usable.** Measured at corpus
   today 2026-08-31: 488 exposable events (R1 50 / R2 422 / R3 16). Two of the
   current four are already dead demos — 계양전기's 매매 마감 is **D+6** and
   아시아나's R3 deadline has passed. **Do not pick a card whose deadline expires
   before the P4 demo on 2026-09-07**: HLB제약 is D-1 and 툴젠 D-7. Prefer
   **D-29…D-54**. A candidate spread with three different companies × three
   different 권리 가족 × three different question shapes: 에코프로비엠 R1 D-32
   (the calculate card, ratio `0.0910905009`) · 대동기어 R2 D-54 (get_event —
   보호예수 / 리픽싱) · 알에프텍 R3 D-22, **or** a bare 접수번호 for get_event.
   **Caveat on R3:** 알에프텍 / 로젠 / the three 스팩 expose only
   `dissent_notice_procedure` on their *current* filing version —
   `appraisal_price` exists only on older versions, so a 「주식매수청구 가격」
   question on them answers 공시에 없음. 아시아나 is the one with it on the current
   version, and its deadline has passed.
   **Re-run the corpus check yourself before writing any card** — countdowns move
   daily. `psql` is not on PATH; go through `.venv/bin/python` + SQLAlchemy
   (`mijual-postgres`, `localhost:5434`). A per-card end-to-end tool check is
   worth running before you touch the browser, but note it proves only that the
   tools answer, **not that the model routes there** — the browser press is what
   proves the card.
5. **Mechanics.** `key={q}` in `AskPage.tsx` is the sentence itself, so **all six
   strings must be distinct**. The card grid lives in `AskPage.module.css`
   L92–122 / L174–190 (not `Ask.module.css`, and untouched by S1); `min-height:
   56px`, `word-break: keep-all`, `text-wrap: pretty`, 2 columns → 1 at ≤767 —
   no CSS change should be needed for six, but **the comment at L94 ends 「Four
   cards, no 메타 card.」 and must be updated.** The widget draws no start cards
   (`START_CHIPS_KO` has exactly one importer); this is the `/ask` empty state
   only.
6. **`SAMPLE_HOLDINGS` (`src/mijual/web/portfolio.py` L91–96) names 계양전기 and
   대동기어.** If your 공시 cards name them too, the portfolio card's answer will
   echo them. Decide whether that reads as coherence or as sameness, and say which
   you chose.

## Three questions to settle as you write

- **The get_event card:** a bare 14-digit 접수번호 (crisp routing, ugly sentence)
  or a company + specific field value (natural, but the search row appears too and
  the two 공시 cards risk looking alike)? D11 permits a 접수번호 card.
- **The search_events card:** use a **multi-hit** company (HLB → 4건) so the row
  visibly demonstrates 「several matches are normal」?
- **Consent on the 의견 card.** Pressing it files a real row. `phase.md` Decision
  Q2 holds that the first-person sentence *is* the consent — make the sentence
  carry that weight, and name the point in your `result.md` so the review can fold
  it into the gate walkthrough.

## Copy rules — inventing a Korean string is a design change

`frontend.md` L465–467: a Korean string enters through the surface's own `copy.ts`
**with a citation**. Your authorization is this phase's `intent.md` §2 +
`phase.md` `## Decisions`; cite them beside the entries in the same voice the file
already uses for an operator override (see `chrome/copy.ts` L64–69's P7 note, and
the existing `presets.ts` per-line citations). **Rewrite the D11 「넷이다」
paragraph at `copy.ts` L312–317** — do not leave it standing beside a six-element
array. R16 D11's two set-level rules survive the count change and bind you: every
공시 first question carries a 회사 (or 접수번호), and the 공시 cards are different
companies × different 권리 가족 × different question shapes. The three non-공시
cards carry no company and do not breach it.

## Verify — live, one card at a time, in the operator's runtime

`docs/current/operations.md` `## Operator Runtime`: `make stack-up`,
`http://127.0.0.1:3010`, Chrome desktop **and** 390, plus the production build.
**Press every one of the six cards** and record, per card: the tool row(s) that
appeared, whether the intended one is among them, and whether the answer is real.
A sentence that routes elsewhere gets **rewritten and re-pressed** — record which
and why, because that is the finding this slice is most likely to produce.
Specifically confirm the 계산 card shows one 「입력」 marker beside one cited chip,
the 포트폴리오 answer says **구성 예시**, and the 연락처 answer is the honest-unset
line without inventing an address.

Also check the cards themselves at **390**: six sentences of differing length in a
1-column grid, `min-height: 56px`, no clipping, no orphan.

**Instrument:** prefer Aside (`aside mcp`). `P11.S1` found it is not installed on
this machine, so the documented fallback applies — the same sweep, at the same
viewports, in the same manifest runtime, through the real browser this machine
has. Name the instrument you actually used and never claim a run you did not make.

**Say how many `conversation_feedback` rows your verification left.** Pressing the
의견 card writes one each time; that is the capability working, but the count
belongs in `result.md`.

Run the frontend's own checks too (`npm run typecheck`, `npm run build`,
`npm run smoke`) and `python3 scripts/workflow.py validate`.

## Scope

`frontend/components/ask/copy.ts`, and `AskPage.module.css`'s stale comment. No
backend, no agent instructions, no `presets.ts`, no chip work (S1 owns that and it
has landed). If a card cannot be made to route without a change outside this
scope, **stop and say so in `result.md`** rather than widening.

## Notebook and result

Edit `phase.md` under budget (it is at 166 lines / 14.4 KB of 200 / 16 KB — you
will need to **compress**, not just add; the pre-edit notebook is in git and the
detail belongs in `result.md`). Replace superseded `## Decisions` lines, refine the
foreseen `experience.md` `## Doc impact` line to what you shipped — it also owes
the section's **stale P9 lines** (L205 lists five tools, L206 says the agent never
calculates, both superseded) — keep the `qa.md` regression line, drop the note
block you consumed, and rewrite `## Now` last. Do **not** run `doc-new-version`.

Write `result.md` **verdict block first** with the per-card routing table, the
instrument, the deviations and what you rejected. Return the structured verdict.
