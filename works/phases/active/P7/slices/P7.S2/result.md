# Result — P7.S2: login reachable (the chrome account slot answers in dev)

Operator item 5 is closed. **One file changed** — `frontend/components/chrome/useAccount.ts` — and
the chrome now renders 로그인 on the operator's own origin, with a full 계정 만들기 → 로그인 →
로그아웃 → 계정 삭제 round trip measured end to end in `next dev` and no test data left behind.

## The change

The probe effect lost its `live` cleanup flag; the `probedPath === pathname` check at resolve time
stayed:

```ts
useEffect(() => {
  if (probedPath === pathname) return;
  probedPath = pathname;
  void fetchAuthState().then((next) => {
    if (probedPath === pathname) setAccountState(next);
  });
}, [pathname]);
```

**Why the flag was the bug and not a safety net.** Under `next dev` the App Router tree is wrapped
in `React.StrictMode`, so the effect runs twice: run 1 claimed the module-level `probedPath`,
started the probe and then had its cleanup set `live = false`; run 2 returned early on the claim run
1 had just made. The single answer on the wire was discarded, `state` stayed `null` — "not answered
yet" — and `AccountSlot` rendered an empty `<div>` (desktop) / `null` (sheet) **for the whole
visit**. `next start` invokes the effect once, so production was never affected, which is why
`P5.S19` passed.

The flag is the wrong instrument regardless of StrictMode: what it guards is a **module** store
that outlives every component, so an answer landing after a subscriber unmounted is still the
answer the next subscriber wants. Two further facts make the removal safe, both checked in the
source rather than assumed:

- **Two effect runs cost one request.** `lib/session.ts`'s `fetchAuthState()` shares the in-flight
  probe, so the double invocation resolves to the same promise. Measured: exactly **1**
  `GET /api/auth/me` per page load, before and after.
- **A stale answer cannot overwrite a newer one.** Because at most one probe is ever on the wire,
  a second probe can only start after the first has settled (and therefore already published or
  been discarded by the `probedPath` check). The path check still does the job it was written for:
  an answer that lands after a client-side navigation moved the reader is dropped.

The doc comment gained a `## Why the probe carries no `live` cleanup flag (`P7.S2`)` section
recording the above. `components/auth/useAuthState.ts` was **not** touched (DECOMP note: its guard
is component state and self-heals). `AccountSlot.tsx` was not touched — the probe fix alone makes
it render.

## Before → after, `next dev`, fresh Chrome profile, `mijual.portfolio.sample` cleared

| check on `/` | `127.0.0.1:3000` before | `127.0.0.1:3000` **after** | `100.77.164.42:3000` **after** |
|---|---|---|---|
| desktop slot markup | `<div class="…__slot"></div>` | **`<a class="…__login" href="/auth/login">로그인</a>`** | same |
| `a[href="/auth/login"]` in the document | **0** | **2** (desktop slot + sheet row) | **2** |
| elements whose text is exactly 로그인 | **0** | **2** | **2** |
| mobile 390 sheet, opened | no 로그인 row | **`… AI 질문로그인의견 보내기`** | — |
| `GET /api/auth/me` per load | 1 → **discarded** | **1**, status 200, **published** | **1**, 200 |
| `position: fixed` nodes (hydration sanity) | 2 | 2 | 2 |

Two anchors, not one, is correct: the desktop slot and the mobile sheet row both live in the DOM at
every width and are shown by CSS.

## The round trip (127.0.0.1:3000, `next dev`, fresh profile, one browser session)

| # | action | observed |
|---|---|---|
| 1 | land on `/` anonymous | slot = 로그인; 1 probe |
| 2 | click the chrome's 로그인 | client-side nav to `/auth/login` (**0** document loads), panel renders |
| 3 | 계정 만들기 → `p7s2-probe@example.com` | `POST /api/auth/signup` **201** → `router.push` to `/portfolio` (**0** document loads, 1 `navigatedWithinDocument`) → slot switches **without a reload** to the 축약 이메일 menu button `p7s2…com` (`aria-haspopup="menu"`) |
| 4 | client-side nav to 관제 현황판 | slot still `p7s2…com` (**0** document loads) |
| 5 | open menu → 로그아웃 | rows are 내 포트폴리오 / 알림 설정 / 로그아웃; `POST /api/auth/logout` **200**; fresh load to `/auth/login`; slot back to **로그인**; 「로그아웃되었습니다」 shown once |
| 6 | 로그인 with the same credentials | **200** → `/portfolio`, account menu returns |
| 7 | 알림 설정 → 계정 삭제 | first click **arms** (계정 삭제 + 취소), second click → `DELETE /api/auth/account` **200** → lands on `/`; slot back to **로그인** |
| 8 | try to log in again | **401** + 「이메일 또는 비밀번호가 일치하지 않습니다.」 — the account is gone |

