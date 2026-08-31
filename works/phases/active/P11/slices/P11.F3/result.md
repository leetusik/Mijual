# Result — P11.F3 (Silence the browser-injected hydration warning and check the root layout's cached read)

- **status:** `done`
- **summary:** The operator's single hydration report was two separate faults and both are now closed.
  The warning they saw is **Chrome's own** — `__gchrome_remoteframetoken` written onto `<html>` before
  React hydrates — reproduced byte-for-byte against their diff and silenced by a `suppressHydrationWarning`
  scoped to that one element. Hunting D34 I **cleared the plan's suspect** (the root layout's cached
  contact read: 19,720 documents against an adversarial upstream, across a fetch revalidation *and* an
  ISR revalidation, 0 with a torn HTML/flight pair) and then **found and fixed the real production
  #418(text) somewhere else**: `/_not-found` was statically prerendered while `RequestedPath` renders
  `usePathname()`, so the build baked Next's own literal `/_not-found` into the HTML — readers met a
  wrong address, and React threw #418 and re-rendered the tree. `connection()` makes the page
  request-time; the route is now `ƒ` and the server renders the reader's own path on the first paint.
- **files_changed:**
  - `frontend/app/layout.tsx` — `suppressHydrationWarning` on `<html>`, with the scope/cost recorded
  - `frontend/app/not-found.tsx` — `connection()`, so the page is rendered per request
  - `works/phases/active/P11/phase.md` — notebook edit (compressed from 187/16,395 to **190/16,383**)
- **validation:**
  | command / check | result |
  |---|---|
  | `.venv/bin/python -m pytest` | **pass** — 158 passed |
  | `npm run typecheck` (frontend) | **pass** |
  | `npm run build` (frontend) | **pass** — **19 `ƒ` + 3 icon files; no HTML route prerendered** (§5) |
  | `npm run smoke` (frontend) | **pass** — 22/22 |
  | `python3 scripts/workflow.py validate` | **pass**, and the `phase.md` budget warning is gone |
  | matter 1 reproduced, **dev** 390×844, Chrome attribute injected | **reproduced 2/2**, diff identical to the operator's — §2 |
  | matter 1 after the fix, **dev** 390×844, injected | **pass** — 0/3, page fingerprint unchanged — §2 |
  | scope control A: the same injection on `<body>` instead | **still fires 2/2** — the flag masks nothing below `<html>` — §3 |
  | scope control B: a planted deep text mismatch, dev **and** a rebuilt production | **still throws #418(text) 2/2 and 4/4** — §3 |
  | HTML vs RSC-payload coherence, production, real API | **pass** — 25 documents, 0 incoherent — §6 |
  | adversarial upstream across a **fetch** revalidation (`/`) | **pass** — 3,248 documents, value flipped at 540 s, **0 torn** — §6 |
  | adversarial upstream across an **ISR** revalidation (`/_not-found`) | **pass** — 16,472 documents, entry regenerated at 405 s, **0 torn** — §6 |
  | production sweep **before** the not-found fix, 5 routes, no 404 | 80 loads, 0 — and that is *why* it was missed — §7 |
  | production sweep **with** a 404 route, before the fix | **#418(text) 5/5 on `/nope-404`** — D34 found — §7 |
  | production sweep after the fix, 390 (7 routes incl. all three 404 shapes) | **pass** — 28 loads, 0 — §8 |
  | production sweep after the fix, 1280 (6 routes) | **pass** — 30 loads, 0 — §8 |
  | dev sweep after the fix, 390 (6 routes) and 1280 (3 routes) | **pass** — 24 + 12 loads, 0 — §8 |
  | 404 screen rendered, `127.0.0.1:3010` **and** the tailnet URL | **pass** — R10's three Korean strings, the reader's own path, the footer contact — §8 |
