# Plan — P3.REVIEW (phase review: design-only P3)

Dispatched to `slice-executor-high`. P3 is a **normal (non-parallel) phase**, so a
passing review consolidates docs here. The executor validates and judges to
completion, writes `result.md`, appends phase notes, and returns a structured
verdict — it does NOT run `review-phase` or transition any state (orchestrator's
job), except the sanctioned `doc-new-version` / `rebuild-docs` calls on pass.

## What P3 was

Operator re-scope (verbatim, in `intent.md`): "make this phase design only. one by
one. we have nothing to hurry. vocky will be added as feedback inception, admin
panel required, auth related required." Design-only: **no implementation code, no
HTTP layer, no frontend scaffolding anywhere in P3**. Slices: `P3.DECOMP`,
`P3.S1` (grounding pack), `P3.S2`–`P3.S8` (design rounds R1–R7, all signed and
closed), `P3.REVIEW` (this). Build → P5 (apply, created 2026-08-21); deploy → P4.

## Validation (all slices together)

1. `python3 scripts/workflow.py validate` must pass.
2. Grounding pack (P3.S1): `.venv/bin/python scripts/export_design_grounding.py`
   re-runs at 0 req / 0 calls, exits 0, and leaves `git status` clean for
   `docs/reference/design/grounding/` (idempotency claim).
3. Design record integrity: each of `docs/reference/design/rounds/01-brand-foundations`
   … `07-admin` has `handoff.md` + `output/result.md` + `output/build-prompt.md`;
   `docs/reference/design/SIGNOFF.md` carries seven round entries (R1–R7), each with
   the operator's literal signoff words.
4. **Design-only constraint**: verify no application/implementation code was added
   in P3 — the phase's commits touch only `docs/`, `works/`, and (S1 only)
   `scripts/export_design_grounding.py` (a documented local doc-generation command,
   sanctioned by its Doc impact note). `git log --stat` over the P3 range
   (`dcb6d0b..HEAD`) is the evidence; flag anything under `src/` as a finding.
5. Intent capture: `intent.md` holds verbatim original + confirmed re-scope;
   phase.md links it.

## Judgment

Review against the phase objective, `intent.md`, and the inventory in `phase.md`
(items 1–12): all inventory items covered by the seven signed rounds (map each item
to its round); operator co-work protocol honored (handoff → pending → read-back →
literal signoff → immutable record → regroup); discrepancies at each gate recorded
in SIGNOFF rather than silently fixed; open items properly carried (vocky API shape
→ apply phase; 운영자 연락처; countdown cut-off instant; "정정 이력" label; D1–D4
triggers → apply phase).

## Doc consolidation (ONLY on pass)

The current "Doc impact" list in `phase.md` has two notes (`decisions`,
`operations`). **Judge its completeness first**: seven signed rounds produced
durable product/design truth that the versioned docs should at least point to —
e.g. `frontend` and/or `experience` (bootstrap stubs today) gaining a version that
records the signed design system's existence, its location
(`docs/reference/design/` — rounds, SIGNOFF, grounding) and the binding rules
(RESPECT THE DESIGN; records read-only; revisions = new rounds), and `product`
recording the finalized nav (내 종목 조회 · 관제 현황판 · AI 질문) and surface set
if that is durable product truth. Add any missing one-line Doc impact notes to
`phase.md` yourself (reviewer carve-out), then consolidate: one
`doc-new-version --doc <name> --summary "..." --source P3.REVIEW` per note, then
`rebuild-docs`, then `python3 scripts/workflow.py validate` again. Never hand-edit
`docs/current/*.md`; never touch `docs/versions/` old files; write docs only —
no source code.

On `changes_requested` or `blocked`: complete validation and judgment first,
return numbered findings + proposed fix slices, and do NOT consolidate docs.

## Return

Structured verdict: `review_verdict: pass|changes_requested|blocked`, numbered
findings, `doc_versions:` list (or none), and the fixed pointer
`explain: not written — run /explain for this phase`. Write `result.md` in this
slice's folder; append a review summary to `phase.md`.
