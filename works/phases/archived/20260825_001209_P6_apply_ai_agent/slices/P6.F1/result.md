# Result — P6.F1: thousands-grouped numerals in agent prose (3,200원)

Review finding 4, as the operator dispositioned it («make it 3,200원. dk how»).
The agent now speaks the product's own numerals: **3,200원 · 1,591원 ·
26,900,000,000원**, while 접수번호, dates, years, D-days and every verbatim quote
are byte-identical to what they were.

## The mechanism, in one paragraph

Two halves, one rule — **grouping is presentation, never computation**.

1. **The tool contract serves the reader's form.** New module
   `src/mijual/agent/figures.py`. `ToolResult.__post_init__` runs
   `figures.with_display(payload)`, which walks the payload and puts a
   **`value_display`** string beside every *figure*'s exact `value`
   (`"3200"` → `"3,200"`). "Figure" is the contract's own predicate: a node
   carrying **both** `value` and `estimated`, which is exactly what
   `present.values.Figure.payload()` and `present.event.FieldPayload.payload()`
   emit — so `rcept_no` (its own key), `countdown.days`, `dday`, `span`,
   `event_id`, `window` and every date are structurally not figures and are never
   touched. `grouped()` additionally refuses a value < 1000 (nothing to group) and
   a **14-digit** bare integer (that shape is a 접수번호 in this product; leaving
   one hypothetical 10조 amount ungrouped is cheaper than grouping one filing
   number). One line was added to the system instruction's NEVER COMPUTE block
   telling the model to write a figure as its `value_display` — and naming
   rcept_no/date/year/D-day as *not* figures.
   The key is `value_display`, **not** `display`: `FieldPayload` already uses
   `display` for its render mode (`"value"` / `"추후결정"`).
2. **The gate guarantees it at release.** `CitationGate.learn()` also builds
   `{as the payload writes it: as the reader reads it}` from the same figure
   nodes, and `_release()` runs `figures.regroup(text, table)` **after** every
   check has passed. It rewrites only a token that is *literally* a figure this
   turn's tools returned, only **outside** a 「…」/"…" span (one shared pattern:
   `citations._QUOTED` is now `figures.QUOTED_SPAN`, so the spans the gate
   verifies are exactly the spans the grouping refuses to touch), and never in a
   sentence released because it *is* a tool's own string (a locked
   `notice_ko`/`none_found_ko` is copy and leaves byte-exact). The token pattern's
   lookarounds are the requirement written as regex: not part of a longer number
   (`15.22`, an already-grouped `3,200`), not an ISO year (`2026-08-26`), not
   `2026년`, not the `3` of `D-3`.

**The never-compute gate is unchanged and stays structural.** Membership already
normalized separators (`_decimal` strips commas on both sides); that is now
*stated* in its docstring and beside the check — 3,200 and 3200 are one member,
and grouping can neither add a number to the traceable set nor remove one.
Because the check runs on what the model wrote and the respelling happens after,
an invented figure is still blocked in its raw form.

**What the log stores is what the reader saw**: the respelled string is what
`gate.released` appends, so `TurnEnd.answer` → `record_turn` carries `3,200원`
with no extra step. `TurnEnd.quotes` and the citation events come from
`Citation`s and were not touched at all. No signed format changed — fact rows and
the footer carry only counts and 접수번호, and neither goes through any of this.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **138 passed** (baseline 137 + 1 new case) |
| `python3 scripts/workflow.py validate` | green |
| live smoke — 2 turns, real `gemini-3.7-flash` | grouped prose, ▷ **$0.0107** estimated |

Frontend: **not touched**, so no `build`/`typecheck`/`smoke` was run. (`git status`
shows `frontend/next-env.d.ts` modified — a Next-generated file left dirty before
this slice began; no frontend command was run here and it was left alone.)

**New/updated cases** (terse, per the repo rule):

