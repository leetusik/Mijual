# Design Handoff — Round 1: Brand Identity + Foundations

- Round: **R1 of 7** · slice `P3.S2` · written 2026-08-20
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via **Connect GitHub** (main branch, pushed at handoff commit)

## 1. Product context

**미주알 (MIJUAL)** is a Korean-only web service that watches the whole market for expiring
shareholder rights — 유상증자 신주인수권 (①), CB 오버행 (②), 주식매수청구권 (③) — and turns
DART disclosures into deadlines and money: live countdowns, per-holding value conversion
("500주 보유였다면 83만 원 · 증서 매도 마감 D-3"), and retroactive missed-money lookups.
Positioning: **"시장 전체의 소멸 임박 권리를 감시하는 관제 서비스 + 내 종목 연결"** — a
monitoring board first, a personal tool second. It is the operator's entry to the 2026
금융 AI Challenge; judges will open it cold in a browser, desktop and mobile.

The product's core claim is **trust**: every number is deterministic, every extracted fact
carries a citation back to the filing, estimates are always marked, and anything that
failed a validation gate is simply not shown. The brand has to carry that personality —
this is a market-surveillance instrument, not a hype dashboard. (How that translates
visually is this session's decision, not ours.)

Name meaning (operator-confirmed, see `docs/reference/challenge/00_HANDOFF.md` §3.7):
미주알고주알 (to dig into every last detail — what the AI does to filings), backronym
미리·주(株)·알림, and '알' inheriting 알권리. Sub-brand candidate: **소멸주의보**.

## 2. Scope checklist — what this round must cover

Foundations only. No product screens in this round (they are rounds 2–7).

- [ ] **Logo lockup** — MIJUAL (Latin, uppercase) + 한글 '미주알' 병기: the lockup's visual
      design, its variants (horizontal/compact/favicon-scale), and clear-space rules.
- [ ] **Color palette** — full role-based palette (surface, text, interactive, semantic),
      including the colors that will carry: urgency/D-day escalation, the three rights
      types if the session decides they are color-coded, estimate (▷) vs fact, and the
      state vocabulary below. Whether a dark mode exists is this session's call.
- [ ] **Type scale** — Korean-first text faces and a numeric treatment: 금액, countdowns,
      D-day labels and tables need **tabular numerals** that hold alignment while ticking.
      Web-loadable fonts only (the product is Next.js on the open web).
- [ ] **Spacing / radius / elevation** system.
- [ ] **Motion** — countdown ticks, live-board updates, streaming text (the 해설 panel in
      R6 will stream via SSE). A **reduced-motion floor is locked**: every motion has a
      non-animated equivalent; expression above that floor is in play.
- [ ] **Mobile-first breakpoints** — judges will open this on phones; define the
      responsive grid the later surface rounds will design against.
- [ ] **`tokens.css`** — the round's real values as CSS custom properties; every card
      links it (the pane compiles foundations from it).
- [ ] **Trust primitives** (the product's signature components — foundations because every
      later round composes them):
  - **Fact vs ▷ 추정 marker** — estimates always carry `▷`; the two must be unmistakable
    at a glance (semantics locked, visual in play).
  - **Citation affordance** — a fact can open its evidence: quote + character span +
    `rcept_no` linking to the DART 원문. Compact (inline) and expanded states.
  - **State vocabulary** — 정상 / 임박 / **철회** ("이 유상증자는 철회되었습니다") /
    **추후결정** (a schedule that structurally has *no date* — not an error, not a dash-
    for-missing) / 비노출-adjacent renderings like "발행사 기재 불일치". See
    `states-and-trust.md`; these are product features, not error states.
  - **D-day / countdown component** — D-3 / D-DAY / D+2 labels and live countdown, with
    the urgency escalation expression (how "3 days left" *feels* vs "40 days left").

## 3. Locked vs. in play

**Locked** (system structure, data contracts, brand spirit — not this session's to move):

- Service name 미주알 / romanization **mijual** (operator-confirmed; not in play unless the
  operator reopens it). Lockup *elements*: MIJUAL 대문자 + 한글 '미주알' 병기.
- Product surface is **Korean-only**. UI copy comes from
  `docs/reference/design/grounding/copy-inventory.md` — copy is locked this round.
- Data contracts: what a card can know is `EventExposure` / `FieldView`
  (`docs/reference/design/grounding/samples/*.json`). No field exists that isn't there.
- Trust semantics: every estimate carries ▷; every extracted fact is citable; gate-blocked
  fields are **absent, never shown with a warning**; 추후결정 shows no date at all.
- Accessibility + reduced-motion floor.
- Stack (FastAPI + Next.js) and everything about system architecture.

**In play** (this session decides): palette, type choices and scale, spacing/radius/
elevation values, motion expression, the lockup's visual design, every token value, the
visual form of all trust primitives and states, urgency expression, dark mode or not,
whether/how 소멸주의보 appears as a sub-brand.

## 4. Where to look — real content, never lorem

All in-repo (Connect GitHub):

- `docs/reference/design/grounding/README.md` — index of the grounding pack (measured
  2026-08-20, regenerable).
- `grounding/board-snapshot.md` — real board: 488 exposable events (① 50 / ② 422 / ③ 16),
  urgency distribution, most-urgent live events per type.
- `grounding/headline-numbers.md` — the landing headline material: **▷ 718.1억원 / 32
  offerings** lapsed, open/upcoming counts, gate cost — with the exact ▷ framing.
- `grounding/copy-inventory.md` — every Korean state notice and reason-code rendering.
- `grounding/sample-events.md` + `grounding/samples/*.json` — 11 real events annotated for
  what a designer should notice. **Note: the `r1-`/`r2-`/`r3-` filename prefixes mean
  rights types ①/②/③, not design rounds.**
- `grounding/states-and-trust.md` — the trust primitives and state rules in prose.
- `grounding/ui-traps.md` — rendering traps (two-convention dates, issuer-table
  mismatches, a wrong-corp-name display case).
- `docs/current/product.md` — product truth: three product states, trust claim, non-goals,
  terminology.
- `docs/reference/challenge/00_HANDOFF.md` §3.5–3.7 — surface strategy and brand context.

If the session needs real content that is missing here, **ask for it** — do not invent it.

## 5. Required outputs (a round is incomplete without all three)

1. **The card set** — one card per reviewable unit, each preview HTML starting with the
   line-1 marker, e.g.:

   ```html
   <!-- @dsCard group="⏳ P3.S2 · Foundations" viewport="960x600" -->
   ```

   Review-time groups carry the round address: `⏳ P3.S2 · Brand`,
   `⏳ P3.S2 · Foundations`, `⏳ P3.S2 · Components`. Exact card paths this round must
   produce (what each is for is above; paths are stable, only the group label moves at
   signoff):

   - `foundations/tokens.css` (linked by every card)
   - `brand/Logo.html`
   - `foundations/Colors.html`
   - `foundations/Type.html`
   - `foundations/Spacing.html`
   - `foundations/Motion.html`
   - `components/EstimateMarker.html`
   - `components/Citation.html`
   - `components/StateBadges.html`
   - `components/DDay.html`

   Splitting a unit further (more cards) is fine; merging into fewer/monolithic cards is
   not — the operator reviews and supersedes one card at a time.

2. **A record of what was designed**, with every departure from this handoff logged.

3. **An implementation contract** complete enough to build from without inventing anything
   (token values, faces, sizes, motion specs, state rules). If the session produces Claude
   Design's own handoff bundle, that bundle *is* items 2–3 — it will be landed as-is;
   otherwise the content lands as `result.md` / `build-prompt.md`.

## 6. Open questions — posed to the session, not answered here

1. Dark mode: single theme or light+dark from the start?
2. 소멸주의보: does it appear as a named sub-brand element (e.g. the landing alert strip),
   and if so how is it marked?
3. How does D-day urgency escalate visually as expiry approaches — and what does D-DAY
   itself look like?
4. Are the three rights types (①유증 신주인수권 / ②CB 오버행 / ③매수청구권) visually
   distinguished by color/mark, or by label only?

## 7. Operator setup + definition of done

Setup: open claude.ai/design → project for Mijual → **Connect GitHub** →
`leetusik/Mijual` (main). No attachments required — everything is in-repo. (A local-dir
connection also works if you prefer not to rely on the push.)

**Definition of done: the cards listed in §5 appear in the Design System pane** under the
`⏳ P3.S2 · …` groups, `tokens.css` carries the round's real values, and the record +
implementation contract exist. Then tell the orchestrator to resume (clear `P3.S2` from
`pending`); read-back, landing, and SIGNOFF follow. Approval must be literal — the round
closes on your words, and revisions after that create a new superseding round.
