# Deferred: D27 /ops/feedback overflows horizontally at 1280 — the desktop half of the ops layout gap

## Context

## Why Deferred

The feedback table computes to 1327px inside a 1280 viewport, so the whole page scrolls sideways on the operator's own primary width. No other /ops route overflows at 1280. Same root as D24 (the ops surface has no width strategy at all), but D24 is scoped to 390 and would be closed by a mobile layout that leaves this untouched.

## Trigger to Promote

Whenever D24 is picked up, or the first time the operator needs the feedback tab on a 1280 screen

## Notes

