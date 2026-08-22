# Result — P5.S10: Next.js foundation

**Status: `done`** (2026-08-22, second pass).

The slice ran in two passes. The first built everything and stopped at `needs_operator` on
deliverable 6: the five binary design assets live in the Claude Design project and cannot be
created here. **The operator exported them, and this second pass — the plan's
*Addendum — operator asset delivery* — copied them in byte-for-byte, re-verified the app and
closed the gap.** Nothing was substituted, generated or placeheld at any point, in either
pass. The delivery record is the last section of this file; the first pass's account below
is unchanged except where it stated the files were missing.

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

Serving rather than importing is also what kept the build honest through the days the
binary was missing: a bundled `url()` pointing at a non-existent file fails the build
outright, whereas a served one 404s and `font-display: swap` falls through Pretendard's own
stack. The font is in the repo now (last section) and the vendored file never changed.

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

6. **Second pass (the addendum): three edits beyond the two files it names.** The addendum
   says to update `public/assets/README.md` and the phase notes. Two other places carried the
   same now-false sentence — `frontend/README.md`'s directory listing ("the binary design
   assets — NOT in this repo") and the *provenance header* of the vendored
   `public/foundations/fonts.css` ("PretendardVariable.woff2 is NOT in this repo yet") — and
   both were corrected. The `fonts.css` edit touches **only the header this slice itself
   wrote**; the vendored CSS body was re-diffed against
   `rounds/01-brand-foundations/output/fonts.css` afterwards and is byte-identical, so the
   landed record is still untouched. Third, `public/assets/fonts/.gitkeep` was deleted: it
   existed to keep an empty directory in git and asserted the font was absent, and the
   directory now holds the real font.

Nothing else departs from the plan.

## Doc impact recorded in `phase.md`

