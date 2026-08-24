# Result: P2.S8 — 2026 소멸 신주인수권 가치 총액

_Executed 2026-08-20 by `slice-executor-high`. Every number below is printed by
`.venv/bin/python -m mijual.estimate report --today 20260820`, which runs at **0 OpenDART
requests and 0 LLM calls** (N8: nothing here is hand-copied)._

## The headline

**▷ 71,812,971,649원 — 약 718.1억원 of 신주인수권 value lapsed unexercised in 2026 (YTD 08-20),
across 32 완료된 ① 주주배정 유상증자.**

- 소멸 증서 **51,253,956주** / 배정된 증서 **365,527,824주** → **소멸률 14.02 %**
- ▷ band lower edge (권리락-조정 가정): **548.7억원**; ▷ upper edge if the three gate-blocked
  offerings were priced at the corpus median 할인율: **767.3억원**
- Largest single offering: **한화솔루션 ▷ 206.4억원** (청약 종료 2026-07-23, 소멸 3,734,925주,
  `20260730000366`)
- 18 more ① offerings are still open (11 with a 청약 ahead, 2 awaiting their 실적보고서,
  2 철회, 2 추후결정, 1 identity-flagged)

## Method — one line, three inputs, all DART

    소멸가치 = Σ (소멸한 증서 수) × 확정발행가 × 할인율 / (1 − 할인율)

| input | tier | source | evidence |
|---|---|---|---|
| 소멸한 증서 수 | deterministic table | 증권발행실적보고서 `Ⅶ`: 발행 증서 − 증서 청약 | 실적보고서 `rcept_no` + char span |
| 확정발행가 | `본문-label` | 주요사항보고서 `6. 확정발행가`, cross-checked against 실적보고서 최종금액 ÷ 수량 | 유증결정 `rcept_no` + span |
| 할인율 | `본문-prose` | `24-가 신주발행가액 산정방법`, **only when P2.S5's gate passed** | extraction quote + verified span |

**Why the unit value is `확정발행가 × d/(1−d)` and why it is defensible.** There is no price
feed in this repo (`data.md`: DART only). The filing supplies the price itself — every
주주배정 유증 states 발행가액 = 기준주가 × (1 − 할인율) — so the issuer's own 기준주가 is
recoverable by inverting the same equation, and a 증서 is worth ex-rights 주가 − 확정발행가.
The identity holds for **both** pricing formulas, which is why the function takes no formula
argument (`tests/test_estimate.py::test_the_two_pricing_formulas_give_the_same_증서_value`):

- 2차 산식 `기준주가 × (1−d)` measures 기준주가 at 구주주 청약일 전 제3거래일 — already
  ex-rights — so the value is directly `기준주가 − 확정 = 확정·d/(1−d)`;
- 1차 산식 `[기준주가 × (1−d)] / [1 + (증자비율 × d)]` uses a cum-rights 기준주가, and its
  증자비율 term **is** the 권리락 adjustment: 이론권리락주가 − 확정 = `(기준주가 − 확정)/(1+r)`
  = `확정·d(1+r)/((1−d)(1+r))` = the same expression.

All arithmetic is in `mijual.calc` (`warrant_intrinsic_value`, `warrant_intrinsic_value_floor`,
`implied_reference_price`, `lapsed_warrants`), Decimal, rounded once, unit-tested with no LLM.

**Sensitivity — one paragraph, honestly.** The proxy is the *filing's own implied* intrinsic
value, marked ▷, not an observed 증서 시세. Three directions of error, all stated rather than
averaged away. (1) A minority of filers write the 1차 산식 **without** the 증자비율 term
(형지I&C `20260707000087`: `예정발행가액 = [기준주가 × (1-할인율)]`); if such a price came off a
cum-rights 기준주가 the ex-rights value is smaller by `1 + 배정비율`. Applying that factor to
every row gives the band's lower edge, **▷ 548.7억원** — so the true figure sits in
**▷ 549억 ~ 718억**. (2) The `MAX(…, 기준주가의 60%)` floor branch means an issue priced at the
floor carries an effective 40 % discount rather than the stated `d`, which makes the headline
*conservative* there. (3) The market price on the actual 매매기간 can be anywhere; a 증서 whose
stock fell below 발행가 was worth nothing, which the proxy cannot see. The alternative proxies
considered and rejected: 예정발행가 (superseded by the time the 증서 traded), 실권주 일반공모
경쟁률 (evidence of demand, not of price — though 247:1 · 1,092:1 · 43:1 competition on the
resold 실권주 does corroborate that the discount was real), and any external 시세 (forbidden).

