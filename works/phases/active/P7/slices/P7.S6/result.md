# Result — P7.S6: nav — drop the 내 종목 조회 slot

## What changed

`frontend/components/chrome/copy.ts` only. Removed the
`{ label: STOCKS_LABEL_KO, href: ROUTES.stocks }` entry from `NAV_LINKS` (now two entries:
관제 현황판 · AI 질문) and rewrote the doc comment above it so it states the current, true shape —
two slots, not three — and records *why*: P7 item 1 is an operator override of the signed
three-slot nav, not a relabelling, and the surface stays reachable elsewhere (landing hero search,
R3's detail link-out, the AI 질문 link row). The supersession history the comment already carried
(R2 → R4 → R6) is kept verbatim; only the framing sentence and the final paragraph changed.

```diff
-/** The three signed nav destinations, in R6's finalized order:
- * **내 종목 조회 · 관제 현황판 · AI 질문**.
+/** The nav's two remaining destinations, R6's finalized order minus the slot the
+ * operator withdrew in P7: **관제 현황판 · AI 질문**.
  *
- * R2 landed 내 종목 연결 · 관제 현황판 · 해설 and posed the labels back as
- * provisional. Both were then settled by later signed rounds and both are in the
- * supersession table: R4 named the surface **내 종목 조회** ("Naming
- * consequences: nav label 내 종목 연결 → 내 종목 조회"), and R6 "retires the
- * provisional 해설 nav label in favor of 「AI 질문」" — its build prompt puts
- * 「AI 질문」 in "nav 세번째 자리". Rendering R2's literals would be rendering a
- * superseded decision. */
+ * R2 landed 내 종목 연결 · 관제 현황판 · 해설 as a three-slot nav and posed the
+ * labels back as provisional. Both were then settled by later signed rounds and
+ * both are in the supersession table: R4 named the surface **내 종목 조회**
+ * ("Naming consequences: nav label 내 종목 연결 → 내 종목 조회"), and R6 "retires
+ * the provisional 해설 nav label in favor of 「AI 질문」" — its build prompt puts
+ * 「AI 질문」 in "nav 세번째 자리". P7 item 1 then removed the 내 종목 조회 slot
+ * itself (an operator override of the signed three-slot nav, not a relabelling):
+ * the surface stays reachable from the landing hero's own search, R3's detail
+ * link-out, and the AI 질문 link row — see `phase.md`'s P7 Item 1 note. */
 export const STOCKS_LABEL_KO = "내 종목 조회";
 export const BOARD_LABEL_KO = "관제 현황판";
 /** Also the footer's bottom-row link, where R2 landed the retired 해설. */
 export const ASK_LABEL_KO = "AI 질문";

 export const NAV_LINKS = [
-  { label: STOCKS_LABEL_KO, href: ROUTES.stocks },
   { label: BOARD_LABEL_KO, href: ROUTES.board },
   { label: ASK_LABEL_KO, href: ROUTES.ask },
 ] as const;
```

`STOCKS_LABEL_KO` was left in place, as the plan required: still imported by
`components/lookup/LookupHeader.tsx` (the `/stocks` page H1 and search label),
`components/ask/links.ts`, `components/ask/copy.ts` (re-export) and `components/lookup/copy.ts`
(re-export). Confirmed via `grep -rn STOCKS_LABEL_KO frontend/`. `ROUTES` stays imported and used
in `copy.ts` — `NAV_LINKS`'s remaining two entries still reference `ROUTES.board` /
`ROUTES.ask`, so nothing became an unused import. `Nav.tsx`, `Nav.module.css`, `Footer.tsx` and no
other file were touched.

## Verify

- Dev stack was already up (`make stack-status`): postgres healthy, `api` and `web` running,
  `http://127.0.0.1:3000`. Fast Refresh picked up the edit; stack left running afterward,
  unchanged from before.
- `cd frontend && npm run typecheck` — **pass** (`tsc --noEmit`, no errors).
- Served-HTML counts on `GET http://127.0.0.1:3000/` (root `/`, the landing page), before vs.
  after the edit:

  | | before | after |
  |---|---|---|
  | `내 종목 조회` occurrences (`grep -o … \| wc -l`) | 6 | **4** |
  | `href="/stocks"` occurrences (`grep -o … \| wc -l`) | 2 | **0** |

  The two occurrences removed are exactly the nav's desktop link and mobile-sheet row (confirmed
  by inspecting the matched context before the edit: `class="Nav-module__…__link" href="/stocks"`
  and `class="Nav-module__…__sheetRow" href="/stocks"`, both `>내 종목 조회<`). The 4 remaining
  `내 종목 조회` occurrences after the edit are all off-nav and unaffected: the hero `<h1>` (once),
  the hero search input's `aria-label` (once), and their two duplicates inside the RSC flight
  payload (`self.__next_f` inline script) — none inside a `Nav-module__` class.
  (Note: a plain `grep -c` undercounts on this file because Next.js serves the whole document as
  one line — `grep -c` counts *matching lines*, not occurrences — so the before/after table above
  uses `grep -o | wc -l` throughout.)
- Nav region check on the "after" HTML: the only `Nav-module__*` elements with an `href` are the
  brand mark (`href="/"`), the desktop link + mobile-sheet row for 관제 현황판
  (`aria-current="page" href="/"`, the board route is `/`), and the desktop link + mobile-sheet
  row for AI 질문 (`href="/ask"`). Both the desktop nav and the mobile sheet render exactly the
  same two-entry set (they map over the same `NAV_LINKS` array — same SSR HTML serves both
  widths, CSS handles the breakpoint), so this single served-HTML check covers "at 1440 the nav
  shows 관제 현황판 · AI 질문" and "at 390 the 메뉴 시트 shows the same two rows" together — no
  extra CDP probe was needed for that part.
  This satisfies the plan's fallback ("the served-HTML count plus `grep -c 'href="/stocks"'` in
  the nav region is acceptable for this slice"); no headless-Chrome/CDP session was spun up (the
  scripted recipe from `P7.S1`–`S4` lived only in prior sessions' scratch space and was not
  committed, so there was nothing to reuse, and the served-HTML evidence above is unambiguous for
  a one-entry-removal fix).
- `GET http://127.0.0.1:3000/stocks` — **200**, `<h1 class="Lookup-module__…__title">내 종목
  조회</h1>` still renders: the surface itself is untouched and still reachable by direct URL.
- `python3 scripts/workflow.py validate` — **`Workflow validation passed.`**

## Deviations from plan.md

None. Exactly the one entry + its doc comment changed in `frontend/components/chrome/copy.ts`;
`Nav.tsx`, `Nav.module.css`, the footer and every label were left alone. No unused-import cleanup
was needed (`ROUTES` and `STOCKS_LABEL_KO` both stayed in use). No CDP/headless-Chrome check was
run — the served-HTML evidence was unambiguous and the plan explicitly allows the served-HTML
route as an acceptable substitute for this slice.

## Doc impact

See `phase.md`'s "Doc impact" list — one `frontend` line appended by this slice per the plan
(nav is now two slots; `NAV_LINKS` no longer carries `/stocks`; `STOCKS_LABEL_KO` stays in use
elsewhere). No `doc-new-version` run (fix slice; the review consolidates on a pass).
