# Plan — P7.S4: 내 종목 조회 typeahead — candidate suggestions before submit (API route + search UI)

## Why

Operator item 2: "내 종목 조회 search shows a list of related ones when a user types the text on
the input, before the submit." Today both search rows — the landing hero
(`frontend/components/landing/Hero.tsx`, a plain GET form to `/stocks?q=`) and the R4 surface
(`frontend/components/lookup/LookupHeader.tsx`, the same form) — show nothing until submit, and
the API has **no suggestion endpoint**: `GET /stocks?q=` (`src/mijual/web/routers/stocks.py`)
resolves exactly one issuer through `mijual.web.reads.resolve_corp`'s four unique-or-decline
tiers or returns `{found: false}`, and both docstrings state the product rule this item
overrides: *"never a candidate list … a guess that opened a different company's 놓친 돈 is the one
defect class this product cannot ship."*

Read first: `phase.md` → "Item 2", **Design-collision reading #4** (it is the contract for this
slice), Constraints, and the `P7.S1`/`S2`/`S3` findings (StrictMode: no module-level effect state;
CDP approach; isolated prod build). Then R4's record
(`docs/reference/design/rounds/04-lookup/output/build-prompt.md` §Search row + `result.md`) and
R2/R2.1's hero search row (`rounds/02-landing-chrome/output/build-prompt.md`), and
`docs/current/api.md` §/stocks.

## The reading this slice implements (from collision reading #4 — do not re-argue it)

The "never a candidate list" rule exists so that *the system* never silently opens the wrong
company. A reader **choosing** from a list is the opposite of a silent guess. So:

- every suggestion carries its **종목코드** (and name) and, when chosen, navigates by the exact
  handle **`/stocks/{corp_code}`** (`stockPath(corp_code)` in `lib/routes.ts`) — never by
  re-running a fuzzy resolve;
- typing and submitting **without choosing** keeps today's behaviour exactly: the plain GET form
  to `/stocks?q=` → `resolve_corp` → hit redirects to the handle, a miss renders R4's locked 검색
  불일치 sentence (ambiguous prefix included). The form must keep working with JavaScript off.

## Backend (FastAPI, `src/mijual/web/`)

1. New read-only route **`GET /stocks/suggest?q=<text>`** in `routers/stocks.py` →
   `{"query": q, "candidates": [{"corp_code", "corp_name", "stock_code"}, …]}`, at most **8**,
   empty list for no match (200, never 404). Matching over the ~614 `Corp` rows (cheap — the
   same narrow `(corp_code, corp_name, stock_code)` scan `resolve_corp` does): all-digit query →
   `stock_code` prefix; otherwise normalized-name (`_name_key` / `mijual.present.bare_name`)
   **prefix first, then substring**, stable order (prefix hits, then substring hits; name
   alphabetical within each), excluding nothing the corpus has. `min_length=1`. Put the reading
   function in `reads.py` beside `resolve_corp` (e.g. `suggest_corps(session, query, limit=8)`).
   **Declare it before `GET /stocks/{corp_code}`** (FastAPI matches routes in order —
   `/stocks/suggest` would otherwise be captured as a `corp_code` and 404).
2. Rewrite the "never a candidate list" sentences in the `stocks.py` module docstring and the
   `resolve_corp` docstring to the new reading (a chosen candidate navigates by `corp_code`; the
   resolver still never guesses on submit). Keep the "no holding count is ever received here"
   promise untouched — the suggest route takes only `q`.
3. Tests stay terse: add the minimal cases (digits prefix, name prefix, substring, empty,
   cap of 8, order) to the existing web/reads test file if one covers `resolve_corp`/the stocks
   router (`grep -rln "resolve_corp\|/stocks" tests/`), else one small new `tests/test_web_stocks_suggest.py`
   using the same fixtures style. `.venv/bin/python -m pytest` must stay green (59 → +N).
   **The API must be restarted** for the new route to serve (`make stack-down`'s api part or kill
   the api pid and `make api-up`; leave it running; verify `curl 127.0.0.1:8000/stocks/suggest?q=계양`).

## Frontend (`frontend/`)

