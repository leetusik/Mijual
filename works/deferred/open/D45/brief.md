# Deferred: D45 Measure Malgun Gothic's Hangul advance and close the Windows half of the font fallback

## Context

## Why Deferred

notoSansKr Fallback Malgun ships size-adjust: 100% with the vertical overrides only — P4.F5 could not obtain or measure Malgun Gothic on a Mac and refused to guess, so Windows readers get a strict improvement with the width half open; closing it is one advance-width read plus one number in frontend/app/shell.css (recipe in the CSS comment)

## Trigger to Promote

The next time a Windows machine is available, or the first Windows-sourced report of a cold-cache re-wrap

## Notes

