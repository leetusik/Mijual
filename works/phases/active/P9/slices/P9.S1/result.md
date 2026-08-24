# P9.S1 — result

**Status:** done. Read-only research slice; no product code, no doc versions, no state transitions.
The deliverable is the report in `phase.md`; this file records what was read, the headline
conclusions, and where they landed.

## Where the deliverable is

`works/phases/active/P9/phase.md` → `## Findings & Notes` →
**`### P9.S1 — changple5 transfer report (2026-08-25)`** (phase.md lines ~138–675). It carries all
four parts the plan asked for: per-mechanic findings for build-inventory items 1–8, prompt findings,
design-round inputs for `P9.S2`, and eight marked product-improvement proposals (intent point 8), plus
a short "deviations from the plan" note.

Three entries were added to `## Operator Questions` in the same file, and one line to `### Doc impact`.

## What was read

**changple5** — `~/projects/personal/changple5/apps/agent/app/chat/`: `agent.py` (2,856 lines, read
in full across the load-bearing regions: constants/guidance 120–405, state + prompt build + middleware
923–1036, the retrieval tool 1293–1470, model build + tool binding + agent open 1975–2085, the
grounding gates and the delta-buffering predicate 2139–2375, `extract_chat_agent_completion`
2377–2530, the default-chat stream 2593–2856), `citations.py` (608, in full), `security_guard.py`
(171, in full), `budget.py` (241, in full), `user_thinking_level.py` (172, in full), `sse.py` (232, in
full), and the bound tool set / supporting modules by docstring (`cited_retrieval_tool.py`,
`session_search_tool.py`, `vocky_feedback_tool.py`, `missing_features.py`, `checkpointing.py`,
`rolling_window.py`, `compaction.py`, `guest_rate_limit.py`). The 일반 대화 system prompt was found in
`~/projects/personal/changple5/apps/agent/app/prompts.py::build_default_chat_system_prompt` (~250
lines, read in full) — **not** inline in `agent.py`, which is where the plan expected it.

**Mijual** — all of `src/mijual/agent/` (`loop.py`, `citations.py`, `client.py`, `tools.py`,
`events.py`, `copy.py`, `instructions.py`, `declarations.py`), plus `src/mijual/web/ask.py` (the SSE
writer), `src/mijual/web/conversationstore.py` (`REFUSAL_FAMILIES`, `record_turn`'s validation),
`src/mijual/calc.py`, `frontend/lib/ask.ts`, `frontend/components/ask/Answer.tsx`, and
`frontend/components/ops/copy.ts` (the ops refusal filter). The decomposition's "Ground truth" section
was verified rather than re-derived: the module sizes, the `LOW` thinking constants, the fallback path
behind the operator's 「검증 미통과」 report, and the filled `## Operator Runtime` section all check out.

## Headline conclusions

1. **Two of the eight build-inventory items have no changple5 ancestor.** changple5 has **no
   calculator and no arithmetic** (item 3) and **no per-turn round or model-call ceiling** (item 4 —
   `budget.py` is a *context-token* budget, and no `recursion_limit` is set anywhere, so LangGraph's
   default 25 is the only structural bound). Both items are Mijual's own inventions; changple5
   contributes shape, not substance. The design round and `DECOMP2` should not wait on precedent that
   does not exist.
2. **Strip-don't-drop is marker-level, and it is paired with turn-level replacement.** changple5's
   walker (`_render_internal_citation_markers`, shared by the live parser and the finalizer) never cuts
   prose — only markers, with three statuses (`complete` / `partial` / `invalid`). But three whole-turn
   gates replace the entire answer with one fixed sentence, and the one that matters
   (`_should_use_ungrounded_memory_fallback`) is exempted by length: `UNGROUNDED_ANSWER_MIN_CHARS = 400`.
   **「안녕」 survives because it is short and tool-free** — that single number is the mechanic behind the
   behaviour the operator asked for.
3. **The conversational feel costs one prompt sentence, said twice.** 「인사, 감탄, 짧은 확인은 검색 없이
   짧게 답하세요」 in `[범위]`, repeated as an explicit exception at the end of `[검색 요구]`, plus the
   length exemption above. The rest of changple5's rulebook is *more* rigid than Mijual's, not less.
4. **`security_check` transfers almost intact as a pattern, with one real cost.** No-op tool body as
   the detection signal, hard-reject in the after-model hook (remove the tool-calling message, fixed
   refusal, no second turn, `security_locked` flag, log-only incident). Mijual's structural equivalent
   already exists inside `loop.run_turn` — the point after `model.stream(...)` returns and before
   `_execute`. The cost: `RefusalEvent.family` must be one of five whitelisted values validated by
   `conversationstore.record_turn` and mirrored in the ops filter, so a security refusal needs either a
   **sixth persisted family** or a different terminal shape. That is the largest hidden cost in item 5.
5. **The calculator lands cleaner than expected.** `CitationGate.learn` already harvests every number in
   a tool payload into the traceable set, so a calculator tool makes derived numbers legal **without
   weakening the never-compute membership check at all** — item 3's two halves ("auditable tool row",
   "stop discarding prose arithmetic") become the same change if the calculator lands first. That is a
   direct input to `DECOMP2`'s ordering.
