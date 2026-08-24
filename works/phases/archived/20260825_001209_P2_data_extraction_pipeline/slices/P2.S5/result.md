# Result: P2.S5 — deterministic validation gates (layer 2) + per-field reason codes

Status: **done**. `mijual.gates` judges every stored extraction against evidence the model never
saw, writes a named verdict and reason code to the reserved `gate_*` columns, and derives the
**exposure contract** P3 will read. `mijual.calc` holds every number the product will ever display.

Headline: **304 field rows judged — 275 passed, 4 `tbd` (추후결정), 5 failed, 20 not evaluable** —
and the two countdown-critical findings S4 handed over are closed in code:

- **철회 is detected deterministically and the withdrawn events are off the board.** 썸에이지
  `20260805000454` and 제이알글로벌리츠 `20260205000605` are `exposure_state='withdrawn'` and render
  **"이 유상증자는 철회되었습니다"** instead of a cancelled 매매기간. Scanning the whole corpus turned
  up **two more** the slice plan did not know about (디모아, 코퍼스코리아 — both on already-suppressed
  placeholders).
- **`추후결정` is a first-class third state.** 경남제약 + 에이전트AI expose their 매매기간 and 청약
  취급처 as **추후결정**, never as the superseded schedule.

Spend: **0 LLM calls, 0 OpenDART requests, $0.00.** The stored call ledger is untouched at 100
calls / ▷ $1.4136 (S4's), and the docker Postgres corpus was **not reset** — four nullable columns
were added through `ensure_columns` (N27).

## What landed

```
src/mijual/gates/__init__.py     public surface + why layer 2 exists
src/mijual/gates/outcome.py      passed | failed | tbd | not_evaluable, Check, reason codes (+KO)
src/mijual/gates/context.py      the independent witnesses: 본문 labels + the stored API detail row
src/mijual/gates/rules.py        one named gate per §7 row (1–10) + the citation gate
src/mijual/gates/withdrawal.py   the 철회 detector — row shape, never the keyword
src/mijual/gates/exposure.py     the exposure contract (event level + field level)
src/mijual/gates/runner.py       corpus run: drop-and-re-derive, persist, report
src/mijual/gates/__main__.py     run | summary | show | reasons | withdrawals
src/mijual/calc.py               D-day (KST), window state, 배정/초과청약 주수, 소멸가치 (Decimal)
tests/test_gates.py              7 offline cases (no DB, no network, no LLM)
```

Touched elsewhere (additive only): `db/models.py` — `Event.exposure_state` / `.exposure_reason` /
`.exposure_note` / `.exposure_checked_at` + `Event.is_exposable` / `Extraction.is_exposable`, and
the `gate_*` docstrings updated from S4's placeholder (`pass|block`) to the real vocabulary.
`bodydoc`, `collect`, `dart`, `extract` are **read-only** from here: this slice adds a judgement
layer, it does not touch the evidence.

## The verdict vocabulary, and why there are four

| status | meaning | shown? |
|---|---|---|
| `passed` | ≥1 substantive check ran, none failed | **yes** |
| `tbd` | verified citation, null dates, and the document says `추후결정` (N40) | **yes**, as `추후결정` |
| `failed(code)` | a named check failed | **never** — recorded with its reason |
| `not_evaluable(code)` | nothing could be checked (field absent, no reference value) | **never** |

A check whose reference does not exist is **skipped**, not passed, and a gate all of whose checks
were skipped is `not_evaluable` — a gate that compared nothing has not vouched for anything. That
distinction is why the verdict is derived from a `Check` list rather than written by hand, and why
`gate_note` carries the whole list: `citation=ok(verified) date_order=ok(2026-08-19~2026-08-25)
after_record_date=ok(> 2026-07-28) before_subscription=ok(< 2026-09-03)`.

## The gates, and what measuring the corpus changed about them

§7's *gate* column is the spec; three of the ten needed a decision that only the data could settle.

**#1 매매기간** — date order, `start > 배정기준일`, `end < 첫 청약일`. **25/25 pass all three** on the
current versions. Strict inequalities: a 매매기간 that opens on the 배정기준일 fails.

**#2 청약 취급처 — the equality §7 states has no reference for one 대상자 family.** Measured: **55
우리사주조합/구주주 entries match 본문 `11.` exactly** (50 + 5), **0 mismatches** — while **23
일반공모 entries have no `11.` row at all**, because the 실권주 일반공모 청약 is a *later, separate*
window (계양전기: 구주주 09-03~09-04, 일반공모 09-08~09-09). Gating those on equality would have
failed 23 correct fields. They are gated on **ordering** instead — a 일반공모 청약 must start after
the 구주주 청약 closes — and the note records which arm ran for each entry.

**#3 실권주** — §7's enum, applied literally. `기타` is a **failure** (`method_not_enumerated`), not a
shrug: 4 rows on 이렘's two event keys are recorded and blocked.

**#4 초과청약** — `0 < ratio ≤ 1` (27/27). §7 also asks for the *배정주식수 × ratio* arithmetic, but a
filing states only the **ratio** — the multiplication needs a holder's 주수 — so that arithmetic
lives in `mijual.calc.excess_subscription_cap` (unit-tested, P3's calculator) and the gate checks
what a document *can* answer: the normalized ratio must equal the ratio the cited text states
(`배정 신주 1주당 0.2주` / `20%`). 27/27 agree. It catches the real failure mode of a normalized
number — a unit slip (`20` for `0.2`).

**#5 발행가액 산정방법 — a window, not an equality, and the corpus is why.** §7 writes *확정발행가 ≤
MAX(…) vs 본문 6.*; the MAX's operands are 가중산술평균주가, market data this repo does not hold. What
is deterministically checkable is the shape and the schedule: a 확정 산식 must exist, 할인율 must be a
fraction, and the 확정가 공시일 must fall in `[본문 6. 확정예정일, 첫 청약일]`. Over the 27 ① rows:
**16 state the same date in both places, 3 state exactly +1 day, 5 have no label date, 1 no prose
date, 2 neither.** The +1 day is not an error — 본문 `6.` names the day the price is **determined**
(구주주청약 초일 전 제3거래일), the prose the day it is **공시** (계양전기 `…에 공시될 예정이며`).
A naive equality gate would have blocked 3 correct fields; the window passes all 19 that have both.

**#6–8 (②)** — written from §7 (floor == API `act_mktprcfl_cvprc_lwtrsprc`; option dates inside
발행일~만기일; 해제일 ≥ 발행일) and **unexercised**: `P2.S7` owns ②'s corpus. Unit-tested shape only,
stated as unexercised rather than claimed.

**#9 반대의사** — the strictest gate, and it can afford to be: both sides are machine values.
**9/9 current-version rows equal the stored API `mgsc_mgop_rcpd_bgd/_edd` exactly.**

**#10 정정 해석** — the `<CORRECTION>` block is **re-parsed from the snapshot** and the stored record
must hold every changed row the document still yields (a row that stopped parsing is a silent loss
of evidence), plus `deterministic_check.unsupported == 0`. **30/30 pass.** Rows the model did not
mention stay *recorded*, never a failure — that is `P2.S9`'s recall measurement, not a correctness
claim.

**The citation gate runs first on every field.** `span_status='resolved'` is required;
`span_verified` is preferred and recorded (the 2 `trimmed` cases differ from the document only by a
list marker the model re-rendered). **1 row blocked**: LB세미콘 `20260730000278`
`issue_price_formula` → `failed(span_unresolved)`, exactly as N37 required.

### One correction the run itself forced

The first pass reported **3 `dissent_period_mismatch` failures**. All three were **superseded
versions** compared against today's API row — and N2 says a detail endpoint returns *one row per
event, the newest only*, so the stored API payload is a reference value for the **current version
and for no other**. Comparing a superseded 본문 against it measures the correction, not the reading.
The API reference is now version-scoped (`VersionContext.api_value`), those rows read
`not_evaluable(superseded_api_reference)`, and gates 6–9 all inherit the scoping.

## 철회: the detector, measured against the whole corpus

Signal: a `3. 정정사항` row shaped **항목 `유상증자 결정` · 정정 전 `유상증자 결정` · 정정 후 `유상증자
철회`**. A keyword test is measurably wrong — over **1,282 정정사항 rows in 328 distinct 본문
documents**, `철회` appears in the 정정 후 cell of **14 rows and only 4 are withdrawals** (71 % false
positives: ③ 반대의사 boilerplate ×10, a 정정신고서 notice, a 주주명부폐쇄 paragraph). The rules are
shape rules: 정정 후 ≤ 30 squashed chars, the cell **ends** with 철회, the 항목 carries **no form
number**, and the subject either restates 정정 전 or names a filing-level decision. On this corpus
the length bound alone is already exact (4 short cells, 4 withdrawals); the rest is defence in depth.

**Rule 4 was widened because the first draft missed a real one.** 코퍼스코리아 `20260130000680` files
항목 `전 항목` · 정정 전 `-` · 정정 후 `유상증자 발행 결정 철회` — nothing to restate. The audit view
(`python -m mijual.gates withdrawals`) exists so that miss is visible instead of silent.

| withdrawal | event state | effect |
|---|---|---|
| 썸에이지 `20260805000454` | **withdrawn** | was exposable — now off the board |
| 제이알글로벌리츠 `20260205000605` | **withdrawn** | was exposable (`warrant_conflict`) — now off the board |
| 디모아 `20260625000227` | suppressed (`unpaired_correction`) | recorded; no exposure change |
| 코퍼스코리아 `20260130000680` | suppressed (`unpaired_correction`) | recorded; no exposure change |

Nothing is deleted: the flag, the `exposure_note` (rcept_no, 항목, 정정 전 → 정정 후, span) and every
extraction stay. The evidence of what the filing *once* said is what makes the 철회 notice tellable.

**③/② generalise on shape** (`회사합병 결정 → 회사합병 철회` passes unchanged, unit-tested) but there is
**no ③ or ② case in today's corpus** — implemented and untested against real data, stated plainly.

## The exposure contract (the durable P2 → P3 boundary)

One derivation, `mijual.gates.exposure`. **P3 never decides exposure for itself.**

An **event** is exposable iff it is *not suppressed*, *not withdrawn*, and carries *no identity /
rights conflict flag* — `warrant_conflict`, `detail_conflict`, `event_key_collision`,
`hint_split_evidence`. Persisted as `Event.exposure_state` / `.exposure_reason` / `.exposure_note`
(+ `Event.is_exposable`), re-derived every run.

A **field** is exposable iff its gate said `passed` (render the value) or `tbd` (render `추후결정` —
`FieldView.value` is deliberately `None` there, so a superseded date cannot leak through). The two
are independent, and only `EventExposure.renderable_fields` combines them.

**This closes O-8.** Conflicting evidence is *not* a reason to delete an event (S2/S3's rule) and
*not* a reason to publish it — the two halves of the same conservative default. 제이알글로벌리츠's
`warrant_conflict` is moot in practice (it is also 철회, and 철회 outranks it as the more specific
truth), so the policy is asserted by test rather than by the corpus:
`test_the_exposure_contract_blocks_a_flagged_event_and_shows_only_gated_fields`.

### What is exposable today, plainly

```
events      : 44 considered, 35 exposable
  by state  : R1 exposable 25 · flagged 2 · withdrawn 2      (29 ① events)
              R3 exposable 10 · flagged 1 · no 본문 4         (15 ③ events)
  fields exposable on an exposable event:
    warrant_trading_period      25  (추후결정 2 → 23 live 매매기간)
    subscription_agents         25  (추후결정 2)
    excess_subscription         25
    correction_interpretation   26
    forfeited_share_method      24
    issue_price_formula         24
    dissent_notice_procedure     8
  blocked   : detail_conflict 3 · withdrawn 2 · no_document 4
```

**157 field instances are renderable today**, across 35 events; every exposable event has at least
one (① 17 events show all 6 fields, 8 show 5; ③ 5 show 2, 5 show 1). The 3 `detail_conflict` blocks
are 한솔테크닉스, 이렘 and 모다이노칩 — and blocking 이렘's flagged twin has a useful side effect: its
`rcept_no` sits under two event keys (N21's residue) and the board now shows it **once**.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **31 passed** (24 from S1–S4 + 7 new), 0.40 s, no DB / network / LLM |
| `python -m mijual.gates run` ×2 | **byte-identical output** — idempotent, 434 events / 304 rows, ~7 s |
| `python -m mijual.gates summary` | the counts quoted above, regenerated from the DB (N8) |
| `python -m mijual.gates show 20260724000546` | 6/6 passed with the full check trail |
| `python -m mijual.gates show 20260805000454` | `[철회] withdrawn` + `이 유상증자는 철회되었습니다` |
| `python -m mijual.gates show 20260623000409` | 매매기간 + 청약 취급처 `tbd:schedule_tbd`, other 3 passed |
| `python -m mijual.gates withdrawals` | 17 rows named (5 accepted / 12 rejected) → **4 distinct filings**; 썸에이지 counts twice because its `rcept_no` sits under two event keys (N21) |
| `python -m mijual.gates run --rights R3 --only-exposable` | scoped run works (15 events / 27 rows) |
| `python -m mijual.extract summary` | **unchanged**: 304 rows, 100 calls, ▷ $1.4136 — 0 new spend |
| `.venv/bin/python -m mijual.smoke --database-url sqlite:///var/smoke-s5.db` | **OK** (S1 chain green; Postgres corpus untouched) |
| key-leak grep (`src tests docs works scripts var`, both keys) | **0 files** |
| `python3 scripts/workflow.py validate` | **passed** |

Per-field verdicts over all 304 rows (`var/s5-gates.json`, gitignored, regenerated from the final
run): 275 `passed`, 4 `tbd`, 5 `failed`, 20 `not_evaluable`. Reason codes: `field_absent` 11,
`superseded_api_reference` 8, `method_not_enumerated` 4, `schedule_tbd` 4, `span_unresolved` 1,
`api_deadline_absent` 1.

## Deviations from `plan.md`

1. **Gate 5 checks a window, not an equality** (`[본문 6. 확정예정일, 첫 청약일]`). The plan says
   "consistency vs label `6.` values where present". Measured first: 3 of 19 comparable filings
   state the prose date exactly one day after the label, because 본문 `6.` is the *결정일* and the
   prose the *공시일*. Equality would have blocked 3 correct fields.
2. **Gate 2's 일반공모 entries are gated on ordering, not on §7's equality** — 23 of them have no
   `11. 청약예정일` row to compare against, because that window is a different, later one.
3. **§7 #4's *배정주식수 × ratio* arithmetic moved to `mijual.calc`.** A filing states a ratio, not a
   holder's 주수; the gate checks the ratio against the cited text (a real unit-slip check) and the
   multiplication is a unit-tested primitive for P3's calculator.
4. **A reason code the plan did not anticipate: `superseded_api_reference`.** Forced by the first
   run (see above) and grounded in N2.
5. **`event_key_collision` was added to the blocking-flag set**, beside the plan's
   `warrant_conflict` / `detail_conflict` / `hint_split_evidence`. It is an identity flag and the
   plan's own wording is "no unresolved identity … flags"; a no-op today (the same 3 events carry
   both), conservative tomorrow.
6. **The 철회 detector found 4 withdrawals, not the 2 the plan named**, and its subject rule was
   widened mid-slice after 코퍼스코리아's `전 항목` row was missed by the first draft.
7. **`run` judges every event by default** (`--only-exposable` narrows it), so the 철회 detector sees
   suppressed placeholders too. The whole pass costs ~7 s, so scoping it bought nothing but blind
   spots.
8. **`mijual.calc` is a module, not a package** — five functions do not need a directory.
9. **No `defer-job` was filed** for the collector-side items below: workflow state commands are the
   orchestrator's. They are handed forward here and in `phase.md` instead.

## Open items handed forward

- **3 exposable-quality events are blocked on identity, not on their content** — 한솔테크닉스
  (a real 주주배정 유증), 이렘, and 모다이노칩's 로젠 chain. Unblocking them is **collector-side**: split
  the collided event keys using the 본문 `최초제출일` hints S3 already stored (`hint_split_evidence`).
  A good `defer-job` candidate; ~1 event per week of judging-window value.
- **휴온스 `20260804000344`**: the API's 반대의사 접수기간 is `-`, so gate 9 is `not_evaluable`. The
  증권신고서 is the only remaining reference — same collector-side gap as the 4 SPAC ③ events with
  no 본문 at all.
- **아시아나항공 `20260713000482`**: 반대의사 절차 `field_absent` (the filing states the right but not
  the procedure) — a genuine gap, correctly not shown.
- **Gates 6–8 are unexercised.** `P2.S7` runs them the moment ②'s corpus exists; the API field names
  they read (`act_mktprcfl_cvprc_lwtrsprc`, `bd_isu_dt`/`pymd`, `bd_mtd`) should be re-checked
  against a real `cvbdIsDecsn` payload there, since no ② detail row has been gated yet.
- **`mijual.calc` is S8's arithmetic already.** `lapsed_warrant_value(주수, 배정비율, 증서가치)` is the
  shape S8 sums; `d_day` / `window_state` are S6's and P3's. Neither needs re-deriving.
- **`var/mijual-preS3.dump`** (gitignored) is still unused and still deletable.
