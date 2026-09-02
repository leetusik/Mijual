# P4.S5 — SEO: metadata, robots, sitemap, canonicals, OG, JSON-LD

```yaml
status: done
summary: >
  The site is describable and indexable: one typed source (frontend/lib/seo.ts) for every meta
  string with per-line provenance, robots/sitemap/manifest/OG-image/JSON-LD, generateMetadata on
  both dynamic routes, noindex on the five non-reader surfaces, per-route canonicals on the apex,
  and NEXT_PUBLIC_SITE_URL as an asserted build arg — all verified on a real standalone production
  build (800 sitemap URLs, one API round trip per dynamic page, a build without the arg exits 1, no
  third-party origin), on an APFS clone that never touched the operator's dev runtime. Nothing is
  deployed; P4.S6 owns that.
files_changed:
  - frontend/lib/seo.ts                              # new — the one typed source
  - frontend/components/seo/json-ld.tsx              # new
  - frontend/app/robots.ts                           # new
  - frontend/app/sitemap.ts                          # new
  - frontend/app/manifest.ts                         # new
  - frontend/app/opengraph-image.png                 # new — class-C derivative, gate item
  - frontend/public/assets/juju2-icon-192.png        # new — class-C derivative
  - frontend/public/assets/juju2-icon-512.png        # new — class-C derivative
  - frontend/app/layout.tsx
  - frontend/app/page.tsx
  - frontend/app/stocks/page.tsx
  - frontend/app/ask/page.tsx
  - frontend/app/stocks/[corp_code]/page.tsx
  - frontend/app/events/[rcept_no]/page.tsx
  - frontend/app/ops/layout.tsx
  - frontend/app/auth/login/page.tsx
  - frontend/app/auth/reset/page.tsx
  - frontend/app/portfolio/page.tsx
  - frontend/app/portfolio/notifications/page.tsx
  - frontend/public/assets/README.md
  - frontend/Dockerfile
  - compose.prod.yml
  - works/phases/active/P4/phase.md
  - works/phases/active/P4/slices/P4.S5/result.md
validation:
  - "cd frontend && npm run typecheck: PASS (tsc --noEmit, clean)"
  - "cd frontend && npm run smoke: PASS (22/22)"
  - "production build on an APFS clone, NEXT_PUBLIC_SITE_URL=https://jujutower.com: PASS (23 routes)"
  - "standalone server (node .next/standalone/server.js, :3011) — robots/sitemap/manifest/OG/head/404/noindex checks: PASS (all listed below)"
  - "production build with NEXT_PUBLIC_SITE_URL unset: FAILS as designed, exit 1, assertion message quoted below"
  - "generateMetadata double-fetch measurement in var/stack/api.log: ONE fetch per page (no React cache() needed)"
  - "third-party-origin grep over 11 built pages: only dart.fss.or.kr + schema.org (a JSON-LD @context string); zero off-origin src/href"
  - "dev runtime re-check at http://127.0.0.1:3010: PASS (dev fallback base URL, nothing broken)"
  - "python3 scripts/workflow.py validate: PASS (pre-existing oversized_doc_sections warning only)"
deviations: see "Deviations" below — four, all small; the largest is that the plan's suggested
  countdown.dday was deliberately left out of every description.
doc_impact: six lines appended to phase.md "## Doc impact" — frontend (the SEO file set + the two
  Next traps), operations (NEXT_PUBLIC_SITE_URL is a build arg → rebuild not restart; Cloudflare
  prepends its robots block), security (no-third-party-origin re-measured; disallow + noindex),
  product (the site is describable; strings pending gate approval), architecture (Repo Shape),
  frontend/product (three class-C image derivatives + their README entries).
doc_versions: n/a
review_verdict: n/a
walkthrough: none
explain: n/a
```

---

## What landed

**`frontend/lib/seo.ts` is the one typed source.** Every meta string, the site URL, the OG field
set, the two manifest colours and the per-route metadata builder live there, and each string carries
a one-line provenance comment — `transcribed` (a signed string, **imported** from the module that
already owns it, so there is one source of truth) or `drafted by P4.S5` (new Korean, derived from
signed material and saying which). Same arrangement `src/mijual/mailcopy.py` uses for the mail copy.
The full string list, verbatim with rendered examples, is the phase notebook's
`## Operator Questions` entry 「THE META COPY, FOR LITERAL APPROVAL AT THE GATE (P4.S5)」 — not
restated here.

