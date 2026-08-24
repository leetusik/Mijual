# P9.DECOMP — result

Decomposed phase P9 (Smart Mijual Assistant) as a **design-bearing, two-pass** phase: this first pass
created only the groundwork (research), the design round, and the second decomposition slice, and
recorded a build inventory in `phase.md` in place of build slices.

## What I did

1. **Read for context** (read-only): `works/phases/active/P9/phase.md`, `intent.md`, `phase.json`;
   `docs/current/architecture.md` (agent layer, the no-LLM-in-request-path invariants, the
   never-compute rule), `docs/current/decisions.md` (the generation-boundary citation gate that
   *drops* rather than flags, D-13's unlimited/anonymous companion, the R6/R14 rounds),
   `docs/current/frontend.md` (the `/ask` surface, the one store / two views rule, `Answer` +
   `InlineCitation`), `docs/current/operations.md` §Operator Runtime; skimmed `src/mijual/agent/`
   (`loop.py` `TurnBudget`/`run_turn`, `client.py` `THINKING_BY_TASK`/`AgentGeminiClient`/ledger,
   `citations.py` `CitationGate`, `tools.py` the five tools, `events.py` the seven typed events,
   `copy.py` `AGENT_INTRO_KO`/`REFUSAL_SENTENCES`) plus
   `src/mijual/web/conversationstore.py::REFUSAL_FAMILIES` and `frontend/components/ask/`. Deep
   changple5 study was **deliberately not** done here — it is `P9.S1`'s job.

2. **Created exactly three middle slices** (bare folders — each holds only `slice.json`; no `plan.md`
   was pre-filled for any of them):

   | command | result |
   | --- | --- |
   | `new-slice --phase P9 --slice P9.S1 --name "research changple5 일반 대화 agent" --kind research --risk high --order 1` | `works/phases/active/P9/slices/P9.S1` |
   | `new-slice --phase P9 --slice P9.S2 --name "design round 1: unified assistant & rich chat surface" --kind co-work --risk high --order 2 --depends-on P9.S1` | `works/phases/active/P9/slices/P9.S2` |
   | `new-slice --phase P9 --slice P9.DECOMP2 --name "second decomposition: cut build slices from the signed design" --kind decomposition --risk high --order 3 --depends-on P9.S2` | `works/phases/active/P9/slices/P9.DECOMP2` |

3. **Recorded in `phase.md`**: the slice breakdown + rationale under `## Decomposition` (including
   what is deliberately *not* decomposed yet and why), and under `## Findings & Notes` an 8-item
   **build inventory** (thinking MID · strip-don't-drop citations · calculator tool + free prose
   arithmetic · ~20-round generous budgets · `security_check` + after-model hard-reject with a fixed
   Korean refusal · unified conversational behavior · structured chat-surface rendering end to end ·
   the ▷ ledger preserved), the invariants nothing in P9 may break, the ground truth read at
   decomposition, and the empty **Doc impact** running list.

4. **Appended one `## Operator Questions` entry**: thinking `LOW` → `MID` combined with a ~20-round
   ceiling multiplies the worst-case cost of one turn on a surface that is free, anonymous and
   unlimited by decision (D-13) — the operator decides whether that stands as-is or whether P9 should
   also land a cheap, never-rendered abuse backstop. It must be routed at `P9.REVIEW` (walkthrough or
   `defer-job`).

## Validation

| command | outcome |
| --- | --- |
| `python3 scripts/workflow.py validate` | **pass** — `Workflow validation passed.` |
| `python3 scripts/workflow.py next` (spot check) | current slice `P9.DECOMP`, next `P9.S1` |
| `works/backlog.md` regenerated | shows `P9.S1` / `P9.S2` / `P9.DECOMP2` at order 1 / 2 / 3 between `P9.DECOMP` and `P9.REVIEW` |

## Deviations from plan.md

None. The plan's three slices, kinds, risks, orders and `depends_on` chain were created exactly as
specified, and nothing else was created.

## Notes for the orchestrator

- `phase.json` still carries `acceptance.required: null`. Declaring it is the orchestrator's step
  right after `finish-slice P9.DECOMP`; P9 changes the operator-visible `/ask` chat surface, so
  `accept-gate P9 --require` is the expected declaration.
- `P9.S2` is `kind: co-work` — per the design-cowork skill it is **run inline on the main thread**
  (handoff → `pending` → STOP), never dispatched to an executor. The `do-whole-phase` loop halting
  there is expected, not a failure.
- No doc versions were created (decomposition never versions docs; `P9.REVIEW` consolidates on a
  pass).