- `tests/test_agent_loop.py::test_a_figure_reaches_the_reader_grouped_and_a_quote_reaches_it_verbatim`
  — one scripted turn covers the whole rule: `3200원` → `3,200원`; the
  already-grouped form traced and left alone (membership, both directions);
  `접수번호 20260724000546는 2026년 공시입니다` untouched; the stored answer carries
  the reader's form; and a second turn where **`「1591」` stays verbatim inside the
  span while the same digits outside it become `1,591원`**.
- `tests/test_agent_tools.py` (inside the existing `get_event` case) — the payload
  carries `("3200", "3,200")` beside each other, a ratio (`0.2314082845`) gains
  nothing, and `grouped(R1_RCEPT) is None` / `grouped(16907605) == "16,907,605"`.

**Live smoke (2026-08-23, bounded).** Two scoped turns against the real
`AgentGeminiClient` over the in-memory corpus, with `figures.regroup` instrumented
to record every (model form → reader form) pair:

- Q1 「예정발행가액이 얼마로 적혀 있나요?」 → 「…예정발행가액은 **3,200원**입니다.」 +
  the 확정 전 family, `blocked 0`.
- Q2 「전환가액과 사채 총액이…」 → 「전환가액은 **1,591원**입니다. 사채의 권면총액은
  **26,900,000,000원**입니다.」, `blocked 0`.
- **All five released sentences arrived already grouped**: every `regroup` call was
  a no-op. The model reads `value_display` and writes it, so the release-time
  rewrite is the guarantee rather than the mechanism in practice. Dates came
  through as `2026-08-20`/`2026-08-26`, ungrouped.
- ▷ **$0.0107 estimated** total (4 calls, 12,287 tokens, thinking **LOW**
  throughout) — never billed.

## Deviations from `plan.md`

None in substance. Two choices the plan left open, taken and recorded:

- The plan's suggested seam ("serve display-grouped figure strings … add a
  release-time fallback **only if needed**") — **both** were built. The fallback is
  what makes the requirement testable without a model and true regardless of one;
  the live measurement above then showed the model complying on its own, and that
  is reported honestly rather than used to drop the guarantee.
- The transform runs in `ToolResult.__post_init__` (via `object.__setattr__` on the
  frozen dataclass) rather than at the five call sites or in `response()`: one
  rule, no call-site drift, and the gate then *learns* the same strings the model
  sees — so a model writing 「3,200」 is not blocked by a vocabulary that lacks it.

## Honest limits

- Grouping reaches **contract figures only**. A bare integer that is a genuine
  quantity but not a `Figure` — `holdings[].shares` in the portfolio payload — is
  still spoken ungrouped. The sample's holdings are 500/300/500/100, so nothing
  visible today; a real account holding ≥1000 shares would read `1500주`. Widening
  the predicate means naming keys by hand, which is the drift this seam avoids;
  raise it if a reader ever sees it.
- A figure inside a filing's own **quote** keeps the filing's spelling, whatever it
  is. That is the point (R6: 인용문 재구성 금지) and it is why the detail page's
  `(4,985원 -> 3,200원)` reads correctly — it was already grouped in the source.
- `regroup` is a string rewrite over a closed table; it cannot change *which*
  number a sentence states, but it also cannot fix a number stated in the wrong
  unit. That was already the membership check's honest limit and is unchanged.

## Files changed

- `src/mijual/agent/figures.py` (new — the whole mechanism)
- `src/mijual/agent/tools.py` (import + `ToolResult.__post_init__` + docstring)
- `src/mijual/agent/citations.py` (grouping table, release-time respelling, the
  shared quoted-span pattern, the normalization comments)
- `src/mijual/agent/instructions.py` (one HOW TO WRITE A FIGURE block)
- `tests/test_agent_loop.py`, `tests/test_agent_tools.py`
- `works/phases/active/P6/phase.md` (note 26 + Doc impact addendum)
