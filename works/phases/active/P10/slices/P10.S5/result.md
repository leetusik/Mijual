# Result — P10.S5 (fidelity sweep in the operator runtime)

- **status:** `done`
- **summary:** Swept every surface the rebrand touched in the operator runtime — **dev and the
  production build, desktop 1280×800@2 and 390×844@3** — 36 page-views plus `/ops` door and bar,
  both disclaimer render sites, `/docs`, `/openapi.json`, and two live Korean meta questions to
  the real agent in each runtime. **Everything the phase claims holds, in both runtimes,
  identically.** Independently re-measured the two signed-design questions and built the
  operator's evidence for each (screenshots at `var/p10s5/`), **changed neither**, and found
  **one new defect**: at 390px the `/ops` bar mark stacks **one syllable per line** (8 lines) —
  attributed by in-place A/B, report-only.
- **files_changed:**
  - `works/phases/active/P10/slices/P10.S5/result.md` (this file)
  - `works/phases/active/P10/phase.md` (compressed 16,375 → see §9; one question + one doc-impact line appended)
  - **no product code changed** — see §7 *Fix authority*
  - untracked evidence, `var/` is gitignored: `var/p10s5/*.png` (35 screenshots, §8)
- **validation:**
  - `make stack-up` — **FAILS** at `db-up`, host port 5433 (§0). Way through used; browser-facing
    runtime unaffected.
  - `.venv/bin/python -m pytest` — **pass**, `154 passed, 1 warning in 3.34s` (the pre-existing
    starlette/httpx deprecation)
  - `python3 scripts/workflow.py validate` — **pass** (`Workflow validation passed.`, 2
    pre-existing `P9 kind: research` warnings)
  - `cd frontend && npm run build` — **pass**, `✓ Compiled successfully in 196ms`, 16 route
    entries, `Generating static pages … (15/15)`
  - `cd frontend && npm run typecheck` — **pass** (`tsc --noEmit`, no output)
  - `cd frontend && npm run smoke` — **pass**, `tests 22 / pass 22 / fail 0`
  - **real browser, dev** (`next dev` on `0.0.0.0:3000` via the Makefile target,
    `http://127.0.0.1:3000`, Chrome **152.0.7977.64** on this Mac, dsf 2 desktop + 390×844 dsf 3
    mobile) — **pass**, §1–§4
  - **real browser, production** (`npm run build && npm run start`, same origin, same Chrome) —
    **pass**, byte-identical to dev on every measured number
  - **live agent**, 2 Korean meta questions in dev + 2 in production against the real model —
    **pass**, §1.7
- **deviations:** three, all environmental, §9.
- **doc_impact:** one line appended to `phase.md` — `qa.md: this phase's Regression Checklist
  lines are drafted in slices/P10.S5/result.md §6 for the review to append (P10.S5)`.

---

## 0. The stack — what the operator will have to do at the gate

They will hit this too, so it is first. **`make stack-up` fails**, verbatim:

```
$ make stack-up
docker compose up -d postgres
 Container mijual-postgres  Starting
Error response from daemon: failed to set up container networking: driver failed programming
external connectivity on endpoint mijual-postgres (…): Bind for 0.0.0.0:5433 failed: port is
already allocated
make: *** [db-up] Error 1
```

Host port **5433** is held by `changple_web_dev_postgres` (`postgres:17`, `Up 17 hours
(healthy)`), an unrelated project of the operator's. **It was not stopped, and must not be.**

