# Result: P2.F1 — full-2026 discovery re-run + reconcile

_Executed 2026-08-20 by `slice-executor-high`. **No package code was changed** — the slice ran
the existing machinery (`mijual.collect`, `mijual.bodydoc`, `mijual.extract`, `mijual.gates`,
`mijual.estimate`) and reconciled what it found. `git diff --stat src/ tests/` is empty._

## Verdict against the plan's four checks

| plan check | outcome |
|---|---|
| the 3 named originals present, gated, correctly classified | **yes** — all three `warrant_confirmed` + `exposable`, **5/5 fields `passed`** with verified citations |
| `pifricDecsn` 2026 events on the board | **yes** — 7 → **9** events, all `warrant_confirmed`/`exposable`; the 2 new ones (퓨쳐켐, 엘앤씨바이오) both have a 청약 **ahead** |
| spend inside budget, reported | **585 / 700** OpenDART requests, **11 / 30** LLM calls (all `thinking_level=LOW`), ▷ $0.0898 |
| an immediate second run adds 0 events / 0 versions | **yes** — 1 request, 0 rows, gate summary byte-identical |

## Spend

**OpenDART: 585 live requests of the 700 ceiling** (▷ ~3 % of the 20,000/day quota, O-1).

| step | command | requests |
|---|---|---|
| ① sweep | `collect --endpoints piicDecsn pifricDecsn` | 400 (ceiling hit) |
| ③ sweep | `collect --endpoints cmpMgDecsn` | 100 |
| ① 증서 verdict | `bodydoc warrants` | 10 |
| 정정 backfill (offline, N34) | `bodydoc --offline backfill` | 0 |
| resume ①/③ 본문 | `collect --endpoints piicDecsn pifricDecsn cmpMgDecsn` | 74 |
| warrants + backfill again | — | 0 |
| `gates run`, `estimate report` ×2 | — | 0 |
| idempotence pass (all stages) | — | 1 |

**LLM: 11 calls, 0 failures, 85,769 tokens (77,285 prompt + 8,484 output + **0 thinking**),
▷ $0.0898** at the N35 rate card. 5 `r1_prose` + 6 `r3_prose`, every call stored with
`extraction_call.thinking_level='LOW'` (N65). The **§7 #10 정정 재추출 pass was deliberately not
run** — see *Deviations*.

## What the sweep actually found

Discovery over **2026-01-01 ~ 2026-08-20, KOSPI+KOSDAQ, `pblntf_ty=B`**: 4,634 list rows in 3
chunks (50 pages; KOSDAQ needs 14/15/8 pages per chunk — N23's truncation is now paid off for
2026), yielding 1,145 `piicDecsn` + 25 `pifricDecsn` + 286 `cmpMgDecsn` + 823 `cvbdIsDecsn`
target rows.

