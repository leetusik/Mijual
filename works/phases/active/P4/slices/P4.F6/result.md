# P4.F6 — result

- **status:** done
- **summary:** The landing now serialises a **projection** of `/board` instead of the whole
  response: `app/page.tsx` maps every ranked and pinned row to a narrowed
  `countdown: {label_ko, date, dday, days}` before handing it to the client `<Board>`, and
  `lib/types.ts` grows `Landing{Countdown,Row,Strip,Board}` as `Pick`/`Omit` **over** the real
  shapes — `/board`'s contract, `BoardResponse`, the event page, the 종목 lookup and 보유 종목 are
  untouched. On the dev corpus (445 serialised rows) the landing document drops
  **345,613 → 283,363 B (−62,250 B, −18.0 %)** and its RSC flight **269,411 → 207,161 B (−23.1 %,
  78.0 % → 73.1 % of the document)**; `window_state` occurrences in the document go **445 → 0**.
  The timing win is real but small, exactly as `P4.R1` warned: cold-cache mobile **FCP/LCP
  812 → 796 ms (−16 ms)**, **DCL 680.2 → 663.0 ms (−17.2 ms)** over 15 interleaved load pairs.
  Zero visual change is **byte-proved**, not eyeballed: the non-flight document is byte-identical
  (equal sha256) and the full-page screenshots at 390 and 1280 have **equal sha256 and `AE = 0`**.
- **files_changed:** `frontend/app/page.tsx`, `frontend/lib/types.ts`,
  `frontend/components/landing/Board.tsx`, `frontend/components/landing/BoardRow.tsx`,
  `works/phases/active/P4/phase.md`, `works/phases/active/P4/slices/P4.F6/result.md`
- **validation:** `npm run typecheck` (`tsc --noEmit`) → **clean**, plus a **negative control** that
  proves the narrowing bites (four `TS2339`s, reverted); `npm run smoke` → **22/22**; `npx next
  build` in the scratch copy → **exit 0**; the plan's grep over `frontend/components/landing` →
  **no hits**; document/flight bytes over 3 captures per build → **deterministic, identical bytes
  each time**; 15 interleaved cold mobile load pairs in real headful Chrome 152 over CDP; 30 paired
  server-TTFB samples; screenshot equivalence `compare -metric AE` = **0** at 390 and 1280 (equal
  sha256); tabs / 「15건 더 보기」 / strip / a forced refresh driven live on **both** builds;
  `python3 scripts/workflow.py validate` → **passed** (pre-existing `oversized_doc_sections`
  warning only); `git diff --stat` → the four frontend files + `phase.md` + this file (plus the
  generated `works/` files `start-slice` already touched). **No deploy, nothing on the box,
  production never contacted.**
- **deviations:** four, all recorded in full below — (1) the **before** build was served on
  **:3015** beside the after build on the plan's **:3014**, so the loads could be interleaved A/B/A/B
  in one browser session against one unchanged corpus; (2) **15** load pairs instead of the plan's 3,
  because the effect is ~2 % and three loads cannot separate that from machine noise; (3) rows are
  rebuilt by **rest-spread** rather than by naming every kept key (naming them would emit
  `offering: undefined`, which the flight encodes as `$undefined` — bytes spent to say a key is
  missing); (4) one negative-control edit was made to `BoardRow.tsx` mid-slice and reverted (the
  file is byte-identical to its pre-control state and typechecks clean).
- **doc_impact:** one `frontend` line appended to `phase.md` (the landing's projection, the
  `Landing*` types, and the refresh path still fetching the full board).
- **doc_versions:** n/a (not a review slice — durable docs are versioned in a docs phase).
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a
- **operator_need:** none

---

## 1. What changed, and what deliberately did not

Four files, all under `frontend/`:

| file | change |
|---|---|
| `lib/types.ts` | `LandingCountdown = Pick<Countdown, …>`, `LandingRow = Omit<BoardRow,"countdown"> & {…}`, `LandingStrip`, `LandingBoard`. **Derived from** the real shapes, never copies of them. |
| `app/page.tsx` | `landingRow` / `landingStrip` / `landingBoard` — a small pure projection, applied once at `<Board board={landingBoard(board)} />`. |
| `components/landing/Board.tsx` | prop, `apply()` and `diff()` typed `LandingBoard`; row type `LandingRow`. |
| `components/landing/BoardRow.tsx` | row type `LandingRow`. |

Untouched, on purpose: `/board` and every server-side shape (`BoardResponse` still describes the
endpoint exactly), `app/sitemap.ts` (which reads `BoardRow` server-side and never ships it),
`/events/[rcept_no]`, `/stocks/[corp_code]`, `/portfolio`, and `Board`'s 60 s refresh — which keeps
calling the unnarrowed `getBoard()`. Measured on the after build: `window_state` still appears
**1×** on `/stocks/00547510`, **1×** on `/events/20250902000288` and **6×** on `/portfolio?sample=1`,
and **0×** on the landing. That is the whole intent in one line of evidence — the field is gone from
the one surface that never read it, and nowhere else.

