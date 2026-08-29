---
name: review-phase
description: Review a completed phase against its objective and record a pass / changes_requested / blocked verdict.
allowed-tools: Bash(python3 scripts/workflow.py:*), Read, Edit, Write, Glob, Grep, Bash
disable-model-invocation: true
---

# review-phase

The phase review is executed by `slice-executor-high` — the top executor tier; reviews never run on a lower tier — dispatched by the orchestrator at the `REVIEW` slice; this is its checklist. It is where the phase's slices are **validated together** — the orchestrator trusted each executor's `done` and did not re-run per-slice validation, so re-run it here across the whole phase — and where the phase's durable-doc changes are **consolidated into new versions on a passing review** (from the "Doc impact" notes in `phase.md`). Write only docs here, never source code; do not implement fixes — those are done by fix slices.

**Parallel mode changes exactly one thing: the consolidation.** If the phase's `phase.json` carries an `execution` block with `mode: "parallel"` (the review then runs in that phase's branch worktree), a passing review creates **no** doc versions — doc versions are allocated from one shared `docs/index.json`, so two branches consolidating at once collide. Everything else — validating all slices together, judging the phase, recording the verdict — is unchanged. See the `parallel-phase` skill for the post-merge sequence that consolidates instead.

**The operator acceptance gate: on a gated phase you are not the last word.** Read the phase's `phase.json`. `acceptance.required` is `true` (the phase changes operator-visible surfaces — declared by the orchestrator at the `DECOMP` boundary), `false` (waived, with the reason in `note`), or `null` (undeclared — the engine refuses a `pass` until the orchestrator declares it; report that as a finding rather than guessing). A phase carrying **no `acceptance` block at all** is legacy (created before workspace v32) and reviews exactly as it always did. Only when `required` is `true` do the gate stages below apply, and only then do you return a `walkthrough` — the concrete script the operator runs against the running product. You never run `accept-gate` yourself: you return the walkthrough, the orchestrator opens the gate, and the operator has the last word. In parallel mode the gate composes unchanged — the review runs on the branch, and the gate opens and is cleared there against the branch's running product before `pass` is recorded, so `parallel-gate`'s "branch phase `done` + review `pass`" already implies the operator accepted it; only the doc consolidation is deferred.

Read:

- `CLAUDE.md`
- the `docs/current/` **sections** the phase actually touched (per its `## Doc impact` list) — not the whole doc set, and not `docs/index.json`: that is version history, and `validate` checks currency for you
- `python3 scripts/workflow.py next` for the pointer (no per-slice re-read of `works/backlog.md` — it is generated from the same state)
- the phase folder under `works/phases/active/<P>/`: `phase.md` — the **bounded notebook**, rewritten as the phase ran — and each completed slice's `slice.json` + `result.md`, read **head-first** (each `result.md` opens with that slice's verdict block: status, validation commands, deviations), whole wherever the detail matters
- the phase's `## Operator Questions` list in `phase.md` — every entry has to be routed before this review can pass
- on a gated phase: `## Operator Runtime` in `docs/current/operations.md` (how the operator runs and views the product) and `## Regression Checklist` in `docs/current/qa.md` (the cumulative product smoke list)

Check:

- Did the phase objective actually ship?
- Did each slice meet its brief and plan? Are deviations explained in `result.md`?
- **Validate all slices together** (the orchestrator no longer re-runs per-slice validation): re-run each slice's validation commands — they are in the verdict block at the head of its `result.md`, with its `plan.md` as the fallback — plus `python3 scripts/workflow.py validate`. Do they pass across the finished phase?
- Were the phase's durable-truth changes (product, architecture, API, …) consolidated into new doc versions **at this review** — not per-slice, not in-place edits? (Parallel mode: instead check that the "Doc impact" list in `phase.md` **covers every durable-truth change the phase made** — that list is the sole input to the post-merge consolidation, so an incomplete list is a review finding, not a detail.)
- Do `docs/current/*.md` match the latest versions in `docs/index.json` after consolidation? (`python3 scripts/workflow.py validate` checks this.) In parallel mode this applies at consolidation time on the default stream, not at the branch review.
- **Cross-check the notebook against the logs.** `phase.md` is bounded state that each slice *rewrote*, so what a slice knew survives only if it was written into `## Decisions` (or consumed and dropped on purpose). Read the notebook **and** every `result.md`: a decision or constraint a `result.md` records that no longer appears anywhere in `phase.md` is a **finding**, and so is a `## Doc impact` line missing for a durable-truth change a slice's log describes. (The notebook being *shorter* is not a finding — that is the point; the pre-edit text is in git.)
- Is every entry on `phase.md`'s `## Operator Questions` list **routed** — folded into the walkthrough as a decision for the operator, or listed for the orchestrator to file with `defer-job`? An unrouted entry is a finding, and the review may not pass with one.
- On a gated phase: did you open the running product **yourself**, or are you about to pass on other slices' reports?
- Did a design round ship a **throwaway mockup route**? Then no **orphaned design route** may remain: whichever slice implemented the surface for real deletes it (under `design-only` the route deliberately survives into the apply phase and is deleted there). A leftover route is a finding.
- Are any issues serious enough to require fix slices?

