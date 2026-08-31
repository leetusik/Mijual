# frontend — the 주주의관제탑 Next.js app

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

The other half of the smoke check is `npm run build` itself: it compiles and type-checks every
route and prerenders the static ones, so a broken component fails the build. The landing is
**request-time** (`connection()` in `app/page.tsx`), so it is built without an API and rendered
per request — a board that was a build-time snapshot would be a stale board.

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
  page.tsx          관제 현황판 — the landing (R2/R2.1), live from /board/summary + /board
  stocks/page.tsx   내 종목 조회 — a bare shell; P5.S14 builds the surface
  ask/page.tsx      AI 질문 — a bare shell; the surface is P6's, by the phase split
components/         the R1/R2 trust primitives; every surface composes these
  chrome/           the global chrome (R2): nav, mobile sheet, footer, vocky triggers
  landing/          the landing surface (R2/R2.1 + R3's 추후결정 strip) — cosmos, hero,
                    anchor cards, countdown, 소멸주의보, board
lib/
  api.ts            the one API client — hard-coded routes, CSRF, credentials, envelope
  types.ts          the presentation contract, typed
  copy.ts           every Korean string a primitive renders, each with its source
  format.ts         won / count / percent / kstStamp — exact decimal strings, never a float
  routes.ts         the route map — one place a path is stated
  motion.ts         useReducedMotion() — the JS half of the reduced-motion floor
app/
  fonts.ts          the two self-hosted faces (next/font/local)
  fonts/            NotoSansKR + IBMPlexMono woff2 subsets, and their OFL files
  icon.png icon1.png apple-icon.png    the favicon tiles, 32 / 16 / 180 (R17 §2; transparent,
                    #2b8e6c ink at 75% width since R18/P10.review — assets/README.md)
scripts/            dev-only: re-subset the two faces, re-extract the Korean charset
public/
  foundations/      tokens.css, VENDORED VERBATIM from the landed record
  assets/           the brand binaries — see assets/README.md for the provenance classes
```

### Routes and the chrome

| route | surface | who builds it |
|---|---|---|
| `/` | 관제 현황판 (the landing) | `P5.S12` — built; rows link to `/events/{rcept_no}` (`P5.S13`) |
| `/stocks` | 내 종목 조회 | `P5.S14` |
| `/ask` | AI 질문 | **P6** — P5 ships the signed nav slot and an empty page, never a fake chat |
| `/auth/login` | 로그인 / 계정 만들기 | `P5.S15` — **no page yet**; the nav's 로그인 slot points here |
| `/ops` | 운영 관제 | `P5.S17` — linked from nowhere in the reader chrome, by design |

`components/chrome/` wraps every route from the root layout: the 52px nav with **R8's two
signed destinations** (AI 질문 · 보유 종목 — the ring wordmark is 관제 현황판's own
destination), the mobile top bar + overlay sheet, the footer, and the 의견 보내기 surface
(`Feedback.tsx`, which posts to this app's own `/api/feedback`). Its one seam is named in the
file — `AccountSlot.tsx` (the 로그인 slot `P5.S16` swaps for the account menu, re-cut by R8 as
the full email + `Identicon` + frame).

### Environment

| variable | what it does |
|---|---|
| `MIJUAL_API_ORIGIN` | where `next.config.ts` proxies `/api/*` (default `http://localhost:8000`) |
| `NEXT_PUBLIC_API_BASE_URL` | overrides the client's base; normally unset, so calls stay same-origin |

**`NEXT_PUBLIC_VOCKY_SRC` is retired** (R8 / `P8.S3`): vocky ships no embeddable widget, so
주주의관제탑 owns the 의견 screen and the browser posts to `/api/feedback` on this origin. The
credential stays server-side in `MIJUAL_VOCKY_API_BASE` / `MIJUAL_VOCKY_API_KEY` — **no vocky
value is ever inlined into this bundle**.

### The token sheet is vendored, not authored

`public/foundations/tokens.css` is `rounds/02-landing-chrome/output/tokens.css` (R1's 66-property
light `:root` plus R2.1's `.cosmos` scope), byte-identical to the record with a provenance header
added. **Do not edit it, reformat it or rename a token**: a change there is a design change. It is
served as a static file rather than bundled so nothing can rewrite it on the way through.

### The two faces are self-hosted subsets

`public/foundations/fonts.css` is **gone** (`P10.S7`). It was the other vendored foundation, and it
`@font-face`d a 2,057,688-byte un-subset Pretendard Variable while `@import`ing IBM Plex Mono from
the Google Fonts CDN. Both are replaced, at the operator's instruction, by the pipeline
`~/projects/personal/changple_web` uses: **Noto Sans KR** and **IBM Plex Mono** as `next/font/local`
subsets in `app/fonts/`, declared in `app/fonts.ts` and generated by `scripts/subset_noto_sans_kr.sh`
+ `scripts/subset_plex_mono.sh`. **330,480 bytes total and no third-party origin**, against
2,057,688 bytes plus a cross-origin stylesheet before. The retired files and their hashes are
recorded in `public/assets/README.md`.

Two things about that pipeline are load-bearing and are explained where they live:

- **the charset is auto-extracted** (`scripts/gen-korean-charset.mjs`), because a hand-maintained
  one goes stale and renders missing syllables **자모 분리**;
- **the subset omits the conjoining-jamo block U+1100–11FF** on purpose, so a syllable it does not
  carry falls back to the system face *composed* rather than decomposed. Which matters here more
  than it did upstream: this product renders **dynamic DART company names** everywhere, so the
  Korean subset deliberately covers far more than the glyphs the source happens to contain.
  `scripts/subset_noto_sans_kr.sh`'s header carries the measured payloads behind that choice.

`tokens.css` still names Pretendard and CDN Plex Mono in `--font-sans` / `--font-mono`, and it stays
that way — it is frozen. `app/shell.css` overrides those two variables in **application** code
instead, at `html:root` specificity, because `tokens.css` is linked after the bundled CSS and would
otherwise win the tie.

### What is deliberately *not* here

The remaining page surfaces (`P5.S13`–`P5.S17`), R7's ornament-free ops panel (`P5.S17`), and
the AI 질문 agent in every form (P6). The landing fills the `.backdrop` slot `shell.css`
reserves and, like the chrome, positions **nothing else** `fixed` and adds no floating button
(R2 §6-4) — the bottom-right corner stays free for P6's launcher.

## Rules that are not negotiable at the visual layer

- An estimate never renders untagged and a fact never carries the mark — `EstimateMarker`
  takes a required `estimated`, mirroring `mijual.present.Figure`.
- A gate-blocked field is **absent**, never a placeholder, a dash or a "확인 필요".
- 추후결정 means *no date* — never a date beside the badge.
- D-days and dates are computed upstream in KST; the browser only diffs.
- A past ② is 진행 중, never 종료; a past D+n renders **faint**, never in alert ink.
- Korean-only product surface, and **inventing a Korean string is a design change**. Copy comes
  from `docs/reference/design/grounding/copy-inventory.md` via `lib/copy.ts`.
