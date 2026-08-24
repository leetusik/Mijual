# Phase P9: Smart Mijual Assistant

_Intent: see [intent.md](intent.md)._

## Objective

Rebuild the AI 질문 agent from rigid grounded bot into a unified smart assistant modeled on changple5's 일반 대화 agent: gemini-3.7-flash at thinking MID, strip-don't-drop citations, a calculator tool with free prose arithmetic, generous turn ceilings, a security_check prompt-injection guard, naturally conversational behavior, and a chat surface that renders structured content (data rows, calculation results) in the conversation — research changple5 first, then a design round, then DECOMP2 cuts the build.

## Context

## Decomposition

_Filled by `P9.DECOMP` (2026-08-25)._

P9 both **designs** and **builds**, so it decomposes in **two passes** (the `design-cowork` mixed-phase
pattern), exactly as `intent.md` fixes the shape: research → design → `DECOMP2`. This first pass
therefore creates **no build slices at all** — the signed design decides what gets built, and a build
inventory (below, under *Findings & Notes*) stands in for them until `P9.DECOMP2` cuts them.

| slice | kind | risk | order | depends on | what it covers |
| --- | --- | --- | --- | --- | --- |
| `P9.S1` | research | high | 1 | — | Study changple5's 일반 대화 agent; report what transfers to Mijual's stdlib loop, and propose product improvements |
| `P9.S2` | co-work | high | 2 | `P9.S1` | Design round 1 — the unified assistant's behavior/copy and the rich chat surface |
| `P9.DECOMP2` | decomposition | high | 3 | `P9.S2` | Cut the build slices from the signed design — backend first, design implementation after |

**Why these three, and why nothing else yet.**

- **`P9.S1` (research) first, by operator instruction.** The whole phase is "do it the way changple5
  did it", and changple5 is a **LangChain** app while Mijual's agent is a hand-rolled stdlib
  function-calling loop (`mijual.agent.loop.run_turn` driving `AgentGeminiClient`, no SDK framework).
  Nothing ports by copy-paste; every mechanic has to be re-derived. S1 reads
  `~/projects/personal/changple5/apps/agent/app/chat/` — `agent.py`, `citations.py` (marker stream
  parsing + strip helpers), `security_guard.py`, `budget.py`, and the prompts — and reports, per
  mechanic, **what transfers, what must be rebuilt, and what Mijual should do differently**. It also
  carries intent point 8: actively propose better ways to use this AI, not just port mechanics.
  Findings land in this file so both the design round and `DECOMP2` build on them. It is `research`
  and writes no product code; `risk: high` because the reading is deep and the output steers the phase.
