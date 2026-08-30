# Deferred: D26 The AI 질문 launcher's open state is covered by the widget and can never be seen

## Context

## Why Deferred

The widget is position:fixed right/bottom var(--space-6) z-index:40 at 440x620 and the launcher is the same corner at z-index:30, so the widget sits exactly on top of it; elementFromPoint at the launcher's centre returns the widget's 보내기 button, and the launcher is inert while open. R17 re-signed an open-state row (mark fades to a 16px x in #eaf2ed) that therefore renders for nobody. The widget's own header x works, so nothing is unreachable -- but either the state should be retired from the record or the geometry should let it show, and both are design decisions. Pre-existing since R14/P8; Ask.module.css was not touched by P10.

## Trigger to Promote

The next design round that opens the AI 질문 surface, or the next time the launcher's state table is edited

## Notes

