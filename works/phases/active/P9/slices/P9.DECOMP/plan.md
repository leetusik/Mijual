# P9.DECOMP — decompose phase P9 (Smart Mijual Assistant)

## Context

P9 rebuilds the AI 질문 agent (`src/mijual/agent/`) from a rigid grounded bot into one unified smart assistant modeled on changple5's 일반 대화 agent, plus a richer chat surface (data rows, calculation results rendered in the thread). The confirmed intent lives in `works/phases/active/P9/intent.md` — it is detailed and already fixes the phase shape: **research slice first, then design co-work round(s), then `P9.DECOMP2`** cuts the build slices. This is the design-cowork mixed-phase two-pass pattern: this DECOMP creates only the groundwork, design, and DECOMP2 slices, and records a build inventory (what, not how) in `phase.md`.

## What the executor (slice-executor-high) does

1. **Read for context** (read-only): `works/phases/active/P9/phase.md` and `intent.md`; `docs/current/frontend.md`, `architecture.md`, `decisions.md` (the signed design records this phase will supersede — R6 refusal families, never-compute rule, the 검증 line in the `/ask` rail); skim `src/mijual/agent/` (`loop.py`, `citations.py`, `client.py`, `tools.py`, `instructions.py`) enough to scope the breakdown — deep study belongs to the research slice, not here.

2. **Create the middle slices** with `python3 scripts/workflow.py new-slice` — bare folders only, never pre-filling any `plan.md`:
   - `P9.S1` — "research changple5 일반 대화 agent" — `--kind research --risk high --order 1`. Study `~/projects/personal/changple5/apps/agent/app/chat/` (`agent.py`, `citations.py`, `security_guard.py`, `budget.py`, prompts) and report what transfers to Mijual's stdlib loop; also propose product improvements (intent point 8). Findings land in `phase.md` for the design round and DECOMP2 to build on.
   - `P9.S2` — "design round 1: unified assistant & rich chat surface" — `--kind co-work --risk high --order 2`. **One design round** (a superseding revision round would be inserted later with a fractional order if needed). Scope: the new chat-surface display elements (data rows, calculation results), the superseded copy (R6 refusal families, never-compute rule, 검증 rail line, agent intro), and the unified conversational behavior.
   - `P9.DECOMP2` — "second decomposition: cut build slices from the signed design" — `--kind decomposition --risk high --order 3`. Cuts the build slices once the design has landed — backend first, design implementation after.
   - `depends_on` chain S1 ← S2 ← DECOMP2 (advisory).

3. **Record in `phase.md`**: the slice breakdown and rationale under `## Decomposition`; a **build inventory** under `## Findings & Notes` — *what* must exist by phase end, not how: thinking MID, strip-don't-drop citations, calculator tool + free prose arithmetic, ~20-round generous budgets, `security_check` guard + after-model hard-reject with fixed Korean refusal, unified conversational behavior, structured chat-surface rendering, per-turn ▷ ledger preserved.

4. Write `result.md`, return a structured verdict. No commits, no state transitions (beyond the decomposition carve-outs), no code.

## Orchestrator steps after the executor returns `done`

- `finish-slice P9.DECOMP` → `validate`.
- **Declare the acceptance gate in the same commit**: `python3 scripts/workflow.py accept-gate P9 --require` — the phase changes the operator-visible chat surface, so the gate is clearly required.
- Commit (`chore(p9): decompose phase — research → design → DECOMP2, acceptance gate required`).

## Rest of the loop (gated mode)

Continue `do-whole-phase` under the plan-approval gate: plan `P9.S1` at the gate → approval → dispatch `slice-executor-high` → finish/validate/commit. Then the `P9.S2` co-work slice runs **inline on the main thread** per the design-cowork skill (handoff.md → `pending` → STOP); the loop halts there for the operator's design session — that stop is expected, not a failure. `DECOMP2` and everything after happen on resume, after the signed design lands.

## Verification

- `python3 scripts/workflow.py validate` passes after the DECOMP finishes.
- `works/backlog.md` (regenerated) shows P9.S1, P9.S2, P9.DECOMP2 in order 1/2/3 between DECOMP and REVIEW.
- `phase.json` carries `acceptance.required: true`.
