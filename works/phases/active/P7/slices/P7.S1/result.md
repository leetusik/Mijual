# Result — P7.S1: dev origin unblock

Two files changed, no product code. `next dev` now serves its dev resources to the origins the
operator actually browses, and the six complaints that were one blocked origin are measured closed
**on `127.0.0.1` and on the Tailscale IP**, not only on `localhost`. The full measurement record,
the matcher facts and the notes later slices need are in [`../../phase.md`](../../phase.md)
(§Findings → "RC-A closed"); this file records what was done, what was validated and what it means
for the phase.

## What changed

- **`frontend/next.config.ts`** — an `allowedDevOrigins` seam beside the existing API seam:
  a static list (`127.0.0.1`, `[::1]`, `**.ts.net`) plus `MIJUAL_DEV_ORIGINS`, comma-separated
  hosts read from the environment. One comment block in the file's own style explains the block,
  the mechanism, why the tailnet IP is not a literal, and that the setting is dev-only.
- **`Makefile`** — `web-up` passes `MIJUAL_DEV_ORIGINS="$(TS_IP)"` into `next dev`, where `TS_IP`
  is the same `tailscale ip -4` lookup `stack-status` already printed (now hoisted to a variable
  and shared by both targets, so the URL that is printed and the origin that is allowed can never
  disagree). It echoes the effective origin list on start. The header comment no longer just
  claims both URLs "work" — it says why, and what to do when starting `next dev` by hand.

Nothing else was touched: no component, no copy, no API, no doc version, no state transition,
no commit.

## Why the tailnet IP goes through an env var instead of a wildcard

Next 16.3.2's matcher (`isCsrfOriginAllowed`) was read **and exercised** rather than assumed. It
compares hosts only, splits on `.`, pops segments from the right, and accepts `*` per segment and
`**` only as the leftmost segment. Consequences, all verified against the real module:

- `**.ts.net` matches Tailscale MagicDNS names; `100.**` is rejected outright.
- an IPv4 literal matches only exactly or by whole-octet wildcards: `100.64.*.*` matches
  `100.64.5.6` but **not** `100.77.164.42`, and the tailnet's 100.64.0.0/10 cannot be expressed.
- the only pattern that would cover it, `100.*.*.*`, opens **all of 100.0.0.0/8** — public address
  space included. That is a wider hole than this bug is worth, so the exact IP arrives from the
  Makefile through `MIJUAL_DEV_ORIGINS`.

The allow-list is still an allow-list. With the seam live, a `/_next/*` chunk requested with
`Origin: http://evil.example.com`, `http://100.1.2.3:3000` or `http://192.168.1.9:3000` still gets
**403**; `127.0.0.1`, `100.77.164.42` and a `*.ts.net` host get **200**.

## Measurements (headless Chrome over CDP, 1440×900, one dev server)

"before" is a genuine re-run of the baseline in this session: the original `next.config.ts` was
restored on disk, the dev server reloaded it by itself, and the origin was re-measured.

| check on `/` | `localhost:3000` | `127.0.0.1:3000` | `100.77.164.42:3000` |
|---|---|---|---|
| `/_next/*` 403s — before → **after** | 0 → **0** | 2 → **0** | 2 → **0** |
| HMR handshake — before → **after** | 101 → **101** | none (5 frame errors) → **101** | none (5 frame errors) → **101** |
| AI 질문 launcher in DOM — before → **after** | 1 → **1** | 0 → **1** | 0 → **1** |
| `position: fixed` nodes — before → **after** | 2 → **2** | 1 → **2** | 1 → **2** |
| countdown ticks over 2.6 s — before → **after** | yes → **yes** | no → **yes** | no → **yes** |
| 펼치기 ① 전환청구 진행 중 — before → **after** | 386→446 → **386→446** | 386→386 → **386→446** | 386→386 → **386→446** |
| 펼치기 ② 일정 추후결정 — **after** | **446→450** | **446→450** | **446→450** |
| typed 계양 after 150 s — before → **after** | kept → **kept** | wiped at 40 s → **kept** | wiped (DECOMP) → **kept** |
| top-frame navigations in 150 s — **after** | **0** | **0** | **0** |

`+60` and `+4` on the two strips match the board's `open_now` 60 / `tbd` 4 exactly. The two 403s
were always the same chunks (`_next/static/chunks/_03keo62._.js`,
`node_modules_next_0o9ro4l._.js`).

**One near-miss worth keeping:** the first pass waited 30 s for the reload and saw the value
survive on a *blocked* origin — a false negative. A dedicated watcher put the reload at **40 s**.
Any later slice measuring item 7 must wait ≥60 s.

### Deeper checks, all on `127.0.0.1` — the operator's own origin

- **AI 질문 (item 8), end to end.** Launcher clicked → widget open → composer typed with real key
  events → `POST /api/ask` **200** → 도구 행 「이벤트 검색 「계양전기」 → 1건 · ① 유상증자 ·
  20260724000546」 and 「이벤트 읽기」 → the answer with four DART 원문 citations → the 근거 footer.
  The turn completed and the composer returned to idle.
