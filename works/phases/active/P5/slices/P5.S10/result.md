# Result — P5.S10: Next.js foundation

**Status: `needs_operator`.** Everything in the plan is built, validated and landed. The
one item that cannot be finished here is deliverable 6: the binary design assets are
**not in this repository** (re-verified: nothing matching `*wordmark*`, `*ring*.png`,
`*Pretendard*` or `*.woff2` exists anywhere in the checkout outside `.venv`/`.git`). The
paths are wired, the directory and its README exist, and nothing was substituted,
generated or placeheld. The export list is at the bottom of this file.

## What exists now

`frontend/` — a Next.js **16.3.2** app (App Router, Turbopack) on React **19.2.8** and
TypeScript **5.9.3**, and *nothing else*: no UI library, no CSS framework, no test
framework, no linter config. 30 npm packages, 0 vulnerabilities.

```
frontend/
  package.json  tsconfig.json  next.config.ts  README.md
  app/      layout.tsx · shell.css · page.tsx + page.module.css (the proof page)
  components/  CraftPanel · EstimateMarker · Citation · StateBadge · DDay ·
               RightsChip · LapseAlert   (+ .module.css each, + index.ts)
  lib/      api.ts · types.ts · copy.ts · motion.ts · api.test.ts
  public/foundations/  tokens.css · fonts.css   (VENDORED VERBATIM)
  public/assets/       README.md + fonts/.gitkeep   (the missing binaries' slots)
```

Also touched: `.gitignore` (`*.tsbuildinfo`; `node_modules/` and `.next/` were already
covered and were confirmed to match at this depth) and `compose.yaml`'s header comment,
which now documents `npm run dev` beside the uvicorn line exactly as `P5.S1` documented
that one.

## The decisions, and why

### 1. The API seam: same origin, therefore **no CORS at all**

`P5.S1` note 7 left "the CORS/origin question" to this slice. The answer is that the
question does not arise. Every call goes to `/api/…` on the app's own origin and
`next.config.ts` rewrites it to `MIJUAL_API_ORIGIN` (default `http://localhost:8000`).
Consequences worth stating, because a later slice must not "fix" this by adding CORS:

- The FastAPI service still configures **no CORS middleware and grants no preflight** —
  which is precisely what `P5.S7` note 4's CSRF design rests on ("a cross-origin page
  cannot set `X-Mijual-CSRF` without a CORS preflight this service does not grant").
  Adding CORS to save a proxy line would weaken a landed security decision.
- `mj_session` (`HttpOnly` · `SameSite=Lax` · `Path=/`) arrives through a same-origin
  response, so it is stored for the app's origin and returned on every `/api/…` call —
  with no `SameSite=None` and no `Secure`-on-http trap (`P5.S7` note 2).

Verified live: `curl localhost:3000/api/health` returned the identical body to
`curl localhost:8000/health`, including the same `now_kst`.

The rewrite is not dev-only — it is the same seam in `next start`, and P4 repoints it
with an environment variable rather than a code change.

### 2. The foundations are **served**, not bundled — and needed no path edit

`tokens.css` and `fonts.css` are byte-identical to the landed records (diffed; only a
provenance header was prepended, which the plan asks for). They sit at
`public/foundations/` with the assets at `public/assets/`, mirroring the design project's
own `foundations/` + `assets/` layout — so `fonts.css`'s `url("../assets/fonts/PretendardVariable.woff2")`
resolves as `/assets/fonts/PretendardVariable.woff2` **with the relative path completely
unchanged**. That is the whole path "mapping" the plan asked to record: there isn't one.

Serving rather than importing is also what keeps the build honest while the binary is
missing: a bundled `url()` pointing at a non-existent file fails the build outright,
whereas a served one 404s and `font-display: swap` falls through Pretendard's own stack.

### 3. One apply-time to-do against a landed nit (record untouched)

The landed `fonts.css` places `@import url(…IBM+Plex+Mono…)` **after** its `@font-face`
block. A CSS `@import` that does not precede every other rule is invalid and is dropped
by every browser — so the mono face the design puts on **every numeral** would silently
never load. The record is read-only, so the file is vendored exactly as it landed and the
same URL is linked from `app/layout.tsx` instead: the round's own mechanism (Google Fonts
CDN), in a position where it applies. Confirmed in the served HTML.

### 4. Two readings of the record that could have gone the other way

Both are recorded here and in `phase.md` so `P5.S19` can check them against the actual
cards, which live in the Claude Design project and are not readable from here.

