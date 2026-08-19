# Result: P2.S7 — ② CB collection + backfill to ≥ 2025-06

_Executed 2026-08-20. Zero commits, zero state transitions, zero `doc-new-version`._

## What the slice was for, and whether it worked

D-1 funded this slice on one condition: **backfill to ≥ 2025-06**, because 0 of the 267
cached 2026-filed CB events opened 전환청구 before 2027-01-15 — ② had density but no urgency.
The condition is met and the number that proves it is this:

> **33 ② events open 전환청구 within 30 days of the judging week (2026-09-07), 82 within 90,
> 152 within 180 — and 197 of the 422 exposable events are the 2025-H2 vintage that supplies
> them.** Before the backfill the 30-day count was **1**.

The board went from **35 exposable events / 157 renderable fields** to **457 / 280**.

## Spend against the ceilings

| | ceiling | spent |
|---|---|---|
| OpenDART requests | ≤ 2,500 (`max_requests`) | **1,398** (56 %) |
| LLM calls | ≈ 80 | **80** extraction + **3** operator-directed probes = 83 |
| LLM tokens | — | 797,099 (extraction) + ~38,300 (probes) |
| ▷ estimated cost | — | **▷ $1.068** + ▷ $0.040 = **▷ $1.108** |

Request breakdown: 584 live collection (discovery 175 pages + 410 detail + history) · 700
정정 본문 · 90 urgency 본문 · 13 blocked-event 본문 · 11 targeted probes · **0** for every
offline pass, gate run and calendar. Quota is 20,000/day (O-1, closed), so the ceiling was a
guard, never a constraint — nothing was skipped for budget.

## Deliverables

### 1. ② target in the collector

`cvbdIsDecsn` → `전환사채권발행결정` → `RightsType.CONVERTIBLE_OVERHANG`, riding the existing
discover → pair → detail → snapshot path unchanged (정정 pairing included: 1,181 기재정정
versions collected against 530 originals). The subtype match is **exact string equality on the
`report_nm` parenthetical**, which is load-bearing: the same `pblntf_ty=B` stream carries
자기전환사채매도결정, 자기전환사채만기전취득결정, 전환사채매수선택권행사자지정,
제3자의전환사채매수선택권행사, 신주인수권부사채권발행결정 and 교환사채권발행결정 (EB, out by
D-1) — a substring match on `전환사채` would have collected all of them. Asserted by test.

**②'s exposure semantics** (`gates/exposure.py`, R2 arm): ② is the one rights type whose
countdown is **not** a 본문 reading, so requiring a stored 본문 would block a perfectly
renderable event. The arm keeps suppression, 철회 and the blocking flags unchanged and replaces
the document requirement with an **API-completeness** requirement — 전환가액 · 전환청구기간
개시·종료 · 오버행 수량 · 오버행 비율 all present and parseable on the current version's detail
row (`R2_REQUIRED_API_FIELDS`). Two new event states, both conservative: `no_detail` (no stored
detail row) and `incomplete_api_row` (a row exists but is blank or partial).

**해외/USD rule, decided and recorded:** *exposable iff the KRW conversion fields parse*, never
on the strength of `ovis_*`. Measured — the corpus holds exactly **one** 해외 case (헝셩그룹
`20260213002703`, 16,000,000 **HKD**) and it states 전환가액 174원 / 17,110,804주 in KRW and
shares like any domestic issue, so it passes on its own merits. `ovis_fta_crn` is parsed and
carried as `ConvertibleFacts.overseas_currency` for display, not as a filter.

### 2. 철회 for ②