- **`/portfolio?sample=1` (item 9's action).** The 챙겼습니다 checkbox toggles: label flips
  놓친 돈 → **챙긴 돈** with the figure unchanged (`679,575원` + 「추정」), exactly R5-8.
- **`/auth/login` (item 5's form).** Submitting a wrong password round-trips —
  `POST /api/auth/login` → **401**, and the form renders 「이메일 또는 비밀번호가 일치하지
  않습니다.」. No account was created.

### The production build is untouched

`allowedDevOrigins` is read only by the dev router server (`router-server.js:207/336/669`, all
behind `development`). Empirically: `npm run build` succeeded, and `next start -H 0.0.0.0 -p 3100`
served **0** 403s, 1 launcher, 2 fixed nodes, ticking countdowns and working 펼치기 (386→446→450)
on **both** `127.0.0.1:3100` and `100.77.164.42:3100`, with no HMR socket at all. That is the
`P5.S19` / `P6.S7` gap in one sentence: **production was always fine on every origin; dev was
broken on every origin except `localhost`.** The prod server was killed afterwards and :3100 is
free.

## Operator items closed by this slice, with no further product code

| item | evidence on `127.0.0.1` |
|---|---|
| **4b** 펼치기 does nothing | 386 → 446 rows, `aria-expanded` false → true; ② strip 446 → 450 |
| **6** countdown static | digits change over 2.6 s |
| **7** auto reload wipes typing | 150 s, value kept, marker alive, 0 navigations (was: reload at 40 s) |
| **8** AI 질문 can't send | full turn streamed, `POST /api/ask` 200, tool rows + citations + 근거 footer |
| **11** no widget | launcher present (1), fixed nodes 2 |
| **5** (hydration half) | login form reaches the API — 401 + the signed error sentence |
| **9** (hydration half) | 챙겼습니다 flips 놓친 돈 → 챙긴 돈, same figure, 「추정」 kept |

Not closed here, and deliberately so: **5**'s real cause (RC-B, `useAccount` — `P7.S2`), **9**'s
layout tidy (`P7.S8`), and 의견/vocky (an operator decision, Open Question Q1). Nothing failed to
close that was expected to.

## Validation

| command | outcome |
|---|---|
| `cd frontend && npm run typecheck` | **pass** (`tsc --noEmit`, no output) |
| `cd frontend && npm run smoke` | **pass** — 15 passed, 0 failed |
| `cd frontend && npm run build` | **pass** — 16 routes, then started on :3100 for the prod check and stopped |
| CDP probes, 3 origins × before/after | table above; after-state has 0 403s and a 101 handshake everywhere |
| `curl` origin matrix against a live `/_next/*` chunk | allowed 200 ×3, foreign 403 ×3 |
| `grep -c "Blocked cross-origin" var/stack/web.log` | **4** since the restart — all four are the deliberate negative controls (`evil.example.com` ×2, `100.1.2.3`, `192.168.1.9`); **none from `127.0.0.1` or the tailnet IP**. Pre-fix log kept at `var/stack/web.log.pre-p7s1` (11 lines, all from the operator's own origins) |
| `make stack-status` | postgres **Up (healthy)**, api **running** (pid 99133), web **running** (pid 13009) — left up |
| `python3 scripts/workflow.py validate` | **Workflow validation passed.** |

## Doc impact (appended to `phase.md`, no `doc-new-version`)

- `frontend` — the existing line was **extended**: the `P5.S19` browser-check note
  (`docs/current/frontend.md:313`) now inverts — dev verification runs on `127.0.0.1` and the
  Tailscale origin, never `localhost`, because `localhost` is the one origin that could never show
  this defect class; plus the seam itself and the matcher's limits.
- `operations` — **new line**: `MIJUAL_DEV_ORIGINS` belongs in the Environment Variables table
  (frontend, dev-only, filled by `make web-up` from `tailscale ip -4`).

## Deviations from `plan.md`

1. **No `100.*.*.*` wildcard in the static list**, though the plan floated one. The matcher does
   support it (tested), but it would allow all of 100.0.0.0/8 rather than Tailscale's
   100.64.0.0/10, which the matcher cannot express. The env seam covers the case exactly instead.
   `[::1]` and `**.ts.net` were added for free; `[::1]` is inert while the server binds
   `-H 0.0.0.0` (v4 only) and the file says so.
2. **The "before" column was re-measured, not copied.** The dev server auto-reloads
   `next.config.ts`, so the first "before" pass was already contaminated by the edit. The original
   config was restored on disk, the baseline re-measured (it reproduced `P7.DECOMP` exactly), then
   the fix restored. Nothing else was reverted and the tree ends with only the two intended edits.
3. **Item 7 was measured over 150 s, not 30 s** — 30 s sits below the ~40 s reload and produced a
   false negative in both directions.
4. **The prod check also ran on the Tailscale origin**, not only `127.0.0.1:3100`, since that is
   the origin the claim "dev-only" is really about.
