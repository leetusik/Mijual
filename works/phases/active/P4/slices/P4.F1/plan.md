# P4.F1 — Sample portfolio picks live issuers per state at request time; fixed list as fallback

Orchestrator plan, written 2026-09-02 after `P4.S6` landed (`cfd7f8b`). Kind `fix`, risk `high`,
cut on the operator's instruction the same day: **「just like prepared questions, the sample
portfolio should also all outdated situation isn't it?」** — answer: yes, and they chose the fix.

Read first: `works/phases/active/P4/phase.md` whole (`## Now`, the R2 baseline, the deploy
freeze), `src/mijual/web/portfolio.py` (`SAMPLE_HOLDINGS`, `sample_entries`), `src/mijual/web/routers/portfolio.py`
(the `/portfolio/sample` route), `src/mijual/web/reads.py` — `_board_views` (~246),
`load_portfolio` (~1339, its upcoming / open ② / tbd / past classification at ~1399–1430),
`_lapse_by_event`, `HoldingEntry` (~1234), and the start-card selectors `_search_card` /
`_calculate_card` / `load_start_cards` (~1509–1646) — the pattern this fix mirrors;
`frontend/lib/sample.ts` (the localStorage store) and `frontend/components/portfolio/Portfolio.tsx`
(lines ~60–135: the seed-on-first-visit and the `shown()` filter; the mutations at ~175/212/229);
`frontend/components/portfolio/copy.ts` (`SAMPLE_BANNER_KO`); the signed records
`docs/reference/design/rounds/05-account/output/build-prompt.md` §샘플 포트폴리오 (R5-4) and
`docs/reference/design/rounds/13-portfolio/output/result.md` (Q-D, Q-E) — read-only;
`tests/test_web_portfolio.py`; `src/mijual/mailcopy.py` for how the 발행가 「확정 전」 state is
decided (reuse that predicate, do not invent another).

## The fact this fixes

`SAMPLE_HOLDINGS` is four **fixed** issuers pinned on 2026-08-22, one per state R5-4 wanted the
surface to show: 계양전기 500주 (① 발행가 확정 전, live countdown), 대동기어 300주 (② 전환청구
개시), 한화솔루션 500주 (① 소멸 — 놓친 돈), 세기상사 100주 (③ 통지 마감 지남). Measured live on
2026-09-02: `upcoming` = 1 (대동기어 ② D-52), `past` = 4 — 계양전기's ① closed on 08-25. During the
judging window (09-07 → 09-11) a judge opening 샘플 포트폴리오 sees no ① counting down at all. Any
fixed list rots the same way within weeks, because ① windows are about a week long.

The `/ask` start cards had the identical problem and the operator rejected fixed ones at the P11
gate (「real time catch. not fixed.」) — `load_start_cards` resolves the companies per request from
`_board_views`. This fix does the same for the sample, keeping the **four states** and the **four
example share counts** exactly, and keeping the banner 「종목·공시·마감은 실제, 계정·보유량은 예시입니다」
true. R5-4's 「구성 (고정)」 clause is **superseded by the operator's 2026-09-02 instruction**; record
that as a `## Decision` (with the P11 precedent) — it is not a silent design change.

## Part 1 — the backend selector (`src/mijual/web/reads.py` + `portfolio.py`)

