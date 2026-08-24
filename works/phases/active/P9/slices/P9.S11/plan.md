# P9.S11 — fidelity and the functional sweep in the Operator Runtime

## Context

The last slice before the review: the phase's work meets the running product. Binding spec:
`works/phases/active/P9/phase.md` → `### DECOMP2` → **`P9.S11` — fidelity and the functional sweep**
(read in full) and `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` **§4 — the
26 checks** (the checklist is the contract; the three known-stale lines are overridden by the signed
copy: **4** start cards, **no** meta card, **no** rail — see `### P9.S2 — R16 design landed` in
`phase.md`). Two mandatory yardsticks (design-cowork §Verifying): **matches the record** *and*
**works as a product**.

Read first: `phase.md`'s `### P9.S3`–`### P9.S10` decision sections — every decision there is
inherited fact (notably S10's: `newChat()` semantics, `state.turns.length` as the only state switch,
the `plain` composer flag and its known text-loss consequence, `.atop` as a column sibling, the
retired 프리셋 스트립 catalogued as an Operator Question, the cosmos-scope harness caveat and the
headless-Chrome 500px window floor). Flagged for you specifically: the in-place `pending → done`
calc replacement without block jump (S3/S9 notes ~line 1562) and the 근거 N건 chip-count
reconciliation once data-row chips render (~line 1587) — confirm both in the flesh, don't rediscover.

## The runtime (the manifest, verbatim discipline)

`docs/current/operations.md` §Operator Runtime is binding:

- **Dev:** `make stack-up` → Postgres + API `127.0.0.1:8000` + `next dev` on `0.0.0.0:3000`.
  Browse **`http://127.0.0.1:3000`**. Logs in `var/stack/{api,web}.log`. `make stack-status` / `make stack-down`.
- **Production build, additionally:** `cd frontend && npm run build && npm run start` (API unchanged)
  — this phase touched hydration-adjacent surfaces (SSR start screen, sessionStorage restore,
  StrictMode double-effects on the stream), exactly the dev/prod gap classes.
- **Browser:** real Chrome via headless CDP from Bash (the S9/S10 precedent). Desktop 1440 and a
  mobile ≤767 viewport — use CDP `Emulation.setDeviceMetricsOverride` to get a true 390 metrics
  emulation past the 500px window floor S10 recorded.
- The **tailnet-from-another-device** origin is operator-only — do not claim it; list it explicitly
  as walkthrough material in `result.md`.
- Live model turns need the configured Gemini key (the stack's own env). If a live streamed turn
  cannot be exercised, do **not** fake or skip silently: verify everything else, and return the
  un-exercised checks as an explicit list for the review/walkthrough. Never claim a check you did
  not see.

## Scope

1. **build-prompt §4, all 26 checks**, in dev at 127.0.0.1:3000, desktop + mobile viewport; re-check
   the hydration/stream-sensitive ones (start screen, reload-restore, streaming replacement,
   새 대화, widget↔page) in the **production build** too. Record each check pass/fail/blocked with
   one line of evidence.
2. **Functional sweep:** every visible control does something observable (start cards send their own
   sentence, 새 대화, 중지, 재시도 on a disconnect, 자세히/접기 folds, 모두 보기 (N), citation chips
   open/close, footer links, widget ↗ and ×); focus/hover/keyboard on every new control; liveness
   over time — status line replaces per phase and dies at first text, ToolTrace folds at ≥4 on
   completion, calc `pending → done` replaces in place with **no block jump**, a long streaming turn,
   typing-and-waiting rather than submit-only.
3. **The whole `## Regression Checklist`** in `docs/current/qa.md` (line ~262) — every line, not just
   P9's. Known-stale baselines: it says pytest **142** and smoke **16/16**; the tree is now **154**
   and **22** — expected growth, not a failure; note the correction as a `qa` Doc impact line for the
   review to consolidate (never hand-edit `docs/current/`).
4. **Departures from the record are fixed here** (small, surgical — this is an implementation slice);
   anything the record never settled, or drew but reads badly in the flesh, is catalogued on
   `## Operator Questions`, never silently improved. RESPECT THE DESIGN.
5. Leave the machine clean: `make stack-down`, kill the production `npm run start` you started.

## Constraints

- No new features, no restyling, no invented Korean; fixes only restore fidelity or basic function.
- Terse tests only if a fix warrants one; `npm run typecheck` + `npm run smoke` + `npm run build` +
  `.venv/bin/pytest -q` + `python3 scripts/workflow.py validate` all green at the end.
- Doc impact lines (qa headline checks for this phase; the count correction) + durable notes to
  `phase.md`; `result.md` from scratch with the full 26-check table and the sweep findings;
  structured verdict. Never commit or transition state.
