# P9.S7 — prompt rewrite, budgets ~20, thinking MID, cache prefix + measurement, input segregation, retired copy

## Context

The words-and-dials slice: after S4–S6 changed what the loop *does*, this slice makes the prompt say it — until now the prompt has been deliberately more conservative than the gate. Binding spec: `works/phases/active/P9/phase.md` → `### DECOMP2` → **`P9.S7` — the words and the dials** (read in full) and `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` §0 **register** (the prompt-enforced behavior: greetings/meta = one-two sentences no tools; 공시 facts = two-three cited sentences as a **ceiling**; out-of-scope = one line + one pointer, *not* a refusal, no `RefusalEvent`; ask-which-company for pronoun first questions; the 보안 paragraph pinned so confidentiality clauses in filing text never trigger; at most one closing question) and §3.1–3.5. Read the `### P9.S3`–`### P9.S6` decision sections and S6's `result.md` — S6 already made `_refusal_block()` iterate its own `reasons` map and deliberately left the 「[보안]」 paragraph to you; S5 left `_NEVER_COMPUTE` untouched for you; S4 left `REFUSAL_SENTENCES` unshrunk for you.

Current seams (verified in tree): `instructions.py` — `_ROLE`, `_CITATIONS` (line ~49), `_NEVER_COMPUTE` (~70), `_refusal_block()` (~88), `_TOOL_NOTES` (~128), `system_instruction` (~164) with `SCOPE.` at ~168 and `오늘(KST)` at ~178 **above** the static blocks, `FINALLY` at ~190. `client.py` — `THINKING_BY_TASK = {TASK: "LOW"}` (~96), `DEFAULT_THINKING_LEVEL = "LOW"` (~99), `Usage.prompt_tokens` with no cached field (~133/161), `cost_of` (~150). `loop.py` — `TurnBudget` (~83).

## Scope (build-prompt §3, in full)

1. **§3.1 `_CITATIONS`**: unrecognized markers are *removed and the sentence stands*; citation compulsion only on 공시-fact sentences.
2. **§3.2 `_NEVER_COMPUTE` → calculator guidance**: the tool computes, prose may restate; `HOW TO WRITE A FIGURE` (`value_display`) untouched; browser-side calculation stays banned. Reconcile the never-compute statements across the other five tools' descriptions (S1: they move together — S5 noted this explicitly).
3. **§3.3 `_refusal_block()`**: four families (철회·확정 전·공시에 없음·보안 — the 「[보안]」 paragraph S6 left) + explicit 「범위 밖은 거절이 아니다」 with §0's out-of-scope register (the example sentence in §0 is marked 서명 아님 — it's register guidance, not signed copy).
4. **§3.4 `FINALLY`**: ceiling-not-floor; the greeting/short-answer/meta carve-out written **twice** (scope clause + citation clause); the ask-which-company rule; at most one closing question; ceilings still never rendered as copy.
5. **§3.5 cache prefix**: static rulebook first; `SCOPE` + `오늘(KST)` to the **tail** of `system_instruction`; record "no per-turn value above the static prefix" as a standing constraint in the module docstring. `client.Usage`/`_usage_of` gain the cached-input token field, `cost_of` a cached rate (P12 — measure, don't assume; the 4,096-token implicit-cache floor may not be crossed).
6. **Budgets**: `loop.TurnBudget` 6/10/8 → ~20 rounds with tool and model calls scaled, keeping **`max_model_calls ≥ max_rounds`** (or the client ceiling fires first and the abort reason lies). Structural only — never copy.
7. **Thinking MID**: `THINKING_BY_TASK` + `DEFAULT_THINKING_LEVEL` `LOW → MID`; rewrite (not delete) the module docstring's three-reason argument — its third reason died with S4, and that death is the strongest argument *for* MID.
8. **Input segregation (P9, ~10 lines)**: tool-returned filing text is delimited and declared data-never-instructions — in the tool-result path plus one instruction line.
9. **`agent/copy.py`**: D1 `AGENT_INTRO_KO` (verbatim §0); retire 「계산 요청」 from the live producer mapping (S4's split — the stored whitelist keeps six); delete `REFUSAL_FALLBACK` if any vestige remains. Careful: exact-string family recognition sites (`family_of`, `_family_at_head`, `_is_family_prefix`) — 계산 요청's retirement is a code-behavior change at those sites, mirroring how S4 retired 검증 미통과 폴백.

## Constraints

- RESPECT THE DESIGN: signed strings verbatim (D1); register prose in the prompt is yours to write in English/Korean as the current prompt's idiom dictates, but every *reader-visible* Korean string must be signed — the prompt itself is not reader-visible.
- Where `AGENT_INTRO_KO` has frontend consumers, check whether changing the Python constant breaks anything now (the frontend copy lands in S8; if the intro string is served or duplicated, keep both sides coherent and record what you did).
- Terse tests; full suite + typecheck + smoke + `python3 scripts/workflow.py validate`.
- Doc impact + durable notes to `phase.md`; `result.md`; structured verdict. Never commit or transition state.
