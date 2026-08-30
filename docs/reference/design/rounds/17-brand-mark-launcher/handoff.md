# R17 handoff — 주주의관제탑: the mark in the chrome, and the chatbot launcher

- Round **R17** · slice `P10.S6` (co-work) · the apply slice `P10.S7` follows immediately
- Claude Design project: **"Mijual Design System"** — connected to this repository as a
  **local directory** this round (not GitHub; the repository stays unpublished)
- Review groups for this round's cards: **`⏳ P10.S6 · Chrome`** and **`⏳ P10.S6 · Ask`**
- **Token freeze:** `foundations/tokens.css` is signed (R8) and this round is expected to change
  no token. If the session decides otherwise, the delta is signed in `result.md` like any decision.
- Common rules: **R10 §0 stands as-is** (keep-all, nowrap mono, tabular-nums, border-box, single
  767px breakpoint, hit floors 32px desktop / 44px ≤767).

**Read this first — the product was renamed underneath the design system.** Phase P10 replaced the
product's identity: **미주알 → 주주의관제탑**, unspaced, **no latin mark anywhere**. The English
`MIJUAL` wordmark and the R2 ring logo are **retired and deleted**. Every card, contract and record
from R1–R16 that says 미주알 or draws the ring is describing something that no longer exists — the
*structure* those rounds signed still governs, the *name and the artwork* do not. (The design
project keeps its own name, "Mijual Design System"; that is out of scope by the operator's
decision.)

That rebrand shipped and the operator walked its acceptance gate. **They did not clear it.** Two of
its three open questions they answered on the spot; the third they sent to this round, verbatim:
*"just open a design slice, I'll handle there."* Then they replaced the mark itself —
*"previous one was so thin"*. This round is the consequence.

---

## 1. Product context

**주주의관제탑** — free, anonymous, **Korean-only** reader over verified Korean corporate filings
(유상증자 rights offerings), on a dark "cosmos" surface (R2.1). Its one promise: **numbers come from
filings, auditable end to end.** Readers are Korean retail shareholders checking whether a filing
affects a stock they hold; they arrive from search or a link, on desktop and on phones.

The two surfaces this round touches are the ones present on **every** page:

- the **global chrome** — a 52px nav bar and a one-row footer, both carrying the brand mark
  (R2 §Page shell, re-cut by R8 §1/§3/§4);
- the **chatbot launcher** — a fixed bottom-right affordance that opens the AI 질문 widget
  (R6 §Surfaces 「런처 (클릭 전)」 + §런처 마크, revision ⑧; polished by R14).

## 2. What this round must decide

Two subjects. **Nothing else** — the operator cut a wider plan this phase as overcomplicated, and
the rest of the work is already assigned to the apply slice (§6).

### 2.1 The wordmark in the chrome

The mark is set at **`h19`** in the nav and **`h17`** in the footer — R2's two numbers, unchanged
since. The new artwork changes the arithmetic underneath them (§4), and the operator has asked this
round to settle the size rather than accept the signed one by default.

In play: **the rendered height in each of the two surfaces, the vertical alignment inside the 52px
bar and inside the footer row, and the clear space around the mark.**

### 2.2 The chatbot launcher's mark

R6 signed a **22×22 "Saturn"** built entirely in CSS — a `#dfe9e4` planet with a repeating-gradient
rotation band on a 4.5s loop, and a `rgba(95,208,165,.9)` ring split into two clipped halves
(painted behind and in front of the planet, sharing one 14s `ringdrift`) so it reads as a ring the
planet passes through. It sits inside a **68×50** `#0e1a15` chat-message frame with an 11×11 tail
rotated 45° at right 12 / bottom −6. Hover scales the mark 1.35 (frame fixed), active 1.15; when
the widget opens the mark fades out and a 16px × replaces it. **This is the product's one
sanctioned ambient-motion exception**, granted by an operator note in R6 — everywhere else, "no
spinners, no ambient motion" holds.

The operator is retiring that mark for the sparkle symbol they have supplied (§3). What the round
must decide:

- **what the mark becomes** — the sparkle cluster, at what size, in what colour treatment;
- **whether the 68×50 frame and its tail survive**, or the launcher becomes a bare mark in the
  corner;
