# P4.F6 — Trim the four unread `countdown` fields out of the landing's RSC payload

`kind: fix`, `risk: high`, `slice-executor-high`. Cut from `P4.R1`'s ranked list (item 2). Operator
instruction behind it (2026-09-02, verbatim): 「you look up the cloudflare's poor LCP, INP, and CLS
performance stuffs … and create slices for fix them.」 Frontend only, **zero visual change**, **no
deploy in this slice** (`P4.S9` releases F5 + F6 + F8 together).

## What R1 measured (`slices/P4.R1/result.md` § 1 payload; do not re-derive)

The landing document is **354,266 B**, of which **277,870 B (78 %) is the RSC flight** — the whole
`BoardResponse` serialised as props for the client `<Board>` (`frontend/app/page.tsx:57–67`:
`const [summary, board] = await Promise.all([getBoardSummary(), getBoard()])` → `<Board board={board} />`).
`/api/board` is 164,534 B / 393 rows (median 378 B a row) + a 24,873 B `open_now` strip + `tbd`.
All rows must stay (the tabs filter in the browser by design and the 60 s refresh diffs previous
against next), so the lever is **field width**: `BoardRow` reads `countdown.label_ko / date / dday /
days` and `offering` only, while every row also carries `countdown.window` (a 2-tuple),
`window_state`, `reference` and `source` — ~135 B a row, ~35 % of the row — which only the event
page, the lookup and the portfolio ever read. On the wire the landing is 40 KB br, so this is a
**parse/hydrate** saving (tens of ms at 390 with 4× CPU, maybe less), not bandwidth. Expected: ~90 KB
off the document. **Measure before and after and report the delta honestly, even if small.**

## Do

1. **Project on the server, once, in `frontend/app/page.tsx`.** After `getBoard()` resolves, map
   the response to a landing projection: every row in `rows`, `open_now.rows` and `tbd.rows` keeps
   `event_id, corp_code, corp_name, rights_type, rcept_no, state, offering` and a **narrowed**
   `countdown: { label_ko, date, dday, days }`; `reference`, `counts` and `freshness` stay as they
   are. Keep it a small pure function (in `page.tsx`, or `frontend/lib/board.ts` if one exists —
   check `frontend/lib/` first and do not create a module for one function if `page.tsx` reads
   cleanly), with a comment saying why (the flight is serialised into the HTML; these four fields
   are read by nobody on the landing) and pointing at `P4.R1`.
2. **Narrow the types, do not fork them.** In `frontend/lib/types.ts` add
   `LandingCountdown = Pick<Countdown, "label_ko" | "date" | "dday" | "days">`,
   `LandingRow = Omit<BoardRow, "countdown"> & { countdown: LandingCountdown }`, and a
   `LandingBoard` shaped like `BoardResponse` with `LandingRow` rows in the three lists (keep the
   doc-comment register of that file — it explains *why* a shape is what it is). `Board.tsx`,
   `BoardRow.tsx` and the helpers they import type against the landing shapes; the browser-side
   refresh (`Board.tsx` ~line 165, `const next = await getBoard()` → `apply(next)`) keeps fetching the
   full `/api/board` — a `BoardResponse` is structurally assignable to `LandingBoard`, so `apply`
   accepts it unchanged; if TypeScript disagrees anywhere, narrow at the call site with the same
   projection function rather than widening the prop type back. `BoardResponse`, `/api/board`'s
   contract, the event page, the lookup and the portfolio are **untouched**.
3. **Prove nothing on the board reads the dropped fields:** `npx tsc --noEmit` (or the repo's
   typecheck script) passes with the narrowed prop type — that is the proof; also `grep -rn
   'window_state\|\.reference\b\|\.source\b\|countdown\.window' frontend/components/landing` → no
   hits. Confirm `diff()` / `keep()` / `RowChange` in the board helpers compare only fields that
   survive the projection (if the diff keys on a dropped field, the 갱신됨 highlight would change —
   read it before deciding).
