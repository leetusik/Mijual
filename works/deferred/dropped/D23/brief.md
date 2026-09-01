# Deferred: D23 P4 mail subject still carries the retired name [미주알]

## Context

## Why Deferred

The signed R5 mail spec quoted at src/mijual/mail.py:14 renders the subject [미주알] {jongmok} — {magamname} D-{n} ({date}). It is unimplemented, so nothing sends it today and it was out of P10's scope — but P4 implements the 마감 임박 mail and will ship the retired name unless the operator re-signs the subject.

## Trigger to Promote

When P4 implements the 마감 임박 mail, before the first send

## Notes