- **instrument:** **not Aside** — `command -v aside` finds nothing, there is no `/Applications` entry
  and no `aside mcp` tool in this session. That is the **sixth** slice to record it. The documented
  fallback applies: the same sweep, at the same viewports, in the runtime `## Operator Runtime` names,
  driven through the real **Google Chrome 152.0.7977.65** on this machine over the DevTools protocol
  from a throwaway node harness (no Playwright), run **headful**. Every number below was read out of
  that live DOM or off the wire. Nothing here is a claimed run I did not make.
- **deviations:** three, all named in §9. (1) The plan's named suspect for matter 2 — the root layout's
  cached contact read — was **exonerated, not fixed**; the evidence is §6. (2) Matter 2 turned out to be
  real but in a different file, so the change list includes `frontend/app/not-found.tsx` as well as
  `layout.tsx` — inside the plan's "whatever matter 2 genuinely requires", and outside every area the
  plan excluded (S1's chip, F1's cards, F2's footer/endpoint). (3) One planned experiment (forcing the
  cached read to expire by deleting the on-disk fetch cache) proved **inconclusive** and was replaced
  by waiting out the real 600 s window; §6 says so rather than quoting its clean result as proof.
- **doc_impact:** three lines appended to `phase.md` `## Doc impact` —
  - `frontend.md`: the root layout's `<html>` carries a **scoped** `suppressHydrationWarning`, why, and
    that it must never be copied down.
  - `frontend.md`: `app/not-found.tsx` is request-time (`connection()`), `/_not-found` is `ƒ`, the route
    table is **19 `ƒ` + three icon files with nothing prerendered** (superseding F2's 「route kinds
    unchanged」), and the durable rule that **no prerenderable tree renders a request-dependent client value**.
  - `qa.md` `## Regression Checklist`: an unknown URL in the **production** build echoes the reader's own
    address, not `/_not-found`, with no React #418.
- **operator_need:** none.
- **for the review:** two notes are waiting in `phase.md` `## Notes for later slices` — re-verify F3 in
  the **production** build (dev shows neither fault), and consider a `defer-job` for the pre-existing
  `__next_error__` behaviour in §8.4. **D34's disposition is not mine to take** (§7.4).

---

## 1. What this slice had to keep apart

The operator accepted everything else at their second gate walk and reported one React hydration
warning on mobile. Two different faults hide behind that one report, and the plan's central instruction
was not to let the cheap one close the real one. They are kept apart throughout, and §3 is the proof
that the fix for the first cannot hide the second.

