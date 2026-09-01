---
name: create-phase
description: Capture operator intent (refine → clarify → confirm), then create one or more phases (intent.md + DECOMP/REVIEW only) or route to defer-job. Stops before decomposition.
allowed-tools: Bash(python3 scripts/workflow.py:*), Read, Edit, Write, Glob, Grep
---

# create-phase

Turn an operator request for new work into one or more phases — or a deferred job — with the operator's intent captured first. **This skill creates phases; it never decomposes or implements them** (see *Making a phase ≠ executing it* in the contract — `CLAUDE.md`).

**Who may invoke it.** The operator, or **the agent when instructed** — by an approved plan that says to create a phase, or by a direct operator instruction. **Never on the agent's own initiative**: this is a narrower exception to the contract's "workflow command-skills are explicit-invocation only" than `design-cowork`, which does fire by itself. And invocation is not where the safety lives: **the confirmation gate at step 3 does not move**. Whoever started the intake, `new-phase` runs only after the operator has explicitly confirmed each phase's name and objective. **Invocation is not the gate; confirmation is.**

## Procedure

1. **Refine.** Restate the operator's request in clear language. Read the `docs/current/` **sections** the request actually touches (just in time — never the whole doc set; `python3 scripts/workflow.py docs` lists what exists) and run `python3 scripts/workflow.py next` for the current pointer, if useful. Preserve the operator's exact words — you will record them verbatim later.

2. **Clarify.** Ask the operator about anything ambiguous before acting: scope and boundaries, whether this is one phase or several, a sensible name and objective for each, and whether the work should start now (a phase) or be parked for later (a deferred job). Wait for answers. Do not run any `workflow.py` command yet.

   **If the work touches product visual design, one of those questions is the design style** — read the `design-cowork` skill (`## Shape — three styles`) and ask which of the three the work wants. **You suggest one and give the reason; the operator confirms or overrides.** It is never your decision alone and never left implicit:

   - **`build-after`** — one phase, two decomposition passes: `DECOMP` → groundwork → design round(s) → `DECOMP2` → build slices. Choose it when the whole design should land before any of it is built and the build fits in the same phase.
   - **`design-only`** — a *design* phase, then a separate *apply* phase; both keep the single pass. Choose it when the design is big.
   - **`paired`** — one phase, alternating design 1 → apply 1 → design 2 → apply 2; `DECOMP` cuts the pairs as **bare folders** and there is **no `DECOMP2`**. Choose it when the rounds are independent surfaces and each is small enough to apply before the next design starts.

   **`design-only` must be chosen here** — the `DECOMP` slice's executor is forbidden from running `new-phase`, so a phase split decided later cannot be created from inside decomposition. That is the deadline this choice has; the other two styles can still be settled at `DECOMP`. When a phase was created before its visual nature was clear, `DECOMP` asks the style instead and stops **`pending`** for the answer — and if the answer turns out to be `design-only`, the apply phase is created on the main thread through this skill, never from inside a `DECOMP`.

   **If the request is "consolidate the docs" / "run a docs phase" — or the operator is clearing a `consolidation_owed=` line from `next` — the scope is already written down.** Run `python3 scripts/workflow.py docs-debt` and propose what it prints; see *The docs-phase route* below. It is an ordinary phase through this same procedure, confirmed at step 3 like any other.

3. **Confirm.** Present your refined understanding back to the operator — for each phase, the proposed **name** and **objective**; for deferred work, the title, reason, and trigger. Get explicit confirmation. Per the contract, do **not** run `new-phase` until the operator confirms.