## Gate stages — only when `acceptance.required` is `true`

Run these after validating all the slices together and before rendering the verdict. On a waived (`false`) or legacy phase, skip the whole section.

1. **Find the manifest.** `## Operator Runtime` in `docs/current/operations.md` gives the run command(s), the mode (dev vs production build), the origin/host the operator browses, the devices/viewports/browsers, and the production build command + origin when they differ. If that section is **absent, or still carries its `UNFILLED` marker**, stop and return `needs_operator` asking the operator to fill it — never substitute your own most convenient runtime.
2. **Independent spot-check (you open the product).** Open the running product in that runtime and access path and verify the phase's headline claims yourself — a handful of key flows, end to end. Never pass a phase purely on the fidelity slice's or any other slice's report. When the manifest's runtime differs from the production build, check both: whole bug classes (dev-only double effects, reload semantics, origin and viewport differences) live in exactly that gap.
3. **Fresh-eyes UX walkthrough.** Use the product as a first-time user would and report everything dead, confusing, or annoying — **explicitly not judged against the design record**. Something the record drew is still a finding if it is bad in the flesh; something the record never drew (focus treatment, typeahead, empty and loading states) is still a finding even though no check exists for it. These findings go into the walkthrough for the operator to decide on — never into silent fixes, and never into overriding an approved design on your own authority. **One qualifier, for a phase whose operator-visible surface is a design mockup:** a mockup is stubbed by design and **exempt from the functional sweep**, so its non-functional controls are not defects — name them in the walkthrough as deliberately unwired instead, and keep judging what it *is* for (does it run, does every designed element and state render, does it match the record). A phase shipping real wiring gets the unqualified stage above.
4. **Re-run the whole smoke list.** Run every line of `## Regression Checklist` — the qa doc's cumulative product smoke list — in the manifest runtime, not just this phase's lines: a later phase touching shared surfaces is exactly how an earlier phase's pass goes stale. Then append this phase's headline checks in the shipped shape `- [ ] <surface>: <one observable behaviour> (P<N>)`. That append is a doc change and rides the consolidation below.
5. **Route every operator question.** Each entry on `phase.md`'s `## Operator Questions` list is either folded into the walkthrough as a decision for the operator to take, **or** filed as a deferred job. You may not run `defer-job`: list the jobs to file — title, reason, trigger — in `result.md` and in your return, and the orchestrator files them. An unrouted entry is a finding.
6. **Return the walkthrough.** Beside `review_verdict`, return a **`walkthrough`** field: the concrete script the operator runs — URLs to open, actions to try, in the manifest runtime and access path — plus the routed questions as decisions to take. Keep it short enough that an operator will actually run it.

**Form the verdict from the complete picture, then branch on it.** Finish the validation and the judgment across every slice *first* — never abort at the first failing check, or the orchestrator learns one finding per review cycle instead of all of them at once. Only once the verdict is settled does the review split:

