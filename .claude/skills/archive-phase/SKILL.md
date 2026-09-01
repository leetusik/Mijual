---
name: archive-phase
description: Archive review-passed phases: archive-all (full sweep), rotate-backlog (partial), or archive-phase (single).
allowed-tools: Bash(python3 scripts/workflow.py:*)
disable-model-invocation: true
---

# archive-phase

Archiving is **manual and explicit** — never automatic. A passing review marks a phase `done` but leaves it in `active/`; the **operator** decides when to archive (invoking this skill is that decision — never archive unasked). Archive whole phases only, never individual slices. Three first-class options:

**Archive everything — end-of-batch sweep.** When every active phase is done (the last review slice across all phases is complete), sweep them all to archived at once:

```sh
python3 scripts/workflow.py archive-all
```

`archive-all` refuses unless every active phase is `done` with a passing review — and, for any phase still owing its deferred doc consolidation, unless that has landed too.

**Rotate the done phases — partial sweep.** When only some phases are done, archive exactly those and leave the in-progress ones active:

```sh
python3 scripts/workflow.py rotate-backlog
```

**Archive one phase.** Archive a single review-passed phase by id:

```sh
python3 scripts/workflow.py archive-phase <P>
```

All three gate on the same rule: a phase must be `done` with a passing review to archive. **A phase owing docs has one more gate:** the engine blocks it while `consolidation` is still `"pending"` (`archive-phase` refuses, `archive-all` lists it, `rotate-backlog` leaves it active) — that debt is stamped by a passing review whose phase left "Doc impact" notes, and archiving is exactly what would move those notes out of `active/`. Run the docs phase (`docs-debt` for the worklist, `doc-new-version` per note), then `python3 scripts/workflow.py docs-consolidated <P>`; a parallel-mode phase merges first and uses `parallel-consolidated <P>` (see the `parallel-phase` skill). Use `--force` (on `archive-all`/`archive-phase`) only for exceptional cleanup of an unfinished phase.
