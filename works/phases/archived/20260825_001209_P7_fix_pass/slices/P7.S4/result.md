# Result — P7.S4: 내 종목 조회 typeahead (candidate suggestions before submit)

**Status: done.** Operator item 2 is live on both search rows — the landing hero and R4's header
— in `next dev` on `127.0.0.1`, on the Tailscale origin and in an isolated production build, at
1440 and 390. The API grew one read-only route; the two rows became **one component**; **no Korean
copy was minted**; and typing + Enter without choosing still behaves exactly as it did yesterday,
with JavaScript on or off.

## The route contract

```
GET /stocks/suggest?q=<종목명|종목코드>            (read-only, anonymous, `q` is the only parameter)
→ 200 {"query": q, "candidates": [{"corp_code", "corp_name", "stock_code"}, …]}   ≤ 8, never 404
```

- **Declared before `GET /stocks/{corp_code}`** — proof it matters and that it worked:
  `curl /stocks/suggest` (no `q`) returns **422** (the suggest route matched and demanded its
  parameter), not the 404 the handle route would have raised for an unknown code `suggest`.
- Matching lives in `mijual.web.reads.suggest_corps(session, query, *, limit=8)`, beside
  `resolve_corp`, over the same one narrow `(corp_code, corp_name, stock_code)` scan of the ~614
  `Corp` rows:
  - all-digit query → `stock_code` **prefix**, plus the zero-padded exact (`12200` → `012200`),
    ordered by 종목코드;
  - otherwise → normalized name (`_name_key` / `present.bare_name`) **prefix first, substring
    after**, each group alphabetical by the normalized name.
  - The tiers are **unioned**, unlike `find_corps` (R6's agent tool), which stops at the first
    tier that matches. Nothing is filtered out of the corpus — an issuer with no events still
    belongs in the list, because it has an honest "권리가 없습니다" page to land on.
- **The invariant that makes this safe:** every tier `resolve_corp` can hit is a *prefix* hit
  here, so the row a bare submit would land on is at the top of the list, never buried by the cap.
- Live corpus spot-checks (`127.0.0.1:8000`): `계양` → 1 (계양전기 · 012200); `에스` → **8**
  (7 에스* prefix hits, then 나노씨엠에스 as the substring hit); `012` → 4 code-prefix hits in
  code order; `0122` → 계양전기 + 삼미금속; `없는종목` → `[]` with **200**.

## What changed, file by file

| file | what |
|---|---|
| `src/mijual/web/routers/stocks.py` | the new route (before `/stocks/{corp_code}`), and the docstring rewrites |
| `src/mijual/web/reads.py` | `suggest_corps` + `_corps_in_order`, `__all__`, `resolve_corp`'s docstring |
| `tests/test_web_stocks.py` | 12 name-only corps in the fixture + **one** test (6 assertions on the list, 2 that the resolver is unchanged) |
| `frontend/lib/types.ts` | `StockSuggestion` / `StockSuggestions` |
| `frontend/lib/api.ts` | `suggestStocks(q, init)` → `/api/stocks/suggest` (the same-origin rewrite) |
| `frontend/components/lookup/SearchRow.tsx` | **new** — the shared client search row + typeahead |
| `frontend/components/lookup/SearchRow.module.css` | **new** — the candidate panel, in the surrounding idiom |
| `frontend/components/landing/Hero.tsx` | renders `SearchRow` with the hero's own classes |
| `frontend/components/lookup/LookupHeader.tsx` | renders `SearchRow` with R4's own classes |
| `frontend/components/lookup/index.ts` | exports `SearchRow` |
| `frontend/components/landing/Hero.module.css` | **the one unplanned edit** — the ring clip moved from `.hero` to `.orbits` (see below) |

The two surfaces pass their **own** form/input/button classes in, so R2's 560px/52px hero row and
R4's 48px row are still each surface's own CSS; the component adds a positioning wrapper around
the input and the panel, nothing else.

## The docstring rewrites (the rule did not change — its scope was stated)

`stocks.py`'s module docstring and `resolve_corp`'s both said the miss "names … never a candidate
list, because no signed surface renders one and a guess that opened a different company's 놓친 돈
is the one defect class this product cannot ship." Both now say that the rule is about **the
system** picking silently, that it is untouched, and that a **reader's choice** travels as the
exact handle `/stocks/{corp_code}` and never back through `?q=`. The `?q=` miss payload still
names no reason and no near-miss; the "no holding count is ever received here" promise is intact
and the suggest route keeps it the short way — its only parameter is `q`.

## Two decisions worth not re-arguing

**1. The candidate panel is opaque, and it is still the field's own colour.** Both console fields
are translucent by design (`rgba(8,17,13,.72)` in the hero, `--surface-inset` = `rgba(255,255,255,.08)`
on /stocks) — right for a field lying *on* the page, wrong for a panel floating *over* it, where
the stat line underneath would read straight through. So the panel composites the same ink over
the page's own `--paper`: `background-color: var(--paper)` + `linear-gradient(<field colour>)`.
Measured, that is `rgb(10, 19, 16)` under `linear-gradient(rgba(8, 17, 13, 0.72) …)` — the field's
own rendered colour, made opaque. No new colour was invented.

**2. `.hero { overflow: hidden }` moved to `.orbits`, and this was necessary.** Measured before
the change at 1440: the eight-option panel spans y 440→761 while the hero ends at **732**, so its
last option was clipped and `document.elementFromPoint` there returned the Anchor 크래프트 panel
below. At 390 it would have cut the list roughly in half. `.orbits` is `position: absolute; inset: 0`
of the hero, so it is **the same rectangle** — measured identical afterwards (hero `[52, 732, 1440]`,
orbits `[52, 732, 1440]`) — and R2.1 §3's "never shrink the rings; the hero's own overflow clips
them" is unchanged. Evidence the clip still works: `document.documentElement.scrollWidth` equals
the viewport at **both** 1440 and 390 (the rings are 1251px wide), and the document height is
**3,047 px** at 1440 and **4,523 px** at 390 — byte-identical to `P7.S3`'s post-board measurements,
i.e. no geometry moved.

## Copy minted: **none**

Zero new Korean strings. A candidate renders its 회사명 (sans) and its 종목코드 (mono) and nothing
else; the list has no heading; an empty result renders **nothing** (the submit already owns R4's
locked 검색 불일치 sentence). The input reuses each surface's signed name as its label
(`HERO_TITLE_KO` / `STOCKS_LABEL_KO`) and R4's placeholder, both already in `copy.ts`.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **139 passed** (138 → 139; the phase note's "59" is a stale baseline — `HEAD` is 138) |
| `npm run typecheck` (frontend) | pass |
| `npm run smoke` (frontend) | **15/15** pass |
| API restart (`kill` + `make api-up`) + `curl 127.0.0.1:8000/stocks/suggest?q=계양` | 200, 계양전기 · 012200 |
| `npx next build` in an isolated copy + `next start -p 3100`, full typeahead pass, port freed | pass, 16 routes |
| `python3 scripts/workflow.py validate` | **Workflow validation passed** |
| `make stack-status` | postgres + api (pid 25177, restarted) + web (pid 13009) **left running** |

