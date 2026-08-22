# Plan — P7.S6: nav — drop the 내 종목 조회 slot (operator override of the signed three-slot nav)

## Why

Operator item 1: remove the "내 종목 조회" item from the global nav — that surface is reached from
the 관제 현황판 (the landing hero *is* the 내 종목 조회 search), R3's detail link-out, and the AI
질문 link row. `P7.DECOMP` verified (`phase.md` → "Item 1" and **Design-collision reading #2**) that
this is exactly one entry removal: `NAV_LINKS` in `frontend/components/chrome/copy.ts` is read only
by `Nav.tsx` (desktop links + mobile sheet rows, both `.map` over it), and `STOCKS_LABEL_KO` is
imported independently by `lookup/LookupHeader.tsx`, `ask/links.ts`, `ask/copy.ts`, `lookup/copy.ts`
— so the constant stays and no import breaks.

This is an **operator override of the signed record** (R2 signs a three-slot nav; R4/R6 relabelled
slots; R5-6 withdrew a fourth). Do only the override: remove the entry and nothing else — no
re-centring, no re-spacing, no new slot, no change to `Nav.tsx`, `Nav.module.css`, the footer, or
any label.

## The edit (one line + its comment)

In `frontend/components/chrome/copy.ts`: delete the `{ label: STOCKS_LABEL_KO, href: ROUTES.stocks }`
entry from `NAV_LINKS`, and amend the doc comment above it so it is true: the nav now renders two
slots — 관제 현황판 · AI 질문 — because the operator removed 내 종목 조회 in P7 (item 1; the surface
stays reachable from the hero search, the R3 link-out and the agent's links); keep the supersession
history the comment already tells. If `STOCKS_LABEL_KO` would otherwise become unused in this file,
keep it anyway — it is imported elsewhere (verify with `grep -rn STOCKS_LABEL_KO frontend/`). If
`ROUTES` is now unused in `copy.ts`, drop the unused import only if typecheck/lint would complain;
otherwise leave it.

**If this turns out to be more than that** (another reader of `NAV_LINKS`, a layout that assumes
three links, a failing typecheck you cannot fix in `copy.ts`), return `escalate` with what you saw.

## Verify

Dev stack up (`make stack-status`); Fast Refresh. `cd frontend && npm run typecheck` (pass). Then,
with `curl -s http://127.0.0.1:3000/ | grep -o '내 종목 조회' | wc -l` (served HTML — the hero H1 still
says 내 종목 조회 once, the nav no longer does: compare before/after counts) and a quick headless
Chrome check if the CDP approach from `P7.S1`–`S4` `result.md` is easy for you — otherwise the
served-HTML count plus `grep -c 'href="/stocks"'` in the nav region is acceptable for this slice:
at 1440 the nav shows exactly 관제 현황판 · AI 질문; at 390 the 메뉴 sheet shows the same two rows;
`/stocks` still renders when opened directly. `python3 scripts/workflow.py validate`. Leave the
dev stack running.

## Record

`result.md` (the diff, the before/after counts). `phase.md`: a one-line Findings note + a
**`frontend`** Doc impact line (nav is two slots — 관제 현황판 · AI 질문 — P7 operator override of
R2's three-slot nav; `NAV_LINKS` no longer carries `/stocks`; the label constant stays in use) and
note for the review the two P5 catalogue items that get more visible (#4 footer 내 종목 연결 line,
#12 hero H1 wording) — not this slice's to change. No `doc-new-version`, no commits, no state
transitions.