| | matter 1 | matter 2 (D34) |
|---|---|---|
| signature | **attribute** mismatch on `<html>` | **text** mismatch (#418 `args[]=text`) |
| where | **dev** overlay (`next dev`) | **production** build |
| cause | Chrome, not this product | this product |
| does `suppressHydrationWarning` on `<html>` hide it? | yes — that is the point | **no** — proved in §3 |

## 2. Matter 1 — reproduced, then silenced

Chrome does not inject `__gchrome_remoteframetoken` into a fresh automation profile, so a plain load of
`http://127.0.0.1:3010/` at 390×844 was clean (2/2) and told me nothing. I therefore reproduced the
browser's own behaviour exactly: a document-start script that sets that attribute on `<html>` as soon as
the element exists — before the bundle loads, which is Chrome's timing.

Before the change, dev, 390×844, 2/2 loads:

```
A tree hydrated but some attributes of the server rendered HTML didn't match the client properties.
  …
        <HotReload globalError={[...]} webSocket={WebSocket} staticIndicatorState={{pathname:null, ...}}>
          <AppDevOverlayErrorBoundary globalError={[...]}>
            …
                          <RootLayout>
                            <html
                              lang="ko"
                              className="cosmos notosanskr_d4ff9071-module__8yb5Oq__variable plexmono_735eac66-module__cgj..."
-                             __gchrome_remoteframetoken="369be69d8f14cee0c3da613d5529c729"
                            >
```

That is the operator's report line for line: the same `HotReload` / `AppDevOverlayErrorBoundary` frames,
`lang="ko"` and both font `className` variables carrying **no** diff marker, and exactly one `-` line —
the attribute Chrome added. No server change can prevent it, because no server rendered it.

After adding `suppressHydrationWarning` to `<html>` (`frontend/app/layout.tsx`): **0 of 3** loads, same
conditions. The page is byte-for-byte the same product — the fingerprint before and after is identical:

```
{"title":"주주의관제탑","htmlAttrs":["__gchrome_remoteframetoken","class","lang"],
 "bodyTextLen":1180,"footer":"자료: 금융감독원 DART 전자공시·© 주주의관제탑·leetusik@gmail.com·010-3772-9916 …",
 "nodes":666}
```

The code comment states the scope and the cost, as the plan asked: the flag covers that element's own
attributes and direct text and nothing else, so it also hides a *genuine* `<html>`-level mismatch — the
`lang` or the two font variables — which is acceptable only because all three are literals with no
runtime input. It is not on `<body>`, not on `SiteChrome`, and the comment says why it must not be.

## 3. Proof that matter 1's fix hides nothing (the plan's "confirm you have not masked anything real")

Two controls, both run with the fix in place.

**A — one level down.** The same injection aimed at `<body>` instead of `<html>` still fires, 2/2, and
React's own tree print shows the suppression sitting where it belongs and doing nothing below itself:

```
<html lang="ko" className="cosmos not..." suppressHydrationWarning={true}>
  <head>
  <body
-   __gchrome_remoteframetoken="369be69d8f14cee0c3da613d5529c729"
  >
```

**B — a genuine text mismatch, D34's own signature.** I temporarily rendered `probe-${Math.random()}`
inside `Footer.tsx` (a client component beneath `SiteChrome`, i.e. the exact subtree the plan warned
against blinding). Dev, 2/2:

```
Error: Hydration failed because the server rendered text didn't match the client. …
+                                 probe-0.024372179496842894
-                                 probe-0.7809927037249959
```

and — the control that matters, because production is where D34 lives — the same probe in a **rebuilt
production** build, 4/4:

```
Error: Minified React error #418; visit https://react.dev/errors/418?args[]=text&args[]= …
```

That is the review's recorded string exactly, and it also proves my detector is not blind in a minified
production build; without it, "0 hits in N loads" would have meant nothing. The probe was reverted and
the tree rebuilt clean before anything else was measured (`git status` on `frontend/` shows only the two
intended files).

For the record, React 19.2.8's own source confirms the scoping rather than my inference: in
`react-dom-client.production.js`, both text-hydration paths accept a mismatch when
`props.suppressHydrationWarning === true` on the **host parent of the text node** — which is why a flag
on `<html>` cannot reach a text node inside the footer.

## 4. Matter 2 — where the frontend's non-determinism actually lives

Before testing anything I enumerated every place a client render could disagree with the server:

- `useState` lazy initialisers reading a client-only value: exactly **one**, `Countdown` (`Date.now()`),
  and its three variable text nodes each already carry `suppressHydrationWarning`.
- `OpsClock` (`/ops`) — same pattern, already guarded.
- every `useSyncExternalStore` (`useAsk`, `useAccount`, `lib/sample`) supplies a `getServerSnapshot`, so
  the hydration render matches the server by construction.
- `useReducedMotion` renders `false` on both sides and corrects in an effect.
- `Cosmos` is seeded (`mulberry32`), explicitly never `Math.random`.
- every other `window` / `localStorage` / `matchMedia` read is inside an effect.

So the *component* surface was clean. That left the two data-shaped hypotheses: the plan's (the layout's
cached contact read) and one nobody had named.

## 5. The route table, which reframes the plan's hypothesis

```
ƒ /            ○ /_not-found  10m      ƒ /ask            ƒ /auth/login   ƒ /auth/reset
ƒ /events/[rcept_no]          ƒ /ops…  ƒ /portfolio…     ƒ /stocks       ƒ /stocks/[corp_code]
○ /icon.png    ○ /icon1.png   ○ /apple-icon.png
```

The plan's shape — "a statically rendered route bakes a build-time value into its HTML" — could apply to
**exactly one** HTML route, `/_not-found` (the three `○` icons are image handlers and render no tree).
Every other route carrying the footer is `ƒ`. That single static route turned out to matter enormously,
just not for the contact.

