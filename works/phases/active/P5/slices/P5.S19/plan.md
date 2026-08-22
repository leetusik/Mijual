# Plan — P5.S19: Design-fidelity verification in a real browser

## Context

The phase's last middle slice, per `design-cowork`: faithful implementation and
real-browser fidelity are separate concerns, and this is the fidelity pass — run the
whole product and check **every surface against its signed contract**. Nits found
during the phase are **fixed here, in code — never by editing a landed record**;
anything that would require a *new visual decision* is not yours to make — catalogue
it for the operator instead.

Read `works/phases/active/P5/phase.md` **in full** — every findings section carries
fidelity items that were deliberately deferred to this slice. Then the full design
chain per the phase read order: `docs/current/frontend.md` (supersession table) →
`SIGNOFF.md` (all seven rounds — supersession order binding) → all seven
`rounds/*/output/build-prompt.md` (+ `result.md` where the build prompt references
it) → `grounding/` (`ui-traps.md`, `states-and-trust.md`, `copy-inventory.md`).

## The job

### 1. Systematic surface-by-surface verification (headless Chrome, `npm run build`
+ `npm run start` against the live API — the S11 localhost rule)

Check each signed surface against its round's contract, both viewports where the
design defines both (desktop 1440 / 390×844), with screenshots per surface:

- **R1 foundations everywhere**: tokens only (no off-token colors), square corners,
  no shadows, mono for every numeral, Korean prose never mono, motion
  durations/eases, reduced-motion behavior (freeze/hide/cut).
- **R2/R2.1 landing + chrome** (S11/S12): the cosmos layers' counts/timings, hero
  anatomy, the two anchor cards, countdown behavior, 소멸주의보, board anatomy
  (grid, freshness, tabs, extras, the two strips), nav/footer measurements and
  copy, mobile sheet.
- **R3 event detail** (S13): the full anatomy per type; the state pages (철회 ·
  추후결정 · 기재 불일치 · sparse ②); CorrectionStory; the identity rule; per-field
  citations incl. a multi-part case.
- **R4 조회** (S14): search, 보유량 strip + restore chip, live rights, the N주
  conversion (both 확정발행가 branches), 놓친 돈 breakdown anatomy, empty states,
  the coverage boundary.
- **R5 auth + portfolio** (S15/S16): the auth panel's four states + PII inset,
  reset flow surfaces, conversion touchpoints, holdings rows + inline edit + undo,
  D-day sections, 챙긴 돈 flip, 알림 설정 (KakaoTalk no-control row), sample mode
  end to end, the logged-in chrome swap + abbreviated email, mobile.
- **R7 운영 관제** (S17/S18): the door, the ops chrome, all six tabs + the vocky
  view's three states, desktop-only, zero ornament, raw codes.
- **Cross-cutting trust rules** (ui-traps + hard-rules blocks): no untagged
  estimate / no tagged fact anywhere; no money before 확정발행가 (any surface); no
  ②/③ per-holding money; no browser-computed or non-KST D-day; past ② never 종료;
  추후결정 never beside a date; no placeholder where a gate blocked a field; 조회
  and 포트폴리오 never disagree on a number (spot-check the 한화솔루션 679,575원
  chain on both).

### 2. The accumulated fidelity checklist (fix here, in code)

Every deferred item recorded in phase.md — at minimum:

- **The footer estimate tag at 6.72px** (S11): apply the sanctioned fix — a named
  size prop/variant on `EstimateMarker` honoring R2's 10px literal on landing
  surfaces — never a local restyle.
- **The mono/Hangul fallback** (S10 asset note): Korean glyphs inside `--font-mono`
  elements (`StateBadge` 추후결정, 소멸주의보 badge, `[근거]`'s 근거) fall to the
  OS Korean face per platform. Judge against R1's rule ("Korean prose never mono" —
  are these *prose* or *chips the design draws in mono*?) and the cards' spec
  wording; if the record does not settle which face those chips intend, that is an
  operator question, not a fix — record the reading you can defend and flag it.
- **The two S10 record readings** (`추정` tag form; faint `D+n`) — re-verify
  implemented consistently on every surface that renders them.
- **The S12 hero 680px floor and the S13 collapsed-citation width rule** — verify
  they hold at intermediate widths (768/1120 breakpoints), not just the two
  endpoints.
- Anything else the phase notes marked "for P5.S19" — sweep `phase.md` for the
  token `S19`/`P5.S19` and address each mention: fix (code), verify (browser), or
  catalogue (operator question). List every one in `result.md` with its
  disposition.

### 3. The operator-question catalogue (do NOT fix)

Collect into one clearly-labeled section of `result.md` (and mirror in `phase.md`)
the open design/product questions the phase accumulated — the gate-cost 49.2억원
dated figure, the Korean-less 404 and `invalid_reset_token` silence, the
closed-청약/no-실적보고서 gap, the vocky no-widget-script finding, the 정정 이력
label, the countdown/stale defaults awaiting confirmation, 수신 주소 재인증, the
샘플-로드-여부 absent fact, the 「API shape 확정 대기」 literal staleness — so the
phase review and the operator get one consolidated list. No code for these.

## Constraints

- Fixes are faithful-implementation corrections only; a fix that requires choosing
  a visual value the record does not state is an operator question instead.
- Landed records read-only (S18's §6.3 addition was the one sanctioned edit and is
  done). Tokens/`fonts.css` untouched.
- Keep fixes surgical; re-run the affected checks after each. No new dependencies.
- Suite + smoke stay green (118 Python / 11 smoke baseline); add nothing heavy.

## Validation

- The full browser pass complete, with a per-surface pass/fail table in
  `result.md` (every failure either fixed-and-rechecked or catalogued with why it
  is not fixable here).
- `npm run build` + `typecheck` + `smoke`; `.venv/bin/python -m pytest`; both
  servers stopped after.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md` (the verification table, the fix list, the operator catalogue);
`phase.md` *Findings & Notes* (fidelity outcome — what `P5.REVIEW` should trust)
and *Doc impact* (`frontend`/`experience`/`qa` for any fixes; the consolidated
operator catalogue pointer). Structured verdict. No commits, no status
transitions.
