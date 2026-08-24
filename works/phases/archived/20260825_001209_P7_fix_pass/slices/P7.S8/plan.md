# Plan — P7.S8: 포트폴리오 — tidy the sample layout and make 청약·매도로 챙겼습니다 visibly move the 놓친 돈

## Why

Operator item 9: "sample portfolio page just looks not organized; and '청약·매도로 챙겼습니다'
clicked should make the 놓친 돈 stuff gone or something." `P7.DECOMP` (`phase.md` → "Item 9",
**Design-collision reading #5**, Open Question Q4 — unanswered, so reading #5 stands) found: the
checkbox in `frontend/components/portfolio/Deadlines.tsx` implements R5-8 literally (check → label
놓친 돈 → **챙긴 돈**, same amount with 「추정」, alert → live hue, caption swap) and was simply dead
on an un-hydrated origin; `P7.S1` fixed hydration and measured the flip working on `127.0.0.1`
(`679,575원` + 「추정」 unchanged, label flipped). `P7.S7` trims the local caption to `본인 표시`.
What remains for this slice is (a) **layout fidelity** of the sample page against the R5 record
and (b) making sure the 챙겼습니다 change is unmistakable and persistent.

Read first: `phase.md` (Item 9, reading #5, Constraints, the S1–S7 findings — especially what S7
changed in `portfolio/copy.ts`), `intent.md` item 9, and the R5 record:
`docs/reference/design/rounds/05-account/output/build-prompt.md` §Portfolio, §D-day 목록, §샘플
포트폴리오, §Mobile, plus `result.md` (the card descriptions — `account/Portfolio*.html`,
`account/AccountMobile.html` — and the sample composition table), and `docs/current/frontend.md`'s
portfolio notes. `docs/reference/design/` is read-only.

## (a) Layout — faithful-implementation fixes only

"Not organized" is the operator's impression; this slice turns it into measured deviations from
the record and fixes **those**, restyling nothing beyond them. Load the sample through the product
(the 샘플 entry on `/auth/login` or the landing footer) in headless Chrome on `127.0.0.1:3000` at
1440 / 768 / 390 and walk the page against R5's anatomy:

- page shell: no 「내 포트폴리오」 H1 in the body (nav is the location); the 샘플 inset banner
  ("구성 예시" wording) at the top of the 2층 surface; 알림 설정 hidden in sample mode;
- D-day 목록 home: two sections — 다가오는 마감 (D-day ascending) · 지나간 마감 (most recent
  first) — each with the anchor date line `기준 YYYY-MM-DD (KST)`; rows = 종목 / governing anchor
  label + `D-n · date` / RightsChip / the ① amount with 「추정」 (or 발행가 확정 전 chip + date) /
  ②·③ with no money; past rows = inset chip `기간 지남 · D+n` / `통지 마감 지남 · D+n` in a non-alert
  colour, ① lapsed rows with the 500주-basis 「추정」 amount + "놓친 돈 상세 →" link + the R5-8
  checkbox;
- holdings: the 4 sample rows (계양전기 500주 · 대동기어 300주 · 한화솔루션 500주 · 세기상사 100주),
  row anatomy 종목 / 보유량 (inline edit) / 진행 중인 권리 요약 / 수정·삭제, 종목 추가 as the bottom
  panel on mobile;
- the signed primitives: craft panel / inset surfaces, hairlines, radius 0, mono numerals, tokens
  only for spacing, 44px targets on mobile, the `.mono` size rule from `app/shell.css`.

For every place the rendered page departs from the record — misaligned columns, inconsistent
spacing between sections/rows (compare computed margins/paddings against the tokens the modules
claim), wrapped or overflowing cells at 768/390, a section header that does not read as a header,
rows whose anatomy differs between 다가오는 and 지나간, a caption that floats away from its row —
fix it in `components/portfolio/*.module.css` / the component markup so it matches the record.
**Where the record itself is silent or the operator's impression is about something the record
drew that way, do not invent**: list it in `result.md` as an operator question (and if you believe
a layout decision needs the operator, say which). Keep a before/after table: element · what was off
(numbers) · record reference · fix. Do not change copy (S7's domain) beyond what a layout fix needs.
Note P5.S19 catalogue #6 (the sample subline says 4건 while 5 D-day rows render) — a known
data-vs-sentence item; do not "fix" it by hiding a row; just confirm and mention.

## (b) 챙겼습니다 — the record's behaviour, visible and persistent

Reading #5: the **놓친 돈 framing leaves** (label → 챙긴 돈, alert → live hue, the caption), the row
and its figure stay (R5-8: 금액 동일, 「추정」 유지). Verify each part actually changes on click in
`next dev` on `127.0.0.1` **and** on reload (sample/anonymous: the mark persists in localStorage per
R5-8; account mode: `PUT` to the API — check the code path exists and works for a logged-in
account too; create/delete a throwaway account the way `P7.S2` did if you test it). If any visible
part of the flip is missing or too subtle to notice (e.g. the label changes but the row's alert
colour does not, or the caption does not appear), fix it to the record. Do **not** remove the row
(Q4 for the operator). Make sure the unchecked → checked transition does not shift layout.

## Verify — operator runtime

Dev stack up (`make stack-status`); Fast Refresh. CDP on `http://127.0.0.1:3000` (fresh profile;
S1–S7 `result.md` show the approach) at 1440/768/390 with the sample loaded: the before/after
measurements for every layout fix; the 챙겼습니다 flip (label text, computed colour of the amount /
row, caption present) and its persistence across reload; one pass on the Tailscale origin; keyboard:
Tab to the checkbox shows the 2px ring (S5's treatment), Space toggles it. Production build in an
isolated copy (`P7.S2` method) + `next start -p 3100`, spot-check the sample page layout, kill it.
`cd frontend && npm run typecheck && npm run smoke`; `python3 scripts/workflow.py validate`. Leave
the dev stack running; remove any test account.

## Record

`result.md` (deviation table with numbers, what the operator's "not organized" resolved to,
operator questions, commands/outcomes). `phase.md`: Findings note + Doc impact line(s)
(**`frontend`** if any portfolio layout rule or the 챙겼습니다 behaviour description changes;
`experience` if it describes the sample page). No `doc-new-version`, no commits, no state
transitions.

## Out of scope

Copy (S7), focus (S5), nav (S6), anything outside `components/portfolio/*` and its CSS unless a
shared primitive is demonstrably broken (then stop and report rather than editing it).

## Reconciled against P7.S5–S7 (landed after this plan was drafted)

- `P7.S7` trimmed `CLAIM_CAPTION_LOCAL_KO` to `본인 표시` (account caption unchanged: `본인 표시 · 계정에
  저장`); no other portfolio copy changed. Verify the caption as it now reads.
- `P7.S5`: text fields indicate focus by border (`--field-focus-border`), checkboxes/buttons keep the 2px
  ring — `SharesInput`/`AddHolding` fields are already covered; do not add focus rules here.
- The sample's past rows: two carry the 챙겼습니다 check (DECOMP measured 3 past rows). Account-mode
  persistence: the S2/S5 executors created and deleted throwaway accounts through the product — do
  the same if you test the account path; the pre-existing `s19-fidelity@example.com` row is P5.S19's
  leftover, not yours to delete.
