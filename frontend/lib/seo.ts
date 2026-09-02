/**
 * Every string a crawler reads, and the one site URL they all resolve against.
 *
 * ## Why this module exists at all
 *
 * The signed design record writes **no document-level copy** — no tagline, no
 * meta description, no per-route `<title>` pattern — and `app/layout.tsx` said so
 * for eleven slices ("inventing a Korean sentence would be a design change").
 * `P4.DECOMP` settled how that gets unblocked without a design round, and the
 * ruling is on the phase's `## Operator Questions` list: **the phase drafts the
 * strings and the operator approves the exact strings literally at the P4
 * acceptance gate.** So this file is neither pure transcription (the way
 * `lib/copy.ts` is) nor free invention. It is a *draft awaiting literal
 * approval*, and every string carries its provenance on the line above it:
 *
 * - **transcribed** — a signed string, **imported** from the module that already
 *   owns it rather than re-typed here, so there is exactly one source of truth
 *   for it (`lib/copy.ts`, `components/chrome/copy.ts`, `components/auth/copy.ts`);
 * - **drafted by P4.S5** — new Korean this slice proposes. Each one is derived
 *   from signed material and says which; none of them is free-hand.
 *
 * `src/mijual/mailcopy.py` carries the identical arrangement for the mail copy
 * `P4.S2` drafted under the same ruling, and the two lists are approved together.
 *
 * ## Two rules that bind every string below
 *
 * **No won amount, ever.** 「확정발행가 전 금액 금지」 is a product rule about what
 * this product is allowed to *state*, and it applies to what a crawler quotes
 * exactly as it applies to what a mail says (P4 `## Decisions`). No builder here
 * reads `offering`, `unit_value`, `lapsed_value` or any other `Figure`: a
 * description carries names, labels and dates, and never a figure.
 *
 * **Korean only, and the name is unspaced 주주의관제탑.** 미주알 is retired (P10)
 * and appears nowhere.
 */

import type { Metadata } from "next";
import { RIGHTS_LABEL_KO, TBD_DISPLAY_KO, WITHDRAWN_NOTICE_KO } from "./copy";
import type { EventView, StockPage } from "./types";
import { RESET_LINK_KO } from "@/components/auth/copy";
import {
  ASK_LABEL_KO,
  BRAND_ALT_KO,
  LOGIN_KO,
  NOTIFICATIONS_LABEL_KO,
  PORTFOLIO_LABEL_KO,
  SOURCE_KO,
  STOCKS_LABEL_KO,
} from "@/components/chrome/copy";

// ---------------------------------------------------------------------------
// The site URL — build-baked, asserted, and never quietly wrong
// ---------------------------------------------------------------------------

/**
 * Where the dev server thinks it lives. **Non-production only.**
 *
 * `next dev` runs on 3010 (`package.json`) and this is the origin the operator
 * actually opens, so a development build keeps working with nothing configured —
 * canonicals and OG URLs simply point at the dev origin, which is the honest
 * answer for a page nobody is crawling.
 */
const DEV_FALLBACK_SITE_URL = "http://127.0.0.1:3010";

/**
 * The production origin, from a **build arg** — and a production build with it
 * unset **fails here**, at module load.
 *
 * The trap this avoids is the one `frontend/Dockerfile` already documents for
 * `MIJUAL_API_ORIGIN`, in its most expensive form: a `?? "https://jujutower.com"`
 * fallback lets a build **succeed** while baking a canonical, a sitemap and an OG
 * URL that may name the wrong origin — and wrong canonicals are the one SEO fault
 * that is invisible in the HTML and visible only months later in a search index.
 * Failing the build is cheap; a silently wrong image is not.
 *
 * It is a `NEXT_PUBLIC_` variable because Next inlines those at **build** time,
 * which is what "build-baked" means here — changing the origin needs a rebuild,
 * not a container restart (`compose.prod.yml` sets it in `build.args`, and it is
 * deliberately **not** an `.env.prod` key: the web container carries no env_file).
 *
 * `jujutower.com` is **apex-only**: `www.jujutower.com` exists and 301s to the
 * apex (`P4.S4`), so no canonical and no sitemap URL may ever name `www`.
 */
