# Deferred: D47 scrollbar-gutter: stable cannot be verified on macOS overlay scrollbars (R1 F14 / Q5)

## Context

## Why Deferred

lib/scrollLock.ts sets body { overflow: hidden } with no gutter compensation and no scrollbar-gutter exists in the CSS; on Windows/Linux or macOS 'always show scroll bars' the page widens by the scrollbar width every time a sheet opens, but on this Mac the gutter measures 0, so the one-line fix would ship unverified

## Trigger to Promote

a Windows/Linux reader, a machine set to 'always show scroll bars', or a reader report of the page widening when a sheet opens

## Notes

