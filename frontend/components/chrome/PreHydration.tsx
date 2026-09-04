/**
 * The **pre-hydration mirror** — the browser's own storage facts, on `<html>`,
 * before the affected content paints (`P12.F3`).
 *
 * ## The problem this exists to solve
 *
 * Family A of `P12.R1`'s flicker hunt is one defect repeated: content whose
 * existence **only the browser** knows — a `localStorage` sample, a
 * `sessionStorage` flag, a one-time flash — is rendered in a mount effect, so it
 * lands *after* first paint and shoves painted content down (the worst of them,
 * `/portfolio`'s 계정 이전 band, pushed the whole surface **215.28 px**).
 *
 * The server cannot be told: `docs/current/security.md` — 「Anonymous state never
 * reaches the server, and that is now structural: there is no anonymous write
 * endpoint at all」. A cookie mirroring 조회's holdings, the sample's edits or the
 * offer-declined flags would send exactly that state to the server on every
 * request, so **there is no cookie here and there must not be one**. What can be
 * done instead is to let the **browser** read its own storage before it paints,
 * and let CSS reserve or hide from what it read.
 *
 * ## The contract
 *
 * A tiny inline script — parser-blocking, in `<head>` for the facts a page does
 * not have to supply, or beside the element for the facts that need the page's
 * own server-rendered data — reads **named keys only**, in `try/catch`, and
 * stamps what it learned onto `<html>` as `data-mj-*` attributes. It **writes
 * nothing to storage, sends nothing, loads nothing** (the edge CSP is
 * `upgrade-insecure-requests` only and this product has a measured
 * no-third-party-origin property, so an inline script costs neither).
 *
 * `<html>` is the one element whose attribute mismatches React already ignores
 * (`app/layout.tsx`'s `suppressHydrationWarning`, `P11.F3`), so a stamp never
 * produces a hydration warning. Everything below `<html>` still reports normally.
 *
 * Then, in order:
 *
 * 1. **CSS reserves or hides from the attribute**, in the state where the band
 *    will exist, and does **nothing** otherwise — the resting layout with no band
 *    stays pixel-identical.
 * 2. **React's first client render matches the server markup** — the mirror is
 *    read by *CSS*, never by a component, so no component renders differently on
 *    the client than it did on the server.
 * 3. **The effects reconcile after hydration**: the band that used to be
 *    *inserted* is now only *filled* (into a slot already the right size) or
 *    *removed* (a `display: none` element leaves without moving anything).
 *
 * ## The attributes, and who owns each
 *
 * | Attribute | Source key | Meaning |
 * |---|---|---|
 * | `data-mj-offer-seen` | `sessionStorage["mijual.convert.offer"]` | 전환 제안 has already been shown this session, so the server-rendered band must not paint (`P12.F3`, `components/auth/ConversionOffer.tsx`) |
 * | `data-mj-carry-rows` / `data-mj-carry-kind` (+ the `--mj-carry-rows` custom property) | `localStorage["mijual.portfolio.sample"]`, `sessionStorage["mijual.portfolio.migrate"]` / `["mijual.portfolio.carry"]` / `["mijual.lookup.holdings"]` | how many rows the 계정 이전 · 세션 이월 band will have, so its slot can be sized before it exists (`P12.F3`, page-level — it needs `/portfolio`'s own served composition beside it) |
 * | `data-mj-lookup-holding` | `sessionStorage["mijual.lookup.holdings"]` | this browser remembers a count for **this** stock, so ①'s 환산 row will draw its four-cell shape and its foot will lose the prompt — `Lookup.module.css` holds both at that geometry until the effect fills them (`P12.F4`, page-level: the memory is per issuer, so the script needs the page's own `corp_code`). Presence only; the count itself is never stamped, because no rule reads it |
 * | `data-mj-sample-removed` | `localStorage["mijual.portfolio.sample"]` | the `corp_code`s this browser removed from its 샘플, space-separated, so the anonymous 보유 종목 surface can hide them **before first paint** (`P12.F10`). The server renders the composition it serves and only the browser knows which issuers the reader dropped, so the rows are hidden by CSS until React owns the list: `components/portfolio/SampleRules.tsx` emits one static rule per **served** code (`~=` matches one word of the attribute), the rows carry `data-corp`, and `Portfolio` releases the stamp once `useSample()` has answered — a 되돌리기 must be able to bring a row back. Digit strings only (a code that is not one is not stamped and not ruled: it simply behaves as it does today) |
 *
 * **Adding one** (`P12.F5`'s 로그아웃 flash): read
 * the key here if the fact is page-independent, or with {@link InlineScript} beside
 * the element if the computation needs the page's server data; name the attribute
 * `data-mj-<thing>`; put the CSS that reads it in the component's own module; add a
 * row to the table above.
 *
 * **One development-only wrinkle, and it costs nothing here.** React's Strict Mode
 * remounts once in `next dev` and, on that remount, resets `<html>`, `<head>` and
 * `<body>` to the attributes it manages from JSX — so a stamp disappears at
 * hydration in dev (Next's *Preventing flash before hydration* guide says so
 * outright). Every attribute in the table above is a **pre-hydration** device
 * whose job is finished by then, and the component that owns it has taken over,
 * so nothing re-applies it. A future attribute that must outlive hydration would
 * have to (that guide's `useLayoutEffect` re-apply) — none does today.
 *
 * A stamped attribute lives as long as the document. When the fact it mirrors can
 * change **after** hydration — as a reserved slot's does the moment the reader
 * dismisses the band — the owning component releases it with {@link clearMirror}
 * once its own state is settled, and the reservation is then a pre-hydration
 * device only (exactly like `P12.F2`'s ≤767 launcher guard).
 */

