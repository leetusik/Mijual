import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { connection } from "next/server";
import { EventDetail } from "@/components/event";
import { ApiError, getEvent } from "@/lib/api";
import { eventPath } from "@/lib/routes";
import { eventDescriptionKo, eventTitleKo, routeMetadata } from "@/lib/seo";
import { readAuthState } from "@/lib/session.server";

/**
 * `/events/{rcept_no}` — one event's detail page (R3).
 *
 * **The route key is `rcept_no`**, resolved server-side against every stored
 * version of every event (`P5.S3`'s recorded choice): it is what the design links
 * by — the board row, the DART link and the 정정 rail all speak filing numbers —
 * and it survives the thing that makes the number awkward as a key, that it
 * *mutates* to the newest version. Yesterday's link therefore still opens the
 * page, and the page still renders **today's** readable version.
 *
 * ## The 404 is a 404, and deliberately says nothing
 *
 * Only a renderable event has a page: `exposable` renders the card and
 * `withdrawn` renders its notice — 철회 is a surface, not an error — while
 * everything else (suppressed · flagged · `no_document` · `no_detail` ·
 * `incomplete_api_row`) is a 404 envelope from the API. An event the contract
 * does not expose must **not** become a page explaining why it is not exposed:
 * the reason is internal and the operator's panel is the only surface that sees
 * it (`states-and-trust.md` §4, D-14).
 *
 * So this calls `notFound()`, which now lands on **미주알's own** not-found
 * surface (`app/not-found.tsx`, R10 §8): Korean, inside the R8 chrome, status
 * 404, the requested address echoed in mono — and **still no reason**. R3 wrote
 * *state* copy and deliberately no 404 copy, so until R10 designed the page and
 * signed its three strings, the framework's English default was what a Korean
 * reader met (`P5.S19` recorded it; P8 Q15 closed it).
 *
 * `connection()` marks the page request-time, so `next build` needs no API and a
 * countdown is never a build-time snapshot served hours later.
 */
/**
 * The event's own `<title>`, description and canonical, from the event itself.
 *
 * Shapes are `lib/seo.ts`'s — 「{종목} — {마감명}」 for the title (the same shape
 * `P4.S2`'s mail subject uses, so the two surfaces name one event the same way)
 * and a description that branches on 철회 / 추후결정 / 일정 있음 and carries **no
 * won amount and no D-day**. The file says why for each.
 *
 * **A 404 must not become a 500 here.** `getEvent` throws `ApiError(404)` for
 * every non-renderable event, and an unhandled throw inside `generateMetadata`
 * is a server error rather than a not-found. So this catches and returns `{}` —
 * an empty object inherits the root layout's default title and, because the root
 * sets no `alternates`, contributes **no canonical**, which is exactly right for
 * a page that does not exist. `notFound()` is legal in `generateMetadata` in this
 * version and would work too; leaving the 404 decision to the page below keeps
 * one place deciding it, and that place already explains itself at length.
 *
 * The `getEvent` call is the same one the page makes, with the same argument, so
 * Next's per-render `fetch` memoization serves both from one round trip —
 * **measured** in `var/stack/api.log`, not assumed (`P4.S5`).
 */
export async function generateMetadata({
  params,
}: {
  params: Promise<{ rcept_no: string }>;
}): Promise<Metadata> {
  const { rcept_no: rceptNo } = await params;
  const detail = await getEvent(rceptNo).catch(() => null);
  if (!detail) return {};

  return routeMetadata({
    title: eventTitleKo(detail),
    description: eventDescriptionKo(detail),
    path: eventPath(rceptNo),
  });
}

/**
 * ## The session is resolved **here**, on the server, and travels as one boolean
 *
 * R5-2's 「이 마감 알림 받기 →」 / 「보유 종목에 담기 →」 line has two states
 * and `DeadlineOffer` renders **neither** until it knows which — showing the
 * anonymous label first would tell a logged-in reader for a moment that they have
 * no account. That reading is unchanged and still right; what moved is *when* the
 * answer exists. It used to arrive in the browser, from `GET /auth/me` after
 * hydration, and inserting a 44px line above the fold at ~2.4s cost this route a
 * **0.0325 mobile CLS** — the last route above P4's 0.01 target (`P4.F5`
 * measured it; `P4.F10` is this).
 *
 * `readAuthState()` is the same server read `app/auth/login/page.tsx` makes: it
 * forwards this request's own `cookie` header and **never throws** (a service
 * that is down is answered as anonymous). It runs in `Promise.all` **beside**
 * `getEvent`, not after it, so the page pays one round trip's latency rather than
 * two — and for a reader carrying no cookie at all it costs no request at all
 * (`lib/session.server.ts` short-circuits, which is what keeps a crawl of 445
 * event pages exactly as cheap as it was).
 *
 * **Only a boolean goes down the tree.** `AuthState` carries the reader's
 * `Account` — email included — and passing the object would serialise it into the
 * HTML of a page that has no use for it. The line needs one bit and gets one bit.
 *
 * `connection()` above already makes this route request-time, so nothing about
 * caching changes: a session state must never be a build artifact, and this page
 * was never one.
 */
export default async function EventPage({
  params,
}: {
  params: Promise<{ rcept_no: string }>;
}) {
  await connection();
  const { rcept_no: rceptNo } = await params;

  let detail;
  let auth;
  try {
    [detail, auth] = await Promise.all([getEvent(rceptNo), readAuthState()]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return <EventDetail detail={detail} initialAuthenticated={auth.authenticated} />;
}
