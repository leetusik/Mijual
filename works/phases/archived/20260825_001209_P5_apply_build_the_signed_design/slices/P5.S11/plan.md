# Plan — P5.S11: Global chrome (R2)

## Context

Read `works/phases/active/P5/phase.md` in full — the S10 findings (component map,
`lib/copy` citation convention, reduced-motion convention, the `.backdrop` slot, the
`추정`-tag and faint-`D+n` readings) plus DECOMP notes 7 and 8 (the AI 질문 slot) are
binding. Design chain: `docs/current/frontend.md` supersession table → `SIGNOFF.md`
(R2's entry — the chrome copy was explicitly signed) → R2 `build-prompt.md`
(`rounds/02-landing-chrome/output/` — the *Page shell*, *Footer*, *vocky* and
*Cosmos* sections) → `grounding/copy-inventory.md`. **RESPECT THE DESIGN.**

This slice is the chrome every page sits inside: nav, footer, mobile top bar + sheet,
and the vocky touchpoints. The landing content (hero, cards, board, starfield) is
`P5.S12`'s; the logged-in account-menu swap is `P5.S16`'s — leave the 로그인 slot
cleanly replaceable.

## Deliverables

1. **Desktop nav** — 52px, transparent over the cosmos, 1px `rgba(255,255,255,.12)`
   bottom. Left: the white ring wordmark PNG at h 19px (the delivered asset —
   `mijual-logo-ring-white.png`; confirm against R2's "white ring wordmark" wording
   and record which file you used) + the three signed slots **with their superseded
   labels**: **내 종목 조회 · 관제 현황판 · AI 질문** (R2's literals 내 종목 연결/해설
   are superseded by R4-5 and R6 — the supersession table governs; render the
   superseded labels, never R2's originals). 13.5px; active = 600 + 2px #fff
   underline. Right: 로그인 (quiet, `rgba(255,255,255,.68)`) + the vocky trigger
   `[의견]` (mono, hairline `rgba(255,255,255,.3)`).
2. **Routes behind the slots** — decide and record the route map (S12–S14 inherit
   it): the landing (관제 현황판) at `/`, a 내 종목 조회 route, and the **AI 질문
   route as a bare page shell** — chrome only, no invented copy, no fake chat, no
   placeholder text; the page body is honestly empty (DECOMP note 7: P6 owns and
   replaces it). Nav-active state works for all three.
3. **Footer** — white-on-dark, 1px `rgba(255,255,255,.14)` top. Left column: white
   ring wordmark h 17 + the positioning line (mono 11, `rgba(255,255,255,.45)`) —
   the line's text comes from the landed record/copy-inventory, transcribed with a
   citation. Right column, 12px `rgba(255,255,255,.72)`, the three signed sentences
   verbatim: ① provenance ("모든 수치는 DART 공시에서만 나왔고, 추정치는 [추정]
   표시로 구분했습니다." — signed at the R2 gate; `[추정]` here is prose describing
   the mark, render the sentence verbatim — S10 note 4a), ② the gate-cost sentence
   (its 49.2억원 carries the 추정 tag; its only remaining placement), ③ the
   disclaimer. Bottom hairline row: © · 자료: 금융감독원 DART 전자공시 | 의견 보내기
   · **AI 질문** (R2 landed 해설; R6 superseded the label — DECOMP note 7) — mono 11.
4. **Mobile (≤480px)** — top bar 52px (white ring wordmark + `메뉴` button, mono,
   44px hit) + sheet menu: rows ≥48px, the three nav slots, 로그인, and the 의견
   보내기 row (a vocky trigger); sheet close = 200ms fade (a cut under reduced
   motion, per the S10 convention).
5. **vocky wiring** — load the vocky script **once, deferred, in the shell**; the
   script URL is external and not in any record — wire it through an env seam
   (`NEXT_PUBLIC_VOCKY_SRC` or similar; unset → no script tag, triggers still render)
   and record it (its real value is `P5.S18`/P4 territory). Exactly three trigger
   elements, each a plain element with `data-vocky-trigger`: nav `[의견]`, mobile
   sheet 의견 보내기, footer 의견 보내기. Style triggers per each surface's spec in
   R2; do not style the widget; **no floating button, and keep the bottom-right
   corner clear** (P6's launcher lands there — phase note).
6. **Wrap the app** — the chrome becomes part of the root layout (or a layout
   component every page uses; record the mechanism). S10's `app/page.tsx` stays as
   is (S12 replaces it) but now renders inside the chrome.

## Constraints

- Copy: every Korean string transcribed verbatim with a cited source per S10 note 11
  (extend `lib/copy` or a slice-local module following the same convention). **No
  invented Korean** — if a needed string genuinely has no source, stop and say so in
  the verdict rather than writing one.
- The nav/footer wordmark files are the operator-delivered PNGs — never re-encoded,
  height-constrained rendering only.
- Primitives/tokens untouched; sizes in em/token terms per S10 note 5.
- No new npm dependencies.

## Validation

- `npm run build` + `npm run typecheck` + `npm run smoke` — green.
- Dev server + headless-Chrome check (S10's CDP pattern): the three nav labels and
  active state, the wordmark image actually loading (natural size 2178×346, rendered
  h 19), the three footer sentences present verbatim, the bottom row's AI 질문 label,
  three `data-vocky-trigger` elements and **no** script tag with the env unset, the
  mobile sheet at ≤480px viewport. Screenshot for the record. Stop everything after.
- `.venv/bin/python -m pytest` untouched (113); `python3 scripts/workflow.py
  validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (route map, chrome component API, the
로그인-slot swap seam for S16, vocky env seam for S18) and *Doc impact* (`frontend` —
the chrome; `experience` if the route map is durable truth). Structured verdict. No
commits, no status transitions.