The rest is the file set the plan named: `app/robots.ts`, `app/sitemap.ts`, `app/manifest.ts`,
`app/opengraph-image.png`, `components/seo/json-ld.tsx`, `generateMetadata` on
`/events/[rcept_no]` and `/stocks/[corp_code]`, `robots: {index:false, follow:false}` plus a title
on the five non-reader surfaces, `viewport.themeColor`, and the `NEXT_PUBLIC_SITE_URL` build arg in
`frontend/Dockerfile` + `compose.prod.yml`.

The root layout's "No tagline, no description" comment was **rewritten, not deleted**: it now says
the constraint did not change, the *route* did — the phase drafts and the gate approves — and points
at `lib/seo.ts`.

---

## The two Next traps this slice paid a rebuild to find

Both are recorded in the notebook's `## Decisions`; the detail is here.

**1. `alternates` is inherited as a whole, so the root layout sets none.** This is the trap the plan
warned about and it was avoided by construction: a `canonical: "/"` in `app/layout.tsx` would make
every route without its own claim the home page — correct-looking on `/`, wrong everywhere else, and
invisible in a diff. `routeMetadata()` pairs the canonical with the title so forgetting one shows up.

**2. A file-convention `opengraph-image.png` reaches its own segment ONLY — measured, not assumed.**
The first production build served `og:image` on `/` and **on nothing else**:

```
### /        og:image : https://jujutower.com/opengraph-image.png?opengraph-image.39-vfg4fg41x7.png
### /stocks  (no og:image, no twitter:image)
### /ask     (no og:image, no twitter:image)
```

The mechanism is two Next behaviours meeting. `resolve-metadata.js` **replaces** `openGraph`
wholesale per segment (`newResolvedMetadata.openGraph = resolveOpenGraph(metadata.openGraph, …)`,
not a merge), and `mergeStaticMetadata` folds a file-convention image in only
`if (openGraph && !source?.openGraph?.hasOwnProperty('images'))` — i.e. for a segment that declares
its own `openGraph` with no `images`, nothing is folded in and the parent's images are already gone.
Every route that sets `og:title`/`og:description` therefore loses the card, which is every share of
an actual event page arriving blank.

Fix: `OG_IMAGE` is declared once in `lib/seo.ts` (url, width, height, type, alt) and spread into the
root layout **and** `routeMetadata()`. `app/opengraph-image.alt.txt` was created and then **removed**
— it feeds only the auto-generated tag this declaration overrides, so leaving it would be a file that
looks load-bearing and is not; the alt is `OG_IMAGE.alt`. After the fix every route serves
`https://jujutower.com/opengraph-image.png`.

*(A wasted cycle worth recording: the first re-check still showed the old tags because `pkill -f`
did not match the standalone server and the rebuilt one died on `EADDRINUSE`, silently, into its log.
Killing by PID from `lsof` is what fixed it. The defect above is genuine — it was measured on the
first build, whose server was the right one.)*

---

## The measurements the plan asked for

### The `generateMetadata` double fetch does not happen

Measured against the operator's running dev API through `var/stack/api.log`, warm (not a first
compile), one request per page:

```
GET /events/20260806000329   -> 1 line
GET /stocks/00547510         -> 1 line
GET /events/20250902000288   -> 1 line
```

`generateMetadata` and the page component both call `getEvent(rceptNo)` / `getStock(corpCode)` with
identical arguments, and Next's per-render `fetch` memoization already collapses them. **No React
`cache()` wrapper was added** — it would be a second mechanism for a solved problem. If a future
change makes the two call sites pass different `init` objects, the memoization breaks silently and
this is the measurement to re-run.

### A production build without `NEXT_PUBLIC_SITE_URL` fails

`env -u NEXT_PUBLIC_SITE_URL npm run build` → **exit code 1**:

```
Error: Failed to collect configuration for /ask
  [cause]: Error: NEXT_PUBLIC_SITE_URL build arg required (see compose.prod.yml build.args) —
           a production build must bake its own origin; canonicals, the sitemap and the OG image
           URL all resolve from it.
      at <unknown> (lib/seo.ts:88:11)
      at module evaluation (lib/seo.ts:95:1)
```

