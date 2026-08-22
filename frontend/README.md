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
  layout.tsx        the cosmos page root: <html lang="ko" class="cosmos">, the foundations
  shell.css         content column, type floor, focus ring, reduced-motion convention
  page.tsx          the foundation proof page — P5.S12 (landing) replaces it
components/         the R1/R2 trust primitives; every surface composes these
lib/
  api.ts            the one API client — hard-coded routes, CSRF, credentials, envelope
  types.ts          the presentation contract, typed
  copy.ts           every Korean string a primitive renders, each with its source
  motion.ts         useReducedMotion() — the JS half of the reduced-motion floor
public/
  foundations/      tokens.css + fonts.css, VENDORED VERBATIM from the landed record
  assets/           the brand binaries, exported from the design project — see assets/README.md
```

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

Page surfaces (`P5.S11`–`P5.S17`), the starfield/glow/shooting-star layers (`P5.S12`), R7's
ornament-free ops panel (`P5.S17`), and the AI 질문 agent in every form (P6). The shell
guarantees a full-page fixed backdrop is possible (`.backdrop` in `shell.css`) and keeps the
bottom-right corner free for P6's launcher.

## Rules that are not negotiable at the visual layer

- An estimate never renders untagged and a fact never carries the mark — `EstimateMarker`
  takes a required `estimated`, mirroring `mijual.present.Figure`.
- A gate-blocked field is **absent**, never a placeholder, a dash or a "확인 필요".
- 추후결정 means *no date* — never a date beside the badge.
- D-days and dates are computed upstream in KST; the browser only diffs.
- A past ② is 진행 중, never 종료; a past D+n renders **faint**, never in alert ink.
- Korean-only product surface, and **inventing a Korean string is a design change**. Copy comes
  from `docs/reference/design/grounding/copy-inventory.md` via `lib/copy.ts`.
