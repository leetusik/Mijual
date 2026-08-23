# Result — P8.DECOMP (decompose the design polish pass)

Executor: `slice-executor-high`, 2026-08-23. Worked from this folder's `plan.md`, `intent.md`,
`CLAUDE.md`, `.claude/skills/design-cowork/SKILL.md`, `docs/current/{frontend,experience,qa,
operations,product}.md`, `docs/reference/design/SIGNOFF.md` + the seven round folders, and
`works/phases/active/{P3,P7}/phase.md`.

## What was created

**17 middle slices, bare folders (only `slice.json`)** — exactly the shape `plan.md` specifies, no
`P8.DECOMP2`, all `--risk high`:

| slice | kind | order | depends on |
|---|---|---|---|
| `P8.S1` AskWidget `t1` 중복 키 — collision-free turn ids after a restored thread | `fix` | 1 | — |
| `P8.S2` R8 폴리시 라운드 — foundations/tokens + global chrome (nav · footer · vocky) | `co-work` | 2 | — |
| `P8.S3` Apply R8 | `implementation` | 3 | `P8.S2` |
| `P8.S4` R9 — landing 관제 현황판 + board | `co-work` | 4 | — |
| `P8.S5` Apply R9 | `implementation` | 5 | `P8.S4` |
| `P8.S6` R10 — event detail ①②③ + trust states | `co-work` | 6 | — |
| `P8.S7` Apply R10 | `implementation` | 7 | `P8.S6` |
| `P8.S8` R11 — 내 종목 조회 + 놓친 돈 조회기 | `co-work` | 8 | — |
| `P8.S9` Apply R11 | `implementation` | 9 | `P8.S8` |
| `P8.S10` R12 — auth (로그인 · 비밀번호 재설정) | `co-work` | 10 | — |
| `P8.S11` Apply R12 | `implementation` | 11 | `P8.S10` |
| `P8.S12` R13 — 내 포트폴리오 + 알림 설정 | `co-work` | 12 | — |
| `P8.S13` Apply R13 | `implementation` | 13 | `P8.S12` |
| `P8.S14` R14 — AI 질문 (런처 · 위젯 · `/ask` · 질문 스트립) | `co-work` | 14 | — |
| `P8.S15` Apply R14 | `implementation` | 15 | `P8.S14` |
| `P8.S16` R15 — 운영 관제 admin `/ops` | `co-work` | 16 | — |
| `P8.S17` Apply R15 | `implementation` | 17 | `P8.S16` |

`--depends-on` was added on each apply slice pointing at its own round (advisory; `order` is what
selects). **No other slice's `plan.md` was written or touched**, per the contract.

## What was recorded in `phase.md`

- **Context** — the rhythm in one place (walk → ask → round → apply), then the **surface map**: for
  each of the eight surfaces its routes, components, copy modules, CSS modules, the original round(s)
  that designed it, and the later P6/P7 overrides in force. Every path was verified to exist (`find`
  over `frontend/app`, `frontend/components`, `frontend/lib`, `frontend/public/foundations`).
- **Polish inventory** — per surface, *what to audit* (controls, states, viewports), derived from P3's
  §Design Inventory and the qa doc's `## Regression Checklist`, with P3 items 11 (Korean copy) and 12
  (mobile-first) marked cross-cutting so no round owns them and none skips them.
- **Decomposition** — the table as cut, plus the rationale: why no `DECOMP2` is legitimate under this
  operator override (the unknown is each apply slice's *content*, and content lives in `plan.md`,
  written after the gate), why the surface order stands as `intent.md` lists it, why every slice is
  `high`, the R8–R15 numbering with suggested round slugs (`08-polish-foundations-chrome` …
  `15-polish-admin`) in the existing project + `SIGNOFF.md`, bare folders, and fractional orders for
  anything a landed round re-shapes. Plus a "what each kind of slice does" summary (design slice
  inline-only and never dispatched; apply slice under RESPECT THE DESIGN with both yardsticks and the
  full regression re-run).
