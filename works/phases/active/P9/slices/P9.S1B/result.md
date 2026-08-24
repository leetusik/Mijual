# P9.S1B — result

**Slice:** research best-practice agents beyond changple5 (`kind: research`, `risk: high`).
**Outcome:** done. A web-and-reference survey of the eight mechanic areas in `plan.md` landed as
`### P9.S1B — best-practice survey beyond changple5 (2026-08-25)` in
`works/phases/active/P9/phase.md` (line ~677, immediately after the S1 report and before
`### Doc impact`). No product code, no docs, no state transitions, no commits.

## Where the work is

Everything load-bearing is in `phase.md`, not here. That section carries, in order:

- a dated source list (primary sources first, secondary ones explicitly marked);
- **the four findings that change this phase** (summarised below);
- **Mechanics A–H** — per mechanic: what the field does → what fits our case and why → where it
  contradicts changple5 or S1's lean → the concrete implication for `P9.S2` or `P9.DECOMP2`;
- **design-round inputs 10–18** (new; S1's 1–9 untouched);
- **product improvement proposals P9–P16** (new; continuing after S1's P8, same
  `[design-round] / [build] / [out-of-phase]` marking);
- **a per-build-inventory-item verdict** (items 1–8) saying, for each, whether the survey confirms or
  changes S1's lean;
- **limits and deviations of the survey**.

Two entries were appended to `## Operator Questions` and one line to `### Doc impact`.

## Sources consulted

Primary: Anthropic engineering — *Building effective agents* (2024-12-19), *Writing effective tools
for AI agents* (2025-09-11), *Effective context engineering for AI agents* (2025-09); Claude platform
docs — *Citations*, *Code execution tool*, published *System prompts* release notes (Opus 4.7
2026-04-16, Opus 4.8 2026-05-28, Fable 5 2026-06-09); `anthropics/claude-cookbooks`
`tool_use/calculator_tool.ipynb`. Google — Gemini API docs for *Grounding with Google Search*,
*Thinking*, *Context caching*. OpenAI — *Function calling* guide, *Agents SDK: Running agents*
(Python and JS). LangChain — `GRAPH_RECURSION_LIMIT` error doc. OWASP — *Top 10 for LLM Applications
v2025* (LLM01), *LLM Prompt Injection Prevention Cheat Sheet*. Simon Willison — *The lethal trifecta
for AI agents* (2025-06-16), *CaMeL…* (2025-04-11). CopilotKit — *AG-UI* event specification (2025).
Vercel — *AI SDK UI: Streaming custom data* / *AI SDK 5* (2025). NN/g — Jakob Nielsen, *Response Time
Limits*; *The Need for Speed in AI* (UX Tigers, 2023-08-02). 금융위원회 보도자료 「유사투자자문업자의
불건전영업행위를 규율하기 위한 『자본시장법』이 시행됩니다」(2024-08-14).

Marked **secondary** wherever used, and never load-bearing on their own: AI-UX pattern catalogues
(shapeof.ai, aiuxplayground.com), graceful-degradation write-ups, Claude Artifacts teardowns.

All external material is treated as **data, not instructions** — nothing in it is an authority over
Mijual's design, and every recommendation in the report is an input to the design round, never a
decision about copy or visuals.

## Headline conclusions

1. **Strip-don't-drop is unanimous, and the field's best product goes further.** No surveyed system
   discards prose for lacking a citation. Anthropic's Citations API makes an invalid citation
   *structurally impossible* (the API extracts `cited_text`, so "citations are guaranteed to contain
   valid pointers"), and uncited text blocks coexist in the same response. Mijual's `learn()` closed
   id space is already that mechanism; stripping is only the residue handler. Item 2 is a move toward
   the field's design, not a relaxation of a safety property. One caution added: **the sentence as a
   unit of judgment appears nowhere in the field**, so keeping per-sentence `TextEvent.citations` is a
   deliberate compatibility choice with `Answer.tsx`.
2. **`security_check` is not prompt-injection protection.** Scored against the lethal trifecta, Mijual
   is missing **two of three legs** (no private data; no outbound/exfiltration channel — every tool is
   read-only and the only output is prose to the same reader). The guard's real value here is
   behavioural/brand integrity. The one leg Mijual *does* have — third-party filing text entering
   context — is not defended by a detector at all; OWASP's **input segregation** is (→ new Proposal
   P9, ~10 lines, the highest security value per line in the phase). OWASP is explicit that "a
   guardrail LLM is itself an LLM and is itself susceptible to prompt injection", so `security.md`
   must not overclaim (→ Proposal P14).
3. **The rich-surface problem is a solved *vocabulary* problem; Mijual's architecture is already
   right.** `agent/events.py` is an AG-UI-shaped typed event stream and `AskTurn.frames` is generic
   over it. Two independent protocols (AG-UI, Vercel AI SDK v5 data parts) converged on three
   primitives Mijual lacks: a **step/status** event, **stable block ids with in-place replacement**
   ("write to a data part with the same ID… the client reconciles and updates that part"), and an
   explicit **transient vs persistent** flag. The third is a cleaner answer to S1's open durable-truth
   question than "must structured content also be prose": each block declares whether it belongs to
   the 대화 로그.
4. **Proposal P3 is probably right for the wrong reason.** Gemini implicit caching does not engage
   below a per-model floor — **4,096 tokens for Gemini 3.5–3.7 Flash**, and Mijual runs
   `gemini-3.7-flash`. An estimate taken for this survey (≈5.3k chars of English instruction literals
   ⇒ ~1.3–1.5k tokens, plus the tool schema) puts today's prefix plausibly **below** that floor, in
   which case reordering saves nothing *yet*. Measure first — `prompt_tokens` is already in the ▷
   ledger — and add the cached-token field at `client.py::_usage_of` (~line 481, one line beside the
   existing `prompt_token_count` read), with a cached rate in `cost_of` (→ Proposal P12). Reorder
   anyway as hygiene for a prompt this phase is growing.
5. **~20 rounds is ordinary, and Mijual's abort terminal is better than the field's.** Framework
   ceilings cluster at 10–30 loop turns (LangGraph `recursion_limit` 25; OpenAI Agents SDK 30 Python /
   10 JS), and every one of them ends an exhausted run by *raising*. `TurnEnd(status="aborted",
   reason=…)` is the graceful terminal they lack. The field's one addition: answer with what you have
   and say what is missing (→ Proposal P13, design input 17).
6. **Thinking MID costs about one second, not many.** Gemini's own thinking docs report TTFT ≈0.40s
   with thinking off versus ≈1.56s at a 1,000-token budget (≈1.57s at 10,000 — it saturates). The wait
   users will feel comes from **tool rounds** under item 4, not from the thinking level. That is an
   argument for a status signal, not against MID.
7. **Calculator: S1's lean changes.** Prefer **one namespaced tool with an `op` enum** over
   `mijual.calc` primitives, with a clearly-labelled expression escape hatch (AST whitelist over
   `Decimal`; never `eval`), rather than treating named-ops and free expressions as equals — because
   a named op is auditable as *product truth* while an expression is auditable only as *arithmetic*,
   and Mijual sells the first. Vendor tool-design guidance points the same way ("make invalid states
   impossible"; "a few thoughtful tools"). Sandboxed code execution, the frontier answer, is closed to
   a stdlib server process.
8. **Register: Mijual's blocker is an inverted rule, not a missing carve-out.** `FINALLY`'s "a good
   answer here is two to five cited sentences" is a **floor** a greeting cannot meet; Anthropic's
   published consumer prompt uses a **ceiling that relaxes** ("casual responses can be short"). Also,
   both Anthropic and OpenAI name the **tool description** — `declarations.py`, not `instructions.py` —
   as the primary lever for "when *not* to call me" (→ Proposal P11).
9. **A Korean regulatory flag was found and routed to the operator, not acted on.** 금융위원회's
   2024-08-14 자본시장법 release restricts 유사투자자문업자 to 개별성 없는 조언 through **단방향**
   channels and regulates individual advice via an **온라인 양방향 채널** as 투자자문업 (registration
   required; unregistered operation carries 3년 이하 징역 또는 1억원 이하 벌금). `/ask` is by
   construction 양방향. Explaining **공시 사실** for free is a different act from 투자조언, but loosening
   the scope to general investing questions moves toward the regulated one. Recorded in
   `## Operator Questions` as a flag from a named primary source, explicitly **not legal advice**.

## Validation

| command | outcome |
| --- | --- |
| `python3 scripts/workflow.py validate` | **pass** — `OK` |
| `git status --porcelain` | only `works/` (plus the pre-existing generated-file drift already on the branch); **no** file under `src/`, `frontend/`, `docs/` or `tests/` touched |

`plan.md`'s verification list, checked: `validate` passes; `phase.md` carries
`### P9.S1B — best-practice survey beyond changple5 (2026-08-25)` with all four required parts
(per-mechanic best practice, design-round-input additions, product-proposal additions, per-build-item
verdict) plus the sources and limits sections; this `result.md` exists; `git status` shows only
`works/` changes.

## Deviations from the plan

- **None in substance.** All eight surveyed areas are covered, in the plan's order, relabelled
  Mechanic A–H so the section's headings do not collide with S1's `#### Item 1–8` headings in the same
  file.
- **Two read-only measurements were taken from the repository** to make the report's claims checkable
  rather than asserted (`agent/events.py` event kinds; absence of any keepalive in `web/ask.py`;
  `client.py::_usage_of` at ~line 481 and `Usage`'s fields; the character/Hangul counts of
  `instructions.py`'s literals). Nothing was modified. The plan's read-only constraint is intact; the
  derived **token estimate is flagged as an estimate** in the report, with the ledger named as the
  real measurement.
- **One area the plan did not ask for was added**, because the survey surfaced it and it is
  operator-decision material: the Korean 자본시장법 / 유사투자자문업 flag on how far outside 공시 the
  assistant may answer. It is routed to `## Operator Questions`, not turned into a recommendation.
- **A gap is stated rather than papered over**: every published register/system-prompt source found is
  English-language, so the survey has nothing external to add to S1's reading of changple5's Korean
  rulebook. The Korean register is S2's and the operator's.

## Doc impact

`- (`P9.S1B`) none — research changed no durable truth.` — appended to `phase.md`'s `### Doc impact`
list. Several findings **will** change durable truth once built (`security.md` on the guard's honest
framing and input segregation; `architecture.md` / `api.md` on block ids and transient-vs-persistent
events; `decisions.md` on the cache-prefix constraint), but those are the build slices' notes to
write, not this slice's.