4. `lib/api.ts`: a `suggestStocks(q, signal)` helper hitting **`/api/stocks/suggest`** (same-origin
   rewrite, like every other call) + the `types.ts` shape.
5. One client component (e.g. `components/lookup/SearchRow.tsx` or a `Typeahead` wrapping the
   input) used by **both** search rows — the hero and `LookupHeader` — so the two stay one
   behaviour. Progressive enhancement: it renders the same `<form method="get" action="/stocks">`
   + `<input name="q">` + 조회 button, and adds: debounce ~150 ms, `AbortController` on every
   keystroke, no request for an empty/whitespace query, a listbox under the input
   (WAI-ARIA combobox pattern: `role="combobox"`, `aria-expanded`, `aria-controls`,
   `aria-activedescendant`; options `role="option"`), ↑/↓ to move, **Enter on a highlighted option
   → `router.push(stockPath(corp_code))`**, Enter with nothing highlighted → native submit
   (unchanged), Esc/blur closes. Each option renders **name (sans) + 종목코드 (mono)**. No request
   on mount (StrictMode-safe: all state in the component, cleanup aborts). Result list never
   "auto-selects" — the first option is not pre-highlighted (the reader chooses).
6. **Styling, in the surrounding signed idiom and nothing new**: the hero's listbox in R2 §Cosmos's
   dark console field colours (`rgba(8,17,13,.72)` bg, hairline `rgba(163,196,180,.4)`, white ink,
   radius 0), the /stocks one in R4's console-field colours (`Lookup.module.css` `.input`);
   absolute-positioned under the input, full input width, fade-only motion (or none),
   `prefers-reduced-motion` respected, 44px option height on mobile / 40px desktop, hover/active
   option = `--surface-inset`-style tint. Reuse tokens; invent no new colour. **Mint no Korean copy**
   if possible — the list needs no heading; if an empty-result state is wanted, render nothing
   (the miss sentence already exists on submit). Any string you cannot avoid goes in Doc impact +
   `result.md` for the review's operator questions.
7. Do **not** touch focus-ring styling (S5 owns it) or the nav (S6); do not change the hero's
   geometry (560px row, 48/52px heights) or the R4 header's.

## Verify — operator runtime first

Dev stack up (`make stack-status`; restart the **api** for the new route; Fast Refresh handles the
frontend). Headless Chrome over CDP on **`http://127.0.0.1:3000`** (once on the Tailscale URL),
fresh profile, 1440 and 390, **on both `/` and `/stocks`**:
- type `계양` → a listbox appears with 계양전기 + its 종목코드 within ~300 ms; `삼성전` → both 삼성전자
  and 삼성전기 listed; `0000` (digits) → code-prefix hits; clear the input → list gone; no request
  for empty input (count network calls);
- ↓ + Enter on 계양전기 → URL is `/stocks/{corp_code}` (the handle), page renders the stock;
- type `계양` + Enter with nothing highlighted → `/stocks?q=계양` → redirects to the handle (today's
  path); type `삼성전` + Enter unchosen → stays on `/stocks` with the 검색 불일치 sentence (today's
  path, unchanged);
- StrictMode: exactly one `/api/stocks/suggest` request per debounced keystroke, none on mount;
- Esc closes; clicking an option works on 390 (44px targets); no layout shift of the row;
- measure the listbox's computed bg/border/radius against the idiom named above;
- `npm run typecheck && npm run smoke`; `.venv/bin/python -m pytest`; production build in an
  isolated copy (`P7.S2` method) + `next start -p 3100`, one typeahead pass on `127.0.0.1:3100`,
  kill it; `python3 scripts/workflow.py validate`. Leave the dev stack (postgres + api + web) running.

## Record

`result.md` (commands/outcomes, the route contract, measurements, copy minted if any, deviations).
`phase.md`: Findings note + Doc impact lines: **`api`** (new `GET /stocks/suggest`, and the
/stocks rule sentence now reads "no silent guess on submit; suggestions are a reader's choice by
corp_code"), **`frontend`** (the shared search row + typeahead on both surfaces), and `product` /
`experience` if they state the no-candidate promise. No `doc-new-version`, no commits, no state
transitions.
