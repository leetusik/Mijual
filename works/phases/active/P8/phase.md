# Phase P8: Design polish pass — audit & polish every surface

_Intent: see [intent.md](intent.md)._

## Objective

Audit and polish the whole 미주알 product surface by surface — no new features. For each surface: the orchestrator walks it in the operator's runtime, reports what is dead/confusing/off, and asks the operator what's wrong; the operator answers how it should be fixed; a Claude Design round (design-cowork, one handoff + pending gate per surface) polishes it; an apply slice implements that signed round faithfully (RESPECT THE DESIGN) and verifies it in the operator's runtime — then the next surface. Opens with a small fix slice for the AskWidget t1 duplicate-key bug.

## Context

## Decomposition

_Slice breakdown and rationale — filled by the `P8.DECOMP` slice._

## Findings & Notes

_Durable findings and cross-slice notes; `DECOMP` seeds this, and each slice appends when it finishes._

## Operator Questions

_Questions only the operator can answer; every entry is routed at the review -- folded into the acceptance walkthrough (`accept-gate --open`) or filed with `defer-job`. An unrouted entry is a review finding._

## Constraints

## Open Questions

-
