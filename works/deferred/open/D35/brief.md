# Deferred: D35 동적 세그먼트의 404는 SSR 없이 클라이언트에서만 그려진다

## Context

## Why Deferred

notFound() thrown by a dynamic segment (/events/<unknown>, /stocks/<unknown>) returns <html id="__next_error__"> with no SSR content, so that 404 is drawn wholly on the client and has an empty first paint. Pre-existing; found while fixing P11.F3's prerendered /_not-found and deliberately not touched there.

## Trigger to Promote

Next 404/error-surface work, or P4 deployment hardening

## Notes

