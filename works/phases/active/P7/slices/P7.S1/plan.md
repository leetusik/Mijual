# Plan — P7.S1: dev origin unblock — hydration on 127.0.0.1 / Tailscale

## Why this slice exists

`P7.DECOMP` (see `phase.md` → "RC-A") measured that `next dev -H 0.0.0.0` (what `make stack-up`
runs) serves its `/_next/*` dev resources only to `localhost` / `**.localhost` / `0.0.0.0`:
Next's `block-cross-site-dev.js` builds `['**.localhost', 'localhost', ...allowedDevOrigins,
hostname]` and 403s everything else. The operator opens `http://127.0.0.1:3000` (the URL
`make stack-status` prints) and the Tailscale `http://100.x.x.x:3000` — neither is allowed, so
two client chunks 403, the HMR socket is rejected, hydration never completes, and the dev client
reloads the tab on failed reconnect. That one bug *is* operator items **4b (펼치기 dead), 6
(countdown static), 7 (typing wiped by "auto reload"), 8 (AI 질문 can't send), 11 (no widget)**,
and also the dead-hydration half of 5 and 9. Nothing in product code is at fault for those.

This slice is the gate for the whole phase: until it lands, no later slice can honestly verify a
fix in the operator's browser.

## Scope

1. **`frontend/next.config.ts` — add `allowedDevOrigins`.** It must cover:
   - `127.0.0.1` (always), and
   - the operator's Tailscale IPv4 (`100.x.x.x`, not stable across machines — do not hardcode a
     literal IP as the only path). Read Next 16.3.2's actual matcher
     (`node_modules/next/dist/server/lib/router-utils/block-cross-site-dev.js` and whatever
     `isCsrfOriginAllowed` delegates to) to learn exactly which patterns are accepted (Next docs
     document hostnames and `*.example.com`-style wildcards; the DECOMP note says `**.`-style
     patterns work — verify). Prefer a small, honest seam: a static list (`127.0.0.1`, a
     wildcard for the 100.64.0.0/10 Tailscale range **if** the matcher genuinely supports it —
     test it, don't assume) plus an env override (e.g. `MIJUAL_DEV_ORIGINS`, comma-separated
     hostnames) that the Makefile can fill. Keep a comment in the config explaining why (one
     tight paragraph in the style of the existing API-seam comment; cite `P7.S1`). This setting
     is dev-only — confirm it has no effect on `next build && next start`.
2. **`Makefile` — make the seam real.** `web-up` should pass the Tailscale IP (the same
   `tailscale ip -4` lookup `stack-status` already does) into the env seam when available, so
   the dev server accepts the Tailscale origin without the operator editing anything. Update the
   header comment (it currently claims both origins "work"; make it true and say why). Keep the
   Makefile's existing shape — no new targets unless really needed.
3. **Restart the dev web process** so the new config is live (`next.config.ts` is read at start):
   the stack is up (`make stack-status`; api pid + web pid in `var/stack/`). Stop **only the web
   process** cleanly (the `stack-down` loop logic for `WEB_PID`, or `make stack-down && make
   stack-up` — either is fine, but leave postgres + api + web all running at the end and confirm
   with `make stack-status`). Check `var/stack/web.log` shows no `Blocked cross-origin request`
   lines after the restart.
4. **Verify in the operator's runtime — this is the substance of the slice.** Headless Chrome
   over CDP (the way DECOMP measured it; the Chrome binary and approach it used are in
   `P7.DECOMP/result.md`), against the running `next dev`, on **three origins**:
   `http://localhost:3000`, `http://127.0.0.1:3000`, and the Tailscale URL
   `make stack-status` prints. For each origin re-measure DECOMP's table:
   - `/_next/*` requests returning 403 → must be **0** on all three;
   - HMR WebSocket handshake → connected on all three;
   - AI 질문 launcher present in the DOM on `/` at 1440 wide → **1** on all three;
   - countdown digits change over ~2.5 s on `/` → yes on all three;
   - a 펼치기 strip click (전환청구 진행 중 / 일정 추후결정) grows the row count → yes;
   - type into the hero input, wait 30 s → value **kept**, no document reload (compare
     `performance.navigation`/a marker set on `window`);
   - open the AI 질문 widget, send a short question (e.g. `계양전기 유상증자`) → an answer streams
     (tool rows / answer / footer appear) on `127.0.0.1` — item 8 closed in the operator's own
     origin, not only on localhost;
   - `/portfolio` sample: the 챙겼습니다 checkbox toggles (label flips) on `127.0.0.1`;
   - `/auth/login` form submit reaches the API on `127.0.0.1` (a wrong password yields the form's
     error, i.e. the request round-trips — do not create accounts).
   Also confirm the production path is untouched: `npm run build && npm run start` on a
   **different port** (e.g. `-p 3100`; never touch the dev server's `.next` — see Constraints in
   `phase.md`: build into a separate dir or stop dev first and restart after; the simplest safe
   option is `NEXT_DIST_DIR`-less: stop web, build, start on 3100, run the same checks on
   `http://127.0.0.1:3100` for launcher/countdown/펼치기, stop it, restart `make web-up`). Kill
   every process you start; leave the dev stack as you found it.
5. **Record which operator items are closed by this slice with no further product code**
   (expected: 4b, 6, 7, 8, 11; plus the hydration half of 5 and 9) in `result.md` and in
   `phase.md` Findings, with the measured numbers. If any of them does **not** close on
   `127.0.0.1` after the fix, that is a real finding — record it precisely (selector, origin,
   numbers) so the orchestrator can cut or re-plan a slice; do not silently widen this slice into
   product fixes.
6. **Doc impact:** extend the existing `frontend` Doc impact line in `phase.md` (DECOMP wrote it)
   with what the fix is (`allowedDevOrigins` + the `MIJUAL_DEV_ORIGINS`/Makefile seam) and the
   rule for future browser checks: dev verification runs on `127.0.0.1`/Tailscale, not
   `localhost`. Add an `operations` Doc impact line if the operations doc describes the dev stack
   / Makefile (check `docs/current/operations.md`). No `doc-new-version`.
7. **Validation commands** (report outcomes in `result.md`): `cd frontend && npm run typecheck`
   (config is TS), `make stack-status` (all three up at the end), the CDP measurements above
   (numbers per origin), and `python3 scripts/workflow.py validate`.

## Out of scope

No product code changes (components, copy, API). No fix for `useAccount` (that is `P7.S2`). No
board pagination, typeahead, focus, nav, copy, portfolio work. No `doc-new-version`. No commits,
no state transitions.

## Verdict

Return `done` with: files changed, the per-origin measurement table (before/after), the list of
operator items closed, the production-build check result, the stack state on exit, and any
finding that needs a new slice. `needs_operator` only if the Tailscale interface is down and the
origin cannot be exercised at all (then verify 127.0.0.1 fully and say so). `blocked` if Next's
matcher cannot be made to accept the origins.
