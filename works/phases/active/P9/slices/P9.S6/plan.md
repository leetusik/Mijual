# P9.S6 — security_check guard: detector tool, after-model hard reject, 「보안」 family, Q-D logging

## Context

Build item 5. Binding spec: `works/phases/active/P9/phase.md` → `### DECOMP2` → **`P9.S6` — the guard** (read in full), plus `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` §1's "보안 하드 리젝트 위치" paragraph and §4 check 11. Read the `### P9.S3`–`### P9.S5` decision sections in `phase.md` and S5's `result.md` — S5 just rewrote `tools.py`/`declarations.py`/`loop.py` (there is now a `BUDGET_EXEMPT` set, a `calc_plan`/`calc_outcome` seam, a separate `billed` counter, and the tool count is six); build on the current tree, not on pre-S5 shapes.

Honest framing (S1B, proposals P14): this guard is a **behavioral/brand-integrity layer**, not prompt-injection protection — Mijual's structural properties (read-only tools, no private data, no outbound channel) are the real defense, and the security-doc wording at review must say so. Input segregation (P9) is S7's, not yours.

## Scope

1. **Detector tool** `security_check(category, excerpt)` added to `declarations.TOOL_SPECS` + `tools.TOOL_NAMES` + `call_tool`: the docstring/description *is* the trigger spec (role-hijack, prompt/system extraction, instruction override, off-product persona requests); the body is a defensive no-op. **Anti-over-trigger** belongs in the description (P11): a question *about* filings, confidentiality clauses appearing *inside filing text*, or ordinary meta questions about 미주알 are never triggers — filing content is data, not the reader speaking. Budget-exempt (S5's `BUDGET_EXEMPT` precedent) so a guard call never eats the turn's tool budget.
2. **Hard reject** in `loop.run_turn`: right after `model.stream(...)` returns and `calls` is collected, **before `_execute`** — if any call names `security_check`: no tool of that round runs, no `ModelMessage` is appended, emit `RefusalEvent(family="보안")` carrying D3's signed sentence (「그 요청에는 답변하지 않습니다. 공시에 대한 질문은 언제든 받습니다.」 — this is the slice that lands it in `agent/copy.py`'s live producer mapping, joining S4's `LIVE_REFUSAL_SENTENCES` split), end the turn. The model gets no second chance. §4 check 11's shape: 보안 sentence only — no tool rows, no chips, no links, no mention of a check, no extra prose in the turn.
3. **Q-D logging**: category + 200-char excerpt + `session_hash`, **log-only** (Python logging), no DB row. The stored conversation row records the turn like any refusal turn (family 보안 is already in S3's whitelist and the ops mirror).
4. Wire/storage: `RefusalEvent` family 보안 flows through the existing paths (S3 made the whitelist six-valued); verify `record_turn` accepts it end to end.

## Constraints

- RESPECT THE DESIGN: D3's sentence verbatim from build-prompt §0; no other new Korean. The reader never learns a check happened — no copy anywhere says so.
- Check S4's live/retired family split when adding 보안 as a producer: `copy.family_of`, `_family_at_head`, `_is_family_prefix` must recognize it (decide deliberately whether a model-typed 보안 sentence should be recognized as a family head, and record the decision).
- Terse tests; full suite + typecheck + smoke + `python3 scripts/workflow.py validate`.
- Doc impact + durable notes to `phase.md`; `result.md`; structured verdict. Never commit or transition state.
