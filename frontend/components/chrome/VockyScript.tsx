import Script from "next/script";

/**
 * vocky's script — loaded **once, deferred, in the shell** (R2 §vocky), behind an
 * environment seam.
 *
 * ## Why an env var and not a hard-coded URL
 *
 * vocky is the operator's own feedback service and an **external product**: its
 * script URL appears in no landed record, no grounding file and no doc. Writing
 * one here would be inventing a fact about someone else's system — the same
 * class of mistake as inventing a Korean string — and a wrong URL fails silently
 * (a 404'd script leaves three buttons that do nothing). So the URL is
 * configuration:
 *
 * - `NEXT_PUBLIC_VOCKY_SRC` set → the script is loaded once for every route;
 * - **unset → no script tag at all**, and the three triggers still render. They
 *   are plain elements with `data-vocky-trigger`; with nothing bound they do
 *   nothing, which is the honest state of a chrome whose widget is not wired
 *   yet, and exactly what the round asks the markup to be.
 *
 * The real value is `P5.S18`'s / P4's (`P5.S18` decides vocky's observation API
 * against the live service and the operator holds the credentials).
 *
 * `next/script` in the root layout is Next's documented way to load a
 * third-party script for all routes and is what guarantees the round's "once":
 * "Next.js will ensure the script will only load once, even if a user navigates
 * between multiple routes in the same layout"
 * (`node_modules/next/dist/docs/01-app/02-guides/scripts.md`). The default
 * `afterInteractive` strategy injects it after hydration, i.e. deferred — it
 * never blocks the first paint of a page whose whole point is a 3-second read.
 */
const VOCKY_SRC = process.env.NEXT_PUBLIC_VOCKY_SRC;

export function VockyScript() {
  if (!VOCKY_SRC) return null;
  return <Script src={VOCKY_SRC} strategy="afterInteractive" />;
}
