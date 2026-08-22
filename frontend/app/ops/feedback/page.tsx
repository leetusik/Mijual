import { Door } from "@/components/ops/Door";
import { Vocky } from "@/components/ops/Vocky";
import { opsRead } from "@/components/ops/server";
import { getOpsVocky } from "@/lib/api";

function one(value: string | string[] | undefined): string | undefined {
  return typeof value === "string" && value !== "" ? value : undefined;
}

/**
 * 피드백 — the vocky 관찰 뷰 (R7 §6.3).
 *
 * The record maps its `Feedback` card to this section ("**Feedback** — vocky
 * 관찰 뷰 프레임 (§6.3)") and draws the `save_feedback` 대기열 on the
 * Conversations card instead; `Vocky.tsx` carries the full mapping and the
 * privacy reasoning behind it. `P5.S18` decided the observation API's shape
 * against vocky's running product and wrote it back into §6.3, so this page
 * renders real columns rather than the card's placeholder `?` headers.
 *
 * The read goes through the service (`GET /ops/vocky`): the `vk_` key is a server
 * secret and the browser never holds one.
 */
export default async function OpsFeedbackPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const page = await opsRead((init) => getOpsVocky({ cursor: one(params.cursor) }, init));
  if (!page) return <Door />;
  return <Vocky page={page} />;
}
