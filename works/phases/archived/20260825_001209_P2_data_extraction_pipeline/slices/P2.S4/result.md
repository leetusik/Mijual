# Result: P2.S4 — LLM extraction (layer 1): Gemini schema extraction + 정정 재추출

Status: **done**. `mijual.extract` reads the §7 prose fields out of a stored 본문 snapshot and
returns, per field, a normalized value plus a **citation span that this package located itself**.
Across the whole target corpus: **304 extraction rows over 70 filing versions / 40 events**,
**292 of 293 model quotes located in the stored snapshot (99.7 %)**, **0 failed calls**, and
**▷ $1.41** of estimated spend over **100 stored calls** (102 including two scratch probes) — well
inside the plan's ~150–200 ceiling.

Both blocking operator questions closed: **O-2** (credential + model id + the preset thinking level,
measured) and **O-1** (20,000 OpenDART requests/day, recorded).

Two findings are worth more than the code: **two exposable ① events have already been 철회
(withdrawn)** and the deterministic layer cannot see it (their label table still reads 10/10), and
**`추후결정` is a third field state** the gate must handle. Both are countdown-critical and land on
`P2.S5` — see N39/N40.

## What landed

```
src/mijual/extract/__init__.py   public surface + the four fences on this layer
src/mijual/extract/fields.py     the 10 §7 targets: value schema, instruction, gate, anchor
src/mijual/extract/client.py     GeminiClient — structured output, max_calls ceiling, usage ledger
src/mijual/extract/locate.py     quote -> span, deterministically (the model never supplies one)
src/mijual/extract/inputs.py     input regime: whole 주요사항보고서 / window / 증권신고서 section
src/mijual/extract/prompt.py     Korean prompts; deliberately context-free (see N38)
src/mijual/extract/store.py      idempotent upserts + call accounting
src/mijual/extract/runner.py     corpus run, 정정 재추출 + diff, deterministic relocate pass
src/mijual/extract/__main__.py   probe | fields | run | corrections | relocate | summary | show
tests/test_extract.py            5 terse offline cases (no live API call in pytest)
```

Touched elsewhere (additive): `db/models.py` (+`ExtractionCall`, +`Extraction`, and `Boolean`/`Float`
imports), `db/__init__.py` (exports), `pyproject.toml` (`google-genai>=1.0`).
`bodydoc`, `collect`, `dart` untouched — this slice only *reads* them.

## O-2 closed: the probe, and what the preset actually does

`python -m mijual.extract probe` (one call, no thinking config sent):

```
model      : gemini-3.7-flash (server: gemini-3.7-flash)   # models.get -> version 3.7-flash-08-2026
status     : ok, 1 attempt
usage      : prompt=71 thinking=423 output=30 total=524
thinking   : preset ACTIVE (no thinking config was sent)
```

- The credential's model list contains **`models/gemini-3.7-flash`** (50 models visible; also 3.6, 3.5,
  3.1, 2.5 flash lines) — the operator's model id is real and reachable.
- **The project preset applies a thinking level**: 423 thought tokens on a trivial prompt, 565 on a
  small extraction, ~1.2k on a real one. Per the plan, **no thinking config is hardcoded** — passing
  one would silently override an operator-side decision (D-4).
- Structured output works through `response_json_schema` including union types (`["string","null"]`)
  and `enum` with `null`, which is what let the value schemas stay honest about "not stated".
- ▷ Rate card used for every cost figure below: **$0.75 / $3.75 per 1M input / output tokens**
  (gemini-3.7-flash introductory pricing through 2026-12-31; $1.50 / $7.50 from 2027-01-01), thinking
  tokens billed as output. **Estimates, not billed amounts.**

## The run

Priority order was the plan's: ① first, ③ second, 정정 last. Every document came from a **stored
snapshot — 0 OpenDART requests were spent in this slice.**

