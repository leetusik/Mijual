# Deferred: D43 This Mac's MagicDNS answer for www.jujutower.com (false-red make smoke-prod www line)

## Context

## Why Deferred

Tailscale's resolver (100.100.100.100) returns 104.219.250.36 / 2.59.170.19 for www.jujutower.com, in no Cloudflare range, so make smoke-prod can show a red www line that is not production; dig @1.1.1.1 returns the real pair.

## Trigger to Promote

The next red www line — check dig @1.1.1.1 before believing it; fix the local resolver or split-DNS.

## Notes