## What the slice built

| file | what |
|---|---|
| `src/mijual/estimate/perf.py` | 증권발행실적보고서 census (`list.json pblntf_ty=C`) + the deterministic table read, every figure a `Cited(value, raw, span)` |
| `src/mijual/estimate/adopt.py` | targeted, corp-scoped adoption of a 유상/유무상증자결정 the corpus does not hold (3–4 requests per offering) |
| `src/mijual/estimate/runner.py` | census → 본문 → parse → link → adopt → persist, plus the per-event backstop |
| `src/mijual/estimate/__init__.py` | `build_report` — the estimate from persisted rows only |
| `src/mijual/estimate/__main__.py` | `report` / `collect` / `census` / `show` |
| `src/mijual/db/models.py` | new `PerformanceReport` table (raw ZIP retained + `content_sha1`, `facts` JSONB with spans) |
| `src/mijual/calc.py` | `lapsed_warrants`, `implied_reference_price`, `warrant_intrinsic_value`, `warrant_intrinsic_value_floor` |
| `src/mijual/collect/targets.py`, `collect/filters.py`, `bodydoc/backfill.py` | register `pifricDecsn` (유무상증자결정) as an ① target and teach the two `ic_mthn` readers its `piic_` prefix |
| `tests/test_estimate.py` | 7 terse tests: the formula identity, the value helpers' refusals, `lapsed_warrants`, one real 실적보고서 read with span verification, the mismatch case, the header-not-position rule, one offline end-to-end |

**No LLM reads the 실적보고서.** Everything it contributes is a labelled table, so the phase
constraint ("anything deterministically readable must not be paid for with an LLM call") makes
0 calls the right answer there. The 22 calls this slice did spend are all `r1_prose` — the
할인율 of the 22 newly adopted offerings.

### Storage design (why not a `FilingVersion`)

A 실적보고서 is a *different filing about the same offering*: filed on the 납입일, weeks after
the last 정정, carrying no 유상증자결정 form. Attaching it as a version would make it the
event's `latest_version` — the row the gates, the exposure contract and the ② calendar all read
as "today's reading" — and the countdown would then be derived from a document with no schedule
in it. So it is a sibling table keyed by its own `rcept_no`, keeping `Snapshot`'s evidence
contract (raw bytes + sha1, idempotent re-collection). `create_all` adds the table; no reset.

### Linking is an equality between two independently filed schedules

The report's `1. 청약 및 납입일정` must equal the 주요사항보고서's `11. 청약예정일`. **32/32
linked by `schedule_match`** — no row rests on the corp-only fallback. That fallback also
respects time (a corp's only ① event may be a *later* offering: 트리니티항공's single event was
dated 2026-06-22 against a 2026-03-19 report, and binding those would have attached the wrong
확정발행가 and 할인율 to a real 실권 count).

## Coverage — and why the corpus alone would have been wrong by 3×

Framing the year on the **주요사항보고서** filing window is the wrong frame for a *lapse*
number: the 청약 lands two to six months after the 결정. Framing it on the **실적보고서** makes
the population exactly "what completed in 2026".

- census: **8,841 발행공시 rows → 2,533 증권발행실적보고서 → 68 on an equity offering**
- documents read: **69** (68 census candidates + 1 backstop) → **32 carry a 신주인수권증서
  table**, 37 do not (IPO / 스팩 / 제3자배정 — recorded with a reason, not dropped)
- of those 32, **10 were reachable from the pre-S8 corpus and 22 were not.**

The 22 split into three distinct blind spots, each now measured:

1. **14 offerings were decided before 2026-01-01** — outside `P2.S2`'s collection window.
2. **7 were filed as `주요사항보고서(유무상증자결정)`** — a subtype string the collector's exact
   match never accepted, on an endpoint (`pifricDecsn`) it did not know. Registered now.