## 6. The plan's suspect is exonerated — 19,720 documents, 0 torn

A hydration **text** mismatch from the contact would require one served document whose SSR HTML says one
thing and whose RSC flight payload — which is what hydration actually consumes — says another. So that is
what I measured: strip every `self.__next_f.push(...)` script out of a document, extract the contact from
the HTML remainder and from the payload, compare.

- **Baseline, real API, production:** 25 documents across `/`, `/ask`, `/stocks`, `/portfolio` and a
  404 — 0 incoherent.
- **The build artifacts:** `.next/server/app/_not-found.html` and `_not-found.rsc` both carry the same
  contact; the prerender writes the pair from one render.
- **Adversarial upstream.** A stub on `:8099` proxied the real API but served `/site/contact` from a file
  I could change; production ran on the manifest origin with `MIJUAL_API_ORIGIN` pointed at it.
  - **Inconclusive attempt, reported as such.** Flipping the value and deleting `.next/cache/fetch-cache`
    between bursts produced 96 coherent documents — but `upstream_reads = 0`, so the in-memory cache had
    served every render and the value never actually changed. That run proves nothing and is not counted.
  - **The real fetch-revalidation boundary (`/`, dynamic).** Value flipped to `beta`, then hammered 8
    concurrent renders at a time until the 600 s window expired: **3,248 documents**, the served value
    flipped `alpha` → `beta` at **540 s**, and requests straddling the flip were still each internally
    coherent. **0 torn.**
  - **The real ISR boundary (`/_not-found`, static).** In parallel: **16,472 documents**, the prerendered
    entry regenerated at **405 s** (build-time contact → runtime contact). **0 torn.**

**19,720 documents in total, across both kinds of revalidation, none mixed.** The mechanism is that
`RootLayout` awaits `getSiteContact` **once** per render and that one value flows into both the HTML and
the serialised props; the fetch-cache entry and the ISR page entry are each replaced atomically. Browser
confirmation of the same thing: loaded against the stub, the footer hydrated to `alpha@example.com` with
no warning, while the not-yet-revalidated static 404 still served the build-time contact — two documents
disagreeing with *each other*, each perfectly agreeing with *itself*, which is what makes it harmless.

**Conclusion: the `revalidate: 600` read `P11.F2` added is not a hydration hazard, and D34 should not be
re-opened against it without new evidence.**

## 7. The real one — found, and it is D34's signature

The 80 production loads I ran first (25 at 390, 25 at 1280, 30 repeats of `/`) were all clean — because
none of those five routes was a 404. Adding one changed everything. A clean-rebuild sweep over
`/`, `/ask`, `/stocks`, `/portfolio`, `/nope-404` at 390×844:

```
....X|....X|....X|....X|....X|
loads=25 loads_with_hydration_messages=5
### round 1 /nope-404
Error: Minified React error #418; visit https://react.dev/errors/418?args[]=text&args[]= …
```

**5 of 5 on `/nope-404`, and only there.** The cause is in the prerendered artifact:

```
.next/server/app/_not-found.html:  <p class="not-found-module__sxuMuG__path">/_not-found</p>
```

`app/RequestedPath.tsx` renders `usePathname()`. Statically prerendered, the only pathname that exists is
Next's own internal segment name, so the build bakes the literal string **`/_not-found`** into the HTML and
into the flight payload. Then, in the browser, `usePathname()` returns the reader's real address, the text
does not match, React throws **#418 (text)** and — as its own message says — regenerates the tree on the
client. It never happened in dev because `next dev` renders the page per request and so never disagrees
with itself.

Two things follow.

1. It is a **visible product defect**, not only a console error: on the one screen whose entire job is to
   echo the address the reader supplied (R10 §8: "it echoes the address and nothing else about it"), every
   production reader was first shown `/_not-found` — a Next internal name, and the only non-address string
   that box could possibly contain.