Two design notes that are in the code comments and are worth repeating here because they are the
kind of thing a later slice would otherwise "clean up":

- **Rest-spread, not an explicit key list.** `landingRow` destructures `countdown` off and spreads
  the rest. Naming the kept keys instead would write `offering: undefined` on the 433 ②/③ rows that
  carry no `offering`, and React's flight encodes an explicit `undefined` as `$undefined` — real
  bytes, spent to say a key is missing. It would also silently drop any *optional* field later added
  to `BoardRow` (a required one would at least be a type error, via the `Omit`).
- **The refresh is not narrowed.** `getBoard()` in the browser returns a full `BoardResponse`, which
  is structurally assignable to `LandingBoard`, so `apply()` takes it unchanged. A value fetched in
  the browser is never serialised into a document, so there is nothing to save there — and narrowing
  it would have meant a second copy of the projection on the client. Proved at runtime in §5.

## 2. The proof that nothing on the landing reads the four fields

The typecheck is the proof, and a **negative control** is what makes it a proof rather than an
absence of evidence. `npm run typecheck` is clean as shipped. Temporarily adding

```ts
const __probe = [countdown.window_state, countdown.window, countdown.reference, countdown.source];
```

to `BoardRow.tsx` produced exactly four errors and nothing else:

```
components/landing/BoardRow.tsx(57,30): error TS2339: Property 'window_state' does not exist on type 'LandingCountdown'.
components/landing/BoardRow.tsx(57,54): error TS2339: Property 'window' does not exist on type 'LandingCountdown'.
components/landing/BoardRow.tsx(57,72): error TS2339: Property 'reference' does not exist on type 'LandingCountdown'.
components/landing/BoardRow.tsx(57,93): error TS2339: Property 'source' does not exist on type 'LandingCountdown'.
```

The probe was removed and `tsc --noEmit` is clean again. The grep the plan asked for
(`window_state\|\.reference\b\|\.source\b\|countdown\.window` over `frontend/components/landing`) is
**empty**; the only hit anywhere on the landing is the sentence in `page.tsx`'s own doc comment
naming the four fields.

**The board's helpers were read before deciding, per the plan.** `keep()` filters on
`rights_type`; `hasExtras()` / `extrasKey()` read `offering.{price_confirmed,subscription_start,
subscription_end}`; `diff()` compares `countdown.date`, `countdown.label_ko`, `countdown.dday` and
`extrasKey`, keyed by `event_id`. Every one of those survives the projection, so the 갱신됨 badge
and the per-value `--live` fade key on exactly what they keyed on before — confirmed live in §5.

## 3. Bytes — measured, deterministic

Local production builds of the **unmodified** tree (before) and the working tree (after), each
`NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npx next build`
in a scratchpad copy, served as `node .next/standalone/server.js` with `.next/static` and `public/`
staged in — R1's recipe, and what `frontend/Dockerfile` does on the box. Both against the operator's
dev API on 8010, whose board did not move during the slice (`freshness.as_of`
`2026-09-02T20:05:28+09:00` throughout).

**n = 445 serialised rows** (375 ranked + 66 `open_now` + 4 `tbd`; `/board` = 157,563 B, counts
`all 445 · R1 12 · R2 422 · R3 11`). Production's board is a different corpus — R1 measured 393
ranked rows and a 354,266 B document there — so the *proportion* transfers and the absolute number
does not. **Production numbers land at the review, after `P4.S9`.**

