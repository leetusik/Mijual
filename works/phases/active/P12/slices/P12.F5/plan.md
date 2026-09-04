# P12.F5 — `/auth/login`: the 로그아웃되었습니다 flash lands after paint and pushes the form 56.6 px (R1 F4)

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.F10` (`3435d1f`). **Family A**, the pre-hydration mirror seam's fourth use — the
head half, the easiest case.

## Read first

- `phase.md`: `## Decisions` — the seam line (F3), F4's and F10's lines (the reservation pattern
  and the release rule), the instrument seam with F3's additions, the build recipe; the shared
  bar (keep it); F1's measurement-seams note; and the **two notes tagged `for P12.F5`** (F3: head
  half, `data-mj-auth-flash`, keep `readFlashOnce`'s 1회 표시 semantics and write moment; F4:
  place the script where the parser meets it before the thing it reserves, **`min-height` never
  `height`**, release in an effect gated on the state that *fills*). Consume both.
- `slices/P12.R1/result.md` § F4 — the "before": after 로그아웃, `/auth/login` paints, then
  `p.Auth-module__flash` 「로그아웃되었습니다」 `[449, 169, 382, 40.59]` is inserted at **+27 ms after
  FCP**, **CLS 0.00973**, `Auth__form` y 241.92 → 298.52 and `Auth__sample` 564.11 → 620.70, both
  **+56.6 px** (the box plus the panel's gap).
- The code: `components/auth/AuthPanel.tsx` (`flash` starts `false`; the effect at ~L119 reads
  `readFlashOnce() === "logout"`; rendered at ~L198 as `<p className={styles.flash} role="status">`
  above the form; `setFlash(false)` on the first field change at ~L129), `lib/session.ts`
  (`readFlashOnce` reads **and clears** `sessionStorage["mijual.auth.flash"]` — the read is the
  consumption; `writeFlash` is called by 로그아웃 before a fresh document load),
  `Auth.module.css` (`.flash`: padding 10px 14px, hairline, `--text-sm`; the panel's layout and
  its gap), `app/auth/login/page.tsx` (a server component: redirect when authenticated, else
  `<AuthPanel />` — it must **not** learn about the flash; no cookie, no query param), and
  `components/chrome/PreHydration.tsx` (`HEAD_SOURCE`, `clearMirror`, the header table).

## The change

1. **Stamp — head half.** In `HEAD_SOURCE`, read `sessionStorage["mijual.auth.flash"]` (one more
   `getItem` inside the same `try`) and stamp `data-mj-auth-flash="logout"` when the value is
   exactly `"logout"`. Do **not** clear the key there — `readFlashOnce()` stays the one consumer,
   called at the same moment as today. Add the header-table row.
2. **Reserve — the slot pattern.** `AuthPanel` renders a slot at the flash's position (F3's
   `display: contents` shape: empty → not a layout box, so the no-flash page is byte-identical;
   filled → lays out as if the wrapper were not there), and one rule reserves under the stamp:
   `html[data-mj-auth-flash="logout"] .flashSlot:empty { display: block; min-height: … }` —
   `min-height`, measured on the fixed build against HEAD's filled flash at **1280 and 390**
   (the sentence may wrap at 390 — measure, do not assume 40.59), and whatever the panel's gap
   needs so the reserved slot occupies exactly what the filled `<p>` occupies (56.6 total at
   1280). The existing effect then fills the slot with the same `<p className={styles.flash}
   role="status">` — same copy, same style, same `role`.
3. **Release.** `clearMirror("data-mj-auth-flash")` in an effect gated on `flash` (after the
   commit that renders the line), never in the effect that reads the key. Then the first field
   change removes the flash exactly as today (a user-initiated change; unchanged behaviour), and
   a reload shows no flash and no reservation (the key was consumed).
4. Nothing else: the redirect logic, the two modes, the reset panel, `writeFlash`, and the
   sentence are untouched. **RESPECT THE DESIGN.** (R1 F10 — the panel growing on 로그인 ↔ 계정
   만들기 — is `P12.F6`'s; do not touch it here.)

Why not F3's other shape (server-render the line, CSS-hide when not flagged): it would put the
sentence and a `role="status"` element into every login page's HTML for a message that exists on
one visit in a hundred; the reserve-slot shape touches nothing in the common case. Take the slot.

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`; `npm run build` in a fresh copy (no
  warnings).
- **Controls:** HEAD production build on 3015 beside the fixed build 3014, plus dev 3010. On each
  port: create the throwaway account through the signup form, sign in, then **로그아웃 from the
  account menu** so the browser lands on `/auth/login` with the flash — measure that landing.
- **Before/after**, Aside `--account u2`, **1280 and 390**, dev + fixed vs HEAD: the R1 probe
  (late-insert timeline, layout-shift observer with sources, rect diff on `.Auth-module__form`,
  `.Auth-module__sample`, the panel). Pass = the stamp is on `<html>` before FCP, the slot is
  reserved from the first frame, the `<p>` fills it with **0 px** movement of the form and the
  sample entry (CLS from this source 0), filled rect and text identical to HEAD's flash. Then
  **no flash** (a plain visit to `/auth/login`): no stamp, page `AE = 0` vs HEAD at both
  viewports. Then type into a field: the flash leaves as at HEAD; reload: no flash, no
  reservation. Then a **stale stamp** cannot survive: after the fill, `<html>` carries no
  `data-mj-auth-flash`.
- **Hydration:** console capture on every measured load — no warning, no error.
- Hygiene: the logout measurement happens **before** the account is deleted (deletion lands
  signed out on `/`, not here); delete it through 계정 삭제 at the end; production read-only;
  3014/3015 stopped; `make stack-status` as found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the logout flash reserves its line from `data-mj-auth-flash` (files,
  measured heights per viewport, the release point, the after-numbers).
- `## Doc impact`: `frontend.md` — Surfaces / 로그인 panel: the flash no longer inserts after paint
  (the seam's fourth use; the attribute; the reservation) (P12.F5).
- `## Notes for later slices`: consume the two `for P12.F5` notes. Add `**(from P12.F5, for
  P12.F6)**` only if you learned something about `AuthPanel`'s layout that the mode-switch fix
  needs (F6 touches the same file — say which lines you changed so it does not collide). Do not
  touch the shared bar, F1's seams note, or the `for P12.REVIEW` notes.
- `## Now` (≤ 15 lines): F5 landed with numbers; `P12.F6` next (Family B, three components, the
  `Nav.module.css` ghost); freeze date; production on `a74c58a`.

`result.md`, verdict block first, before/after tables at both viewports.

## Do not

- carry the flash through the server (no cookie, no query param, no header), clear the key
  anywhere but `readFlashOnce`, change the sentence or its style, touch the mode switch, add a
  test file, commit, run any workflow state command, write on production, or drive Aside `u0`.