| pass | events | calls | prompt tok | thinking tok | output tok | ▷ cost |
|---|---|---|---|---|---|---|
| `run --rights R1 --include-conflict` | 29 (28 `warrant_confirmed` + 1 `warrant_conflict`) | 28 + 1 pilot | 155,146 | 36,629 | 41,100 | $0.408 |
| `run --rights R3` | 15 (11 with 본문) | 11 | 137,561 | 10,742 | 4,000 | $0.159 |
| `corrections --rights R1` | 22 pairs | 44 (22 prev-version + 22 해석) | 272,028 | 50,721 | 52,460 | $0.591 |
| `corrections --rights R3` | 8 pairs | 16 | 193,481 | 16,875 | 12,786 | $0.256 |
| **stored total** | **40 events** | **100** | **758,216** | **114,967** | **110,346** | **▷ $1.4136** |

Plus **2 scratch probe calls** (model probe + schema probe, ~1,800 tokens, ▷ $0.003) →
**102 calls total**, cap ~150–200. **0 failed calls, 0 retries.**

`python -m mijual.extract summary` (regenerated from the database, N8):

```
extractions: 304 row(s) over 70 filing version(s), 40 event(s)
  field                        rows extract absent  err span_ok unres verif
  correction_interpretation      30      30      0    0      30     0    30
  dissent_notice_procedure       19      18      1    0      18     0    18
  excess_subscription            51      49      2    0      49     0    49
  forfeited_share_method         51      49      2    0      49     0    47
  issue_price_formula            51      49      2    0      48     1    48
  subscription_agents            51      49      2    0      49     0    49
  warrant_trading_period         51      49      2    0      49     0    49
  locate methods: {'-': 1, 'exact': 290, 'trimmed': 2}
corrections: 30 interpretation(s) | 정정사항 rows 137 (uncovered 20) | model changes 121
             (unsupported 0) | prose value moves 95 | change quotes located 121/121
calls      : 100 stored {'correction': 30, 'r1_prose': 51, 'r3_prose': 19}, 0 not ok
model      : {'gemini-3.7-flash/gemini-3.7-flash': 100}
```

**Product-facing coverage on each event's current version** (what P3 could actually show):

| field | ① 29 events | ③ 11 events with 본문 |
|---|---|---|
| 신주인수권증서 상장·매매기간 | **25 citable**, 2 철회, 2 `추후결정` | — |
| 청약 취급처 | **27 citable**, 2 철회 | — |
| 실권주 처리 방식 | **27 citable**, 2 철회 | — |
| 초과청약 조건 | **27 citable**, 2 철회 | — |
| 발행가액 산정방법 | **26 citable**, 2 철회, 1 span-unresolved | — |
| 반대의사 통지 방법·절차 | — | **10 citable**, 1 절차 미기재 |

(4 further ③ events — all SPAC 합병 — hold **no 본문 at all**, so they were never sent anywhere.)

### Worked example — 계양전기 `20260724000546`, §7 field 1

```
warrant_trading_period       extracted span=(30615, 30663) resolved exact verified=True
    값: start_date=2026-08-19, end_date=2026-08-25
    인용: 3) 신주인수권증서 상장예정기간 : 2026년 08월 19일~ 2026년 08월 25일
```

`BodyDocument.verify(Span(30615, 30663), quote)` is **True** — S3's contract (N33), applied to a model
quote. Field-matrix §1.1 lists exactly `2026-08-19 ~ 08-25` for this `rcept_no`, from an independent
P1 reading, so the value is right as well as located.

## The span contract, measured

The model returns a value **and a verbatim quote**; `mijual.extract.locate` then finds that quote in
the stored snapshot through bodydoc's offset map. **No span is ever read from the model.**

| outcome | count | what it means |
|---|---|---|
| `exact` | 290 | the quote is a substring of the flattened snapshot; `doc.verify` is **True** |
| `trimmed` | 2 | matched after dropping a leading list marker the model re-rendered (`①` → `1)`) |
| `nospace` / `head` | 0 | not needed on this corpus (both paths exist and are tested) |
| `unresolved` | **1** | LB세미콘 `20260730000278` `issue_price_formula` |

