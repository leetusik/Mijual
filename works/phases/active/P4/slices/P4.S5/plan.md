# P4.S5 — SEO: metadata, robots, sitemap, canonicals, OG, JSON-LD

Orchestrator plan, written 2026-09-02 after `P4.S4` put the product live at `https://jujutower.com`
(`af8b57c`). This slice was promoted from **D5** ("Favicon + per-route `<title>`/meta for the reader
chrome"): the favicon half shipped in P10 (`app/icon*.png`, 16/32/180); the title/meta half — and
everything a public site needs to be found — **is this slice**. It writes frontend code only; the
production redeploy that puts it on the box belongs to `P4.S6` (see *Handoff*).

Read first: `works/phases/active/P4/phase.md` whole (especially **(from P4.DECOMP, for P4.S5)** and
**(from P4.S4, for P4.S5)** — the measured current state and what the live origin inherits, and the
`## Operator Questions` entry on Korean copy approval), `frontend/app/layout.tsx`,
`frontend/lib/routes.ts`, `frontend/components/ops/routes.ts` (read, never import from a reader
module), `frontend/lib/api.ts` (`request`, `getBoard`, `getEvent`, `getStock`, `getSiteContact`),
`frontend/lib/types.ts` (`BoardRow`, `EventView`, `StockPage`, `Countdown`), the two dynamic pages
`app/stocks/[corp_code]/page.tsx` + `app/events/[rcept_no]/page.tsx`, `frontend/lib/copy.ts` +
`components/landing/copy.ts` + `components/chrome/copy.ts` (the signed Korean strings you may
derive from), `frontend/public/assets/README.md` (asset provenance rules — binding), `frontend/Dockerfile`,
`compose.prod.yml` (the `mijual-web` build args), `frontend/AGENTS.md` (this Next is 16.3.2 — read the
metadata / `generateMetadata` / file-convention docs under `node_modules/next/dist/docs/` before
writing any of it), and the reference implementation this mirrors file for file:
`~/projects/personal/hi2vi_web/src/app/{robots,sitemap,manifest}.ts`, its `layout.tsx` metadata
block, `components/seo/json-ld.tsx`, `content/site.ts` — read-only, another repo.

## What "done" means

`https://jujutower.com` (apex-only — `www` 301s to it) is describable and indexable exactly where it
should be: every indexable page has a real `<title>`, a description, a canonical, Open Graph and
Twitter cards and an OG image; `robots.txt`, `sitemap.xml` and a web manifest exist at the origin;
JSON-LD names the site; `/ops`, `/auth/*` and `/portfolio*` are `noindex`; the site URL is
build-baked from an asserted build arg; **every new Korean string is listed for literal operator
approval at the gate**; all of it is verified on a **production build** on this Mac; and the notebook
tells `P4.S6` exactly how to ship and re-check it live.

## Hard constraints

1. **Copy discipline.** The signed design writes no document-level copy, so every meta string is a
   **draft this phase proposes and the operator approves literally at the gate** (P4.DECOMP's
   ruling, already on `## Operator Questions`). Derive from signed strings where one exists
   (`HERO_SUB_KO` 「종목명 하나로 놓친 권리와 진행 중인 권리를 조회합니다」, `RIGHTS_LABEL_KO`,
   `STOCKS_LABEL_KO` 「내 종목 조회」, `BOARD_LABEL_KO`, `ASK_LABEL_KO`, `BRAND_ALT_KO`, the countdown's
   own `label_ko` / `dday`), and from `docs/current/product.md` `## Summary` for the one sentence
   nothing signed covers. Korean-only, unspaced 주주의관제탑, never 미주알. **No won amount in any
   meta string, ever** — descriptions carry names, labels and dates, never a figure (확정발행가 전 금액
   금지 applies to what a crawler quotes just as it does to mail). **Every string lives in ONE typed
   module** (`frontend/lib/seo.ts`), never inline, with a one-line provenance comment per string
   (transcribed-from / drafted-by-P4.S5), exactly as `src/mijual/mailcopy.py` does.
2. **Rewrite, do not delete, the root layout's comment** that says "No tagline, no description: the
   signed design writes no document-level copy, and inventing a Korean sentence would be a design
   change" — the ruling now is that the phase drafts and the gate approves; say so there and point
   at `lib/seo.ts`.
3. **No third-party origin, still.** `security.md` carries the measured property that no page
   contacts one. JSON-LD is inline; the OG image is self-hosted; no analytics, no external
   verification scripts. Grep the built HTML for `https?://` hosts other than `jujutower.com` and
   `dart.fss.or.kr` and report the result.
4. **`/ops` never enters a reader module.** `components/ops/routes.ts` stays imported by nothing
   under `components/chrome`, `components/landing`, `lib/`. `app/robots.ts` and the noindex on
   `app/ops/layout.tsx` are the two places that may name `/ops`; if `robots.ts` imports
   `OPS_ROOT`, say why that is not a reader module; a literal with a comment is also fine.
5. **Asset provenance rules bind.** Any new image (the OG image, 192/512 manifest icons) is a
   **class-C derivative produced by ONE recorded ImageMagick command** from an existing class-B/C
   asset, documented in `public/assets/README.md` in that file's own style (command, source,
   dimensions, signature line), never hand-drawn, never trimmed if the symbol (the README forbids
   `-trim` on it), never invented. The OG image is a design-adjacent artifact: produce it, view it
   yourself (the Read tool renders PNGs), and put it on the gate list for the operator to accept or
   reject — if rejected the phase removes it, so keep it one command and one file.
