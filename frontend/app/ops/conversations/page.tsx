import { Conversations, type LogFilters } from "@/components/ops/Conversations";
import { Door } from "@/components/ops/Door";
import { Feedback } from "@/components/ops/Feedback";
import { opsRead } from "@/components/ops/server";
import { getOpsConversations, getOpsFeedback } from "@/lib/api";

function one(value: string | string[] | undefined): string | undefined {
  return typeof value === "string" && value !== "" ? value : undefined;
}

/**
 * 대화 로그 — the log, its two signed filters and its cursor pagination, over a
 * port that has nothing in it yet (P5 stores no conversation; P6 fills the same
 * port with no route change).
 *
 * `?session=` is the page's own name for the cross-link the 사용자 tab sends;
 * the API's filter is `session_hash`, and the translation happens here.
 *
 * **The `save_feedback` 대기열 is on this page**, below the log, because that is
 * where R7 draws it (the Conversations card: "… save_feedback 대기열 — 대기 0건
 * …"; the round's handoff calls the card "the anonymous 해설 log viewer **+ agent
 * feedback queue**"). Two panels, one privacy contract — the queue's rows come
 * from the same anonymous conversations, and its optional 답장 이메일 is the one
 * thing a reader volunteered. The vocky 수집분 stays in its own section
 * (`Vocky.tsx`), linked and never merged. Its cursor is `?feedback_cursor=` so
 * paging one table cannot move the other.
 */
export default async function OpsConversationsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const filters: LogFilters = {
    kind: one(params.kind),
    refusal_category: one(params.refusal_category),
    session: one(params.session),
    cursor: one(params.cursor),
  };

  const page = await opsRead((init) =>
    getOpsConversations(
      {
        kind: filters.kind,
        refusal_category: filters.refusal_category,
        session_hash: filters.session,
        cursor: filters.cursor,
      },
      init,
    ),
  );
  const queue = await opsRead((init) =>
    getOpsFeedback({ cursor: one(params.feedback_cursor) }, init),
  );
  if (!page || !queue) return <Door />;

  return (
    <>
      <Conversations page={page} filters={filters} />
      <Feedback page={queue} />
    </>
  );
}
