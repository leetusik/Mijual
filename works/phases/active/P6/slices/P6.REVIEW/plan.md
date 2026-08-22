# Plan — P6.REVIEW: phase review of P6 (Apply — AI 질문 agent)

## Goal

Review the whole phase against its objective, `intent.md` (including the
binding mid-phase operator addition *"we need to build a agent not just llm
chain"*), R6's signed design record, and the docs — then, **only on a passing
verdict**, consolidate the phase's "Doc impact" notes into new doc versions.
P6 is **not** in parallel mode: consolidation happens here.

## Inputs

- `works/phases/active/P6/intent.md` and `phase.md` end to end — objective,
  decomposition, findings 1–24, constraints (the acceptance criteria), open
  questions, and the **Doc impact** list (entries for S1–S7; DECOMP's is
  "none").
- Every slice's `plan.md` + `result.md` (`P6.DECOMP`, `S1`–`S7`) — including
  S7's disposition table and its consolidated operator questions.
- `docs/reference/design/rounds/06-explain/output/build-prompt.md` +
  `result.md` (READ-ONLY — the contract reviewed against).
- `docs/current/*.md` + `docs/index.json` (what the versions will supersede).

## Validation (run it all, fresh)

- `.venv/bin/python -m pytest` — expect **137 passed**.
- `cd frontend && npm run build && npm run typecheck && npm run smoke`.
- `python3 scripts/workflow.py validate`.
- Spot-verify the phase's structural promises directly (cheap, high-value):
  the four AST boundary scans exist and pass (they're in the suite — confirm
  by name); the anonymity test walks the two conversation tables; grep the
  frontend for forbidden strings (`남은 질문`, `저장 이력 없음`, `탭을 닫으면`,
  quota) and for `localStorage` in the ask surfaces; confirm
  `docs/reference/design/` is untouched by P6 commits (`git log --stat` or
  diff against the P5 review commit).

## Judgment

Review against the objective and the constraints in `phase.md`:

1. **Agent, not chain** (the operator's binding addition): read
   `mijual/agent/loop.py` and its tests — is tool choice/order/round-count/
   answer-timing genuinely the model's? Is there any hidden forced call?
2. **RESPECT THE DESIGN**: every R6 build-prompt element has an owning,
   landed implementation (DECOMP's result.md has the coverage walk; S7
   measured it live). Nothing dropped, simplified, restyled.
3. **The hard rules as acceptance criteria**: citation forcing structural,
   never-compute, refusal families only, schema-level anonymity, no quota,
   sessionStorage-only client persistence, server-side anonymous storage
   feeding the ops tabs, `get_contact` honest-unset.
4. **The catalogued items**: S7's dispositions and the nine operator
   questions are *catalogued*, not defects — judge whether any of them is
   actually a phase-blocking gap (something signed but missing) versus an
   operator decision to surface. The record's own contradictions (mobile
   menu row) are operator questions, not failures.
5. **Workflow hygiene**: every slice has `plan.md` + `result.md`, statuses
   consistent, Doc impact list complete against what actually changed (spot
   check: does anything in `git log` for this phase change durable truth
   without a Doc impact line?).

**A non-passing verdict stops before consolidation**: complete the whole
validation + judgment first, then return `changes_requested` with numbered
findings and proposed fix slices (names + kinds), touching no docs. `blocked`
only for something outside the phase's power.

## On pass only — consolidate the docs

Turn the Doc impact list into new versions with
`python3 scripts/workflow.py doc-new-version --doc <name> --summary "..." --source P6.REVIEW`,
one per doc that durable truth moved (from the list: **architecture · backend
· api · data · security · product · experience · frontend · operations · qa**,
and **decisions** if you judge the phase took D-number-worthy decisions — the
agent-not-chain architecture and the model-in-request-path boundary re-aim are
the recorded candidates; state them as operator-attributable facts, dating the
operator addition 2026-08-22). For each: write the new version file under
`docs/versions/<doc>/` per its existing conventions (read the latest version
first; carry forward what still holds, integrate the phase's changes — these
are full documents, not changelogs), then `rebuild-docs` regenerates
`docs/current/`. Never hand-edit `docs/current/*`.

⚠ `P5.REVIEW` note 8: the ops 개요 tab parses `docs/current/decisions.md` for
`- **Open…` bullets — after any decisions rewrite, re-check the open-bullet
count renders sanely (and note what changed).

## Return

- `review_verdict: pass | changes_requested | blocked` with numbered findings
  (pass may carry non-blocking observations), proposed fix slices if any.
- The list of doc versions created (or `none — verdict was not pass`).
- `explain: not written — run /explain for this phase`.
- `result.md` in this slice folder; a phase-review note appended to
  `phase.md`. Run `python3 scripts/workflow.py validate` last; it must pass.
- Do **not** commit; do **not** run `review-phase`/`finish-slice`/status
  commands (the orchestrator records the verdict).