6. **The site URL is build-baked and asserted.** `NEXT_PUBLIC_SITE_URL`: `frontend/Dockerfile` gets an
   `ARG`/`ENV` pair asserted non-empty exactly as `MIJUAL_API_ORIGIN` is; `compose.prod.yml`'s
   `mijual-web` `build.args` gets `NEXT_PUBLIC_SITE_URL: "https://jujutower.com"`. In code, a
   production build with it unset must **fail** (throw at module load in `lib/seo.ts` when
   `process.env.NODE_ENV === "production"`); a non-production build/dev server falls back to
   `http://127.0.0.1:3010` so the operator's `next dev` keeps working untouched. Never the
   `?? "https://…"` trap.
7. **Do not touch the operator's runtime.** `frontend/.next` belongs to the running `next dev`
   (Fast Refresh picks your edits up); build the production check on an **APFS clone** of
   `frontend/` exactly as `P4.S1` did (its recipe is in
   `works/phases/active/P4/slices/P4.S1/result.md`), never in place. Do not restart `make stack-*`.
   Do not run `compose.prod.yml` locally. Do not push, do not commit, do not deploy — the box is
   `P4.S6`'s.
8. **Tests:** none new. This is surface; it is verified live (below). `npm run typecheck` and
   `npm run smoke` must stay green; `.venv/bin/python -m pytest` is untouched by this slice.

## Deliverables (mirror hi2vi file for file, adapted)

1. **`frontend/lib/seo.ts`** — the one typed source: `SITE_URL` (constraint 6), `SITE_NAME`
   (`주주의관제탑`), `SITE_DESCRIPTION_KO` (drafted), `TITLE_TEMPLATE` (`%s | 주주의관제탑`, default
   `주주의관제탑`), per-route title/description builders for the two dynamic routes, the OG/Twitter
   field set, `theme_color` / `background_color` from `public/foundations/tokens.css` (dark paper
   `#0a1310`, light `#f2f3f2` — pick and say which the manifest uses), and the verification tokens
   (`NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION`, `NEXT_PUBLIC_NAVER_SITE_VERIFICATION`) **conditionally
   spread** so an empty value renders no tag. Search Console is a DNS-TXT domain property through
   Cloudflare (nothing in HTML); Naver Search Advisor needs an HTML tag → an Operator Question
   (register or not; a token means one rebuild), not a default.
2. **`app/layout.tsx` metadata**: `metadataBase: new URL(SITE_URL)`, `title: { default, template }`,
   `description`, `applicationName`, `openGraph` (type website, locale `ko_KR`, siteName, title,
   description, url `/`), `twitter` (`summary_large_image`), `verification` (conditional),
   `robots` default index/follow. **Trap: do NOT put `alternates.canonical: "/"` in the root
   layout** — `alternates` is inherited as a whole, so every route without its own would claim the
   home as canonical. Canonicals are set **per indexable route** (item 5).
3. **`app/robots.ts`**: allow `/`; disallow `/api/`, `/ops`, `/auth/`, `/portfolio`; `sitemap:
   ${SITE_URL}/sitemap.xml`. Cloudflare **prepends** its managed content-signals block to the served
   file (measured by S4: 1836 bytes, `Disallow: /` for `GPTBot`/`Google-Extended`/
   `meta-externalagent`) — do not duplicate those signals at the origin.
