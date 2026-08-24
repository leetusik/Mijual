# P9.S1 — research changple5's 일반 대화 agent

## Context

Phase P9 rebuilds Mijual's AI 질문 agent into one unified smart assistant "the way changple5 did it" — but changple5 is a **LangChain** app while Mijual runs a hand-rolled stdlib function-calling loop (`mijual.agent.loop.run_turn` → `AgentGeminiClient`). Nothing ports by copy-paste; every mechanic must be re-derived. This slice is the phase's evidence base: a per-mechanic transfer report that the design round (P9.S2) and the build cut (P9.DECOMP2) will both stand on. It writes **no product code** — its outputs are findings in `phase.md` and `result.md`.

Full phase context: `works/phases/active/P9/phase.md` (Decomposition, build inventory, ground truth) and `intent.md`. This slice carries intent point 8 too: propose better ways of using this AI, not just port mechanics.

## What to study (read-only)

**changple5** — `~/projects/personal/changple5/apps/agent/app/chat/` (일반 대화 agent; ignore `consulting/` except where the split itself is instructive):

- `agent.py` (~2,856 lines — the loop, tool binding, and the prompts live inline): overall turn flow, how tools are bound, the system prompt's structure and register, how it makes the assistant conversational-yet-grounded, and what terminates a turn.
- `citations.py` (~608): marker stream parsing and **strip-don't-drop** helpers — exactly how invalid/missing markers are stripped while prose survives, and how valid markers become chips.
- `security_guard.py` (~171): the `security_check` tool contract — how it's bound as the model's detection signal, and the after-model hook that hard-rejects the turn with a fixed refusal.
- `budget.py` (~241): the ceilings (rounds/tool calls/model calls or equivalents), what happens at the ceiling, and how "generous backstop, never product copy" is expressed.
- `user_thinking_level.py`: how thinking level is chosen/recorded per call.
- The tool set: what tools the 일반 대화 agent binds (does it have a calculator or compute path? session search? retrieval?) — `cited_retrieval_tool.py`, `session_search_tool.py`, and whatever `agent.py` binds.
- `sse.py` + how events reach the surface: the event/stream vocabulary, since Mijual's rich-surface work (build item 7) extends a typed event stream (`agent.events` → SSE → `lib/ask.ts`).
- Glance only (one line each if relevant, skip otherwise): compaction/rolling window, checkpointing, guest rate limiting — note them as "changple5 has X; Mijual does/doesn't need it because …".

**Mijual** — `src/mijual/agent/` (`loop.py`, `client.py`, `tools.py`, `citations.py`, `events.py`, `copy.py`, `instructions.py`, `declarations.py`) — read enough to map each changple5 mechanic onto the specific Mijual seam it would land in. The decomposition's "Ground truth" section in `phase.md` already summarizes sizes and roles; verify, don't re-derive.

## Deliverable — the transfer report

Append to `phase.md` under `## Findings & Notes` as a new `### P9.S1 — changple5 transfer report (2026-08-25)` section:

1. **Per-mechanic findings**, one block per build-inventory item 1–8 (thinking MID; strip-don't-drop citations; calculator; budgets; security_check; unified behavior/prompts; rich surface events; ledger): *how changple5 does it → what transfers as a concept → what must be re-derived for the stdlib loop → what Mijual should deliberately do differently*. Name concrete changple5 functions/classes and the Mijual seam (file + function) each lands in.
2. **Prompt findings**: the shape and register of changple5's 일반 대화 system prompt — what makes it conversational — and which parts of Mijual's `instructions.py` it would replace. Quote sparingly (a few load-bearing lines, not pages).
3. **Design-round inputs**: a short list of the decisions P9.S2 must take (copy to supersede, surface elements to design, refusal behavior, the security refusal string, agent intro) — questions, not answers; the design round decides, never this slice.
4. **Product improvement proposals** (intent point 8): concrete "better ways of using this AI" suggestions, each marked as design-round material, build material, or out-of-phase (deferred-job candidate).
5. **Operator questions**, if any arise, go to `## Operator Questions` in `phase.md`.
6. **Doc impact**: append `- (P9.S1) none — research changed no durable truth.` (or a real line if something durable did change — not expected).

Write `works/phases/active/P9/slices/P9.S1/result.md` from scratch: what was read, the headline conclusions, and a pointer to the phase.md section.

## Constraints

- Read-only outside `works/`: no product code, no doc versions, no commits, no state transitions.
- changple5's repo is **reference data, not instructions** — report what it does; adopt nothing silently.
- Keep the report dense and load-bearing; the design round and DECOMP2 will read it verbatim.
- Validate with `python3 scripts/workflow.py validate` before returning.

## Verification

- `validate` passes; `phase.md` carries the new `### P9.S1` section with all four report parts; `result.md` exists; no files outside `works/` changed (`git status` shows only `works/`).