The one unresolved case is instructive and is exactly what the design is for: the model **stitched
three formulas that sit in different paragraphs** (`▶ 1차 … ▶ 2차 … ▶ 확정 …`) into one quote. Each
fragment is genuine; the concatenation is not in the document, so it is **not** a citation. The value
is stored with `span_status='unresolved'` and `P2.S5`'s citation gate will block it.

Because location is a pure function of (quote, snapshot), improving it must never cost another call:
**`python -m mijual.extract relocate` re-derives every span for 0 calls** (293 row-level quotes + 121
정정 change quotes). It is also the honest re-check after a re-collection — a snapshot that changed
under a stored span makes the quote stop locating instead of pointing at the wrong characters.

## 정정 재추출 + diff (§7 field 10)

Per corrected event: re-extract the prose fields on the **previous** version, diff them **in Python**
against the newest version's values, hand the model (a) bodydoc's deterministic `3. 정정사항` rows and
(b) that value diff, and ask only for normalisation + schedule interpretation.

- **30 interpretations** (22 ① + 8 ③), every one with a located, verified row-level span.
- **137 deterministic 정정사항 rows** fed in; the model produced **121 changes, 0 of them unsupported**
  by the rows (the consistency check runs on every record and stores its counts), and **left 20 rows
  uncovered** — mostly in the two 13-row 합병 corrections, where it merged near-duplicate rows.
- **95 prose value moves** computed deterministically across version pairs.
- **121/121 per-change quotes located** in the 정정 후 본문.

계양전기's record, stored on `20260724000546`, reads: 2 deterministic items (자금조달의 목적,
6. 신주발행가액 예정발행가 4,985 → 3,200), both covered, `schedule_impact: "일정 변동 없음"`,
`summary: "1차 발행가액 확정에 따라 예정발행가액(4,985원 → 3,200원) 및 자금조달의 목적별 금액이
하향 조정되었습니다."` — and the 3 prose fields whose wording moved between `20260611000483` and
`20260724000546`, each with a span on the new version.

## Two findings that outrank the code

**1. 철회 (withdrawal) is invisible to the deterministic layer, and two exposable ① events are
already withdrawn.** 썸에이지 `20260805000454` (`warrant_confirmed`) and 제이알글로벌리츠
`20260205000605` (`warrant_conflict`) both file a ~1.9k-char `[기재정정]` whose 정정사항 table holds a
single row — **항목 `유상증자 결정`, 정정 전 `유상증자 결정`, 정정 후 `유상증자 철회`** — and whose
prose says `부득이하게 금번 유상증자를 철회하기로 결정하였습니다`. Their label table still parses
**10/10**, so `bodydoc`'s ① filter reports a perfectly healthy event; it was the extractor returning
`present=false` on all five fields that surfaced it. **Publishing 썸에이지 today would advertise a
매매기간 that has been cancelled.** The detector is deterministic and cheap (that one 정정사항 row) —
`P2.S5` should implement it there, not in the LLM. A naive `"철회" in 본문` keyword test does **not**
work: it also fires on 증권신고서 boilerplate (2 ① events) and on 매수청구 boilerplate (7 of 15 ③).

**2. `추후결정` is a third state, not a missing value.** 경남제약 `20260623000409` and 에이전트AI
`20260619000455` are 정정 filings that suspended the whole schedule: `3) 신주인수권증서 상장예정기간 :
추후결정`, `청약일 추후결정`. The extraction is `status='extracted'` with a located, verified span and
**all dates `null`** — deliberately not `absent`, because the document does say something. The gate
must distinguish "no date yet" from "field absent" from "stale date", and the board must not fall back
to the superseded schedule.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **24 passed** (19 from S1–S3 + 5 new), 0.4 s, no live API call |
| `python -m mijual.extract probe` | ok — model reachable, preset thinking measured (423 thought tokens) |
| `python -m mijual.extract --dry-run run --rights R1` | 28 calls / 187,367 chars planned, 0 spent |
| `python -m mijual.extract run --rights R1 --include-conflict` | 29 events, 28 calls, 0 failures |
| `python -m mijual.extract run --rights R3` | 11 documents, 11 calls, 0 failures |
| `python -m mijual.extract corrections --rights R1` / `--rights R3` | 44 + 16 calls, 0 failures |
| re-run of any of the above | **0 calls** (already-stored fields are skipped) — idempotent |
| `python -m mijual.extract relocate` ×2 | 293 + 121 spans re-derived, **0 calls**, stable |
| `python -m mijual.extract summary` | the numbers quoted above, regenerated from the DB |
| `.venv/bin/python -m mijual.smoke --database-url sqlite:///var/smoke-s4.db` | **OK** (S1 chain still green; Postgres corpus untouched) |
| key-leak grep (`src tests docs works scripts var`, both keys) | **0 files**; 0 stored rows contain a key value |
| `python3 scripts/workflow.py validate` | **passed** |

