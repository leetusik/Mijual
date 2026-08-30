# Plan — P10.S6 · Design round: the mark in the chrome, and the chatbot launcher

`kind: co-work` · `risk: high` · order 6 · Round **R17**, `docs/reference/design/rounds/17-brand-mark-launcher/`

This is the phase's one design round. It runs **inline → dispatched → inline** and stops the
loop **twice**, per the `design-cowork` skill. I write the handoff and decide nothing.

## Why this round exists

`P10.S5` shipped the rebrand and the operator walked the acceptance gate. They did not clear it.
Two of the three gate questions they answered on the spot; the third they sent here, in their own
words: *"just open a design slice, I'll handle there."* Then they replaced the mark itself —
*"previous one was so thin"* — and added the launcher to this round's subject by declining to pick
a treatment for it (the colour work is mine; the treatment is not).

So the round has exactly two subjects, and I am not to widen it. The operator has already cut one
over-elaborate plan this phase: *"just one design round and then do rest. you overcomplicating it."*

## The two subjects

1. **The wordmark in the chrome** — how big it is in the 52px nav bar and in the footer row, and
   how it sits there vertically. Signed today at `h19` / `h17` (R2 §Page shell, re-cut by R8).
2. **The chatbot launcher's mark** — R6's animated CSS Saturn is being retired for the operator's
   sparkle symbol. What replaces it, whether the 68×50 chat-bubble frame and tail survive, what
   happens to R6's sanctioned ambient-motion exception, and what the open/hover/active states look
   like.

Everything else in round 2 is **`P10.S7`'s** mechanical work and is *not* this round's subject:
the bold source file, the white derivation, the favicon, the `/ops` mono drop, the Noto Sans KR
pipeline. The round is told about them where they change what it is looking at.

## What I do in this slice, in order

**Span 1 — inline (this one).** `start-slice`, write
`docs/reference/design/rounds/17-brand-mark-launcher/handoff.md`, commit, `set-slice-status
P10.S6 pending`, and **STOP at PENDING #1**.

- **No `git push`.** The operator chose a **local-directory** connection for Claude Design
  (`intent.md` § Clarifications Resolved), so the repository stays unpublished. The skill's "push
  the branch" step does not apply and this round authorises no push.
- The operator uploads both PNGs into the session as **attachments** — that is why no asset slice
  runs first.
- Report PENDING #1 as what it is: a **mechanical wait, not an approval**.

**Span 2 — inline, on resume.** `DesignSync` read-back (`list_files` first, verify the exact card
paths the handoff names), the card-contract and concreteness checks, land the returned record
**as-is** under `output/`, write the spec pointers into `phase.md`, commit.

**Span 3 — dispatched.** `slice-executor-high` builds the runnable mockup from `build-prompt.md`
— no DesignSync, stubbed data, throwaway route, verified in the `## Operator Runtime` runtime and
additionally in the production build. Commit, then **STOP at PENDING #2**, the gate.

**Span 4 — inline, on the operator's literal approval.** `SIGNOFF.md`, the pure regroup (line 1's
`group` value only, every byte below identical), `finish-slice`, commit, and the loop continues to
`P10.S7`.

## The handoff's shape

House shape, following `rounds/16-smart-assistant/handoff.md`:

1. **Product context** — what 주주의관제탑 is, and that this is a rebrand mid-flight.
2. **Locked vs. in play.** In play: the wordmark's rendered size, optical alignment and clear
   space in both chrome surfaces; the launcher's mark, frame, states and motion. Locked: the mark
   **artwork** (an operator delivery, not redrawable), the name string, `foundations/tokens.css`
   (signed R8), R8's chrome structure (nav destinations, account slot, footer row content and
   order), where the launcher may render (desktop only, never `/ask`, never ops — R14's boundary),
   all copy, and the a11y / reduced-motion floor.
3. **Where to look** — real paths and the real measured numbers, as **documentation**.
4. **Required-output manifest** — the `@dsCard` card set at named paths, a record with every
   departure logged, and a `build-prompt.md` complete enough to build the mockup from without
   inventing anything.
5. **Open questions, posed back** — never answered here.

## The measurements the handoff carries as documentation

Measured, not asserted. Retired thin mark vs. the operator's replacement:

| | shipped (thin) | `juju2.png` (new) |
|---|---|---|
| trimmed box | 1213×319 (3.80:1) | **1292×371 (3.48:1)** |
| Korean glyph band | 1063×162 — 50.8% of box | **1132×176 — 47.4% of box** |
| ink coverage in that band | 16.1% | **37.5% (2.3×)** |
| band at `h19` / `h17` | 9.65 / 8.63px | **9.01 / 8.06px** |

Adjacent type: nav link `--text-base` **13.5px**, footer source line `--text-sm` **12px**, bar
height **52px**. So at the signed heights the brand is **0.72×** the type beside it, where the
retired R2 ring was **1.07×**. The ink is bottom-half only, so box-centring also sits the glyph
band **4.18px below** the bar's optical centre. `P10.S2` measured all of this in the running
product; the numbers are in `slices/P10.S2/result.md`.

The symbol: `favicon_and_chatbot_widget.png`, 278×278, the sparkle cluster alone on transparency,
trimming to **261×216** — so it is *not* square, and how it sits in a square box is a real
decision rather than a crop.

## The ordering risk I must surface, not solve

`P10.S7` swaps the Korean face from **Pretendard Variable** to **Noto Sans KR** in the same slice
that applies this round. The two have different Korean glyph proportions, so a mark size signed
against today's rendering may read differently once the face lands. This is **not mine to
resolve** — I state the incoming face as fact in the handoff, pose the question back (design
against which face?), and flag it to the operator at PENDING #1. I do not reorder the phase around
it; the operator already rejected preparatory slices.

## Card contract

- Groups carry the round's address while it is under review: **`⏳ P10.S6 · Chrome`** and
  **`⏳ P10.S6 · Ask`** (the launcher lives in `components/ask/`; `Ask` and `Chrome` are both
  existing library groups, from R14 and R8). Retired at SIGNOFF by the pure regroup.
- One card per reviewable unit, never a monolith. Exact paths named in the handoff so the
  read-back can verify them with `list_files`.
- Line 1 of every card is `<!-- @dsCard group="…" viewport="…" -->` — no `name`, no `subtitle`.

## Validation for this slice

Spans 1 and 2 write no code, so validation is `python3 scripts/workflow.py validate` plus the
read-back's own two checks (every named card path present; concreteness bar met). Span 3's mockup
is the executor's to verify — it runs, every designed element and state renders, it matches the
record, in the operator's runtime and in a production build. The **functional sweep does not apply
to the mockup**; non-functional controls are acceptable there and must be named as such in the
PENDING #2 walkthrough.

## What would make me stop instead of continue

- Read-back returns prose, a monolith, or misses a named card path → `needs_operator`, card
  contract restated. I do not write the cards myself.
- The record leaves a decision to invent → `needs_operator`. I never fill a design gap.
- The mockup executor returns `needs_operator` because the record is wrong, inconsistent or too
  thin → I raise it with the operator rather than inventing the missing piece.