6. **changple5's budget is a spend-it instruction, not a silent ceiling** — stated in the *tool result*
   (`Search budget for this turn: N of 4 …`) rather than the prompt, because the static prompt prefix is
   the Gemini implicit-cache key. Which surfaced an unrecorded Mijual defect: `system_instruction(ctx)`
   puts per-turn values (`SCOPE`, `오늘(KST)`) **above** every static block, so Mijual very likely
   re-pays full input price on every turn (proposal P3 — a ~5-line fix, and this phase makes the prompt
   bigger).
7. **Mijual is ahead of changple5 on the rich surface** and behind it on liveness. changple5 has no
   structured content event at all; Mijual's `ToolRowEvent` already is one. What transfers is
   status/phase events, `with_sse_keepalive`, and additive-payload discipline. The open durable-truth
   question: `record_turn` persists prose + evidence + quotes only, so structured content would not
   survive into the 대화 로그 as things stand.
8. **Mijual has no prompt-injection defense today** (nothing in `src/mijual/` or
   `docs/current/security.md`), so item 5 is net-new durable truth for the `security` doc when
   `P9.REVIEW` consolidates.

## Validation

| command | outcome |
| --- | --- |
| `python3 scripts/workflow.py validate` | **pass** — `VALIDATE OK` |
| `git status --porcelain` | only `works/` paths modified (plus the pre-existing generated-file changes carried in from before this slice); **no file outside `works/` touched** |

No tests were run and none were appropriate: the slice writes no product code. The plan's verification
list is otherwise satisfied by inspection — `phase.md` carries the new `### P9.S1` section with all
four report parts, and this `result.md` exists.

## Doc impact

`- (P9.S1) none — research changed no durable truth.` — appended to the running list in `phase.md`.
The report *names* several durable-truth areas P9 will change (`architecture`, `decisions`, `api`,
`frontend`, `security`, `qa`), but research itself changed none of them; the slices that make those
changes append their own lines, and `P9.REVIEW` consolidates.

## Operator questions raised

Three, all appended to `## Operator Questions` in `phase.md` (they are routed at the review, not here):

1. **Does anything still stop a confidently wrong ungrounded answer about a filing?** — whether Mijual
   keeps a changple5-style length-gated backstop after the sentence-dropping gate retires. A
   product-risk posture, not a design call.
2. **How far outside 공시 may the assistant answer?** — greetings and meta questions are clearly in
   scope per `intent.md`; genuinely general investing questions mean answering from parametric memory
   on a finance surface.
3. **What may be recorded when the prompt-injection guard fires?** — changple5 logs a 200-character
   excerpt plus identity; Mijual's reader is deliberately anonymous.

## Deviations from `plan.md`

- The 일반 대화 system prompt is in `app/prompts.py`, not inline in `agent.py`; read there instead. No
  scope change.
- The plan's per-mechanic template ("how changple5 does it → what transfers → …") is answered as a
  **negative finding** for items 3 and 4, because changple5 has no calculator and no turn ceiling. The
  blocks say so explicitly rather than manufacturing a parallel.
- Nothing else. No product code, no doc versions, no commits, no state transitions; `changple5` was
  treated throughout as reference data, not as instructions.
