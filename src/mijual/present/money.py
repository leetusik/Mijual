"""The money shapes: ① offering inputs, the 소멸 outcome, and a filing at odds with itself.

Every won figure in the product is built from these three, and each one carries a
rule that the design states as a prohibition and this module makes structural.

**No money before 확정발행가.** An offering whose 확정발행가 is not yet fixed has
no 증서 이론가치, no 환산액 and no 소멸가치 — *anywhere*, mail included (R2/R3/R4
all restate it). :class:`OfferingInputs` and :class:`LapseResult` refuse to
construct with a money figure and no confirmed price, so "no money number at all"
is not a discipline a later surface has to keep: there is no object that could
carry one. Share counts still render — ⌊N × 배정비율⌋ needs no price.

**Facts are never tagged and estimates always are.** 주수, 소멸률, 확정발행가 and
할인율 are read from filings and come back as facts; 증서 1주 이론가치 (and every
won amount built on it) is derived by inverting the filing's own 발행가 산식 —
there is no price feed in this product — and comes back 「추정」. The split is
`states-and-trust.md` §1 and `headline-numbers.md`'s governing rule, in code.

**A filing that contradicts itself is shown contradicting itself.** In five
증권발행실적보고서 the issuer's own 실권주 cell disagrees with its own Ⅶ table
(대한광통신: stated 2,117,937 against 발행 23,465,365 − 청약 21,382,063 =
2,083,302). :class:`Disagreement` holds **both** readings with **both**
citations, and has no field in which a reconciled number could be put — no
average, no pick, no hidden conflict (`ui-traps.md` #2).

Nothing here reads a database or re-implements arithmetic: the inputs are already
loaded by the caller and every formula is :mod:`mijual.calc`'s.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any

from mijual.calc import warrant_intrinsic_value, warrant_intrinsic_value_floor
from mijual.present.event import field_value
from mijual.present.values import Figure, decimal_str, iso_day

if TYPE_CHECKING:  # pragma: no cover - imported for types only
    # ``mijual.estimate`` is **never** imported at runtime: it pulls
    # ``mijual.dart``, ``mijual.collect`` and ``mijual.extract`` at module level
    # (measured), and this layer is on a request path. The types below are for
    # readers and type-checkers; the functions read attributes.
    from mijual.estimate import EventInputs, LapseRow
    from mijual.gates.exposure import EventExposure

__all__ = [
    "Disagreement",
    "LapseResult",
    "MISMATCH_LABEL_KO",
    "OfferingInputs",
    "Reading",
    "issuer_disagreement",
    "lapse_result",
    "offering_inputs",
]

#: The locked literal `ui-traps.md` #2 names as *the exposed contract*, and the
#: string the R3 badge renders. Pre-existing copy, not invented here.
MISMATCH_LABEL_KO = "발행사 기재 불일치"

#: ``LapseRow`` attribute → the key its ``as_json()`` uses, where they differ.
#: :meth:`mijual.estimate.EventInputs.as_json` needs no aliases — its keys *are*
#: the attribute names, deliberately, so both forms read identically here.
_ROW_ALIASES = {"value": "value_krw", "value_floor": "value_floor_krw"}


def _read(row: Any, name: str) -> Any:
    """One field of a stored row, whether it arrived as an object or as JSON.

    ``build_report`` produces :class:`~mijual.estimate.LapseRow` objects and
    :func:`~mijual.estimate.event_inputs` produces ``EventInputs`` ones, but a
    request path cannot call either (importing :mod:`mijual.estimate` pulls
    :mod:`mijual.dart`, :mod:`mijual.collect` and :mod:`mijual.extract`).
    Accepting the stored ``as_json()`` form too means a caller can serve the same
    shape from a persisted row — ``PerformanceReport.lapse``,
    ``OfferingInput.inputs`` — without importing ``mijual.estimate`` at all.
    """
    if isinstance(row, Mapping):
        return row.get(_ROW_ALIASES.get(name, name))
    return getattr(row, name, None)


def _shareholder_window(subscription: Any) -> tuple[str | None, str | None]:
    """구주주(주주배정) 청약 window out of a ``subscription`` mapping.

    The same selection :attr:`mijual.estimate.EventInputs.shareholder_window`
    makes — 구주주 first, 주주배정 as the other name for it — restated for the
    stored JSON form. 일반공모 is deliberately not a fallback: it is a *later*
    offering to the public, and the 증서 that lapse are the shareholders'.
    """
    if not isinstance(subscription, Mapping):
        return (None, None)
    window = subscription.get("구주주") or subscription.get("주주배정") or {}
    if not isinstance(window, Mapping):
        return (None, None)
    return (iso_day(window.get("start")), iso_day(window.get("end")))


# ---------------------------------------------------------------------------
# ① offering inputs
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class OfferingInputs:
    """What an ① offering multiplies by — the factors, never the products.

    R4 composes the N주 math client-side from exactly these, so the same holding
    can never produce two divergent readouts. The 배정비율 is a decimal **string**
    at its printed precision (``0.2314082845``): ten decimal places are part of
    the design, and a float loses them.
    """

    rcept_no: str | None = None
    #: 예정발행가 — a price that is still provisional. Never a basis for money.
    planned_price: Figure | None = None
    #: 확정발행가. **The gate for every won figure in this class.**
    confirmed_price: Figure | None = None
    #: 할인율, and only when its citation gate passed (``issue_price_formula``).
    discount_rate: Figure | None = None
    #: 1주당 신주배정주식수, printed to 10 decimals.
    allotment_ratio: Figure | None = None
    #: 초과청약 비율 — 배정주식수 × this, floored (``mijual.calc``).
    excess_ratio: Figure | None = None
    new_shares: Figure | None = None
    record_date: str | None = None
    #: When the 확정발행가 is due, for the 발행가 확정 전 state. A date, not money.
    final_price_date: str | None = None
    #: 청약일정 per 대상자 — ``{"구주주": {"start": …, "end": …}, …}``.
    subscription: dict[str, dict[str, str]] | None = None
    #: 「추정」 증서 1주 이론가치 = 확정발행가 × 할인율 / (1 − 할인율).
    unit_value: Figure | None = None
    #: 「추정」 the band's lower edge (권리락 조정 가정).
    unit_value_floor: Figure | None = None

    def __post_init__(self) -> None:
        _assert_money_needs_a_price(
            self.confirmed_price, (self.unit_value, self.unit_value_floor)
        )

    @property
    def price_confirmed(self) -> bool:
        """Is a won figure permitted for this offering at all?"""
        return self.confirmed_price is not None

    def payload(self) -> dict[str, Any]:
        """JSON. With no 확정발행가 there is **no money key at all**, not a null."""
        out: dict[str, Any] = {
            "rcept_no": self.rcept_no,
            "price_confirmed": self.price_confirmed,
        }
        figures = {
            "planned_price": self.planned_price,
            "confirmed_price": self.confirmed_price,
            "discount_rate": self.discount_rate,
            "allotment_ratio": self.allotment_ratio,
            "excess_ratio": self.excess_ratio,
            "new_shares": self.new_shares,
            "unit_value": self.unit_value,
            "unit_value_floor": self.unit_value_floor,
        }
        out.update({key: fig.payload() for key, fig in figures.items() if fig is not None})
        if self.record_date is not None:
            out["record_date"] = self.record_date
        if self.final_price_date is not None:
            out["final_price_date"] = self.final_price_date
        if self.subscription:
            out["subscription"] = self.subscription
        return out


def _assert_money_needs_a_price(price: Figure | None, money: tuple[Figure | None, ...]) -> None:
    if price is None and any(figure is not None for figure in money):
        raise ValueError(
            "확정발행가 null ⇒ no money number at all: an offering with no "
            "confirmed price cannot carry a 증서 가치 or a won amount"
        )


def _cite(exposure: "EventExposure", field_key: str) -> dict[str, Any]:
    """The citation triple of a gate-passing field, for a value derived from it."""
    view = exposure.fields.get(field_key)
    if view is None or not view.exposable:
        return {}
    return {
        "quote": view.quote,
        "span": tuple(view.span) if view.span else None,
        "rcept_no": view.rcept_no,
    }


def offering_inputs(
    exposure: "EventExposure", inputs: "EventInputs | Mapping[str, Any]"
) -> OfferingInputs:
    """①'s money inputs, from an exposure + ``event_inputs`` (object **or** JSON).

    The prices, 배정비율 and 신주발행수 are ``본문-label`` reads (deterministic, no
    LLM); the 할인율, 초과청약 비율 and 확정 예정일 come from **gate-passing**
    extraction fields only — a blocked field contributes nothing, exactly as it
    contributes no row to the card.

    ``inputs`` may be a live :class:`~mijual.estimate.EventInputs` (a worker) or
    its stored ``as_json()`` mapping (``OfferingInput.inputs``, which is how a
    request path gets it — see :func:`_read`). The two produce the same object.
    """
    price_cite = _cite(exposure, "issue_price_formula")
    formula = field_value(exposure, "issue_price_formula")
    excess = field_value(exposure, "excess_subscription")

    rcept_no = _read(inputs, "rcept_no")
    confirmed_price = _read(inputs, "confirmed_price")
    discount_rate = _read(inputs, "discount_rate")
    allotment_ratio = _read(inputs, "allotment_ratio")
    price_span = _read(inputs, "price_span")

    confirmed = Figure.fact(
        decimal_str(confirmed_price),
        span=tuple(price_span) if price_span else None,
        rcept_no=rcept_no,
    )
    unit = warrant_intrinsic_value(confirmed_price, discount_rate)
    floor = warrant_intrinsic_value_floor(confirmed_price, discount_rate, allotment_ratio)
    return OfferingInputs(
        rcept_no=rcept_no,
        planned_price=Figure.fact(
            decimal_str(_read(inputs, "planned_price")), rcept_no=rcept_no
        ),
        confirmed_price=confirmed,
        discount_rate=Figure.fact(decimal_str(discount_rate), **price_cite),
        allotment_ratio=Figure.fact(decimal_str(allotment_ratio), rcept_no=rcept_no),
        excess_ratio=Figure.fact(
            decimal_str(excess.get("ratio")) if isinstance(excess, Mapping) else None,
            **_cite(exposure, "excess_subscription"),
        ),
        new_shares=Figure.fact(_read(inputs, "new_shares"), rcept_no=rcept_no),
        record_date=iso_day(_read(inputs, "record_date")),
        final_price_date=(
            iso_day(formula.get("final_price_date")) if isinstance(formula, Mapping) else None
        ),
        subscription={
            group: {key: iso_day(value) for key, value in window.items() if iso_day(value)}
            for group, window in (_read(inputs, "subscription") or {}).items()
        },
        unit_value=Figure.estimate(decimal_str(unit), rcept_no=rcept_no),
        unit_value_floor=Figure.estimate(decimal_str(floor), rcept_no=rcept_no),
    )


# ---------------------------------------------------------------------------
# the 소멸 outcome
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LapseResult:
    """What one ① offering's 청약 left behind: how many rights died, and their value.

    A lapse is a fact about the **past**, so a row exists even for an event the
    exposure contract would not publish today (``LapseRow.event_state``). What it
    never contains is the report's internal ``reason`` string — "할인율 게이트
    미통과 (gate=failed)" is an operator sentence, and a reader surface states its
    own signed copy from ``status`` instead (`states-and-trust.md` §4).
    """

    #: ``valued`` (money) · ``counted_only`` (shares, no price/할인율) · ``pending``.
    status: str
    corp_code: str | None = None
    corp_name: str | None = None
    decision_rcept_no: str | None = None
    performance_rcept_no: str | None = None
    subscription_end: str | None = None
    #: Ⅶ 발행된 신주인수권증서 — the denominator of the 소멸률.
    warrants_issued: Figure | None = None
    warrants_exercised: Figure | None = None
    #: 발행 − 청약. A subtraction of two cited counts is still a **fact**.
    lapsed: Figure | None = None
    lapse_rate: Figure | None = None
    confirmed_price: Figure | None = None
    discount_rate: Figure | None = None
    allotment_ratio: Figure | None = None
    unit_value: Figure | None = None
    unit_value_floor: Figure | None = None
    #: 「추정」 소멸가치 = 소멸 주수 × 증서 1주 이론가치, in 원.
    value: Figure | None = None
    value_floor: Figure | None = None

    def __post_init__(self) -> None:
        _assert_money_needs_a_price(
            self.confirmed_price,
            (self.unit_value, self.unit_value_floor, self.value, self.value_floor),
        )

    @property
    def is_valued(self) -> bool:
        return self.status == "valued" and self.value is not None

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"status": self.status}
        for key in ("corp_code", "corp_name", "decision_rcept_no", "performance_rcept_no",
                    "subscription_end"):
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        for key in ("warrants_issued", "warrants_exercised", "lapsed", "lapse_rate",
                    "confirmed_price", "discount_rate", "allotment_ratio", "unit_value",
                    "unit_value_floor", "value", "value_floor"):
            figure: Figure | None = getattr(self, key)
            if figure is not None:
                out[key] = figure.payload()
        return out


def lapse_result(row: "LapseRow | Mapping[str, Any]", *, facts: Mapping[str, Any] | None = None
                 ) -> LapseResult:
    """One offering's 소멸 outcome, from a report row (object **or** its JSON).

    ``facts`` is the linked 실적보고서's stored ``facts`` mapping; when given, the
    share counts carry the Ⅶ table's own printed text and span as their citation,
    which is what makes "발행 − 청약 = 소멸" answerable in one tap.
    """
    facts = facts or {}
    performance_rcept = _read(row, "performance_rcept_no") or facts.get("rcept_no")
    price = Figure.fact(decimal_str(_read(row, "confirmed_price")))
    return LapseResult(
        status=_read(row, "status") or "pending",
        corp_code=_read(row, "corp_code"),
        corp_name=_read(row, "corp_name"),
        decision_rcept_no=_read(row, "decision_rcept_no"),
        performance_rcept_no=performance_rcept,
        subscription_end=iso_day(_read(row, "subscription_end")),
        warrants_issued=_cited_count(
            _read(row, "warrants_issued"), facts.get("warrants_issued"), performance_rcept
        ),
        warrants_exercised=_cited_count(
            _read(row, "warrants_exercised"), facts.get("warrants_exercised"), performance_rcept
        ),
        lapsed=Figure.fact(_int(_read(row, "lapsed")), rcept_no=performance_rcept),
        lapse_rate=Figure.fact(
            decimal_str(_read(row, "lapse_rate")), rcept_no=performance_rcept
        ),
        confirmed_price=price,
        discount_rate=Figure.fact(decimal_str(_read(row, "discount_rate"))),
        allotment_ratio=Figure.fact(decimal_str(_read(row, "allotment_ratio"))),
        unit_value=Figure.estimate(decimal_str(_read(row, "unit_value"))),
        unit_value_floor=Figure.estimate(decimal_str(_read(row, "unit_value_floor"))),
        value=Figure.estimate(decimal_str(_read(row, "value"))),
        value_floor=Figure.estimate(decimal_str(_read(row, "value_floor"))),
    )


def _int(value: Any) -> int | None:
    return None if value is None else int(value)


def _cited_count(count: Any, cited: Any, rcept_no: str | None) -> Figure | None:
    """A share count, carrying the cell it was printed in **when that cell says it**.

    The citation is attached only if the stored cell's own text parses to exactly
    the number it would sit beside. That guard is not hypothetical: in 4 of the 32
    parsed 증권발행실적보고서 the 청약 (and 초과청약) figure is a **sum of two table
    rows** while ``raw``/``span`` point at one of them — 한화솔루션's 청약 38,430,497
    against a cell reading 38,427,609, and the same shape at SKC, 에스에너지 and
    루닛 (measured 2026-08-22). A ``[근거]`` chip quoting one addend as if it backed
    the whole number is a *false* citation, which is worse than none in a product
    whose one claim is "a number only when it can show where the number came from".

    So the value keeps its filing (``rcept_no`` — the DART link still resolves) and
    loses the verbatim quote. Making those figures properly citable, with a span
    per addend, is deferred job **D4**; this is the honest reading until it lands.
    """
    if count is None:
        return None
    if not isinstance(cited, Mapping):
        return Figure.fact(_int(count), rcept_no=rcept_no)
    if _backs(cited.get("raw"), count):
        span = cited.get("span")
        return Figure.fact(
            _int(count),
            quote=cited.get("raw"),
            span=tuple(span) if span else None,
            rcept_no=rcept_no,
        )
    return Figure.fact(_int(count), rcept_no=rcept_no)


def _backs(raw: Any, value: Any) -> bool:
    """Does this printed cell state exactly this number? Commas and 주 ignored."""
    if not isinstance(raw, str) or value is None:
        return False
    text = raw.replace(",", "").replace("주", "").strip()
    try:
        return Decimal(text) == Decimal(str(value))
    except (InvalidOperation, ValueError):
        return False


# ---------------------------------------------------------------------------
# 발행사 기재 불일치
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Reading:
    """One of two ways the same filing answers the same question."""

    #: ``lapse_stated`` (the issuer's own cell) / ``lapse_derived`` (발행 − 청약).
    key: str
    figure: Figure
    #: The filer's **own** header text for the cell, where the reading is one
    #: cell. ``None`` for a derived reading — the surface names it in its signed
    #: copy rather than this layer inventing a Korean label.
    label: str | None = None
    #: The cited figures a derived reading was computed from, each with its own
    #: quote and span. Empty for a directly printed reading.
    inputs: tuple[Figure, ...] = ()
    #: Whether the product's own totals use this reading. Stating which one is
    #: used is not the same as reconciling them.
    used: bool = False

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"key": self.key, "used": self.used, **self.figure.payload()}
        if self.label is not None:
            out["label"] = self.label
        if self.inputs:
            out["inputs"] = [figure.payload() for figure in self.inputs]
        return out


@dataclass(frozen=True)
class Disagreement:
    """A filing at odds with itself — both readings, both citations, no verdict.

    There is deliberately **no** field on this class for a resolved value. The
    product does not average the two, does not pick one silently and does not
    hide the conflict; it states which reading its totals use and shows the other
    beside it.
    """

    kind: str
    label_ko: str
    readings: tuple[Reading, ...]

    def __post_init__(self) -> None:
        if len(self.readings) < 2:
            raise ValueError("a disagreement needs both readings — one reading is just a value")
        if sum(1 for reading in self.readings if reading.used) != 1:
            raise ValueError(
                "exactly one reading is the one the totals use; naming none hides "
                "the choice and naming two is a reconciliation"
            )

    def payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "label_ko": self.label_ko,
            "readings": [reading.payload() for reading in self.readings],
        }


def issuer_disagreement(
    facts: Mapping[str, Any], *, rcept_no: str | None = None
) -> Disagreement | None:
    """The 실권주 conflict of one 실적보고서, or ``None`` when the filing agrees.

    ``facts`` is the stored :class:`~mijual.estimate.perf.PerformanceFacts` JSON
    (``PerformanceReport.facts``) — available from a persisted row, so no part of
    this needs the parser. The product's totals use **발행 − 청약** because the
    단수주 in the issuer's own cell was never issued as a 증서 at all
    (:func:`mijual.calc.lapsed_warrants`), and that choice is stated, not hidden.
    """
    stated = facts.get("lapse_stated")
    derived = facts.get("lapse_derived")
    if not isinstance(stated, Mapping) or derived is None:
        return None
    stated_value = _int(stated.get("value"))
    if stated_value is None or stated_value == int(derived):
        return None

    cited = _cited_count(stated_value, stated, rcept_no or facts.get("rcept_no"))
    if cited is None:  # unreachable while stated_value is an int; never a half-shown clash
        return None
    issued = _cited_count(
        _cited_value(facts, "warrants_issued"),
        facts.get("warrants_issued"),
        rcept_no or facts.get("rcept_no"),
    )
    exercised = _cited_count(
        _cited_value(facts, "warrants_exercised"),
        facts.get("warrants_exercised"),
        rcept_no or facts.get("rcept_no"),
    )
    return Disagreement(
        kind="lapse_mismatch",
        label_ko=MISMATCH_LABEL_KO,
        readings=(
            Reading(key="lapse_stated", figure=cited, label=stated.get("label"), used=False),
            Reading(
                key="lapse_derived",
                figure=Figure(
                    value=int(derived),
                    estimated=False,
                    rcept_no=rcept_no or facts.get("rcept_no"),
                ),
                inputs=tuple(f for f in (issued, exercised) if f is not None),
                used=True,
            ),
        ),
    )


def _cited_value(facts: Mapping[str, Any], key: str) -> Any:
    cited = facts.get(key)
    return cited.get("value") if isinstance(cited, Mapping) else None
