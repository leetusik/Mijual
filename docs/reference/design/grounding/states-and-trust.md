# Product states and trust primitives

The rules on this page are not measurements and they do not drift. They come from
`docs/current/product.md` (v0002) and `src/mijual/gates/exposure.py`, and they are the product's trust
claim expressed as things a screen must do. A design that breaks one of them is not shippable, however
good it looks.

## The one-sentence claim

**미주알 shows a number only when it can show where the number came from.** Everything below is a
consequence of that sentence.

## 1. Fact vs ▷ 추정

Two kinds of number appear in this product and they must never look alike.

| | what it is | example |
|---|---|---|
| **fact** | read from a filing, with a quote and a span into the original document | 확정발행가 22,100원 · 소멸 증서 3,734,925주 · 전환청구 개시 2026-10-24 |
| **▷ 추정** | *derived* — computed from facts by a formula the product owns | ▷ 증서 1주 이론가치 5,525원 · ▷ 2026 소멸가치 718.1억원 |

**Every estimate carries the `▷` marker, always, at every size.** There is no price feed in this
product: the 증서 가치 is derived by inverting each filing's own 발행가 산식, so it is an estimate by
construction and is marked as one even in the landing headline. The marker is a design primitive
(R1 owns its visual form), not a footnote — a `▷ 718.1억원` shrunk into a caption while the number
grows to 72pt has broken the rule.

Estimates are also **conservative on purpose**: where the arithmetic admits a band, the product reports
the band rather than resolving it (▷ 718.1억원 with a ▷ 548.7억원 lower edge). Whether the UI shows one
figure or two is a design decision; hiding the fact that it is a band is not.

## 2. The citation affordance

Every rendered field carries three things: a verbatim `quote`, a `span` (byte offsets into the stored
document) and the `rcept_no` of the filing it came from. That triple is what makes "where did this come
from" answerable in one tap, straight to the 원문 on DART.

Design consequences:

- The affordance is **per field**, not per card. `samples/r1-live-healthy.json` has six independent
  citations on one event.
- The quote is Korean prose of wildly varying length — from `3) 신주인수권증서 상장예정기간 : 2026년
  08월 19일~ 2026년 08월 25일` to a 600-character 콜옵션 clause. Whatever surface shows a quote has to
  survive both.
- **A quote is never paraphrased, corrected or re-punctuated.** It is a copy of the filing's own words;
  that is the entire point.
- Fields whose citation could not be located are *not shown at all* (reason code `span_unresolved`,
  five rows corpus-wide today). There is no "값은 있는데 근거를 못 찾음" state on a user surface.

## 3. The state vocabulary

Five states, and each one is a product feature rather than error handling.

| state | what the user sees | where it comes from |
|---|---|---|
| **정상** | the card, its fields and a live countdown | `state: exposable`, fields `passed` |
| **임박** | the same card, urgent — `D-5`, `D-DAY` | `mijual.calc.d_day` / `DDay.label`, computed in KST |
| **철회** | the 철회 notice **instead of** the card body | `state: withdrawn` → `notice_ko` |
| **추후결정** | the field renders as `추후결정`, **with no date at all** | field `gate_status: tbd`, `value: null` |
| **비노출** | nothing — the event is not on the board | `suppressed` / `flagged` / `no_document` / `no_detail` / `incomplete_api_row` |

`D-3` / `D-DAY` / `D+2` is the product's own countdown vocabulary (`DDay.label`) and is computed
deterministically in Asia/Seoul — never in the browser's local timezone, and never by the AI.

## 4. Gate-blocked fields are absent — never explained

**A field that fails its deterministic gate is not shown.** Not greyed out, not marked "확인 필요", not
replaced by a dash with a tooltip. It is absent from the card, and the card renders around the hole as
if the row had never existed. `samples/r3-field-absent.json` is that state in the wild.

This is the rule most likely to be broken by good design instinct, so it is worth stating why it holds:
the reason a field failed is *internal* — a citation that did not resolve, an API value that did not
match, a superseded version. Surfacing it would teach the user to distrust the rest of the card in
exchange for information they cannot act on. **The place where blocked fields are visible, with their
reason codes, is the operator's admin panel (R7) — and only there.**

The same rule one level up: a blocked *event* is simply not on the board. It does not appear greyed
out, and the board's counts do not include it. What the board says to a user who searched for that
stock is an R4 design question ("찾을 수 없음" is not the same claim as "해당 없음").

## 5. Determinism is a feature, and the AI's role is bounded

- **The AI reads. Determinism calculates.** The model extracts a value *and* a verbatim quote; the
  package locates the quote in the stored document; every 금액 and every D-day is computed by
  `mijual.calc`, which is pure, LLM-free and unit-tested.
- Every headline number is **regenerable at zero spend** — `mijual.estimate report` makes 0 OpenDART
  requests and 0 LLM calls, and two runs agree. A screenshot of a number can always be reproduced.
- The 해설 layer (R6) speaks **over verified data only**, with inline citations, and **refuses** when
  the data is not gate-passing. A refusal is a designed state, not an error toast.
- Accuracy figures the product may quote are **cross-model judgements, not human ground truth**
  (98.6 % strict). Any user-facing use of that number has to say so — see `docs/current/qa.md`.

## 6. The gate has a price, and the product says so out loud

**▷ 49.2억원 — 6.4 % of what the product could have claimed — is deliberately left on the table**,
because three offerings
with a citable 실권 count had their 할인율 extraction fail its citation gate. The product could show a
bigger number. It doesn't.

That sentence is a differentiator, not an apology, and it is available to the landing page and to the
해설 layer. It is also the reason the trust rules above are not negotiable at the visual layer: the
product is already paying for them in the headline.
