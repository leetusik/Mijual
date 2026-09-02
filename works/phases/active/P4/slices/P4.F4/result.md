# P4.F4 — result (dispatch 1 of 2)

- **status**: `needs_operator`
- **summary**: Added the `MIJUAL_EXTRACT_MAX_CALLS` env knob — read by `Settings`, applied to every
  beat/Celery run through `PipelineConfig.from_kwargs()` and to `once` unless `--max-calls` is typed,
  with the dataclass default unchanged at 60 — plus one test, the `.env.prod.example` entry, and the
  single `MIJUAL_EXTRACT_MAX_CALLS=300` line appended to `/home/opc/Mijual/.env.prod` (mode 600
  preserved, inert until the containers are recreated). Nothing was deployed and nothing on the box
  was restarted. The slice now stops for the operator's `git push origin main`; dispatch 2 deploys
  and drains.
- **files_changed**:
  - `/Users/sugang/projects/personal/Mijual/src/mijual/config.py`
  - `/Users/sugang/projects/personal/Mijual/src/mijual/scheduler/config.py`
  - `/Users/sugang/projects/personal/Mijual/src/mijual/scheduler/__main__.py`
  - `/Users/sugang/projects/personal/Mijual/tests/test_scheduler.py`
  - `/Users/sugang/projects/personal/Mijual/.env.prod.example`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/slices/P4.F4/result.md`
  - (on the box, not in the repo) `/home/opc/Mijual/.env.prod` — three appended lines
- **validation**: see § *Validation* — `uv run pytest -q` **167 passed, exit 0**;
  `python3 -m py_compile` on the four touched files clean; `once --help` shows the new default
  wording; the offline proof run prints `extract<=300 calls`; `python3 scripts/workflow.py validate`
  passed; `git diff --stat` is exactly the six repo files above.
- **deviations**: three, all small — see § *Deviations*.
- **doc_impact**: two lines appended to `phase.md`'s `## Doc impact` —
  `operations` (Environment Variables: the new key, default 60, production 300, the ~$3 bound, and
  that a malformed value is fatal rather than ignored) and `backend` (Background Jobs: the extract
  ceiling is env-overridable, all three beat entries inherit it through `from_kwargs`,
  `once --max-calls` wins per run, `DEFAULT_EXTRACT_MAX_CALLS` / `env_extract_max_calls()`).
- **operator_need**: **push `main` to GitHub — `git push origin main`** (after the orchestrator
  commits this slice). The box deploys `origin/main`, and neither the orchestrator nor an executor
  pushes. Dispatch 2 then runs `deploy/deploy.sh` on the box and a first drain run. **It must land
  before the deploy freeze opens 2026-09-07 11:00 KST.**

---

## What changed, and why there

The ceiling was `PipelineConfig.extract_max_calls = 60`, a dataclass default no env var could reach.
Three edits, smallest coherent diff:

1. **`src/mijual/config.py`** — `Settings.extract_max_calls: int | None = None`, read in
   `load_settings()` through the existing `pick()` (environment first, then the repo-root `.env`) and
   parsed by a new `_positive_int(name, raw)` helper. The helper raises `ValueError` naming **the key
   and never the value**, and deliberately does not chain the built-in `int()` error, because that
   one quotes the offending literal.
2. **`src/mijual/scheduler/config.py`** — the literal `60` became `DEFAULT_EXTRACT_MAX_CALLS` (same
   value, one spelling), and a new `env_extract_max_calls()` is **the one reader** both consumers
   use. `PipelineConfig.from_kwargs()` applies it when the kwargs carry no `extract_max_calls` key —
   that is the beat/Celery path, and no beat entry names a ceiling — so all three `daily_pipeline`
   entries (07:30, 19:30, Sun 04:30) inherit it while an entry that names one keeps it.
3. **`src/mijual/scheduler/__main__.py`** — `--max-calls` now defaults to `None` (so "typed 60" and
   "typed nothing" are distinguishable) and `_config()` resolves
   `--max-calls` → `$MIJUAL_EXTRACT_MAX_CALLS` → `60`. Help text updated.

The dataclass default stays **60**, so offline tests, fixtures and the module's own reasoning are
unaffected by the environment; unset behaves exactly as it did yesterday.

### The one deliberate departure from this codebase's convention

