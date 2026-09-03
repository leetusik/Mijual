# Deferred: D46 Cut the landing's residual idle main-thread frame: the IntersectionObserver that forces a style update on every serviced rendering opportunity

## Context

## Why Deferred

After P4.F11 the landing no longer produces a main-thread frame per display frame, but it still services ~1 in 6 of the compositor's rendering opportunities, each running IntersectionObserverController::computeIntersections twice and one UpdateLayoutTree over ~200 elements (122–159 UpdateLayoutTree per 8 s at 120 Hz, ~2 ms each, against 0 on the Cosmos-free /stocks). It sits outside Cosmos and is now the largest remaining idle cost on the route.

## Trigger to Promote

The next time landing idle cost is on the table, or the first battery/heat report from a reader on a high-refresh display

## Notes