The detector's four shape rules (N47) generalised to ② **with no change at all**. Measured over
the collected ② corpus: **808 documents, 4,627 정정사항 rows, 10 rows whose 정정 후 contains
`철회`, 9 accepted — precision 9/9**, against the keyword test's 71 % false-positive rate on
①/③ (a CB's 정정 후 cells carry none of the 매수청구 boilerplate).

**8 ② events / 9 filings withdrawn:** 드래곤플라이 `20250915000168`, 캔버스엔 `20250806000321`,
아이톡시 `20251231000642`, 베노티앤알 `20260211001003`, 코퍼스코리아 `20260130000634` + `…642`
(one event, two filings), 센서뷰 `20260227007913`, 핀텔 `20260417000537`, 대진첨단소재
`20260714000506`. Two corps (베노티앤알, 코퍼스코리아) withdrew a 유상증자 **and** a CB on the
same day.

The finding that matters is *why* it matters: **when a CB is withdrawn, OpenDART keeps the
detail row and blanks all 46 fields to `-`.** So the API-completeness rule already refuses to
render these — but it refuses saying *"we do not have the numbers"* about an event whose truth
is *"this was cancelled"*. The detector converts a silence into `이 사채 발행은 철회되었습니다`
with a 정정사항 row and a span behind it. N55's rule held again: 대진첨단소재 was found only
after one more 본문 was fetched, which is why `python -m mijual.cb documents --blocked` exists.

**One known false negative, left uncaught deliberately:** 비트플래닛 `20260616000274` withdraws
its CB in a 143-character *paragraph* under `23. 기타 투자판단에 참고할 사항`
(`발행대상자 … 의 투자 진행 철회 통보에 따라 부득이하게 철회하게 됨`), failing three of the four
rules. Relaxing any of them re-admits the ①/③ boilerplate the rules exist to reject, and the
second line of defence holds: its API row is blank in all 46 fields, so the event is blocked
`incomplete_api_row` anyway. Recorded, not rendered — but with a weaker reason than the truth.

### 3–4. 2026 YTD collection and the backfill

Offline-first, then one live combined window rather than two:

```
# 1. offline over the P1 cache — 0 requests, 282 ② events
python -m mijual.collect --bgn 20260101 --end 20260818 --endpoints cvbdIsDecsn \
    --offline --cache-dir scripts/spike/samples --detail-window 20260101 20260818 --no-documents
# 2. live, 2025-06-01 → today in one window — 584 requests
python -m mijual.collect --bgn 20250601 --end 20260820 --endpoints cvbdIsDecsn \
    --detail-window 20250501 20260820 --no-documents --max-requests 1800
```

One window, not two, because it makes pairing see originals and their 2026 corrections together
(no placeholder churn) and costs **one** detail call per corp instead of two. A 15-month detail
window was probed first and is accepted (`status 000`, 2 rows) — the 3-month cap is `list.json`'s
alone, and only without `corp_code`.

Live run: 8,536 list rows scanned in 5 chunks × 2 markets → 1,508 target rows (529 originals,
864 기재정정, 115 첨부정정) → 566 events, 1,508 versions; 410 detail calls → 548 rows, 542
matched, 1 adopted, 5 unmatched; 66 placeholder events retired `superseded_by_pairing`.
Database `(event, version, snapshot)` **(435, 1227, 2008) → (1182, 3300, 5785)**.

본문 prioritisation, as the plan asked — urgency set first, then corrections for pairing hints:
90 documents for the soonest-opening events, 700 for the 정정 backfill, 13 for the blocked set.
The 정정 pass took `ambiguous` **576 → 413 versions**, reattached 60 versions to the event their
본문 `최초제출일` names, and raised the parsed-정정 count **436 → 1,149** (6,227 정정사항 rows).

Side effect worth keeping: the 2025-06→12 `list.json` pages are now in `var/dart-cache`, so an
①/③ backfill over the same period costs **0 discovery requests**.

### 5. Prose extraction (fields 6–8) and the first exercise of gates 6–8

```
python -m mijual.cb extract --until 20261231 --today 20260907 --limit 45 --max-calls 80
```

**80 calls exactly, 797,099 tokens, ▷ $1.0677, 0 failures** — 44 `r2_prose` (3 fields per call,
N36's grouping) over the 45 soonest-opening exposable events, then 36 correction calls over the
18 of them with two documented versions. Extraction: lockup_release 42/44, option_schedule
39/44, refixing_terms 33/44; **112 of 114 quotes located**, 111 byte-verified.

Triage, stated plainly: the urgency set is **171 events** and 45 were read. The other 126 keep
their full API countdown (전환가액 · 전환청구기간 · 오버행 비율) and simply have no 리픽싱/콜풋/
보호예수 narrative — D-1's structured-only floor, taken deliberately, soonest-opening first.

Gates 6–8, per gate, on 62 rows each:

| gate | passed | failed | n/a | the substantive check |
|---|---|---|---|---|
| **#6 리픽싱** | 42 | 1 | 19 | `floor == API act_mktprcfl_cvprc_lwtrsprc` **compared 29 times, agreed 29/29, 0 mismatches**; 13 skipped (the API field is blank in 87/267 rows) |
| **#7 콜·풋** | 53 | 2 | 7 | dates within 발행일~만기일: 37 checked, **1 real catch**, 16 skipped |
| **#8 보호예수** | 48 | 3 | 11 | see below — the gate had to move |

**§7 #6 held exactly as written** — the first corpus confirmation that the 본문's 리픽싱 최저
조정가액 equals the API's. **§7 #8 had to move, and this is an N45-class finding:** a CB states
전매제한 as a **duration, not a date** (`사모발행에 의한 1년간 행사 및 분할금지`) in **31 of 62
rows**, and every row that did carry a date carried one the *model* had computed by adding 12
months to the 발행일 — which is precisely the arithmetic §3.6 assigns to the code. Gate 8 now
derives the 해제일 deterministically (`mijual.calc.lockup_release_date`, API `pymd` + 개월수),
checks any model-stated date **against** that derivation (±3 days for the 발행일/납입일 wobble),
and records a filing that quantifies nothing as `not_evaluable(lockup_not_quantified)` rather
than a failure. Result: 31 failures → 3, and the 3 are real.

**The 4 remaining ② failures are all one finding, and it is a good one.** 엑시큐어하이트론
`20260630000509`, 알파AI `20250930000580`, 제이에스링크 `20251204000439` are 정정 filings whose
본문 `최초제출일` names an event this workspace never collected (2024-09-06, 2025-05-07,
2024-12-17), so nearest-earlier pairing attached each to a **different CB of the same corp**.
The API-derived cross-checks in gates 7 and 8 are the **only** layer that noticed — no other
check compares a 본문 reading against a machine value that belongs to a specific 사채. 30 of the
422 exposable ② events carry `hint_mismatch`. Not fixed here: making `hint_mismatch` blocking
would also block 42 passing ① rows and reopen S5/N48's settled decision. **Defer-job candidate,
named in `phase.md` (N63).**

### 6. Beat registration

② rides the existing schedule; it got **no** task and **no** beat entry of its own.
`DEFAULT_ENDPOINTS` is derived from `TARGETS`, and `PipelineConfig.endpoints` defaults to it, so
registering the target put ② inside the existing `collect` stage — same window, same lock, same
ceilings — instead of adding a second schedule that could interleave with the first.
`extract_rights` stays `(R1, R3)`: ② needs zero LLM (N6). The backfill stays a one-off CLI —
a scheduled job's window rolls forward, so a fixed historical window has no business in one.

### 7. 오버행 캘린더 evidence (regenerated from the final run, N8)

`python -m mijual.cb calendar --today 20260907` — 0 requests, 0 calls:

```
events     : 673 ② event(s) held, 422 exposable with a complete API countdown
blocked    : {event_key_collision 58, incomplete_api_row 1, no_detail 68,
              superseded_by_pairing 107, unpaired_correction 9, withdrawn 8}
vintage    : {2023: 1, 2024: 1, 2025: 197, 2026: 223}   (by 최초 접수연도)
open now   :  67 event(s) already inside 전환청구기간
opens ≤ 30d:  33 event(s) | 최대 오버행 49.14% (지엔코 20250908000230, 2026-09-10)
opens ≤ 90d:  82 event(s) | 최대 오버행 67.80% (효성화학 20251031000547, 2026-12-04)
opens ≤180d: 152 event(s) | 최대 오버행 67.80% (효성화학 20251031000547, 2026-12-04)
  2026-09-08  D-1    9.28%  한국석유공업      20250905000042
  2026-09-10  D-3   49.14%  지엔코           20250908000230
  2026-09-10  D-3   14.13%  퀄리타스반도체     20250902000219
  2026-09-11  D-4    4.69%  한중엔시에스      20250903000369
  2026-09-11  D-4    9.09%  케이엔에스        20250904000437
  2026-09-11  D-4   18.99%  삼기에너지솔루션즈  20250902000329
  2026-09-12  D-5   10.38%  신테카바이오      20250912000367
```

**Density vs P1's measurement:** P1 measured 263 distinct CB reports in 7.5 months of 2026
(▷ ~35/month). This corpus holds **530 CB originals over 14.7 months** (2025-06-01 → 2026-08-20)
= ▷ ~36/month — consistent, and the 2025 half is not thinner than the 2026 half. The urgency is
not a rate effect; it is the **~12-month 전환청구 lockup**: a CB filed in 2025-H2 opens in
2026-H2, which is why the backfill and only the backfill produces a judging-week calendar.

## Operator directive (2026-08-20): per-task thinking level

Arrived mid-slice, after the 80 extraction calls were already spent. Per the directive those
were **not** re-run; the knob lands for future runs.

**Mechanism** (verified against the installed SDK, `google-genai` 2.18.1): gemini-3.7-flash is a
3.x model, so the knob is `types.ThinkingConfig(thinking_level=…)` with
`MINIMAL | LOW | MEDIUM | HIGH` — not the older `thinking_budget` token count. Sending **no**
`thinking_config` at all is what inherits the project preset; sending an empty `ThinkingConfig()`
would still be an instruction, so the code omits the field entirely when a task inherits.

**Measured, on one real `r2_prose` prompt (11,491 prompt tokens, 신테카바이오 `20250912000367`):**

| level | thinking tokens | output | ▷ cost | fields returned |
|---|---|---|---|---|
| preset (as spent) | **866** | 1,111 | $0.0160 | 3/3 |
| explicit `LOW` | **0** | 1,067 | $0.0126 | 3/3 |

**–100 % thinking tokens, –21 % cost on the same prompt.** A third call diffed the `LOW` payload
against the stored preset-level extraction: **every gated value is identical** — `floor_price`
3,962, `floor_ratio` 0.7, `release_date` 2026-09-12, `months` 12, the put option's
2026-08-24~2028-08-07 — and only the free-text `detail` wording differs. Applied to this slice's
actual run, `LOW` on the 44 prose calls would have saved ▷ $0.19 of ▷ $1.07 (18 %).

**What landed:** `THINKING_BY_TASK` in `extract/client.py` — `r1_prose`/`r2_prose`/`r3_prose` →
`LOW`; `correction` and `probe` → inherit the preset; anything unlisted → `LOW`
(`DEFAULT_THINKING_LEVEL`), so a new routine reader cannot silently inherit HIGH.
`generate_json(..., thinking_level=…)` overrides per call. `correction` keeps the preset by
judgement, not by omission: it is the only task that *reasons* (diffs two versions, decides which
changes moved a D-day) and N41's quality measurement — 121 changes, 0 unsupported — was taken at
the preset level; re-measuring it belongs with `P2.S9`'s accuracy report, not here. The level
used is recorded per call (`CallResult.thinking_level` → new nullable
`extraction_call.thinking_level`, added through `ensure_columns`, no reset), because a ▷ cost is
only comparable across runs if the level it was measured at is known. The 180 calls spent before
the column existed read `NULL`, honestly.

Directive spend: **3 live calls, ▷ $0.040**, over the ~80 cap and reported as its own line.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **44 passed** (37 inherited + 7 new, all offline) |
| `python -m mijual.collect … --endpoints cvbdIsDecsn` (live) | 584 req, 566 events / 1,508 versions, no quota error |
| same command re-run, identical inputs | **0 new events, 0 new versions, 0 new snapshots** (N14 idempotence) |
| offline replay of the live window | +36 versions / +50 snapshots on the first pass, **0 on the next two** — N34's rule, converged |
| `python -m mijual.gates run` × 2 | **byte-identical** output (`diff` clean) |
| `python -m mijual.scheduler once --offline --bgn 20260601 --end 20260820` | green, 4/4 stages, **0 requests / 0 calls**, ② collected inside the `collect` stage |
| `python -m mijual.cb calendar --today 20260907` | 0 requests, 0 calls, table above |
| secret scan (all 184 tracked-ish files vs `.env` values) | **0 hits** |
| `python3 scripts/workflow.py validate` | OK |

The 7 new tests (`tests/test_cb.py`, terse, offline against the P1 cache + SQLite): the ② target
vs its six lookalike subtypes; the API row parsed into field-matrix §2.1's exact numbers plus the
partial 파이온엑스 row; the R2 exposure arm (no detail → `no_detail`, complete → exposable with
**zero** fields, one field dropped → `incomplete_api_row`, 철회 → ②'s notice) and the calendar
reading it; the ② withdrawal row shape vs ②'s own boilerplate; gate 8's derivation; the 2025-H2
window chunking; and the thinking-level map.

## Deviations from `plan.md`

1. **One live collection window (2025-06-01 → 2026-08-20) instead of "2026 YTD, then the
   backfill".** Same coverage, better pairing (originals and their corrections in one pass, no
   placeholder churn) and ~half the detail calls. The offline 2026 pass over the P1 cache still
   ran first, as the plan asked.
2. **A new `mijual.cb` package** rather than only extending existing modules. ②'s structured
   reading (`ConvertibleFacts`), the 오버행 캘린더 and the urgency selector needed one home, and
   `P2.S8` inherits it. The CLI is `calendar` / `show` / `documents` / `extract`; collection
   itself deliberately got **no** ② command, because ② is a normal collector target.
3. **Gate 8 was rewritten, not just exercised.** The plan said "run gates afterwards — first real
   exercise of gates 6–8". §7 #8 as written failed 31 correct readings and rewarded the model for
   doing arithmetic the phase assigns to `mijual.calc`. Fixing it is inside "exercise the gate"
   as N45 established for ①'s rows #2/#4/#5; leaving it would have shipped a 50 % failure rate
   that means nothing.
4. **Two beyond-plan cheap fetch passes:** 700 정정 본문 (the plan's "then corrections needed for
   pairing hints") and 13 documents for the *blocked* set. The second found 대진첨단소재's
   withdrawal and is the reason `documents --blocked` exists. Both inside the request ceiling.
5. **A pre-existing CLI bug fixed:** `python -m mijual.collect --report` crashed writing its JSON
   (`rows_by_kind` is a `Counter` keyed by `CorrectionKind`; JSON object keys must be strings).
   The run itself had already persisted everything. One-line fix in the report writer.
6. **The operator directive** (per-task thinking level) was folded in as described above; the
   spent extraction calls were not re-run, per the directive.

## Doc impact notes appended to `phase.md`

Three one-liners — ②'s collection + exposure semantics, the ② 철회 / gates 6–8 outcome, and the
D-4 thinking-level amendment. No `doc-new-version` was run (that is `P2.REVIEW`'s job).