- **Findings & Notes** — the verified `t1` root cause (below), the **shared-primitive usage table**
  (which surfaces render `CraftPanel` / `StateBadge` / `EstimateMarker` / `RightsChip` / `DDay` /
  `Citation` / `LapseAlert`, plus the `SearchRow` and `QuestionStrip` cross-bindings and the shared
  `lib/holding.ts`), the fact that `public/foundations/tokens.css` is a **vendored landed artifact**
  (R2's file + a 5-line header, verified by diff), a table mapping **P7's 13 unanswered operator
  questions onto P8's surfaces**, and the smaller facts a later slice will want (record read-only,
  `SIGNOFF.md` precedence, zero Korean minted, `/ops` desktop-only, the 404 page is Next's default).
- **Doc impact** — header seeded; `P8.DECOMP: none`.
- **Operator Questions** — four genuine entries (Q1 where the inherited P7 decisions get answered;
  Q2 vocky has nothing to bind to, so surface 1 has three dead controls no slice may fix by
  inventing a URL; Q3 does chrome polish include the default 404 page; Q4 is copy in play this pass).
- **Constraints** — no new features; RESPECT THE DESIGN + supersession via `SIGNOFF.md`; design record
  read-only (incl. the vendored token files); Korean-only, zero minted; every browser claim in the
  operator's runtime + production build; `co-work` inline-only and apply plans written only after
  SIGNOFF; docs versioned once at the review; gate expected `required` (orchestrator declares it);
  the regression floor every apply slice re-runs.

## `t1` root cause — verified read-only, and it is more than a key warning

Confirmed as `plan.md` describes, plus one thing the plan did not state:

- `frontend/lib/ask.ts:252` `let counter = 0;` is **module scope**; `nextId()` (253–255) returns
  `` `t${counter}` ``, so the counter restarts at 0 on every full page load.
- `hydrate()` (`ask.ts:438`, called from `components/ask/useAsk.ts:62`) installs the restored
  `sessionStorage` turns — already named `t1`, `t2`, … via `readThread()` (207) — **without advancing
  `counter`**. The first fresh `ask()` (`ask.ts:471`) therefore mints `t1` again → duplicate
  `key={turn.id}` at `AskWidget.tsx:96` **and identically at `AskPage.tsx:99`**.
- **Not just React:** `patchTurn(id, …)` (`ask.ts:285`) rewrites *every* matching turn,
  `history(exceptId)` (298) filters by id, and `retry(turnId)` (485) `find`s the **first** match — so
  a collision streams one answer into two turns and retries the wrong one. That makes this a data
  bug, which is why `P8.S1` stays `high` and needs the restored-session repro (ask → reload → ask).
- Candidate directions recorded for `P8.S1`'s planner without choosing one: seed the counter from the
  restored turns, or mint collision-free ids (`crypto.randomUUID()` / session-unique prefix) — with
  the caveat that ids are persisted, `Persisted.v` is `1` and `readThread` rejects any other version,
  so a thread written by the old build must still hydrate. `frontend/lib/ask.test.ts` exists (four
  cases, `npm run smoke` → `node --test "lib/*.test.ts"`) and exports `createAskStore`, so a
  hydrate-then-ask case is cheap; keep it terse per the repo rule.

## Validation

| command | outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **passed** (`Workflow validation passed.`) — re-run after `phase.md`/`result.md` were written |
| `python3 scripts/workflow.py next` | `current_slice=P8.DECOMP`, **`next_slice=P8.S1`** |
| folder check (`ls` over `works/phases/active/P8/slices/*/`) | all 17 new folders hold **only `slice.json`**; `P8.DECOMP` holds `plan.md` + `slice.json` (+ this `result.md`), `P8.REVIEW` holds `slice.json` |
| `diff` R2 landed `tokens.css` vs. `frontend/public/foundations/tokens.css` | only `0a1,5` (the provenance header) — the vendoring claim is measured, not assumed |
| read-only source reads (`ask.ts`, `AskWidget.tsx`, `AskPage.tsx`, `useAsk.ts`, `ask.test.ts`) | root cause confirmed; **nothing edited** |

No code, no docs, no `plan.md` for any other slice, no `accept-gate`, no state transition, no commit.

## Deviations from `plan.md`

None on shape or content. Two judgment calls the plan left open:

1. **Surface order kept exactly as `intent.md` lists it.** The plan allowed re-ordering if the reading
   found a better one; it did not — the given order already reproduces P3's own R1→R7 dependency
   direction (tokens + shared primitives first, chrome decided by placing it on a real surface, then
   the reader's path, auth before the surface it serves, `/ops` last because nothing waits on it).
   Recorded in `phase.md` §Rationale.
2. **Four `## Operator Questions` entries were added.** The plan said to add entries only for genuine
   operator decisions; all four are (dead vocky triggers, the unowned 404 page, whether copy is in
   play, and where P7's 13 inherited decisions get answered). None of them creates work — each is a
   decision a round cannot make for the operator.

## Uncertain / worth the orchestrator's attention

- **The gate is undeclared** (`phase.json` `acceptance.required: null`). Declaring it is the
  orchestrator's next action after this slice; `intent.md` expects `accept-gate P8 --require`.
- **R8's blast radius is the whole product.** The shared trust primitives are decided in surface 1,
  so `P8.S3` will touch files every later surface renders, and each later round should be told what
  R8 already changed rather than re-deciding it. Worth a line in `P8.S2`'s plan.
- **`P8.S1` runs before any round**, so its browser repro is the phase's first runtime claim — if
  `## Operator Runtime` is ever wrong in practice, that slice is where it surfaces first.
