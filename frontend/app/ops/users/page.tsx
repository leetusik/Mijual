import { Door } from "@/components/ops/Door";
import { Users } from "@/components/ops/Users";
import { opsRead } from "@/components/ops/server";
import { getOpsUsers } from "@/lib/api";

/**
 * 사용자 — 독자 계정 and 익명 세션 side by side, with **no join between them**.
 *
 * One response, two independent reads (`/ops/users`), and nothing on the page
 * offers to relate a row on one side to a row on the other: 계정↔대화 연결
 * 컴럼·조인·추정 매칭 금지, kept where it belongs — in the schema.
 */
export default async function OpsUsersPage() {
  const data = await opsRead((init) => getOpsUsers({}, init));
  if (!data) return <Door />;
  return <Users data={data} />;
}
