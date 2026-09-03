"use client";

import { usePathname } from "next/navigation";
import { ROUTES, isActiveRoute } from "@/lib/routes";
import { AskLauncher } from "./AskLauncher";
import { AskWidget } from "./AskWidget";
import { useAskState, useAskStore, useDesktop } from "./useAsk";

/**
 * Where the launcher and the widget are allowed to exist.
 *
 * Three rules, all signed, all enforced here so no component has to remember one:
 *
 * - **≤767px: nothing.** 「위젯·런처 없음 — AI 질문 = 전폭 페이지 하나」 (R6
 *   §Surfaces / §Mobile, **at R14 Q-A's 767 line** — the round moved R6's own
 *   narrower boundary onto the product's single one, and on this surface that
 *   line decides existence rather than layout). **After hydration: not rendered**,
 *   exactly as it always was — `useDesktop`'s effect answers `false` at ≤767 and
 *   this component returns `null`, so there is no launcher to tab to and none to
 *   open a widget with. **Before hydration: not painted**, by
 *   `Launcher.module.css`'s `@media (max-width: 767px) { .launcher { display: none } }`.
 *   That second half is `P12.F2`: this component now asks for `useDesktop(true)`
 *   so the server can put the launcher in the first painted HTML for the desktop
 *   readers who get one — it used to be inserted 44–288 ms *after* first paint on
 *   every desktop load (`P12.R1` F1) — and the CSS rule covers the ~100 ms before
 *   React runs. The original argument for keeping the rule out of a media query
 *   was that "a launcher merely not *painted* at 600px would still be in the tab
 *   order and would still open a widget"; a `display: none` element is in **no**
 *   tab order and cannot be clicked or activated, so it holds for that window too,
 *   and the end state the rule describes is still a render decision made here.
 * - **`/ask`: no launcher.** 「페이지에는 런처 렌더 금지 (중복 표면 금지)」. The
 *   page is the other view of the same thread, and `P6.S6` builds it.
 * - **운영 관제: nothing.** `SiteChrome` renders the ops tree without any reader
 *   chrome at all, so this component is never mounted there.
 *
 * The corner itself was left clear on purpose (`SiteChrome`: "nothing here is
 * `position: fixed` and nothing occupies a corner … P6's AI 질문 launcher lands in
 * the bottom-right"), so 「런처·위젯은 vocky 트리거와 모서리 충돌 금지」 holds
 * without moving anything — and since **R8 deleted every `data-vocky-trigger`
 * element** (`components/chrome/index.ts`) there is no chrome corner element left
 * to collide with at all.
 */
export function AskSurface() {
  const pathname = usePathname() ?? "";
  // `true`: the server and the hydrating client both render the launcher, and the
  // media-query effect then unmounts it at ≤767 (guarded until then by the CSS
  // rule above). `QuestionStrip`'s bare `useDesktop()` keeps the `false` default.
  const desktop = useDesktop(true);
  const store = useAskStore();
  const state = useAskState();

  if (!desktop) return null;
  if (isActiveRoute(pathname, ROUTES.ask)) return null;

  return (
    <>
      <AskLauncher open={state.open} onOpen={store.open} />
      {state.open ? <AskWidget /> : null}
    </>
  );
}
