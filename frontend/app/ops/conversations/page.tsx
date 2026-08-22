import { Conversations, type LogFilters } from "@/components/ops/Conversations";
import { Door } from "@/components/ops/Door";
import { opsRead } from "@/components/ops/server";
import { getOpsConversations } from "@/lib/api";

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
  if (!page) return <Door />;

  return <Conversations page={page} filters={filters} />;
}