3. **3 were 2026 KOSDAQ `유상증자결정` originals that `P2.S2`'s run simply missed**
   (레이저옵텍 `20260109000634`, RF머트리얼즈 `20260408002647`, 피엠티 `20260409002139`).
   Discovery finds all three today (verified: a 1-day `discover` over 2026-01-09 returns
   `20260109000634`), so this is a **run** gap, not a code gap — the corpus is not a census.
4. **1 more was invisible to the census itself**: KB스타리츠 `20260423000439` is filed as
   증권발행실적보고서(집합투자증권) and appears on **no page** of the 2026 발행공시 census. The
   per-event backstop (one corp-scoped `list.json` per closed-청약 event) caught it.

Adoption also **healed** N21 residue: the corpus held `unpaired_correction` placeholders for
코이즈, 캠시스, 진양폴리우레탄, 트리니티항공, 레이저옵텍, RF머트리얼즈, 피엠티 precisely because
their original was outside the window or of the unknown subtype. Adopting the real original let
`P2.S2`'s own `retire_superseded_unpaired` retire the placeholders as `superseded_by_pairing`.

## Cross-checks that make the numbers facts rather than readings

- **확정발행가, two documents, two arithmetics: 31/31 exact.** 본문 `6. 확정발행가` equals the
  실적보고서's 최종 배정 금액 ÷ 최종 배정 수량 on every offering that states both. The 32nd
  (형지엘리트) prints a 9-column `계` row, so it is 본문-only and labelled as such.
