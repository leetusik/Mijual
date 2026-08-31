# Deferred: D39 404 라우트에만 폰트 preload 링크가 없다

## Context

## Why Deferred

Every reader route carries one link[rel=preload][as=font]; /_not-found carries none since it became request-time at P11.F3. Both faces still load and paint, one hop later. Whether P11.F3 caused it is UNTESTED — the decisive experiment was denied by the sandbox, so it is not attributed.

## Trigger to Promote

The next font or 404 work, or any Next upgrade

## Notes

