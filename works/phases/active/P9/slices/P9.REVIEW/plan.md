# P9.REVIEW — the phase review, gated

## Context

P9 rebuilt the AI 질문 agent into the R16-signed smart assistant: twelve slices done
(DECOMP · S1 · S1B · S2 co-work · DECOMP2 · S3–S11). The acceptance gate is **required**, so this
review runs the gate stages too and returns a **walkthrough** beside its verdict — the orchestrator
opens the gate; you never run `accept-gate` (phase-state command).

Read in full: `works/phases/active/P9/intent.md` (the confirmed intent — eight numbered points),
`phase.md` end to end (DECOMP + DECOMP2 breakdowns, every `### P9.Sx` decision section, the
`### Doc impact` list, `## Operator Questions`),
`docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` (binding record; the three
stale lines are overridden — 4 cards, no meta card, no rail — per `### P9.S2` and SIGNOFF §R16),
and each slice's `result.md` (S11's carries the 26-check table and the un-exercisable list).
`docs/current/operations.md` §Operator Runtime is the runtime manifest.

## Stage 1 — validate all slices together

Run the phase's full validation set once, on the final tree:
`cd frontend && npm run typecheck && npm run smoke && npm run build`; `.venv/bin/pytest -q`
(expect 154); `python3 scripts/workflow.py validate`. Any red = a finding.

## Stage 2 — judge against objective, intent, and record

The eight intent points, each answered with evidence (a file, a measured behavior, a decision
section): (1) gemini-3.7-flash thinking LOW→MID; (2) strip-don't-drop, 「안녕」 answered; (3)
calculator + free prose arithmetic; (4) ~20-round budgets as backstop; (5) security_check guard
with after-model hard reject + fixed Korean refusal; (6) unified conversational behavior, refusal
families relaxed via the design round; (7) rich chat surface (data/calc/status/trace); (8) proposals
actively made (S1 P1–P8, S1B P9–P16 — check they reached the operator's eyes via the design round or
the questions list). RESPECT THE DESIGN throughout: fidelity is S11's evidence; spot-check, don't
re-derive.

## Stage 3 — open the product yourself (gate stage; never pass on reports alone)

`make stack-up`, browse `http://127.0.0.1:3000` in real Chrome (headless CDP; desktop + a true 390
emulation — S11 recorded the 500px window-floor workaround). Spot-check the phase's headline claims
live: 「안녕」 → greeting, no tools, no footer; a 공시 question → cited prose; a calc request → calc
block replacing in place; an injection attempt → 보안 sentence only; `/ask` start screen with 4
cards; 새 대화. Then a **fresh-eyes first-time-user walk**: everything dead, confusing, or annoying
goes into the walkthrough — explicitly NOT judged against the design record, and never silently
fixed. Re-run the **whole cumulative `## Regression Checklist`** in `docs/current/qa.md`. Tear the
stack down when done.

## Stage 4 — route every Operator Questions entry

Thirteen open entries (the five pre-S2 ones are marked answered by the `P9.S2` resolution note —
verify that note and treat them as routed). Each open entry must be routed: **walkthrough** (a
decision the operator takes while walking — the entries themselves name which presses to try) or
**defer-job** (list them for the orchestrator to file with `defer-job` — you never run it). An
unrouted entry is a review finding. Recommended lean: decision-during-walkthrough for the
product-visible ones (data-block one-row ceiling, chip 44px, preset strip, invisible 범위, unsigned
out-of-scope line, chip panel placement, 의견 확인 placement, 식 줄 flooring/units); defer-job for
the ones needing a separate round or ops decision (ops-panel block rendering + stored 미확인 spans,
추정 calc primitives, guard-log retention, marker geometry re-cut) — but judge each yourself.

## Stage 5 — consolidate Doc impact (ONLY on a passing review)

P9 is not in parallel mode. On pass: consolidate the `### Doc impact` list into new doc versions via
`python3 scripts/workflow.py doc-new-version --doc <name> --summary "..." --source P9.REVIEW` — one
version per affected doc (`frontend`, `decisions`, `security`, `api`, `architecture`, `backend`,
`qa`), each version's body being the current doc updated with every line for it, including qa's
count corrections (142→154, 16/16→22/22), the restated unmarked-numeral invariant, and P9's
headline regression checks appended to the cumulative checklist. Never hand-edit `docs/current/`
(generated); write version files per the existing `docs/versions/<doc>/` convention and let the
tool regenerate. Honesty rule from S6/S1B: the security doc must say the guard is a behavioral
layer, not injection protection. A non-pass verdict STOPS before this stage — finish validation and
judgment first, then return numbered findings + proposed fix slices instead.

## Return

Structured verdict with `review_verdict: pass|changes_requested|blocked`, numbered findings on
non-pass, the routed-questions table (walkthrough vs defer-job, with defer-job titles/reasons/
triggers ready for the orchestrator), `doc_versions` listing what was created (or none), the fixed
line `explain: not written — run /explain for this phase`, and — on pass — a **`walkthrough`**: a
concrete Korean-surface walk in the operator runtime (URLs to open, exact questions to ask
including the presses the questions list names: 「계양전기 유상증자 조건 알려줘」, an injection
attempt, the out-of-scope question twice, a data-row chip and calc-input chip press at 390, the
widget-scope-to-card path, a phone tap on a citation chip), plus the operator-only checks S11 could
not exercise (tailnet origin from another device, live budget-exhausted turn, live calc error,
추후결정/≥2-lapse states) and every walkthrough-routed decision stated as a question. Never commit,
never transition state, never run accept-gate.
