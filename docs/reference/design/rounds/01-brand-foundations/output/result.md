# R1 Round Record — Brand Identity + Foundations

- Session: Claude Design + operator, 2026-08-20
- Direction picked by the operator from three built candidates: **C "terminal-light"** (paper-grey control room, mono numerals, hairline borders, square corners). Candidates preserved in `explorations/`.

## Operator decisions (the handoff's open questions)

1. **Dark mode:** light only.
2. **소멸주의보:** yes — named sub-brand element (`brand/Subbrand.html`): mono tag on alert rust, hairline strip with 4px left rule.
3. **Urgency escalation:** faint >30d → ink ≤30d → alert rust ≤7d → filled rust D-DAY badge; D+N stays unfilled (per-type language, ui-traps §5).
4. **Rights types:** subtle hue per type — ① `#2b5aa0` ② `#96610f` ③ `#6d3a5d`, tinted chips only.

## Session decisions (operator skipped, decided to match direction C; revisitable)

- Type: **Pretendard Variable** (Korean UI) + **IBM Plex Mono** (all numerics), both CDN-loaded.
- Estimate/citation color = live green `#0d5c48`; urgency = rust `#b3401e`; brand navy `#1e3a66` reserved for identity, not UI state.
- Square corners system-wide; elevation by hairline borders, no shadows; motion = fades only, 120/200/320ms, one ease.

## Departures from the handoff

- **Card paths**: as specified, plus extra split cards (allowed): `foundations/ColorsRights.html`, `foundations/TypeNumeric.html`, `brand/Subbrand.html`, `components/RightsChip.html`.
- **Intentional addition**: `RightsChip` component — carrier for the per-type hue decision.
- **Group labels**: `⏳ P3.S2 · Brand / Foundations / Components` as required.
- **Logo**: only the provided navy wordmark PNG exists. No favicon-scale mark and no reversed asset were designed — inventing one is out of bounds; the Logo card shows a type fallback and flags the gap. **Ask the operator for a symbol mark + reversed/SVG wordmark.**
- Components are React (`.jsx` + `.d.ts` + `.prompt.md`), compiled into this design system's bundle — consumable now by any project binding this system, and a faithful spec for the Next.js build.

## Copy

No changes proposed. All rendered strings are verbatim from `copy-inventory.md` / `headline-numbers.md`.

## R1 revision (operator, same session)

- Lockup = English wordmark alone; 한글 '미주알' 병기 dropped from the lockup (departure from the handoff's locked lockup elements — operator-directed).
- Brand color moved navy → sky blue \`#2f97cf\`; wordmark recolored from the provided asset (alpha-preserving tint), reversed white version generated from the same shape.
- RightsChip: no ①②③ numbering, label only.
- EstimateMarker and DDay render at fixed/inherited size — urgency and estimate emphasis are color-only, never size.

## R1 revision 2 (operator)

- Adopted the green/red semantic system: green \`#0d5c48\` = 살아있는 가치 (brand + estimates + live, one hue); red = expiring/lost. Sky blue retired (\`--brand-sky\` kept as deprecated alias).
- Alert red brightened \`#b3401e\` → \`#c53030\`.
- Wordmark recolored to brand green (\`assets/mijual-wordmark-green.png\`); reversed white unchanged.
- Rule recorded: red never encodes price movement (국내증시 관례 충돌 방지) — deadlines and 소멸 only.

## R1 revision 3 (operator)

- Brand color settled: **charcoal \`#1f2926\`** (K1) for the wordmark — identity carries no data color; green/red stay purely semantic (alive/loss). Wordmark asset: \`assets/mijual-wordmark-charcoal.png\`; reversed white unchanged.
