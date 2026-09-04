# P12.F5 — result

- **status:** done
- **summary:** `/auth/login`'s 로그아웃되었습니다 band no longer lands after paint — the pre-hydration mirror's **fourth use** and its **head half**: `PreHydration.tsx`'s `<head>` script reads `sessionStorage["mijual.auth.flash"]` (read only; `readFlashOnce()` is still the one consumer) and stamps `data-mj-auth-flash="logout"` on `<html>`, `AuthPanel` renders the band inside a `display: contents` slot, and one `Auth.module.css` rule holds that slot at the band's **measured 40.59375 px** until the mount effect fills it and releases the stamp. Against a HEAD production build the landing's **+56.59 px** push of the form and the sample entry (CLS **0.01184** at 1280 / **0.04140** at 390) becomes **0 px moved, CLS 0** in dev and on the production build at both viewports, with the resting **and** filled pages `AE = 0` byte-identical to HEAD.
- **files_changed:**
  - `/Users/sugang/projects/personal/Mijual/frontend/components/chrome/PreHydration.tsx`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/auth/AuthPanel.tsx`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/auth/Auth.module.css`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P12/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P12/slices/P12.F5/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — pass
  - `cd frontend && npm run smoke` — pass (22/22)
  - `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build` in a fresh copy outside the repo — pass, **no warnings** (a second, HEAD-only copy built the same way as the control)
  - Aside `--account u2`, real 로그아웃 from the account menu, 1280 + 390, dev (3010) + fixed production build (3014) against a HEAD production build (3015) — pass (tables below)
  - `python3 scripts/workflow.py validate` — pass (only the pre-existing P4 consolidation / stale-doc / oversized-section warnings)
- **deviations:** four, all small — see § Deviations
- **doc_impact:** one line appended to `phase.md` (`frontend.md`, Surfaces / 로그인 panel)

---

## The change

**`components/chrome/PreHydration.tsx`** — one more `getItem` inside the same `try`, placed **above**
the sample's early `return` so a browser with no sample still gets it, and stamping only when the
value is exactly `"logout"`:

```
if(sessionStorage.getItem("mijual.auth.flash")==="logout"){h.setAttribute("data-mj-auth-flash","logout")}
```

The key is **not** cleared there. `lib/session.ts`'s `readFlashOnce()` stays the one consumer,
reading *and* clearing at the same moment it always did, so R5-1's 1회 표시 is untouched. The header
table gained the `data-mj-auth-flash` row; `lib/session.ts` and `app/auth/login/page.tsx` are
**unchanged** (no cookie, no query parameter, no header — the flash never goes near the server).

