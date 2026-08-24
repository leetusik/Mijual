# Deferred: D8 Strip the // eyebrow from the accessible name on 조회 and 보유 종목 (Q21)

## Context

## Why Deferred

R10 fixed it on the detail surface with aria-label; 조회 draws it with .eyebrow::before (Chrome folds generated content into the name) and 보유 종목 prints it as literal text. A screen reader reads the slashes on both.

## Trigger to Promote

Each surface next round, or as one small cross-surface job before P4

## Notes

