import { Door } from "@/components/ops/Door";
import { GateQueue } from "@/components/ops/GateQueue";
import type { RowFilterValues } from "@/components/ops/RowInspect";
import { opsRead } from "@/components/ops/server";
import { getOpsGateRows, getOpsGates } from "@/lib/api";

/** 행 검사's page window. A console is one operator deep and the corpus is 710
 * rows, so a page is 50 and the pager is two links. */
const LIMIT = 50;

function one(value: string | string[] | undefined): string | undefined {
  return typeof value === "string" && value !== "" ? value : undefined;
}

/**
 * 게이트 대기열 — reason counts over a served basis, 행 검사, the event-state
 * table, the four blocking flags, the suppression codes and 철회 검사.
 *
 * The filters live in the URL rather than in component state: they are a plain
 * GET form, so the panel is server-rendered, linkable and works with no
 * JavaScript — and an operator can send a colleague the exact row they are
 * looking at.
 */
export default async function OpsGatesPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const filters: RowFilterValues = {
    field_key: one(params.field_key),
    reason_code: one(params.reason_code),
    gate_status: one(params.gate_status),
    rcept_no: one(params.rcept_no),
    limit: LIMIT,
    offset: Math.max(0, Number(one(params.offset) ?? 0) || 0),
  };

  const queue = await opsRead(getOpsGates);
  if (!queue) return <Door />;
  const rows = await opsRead((init) => getOpsGateRows(filters, init));
  if (!rows) return <Door />;

  return <GateQueue queue={queue} rows={rows} filters={filters} />;
}