4. **Measure**, against a local production build (a copy of `frontend/`, built with
   `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build`, served by `node
   .next/standalone/server.js` on **:3014** with `.next/static` and `public/` staged in, against the
   dev API on 8010 — never `next start` under `output: "standalone"`; the operator's 3010/8010 stay
   up): document bytes of `/` (`curl -s -H 'Accept: text/html' … | wc -c`) and the flight share
   before/after; and in real headful Chrome over CDP at R1's mobile profile (412×915, DPR 2.625,
   4× CPU, ≈1.6 Mbps / 150 ms), three cold loads before and after: FCP, LCP, the hydration long
   tasks, `Performance.getMetrics` script duration. Reuse R1's harness (cited by scratchpad path in
   its `result.md` § method). **The dev API's board is the dev corpus (row count may differ from
   production's 393) — say what n was; production numbers land at the review after `P4.S9`.**
5. **Visual + behaviour equivalence:** screenshots of `/` at 390 and 1280 before/after byte- or
   AE-identical with the same data; the tabs, 「15건 더 보기」, and a forced refresh (dispatch a
   `visibilitychange` after hiding, or wait 60 s) still work — drive them once in the CDP session and
   say what you saw.
6. **No test file** (the contract's rule; the typecheck is the proof, the browser the verification).
   Lint/typecheck/build clean.
7. **`phase.md`**: `## Decisions` — one line (the landing serialises a projection; the four fields
   and why; the measured document delta); `## Doc impact` — `frontend` (Landing data flow: the
   projection in `page.tsx`, the `Landing*` types, the refresh path still fetching the full board);
   consume item 2 of the `(from P4.R1, for the fix slices)` note in place; rewrite `## Now` (≤ 15
   lines): F5 + F6 done and **not yet deployed**, `P4.F8` next, then `P4.S9` (the batched
   frontend-only release before **2026-09-07 11:00 KST**, aim 09-05), then the re-review; keep the
   gate-shut line.
8. **`result.md`** verdict-block-first: the before/after byte and timing table (n, medians), the
   typecheck proof, the equivalence checks, deviations.

## Hard rules

Frontend files only (`frontend/app/page.tsx`, `frontend/lib/types.ts`, `frontend/components/landing/
Board.tsx` / `BoardRow.tsx` and their helpers — nothing under `src/`, no API change); no deploy,
nothing on the box, production read-only; never the operator's Chrome profile; keep 3010/8010 up;
stop every server/browser you start; the repo is public — no secret values; no `git commit`/`push`;
no workflow state commands other than `python3 scripts/workflow.py validate`; `uv run` without
`--with`. **Zero visual change** — if the projection would change anything a reader sees, stop and
return `escalate`-style findings in `result.md` with `needs_operator` rather than adapting the UI.

## Validate

`npx tsc --noEmit` and lint clean; `npm run build` succeeds in the copy; the grep above is empty;
document bytes of `/` drop (report the number); screenshots identical; `python3 scripts/workflow.py
validate` passes; `git diff --stat` → the frontend files named, `phase.md`, this slice's `result.md`.

## Addendum (orchestrator, 2026-09-03, at dispatch)

`P4.F5` landed in `frontend/app/fonts.ts` and `frontend/app/shell.css` only (commit `70daeaf`) —
no overlap with this slice's files. It also found that the event page's residual CLS (0.0325) is
「이 마감 알림 받기 →」 being inserted after `GET /me` resolves — **not this slice's concern**; do not
touch it. When you measure, F5's fallback faces are in the tree, so your cold-cache mobile numbers
will already show CLS ≈ 0 on the landing; your before/after is about **bytes and hydration time**.
`npm run typecheck` and `npm run smoke` (22 node tests) are the repo's typecheck/lint equivalents
(there is no ESLint config in this project).
