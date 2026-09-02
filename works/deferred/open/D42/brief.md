# Deferred: D42 Settle the harness's production boundary (ssh oracle-cloud reads, docker compose over ssh, .env.prod credential read)

## Context

## Why Deferred

ssh reads are allowed or denied unpredictably (docker ps yes, docker compose ps no, .env.prod credential read no), which cost the review the /ops 개요 check and cost P4.S4 the D-day demo. Either add explicit allow rules to .claude/settings.local.json or accept that box inspection and /ops logins are operator-run.

## Trigger to Promote

The next slice that needs box inspection or an /ops login.

## Notes

