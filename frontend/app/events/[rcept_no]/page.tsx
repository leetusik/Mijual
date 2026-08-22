import { notFound } from "next/navigation";
import { connection } from "next/server";
import { EventDetail } from "@/components/event";
import { ApiError, getEvent } from "@/lib/api";

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
 * So this calls `notFound()` and renders the framework's own not-found inside the
 * chrome. The signed design writes **no 404 copy** — it writes *state* copy — and
 * a Korean sentence written here would be invented product copy, which is a
 * design change (recorded in `phase.md` for `P5.S19`/`P5.REVIEW`; R4's 검색 불일치
 * line belongs to a different surface and is not borrowable).
 *
 * `connection()` marks the page request-time, so `next build` needs no API and a
 * countdown is never a build-time snapshot served hours later.
 */
export default async function EventPage({
  params,
}: {
  params: Promise<{ rcept_no: string }>;
}) {
  await connection();
  const { rcept_no: rceptNo } = await params;

  let detail;
  try {
    detail = await getEvent(rceptNo);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return <EventDetail detail={detail} />;
}
