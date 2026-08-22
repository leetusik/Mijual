# Result — P7.DECOMP

Nine middle slices cut, all bare folders. No code changed, no record edited, no plan pre-filled.
The full breakdown, the per-item root causes, the six design-collision readings, the constraints
and the open questions are in [`../../phase.md`](../../phase.md); this file records what was done
and how it was checked.

## The finding that shaped the decomposition

**Six of the eleven complaints are one bug, and it is not in the product.** `next dev` bound to
`0.0.0.0` serves its dev resources only to `localhost` unless `allowedDevOrigins` names the host —
and the operator's URL, the one `make stack-status` prints, is `http://127.0.0.1:3000`. Two client
chunks 403, the HMR socket is rejected, **hydration never completes**, and Next's dev client
reloads the tab on its failed reconnect. Items 4b (dead 펼치기), 6 (static countdown), 7
(state-stomping reload), 8 (dead AI 질문 send) and 11 (missing widget) all disappear on
`http://localhost:3000` — measured side by side, three origins, one dev server.

That is why `P7.S1` is one slice covering five complaints and everything else waits on it.

Two further causes are genuinely separate: **item 5** is `useAccount`'s StrictMode double-effect
(`components/chrome/useAccount.ts:74-84` — the module-level `probedPath` guard makes StrictMode's
second run a no-op while the first run's cleanup discards the only answer, so the chrome renders
no 로그인 entry at all in dev), and **의견 (vocky)** is an unset `NEXT_PUBLIC_VOCKY_SRC` with no
vocky script to point it at — an operator decision, deliberately assigned to no slice.

## Slices created (bare folders, `slice.json` only)

| id | order | risk | kind | covers |
|---|---|---|---|---|
| `P7.S1` | 1 | high | fix | dev-origin unblock — items 4b, 6, 7, 8, 11 |
| `P7.S2` | 2 | high | fix | login reachable — item 5 |
| `P7.S3` | 3 | high | fix | board list length + working 펼치기 — item 4 |
| `P7.S4` | 4 | high | fix | 내 종목 조회 typeahead (API route + UI) — item 2 |
| `P7.S5` | 5 | high | fix | focus treatment — item 3 |
| `P7.S6` | 6 | **low** | fix | nav slot removal — item 1 |
| `P7.S7` | 7 | high | fix | self-narrating copy sweep — item 10 |
| `P7.S8` | 8 | high | fix | 포트폴리오 tidy + 챙겼습니다 — item 9 |
| `P7.S9` | 9 | high | fix | fidelity sweep, dev + prod, operator's origins — all 11 |

`S2`–`S8` depend on `S1`; `S9` depends on all of them. `P7.REVIEW` stays last (order 9999).

Only `P7.S6` is `low` (the `mid` tier): verified to be exactly a `NAV_LINKS` entry removal —
`NAV_LINKS` is read only by `Nav.tsx`, and `STOCKS_LABEL_KO` is imported independently by four
other modules, so the constant stays in use and nothing else moves. Everything else writes real
code or spans more than one file.

No `co-work` slice and no `DECOMP2`: the operator ruled out a new design round, so the collisions
are resolved against the landed record in `phase.md` instead.

## Validation

| command | outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **OK** (see below) |
| `python3 scripts/workflow.py next` | shows **`P7.S1`** as the next slice after `P7.DECOMP` |
| `make stack-status` | stack was already up and was left up (postgres, api pid 99133, web pid 99145) |

Read-only investigation used `curl` against the running API, `grep`/`sed` over the repo and
`node_modules/next`, and headless Chrome over CDP against the running dev server (a scratch
profile under the session scratchpad, killed afterwards). Nothing in the repo was written except
this file, `phase.md`, and the nine `slice.json` files `new-slice` created.

### Evidence kept in `phase.md` rather than here

The three-origin measurement table, Next's own allow-list code, the `useAccount` StrictMode trace
with its measured `loginLinks: 0` / one 200 probe / empty-slot markup, the focus-ring geometry
(input right edge 656, 조회 button starts at 656, gap 0; `--focus-ring` → `--r1` → `#8fb2e8`), the
board's 386/60/4/488 counts, the "never a candidate list" product rule that item 2 overrides, and
the item-10 copy inventory.

## Deviations from `plan.md`

1. **No separate "landing liveness (6 + 7)" slice.** The plan's suggested shape listed one; the
   measurements show both items are RC-A artifacts with no product defect behind them (there is
   no auto-refresh feature in the app at all, and `Countdown.tsx`'s interval is correct), so they
   are folded into `P7.S1`'s verification. If the operator wants real data auto-refresh after
   `S1`, that is new behaviour — Open Question Q5, not a P7 fix.
2. **No separate "AI 질문 surfaces (8 + 11 + 의견)" slice.** 8 and 11 are RC-A and close in `S1`
   (a full agent turn was streamed successfully on `localhost` during this investigation); 의견 is
   an operator decision that no amount of code can close. Cutting a slice for it would have handed
   an executor an unfinishable job.
3. **`doc_impact` is not `none`.** The investigation found `docs/current/frontend.md`'s
   browser-check note to be incomplete in a way that hid this class of bug, so one Doc impact line
   is recorded for `P7.REVIEW`.
