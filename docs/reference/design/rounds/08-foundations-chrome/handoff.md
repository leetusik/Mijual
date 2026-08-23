# Design Handoff — Round 8: Polish — Foundations + Global Chrome

- Round: **R8** (P8 polish pass, surface 1 of 8) · slice `P8.S2` · written 2026-08-23
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main branch, pushed at handoff commit)
- Builds on: **R1, R2/R2.1, R5 (account slot), R6 (launcher) as signed** and the P7 operator
  overrides recorded in `docs/reference/design/SIGNOFF.md` / `docs/current/frontend.md`. Those
  rounds are **locked context** except where this handoff explicitly opens them; R8 is a
  **polish round — no new features** — and, per `SIGNOFF.md` precedence, what R8 signs
  supersedes the parts of R1/R2/R5 it touches.

## 1. Product context

미주알 is the Korean-only 관제 현황판 for expiring shareholder rights (유증 신주인수권 · CB 오버행 ·
매수청구권), built over a DART-derived pipeline. P5–P7 shipped the product; P8 walks every
surface with the operator and polishes it. **This round polishes the global chrome** — the
52px bar, the two-slot nav, the account slot, the mobile sheet, the footer — and the product's
**feedback path (의견)**, which today is three dead buttons because vocky ships no widget.

The operator walked the chrome on 2026-08-23 (findings in `works/phases/active/P8/phase.md`
§"R8 walk") and answered item by item. Their answers below are **direction** (what to fix)
and **REFERENCE — data, not a proposal** for how. Claude Design + the operator decide how it
looks.

## 2. Scope checklist — what this round must cover

Operator decisions, verbatim where it matters (2026-08-23):

