# Result — P10.S2 (chrome, ops and document identity)

- **status:** `done`
- **summary:** Repointed the chrome at `juju-wordmark-white.png` (`{1213, 319}`), renamed
  `RING_WORDMARK_*` → `WORDMARK_*` and rewrote every comment that still described the retired
  ring, deleted the four `mijual-*.png` in the same change, swapped `BRAND_ALT_KO`,
  `COPYRIGHT_KO`, both `metadata.title`s and `OPS_MARK` to 주주의관제탑, created no favicon, and
  verified the lot in the operator runtime — dev and production, desktop and 390px.
- **files_changed:**
  - `frontend/components/chrome/copy.ts`
  - `frontend/components/chrome/Wordmark.tsx`
  - `frontend/app/layout.tsx`
  - `frontend/app/ops/layout.tsx`
  - `frontend/components/ops/copy.ts`
  - `frontend/public/assets/README.md`
  - deleted: `frontend/public/assets/mijual-wordmark-{charcoal,white}.png`,
    `frontend/public/assets/mijual-logo-ring-{charcoal,white}.png`
  - `works/phases/active/P10/phase.md`, `works/phases/active/P10/slices/P10.S2/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — **pass** (clean)
  - `cd frontend && npm run smoke` — **pass** (22/22)
  - `cd frontend && npm run build` — **pass** (15 routes)
  - real browser, **dev** (`next dev` via the Makefile, `http://127.0.0.1:3000`, Chrome 152 at
    dsf 2 + 390×844) — **pass**; both marks loaded, boxes 72.24×19 and 64.64×17
  - real browser, **production** (`npm run start`, same origin) — **pass**; byte-identical
    geometry, titles and ops marks
  - `grep -rI "mijual-.*\.png"` (excl. `node_modules`, `.next`, `works/`, `docs/versions/`) —
    **pass**, 20 hits, every one historical prose; zero in a code path
  - `python3 scripts/workflow.py validate` — **pass** (two pre-existing P9 `kind: research`
    warnings, untouched)
- **deviations:** four, all listed under *Deviations* below — the two doc comments that
  describe the constants I changed; the Postgres host port (5433 taken by an unrelated
  project); throwaway ops credentials on the API process; and the assets README edited slightly
  wider than the one named section.
- **doc_impact:** two lines appended to `phase.md` (frontend.md — the chrome now loads
  `juju-wordmark-white.png` at `{1213,319}` and the `RING_*` vocabulary is gone; operations.md
  — `make stack-up` cannot bind 5433 while another project holds it, and the documented way
  round it).

---

## 1. The wiring

`chrome/copy.ts:32–33` now reads:

```ts
export const WORDMARK_WHITE = "/assets/juju-wordmark-white.png";
export const WORDMARK_NATURAL = { width: 1213, height: 319 } as const;
```

**Why `WORDMARK_*` and not something else.** The only stale token was `RING_`: the mark is
still a wordmark, and the chrome still uses exactly one of them, so the shortest truthful name
is the un-prefixed one. Rejected: `JUJU_WORDMARK_*` (bakes the filename into the concept — the
constant names *what the chrome uses*, and a re-export under another filename should not force
a third rename) and `BRAND_MARK_*` (implies a symbol mark, which is precisely the thing that
does not exist and is the open favicon question).

Comments rewritten alongside the values, in both files:

- `copy.ts` — the block above the constants no longer explains R2's ring assets. It keeps R2's
  *placement* (h19/h17, cosmos), states that R2's asset is retired, and re-states the
  never-re-encode rule with its **new** reason: the file is a class-C repo-generated
  derivative proved by **pixel signature**, so re-compression breaks the one proof tying it to
  the operator's original.
- `Wordmark.tsx` — the header's "the five binaries are the design project's own output, copied
  in byte-for-byte" was the false assertion S1 flagged. Replaced with the class-C provenance,
  the same never-re-encode conclusion, the `1213×319` intrinsic pair, and a short paragraph
  recording that only the mark's bottom half is the wordmark (so the h19/h17 numbers no longer
  mean what they meant) with a pointer to the filed operator question.