- **`P9.S2` (design co-work) second, and exactly one round.** Two things in this phase are *visual
  and copy* decisions that an executor may never invent: (a) the **new chat-surface display
  elements** — data rows, calculation results, and whatever else structured content the thread
  should render (today the surface has only mono tool fact rows + numbered citation chips); (b) the
  **superseded signed copy** — R6's five refusal families (`철회 · 확정 전 · 공시에 없음 · 검증 미통과
  폴백 · 계산 요청`), the never-compute rule, the 검증 line in the `/ask` rail, and `AGENT_INTRO_KO`
  ("검증을 통과한 공시에 대해서만 답합니다…"), all of which the unified assistant contradicts. RESPECT
  THE DESIGN holds until a new signed round supersedes them, so this round exists to produce that
  supersession. One round is planned; a revision round, if the operator asks for one, is inserted
  later at a fractional order (`--order 2.5`) as a new immutable superseding round — never by editing
  round 1. Run **inline on the main thread** per `design-cowork` (handoff → `pending` → stop); it is
  never dispatched to an executor and never writes implementation code.
- **`P9.DECOMP2` third.** The build slices cannot honestly be cut now: how many frontend slices exist,
  and what they render, depends on what the design signs off. `DECOMP2` cuts them once the design has
  landed, **backend first, design implementation after** — so the stream can already carry the new
  structured content before the surface is asked to draw it.
- **`depends_on` chain S1 ← S2 ← DECOMP2** (advisory, but it is the real order: research feeds the
  design, the design feeds the build cut).

**Not in this phase's decomposition (deliberate):**

- No build slices, no `plan.md` pre-filled for any of the three (each slice's plan is written at its
  own turn by the orchestrator).
- No doc versions here. P9 changes durable truth in at least `architecture`, `decisions`, `frontend`,
  `api`, `security` and `qa`; each slice appends to the **Doc impact** list below and `P9.REVIEW`
  consolidates once, on a pass.
- The **acceptance gate** is the orchestrator's call right after this slice: the phase changes the
  operator-visible `/ask` chat surface, so `--require` is the expected declaration.

## Findings & Notes

_Durable findings and cross-slice notes; `DECOMP` seeds this, and each slice appends when it finishes._

### Build inventory — what must exist by the end of P9 (what, not how)

Cut into slices by `P9.DECOMP2`, after the design lands. Each line is a **required end state**, not an
implementation instruction; the design round and the research findings decide the how.

1. **Thinking MID.** The agent turn runs at thinking level **MID**, not `LOW` — today
   `client.THINKING_BY_TASK = {"agent_turn": "LOW"}` and `DEFAULT_THINKING_LEVEL = "LOW"`, with the
   choice argued in the module docstring and in `decisions` D-4's amendment. The level is still
   *recorded per call* in the ▷ ledger, and the docstring's argument is rewritten rather than deleted.
2. **Citations: strip, don't drop.** The generation-boundary gate that *discards* sentences
   (`citations.CitationGate`, `Blocked`) is retired as a dropper: valid `[[cite:…]]` markers still
   resolve to numbered evidence chips, invalid or missing markers are **stripped** and the prose
   survives. This is the single change that stops 「안녕」 from returning the 검증 미통과 refusal. The
   per-answer numbering rule (same source → same number, numbering per answer) stays.
3. **Calculator tool + free prose arithmetic.** A server-side calculator tool exists so derived
   numbers appear as an **auditable tool row**, *and* the never-compute sentence rule stops
   discarding prose that computes, converts or restates numbers. `mijual.calc` stays the LLM-free
   home of 금액/D-day arithmetic; the calculator tool is the agent's auditable window onto arithmetic,
   not a second implementation of the product's money math.
4. **Generous budgets, not unlimited.** `loop.TurnBudget` rises from `6 rounds / 10 tool calls /
   8 model calls` to ceilings no real conversation reaches (order of **~20 rounds**, tool and model
   calls scaled with it), keeping the runaway-spend backstop and the honest `aborted` terminal. The
   ceilings remain structural and are still never rendered as copy (R6-5: 질문 수 무제한).
5. **Prompt-injection guard.** A changple5-style **`security_check`** tool is bound to the model as
   its detection signal, plus an **after-model hard-reject** that ends the turn with a fixed Korean
   refusal. The refusal string is user-visible copy and therefore belongs to the design round.
6. **Unified conversational behavior.** One assistant: it chats naturally (greetings, general
   questions, meta questions about 미주알) and grounds filing facts with tools and citations when it
   uses them. R6's five rigid refusal families are relaxed/retired per the signed design;
   `instructions.py` and `copy.py` (`AGENT_INTRO_KO`, `REFUSAL_SENTENCES`, `REFUSAL_FALLBACK`) are
   rewritten to match, and `web.conversationstore.REFUSAL_FAMILIES` — the persisted analytics column
   with a five-value whitelist — must stay consistent with whatever survives.
7. **Rich chat surface.** The thread renders **structured content**, not only prose: data rows,
   calculation results and whatever else the design specifies, alongside today's mono tool fact rows
   and citation chips. This runs end to end — new typed events in `agent.events` (today:
   `ToolRowEvent`, `CitationEvent`, `TextEvent`, `RefusalEvent`, `LinksEvent`, `FooterEvent`,
   `TurnEnd`), through the `POST /ask` SSE transport, the `lib/ask.ts` store, into new
   `components/ask/*` renderers used by **both** views (widget and `/ask` page are two views over one
   store — do not fork).
8. **The ▷ per-turn ledger stays.** The agent remains the system's only in-request LLM spend; every
   turn still reports its tokens, thinking levels and ▷ cost.

**Invariants nothing in this phase may break:** no OpenDART call and no LLM call outside the agent in
a request path; the model is reached **only** through `mijual.agent`; `mijual.agent` imports no
spending module (all three AST-scanned by tests); the agent still derives no number *except* through
the new, auditable calculator tool.

### Ground truth read at decomposition (2026-08-25)

- **The agent is a hand-rolled stdlib loop, not a framework app.** `src/mijual/agent/` is ~3.1k lines
  across `loop.py` (338), `client.py` (495), `tools.py` (625), `citations.py` (411), `events.py`
  (290), `copy.py` (206), `instructions.py` (196), `declarations.py` (190), `figures.py` (164),
  `context.py` (76). changple5 is LangChain. **Expect to re-derive, not port** — that framing is
  `P9.S1`'s core question.
- **Why 「안녕」 refuses today.** The citation gate drops uncited sentences at the generation boundary,
  and the loop's fallback family is `검증 미통과 폴백` — literally the string the operator saw. Item 2
  above is the fix; the copy that replaces the refusal is design-round work.
- **The signed copy P9 supersedes** lives in `src/mijual/agent/copy.py` (`AGENT_INTRO_KO`,
  `REFUSAL_SENTENCES` with the five families, `REFUSAL_FALLBACK`), mirrored by
  `src/mijual/web/conversationstore.py::REFUSAL_FAMILIES`, and is documented in `docs/current/decisions.md`
  (the generation-boundary-gate record, the never-compute rule, the R6/R14 design rounds) and
  `docs/current/frontend.md` (the `/ask` surface, the 340px rail, `InlineCitation`, `Answer`).
- **Operator runtime is on file.** `docs/current/operations.md` §Operator Runtime is filled (not
  `UNFILLED`): `make stack-up`, **dev** mode, `http://127.0.0.1:3000` on this Mac plus the machine's
  Tailscale URL from other devices. Every P9 slice claiming real-browser verification verifies there,
  and additionally in the production build where the two differ.

### Doc impact

_One line per durable-truth change; `P9.REVIEW` consolidates these into doc versions on a pass._

- (`P9.DECOMP`) none — decomposition changed no durable truth.

## Operator Questions

_Questions only the operator can answer; every entry is routed at the review -- folded into the acceptance walkthrough (`accept-gate --open`) or filed with `defer-job`. An unrouted entry is a review finding._

- **(`P9.DECOMP`) Worst-case spend per anonymous turn.** Raising thinking `LOW` → `MID` *and* the turn
  ceiling from 6 to ~20 rounds multiplies the worst-case cost of a single turn on a surface that is
  **free, anonymous and unlimited by decision** (`decisions` D-13: 질문 수 무제한, no quota). The ▷
  ledger still prices every turn, but nothing caps a day. Is that acceptable as-is, or should P9 also
  land a cheap abuse backstop (e.g. a per-session or per-IP turn ceiling that is never shown as copy)?
  Only the operator can decide the money/product trade here.

## Constraints

## Open Questions

-