### Browser (headless Chrome over CDP, fresh profile, `P7.S1`'s method)

Every row below was measured on **both `/` and `/stocks`**, at **1440×900 and 390×844**, on
`http://127.0.0.1:3000` (`next dev`, StrictMode), and the whole pass was repeated once on
**`http://100.77.164.42:3000`** (Tailscale) and once against the **production build** on `:3100`.
All four runs agree.

| check | result |
|---|---|
| `/api/stocks/suggest` requests **on mount** | **0** (every run) |
| four characters typed 60 ms apart | **1** request (debounce, ~150 ms) |
| four characters typed 400 ms apart | **4** requests — one per keystroke, never two |
| clearing the box (4× Backspace) | **0** requests, list closed, `aria-expanded=false` |
| `계양` | 1 option — **계양전기 012200** |
| `에스` | **8** options: 7 에스* prefix hits, then 나노씨엠에스 (substring) |
| `0122` (digits) | 계양전기 012200 · 삼미금속 012210 |
| ↓ | `aria-activedescendant` set, `aria-selected` **true on exactly one**, nothing pre-selected before it |
| ↓ then Enter | URL = **`/stocks/01258020`** — the handle — and the stock page rendered (진행 중인 권리) |
| a real mouse press on a candidate | URL = **`/stocks/00102618`**, page rendered |
| `계양` + Enter **unchosen** | `/stocks?q=계양` → **307** → `/stocks/00102618` (today's path, unchanged) |
| `에스` + Enter **unchosen** (ambiguous prefix) | stays on `/stocks?q=에스` with **‘에스’와 일치하는 종목이 없습니다 — …** |
| Esc | closes; the typed text stays in the box |
| row geometry | hero **560 × 52** (48 at 390), R4 **560 × 48**, input↔button gap **0** — unchanged |
| panel vs the input | width **equal** (484/472 at 1440, 282/270 at 390), `dx = 0`, `dy = 0` |
| panel ink — hero | `rgb(10,19,16)` + `linear-gradient(rgba(8,17,13,.72))`, border `1px solid rgba(163,196,180,.4)`, `border-top: 0`, radius **0** |
| panel ink — /stocks | same base + `rgba(255,255,255,.08)` (`--surface-inset`), border `rgba(163,196,180,.32)` (`--border-strong`), radius **0** |
| motion | `candidates-in 0.12s` — a fade, `--dur-fast`; the global reduced-motion floor neutralises it |
| option height | **44px at 390**, 40px at 1440; every option hit-testable at both widths |
| horizontal overflow | none — `scrollWidth == viewport` at 390 and 1440 |
| console | **no** errors, warnings or React hydration complaints on `/`, `/stocks`, `/stocks?q=<miss>`, `/stocks/{code}` |
| responses ≥ 400 | only the pre-existing **`/favicon.ico` 404** on `/` (nobody's item, `P7.S2`/`S3` note it too) |
| **JavaScript disabled** (`Emulation.setScriptExecutionDisabled`) | both rows still render `<form action="/stocks" method="get">` + `input[name=q]` + 조회, and **no listbox** |

## Deviations from `plan.md`

1. **One extra file: `frontend/components/landing/Hero.module.css`.** The plan said not to change
   the hero's geometry; it does not — the ring clip moved from `.hero` to `.orbits`, the same
   rectangle, measured. Without it the hero's `overflow: hidden` clipped the candidate panel (see
   above). Geometry, padding, ring sizes and both document heights are unchanged.
2. **The plan's browser script used 삼성전자/삼성전기.** The live corpus is filing-derived and holds
   neither, so the equivalent live ambiguous prefix **`에스`** (7 prefix hits + 1 substring, and a
   `resolve_corp` miss on submit) was used instead. The 삼성 family exists in the *test* fixture,
   where the cap of 8 and the prefix ordering are asserted deterministically.
3. **The test count baseline** in the plan (59) is stale; the suite is 138 at `HEAD` and 139 now.
4. `suggest_corps` returns tiers **unioned**, so it could not reuse `find_corps` (first-tier-wins,
   limit 5, exact-ticker only). Both now cross-reference each other in their docstrings.

## For `P7.S5` (focus rings) and `P7.S9` (the sweep)

- The input is now wrapped in `span.SearchRow.field` (`position: relative; flex: 1 1 auto`). Focus
  styling was **not** touched — `:focus-visible` still lands on the `input` itself — but S5 should
  know the wrapper exists if it reaches for an inset ring or a parent selector.
- Selectors for a browser probe: `form[role="search"]`, `input[name="q"][role="combobox"]`,
  `[role="listbox"]`, `[role="option"]`. Type with `Input.insertText`; **an Enter dispatched
  without `text: "\r"` fires no keypress and therefore never submits the form** — that is a
  harness bug that looks exactly like "the form is broken" (it cost one wrong reading here).
