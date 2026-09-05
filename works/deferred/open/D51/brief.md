# Deferred: D51 Janitor for long-dead unverified accounts and their spent code grants

## Context

## Why Deferred

P13 ships no sweep by design (a re-signup re-takes any address at any age), so unverified account rows and email_verification rows accumulate with nothing to remove them; verification_pending_since already doubles as the age stamp.

## Trigger to Promote

When the unverified count on production becomes noticeable, or the next backend housekeeping phase.

## Notes

