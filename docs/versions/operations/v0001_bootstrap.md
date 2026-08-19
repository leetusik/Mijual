---
doc_id: operations
version: v0001
created_at: 2026-08-19T16:19:45+09:00
source: bootstrap
summary: Initial operations doc
previous: null
---

# Operations

## Status

No operations truth is finalized yet.

## Purpose

Use this doc for local development, environment variables, deployment, infra, jobs, observability, backups, and recovery.

## Local Development

- Install:
- Run:
- Test:
- Build:

## Environment Variables

| Name | Required | Purpose | Notes |
|---|---|---|---|
| <NAME> | yes/no | <purpose> | <notes> |

## Knowledge (phase explainers)

The `explain` skill ships with this workspace, in `.claude/skills/`.
Explaining is an **operator-run step, separate from the phase review**:
run `/explain` for a phase when you want one and it saves an interactive HTML explainer to
the knowledge service. The review itself writes no explainer — it only reports the pointer
`explain: not written — run /explain for this phase`.

**Setup is on first use, and it asks first.** Run `/explain`; if no knowledge base is
configured it offers to create one on the hosted service at `https://knowledge.hi2vi.com`
— it asks for an email, installs the `knowledge` CLI, signs you up (or logs you in), and
writes an org-level key to `~/.config/knowledge-kb/config.json` at mode 0600. One org key
serves every repo. Each document's project defaults to the repo's directory name.

Already have a knowledge base — hosted or self-hosted? Skip the setup entirely by exporting
the credentials in `~/.zshenv` (sourced by every zsh invocation) — never a repo `.env`,
which Claude Code does not auto-load and which risks committing the secret:

    export KB_API_BASE_URL="https://knowledge.hi2vi.com"
    export KB_API_TOKEN="vk_..."

- **Alternative (Claude Code plugin):** `/plugin marketplace add leetusik/knowledge` →
  `/plugin install knowledge@knowledge` → `/knowledge:setup`, then `/knowledge:explain`.
  A separate namespace from this workspace's `/explain`; you do not need both.

Drive knowledge through the skill/agents; REST is the substrate.

## Deployment

- Target:
- Process:
- Rollback:

## Scheduled Jobs / Workers

- <job>: <schedule/trigger>

## Observability

- Logs:
- Metrics:
- Alerts:

## Backup / Restore

- <policy>

## Open Questions

-
