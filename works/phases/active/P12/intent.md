# Intent — P12

- Captured at: 2026-09-03T20:57:00+09:00
- Origin: operator

## Original Input (verbatim)

> for the OG image adding and some design polish.
> ---
> 1. currently got no OG Image I guess. using our logo "주주의관제탑" create one. let the claude design make it.
> 2. the design polish, the disturbing part is logged in user dropdown on the nav. close, open icon size difference, and flickering it's size bcs of the defference.
> 3. find out another might flickering causes and fix them.
> ---
> gonna do this phase parallely.

Follow-ups during intake, verbatim:

> oh well kakaotalk shows me nothing though. and this isn't cached I never sent this before.

(with a KakaoTalk screenshot: the jujutower.com card showing the title 주주의관제탑 and the description, and a blank grey image area)

> I think just kakaotalk is bad discord work. diagnose kakao. could be ratio problem but you find out.

> I think current og image is enough

> oh find out it works. the kakaotalk. you can only handle flickering on the p12

Follow-ups after the phase was created, verbatim:

> maybe no design round is required. just use aside claude2 profile. fix it directly.

> no I like the phase. but the context is skip the design round fix it directly in the phase.

## Confirmed Intent (refined + clarified)

P12 is a **flicker-polish** phase and nothing else. Two things, in this order of certainty:

