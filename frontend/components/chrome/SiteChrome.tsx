"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { AskProvider, AskSurface } from "@/components/ask";
import { isOpsPath } from "@/components/ops/routes";
import type { AuthState, SiteContact } from "@/lib/types";
import { SiteFooter } from "./Footer";
import { SiteNav } from "./Nav";
import { InitialAccountContext } from "./useAccount";
import styles from "./SiteChrome.module.css";

/**
 * The chrome every **reader** page sits inside — nav, page, footer.
 *
 * R2 designs the landing *and* "the **global chrome** every later surface lives
 * in (nav, footer, mobile navigation, page shell)", so this is a layout
 * component the root layout wraps every route in: one nav and one footer, no
 * matter how many routes a reader walks through. A page renders its own
 * `<main>` — the chrome does not wrap the content in an element that would
 * compete with a surface's own composition.
 *
 * **R8 removed the third thing that used to live here**, vocky's `<Script>` seam:
 * the 의견 보내기 surface is 미주알's own and is mounted by its two entry points
 * (the footer button, the mobile sheet row), so no external script is loaded on
 * any route and no `data-vocky-trigger` element exists.
 *
 * What it deliberately does not do: nothing here is `position: fixed` and
 * nothing occupies a corner. R2's §6-4 decision is "chrome-level but not
 * floating … No floating corner button", and P6's AI 질문 launcher lands in the
 * bottom-right ("런처·위젯은 vocky 트리거와 모서리 충돌 금지") — that corner is
 * left clear. **`P6.S5` took it**: `AskSurface` is the only fixed pair in the
 * reader chrome, and it renders nothing at ≤480px, nothing on `/ask` and nothing
 * under `/ops`.
 *
 * ## Why the ask store is provided here (`P6.S5`)
 *
 * R6 requires a conversation that keeps streaming while the reader moves between
 * the widget and `/ask` (「스트리밍 중 이동/전환에도 끊김 없음」). The root layout
 * persists across navigation and this component is its client half, so
 * `AskProvider` wraps the whole reader tree from one place — the widget here and
 * `P6.S6`'s page inside `children` are two views over one thread. It holds no
 * state of its own (the store is module-scoped in `lib/ask.ts`), so a frame
 * arriving mid-stream re-renders the views and never the pages.
 *
 * ## 운영 관제 gets none of it (`P5.S17`)
 *
 * R7's admin surface is "**reader chrome 어디에서도 링크 금지**" and its own
 * pages carry the **ops** chrome instead (the pre-auth door carries no chrome at
 * all: 빈 페이지 가운데 문 하나). So under `/ops` this component renders its
 * children and nothing else — no nav, no footer, and no reader link anywhere in
 * the markup.
 *
 * ## Why the contact arrives as a prop (`P11.F2`)
 *
 * Being a client component has one cost: nothing below it can read the API on the
 * server. The footer publishes the 운영자 연락처 on every page, so the root layout
 * — the nearest server component — reads it and passes it through here. It is
 * plain serializable data (three strings or nulls) and this component does
 * nothing with it but hand it to the footer; `/ops` renders no footer and
 * therefore never publishes it.
 *
 * That decision has to be made where the path is known, which is why this is a
 * client component: a root layout cannot read the pathname, and the alternative
 * — moving every reader route into a route group with its own layout — would
 * have changed which layout the framework's own 404 renders inside, a surface
 * `P5.S13` already verified. The children are server-rendered and passed in as a
 * prop, so nothing about the pages themselves moves to the client.
 *
 * ## And why the session arrives the same way (`P12.F1`)
 *
 * `initialAccount` is the second value with that shape, and for the same reason:
 * the account slot is client code two levels down inside the nav, so the session
 * it renders can only be resolved by a server component above it — this layout's
 * `RootLayout`, which reads it from the request's own cookie. It is provided here
 * through `InitialAccountContext` rather than threaded as a prop because neither
 * `SiteNav` nor the mobile sheet has any use for the value; only
 * `useAccount()` reads it, and it reads it to render the 로그인 link or the account
 * frame **in the first painted HTML** instead of inserting it 45–293 ms later
 * (`P12.R1` F1). The seam — and the rule that the server never writes the module
 * store — is documented in `useAccount.ts`.
 *
 * `/ops` provides nothing, so the hook there sees `null` and probes exactly as it
 * always has.
 */
export function SiteChrome({
  children,
  contact = null,
  initialAccount = null,
}: {
  children: ReactNode;
  contact?: SiteContact | null;
  /** The session as the **server** resolved it for this request (`P12.F1`), or
   * `null` when no host resolved one — in which case `useAccount()` probes from
   * the browser exactly as it always has. */
  initialAccount?: AuthState | null;
}) {
  const pathname = usePathname();
  if (isOpsPath(pathname ?? "")) return <>{children}</>;

  return (
    <InitialAccountContext value={initialAccount}>
      <AskProvider>
        <div className={styles.frame}>
          <SiteNav />
          <div className={styles.page}>{children}</div>
          <SiteFooter contact={contact} />
          <AskSurface />
        </div>
      </AskProvider>
    </InitialAccountContext>
  );
}
