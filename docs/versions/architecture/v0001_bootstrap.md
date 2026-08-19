---
doc_id: architecture
version: v0001
created_at: 2026-08-19T16:19:45+09:00
source: bootstrap
summary: Initial architecture doc
previous: null
---

# Architecture

## Status

New Project is newly bootstrapped. This document should describe stable system-level truth as the app takes shape.

## Current Repo Shape

- `CLAUDE.md`: the compact routing contract
- `docs/current/`: generated latest doc snapshots
- `docs/versions/`: immutable durable doc versions by category
- `docs/index.json`: latest-version map
- `works/state.json`: current/next pointer
- `works/index.json`: generated machine index
- `works/backlog.md`: generated human dashboard
- `works/phases/active/`: active phase folders
- `works/phases/archived/`: archived phase folders
- `works/deferred/`: deferred job folders
- `scripts/workflow.py`: workflow and docs version manager
- `.claude/`: Claude Code entry points (skills, subagents, settings)

## System Shape

- <frontend runtime>
- <backend runtime>
- <database / persistence>
- <background workers / queues>
- <external integrations>

## Boundaries

- Frontend boundary:
- Backend boundary:
- Data boundary:
- External service boundary:

## Cross-Cutting Constraints

- <constraint>

## Open Questions

-