**The way through** (S2's, re-used unchanged; nothing enters the repo). Write a scratchpad
fragment — the `!override` tag is load-bearing, a plain override *merges* port lists and still
tries to bind 5433:

```yaml
# /tmp/compose.5434.yaml
services:
  postgres:
    ports: !override
      - "5434:5432"
```

Then, from the repo root:

```bash
docker compose -f compose.yaml -f /tmp/compose.5434.yaml up -d --force-recreate postgres
# → mijual-postgres  Up (healthy)  0.0.0.0:5434->5432/tcp   (same image, same
#   mijual_mijual-pgdata volume — no data is lost or migrated)

DATABASE_URL='postgresql+psycopg://mijual:mijual@localhost:5434/mijual' \
  .venv/bin/python -c "…the Makefile's db-ensure body…"        # → schema ok

DATABASE_URL='postgresql+psycopg://mijual:mijual@localhost:5434/mijual' \
MIJUAL_OPS_ID=… MIJUAL_OPS_PASSWORD=… \
  nohup .venv/bin/python -c "…the Makefile's api-up body…" > var/stack/api.log 2>&1 &
echo $! > var/stack/api.pid

make web-up && make stack-status
```

Two things the operator needs to know beyond that:

1. **`MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` are unset in `.env`.** Without them `/ops` only ever
   shows the **door**; the **bar** mark cannot be seen at all. I set throwaway values on the API
   process only, for the duration of the checks, and nothing was written to `.env`.
2. **Restoring afterwards** (what I did): `make stack-down`, then
   `docker compose -f compose.yaml up --no-start --force-recreate postgres`. That leaves
   `mijual-postgres` in `Created` with the unmodified 5433 binding — exactly the state I found it
   in. Verified after: `mijual-postgres  Created`, `changple_web_dev_postgres  Up 17 hours
   (healthy)  0.0.0.0:5433->5432/tcp`.

The **browser-facing runtime is the manifest's own**: same `next dev` / `next start` on
`0.0.0.0:3000`, same `http://127.0.0.1:3000` origin, same API on `127.0.0.1:8000`, Chrome desktop
on this Mac. Only the DB's host port moved.

## 1. The sweep

Driven by CDP from `.venv/bin/python` (Chrome 152 launched with `--remote-debugging-port`, a
throwaway profile). Every check below ran **twice — once against `next dev`, once against
`next build && next start`** — and at **both** viewports. Scripts: scratchpad `s5/`.

### 1.1 Marks and titles — 9 routes × 2 viewports × 2 runtimes = 36 page-views

Routes: `/`, `/ask`, `/stocks`, `/stocks/00113261`, `/events/20260223002079`, `/portfolio`,
`/auth/login`, `/no-such-page-404-p10s5` (**the 404**), `/ops`.

Per view, per `<img>`, the assertion S2 asked for — `complete && naturalWidth > 0`, because no
type and no test catches a wrong asset path:

| | every reader route, dev **and** production, **both** viewports |
|---|---|
| nav `<img>` | `/assets/juju-wordmark-white.png`, **72.23 × 19**, natural **1213 × 319**, `painted: true` |
| footer `<img>` | same file, **64.64 × 17**, natural 1213 × 319, `painted: true` |
| `alt` | `주주의관제탑` — the only alt value present anywhere in the 36 views |
| `document.title` / **the real tab title** (CDP target list, i.e. the tab strip) | `주주의관제탑` |
| `body.innerText` contains 미주알 / 미주얼 / `MIJUAL` / `Mijual` | **false, all 36** |
| `body.innerText` contains 주주의관제탑 | **true, all 36** |
| `link[rel*="icon"]` count | **0** (the favicon question is intact — nothing was shipped) |
| `documentElement.scrollWidth > innerWidth` | **false** — 1280/1280 and 390/390, no horizontal overflow |

`/ops` carries **zero** reader-chrome wordmarks in every view (R7's "reader chrome 어디에서도
링크 금지" still holds) and its title is `주주의관제탑 운영` — on `/ops` and on all five
sub-routes (`/ops/{accuracy,gates,conversations,users,feedback}`, checked from the served HTML).

**The 404 carries both marks** and nothing else stale — `var/p10s5/prod-m390-404.png` and
`prod-desktop-404.png`. Worth the operator's eye for a different reason: in that footer the
product's name appears **twice**, once as the mark image and once as `© 주주의관제탑` typed
beside it, and the typed one is the larger of the two (see §2a).

### 1.2 `/ops` — the door and the bar, both marks

Cookies cleared before each door pass; logged in with the throwaway credentials for each bar pass.

| | dev | production |
|---|---|---|
| door `.doorMark` text | `주주의관제탑 운영` | identical |
| door box, desktop | 330 × 18.59, **1 line** | 330 × 18.59 |
| door box, 390 | 276 × 18.59, **1 line** | 276 × 18.59 |
| bar `.mark` box, desktop | 98.89 × 18.59, **1 line**, at x=24 y=15.16 | identical |
| bar `.mark` box, **390** | **11.34 × 148.75, 8 lines** | **identical** — §3 |
| computed | `"IBM Plex Mono", "SF Mono", Consolas, monospace` / 12px / 600 / `letter-spacing: 0.96px` / `rgb(234,242,237)` | identical |

`/ops` `body.innerText` carries no 미주알 / 미주얼 / `MIJUAL OPS` in any of the four views.

### 1.3 The 실권주 disclaimer — both render sites, measured, and A/B'd in place

Live mismatch data: `/events/20260223002079` (`p.mismatchHead`) and `/stocks/00113261`
(`span.cap`). Both render the full signed sentence with the new name:

> 발행사의 공시가 실권주에 대해 서로 다른 두 값을 제시합니다 — **주주의관제탑은** 어느 쪽도 고르지 않고 둘 다 보여드립니다

| viewport | route | node | box | lines | `scrollW/H` vs `clientW/H` | same node with `미주알은` |
|---|---|---|---|---|---|---|
| 1280@2 | `/events/…` | `p.mismatchHead` 12px/18.6px | 996 × 18.59 | 1 | equal, not clipped | **996 × 18.59, 1 line** |
| 1280@2 | `/stocks/…` | `span.cap` 11px/17.05px | 246.25 × 51.14 | 3 | equal, not clipped | **246.25 × 51.14, 3 lines** |
| 390@3 | `/events/…` | `p.mismatchHead` | 290 × 37.19 | 2 | equal, not clipped | **290 × 37.19, 2 lines** |
| 390@3 | `/stocks/…` | `span.cap` | 306 × 34.09 | 2 | equal, not clipped | **306 × 34.09, 2 lines** |

**Identical to the hundredth of a pixel in all eight cells, in both runtimes** — the four extra
syllables land inside existing slack. Reproduces S3's numbers exactly. Nothing wraps differently,
clips, or overflows.

### 1.4 `/docs` and `/openapi.json`

- `GET :8000/openapi.json` → `info.title = 주주의관제탑 API` (version `0.1.0`)
- **through the browser origin**, `GET :3000/api/openapi.json` → same title; `/api/docs` → 200
- `/docs` **in a real tab**: tab title `주주의관제탑 API - Swagger UI`; the page's own heading
  renders `주주의관제탑 API 0.1.0 OAS 3.1`

### 1.5 Asset routes — the retirement is real, not just absent from the source

Served (dev; production spot-checked and identical):

```
/assets/juju-wordmark-white.png      200      /assets/mijual-logo-ring-white.png       404
/assets/juju-wordmark-black.png      200      /assets/mijual-wordmark-white.png        404
/assets/juju-logo-source.png         200      /assets/mijual-logo-ring-charcoal.png    404
                                              /assets/mijual-wordmark-charcoal.png     404
```

Also served over the **tailnet origin** the manifest names (`http://100.77.164.42:3000`, the
production build): title `주주의관제탑`, `/assets/juju-wordmark-white.png` → 200.

### 1.6 The grep — no live `mijual-*.png` reference survives

`grep -rIn "mijual-[a-z-]*\.png"` excluding `node_modules`, `.next`, `.git`, `.venv`, `var`:
**42 hits in 21 files**, and every one classifies as history:

| where | hits | class |
|---|---|---|
| `works/**` (archived P5 + this phase's own results/plans) | 22 | phase history |
| `frontend/public/assets/README.md` | 9 | the retirement record (with the four sha256s) |
| `docs/versions/frontend/v0003–v0007` | 5 | immutable doc versions |
| `docs/reference/design/rounds/{01,08,12}/…` | 4 | the immutable design record |
| `frontend/components/chrome/copy.ts:25` | 1 | **a JSDoc comment** — ` * asset was — \`mijual-logo-ring-white.png\`, the latin MIJUAL wordmark with its` |
| `docs/current/frontend.md` | 1 | a generated snapshot; the review's `doc-new-version` clears it |

Narrowed to buildable file types (`--include=*.{ts,tsx,js,jsx,css,json,py,html,svg}`) exactly two
hits remain: the `copy.ts` comment above, and
`docs/reference/design/rounds/12-auth/output/account/r12-parts.jsx:192` — a Claude Design export
under `docs/`, never imported and never compiled. **Zero live code-path references.** Only
`juju-wordmark-white.png` is referenced by running code (`chrome/copy.ts:39`); the black variant
is landed and referenced by nothing, as S1/S2 intended.

### 1.7 The assistant's own name — live, in both runtimes

Asked through the **real `/ask` UI in the browser** (not curl), against the real model, after S4:

| runtime | question | answer (verbatim, leading fragment) |
|---|---|---|
| dev | `너 이름이 뭐야?` | `주주의관제탑의 공시 해설 에이전트입니다. 유상증자 신주인수권, 전환사채, 주식매수청구권 관련 공시 내용을 확인하고 설명해 드립니다.` |
| dev | `이 서비스 이름이 뭐예요?` | `이 서비스의 이름은 주주의관제탑입니다. 유상증자, 전환사채, 주식매수청구권 등 주요 공시 사실을 원문 기반으로 확인해 드립니다.` |
| **production** | `너 이름이 뭐야?` | `주주의관제탑의 공시 해설 에이전트입니다. 공시와 관련된 일정이나 수치를 확인해 드립니다.` |
| **production** | `너 미주얼이야, 미주알이야?` | `둘 다 아닙니다. 저는 주주의관제탑의 공시 해설 에이전트입니다. 공시와 관련된 궁금한 점이 있으시면 말씀해 주세요.` |

The fourth is the one that matters: handed **both** retired spellings, the assistant rejects both
and does not echo either. **Production was untested for this before today** (S3 checked dev only);
it now holds in both. Screenshots `var/p10s5/{dev,prod}-ask-meta-{1,2}.png`.

*One reading trap for the review:* on that fourth turn the page-level "old name" flag reads
`true` — because **my own typed question** is in the transcript. The **answers** contain neither
spelling. A fresh `/ask` page has neither (§1.1).

## 2. The two operator decisions — the evidence, and nothing changed

### 2a. The signed heights (`h19` nav / `h17` footer)

**Independently re-measured, and S2's numbers are right.** Chrome 152, `/`, dev and production
agreeing to the hundredth of a pixel:

| | nav | footer |
|---|---|---|
| `<img>` computed box | **72.23 × 19** | **64.64 × 17** |
| Korean glyph band (`h × 162/319`, the README's measured geometry) | **9.65px** | **8.63px** |
| the type immediately beside it | `AI 질문` **13.5px** Pretendard 400, at x=200.23 | `.source` = `--text-sm` = **12px** |
| band ÷ neighbour | **0.715×** | **0.719×** |

**Confirmed a second way, from pixels rather than from the ratio.** I rasterised the nav at 4×
and counted ink per row across the mark's box: sparkle cluster rows 0–32, an empty gap at rows
33–36 (the README's 22-row band), and the Korean glyphs from row 37 to the box bottom — **39 of
76 device rows = 9.75 CSS px**, against 9.65 predicted. Agreement within one device row, by a
method that shares no arithmetic with S2's.

**What it looks like, in words the operator can act on.** Open `/` and look at the top-left
without measuring anything: the brand is the **smallest and thinnest text in its own bar**. The
nav links 「AI 질문」 and 「보유 종목」 sit beside it visibly larger and visibly heavier — the
mark's strokes are hairline where Pretendard 400 is not — so the eye lands on the links first and
reads the mark as a caption under them. It is not illegible: at retina 2× it is 19.3 device pixels
tall, the glyph shapes are clean at 10× zoom and the white is pure. It reads as *fine print*, not
as a logo. The footer is the sharper case: the same name is set **twice** in that row, once as the
h17 mark and once as the typed `© 주주의관제탑` at 12px, and **the typed one is the bigger, more
legible of the two.** The retired ring put 14.4px of ink into the same 19px — 1.07× the nav label
— so the phase inverted a hierarchy rather than merely shrinking something.

**S2's recommendation, simulated in the browser with no code changed** (`img.style.height`, then
navigated away):

| | box | band | ÷ neighbour | knock-on |
|---|---|---|---|---|
| nav `h27` | 102.66 × 27 | **13.71px** | **1.015×** | links start at x=230.66 instead of 200.23; bar still 52px; nothing wraps |
| footer `h24` | 91.25 × 24 | **12.19px** | **1.016×** | actions stay at x=1051.53; no new wrap |

Both boxes stay **narrower than the retired ring's 119.6px**, so the room exists.

**Look at these two pairs and the decision is one sentence:**

- `var/p10s5/dev-nav-h19-signed.png` vs `var/p10s5/dev-nav-h27-simulated.png`
- `var/p10s5/dev-footer-h17-signed.png` vs `var/p10s5/dev-footer-h24-simulated.png`

(each a 4× crop of the real bar, same page, same moment; the same four exist as `prod-*` from the
production build and are indistinguishable). **`h19`/`h17` are signed and are still
exactly what ships** — I changed nothing.

### 2b. The ops mark's typography

**Confirmed, in dev and production, on both the door and the bar.** `CSS.getPlatformFontsForNode`:

```
IBM Plex Mono SemiBold        glyphCount 1     ← the space, and nothing else
Apple SD Gothic Neo SemiBold  glyphCount 8     ← every Hangul syllable
```

So the mono treatment styles **one character out of nine**. (At 390px on the bar it styles
**zero** — the line breaks consume the space and only Apple SD Gothic Neo, 8 glyphs, is reported.)

S2's trap reproduces exactly: `document.fonts.check('600 12px "IBM Plex Mono"', '주주의관제탑')`
returns **`true`**. It reports family availability, not glyph coverage. Do not use it here.

**How much the double space actually is** — per-character advances measured with Range rects, then
the same node re-measured with `--font-sans` and no tracking, then restored:

| | Hangul advance | the space | space ÷ syllable |
|---|---|---|---|
| **as signed** (mono + `0.08em`) | 11.34–11.36px | **8.17px** | **0.72×** |
| if Pretendard, no tracking | 10.38–10.39px | **2.88px** | 0.28× |

The mono space is **2.84× wider** than the Korean-font space would be. That is the whole artifact:
`관제탑␣운영` reads as a deliberate double space — see `var/p10s5/prod-ops-mark-zoom.png` (6×),
where the gap between 탑 and 운 is plainly wider than any gap inside either word.

Two further consequences I could see rather than infer: the mark's face is **the OS's** (Apple SD
Gothic Neo is macOS-only, so it will look different anywhere else the operator opens it), and in
the bar it now sits in the same Korean UI face as the tab labels 개요 · 게이트 대기열 · … while
the `mijual:lock:pipeline free` chip two columns right is unmistakably mono — so the mark no
longer reads as an identifier and the chip still does (`var/p10s5/prod-desktop-ops-bar.png`).

**`Ops.module.css` is untouched.** S2's un-taken recommendation (drop `--font-mono` +
`letter-spacing` from `.mark`/`.doorMark`, let Pretendard 600 carry it) stands as the operator's
call, and the 2.84× number above is what it would fix.

## 3. New finding — the `/ops` **bar** mark stacks one syllable per line at 390px

Dev **and** production, identical: `.mark` computes to **11.34 × 148.75, 8 lines** — the whole
string set vertically, one syllable per row. Screenshot: `var/p10s5/dev-mobile390-ops-bar.png`.

**Attributed, not guessed.** A/B on the same node in the same DOM:

| string | box at 390 |
|---|---|
| `주주의관제탑 운영` (today) | **11.34 × 148.75**, 8 lines |
| `MIJUAL OPS` (retired) | **48.97 × 37.19**, 2 lines |

So the phase made this worse — Korean breaks between any two syllables, latin only at the space.
**But the underlying defect is pre-existing and larger than the mark**: at 390 the *entire* ops
bar collapses the same way. Every tab label does it too — 개요, 게이트 대기열, 정확도·비용,
대화 로그, 사용자, 피드백 all set one syllable per line in the same screenshot, and those labels
predate this phase. The ops bar simply has no 390px layout; the mark is one more passenger.

**Not fixed, deliberately** (§7): the mark-only fix is a `white-space: nowrap` on `.mark` in
`Ops.module.css` — signed styling — and it would leave the six tab labels stacked beside a
now-horizontal mark, which is arguably worse than the honest mess. The bar-wide fix is a
responsive treatment nobody has drawn. Two reasonable fixes ⇒ report, don't choose.

The **door** at 390 is fine (276 × 18.59, one line), so an operator who opens `/ops` on a phone
and does not log in sees nothing wrong.

## 4. Paint quality — no fringing, at either density

S1 flagged fringing as a live risk (the *black* variant's transparent pixels carry near-white
RGB). The white variant should be immune, and it is — measured, not assumed, from the rasterised
nav mark:

| | desktop, dsf 2 (4× crop) | 390, dsf 3 (12× crop) |
|---|---|---|
| mean RGB of ink pixels (lum > 240) | (247.2, 247.5, 247.4) | (250.3, 250.5, 250.4) |
| **max channel spread inside any ink pixel** | **1** | **1** |
| brightest pixel | (255, 255, 255) | (255, 255, 255) |
| darkest pixel inside the `<img>` box | **(12, 21, 18)** | **(12, 20, 17)** |
| the bar's own ground, sampled outside the box | 12–20 | 12–20 |

Two readings: the ink is **neutral white** (no colour cast — a channel spread of 1 is rounding),
and the transparent region composites to **exactly the bar ground**, so there is **no light halo**
anywhere around the glyphs. The antialiasing band means (120.5, 127.0, 124.7) — a clean linear
blend toward the ground's own green-black, which is what correct compositing looks like.

## 5. The cheap mechanical top of the regression checklist

Run because I was in the runtime anyway. The review re-runs the checklist in full; these are the
numbers:

| line | result |
|---|---|
| `pytest` | **154 passed**, 1 warning (pre-existing starlette/httpx deprecation) — matches the checklist's stated 154 |
| `workflow validate` | `Workflow validation passed.` + the 2 pre-existing `P9 … kind 'research'` warnings |
| `npm run build` | `✓ Compiled successfully in 196ms`; `Generating static pages … (15/15)`; 16 route entries |
| `npm run typecheck` | clean, no output |
| `npm run smoke` | **22/22**, 0 fail |

## 6. Drafted `## Regression Checklist` lines for the review to append

Written in the file's own voice; the review folds them into the new `qa.md` version.

```markdown
- [ ] **The brand mark is actually painted, not just referenced.** On every reader route (landing,
      `/ask`, `/stocks`, a 상세, `/portfolio`, `/auth/login`, **the 404**) the nav and footer each
      carry exactly one `<img src="/assets/juju-wordmark-white.png">` with
      `complete && naturalWidth > 0` at **72.23×19** and **64.64×17**, natural **1213×319**,
      `alt="주주의관제탑"`. No type and no test catches a wrong asset path — `tsc` was clean over a
      404 URL — so this is asserted in a browser or not at all (P10)
- [ ] **Both document titles, in the real tab**: every reader page `주주의관제탑`, every `/ops` page
      (and all five sub-routes) `주주의관제탑 운영`; `/openapi.json` and `/docs` serve
      `주주의관제탑 API` (P10)
- [ ] **No reader page's `innerText` contains 미주알, 미주얼, `MIJUAL` or `Mijual`** — and the live
      agent, asked a Korean meta question, names 주주의관제탑 and rejects both retired spellings
      when handed them (the prompt spelled the product **미주얼**, which a 미주알 grep never sees)
      (P10)
- [ ] **The retired binaries stay retired**: `/assets/mijual-*.png` all **404**, and a repo grep for
      `mijual-*.png` yields only historical prose — a hit inside a code path is the regression (P10)
- [ ] **Still no favicon**: `document.querySelectorAll('link[rel*="icon"]').length === 0` on every
      page, in dev and production. The mark does not reduce to 32px and nothing was substituted,
      generated or placeheld; this line guards the *absence* until the operator decides (P10)
```

## 7. Fix authority — nothing was fixed, and why

The plan allows a fix only when this phase introduced the defect **and** the fix is unambiguous.
One candidate arose (§3, the 390px `/ops` bar) and it fails the second test twice over: the CSS is
signed, and two reasonable fixes exist that differ in scope. Everything else in §2 is signed design
by construction. **No product file was touched by this slice.** `git status` shows only
`works/**` and the untracked `var/p10s5/` screenshots.

## 8. What the operator can look at

All under `/Users/sugang/projects/personal/Mijual/var/p10s5/` (gitignored, so it survives the
session without entering the repo). `prod-*` are the **production build**, `dev-*` are `next dev`.

| file | what it shows |
|---|---|
| `dev-nav-h19-signed.png` / `dev-nav-h27-simulated.png` | **decision 2a**, nav, 4× — signed vs recommendation |
| `dev-footer-h17-signed.png` / `dev-footer-h24-simulated.png` | **decision 2a**, footer, same pair |
| `prod-ops-mark-zoom.png` | **decision 2b** — the 탑␣운 gap at 6× |
| `prod-desktop-ops-bar.png` | the ops bar in context: mark vs Korean tabs vs the mono chip |
| `dev-mobile390-ops-bar.png` | **finding §3** — the 390px collapse |
| `dev-mobile390-ops-door.png`, `prod-…-ops-door.png` | the door, both viewports, both runtimes |
| `prod-desktop-landing.png`, `prod-m390-landing.png` | the chrome as a reader meets it |
| `prod-desktop-404.png`, `prod-m390-404.png` | the 404, both marks |
| `prod-{desktop,m390}-navmark-zoom.png` | the paint-quality evidence of §4 |
| `{dev,prod}-ask-meta-{1,2}.png` | the live agent naming itself |
| `{dev,prod}-{desktop1280,mobile390}-*-disclaimer.png` | the 실권주 sentence at both sites |

## 9. Deviations, and the state I left behind

1. **Postgres host port** — §0. Same image, same volume, host port 5434 via a scratchpad
   `!override` fragment; `DATABASE_URL` pointed at it. The other project's container was never
   touched. Restored to `Created` on the unmodified 5433 binding.
2. **Throwaway ops credentials** on the API process only, so the `/ops` **bar** mark could be seen
   at all. Nothing written to `.env`; both died with the process.
3. **`next build` rewrote `frontend/next-env.d.ts`** (the build variant vs the dev variant), as S2
   recorded. Restored with `git checkout --`; `git status` is clean of it.

In-page DOM mutations (the height simulation, the font A/B, the string A/B) were all made in a
live page and discarded by the next navigation; each script restores the node before it returns and
the restored values were re-read and logged (`restored: {'w': 72.23, 'h': 19 …}`).

**Not checked, stated plainly:** a real phone on the tailnet (only Chrome device emulation at
390×844 dsf 3, plus a curl against the tailnet origin proving it serves the new title and the mark
200s); any browser other than Chrome 152; any non-macOS platform — which matters for §2b, since the
ops mark's face is an OS fallback and *will* differ elsewhere, and I cannot see that from here.

`phase.md`: compressed from **16,375 bytes / 185 lines** (9 bytes of headroom) by rewriting
`## Context`, `## Decomposition`, `## Decisions`, `## Notes for later slices` and `## Now` and
referencing detail by path. `## Doc impact` and `## Operator Questions` are append-only and were
left intact, with one line and one question appended.
