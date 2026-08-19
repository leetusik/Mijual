# Result: P2.F4 — the 정정 recall proxy is a measurement again (88.70 %)

_Executed 2026-08-20 by `slice-executor-high` (Claude, Opus 5). **0 LLM calls, 0 OpenDART
requests.** No commit, no state transition, no `doc-new-version`._

## What the defect actually was, and what it was not

`check_against_items` scored each model change against the deterministic `3. 정정사항` rows by
walking the rows and taking the **first** one that matched either arm — the item name, or (the
fallback) the change's new value inside the row's `after` cell. Nothing stopped several changes
from taking the **same** row. A filing that corrects many rows to one identical string —
에이전트AI `20260619000455` moves five schedule rows to `-(추후 확정)` — therefore had every change
bind to row 0, and four genuinely covered rows were counted `uncovered`.

So the number the repo had been quoting was a scoring artifact, not a model regression: the
model's changes were right, the arithmetic over them was wrong, and it could only ever
**understate** recall.

## The fix (`src/mijual/extract/runner.py`)

Matching is now **one-to-one**, with the item name as the primary key:

1. `_candidate_items` splits each change's candidate rows into the **name** arm and the **value**
   arm. The two predicates are byte-for-byte the old ones and are still evaluated per row in the
   same order.
2. `_assign_one_to_one` settles the name arm first (augmenting-path matching *within* that arm, so
   an unlucky order cannot strand a matchable row), then lets the value arm fill what is left. A
   value match can never displace a name match, so `deterministic_item` still points at the row a
   change actually names. Each row is claimed at most once, because recall counts **rows**.
3. A change whose every candidate row is held by another change stays `supported` — the table does
   back it — and simply adds no coverage.

**The invariant that made re-scoring stored evidence safe:** because the per-row predicate is
unchanged and only the *assignment* changed, a change is supported now **iff** it was supported
before. `unsupported` is therefore invariant by construction, which is why no gate verdict and no
exposure state could move (both key on `unsupported`, never on `uncovered`). Verified per record,
not just argued — see the audit below.

Output shape is unchanged (`items` / `changes` / `unsupported` / `uncovered` + the per-change
`supported` / `deterministic_item`), so stored records stay comparable with the ones S4 wrote.

## Re-scoring the stored corpus — `python -m mijual.extract recheck`

`deterministic_check` is **derived** data: a pure function of the stored 정정사항 rows and the
model changes stored beside them. So it is re-scored from what is already in Postgres, exactly as
`relocate` re-derives spans without re-paying for the quote (N37). New command, same shape as
`relocate`; the global `--dry-run` (before the subcommand) measures and writes nothing.

```
task       : recheck (deterministic re-match of stored 정정 해석)
records    : 48 stored, 45 with parsed 정정사항 rows (3 without — excluded, N86)
rows       : 177 deterministic 정정사항 row(s), 157 model change(s)
uncovered  : 26 -> 20  |  recall 85.31% -> 88.70%
unsupported: 0 -> 0
rewritten  : 3 record(s)
  20260619000455 uncovered 5 -> 1
  20251204000439 uncovered 1 -> 0
  20250925000611 uncovered 1 -> 0
```

Exactly the three records N92 predicted, and no others. The second run reports `rewritten: 0`.

### Evidence audit — what moved and what did not

All 48 stored `correction_interpretation` records were dumped **before** the write and compared
against the database after it:

| checked | outcome |
|---|---|
| `quote`, `span_start`/`span_end` | identical on all 48 |
| `interpretation` body (summary, per-change `item`/`new`/`quote`/`kind`/spans), `deterministic_items`, `field_moves`, `old_rcept_no`/`new_rcept_no` | identical on all 48 |
| every change's `supported` flag | identical on all 48 (the invariant, measured) |
| per-record `items`, `changes`, `unsupported` | identical on all 48 |
| `deterministic_check.uncovered` | moved on **3** records (5→1, 1→0, 1→0) |
| `deterministic_item` | reassigned on **6** changes |