`load_sample_composition(session, *, today) -> list[HoldingEntry]` (name it in the reads module's
style), fed from `_board_views(session, today=today)` (exposable views + ① offering inputs), the
same source the board and the start cards read, so the sample can only name what the board would
show. Four slots, **distinct issuers**, deterministic tie-breaks (D-day tier as `_dday_tier`, then
`rcept_no` / `corp_code`), each slot falling back to the corresponding entry of the old tuple
(rename it `SAMPLE_FALLBACK`, keep the comment's provenance) when the corpus has no candidate:

1. **① upcoming, 발행가 확정 전** — `rights_type == "R1"`, `countdown.days >= 0`, the offering's
   price not yet fixed (the predicate `mailcopy`/`notify` already use for 「확정 전 (확정 예정일 …)」);
   prefer the comfortable D-day tier over D-0/D-1, then a single-① issuer, then the latest
   deadline inside the tier. If no 확정 전 candidate exists, any upcoming ①. Example shares **500**.
2. **② 전환청구 개시** — `rights_type == "R2"`; prefer upcoming (`days >= 0`, soonest), else open
   (`countdown.is_open`, most recently opened). **300**.
3. **① closed with a 소멸 outcome** — a past ① whose `_lapse_by_event` row is inside coverage and
   carries the 놓친 돈 figure (so the row states money, not 「기간 지남」 only), most recent first.
   **500**.
4. **③ 통지 마감 지남** — `rights_type == "R3"`, past, most recent. **100**.

Slots 1–2 are what makes the sample alive in the window; 3–4 are the 놓친 돈 lesson. An issuer may
qualify for two slots; it takes the first and the next slot skips it. `sample_entries()` becomes
`sample_entries(db, today)` and the route passes `db` + `clock.now().date()`. **Cost:** one
whole-board read per `/portfolio/sample` request — the same the board and `/ask/start-cards` pay
today; say so in the docstring and do not add a cache.

**One small test** in `tests/test_web_portfolio.py` (the suite's own fixtures): the composition
returns four distinct issuers, one per slot, and a corpus missing a slot's state falls back to that
slot's fixed entry. Keep the anonymity test. No fixture sprawl.

## Part 2 — the browser store (`frontend/lib/sample.ts`, `Portfolio.tsx`)

Today the first sample visit **seeds** `localStorage["mijual.portfolio.sample"]` `{v:1, holdings:
[{corp_code, shares}], claims}` from the served holdings, and every later visit **filters the served
rows by the stored corp codes** (`shown()`). With a live composition that is a bug on its own: a
returning browser whose seed holds retired issuers renders an **empty** sample. So:

- **The served composition is always shown.** The browser keeps only per-reader edits keyed by
  `corp_code`: share overrides, **explicit** removals, claims. An issuer the browser has never
  seen renders; a removed issuer stays hidden while it is served; an override or removal for an
  issuer no longer served is inert (prune or keep — say which, and why).
- Store **v2**, e.g. `{v: 2, shares: {[corp_code]: n}, removed: [corp_code], claims: [...]}`, with
  a **migration from v1**: v1's `holdings` become share overrides; v1 recorded removals only as
  absence from a seed it never stored, so a v1 removal is forgotten once — document it in the
  module and in `result.md`. `readSample()` returns v2 or `null`; never throws on v1/garbage.
- R13 Q-D (「영구 브라우저 편집을 수용한다」) stays true for edits that still apply; edits against
  issuers that have left the composition become inert. Record as a `## Decision` for the gate.
- Look at how the mutations (~175/212/229) and `AddHolding` render an issuer **added** in sample
  mode that the served payload does not carry (re-read? resolved via `/stocks/{code}`? not shown?)
  — keep whatever works today, **do not widen scope**; if it is a pre-existing limitation, say so
  in `result.md` and leave it.
- `SampleBanner`, `CarryOver` (the sample → account migration offer) and the 챙긴 돈 claims must
  read the **merged** view. Banner copy unchanged. No new Korean strings (if one is unavoidable,
  it goes on `## Operator Questions` for the gate).

## Verification

- `.venv/bin/python -m pytest -q` (the new test + the suite), `cd frontend && npm run typecheck &&
  npm run smoke`.
- **Real browser on the operator's running dev runtime** (`http://127.0.0.1:3010`, Fast Refresh;
  do not restart it; `frontend/.next` is theirs) — real Chrome over CDP, headful via `open -na`
  (a `nohup` launch is headless; ports 9223/9333 may hold stale sessions — use another), 1280 and
  390: `/portfolio?sample=1` shows four holdings, one per state, 다가오는 마감 carries a ① D-day
  row and the ② row, 지나간 마감 the 소멸 and ③ rows; edit a share count → reload → persists; remove
  one → reload → still hidden; then **simulate a composition change** (pre-write a v1 store with
  retired corp codes, or a v2 store with a removal + an override for an issuer not served) →
  reload → the live issuers render, the applicable override is kept, nothing is empty. Name the
  instrument in `result.md`; never claim a run you did not make.
- `curl -s http://127.0.0.1:8010/portfolio/sample | python3 -c …` — four distinct `corp_code`s;
  ≥ 1 `upcoming` row with `rights_type == "R1"` and `days >= 0`; the response shape unchanged
  (`reference`, `holdings`, `upcoming`, `past`, `sample: true`; no `claimed` key).
- Production build not required for this change (server + store); say so.

## STOP POINT — then the deploy (this slice's own)

Return **`needs_operator`** once Parts 1–2 are verified on dev: the one ask is **push `main`**
(the orchestrator commits first). On resume (dispatch 2): `deploy/deploy.sh` on the box detached +
polled (default `REF=origin/main`; `:previous` first; expect **both** `mijual-api` and
`mijual-web` rebuilt this time, since `src/` changed), the four no-harm assertions against the R2
baseline in `## Now`, `make smoke-prod` 17/17, and
`curl -s https://jujutower.com/api/portfolio/sample` showing four distinct issuers with ≥ 1
upcoming ① — plus one look at `https://jujutower.com/portfolio?sample=1` in the real browser at
390. **The deploy freeze opens 2026-09-07 11:00 KST**; this must land before it. Then `done`.

## Notebook and docs

`## Decisions`: the supersession of R5-4 「고정」 (operator, 2026-09-02, P11 precedent); the store-v2
semantics and what v1 removals lose; the per-request cost. `## Doc impact`: `product` (샘플
포트폴리오 = four live issuers per state, example shares fixed; supersedes R5-4 「고정」), `backend`
(the selector, its source and cost), `frontend` (store v2 + migration; the served composition is
always shown), `api` (payload shape unchanged; the issuers vary by day), `qa` (regression line: the
sample shows an upcoming ① and four distinct issuers; `make smoke-prod` unchanged), `operations`
(the deploy, when it happens). Notes **(from P4.F1, for P4.S8)**: how 첨부2 §5 describes the sample
(「오늘의 실제 공시에서 상태별로 고른 4종목, 보유량은 예시」) and that judges see live rows;
**(from P4.F1, for P4.REVIEW)**: the gate items (accept the supersession; the store semantics;
what to click). Rewrite `## Now` (≤ 15 lines) last; never touch the generated `## Slices` block.
Return the verdict block: `status`, `summary`, `files_changed`, `validation`, `deviations`,
`doc_impact`, `doc_versions: n/a`, `review_verdict: n/a`, `walkthrough: none`, `explain: n/a`,
`operator_need`.
