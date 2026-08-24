# Intent — P9

- Captured at: 2026-08-25T01:02:49+09:00
- Origin: operator

## Original Input (verbatim)

> ---
> 1. Make it gemini-3.7-flash mid2. no sentence lmitation with citation 3. Let it calcualte4. No hard limits.5. Add prompt injection tool like changple5/6. Suggest a better way of using this AI. ---Currently just saying "안녕" got "이 데이터는 검증을 통과하지 못했습니다. 검증되지 않은 내용은 해설하지 않습니다.내 종목 조회" and it shouldn't.This agent should be more like smart mijual assistant not rigid bot.Overall, you can follow how changple5 made its 일반 대화 mode chat agent. It's more like what I want. One phase, research slice comes first, then design, then decomp2.

Follow-up (same conversation, during plan review):

> and unlike changple5, we should also care about showing stuff on the chat surface. like showing data rows, or calculation results, etc..

## Confirmed Intent (refined + clarified)

Rebuild the AI 질문 agent (`src/mijual/agent/`) from a rigid grounded bot into **one unified smart Mijual assistant**, modeled on how changple5 built its 일반 대화 (default chat) agent (`~/projects/personal/changple5/apps/agent/app/chat/`). Concretely:

1. **Model:** keep `gemini-3.7-flash`, raise the thinking level LOW → **MID**.
2. **Citations — strip, don't drop:** retire the generation-boundary sentence-discarding gate. Valid citation markers still render as evidence chips; invalid or missing markers are stripped and the prose survives. The agent is still instructed to cite filing facts, but nothing is silently deleted. (This is why 「안녕」 currently gets the 검증 미통과 refusal — that must stop.)
3. **Let it calculate:** add a server-side **calculator tool** so derived numbers appear as an auditable tool row, *and* stop discarding sentences that compute, convert, or restate numbers in prose.
4. **Budgets — generous ceilings, not unlimited:** raise the per-turn limits (today 6 rounds / 10 tool calls / 8 model calls) high enough that no real conversation ever hits them (order of ~20 rounds), keeping a backstop against a runaway loop spending money.
5. **Prompt-injection guard:** add a changple5-style `security_check` tool bound to the model as its detection signal, with an after-model hook that hard-rejects the turn with a fixed Korean refusal.
6. **Unified conversational behavior:** the assistant chats naturally (greetings, general questions, meta questions about 미주알) and grounds filing facts with tools and citations when it uses them. The five rigid R6 refusal families are relaxed/retired — superseding that signed copy goes through the design round.
7. **Rich chat surface (unlike changple5):** the conversation surface should **show structured content**, not only prose — data rows, calculation results, and similar display elements rendered as UI in the thread. Today the surface has only mono tool fact rows and citation chips; what these elements look like is a core subject of the design round.
8. **Suggest better ways of using this AI:** the research and design slices should actively propose product improvements, not just port changple5's mechanics.

**Phase shape (operator-specified):** one phase. The **research slice comes first** (study changple5's 일반 대화 agent and report what transfers to Mijual's non-LangChain stdlib loop), **then the design co-work round(s)**, **then `P9.DECOMP2`** cuts the build slices — the design-cowork mixed-phase pattern.

## Clarifications Resolved

- Q: How should citations work after removing the sentence-drop gate? — A: **changple5-style strip-don't-drop** — valid markers render as chips, uncited prose survives, agent still instructed to cite filing facts.
- Q: How should calculation work — free prose, a calculator tool, or both? — A: **Calculator tool + free prose** — auditable tool rows for derived numbers, and no sentence-discarding for prose arithmetic.
- Q: "No hard limits" — remove budgets entirely or raise them? — A: **Generous ceilings** — high enough no real conversation hits them, kept as a runaway-spend backstop.
- Q: One unified assistant, or two modes like changple5 (일반 대화 + consulting)? — A: **One unified assistant**; refusal families relaxed/retired via the design round.
- Interpretation confirmed via plan approval: "gemini-3.7-flash mid" = thinking level **MID**; "prompt injection tool like changple5" = changple5's **`security_check`** guard tool + after-model hard-reject (`apps/agent/app/chat/security_guard.py`).

## Notes

- The research slice should read changple5's `apps/agent/app/chat/` — `agent.py`, `citations.py` (marker stream parsing, strip helpers), `security_guard.py`, `budget.py`, prompts — and report what transfers to Mijual's stdlib loop (`mijual.agent.loop` / `client` / `citations`).
- Superseded signed design decisions (R6 refusal families, never-compute rule, the 검증 line in the `/ask` rail, agent intro copy) must be superseded by new signed design rounds, never silently edited — RESPECT THE DESIGN applies until then.
- The agent remains the system's only in-request LLM spend; the ▷ per-turn ledger stays.