- On a **passing** review, before recording `pass`, consolidate docs: for each durable-truth area changed across the phase (per the "Doc impact" notes in `phase.md`), run `python3 scripts/workflow.py doc-new-version --doc <doc> --summary "..." --source <P>.REVIEW`, edit only the returned `edit_path`, then `python3 scripts/workflow.py rebuild-docs` — one version per affected doc, capturing the whole phase. **In parallel mode, skip this step entirely**: run no `doc-new-version` and no `rebuild-docs` on the branch, and report `doc_versions: none — deferred to post-merge consolidation (parallel mode)`. The orchestrator consolidates on the default stream after the merge, from the same "Doc impact" list you just verified (`parallel-phase` skill). **A gated phase changes nothing about the timing:** consolidate here, in the pass path, *before* the gate opens — the stage-4 smoke-list append rides the same consolidation. If the operator then reports failures, the `changes_requested` → fix → re-review cycle consolidates again and the newer versions supersede; doc versions are append-only durable truth, and a version describing code that exists is not false.
- On **`changes_requested` or `blocked`, stop here and hand back.** Doc consolidation is pass-only work: do not run it, and do no other pass-only step either. Return to the orchestrator the verdict, the numbered findings, and the proposed fix slices (`<P>.F<n>`, one line of scope each); it decides what happens next — create the fix slices, or take the decision to the operator. This is a full stop, not a skipped step you carry on past: the review ends there, and the docs stay unversioned until a later passing re-review consolidates the whole phase in one go.

## After a passing review — what the orchestrator does with it

On a phase whose gate is `required: true`, your `pass` does not end the phase:

1. The orchestrator runs `python3 scripts/workflow.py accept-gate <P> --open --walkthrough "<the walkthrough you returned>"` — the phase goes `pending` — files any deferred jobs you listed, commits, reports the walkthrough to the operator, and STOPS. `next` then prints `WAITING ON OPERATOR` with the walkthrough and the clear command.
2. The operator walks the running product. If they accept, the gate clears with `python3 scripts/workflow.py accept-gate <P> --clear [--note "..."]` (the operator's command, or the orchestrator's on their explicit say-so) and the phase returns to `in_progress`.
3. On the resume the `REVIEW` slice is still `in_progress`, your `result.md` still carries `review_verdict: pass`, and the gate now shows `cleared_at`: the orchestrator records `review-phase <P> --verdict pass` **without re-dispatching the review**, validates, and commits.
4. If the operator reports failures instead, the orchestrator records `review-phase <P> --verdict changes_requested --note "operator-reported: ..."` — never refused, and it resets `walkthrough` / `requested_at` / `cleared_at` — creates `fix` slices from the report, runs them, and the review starts again from the top, gate stages included.

Waived and legacy phases skip all of that: the verdict is recorded straight away, as it always was.

**Two commands you never run on a review slice:** `accept-gate` (a phase-state command — you return the walkthrough, the orchestrator opens the gate) and `defer-job` (you list the jobs, the orchestrator files them). Your workflow commands stay `doc-new-version` / `rebuild-docs` on a pass, plus `validate`.

**The review does not write the phase explainer.** Explaining is a separate operation the operator runs when they want one (`/explain`); it left the review's default behaviour, so the review locates no explain skill, runs no KB probe, and has no offline fallback or commit of any kind. Its whole obligation is one pointer line, reported in `result.md` and in the structured return, identical on every verdict: `explain: not written — run /explain for this phase`.

The orchestrator records exactly one verdict (the executor returns it; the executor never runs `review-phase` itself):

```sh
python3 scripts/workflow.py review-phase <P> --verdict pass --reviewer slice-executor-high --note "short justification"
# or
python3 scripts/workflow.py review-phase <P> --verdict changes_requested --reviewer slice-executor-high --note "numbered issues + proposed fix slices like P1.F1"
# or
python3 scripts/workflow.py review-phase <P> --verdict blocked --reviewer slice-executor-high --note "the blocker and needed input"
```

On a gated phase the engine refuses `--verdict pass` until `accept-gate <P> --clear` has stamped `cleared_at`, so the pass above is recorded on the resume after the operator's walkthrough, not in the same turn as the review. `pass` also marks the phase `done` **and closes the `REVIEW` slice** — the phase stays in `active/`; archiving is a separate, manual step (`archive-all`, `rotate-backlog`, or `archive-phase`). `changes_requested` returns the phase to `in_progress` and sets the `REVIEW` slice to `changes_requested` (reopened for re-review). `blocked` sets **both the phase and the `REVIEW` slice** `blocked`. For a parallel-mode phase, a recorded `pass` is also what opens the integration sequence the orchestrator then runs (`parallel-gate <P>` → push → PR → CI → merge → `parallel-merge-finish` → deferred consolidation → `parallel-consolidated <P>` → `parallel-teardown <P>`); archiving stays blocked until that consolidation is recorded.
