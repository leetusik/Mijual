# Deferred: D48 조회 revisit reflow on a 놓친 돈 stock (+140 px, CLS 0.01232, identical on HEAD)

## Context

## Why Deferred

On a stock serving 놓친 돈 rows, a revisit with a remembered holding still reflows that section: the per-holding cells fill, the 계산 근거 band inserts and the mmhead prompt leaves, moving the breakdown 140.19 px once; P12.F4 neither caused nor cured it, and reserving it means measuring row heights that depend on served text nobody has measured

## Trigger to Promote

the next phase touching /stocks/{corp_code}, or a reader complaint about the breakdown jumping on revisit

## Notes

