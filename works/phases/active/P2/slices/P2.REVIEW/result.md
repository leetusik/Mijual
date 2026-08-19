# Result: P2.REVIEW — phase review of P2 (Data & Extraction Pipeline), cycle 1

**Verdict: `changes_requested`.** One blocking finding, two recommended fixes, five carry-forward
items. The phase's substance is done and verified — every objective is met, the trust claim holds on
the live corpus, and the honesty discipline is intact everywhere the operator or a judge will look.
What blocks the freeze is narrow: **`python -m mijual.evalset --help` still tells its reader the
evalset is "hand-labelled"**, which the operator's own 2026-08-20 amendment made false and which N89
declares forbidden. The docs are not consolidated (a non-pass stops before that), so P2 still has no
doc version.

Spend for this slice: **0 OpenDART requests, 0 LLM calls, 0 source edits, 0 commits, 0 state
transitions.** The docker Postgres corpus was read only and not reset.

---

## 1. Validation — the phase run together, today

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **PASS — 56 passed**, exit 0 (collection: 4+7+5+5+5+7+5+5+7+6 across the ten test files) |
| `python3 scripts/workflow.py validate` | **PASS — `Workflow validation passed.`** |
| `.venv/bin/python -m mijual.gates run` ×2 | **PASS — byte-identical** (`diff` clean); 1,345 events judged, 649 field rows, 0 requests, 0 calls |
| `.venv/bin/python -m mijual.estimate report --today 20260820` ×2 | **PASS — byte-identical**; ▷ 718.1억원, 32 offerings, 0 requests, 0 calls |
| `.venv/bin/python -m mijual.evalset report` | **PASS** — 98.6 % strict (213/216), Wilson [96–100 %], over-block 100 % (19/19), 344/344 labelled |
| `.venv/bin/python -m mijual.scheduler once --offline` | **PASS** — all four stages green, **0 requests / 0 calls / ▷ $0.0000**, 31.5 s |
| exposure-invariant re-derivation (read-only, `gates.exposure.exposure_of_all`) | **PASS — 0 violations**, see §2 |
| secret scan: both `.env` values × every tracked file + the 4 `evalset/` artifacts | **PASS — 0 hits**; `.env`, `.venv`, `var/` all gitignored |
| 금지선 grep (`fine-tun`, `pytorch`, `huggingface`, `transformers`, `파인튜닝`) over `src tests docs works evalset scripts` | **PASS** — every hit is the *rule itself* being restated; **0** framings in code, docs or notes |
| request-path check: `grep -rn DartClient src/mijual` | **PASS** — `gates/`, `calc.py`, `db/models.py` contain **no** DART import; only collect/bodydoc/estimate/cb/scheduler/smoke do |

No slice's validation was re-run in isolation; the six commands above are the phase's own headline
claims re-measured against today's corpus, which is what the review is for.

### Headline claims re-measured (N8 discipline)