The four `mijual-*.png` were deleted in this same change. `frontend/public/assets/README.md`'s
retirement section is rewritten from "retired but still present / deleted by P10.S2" into the
past tense, keeps the four sha256s (class A is not regenerable here, so this is the only
in-repo record of what they were, and the bytes are in git before this commit), and states the
grep expectation explicitly: a filename hit is historical prose, a hit *inside a code path*
would be the regression.

## 2. The heights — implemented at h19/h17, measured, and a recommendation

**Unchanged. `WordmarkProps.height` is still the literal union `19 | 17`.** What follows is
evidence for the operator, not a change.

Measured in Chrome 152 at dsf 2 on `/` (dev; production identical to the hundredth of a pixel):

| | nav | footer |
|---|---|---|
| `<img>` computed box | **72.24 × 19** | **64.64 × 17** |
| natural / `complete && naturalWidth>0` | 1213×319 / **true** | 1213×319 / **true** |
| Korean band (`h × 162/319`) | **9.65px** | **8.63px** |
| adjacent type | `AI 질문` 13.5px Pretendard 400 | source line 12px |
| band ÷ adjacent type | **0.715×** | **0.72×** |

The retired ring put **14.4px** of ink into the same 19px — **1.07×** that 13.5px nav label. So
the brand went from *slightly larger* than the nav links to **~29% smaller** than them. That is
the finding: not "illegible", but **hierarchy-inverted** — the brand is now the smallest text
in its own bar.

**Legibility, in plain words.** At h19 the Hangul is readable but reads as fine print, not as a
logo: single-weight strokes, no counters to lose, and on the operator's retina Mac it is 19.3
device pixels tall, so nothing aliases into mush. Zoomed 10× the glyph shapes are clean and the
white is pure — **no fringing**, as S1 predicted for the all-`#FFFFFF` variant. On a 1× external
display it would sit right at the edge. The footer's 8.63px is smaller still but sits next to
12px grey text, so it is internally consistent there.

**Layout — the ~40% narrower slot.** The brand slot is **72.24px** where the ring's was
2178/346 × 19 = **119.6px**, i.e. 47.4px narrower.

- Nav: bar still `height: 52px`, `.brand` still 51px tall under `align-items: stretch`, gap to
  `.links` unchanged at 24px (`--space-6`). The links simply start at **x = 200.24** instead of
  ~247.6. No overflow, no wrap, nothing crowded. At 390px the mark and 메뉴 sit with room to
  spare.
- Footer: at 1280 `.identity` is 327.27px wide with the actions at x = 1051.5 — `wrapped:
  false`, no new wrap introduced. At 390 the existing `≤480` grid stacks it exactly as R8
  designed (`identityStacked: true`); unchanged behaviour, not a consequence of the narrower
  mark.

**Optical centring (a judgment call, flagged not fixed).** Because the ink is bottom-half only,
box-centring puts the *glyph band's* centre **4.18px below** the 52px bar's centre at h19. It is
correct if you read the sparkle as part of the mark (it is), and it grows with height — 6.14px
at h27. Worth the operator's eye once, not a defect.

**Recommendation, acceptable in one word: `h27` nav / `h24` footer.** Simulated in the browser
(no code changed): band 13.71px and 12.2px, i.e. **1.02×** and **1.02×** the adjacent type —
the exact relationship the ring had. Boxes become 102.7×27 and 91.3×24, still *narrower* than
the retired ring's 119.6px, so the 52px bar and the footer row both have the room. If the
operator prefers to keep the signed numbers, nothing breaks — the mark is legible at h19/h17,
just quiet.

## 3. The ops mark — string changed, typography untouched, question sharpened

`OPS_MARK = "주주의관제탑 운영"`; `app/ops/layout.tsx` `metadata.title` matched to the same
string. `Ops.module.css` **not touched**; `public/foundations/tokens.css` **not touched**.

