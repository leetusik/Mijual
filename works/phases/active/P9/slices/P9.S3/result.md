# P9.S3 — result

R16 build-prompt §1 landed end to end: the event vocabulary, block ids with in-place replacement
(P10), and both signed contract changes. Nothing in this slice draws anything — the two views are
untouched and keep rendering exactly as before, because every new frame kind is ignored by
`lib/ask.ts`'s `switch (frame.event)` (`default: return turn`) and every old frame's payload is
byte-identical to yesterday's.

## What changed

**`src/mijual/agent/events.py`** — `AgentEvent` gains keyword-only `block_id` / `persistent`, and
`_block_fields()` puts them on the wire **only when `block_id` is set**, so pre-R16 frames are
unchanged. New `StatusEvent` (transient, `phase` validated against the new `STATUS_PHASES`, carrying
its signed sentence), `DataRow` (the row schema §2.3 fixes, shared with `P9.S5`'s calc inputs) and
`DataBlockEvent` (`rows`, optional `title`). `TextEvent` gains `unverified` spans — **field only**,
always empty until `P9.S4`, therefore never on the wire. `RefusalEvent`'s docstring moves to the
6-value whitelist. `TurnEnd`: `blocked` re-documented as *removed markers*, and a new `filings` count
for D8's 「공시 M건 읽음」.

**`src/mijual/agent/copy.py`** — `STATUS_KO`, the five D5 phrases, **verbatim** from build-prompt §0.
No other Korean was added anywhere in this slice.

**`src/mijual/agent/loop.py`** — the emission points. One live status line (constant `block_id`,
replaced per phase, silent once anything is released): `read` on round 1, `write` on every later
round, and the tool's own phase immediately **before** the call runs (the wait is the call). A
`DataBlockEvent` after each tool result that reads as label/value pairs, its rows' chips allocated
from the citation gate's one numbering and emitted immediately before it. `_filings_read()` counts
filings whose contract a tool actually returned.

**`src/mijual/web/ask.py`** — `_Released.absorb` keeps **any** persistent event with a `block_id`,
storing `event.frame()` keyed by that id, so a `pending → done` replacement stores one block in its
final state and `P9.S5` needs no second storage change; `_persist` passes them to `record_turn`.

**`src/mijual/web/conversationstore.py`** — `REFUSAL_FAMILIES` → six values (보안 added; 계산 요청 and
검증 미통과 폴백 kept read-only for past rows), `record_turn(blocks=…)` storing them verbatim (NULL
when there are none), and the error message that named 「five signed families」 now names six.

**`src/mijual/db/models.py`** — `ConversationTurn.blocks`, a **nullable, default-free** `JSONBody`
column, exactly the shape `schema_sync.ensure_columns` accepts (no Alembic — N16).

**`frontend/components/ops/copy.ts`** — `REFUSAL_CATEGORIES_KO` mirrors the six values in the same
order, with why the two retired ones stay in the filter.

Two files beyond the plan's list, both inside its intent and recorded as deviations below:
`agent/citations.py` (public `cite()`) and `agent/tools.py` (`ValueRow`, `value_rows()`,
`STATUS_PHASE`).

## Validation

| command | outcome |
| --- | --- |
| `.venv/bin/python -m pytest tests/ -q` | **pass** — 144 tests, including the three AST-scan invariants (`test_agent_tools.py::test_the_agent_package_imports_no_spending_module`, `test_web_smoke.py::test_no_request_path_module_imports_a_spending_module`, `…::test_the_model_is_reached_only_through_the_agent_package`) |
| `cd frontend && npm run typecheck` | **pass** |
| `cd frontend && npm run smoke` | **pass** — 16/16 |
| `cd frontend && npm run build` | **pass** (the generated `next-env.d.ts` it rewrites was restored, and typecheck re-run clean) |
| `python3 scripts/workflow.py validate` | **pass** |
| additive-column check (ad-hoc, `ensure_columns` against a live table holding a row) | **pass** — added once, idempotent on a second run, the existing row untouched and reading `blocks = NULL` |

Test changes are terse and all in existing suites: one new case in `tests/test_agent_loop.py` (the
status line's phases/id/transience and the data block's rows + shared chip number), the frame-sequence
and stored-row assertions in `tests/test_web_ask.py`, and the six-family count + block-storage
assertions in `tests/test_web_conversations.py`.

**Not claimed: real-browser verification.** This slice adds no visible element — the elements are
`P9.S9`'s — and its rendering claim ("a turn today renders identically") is structural: today's client
ignores unknown event kinds and no existing payload changed. The Operator Runtime sweep belongs to
`P9.S11`, with one interim effect it should confirm rather than rediscover: data-row chips are
*defined* from now on but not *drawn* until `P9.S9`, so 「근거 N건」 (counted client-side from
`turn.chips.length`) can exceed the visible chip count until that slice lands. The record signs the
end state (fixture ②: three data rows, prose citing one, 근거 3건).

## Deviations from `plan.md`

1. **Two files beyond the seven listed.** `agent/citations.py` gained a 6-line public `cite()`: a data
   row's chip must come from the *same* numbering as prose (같은 근거 = 같은 번호, R6-4), and the
   allocator has exactly one owner — reaching into `_number_for` from the loop would have opened a
   second. `agent/tools.py` gained `ValueRow` + `value_rows()` + `STATUS_PHASE`: payload-shape
   knowledge belongs beside `citations_in`, and keeping it out of `loop.py` is what preserves the
   loop's 「no tool name in the control flow」 property. Both are additive and covered by tests.
2. **`StatusEvent` carries its sentence, not only its phase.** §1's table names one field; §0 signs
   `STATUS_KO` in `copy.py`, server-side. Carrying the text keeps one copy of a signed string instead
   of two (the repo's existing convention for 도구 행 and 거절 문장). `P9.S8`/`P9.S9` render
   `frame.data.text`; no status strings go into `components/ask/copy.ts`.
3. **A data row exists only where the server can state its value without inventing a format.**
   추후결정 · `value_display` · a scalar · a `{start_date, end_date}` period written `start ~ end`
   (the format `components/event/Fields.tsx::Period` already renders). Composite shapes — 청약 취급처
   목록, 발행가액 산식, 콜·풋 스케줄 — get **no row**, because rendering them server-side would fork
   the product's field surface. Recorded in `phase.md` as `P9.S9`'s inheritance, with the two honest
   options (server-side vocabulary, or a typed row schema — the latter is a design change).
4. **The ops read side is untouched** — `blocks` is stored but not served, so R7's row shape and its
   test are unchanged and the `P9.DECOMP2` Operator Question (payload-only / undesigned dump / later
   round) stays the operator's to answer.

## Notes appended to `phase.md`

A `### P9.S3 — the contract slice landed (2026-08-25)` section: the frame sequence a real turn now
produces, thirteen numbered decisions later slices inherit (the kw-only base fields, the status id and
its partial tool→phase map, the `value_rows` producer seam and its stated-value rule, the shared chip
numbering and its 근거 N건 consequence, `filings`, the generic block storage and the `ToolRowEvent`
trap it implies, the additive column, the untouched ops read side, the six-value vocabulary and who
retires the two), plus the deviation note. Three **Doc impact** lines (`api`, `architecture`,
`decisions`) were added to the running list for `P9.REVIEW` to consolidate. No new Operator Questions:
the seams this slice opened are build decisions for `P9.S9` / `P9.S11`, not operator ones.