**`components/auth/AuthPanel.tsx`** — the band is now rendered inside `<div className={styles.flashSlot}>`,
same `<p className={styles.flash} role="status">{LOGOUT_DONE_KO}</p>` inside it. Two effects instead
of one: the existing reader (unchanged in what it does) also sets a new `flashResolved`, and a second
effect gated on `flashResolved` calls `clearMirror("auth-flash")` — after the commit that renders the
band, never inside the effect that reads the key (F4's rule).

**`components/auth/Auth.module.css`** — `.flashSlot { display: contents }` plus one reservation:

```
html[data-mj-auth-flash="logout"] .flashSlot:empty { display: block; min-height: 40.59375px; }
```

`min-height`, never `height` (F4's rule). The number is measured on the filled band, not derived, and
is the **same at 1280 and 390** — 「로그아웃되었습니다」 is one line in the 480 px column and in the
≤767 panel alike, so one rule serves both viewports. The 56.59 px the band used to push is this
40.59375 px plus the panel's own 16 px grid gap, which the empty `display: contents` slot does not
take and the reserved block does.

## Before / after — the real 로그아웃 landing, production builds (HEAD 3015 vs fixed 3014)

The account was created through the 계정 만들기 form, signed in, and logged out **from the account
menu** (desktop menu row at 1280, the mobile sheet's row at 390) on each port, so every reading below
is of the document `window.location.assign('/auth/login')` actually loaded.

| 1280 | HEAD (3015) | fixed (3014) |
|---|---|---|
| `<html data-mj-auth-flash>` | never set | **`"logout"` at t = 44.6 ms, FCP 56 ms** |
| the band | inserted at t = 53.1 ms | slot reserved `[449, 169, 382, 40.594]` from the first frame; filled at t = 54.7 |
| `.Auth__form` y | 241.922 → **298.516** (+56.594) | **298.516 from the first frame** (0 px) |
| `.Auth__sample` y | 564.109 → **620.703** (+56.594) | **620.703 from the first frame** (0 px) |
| `h1` y | 169 → 225.594 | 225.594 throughout |
| document height | 900 → 922 | **922 throughout** |
| `layout-shift` | 1 entry, **CLS 0.01184** (form, sample, `.head`, footer) | **no entry at all, CLS 0** |
| filled `<p>` rect | `[449, 169, 382, 40.59375]` | `[449, 169, 382, 40.59375]` — identical |
| distinct frames | 2 (moved) | 2 (empty slot → filled slot, **nothing moved**) |

| 390 | HEAD (3015) | fixed (3014) |
|---|---|---|
| `<html data-mj-auth-flash>` | never set | **`"logout"` at t = 40.7 ms, FCP 52 ms** |
| the band | inserted at t = 57.7 ms (FCP 56) | slot reserved `[33, 165, 324, 40.594]` from the first frame; filled at t = 50.3 |
| `.Auth__form` y | 237.922 → **294.516** (+56.594) | **294.516 from the first frame** (0 px) |
| `.Auth__sample` y | 556.109 → **612.703** (+56.594) | **612.703 from the first frame** (0 px) |
| `.quietRow` y | 475.109 → 531.703 | 531.703 throughout |
| document height | 991 → 1048 | **1048 throughout** |
| `layout-shift` | 1 entry, **CLS 0.04140** | **no entry at all, CLS 0** |
| filled `<p>` rect | `[33, 165, 324, 40.59375]` | `[33, 165, 324, 40.59375]` — identical |

R1 F4's dev "before" (form 241.92 → 298.52, sample 564.11 → 620.70, +56.6 px, CLS 0.00973, +27 ms
after FCP) reproduced on the HEAD **production** build with the same rects — the P7 rule again: only
the post-paint gap differs (production inserts at +53–58 ms, borderline against its own faster FCP;
dev at +30–40 ms after it).

**Dev (3010), same real logout, same probe:** 1280 stamp at t = 57.1 (FCP 64), slot
`[449, 169, 382, 40.594]`, filled at 92.7, form 298.516 and sample 620.703 from the first frame, doc
922 throughout, **0 shift entries**; 390 stamp at 53.7 (FCP 60), slot `[33, 165, 324, 40.594]`,
filled at 80.6, form 294.516 and sample 612.703 from the first frame, doc 1048 throughout,
**0 shift entries**.

## The other five states

- **No flash — a plain visit to `/auth/login`** (fixed vs HEAD, both viewports): no `data-mj-*` stamp,
  no `<p>`, the slot generates **no box at all** (`getBoundingClientRect()` all zeros), document
  height **900 / 991** and form `[449, 241.922, 382, 221.188]` / `[33, 237.922, 324, 221.188]` — the
  same numbers HEAD produces. Full-page screenshots **`AE = 0`** at 1280 and 390 (the PNGs are
  byte-identical: 44,076 B and 32,956 B on both builds).
- **Filled — the band showing, settled** (fixed vs HEAD, both viewports): rect, `role="status"` and
  text identical, document 922 / 1048 identical, screenshots **`AE = 0`** (34,829 B on both at 390).
- **Typing into a field** retires the band exactly as at HEAD: doc 922 → 900 (1280) and 1048 → 991
  (390), form back to 241.922 / 237.922 on **both** builds — the stamp was already released, so no
  reserved gap survives the band.
- **Reload** after that: no flash, no stamp, no reservation, doc 900 / 991 — the channel was consumed
  by `readFlashOnce()` exactly as before.
- **A stale stamp cannot survive.** In every one of the six measured landings the post-fill frame
  reads `data-mj-auth-flash = null`. Two further probes: an **unrelated page** carrying the stamp
  (`/` with the key set) renders at document height **2154, identical with and without it** — the only
  rule keyed on the attribute is scoped to `.flashSlot`; and a **client navigation** into
  `/auth/login` while the stamp still stands (landing → nav 로그인 link) reserves the slot at
  `[169, 40.594]` in the surface's first commit and then fills it at the same rect, form 298.516 in
  both frames — 0 px there too, and the stamp released after.
- **Hydration:** console captured from document start on every measured load — **no warning, no
  error** in any of them (dev's only line is `[HMR] connected`).

## Cost

The head script grows **105 B**; the served page grows **234 B** (that literal plus its escaped copy
in the RSC flight payload — measured on `/`, where the two builds differ by nothing else), and
`/auth/login` **284 B** (the extra ~50 B is the empty slot `<div>`). The larger raw deltas on
`/stocks` (569 B) and `/portfolio` (802 B) are **chunk-filename length noise between two independent
builds** — an opcode diff of the two `/stocks` documents shows only `/_next/static/chunks/…` hashes
plus the script. Nothing is written, nothing is sent, nothing is loaded.

## Deviations

1. **`clearMirror("auth-flash")`, not `clearMirror("data-mj-auth-flash")`.** `clearMirror` prepends
   `data-mj-` itself (`PreHydration.tsx`, and the two existing callers pass `"lookup-holding"` /
   `"sample-removed"`), so the plan's spelling would have removed a `data-mj-data-mj-…` attribute.
   Naming shorthand in the plan, not a design change.
2. **The release is gated on a new `flashResolved`, not on `flash`.** Gating on `flash` alone never
   fires in the one pathological case — the stamp set at parse time but the key gone by the time the
   effect reads it (another tab, evicted storage) — and would leave a **permanent 40.59 px gap**.
   `flashResolved` is set in the same `setState` batch as `flash`, so the release still lands after
   the commit that renders the band (the plan's requirement) *and* covers the case where no band
   comes.
3. **One measured number, not two.** The plan asked for a measurement per viewport in case the
   sentence wraps at 390; it does not — the filled band is **40.59375 px** at 1280 and at 390 — so one
   rule serves both.
4. **The reader effect keeps `if (… === "logout") setFlash(true)`** rather than assigning the read.
   Strict Mode runs it twice in `next dev` and the second run reads a channel the first already
   consumed; assigning would blank the band in dev. Recorded as a comment beside it.

## Instrument, hygiene

**Aside `aside repl --account u2`** (profile 「claude2」), never `u0`. CDP through `page._sendToTarget`;
the probe installed once per invocation with `Page.addScriptToEvaluateOnNewDocument` **before** the
navigation, its `MutationObserver` on `document`; rects sampled every `requestAnimationFrame` and kept
as distinct states; `layout-shift` read as corroboration beside the rects, never as the evidence; the
product's own controls driven with `Input.dispatchMouseEvent` / `Input.insertText`. No new instrument
seam — the ones in `phase.md` were sufficient and all held.

The throwaway account (`p12f5.throwaway@example.com`) was created through the 계정 만들기 form,
used for six real 로그아웃 landings **before** it was deleted, and then deleted through 계정 삭제 on
the notifications surface (the API now answers `invalid_credentials` for it). Production was never
visited and never written to. Both fresh build copies live outside the repo; **3014 and 3015 are
stopped** and their ports free, and their profile storage was reset to an unedited sample.
`make stack-status` as found (postgres up, api 8010, web 3010). No test file added.