- **what happens to the motion exception** — does the sparkle move at all, and if so how, or does
  R6's exception retire with the Saturn;
- **the states**: rest, hover, active, and the open state (today: mark fades, × appears).

## 3. Operator attachments — upload these into the session

Both are the operator's own files, delivered outside the design project. They are **the artwork**;
this round places it, it does not redraw it.

| file | what it is |
|---|---|
| `juju2.png` | the wordmark **주주의관제탑** with a small sparkle cluster at the upper right, black on transparency. 1614×1076, trimming to **1292×371**. |
| `favicon_and_chatbot_widget.png` | the **sparkle cluster alone**, black on transparency. 278×278, trimming to **261×216** — note it is **not square**. |

Neither is a design-project export and neither is redrawable here. The apply slice lands them
byte-exact and derives a white variant from each by an alpha-preserving recolor; the *shape* never
changes.

## 4. Where to look, and the numbers — documentation, not a proposal

Every number below was measured in the running product by `P10.S2` and re-measured on the new
artwork by the orchestrator. They are stated so the round can decide with facts in front of it.
**None of them is a recommendation.**

### 4.1 The artwork, old and new

| | shipped mark (the thin one) | `juju2.png` (the replacement) |
|---|---|---|
| trimmed box | 1213×319 — **3.80 : 1** | **1292×371 — 3.48 : 1** |
| Korean glyph band | 1063×162 — **50.8%** of box height | **1132×176 — 47.4%** of box height |
| ink coverage within that band | **16.1%** | **37.5%** — 2.3× |
| glyph band rendered at `h19` / `h17` | 9.65 / 8.63 px | **9.01 / 8.06 px** |

The box is **not filled evenly**: the sparkle cluster sits alone in the upper right, the Korean
glyphs in the bottom portion, with an empty band between them. So a height-constrained placement
renders a mark whose *legible* part is roughly half the declared height — and, because the ink is
bottom-heavy, box-centring sits the glyph band **4.18px below** the 52px bar's optical centre.

For comparison, the **retired R2 ring** put **14.4px** of ink into the same 19px box (75.7% of a
2178×346 box).

### 4.2 The type the mark sits beside

- nav link: `--text-base` = **13.5px**, active 600 + 2px `#fff` underline; nav bar **52px**,
  `gap: var(--space-6)` between brand and links
- footer source row: `--text-sm` = **12px**, `rgba(255,255,255,.45)`, reading
  `자료: 금융감독원 DART 전자공시 · © 주주의관제탑 · 의견 보내기 · AI 질문`

So at the signed heights the brand renders **0.72×** the type beside it. The retired ring was
**1.07×**. In the footer the name is set **twice** in one row — the mark and the typed
`© 주주의관제탑` — and the typed one is currently the larger and more legible of the two.

### 4.3 The face beneath it is changing in the same apply slice

The Korean face moves from **Pretendard Variable** to **Noto Sans KR** in `P10.S7` — the operator's
instruction, adopting a sibling product's pipeline (self-hosted subset, `next/font/local`). Noto
Sans KR and Pretendard have different Korean glyph proportions at the same `font-size`, so the type
beside the mark will not render identically to what a screenshot of today's product shows. **This
round should know that**, which is why §7 poses it back rather than assuming an answer.

### 4.4 Real paths in this repository

The project reads this directory, so these are live:

- chrome: `frontend/components/chrome/Nav.tsx` · `Nav.module.css` · `Footer.tsx` ·
  `Footer.module.css` · `Wordmark.tsx` · `copy.ts` (`WORDMARK_WHITE`, `WORDMARK_NATURAL`,
  `BRAND_ALT_KO`, `COPYRIGHT_KO`)