| | before | after | delta |
|---|---|---|---|
| document (decoded) | **345,613 B** | **283,363 B** | **−62,250 B (−18.0 %)** |
| RSC flight | 269,411 B | 207,161 B | −62,250 B (−23.1 %) |
| flight share of the document | 78.0 % | 73.1 % | −4.9 pp |
| everything but the flight | 76,202 B | 76,202 B | **0 B — byte-identical** |
| on the wire (server's own gzip) | 44,235 B | 40,804 B | −3,431 B (−7.8 %) |
| offline `gzip -9` | 41,506 B | 38,341 B | −3,165 B (−7.6 %) |
| `window_state` occurrences | 445 | **0** | — |

Three captures of each build returned **identical bytes every time**, so these are not medians of a
noisy quantity.

**Two honest corrections to the note's expectation.** The R1 note projected «~90 KB (≈33 %) off a
354 KB document; ~9 KB brotli on the wire». Measured, on this corpus, it is **62 KB (−18 %)** and
**~3.4 KB gzip** — the four fields are extremely repetitive (`"window_state":"open"`,
`"source":"cvbdIsDecsn.cvrqpd_bgd"` 422 times), so a compressor was already doing most of that work
and the wire saving is a third of the estimate. Raw JSON of just the four fields across the 445 rows
is 58,261 B, which brackets the 62,250 B measured (flight escaping adds the rest). Brotli was not
measured locally — no brotli module on this machine, and the local server serves gzip; Cloudflare's
brotli figure comes at `P4.S9`.

## 4. Timing — real Chrome, interleaved, and small

Instrument: **real Google Chrome 152.0.7977.65, headful**, launched through LaunchServices with a
**throwaway profile** (`--user-data-dir=<scratchpad>/f6prof`, port 9361) and driven over the
DevTools protocol by `P4.R1`'s own harness (`r1_cdp.py`). This is the fallback instrument
`## Operator Runtime` records — **Aside was not used and is not installed here** (its daemon does not
run on this Mac and no agent Aside account exists). The operator's Chrome profile was never touched.
Profile: R1's *mobile* — 412×915, DPR 2.625, `Emulation.setCPUThrottlingRate 4`, 150 ms RTT /
1.6 Mbps / 0.75 Mbps up, `Network.setCacheDisabled` + `clearBrowserCache` and a fresh tab per load.

**15 load pairs, interleaved before/after within each round**, medians of 15:

| metric | before | after | delta |
|---|---|---|---|
| FCP | 812.0 ms | 796.0 ms | **−16.0 ms (−2.0 %)** |
| LCP | 812.0 ms | 796.0 ms | −16.0 ms (LCP == FCP, R1's finding, still true) |
| DOMContentLoaded | 680.2 ms | 663.0 ms | **−17.2 ms (−2.5 %)** |
| load | 3132.1 ms | 3115.7 ms | −16.4 ms |
| long tasks (count) | 2 | 2 | 0 |
| long-task total | 140.0 ms | 136.0 ms | −4.0 ms |
| long tasks at/after FCP (hydration) | 65.0 ms | 64.0 ms | −1.0 ms |
| longest task | 75.0 ms | 73.0 ms | −2.0 ms |
| `Performance` ScriptDuration | 0.087 s | 0.087 s | **0.000 s** |
| `Performance` TaskDuration | 1.837 s | 1.774 s | −0.063 s |
| `Performance` RecalcStyleDuration | 0.538 s | 0.514 s | −0.024 s |
| `Performance` LayoutDuration | 0.075 s | 0.072 s | −0.003 s |
| DOM nodes | 936 | 936 | **0** |
| rows in the DOM | 15 | 15 | **0** |
| CLS | 0.0002–0.0012 | 0.0002–0.0012 | no signal (see below) |

**Read it honestly.** The saving is **~16–17 ms of a ~800 ms mobile FCP** — ~2 %, at 4× CPU on a
1.6 Mbps link, and it shows up as an earlier DCL rather than as a shorter hydration long task. The
hydration long task barely moves (−1 ms) because at 4× CPU it is dominated by React rendering 15
rows plus the 250-element starfield, not by parsing the flight string; what 62 KB buys is fetch and
parse time ahead of it. `ScriptDuration` does not move at all. This is exactly what the R1 note said
to expect («tens of ms … it may be small»), and it is worth shipping because the byte and parse cost
is paid by every reader on every cold landing view, forever, for four fields nobody reads.

**CLS is not a signal here.** Both builds produce the same two-valued jitter (0.0002 or 0.0012 per
load, appearing on both targets in both batches) — two orders of magnitude under the 0.01 target and
`P4.F5`'s fallback faces are in both trees.

**Server cost: none measurable.** 30 paired `curl` requests, medians: TTFB **100.55 → 99.93 ms**
(−0.62 ms), total **100.72 → 100.09 ms**. Rebuilding 445 row objects is inside the noise of the
~100 ms `/board` round trip the landing already pays. (`GET /board` is confirmed hit once per landing
request in `var/stack/api.log` — the projection did not accidentally introduce or remove a fetch.)

## 5. Zero visual change, and the board still works

**Screenshots — byte-identical, not merely similar.** Full-page captures of `/` on both builds at
**390×844 DPR 2** and **1280×800 DPR 1**, with `P4.F5`'s control CSS (animations/transitions off so
the 240-star cosmos cannot twinkle between captures, the live 1 s countdown hidden by `visibility`
so it keeps its layout box), taken after `document.fonts.ready`:

| capture | dimensions | sha256 (first 16) | `compare -metric AE` |
|---|---|---|---|
| `/` @ 390 before / after | 780×5642 / 780×5642 | `8009af94534d0489` / `8009af94534d0489` | **0** |
| `/` @ 1280 before / after | 1280×2151 / 1280×2151 | `def679ec5751b816` / `def679ec5751b816` | **0** |

And upstream of the pixels, **the served markup is byte-identical**: replacing the single
`self.__next_f.push([1,"…"])` flight chunk with a placeholder in both documents gives the same
76,202 B and the same sha256. Nothing the browser lays out changed; only the props payload did.

**Behaviour, driven live in the same browser** (1280, both builds):

- **The four tabs** — 전체 / 유상증자 / 전환사채 / 주식매수청구 — behave **line-for-line identically**
  on before and after: counts `445 / 12 / 422 / 11`, filtered lists `15 / 10 / 15 / 9`, the row kinds
  in each list correct (`유증` only, `CB` only, `매수청구` only), the window footer reading
  `남은 360건` on 전체 and `남은 341건` on CB, and 전체 restoring its first window on the way back.
- **「15건 더 보기」**: 15 → **30** → **45** rows, with `남은 360건` → `345건` → `330건`.
- **The pinned strip** 펼치기 opened a second list of **66** rows on the panel's own column plan;
  접기 closed it.
- **The 60 s refresh** was forced rather than waited out, and forced with the case that matters:
  `window.fetch` was patched to return a **full `/board` response** — the payload's
  `rows[0].countdown` still carried all **eight** keys (`label_ko, date, dday, days, window,
  window_state, reference, source`), i.e. exactly what the real refresh delivers into the narrowed
  prop — with `freshness.as_of` moved on and row `876`'s D-day changed. Result: **갱신됨 appeared**,
  the 기준시각 chip moved, row `876` alone took the `changed` (`--live`) class, and it re-rendered
  `2027-01-01 / D-999`. That is `apply()` + `diff()` accepting a `BoardResponse` through a
  `LandingBoard` prop at runtime, which is the one thing structural assignability could have got
  wrong.
- **No console error, warning, `onerror` or unhandled rejection** was captured on any load or any
  interaction, on either build — so no hydration mismatch was introduced by rendering from a
  narrower payload.

## 6. Deviations, in full

1. **Two servers, not one.** The plan says the local production build is served on :3014. The
   **after** build is on :3014 as specified; the **before** build was additionally served on
   **:3015** so that the 15 load pairs could be interleaved A/B inside one browser session against
   one unchanged corpus. With a ~2 % effect and a machine whose per-load spread is wider than that,
   sequential batches minutes apart would not have separated the effect from drift. Both servers were
   stopped at the end (ports verified free).
2. **15 load pairs instead of 3.** Same reason. Batch 1 (5 pairs) and batch 2 (10 pairs) agree —
   DCL −17.2 / −19.2 ms, FCP −4 / −18 ms — and the combined medians are reported.
3. **Rest-spread rather than an explicit key list** in `landingRow`, for the `$undefined` reason in
   §1. The plan's field list is satisfied exactly: the dev API's rows carry precisely
   `event_id, corp_code, corp_name, rights_type, rcept_no, state, countdown, offering` and no other
   key (checked across all 445 rows), which is `BoardRow` exactly, so the spread drops nothing and
   adds nothing.
4. **A negative-control edit to `BoardRow.tsx`** (§2) was made and reverted inside the slice. It was
   not in the plan; it is what turns "the typecheck passes" into "the typecheck would have failed if
   anything read them". The file was restored from a copy taken before the edit and `tsc --noEmit`
   is clean.

Not a deviation, but worth naming: **brotli was not measured** (no brotli module here and the local
standalone server serves gzip). The production wire number is `P4.S9`'s to read through Cloudflare.

## 7. Artefacts, and what was left running

All outside the repository, in the session scratchpad
`/private/tmp/claude-502/-Users-sugang-projects-personal-Mijual/79e813fa-984f-4074-b1b7-7f62151138db/scratchpad/`:
`f6be/` + `f6af/` (the two scratch production builds), `f6_build_before.log` / `f6_build_after.log`,
`f6_web3015_before.log` / `f6_web3014_after.log`, `f6_flight.py` (the document/flight splitter),
`f6_loads.py` + `f6_loads_mobile.jsonl` + `f6_loads_mobile2.jsonl` (the interleaved cold loads),
`f6_ttfb2.txt`, `f6_shot.py` + `f6_{before,after}_home_{390,1280}.png`, `f6_interact.py`,
`f6_tabs.py`, `f6_{before,after}_home_{1,2,3}.html`, `f6_board_before.json`, `f6prof/` (the throwaway
Chrome profile). The harness they build on is `P4.R1`'s `r1_cdp.py` and `P4.F5`'s `f5_shot.py`,
already in the same scratchpad.

**Stopped:** Chrome (`Browser.close`; port 9361 free, no process on the throwaway profile), the
:3014 and :3015 servers (both ports free). **Left up, untouched:** the operator's dev stack — 3010
and 8010 both answering **200** after teardown. Nothing was built into `frontend/.next` (both builds
ran in scratchpad copies, so the running `next dev` was never disturbed), nothing was installed into
the project, and **production was never contacted**.
