# P9.S10 — /ask re-cut: rail retired, start screen, 새 대화, sticky composer, widget empty state, three retirements

## Context

The last building slice: the page and widget become what R16 signed. Binding spec: `works/phases/active/P9/phase.md` → `### DECOMP2` → **`P9.S10` — the page, the widget, and the retirements** (read in full) and `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` §0's **폐기** block + §2.7b (page structure — remembering the two stale lines: **4** start cards, **no** meta card; the rail is gone) + §4 checks 19–26, with `output/r16-ask.css`'s page-section classes (`.apagec`/`.acol1`/`.atop`/`.anew`/`.astart`/`.acards`/`.acard` etc.) as the CSS source and `output/r16-parts.babel.js` (`A16Start`, `A16New`, `A16Header`, card fixtures) as reference markup. Read the `### P9.S3`–`### P9.S9` decision sections and S9's `result.md` — S9 left §2.7b's page classes and the `.m390` mirror deliberately to you; `Answer.tsx` now renders §2.8 and still carries the `다시 질문` footer control you retire; S8 landed `START_HEADING_KO`/`NEW_CHAT_KO`/`START_CHIPS_KO` (4 cards)/D1 in `copy.ts` and left the three retired constants for you to delete **with their call sites**.

Known call sites (verified pre-S9): `AskPage.tsx:82–93` — the `CraftPanel` rail with the scope chip (`scopeLabel` + ×), `VERIFIED_ONLY_KO`, `ANONYMITY_KO`; `AskWidget.tsx` — header scope chip + anonymity line in the empty state; `Answer.tsx` — `REASK_KO`/다시 질문 in the completed footer; `AskPageScope.tsx` — the scope UI component. Reconcile against the current tree (S9 touched `Answer.tsx`).

## Scope

1. **`/ask` single column** (§2.7b): delete the 340 rail and the two-column grid; one `max-width: 760px` centered column. **Empty state**: vertically centered (`min-height 560px`, 420 ≤767) — `START_HEADING_KO` (`--text-2xl`, `--text-xl` ≤767) → D1 intro (`--text-sm` ink-2) → composer → **4 start cards** (2-col grid, 1-col ≤767; `--surface-raised` + 1px `--border-soft`, min-height 56px, 12px padding, sans `--text-sm` ink-1, hover border `--live`; pressing sends the card's own sentence verbatim). Center-aligned start screen; input text and card text left-aligned. No anonymity line anywhere.
2. **새 대화** (D10): exists **only when a thread does** — sticky `.atop` top-right of the column (`--paper` bg, mono `--text-xs` ink-2 underline, 32/44px target); empties the thread only; no history UI. Not on the start screen.
3. **Composer**: page composer has no wrapping frame and no divider (input's own 1px only); bottom-sticky `.abar` (`--paper` bg) in the conversation state. Widget composer's R14 geometry untouched.
4. **Widget**: empty state = D1 intro (no anonymity line); header keeps only ↗ and × (scope chip + × removed — the store's `scope` may stay, it is simply not drawn); the event-detail preset strip behavior stays untouched.
5. **Three retirements, with call sites**: scope chip/× (header + rail; retire or gut `AskPageScope.tsx` as the tree dictates), anonymity line (both surfaces), 다시 질문 (`Answer.tsx` footer; `재시도` stays on disconnect turns only). Delete the retired constants from `copy.ts` (`VERIFIED_ONLY_KO`, `ANONYMITY_KO`, `REASK_KO` — real names per the tree) once no call site remains.
6. **≤767 mirror**: the `.m390`-equivalent rules S9 left — full-bleed blocks are S9's; your page classes need their ≤767 forms (1-col cards, 420 min-height, `--text-xl` heading, 44px targets).

## Constraints

- RESPECT THE DESIGN: §0/§2.7b verbatim; 4 cards, no meta card, no rail (the stale lines are overridden); no invented Korean; no history UI; exhausted turn stays as S9 drew it (no new string/inset/button).
- Both views over one store — no fork; check the widget↔page navigation and reload-restore still work (sessionStorage thread survives; the R14 baseline behaviors not superseded must keep working).
- Terse tests; `npm run typecheck` + `npm run smoke` + `npm run build` green; Python suite untouched; `python3 scripts/workflow.py validate`.
- Unsettled-in-the-flesh readings: catalogue on `## Operator Questions`, never invent.
- Doc impact + durable notes to `phase.md`; `result.md`; structured verdict. Never commit or transition state.