The docker Postgres corpus was **not reset**: 434 events / 1,226 versions / 364 본문 snapshots are
untouched, and the two new tables were created by `create_all` beside them.

## Deviations from `plan.md`

1. **One call per document, not per field.** The plan's deliverable 2 says "per-field JSON schema";
   the *response* is still one envelope per field (`present`/`value`/`quote`/`note`) and every stored
   row is per field, but the five ① fields are read in a **single call** because they live in the same
   `24.` block of a 2.6k–10k-char document. Per-field calls would have cost 140 calls for ① alone —
   most of the slice's whole ceiling — for the same input text read five times. Recorded as **N36**.
2. **The 증권신고서 secondary-source path is implemented but never exercised.** `build_input` enforces
   §5 (a 증권신고서 is section-sliced, never sent whole, and the slicing is unit-tested), but no ① field
   was actually missing for a reason a 증권신고서 could fix: the only gaps are the two **철회** filings
   (where confirming a cancelled schedule is meaningless) and the two `추후결정` ones (where the
   신고서 says 추후결정 too). Wiring it further would also need collector-side work — a 증권신고서 is a
   *different* filing, not a version of these events — which is `P2.S2`/`P2.S7` territory. Handed
   forward rather than half-built.
3. **A `relocate` and a `summary` command were added.** Neither is in the plan. `relocate` exists
   because the locator improved *during* the slice (the leading-marker case) and re-paying for
   extraction to fix a deterministic function would be indefensible; `summary` exists because N8 says
   a committed number must be regenerated from the final state, and a scratch script cannot be.
4. **② (fields 6–8) has schemas but no run**, as the plan directs. `TASKS['r2_prose']` is wired and
   would run today; `P2.S7` owns the corpus.
5. **The `warrant_conflict` event was included** (the plan's "only if cheap"): 1 call. It returned
   `present=false` on all five fields — because it is 철회 — so the conflict question is now moot in
   practice, though `P2.S5` still owns the formal decision (O-8).

## Open items handed forward

- **`P2.S5` must add the deterministic 철회 detector** (정정사항 항목 `유상증자 결정` → `유상증자 철회`)
  and decide the `추후결정` exposure rule. Both are countdown-critical; see N39/N40 and O-9.
- **`P2.S5`'s citation gate has a concrete input**: `Extraction.is_citable` (`status='extracted'` and
  `span_status='resolved'`), plus `span_verified` if it wants to insist on byte-faithful quotes
  (290 of 292 resolved spans are `verified=True`; the other 2 differ only by a list marker).
- **1 span-unresolved value** (LB세미콘 `20260730000278` `issue_price_formula`) is stored and must be
  blocked, not dropped — it is also `P2.S9`'s first accuracy data point.
- **20 deterministic 정정사항 rows the model did not mention** are recorded per record
  (`deterministic_check.uncovered`); `P2.S9` can measure recall from them without another call.
- **4 ③ events (SPAC 합병) hold no 본문**, and 아시아나항공 `20260713000482` holds one with no 절차
  detail — the 증권신고서 is the only remaining source for those five.
- **`var/mijual-preS3.dump`** (gitignored, S3's backup) is no longer needed and can be deleted.
