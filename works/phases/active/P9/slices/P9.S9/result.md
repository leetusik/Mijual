# P9.S9 — result

**Status: done.** R16's five elements are drawn, both views draw them through the one `Answer.tsx`,
and the answer's children are in §2.8's order. No source file outside `frontend/components/ask/`
(plus one new test under `frontend/lib/`) was touched; the Python side was not touched at all.

## What landed

| file | what it is |
| --- | --- |
| `frontend/components/ask/Blocks.module.css` | **new** — `output/r16-ask.css` §2.1–2.5 ported declaration by declaration into this repo's CSS Module convention. Tokens only, **zero new tokens**, numbers exact. |
| `frontend/components/ask/StatusLine.tsx` | **new** — §2.1. One line, mono `--text-xs` ink-3, 2px **dashed** left border + 8px padding, nowrap + hidden scroll, `role="status"`, **no animation**. Renders the server's own signed sentence. |
| `frontend/components/ask/ToolTrace.tsx` | **new** — §2.2. Rows verbatim in R14's `.toolRow`; flat at ≤3 rows or while the turn is live; folded to `trace(tools, events)` + `자세히` at ≥4 once it settles, with mono order numbers on expand. Fold state is component state and is never stored. `events` = `turn.filings`. |
| `frontend/components/ask/DataBlock.tsx` | **new** — §2.3. `DataBlock` + `DataRowLine` (the row schema §2.4 reuses). Three columns `minmax(0,40%) minmax(0,1fr) auto` (36% ≤767), value-cell-only scroll, fixed third column (「입력」 marker and/or the citation chip), 6 rows + `모두 보기 (N)`/`접기`, `margin-inline:-12px` ≤767. No 3-column table. |
| `frontend/components/ask/CalcBlock.tsx` | **new** — §2.4. `--border-strong`, heading = `--live` mode word + name, inputs through `DataRowLine`, 식 줄 (hidden on `error`), and **one slot** for `계산 중` / 결과 행 (`--live-tint`, `--text-md` mono 600 `--live` + 「계산」) / `calcError(why)` with no alert colour or icon. |
| `frontend/components/ask/ValueMarker.tsx` | **new** — §2.5. 계산 and 미확인 as siblings of 추정, wearing `components/EstimateMarker.module.css`'s own `.tag`; colour per family, `kind` with **no default**. |
| `frontend/components/ask/render.ts` | **new** — pure, React-free: §2.8's region split (`answerParts`), the 미확인 span cut (`proseSegments`), 소진 vs 연결 끊김 (`exhausted`), the fold threshold (`foldable`). |
| `frontend/components/ask/Answer.tsx` | re-cut to §2.8's child order; the `isProse` placeholder guard from `P9.S8` is gone; 소진 draws no inset/button/string while a disconnect keeps R14's row. |
| `frontend/components/ask/InlineCitation.tsx` | one optional prop, `place="prose" \| "row"` — markup unchanged (§2.6 「변경 없음」). |
| `frontend/components/ask/Ask.module.css` | three placement rules for a row's chip (`.citationRow`), nothing else changed. |
| `frontend/lib/askRender.test.ts` | **new** — three terse cases over `render.ts` (the `lib/auth.test.ts` arrangement, because `npm run smoke` globs `lib/*.test.ts`). |

## Validation

| command | outcome |
| --- | --- |
| `cd frontend && npm run typecheck` | **pass** (clean) |
| `cd frontend && npm run smoke` | **pass** — 21 tests, 0 fail (18 existing + 3 new) |
| `cd frontend && npm run build` | **pass** — 16 routes built, no warnings from this slice |
| `.venv/bin/pytest -q` | **pass** — 154 tests, 0 fail (suite untouched by this slice) |
| `python3 scripts/workflow.py validate` | **pass** |

`npm run build` rewrites the generated `frontend/next-env.d.ts` (dev → build import paths); it was
restored with `git checkout` so the slice's diff carries no generated churn.

### What the validation does *not* cover, and one thing it did

No Operator Runtime pass: nothing here ran under `make stack-up` at `http://127.0.0.1:3000`, and no
§4 check is claimed. `P9.S11` owns that sweep.

Two layout questions could not be answered by reading, so they were answered by **measurement**: a
static harness (the real `public/foundations/tokens.css` plus the three CSS modules, with DOM copied
from the components) rendered in headless Chrome at a 390-equivalent block width and at 760.

1. **A 인용 칩 inside a 데이터 행 breaks the row if its panel is measured there.** With the panel in
   the fixed third column, that `auto` track grows toward the quote's max-content and the
   `minmax(0,1fr)` value column collapses to **zero** — the value vanished entirely, closed panel
   included (our `InlineCitation` always renders the panel for R6-4's grid-height open; the design
   mock renders nothing when closed, which is why the round never met this). Fixed by placing the two
   halves as grid items of the row: chip in the third column, panel `grid-column: 1 / -1` under it.
   Re-measured: label, value, chip and panel all survive at both widths, and at ≤767 the panel picks
   up R6 §Mobile's 전폭 quote rule.
2. **The ported CSS renders as the record draws it** — trace folded and expanded, data block with its
   fold, calc block in all three states, 미확인 in prose, the status line's dashed rule, and §4 check
   8b's 「블록이 답변 상자의 좌·우 끝까지 닿는다」 at the 390-equivalent width.

## Deviations from `plan.md`

- **One extra file the plan did not name: `InlineCitation.tsx` (+3 rules in `Ask.module.css`).** The
  plan says the chip is 「the same component, new *places* only」; giving it a place turned out to
  require saying *where the panel opens* in a row, which the record never settled and which cannot be
  left at its default without losing the value column (measured, above). The component's markup and
  styling are unchanged; what was added is a placement prop and its three CSS rules, and the reading
  is catalogued as an Operator Question rather than treated as settled.
- **`components/ask/index.ts` was not touched.** Its stated rule is that a piece is exported because
  *both views compose it*; these five are composed only by `Answer`, which is already exported.
- Nothing else. No copy was invented (every Korean string comes from `copy.ts`'s landed §0 block or
  from the server), no designed element was dropped or restyled, and no animation was added.

## Notes carried to `phase.md`

Eleven decisions under `### P9.S9 — the five elements landed`, two **Doc impact** lines (`frontend`),
and three new `## Operator Questions` entries: where a row's 인용 블록 should open, the two spellings
of the marker family's geometry (`r16-ask.css`'s em values vs. the shipped `EstimateMarker` tag — the
sentence 「셋 다 EstimateMarker 그대로」 governed here), and where R6's 의견 확인 한 줄 belongs in
§2.8's order.

Two things `P9.S11` should watch in the flesh, both recorded there: the 계산 블록 grows by the 식 줄
when it settles (the server sends `expr` only with the outcome — the *slot* does not jump, but the
block gets one line taller), and `AskWidget`'s auto-scroll key counts `blocks.length`, which a
status line replaced in place does not change.