4. **`app/sitemap.ts`**: `export const dynamic = "force-dynamic"`, `revalidate = 0`; static half from
   `ROUTES` (`/`, `/stocks`, `/ask` — never `/auth/*`, `/portfolio*`, never `/ops`); dynamic half
   from one `getBoard()` call inside `try/catch` (an API outage degrades to the static list, never a
   500): every row with `state === "exposable"` and a non-null `rcept_no` → `eventPath(rcept_no)`,
   every distinct `corp_code` → `stockPath(corp_code)`; `lastModified` from the board's `reference`
   or the row's date if one is honest — say which; absolute URLs on the apex only. Report the URL
   count from the production build. `/stocks` has no nav link (crawler-orphaned) — the sitemap is
   what reaches it; do not add navigation (a design change).
5. **Per-route metadata and canonicals**: `/` (title default, canonical `/`), `/stocks` (title from
   `STOCKS_LABEL_KO`, canonical `/stocks`), `/ask` (title from `ASK_LABEL_KO`, canonical `/ask`);
   **`generateMetadata`** in `app/stocks/[corp_code]/page.tsx` and `app/events/[rcept_no]/page.tsx`
   — title and description from the fetched `StockPage` / `EventView` (corp_name, the signed
   `RIGHTS_LABEL_KO[rights_type]`, `countdown.label_ko`, `countdown.dday`, `countdown.date`; a
   withdrawn event says so with its own signed `notice_ko` shape, never invents), canonical to the
   route itself, OG title/description matching. **Trap: the double fetch** — `generateMetadata` and
   the page both call `getEvent`/`getStock`; Next memoizes identical server `fetch` calls within
   one render, but **measure it** (one vs two `GET /events/…` lines in the operator's dev API log,
   `var/stack/api.log`) and wrap the getter in React `cache()` if it is two. On a 404 the metadata
   function must not throw a 500: return the default title (or call `notFound()` — read the 16.3
   docs and say which).
6. **`noindex`**: `robots: { index: false, follow: false }` on `app/ops/layout.tsx` (already the
   ops title holder), `app/auth/login/page.tsx`, `app/auth/reset/page.tsx`, `app/portfolio/page.tsx`,
   `app/portfolio/notifications/page.tsx` — all server components, so page-level `metadata` exports
   work; give them titles too (`로그인`, `비밀번호 재설정`, `내 포트폴리오`, `알림 설정` — the signed
   chrome labels), listed for approval like every other string.
7. **`app/manifest.ts`**: name/short_name `주주의관제탑`, description, `start_url: "/"`, `display:
   standalone`, `lang: ko`, theme/background colours, icons: the existing `app/icon*.png` sizes
   plus 192/512 **only** as recorded derivatives per constraint 5 (from the class-C symbol tile
   the favicon tiles came from, same ink and transparency — or omit 192/512 and say so).
8. **`app/opengraph-image.png`** (1200×630) — constraint 5: one recorded `magick` command laying
   the class-C `juju2-wordmark-white.png` (1247×371) centred on the dark paper `#0a1310` with
   breathing room (state the exact geometry), plus its `alt` via the file-convention sibling if
   the docs want one. View it. Gate item.
9. **`components/seo/json-ld.tsx`**: one inline `application/ld+json` `@graph` with `WebSite`
   (`@id #website`, `name`, `url`, `inLanguage ko-KR`, `publisher` → org) and `Organization`
   (`@id #organization`, `name`, `url`, `logo` → the self-hosted wordmark/symbol URL). Contact
   details only if trivially available from `getSiteContact()` already fetched in the layout and
   only the public 운영자 연락처 that the footer already publishes — otherwise omit; never a new
   secret or a new origin. Rendered from the root layout.
10. **`frontend/Dockerfile` + `compose.prod.yml`**: the `NEXT_PUBLIC_SITE_URL` build arg (constraint
    6). `.env.prod.example` stays untouched (this is a build arg, not an env_file key — say so in a
    comment beside `MIJUAL_API_ORIGIN`'s existing note).
11. **`viewport.themeColor`** if `app/layout.tsx`'s `Viewport` export does not already set it (D5
    named the missing theme-color) — one line, from the same token.

## Verification (production build, on this Mac)

