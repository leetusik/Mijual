# P4.F8 — Ship the wordmark at display size and stop serving `public/` at max-age 4 h

`kind: fix`, `risk: high`, `slice-executor-high`. Cut from `P4.R1`'s ranked list (item 3). Operator
instruction behind it (2026-09-02, verbatim): 「you look up the cloudflare's poor LCP, INP, and CLS
performance stuffs … and create slices for fix them.」 Frontend only, **no deploy in this slice**
(`P4.S9` releases F5 + F6 + F8 together). No Core Web Vitals metric moves here (the wordmark is never
the LCP); the gain is ~20 KB off every cold page load on every route, and fewer 4-hourly
revalidations of static files.

## Facts (R1 measured; the orchestrator re-checked the headers 2026-09-03)

- `frontend/public/assets/juju2-wordmark-white.png` — **1247×371, 21,920 B** — is the only image the
  chrome loads; `Wordmark.tsx` renders it with `width`/`height` = `WORDMARK_NATURAL` (intrinsic size
  for the aspect ratio) and a CSS `height` of **27 px** (nav) / **24 px** (footer), so it paints at
  **91×27** and **81×24** CSS px — at DPR 3 that is at most **273×81** device px. Lighthouse flags
  exactly it (`uses-responsive-images`).
- The file is a **class C** derivative (regenerable here by one recorded ImageMagick command from
  the class-B `juju2-logo-source.png`); `frontend/public/assets/README.md` records every class-C
  file with the command, geometry, sha256 / pixel signature, and a verify block
  (`compare -metric AE … = 0` after regenerating). `magick` is installed at `/opt/homebrew/bin/magick`.
- Production serves `/assets/*` and `/foundations/*` with `cache-control: public, max-age=14400`
  (`cf-cache-status: REVALIDATED`) — that is Cloudflare's default browser TTL because Next sends none
  for `public/`, while hashed `/_next/static/*` gets a year.

## Do

