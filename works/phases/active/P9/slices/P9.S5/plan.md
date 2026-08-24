# P9.S5 — calculator tool + calc block

## Context

Build item 3 — the auditable calculator, R16's headline element (P7). Binding spec: `works/phases/active/P9/phase.md` → `### DECOMP2` → **`P9.S5` — the calculator** (read in full), plus `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` §0 (calc vocabulary — server side emits data; the Korean render strings land client-side in S8/S9), §1 (`CalcBlockEvent` schema: `block_id`, `mode: verified|expr`, `name`, `inputs` [DataRow schema], `expr`, `result`, `state: pending|done|error`, `why`), §2.4 (block behavior: appears at call time with inputs, in-place `pending → done|error`, result not counted in 근거 N건). Read the `### P9.S3` and `### P9.S4` decision sections in `phase.md` and both slices' `result.md` — you inherit the block/storage seams (`absorb` is already generic; `value_rows()`/`ValueRow` exist in `tools.py`; `cite()` is the one chip numbering; S4 deliberately left a reader-typed figure untraced *until the calculator returns it*).

## Scope

1. **One namespaced tool** in `src/mijual/agent/` (`declarations.TOOL_SPECS` + `tools.TOOL_NAMES` + `call_tool`): an **`op` enum** over `mijual.calc`'s named operations — draw from the real module (`d_day`, `window_state`, `allotted_shares`, `excess_subscription_cap`, `add_months`, `lockup_release_date`, `lapsed_warrant_value`, `lapsed_warrants`, `implied_reference_price`, `warrant_intrinsic_value`, `warrant_intrinsic_value_floor`) — choosing the subset that makes sense as reader-facing product truth, plus a clearly-labelled **`expr` escape hatch**: `ast.parse(mode="eval")` + node whitelist over `Decimal`. **Never `eval`**; `literal_eval` is not an arithmetic evaluator.
2. **Budget-exempt** (the zero-I/O precedent) — the calculator never burns tool-call budget. Errors read as guidance (`why` strings are data; the signed Korean error template renders client-side), never tracebacks. "When *not* to use me" goes in the tool description (P11): don't restate a number a tool already returned.
3. **Surface half**: `CalcBlockEvent` (extends S3's persistent-block machinery — same `block_id` replacement, generic storage already handles it): emitted **at call time with inputs already drawn** (`pending`), replaced in place with `done` (result carries `figures.with_display`-ready values) or `error` + `why`. `mode: verified` for named ops, `expr` for the escape hatch — never rendered identically (§3-7). Inputs reuse the DataRow row schema: reader-supplied values get `reader_input: true` (the 「입력」 marker), filing values carry their citation via `cite()`. A calculation result is **not** counted in 근거 N건.
4. Close S4's deliberate gap: a figure the calculator returns becomes traceable (enters the gate's `_values` via `learn`), so restating a computed result in prose is no longer flagged 미확인.

## Constraints

- RESPECT THE DESIGN; no new Korean copy server-side beyond what §0 signs for the server (check: §0 puts calc vocabulary in `frontend/components/ask/copy.ts` — if any string must originate server-side, follow S3's precedent of signed-copy-in-`agent/copy.py` and record the decision).
- The AST-scan invariants must stay green — the agent still derives no number except through this tool; `mijual.calc` stays the LLM-free home of money math (the tool is a window, not a second implementation).
- Wire-additive; both views keep working (calc block rendering is S9's).
- Terse tests; full suite + typecheck + smoke + `python3 scripts/workflow.py validate`.
- Doc impact + durable notes to `phase.md`; `result.md`; structured verdict. Never commit or transition state.