`MIJUAL_STALE_AFTER_HOURS` and `SMTP_PORT` both **ignore** a malformed value, with the reason in a
comment ("a mistyped ops env var must not take the board down"). This key does not: it raises. The
plan asked for that, and it is right for this key specifically — it is a **spend ceiling**, and
falling back to 60 would run a whole schedule at a budget the operator believes they raised. The
blast radius is accepted knowingly and recorded in `phase.md`'s `## Decisions`: a bad value stops
api/worker/beat at startup, which `deploy/deploy.sh`'s health gate turns into an automatic rollback.
An **empty** value is "unset" (that is `pick()`'s rule for every key), not an error — measured below.

## Validation

| Command | Outcome |
|---|---|
| `python3 -m py_compile src/mijual/config.py src/mijual/scheduler/config.py src/mijual/scheduler/__main__.py tests/test_scheduler.py` | clean |
| `uv run pytest -q` | **167 passed**, exit 0 (72+72+23), no `--with` |
| `uv run python -m mijual.scheduler once --help` | `--max-calls` reads *"LLM call ceiling for the run (default: $MIJUAL_EXTRACT_MAX_CALLS if the environment sets one, else 60); an explicit value here wins over the environment"* |
| `MIJUAL_EXTRACT_MAX_CALLS=300 uv run python -m mijual.scheduler once --offline --stages extract --window 14 --label f4-proof --no-run-log --no-lock` | `config : … budgets collect<=500 req, bodydoc<=200 req, **extract<=300 calls** [offline]`, `spend : 0 OpenDART request(s), **0 LLM call(s)**, ▷ $0.0000` |
| `python3 scripts/workflow.py validate` | passed (one pre-existing `oversized_doc_sections=11` warning, not this slice's) |
| `git diff --stat` | the three source files, the test file, `.env.prod.example`, `phase.md` — nothing else |
| `ssh oracle-cloud` verification (below) | `grep -c` = 1, `stat -c %a` = 600 |

### The env matrix, probed directly

Run under `MIJUAL_ROOT` pointed at an empty scratch dir so no repo-root `.env` could interfere:

```
unset    -> 60          # unchanged behaviour
"300"    -> 300         # the beat path takes it
explicit -> 5           # from_kwargs(extract_max_calls=5) keeps 5
"6O" / "0" / "-5" / "60.5" -> ValueError: MIJUAL_EXTRACT_MAX_CALLS must be a positive integer (>= 1)
                          (the offending value appears nowhere in the message)
""       -> 60          # empty == unset, per pick(); not an error
```

### What the dry run says the backlog costs

The offline proof run's extract line is itself evidence for the value 300:

```
extract : [dry-run] label 61row/0call; r1_prose 54ev/0call; r3_prose 18ev/0call;
          정정 R1 50ev/59call; 정정 R3 13ev/10call | 0 live call(s), 0 token(s), ▷ $0.0000
```

**69 정정 calls** (59 + 10) in a 14-day window on the dev corpus — the same number `D40` was filed
with, and above the old 60-call ceiling on its own. 300 is ~4× that, so a run drains rather than
carries, and it bounds one run at roughly $3 (the exhausted 60-call production run cost $0.61 /
466,729 tokens).

## The box

One `ssh oracle-cloud` invocation, additive only, nothing else touched — no `docker` command, no
restart, no deploy, `edge-nginx` never approached, and the file was never `cat`'d:

```
printf '\n# extract ceiling per run (P4.F4, operator 2026-09-02)\nMIJUAL_EXTRACT_MAX_CALLS=300\n' \
  >> /home/opc/Mijual/.env.prod
```

Before: mode `600 opc:opc`, `grep -c '^MIJUAL_EXTRACT_MAX_CALLS='` = **0**, 131 lines.
After: mode `600 opc:opc` (unchanged), `grep -c` = **1** at line **134**, 134 lines (+3: blank,
comment, key). The value is **inert** until the containers are recreated — a running container keeps
the environment it started with — which is dispatch 2's deploy.

## Deviations

1. **The offline proof run added `--no-run-log --no-lock`** to the plan's command. The plan's exact
   form would have written a `pipeline_run` row into the operator's **dev** run log and taken the
   real lock for a slice-internal proof. The flags change nothing about what was being proven (the
   `budgets` line comes from `PipelineConfig.describe()` either way) and leave the dev log untouched.
2. **`DEFAULT_EXTRACT_MAX_CALLS` and `env_extract_max_calls()` were added** rather than repeating the
   literal `60` and the `load_settings()` call in two files. The plan named the two application
   points but not how they share a spelling; one constant and one reader is what keeps the beat path
   and the CLI from ever disagreeing about which value wins.
3. **`.env.prod.example`'s *Optional* block header** said "Both have working defaults" and now says
   "All three" — a one-word correction forced by adding a third key to that block.

Not a deviation but worth stating: the plan's step 5 asked for the D-4 thinking-*level* question to
stay open as `D40`. It is open and untouched; `phase.md`'s `## Operator Questions` records that its
**trigger has fired** and that this slice answers only the ceiling half.

## What dispatch 2 inherits

In `phase.md` under `## Notes for later slices` (**(from P4.F4 dispatch 1, for P4.F4 dispatch 2)**):
the box line is already written and must not be appended twice; both images will genuinely rebuild
because `src/` changed; verify with `printenv` **and** the drain run's `extract<=300 calls` line
(only the second proves the code path took it); expect a low-single-dollar drain; and if it still
reports `BUDGET EXHAUSTED` at 300, report it and stop — the next value is the operator's.
