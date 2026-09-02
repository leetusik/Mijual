import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Door } from "@/components/ops/Door";
import { OpsChrome } from "@/components/ops/OpsChrome";
import { opsAuthenticated, opsHeaders } from "@/components/ops/server";
import { getOpsLock } from "@/lib/api";

/**
 * 운영 관제 (R7) — the layout every section sits inside, and the door in front
 * of it.
 *
 * ## The door renders **in place**, and that is the whole tab-restore mechanism
 *
 * R7: "세션 만료 → 문으로 복귀, 로그인 후 있던 탭 복원." This layout probes
 * `GET /ops/session` and, when there is no operator session, renders the Access
 * card *at the URL that was asked for* — no redirect, no `?next=`, nothing
 * stored. `/ops/accuracy` shows the door on `/ops/accuracy`, and the
 * `router.refresh()` after a successful login re-runs this same route with the
 * new cookie. The path never moved, so there is nothing to restore.
 *
 * It also means the tab's own component **never runs** while the panel is
 * locked: `children` is an element, so a layout that does not render it never
 * executes the page, and no ops read is attempted without a session.
 *
 * ## No reader chrome, in either direction
 *
 * `SiteChrome` renders nothing under `/ops` (R7: reader chrome 어디에서도 링크
 * 금지), so the pre-auth surface is the empty page with one door the round draws,
 * and the authenticated surface carries the **ops** chrome instead. Nothing here
 * links back to a reader surface either.
 */
export const metadata: Metadata = {
  // 운영자 전용: the panel says what it is, and the reader product's own title
  // does not belong on it. P10 retired the latin mark — same shape, the product
  // name plus 운영, matching `OPS_MARK`.
  //
  // **`absolute`, and that is not a style choice.** `P4.S5` gave the root layout
  // a `title.template` of `%s | 주주의관제탑`, which applies to every child
  // segment — this one included. Left as a plain string the panel would title
  // itself 「주주의관제탑 운영 | 주주의관제탑」. `absolute` opts out of the
  // template and keeps the string exactly as it was written.
  title: { absolute: "주주의관제탑 운영" },
  // **`noindex, nofollow`.** R7's first rule for this surface is that the reader
  // chrome links it from nowhere — 「nav·푸터·계정 메뉴·sitemap」 — and a search
  // result is the one link that rule cannot forbid structurally. `app/robots.ts`
  // disallows `/ops` as well; the two controls do different jobs, because a
  // crawler that never fetches the page never reads this tag, and a URL already
  // in an index is dropped by this tag and not by the disallow.
  robots: { index: false, follow: false },
};

export default async function OpsLayout({ children }: { children: ReactNode }) {
  if (!(await opsAuthenticated())) return <Door />;

  // The bar's chip starts from a server read and polls `/ops/lock` from there;
  // its `as_of` is the instant this page's chrome was served.
  const lock = await getOpsLock({ headers: await opsHeaders() }).catch(() => null);

  return (
    <OpsChrome lock={lock} asOf={lock?.as_of}>
      {children}
    </OpsChrome>
  );
}
