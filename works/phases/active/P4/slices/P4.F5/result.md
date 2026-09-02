# P4.F5 — result

- **status:** done
- **summary:** Replaced `next/font/local`'s Arial-metric fallback with three hand-declared,
  **measured** metric-matched Korean fallback faces (`adjustFontFallback: false` +
  `notoSansKr Fallback Apple / Noto / Malgun` in `app/shell.css`). Cold-cache mobile CLS on a local
  production build fell **`/` 0.0953 → 0.0002 · `/stocks` 0.1378 → 0.0003 · `/ask` 0.0894 → 0.0003**
  (medians of 3, real Chrome 152 over CDP), the loaded-font rendering is **pixel-identical**
  (`AE = 0` on `/` and `/stocks` at 390 and 1280), and `font-display` stayed `swap` — no design
  decision was needed. The event page's remaining **0.0325** is a *different*, pre-existing defect
  (「이 마감 알림 받기 →」 inserted after `GET /me` resolves), proved and written up for its own slice.
- **files_changed:** `frontend/app/fonts.ts`, `frontend/app/shell.css`,
  `works/phases/active/P4/phase.md`, `works/phases/active/P4/slices/P4.F5/result.md`
- **validation:** `npm run build` in the build copy → **exit 0**; `npm run typecheck` (`tsc
  --noEmit`) → **clean**; `npm run smoke` → **22/22**; no ESLint in this project (Next 16 dropped
  `next lint`, no eslint config — typecheck + build + live verification are the repo's equivalent);
  cold-load CLS sweep 4 routes × 2 profiles × 3 loads before and after (table below);
  layout-equality sweep on **6** routes with the webfont blocked (max element displacement
  **0.25 px**, identical document heights); screenshot equivalence `magick compare -metric AE` = **0**
  on 4 captures; `python3 scripts/workflow.py validate` → **passed** (pre-existing warnings only);
  `git diff --stat` → the two frontend files + `phase.md` + this file (plus the four generated
  `works/` files the orchestrator's `start-slice` already touched).
- **deviations:** three, all small and recorded below — (1) the fit/measurement iteration ran by
  injecting candidate CSS over the *unchanged* build rather than rebuilding per candidate (the
  winning numbers were then baked in and re-measured for real); (2) per-weight fallback faces were
  declared even though synthesised bold measured the *same* advance width, because the real
  Medium/SemiBold/Bold cost three CSS blocks and make the swap window look right; (3) the Windows
  face ships `size-adjust: 100%` — Malgun Gothic could not be measured or legitimately obtained, and
  guessing its width would have been a *worse* fallback than none.
- **doc_impact:** two lines appended to `phase.md` — `frontend` (Fonts: `adjustFontFallback: false`,
  the three hand-declared fallback families and their measured overrides, why Arial could not work,
  how to re-derive after a subset regeneration, and Chrome's full-name/PostScript-name `local()`
  rule) and `qa` (the regression line: cold-cache mobile CLS ≤ 0.01 on `/`, `/stocks`, `/ask`, the
  method, and the event page's non-font residual).
- **doc_versions:** n/a (not a review slice — versioning is deferred to a docs phase)
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a
- **operator_need:** none. `font-display: optional` was never reached — the metric route hit the
  target on every route where the font was the cause.

---

## 1. What was wrong, and what replaced it

`P4.R1` proved the cause and this slice did not re-derive it: `next/font/local` generated

```
@font-face{font-family:notoSansKr Fallback;src:local(Arial);ascent-override:117.61%;
           descent-override:29.2%;line-gap-override:0.0%;size-adjust:98.63%}
```

and **Arial has no Hangul**, so Korean text painted in the next family with no override at all and
the document re-wrapped when the 291,072-byte subset landed ~3 s in.

`frontend/app/fonts.ts` now sets `adjustFontFallback: false` and leads its `fallback` array with
three families declared in `frontend/app/shell.css`. The **built** CSS
(`.next/static/chunks/*.css` of the build copy) carries exactly this — the Arial face is gone, and
Plex Mono's is untouched:

```
@font-face{font-family:notoSansKr;src:url(../media/NotoSansKR_subset.p.…woff2)format("woff2");font-display:swap;font-weight:100 900;font-style:normal}
@font-face{font-family:plexMono Fallback;src:local(Arial);ascent-override:77.95%;descent-override:20.91%;line-gap-override:0.0%;size-adjust:131.49%}
@font-face{font-family:notoSansKr Fallback Apple;src:local(AppleSDGothicNeo-Regular),local(Apple SD Gothic Neo Regular);font-weight:400;…;size-adjust:106.36%;ascent-override:109.06%;descent-override:27.08%;line-gap-override:0%}
… (Medium 500, SemiBold 600, Bold 700 900) …
@font-face{font-family:notoSansKr Fallback Noto;src:local(NotoSansKR-Regular),…,local(NotoSansCJK-Regular);font-weight:100 600;…;size-adjust:100%;ascent-override:116%;descent-override:28.8%;line-gap-override:0%}
@font-face{font-family:notoSansKr Fallback Malgun;src:local(MalgunGothic),local(Malgun Gothic Regular),local(Malgun Gothic);font-weight:100 600;…;size-adjust:100%;ascent-override:116%;descent-override:28.8%;line-gap-override:0%}
```

and the emitted stack, read off `getComputedStyle(document.body).fontFamily` on the running build:

```
notoSansKr, "notoSansKr Fallback Apple", "notoSansKr Fallback Noto", "notoSansKr Fallback Malgun",
system-ui, -apple-system, sans-serif, "Noto Sans KR", system-ui, -apple-system, sans-serif
```

(the tail after the first `sans-serif` is shell.css's own and is unreachable, exactly as it was
before this slice; the bare `"Apple SD Gothic Neo"` / `"Malgun Gothic"` entries were dropped from it
because they name the same faces **unadjusted**, which is the defect.)

**The grep the plan asked for.** `Apple SD Gothic Neo` / `Malgun` / `--font-sans` / `system-ui`
appear in source in exactly three places: `app/fonts.ts`, `app/shell.css` (both changed) and
`public/foundations/tokens.css` — the **frozen R8 vendored token file**, whose `--font-sans` is
Pretendard and is deliberately *overridden* by `shell.css` rather than edited (its own recorded
rule). It was not touched. Everything else is build output under `frontend/.next/`.

## 2. The metrics, measured two ways

**From the font tables** (`uvx --from fonttools --with brotli python …`, a tool run — no project
dependency, no `uv run --with`):

| face | upem | hhea asc / desc / gap | Hangul advance (56 syllables from the product's own copy) | space |
|---|---|---|---|---|
| `NotoSansKR.subset.woff2` (what we ship) | 1000 | 1160 / −288 / 0 | **920** — one value, `min == max`, at `wght` 400 **and** 700 | 220–227 |
| Apple SD Gothic Neo — Regular / Medium / SemiBold / Bold | 1000 | 900 / −300 / 0 | **865** in *every* weight | 263 |
| Noto Sans CJK KR (`noto-cjk` `Sans/SubsetOTF/KR/NotoSansKR-Regular.otf`, downloaded to the scratchpad to be read) | 1000 | 1160 / −288 / 0 | **920** | 224 |
| Malgun Gothic | — | — | **not measurable here** (Windows-only, no trustworthy published tables) | — |

**In Chrome** (canvas `measureText` / `TextMetrics` at 100 px, on the running build): the loaded
`notoSansKr` reports `fontBoundingBoxAscent/Descent` **116 / 29**, Apple SD Gothic Neo **90 / 30**,
and the per-syllable Hangul advances come out at exactly **92.0 px** and **86.5 px** — the table
values, confirmed by the renderer that has to agree with them.

**The four numbers, and why they are divisions and not choices:**

```
size-adjust      = 920 / 865            = 106.36 %      (Apple)      100 %  (Noto CJK — same design)
ascent-override  = (1160/1000) / 1.0636 = 109.06 %                   116 %
descent-override = ( 288/1000) / 1.0636 =  27.08 %                    28.8 %
line-gap-override= 0 %                                                0 %
```

`size-adjust` scales the overrides too, which is why both are divided by it — the same arithmetic
Next itself does for the Arial face (its 117.61 % is 116 % / 0.9863).

**Two measurements that changed the design:**

- **Chrome's `local()` matches a full name or a PostScript name — never a family name.** Declaring
  `src: local("Apple SD Gothic Neo")` and calling `document.fonts.load()` throws *"A network error
  occurred"* and measures identically to a deliberately bogus control, while
  `local("AppleSDGothicNeo-Regular")` and `local("Apple SD Gothic Neo Regular")` both resolve. Every
  `src` therefore names the PostScript form first and the full name second. (`f5_measure1.json`.)
- **Synthesised bold does not change advance width** on this face (a Korean sample measures 2831.7 px
  at both `400` and `700`), so no per-weight `size-adjust` is needed — the per-weight faces exist for
  *appearance* during the swap window, not for layout.

## 3. Fitting the number against the real thing

Before touching the build, the candidate overrides were fitted by rendering each route twice — once
with the webfont **loaded**, once with it **blocked** and a candidate face injected — and comparing
the bounding rect of every element in `body *` (mobile 412 × 915 @ 2.625, R1's profile). Noise floor
(loaded vs loaded): **0 elements moved, max 0.02 px**.

| candidate | `/` | `/stocks` | `/ask` | `/events/…329` |
|---|---|---|---|---|
| shipped then (blocked, Arial face) | 336 moved, max **44.9 px**, docH −2 | 23 moved, max 42.8 px | 8 moved, max 42.8 px | 65 moved, max **55.8 px**, docH −13 |
| `size-adjust: 105 %` | 0 moved (max 0.19) | 0 | 0 | **65 moved, max 18.6 px** |
| **`size-adjust: 106.36 %`** | **0 moved (max 0.25)** | **0** | **0** | **0** |
| `size-adjust: 107 %` | 310 sub-pixel drifts, max 0.77 | 0 | 0 | 0 |

106.36 % — the value the font tables give — is also the value the browser agrees with, and 105 %
(the ratio you get if you weight the sample by all visible characters instead of by Hangul) misses a
wrap boundary on the event page. That is why the shipped number is the derived one.

**Re-run on the SHIPPED stack after the rebuild** (webfont blocked, nothing injected), six routes:

| route | elements | moved > 0.5 px | max Δtop | document height |
|---|---|---|---|---|
| `/` | 623 | 0 | 0.25 px | 2822 = 2822 |
| `/stocks` | 70 | 0 | 0.00 px | 915 = 915 |
| `/ask` | 51 | 0 | 0.00 px | 915 = 915 |
| `/events/20260806000329` | 159 | 0 | 0.00 px | 2197 = 2197 |
| `/stocks/00547510` | 132 | 0 | 0.00 px | 1522 = 1522 |
| `/portfolio?sample=1` | 215 | 0 | 0.20 px | 2255 = 2255 |

## 4. Cold-cache CLS — before and after, same build path, same instrument

Local production build on **:3014** (`node .next/standalone/server.js` with `.next/static` and
`public/` staged in — never `next start`, which Next 16 refuses under `output: "standalone"`),
against the operator's dev API on 8010. Real Google **Chrome 152.0.7977.65**, headful, throwaway
profile, CDP port **9391**. Mobile = 412 × 915 @ DPR 2.625, 4× CPU, 150 ms / 1.6 Mbps; desktop =
1280 × 800 unthrottled. Cache cleared and a fresh tab per load; **3 loads per cell, medians**.

| route | mobile before | mobile after | desktop before | desktop after |
|---|---|---|---|---|
| `/` | **0.0953** | **0.0002** | 0.0000 | 0.0000 |
| `/stocks` | **0.1378** | **0.0003** | 0.0000 | 0.0000 |
| `/ask` | **0.0894** | **0.0003** | 0.0000 | 0.0000 |
| `/events/20260806000329` | 0.0328 | **0.0325** | 0.0089 | 0.0089 – 0.0106 |

The before column reproduces `P4.R1`'s production numbers (0.095 / 0.138 / 0.089 / 0.033) almost
exactly, which is what makes the two columns comparable. After the change **no layout-shift entry of
any size lands near the font's `responseEnd`** on `/`, `/stocks` or `/ask` — the residual 0.0002–3 is
a single sub-0.001 entry early in the load.

### The event page's 0.0325 is a different defect, and it is not a regression

Attributed, not assumed. The shift fires at ~2.44 s mobile — the font's `responseEnd` is ~3.21 s —
and its sources are whole sections moving down by exactly **52 px**:

```
SECTION.Event…offering  y 479.1 -> 531.1      DIV.Event…qstrip  y 389.1 -> 441.1
SECTION.Event…sec       y 695.4 -> 747.4      A.Event…dart      y 333.1 -> 385.1
```

A DOM snapshot at 2.0 s and again at 5.0 s shows what arrives in between, right after
`GET /me` returns (2273 → 2433 ms): **`A.Auth-module__deadlineOffer` 「이 마감 알림 받기 →」**, plus
the nav's 로그인 slot. It is the anonymous variant being decided in the browser after hydration, not
type. It measured 0.0328 before this slice and 0.0325 after.

The desktop `0.0106` seen in 2 of 3 runs is the same 0.0089 insertion **plus ~0.0016 of Plex Mono
swapping**: with `Network.setBlockedURLs ["*IBMPlexMono*"]` four desktop loads report exactly
`0.0089` and nothing else. Plex Mono is `preload: false` by design and this slice did not touch it;
whether it lands before or after first paint on an unthrottled desktop is a race that predates F5.

Both are written up in `phase.md` `## Notes for later slices` as a candidate `P4.F10`.

## 5. RESPECT THE DESIGN — the loaded-font rendering did not move a pixel

Full-page screenshots of the build copy, **font loaded**, before the change and after it, at
**390 × 844 @ DPR 2** and **1280 × 800**:

| capture | dimensions | `magick compare -metric AE` |
|---|---|---|
| `/` at 390 | 780 × 5642 | **0** |
| `/` at 1280 | 1280 × 2151 | **0** |
| `/stocks` at 390 | 780 × 1724 | **0** |
| `/stocks` at 1280 | 1280 × 800 | **0** |

Two things are neutralised in *both* captures so that two shots of the *same* build are byte-equal,
and neither touches type: CSS animation/transition (the 240-star cosmos twinkles) and the live 1 s
countdown text (`Countdown.module`, hidden with `visibility` so it still occupies its box). With
those two frozen, a same-build control pair is **AE = 0** on all four captures — that is the noise
floor the table above is measured against. Before the freeze the control pair differed only in the
ticking-seconds region, which the difference image showed directly.

The fallback faces change what a reader sees **only during the swap window**, where a metric-matched
system face replaces an unmatched one.

## 6. Where it was verified, and what was left running

- **Runtime.** `## Operator Runtime` (operations doc) records the dev stack on 3010/8010 and — via
  `P4.S4`'s owed Doc-impact line — production as a standalone build behind Cloudflare. This slice
  ships nothing, so the target was the **local production build** on :3014, exactly as `P4.R1` used,
  which is the same `node .next/standalone/server.js` path the box runs. The change was additionally
  loaded in the operator's own **dev runtime** (`http://127.0.0.1:3010/`, read-only): the emitted
  stack is the new one, `notoSansKr Fallback Apple` reports `loaded`, the board renders its 15 rows.
- **Instrument.** Real Google Chrome 152 over the DevTools protocol, headful, launched through
  LaunchServices with a **throwaway profile** (`scratchpad/chrome-f5`) on a fresh port — never the
  operator's profile. **Aside was not used and is not installed on this Mac** (no daemon, no agent
  account); this is the fallback instrument `## Operator Runtime` names.
- **Everything started was stopped.** `node server.js` on :3014 — pids **53059** (before build) and
  **56794** (after build), both killed, port free. Chrome CDP **:9391** closed with `Browser.close`;
  the port answers nothing and no process matches. The operator's stack was never touched and
  answers **3010 → 200** and **8010 /health → 200** after the run.
- **Nothing on the box, no deploy, production read-only** (not a single production request was made
  in this slice). No secret value appears anywhere here.

## 7. Artefacts (all outside the repo, in the session scratchpad)

`f5_metrics.py` / `f5_metrics2.py` / `f5_metrics3.py` (fontTools table reads, incl. the downloaded
`notocjkkr.otf`), `f5_measure.py` + `f5_measure1.json` (Chrome-side metrics and the `local()`
name-matching probe), `f5_measure2.py` + `f5_ratios.jsonl` (per-route visible-text width ratios),
`f5_fit.py` + `f5_fit_412.log` (the rect-equality fit), `f5_cls.py` + `f5_cls_before.jsonl` /
`f5_cls_after.jsonl` (the cold-load sweeps), `f5_event.py` / `f5_event2.py` (residual attribution),
`f5_shot.py` + `f5_{before,noise,after}_{home,stocks}_{390,1280}.png` and the diff images,
`f5_dev.py` (the dev-runtime check), `f5_build.log`, `f5_web3014_{before,after}.{log,pid}`, and
`r1fe/` — `P4.R1`'s build copy, rebuilt on the F5 sources. `r1_cdp.py` (R1's CDP client and
observers) was reused unchanged. Nothing was written into the repository except the two frontend
files, `phase.md` and this file.
