# Plan — P8.DECOMP (decompose the design polish pass)

Orchestrator plan, written inline (auto mode) on 2026-08-23. Executor: `slice-executor-high`.

## Goal

Cut P8's middle slices as **bare folders** and seed `phase.md` with the context every later slice needs: the per-surface route/file map, the polish inventory (what to audit, not how), the decomposition table with rationale, constraints, and the running-list headers. Nothing else: no code, no `plan.md` for any other slice, no docs, no `accept-gate` (the orchestrator declares the gate right after this slice).

Read first: `works/phases/active/P8/intent.md` (the confirmed operator intent — the shape below is a deliberate operator override and must be cut exactly that way), `CLAUDE.md`, `.claude/skills/design-cowork/SKILL.md`, `docs/current/frontend.md`, `docs/current/experience.md`, `docs/reference/design/SIGNOFF.md`, and `docs/reference/design/rounds/*/output/result.md` headings (which round designed which surface).

## The shape to cut — exactly this, it is the operator's decision

**No `DECOMP2`.** One phase, interleaved **design slice → apply slice** per surface, in surface order. Operator's verbatim: "design part a slice -> apply part a slice -> design part b slice -> so on."

| slice | kind | risk | order | what |
|---|---|---|---|---|
| `P8.S1` | `fix` | high | 1 | AskWidget `t1` duplicate-key bug (root cause below) |
| `P8.S2` | `co-work` | high | 2 | **R8** design polish — surface 1: foundations/tokens + global chrome (nav, footer, vocky touchpoint) |
| `P8.S3` | `implementation` | high | 3 | apply R8 (`--depends-on P8.S2`) |
| `P8.S4` | `co-work` | high | 4 | **R9** — surface 2: landing 관제 현황판 + board |
| `P8.S5` | `implementation` | high | 5 | apply R9 (`--depends-on P8.S4`) |
| `P8.S6` | `co-work` | high | 6 | **R10** — surface 3: event detail ①②③ + trust states |
| `P8.S7` | `implementation` | high | 7 | apply R10 |
| `P8.S8` | `co-work` | high | 8 | **R11** — surface 4: 내 종목 조회 + 놓친 돈 조회기 (`/stocks`, `/stocks/[corp_code]`) |
| `P8.S9` | `implementation` | high | 9 | apply R11 |
| `P8.S10` | `co-work` | high | 10 | **R12** — surface 5: auth (login / reset) |
| `P8.S11` | `implementation` | high | 11 | apply R12 |
| `P8.S12` | `co-work` | high | 12 | **R13** — surface 6: portfolio + notifications |
| `P8.S13` | `implementation` | high | 13 | apply R13 |
| `P8.S14` | `co-work` | high | 14 | **R14** — surface 7: AI 질문 (launcher / widget / `/ask` / question strip) |
| `P8.S15` | `implementation` | high | 15 | apply R14 |
| `P8.S16` | `co-work` | high | 16 | **R15** — surface 8: admin `/ops/*` |
| `P8.S17` | `implementation` | high | 17 | apply R15 |
| `P8.REVIEW` | review | high | 9999 | already exists |