- [ ] **의견 (feedback) placement + the feedback-send surface.** Operator: *"the 의견 will be
      shown at the footer, and the stacked menu. not the bare nav. and you should connect
      vocky service … note that we should make feedback send design. no agent mcp linked
      yet."* So: **drop the nav `[의견]` chip**; keep the **footer link** and the **mobile
      sheet row**; and **design the feedback-send surface itself** — vocky has **no
      embeddable widget**, so 미주알 owns the UI: what opens when a reader taps 의견 보내기
      (panel / sheet / inline — the session's call), the message field, the send action, and
      the states **sending / sent / failed (retry) / empty-message**. Data contract is locked
      (§3, §4): the page posts to 미주알's own API, which forwards server-side to vocky
      `POST /api/feedback` with `message`, `source.product="mijual"`, `recorded_by="human"`,
      `channel` (`web`/`mobile`), `target_type="surface"`, optional `session_id`/`tags`. Nothing
      else is collected unless the session decides a field is needed (e.g. optional contact) —
      log it as a departure and keep it optional. **Korean copy for this surface is in play
      this round** (none exists yet — P3's copy inventory never drew it).
- [ ] **Nav: two destinations + a new third slot for the reader's holdings.** Operator on the
      empty band under the board (walk item 9): *"we gonna add a section for the portfolio.
      '포트폴리오' → with no signin, just sample, with a sign[-in], then show the user's
      portfolio. but i'm not sure we can call it 'portfolio'. you suggest if better term."* So
      the nav becomes **관제 현황판 · AI 질문 · ⟨holdings slot⟩**, where the slot opens the
      **sample portfolio** signed out and the **reader's own portfolio** signed in (both already
      exist: `/portfolio` with `SampleBanner` / 샘플 모드). This **replaces** the lonely landing
      link "내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →" (and closes the empty band). The
      **label is open** — see §6 Q1; orchestrator's suggestion listed there as REFERENCE.
- [ ] **Account slot (signed in).** Operator: *"show the full email. and random generated icon
      for the account. we could give a frame for the show that the email and the icon
      interaction possible."* So: the **full email** (no `swan…com` truncation), a **generated
      identicon** (deterministic from the account — style is the session's), and a **frame /
      affordance** that says "this is a menu"; fix the dropdown's alignment (today it hangs
      off-centre between the email and the edge). Menu rows stay 내 포트폴리오 / 알림 설정 /
      로그아웃 (R5) — reconcile the first row with the new nav slot (same destination: one of
      them may go; the session decides, log it).
- [ ] **Footer.** Operator: *"remove the text and keep it simple and clean."* Remove the prose
      — the tagline, the provenance sentence, the gate-cost sentence ("49.2억원 [추정]은 할인율
      인용이 …"), the disclaimer — and re-cut a minimal footer: wordmark, the 의견 보내기 entry,
      whatever else the session judges essential (source attribution "자료: 금융감독원 DART
      전자공시" and © are candidates, not requirements). Note the Korean prose in the footer
      today is set in the mono numeral face at 11px — whatever remains should read as Korean.
- [ ] **Mobile sheet + mobile footer.** Operator delegated (*"you fix it as you want"*): the
      `메뉴` sheet currently pushes the page down inline with no overlay/backdrop/닫기 state,
      and the footer's bottom row orphans "AI 질문" on its own line at 390px. **In play** — the
      session decides (sheet vs inline, close affordance, row wrapping), on the rows-≥48px floor.
- [ ] **Cards refreshed for everything above, desktop and 390px mobile**, signed-out and
      signed-in, with the AI 질문 launcher corner respected (R6: the launcher owns bottom-right;
      nothing of 의견 floats).

**Explicitly NOT in this round (operator decisions at the same gate):** favicon — *"leave the
favicon for now. defer"* (filed as a deferred job); 404 page — *"make 404 default"* (stays
Next's default; no card); nav hover — *"current hover interaction of AI 질문 is enough"*; focus
treatment — unchanged (P7 split stands); motion — *"motion is fine so far"*; `<title>` / meta —
untouched.

Cross-cutting (every round): Korean-only surface; mobile-first; a11y/reduced-motion floor;
**no new features** — the holdings nav slot points at a surface that already exists.

## 3. Locked vs. in play

**Locked:** R1 tokens/type/spacing/motion/square-hairline system and the `.cosmos` scope
(R2.1); Pretendard for Korean prose, IBM Plex Mono for numerals only; the 52px bar; the two
existing nav destinations and their labels (관제 현황판 · AI 질문); R5's account-menu rows and
R5-1's 로그아웃-without-dialog; R6's launcher corner; the P7 focus split; the vocky **data
contract** (§4 — which fields exist and that the key never reaches the browser); the rule
that 의견 is **chrome-level, never a floating corner button** (R2 §6-4, restated by the
operator: footer + sheet only); all other product copy.

**In play:** the feedback-send surface (layout, states, **and its Korean copy — the dated
exception of this round**); the nav's third-slot label (Q1) and how the slot reads signed
out vs in; the account slot's identicon, frame, full-email layout and menu alignment; the
footer's content and arrangement after the prose removal; the mobile sheet pattern and the
mobile footer wrap; whatever the session finds in the chrome that this list missed (log it
as a departure). A token change, if any, is a **new `foundations/tokens.css` from the
session** — the repo's copy is re-vendored from the landed file, never hand-edited.

## 4. Where to look — real paths, real data shapes

- **Chrome as built:** `frontend/components/chrome/` — `SiteChrome.tsx`, `Nav.tsx`, `Footer.tsx`,
  `AccountSlot.tsx` (+ `useAccount.ts`), `Wordmark.tsx`, `VockyTrigger.tsx` (the three
  `data-vocky-trigger` elements), `VockyScript.tsx` (the env seam that never bound), `copy.ts`
  (every chrome string with its citation — read it before touching a label), the `.module.css`
  files beside them; `frontend/app/layout.tsx`, `frontend/app/shell.css`.
- **Tokens / type:** `frontend/public/foundations/tokens.css` (= R2's landed file + provenance
  header), `fonts.css`; the landed records `docs/reference/design/rounds/01-brand-foundations/
  output/` and `rounds/02-landing-chrome/output/` (R2 §Page shell, §vocky, R2.1 cosmos re-cut).
- **Account slot record:** `rounds/05-account/output/` (§Chrome 개정 ⑤ — 축약 이메일 메뉴, which
  this round supersedes with the full email + identicon).
- **The portfolio surface the new slot opens:** `frontend/app/portfolio/page.tsx`,
  `frontend/components/portfolio/` (`SampleBanner`, 샘플 모드 carry-over — P7.S8 notes in
  `works/phases/active/P7/phase.md`), `frontend/lib/sample.ts`, `frontend/lib/routes.ts`.
- **Feedback today:** the AI 질문 agent's `save_feedback` tool
  (`src/mijual/agent/tools.py` → `mijual.web.conversationstore.record_feedback`, an operator
  queue visible at `/ops/feedback`). The new 의견 surface is a separate, human-recorded path;
  whether the ops queue should also see vocky-sent 의견 is an apply-time question, not a design
  one.
- **vocky (external, REFERENCE — data, not a proposal):** `https://vocky.hi2vi.com`, README
  `https://github.com/leetusik/vocky#readme`. `POST /api/feedback`, `Authorization: Bearer
  vk_…` (a **project-scoped key the operator holds; it lives in the server's `.env` as
  `VOCKY_API_KEY` and is never shipped to the browser or written into any record**). Payload:
  `message` (required, non-blank), `source.product` (required → `"mijual"`), optional
  `feedback_value` (int), `comment`, `recorded_by` (`"human"` for this surface), `tags[]`,
  `source.integration`, `session_id`, `user_id`, `project`, `channel` (`web`|`mobile`|
  `support`|null), `target_type` (`message`|`conversation`|`surface`), `attachment_ids`
  (no upload endpoint documented — **no attachments in this surface**). Response `202
  {request_id, accepted_at, status:"accepted"}`; `400` schema error, `401` key
  invalid (stop), `503` transient. The README frames the endpoint as trusted server-side
  code → the browser talks only to 미주알's own API. "No agent MCP linked yet" = the `/mcp`
  endpoint is **not** part of this round.
- **Walk findings + screenshots:** `works/phases/active/P8/phase.md` §"R8 walk" (12 items, with
  the operator's per-item answers recorded beside them).
- **Terminology / product truth:** `docs/current/product.md`, `docs/current/frontend.md`
  (supersession table), `docs/reference/design/SIGNOFF.md`.

Missing real content → ask for it; do not invent it.

## 5. Required outputs (a round is incomplete without all three)

1. **The card set** — line-1 `@dsCard` markers, review-time groups **`⏳ P8.S2 · Chrome`**
   and **`⏳ P8.S2 · Components`**, one card per reviewable unit (never a monolith). Required
   card paths (split further if useful; paths are stable across the post-approval regroup):

   - `chrome/Nav.html` — desktop bar, signed out (로그인) and signed in (account slot), three
     slots incl. the holdings slot
   - `chrome/NavMobile.html` — ≤480 bar + the sheet open/closed (rows, 의견 보내기, close state)
   - `chrome/AccountSlot.html` — full email + identicon + frame, menu open, alignment
   - `chrome/Footer.html` — the re-cut minimal footer, desktop + 390px
   - `chrome/Feedback.html` — the 의견 보내기 surface in context (from footer and from sheet)
   - `chrome/FeedbackStates.html` — idle / typing / sending / sent / failed+retry / empty
   - `components/Identicon.html` — the generated account mark (how it derives, sizes)
   - `foundations/tokens.css` — **only if tokens change**; then the full file, linked by the cards

2. **A record of what was designed** with every departure logged — `result.md` for this round
   (what changed vs R2/R5, the label chosen for the holdings slot, the feedback surface's copy
   with each string listed, what the footer keeps).

3. **An implementation contract** complete enough to build from without inventing anything —
   `build-prompt.md` (layout, tokens, states, copy table, the identicon algorithm's inputs,
   the API shape the page calls and its error handling, mobile rules). If the session produces
   Claude Design's own handoff bundle, that **is** the record and the contract — land as-is.

**Definition of done: the cards appear in the Design System pane** under the `⏳ P8.S2 · …`
groups, and the record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. **The holdings slot's label.** The operator doubts "포트폴리오". The session decides, with the
   operator. REFERENCE candidates the orchestrator can see in the product's own vocabulary
   (data, not a proposal): **보유 종목** (plain Korean for "the stocks I hold"; distinct from the
   hero's 내 종목 조회 lookup), **내 종목** (echoes 내 종목 조회 / 내 종목 연결, shortest — but
   may read as the lookup), **내 포트폴리오** (R5's existing account-menu row, unchanged).
   Whatever is chosen is the one name used in the nav, the sheet, and the account menu.
2. **Where the feedback surface opens** — a small panel anchored to the footer/sheet entry, a
   full mobile sheet, or a dedicated route — and whether it asks for an optional contact.
3. **Does the first account-menu row (내 포트폴리오) stay** once the nav carries the same
   destination, or does the menu shrink to 알림 설정 / 로그아웃?
4. **What the minimal footer keeps** beyond the wordmark and 의견 보내기 (source attribution? ©?
   the AI 질문 link R2 put in the bottom row?).
5. **Identicon derivation input** — hashed email (stable across devices) vs a stored per-account
   seed — is a data question the apply slice can answer either way; the session only needs to
   fix the visual (size, palette, shape family).

## 7. Operator setup + definition of done

Same project ("Mijual Design System"), Connect GitHub already in place — pull latest `main`
in the session so it sees this handoff, the walk findings and the landed R1–R7 records. When
the cards are up and the record + contract exist, tell the orchestrator to resume; read-back,
landing, SIGNOFF, and the regroup (retiring the `⏳ P8.S2 ·` address) follow. Approval must be
literal. Then `P8.S3` applies R8 from the landed `build-prompt.md`.