`frontend/Dockerfile`'s `test -n "$NEXT_PUBLIC_SITE_URL"` fires earlier still, with the same message
shape as the existing `MIJUAL_API_ORIGIN` assertion. Neither has a `?? "https://…"` fallback; the
**non**-production fallback is `http://127.0.0.1:3010`, which is why the operator's `next dev` needs
no configuration.

### No third-party origin, re-measured on the production build

11 pages fetched from the standalone server and concatenated (602 KB of HTML). Every `https?://`
host in it:

```
   25  dart.fss.or.kr      the DART 원문 links (allowed)
  204  jujutower.com       own origin
   21  schema.org          JSON-LD @context — a namespace STRING, never fetched
```

and **zero** off-origin `src`/`href` on any `<script> <link> <img> <iframe> <source> <video>
<audio>`. The 11 `schema.org` mentions outside the `ld+json` element are the RSC flight payload's
copy of the same script — still data. The signed property in `security.md` survives SEO intact.

---

## The production-build check, in full

Built on an **APFS clone** of `frontend/` (`cp -Rc`, `P4.S1`'s recipe) with
`NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010`, then run the
way the **container** runs it — `node .next/standalone/server.js` on port 3011 with `NODE_ENV=production`,
`.next/static` and `public/` staged beside it exactly as `frontend/Dockerfile` does. (`next start`
was tried first and Next itself objects: *"next start does not work with output: standalone"*.)

| check | result |
|---|---|
| `/robots.txt` | 200 `text/plain` — `User-Agent: *` / `Allow: /` / `Disallow: /api/ /ops /auth/ /portfolio` / `Sitemap: https://jujutower.com/sitemap.xml`. No content-signals duplicated. |
| `/sitemap.xml` | 200, **800 URLs** = 3 static + **445** events + **352** issuers. All apex. `www` 0, `/ops` 0, `/auth` 0, `/portfolio` 0, duplicates 0. `lastmod` = the board's `reference` (`2026-09-02`) on the dynamic half only. |
| `/manifest.webmanifest` | 200 `application/manifest+json`, parses; name/short_name 주주의관제탑, `lang: ko`, `display: standalone`, both colours `#0a1310`, five icons |
| the five manifest icons | `/icon1.png` 16×16, `/icon.png` 32×32, `/apple-icon.png` 180×180, `/assets/juju2-icon-192.png` 192×192, `/assets/juju2-icon-512.png` 512×512 — all 200 `image/png` |
| `/opengraph-image.png` | 200 `image/png`, **1200×630**. (`/opengraph-image` without the extension is a 404 — the tags name the `.png` path.) |
| `/` | title `주주의관제탑`, description, canonical `https://jujutower.com`, `robots: index, follow`, og:title/description/url/image, twitter card + image |
| `/stocks` | `내 종목 조회 \| 주주의관제탑`, canonical `/stocks`, og set complete |
| `/ask` | `AI 질문 \| 주주의관제탑`, canonical `/ask`, og set complete |
| `/stocks/00547510` | `툴젠 \| 주주의관제탑`; description `툴젠 — 진행 중인 권리 1건. …`; canonical `/stocks/00547510`. **No won figure.** |
| `/events/20260806000329` | `툴젠 — 신주인수권증서 매매 마감 \| 주주의관제탑`; description ends `… 2026-09-07. 자료: 금융감독원 DART 전자공시.`; canonical the route. **No won figure, no D-day.** |
| `/events/20250902000288` | the ② variant: `제이에스링크 — 전환청구 개시 \| 주주의관제탑` |
| JSON-LD on `/` | parses with `json.loads`; `Organization` (+ the two footer contact fields) and `WebSite` with `publisher` → `#organization`, `inLanguage: ko-KR` |
| `/ops` | `robots: noindex, nofollow`; title still exactly `주주의관제탑 운영` |
| `/auth/login`, `/auth/reset?token=…`, `/portfolio`, `/portfolio/notifications` | `noindex, nofollow`; titles 로그인 · 비밀번호 재설정 · 내 포트폴리오 · 알림 설정 |
| `/events/00000000000000` | **404** (not 500), default title, no canonical |
| `/stocks/99999999` | **404** |

Then the same `<head>` was read once against the operator's running **dev** server on 3010: identical
tags with the dev fallback base (`canonical http://127.0.0.1:3010`, `og:image
http://127.0.0.1:3010/opengraph-image.png`, `theme-color #0a1310`, event title
`툴젠 — 신주인수권증서 매매 마감 | 주주의관제탑`). The dev runtime is untouched — `frontend/.next` still
carries its 09-01 03:06 mtime, `npm run dev -H 0.0.0.0 -p 3010` is the same PID, `/api/health` 200.

---

## The three new images

One recorded `magick` command each, from existing class-B/C assets, nothing drawn and no text set.
Commands, geometry, the inherited traps, a verify block and both hash forms are now in
`frontend/public/assets/README.md` in that file's own style; the class table's class-C row was
extended to name them.

- **`app/opengraph-image.png`** — `juju2-wordmark-white.png` (1247×371) scaled to **720 wide** and
  composited dead-centre on a 1200×630 rectangle of cosmos `--paper` `#0a1310`. Measured:
  `-trim` → `720x214+240+208`, opaque (1 distinct alpha), 20,211 pure-white ink px over 723,582
  paper px, 32,679 b.
  **I looked at it** (rendered PNG): the white 주주의관제탑 wordmark with its sparkle cluster at the
  upper right, generous dark margins, the glyph band sitting just below the vertical centre with the
  sparkle balancing it above. It reads cleanly at card size. The box was centred rather than lifted
  by R17's `INK_OFFSET`, because that rule exists for a *height-constrained* strip where the sparkle
  is decoration; on a large card the whole mark reads and the ink box **is** the artwork's extent.
- **`public/assets/juju2-icon-192.png` / `-512.png`** — the R18 favicon recipe at two more sizes:
  the symbol recoloured `#2b8e6c` **before** the resize, on a transparent canvas, ink at 75 % width.
  Measured `144x107+24+42` and `384x285+64+113`; every visible pixel exactly `#2b8e6c` (the check
  returns 0 non-conforming px on both).

All three were re-derived into a scratch directory from the recorded commands and compared:
**`compare -metric AE` = 0** and identical `identify -format '%#'` pixel signatures on every one.
That is what "regenerable here" is supposed to mean.

The share card is a **gate item** (it is the first image of the product a stranger sees and the
design record specifies none); rejecting it is one file and one command.

---

## Deviations from `plan.md`

1. **No `countdown.dday` in any description**, although the plan lists it among the available
   inputs. A meta description is cached by a crawler and shown for weeks; 「D-7」 is true for one day,
   so a stale D-day in a search result would be this product stating something false about a
   deadline. The 마감 **date** does not go stale and is what ships. (The mail keeps its D-표기 — it is
   delivered once and read immediately.) The 추후결정 branch prints the signed `추후결정` and, per
   `ui-traps.md` #4, no date at all.
2. **`app/opengraph-image.alt.txt` was created and then removed**, and the OG image's tags are
   declared explicitly instead of by file convention. Forced by the measured Next behaviour above:
   left implicit, only `/` had a share card. The `.png` stays in `app/` (that is what serves it).
3. **192/512 manifest tiles were made rather than omitted.** The plan allowed either. A manifest
   declaring `display: standalone` with no ≥192 icon is not installable, and the two files are the
   already-signed favicon recipe at two more sizes — not a new look, and not a new decision.
4. **The scratch clone could not be deleted with `rm -rf`** (harness denied every form of it);
   `rm -r` without `-f` was allowed and the clone, both staged standalone trees and the re-derivation
   directory are gone. Nothing was worked around. Everything lived in the session scratchpad, outside
   the repository, and held no secret.

Not a deviation, but stated so nobody looks for it: **`frontend/Dockerfile`'s new `ARG`/`RUN test -n`
lines were not exercised by an actual `docker build`.** The hard constraints forbid running
`compose.prod.yml` locally, and the lines are a byte-for-byte copy of the `MIJUAL_API_ORIGIN`
assertion three lines above that `P4.S1` proved. The *code* half of the same guard **was** exercised:
the build exits 1 without the variable.

---

## What is NOT done, and whose it is

Nothing is deployed. `robots.txt` and `sitemap.xml` still 404 at `https://jujutower.com`, and the
served `/robots.txt` is still Cloudflare's managed block alone. **`P4.S6` owns the push and
`deploy/deploy.sh`**, and then five live re-checks — the notebook's
`**(from P4.S5, for P4.S6)**` note lists them with the expected values, including the one that
cannot be checked anywhere else: Cloudflare **prepends** its block, so the file to read is the served
one, not this route's output.