function resolveSiteUrl(): string {
  const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  if (configured) return configured.replace(/\/+$/, "");
  if (process.env.NODE_ENV === "production") {
    throw new Error(
      "NEXT_PUBLIC_SITE_URL build arg required (see compose.prod.yml build.args) — " +
        "a production build must bake its own origin; canonicals, the sitemap and " +
        "the OG image URL all resolve from it.",
    );
  }
  return DEV_FALLBACK_SITE_URL;
}

export const SITE_URL = resolveSiteUrl();

/** Optional, production-only, and **never given a fallback**: unset ⇒ `undefined`
 * ⇒ the `<meta>` is not rendered at all (never a blank `content=""`). Google's
 * property is a DNS-TXT domain property through Cloudflare and needs nothing in
 * the HTML; Naver Search Advisor needs an HTML tag, and whether to register at
 * all is an operator decision on the phase's `## Operator Questions` list. */
export const GOOGLE_SITE_VERIFICATION = process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION;
export const NAVER_SITE_VERIFICATION = process.env.NEXT_PUBLIC_NAVER_SITE_VERIFICATION;

// ---------------------------------------------------------------------------
// The site's own words
// ---------------------------------------------------------------------------

/** transcribed — `components/chrome/copy.ts` `BRAND_ALT_KO`, the wordmark's own
 * text equivalent and the product's name in `docs/current/product.md`. Unspaced. */
export const SITE_NAME = BRAND_ALT_KO;

/**
 * drafted by P4.S5 — the site description, in two sentences from two signed
 * sources and nothing else.
 *
 * Sentence 1 restates `docs/current/product.md` `## Summary`'s first clause
 * ("watches Korean disclosure (DART) for shareholder rights with a deadline")
 * with the footer's own provenance noun phrase, 금융감독원 DART 전자공시
 * (`SOURCE_KO`, R2). Sentence 2 is `HERO_SUB_KO` **verbatim** — the landing's
 * signed subline, which is already the product's own one-line description of
 * what a reader does here.
 *
 * No figure, and deliberately no number at all: the board's counts move twice a
 * day and a description is quoted by a crawler long after it was read.
 */
export const SITE_DESCRIPTION_KO =
  "금융감독원 DART 전자공시에서 마감이 있는 주주의 권리를 감시합니다. " +
  "종목명 하나로 놓친 권리와 진행 중인 권리를 조회합니다.";

/** drafted by P4.S5 — the title template. The separator is a plain pipe and the
 * suffix is the product's own name; `title.default` (below) is what a route
 * without its own title gets, and it is the bare name rather than the template
 * applied to nothing. */
export const TITLE_TEMPLATE = `%s | ${SITE_NAME}`;
export const TITLE_DEFAULT = SITE_NAME;

/** The provenance clause every dynamic description ends on.
 * transcribed — `components/chrome/copy.ts` `SOURCE_KO`, the footer's literal;
 * the trailing period is this module's sentence punctuation, not part of it. */
const SOURCE_SENTENCE_KO = `${SOURCE_KO}.`;

// --- the static routes' titles: all four transcribed, none of them new --------

/** transcribed — `STOCKS_LABEL_KO` (R4 named the surface 내 종목 조회). */
export const STOCKS_TITLE_KO = STOCKS_LABEL_KO;
/** transcribed — `ASK_LABEL_KO` (R6 retired 해설 in favour of AI 질문). */
export const ASK_TITLE_KO = ASK_LABEL_KO;
/** transcribed — `LOGIN_KO` (R2 §Page shell's nav slot). */
export const LOGIN_TITLE_KO = LOGIN_KO;
/** transcribed — `components/auth/copy.ts` `RESET_LINK_KO` (R5-1). */
export const RESET_TITLE_KO = RESET_LINK_KO;
/** transcribed — `PORTFOLIO_LABEL_KO` (R5-6; the 2층 surface's own name). */
export const PORTFOLIO_TITLE_KO = PORTFOLIO_LABEL_KO;
/** transcribed — `NOTIFICATIONS_LABEL_KO` (R5-6). */
export const NOTIFICATIONS_TITLE_KO = NOTIFICATIONS_LABEL_KO;

// ---------------------------------------------------------------------------
// The two dynamic routes
// ---------------------------------------------------------------------------

