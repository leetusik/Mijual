## Promoted Deferred Context

# Deferred: D7 Make the notification_pref save an upsert (Q49)

## Context

## Why Deferred

Two concurrent PUT /portfolio/notifications -> 500: unique constraint on account_id with a read-then-insert path; both saves miss the row and the second INSERT raises UniqueViolation (measured, traceback in var/stack/api.log, uq_notification_pref_account). Unreachable by hand today only because the chip handler disables chips in flight.

## Trigger to Promote

Before P4 Ship & Submit, or the moment any second client can save preferences

## Notes

