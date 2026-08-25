# Deferred: D22 암시적 프롬프트 캐시가 한 번도 적립되지 않는 이유를 조사

## Context

## Why Deferred

cached 0 on every live turn of two independent passes (16 + 12), including the same question minutes apart, against a ~5.5k-token static prefix that should clear Gemini's 4,096-token floor; MID + 20 rounds is not being blunted by caching.

## Trigger to Promote

When per-turn cost matters, or before deploy.

## Notes