2. It is **D34's signature**, precisely: `#418`, `args[]=text`, production only, invisible when routes are
   loaded one at a time unless the 404 is one of them. The review saw theirs "once in roughly 20 production
   loads during a multi-route sweep" and could not reproduce it in 11 isolated loads.

**What I can and cannot conclude.** I can conclude that a reproducible production #418(text) with D34's
exact signature existed on this route, that its cause is understood, and that it is now fixed. I **cannot**
prove that the single occurrence the review logged was this one — nobody recorded which URL was in flight.
It fits (a sweep that touches a 404 once in ~20 loads; nothing reproducing in isolation), but "it fits" is
not "it is". So **I have not closed D34 and I have not run any deferred-job command**; whether to
`drop-deferred` it or leave it open for a third sighting is the orchestrator's call, and the phase notebook
says so.

## 8. The fix, and the verification

`app/not-found.tsx` now `await connection()`s, exactly as `app/ask/page.tsx` does for its start cards
(`P11.F1`'s precedent). This is not symptom suppression: `suppressHydrationWarning` on the path element
would have *kept the server's wrong string on screen*, since React does not patch suppressed text. Stating
that the page depends on the request is the truth, and it makes the server render the reader's own path on
the first paint — no mismatch to hide, no element appearing a beat late, no layout shift on a `<p>` that
carries a `--surface-inset` background.

- `/_not-found` is now **`ƒ`**. The route table is **19 `ƒ` + the three icon files, nothing prerendered**,
  which supersedes `P11.F2`'s "route kinds unchanged" note and, incidentally, removes the last place the
  contact could be baked at build time.
- SSR echo, straight off the wire: `/nope-404` → `/nope-404`; a deep path → `/nope-404/some/deep/path`.
- **Production**, Chrome attribute injected: 28 loads at 390 over 7 routes including **all three 404
  shapes**, 0 hydration messages; 30 loads at 1280 over 6 routes, 0. Coherence re-checked: 20 documents,
  0 incoherent.
- **Dev** (`make stack-up`, the manifest runtime): 24 loads at 390 over 6 routes, 0; 12 at 1280, 0.
- The 404 screen itself, read out of the live DOM at 390×844 on **both** access paths the manifest names —
  `http://127.0.0.1:3010` and the tailnet `http://100.77.164.42:3010`:
  R10's three Korean strings, the reader's own path in the mono box, and the footer contact. 0 hydration
  messages on either.
- **8.4 — one pre-existing behaviour I found and deliberately did not touch.** A `notFound()` thrown by a
  *dynamic* segment (`/events/<unknown>`, `/stocks/<unknown>`) does not render this page server-side at
  all: Next returns `<html id="__next_error__">` with no SSR content and the whole 404 screen is drawn on
  the client. There is no hydration, so there is no #418 and it is not part of D34 — but those two 404s
  have an empty first paint. It predates P11, it is outside this slice's scope, and it is left alone; the
  notebook flags it for the review as a possible `defer-job`.

## 9. Scope and deviations

The plan scoped this to `frontend/app/layout.tsx` "and whatever matter 2 genuinely requires if it turns
out to be real", excluding S1's citation chip, F1's start cards and F2's footer content and contact
endpoint. Matter 2 was real, and what it required was `frontend/app/not-found.tsx` — none of the excluded
areas, and nothing in the footer's behaviour or the contact's content was widened or revisited. Two source
files changed in total.

The plan's named suspect was cleared rather than fixed (§6), and one planned experiment was inconclusive
and is reported as inconclusive rather than counted (§6).

No workflow state-transition command was run, nothing was committed, and no deferred job was filed or
dropped. The throwaway probe in `Footer.tsx` was reverted and rebuilt away before any measurement that is
quoted here. The CDP harness, the stub upstream and the parked build caches live in the session scratchpad,
outside the repo; the stub, the temporary production servers and every Chrome instance are stopped, and the
dev stack is back exactly as it was found (`make stack-status`: postgres up, api pid on `:8010`, web on
`:3010`, tailnet `100.77.164.42:3010`). `frontend/next-env.d.ts`, which Next rewrites between `dev` and
`build`, was restored to its committed state.