- launcher: `frontend/components/ask/AskLauncher.tsx` · `Launcher.module.css` (every literal in
  that file is R6's own, with its reason beside it) · `AskSurface.tsx` (where it may render)
- tokens and foundations: `frontend/public/foundations/tokens.css` · `fonts.css`
- the brand binaries and their provenance rules: `frontend/public/assets/README.md`
- the anti-lorem pack: `docs/reference/design/grounding/` — real board counts, real headline
  numbers, the real Korean copy (`copy-inventory.md`), real edge states. **Ground the cards in
  this; never lorem.**
- what the two surfaces were signed as: `rounds/02-landing-chrome/output/` (R2, R2.1),
  `rounds/08-foundations-chrome/output/` (R8), `rounds/06-explain/output/` (R6 — the launcher),
  `rounds/14-ask/output/` (R14 — the ask surface's current baseline)

## 5. Locked vs. in play

**In play this round:**

- the wordmark's **rendered height** in the nav and in the footer, its **vertical alignment** in
  both, and the **clear space** around it;
- the launcher's **mark, frame, tail, states and motion** — including whether R6's ambient-motion
  exception survives the Saturn's retirement, and whether the chat-bubble frame survives at all.

**Locked:**

- **the artwork itself.** Both PNGs are operator deliveries. The round places, sizes and colours
  them; it does not redraw, recompose, re-letter or crop the wordmark. (Whether the *symbol* is
  padded or positioned inside a square box is a placement decision and is in play — see §7 Q3.)
- **the name string** `주주의관제탑` — unspaced, no latin mark, no tagline. Settled by the operator
  at phase intent.
- **`foundations/tokens.css`** — signed R8, frozen (see the header note).
- **R8's chrome structure** — nav destinations (`AI 질문 · 보유 종목`), the account slot and its
  menu, the mobile sheet's behaviour, the footer's single row and the content and order within it.
  This round changes how the *mark* sits in that structure, not the structure.
- **where the launcher may render** — desktop only (≤767px renders nothing), never on `/ask`, never
  inside the ops chrome, and never colliding with the 의견 보내기 trigger's corner. R14's boundary,
  structural.
- **all copy.** Not in play this round, and no new Korean string is needed by either subject.
- **the a11y floor** — `prefers-reduced-motion` stops every animation and the hover scale; hit
  targets ≥32px desktop / ≥44px ≤767; the mark keeps a text equivalent (`BRAND_ALT_KO`).

## 6. Not this round's subject

The apply slice `P10.S7` does all of this mechanically, from decisions the operator has already
taken. Listed so the session does not spend itself on them:

- landing the new source PNGs and deriving their white variants (an alpha-preserving recolor with a
  recorded command, verified by pixel signature);
- the **favicon** — the operator answered the gate's favicon question by supplying the square symbol
  export, so one finally ships. *How* the symbol sits inside a square icon box is the one part of
  this that touches design, and it is posed back as Q3;
- the **`/ops` mark's typography** — the operator answered at the gate: drop `--font-mono` and its
  0.08em tracking from `.mark` / `.doorMark`. Decided, not in play;
- the **Korean font pipeline** — Pretendard → Noto Sans KR, self-hosted subset. Decided, not in
  play; relevant only as §4.3's context.

## 7. Open questions — posed back, answered in the session

**Q1 — the wordmark's size, the operator's own question.** At `h19`/`h17` the brand renders 0.72×
the type beside it, where the ring it replaced was 1.07× (§4.2). The new artwork is 2.3× denser in
ink but marginally *shorter* in proportion (§4.1). Do the signed heights stand, or does the mark
grow? If it grows: to what, in each of the two surfaces, and does the footer — where the name is
already set twice in one row — take the same treatment as the nav?

**Q2 — the vertical placement.** The ink is bottom-heavy, so box-centring sits the glyph band
4.18px below the 52px bar's optical centre (§4.1). Is the mark centred by its **box** or by its
**ink**, and does the sparkle cluster count as ink for that purpose?

**Q3 — the symbol in a square.** The sparkle export trims to 261×216 — not square. In a favicon box
and in the launcher, does it sit centred with padding, optically centred, or filling one axis? Is
the answer the same in both places?

**Q4 — the launcher, the whole of it.** Does the sparkle sit inside R6's 68×50 chat-bubble frame
and tail, or does the frame retire with the Saturn? If the frame goes, what tells a reader the
corner is a chat affordance at all?

**Q5 — the motion exception.** R6 granted the launcher the product's only ambient motion, by
operator note, and the Saturn was the reason. Does the sparkle move — and if so, is it ambient
(always) or a response to hover/focus — or does the exception retire here and the corner go still?

**Q6 — which face to design against.** §4.3: Pretendard is replaced by Noto Sans KR in the same
apply slice. Should this round judge the mark against today's Pretendard rendering or against the
incoming Noto Sans KR? If the latter, the cards should set Noto Sans KR so the comparison is real.

**Q7 — is there a mark this round should *not* place?** The retired R2 ring closed R1's disclosed
"missing symbol mark" gap; the wordmark alone reopened it, and the sparkle now fills it for the
favicon and the launcher. Does the sparkle become a first-class symbol mark in the design system —
with its own card and its own rules — or is it only these two placements?

## 8. Required outputs — a round is incomplete without all three

### 8.1 The card set

The Design System pane builds its index from a **first-line marker** in each preview HTML. **No
marker → no card → an empty pane**, however good the design is.

- **Line 1 of every card file** is exactly:
  `<!-- @dsCard group="⏳ P10.S6 · Chrome" viewport="1280x400" -->`
  (or the `Ask` group, and whatever viewport suits the card). There is **no `name` and no
  `subtitle` attribute** — a card is addressed by its **file path**, so say what it is in the
  filename and in `result.md`.
- **One card per reviewable unit.** Never one monolithic "design system" page — the operator fixes
  one card at a time, and a monolith cannot be reviewed or superseded piecemeal.
- Cards link a `tokens.css` carrying the round's real values (expected: byte-equal to the frozen
  R8 file).
- **Ground every card in `grounding/`** — real nav labels, the real footer row, real Korean copy.
  Never lorem.

**The exact card paths this round must produce** (the read-back verifies these with `list_files`;
extra cards are welcome, missing ones are not):

| path | group | what it must show |
|---|---|---|
| `chrome/NavMark.html` | `⏳ P10.S6 · Chrome` | the mark in the real 52px bar beside the real nav links, at the decided size and alignment |
| `chrome/FooterMark.html` | `⏳ P10.S6 · Chrome` | the mark in the real one-row footer, beside the typed `© 주주의관제탑` |
| `chrome/MarkScale.html` | `⏳ P10.S6 · Chrome` | the size decision itself — the signed `h19`/`h17` against whatever the round chooses, so the operator can see what they are picking |
| `ask/Launcher.html` | `⏳ P10.S6 · Ask` | the launcher at rest, in its corner, on the cosmos surface |
| `ask/LauncherStates.html` | `⏳ P10.S6 · Ask` | every state: rest · hover · active · open · reduced-motion |
| `components/BrandSymbol.html` | `⏳ P10.S6 · Chrome` | the sparkle as a symbol — how it sits in a square box, at favicon sizes (16/32/180) and at launcher size |

### 8.2 A record of what was designed

Every decision, and **every departure logged** — including anything the session abandoned or re-cut
mid-way, and the operator's in-session answers to Q1–Q7. If the session produces Claude Design's own
**handoff bundle**, that bundle **is** the record and the contract; it is taken as-is and
`result.md` / `build-prompt.md` are only the names it lands under if it brings none of its own.

### 8.3 An implementation contract

Complete enough to **build the mockup from without inventing anything** — exact values, states,
breakpoints, motion timings and easings, and what supersedes what in R2/R6/R8. Markdown alone is
not a round. Two consumers read it and **neither can see the cards**: the mockup build and the
apply slice are both dispatched to an executor with no access to the design project. If the cards
are needed to make it buildable, the contract is what is short.

## 9. Definition of done

- The cards **appear in the Design System pane** — not merely that the files exist.
- Every path in §8.1 is present, each with a valid `@dsCard` marker on line 1.
- Q1–Q7 are answered in the record, in the operator's own decisions.
- The contract of §8.3 is complete enough that the mockup can be built from it alone.
- Any token change is signed explicitly; otherwise the record states **"Token delta: None."**

---

*This handoff says what to cover and poses questions back. It proposes no size, no colour, no
motion and no layout — those are the session's to decide, with the operator.*