4. **Route on the operator's choice:**

   **Defer for later** → fold the confirmed intent into the arguments and run:
   ```
   python3 scripts/workflow.py defer-job --title "..." --reason "..." --trigger "..." [--source ...]
   ```
   This parks the job under `works/deferred/open/<DID>/` and never affects next-slice selection until promoted (the same command the `defer-job` skill wraps). Report and STOP.

   **Make a phase (or several)** → for each phase, in operator-confirmed order:
   1. Create it:
      ```
      python3 scripts/workflow.py new-phase --phase P<N> --name "..." --objective "..."
      ```
      `new-phase` creates only `P<N>.DECOMP` and `P<N>.REVIEW`, scaffolds `intent.md`, and links it near the top of `phase.md`.
   2. Fill `works/phases/active/P<N>/intent.md`:
      - leave **Origin** as `operator`;
      - paste the operator's request **word-for-word** under *Original Input (verbatim)* — do not fix grammar or wording;
      - write the confirmed, refined wording under *Confirmed Intent (refined + clarified)*;
      - record any clarifying Q/A under *Clarifications Resolved*;
      - **for a visual-design phase only**, append a `## Design Style` section naming the confirmed
        style (`build-after` / `design-only` / `paired`) and the one-line reason. `DECOMP` reads it.
        It is added **only when the phase is visual** — the scaffold does not carry the heading, and
        every reader treats its absence as "not a design phase", never as an unanswered question.

      (`new-phase` already filled the phase id and captured-at timestamp.)
   3. Confirm `phase.md` links `intent.md` near the top (the engine added `_Intent: see [intent.md](intent.md)._`).
   4. **Relay the parallel hint if `new-phase` printed one.** When another phase is already
      `in_progress`, the engine prints a `hint:` line offering
      `python3 scripts/workflow.py parallel-start P<N>` — surface it to the operator as a
      **suggestion, never a default**: this phase can run on its own branch and worktree instead of
      queueing behind the current one. **Now is the only moment to opt in** — `parallel-start`
      requires the phase to still be `planned`, so it must run before any decomposition or execution.
      If the operator says yes, run it and report the branch and worktree it created; the phase is
      then driven from a session opened in that worktree. See the `parallel-phase` skill for the full
      lifecycle (work, branch review, PR, merge, deferred doc consolidation, teardown).

5. **STOP and report.** List the phases created — IDs, names, and `intent.md` paths — or the deferred job created. Do **not** decompose into middle slices, write any slice's `plan.md`, or implement code. Decomposition is the `DECOMP` slice's own job, later, when the operator executes the phase (`/do-next-slice`, `/do-whole-phase`) or explicitly tells you to.

## The docs-phase route

Durable docs are versioned **in a docs phase the operator creates** — never per slice, and no longer at the review, which only *verifies* each phase's `## Doc impact` list and lets the engine stamp that phase's `consolidation` debt. So "consolidate the docs", "clear the doc debt", and a `consolidation_owed=` line in `next` all land here. Nothing is special-cased: same refine → clarify → **confirm at step 3** → `new-phase` → stop. What the route adds is that the scope is already recorded — do not re-derive it by hand:

1. **Read the debt** (read-only): `python3 scripts/workflow.py docs-debt`. It prints every owing phase with its `## Doc impact` notes, the docs those notes touch, and the command that pays each phase.
2. **Propose that as the scope** in step 2 — the phases and the docs it names. The operator may narrow it; a phase left out simply keeps owing and stays in `active/`.
3. **Confirm the name and objective at step 3, unchanged.** An objective that works: *"consolidate the `## Doc impact` notes from P12–P16 into new versions of architecture, operations and qa"* — name the phases, because they are what gets cleared at the end.
4. **`new-phase`, fill `intent.md`, STOP.** Record the `docs-debt` scope in `intent.md`; decomposition is the docs phase's own `DECOMP` slice, later.

**What that `DECOMP` will cut** (write it into `intent.md`; do not cut it here): **one slice per doc**, `--kind docs` — `doc-new-version` is per doc and one doc usually collects notes from several phases, so per-doc keeps each doc to a single new version. Risk by the normal rule. Each slice runs, per note it covers:

```sh
python3 scripts/workflow.py doc-new-version --doc <doc> --summary "..." --source <P>.REVIEW
# edit only the returned edit_path, then:
python3 scripts/workflow.py rebuild-docs
```

and the phase records the payment **for each phase it covered**: `python3 scripts/workflow.py docs-consolidated <P>` (a merged parallel phase: `parallel-consolidated <P>`), which is also what unblocks archiving those phases. All of it on the **default stream** — doc versions come from one shared index.

Two things that keep the route from feeding itself: a docs phase leaves **no `## Doc impact` notes of its own** (it pays other phases' notes; it creates no new durable truth), so its own review stamps no new debt — and it changes no operator-visible surface, so its acceptance gate is normally `--waive`d at the `DECOMP` boundary.
