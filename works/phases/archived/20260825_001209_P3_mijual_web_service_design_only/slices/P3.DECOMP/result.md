# Result — P3.DECOMP

P3 is decomposed as a **design-only** phase: one grounding-pack slice, **seven** `co-work` design rounds,
then the existing `P3.REVIEW`. **No `P3.DECOMP2`, no build slices, no implementation code.**

## What landed

**`intent.md`** — the re-scope is now consultable. Appended to *Clarifications Resolved*: the operator's
verbatim 2026-08-20 re-scope (explicitly marked as superseding the earlier "one mixed phase" answer),
vocky = the operator's existing feedback-collection service to be embedded, the FastAPI + Next.js stack,
and admin panel + auth as required scope. The verbatim *Original Input* block was not touched.

**`phase.md`** — rewritten around the design-only scope:
- Title/objective now say design only; the build is a later **apply phase** created with `create-phase`
  after P3's signed design, sized from each round's `build-prompt.md`. "No `DECOMP2` in this phase" is
  stated in the objective.
- *Context* records the stack decision, what P2 already provides (`gates/exposure.py`, `calc.py`, the
  dated live-board numbers, the Korean state copy), what does **not** exist yet (no HTTP layer, no
  frontend, stub docs, no `docs/reference/design/`), and the brand context.
- *Design Inventory* — 12 numbered items, what to design and not how; items 11 (Korean copy) and 12
  (responsive) are cross-cutting and belong in every round's handoff.
- *Decomposition* — the slice table plus a *Round-packing rationale* section.
- *Findings & Notes*, *Doc impact*, *Constraints*, *Open Questions*.

**Eight new slices, bare folders (only `slice.json`; no `plan.md` pre-filled anywhere):**

| Slice | Kind | Risk | Order | Depends on |
|---|---|---|---|---|
| `P3.S1` grounding pack | `feature` | high | 1 | — |
| `P3.S2` R1 brand + foundations | `co-work` | high | 2 | `P3.S1` |
| `P3.S3` R2 landing 현황판 + chrome + vocky | `co-work` | high | 3 | `P3.S2` |
| `P3.S4` R3 event detail ①②③ + states | `co-work` | high | 4 | `P3.S3` |
| `P3.S5` R4 검색 + 슬라이더 + 놓친 돈 조회기 | `co-work` | high | 5 | `P3.S4` |
| `P3.S6` R5 개인화 2층 (auth + portfolio + D-day + sample) | `co-work` | high | 6 | `P3.S5` |
| `P3.S7` R6 grounded 해설 panel | `co-work` | high | 7 | `P3.S6` |
| `P3.S8` R7 admin panel | `co-work` | high | 8 | `P3.S7` |

Seven rounds (the plan's ~5–7 band, at the top of it) because the operator asked for "one by one … we
have nothing to hurry": one theme per round, foundations first. Two departures from the plan's example
packing, both argued in `phase.md`: 검색+슬라이더 and 놓친 돈 조회기 are merged (same anonymous
holding → 금액 환산 family, same input primitive and money readout), and 해설 panel / admin panel are
split (different audience and density; both are named operator requirements).

## Validation

| Command | Outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **passed** (exit 0) |
| `python3 scripts/workflow.py next` | `current_slice=P3.DECOMP`, `next_slice=P3.S1` — as expected |
| `works/backlog.md` regeneration | shows all 8 new slices with `co-work` on every design round |
| `slice.json` sweep (kind/risk/order/depends_on) | all 8 match the table above; every design round `co-work` + `high` |

Every new slice folder contains `slice.json` only — verified by listing the folders.

## Deviations from `plan.md`

1. **Seven rounds, repacked** (plan: "~5–7", "repacking is the executor's call") — merge of 검색/슬라이더
   with 놓친 돈 조회기, split of 해설 from admin. Rationale is in `phase.md` → *Round-packing rationale*.
2. **`intent.md`'s *Confirmed Intent* paragraph was also refined**, not just the clarifications list. The
   plan asked only for the clarifications append, but leaving the paragraph asserting "this is a mixed
   design+build phase … `P3.DECOMP2`" would have left the phase's source of truth self-contradicting.
   The verbatim original stays immutable; only the confirmed wording moved, and it is dated and points at
   the clarification that supersedes it.
3. **`depends_on` chained** (each round on the previous, `P3.S2` on `P3.S1`). Not requested; advisory
   only, and it records the operator's "one by one" sequencing.

## For the orchestrator

- `works/phases/active/P3/phase.json` still carries `name` / `objective` from the original mixed
  design+build scope, so `works/backlog.md` renders "Mijual Web Service (design + build)". `phase.md` and
  `intent.md` are the corrected truth. There is no workflow command to rewrite a phase's name/objective
  and it is not a status transition I own — flagging it rather than editing phase state.
- `P3.S1` is the only non-design slice and is dispatchable. **`P3.S2`–`P3.S8` are `co-work` and must be
  run inline by the orchestrator, never dispatched** (an executor has no `DesignSync`); each ends the run
  at its `pending` gate.