`frontend` (the foundation exists: stack, layout, the vendoring provenance and its
read-only rule, the `.cosmos` shell + reduced-motion convention, the seven primitives and
the two record readings, the CORS/origin answer, and the **binary assets now in the repo** —
the doc's binary-asset Open Question is closed, with the white wordmark named), `api` (the client's
view of the contract — nothing new on the wire), `qa` (the frontend's own check: `next
build` + `tsc --noEmit` + 3 node:test cases; Python stays 113), `architecture` (the
frontend/API seam is a same-origin rewrite, so the service needs no CORS), `operations`
(`npm run dev` beside uvicorn in `compose.yaml`; the binaries were an operator export step and
it is done — replacing one means a new export from the design project, never a local edit),
`decisions` (same-origin proxy over CORS; 「추정」 renders 추정; D+n is faint, never alert).

## Deliverable 6 — the binaries landed (operator delivery, 2026-08-22)

The operator exported all five files out of the Claude Design project **"Mijual Design
System"** to `~/Downloads/handoff-output/brand-binaries/`. They were copied into the paths
this slice had already wired, **unmodified** — not re-encoded, resized, optimised or
metadata-stripped; each copy was `cmp`-verified against its source and is byte-identical:

| repo path | format | sha256 |
|---|---|---|
| `frontend/public/assets/fonts/PretendardVariable.woff2` | WOFF2 / TrueType, variable `wght 45–920`, 2,057,688 b | `9599f12f…d900b4` |
| `frontend/public/assets/mijual-wordmark-charcoal.png` | PNG 1788×324 RGBA, 42,403 b | `2119682f…fb3d25c` |
| `frontend/public/assets/mijual-wordmark-white.png` | PNG 1788×324 RGBA, 37,242 b | `8725c501…ca78807` |
| `frontend/public/assets/mijual-logo-ring-charcoal.png` | PNG 2178×346 RGBA, 76,558 b | `454a07c0…852b68` |
| `frontend/public/assets/mijual-logo-ring-white.png` | PNG 2178×346 RGBA, 64,605 b | `7bef551a…75ff4b` |

**The open filename question is answered: the reversed wordmark ships as
`mijual-wordmark-white.png`** — the landed record described it without naming a file, and
this is the exact name `P5.S11` wires. It is the same 1788×324 shape as the charcoal one;
the white pair is what the cosmos-dark chrome uses, the charcoal pair is for light
surfaces, and neither substitutes for the other. There is still **no SVG wordmark** and no
favicon-scale mark beyond the ring logo.

`fonts.css` needed **no edit**: its landed
`url("../assets/fonts/PretendardVariable.woff2")` resolves from `/foundations/fonts.css` to
`/assets/fonts/PretendardVariable.woff2`, which is exactly where the font now sits. The
vendored file's body is still byte-identical to
`rounds/01-brand-foundations/output/fonts.css` (re-diffed after this pass).

### Re-verification (all commands run this pass)

| command / check | result |
|---|---|
| `cd frontend && npm run build` | **pass** — compiled, 3 static pages prerendered; run again at the end so `next-env.d.ts` is back in its committed build form (`next dev` rewrites it to the `.next/dev/types/…` variant) |
| `cd frontend && npm run typecheck` | **pass**, no output |
| `cd frontend && npm run smoke` | **pass** — 3/3 in 91 ms |
| `.venv/bin/python -m pytest` | **113 passed**, 2.60 s — baseline untouched, no Python file edited |
| `python3 scripts/workflow.py validate` | **Workflow validation passed.** |
| dev server: `GET /` | **200**, 19,552 b |
| dev server: `GET /assets/fonts/PretendardVariable.woff2` | **200**, `font/woff2`, 2,057,688 b — served body sha256-**identical** to the file on disk |
| dev server: the four PNGs at `/assets/…` | **200** each, `image/png`, 42,403 / 37,242 / 76,558 / 64,605 b |
| dev server: `GET /foundations/fonts.css` | **200**, `text/css` |
| **real browser** (headless Chrome 141 over CDP) | **Pretendard is loading, not falling back** — see below |
| both servers | **stopped** (dev server and Chrome; verified with a follow-up curl returning `000`) |

The font check is the one the addendum asks for, and it was done in a real browser rather
than inferred from a 200:

- `document.fonts` reports the face `Pretendard Variable` with `status: "loaded"` and
  `weight: "45 920"`; `document.fonts.check('400 16px "Pretendard Variable"')` → `true`.
- `CSS.getPlatformFontsForNode` — what Blink *actually drew with* — reports **Pretendard
  Variable** for Korean prose: the `RightsChip` label 유상증자 신주인수권 (×10 glyphs) and the
  `Citation` quote (×48). Before the export this text rendered in the `-apple-system`
  fallback.
- IBM Plex Mono is loaded at 400 and 600 from the CDN (unaffected by this delivery), and a
  screenshot at 1280×1200 shows the cosmos-dark shell with every primitive rendering Korean
  correctly — no tofu, no fallback metrics.

**One finding, recorded for `P5.S19` and deliberately not acted on:** now that the real face
is loaded it is visible that Korean glyphs inside a `--font-mono` element never reach
Pretendard — the token stack `"IBM Plex Mono","SF Mono",Consolas,monospace` has no Hangul, so
`StateBadge` 추후결정, the `LapseAlert` 소멸주의보 badge and the 근거 of the `[근거]` chip are
drawn by the OS Korean face (macOS: Apple SD Gothic Neo), i.e. a different face per platform.
Numerals are unaffected and Korean prose is correct. Both `tokens.css` and those components
are as landed/approved, so this is a fidelity question for the real-browser slice — **not a
licence to restyle a primitive or edit the vendored token file.**

### Files touched in this pass

- the five binaries (new, unmodified copies);
- `frontend/public/assets/README.md` — rewritten from an export list into a delivery record
  (what is here, formats, dimensions, sha256, the white-wordmark answer, and the rule that a
  replacement is a new export rather than a local edit);
- `frontend/public/assets/fonts/.gitkeep` — **deleted**: it existed only to keep an empty slot
  in git and its text asserted the font "is not in this repo", which is now false; the
  directory holds the real font;
- `frontend/README.md` — the one line calling `assets/` "NOT in this repo";
- `frontend/public/foundations/fonts.css` — **only the provenance-header line** that said the
  woff2 was not in the repo yet (the vendored CSS body is untouched and still byte-identical
  to the record);
- `works/phases/active/P5/phase.md` — S10 findings notes 17–19 (the delivery table, the
  browser verification, the mono/Hangul finding), the "binary assets are outside the repo"
  gotcha, the S10 *Doc impact* entry, and the *Binary design assets* Open Question, now closed.

`P5.S11` is unblocked: it renders the real files, at these exact names.