| claim (source) | measured today | verdict |
|---|---|---|
| board = 488 exposable / 409 renderable (N83, F1) | 488 (① 50, ② 422, ③ 16) / 409 | ✅ exact |
| field verdicts (S5's 275/4/5/20 over 304) | **566 passed / 4 tbd / 14 failed / 65 n/a over 649** | ⚠️ superseded, correctly — see N97 |
| ▷ 718.1억원 · 51,253,956 / 365,527,824 = 14.02 % · 32 offerings (N77/N83) | identical, byte-for-byte, twice | ✅ exact |
| "still open 23, 청약 ahead 15" (N83, F1) | 23 open; 15 rows print `청약 예정` | ✅ exact |
| gate cost ▷ 49.2억원 = 6.4 % of headline (N76) | report prints ▷ upper bound 767.3억 − 718.1억 = **49.2억** | ✅ exact |
| accuracy 98.6 % strict, over-block 19/19 (N90/N91) | identical from `evalset report` | ✅ exact |
| 16 duplicate `(rcept_no, field_key)` extraction rows (N87); 649 − 16 = 633 deduped | SQL: **16** | ✅ exact |
| 69 증권발행실적보고서 stored (S8) | `select count(*) from performance_report` → **69** | ✅ exact |
| 정정 재추출 backlog = 69 calls (N82) | dry-run: 정정 R1 50ev/**59**call + R3 13ev/**10**call = **69** | ✅ exact |

---

## 2. Judgement against the objective and `intent.md`

| `intent.md` deliverable | verdict | evidence |
|---|---|---|
| 1. Collection pipeline — scheduled, 정정-aware, snapshot-based | **✓** | `collect → bodydoc → extract → gates` on Celery beat (07:30/19:30 KST + Sunday 90-day), one `mijual:lock:pipeline` on every corpus-writing entry point, event key `(corp_code, report_subtype, original_rcept_dt)` with every `rcept_no` a version and every version snapshotted; 정정 discovery windowed on the **original** date (N3), pairing = nearest-earlier-original + the 본문 `최초제출일` verdict. F1 turned the 2026 ①/③ corpus into a swept census (244 of 2,279 filings had been missed; 0 unstored after). |
| 2. Schema-based LLM extraction for the unstructured fields | **✓** | `mijual.extract` reads exactly the §7 ten prose targets, one call per document (N36), value **plus a verbatim quote** whose span *this package* locates (never the model). Corpus-wide the quotes land: **0** rows are `span_unresolved` outside the 5 the gate blocks. 정정 재추출 + Python-side value diff + a deterministic check the model cannot game. |
| 3. Deterministic gates, reason codes, failed-never-exposed | **✓ verified on data** | Four-state verdict (`passed`/`tbd`/`failed`/`not_evaluable`), a skipped check never a pass. Re-derived read-only over all 630 judged events: **409 renderable fields, 0 outside `passed`/`tbd`; 0 `tbd` fields leaking a value; 0 exposable events in a non-exposable state.** All 금액/D-day arithmetic sits in `mijual.calc` with no LLM and no clock unless passed. |
| 4. 2026 소멸 신주인수권 가치 총액 | **✓** | ▷ **718.1억원** (band ▷ 549억~718억), 32 offerings framed on the 증권발행실적보고서 (N72 — the correction that matters), 소멸 증서 = 발행 − 청약 (N68), 확정발행가 agreeing across two independently filed documents 31/31, regenerable at 0 requests / 0 calls. |
| 5. ~100-filing evalset + per-field precision & gate-block rate | **✓, with the provenance qualifier** | 99 filings / 344 rows, frozen sample, both error directions measured (precision **and** over-blocking — the discipline that stops a gate buying precision by blocking more), 95 % Wilson intervals, rates computed only on the random draw. Provenance is Claude-judged cross-model, stated in `LABELING.md`, `result.md` and `phase.md` — **and misstated in the CLI, which is finding 1.** |

### Binding constraints

- **No OpenDART call in a request path — ✓ structurally.** P2 wrote no HTTP layer by design (N1), and the surface P3 will read (`gates.exposure`, `mijual.calc`, the persisted `Event.exposure_state`) imports no DART client at all.
- **Anything deterministically readable is not paid for with an LLM call — ✓.** ② needs zero LLM for its countdown; the whole 증권발행실적보고서 layer spent **0 calls**; the 본문-label tier never reaches the extractor (a test asserts the registries stay disjoint).
- **Secrets — ✓ clean.** 0 hits across every tracked file and every evalset artifact; the key touches only the live request URL, never a filename, a recorded `_url` or an exception.
- **금지선 — ✓ clean.** No fine-tuning/PyTorch/HF framing anywhere; the only matches are the rule being restated.
- **Evidence tags — ✓.** Costs, the 소멸 headline, the band and every model-derived generalisation carry `▷`; measured counts do not. Two habits worth naming as exemplary: the 철회 detector's 71 % keyword false-positive rate was *measured* before the rule was trusted, and every 철회 count is quoted with the document coverage it was measured at (N55).

---

## 3. Findings

### Blocking

**1. `python -m mijual.evalset --help` tells the operator the evalset is "hand-labelled".**
`src/mijual/evalset/__main__.py:1` is the argparse `description` (`description=__doc__`, line 44), so
the false claim is *printed output*, not an internal comment:

```
CLI for the hand-labelled evalset — 0 OpenDART requests, 0 LLM calls.
```

`src/mijual/evalset/__init__.py:1` opens `"""``mijual.evalset`` — the hand-labelled accuracy
measurement (P2.S9).` and its body describes "a sheet the operator labels by hand". Since the
operator's 2026-08-20 amendment the 344 labels are **Claude-judged**, and N89 states that **nothing
in this phase may be described as "hand-labelled"**. `P2.S9` correctly fixed this exact class of
wording in the *generated report* (`사람이` → `판정자가`) and missed the module level. Everything
else — `LABELING.md`'s footer, `result.md`, `phase.md`, the report itself — is right, which is what
makes this a two-line repair rather than a rewrite.

Why it blocks rather than carries: the review's next act is to freeze a `qa` doc asserting that these
numbers are explicitly *not* human ground truth, while the tool that computes them says the opposite
to anyone who runs `--help`. Consolidating that pair would publish a contradiction.

### Recommended in the same cycle (both already named as fix-slice material by `P2.S9`)

**2. `evalset/labels.json` carries no provenance field.** Verified: its keys are exactly
`{labelled, corrections, source}`. The labels are the one artifact in this repo that **cannot be
regenerated**, and their provenance currently lives only in prose. A `judged_by` field written by
`import` (and echoed by `status` / `report`) makes it travel with the data. (N93c.)

**3. `check_against_items` understates a number the docs are about to freeze.**
`src/mijual/extract/runner.py:464-475` — the value-fallback arm (`new_key in item["after"]`) is
evaluated per item *inside* the item-name loop and nothing stops several changes binding to one item,
so a filing that corrects many rows to the identical string (에이전트AI `20260619000455`, five rows to
`-(추후 확정)`) counts covered rows as `uncovered`. Stored recall reads **85.3 %** where a one-to-one,
name-first matcher gives **88.7 %** (3 records affected, 0 unsupported either way). It only ever
understates, so nothing published is false — but the re-check runs over *stored* records at **0 LLM
calls and 0 OpenDART requests**, so freezing a floor the repo knows is low is the more expensive
choice. (N92.)

### Carry forward — recorded, bounded, not blocking

**4. Two `rcept_no` render on two exposable events each.** Measured today: 840 of the corpus's
`rcept_no` sit under 2+ event keys and exactly **2** reach two *exposable* events — 코이즈
`20260122000058` (`piicDecsn/2022-10-13` + `/2025-09-15`) and ②'s 사토시홀딩스 `20251219000402`. N81
called this to the row; `hint_duplicate` is deliberately outside N48's blocking set because the
field-level repair N63 argues for is the same decision and needs its own measurement pass.
**Recommendation: add the exposure-duplicate trigger to `D2` rather than cut a fix slice** — 2 rows of
488 events, and P3's event page is where it becomes visible.

**5. The multi-addend citation defect (3 of 344 strict misses).** SKC `20260522000297` ×2 and
에스에너지 `20260312000380`: the value is a *correct* sum of two table rows (예탁결제원 청약 + 직접청약)
and the citation points at one addend. Summing is the right behaviour — not summing would under-report
청약 and over-report 실권주 — so the defect is the citation contract, not the reading. ▷ ~3 of the
corpus's 31 실적 filings carry the split-row form. **Recommendation: a `defer-job` for multi-span
citation (or "sum of N cited rows"), triggered when P3 renders the 실적 figures.**

**6. The 정정 재추출 backlog will be drained by the beat — at the HIGH preset, unattended.** N82's
claim checks out exactly: today's dry-run prices it at **69 calls (59 ① + 10 ③)** against
`extract_max_calls = 60` per run, so two scheduled runs clear it. But
`THINKING_BY_TASK['correction'] = INHERIT_PRESET`, so **an unattended run makes the thinking-level
decision N82 asks a human to make.** Harmless today (no worker runs unattended), a real cost decision
before P3 deploys one. **Recommendation: decide the level — or cap `correction` at `LOW` and re-measure
N41's 121-changes/0-unsupported quality there — before a worker runs in production.**

**7. ③'s 44 % gate-block rate is version scoping, and must be documented as such.** Of the 11 blocked
`dissent_notice_procedure` rows: **8 `superseded_api_reference`**, 1 `api_deadline_absent`, 1
`field_absent`, and exactly **1** real `dissent_period_mismatch`. N85's "mostly N46's version-scoping,
not a reading failure" is accurate to the row. Any doc quoting 44 % without that split reads as "③ is
badly extracted", which the data does not say.

**8. Mid-phase result figures are superseded and must not reach a doc.** S5's 275/4/5/20-over-304,
S7's 457/280 board and S8's "18 open / 11 청약 ahead" were honest when written and F1 restated each
delta. The consolidation figures are pinned in **N97**.

### Observation, not a finding

`works/phases/active/P2/phase.json` still reads `"status": "planned"` with eleven slices `done`.
`validate` tolerates it and `review-phase` will transition it; noted only so the orchestrator is not
surprised.

---

## 4. Proposed fix slices

| id | name | kind | risk | why that risk | blocking? |
|---|---|---|---|---|---|
| `P2.F2` | Correct the "hand-labelled" provenance wording in `mijual.evalset` (`__init__.py`, `__main__.py`) so `--help` and the module docstring state the true judge-neutral provenance | `fix` | **low** | two docstrings, no behaviour, no test change — the `mid` tier's exact shape | **yes** |
| `P2.F3` | Record label provenance in `labels.json` (`judged_by`) and surface it in `status` / `report` | `fix` | **high** | real code across `labels.py` + the CLI/report + a test — more than one file | no |
| `P2.F4` | Fix `check_against_items` (name-first, one-to-one), re-run the deterministic check over the stored corpus, re-freeze the recall number | `fix` | **high** | logic change plus a corpus re-derivation; **0 LLM calls, 0 OpenDART requests** | no |

Only **`P2.F2`** is required for a pass. `P2.F3`/`P2.F4` are the orchestrator's call — land them now
while the context is hot, or file them as deferred jobs beside `D1`–`D3`; either is defensible, and
`P2.F4` is the one whose absence a durable doc would notice.

---

## 5. Docs — deliberately not consolidated

`doc_versions: none`. A non-pass stops before consolidation, so **no `doc-new-version` was run and
`docs/current/*.md` is untouched** (still `data` v0002 / `operations` v0002 / `decisions` v0002 from
`P1.REVIEW`, everything else at v0001).

The Doc impact list was still audited, and it is **complete** — every durable-truth change P2 made
carries a note, grouping cleanly onto six docs:

| doc | what the consolidated version owes | notes behind it |
|---|---|---|
| `architecture` | the whole data-backbone stack: plain Python package → Postgres/SQLAlchemy, Celery beat + Redis, FastAPI deferred to P3; the `corp → event → filing_version → snapshot` schema; the `collect → bodydoc → extract → gates` topology; no Alembic + `ensure_columns` | S1/S2/S3/S4/S5/S6 running note |
| `data` | the three-tier field model as *measured* (94/94 at 10/10 labels, spans 23,493/23,493), the 유상증자결정 **form family**, `<CORRECTION>` hint at 98.3 %, the 정정 pairing pair `(pairing_method, hint_status)`, the non-injective event key, 철회 / `추후결정` as first-class states, ②'s API-completeness exposure test, the 증권발행실적보고서 + `pifricDecsn` families, the exposure contract | S2–S9 + F1 |
| `operations` | request ceilings and the 20,000/day quota, the beat schedule and per-stage budgets, the one lock, the broker-free `once` fallback, "a corpus is not a census — run both sweeps", the cheap free gap check | S2/S3/S6/S8/F1 |
| `decisions` | O-4/O-5/O-8/O-9 closed, D-4 concretised then amended (per-task thinking level), the conservative-default pair, and the **operator's evalset amendment** (cross-model judging) | S3/S5/S7/S9 |
| `product` | ▷ 718.1억원 and its band, 14.02 %, the largest single loss, the live pipeline, and the gate's measured price (▷ 49.2억원 = 6.4 %) | S5/S7/S8/F1 |
| `qa` | the measurement method (both error directions, frozen sample, Wilson, random-only rates) and the first measured numbers **with their cross-model provenance** | S9 A + B |

Two instructions for the consolidating pass, recorded in `phase.md` beside the list: quote **N97's**
figures, and never write "hand-labelled".

---

## 6. Deviations from `plan.md`

None. Step 5 (doc consolidation) was skipped **because** step 6's verdict is a non-pass, which is what
the plan and the workspace contract require. Budget honoured with room to spare: **0 of ≤ 30 OpenDART
requests, 0 LLM calls.** No source file was edited, no commit and no state transition was made — the
only files this slice wrote are `phase.md` (findings N94–N98 + the Doc impact pointer) and this
`result.md`.

---

## 7. Explain

`not written — run /explain for this phase.` Explaining is a separate, operator-invoked operation; the
review never runs it.

---
---

# Re-review — cycle 2 (2026-08-20, after `P2.F2`/`F3`/`F4`)

**Verdict: `pass`.** The blocking finding is closed at the surface it was found on, both recommended
fixes landed, the phase re-validates as a whole, and the Doc impact list is now **consolidated into
six doc versions**. Cycle 1's history above is unchanged — this section is the second cycle only.

Spend for this cycle: **0 OpenDART requests, 0 LLM calls, 0 source edits, 0 commits, 0 state
transitions.** The docker Postgres corpus was read and deterministically re-derived (`gates run`),
never reset.

## 8. The three fixes, verified against the original findings

| finding (cycle 1) | fix | verification run today | result |
|---|---|---|---|
| **1 (blocking)** — `--help` calls the evalset "hand-labelled" | `P2.F2` | `.venv/bin/python -m mijual.evalset --help` | **CLOSED** — prints `CLI for the labelled evalset (judge recorded per round) — 0 OpenDART requests, 0 LLM calls.` |
| | | `grep -rniE "hand.?labell?ed\|labels? by hand\|operator labels"` over `src tests docs works evalset scripts` | **no description of this evalset as hand-made survives**; every hit is the rule being restated (N89/N95, F2/F3 results, `intent.md`'s original verbatim, and `decisions` v0003's line *forbidding* the phrase) |
| **2** — `labels.json` carries no provenance | `P2.F3` | `labels.json` keys = `{corrections, judged_by, labelled, source}`; 344 labels, 339 `correct` / 5 `partial` / 0 `wrong` | **CLOSED** — `judged_by = {judge: "Claude (Opus 5) … cross-model vs gemini-3.7-flash 추출", basis: "운영자 지시 2026-08-20 … 사람의 정답(ground truth) 아님; 사람이 검증한 라벨 0건", imported_at: "2026-08-20T04:37:31+09:00"}` |
| | | `evalset report` header | prints `- 판정 출처: **Claude (Opus 5) …** · 근거: … · 기록 …` — read off the artifact, not hardcoded (`report.py::_provenance`) |
| | | `import` with no flag → **exit 2**, nothing written; `--judged-by '   '` → `REFUSED / provenance: --judged-by is empty`, **exit 1**, no file created | the guarantee is structural, not advisory |
| **3** — `check_against_items` understates recall | `P2.F4` | `.venv/bin/python -m mijual.extract --dry-run recheck` | **CLOSED** — 48 stored / 45 with parsed rows, **177 rows, uncovered 20 → 20, recall 88.70 % → 88.70 %, unsupported 0 → 0, `rewritten: 0`** (idempotent; the corpus already carries the fixed score) |
| | | `.venv/bin/python -m mijual.evalset refresh-recall` | `unchanged — nothing written`; `git status evalset/` clean |
| | | `evalset report` recall line | `결정론적 정정사항 177행 중 모델이 언급하지 않은 행 20 → 재현율 88.7% (45 건)` — consistent with the stored records and with N100 |

**The number is consistent everywhere it appears**: stored records (`recheck`), the frozen sample
(`refresh-recall`), the rendered report, `phase.md` N100, and now `qa` v0002 / `data` v0003. Nothing
still quotes 85.31 %.

## 9. Phase validation, re-run whole

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **PASS — 59 passed** (56 at cycle 1 + F3's 1 + F4's 2), 0.73 s |
| `python3 scripts/workflow.py validate` | **PASS — `Workflow validation passed.`** |
| `.venv/bin/python -m mijual.gates run` ×2 | **PASS — byte-identical**; **649 field rows — 566 passed / 4 tbd / 14 failed / 65 not_evaluable** (N97 to the row) |
| `.venv/bin/python -m mijual.gates summary` | **PASS — 488 exposable events (① 50, ② 422, ③ 16)**; renderable fields sum to **409** |
| `.venv/bin/python -m mijual.estimate report --today 20260820` ×2 | **PASS — byte-identical**; ▷ **718.1억원** (band lower ▷ 548.7억), 32 offerings, 51,253,956 / 365,527,824 = **14.02 %**, **23 still open / 15 청약 예정**, ▷ upper bound 767.3억 → gate cost ▷ **49.2억 = 6.4 %** |
| `.venv/bin/python -m mijual.evalset report` | **PASS — 98.6 % strict (213/216, 95 % CI [96–100 %])**, lenient 100 %, over-block **100 % (19/19** random; 48/48 pooled**)**, recall 88.7 %, 판정 출처 line present |
| `.venv/bin/python -m mijual.scheduler once --offline` | **PASS** — four stages green, `passed 566 tbd 4 failed 14 n/a 65`, 488 exposable / 409 renderable, **0 requests / 0 calls / ▷ $0.0000**, 33.8 s |
| SQL re-derivation for the docs (read-only) | 633 distinct `(rcept_no, field_key)` rows, **77 blocked = 12.2 %**; 1,345 events / 3,990 versions / 7,076 snapshots / 69 실적보고서; `extraction_call` **213 calls, 2,025,260 tokens, ▷ $2.79, 0 failures**, newest 2026-08-19 17:52 UTC |
| secret scan (both `.env` values × `src tests evalset docs works scripts`, incl. the new doc versions) | **PASS — 0 hits** |
| 금지선 grep (`fine-tun`, `pytorch`, `huggingface`, `파인튜닝`) | **PASS** — the only hit in the doc set is `architecture` restating the rule |
| request-path check (`grep -rn DartClient src/mijual`) | **PASS** — no DART import under `gates/`, `calc.py`, `db/models.py` |

`extraction_call`'s newest row predates both review cycles, which is the machine-checkable form of
"the review spent nothing".

## 10. Carry-forwards 4–8, confirmed in place

| # | item | where it lives now |
|---|---|---|
| 4 | 2 `rcept_no` on two exposable events each | **`D2` brief**, "Additional trigger (P2.REVIEW carry-forward, 2026-08-20)" naming 코이즈 `20260122000058` and 사토시홀딩스 `20251219000402` — verified present |
| 5 | multi-addend citation defect (3 of 344 strict misses) | **`D4`** — `works/deferred/open/D4/`, trigger "when P3 renders 실적보고서 figures with citations" — verified present, and now also in `qa`'s fragile-areas table |
| 6 | 정정 재추출 backlog drained by the beat at the inherited thinking level | **N98(c)**, and now **`operations`** ("Open operational decision before a worker runs unattended") + **`decisions` D-4** |
| 7 | ③'s 44 % block rate is version scoping | **N98(b)**, and now **`qa`** with the 8/1/1/1 split stated as mandatory whenever the 44 % is quoted |
| 8 | mid-phase figures superseded | **N97**, honoured by every doc version written below |

No new work was done on any of them, as the re-review plan requires.

## 11. Docs — consolidated (six versions)

`rebuild-docs` ran; `docs/current/*.md` regenerated from the new latest versions; `validate` clean
afterwards. **No `docs/current/*.md` file was hand-edited and no existing version was patched.**

| doc | new version | what it carries |
|---|---|---|
| `architecture` | **v0002** `data_backbone_landed_package_postgres_schema_celery_beat_topology_and_the_p2_to_p3_exposure_boundary` | the stack (package → Postgres/SQLAlchemy, Celery beat + Redis, FastAPI deferred to P3), the module map, the `corp → event → filing_version → snapshot` schema + `extraction*` / `performance_report`, no-Alembic + `ensure_columns`, the `collect → bodydoc → extract → gates` topology, and the P2→P3 exposure boundary |
| `data` | **v0003** `p2_pipeline_data_model_document_families_measured_field_tiers_pairing_event_states_and_the_exposure_contract` | the three-tier model as *measured* (94/94 labels, 23,493/23,493 spans), the 유상증자결정 **form family**, `pifricDecsn` + 증권발행실적보고서, the two-arm 정정 pairing and the non-injective key, 철회 / `추후결정` as first-class states, the ten gates as implemented (#2 ordering, #5 window, #8 derived), the exposure contract, the 소멸가치 method, and the 88.70 % recall |
| `operations` | **v0003** `pipeline_operations_quota_and_request_ceilings_beat_schedule_and_budgets_the_pipeline_lock_and_how_to_regenerate_every_artifact_at_zero_spend` | the 20,000/day quota + request ceilings, the beat schedule and per-stage budgets, the single `mijual:lock:pipeline`, the broker-free `once` fallback, "a corpus is not a census" + the free gap check, the zero-spend regeneration commands — with P1's submission/결격/timeline truth kept intact below it |
| `decisions` | **v0003** `p2_decisions_data-backbone_stack_per-task_thinking_level_cross-model_evalset_judging_and_the_conservative-default_pair` | D-1…D-5 preserved, **D-4 amended** (per-task thinking level, with the mechanism and the −21 % measurement), **D-6** stack, **D-7** cross-model judging (the operator's verbatim directive), **D-8** the conservative-default pair, and O-1/O-2/O-4/O-5/O-8/O-9 recorded closed |
| `product` | **v0002** `product_truth_after_p2_the_lapsed-warrant_headline_the_live_rights_board_and_the_measured_price_of_the_trust_gate` | ▷ 718.1억원 and its band, 14.02 %, the largest single loss, the live board (488 / 409, ②'s 33-within-30-days), 철회 / 추후결정 / 소규모합병 as product states, and the gate's measured price ▷ 49.2억원 = 6.4 % |
| `qa` | **v0002** `extraction-accuracy_measurement_method_the_frozen_evalset_cross-model_provenance_and_the_first_measured_numbers` | the provenance statement **first**, the method (both error directions, frozen sample, random-only rates, Wilson), the measured numbers, the 44 % split, the 88.70 % recall, the regression checklist (incl. the exposure-invariant re-derivation) and the fragile areas mapped to D1/D2/D4 |

`backend` was folded into `architecture` rather than versioned separately: today the backend *is* this
package, and a second doc would duplicate it. It can be split when P3's HTTP layer exists.

Honesty checks on the written docs: every cost, the 소멸 headline, the band and every generalisation
carry `▷`; measured counts do not. The accuracy numbers carry the cross-model qualifier in `qa`
(first section), `decisions` D-7 and `product`. The string "hand-labelled" appears in the whole doc
set exactly **once** — in `decisions`, as the sentence forbidding it.

## 12. Deviations from `plan.md` (cycle 2)

None. Step 5 ran because step 6's verdict is a pass; `backend` was folded into `architecture`, which
the plan explicitly permits. Budget: **0 of ≤ 30 OpenDART requests, 0 LLM calls.** Files written by
this cycle: the six doc versions, `docs/index.json` + the regenerated `docs/current/*.md`, `phase.md`
(N101–N103 + the Doc impact header), and this `result.md` section. No source file was touched, no
commit and no state transition was made.

## 13. Explain (cycle 2)

`not written — run /explain for this phase.`
