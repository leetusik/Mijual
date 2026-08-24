# Plan: P2.F2 — reword the evalset docstrings judge-neutrally (blocking review finding 1)

_Mode: auto. Two-line docs fix; risk low → slice-executor-mid._

Since the operator's 2026-08-20 amendment, the evalset labels are Claude-judged (cross-model), and N89 forbids "hand-labelled" phrasing. Two module-level strings still say it, and one of them is printed by `--help`:

1. `src/mijual/evalset/__main__.py:1` — module docstring (used as the argparse `description` at line 44): `CLI for the hand-labelled evalset — 0 OpenDART requests, 0 LLM calls.` → reword judge-neutrally, e.g. `CLI for the labelled evalset (judge recorded per round) — 0 OpenDART requests, 0 LLM calls.` (keep the 0-spend claim).
2. `src/mijual/evalset/__init__.py:1` — docstring opens `` `mijual.evalset` — the hand-labelled accuracy measurement (P2.S9).`` → judge-neutral equivalent (e.g. "the labelled-evalset accuracy measurement").

Change only those strings — no behavior, no other files. Verify: `.venv/bin/python -m mijual.evalset --help` no longer prints "hand-labelled"; `grep -ri "hand.labell\?ed" src/` → 0 hits; `.venv/bin/python -m pytest` green; `python3 scripts/workflow.py validate` passes. Write `result.md`; append nothing to phase.md beyond a one-line note if you judge it needed (the review already recorded the finding). Escalate if the fix turns out to require anything beyond these two strings.
