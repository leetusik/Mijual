# Deferred: D24 /ops has no 390px layout — the whole bar stacks, not just the mark

## Context

## Why Deferred

At 390px .mark computes to 11.34x148.75, one syllable per line, and all six tab labels stack the same way. P10's longer Korean string made the mark worse (MIJUAL OPS was 48.97x37.19, 2 lines) but the defect is pre-existing and wider than the mark: the ops bar has no phone layout. Not fixed in P10 because the two available fixes differ in scope — nowrap on .mark is signed styling and leaves six stacked tabs beside a horizontal mark, while the bar-wide fix is a responsive treatment nobody drew. The /ops door at 390 is fine.

## Trigger to Promote

Next ops design pass, or the first time /ops is needed from a phone

## Notes