/** An issuer with no `corp_name` is named by the handle the URL already carries.
 * The API can serve a null name (`Identity.corp_name` is nullable) and a title
 * reading 「— | 주주의관제탑」 would be worse than the code. */
function issuerName(name: string | null, fallback: string): string {
  return name?.trim() || fallback;
}

/** drafted by P4.S5 — `/stocks/{corp_code}`'s title: **the issuer's name and
 * nothing else**, because the template already supplies the site's. Rendered:
 * 「툴젠 | 주주의관제탑」. */
export function stockTitleKo(page: StockPage): string {
  return issuerName(page.stock.corp_name, page.stock.corp_code);
}

/**
 * drafted by P4.S5 — `/stocks/{corp_code}`'s description.
 *
 * Shape: `{종목명} — 진행 중인 권리 {N}건. {HERO_SUB_KO의 술어}. {출처}`. 진행 중인
 * 권리 is `HERO_SUB_KO`'s own phrase and `page.rights.count` is the served count
 * of exactly those rows, so the number is the page's own fact rather than a claim.
 * With no rights rows the count clause is dropped rather than printed as 0건.
 *
 * **No 소멸 value and no won amount**: the 놓친 권리 half of this page is money,
 * and money never enters a meta string.
 */
export function stockDescriptionKo(page: StockPage): string {
  const name = issuerName(page.stock.corp_name, page.stock.corp_code);
  const count = page.rights.count;
  const head = count > 0 ? `${name} — 진행 중인 권리 ${count}건. ` : `${name} — `;
  return `${head}놓친 권리와 진행 중인 권리를 마감일과 함께 조회합니다. ${SOURCE_SENTENCE_KO}`;
}

/**
 * drafted by P4.S5 — `/events/{rcept_no}`'s title, in the shape `P4.S2`'s mail
 * **subject** already uses (`{종목} — {마감명} …`), so the two surfaces name the
 * same event the same way. `countdown.label_ko` is served, never composed here.
 *
 * The D-day is deliberately **absent** from the title — see the description.
 */
export function eventTitleKo(view: EventView): string {
  const name = issuerName(view.corp_name, view.corp_code);
  return `${name} — ${view.countdown.label_ko}`;
}

/**
 * drafted by P4.S5 — `/events/{rcept_no}`'s description, in three variants
 * because the payload has three shapes and none of them may be invented into
 * another:
 *
 * - **철회** — the served `notice_ko` (the locked 철회 sentence), never a
 *   composed one, and no schedule: a withdrawn event has none to state;
 * - **일정 추후결정** (`countdown.date === null`) — the signed `TBD_DISPLAY_KO`,
 *   which means *no date*; `ui-traps.md` #4 forbids a date anywhere near it, so
 *   this branch prints none;
 * - **일정 있음** — the deadline's own label and its date.
 *
 * **`countdown.dday` is read by neither branch, on purpose.** A snippet is cached
 * by a crawler and shown for weeks; 「D-7」 is true for one day, and a stale D-day
 * in a search result would be this product stating something false about a
 * deadline — the exact failure the 확정발행가 rule exists to prevent, one axis
 * over. The date does not go stale, so the date is what ships.
 */
export function eventDescriptionKo(view: EventView): string {
  const name = issuerName(view.corp_name, view.corp_code);
  const rights = RIGHTS_LABEL_KO[view.rights_type];
  const head = `${name} ${rights} — `;

  if (view.state === "withdrawn") {
    const notice = view.notice_ko ?? WITHDRAWN_NOTICE_KO[view.rights_type];
    return `${head}${notice}. ${SOURCE_SENTENCE_KO}`;
  }

  const { label_ko: label, date } = view.countdown;
  const schedule = date ? `${label} ${date}` : `${label} ${TBD_DISPLAY_KO}`;
  return `${head}${schedule}. ${SOURCE_SENTENCE_KO}`;
}

// ---------------------------------------------------------------------------
// The share card
// ---------------------------------------------------------------------------

