# R1 Implementation Contract — build from this without inventing anything

Tokens: `foundations/tokens.css` is the single source (66 custom properties). Fonts: Pretendard Variable + IBM Plex Mono via the CDN imports in `foundations/fonts.css`.

## Color roles
- Page `--paper #f2f3f2`; card `#fff` + 1px `--border-strong #c9cec9`; card header `--surface-raised #fafbfa` + `--border-soft #e3e6e3`; inset panels `--surface-inset #eef0ee`.
- Ink `#15201d / #5a655f / #8b948e`. Brand charcoal `--brand #1f2926` (tint `#e9ebe9`) = identity only: the wordmark is neutral so color is reserved for data. Green `--live #0d5c48` = alive (estimates ▷, live counters, recoverable value); red `--alert #c53030` = expiring/lost only (D-day ≤7d, D-DAY fill, 소멸 figures) — never brand, never price direction.
- `--live #0d5c48` (+tint `#e6efe9`): ▷ estimates, [근거] citations, live counts.
- `--alert #c53030` (+tint `#f6e9e2`): urgency ≤7d, D-DAY fill, 소멸주의보, 발행사 기재 불일치.
- Rights: ① `#2b5aa0`/`#e9eff8` · ② `#96610f`/`#f7efdd` · ③ `#6d3a5d`/`#f4e9f0` — tinted chips only.

## Type
- Sans: Pretendard; sizes 11/12/13.5/15/17/20/24/32/44; display ≥24 gets `-0.02em`, weight 700; body 13.5/1.55.
- Mono: IBM Plex Mono for every numeral (금액·주수·%·dates·D-day·rcept_no), weights 400–600, ~0.95em of surrounding sans. Korean prose never mono.

## Spacing / shape / elevation
- 4px scale (4·8·12·16·20·24·32·48·64). Radius 0 everywhere. No shadows — borders carry elevation. Data rows: 8–9px v-padding, dashed `--border-soft` separators. Card content column ≈620px; breakpoints 480/768/1120 (mobile-first).

## Motion
- Durations 120/200/320ms, ease `cubic-bezier(.2,0,.2,1)`. Hover: surface shift + border darken. Press: inset surface. Board row updates: fade only. Citation panel: 320ms height+fade. Countdown: colon blink 1s step-end. `prefers-reduced-motion`: ticks freeze, fades become cuts.

## Trust primitives (reference implementations in `components/`)
- **EstimateMarker**: `▷` + value, mono 600, `--live`; sizes via `font-size: inherit` (0.95em) — the component never sets its own size.
- **Citation**: per-field `[근거]` chip (mono 11, `--live`, dotted underline) → inset panel (2px left rule `--live`), verbatim quote (pre-wrap, scroll >180px), link `https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}`.
- **StateBadge**: 추후결정 = mono chip on `--surface-inset`, never with a date; 철회 = full-width centered notice replacing card body (locked copy per type); 발행사 기재 불일치 = alert-tint chip. Gate-failed fields/events: rendered as nothing.
- **DDay**: mono 600 at a single fixed size (17px); urgency changes color only — >30d `--ink-2`, ≤30d `--ink-1`, ≤7d `--alert`, D-DAY white on `--alert` (2px 10px); date below in mono 11 `--ink-3` + "KST".
- **RightsChip**: label only (no ①②③ numbering), 11px/600, type tint bg + type color text; `compact` = short label (유증 / CB / 매수청구).
- **소멸주의보 strip**: white card, 1px `--alert` border + 4px left rule, mono tag (white on `--alert`, 3px 9px, .08em), body 13.5 with mono numerals in `--alert`.
