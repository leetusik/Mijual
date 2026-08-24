# P9.S5 — calculator tool + calc block (result)

R16's headline element is on the wire. The agent now has a sixth tool, `calculate`, and a turn that
uses it puts a 계산 블록 on the reader's screen **at call time, with its inputs already drawn and
cited**, then replaces it in place with the result — or with a failure that reads as guidance.

## What landed

**The tool half.** One tool whose `op` enum is the namespace (S1B's 「one namespaced tool with an `op`
enum」): five named operations over `mijual.calc` — `allotted_shares` · `excess_subscription_cap` ·
`lapsed_warrants` · `d_day` · `lockup_release_date` — plus a clearly-labelled `expr` escape hatch. The
inputs **are** the arguments (`{key, label, value, display?, cite?}`), so the block is the call rather
than a description of it; a named op must receive exactly its own parameters, and its heading name is
the **server's** (`copy.CALC_NAMES_KO`) so 「검증된 계산 · {이름}」 always names the operation that ran.
Budget-exempt on the zero-I/O precedent. Errors are guidance: a call that is not a calculation is never
drawn at all (`계산 → 0건` + English guidance), and a drawn calculation that cannot run settles as
`error` whose `why` is the input that stopped it, in its own label and value.

**The escape hatch is an AST node whitelist over `Decimal`, never `eval`.** `ast.parse(mode="eval")`
then a recursive walk accepting only `Expression` · `Constant`(finite int/float) · `Name`(bound to a
declared input) · `UnaryOp`(±) · `BinOp`(+ − × ÷); every other node shape is refused **before its
operands are read**, so there is no call, attribute, subscript, comprehension or `**` in the picture.
Bounded at 160 characters and 48 nodes; non-finite constants/results and division by zero are refused.

**The surface half.** `CalcBlockEvent` (`mode: verified|expr`, `name`, `inputs` reusing `DataRow`,
`expr`, `result`, `state: pending|done|error`, `why`) is emitted by the loop from
`tools.calc_plan(call)` *before* `call_tool` runs and replaced on the same `block_id` from
`tools.calc_outcome(result)` — the same "ask the tools module about the shape" seam `P9.S3` used for
`value_rows`, so **no tool name enters the loop's control flow**. An input carrying a `cite` id becomes
a chip through the new `CitationGate.cite_ref()` (the one chip numbering, so 같은 근거 = 같은 번호
across prose · 데이터 행 · 계산 입력); one carrying none is the reader's value and gets the 「입력」
marker. The result carries no citation, so it is **not counted in 근거 N건**.

**S4's deliberate gap closed.** The result node is figure-shaped (`value` + `estimated`), so
`CitationGate.learn` harvests it — and the inputs — into the turn's traceable values. Restating 「200주」
in prose now carries **no 「미확인」 span**, and a reader-typed 「1,000주」 stops being marked the moment it
goes through the calculator. Nothing about the membership check was weakened to get there.

Every decision, its reason, and the interim mismatches `P9.S7` closes are recorded in
`works/phases/active/P9/phase.md` → **`### P9.S5` — the calculator landed** (14 numbered notes).

## Files

- `src/mijual/agent/tools.py` — the calculator: `CALC_TOOL` · `EXPR_OP` · `BUDGET_EXEMPT` · `CalcOp` /
  `CALC_OPS` · `CalcInput` · `CalcPlan` · `calc_plan()` · `calc_outcome()` · `calculate()` · the AST
  evaluator; `TOOL_NAMES` and `STATUS_PHASE` gain the sixth tool; `call_tool` dispatches it
- `src/mijual/agent/declarations.py` — the `calculate` spec (op enum, structured `inputs`, the P11
  「when *not* to use me」 paragraph); `_schema` gains `enum` and `items`
- `src/mijual/agent/loop.py` — `_calc_pending` / `_calc_settled`, the `pending → done|error` emission
  in `_execute`, and the budget exemption (`_Turn.billed` beside `tool_calls`)