/**
 * The Open Graph / Twitter card image, **declared explicitly** rather than left
 * to the `app/opengraph-image.png` file convention — and the reason is a Next
 * behaviour that is invisible until you look at a child route's HTML.
 *
 * Next attaches a file-convention image to the segment it sits in. `openGraph`,
 * meanwhile, is **replaced** wholesale at every segment rather than merged
 * (`resolve-metadata.js`), and the static-file merge only fires for a segment
 * whose own `openGraph` declares no `images`. Put those two together and the
 * root's `opengraph-image.png` reaches `/` and **nothing else**: `P4.S5` measured
 * exactly that on the production build — `/` carried `og:image`, while `/stocks`,
 * `/ask` and both dynamic routes carried none, which is every share of an actual
 * event page arriving with no card.
 *
 * So the image is stated here, once, and every route gets the same four tags.
 * The file stays in `app/` because that is what serves it at
 * `/opengraph-image.png` with the right content type; only its *tags* are ours.
 * (The `opengraph-image.alt.txt` sibling was therefore removed — it feeds only
 * the auto-generated tag this declaration overrides, so leaving it would be a
 * file that looks load-bearing and is not. `alt` is the `alt` field below.)
 *
 * 1200×630 is the measured file (`public/assets/README.md`); the alt is the
 * wordmark's own text equivalent, exactly as the chrome's `<img>` uses it.
 */
export const OG_IMAGE = {
  url: "/opengraph-image.png",
  width: 1200,
  height: 630,
  type: "image/png",
  /** transcribed — `BRAND_ALT_KO`, the mark's signed text equivalent. */
  alt: BRAND_ALT_KO,
} as const;

// ---------------------------------------------------------------------------
// The one shape every indexable route's metadata takes
// ---------------------------------------------------------------------------

/**
 * Title + description + **canonical** + the Open Graph / Twitter field set for
 * one indexable route, built in one place.
 *
 * Two Next traps make a helper the right answer rather than a tidiness:
 *
 * 1. **`openGraph` is replaced wholesale at every segment**, not merged
 *    (`resolve-metadata.js`: `newResolvedMetadata.openGraph = resolveOpenGraph(
 *    metadata.openGraph, …)`). A route that sets `openGraph: { title }` and
 *    expects to inherit `type` / `locale` / `siteName` from the root layout
 *    silently loses all three. Every caller here gets the whole set.
 * 2. **A canonical must be per route** — the root layout deliberately sets no
 *    `alternates`, because that key *is* inherited as a whole and would make
 *    every route claim `/`. Pairing the canonical with the title in one call is
 *    what makes forgetting it visible.
 *
 * `path` is root-relative (`/`, `/stocks`, `/events/20260806000329`); Next
 * resolves it against `metadataBase`, which is `SITE_URL` — apex-only, so no
 * canonical can name `www`.
 *
 * `og:title` is the route's **own** title rather than the templated one: the
 * brand travels in `og:site_name`, which is the field consumers render beside it.
 */
export function routeMetadata(route: {
  title: string;
  description: string;
  path: string;
}): Metadata {
  const { title, description, path } = route;
  return {
    title,
    description,
    alternates: { canonical: path },
    openGraph: {
      type: "website",
      locale: "ko_KR",
      siteName: SITE_NAME,
      url: path,
      title,
      description,
      images: [OG_IMAGE],
    },
    twitter: { card: "summary_large_image", title, description, images: [OG_IMAGE] },
  };
}

// ---------------------------------------------------------------------------
// The manifest's two colours
// ---------------------------------------------------------------------------

/**
 * `#0a1310` — the **cosmos** `--paper`, read out of the frozen
 * `public/foundations/tokens.css` (line 51, the `.cosmos` block).
 *
 * The product renders on cosmos and only on cosmos: `app/layout.tsx` puts
 * `class="cosmos"` on `<html>` unconditionally, so the light `--paper`
 * (`#f2f3f2`, line 9) is never the surface a reader or an installed PWA sees.
 * Both manifest colours are therefore the dark one, and `viewport.themeColor`
 * is the same value — the browser chrome should match the page it frames.
 *
 * Copied as an ImageMagick/CSS **literal**, exactly as `#2b8e6c` is in
 * `public/assets/README.md`: `tokens.css` stays frozen and is never imported.
 */
export const THEME_COLOR = "#0a1310";
export const BACKGROUND_COLOR = "#0a1310";
