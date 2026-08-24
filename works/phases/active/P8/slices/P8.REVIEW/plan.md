# P8.REVIEW plan — gated phase review: design polish pass (surfaces 1–7 applied, 8 cancelled)

## What this phase was

P8 polished every product surface, one Claude Design round + one apply slice per surface
(R8 chrome/foundations … R14 ask), **no new features**. Surface 8 (운영 관제 `/ops`, R15) was
**cancelled by operator decision** on 2026-08-24 (phase.md §"R15 cancelled") and parked as
deferred job **D6** — that cancellation is recorded operator intent, **not a review finding**,
and `/ops` ships in its R7+P5/P7 state. The phase's operator acceptance gate is **required**.

Read: `phase.md` (whole — decomposition, per-round landed-spec sections, `## Doc impact`,
`## Operator Questions`, constraints), `intent.md`, `docs/current/*.md` (esp. operations'
`## Operator Runtime`, qa's `## Regression Checklist`), `docs/reference/design/SIGNOFF.md`
(R8–R14 entries — precedence over R1–R7 where superseded), and each slice's `result.md`.

## Stage 1 — validate all slices together

- `.venv/bin/python -m pytest` · `cd frontend && npm run typecheck && npm run smoke` ·
  `npm run build` in a scratch copy (never rewrite the repo's `next-env.d.ts`) ·
  `python3 scripts/workflow.py validate`.
- Spot-re-run each apply slice's cheapest headline check (their `result.md`s list them) rather
  than re-executing full per-slice suites.

## Stage 2 — the gate stages (phase gate is required: true)

All in the **operator runtime** per the manifest: `next dev` at `http://127.0.0.1:3000` and
`http://100.77.164.42:3000` (tailnet — not a secure context), plus a **production build** served
on a spare port (e.g. `:3100`); Chrome headless over CDP in an **isolated profile**. Never touch
the operator's own browser or session. For account states use temporary accounts created through
the product's 계정 만들기 and delete them through 계정 삭제 afterwards, re-counting the DB rows
back to baseline. The `/ops` authenticated tabs are unreachable to you (separate operator
credentials — **never attempt or simulate that login**); verify the door's SSR only, and put any
ops-tab check the operator should make into the walkthrough instead.

1. **Spot-check the phase's headline claims yourself** — never on other slices' reports alone:
   R9 landing/board rhythm; R10 event detail (①②③, trust states, single 767); R11 lookup +
   놓친 돈; R12 auth (rail, reset, ConversionOffer, error map); R13 portfolio (four-track D-day
   edges, 챙겼습니다 0px shift, notifications frame, sample band); R14 ask (767 existence
   boundary at 767/768, 보내기, signed preset sentences sent behind labels, one-paragraph
   prose, chip-counted 근거 N건, link-only API-tier block, centered /ask bundle, thin
   scrollbars, tool-row nowrap at 390). Widths per the rounds: at least 1440 / 768 / 767 / 390.
2. **Fresh-eyes first-time-user walk** of the whole reader product, once, **not judged against
   the design record**: report everything dead, confusing, or annoying as walkthrough items —
   never silent fixes, never code changes.
3. **Re-run the whole cumulative `## Regression Checklist`** in `docs/current/qa.md` (14 boxes —
   including the structural guards) and **append this phase's headline checks** to it in the qa
   doc version you cut at consolidation. An ops-session-only box is marked for the operator in
   the walkthrough, not skipped silently.
4. **Route every `## Operator Questions` entry.** Entries already marked answered by a round's
   signoff, resolved in-slice, or routed (Q59–Q65 → D6) are done — verify the marking exists.
   Every remaining open entry must be routed: **either** folded into the acceptance walkthrough
   as a concrete decision for the operator to take while walking, **or** listed by you for the
   orchestrator to file as a deferred job (give title/reason/trigger per item — you do not run
   `defer-job` yourself). An unrouted entry is a review finding; the review may not pass with
   one. (Q49's backend race: recommend the deferred-job route it proposed. Q56/Q57/Q58 from
   P8.S15, Q39/Q40/Q46-adjacent defaults, and the older Q9…Q38 backlog — check each entry's own
   text for its recorded default/answer before routing.)

## Stage 3 — verdict, then pass-only work

Complete Stages 1–2 and reach the verdict **before** any consolidation. On
**`changes_requested`/`blocked`**: stop before consolidation; return numbered findings +
proposed fix slices (whole picture in one cycle).

On **`pass`** only (this phase is not parallel-mode):
- Consolidate `phase.md`'s `## Doc impact` list into new doc versions:
  `python3 scripts/workflow.py doc-new-version --doc <doc> --summary "..." --source P8.REVIEW`
  per affected doc (group the per-slice lines by doc; write the version bodies from
  `docs/current/*` + the noted changes — never hand-edit `docs/current/`), then
  `rebuild-docs` and `validate`. The qa version carries the appended regression boxes.
  copy-inventory is a hand-registered grounding file, not a versioned doc — leave it.
- Do **not** run `accept-gate` (phase-state command — orchestrator's) and do not record the
  review verdict with `review-phase` (also orchestrator's).

## Return

Structured verdict: `review_verdict` (pass | changes_requested | blocked), numbered findings,
`walkthrough` (concrete URLs to open and actions to try in the operator runtime — dev origin(s)
and production where they differ — including the fresh-eyes items and every operator-decision
question folded in per Stage 2.4), the deferred-job list for the orchestrator to file,
`doc_versions` written (pass only), validation table, and the fixed line
`explain: not written — run /explain for this phase`.
