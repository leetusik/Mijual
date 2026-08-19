# Result: P2.F3 — `judged_by` provenance inside `labels.json`, printed by the report

Review finding 2 (N96a): `evalset/labels.json` is the repository's only non-regenerable artifact,
and until now its provenance lived only in prose beside it. It now travels **inside** the file, the
import path cannot produce an unstamped one, and the report prints what the file says instead of a
sentence written when the labels were made.

## What changed

**1. `src/mijual/evalset/labels.py` — the stamp, and the refusal.**
New frozen `Provenance(judge, basis, imported_at)` with `stamp()` / `as_dict()` / `from_payload()`.
`Labels` gains `provenance: Provenance | None = None`, and **`Labels.write()` raises `LabelError`
when it is `None`** — the guarantee is structural, at the library level, not only in the CLI, so no
future caller can mint an unstamped artifact. `read_sheet_labels(..., provenance=…)` carries the
stamp through; parsing a sheet says nothing about who judged it, so the caller must. `load_labels()`
still reads a pre-provenance file (`provenance is None`) rather than crashing on history —
malformed is a different case and *is* refused (`judged_by` present but not an object with a
non-empty `judge`). `imported_at` is KST, offset-qualified (`mijual.calc.KST`), so the stamp lines
up with the Korean disclosure dates beside it without a mental conversion.

**2. `src/mijual/evalset/__main__.py` — `--judged-by` is required and never inherited.**
`import` takes `--judged-by` (argparse `required=True` → exit 2 on silence, nothing written) and
optional `--basis` (default `기재되지 않음 (unstated)`, i.e. silence yields a *stamped* file that
openly states its basis is missing — never an unstamped one). **Inheriting the previous file's
stamp was considered and deliberately rejected:** the documented human-override path in
`LABELING.md` is "overwrite column A, re-run `import`", and inheritance would have let a human
re-judgement silently keep Claude's stamp — the exact class of false provenance this slice exists
to remove. The cost is retyping one flag; the flag is also where a mixed round gets described
(`--judged-by "혼합 (Claude 판정 후 사람이 12행 재판정)"`). The import prints the judge and basis it
recorded.

**3. `src/mijual/evalset/report.py` — the line comes from the artifact.**
`_provenance(labels)` renders `- 판정 출처: **{judge}** · 근거: {basis} · 기록 {imported_at}` into
the report header, read off `labels.json`. A file with no stamp renders
`**미기재** — labels.json에 판정 출처가 없습니다 (import --judged-by …로 재수입)` — a stated gap, not
a silent one. No provenance string is hardcoded in the renderer, which is the defect N95 found in
the old wording.

**4. Re-stamped the current round** (below) and updated `evalset/LABELING.md`: the command block now
shows the flag, a new paragraph explains why it cannot be inherited, and the existing 출처 footer now
points at the `judged_by` block as the primary carrier with the prose as its echo.

**5. Two wording leftovers of the same defect class, fixed in passing** (see *Deviations*):
`__init__.py`'s body still read "a sheet **the operator labels by hand**" — the exact phrase N95
forbids, which survived because `P2.F2` was scoped to line 1 of the file — and `report.py` twice
described the labeller as "the operator". Both are now judge-neutral. `__init__.py` also documents
the new fourth load-bearing property and exports `Provenance`.

## The re-stamp: every label preserved, verified

`.venv/bin/python -m mijual.evalset import --judged-by '…' --basis '…'` re-read the already-labelled
`evalset/sheet.csv` through the new path.

| check | result |
|---|---|
| labels imported | **344 / 344**, 344 judged, 0 skip, 0 corrected values |
| `labelled` map before vs after | **identical** (dict equality on all 344 entries) |
| `corrections`, `source` | identical |
| keys added | exactly one — `judged_by` |
| `git diff evalset/labels.json` | **+5 lines, 0 deletions** — the block only |
| label distribution | 339 `correct` / 5 `partial` / 0 `wrong` — matches N90 unchanged |
| report numbers after re-stamp | 98.6 % (213/216) strict, CI [96–100 %], over-block 100 % (19/19) — identical to N90 |

Recorded stamp:

```
judge       : Claude (Opus 5) — P2.S9 슬라이스 실행자, cross-model vs gemini-3.7-flash 추출
basis       : 운영자 지시 2026-08-20 ("you self evaluate and self validate…") — 모델 간 교차판정이며
              사람의 정답(ground truth) 아님; 사람이 검증한 라벨 0건
imported_at : 2026-08-20T04:37:31+09:00
```

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **PASS** — 57 passed (56 before; one added) |
| `.venv/bin/python -m mijual.evalset import --judged-by … --basis …` | **PASS** — 344 labels, stamp written |
| `.venv/bin/python -m mijual.evalset report` | **PASS** — prints `- 판정 출처: **Claude (Opus 5) …** · 근거: … · 기록 2026-08-20T04:37:31+09:00`; all rates unchanged |
| `.venv/bin/python -m mijual.evalset status` | **PASS** — 344 / 344 (100 %) |
| `.venv/bin/python -m mijual.evalset import` (no flag) | **PASS (refused as designed)** — argparse error, **exit 2**, nothing written |
| `.venv/bin/python -m mijual.evalset --labels …/nope.json import --judged-by '   '` | **PASS (refused as designed)** — `import : REFUSED / provenance: --judged-by is empty …`, **exit 1**, no file created |
| label-map diff before/after re-stamp | **PASS** — identical, only `judged_by` added |
| `python3 scripts/workflow.py validate` | **PASS** — "Workflow validation passed." |

Spend: **0 LLM calls, 0 OpenDART requests, 0 database writes** — `import` and `report` read
`sample.json` + the sheet and nothing else (only the `sample` subcommand opens a session). No secret
was read, printed, or stored; the provenance strings name models and an operator directive, no
credentials.

The one added test (`tests/test_evalset.py`, one function) covers the whole contract terse-style:
unstamped `write()` refuses and leaves no file, an unstamped file still loads and renders `미기재`,
a stamped file round-trips through `write` → `load_labels` with labels intact and its judge in the
rendered report, and a blank judge raises.

## Deviations from plan.md

1. **`plan.md` assumed `labels.json` already carried an import timestamp** ("…and the import
   timestamp it already has"). It did not — the file held only `{source, labelled, corrections}`.
   `imported_at` is therefore **new**, and is part of the `judged_by` block as the plan's minimum
   requires.
2. **Two docstring leftovers fixed beyond the plan's four work items** (`__init__.py` body's "a
   sheet the operator labels by hand", `report.py`'s two "the operator judge…"). These are N95's
   finding, which `P2.F2` closed only for the two exact strings its plan named; leaving a forbidden
   description in the same module I was editing for provenance honesty would have re-created the
   finding one file over. Wording only — no behaviour change.
3. **`--basis` defaults instead of being required.** The plan left the design to me and required
   only that silence cannot yield an unstamped artifact. Silence on `--judged-by` is a hard refusal;
   silence on `--basis` yields a stamped file whose basis reads `기재되지 않음 (unstated)`, visible
   in the report. Requiring both flags would have added friction to the human-override path without
   adding a guarantee.

Nothing was relabelled, no sampling changed, no sheet evidence column touched. No commit, no state
transition, no `doc-new-version`.

## Doc impact

Two lines appended to `phase.md`: finding **N99** (the artifact is self-describing) and one entry on
the running **Doc impact** list under **`qa`** — the accuracy numbers do not move, so what the `qa`
doc version should gain is *where the cross-model qualifier now lives* (`labels.json`'s `judged_by`
block, printed by the report), not a new figure.
