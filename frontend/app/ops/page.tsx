import { Door } from "@/components/ops/Door";
import { Overview } from "@/components/ops/Overview";
import { opsRead } from "@/components/ops/server";
import { getOpsOverview } from "@/lib/api";

/**
 * 개요 — 「완전한 페이지」 #1 of six (R7 forbids 컴포넌트 단편 화면).
 *
 * One read: `GET /ops/overview` carries the four `gates summary` tiles, the beat
 * declaration with every instant each entry was due, the run log, the lock and
 * the decisions document's still-open items. The 「실행 기록 없음」 row is the
 * client's join of the first two — the backend states both facts and mints no
 * row for a gap.
 */
export default async function OpsOverviewPage() {
  const data = await opsRead(getOpsOverview);
  // The session expired between the layout's probe and this read; the door is
  // the honest surface, and this URL is the tab it comes back to.
  if (!data) return <Door />;
  return <Overview data={data} />;
}
