# Plan — P7.REVIEW: phase review of P7 (실서비스 정상화 fix pass)

## What you are reviewing

P7 is a fix pass: the operator found the shipped P5/P6 product broken or rough in **11 confirmed
ways** (`intent.md` — the acceptance list), and nine slices (`P7.S1`–`S9`) closed them, each
verified in `next dev` on the operator's own origins (`127.0.0.1`, the Tailscale IP) **and** in a
production build. `P7.S9` re-measured all 11 independently (~553 checks, 5 origin×runtime
combinations, 5 widths) and found no code needing change. Not parallel mode (`phase.json` has no
`execution` block) — so a passing review **does** consolidate docs here.

## Read

`CLAUDE.md`; `intent.md`; `phase.md` **end to end** (Decomposition table, RC-A/RC-B, every slice's
findings block, the six Design-collision readings, Constraints, the **Doc impact** list, Open
Questions Q1–Q13); every slice's `slice.json` + `plan.md` + `result.md` (`P7.DECOMP`, `S1`–`S9`);
`docs/index.json` and the current docs the Doc impact lines name (`docs/current/frontend.md`,
`api.md`, `experience.md`, `operations.md`, `qa.md`, `product.md`); the signed record where a
collision reading is judged (`docs/reference/design/SIGNOFF.md` + the governing round; read-only).
The previous reviews' plans (`works/phases/active/P6/slices/P6.REVIEW/plan.md`) show the house
style for verdict + consolidation.

## 1. Validate all slices together (complete this before judging)

- `python3 scripts/workflow.py validate`; `cd frontend && npm run typecheck && npm run smoke`;
  `.venv/bin/python -m pytest` (139 expected); `git status` clean of source changes outside
  `works/`; `make stack-status` (the dev stack should be up — if not, `make stack-up`).
- Re-run each slice's stated validation **at headline level, not the full 553** — the review is
  independent of the fidelity sweep (it never passes a phase purely on other slices' reports): in
  headless Chrome over CDP (the S1–S9 `result.md` approach; the dev stack, **on `http://127.0.0.1:3000`**,
  fresh profile, 1440 + 390) spot-check the 11 items once each: 2-slot nav; typeahead candidates +
  ↓Enter → `/stocks/{corp_code}`; focused hero input `outline: none` and no paint under 조회; board 30
  rows + 펼치기 → 60, strips open; 로그인 in the slot (sample cleared); countdown ticks over 10 s;
  launcher present, and (one live turn, max) a question streams an answer; sample portfolio
  captions `본인 표시`, 챙겼습니다 flips to 챙긴 돈; `innerText` free of `localStorage`/`이 브라우저`;
  `/_next/*` 403s = 0 and the HMR socket 101 on 127.0.0.1. Also confirm once that the **production
  build** still builds (`npx next build` in an isolated `rsync` copy of `frontend/` per the `P7.S2`
  method — never the dev server's `.next`; no need to start it unless a check demands). Kill what you
  start; leave the dev stack up. Delete any account you create; leave `s19-fidelity@example.com`.

## 2. Judge (complete all of it before branching on the verdict)

- **Each of the 11 items against `intent.md`**: closed, verified in the operator's runtime, and
  closed the way the Confirmed Intent says (e.g. item 3's reading — ring off text fields, keyboard
  indicator kept; item 4's 펼치기 toggles work *and* the list is windowed; item 9's relabel per
  R5-8; item 10's promise-vs-mechanism split). Where a slice chose a default the operator has not
  confirmed (Q2 focus, Q3 = 30, Q4 row stays, S8's Q-A…Q-E, Q9–Q13), judge whether the default is
  defensible under RESPECT THE DESIGN — a defensible default with the question routed to the
  operator is a pass; an invented visual decision or a dropped signed element is a finding.
- **RESPECT THE DESIGN**: every override is one `intent.md` authorised (items 1, 3, 4a, 9/10 trims)
  and scoped to the override; the unsigned elements (typeahead panel, board window control) use the
  signed idiom and mint no Korean copy; trust rules intact (S9's cumulative smoke).
- **Workflow hygiene**: `plan.md`/`result.md` present for every slice, statuses consistent, no
  slice ran `doc-new-version`, commits per slice on `main`, Doc impact list **complete against what
  actually changed** (spot-check the diff `git diff ccbed5a..HEAD --stat` — any durable change
  without a line is a finding).
- **The operator catalogue is routed, not buried**: `phase.md` Open Questions Q1–Q13 (+ S8's
  Q-A–Q-E, S9's additions) must be listed in your `result.md` as one numbered **"Decisions for the
  operator"** section with each slice's live default — this phase exists because such catalogues
  died in P5's review record. Additionally write a **5-minute operator walkthrough** (URLs on
  `http://127.0.0.1:3000` + the actions to try for each of the 11 items) in `result.md` so the
  orchestrator can hand it to the operator verbatim.
- `changes_requested` carries numbered findings + proposed fix slices (`P7.F1`…), `blocked` the
  blocker; either way stop before step 3. The review never edits source.

## 3. On `pass` only — consolidate docs

For each doc named in the Doc impact list, create **one** new version capturing the whole phase:
`python3 scripts/workflow.py doc-new-version --doc <doc> --summary "..." --source P7.REVIEW`, edit
only the returned `edit_path`, then `python3 scripts/workflow.py rebuild-docs`. Expected docs:
**`frontend`** (the `allowedDevOrigins`/`MIJUAL_DEV_ORIGINS` seam and the inverted browser-check
rule; the StrictMode module-store trap; the board window; the shared SearchRow + typeahead panel
and `.orbits` clip; the focus split; the two-slot nav; the trimmed captions; portfolio layout
primitives + the CSS-grid `auto`-track trap; the verification floor + probe traps; the prod-only
Next behaviours — fold P7's `frontend` lines into one coherent version: extend the existing
sections, supersession notes where a P5 statement no longer describes the rendering), **`api`**
(`GET /stocks/suggest`, declaration order, the rule sentence), **`experience`** (board window,
search typing state, 조회 memory bullet, 챙긴 돈 bullet), **`operations`** (`MIJUAL_DEV_ORIGINS`
in the env table; decide whether to add a short "dev stack / Makefile" note — the doc describes
none today), **`qa`** (the SSE contract verified from the browser on prod; the dev-vs-prod
verification floor if `qa` is where verification rules live — check which doc owns it and do not
duplicate). Check `product.md` needs nothing (three slices said so). Keep each version terse and
accurate; never patch an old version or `docs/current/*.md` by hand. Report the versions created.

## Return

`review_verdict` (`pass` | `changes_requested` | `blocked`), validation outcomes, numbered
findings (if any) with proposed fix slices, the "Decisions for the operator" list, the operator
walkthrough, the doc versions created (or none), and `explain: not written — run /explain for this
phase`. Write `result.md`; append a short review note to `phase.md`. No commits, no `review-phase`,
no state transitions — the orchestrator records the verdict.
