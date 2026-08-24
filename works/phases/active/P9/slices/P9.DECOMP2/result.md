# P9.DECOMP2 — result

**Status: done.** The R16 design was read as the binding contract and the phase's build slices are
cut: **nine bare folders**, backend → frontend → fidelity, ordered 4–12 between `P9.DECOMP2` (3) and
`P9.REVIEW` (9999). No product code was touched; only `works/` files changed.

## What was read before cutting

- `phase.md` — the DECOMP breakdown, the build inventory (items 1–8 + invariants), the full `P9.S1`
  changple5 transfer report, the `P9.S1B` best-practice survey (esp. P9 input segregation, **P10
  stable block ids first**, P11 tool descriptions, P12 cache measurement), the `### P9.S2 — R16 design
  landed` section, the Doc impact list and the Operator Questions list.
- The signed record: `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` in full
  (§0 copy · §1 events · §2 element specs · §3 prompt/loop · §4's 26 checks) and `output/result.md`
  (§1 Q-A…Q-E, §3 surface decisions, §5 supersessions, §6 departures, §7 the two contract changes).
- Code, read only deeply enough to cut honest boundaries: `src/mijual/agent/` (`events.py`,
  `loop.py::run_turn/_execute/_finish`, `citations.py`, `copy.py`, `declarations.py`, `tools.py`,
  `instructions.py`, `client.py` seams), `src/mijual/web/ask.py` (`_Released.absorb`, `AskTurn.frames`),
  `src/mijual/web/conversationstore.py` (`record_turn`, `REFUSAL_FAMILIES`), `src/mijual/db/models.py`
  (`ConversationTurn`) and `src/mijual/db/schema_sync.py`, `src/mijual/calc.py`'s `__all__`,
  `frontend/lib/ask.ts` (the `AskBlock` union + `apply`'s `switch`), `frontend/components/ask/*`
  (`Answer.tsx` grouping, `AskPage.tsx` rail, `copy.ts`), `frontend/components/ops/copy.ts`
  (`REFUSAL_CATEGORIES_KO`), `docs/current/operations.md` → `## Operator Runtime`,
  `docs/current/qa.md` → `## Regression Checklist`, and `.claude/skills/design-cowork/SKILL.md`
  §Verifying.

## The slices created

| slice | kind | risk | order | depends on |
| --- | --- | --- | --- | --- |
| `P9.S3` — R16 event vocabulary, block ids and the two storage contracts | implementation | high | 4 | `P9.DECOMP2` |
| `P9.S4` — citations: strip don't drop, and the 미확인 claim marker | implementation | high | 5 | `P9.S3` |
| `P9.S5` — calculator tool and the calculation block | implementation | high | 6 | `P9.S3` |
| `P9.S6` — security_check guard, hard reject and the 보안 family | implementation | high | 7 | `P9.S3` |
| `P9.S7` — prompt rewrite, budgets, thinking MID, cache prefix and input segregation | implementation | high | 8 | `P9.S4` `P9.S5` `P9.S6` |
| `P9.S8` — ask store and R16 copy: keyed blocks on the client | implementation | high | 9 | `P9.S7` |
| `P9.S9` — the five R16 elements (calc · data · status · tool trace · markers) | implementation | high | 10 | `P9.S8` |
| `P9.S10` — /ask re-cut: rail retired, start screen, 새 대화, and the three retirements | implementation | high | 11 | `P9.S9` |
| `P9.S11` — R16 fidelity and functional sweep in the operator runtime | implementation | high | 12 | `P9.S10` |

Each folder holds **only `slice.json`** — no `plan.md` was pre-filled anywhere. The full scope of each
slice, the record→slice mapping, the standing constraints and the deliberate exclusions are recorded in
`phase.md` → `## Decomposition` → `### DECOMP2 (2026-08-25)`.

## Why this cut

- **Backend before frontend**, as the plan and the design-cowork mixed-phase pattern require: the
  stream must speak R16 before the surface draws it. Five backend slices, then three frontend, then
  verification.
- **P10 first.** Stable `block_id` + `persistent` + in-place replacement land in `P9.S3`, the very
  first build slice, because every structured element added afterwards would otherwise invent its own
  progressive state privately (S1B mechanic D).
- **`P9.S3` is the contract slice**: both of the two contract changes the record names (§7 — verbatim
  block storage, 6-value refusal vocabulary) land in one commit, and `_Released.absorb` is required to
  be *generic over persistent structured events* so the calculator slice needs no second storage
  change. The refusal whitelist widens here even though `P9.S6` is what emits 「보안」 — a whitelist is a
  contract, not a producer.
- **The calculator is separated from the guard** although both are "a new tool plus its loop wiring":
  their subsystems, their failure modes and their validation are different, and merging them would
  make one very large slice with two unrelated acceptance stories.
- **`P9.S7` is last among the backend** because §3's prompt rewrite depends on all three preceding
  behaviours (citations wording, calculator guidance, the four-family refusal block).
- **Three frontend slices, not one**: the store's keyed reduce is a prerequisite for every renderer,
  the five elements are a self-contained component + CSS transfer, and the page re-cut plus the three
  retirements is a layout change with a different blast radius. The retired constants
  (`ANONYMITY_KO`, `VERIFIED_ONLY_KO`, `REASK_KO`) are deliberately removed **with their call sites**
  in `P9.S10`, so no intermediate commit fails to build.
- **All nine are `risk: high`.** Every one writes real code and spans more than one file; no genuine
  one-line/docs slice emerged, so nothing routes to the `mid` tier.

## Risk set deliberately, per the contract

`risk` is the phase's main cost lever, so it was set per slice rather than by default. The only
candidate for `low` was the ops refusal-filter mirror (`REFUSAL_CATEGORIES_KO`, a five-line list), and
it was **not** split out: separating a vocabulary mirror from the whitelist it mirrors is exactly how
the two drift.

## Deviations from `plan.md`

**None on substance.** Two judgement calls the plan left to this slice, recorded so the review can
check them:

1. The plan listed "structured-block storage in `record_turn`/`_Released.absorb`" inside the general
   backend scope; it was placed in the **first** slice (`P9.S3`) rather than later, so the two signed
   contract changes travel together and later slices inherit generic storage.
2. `--kind implementation` was used for `P9.S11` (the fidelity slice) rather than inventing a new kind:
   the slice may make faithful-implementation fixes, and `implementation` at `risk: high` routes to the
   correct executor tier while `fix` would imply a defect already reported.

## Validation

| command | outcome |
| --- | --- |
| `python3 scripts/workflow.py validate` | **passed** — `Workflow validation passed.` |
| `python3 scripts/workflow.py new-slice …` ×9 | all nine created; each folder contains `slice.json` only |
| `works/backlog.md` (regenerated by `new-slice`) | P9 lists `S3…S11` in order 4–12, between `P9.DECOMP2` and `P9.REVIEW`; `Next slice: P9.S3` |

## Phase notes appended

- `phase.md` → `## Decomposition` → `### DECOMP2 (2026-08-25)`: the slice table, per-slice scope with
  the record→slice mapping, the standing constraints (RESPECT THE DESIGN · the three known-stale
  build-prompt lines · the Operator Runtime pointer · additive-on-the-wire · the phase invariants ·
  docs versioned once at REVIEW · small tests · validation levers), what is deliberately **not** a
  slice, and two engineering choices flagged for `P9.S7`/`P9.S3` (`temperature=0.2`; who emits
  `DataBlockEvent`).
- `phase.md` → `### Doc impact`: `(P9.DECOMP2) none — decomposition changed no durable truth`.
- `phase.md` → `## Operator Questions`: one new entry — whether the 운영 대화 로그 panel must *show*
  the stored structured blocks, since R16 designed only `/ask` and the widget and regression item 16
  is otherwise satisfiable at the payload level.
