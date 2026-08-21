# Plan — P5.S10: Next.js foundation

## Context

First frontend slice. Read `works/phases/active/P5/phase.md` in full — the Context
read order, Constraints, and every findings section (the backend S1–S9/S20 notes tell
you the API surface a typed client must cover). Then the design chain in order:
`docs/current/frontend.md` (the **supersession table** — binding; R1's light theme and
▷ marker are superseded), `docs/reference/design/SIGNOFF.md`, R1 `build-prompt.md` +
R2's cosmos/craft-panel section (`rounds/{01,02}-*/output/`), and
`docs/reference/design/grounding/` (`ui-traps.md`, `states-and-trust.md` binding;
`copy-inventory.md` is the copy source; `samples/*.json` shows payload shapes but the
live API is the truth). **RESPECT THE DESIGN**: nothing approved is dropped,
simplified, restyled, or improved.

## Deliverables

1. **Scaffold** — a Next.js app (TypeScript, App Router) in a top-level `frontend/`
   directory (record the exact stack versions). Keep it lean: no UI library, no CSS
   framework — the design system is `tokens.css`. Dev proxy/rewrites to the FastAPI
   service (`localhost:8000` default; record the config). Korean-only user-facing
   text; `lang="ko"`.
2. **Vendored foundations** — copy `tokens.css` + `fonts.css` **from the landed R2
   record** (`rounds/02-landing-chrome/output/tokens.css` — it contains R1's set plus
   the `.cosmos` scope; R1's `fonts.css` is unchanged) into the app **verbatim as
   landed** (record provenance in a comment atop each file naming the source path;
   do not reformat, rename tokens, or "clean up"). `fonts.css` self-hosts Pretendard
   from `../assets/fonts/PretendardVariable.woff2` and pulls IBM Plex Mono from
   Google Fonts — keep both mechanisms, adjusting only the relative path to the
   app's asset layout (record the mapping).
3. **The `.cosmos` page shell** — root layout applying `class="cosmos"` with
   `color: var(--ink-1)` per R2, body `#0a1310`, the 1120px content column,
   480/768/1120 breakpoints, motion durations/eases from R1, and
   `prefers-reduced-motion` plumbing (a shared utility/convention the later slices
   use — freeze ticks, fades become cuts). The starfield/glow/shooting-star layers
   are `P5.S12`'s (landing), not this slice's — but the shell must not preclude a
   full-page fixed backdrop.
4. **R1 trust primitives** — faithful component implementations, matching the
   build-prompt specs exactly (sizes, colors, spacing are contract, not suggestion):
   - `EstimateMarker` — **「추정」 bordered tag form** (the supersession: ▷ never
     appears in UI; R2's spec — bordered sans 10px tag beside the value).
   - `Citation` — `[근거]` chip → inset panel, verbatim quote pre-wrap, scroll
     >180px, DART link `https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}`;
     **multi-part support** (S20: a citation may carry `parts` — each part verbatim;
     render all parts, never one addend as the whole).
   - `StateBadge` (추후결정 — never with a date · 철회 full-width notice with the
     locked per-type copy · 발행사 기재 불일치 alert-tint chip; gate-failed =
     rendered as nothing).
   - `DDay` (mono 600 17px fixed, color-only urgency, date + "KST" below,
     upstream-computed values only — no date math in the browser).
   - `RightsChip` (label-only, type tints, `compact` variant).
   - 소멸주의보 strip (R1 spec + R2's craft-panel/hazard-stripe variant).
   - Craft panel (R2: translucent dark card, border-strong, top-edge glow,
     9px corner brackets) as a reusable shell.
   Copy for these comes from `grounding/copy-inventory.md` / the payloads — never
   invented.
5. **Typed API client** — one module typing the read endpoints the pages consume
   (`/board/summary`, `/board`, `/events/{rcept_no}`, `.../corrections`, `/stocks`,
   `/portfolio/*`, `/auth/*` — the phase notes' endpoint maps are the contract):
   payload types mirroring the documented shapes (absent-key-not-null → optional
   fields; exact-decimal strings stay strings; `estimated` flags carried through so
   a component can refuse an untagged estimate), the error envelope type, the
   `X-Mijual-CSRF` header on every mutating call, `credentials: include` for the
   session cookie. Hard-code the route paths (S3's note: the client should
   hard-code these).
6. **Binary assets** — the wordmark PNGs, ring logos
   (`mijual-logo-ring-{charcoal,white}.png`) and `PretendardVariable.woff2` live in
   the Claude Design project, **not in this repo** (verified). You cannot create
   these. Wire the exact asset paths the design names into the layout/`fonts.css`,
   create the asset directory with a short README listing the expected files, and
   **check whether the files are present**. If absent (expected): finish everything
   else, and return **`needs_operator`** with the precise export list — each
   filename, where it comes from (the Claude Design project "Mijual Design System"),
   and the exact repo path to drop it at. Do not substitute, generate, or
   placeholder a wordmark (an empty slot with the path wired is honest; an invented
   mark is a design violation).
7. **A smoke check, terse** — the app builds (`next build`) and renders a minimal
   index page through the shell + one primitive with mocked props (whatever the
   scaffold's lightest test path is — do not pull in a heavy test framework;
   record what you chose). The Python suite is untouched (113 baseline).

## Constraints

- Square corners, no shadows (borders carry elevation), 4px scale, mono for every
  numeral, Korean prose never mono — R1 is the law of the land.
- No page surfaces yet (landing/detail/조회 are S12–S14); the index page may be a
  bare shell proving the foundation — no invented content or copy on it.
- Frontend dir layout: keep the repo root clean (`frontend/` beside `src/`); do not
  touch pyproject/uvicorn; document the dev run (`npm run dev`) in the same places
  S1 documented uvicorn (compose.yaml header comment).
- Commit hygiene: `node_modules`/`.next` gitignored (extend the root `.gitignore`).

## Validation

- `next build` succeeds; dev server renders the shell page (run + curl/screenshot,
  then stop it).
- The smoke check passes; `.venv/bin/python -m pytest` still green (untouched).
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (frontend layout, component API map for
S11–S17, client conventions, asset status) and *Doc impact* (`frontend` — the
foundation exists: stack, layout, vendoring provenance, primitives; `qa` — the
frontend check). Structured verdict — **`needs_operator` with the export list if the
binaries are absent**, else `done`. No commits, no status transitions.