**(a) The 「추정」 tag renders the two characters `추정`, not `「추정」`.** The 「」 are the
design documents' own quoting notation — the same brackets wrap 「예정」, 「진행 중」,
「실행 기록 없음」 and whole sentences such as 「자격증명이 올바르지 않습니다」 elsewhere
in the same files, none of which can literally contain them. The mark is specified as a
*bordered* tag, so the border is the enclosure; `[근거]`, by contrast, is written in
square brackets every time and has only a dotted underline, so **its** brackets are part
of the string and are rendered. (R2's footer provenance sentence writes the mark as
`[추정]` *inside prose* — that is a locked sentence describing the mark, and it is
`P5.S11`'s to render verbatim; it does not respell the tag.)

**(b) A past `D+n` renders faint, never in alert ink.** R1's ladder stops at the filled
D-DAY badge and only says "D+N stays unfilled". Three later rounds settle the colour
explicitly and consistently: R3 "Past deadline = **faint D+**, '기한 지남' — never
종료-colored", R4 "faint chip `기간 지남 · D+{n}` (history styling)", R5
"지나간 행 … **alert 색 금지**". So `DDay` maps `days < 0` to `--urgency-far`. This also
protects `ui-traps` #5: an ② whose window is open right now is 진행 중, and painting its
D+46 in the expiring/lost hue would say the opposite of what the round means.

### 5. Sizing: `0.56em`, which *is* R2's 10px

R2 specifies the estimate tag at 10px on the landing; R3's system-wide re-cut specifies
0.56em of context. They agree — 0.56 × ~17.9px = 10px — and the em form is the one that
honours R1's law that the component never sets its own size. Implemented as `0.56em`.

### 6. The reduced-motion convention later slices inherit

`shell.css` handles the CSS half and fixes two data attributes so nobody invents a second
convention: `data-motion="tick"` freezes (colon blink, twinkle, orbit) and
`data-motion="ambient"` hides (shooting stars); everything else is a fade and a fade
becomes a cut. `lib/motion.ts`'s `useReducedMotion()` is the JS half — R2's countdown
requires "no animation, **static value**", which means the interval must not run, and CSS
cannot stop a `setInterval`.

### 7. What the shell deliberately does **not** do

No page surfaces, no nav, no footer, no starfield. `body` carries no `overflow`,
`transform`, `filter` or `contain`, because any of them would turn `position: fixed` into
a containing-block position and break the one continuous cosmos R2 requires; `.backdrop`
in `shell.css` is the slot `P5.S12` fills. `CraftPanel` has **no ornament-free variant**:
R7's ops panel strips exactly what this component adds, so it is a different panel and
`P5.S17`'s, not a mode of this one.

### 8. The typed client

`lib/api.ts` hard-codes every route path (`P5.S3`'s note), sets `credentials: "include"`
on everything and `X-Mijual-CSRF` on every unsafe method in the wrapper so no call site
can forget, and turns the envelope into an `ApiError` carrying `code` / `message_ko` /
`fields` — with `message` documented as developer-facing and never renderable.
`lib/types.ts` encodes the contract's three serialization rules structurally: optional
(`?:`) for an absent key, `| null` **only** where the server genuinely emits null
(`countdown.date`/`dday`/`days`, `corp_name`, `rcept_no`, `freshness.as_of`, a version
row's `rcept_dt`/`correction_kind`), decimal strings typed as `string`, and `estimated`
required on every `Figure`. `EstimateMarker` takes a required `estimated` with a runtime
guard, so an untagged estimate is unrenderable on this side of the wire the same way it is
unconstructable on the server's.

Server components get a working client too: with a relative base and no `window`, requests
go straight to `MIJUAL_API_ORIGIN` rather than through the proxy. A gated read from a
server component must forward the incoming `cookie` header itself — noted in the module.

## Validation

| command | result |
|---|---|
| `cd frontend && npm run build` | **pass** — compiled in ~1 s, 3 static pages prerendered (`/`, `/_not-found`) |
| `cd frontend && npm run typecheck` (`tsc --noEmit`) | **pass**, no output |
| `cd frontend && npm run smoke` (`node --test lib/*.test.ts`) | **pass** — 3/3 in 75 ms |
| dev server + curl | **pass** — `npm run dev`, then `GET /` → 200, 19,552 b; `GET /api/health` → identical body to the API's own `/health`. Both servers stopped afterwards. |
| `.venv/bin/python -m pytest` | **113 passed**, 2.64 s — the baseline, untouched (no Python file was edited) |
| `python3 scripts/workflow.py validate` | **Workflow validation passed.** |

The served HTML was inspected rather than assumed. It carries
`<html lang="ko" class="cosmos">`, the three stylesheet links in `<head>` (with preloads),
`<title>미주알</title>`, and every primitive rendered: the 추정 tag present on the estimate
and **absent** on the fact, `D-5`/`D-DAY`/`D+41` in the soon/now/**past** inks, 추후결정 and
발행사 기재 불일치 chips, the `[근거]` button with `aria-expanded="false"` over an `inert`
panel holding the verbatim quote and the DART link, four corner brackets on each craft
panel, and the 소멸주의보 placard in its craft/hazard form.

The smoke check is deliberately two halves and no framework: `next build` prerenders
`app/page.tsx` through the shell and every primitive (so a broken component fails the
build), and `node --test` covers the one piece with logic that a render cannot show — the
CSRF header on a mutation and not on a read, `credentials: include`, and the error envelope
becoming an `ApiError`. Three cases, no fixtures, per the repo's terse-tests rule.

## Deviations from `plan.md`

1. **`app/page.tsx` renders the primitives rather than an empty shell.** The plan allows
   "a bare shell proving the foundation"; a shell that renders nothing proves nothing, so
   the page draws each primitive with mocked props. **Every string on it is verbatim from
   the landed record** — the quote and span from `grounding/samples/r1-live-healthy.json`
   (계양전기 `20260724000546`), the figure from `headline-numbers.md`, the 소멸주의보 body
   from that file's 발표용 문장 4 as printed — and nothing is composed into a surface. The
   file says in its own header that `P5.S12` replaces it, and that the pack is dated
   2026-08-20 so these are fixed samples, not live data.
2. **`Citation` accepts a `span` prop it does not render.** Carried so a call site can
   pass the payload's citation triple whole; the offsets are internal, like a reason code.
   Documented on the prop.
3. **`next dev` wrote `frontend/AGENTS.md` and `frontend/CLAUDE.md`** (1 line: `@AGENTS.md`)
   into the tree. They are Next 16's own generated agent-guidance files — see
   `node_modules/next/dist/server/lib/generate-agent-files.js` — warning that this Next
   differs from training data and pointing at the docs bundled in `node_modules`. They are
   not authored here and deleting them only re-creates the change on the next `next dev`,
   so they are left in place, but they are **agent-instruction files this slice did not
   write**: flagged for the orchestrator to keep or drop before committing.
4. **TypeScript pinned to 5.9.3, not the `latest` 7.0.2.** npm's `latest` tag is now the
   Go rewrite. On a foundation slice that nine later slices inherit, a brand-new compiler
   implementation is the wrong place to be first; 5.9.3 is the last 5.x. Revisit at P4.
5. **`allowImportingTsExtensions: true` in `tsconfig.json`.** Node's own test runner strips
   types in place and needs the real extension on a relative import (`./api.ts`). Safe:
   this config never emits. Next also normalised the file's formatting and set
   `jsx: react-jsx` on first build — its own doing, left as it wrote it.

Nothing else departs from the plan.

## Doc impact recorded in `phase.md`

`frontend` (the foundation exists: stack, layout, the vendoring provenance and its
read-only rule, the `.cosmos` shell + reduced-motion convention, the seven primitives and
the two record readings, the CORS/origin answer, the binary-asset gap), `api` (the client's
view of the contract — nothing new on the wire), `qa` (the frontend's own check: `next
build` + `tsc --noEmit` + 3 node:test cases; Python stays 113), `architecture` (the
frontend/API seam is a same-origin rewrite, so the service needs no CORS), `operations`
(`npm run dev` beside uvicorn in `compose.yaml`; the missing binaries are an operator step),
`decisions` (same-origin proxy over CORS; 「추정」 renders 추정; D+n is faint, never alert).

## What the operator must export — deliverable 6

The files live in the Claude Design project **"Mijual Design System"** and cannot be
created here. Drop each at the exact path below (`frontend/public/assets/README.md`
carries the same table beside the slot):

| file | what it is | drop at |
|---|---|---|
| `PretendardVariable.woff2` | Pretendard Variable, the Korean UI face (R1, self-hosted) | `frontend/public/assets/fonts/PretendardVariable.woff2` |
| `mijual-wordmark-charcoal.png` | the English wordmark, brand charcoal `#1f2926` (R1 revision 3) | `frontend/public/assets/mijual-wordmark-charcoal.png` |
| the reversed **white** wordmark | R1 revision 1 generated it from the same shape; the landed record names only the charcoal file, so export it under whatever name the design project gives it and `P5.S11` wires that name | `frontend/public/assets/` |
| `mijual-logo-ring-charcoal.png` | ring logo (R2 — closes R1's missing symbol-mark gap) | `frontend/public/assets/mijual-logo-ring-charcoal.png` |
| `mijual-logo-ring-white.png` | ring logo reversed — what the cosmos nav and footer use | `frontend/public/assets/mijual-logo-ring-white.png` |

There is **no SVG wordmark** and no favicon-scale mark beyond the ring logo. Until they
arrive, Pretendard falls back down its own stack (`font-display: swap`, nothing blocks),
IBM Plex Mono is unaffected because it comes from the CDN, and no image is substituted
anywhere. `P5.S11` is the first slice that renders one, and it renders the real file or
nothing.