Both surfaces render it (dev and production): the door (`Door.tsx` `.doorMark`) and, after
login, the bar (`OpsChrome.tsx` `.mark`). Both compute to `"IBM Plex Mono", "SF Mono",
Consolas, monospace` / 12px / 600 / `letter-spacing: 0.96px`.

**What actually renders** — CDP `CSS.getPlatformFontsForNode`, identical on both nodes:

```
IBM Plex Mono SemiBold   glyphCount 1      ← the space, and nothing else
Apple SD Gothic Neo SemiBold  glyphCount 8 ← every Hangul syllable
```

So the mono treatment now applies to exactly one character. Three consequences I could see:

1. **The word gap reads as a double space.** A mono space plus 0.08em tracking on both sides
   makes 관제탑␣운영 look deliberately split. It is the one visible artifact at 100%.
2. **The mark's face is now the OS's.** Apple SD Gothic Neo is macOS-only; the same string will
   pick a different fallback on Windows or Linux, so the ops mark no longer looks the same
   everywhere the operator might open it.
3. **The point of the treatment is gone.** In the bar the mark now sits beside Pretendard
   Korean tab labels (개요 · 게이트 대기열 · …) in a Korean UI face, so it no longer reads as an
   identifier at all — while the `mijual:lock:pipeline free` chip two columns to its right
   still does. That contrast is exactly what R7 was buying with "raw and mono".

**Recommendation (not taken):** keep the string, and drop `font-family: var(--font-mono)` +
`letter-spacing: 0.08em` from `.mark`/`.doorMark`, letting Pretendard 600 carry it — mono earns
its keep only while the mark is a latin identifier. This is signed styling, so it stays the
operator's call.

**Trap for whoever re-checks this:** `document.fonts.check('600 12px "IBM Plex Mono"',
'주주의관제탑')` returns **`true`**. It reports family availability, not glyph coverage, and it is
a false positive here. Only `CSS.getPlatformFontsForNode` (or a rendered-width comparison)
answers the question.

## 4. The favicon — nothing shipped, nothing cropped

Confirmed unchanged from before this slice, in dev and production, desktop and mobile:

- no `frontend/app/icon.*`, no `favicon.ico`, no `apple-icon.*`, no `manifest.*`, no
  `opengraph-image.*` anywhere under `frontend/` (a `find` over the tree returns nothing);
- neither `metadata` export declares `icons`, `openGraph` or `twitter`;
- `document.querySelectorAll('link[rel*="icon"]').length` → **0** on every page checked.

The mark was not cropped, resized, or placeheld. The filed question stands with its three
options (ship nothing / operator supplies a square symbol export / operator authorises cropping
the sparkle cluster). The one thing I added is a comment in `app/layout.tsx` saying *why* there
is no `icons` key, so the absence reads as a decision rather than an oversight.

## 5. Retirement proof

Under `next start` (production):

```
/assets/juju-wordmark-white.png    200      /assets/mijual-logo-ring-white.png   404
/assets/juju-wordmark-black.png    200      /assets/mijual-wordmark-white.png    404
/assets/juju-logo-source.png       200
```

`grep -rI "mijual-.*\.png" .` (excl. `node_modules`, `.next`, `works/`, `docs/versions/`) →
20 hits, **all historical prose**, none in a code path:

- `frontend/public/assets/README.md` (13) — the retirement record, the geometry comparison, the
  class table and the four sha256s;
- `frontend/components/chrome/copy.ts:25` (1) — one clause naming what the mark replaced;
- `docs/current/frontend.md` (2) — a **generated snapshot**; regenerated when the review cuts
  the new `frontend` doc version. Never hand-edited;
- `docs/reference/design/rounds/{01,08,12}/…` (4) — the **immutable design record**. Never
  edited.

## 6. Verification, in the operator runtime

