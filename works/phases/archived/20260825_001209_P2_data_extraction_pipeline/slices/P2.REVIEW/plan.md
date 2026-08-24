# Plan: P2.REVIEW — phase review of P2 (Data & Extraction Pipeline)

_Mode: auto. Plan written inline by the orchestrator. P2 is NOT in parallel mode — on a pass, this slice consolidates the Doc impact notes into doc versions._

## What to review

Ten work slices: S1 (package/schema/client), S2 (①③ collector), S3 (bodydoc parse layer), S4 (Gemini extraction), S5 (gates + exposure), S6 (Celery beat), S7 (② CB + backfill), S8 (소멸가치 estimation, ▷ 718.1억원), F1 (full-2026 sweep), S9 (evalset + accuracy, Claude-judged per operator directive). Each slice folder holds `plan.md` + `result.md`; `phase.md` accumulates findings N1–N93, Constraints, a long Doc impact list, and Open Questions (O-1/2/4/5/8/9 closed; O-3 resolved by the operator's cross-model directive; O-6 unanswered-by-design; O-7 still homeless — see item 4 below). Deferred jobs D1–D3 exist.

## Steps

1. **Validate the phase together** (not per-slice re-testing in isolation): `.venv/bin/python -m pytest` (56 tests); `python3 scripts/workflow.py validate`; the four stage summaries at 0 spend (`python -m mijual.gates run` ×2 identical, `python -m mijual.estimate report --today <today>` ×2 identical, `python -m mijual.evalset report`, `python -m mijual.scheduler once --offline`); spot-check that every slice's headline claims in `result.md` match what the commands print today (N8 discipline). Budget: ≤ 30 OpenDART requests, 0 LLM calls.
2. **Judge against the objective and `intent.md`**: collection (scheduled, 정정-aware, snapshot-based) ✓/✗; schema extraction for the matrix's unstructured fields ✓/✗; deterministic gates with reason codes and failed-never-exposed ✓/✗; the 소멸 총액 estimation ✓/✗; the ~100-filing evalset + accuracy report (cross-model provenance honestly stated) ✓/✗. Check the binding constraints: no OpenDART call would sit in a request path; secrets clean (grep); 금지선 (grep for fine-tuning/PyTorch/HF framing in code/docs/notes); evidence-tag discipline in committed claims.
3. **Weigh the known soft spots honestly** (they are recorded, decide if any blocks a pass): the `check_against_items` matcher defect (N-noted, fix needs an S4 corpus re-run — fix slice or defer?); the 코이즈 double-exposable row (N81, `hint_duplicate` not in the blocking set — D1's territory); the 정정 재추출 backlog F1 left (69 calls at preset thinking, N82 — the beat's extract stage drains it, verify that claim is plausible); the SKC/에스에너지 multi-addend citation defect class (5 partial labels); ③'s 44% block rate (mostly superseded-API scoping — intended?). A `changes_requested` verdict should name concrete fix slices; do not fail the phase for items that are honestly recorded, deferred, and non-blocking for P3.
4. **O-7 (MTS coverage matrix, carried from P1)**: not pipeline code; recommend its home in the verdict (defer-job or a P3/P4 slice) — do not do it.
5. **On a passing review only — consolidate durable docs**: work through `phase.md`'s Doc impact list and write new doc versions with `python3 scripts/workflow.py doc-new-version --doc <doc> --summary "..." --source P2.REVIEW` for each affected doc (`data`, `architecture`, `operations`, `decisions`, `product`, `qa` — group the notes per doc, write the actual content into the new version files under `docs/versions/<doc>/`, coherent and complete rather than a pasted list of one-liners; `backend` may fold into `architecture` unless a separate doc is clearly warranted). Then `rebuild-docs` if the workflow requires it, and verify `docs/current/*.md` regenerated. Write only docs, never source.
6. **Verdict**: return `review_verdict: pass | changes_requested | blocked` with numbered findings; on non-pass, stop BEFORE doc consolidation and propose fix slices. Either way include `explain: not written — run /explain for this phase` and `doc_versions:` listing what was created (or `none`).

## Out of scope

No source changes, no re-extraction, no new features. No commits, no state transitions (the orchestrator records the verdict via `review-phase`). The one workflow-command carve-out you have is `doc-new-version` / `rebuild-docs` on a pass.

## Re-review (2026-08-20, after fix slices F2–F4)

The first pass returned `changes_requested` on finding 1 (blocking) with findings 2–3 recommended; F2 (docstrings), F3 (judged_by provenance), and F4 (matcher + recall re-freeze, 85.31% → 88.70%) have landed — read their result.md files. Re-review scope:

1. Verify the three fixes against the original findings (grep for the forbidden phrasing incl. --help output; labels.json carries judged_by and the report prints it; recheck/refresh-recall idempotent and figures consistent everywhere the number appears).
2. Re-run the phase validation set (pytest, gates run ×2, estimate report ×2, evalset report, scheduler once --offline, workflow validate).
3. Confirm carry-forwards 4–8 are recorded where the first pass put them (D2 trigger, D4, N-notes) — no new work.
4. On pass: consolidate the full Doc impact list into doc versions per the original plan step 5 (quote N97's pinned figures, the 88.70% recall from N100, and never "hand-labelled"). Return the verdict + doc_versions created.