1. **One new class-C derivative at display size.** From the existing `juju2-wordmark-white.png`
   (class C → class C, as the share card did) or straight from the class-B source (your call —
   pick the one whose command reproduces bit-exactly and say why), produce a **3× of the largest
   render**: width **273** (`-resize 273x` keeps the 1247:371 ratio → 273×81), `-filter Lanczos`
   (or the filter the README's other derivatives use — stay consistent), 8-bit RGBA, no metadata
   (`-strip`), and check it is genuinely small (expect ~3–5 KB; if `pngquant`-style palette
   reduction is needed to get there, do **not** add a tool — report the size you got). Name it so the
   name changes when its bytes would (`juju2-wordmark-white-273.png` or a short content-hash suffix),
   because step 3 gives it a long cache life. Keep the 1247×371 file in place (it is the share
   card / other derivatives' ancestor and stays recorded); nothing else in `public/assets` changes.
2. **Record it in `frontend/public/assets/README.md`** in the class-C style already there: what it
   is, the exact command, geometry, `identify` line, sha256 **and** the verify block
   (regenerate → `compare -metric AE new regenerated null:` → `0`). Add the row to the class-C
   file table. Then **swap the reference**: `WORDMARK_WHITE` in `frontend/components/chrome/copy.ts`
   points at the new file and `WORDMARK_NATURAL` becomes 273×81 (read `Wordmark.tsx`'s comment on
   `INK_OFFSET_PX` and the ink-box reasoning — the offsets are in CSS px at the rendered height and
   must **not** change; verify in the browser that the mark sits exactly where it did). Update the
   comment in `copy.ts` that describes the file.
3. **Cache headers for `public/`** — a `headers()` entry in `frontend/next.config.ts`, with the same
   register of comment as the rewrite above it. Two rules: for the **new, name-versioned** wordmark
   (and anything else under `/assets/*` whose name changes with its bytes — the icons are `P4.S5`'s,
   check how they are referenced before including them) `public, max-age=31536000, immutable`; for
   everything else under `/assets/*` and `/foundations/*` a **moderate** TTL (one week,
   `max-age=604800, stale-while-revalidate=86400`) — **never** a year on a file whose name does not
   change when its content does (`tokens.css` is frozen class-A material but it is still a fixed name).
   Verify on the local production build with `curl -sI` that each path returns what you set and
   that `/_next/static/*` is unchanged; note that Cloudflare honours origin `cache-control` so the
   same headers will show through the edge after `P4.S9` (the review confirms it on production).
4. **Verify in real headful Chrome over CDP** (throwaway profile, fresh port; never the operator's
   profile) on the local production build (`node .next/standalone/server.js` on **:3014**, a copy of
   `frontend/`, the dev API on 8010; 3010/8010 stay up): at 1280 and 390, screenshot the nav and the
   footer wordmark before and after at **DPR 1, 2 and 3** (`Emulation.setDeviceMetricsOverride`) and
   compare — the ink box position must be identical (crop and `compare -metric AE`; a tiny AE from
   resampling inside the glyphs is expected and must be reported as a number, but the **bounding box
   of the ink** must not move by a pixel) and the mark must not look softer at DPR 3 than today; the
   image request must be the new file and its size.
5. **No test file.** Lint/typecheck/build clean.
6. **`phase.md`**: `## Decisions` — one line (display-size wordmark derivative, its size, the cache
   policy chosen and why not `immutable` on fixed names); `## Doc impact` — `frontend` (Assets: the
   new class-C derivative and the README record; `public/` cache headers in `next.config.ts`) and
   `operations` (a reader's browser now caches `/assets/*` / `/foundations/*` for the TTLs you set —
   what to do if a fixed-name asset must change urgently: rename it, or purge at Cloudflare); consume
   item 3 of the `(from P4.R1, for the fix slices)` note in place; rewrite `## Now` (≤ 15 lines):
   F5 + F6 + F8 done and **not yet deployed**, `P4.S9` next (the batched frontend-only release before
   **2026-09-07 11:00 KST**, aim 09-05; it needs the operator's push first), then the re-review; keep
   the gate-shut line.
7. **`result.md`** verdict-block-first: the derivative's command/size/sha256, the header table, the
   DPR screenshots' AE numbers and ink-box check, deviations.

## Hard rules

Frontend files only (`frontend/public/assets/*` + its README, `frontend/components/chrome/copy.ts`
and, only if the offsets demand it, `Wordmark.tsx`, `frontend/next.config.ts`); no deploy, nothing
on the box, production read-only; never the operator's Chrome profile; keep 3010/8010 up; stop
every server/browser you start; the repo is public — no secret values; no `git commit`/`push`; no
workflow state commands other than `python3 scripts/workflow.py validate`; `uv run` without
`--with`; no new tools or dependencies. **RESPECT THE DESIGN (R17/R18)**: same mark, same place,
same size on screen — only the bytes behind it change.

## Validate

`magick identify` of the new file (273×81, size); README verify block reproduces AE 0; `curl -sI`
on :3014 shows the headers per path; the DPR 1/2/3 crops' ink boxes are identical; lint/typecheck/
build clean; `python3 scripts/workflow.py validate` passes; `git diff --stat` → the files named,
`phase.md`, this slice's `result.md`.

## Addendum (orchestrator, 2026-09-03, at dispatch)

`P4.F5` (fonts, commit `70daeaf`) and `P4.F6` (landing projection, commit `HEAD~0` of this tree)
are in the working tree; neither touches this slice's files. `P4.F10` (the event page's late
「이 마감 알림 받기 →」 line, found by F5) is cut and runs **after** you, before `P4.S9`. The repo's
typecheck/lint equivalents are `npm run typecheck` and `npm run smoke` (22 node tests; there is no
ESLint config). Both F5 and F6 built in a copy of `frontend/` and served it with
`node .next/standalone/server.js` on :3014 — do the same; nothing is built into `frontend/.next`.