- **소멸 증서 수, two tables: 26/31 comparable rows agree exactly, 5 disagree and the Ⅶ tables
  win** (the 32nd, KB스타리츠's REIT form, has no `Ⅶ` section to compare against). The
  filer's own `Ⅷ 신주인수권증서 청약 실권주` cell can be wrong: LB세미콘 `20260811000597` states
  2,109,436 where Ⅶ gives 11,970,900 − 9,890,564 = **2,080,336** (the 29,100 gap is 단수주,
  which was never issued as a 증서 and therefore never a right that could lapse); 라온피플,
  대한광통신, 인베니아, 피엠티 differ the same way. `mijual.calc.lapsed_warrants` encodes the rule.
- **Every quoted figure re-slices to itself** in the stored bytes (`estimate show` prints
  `verify=ok` per figure; the test asserts it on three).

## Honest gaps

| gap | size | why |
|---|---|---|
| 3 offerings counted but **not valued** — 진양폴리우레탄, 캠시스, LB세미콘 | 8,235,988 소멸 증서; ▷ ~49.2억원 at the median 할인율 | their `issue_price_formula` extraction **failed its gate with `span_unresolved`** — the model stitched formula fragments from separate paragraphs into one quote, so there is no citation. A field that fails its gate is not used here either. This is the trust claim costing 6.4 % of the headline, on purpose. |
| 2 offerings 청약-closed with no 실적보고서 yet — 센서뷰, 클로봇 (청약 종료 2026-08-14) | not in the total | the 실적보고서 is filed on the 납입일; theirs has not arrived. Listed as pending. |
| 11 offerings with a 청약 still ahead | not in the total | soonest 2026-09-04 (계양전기, SG) |
| 2 철회 (썸에이지, 제이알글로벌리츠), 2 추후결정 (경남제약, 에이전트AI) | not in the total | no 청약 happened / no schedule exists |
| 1 identity-flagged (이렘, `detail_conflict`) | not in the total | N51/N20(b) collector-side work |
| 한솔테크닉스 counted although `event_state=flagged` | ▷ 12.6억원 | a lapse is a fact about the **past**; the flag is a collector identity collision, not a doubt about the offering. Its 실적보고서 links by schedule and its price cross-checks exactly. Called out in the report's own output. |
| KOSDAQ/KOSPI only | — | KONEX adds zero ① (O-4, N24) |
| 소멸률 denominator excludes KB스타리츠 | 2,167,828 소멸 counted, 발행 증서 unknown | the REIT form has no `Ⅶ` section, so 발행 증서 is not stated. Its 실권주 is counted; it just cannot contribute to the rate. |

## Judging-week framing (Korean product surface)

`report --korean` prints these, regenerated from the same table:

> · 2026년에 소멸한 신주인수권 가치는 ▷ 약 718.1억원입니다.
>   (증권발행실적보고서 32건 · 소멸 증서 51,253,956주 × 확정발행가 × 할인율/(1−할인율))
> · 주주에게 배정된 신주인수권증서 365,527,824주 가운데 14.0 %가 청약도 매도도 되지 않고 사라졌습니다.
> · 한 건에서만 206.4억원이 사라졌습니다 (한화솔루션, 청약 종료 2026-07-23, 소멸 3,734,925주 — 20260730000366).
> · 지금도 11건의 신주인수권이 소멸을 앞두고 있습니다 (가장 빠른 청약 마감 2026-09-04, 계양전기).
> · 모든 수치는 DART 공시에서만 나왔고, 추정치는 ▷로 표시했습니다.

The fourth line is the one that turns the number into a product: the same pipeline that
measured the past names the offerings whose 신주인수권 is about to lapse during the judging
window. Per-offering spread worth knowing: 소멸률 ranges **2.51 % (SKC) to 49.09 % (형지I&C)**,
median 11.60 % — "half the shareholders let it go" is a real, cited case, not a rhetorical one.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **51 passed** (44 existing + 7 new), 0 failures |
| `.venv/bin/python -m mijual.estimate report --today 20260820` ×2 | byte-identical; a monkeypatched `DartClient._fetch` that raises proves **0 live requests**, and the run makes **0 LLM calls** |
| `.venv/bin/python -m mijual.estimate collect --bgn 20260101 --max-requests 250` | third consecutive run: 3 live requests, 0 new documents, 0 unlinked — re-running is nearly free (N25) |
| `.venv/bin/python -m mijual.estimate show 20260811000597` | every figure `verify=ok`, mismatch note printed |
| `.venv/bin/python -m mijual.collect --bgn 20260817 --end 20260820 --no-documents` | collector smoke with `pifricDecsn` registered: 10 requests, clean, DB counts unchanged; the estimate is byte-identical afterwards |
| `python3 scripts/workflow.py validate` | **passed** |

### Spend

- **OpenDART: ~337 live requests of the 500 ceiling** — 159 survey/probe (incl. the 85-request
  census pages, now cached), 111 across three `collect` runs, 39 `bodydoc warrants`, 18
  collector smoke/verification. No quota error; the 20,000/day cap (O-1) was never near.
- **LLM: 22 calls, 158,863 tokens, ▷ $0.2186** — all `r1_prose`, all at **`thinking_level=LOW`**
  (D-4 as amended, N65) with **0 thinking tokens** recorded in `extraction_call.thinking_level`.
  Ceiling was 40. 0 failures. The 실적보고서 layer spent **0 calls by design**.
- ▷ cost basis unchanged: $0.75 / $3.75 per 1M in/out (N35). Estimate, not a billed figure.

## Deviations from `plan.md`

1. **The frame moved from "the 2026 ① corpus" to "the 2026 증권발행실적보고서 census."** The plan
   said discovery via `list.json` for the corps of ① events whose 청약일 has passed. That arm
   exists (the per-event backstop) but it would have found **10 of 32** offerings, because a
   right that lapsed in 2026 was usually decided in 2025. The census is the honest population
   and the plan's own discipline ("honest gaps stated") pointed at it.
2. **Collector-side work was done, not deferred**, in two places the plan did not name: the
   `pifricDecsn` (유무상증자결정) target registration, and the targeted per-corp adoption of 22
   missing 유상증자결정 events. Both were the cheapest way to reach an evidence-complete number
   (adoption costs 3–4 requests per offering against ~300 for a market-wide 2025-H2 re-run), and
   both land as ordinary corpus rows so nothing downstream sees a second class of evidence.
3. **Zero LLM calls on the 실적보고서 path** rather than the budgeted bounded pass: the 청약 결과
   is entirely in labelled tables. The 22 calls spent went to the *할인율* of the adopted
   offerings — the same §7 field, the same registry, the same gate, no new field registered.
4. **No `defer-job` was filed** (executors do not run workflow commands); the two candidates are
   named in the phase note for the orchestrator.
