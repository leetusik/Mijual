"""The 소멸 신주인수권 estimate: the arithmetic, the table read, the end-to-end (P2.S8).

Offline by construction — the two documents come from the on-disk response cache
with the client offline, the end-to-end case is built on SQLite, and nothing here
needs a key, a network, the Postgres corpus or an LLM. No filing is invented.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mijual.bodydoc import BodyDocument, Span
from mijual.calc import (
    lapsed_warrants,
    warrant_intrinsic_value,
    warrant_intrinsic_value_floor,
)
from mijual.dart import CacheMiss, DartClient
from mijual.db.models import Base, Extraction, PerformanceReport, RightsType
from mijual.db.repository import ensure_corp, ensure_event, ensure_snapshot, ensure_version
from mijual.estimate import build_report
from mijual.estimate.perf import parse_performance, squash

#: 이뮨온시아 — 실적보고서 and the 유상증자결정 정정 it reports on.
PERF_RCEPT = "20260521000623"
DECISION_RCEPT = "20260511000437"
#: LB세미콘 — the filing whose own 실권주 cell disagrees with its Ⅶ tables.
MISMATCH_RCEPT = "20260811000597"


def _doc(rcept_no: str) -> BodyDocument:
    client = DartClient(offline=True)
    try:
        return BodyDocument.from_bytes(client.get_document(rcept_no), rcept_no=rcept_no)
    except CacheMiss:  # pragma: no cover - the cache is regenerable, not required
        pytest.skip(f"{rcept_no} is not in the response cache")


# --- the arithmetic --------------------------------------------------------
def test_the_two_pricing_formulas_give_the_same_증서_value():
    """1차 (cum-rights, 증자비율 term) and 2차 (ex-rights) must agree — that is
    why :func:`warrant_intrinsic_value` takes no formula argument."""
    price, d, r = Decimal("4860"), Decimal("0.25"), Decimal("0.2263223966")
    ex_rights = warrant_intrinsic_value(price, d)

    reference_1 = price * (1 + r * d) / (1 - d)  # invert the 1차 산식
    cum_rights = (reference_1 - price) / (1 + r)  # 이론권리락주가 − 확정발행가
    assert abs(ex_rights - cum_rights) < Decimal("0.000001")
    assert ex_rights == price * d / (1 - d)


def test_value_helpers_refuse_nonsense_instead_of_guessing():
    assert warrant_intrinsic_value(None, 0.25) is None
    assert warrant_intrinsic_value(4860, None) is None
    assert warrant_intrinsic_value(4860, 1.0) is None  # division by zero
    assert warrant_intrinsic_value(0, 0.25) is None
    # The band's lower edge is the upper divided by the dilution factor.
    assert warrant_intrinsic_value_floor(1000, Decimal("0.5"), 1) == Decimal("500")
    assert warrant_intrinsic_value_floor(1000, Decimal("0.5"), None) == Decimal("1000")


def test_lapsed_warrants_never_counts_단수주_and_never_goes_negative():
    assert lapsed_warrants(16810570, 14964975) == 1845595
    assert lapsed_warrants(100, 120) == 0
    assert lapsed_warrants(None, 5) is None
    assert lapsed_warrants(5, None) is None


# --- reading the 증권발행실적보고서 ------------------------------------------
def test_실적보고서_yields_the_lapse_the_price_and_a_verifiable_span():
    facts = parse_performance(_doc(PERF_RCEPT))
    doc = _doc(PERF_RCEPT)

    assert facts.warrants_issued.int_value == 16810570
    assert facts.warrants_exercised.int_value == 14964975
    assert facts.lapse_derived == 1845595 == facts.lapse_stated.int_value
    assert facts.issue_price == Decimal("4860")  # 최종 금액 ÷ 수량, exact
    assert facts.lapse_rate == Decimal("0.1098")
    # 구주주 청약 window, which is what binds the report to its event.
    assert [(r.begin.value, r.end.value) for r in facts.schedule] == [
        (date(2026, 5, 13), date(2026, 5, 14))
    ]
    # Every figure re-slices to itself in the stored bytes (the N33 contract).
    for cited in (facts.warrants_issued, facts.lapse_stated, facts.final_amount):
        assert doc.verify(Span(*cited.span), cited.raw)


def test_a_filers_own_실권주_cell_can_disagree_and_the_Ⅶ_tables_win():
    facts = parse_performance(_doc(MISMATCH_RCEPT))
    assert facts.lapse_stated.int_value == 2109436
    assert facts.lapse_derived == 2080336  # 11,970,900 − 9,890,564
    assert any("lapse_mismatch" in note for note in facts.notes)


#: 한화솔루션 ``20260730000366``'s Ⅶ 청약내역, cut down to the shape that matters:
#: the same 청약 arrives through 예탁결제원 **and** 직접청약, so the figure the report
#: means is the sum of two rows and is printed nowhere as itself.
SPLIT_SUBSCRIPTION_TABLE = """<DOCUMENT><TABLE>
<TR><TD>청약일</TD><TD>청약자</TD><TD>발행회사와의 관계</TD><TD>주식수</TD></TR>
<TR><TD>2026년 07월 23일</TD><TD>한국예탁결제원(신주인수권증서 청약)</TD><TD>-</TD><TD>38,427,609</TD></TR>
<TR><TD>2026년 07월 23일</TD><TD>한국예탁결제원(초과청약)</TD><TD>-</TD><TD>6,148,305</TD></TR>
<TR><TD>2026년 07월 23일</TD><TD>직접청약(신주인수권증서 청약)</TD><TD>-</TD><TD>2,888</TD></TR>
<TR><TD>계</TD><TD>44,578,802</TD></TR>
</TABLE></DOCUMENT>"""


def test_a_청약_summed_over_rows_keeps_every_addends_own_cell():
    """D4: cite the sum with all of its parts, or it cannot be cited at all."""
    doc = BodyDocument.from_text(SPLIT_SUBSCRIPTION_TABLE)
    facts = parse_performance(doc)

    exercised = facts.warrants_exercised
    assert exercised.int_value == 38430497  # 38,427,609 + 2,888
    assert [p.raw for p in exercised.parts] == ["38,427,609", "2,888"]
    assert all(doc.verify(Span(*p.span), p.raw) for p in exercised.parts)
    # 초과청약 arrived on one row here, so it stays an ordinary one-cell citation
    # — and serializes exactly as it did before parts existed.
    assert facts.excess_subscribed.parts == () and facts.excess_subscribed.raw == "6,148,305"
    assert set(facts.excess_subscribed.as_json()) == {"value", "raw", "span", "label"}
    single = facts.excess_subscribed.citations
    assert len(single) == 1 and single[0].raw == facts.excess_subscribed.raw
    assert len(exercised.as_json()["parts"]) == 2


def test_the_실권주_column_is_found_by_its_header_not_by_its_position():
    """대동기어 ``20260728000264`` puts 단수주 first and labels it 배정 실권주."""
    header = "신주인수권증서 배정 실권주 | 신주인수권증서 청약 실권주 | 실권주 및 단수주 총계"
    cells = header.split(" | ")
    assert squash(cells[0]) == "신주인수권증서배정실권주"
    assert [i for i, c in enumerate(cells) if "청약" in c and "실권주" in c] == [1]


# --- end to end, offline ---------------------------------------------------
def test_end_to_end_one_offering_from_stored_evidence():
    """Corpus → report, on SQLite, with 0 requests and 0 LLM calls."""
    perf_doc, decision_doc = _doc(PERF_RCEPT), _doc(DECISION_RCEPT)
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)

    with factory() as session:
        ensure_corp(session, "01203659", corp_name="이뮨온시아")
        event = ensure_event(
            session,
            corp_code="01203659",
            report_subtype="piicDecsn",
            original_rcept_dt="20260206",
            rights_type=RightsType.SUBSCRIPTION_WARRANT,
        )
        version = ensure_version(session, event, rcept_no=DECISION_RCEPT, rcept_dt="20260511")
        ensure_snapshot(
            session,
            version,
            source="document",
            payload_bytes=DartClient(offline=True).get_document(DECISION_RCEPT),
        )
        session.add(
            Extraction(
                event_id=event.id,
                filing_version_id=version.id,
                rcept_no=DECISION_RCEPT,
                field_key="issue_price_formula",
                status="extracted",
                value={"discount_rate": 0.25},
                gate_status="passed",
            )
        )
        facts = parse_performance(perf_doc)
        session.add(
            PerformanceReport(
                event_id=event.id,
                corp_code="01203659",
                corp_name="이뮨온시아",
                rcept_no=PERF_RCEPT,
                rcept_dt=date(2026, 5, 21),
                parse_status="parsed",
                facts=facts.as_json(),
            )
        )
        session.flush()

        report = build_report(session, today=date(2026, 8, 20))
        assert len(report.rows) == 1
        row = report.rows[0]
        assert row.status == "valued"
        assert row.lapsed == 1845595
        assert row.confirmed_price == Decimal("4860")  # 본문 6.
        assert row.price_check == "agree"  # …and the 실적보고서 agrees exactly
        assert row.unit_value == Decimal("1620")  # 4,860 × 0.25/0.75
        assert row.value == Decimal("2989863900")
        assert report.total_value == Decimal("2989863900")
        # The decision document is real, so 배정비율 comes off 본문 9.
        assert row.allotment_ratio == pytest.approx(0.2263223966)
        assert report.total_value_floor < report.total_value
        assert decision_doc.rcept_no == DECISION_RCEPT
