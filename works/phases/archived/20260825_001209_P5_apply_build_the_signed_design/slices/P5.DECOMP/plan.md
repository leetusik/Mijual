# Plan — P5.DECOMP (decompose phase)

## Job

Decompose P5 "Apply — build the signed design" into middle slices. This is the *apply*
phase of the P3 design/apply split, so it is a **single-pass** decomposition: no `DECOMP2`,
no `co-work` slices — every design decision is already signed and immutable in
`docs/reference/design/`. You create the middle slices as **bare folders** with
`new-slice` (never pre-filling any slice's `plan.md`), record the breakdown, rationale,
findings, and decisions in `phase.md`, and write your own `result.md`. You do not
implement anything, do not commit, and do not transition slice/phase status.

## Scope (from the confirmed intent — `../../intent.md`)

Build Mijual per P3's signed design records (R1–R7):

- **FastAPI backend** exposing the P2 pipeline data per the P2 exposure contract
  (`docs/current/api.md` and the data docs) — events, versions, snapshots, citations,
  the landing 현황판 aggregates, 놓친 돈 조회 computation, D-day/portfolio queries.
- **Next.js frontend** faithful to the signed design under **RESPECT THE DESIGN** —
  never drop, simplify, restyle, or "improve" an approved element. The signed contracts
  are `docs/reference/design/rounds/{01..07}-*/output/build-prompt.md` plus each round's
  `tokens.css`/`fonts.css`, governed by `docs/reference/design/SIGNOFF.md` (supersession
  order matters: e.g. R2.1 cosmos-dark governs over base R2; 「추정」 tag-only, ▷ retired
  from UI).
- **Auth + portfolio layer** (R5: auth surfaces, portfolio 등록, D-day list, sample load).
- **Admin panel** (R7: operator-facing pipeline, gate queue, accuracy, quota).
- **vocky integration** (script widget + observation API; R2 chrome-level triggers).
- **Grounded 해설 panel** (R6: citation-forced, SSE streaming states) — *backend + UI for
  the 해설 feature belong here only insofar as R6 describes non-agent 해설; everything that
  is the AI 질문 agent feature (agent backend, conversation storage, widget + page
  surfaces) is **P6**, not this phase.* If reading R6/R7 shows a component is
  inseparable from the agent/conversation storage, put it on the P6 side of the boundary
  and record that in `phase.md`.

**Out of scope:** the AI 질문 agent feature (→ P6, order 3.7); deployment/hosting and the
unattended 09-07→09-11 requirement (→ P4 Ship & Submit). All user-facing text is Korean;
work/notes in English.

## Read order (before cutting slices)

1. `works/phases/active/P5/intent.md` + `phase.md` (this phase)
2. `docs/reference/design/README.md`, `SIGNOFF.md`, then all seven
   `rounds/*/output/build-prompt.md` (and skim each round's `result.md`/`tokens.css`
   where the build prompt references them)
3. `docs/current/*.md` — especially `api.md` (P2 exposure contract), `architecture.md`,
   `data.md`, `frontend.md`, `experience.md`, `product.md`, `security.md`, `decisions.md`
4. `works/phases/active/P3/phase.md` — the design phase's accumulated findings and any
   build-inventory-like notes
5. The four deferred jobs: `works/deferred/open/D{1..4}/deferred.json`
6. Current repo reality: `src/mijual` (P2 Python package), `compose.yaml`,
   `pyproject.toml` — the backend extends this codebase; no frontend exists yet.

## Decisions this decomposition must make (record each in `phase.md`)

1. **Slice breakdown and order — backend first, then the design implementation** (the
   confirmed intent fixes this ordering). Suggested shape (adapt from what you read, do
   not treat as fixed): API/backend slices over the exposure contract → auth/portfolio
   backend → frontend foundation (Next.js scaffold + R1 tokens/fonts) → page/feature
   slices per design round (landing+chrome, event detail, lookup, account/portfolio,
   해설, admin) → vocky integration → a final real-browser design-fidelity verification
   slice (per `design-cowork`: fidelity work is its own slice). Keep slices sized so
   each is one coherent deliverable; use `--depends-on` advisorily.
2. **Deferred jobs D1–D4** — their triggers fire at this phase (D1: before ② event
   detail pages render; D2: if event pages trip on duplicates; D3: pre-2026 ① depth for
   retrospective views; D4: multi-span citations for 실적보고서 figures). For each:
   promote into P5 (`promote-deferred D<n> --phase P5 --slice P5.S<k> --name "..."`) at
   the right order position, or leave deferred with a one-line rationale in `phase.md`.
   Judge from the design records whether the rendered pages actually hit each trigger.
3. **Admin 대화 로그 / 익명 세션 boundary** — those R7 views depend on P6's conversation
   storage. Decide: frame them now (empty-state UI, storage-agnostic) vs move them to
   P6. Record the decision and rationale in `phase.md` (intent.md flags this
   explicitly).
4. **Risk per slice** — `--risk` selects the executor tier and is the phase's main cost
   lever. Anything that writes real code or touches more than one file is `high`;
   `low` only for a genuinely one-line/few-line or docs-only slice (expect essentially
   all build slices here to be `high`).

## Mechanics

- Create each middle slice: `python3 scripts/workflow.py new-slice --phase P5 --slice
  P5.S<n> --name "..." --kind <feature|fix|...> --risk <low|high> --order <n>
  [--depends-on ...]`. Bare folders only — never write another slice's `plan.md`.
- Seed `phase.md`: fill `## Decomposition` (breakdown + rationale), `## Findings &
  Notes` (what you learned from the design records/docs that later slices need),
  `## Constraints` (RESPECT THE DESIGN; Korean-only user-facing text; keep test files
  small; SIGNOFF supersession rules; P6/P4 boundaries), and note the D1–D4 and admin-
  boundary decisions. Append doc-impact lines only if you change durable truth (a pure
  decomposition usually doesn't).
- Write `result.md` (free-form): what you created, the order, decisions made, anything
  the orchestrator should know.
- Validate: `python3 scripts/workflow.py validate` must pass.
- Return the structured verdict per your agent contract (`done` expected; `escalate`
  does not apply — you are the top tier).