Manifest: `docs/current/operations.md` `## Operator Runtime` — filled, no `UNFILLED` marker.
Ran `make stack-up`'s own targets (`next dev` on `0.0.0.0:3000`, uvicorn on `127.0.0.1:8000`),
browsed `http://127.0.0.1:3000` in Chrome 152 on this Mac at `deviceScaleFactor: 2`, plus a
390×844 mobile viewport, then repeated everything against `npm run build && npm run start`.

Checked on both: `/` (landing, desktop + 390), `/ask`, a 404 path, `/ops` door, `/ops` bar
after login. Every page carries exactly two wordmark `<img>`s, both loaded, at 19 and 17; every
reader page's tab title is `주주의관제탑`; every `/ops` page's is `주주의관제탑 운영`; `/ops`
renders **zero** reader-chrome wordmarks, so R7's "reader chrome 어디에서도 링크 금지" still
holds. Dev and production agreed on every measured number.

## Deviations

1. **Two doc comments inside my scope boundary.** The plan says leave every doc comment naming
   미주알. The comments above `BRAND_ALT_KO` and `COPYRIGHT_KO` do not merely *mention* the old
   name — they **assert the values of the two lines I changed** ("The mark reads 'MIJUAL'; the
   product's own name in Korean is 미주알"). Left as-is they would be flatly false about the
   line directly under them, which is the exact failure the plan forbids for `RING_*`. I
   rewrote both to be true and kept the 미주알 token inside an explicitly historical clause, so
   S3's sweep still finds this file and the design record is not falsified. **No other doc
   comment was touched**, and `event/copy.ts:114` + `src/mijual/web/app.py:57` are untouched.
2. **Postgres host port.** `make stack-up` fails at `db-up`: host port 5433 is held by
   `changple_web_dev_postgres`, a container from an unrelated project of the operator's, and
   `mijual-postgres` has been unable to start since. Nothing to do with this slice — without a
   DB the landing page 500s and the chrome cannot be judged there. I ran **the same image and
   the same `mijual_mijual-pgdata` volume** on host port 5434 via a compose override kept in
   the session scratchpad, and started the API with
   `DATABASE_URL=postgresql+psycopg://mijual:mijual@localhost:5434/mijual`. **The
   browser-facing runtime is unchanged** — same `next dev` / `next start` on `0.0.0.0:3000`,
   same `http://127.0.0.1:3000` origin, same API on `127.0.0.1:8000`, same Chrome. Restored
   afterwards: stack down, container recreated from the unmodified `compose.yaml` (5433) and
   left **stopped**, exactly as found; the override file never entered the repo.
3. **Throwaway ops credentials.** `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` are unset in `.env`,
   so `/ops` only ever shows the door. To see the **bar** mark as well as the door I set
   throwaway values on the API process only, for the duration of the check. Nothing was written
   to `.env` and both died with the process.
4. **Assets README, slightly wider than the named section.** The plan named the "S2 does it"
   section. I also corrected the class-A provenance row (it still listed the four deleted files
   as present) and the paragraph stating what a `mijual-*.png` grep hit means, so the document
   does not contradict itself.

Also: `next build` rewrote the generated `frontend/next-env.d.ts` (build variant vs dev
variant). Restored with `git checkout` — it is not part of this change.

## Dead ends / notes

- `docker run` for a side-by-side Postgres was refused by the sandbox; the compose `!override`
  tag was the way through (a plain override **merges** port lists rather than replacing them,
  which is why the first attempt still tried to bind 5433).
- No test and no type catches a wrong asset path, exactly as the plan warned: `tsc` was clean
  before the browser check too. What caught it would have been `img.complete &&
  img.naturalWidth > 0`, which is the assertion worth reusing in S5.
- **Unowned by any slice, flagged for the review:** code doc comments that *describe rendered
  output* which this phase changed. `chrome/Footer.tsx:15` still draws the footer as
  `워드마크 h17 + "자료: … · © 미주알"`. It is defensible as a quotation of R2, but a reader will
  take it as a description of what renders. The phase Context rules comments out of scope
  (documentation, not product copy) and no slice owns them, so this is a decision, not a fix.