1. **The signed-in account dropdown in the nav jumps in size when it opens and closes.** The
   trigger frame (`frontend/components/chrome/AccountSlot.tsx`, `AccountSlotDesktop`) swaps a glyph
   pair for its caret — `▾` closed, `▴` open — and the two glyphs do not share a width in the font
   stack that renders them, so the frame's width changes on every toggle and the whole slot
   appears to flicker. Fix it so the frame keeps one size in both states; the caret stays a
   readable open/closed affordance (R8's signed design: hairline frame + caret + hover — see the
   component's header comment; do not restyle the frame, only stop the jump).
2. **Hunt for every other visible flicker and fix what is found.** Scope is **every user-facing
   page** — the landing, `/stocks`, `/portfolio`, `/ask`, `/events`, `/auth`, and the shared chrome
   (nav, account slot, footer, launcher) — on **desktop and mobile**, in the operator runtime
   **and** the production build (`## Operator Runtime` in the operations doc names both). "Flicker"
   here means anything that visibly jumps, resizes, re-paints, or pops in after first paint: layout
   shifts on load or on state change, hover/open states that move their neighbours, content that
   renders twice, icons or fonts that swap after paint. The hunt watches interactions over time in
   a real browser rather than one static pass.

**Dropped from the request, with the evidence:** item 1 (a new OG image). One already exists —
`frontend/app/opengraph-image.png`, 1200×630, the white wordmark plus a sparkle cluster on the
dark ground, shipped by P4's SEO slice (`09d56e6`) and wired through `OG_IMAGE` in
`frontend/lib/seo.ts`. During intake the operator saw KakaoTalk render a blank image area for
jujutower.com while Discord showed the card; production was checked from this session and was
correct on paper (absolute `og:image` + `og:image:width/height/type/alt` + `twitter:card
summary_large_image` on `/`; the PNG answers `200 image/png` to a browser UA and to a Kakao-scraper
UA through Cloudflare). Before any diagnosis slice was cut the operator reported KakaoTalk now shows
the image, and said the current image is enough. **No OG work, no design round, no Kakao diagnosis
in this phase.** If the blank Kakao card recurs, it is a new request.

**Not a visual-design phase, and the dropdown is fixed directly inside the phase.** There is no
`## Design Style` section on purpose: nothing here is a design round. The operator's instruction
after creation — "skip the design round, fix it directly in the phase" — means the dropdown fix is
an ordinary `fix` slice of P12 (no `co-work` slice, no handoff, no mockup gate), working inside the
already-signed R8 chrome and verified in Aside on the agent profile `claude2` (`--account u2`).
It does **not** mean an ad hoc edit outside the phase workflow; the phase is the route.

**Sequential, not parallel.** The operator's opening line said parallel, but the intake settled on
queueing P12 behind P4 (see Clarifications). `new-phase` printed the advisory
`parallel-start P12` hint; it was relayed and declined. It stays available only while P12 is
`planned`, and only from a clean tree on the default stream.

## Clarifications Resolved

- Q: An OG image already exists (P4's SEO slice) and production serves it with correct tags, yet
  KakaoTalk shows a blank card — how should item 1 be scoped? — A: "I think just kakaotalk is bad
  discord work. diagnose kakao. could be ratio problem but you find out." Then, at the confirmation
  step: "oh find out it works. the kakaotalk. you can only handle flickering on the p12." →
  **item 1 dropped entirely.**
- Q: The OG card would be a visual design round — which design style (paired / build-after /
  design-only)? — A: "I think current og image is enough" → **no design round; no design style.**
- Q: Where should the hunt for other flicker look? — A: **Every user-facing page, desktop +
  mobile**, in the operator runtime and the production build, watching interactions over time
  rather than one static pass.
- Q: `parallel-start` refuses on a dirty tree and P4.F11's uncommitted work is in it — when should
  the phase go parallel? — A: **"Create now, stay sequential."** No parallel mode.
- Q (confirmation): name "Kakao share preview and flicker polish" + the two-part objective? — A:
  the Kakao half was withdrawn ("you can only handle flickering on the p12"), so the phase was
  created as **"Flicker polish"** with the flicker half of that objective unchanged.
- After creation: "maybe no design round is required. just use aside claude2 profile. fix it
  directly." — read at first as an ad hoc fix outside the phase; the operator corrected it: **"no I
  like the phase. but the context is skip the design round fix it directly in the phase."** → the
  dropdown fix is a plain `fix` slice inside P12, no design round, verified in Aside `--account u2`.
  No product code was changed before the correction; the one throwaway test account the
  measurement needed was created and deleted through the product's own 계정 삭제 (qa hygiene rule).

## Notes

- **The jump is measured, not guessed** (dev runtime, 1280-wide desktop, Aside `--account u2`,
  2026-09-03). The caret renders in `notoSansKr` at 12px. Advance widths there: `▾` 5.67px,
  `▴` 11.05px (`▼` and `▲` are both 11.05px too). So the frame goes **239.67px closed → 245.05px
  open (+5.38px)** with its right edge anchored, i.e. the whole control's left edge slides on every
  toggle; height stays 32px in both states. It is width only, and it is the glyph pair, nothing
  else in the frame changes. Any fix that gives the caret one constant box in both states ends it —
  a single glyph flipped by `transform` (layout-neutral), or a fixed-width centered caret box — the
  slice picks, keeping the ▾/▴ reading R8 signed.
- **Where the caret lives:** `AccountSlotDesktop` renders `{open ? CARET_OPEN : CARET_CLOSED}`
  (`"▴"` / `"▾"`) in a `<span class={styles.caret}>` with `flex: none; font-size: var(--text-sm);
  line-height: 1` (`AccountSlot.module.css`). The frame is `max-width: 280px` with an ellipsised
  email beside it. The mobile sheet (`AccountSlotSheet`) has no caret and is not affected.
- **Do not double-fix the landing.** P4 is mid-flight on the landing's idle cost (`P4.F7` landed the
  starfield twinkle on literal keyframes; `P4.F11` is re-expressing the Hero orbiter as a
  composited transform, uncommitted at capture time). The flicker hunt reads those two slices'
  `result.md` before touching `frontend/components/landing/` and treats their constraint as its
  own: the landing looks and moves exactly as it does today.
- **P4's release freeze opens 2026-09-07 11:00 KST.** P12 runs after P4 on the default stream;
  DECOMP should cut it so nothing lands on production inside that freeze without the operator
  saying so.
- **Instrument:** real-browser work runs through Aside on the agent's own account per the
  `## Operator Runtime` manifest (never the operator's signed-in profile). Desktop and mobile
  viewports, dev runtime and the production build, as the manifest records them.
- **Acceptance gate:** the whole phase is operator-visible surface, so DECOMP will declare
  `accept-gate P12 --require`; the review's walkthrough should have the operator open and close
  the account dropdown and walk the pages the hunt touched.
