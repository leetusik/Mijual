# P4.F1 — result (dispatch 1 of 2: dev is done, the deploy is dispatch 2)

- **status:** `needs_operator`
- **summary:** 샘플 포트폴리오 now picks four **live** issuers — one per R5-4 state — at request time
  from `_board_views` (the `/ask` start-card pattern), with the pinned 2026-08-22 tuple demoted to a
  per-slot fallback and the four example 보유량 (500/300/500/100) untouched; the browser store became
  v2, so the served composition is always shown and `localStorage` keeps only this reader's own
  per-issuer edits (share overrides, explicit removals, 챙긴 돈 claims) with a v1 migration. Verified
  on dev — 166 pytest, frontend typecheck + smoke, a shape check against a scratch API on the dev
  corpus, and a real-Chrome-over-CDP run at 1280 and 390 on both the operator's own dev runtime and
  an isolated copy carrying the new backend.
- **files_changed:**
  - `src/mijual/web/reads.py`
  - `src/mijual/web/portfolio.py`
  - `src/mijual/web/routers/portfolio.py`
  - `src/mijual/agent/tools.py`
  - `tests/test_web_portfolio.py`
  - `frontend/lib/sample.ts`
  - `frontend/components/portfolio/Portfolio.tsx`
  - `works/phases/active/P4/phase.md`
  - `works/phases/active/P4/slices/P4.F1/result.md`
