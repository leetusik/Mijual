# Plan: P2.F1 — full-2026 discovery re-run + reconcile (close the run gap, pick up pifricDecsn)

_Mode: auto. Fix slice inserted by the orchestrator on P2.S8's N78(a)._

## Context

N73(c) proved the corpus is missing at least 3 collectable 2026 KOSDAQ ① originals (레이저옵텍 `20260109000634`, RF머트리얼즈 `20260408002647`, 피엠티 `20260409002139`) — a run gap from P2.S2's budget-interrupted live pass, not a code gap. Separately, `pifricDecsn` (유무상증자결정, N71) only became a collector target in S8, so no scheduled run has ever swept 2026 for it. Both mean the live board under-represents ①. This slice is mechanical: re-run the existing collection machinery over the full 2026 window for all registered targets, then let the standard pipeline stages reconcile, and prove the gap is closed.

## Work

1. Full-window collection: `python -m mijual.collect --bgn 20260101 --end <today>` over all registered endpoints (①: `piicDecsn` + `pifricDecsn`, ③: `cmpMgDecsn`, ②: `cvbdIsDecsn`), both markets, budget **≤ 700 requests** (`max_requests`; N78 estimated ▷ ~120 for the gap itself — the ceiling is a guard). Offline caches first where they help.
2. Then the standard stages once: `bodydoc` sync (fetch missing 본문 for newly live events + hint backfill + warrants), `extract` for new versions (**LOW thinking**, cap ≤ 30 calls — new ① events × 1 call each), `gates run`. The scheduler's `once` path may orchestrate this if convenient.
3. Reconcile + prove: the 3 named rcept_no are now events with versions/snapshots and a gate verdict; report board deltas (exposable events / renderable fields before → after), any new withdrawals/추후결정 the sweep surfaces, and `estimate report` re-run to confirm the headline number's stability (adopted events were already in — state any delta honestly).
4. Idempotence: immediate second run adds 0 events/versions.

## Out of scope

No new code beyond what reconciliation strictly requires (prefer 0 lines; small fixes to bugs the sweep exposes are allowed with tests). No schema changes unless forced. No commits/state transitions/doc-new-version. Findings → N-notes; a Doc impact one-liner only if a durable claim changes (e.g. board counts in the `product` note).

## Verification

- The 3 named originals present, gated, and correctly classified; `pifricDecsn` 2026 events on the board.
- Spend reported (requests ≤ 700, calls ≤ 30 LOW, ▷ cost). `pytest` still green. `estimate report` ×2 byte-identical, delta explained. `workflow.py validate` passes.