- `src/mijual/agent/events.py` — `CalcBlockEvent`, `CALC_MODES`, `CALC_STATES`
- `src/mijual/agent/citations.py` — `CitationGate.cite_ref()`
- `src/mijual/agent/copy.py` — `CALC_ROW` / `CALC_MISS_ROW` / `CALC_NONE_ROW` (composed tier, each
  transcribed from the round's own reference implementation), `CALC_NAMES_KO`, `CALC_UNITS_KO`
- `src/mijual/agent/__init__.py` — exports `calculate`; the 「five tools」 line
- `tests/test_agent_tools.py` — `test_the_calculator_is_a_window_onto_calc_and_never_an_evaluator`
- `tests/test_agent_loop.py` — `test_the_calculation_block_is_drawn_before_the_number_exists`,
  `test_a_calculation_fails_as_guidance_and_costs_no_tool_budget`, the `computes()` helper
- `tests/test_web_ask.py` — `test_a_calculation_is_stored_once_in_the_state_it_settled_in`, `CALC_TURN`
- `works/phases/active/P9/phase.md` — S5 notes, 4 Doc impact lines, 2 Operator Questions

## Validation

| command | outcome |
| --- | --- |
| `.venv/bin/python -m pytest tests/` | **pass** — 148 passed (144 before; +4 new cases) |
| `.venv/bin/python -m pytest tests/test_agent_tools.py tests/test_agent_loop.py tests/test_web_ask.py` | **pass** |
| `cd frontend && npm run typecheck` | **pass** — no frontend file changed (the wire stays additive) |
| `cd frontend && npm run smoke` | **pass** — 16/16 |
| `cd frontend && npm run build` | **pass** |
| `python3 scripts/workflow.py validate` | **pass** |

The AST-scan invariants are green inside that suite: `test_the_agent_package_imports_no_spending_module`
(the new `from mijual import calc` is pure stdlib arithmetic and no spending module), plus the two
`mijual.web` scans. `mijual.calc` is untouched — the tool is a window onto it, not a second
implementation.

**Not verified in a browser, deliberately.** Nothing renders a `calc` frame yet (`lib/ask.ts`'s
`switch` ignores unknown events by design — `P9.S8` adds the store case and `P9.S9` draws the block),
so a real-browser claim would be untestable here. The build-prompt §4 checks 4–6 are verified at the
event and payload level in this slice — 입력 2행(하나는 「입력」, 하나는 칩) · 식 한 줄 · 결과 「200주」 ·
푸터가 계산을 세지 않음 (check 4), same `block_id` replacement with the inputs carried through
(check 5), and 확정 발행가액 미공시 → `error` + the record's own row (check 6) — and re-verified in the
flesh by `P9.S11`.

## Deviations from `plan.md`

1. **Four files beyond the plan's three.** The plan names `declarations.py`, `tools.py`, `loop.py`;
   landing them also needed `events.py` (the event), `citations.py` (the 6-line `cite_ref()` — the chip
   numbering keeps exactly one owner, `P9.S3`'s rule), `copy.py` (the row formats and op names) and
   `__init__.py` (export + docstring). All inside the slice's own intent.
2. **Five ops, not the eleven listed.** The plan says to choose "the subset that makes sense as
   reader-facing product truth". The ▷ 추정 family (`warrant_intrinsic_value`,
   `warrant_intrinsic_value_floor`, `lapsed_warrant_value`, `implied_reference_price`) is excluded
   because R16 §2.5 closes the marker family at three **exclusive** markers and a ▷ value returned as
   「계산」 would lose its 추정 mark; `window_state` has no signed Korean; `add_months`'s product instance
   is `lockup_release_date`. Reasons and the resulting Operator Question are in `phase.md`.
3. **Three server-side Korean row formats** (`계산 → {name} · {expr}` · `계산 → {why} · 0건` ·
   `계산 → 0건`) plus five op names and one unit, all in `copy.py`'s **composed** tier as the plan's
   constraint directs (「if any string must originate server-side, follow S3's precedent … and record
   the decision」). Nothing is invented: the two calculation rows are transcribed from the round's own
   `output/r16-parts.babel.js` (`계산 → 초과청약 한도 · 1,000주 × 0.2주 = 200주` and
   `계산 → 확정 발행가액 미공시 · 0건`, both of which this composes byte for byte), `계산 → 0건` follows
   `EVENT_MISS_ROW`'s existing 0건 idiom, each op name is traced to the product's own existing word in
   the constant's docstring, and 주 is R4's signed share unit. A tool row is required because
   `ToolResult` has one and the record's own calculation fixture shows three tool rows including 계산.
4. **`declarations._NEVER_COMPUTE` left untouched.** Its last clause (「never recompute, re-derive or do
   arithmetic on it」) now reads as a ban on feeding tool values to the calculator, but S1 recorded that
   the never-compute statements 「move together or not at all」 and `P9.S7` owns that pass. The
   calculator's own description states the boundary in the meantime; flagged in `phase.md` note 14.