**Probes across the whole trip: 9 — exactly one per path visited** (`/`, `/auth/login`,
`/portfolio`, `/`, `/auth/login`, `/portfolio`, `/portfolio/notifications`, `/`, `/auth/login`).
Never two for one path, never zero.

**Test data.** The throwaway was `p7s2-probe@example.com`, created and deleted through the
product's own 계정 만들기 / 계정 삭제 controls. Confirmed in Postgres afterwards:
`select id, email from account` returns **one** row, `14 | s19-fidelity@example.com` — a
pre-existing `P5.S19` leftover, not this slice's — and the single `auth_session` row belongs to
that same account 14. Nothing of P7.S2's remains.

## Two regressions specifically checked for

- **R5-4 still outranks the slot.** With `mijual.portfolio.sample` in `localStorage` the slot renders
  `샘플` + `샘플 종료` and **0** 로그인 anchors, on `/portfolio?sample=1` and on the landing.
- **The only 4xx on a clean landing load is `/favicon.ico` 404** — pre-existing, unrelated to this
  slice, present in the before-run too.

## Production build

Built and served from an **isolated copy** of `frontend/` in session scratch (see Deviations), so
the dev server's `.next` was never touched:

- `npx next build` — **pass**, 16 routes, identical route table to `P7.S1`'s.
- `next start -H 127.0.0.1 -p 3100` — `/` serves 로그인 (`<a class="…__login" href="/auth/login">`),
  **2** anchors, **1** `GET /api/auth/me` → 200, **0** responses ≥ 400, 2 `position: fixed` nodes.
  The CSS chunk returned **200** before anything was believed (phase.md's `EADDRINUSE` trap).
  The server was stopped by the script that started it; `:3100` is free.

## Validation

| command | outcome |
|---|---|
| CDP before/after on `127.0.0.1:3000` (desktop 1440 + mobile 390) | table above — 0 → 2 로그인 anchors, 1 probe |
| CDP once on `100.77.164.42:3000` (Tailscale) | 2 anchors, 1 probe, 200 |
| CDP round trip: 계정 만들기 → 로그아웃 → 로그인 → 계정 삭제 | all 8 steps as tabled |
| `docker exec mijual-postgres psql -U mijual -d mijual -c "select id,email from account"` | one pre-existing row; the throwaway is gone |
| `cd frontend && npm run typecheck` | **pass** (`tsc --noEmit`, no output) |
| `cd frontend && npm run smoke` | **pass** — 15 passed, 0 failed |
| `npx next build` (isolated copy) + `next start -p 3100` probe | **pass** — see above |
| `python3 scripts/workflow.py validate` | **Workflow validation passed.** |
| `make stack-status` | postgres **Up (healthy)**, api **running** (pid 99133), web **running** (pid 13009) — left up, as found |

`git status` at the end: `frontend/components/chrome/useAccount.ts` is the only source file
changed. No commit, no state transition, no `doc-new-version`.

## Deviations from `plan.md`

1. **The production build ran in an isolated copy of `frontend/`, not in place.** The plan offered
   "stop web first and restart with `make web-up` after"; copying the sources to session scratch and
   building there is strictly safer — the running dev server and its `.next` were never touched at
   all, and the stack needed no restart. Two facts worth carrying forward: `next build` has **no
   `--dist-dir` flag** in 16.3.2 (`distDir` is config-only), and Turbopack **panics on a symlinked
   `node_modules`** that points outside the project root (`Symlink [project]/node_modules is
   invalid, it points out of the filesystem root`), so the copy has to be a real one (~354 MB, a
   few seconds).
2. **One adjacent sentence in the same doc comment was corrected**, beyond the StrictMode paragraph
   the plan asked for. It claimed "every mutation this app performs itself (로그인 · 로그아웃 ·
   계정 삭제) also publishes through `setAccountState`" — grep says `setAccountState` has exactly
   one caller outside this module, `NotificationsView`'s 수신 주소 변경. 로그인 lands on a new path
   (`AuthPanel` pushes `/portfolio`, which the per-path probe answers — measured in step 3 above)
   and 로그아웃 / 계정 삭제 leave through `window.location.assign`, which resets the module. Comment
   only; no behaviour change.
3. **A `frontend` Doc impact line was added** although `docs/current/frontend.md` does not describe
   the account probe (the plan's "otherwise none" branch). What is durable is the *trap*, and it
   belongs beside the dev-time traps that doc already lists. Trivial for `P7.REVIEW` to drop if it
   disagrees.
