# Deferred: D44 board 자동 갱신 re-downloads the whole board every 60 s per open tab (no ETag/304, no delta endpoint)

## Context

## Why Deferred

One request of 18,360 B br / 164 KB raw per tab-minute straight to the origin; origin load and Oracle egress scale with concurrent readers, not with data change (the corpus moves at 07:30/19:30 KST). Measured by P4.R1.

## Trigger to Promote

When concurrent readers or egress start to matter, or when a 정정 makes a delta endpoint worth having anyway

## Notes

