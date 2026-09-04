# P12.F3 — result

- **status:** done
- **summary:** `/portfolio`'s two late bands are gone as flicker: the 전환 제안 offer is server-rendered from the session the server already knows (a 401, or `?sample=1`'s own read) and hidden before paint by a `sessionStorage` mirror, and the 계정 이전 · 세션 이월 band fills a slot the same mirror sized before the holdings were parsed — measured on a HEAD control build, `+215.28 px`/CLS 0.10126 and `+130 px` at `+2.4 s` become **0 px moved, CLS 0** in dev, the production build and a cold throttled 412×915 load. No browser-only state reaches the server.
- **files_changed:**
  - `frontend/components/chrome/PreHydration.tsx` (new — the shared seam)
  - `frontend/components/chrome/index.ts`
  - `frontend/app/layout.tsx`
  - `frontend/app/portfolio/page.tsx`
  - `frontend/components/portfolio/Portfolio.tsx`
  - `frontend/components/portfolio/Portfolio.module.css`
  - `frontend/components/auth/ConversionOffer.tsx`
  - `frontend/components/auth/Auth.module.css`
  - `frontend/lib/session.server.ts`
  - `works/phases/active/P12/phase.md`, `works/phases/active/P12/slices/P12.F3/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — pass
  - `cd frontend && npm run smoke` — pass (22/22)
  - `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build` in a fresh copy outside the repo — pass, **no warnings**, all routes still `ƒ` (dynamic); both inline scripts present in the served HTML
  - real-browser before/after, **Aside `aside repl --account u2`**, dev (3010) + a fresh local production build (3014) against a **HEAD production build on 3015**, at 1280 / 390 / 412×915 cold-throttled — tables below
  - `python3 scripts/workflow.py validate` — pass
- **deviations:** five, all small and none of them mechanism changes — see *Deviations* below.
- **doc_impact:** two lines appended to `phase.md` (`frontend.md`, `security.md`).

---

## What landed

Three parts, one idea — the plan's own mechanism, built as a **shared seam** so `P12.F4` and
`P12.F5` reuse it.

**1. `components/chrome/PreHydration.tsx` — the pre-hydration mirror.** A parser-blocking inline
script reads **named storage keys only**, in `try/catch`, and stamps what it learned onto `<html>`
as `data-mj-*` attributes (the one element whose attribute mismatches `P11.F3` already suppresses).
It **writes nothing, sends nothing, loads nothing**. Two entry points: `<PreHydrationMirror />` in
the root layout's `<head>` for facts a page need not supply, and `<InlineScript code={…}>` for a
computation that needs the page's own server-rendered data beside it. `clearMirror(…)` drops a stamp
once the owning component's state has taken over. The attribute contract is a table in that file's
header; `jsonLiteral()` is the one way server data enters a script body.

**2. The 전환 제안 offer (R1 F6) is server-rendered.** Three of its four conditions were always the
server's: `app/portfolio/page.tsx` answers **anonymous** from the 401 it already gets (no extra read
at all) or, on `?sample=1`, from `readAuthState()`, and **값 계산 직후** from the payload it just
served. `ConversionOffer` takes `initialAnonymous` (the `P4.F10` shape `DeadlineOffer` uses), the
probe is switched **off**, and the band is in the first painted HTML. The fourth condition — 세션당
1회 — stays the browser's: the head script stamps `data-mj-offer-seen`, `Auth.module.css` hides
`.offerPre` under it, React's first client render still renders the band (matching the server), and
the existing effect calls `markSeen()` exactly as before — `false` unmounts an element that never
painted, `true` keeps the one that did. 조회's `lead` variant passes nothing, keeps its probe, and is
byte-identical (proved below).

**3. The 계정 이전 · 세션 이월 band (R1 F2) fills a reserved slot.** `page.tsx` reads today's served
sample composition in account mode (anonymous, cheap, and exactly the read this client used to make
after mount), so the client has the rows **and their names** at hydration. `Portfolio` renders an
always-present `div.carrySlot` at the band's position — `display: contents`, so a filled slot lays
the band out exactly as before and an empty one is not a grid item at all — followed by a
page-level inline script that reads `mijual.portfolio.sample` / `mijual.lookup.holdings` and the two
담지 않기 flags, applies the same rules `useCarryOffer` applies, and stamps `data-mj-carry-rows` /
`data-mj-carry-kind` / `--mj-carry-rows`. Two CSS rules turn that count into the band's **exact**
height. `useCarryOffer` now reads the dismissal flag during render, so the band lands in the *same
commit* that reads the store; the stamp is released once the band has rendered or the browser has
declined it, so a later 담지 않기 leaves no reserved gap.

**The security constraint held.** No cookie, no query parameter, no header carries browser-only
state. The server uses only what it already knows (the session, the 401, the served payloads); the
sample's edits, the offer-seen flag and both 담지 않기 flags are read **in the browser, by the
browser**, twelve lines before they are needed. `docs/current/security.md` line 188 is unchanged in
substance.

## The reserved height, and why the numbers are measured

`.carry`'s height is not derivable from the tokens, so it was measured (1280 and 390, dev and the
production build):

```
2 px border + 28 px padding + 16 px (2 × --space-2) + 44 px actions
  + 18.59375 px label  (12 px × 1.55, snapped to Chrome's 1/64 px)
  + n × 18.671875 px rows + (n−1) × 4 px      ⇒  H(n) = 104.59375 + 22.671875 n
세션 이월 (no label, no .mono in the sentence)  ⇒  H(n) =  78      + 22.59375  n
```

A 계정 이전 row is **0.078125 px taller than the label** because it carries a `.mono` count whose face
makes the line box taller — precisely the thing a derivation from `--text-sm × --leading-base` would
have got wrong. Measured against the filled band: `n = 4` → 195.28125 (reserved 195.28125),
`n = 3` → 172.60938 (reserved 172.609375), session `n = 1` → 100.59375 (reserved 100.59375). Exact
at every count tested.

## F2 — 계정 이전, before / after

"Before" is a **HEAD production build on 3015** (F1's seam: never a `git stash` sweep against
`next dev`); dev's "before" was measured on the untouched tree before any edit. Storage is
port-scoped, so each port carries its own `mijual.portfolio.sample`.

| Runtime, viewport | build | FCP | the band | everything below | CLS |
|---|---|---|---|---|---|
| dev 3010, 1280 | HEAD | 176 | inserted `[184, 76, 912, 195.28]` at **+62…91 ms** | **+215.28 px** | **0.05419** |
| dev 3010, 1280 | fixed | 152 | empty slot `[184, 76, 912, 195.28]` **at first paint**, band fills the same rect | **0 px** | **0** |
| dev 3010, 390 | HEAD | 104 | inserted `[16, 76, 358, 195.28]` | **+215.28 px** | 0 (no entry at 390) |
| dev 3010, 390 | fixed | 156 | slot = band `[16, 76, 358, 195.28]` | **0 px** | **0** |
| prod build, 1280 | HEAD 3015 | 136 | inserted at **+105 ms** | **+215.28 px** (34 elements) | **0.05419** |
| prod build, 1280 | fixed 3014 | 220 | slot in the DOM at **89 ms** (−131 ms) | **0 px** (0 elements) | **0** |
| prod build, 390 | HEAD 3015 | 100 | inserted at **+62 ms** | **+215.28 px** (51 elements) | 0 |
| prod build, 390 | fixed 3014 | 180 | slot in the DOM at **80 ms** (−100 ms) | **0 px** (0 elements) | **0** |
| **cold 412×915, 4× CPU, ≈1.6 Mbps** | HEAD 3015 | 716 | inserted at **3159 ms (+2.44 s)** | 보유 종목 panel **76 → 291.28** | **0.10126** |
| **cold 412×915** | fixed 3014 | 756 | slot in the DOM at **601 ms (−155 ms)**, empty box `[16, 76, 380, 195.28]` at first paint, band fills it at 2928 ms | panel **291.28 → 291.28** | 0.00027 † |

† the two shift sources are the footer's contact/phone line moving **horizontally** (`787 → 787` in
y) — the mono-face reflow of R1 F5, `P12.F9`'s cause, present on both builds.

**Three rows (one 삭제 + one 보유량 → 777, both made through the product's own controls).** Store
`{"v":2,"shares":{"00109310":777},"removed":["00102618"],"claims":[]}`. Fixed build, 1280 and 390:
band `172.60938` px, reserved `172.609375` px, rows `대동기어 777주 / 한화솔루션 500주 / 세기상사
100주`, **0 elements moved, CLS 0**. Cold 412×915: empty slot `[16, 76, 380, 172.61]` at first paint,
band fills the identical box at 2938 ms, 보유 종목 panel `268.61 → 268.61`.

**세션 이월 (the `session` variant).** The plan allowed noting it instead of covering it; it fell out
naturally, so it is covered and measured. `mijual.lookup.holdings = {v:1, entries:{00109310:500}}`,
empty account, no sample, 6× CPU throttle: empty slot `[184, 76, 912, 100.59]` at 1280 and
`[16, 76, 358, 100.59]` at 390 at first paint, band `100.59375` px, panel `196.59 → 196.59`, CLS 0,
copy unchanged (`조회에서 입력한 대동기어 500주가 이 세션에 남아 있습니다`).

**Behaviour, unchanged.**
- **담지 않기** → band leaves, 보유 종목 panel returns to `y = 76`, `mijual.portfolio.migrate` written;
  **reload in the same tab** → the script reads the flag and stamps nothing, no reservation, no band,
  **nothing moved at all** (`moved: []`, CLS 0) — no 195 px of reserved emptiness left behind.
- **담기** → the 4 issuers land in the account, the band leaves, `clearSample()` runs, no leftover
  stamp, slot height 0.
- **No sample in storage** → no attribute, `display: contents`, and the resting screenshot is
  **byte-identical** to HEAD (same md5, `compare -metric AE` = **0**) at 1280; positive control
  (same build, sample present) = `1.35e9`.

## F6 — 전환 제안, before / after

`curl` on anonymous `/portfolio`: `offerPre` + `offerCta` present in the **served HTML** on 3014,
absent on 3015.

| Runtime, viewport | build | FCP | the band | document height | CLS |
|---|---|---|---|---|---|
| prod build, 1280 | HEAD 3015 | 120 | absent at first paint | **1324 → 1454 (+130)**, 23 elements | 0 |
| prod build, 1280 | fixed 3014 | 92 | `[184, 1142.83, 912, 110]` **at first paint** | **1454, stable** | 0.00039 † |
| prod build, 390 | HEAD 3015 | 104 | absent at first paint | **2131 → 2257 (+126)**, 24 elements | 0 |
| prod build, 390 | fixed 3014 | 128 | `[16, 1815.8, 358, 106]` **at first paint** | **2257, stable** | 0 |
| **cold 412×915** | HEAD 3015 | 792 / 1084 | in the DOM at **2809 / 3015 ms — +2.0 / +1.9 s after paint** | **2131 → 2257** | 0 |
| **cold 412×915** | fixed 3014 | 1000 / 1168 | in the DOM at **583 / 576 ms — ~0.4–0.6 s before paint** | **2257, stable** | 0 / 5e-05 |
| dev 3010, 1280 / 390 | fixed | 112 / 176 | at first paint, rects as above | 1454 / 2257 stable | 0.00039 † / 0 |

† the same F5 mono reflow: `.rowWhen` / `.holdingDDay` / `.factor` moving **horizontally**
(`524.125 → 524.125` in y) at t = 102 ms. Present on HEAD too.

R1's before at 390 records a width of 380; both builds measure **358** here at 390 and **380** at
412 — an emulation-setup difference from R1's sweep, not a change: fixed and HEAD agree on every
viewport.

**Second load in the same session (seen flag set).** `data-mj-offer-seen` stamped, the band renders
into a `display: none` element (so it never paints), `markSeen()` returns `false` and unmounts it:
document 1324 / 2131 **stable from first paint**, 0 elements moved, CLS 0. HEAD is also clean on the
second load (the flag gated it there too), so this state was preserved rather than improved.

**`/stocks/[corp_code]` is untouched.** Anonymous, 500주 typed into 대동기어: identical on both
builds — same copy (`이 보유량은 탭을 닫으면 사라집니다 … 저장하고 알림 받기`), same rect
`[184, 876, 912, 137]`, same document height 1364, `offerPre` **absent** (the class is carried only
by a server-resolved instance), probe still gates it, flag still written.

**Resting layout, anonymous with the seen flag set:** `compare -metric AE` = **0** at 1280 **and**
390 against HEAD, with identical document heights (1324 / 2131) and identical stores. An earlier run
of this comparison differed by 116 px until I noticed the two ports held **different sample stores**
(one carried the removal I had made through the UI) — the sample composition is per-request and per
browser, so this control is only meaningful with the stores equalised. Recorded because it is the
kind of false positive this surface will produce again.

## Hydration and console

**No console output of any kind** — no hydration warning, no error — in **every** measured load:
both dev viewports, both production builds at 1280/390, both cold 412×915 profiles, the dismiss and
담기 flows, the 9-route signed-in sweep and the 5-route anonymous sweep on the fixed build (`console:
[]`, `errors: []` in all of them; CLS 0 on every route except the known mono 3e-05). The capture
overrides `console.error`/`warn` from an init script installed **before** the document exists, so it
sees React's warnings.

## Cost

- **171 bytes** of inline script on every page (the head mirror); **1,035 bytes** on `/portfolio` in
  account mode only (the carry script, including the served codes).
- One `GET /portfolio/sample` per account-mode `/portfolio` render moves from the browser to the
  server — and it now happens even for a browser holding no sample. Against it: 계정 이전 no longer
  spends a `GET /stocks/{corp_code}` **per candidate** (4 requests on the measured sample), and
  `readAuthState` is now request-memoised, so `/events/{rcept_no}` and `/portfolio?sample=1` cost one
  server-side `/auth/me` where they cost two.
- Anonymous `/portfolio` costs **one client request fewer** (the offer's `GET /auth/me` probe is off).

## Deviations from `plan.md`

1. **The server's facts reach the carry script as inlined JSON literals, not as `data-*` attributes
   on the slot.** Same facts, one fewer indirection, and no extra attributes for React to hydrate;
   `jsonLiteral()` escapes `<` so no value can close the element early.
2. **`InlineScript` uses the framework's own idiom for this element** —
   `type="text/javascript"` on the server / `"text/plain"` on the client plus element-scoped
   `suppressHydrationWarning`, from `node_modules/next/dist/docs/01-app/02-guides/preventing-flash-before-hydration.md`.
   It silences React's development warning about rendering `<script>` and makes the
   client-navigation no-op explicit rather than incidental. (That guide also records the dev-only
   Strict Mode reset of `<html>` attributes; every attribute here is a pre-hydration device whose job
   is over by then, so nothing needs re-applying — and the measurements confirm it.)
3. **The 세션 이월 variant is covered**, where the plan allowed noting it instead.
4. **`readAuthState` is wrapped in React `cache()`.** `?sample=1` would otherwise read the session
   twice in one render (the root layout also reads it since `P12.F1`); the memo also removes a
   pre-existing double read on `/events/{rcept_no}`.
5. **계정 이전's names come from the served composition** instead of a `getStock` per candidate. Not
   asked for, but it is what lets the band fill in the same commit that reads the store, and the text
   is identical (the same corpus, the same field). The client-side composition read is **kept as a
   fallback** for when the server's read fails, so that path behaves exactly as it did before.

## Limits worth knowing

- **The reservation assumes one line per row.** Measured at 1280 and 390 with the real sample and
  with 세션 이월's sentence, neither wraps. A company name long enough to wrap at 390 would leave a
  residual of one line (18.6 px) rather than the whole band — strictly smaller than today's push,
  never larger.
- **A row's height depends on the mono face's metrics** (the `.mono` count is what makes it
  18.671875 px). Before IBM Plex Mono lands on a cold load the fallback face could measure
  differently; measured cold at 412×915 the residual was **0** and the only shift entries were the
  footer's horizontal mono reflow. `P12.F9` removes that class of difference.
- **FCP is not measurably worse.** Warm: fixed 92–220 ms vs HEAD 100–136 ms across the same routes
  (overlapping run-to-run variance). Cold-throttled: fixed 1000 / 1168 vs HEAD 792 / 1084 — the extra
  ~130 px of HTML and 171 B of script on a 1.6 Mbps link, and the band is nonetheless in the DOM
  ~2.4 s earlier than HEAD manages.
- **An edited sample still shifts the anonymous surface at hydration, and that is *not* this
  slice's band.** A browser whose sample carries a removal renders the server's 4 rows and drops to
  3 at hydration: dev, anonymous, 1280, `removed: ["00102618"]` → **CLS 0.05206**, document 1208 px.
  It is the same Family A cause on the *holdings list*, it only reproduces for a browser that has
  edited its sample (R1's had `removed: []`, which is why the hunt never saw it), and it is outside
  F3's two named bands. Recorded in `phase.md` for the review to route — noted, not silently fixed.

## Hygiene

Throwaway account `p12f3+1788479557@example.com` created through the signup form in dev and
**deleted through 계정 삭제** (landed on `/`, signed out, 로그인 link restored). Production was never
touched — every signed-in state was exercised on dev and on the two local builds. Both build servers
(3014 fixed, 3015 HEAD control, built in copies outside the repo) are stopped and their ports are
free. `make stack-status` is as found (api pid 60158, web pid 61423, postgres up). The dev browser
profile's `mijual.portfolio.sample` was restored to its unedited value. **Instrument: Aside `repl`
over Bash, `aside repl --account u2` (profile 「claude2」) on every invocation** — never `u0`, never
`aside account use`.

**Instrument notes for later slices** (added to the phase's seam record): `aside repl` code is
evaluated as a **module**, so top-level `await` works but a top-level `return` silently forces script
mode and makes every `await` a SyntaxError — end scripts with `console.log`, never `return`;
`page.waitForTimeout` does not exist (`new Promise(r => setTimeout(r, ms))`); `page.screenshot({path})`
resolves **inside the invocation's own session directory**
(`~/.aside/u/2/sessions/<stamp>/`), not the cwd, and an absolute path throws — capture every image a
comparison needs in **one** invocation, then copy them out.
