# frontend — 미주알's Next.js app

Built from the **signed** P3 design record. Read `docs/current/frontend.md` (the
supersession table) *before* any `docs/reference/design/rounds/*/output/build-prompt.md`,
then `SIGNOFF.md`, then the round. **RESPECT THE DESIGN**: nothing approved is dropped,
simplified, restyled or "improved". A nit found here is an apply-time to-do, never an edit
to the landed record.

## Run it

```bash
cd frontend && npm install
npm run dev          # http://127.0.0.1:3000
```

The API must be up separately (`.venv/bin/uvicorn mijual.web.app:app --reload`, port 8000);
`compose.yaml`'s header documents both. `curl -s localhost:3000/api/health` proves the proxy.

| script | what it does |
|---|---|
| `npm run dev` / `build` / `start` | Next.js |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run smoke` | `node --test lib/*.test.ts` — the API wrapper's three cases, no framework |

The other half of the smoke check is `npm run build` itself: it prerenders `app/page.tsx`
through the shell and every primitive, so a broken component fails the build.

## Stack

Next.js **16.3.2** (App Router, Turbopack) · React **19.2.8** · TypeScript **5.9.3**, and
nothing else. **No UI library and no CSS framework**: the design system is `tokens.css`, and
a framework theme would be a second source of truth for decisions R1 already made. Styling is
plain CSS Modules over the tokens.

## Layout

```
app/
  layout.tsx        the cosmos page root: <html lang="ko" class="cosmos"> + the global chrome
  shell.css         content column, type floor, focus ring, reduced-motion convention
  page.tsx          the foundation proof page — P5.S12 (landing) replaces it
  stocks/page.tsx   내 종목 조회 — a bare shell; P5.S14 builds the surface
  ask/page.tsx      AI 질문 — a bare shell; the surface is P6's, by the phase split
components/         the R1/R2 trust primitives; every surface composes these
  chrome/           the global chrome (R2): nav, mobile sheet, footer, vocky triggers
lib/
  api.ts            the one API client — hard-coded routes, CSRF, credentials, envelope
  types.ts          the presentation contract, typed
  copy.ts           every Korean string a primitive renders, each with its source
  routes.ts         the route map — one place a path is stated
  motion.ts         useReducedMotion() — the JS half of the reduced-motion floor
public/
  foundations/      tokens.css + fonts.css, VENDORED VERBATIM from the landed record
  assets/           the brand binaries, exported from the design project — see assets/README.md
```

### Routes and the chrome

| route | surface | who builds it |
|---|---|---|
| `/` | 관제 현황판 (the landing) | `P5.S12` — `app/page.tsx` is still the foundation proof |
| `/stocks` | 내 종목 조회 | `P5.S14` |
| `/ask` | AI 질문 | **P6** — P5 ships the signed nav slot and an empty page, never a fake chat |
| `/auth/login` | 로그인 / 계정 만들기 | `P5.S15` — **no page yet**; the nav's 로그인 slot points here |
| `/ops` | 운영 관제 | `P5.S17` — linked from nowhere in the reader chrome, by design |

`components/chrome/` wraps every route from the root layout: the 52px nav with the three
signed slots, the mobile top bar + sheet, and the footer. Its two seams are named in the
files — `AccountSlot.tsx` (the 로그인 slot `P5.S16` swaps for the account menu) and
`VockyScript.tsx` (the script URL).

### Environment

| variable | what it does |
|---|---|
| `MIJUAL_API_ORIGIN` | where `next.config.ts` proxies `/api/*` (default `http://localhost:8000`) |
| `NEXT_PUBLIC_API_BASE_URL` | overrides the client's base; normally unset, so calls stay same-origin |
| `NEXT_PUBLIC_VOCKY_SRC` | vocky's script URL. **Unset → no script tag**, and the three `data-vocky-trigger` elements still render. It is read at **build** time (`NEXT_PUBLIC_*` is inlined), so setting it means rebuilding. The real value is `P5.S18`/P4's. |

### The foundations are vendored, not authored

`public/foundations/tokens.css` is `rounds/02-landing-chrome/output/tokens.css` (R1's 66-property
light `:root` plus R2.1's `.cosmos` scope) and `public/foundations/fonts.css` is
`rounds/01-brand-foundations/output/fonts.css`, both byte-identical to the record with a
provenance header added. **Do not edit them, reformat them or rename a token**: a change there
is a design change. They are served as static files rather than bundled so `fonts.css`'s
`../assets/fonts/…` resolves exactly as written — this directory layout mirrors the design
project's own `foundations/` + `assets/`.

One apply-time to-do lives in `layout.tsx`: the landed `fonts.css` puts its
`@import url(…IBM+Plex+Mono…)` after the `@font-face` block, where CSS drops it, so the same
URL is linked from the layout instead. The record stays untouched.

### What is deliberately *not* here

Page surfaces (`P5.S12`–`P5.S17`), the starfield/glow/shooting-star layers (`P5.S12`), R7's
ornament-free ops panel (`P5.S17`), and the AI 질문 agent in every form (P6). The shell
guarantees a full-page fixed backdrop is possible (`.backdrop` in `shell.css`) and keeps the
bottom-right corner free for P6's launcher — the chrome positions nothing `fixed` and adds no
floating button (R2 §6-4).

## Rules that are not negotiable at the visual layer

- An estimate never renders untagged and a fact never carries the mark — `EstimateMarker`
  takes a required `estimated`, mirroring `mijual.present.Figure`.
- A gate-blocked field is **absent**, never a placeholder, a dash or a "확인 필요".
- 추후결정 means *no date* — never a date beside the badge.
- D-days and dates are computed upstream in KST; the browser only diffs.
- A past ② is 진행 중, never 종료; a past D+n renders **faint**, never in alert ink.
- Korean-only product surface, and **inventing a Korean string is a design change**. Copy comes
  from `docs/reference/design/grounding/copy-inventory.md` via `lib/copy.ts`.