**The run gap, measured per endpoint** (each discovered `rcept_no` checked against the stored
`filing_version` table; the "before" column is `observed_at` older than this slice's start) —
this is the number N78(a) asked for:

| endpoint | discovered | **not stored before** this slice | not stored **after** |
|---|---|---|---|
| `piicDecsn` ① | 1,145 | **192** | 0 |
| `pifricDecsn` ① | 25 | **4** | 0 |
| `cmpMgDecsn` ③ | 286 | **48** (17 of them originals) | 0 |
| `cvbdIsDecsn` ② | 823 | **0** | 0 |

**244 filings of 2,279 (10.7 %) that 2026 discovery returns had never been stored.** The ③ figure
was also measured *ahead* of the ③ run by the same method and came out at 48 — the two agree, so
the method is sound. N73(c)'s "at least 3" was a floor by two orders of magnitude.

Database: events **1,204 → 1,345** (+141), versions **3,396 → 3,990** (+594), snapshots
**5,987 → 7,076** (+1,089), corps 595 → 614. 88 placeholder events retired
`superseded_by_pairing` by the existing `retire_superseded_unpaired` path (N74's healing).

### Board delta (`python -m mijual.gates summary`)

| | before | after |
|---|---|---|
| exposable events | **479** | **488** |
| — ① `piicDecsn`+`pifricDecsn` | 47 | **50** |
| — ③ `cmpMgDecsn` | 10 | **16** |
| — ② `cvbdIsDecsn` | 422 | 422 (untouched) |
| renderable field instances | **388** | **409** |
| ③ blocked `no_document` | 9 | **1** (프리시젼바이오 `20260225004946`) |
| ① `withdrawn` | 2 | **3** |
| `detail_conflict` blocked | 3 | 3 |

Per field: `dissent_notice_procedure` 8 → **14**, `excess_subscription` 47 → **50**,
`forfeited_share_method` 46 → **49**, `issue_price_formula` 44 → **47**, `subscription_agents`
47 → **50** (추후결정 2), `warrant_trading_period` 47 → **50** (추후결정 2). ②'s four fields and
`correction_interpretation` (41) are unchanged.

### The three N73(c) originals

All three were **already in the corpus** — `P2.S8`'s targeted per-corp adoption (N74) had healed
them before this slice started. What this slice added is that they are now reached by **ordinary
market-wide discovery**, so the next scheduled run keeps them:

| original | corp | event | current version | verdict |
|---|---|---|---|---|
| `20260109000634` | 레이저옵텍 | `piicDecsn/2026-01-09`, 4 versions | `20260416000230` | exposable, `warrant_confirmed`, 5/5 `passed` |
| `20260408002647` | RF머트리얼즈 | `piicDecsn/2026-04-08`, 5 versions | `20260616000050` | exposable, `warrant_confirmed`, 5/5 `passed` |
| `20260409002139` | 피엠티 | `piicDecsn/2026-04-09`, 3 versions | `20260617000192` | exposable, `warrant_confirmed`, 5/5 `passed` |

Their 청약 has closed, so they are corpus/estimate rows rather than live countdowns.

### The correctness save: 디모아

The sweep collected 디모아's **real** ① original `20260424000529` (2026-04-24), which no earlier
run held — until now its 정정 chain existed only as an `unpaired_correction` placeholder, which is
why N47 recorded its 철회 as changing no exposure. Once the real event existed it was a
`warrant_confirmed` 주주배정 유상증자 and would have been **published as a live right**; the
unchanged N47 row-shape detector read `20260625000227` and blocked it. **Publishing 디모아 today
would have advertised a withdrawn 유상증자** — the same failure mode N39 first named for 썸에이지.

Withdrawal totals are otherwise unchanged: **15 distinct withdrawn filings (① 6, ② 9)**, exactly
N55's 6 and N60's 9 — the sweep found no new withdrawn *filing*, it moved one onto a real event.
Measured at **1,792 / 2,720 기재정정 versions carrying a 본문** (N55's coverage rule). 추후결정 is
unchanged at 2 fields on 2 events.

### `pifricDecsn` (N71)

9 events, all `exposable` + `warrant_confirmed`. The 7 S8 adopted were all *lapsed* offerings; the
2 the sweep added are **live**: 퓨쳐켐 (`pifricDecsn/2026-05-29`, 청약 2026-09-04 — tied for
soonest on the board) and 엘앤씨바이오 (`pifricDecsn/2026-07-31`, 청약 2026-10-15). This is
N78(b)'s under-count showing up on the *live* board, not just in the retrospective number.

## Estimate: headline stable, pipeline longer

`python -m mijual.estimate report --today 20260820 --korean`, run twice, **byte-identical**
(0 requests, 0 calls):

- **▷ 718.1억원 (71,812,971,649원) unchanged**; band ▷ 548.7억~718.1억 unchanged; 32 offerings
  (29 valued, 3 counted only) unchanged; 51,253,956 / 365,527,824 증서 = 14.02 % unchanged.
- **Changed: "still open" 18 → 23, and 청약 ahead 11 → 15.** New: 퓨쳐켐, 엘앤씨바이오,
  케이이엠텍, 한울반도체, 코이즈/센서뷰/클로봇 (청약 종료, 실적보고서 미제출), 디모아 (철회).
  Soonest 청약 is still 2026-09-04, now 계양전기 · SG · **퓨쳐켐**.

The headline being unchanged is the expected result and is the honest one: the lapse number is
framed on the 증권발행실적보고서 (N72) and S8 had already adopted every offering that produced one.
What moved is the **live** side of the same pipeline.

## Idempotence

Immediately after the reconciliation, the same four stages again:

    collect (①+③)  → db (1345, 3990, 7076) -> (1345, 3990, 7076), documents fetched 0, 1 request
    bodydoc warrants → 75 events, confirmed=54 conflict=1 denied=20, 0 requests
    extract R1 / R3  → 54 / 17 versions already extracted, 0 calls, 0 tokens
    gates run        → summary byte-identical (`diff` clean), row counts identical

The **1 request** is explainable and by design: one 본문 comes back as a non-ZIP error body, which
N18 deliberately never caches, so it is retried once per run and never poisons a fixture. Nothing
else spent anything.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m mijual.collect --bgn 20260101 --end 20260820 --endpoints piicDecsn pifricDecsn --history-bgn 20220601 --max-requests 400 --max-documents 150` | ran, `BUDGET EXHAUSTED` at the ceiling (by design), +117 events |
| `.venv/bin/python -m mijual.collect … --endpoints cmpMgDecsn --max-requests 105 --max-documents 60` | pass, 100 requests, +24 events |
| `.venv/bin/python -m mijual.bodydoc --max-requests 170 warrants` | pass, 75 ① events, confirmed 54 / conflict 1 / denied 20 |
| `.venv/bin/python -m mijual.bodydoc --offline backfill` | pass, 0 requests, 1,792 정정 parsed, 1,767 hints |
| `.venv/bin/python -m mijual.collect … --endpoints piicDecsn pifricDecsn cmpMgDecsn --max-requests 90` | pass, 74 requests, +73 본문, 0 new events |
| `.venv/bin/python -m mijual.extract --max-calls 15 run --rights R1` | pass, 5 calls, 0 failures, 0 thinking tokens |
| `.venv/bin/python -m mijual.extract --max-calls 15 run --rights R3` | pass, 6 calls, 0 failures, 0 thinking tokens |
| `.venv/bin/python -m mijual.gates run` | pass, 488 exposable events / 409 renderable fields |
| idempotence: collect + warrants + extract ×2 + gates | pass — 0 rows added, 0 calls, gate summary byte-identical |
| `.venv/bin/python -m mijual.estimate report --today 20260820 --korean` ×2 | pass, byte-identical |
| `.venv/bin/python -m pytest -q` | **51 passed** in 0.89s |
| `python3 scripts/workflow.py validate` | **Workflow validation passed** |

Secrets: no key value was echoed, logged, or written anywhere; `Settings` prints
`dart_api_key=<set>`, and all cache filenames/`_url` fields are key-free by construction (N18).

## Deviations from `plan.md`

1. **② `cvbdIsDecsn` was not re-collected, on measured evidence.** The plan lists ② among the
   endpoints to sweep. A 0-request check showed **0 of the 823 discovered 2026 ② filings are
   unstored** — `P2.S7` backfilled 2025-06-01 → 2026-08-20, which strictly contains this window,
   so the ② run gap is provably empty. A re-run would have cost a *measured* **266 live detail
   requests + up to 69 corp-history queries** (predicted from `DartClient.cache_path` hits) to
   re-fetch rows identical to the ones held, blowing the 700 ceiling for zero new information.
   ② is untouched and its board figures are unchanged (422 exposable).

2. **The sweep ran as three endpoint-scoped `collect` invocations, not one.** Discovery pages are
   cached by window+market and are endpoint-independent, so splitting cost nothing extra and let
   the budget be spent in D-1's drop order (① first, ③ next). The plan allowed the `scheduler
   once` path "if convenient"; it was not, because `stage_bodydoc` drains the 정정 queue before
   the ① warrant check and would have spent the remaining budget on ② 정정 narrative that N58
   says ② does not need.

3. **`--history-bgn 20220601` instead of the default (3 years back = 2023-01-01).** Chosen to
   reuse the 440 already-cached corp-history responses (their key is
   `bgn_de=20220601&end_de=20260820`), which saved ~100 live requests. It reached 7 months
   further back than the default and **had one measurable side effect** — see N81 below: it minted
   a second, 2022-keyed 코이즈 event that now duplicates one exposable row. Recorded, not
   papered over.

4. **The §7 #10 정정 재추출 pass was not run.** A dry run priced it at **69 calls** (59 ① + 10 ③)
   at the *project preset* thinking level, because `THINKING_BY_TASK['correction'] =
   INHERIT_PRESET` (N65). That breaks both binding ceilings — ≤ 30 calls **and** LOW thinking — so
   it was left undone rather than partially run. `correction_interpretation` therefore stays at
   **41** renderable instances while the ① corpus grew. Quantified and handed forward as N82.

5. **No new withdrawals or 추후결정 beyond the 디모아 re-attachment**, so nothing in that part of
   the plan's step 3 needed reporting beyond what is above.

## Doc impact appended to `phase.md`

One entry, `data` / `product` / `operations` — the corpus is now a swept 2026 census for ①/③,
the board figures move (479 → 488 exposable, 388 → 409 renderable fields, ① 47 → 50, ③ 10 → 16),
`pifricDecsn` is confirmed live on the board, and the estimate headline is unchanged while the
open pipeline grows 18 → 23 offerings (11 → 15 with a 청약 ahead).

## Findings appended to `phase.md`

N80 (the run gap, measured per endpoint, and why ② had none), N81 (the pairing-history reach is a
board-quality knob — the 코이즈 duplicate), N82 (the 정정 재추출 pass is now 69 calls at preset
thinking, and what that costs), N83 (디모아 — the sweep's correctness save).