Create them with `python3 scripts/workflow.py new-slice --phase P8 --slice P8.S<n> --name "..." --kind <kind> --risk high --order <n> [--depends-on P8.S<n-1>]`. Names are yours to word (short, specific, surface named; the design slices should carry their round number `R8`…`R15`, continuing the record's `01`–`07` rounds as `08`–`15`). Every risk is `high` — `co-work` is never `low` (design-cowork), every apply slice writes real cross-file code plus a real-browser sweep, and the `t1` fix verifies a restored-session repro in the operator's runtime (more than a one-liner). If your reading of the surfaces finds a better *order* of surfaces (e.g. foundations must come before chrome for a reason), you may re-order surfaces but **keep the pairing and alternation**; say why in `phase.md`. Do not add, merge, or split surfaces — 8 surfaces was the operator's explicit choice; anything a round later re-shapes goes in at fractional orders by the orchestrator.

## What each kind of slice will do (record this in `phase.md` so later planners have it in one place)

- **Design slice (`co-work`, orchestrator-run inline, never dispatched):** (1) *walk first* — the orchestrator opens the surface in the operator's runtime (`## Operator Runtime` in `docs/current/operations.md`: `make stack-up`, `http://127.0.0.1:3000` in Chrome desktop + the Tailscale URL, dev mode; production build when behaviour differs), lists findings as a first-time user (dead/no-op controls, confusing bits, copy, interaction states, liveness, mobile viewport) with URLs/screenshots; (2) sets the slice `pending` and asks the operator "what's wrong and how should it be fixed?"; (3) the operator's answers become the round's `handoff.md` under `docs/reference/design/rounds/<NN>-<slug>/` (direction / REFERENCE data — Claude Design + the operator make the visual decisions; polish only, no new features), second `pending` gate while the operator designs; (4) read-back with DesignSync, land as-is, SIGNOFF, regroup.
- **Apply slice (`implementation`, `slice-executor-high`):** planned only after its round's SIGNOFF, from the landed `build-prompt.md`; implements under RESPECT THE DESIGN; runs the fidelity + functional sweep in the operator's runtime and the production build; re-runs the qa doc's `## Regression Checklist`; appends Doc impact + Operator Questions to `phase.md`.
- **`P8.S1` (`fix`):** React duplicate-key `t1` at `frontend/components/ask/AskWidget.tsx:96`. Root cause (orchestrator read-only check — verify it): `frontend/lib/ask.ts:252` `let counter = 0; function nextId()` restarts per page load while `hydrate()` restores sessionStorage turns already named `t1…`, so the first fresh turn collides with a restored one. Note the candidate fix directions for the planner (seed the counter from the restored turns, or make ids collision-free such as `crypto.randomUUID()`), and that `frontend/lib/ask.test.ts` exists.

## Seed `phase.md`

Fill, in the existing sections:

- **Context** — the per-surface map: for each of the 8 surfaces the routes (`frontend/app/...`), the components (`frontend/components/...`), the copy files, the original design round(s) that designed it (`docs/reference/design/rounds/NN-*`), and any later overrides (P7 operator overrides recorded in `SIGNOFF.md`/P7 notes — e.g. nav three-slot → two-slot, focus treatment, 「추정」 tag). One compact block per surface; this is what every walk and every handoff will cite, so make paths real (verify they exist).
- **Polish inventory** (a subsection under Context or Decomposition) — per surface, *what to audit*, not how: the controls, states, and viewports the walk must cover. Derive it from the design inventory in `works/phases/active/P3/phase.md` and the qa doc's `## Regression Checklist`, not from imagination; keep it to a few lines per surface.
- **Decomposition** — the table above (as cut), plus a short rationale, the R8–R15 round numbering, and the "what each kind of slice does" summary.
- **Findings & Notes** — whatever you learned reading the surfaces that a later slice needs (e.g. which surfaces share components, so a polish in one round affects another — `Citation`, `DDay`, `StateBadge`, `RightsChip`, `CraftPanel`, the chrome). Also note the `t1` root-cause verification result.
- **Constraints** — no new features; RESPECT THE DESIGN (polish rounds supersede per `SIGNOFF.md` rules, never silent restyling in apply slices); Korean-only surface; operator runtime + production build for every browser claim; design record read-only; `co-work` never dispatched; the phase's gate is expected `required` (the orchestrator declares it).
- Leave `## Operator Questions` with its header (add entries only if your reading raises a genuine operator decision). Leave a `## Doc impact` running list header if the file lacks one (the review consolidates).

## Don't

- Don't write any other slice's `plan.md`, don't touch code or docs, don't run `accept-gate`, `doc-new-version`, `start-slice`/`finish-slice`, or commit.
- Don't invent visual decisions or pre-plan past a design gate.

## Validate

`python3 scripts/workflow.py validate` passes; `python3 scripts/workflow.py next` shows `P8.S1` as the next slice after `P8.DECOMP`; all 17 middle slices exist as bare folders (only `slice.json`). Write `result.md` in this slice folder (what was created, what was recorded, anything uncertain) and return the structured verdict.
