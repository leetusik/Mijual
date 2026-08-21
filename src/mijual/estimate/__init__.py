"""``mijual.estimate`` — 2026 소멸 신주인수권 가치 총액 (P2.S8).

The presentation's opening number: **how much 신주인수권 value lapsed unexercised
in 2026**. This is a reporting pipeline over the collected corpus, not part of
the serving path — nothing here is reachable from a request.

### The method, in one line

    소멸가치 = Σ (소멸한 증서 수) × 확정발행가 × 할인율 / (1 − 할인율)

Three inputs, three sources, all DART:

``소멸한 증서 수``
    ``증권발행실적보고서 Ⅶ``: 발행된 신주인수권증서 − 증서로 이루어진 청약.
    Deterministic table read (:mod:`mijual.estimate.perf`), never an LLM call.
``확정발행가``
    본문 ``6. 신주 발행가액 → 확정발행가`` (``본문-label`` tier), cross-checked
    against the 실적보고서's own 최종 배정 금액 ÷ 수량 — **exact on 31/31 filings**
    that state both (the 32nd prints a 9-column 계 row and is 본문-only).
``할인율``
    the only prose input: ``24-가 신주발행가액 산정방법``, read by ``P2.S4``'s
    extractor and **only used when ``P2.S5``'s gate passed it**. A field whose
    gate failed is not quietly used here either — it is a stated gap.

### Why this proxy, and why it is honest

`data.md` fixes DART as the sole source, so there is **no 증서 시세 and no stock
price in this repo**. The filing supplies the price itself: every 주주배정 유증
states 발행가액 = 기준주가 × (1 − 할인율), so the issuer's own 기준주가 is
recoverable by inversion, and 증서 이론가치 = 기준주가 − 확정발행가. The identity
holds for both the 1차 (cum-rights, with the 증자비율 term) and the 2차
(ex-rights) formula — see :func:`mijual.calc.warrant_intrinsic_value`.

Every figure is therefore either an **evidence-tagged fact** (a number printed in
a filing, with its ``rcept_no`` and a character span) or a **▷ estimate** (the
unit value and every total built from it). The two are never blurred, and the
gaps — an offering whose 실적보고서 is not filed yet, a 할인율 whose gate failed —
are listed as gaps rather than filled in.

    .venv/bin/python -m mijual.estimate report          # 0 requests, 0 calls
    .venv/bin/python -m mijual.estimate collect --max-requests 400
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.bodydoc import BodyDocument
from mijual.bodydoc.backfill import load_document
from mijual.calc import (
    lapsed_warrant_value,
    warrant_intrinsic_value,
    warrant_intrinsic_value_floor,
)
from mijual.db.models import Event, Extraction, PerformanceReport, RightsType
from mijual.extract.runner import readable_versions
from mijual.gates.context import version_context

__all__ = [
    "DISCOUNT_FIELD",
    "LapseReport",
    "LapseRow",
    "build_report",
    "event_inputs",
    "won",
]

#: The §7 field whose gate-passed value carries the 할인율.
DISCOUNT_FIELD = "issue_price_formula"


def won(amount: Decimal | int | None) -> str:
    """``2989863900`` → ``29.9억원``. The unit the board and the deck speak."""
    if amount is None:
        return "-"
    value = Decimal(amount)
    if abs(value) >= 10**12:
        return f"{value / Decimal(10**12):,.2f}조원"
    if abs(value) >= 10**8:
        return f"{value / Decimal(10**8):,.1f}억원"
    return f"{value:,.0f}원"


@dataclass
class EventInputs:
    """The three deterministic inputs of one event, each with its evidence."""

    rcept_no: str | None = None
    confirmed_price: float | None = None
    price_source: str | None = None
    price_span: tuple[int, int] | None = None
    planned_price: float | None = None
    discount_rate: float | None = None
    discount_gate: str | None = None
    discount_rcept_no: str | None = None
    allotment_ratio: float | None = None
    new_shares: int | None = None
    record_date: date | None = None
    subscription: dict[str, dict[str, date]] = field(default_factory=dict)

    @property
    def shareholder_window(self) -> tuple[date | None, date | None]:
        window = self.subscription.get("구주주") or self.subscription.get("주주배정") or {}
        return (window.get("start"), window.get("end"))

    def as_json(self) -> dict:
        """The persisted form (``OfferingInput.inputs``), read back by the API.

        Numbers travel as **exact decimal strings** and dates as bare ISO days,
        the same serialization the presentation contract emits — a JSON float
        would quietly round a 10-decimal 배정비율 on the way through storage.
        Keys are the attribute names, so :func:`mijual.present.offering_inputs`
        reads this mapping and a live :class:`EventInputs` identically.
        """

        def number(value: float | Decimal | None) -> str | None:
            return None if value is None else str(value)

        return {
            "rcept_no": self.rcept_no,
            "confirmed_price": number(self.confirmed_price),
            "price_source": self.price_source,
            "price_span": list(self.price_span) if self.price_span else None,
            "planned_price": number(self.planned_price),
            "discount_rate": number(self.discount_rate),
            "discount_gate": self.discount_gate,
            "discount_rcept_no": self.discount_rcept_no,
            "allotment_ratio": number(self.allotment_ratio),
            "new_shares": self.new_shares,
            "record_date": str(self.record_date) if self.record_date else None,
            "subscription": {
                group: {key: str(day) for key, day in window.items() if day is not None}
                for group, window in (self.subscription or {}).items()
            },
        }


def event_inputs(session: Session, event: Event) -> EventInputs:
    """Read one ① event's 확정발행가 · 할인율 · 배정비율 from stored evidence only.

    Zero requests, zero calls: the 본문 comes from the event's own snapshot and
    the 할인율 from the persisted extraction row plus **its gate verdict**.
    """
    inputs = EventInputs()
    versions = readable_versions(event)
    if not versions:
        return inputs
    version = versions[-1]
    inputs.rcept_no = version.rcept_no

    blob, _ = load_document(session, None, version, fetch=False)
    if blob is not None:
        doc = BodyDocument.from_bytes(blob, rcept_no=version.rcept_no)
        context = version_context(session, event, version, doc)
        inputs.confirmed_price = context.confirmed_price
        inputs.planned_price = context.planned_price
        inputs.record_date = context.record_date
        inputs.subscription = context.subscription_dates
        if inputs.confirmed_price is not None:
            inputs.price_source = f"본문 6. 확정발행가 ({version.rcept_no})"
            for row in context.labels.all("issue_price"):
                if "확정발행가" in " ".join(row.qualifier) and row.span is not None:
                    inputs.price_span = row.span.as_tuple()
                    break
        ratio = context.labels.value("shares_per_share")
        if isinstance(ratio, (int, float)):
            inputs.allotment_ratio = float(ratio)
        shares = context.labels.value("new_shares")
        if isinstance(shares, int):
            inputs.new_shares = shares

    row = session.scalar(
        select(Extraction).where(
            Extraction.filing_version_id == version.id,
            Extraction.field_key == DISCOUNT_FIELD,
        )
    )
    if row is not None:
        inputs.discount_gate = row.gate_status
        inputs.discount_rcept_no = row.rcept_no
        if row.gate_status == "passed" and isinstance(row.value, dict):
            rate = row.value.get("discount_rate")
            if isinstance(rate, (int, float)) and 0 < rate < 1:
                inputs.discount_rate = float(rate)
    return inputs


@dataclass
class LapseRow:
    """One offering: what lapsed, what it was worth, and the evidence for both."""

    corp_code: str
    corp_name: str | None
    status: str = "pending"
    reason: str | None = None
    #: 유상증자결정's current version, and the 실적보고서.
    decision_rcept_no: str | None = None
    performance_rcept_no: str | None = None
    #: The linked event's exposure verdict. A lapse is a fact about the **past**,
    #: so an event the contract will not *publish* can still be counted here —
    #: but never silently: a non-``exposable`` row is called out in ``render``.
    event_state: str | None = None
    subscription_end: date | None = None
    record_date: date | None = None
    warrants_issued: int | None = None
    warrants_exercised: int | None = None
    lapsed: int | None = None
    lapse_rate: Decimal | None = None
    confirmed_price: Decimal | None = None
    price_check: str | None = None
    discount_rate: float | None = None
    allotment_ratio: float | None = None
    unit_value: Decimal | None = None
    unit_value_floor: Decimal | None = None
    value: Decimal | None = None
    value_floor: Decimal | None = None
    notes: tuple[str, ...] = ()

    @property
    def is_valued(self) -> bool:
        return self.status == "valued" and self.value is not None

    def line(self) -> str:
        return (
            f"  {(self.corp_name or self.corp_code)[:14]:<15}"
            f"{str(self.subscription_end or '-'):<12}"
            f"{(f'{self.lapsed:,}' if self.lapsed is not None else '-'):>12}"
            f"{(f'{self.lapse_rate:.1%}' if self.lapse_rate is not None else '-'):>8}"
            f"{(f'{self.confirmed_price:,.0f}' if self.confirmed_price else '-'):>10}"
            f"{(f'{self.discount_rate:.0%}' if self.discount_rate else '-'):>7}"
            f"{(f'{self.unit_value:,.0f}' if self.unit_value else '-'):>9}"
            f"{won(self.value):>12}  "
            f"{self.performance_rcept_no or '-'} / {self.decision_rcept_no or '-'}"
        )

    def as_json(self) -> dict:
        return {
            "corp_code": self.corp_code,
            "corp_name": self.corp_name,
            "status": self.status,
            "reason": self.reason,
            "decision_rcept_no": self.decision_rcept_no,
            "performance_rcept_no": self.performance_rcept_no,
            "event_state": self.event_state,
            "subscription_end": str(self.subscription_end) if self.subscription_end else None,
            "warrants_issued": self.warrants_issued,
            "warrants_exercised": self.warrants_exercised,
            "lapsed": self.lapsed,
            "lapse_rate": str(self.lapse_rate) if self.lapse_rate is not None else None,
            "confirmed_price": str(self.confirmed_price) if self.confirmed_price else None,
            "price_check": self.price_check,
            "discount_rate": self.discount_rate,
            "allotment_ratio": self.allotment_ratio,
            "unit_value": str(self.unit_value) if self.unit_value else None,
            "unit_value_floor": str(self.unit_value_floor) if self.unit_value_floor else None,
            "value_krw": str(self.value) if self.value else None,
            "value_floor_krw": str(self.value_floor) if self.value_floor else None,
            "notes": list(self.notes),
        }


@dataclass
class LapseReport:
    """The 2026 소멸 총액, its per-offering evidence, and its honest gaps."""

    today: date
    rows: list[LapseRow] = field(default_factory=list)
    pending: list[LapseRow] = field(default_factory=list)
    census_reports: int = 0
    census_candidates: int = 0

    @property
    def valued(self) -> list[LapseRow]:
        return [r for r in self.rows if r.is_valued]

    @property
    def counted_only(self) -> list[LapseRow]:
        return [r for r in self.rows if r.status == "counted_only"]

    @property
    def total_value(self) -> Decimal:
        return sum((r.value for r in self.valued), Decimal(0))

    @property
    def total_value_floor(self) -> Decimal:
        """▷ The band's lower edge — see :func:`mijual.calc.warrant_intrinsic_value_floor`."""
        return sum((r.value_floor or Decimal(0) for r in self.valued), Decimal(0))

    @property
    def total_lapsed(self) -> int:
        return sum(r.lapsed or 0 for r in self.rows)

    @property
    def total_issued(self) -> int:
        return sum(r.warrants_issued or 0 for r in self.rows)

    @property
    def overall_lapse_rate(self) -> Decimal | None:
        if not self.total_issued:
            return None
        return (Decimal(self.total_lapsed) / Decimal(self.total_issued)).quantize(
            Decimal("0.0001")
        )

    @property
    def upper_bound(self) -> Decimal:
        """▷ Headline + the counted-but-unvalued rows priced at the median 할인율.

        Reported **beside** the headline and never inside it: it exists so the
        size of the gap is visible, not so the gap can be closed by assumption.
        """
        rates = sorted(r.discount_rate for r in self.valued if r.discount_rate)
        if not rates:
            return self.total_value
        median = rates[len(rates) // 2]
        extra = Decimal(0)
        for row in self.counted_only:
            if row.lapsed and row.confirmed_price:
                unit = warrant_intrinsic_value(row.confirmed_price, median)
                if unit is not None:
                    extra += lapsed_warrant_value(row.lapsed, 1, unit)
        return self.total_value + extra

    def render(self) -> str:
        lines = [
            f"today      : {self.today} (KST)",
            f"stored     : {self.census_reports:,} 증권발행실적보고서 read, "
            f"{self.census_candidates} with a 신주인수권증서 table",
            f"offerings  : {len(self.rows)} ① 주주배정 유증 with a 청약 결과 "
            f"({len(self.valued)} valued, {len(self.counted_only)} counted only), "
            f"{len(self.pending)} still open",
            "",
            f"▷ 2026 소멸 신주인수권 가치 총액 : {won(self.total_value)} "
            f"({self.total_value:,.0f}원)",
            f"  ▷ 밴드 하한 (권리락 조정 가정) : {won(self.total_value_floor)}",
            f"  소멸 증서 {self.total_lapsed:,}주 / 발행 증서 {self.total_issued:,}주"
            + (
                f" — 소멸률 {self.overall_lapse_rate:.2%}"
                if self.overall_lapse_rate is not None
                else ""
            ),
            "",
            f"  {'회사':<15}{'청약종료':<12}{'소멸증서':>12}{'소멸률':>8}"
            f"{'확정가':>10}{'할인율':>7}{'증서가치':>9}{'소멸가치':>12}  실적보고서 / 유증결정",
        ]
        for row in sorted(self.rows, key=lambda r: (r.subscription_end or date.min)):
            lines.append(row.line())
        odd = [r for r in self.rows if r.event_state not in (None, "exposable")]
        if odd:
            lines.append("")
            lines.append(
                "counted though the exposure contract would not publish the event "
                "(a lapse is a fact about the past):"
            )
            for row in odd:
                lines.append(f"  {row.corp_name}: event_state={row.event_state}")
        if self.counted_only:
            lines.append("")
            lines.append("gaps (counted, not valued — no gate-passed 할인율):")
            for row in self.counted_only:
                lines.append(f"  {row.corp_name}: {row.lapsed:,}주 — {row.reason}")
            lines.append(
                f"  ▷ upper bound if those were priced at the corpus median 할인율: "
                f"{won(self.upper_bound)}"
            )
        if self.pending:
            lines.append("")
            lines.append("still open (no 청약 결과 yet):")
            for row in sorted(self.pending, key=lambda r: (r.subscription_end or date.max)):
                lines.append(
                    f"  {(row.corp_name or row.corp_code)[:14]:<15}"
                    f"{str(row.subscription_end or '미정'):<12}{row.reason or ''}"
                )
        return "\n".join(lines)

    def as_json(self) -> dict:
        return {
            "today": str(self.today),
            "census_reports": self.census_reports,
            "census_candidates": self.census_candidates,
            "total_value_krw": str(self.total_value),
            "total_value_floor_krw": str(self.total_value_floor),
            "total_lapsed": self.total_lapsed,
            "total_issued": self.total_issued,
            "overall_lapse_rate": (
                str(self.overall_lapse_rate) if self.overall_lapse_rate is not None else None
            ),
            "upper_bound_krw": str(self.upper_bound),
            "rows": [r.as_json() for r in sorted(self.rows, key=lambda r: r.corp_code)],
            "pending": [r.as_json() for r in sorted(self.pending, key=lambda r: r.corp_code)],
        }


def _cited_int(facts: dict, key: str) -> int | None:
    """One :class:`~mijual.estimate.perf.Cited` figure out of the stored JSON."""
    value = (facts.get(key) or {}).get("value")
    return int(Decimal(value)) if value not in (None, "") else None


def _price_check(inputs: EventInputs, derived: Decimal | None) -> tuple[Decimal | None, str]:
    """확정발행가 from the 본문 label, cross-checked against the 실적보고서's own.

    Two independent documents, two independent arithmetics: 본문 ``6. 확정발행가``
    is a printed price, the 실적보고서's is 최종 배정 금액 ÷ 수량. Agreement is not
    decoration — it is what lets the price be treated as a fact rather than as a
    reading.
    """
    label = Decimal(str(inputs.confirmed_price)) if inputs.confirmed_price else None
    if label is not None and derived is not None:
        return (label, "agree" if label == derived else f"disagree(본문 {label} vs 실적 {derived})")
    if label is not None:
        return (label, "본문 only")
    if derived is not None:
        return (derived, "실적보고서 only (본문 6. 확정발행가 미기재)")
    return (None, "none")


def build_report(session: Session, *, today: date) -> LapseReport:
    """Build the whole estimate from persisted rows. **0 requests, 0 LLM calls.**"""
    report = LapseReport(today=today)
    reports = list(session.scalars(select(PerformanceReport)).all())
    report.census_reports = len(reports)
    report.census_candidates = sum(1 for r in reports if r.parse_status == "parsed")
    linked_events: set[int] = set()

    for stored in sorted(reports, key=lambda p: (p.rcept_dt or date.min, p.rcept_no)):
        facts = stored.facts or {}
        if stored.parse_status != "parsed":
            continue
        event = session.get(Event, stored.event_id) if stored.event_id else None
        inputs = event_inputs(session, event) if event is not None else EventInputs()
        if event is not None:
            linked_events.add(event.id)

        lapsed = facts.get("lapse_derived")
        if lapsed is None:
            lapsed = _cited_int(facts, "lapse_stated")
        derived_price = (
            Decimal(facts["issue_price"]) if facts.get("issue_price") else None
        )
        price, check = _price_check(inputs, derived_price)
        row = LapseRow(
            corp_code=stored.corp_code,
            corp_name=stored.corp_name,
            decision_rcept_no=inputs.rcept_no,
            performance_rcept_no=stored.rcept_no,
            event_state=event.exposure_state if event is not None else None,
            record_date=inputs.record_date,
            warrants_issued=_cited_int(facts, "warrants_issued"),
            warrants_exercised=_cited_int(facts, "warrants_exercised"),
            lapsed=lapsed,
            lapse_rate=Decimal(facts["lapse_rate"]) if facts.get("lapse_rate") else None,
            confirmed_price=price,
            price_check=check,
            discount_rate=inputs.discount_rate,
            notes=tuple(facts.get("notes") or ()),
        )
        for entry in facts.get("schedule") or []:
            group = entry.get("group") or ""
            if "일반공모" in group or "우리사주" in group:
                continue
            end = (entry.get("end") or {}).get("value")
            if end:
                row.subscription_end = date.fromisoformat(end)
                break

        if lapsed is None:
            row.status, row.reason = "counted_only", "실적보고서에 증서 실권 수치 없음"
        elif price is None:
            row.status, row.reason = "counted_only", "확정발행가 미확인"
        elif inputs.discount_rate is None:
            row.status = "counted_only"
            row.reason = (
                f"할인율 게이트 미통과 (gate={inputs.discount_gate or 'none'})"
                if event is not None
                else "유상증자결정 미수집 — 할인율 없음"
            )
        else:
            unit = warrant_intrinsic_value(price, inputs.discount_rate)
            floor = warrant_intrinsic_value_floor(
                price, inputs.discount_rate, inputs.allotment_ratio
            )
            row.allotment_ratio = inputs.allotment_ratio
            row.unit_value, row.unit_value_floor = unit, floor
            row.value = lapsed_warrant_value(lapsed, 1, unit) if unit is not None else None
            row.value_floor = (
                lapsed_warrant_value(lapsed, 1, floor) if floor is not None else None
            )
            row.status = "valued"
        report.rows.append(row)

    # Every ① event that has not (yet) produced a 청약 결과 is a stated gap, not
    # a silent omission: an upcoming 청약, a 철회, or a 추후결정 schedule.
    seen_decisions: set[str] = set()
    for event in session.scalars(
        select(Event).where(Event.rights_type == RightsType.SUBSCRIPTION_WARRANT)
    ).all():
        if event.id in linked_events or event.suppressed_reason is not None:
            continue
        if event.exposure_state not in ("exposable", "withdrawn", "flagged"):
            continue
        inputs = event_inputs(session, event)
        # N21's residue: one ``rcept_no`` can sit under two event keys, and the
        # 발표 line counts offerings, not rows.
        if inputs.rcept_no is not None:
            if inputs.rcept_no in seen_decisions:
                continue
            seen_decisions.add(inputs.rcept_no)
        _, end = inputs.shareholder_window
        reason = {
            "withdrawn": "유상증자 철회",
            "flagged": f"식별 충돌 플래그 ({event.exposure_reason})",
        }.get(event.exposure_state or "", "")
        if not reason:
            reason = (
                "청약 예정" if end and end > today else "청약 종료 — 증권발행실적보고서 미제출"
            )
            if end is None:
                reason = "청약일 추후결정"
        report.pending.append(
            LapseRow(
                corp_code=event.corp_code,
                corp_name=event.corp.corp_name if event.corp else None,
                status="pending",
                reason=reason,
                decision_rcept_no=inputs.rcept_no,
                subscription_end=end,
                record_date=inputs.record_date,
            )
        )
    return report