- **validation:**
  - `.venv/bin/python -m pytest -q` → **166 passed**, 1 warning (the standing starlette/httpx
    deprecation). PASS
  - `cd frontend && npm run typecheck` → clean. PASS
  - `cd frontend && npm run smoke` → **22/22**. PASS
  - `python3 scripts/workflow.py validate` → *Workflow validation passed* (one standing advisory:
    `oversized_doc_sections=11`, a docs-phase concern, not this slice's). PASS
  - shape check on the new code against the dev corpus (a scratch API on `:8011` — see *Deviations*):
    four distinct `corp_code`s, ≥ 1 `upcoming` row with `rights_type == "R1"` and `days >= 0`, keys
    exactly `reference` / `holdings` / `upcoming` / `past` / `sample`, **no `claimed` key**. PASS
  - real browser (real Google Chrome 152 over CDP, headful, throwaway profile — see *Instrument*) at
    **1280 and 390**: composition, edit/remove/claim persistence, and the composition-change
    simulation. PASS
- **deviations:** three, all about *where* the verification ran — see *Deviations* below. No
  deviation from what was built.
- **doc_impact:** five lines appended to `phase.md` — `product`, `backend`, `frontend`, `api`, `qa`.
  The sixth the plan lists (`operations`, the deploy) is **owed by dispatch 2**, because the deploy
  has not happened.
- **doc_versions:** n/a
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a
- **operator_need:** **push `main`** (the orchestrator commits first). Then dispatch 2 runs
  `deploy/deploy.sh` on the box. Nothing on the box, no push and no commit happened here.

---

## The fact this fixes, measured rather than argued

`SAMPLE_HOLDINGS` was four issuers pinned on 2026-08-22, one per state R5-4 draws. Served by the
operator's own dev API on 2026-09-02:

```
holdings: 계양전기 500 · 대동기어 300 · 한화솔루션 500 · 세기상사 100
upcoming: [R2 D-52]
past:     [R1 D+8, R1 D+54, R1 D+56, R3 D+58]
```

One upcoming row, **no ① counting down at all**, three of the four rows in 지나간 마감 — nine working
days after the list was pinned, because an ① 매매기간 is about a week long. A judge opening 샘플
포트폴리오 during the 09-07 → 09-11 window would have seen a portfolio of expired rights.

The same corpus through the fixed code:

```
holdings: 아이에이 500 · 제이에스링크 300 · 페니트리움바이오 500 · 휴맥스 100
upcoming: R2 D-1 · R2 D-30 · R1 D-43 (발행가 확정 전, 확정 예정 2026-10-21) · R2 D-322 · R2 D+32(open)
past:     R3 D+6 (통지 마감 지남) · R1 D+37 (소멸, 놓친 돈 79,182원 추정)
```

Four distinct issuers, one per slot, the four example 보유량 unchanged.

## Part 1 — the backend selector

`mijual.web.reads.load_sample_composition(session, *, today) -> list[HoldingEntry]`, fed from
`_board_views(session, today=today)` — the board's own reading, so the sample can only name a company
the board would show. Four slot selectors, each ranked deterministically and each skipping issuers an
earlier slot took:

| slot | predicate | order | 보유량 |
|---|---|---|---|
| ① 발행가 확정 전 | `rights_type == "R1"`, dated, `days >= 0` | 확정 전 first, then `_dday_tier` (the start cards' own comfortable window), then a sole-① issuer, then the latest deadline in the tier, then `rcept_no` | 500 |
| ② 전환청구 개시 | `R2` upcoming, else `countdown.is_open` | soonest ahead; among open ones, most recently opened | 300 |
| ① 소멸 (놓친 돈) | past `R1` **with** a `_lapse_by_event` row whose `lapse_result(...).value` exists | most recent first, over a bounded head of 24 candidates | 500 |
| ③ 통지 마감 지남 | past `R3` | most recent first | 100 |

Three things worth naming because they were decisions, not defaults:

- **The 확정 전 predicate is the presenter's own** — `present.board_offering(...).price_confirmed`,
  which is what the signed 「발행가 확정 전」 chip renders from and what `mailcopy`/`notify` state as
  `price_state`. No second reading of `confirmed_price` was written.
- **Slot ③ demands the money, not just the past tense.** R5-4's third state is the 놓친 돈 lesson, so
  a row that could only say 「기간 지남」 does not fill it; `_lapse_by_event` is reused unchanged, which
  is where the 2026 coverage boundary is applied once for every surface. It needs ORM `Event` rows,
  which `_board_views` does not return, so the slot re-selects them for its **bounded** candidate head
  (`_SAMPLE_LAPSE_CANDIDATES = 24`) rather than for the whole past-① population — a 실적보고서 lands
  weeks after the 매매 마감 it reports, so the most recent past ① usually has none yet.
- **The fallback constant moved modules, and it had to.** `web.portfolio` imports `web.reads`, so the
  selector cannot import the tuple back from `portfolio` without a cycle. `SAMPLE_HOLDINGS` is now
  `reads.SAMPLE_FALLBACK` (with R5's provenance comment intact, as a table), re-exported from
  `web.portfolio.__all__` so the R5-4 record stays reachable where it always was. It does double duty:
  the per-slot fallback issuer **and** the per-slot example share count, which is why it belongs beside
  the selector.

`sample_entries()` became `sample_entries(db, today)`. Two call sites, both updated:
`routers/portfolio.py::sample` (which now computes `today` once and passes it to both calls) and
`mijual.agent.tools`'s anonymous `get_portfolio` branch, where `ctx.session` / `ctx.today` were
already to hand.

A slot with no candidate falls back to its fixed entry; the fallback is dropped **only** if that
issuer is already in the list, which is the one way the endpoint can return fewer than four rows.
Cost is one whole-board read per request (0.08–0.21 s warm, 2.6 s cold on the dev corpus) plus the
bounded 실적보고서 lookup, stated in the docstring, and there is **no cache** — a cached composition is
a fixed list with an expiry date.

**One test**, in the suite's own fixtures, no new scaffolding: a second ① 확정 전 with a comfortable
D-day is added to the mixed corpus and the composition picks **it** over 계양전기's D-3 (live
selection, and the tier preference, in one assertion), the four picks are four distinct issuers with
R5-4's counts, and a bare empty corpus falls back slot by slot to `SAMPLE_FALLBACK`. The anonymity
test was kept untouched and still passes — its fixture corpus has exactly one issuer per state, so it
is now also evidence that the selector picks the right issuer for each slot.

## Part 2 — the browser store

v1 seeded `{v:1, holdings:[{corp_code, shares}], claims}` from the first served payload and every
later visit rendered `payload.holdings.filter(row => localShares.has(row.corp_code))`. With a live
composition that is a second bug on top of the first: a returning browser whose seed names retired
issuers filters today's rows down to **nothing**.

v2 inverts it — the server owns the rows, the browser owns the reader's edits:

```
{ v: 2, shares: { [corp_code]: n }, removed: [corp_code], claims: [rcept_no] }
```

- the **served composition is always shown**; `shown()` is now `!isRemoved(local, corp_code)`;
- an override or removal for an issuer no longer served is **inert and kept, not pruned**. Pruning
  would need the served composition inside the store module — which also runs in 계정 mode, where the
  sample is not served at all — and the composition moves daily: an ① that leaves 다가오는 마감 today
  is in 지나간 마감 tomorrow, and a reader's 삭제 of it should still hold when it comes back. The store
  is bounded by the issuers one reader has actually touched;
- **v1 migrates on read** (`parse()`): `holdings` become share overrides, `claims` carry over,
  `readSample()` returns v2 or `null` and never throws on v1 or garbage. **A v1 removal is forgotten,
  exactly once** — v1 recorded it only as an absence from a seed it never stored, so "the reader
  deleted this row" and "this row was never in that browser's sample" are the same bytes. Documented
  in `lib/sample.ts` and in `phase.md`'s `## Decisions`. Migration is at *read* time, so a migrated
  store stays v1-shaped in `localStorage` until the reader's next edit rewrites it — verified in the
  browser, and harmless because every read migrates;
- the store's **existence** still means 「이 브라우저에 샘플이 로드됨」: a v2 store is written *empty* on
  the first sample render (`ensureSample()`), which is what R5-4's 계정 이전 offer and 샘플 종료 key on.
  That is the part of v1's seed worth keeping; the composition inside it is the part that had to go;
- mutations moved into `lib/sample.ts` (`setSampleShares` / `removeSampleHolding` /
  `restoreSampleHolding` / `setSampleClaim`) instead of four hand-built state objects in the
  component, each reading-or-empty so an edit is never lost to a missing store;
- `SampleBanner` is untouched, `Deadlines`/`Holdings` read the merged view through the same
  `sharesFor` / `shown` callbacks as before, and `claimedOf` reads `local?.claims`;
- **`CarryOver` (계정 이전) now reads the merged view.** In 계정 mode the sample's composition is not
  this page's payload and is no longer in the store, so when — and only when — this browser holds a
  sample, the surface fetches `GET /portfolio/sample` once and merges the browser's overrides and
  removals over it. The offer's *variant* keys on `hasSample` rather than on the fetched rows, so the
  round trip cannot make the 계정 이전 offer flicker as the 세션 이월 one first.

**No Korean string was added or changed anywhere in this slice** — the banner copy, the four states
and the four example counts are exactly what R5-4 signed.

### Two things looked at and deliberately left alone

- **종목 추가 in 샘플 모드 does not exist and this slice did not add it.** `AddHolding` renders in 계정
  mode only, by the ⚠ decision already written into `Portfolio.tsx`: an added issuer would need the
  client to compose that issuer's rows and place them into 다가오는/지나간 itself, a second composition
  site for rules the server owns. So there is no "issuer added in sample mode" rendering path to
  keep working. Pre-existing, correct, and out of scope — recorded, not widened.
- **`useSampleActive()` is still exported and still unused** (R13 Q-D withdrew 샘플 종료 from the
  chrome). Its meaning is unchanged under v2 because the empty-store marker preserves it.

## Verification, and the instrument

**Instrument: real Google Chrome 152 over the DevTools protocol, headful**, launched through
LaunchServices with a throwaway profile (`open -na "Google Chrome" --args --remote-debugging-port=9444
--user-data-dir=<scratchpad>`) and driven from a small `websockets` CDP client, with
`Emulation.setDeviceMetricsOverride` for 390. **Aside was tried first and is unavailable** — `aside
account list` answers *"Aside daemon is not reachable"*, and there is no agent Aside account on this
Mac — which is exactly what `## Operator Runtime` already records as the P11 fallback. The operator's
own Chrome profile was never touched. Chrome was closed afterwards.

What was actually driven, all at **1280 and 390**:

1. **The composition** — four holdings (아이에이 500 · 제이에스링크 300 · 페니트리움바이오 500 · 휴맥스
   100); 다가오는 마감 carrying the ① **D-43** row with 「발행가 확정 전 · 확정 예정 2026-10-21」 and the
   ② **D-1** row; 지나간 마감 carrying the ③ 「통지 마감 지남 · D+6」 and the ① 소멸 row with 「놓친 돈
   500주 기준 79,182원 추정」 and the 챙겼습니다 control. Banner verbatim. No horizontal overflow at 390.
2. **수정 → reload** — clicked 수정 on 아이에이, typed 1234, clicked 저장: the store became
   `{"v":2,"shares":{"00252269":1234},"removed":[],"claims":[]}`, the row reads 1,234주 and the
   browser-side 배정 신주 recomputed 253주 → **626주** from the served factors. Survived a reload.
3. **삭제 → reload** — clicked 삭제 on 휴맥스: `removed:["00787057"]`; after a reload the issuer is
   absent from the holdings **and** from its 지나간 마감 row, and the page is not empty.
4. **A composition change, simulated two ways.** (a) a **v1** store naming the four retired pinned
   issuers plus one override for an issuer that *is* served: after a reload all four live issuers
   render, the applicable override is kept (제이에스링크 **4,321주**), and no empty state appears —
   the v1 code would have rendered nothing at all here. (b) a **v2** store with a removal and an
   override for issuers the server does not serve: they are inert and kept, and the override that
   does apply (아이에이 55주) renders.
5. **챙긴 돈** — ticked the 청약·매도로 챙겼습니다 checkbox: `claims:["20260813001401"]`, and after a
   reload the control comes back **checked**.
6. **On the operator's own running dev runtime** (`http://127.0.0.1:3010`, their `next dev` picking up
   the change through Fast Refresh, their day-old API still serving the pinned composition): the
   surface renders all four served rows at 1280 and 390, writes the v2 store, and — with a v1 store
   naming issuers *that* server does not serve — still renders the served four rather than an empty
   sample. That is the regression fixed, seen in the operator's own runtime.

**Production build not required.** This change is a server-side selection plus a `localStorage`
module; there is no build-time input, no `NEXT_PUBLIC_*` value and no hydration-shaped surface change
(the store is read through the existing `useSyncExternalStore` with the same server snapshot `null`).
The production check that matters is the deployed site, and that is dispatch 2's.

## Deviations

All three are about *where* verification ran. Nothing about what was built departs from `plan.md`.

1. **The shape check ran against a scratch API on `127.0.0.1:8011`, not the operator's `:8010`.** The
   operator's dev API is a plain `uvicorn.run(...)` with **no `--reload`**, started
   **2026-09-01 03:14** — a day older than `src/`'s last commit — so it cannot serve this change, and
   the dispatch forbids restarting the operator's stack. A second API process was started on 8011
   against the same dev database (read-only traffic: `GET /health`, `GET /portfolio/sample`), used,
   and stopped. The operator's 8010 was never signalled and still answers 200.
2. **The combined browser check ran against an isolated `next dev` on `127.0.0.1:3011`** pointed at
   8011, from a copy of `frontend/` in the scratchpad (source `rsync`'d, `node_modules` APFS-cloned,
   its own `.next`). Reason: the Next dev server resolves `MIJUAL_API_ORIGIN` at startup, so the
   operator's 3010 can only talk to their stale 8010. Same code, same Next 16.3.2 dev mode, same
   `127.0.0.1` access path — a faithful stand-in, and the store half of the verification was **also** run
   on the operator's real 3010 (item 6 above). Both scratch processes were stopped; `frontend/.next`
   was never deleted or rebuilt by hand (the operator's dev server recompiled through Fast Refresh,
   which is what the plan expects of a frontend edit).
3. **The `operations` "Doc impact" line is owed by dispatch 2**, since it is about a deploy that has
   not happened. Five of the plan's six lines are in `phase.md` now.

## Not exercised, and honest about it

- **The 계정 이전 (`CarryOver` migrate) offer was not clicked in a browser.** It needs a logged-in
  account, and the only accounts on the dev database are the operator's own — signing a new one up
  would write a row into their dev Postgres for a check the plan does not ask for. The path is
  typechecked, its merge is pure, and the effect only fires in 계정 mode when a sample store exists
  (so a reader with no sample sees byte-identical behaviour to before). Flagged in `phase.md`'s note
  to `P4.REVIEW` as one click for the gate.
- **Nothing on the box changed.** No `deploy.sh`, no `ssh`, no push, no commit.

## Notebook

`phase.md` carries the durable half and is not restated here: three `## Decisions` (the supersession
of R5-4 「고정」 with the P11 precedent and the measurement; the store-v2 semantics and what a v1
removal loses; the per-request cost and why there is no cache), five `## Doc impact` lines, one new
`## Operator Questions` entry (첨부2 §5 must describe the sample **by state, not by 종목**, or it goes
stale the way the pinned list did), and notes **(from P4.F1, for P4.S8)** and **(from P4.F1, for
P4.REVIEW)**. `## Now` was rewritten last and carries the one ask.
