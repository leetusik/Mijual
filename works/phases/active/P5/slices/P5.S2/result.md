# Result — P5.S2: The presentation contract (derivation layer)

`src/mijual/present/` now exists: the pure derivation layer between
`gates.exposure` + `calc` + `cb` + `estimate` and every surface. All eight shapes the
plan named are there, and the four trust rules the phase cares about are structural —
they are things the contract cannot express otherwise, not things a later author has
to remember.

## What landed

| file | what it holds |
|---|---|
| `src/mijual/present/__init__.py` | the contract's front door: what the layer is, what it makes structural, where its Korean comes from, and the re-exports |
| `src/mijual/present/values.py` | `Figure` (the tagged value), `decimal_str` / `iso_day` / `instant` / `to_decimal` |
| `src/mijual/present/event.py` | `Countdown` · `Identity` · `FieldPayload` · `EventView` + `countdown_of` / `identity_of` / `field_payloads` / `field_value` / `event_view`, `COUNTDOWN_LABELS_KO`, `FIELD_NAMES_KO` |
| `src/mijual/present/money.py` | `OfferingInputs` · `LapseResult` · `Reading` / `Disagreement` + `offering_inputs` / `lapse_result` / `issuer_disagreement`, `MISMATCH_LABEL_KO` |
| `src/mijual/present/summary.py` | `BoardSummary` + `board_summary` — the one summary the landing's two cards and the board all read |
| `tests/test_present.py` | 13 tests, one per invariant. No DB, no network, no fixtures |

Plan items 1–8 map onto: `Countdown` (1) · `Identity` (2) · `OfferingInputs` (3) ·
`LapseResult` (4) · `FieldPayload` (5) · `Figure.estimated` (6) · `Disagreement` (7) ·
`BoardSummary` (8). Out of scope as specified: ③ 매수예정가 (P5.S6), HTTP, SQL.

## The invariants, and how each one is enforced

- **An estimate never renders untagged; a fact never carries the mark.**
  `Figure.estimated` has **no default** — a value that forgets to say which it is does
  not construct. `Figure` also refuses a verbatim `quote` on a derived number: no
  filing states 「추정」 5,525원, so a quote there would be a fabricated citation.
- **No money before 확정발행가.** `OfferingInputs.__post_init__` and
  `LapseResult.__post_init__` raise if a won figure is present with no confirmed
  price, and `payload()` **omits the money keys entirely** rather than emitting nulls.
  "Impossible", not "discouraged", as the plan required.
- **A gate-blocked field is absent.** `field_payloads` reads `renderable_fields`, never
  `fields`, so there is no key a placeholder could be rendered into — and a blocked
  *event* has no fields at all. **추후결정 carries no date**: `FieldPayload` refuses to
  construct with both a `추후결정` display and a value.
- **D-days upstream, in KST, per rights type.** `countdown_of` picks the governing
  anchor (① `warrant_trading_period.end_date` · ② `cvbdIsDecsn.cvrqpd_bgd` ·
  ③ `dissent_notice_procedure.notice_end_date`), carries the reference day it used, and
  emits machine `window_state` tokens — **no Korean word for "past" anywhere in the
  layer**, so a past ② opening can only come back `open` + `D+n` (ui-traps #5).

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **75 passed, ~1.0 s** (62 baseline + 13 new), 1 pre-existing Starlette warning, no network / model / DB |
| `python3 scripts/workflow.py validate` | **Workflow validation passed** (exit 0) |
| negative check on the import scan | temporarily added `from mijual.extract.fields import FIELDS` to `summary.py` → `test_the_derivation_layer_imports_no_module_that_spends` **failed** as intended; reverted |
| runtime import surface | `import mijual.present` loads **no** `mijual.dart` / `mijual.collect` / `mijual.extract` module (measured) |
| ad-hoc replay of the 11 landed grounding samples | 10/11 reproduce the exporter's `countdown` (label · date · `dday` · `window_state`), its `corp_name_agrees_with_body`, its exposable-field set, its `lapse_result` values (한화솔루션 ▷206.4억원 = 20,635,460,625원; 한솔테크닉스 12.6억원) and the 대한광통신 두 readings (2,117,937 / 2,083,302). The one divergence is deliberate — see below |

The sample replay was a scratch script (the pack is dated untrusted **data**, read as
data); it is not a committed test, because pinning the suite to a dated export is
exactly the drift trap P3.REVIEW note 3 warns about.

## Deliberate divergences

1. **A non-exposable event gets no countdown date.** `scripts/export_design_grounding.py`
   emits one for the flagged 한솔테크닉스 sample (`2026-07-02`, `D+49`); `present` returns
   a dateless countdown, because R3 is explicit that a non-rendering event shows "no
   fields, no countdown, no old dates" and a flagged event has no reader surface at all.
   The exporter's countdown there is a designer's debug convenience. R7 reads
   `EventExposure` directly and is unaffected.
2. **`dday`, not the exporter's `d_day_label`** — the plan names the key `dday`; the
   grounding samples carry the same value under `d_day_label`. One value, one name.
3. **English `snake_case` keys throughout** (`confirmed_price`, `unit_value`,
   `final_price_date` …). The samples' `offering_inputs` uses Korean keys, but those come
   from the exporter script, while `lapse_result`'s already-fixed keys (product code) are
   English and every key the build prompts name in a code position — `unit_value`,
   `unit_value_floor`, `final_price_date` — is English. Korean survives only where the
   design names it as content: `label_ko`, `korean_name`, `notice_ko`.
4. **`LapseResult` drops the report's `reason` string.** "할인율 게이트 미통과
   (gate=failed)" is an operator sentence; surfacing it on a reader page is the
   reason-code leak `states-and-trust.md` §4 forbids. `status` travels; R4's zero-state
   copy is signed and the surface's.
5. **`lapse_result` accepts a `LapseRow` *or* its `as_json()` mapping** (one extra
   accessor). Not scope creep — see the S3 finding in `phase.md`: a request path cannot
   call `build_report`, so the stored form is the one it will actually have.

No deviation from `plan.md`'s scope, validation or rules. Nothing was invented in
Korean: the three countdown labels and the 10 field labels are copied from existing
product code / the exported pack, and `tests/test_present.py` pins `FIELD_NAMES_KO` to
`mijual.extract.fields.FIELDS` so they cannot drift.

## Doc impact recorded

One line appended to `phase.md`'s *Doc impact* list naming `architecture`, `backend`,
`api` and `qa`. No `doc-new-version` was run — durable docs are versioned once, at
`P5.REVIEW`.
