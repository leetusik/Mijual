# Deferred: D25 Code comments and dev-tooling banners still name the retired product

## Context

## Why Deferred

chrome/Footer.tsx:15 and lib/api.ts:2 describe rendered output the rebrand changed; Makefile:1,110 and compose.yaml:1 print '── mijual dev stack ───' to the operator's own terminal. Left unchanged because the operator scoped P10 to user-facing only, and renaming the banners alone would make the terminal less consistent, not more — mijual-postgres, mijual:lock:pipeline, MIJUAL_* and both package name fields all deliberately stay.

## Trigger to Promote

Next time a slice edits those files anyway, or if the identifier rename is ever taken on

## Notes