/** The one key 전환 제안 asks about; the writer is `ConversionOffer.tsx`'s
 * `markSeen()`, which still writes it at the same moment it always did. */
const OFFER_SEEN_KEY = "mijual.convert.offer";

/** 샘플 포트폴리오's store — `lib/sample.ts`'s `SAMPLE_KEY`, spelled again here
 * because that module is a client module and this one runs in the root layout's
 * server render. The two spellings are one string and must stay one. */
const SAMPLE_KEY = "mijual.portfolio.sample";

/** The attribute the sample's removals are stamped as (`P12.F10`), named once so
 * the head script and `components/portfolio/SampleRules.tsx`'s generated rules
 * cannot drift apart. */
export const SAMPLE_REMOVED_ATTR = "data-mj-sample-removed";

/**
 * The `<head>` half of the mirror: the facts that need nothing from the page.
 *
 * Rendered **first** in `app/layout.tsx`'s `<head>`, so it runs before the body is
 * parsed and long before first paint. Two `getItem`s inside one `try`, in that
 * order: a denied storage or an unparseable sample costs the reader nothing that
 * was already stamped.
 *
 * The sample's `removed` list is stamped as **space-separated digit strings**, so
 * a static `[data-mj-sample-removed~="00102618"]` rule can match one entry of it.
 * Anything that is not a digit string is dropped rather than stamped: the value
 * is interpolated into a CSS selector on the other side of this seam, and a code
 * that cannot be one simply keeps today's behaviour (its row drops at hydration).
 */
const HEAD_SOURCE =
  `(function(){try{var h=document.documentElement;` +
  `if(sessionStorage.getItem(${JSON.stringify(OFFER_SEEN_KEY)})!==null){` +
  `h.setAttribute("data-mj-offer-seen","")}` +
  `var raw=localStorage.getItem(${JSON.stringify(SAMPLE_KEY)});if(!raw)return;` +
  `var st=JSON.parse(raw),rm=st&&Array.isArray(st.removed)?st.removed.filter(` +
  `function(c){return typeof c==="string"&&/^[0-9]+$/.test(c)}):[];` +
  `if(rm.length){h.setAttribute(${JSON.stringify(SAMPLE_REMOVED_ATTR)},rm.join(" "))}` +
  `}catch(e){}})();`;

export function PreHydrationMirror() {
  return <script dangerouslySetInnerHTML={{ __html: HEAD_SOURCE }} />;
}

/**
 * A page-level parser-blocking inline script, for a fact whose computation needs
 * the page's own server-rendered data (`/portfolio`'s served sample composition,
 * say). Render it **immediately after** the element it sizes, so it runs before
 * the content below that element is parsed.
 *
 * `code` is authored by the caller and inlined verbatim; anything server-supplied
 * inside it goes through {@link jsonLiteral}, never string concatenation.
 *
 * On a **client navigation** this element is created by React rather than by the
 * parser, so it does not execute — which is correct and not a gap: there is no
 * pre-hydration window on a client navigation, the component renders its real
 * state in one commit, and the reservation would have nothing to reserve.
 */
export function InlineScript({ code }: { code: string }) {
  // `type` is the framework's own idiom for exactly this element (Next's
  // *Preventing flash before hydration* guide, `01-app/02-guides/`): the server
  // emits an executable script the parser runs, the client renders it inert, and
  // `suppressHydrationWarning` — scoped to this one element — accepts the DOM's
  // `type` over the client's. It also silences React's development warning about
  // rendering `<script>`, and it makes the client-navigation no-op explicit
  // rather than incidental.
  return (
    <script
      type={typeof window === "undefined" ? "text/javascript" : "text/plain"}
      suppressHydrationWarning
      dangerouslySetInnerHTML={{ __html: code }}
    />
  );
}

/** Server data, safe to embed in an inline `<script>`: JSON with `<` escaped, so
 * no value can close the element early. */
export function jsonLiteral(value: unknown): string {
  return JSON.stringify(value).replace(/</g, "\\u003c");
}

/**
 * Drop a stamp once the component that owns it has its own answer — after which
 * the CSS keyed on it must no longer apply (a reservation left standing would
 * become a permanent gap the moment the reader dismisses the band it reserved).
 *
 * Client-only, idempotent, and safe on `<html>` for the same reason the stamping
 * is: React does not manage that element's attributes after the initial render,
 * and its mismatches are suppressed anyway.
 */
export function clearMirror(...attributes: readonly string[]): void {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  for (const name of attributes) {
    root.removeAttribute(`data-mj-${name}`);
    root.style.removeProperty(`--mj-${name}`);
  }
}