- `cd frontend && npm run typecheck && npm run smoke`.
- Production build on the APFS clone with `NEXT_PUBLIC_SITE_URL=https://jujutower.com` and
  `MIJUAL_API_ORIGIN=http://127.0.0.1:8010` (the operator's running dev API — read-only GETs),
  `next start -p 3011` (3010 is the operator's), then `curl` and record: `/robots.txt` (content),
  `/sitemap.xml` (URL count, one event URL, one stock URL, no `www`, no `/ops`, no `/auth`, no
  `/portfolio`), `/manifest.webmanifest` (JSON), `/opengraph-image` (200 `image/png`, 1200×630 via
  `identify`), `/` `<head>` (title, description, canonical, `og:*`, `twitter:*`, the JSON-LD parses
  with `python3 -c "import json…"`), `/stocks/00547510` and one `/events/{rcept_no}` from the board
  (title + description + canonical, **no won figure in either**), `/stocks` and `/ask` (title +
  canonical), `/ops` / `/auth/login` / `/portfolio` (`<meta name="robots" content="noindex…">`),
  a 404 event (`/events/00000000000000` → 404, not 500). Then the API-log double-fetch check
  (item 5). Then the third-party-host grep (constraint 3). Then the production build with
  `NEXT_PUBLIC_SITE_URL` **unset** must **fail** with your assertion's message — record the line.
- Also once against the running **dev** runtime at `http://127.0.0.1:3010` (Fast Refresh): `/`
  `<head>` shows the same tags with the dev fallback base URL, proving nothing broke the
  operator's day-to-day runtime. No browser sweep is owed for `<head>` tags; view the OG image
  itself with the Read tool and say what you saw.
- Tear the clone down; the operator's `frontend/.next` untouched.

## Notebook and docs

- **`## Operator Questions`** — one entry, **"THE META COPY, FOR LITERAL APPROVAL AT THE GATE
  (P4.S5)"**: every string verbatim — site description, the title template, each static route's
  title, the two dynamic title/description patterns with one real rendered example each (툴젠 works
  for both), the noindex pages' titles, the manifest name/short_name, the OG image (path + how it
  was made), and the Naver Search Advisor question. Nothing ships silently.
- **`## Doc impact`** lines: `frontend` (the SEO file set, `lib/seo.ts` as the one source,
  `generateMetadata` on the two dynamic routes, the noindex set, the `NEXT_PUBLIC_SITE_URL` build
  arg and its assertion, the manifest/OG derivatives and their README entries); `operations`
  (`NEXT_PUBLIC_SITE_URL` + the two verification tokens are **build args** in `compose.prod.yml`,
  a change needs a rebuild; Cloudflare prepends its robots block); `security` (robots disallow +
  noindex for `/ops`, `/auth/*`, `/portfolio*`; JSON-LD inline; the no-third-party property
  re-measured on the production build); `product` (meta copy drafted, pending gate approval; the
  OG image); `architecture` (Repo Shape: the new files).
- **`## Decisions`**: canonicals are per-route and apex-only; robots/sitemap scope; the OG image
  provenance; `/stocks` stays crawler-orphaned by design (sitemap only); the double-fetch answer.
- **Notes**: **(from P4.S5, for P4.S6)** — this slice is verified on a local production build
  only; **S6 owns the push + `deploy/deploy.sh` on the box** and must then re-read the *served*
  `/robots.txt` (Cloudflare prepends), count `/sitemap.xml` URLs live, fetch `/opengraph-image`,
  check one event page's `<head>` through Cloudflare, and re-run the third-party grep against the
  live HTML. **(from P4.S5, for P4.REVIEW)** — the strings to approve and the OG image to look at
  belong in the walkthrough. **(for P4.S8)** — 첨부2 may say the site has robots/sitemap/OG only
  after S6 deploys it.
- Drop the two `for P4.S5` notes you consumed; rewrite `## Now` (≤ 15 lines) last; never touch the
  generated `## Slices` block.
- `python3 scripts/workflow.py validate`. Return `done` with the verdict block: `files_changed`,
  `validation` (every command and its outcome), `deviations`, `doc_impact`, `doc_versions: n/a`,
  `review_verdict: n/a`, `walkthrough: none`, `explain: n/a`. Return `needs_operator` only if a
  string decision genuinely cannot be drafted without the operator — the gate is where approval
  happens, so that should not occur.
