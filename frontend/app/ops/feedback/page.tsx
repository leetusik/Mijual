import { Door } from "@/components/ops/Door";
import { Feedback } from "@/components/ops/Feedback";
import { opsRead } from "@/components/ops/server";
import { getOpsFeedback } from "@/lib/api";

function one(value: string | string[] | undefined): string | undefined {
  return typeof value === "string" && value !== "" ? value : undefined;
}

/**
 * 피드백 — the `save_feedback` queue, read-only, with its signed empty state.
 *
 * The vocky observation view belongs on this tab too and is **`P5.S18`'s**: §6.3
 * delegates its return shape to the build against vocky's real API, and a frame
 * with invented column names is what the round forbids.
 */
export default async function OpsFeedbackPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const page = await opsRead((init) => getOpsFeedback({ cursor: one(params.cursor) }, init));
  if (!page) return <Door />;
  return <Feedback page={page} />;
}