Nothing the model produced was touched, nothing was re-extracted, no snapshot was re-collected.

## Re-freezing the number in the two places it is also stored

**(a) The gate note embeds it.** `gate_correction_interpretation` prints
`changes_supported=ok(N건 전부 근거 있음, 미언급 M행)` into `gate_note`, so three notes disagreed
with their own record after the re-score. `python -m mijual.gates run` (deterministic, 0 calls /
0 requests) refreshed them; the verdict distribution is **unchanged**:

- **649 field rows — 566 passed / 4 tbd / 14 failed / 65 not_evaluable** (N97's figures, to the row)
- **488 exposable events**, `gates summary` output **byte-identical** before vs after
- two consecutive `gates run` invocations byte-identical to each other

**(b) The frozen evalset sample carries a copy.** `python -m mijual.evalset report` reads two JSON
files and never the database (deliberately — a label is only true about the reading it was made
on), so the recall line is printed from `evalset/sample.json`'s `correction_recall` block, which
was still `85.31 %`. That block is the one figure on the sheet **no label feeds**, so it is
re-frozen by a new, narrow command rather than by redrawing the sample:

```
$ .venv/bin/python -m mijual.evalset refresh-recall
stored     : 177 row(s), uncovered 26, unsupported 0/157 → 재현율 85.31% (45 건)
corpus     : 177 row(s), uncovered 20, unsupported 0/157 → 재현율 88.70% (45 건)
sample     : …/evalset/sample.json — correction_recall re-frozen (344 row(s) and every label key untouched)
```

`git diff evalset/sample.json` is **2 lines** (`uncovered` and `recall`); `rows`, `seed`,
`generated_at`, `strata`, `field_stats` are untouched, so every `row_id` a label was made against
still means the same reading. `evalset/sheet.csv` and `evalset/labels.json` were never opened
(confirmed by `git status`). A second run prints `unchanged — nothing written`.

Report after the refresh — the recall line moves, every accuracy figure stays:

- `- 결정론적 정정사항 177행 중 모델이 언급하지 않은 행 20 → 재현율 88.7% (45 건)` (was `26 … 85.3%`)
- `- 표가 뒷받침하지 않는 모델 변경(unsupported): 0 / 157` — unchanged
- 정밀도 **98.6 % (213/216, 95 % CI [96–100 %])**, partial 포함 100 %, 과차단 **100 % (19/19)**,
  판정 출처 block — all unchanged

## Tests (`tests/test_extract.py`, +2, suite 57 → 59)

- `test_changes_corrected_to_the_same_string_consume_different_rows` — the multi-bind trap: three
  rows all corrected to `-(추후 확정)`, one change naming its row and two reachable only through the
  value arm; the three must consume three distinct rows (`uncovered: 0`) and the named change must
  keep its own row.
- `test_recheck_rescores_stored_records_and_a_second_run_is_a_no_op` — a stored record carrying the
  old matcher's output (both changes bound to row 0) is re-scored to `uncovered: 0`, the second run
  rewrites nothing, and the quote, summary, per-change quotes and `deterministic_items` are asserted
  unchanged. SQLite in-memory, the file's existing fixture style.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **59 passed** (57 before + 2) — PASS |
| `.venv/bin/python -m mijual.extract --dry-run recheck` (before any write) | 26 → 20 uncovered, 85.31 % → 88.70 %, unsupported 0 → 0, 3 records, **nothing written** — PASS |
| `.venv/bin/python -m mijual.extract recheck` | `rewritten: 3` — PASS |
| `.venv/bin/python -m mijual.extract recheck` (×2, ×3) | `rewritten: 0`, two runs **byte-identical** — PASS (idempotent) |
| 48-record before/after evidence audit (script, read-only) | quotes / spans / values / model notes / `supported` / `items` / `changes` / `unsupported` **identical**; only 3 `uncovered` + 6 `deterministic_item` moved — PASS |
| `.venv/bin/python -m mijual.gates run` ×2 | **566 passed / 4 tbd / 14 failed / 65 not_evaluable over 649 rows**, 488 exposable events, two runs byte-identical — PASS (N97 unchanged) |
| `.venv/bin/python -m mijual.gates summary` before vs after | **no diff** — PASS |
| `.venv/bin/python -m mijual.evalset refresh-recall` ×2 | 85.31 % → 88.70 %, then `unchanged — nothing written`; `sample.json` diff = **2 lines** — PASS |
| `.venv/bin/python -m mijual.evalset report` | 재현율 **88.7 %** (was 85.3 %); 98.6 % / 213/216 / 19/19 / 판정 출처 unchanged; labels untouched — PASS |
| `.venv/bin/python -m mijual.extract summary` | `48 interpretation(s)` · `정정사항 rows 177 (uncovered 20)` · `model changes 162 (unsupported 5)` — the naive aggregate (N86's trap: the 5 come from the 3 unparsed-table records), consistent |
| spend | `extraction_call` rows **213**, newest `2026-08-19 17:52 UTC` (before this slice); `var/` untouched; no `GeminiClient`/`DartClient` is constructed on any path run — **0 LLM calls, 0 OpenDART requests** |
| secret scan (both `.env` values × the 7 touched files) | **0 hits** |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

**Old → new, stated once:** corpus 정정-해석 recall proxy **85.31 % → 88.70 %** (177 deterministic
정정사항 rows, 26 → 20 uncovered, 45 records with a parsed table; **0 unsupported of 157 model
changes both ways**). Regenerate with `.venv/bin/python -m mijual.extract recheck` (0 calls,
0 requests) and read it back with `.venv/bin/python -m mijual.evalset report`.

## Files changed

- `src/mijual/extract/runner.py` — one-to-one name-first matcher (`_candidate_items`,
  `_assign_one_to_one`, `check_against_items`), plus `RecheckReport` + `recheck_corrections`
- `src/mijual/extract/__main__.py` — `recheck` subcommand (0 calls; global `--dry-run` measures)
- `src/mijual/evalset/sample.py` — `_correction_recall` → public `correction_recall` (+ why)
- `src/mijual/evalset/__main__.py` — `refresh-recall` subcommand
- `tests/test_extract.py` — 2 tests
- `evalset/sample.json` — 2 lines: the `correction_recall` block re-frozen
- `works/phases/active/P2/phase.md` — N100 + one Doc impact entry

## Deviations from `plan.md`

1. **The evalset report does not read the stored records** — it reads the frozen
   `evalset/sample.json` (its module docstring makes that a design property: "no database in the
   read-back path"). The plan's step 3 anticipated this with "(if it reads the stored records)",
   but leaving it there would have left the repo's only accuracy artifact printing a figure it
   knows is wrong. So the slice added the narrow `refresh-recall` command instead of stopping at a
   finding: it rewrites that one derived block and nothing else, and the sample/label alignment the
   freeze exists to protect is preserved and verified (2-line diff, labels never opened).
2. **`python -m mijual.gates run` was re-run**, which the plan does not mention. `gate_note` embeds
   the `uncovered` count verbatim, so three notes were left stale by the re-score. Same class of
   work (derived evidence, 0 calls / 0 requests, deterministic) and it doubles as the proof that the
   `unsupported` invariant holds end-to-end: verdicts and exposure came back identical.
3. **`--dry-run` is the existing global flag**, so it goes **before** the subcommand
   (`-m mijual.extract --dry-run recheck`) rather than after it; no new flag was added.

Nothing else departed from the plan: no prompt/schema change, no relabelling, no LLM call, no
OpenDART request, no commit, no status transition, no `doc-new-version`.
