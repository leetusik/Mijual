import { Accuracy } from "@/components/ops/Accuracy";
import { Door } from "@/components/ops/Door";
import { opsRead } from "@/components/ops/server";
import { getOpsAccuracy } from "@/lib/api";

/**
 * 정확도·비용 — the evalset report from its frozen artifacts, and the spend.
 *
 * The judged-by block renders above the numbers and the headline does not render
 * without it (R7's hard rule), every rate carries its decomposition in the same
 * panel, and `mijual.evalset report`'s own markdown sits at the foot so the tab
 * can never quote a number the command does not print.
 */
export default async function OpsAccuracyPage() {
  const data = await opsRead(getOpsAccuracy);
  if (!data) return <Door />;
  return <Accuracy data={data} />;
}
