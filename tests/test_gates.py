"""The five things layer 2 must not get wrong (P2.S5).

LLM-free and request-free by construction: every document comes from an on-disk
response cache, every extraction row is built by hand, and no test needs the
Postgres corpus. Terse by the workspace rule — one case per property whose
failure would put a wrong number, or a cancelled offering, in front of a user.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mijual.bodydoc import BodyDocument, extract_labels, parse_correction
from mijual.bodydoc.correction import CorrectionItem
from mijual.calc import (
    allotted_shares,
    d_day,
    excess_subscription_cap,
    lapsed_warrant_value,
    today_kst,
    window_state,
)
from mijual.config import DEFAULT_CACHE_DIR, SPIKE_CACHE_DIR
from mijual.dart import CacheMiss, DartClient
from mijual.db.models import Base, Extraction, RightsType, Snapshot
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.gates import evaluate_field, event_exposure, is_withdrawal_row
from mijual.gates.context import VersionContext


def _doc(rcept_no: str) -> BodyDocument:
    """A stored 본문, from either on-disk cache. Both are gitignored fixtures."""
    for cache in (SPIKE_CACHE_DIR, DEFAULT_CACHE_DIR):
        if not cache.exists():
            continue
        try:
            blob = DartClient(cache_dir=cache, offline=True).get_document(rcept_no)
        except CacheMiss:
            continue
        return BodyDocument.from_bytes(blob, rcept_no=rcept_no)
    pytest.skip(f"{rcept_no} is in neither response cache (both are gitignored)")


def _ctx(rcept_no: str, **api) -> VersionContext:
    doc = _doc(rcept_no)
    return VersionContext(
        event=None,
        version=None,
        doc=doc,
        labels=extract_labels(doc),
        correction=parse_correction(doc),
        api=api,
    )


def _row(field_key: str, value, *, quote="근거", status="extracted", span="resolved") -> Extraction:
    return Extraction(
        field_key=field_key,
        status=status,
        value=value,
        quote=quote,
        span_status=span,
        span_verified=(span == "resolved"),
        schema_version="v1",
    )


def test_the_citation_gate_blocks_a_quote_that_is_not_in_the_document():
    """N37's one unresolved value (LB세미콘) must never reach a user, whatever it says."""
    ctx = _ctx("20260724000546")
    blocked = evaluate_field(
        _row("issue_price_formula", {"final_price_method": "MAX[...]"}, span="unresolved"), ctx
    )
    assert blocked.status == "failed" and blocked.reason_code == "span_unresolved"
    assert blocked.exposable is False
    # An absent field is not a failure — it is nothing to judge, and it is still
    # not shown. The two must stay distinguishable for the accuracy report (S9).
    assert evaluate_field(_row("warrant_trading_period", None, status="absent"), ctx).reason_code == (
        "field_absent"
    )


def test_gate_1_holds_the_window_and_only_the_document_can_say_추후결정():
    """계양전기: 배정기준일 07-28 < 매매 08-19~08-25 < 청약 09-03 (§7 #1)."""
    ctx = _ctx("20260724000546")
    assert ctx.record_date == date(2026, 7, 28) and ctx.first_subscription_date == date(2026, 9, 3)

    good = evaluate_field(
        _row("warrant_trading_period", {"start_date": "2026-08-19", "end_date": "2026-08-25"}), ctx
    )
    assert good.status == "passed"

    # Boundary: a 매매기간 that starts on the 배정기준일 is not after it.
    early = evaluate_field(
        _row("warrant_trading_period", {"start_date": "2026-07-28", "end_date": "2026-08-25"}), ctx
    )
    assert early.status == "failed" and early.reason_code == "not_after_record_date"

    reversed_ = evaluate_field(
        _row("warrant_trading_period", {"start_date": "2026-08-25", "end_date": "2026-08-19"}), ctx
    )
    assert reversed_.reason_code == "date_order"

    # Null dates are `tbd` only with the document's own word for it (N40) —
    # otherwise a missing schedule would silently render as "추후결정".
    null = {"start_date": None, "end_date": None}
    assert evaluate_field(_row("warrant_trading_period", null), ctx).reason_code == "dates_missing"
    suspended = evaluate_field(
        _row("warrant_trading_period", null, quote="3) 신주인수권증서 상장예정기간 : 추후결정"), ctx
    )
    assert suspended.status == "tbd" and suspended.exposable


def test_gate_2_3_4_5_agree_with_the_independent_witnesses():
    """One case per remaining ① gate: the reference is 본문, never the model."""
    ctx = _ctx("20260724000546")

    # #2 — 우리사주조합/구주주 must equal 본문 11.; the 일반공모 window follows it.
    entries = {
        "entries": [
            {"target": "우리사주조합", "agent": "KB", "start_date": "2026-09-03", "end_date": "2026-09-03"},
            {"target": "구주주", "agent": "KB", "start_date": "2026-09-03", "end_date": "2026-09-04"},
            {"target": "일반공모청약", "agent": "KB", "start_date": "2026-09-08", "end_date": "2026-09-09"},
        ]
    }
    assert evaluate_field(_row("subscription_agents", entries), ctx).status == "passed"
    moved = {"entries": [dict(entries["entries"][1], end_date="2026-09-07")]}
    assert evaluate_field(_row("subscription_agents", moved), ctx).reason_code == (
        "subscription_date_mismatch"
    )

    # #3 — §7's enum is the whole gate; 기타 is a failure, not a shrug.
    assert evaluate_field(_row("forfeited_share_method", {"method": "일반공모"}), ctx).status == "passed"
    assert evaluate_field(_row("forfeited_share_method", {"method": "기타"}), ctx).reason_code == (
        "method_not_enumerated"
    )

    # #4 — range, plus the unit slip a normalized ratio actually suffers.
    quote = "초과청약비율 : 배정 신주 1주당 0.2주"
    assert evaluate_field(
        _row("excess_subscription", {"allowed": True, "ratio": 0.2}, quote=quote), ctx
    ).status == "passed"
    assert evaluate_field(
        _row("excess_subscription", {"allowed": True, "ratio": 20}, quote=quote), ctx
    ).reason_code == "ratio_out_of_range"
    assert evaluate_field(
        _row("excess_subscription", {"allowed": True, "ratio": 0.5}, quote=quote), ctx
    ).reason_code == "ratio_quote_mismatch"

    # #5 — 확정발행가 공시일 sits in [본문 6. 확정예정일, 첫 청약일]; the prose
    # legitimately names the day *after* the label (measured on 3 filings).
    formula = {"final_price_method": "MAX[MIN(1차,2차), 기준주가의 60%]", "discount_rate": 0.2}
    assert evaluate_field(
        _row("issue_price_formula", dict(formula, final_price_date="2026-09-01")), ctx
    ).status == "passed"
    assert evaluate_field(
        _row("issue_price_formula", dict(formula, final_price_date="2026-09-15")), ctx
    ).reason_code == "final_price_date_out_of_window"
    assert evaluate_field(
        _row("issue_price_formula", dict(formula, discount_rate=25)), ctx
    ).reason_code == "discount_rate_out_of_range"


def test_gate_9_compares_against_the_api_row_and_refuses_to_guess():
    """③: 반대의사 기한 == API ``mgsc_mgop_rcpd_bgd/_edd`` (§7 #9)."""
    ctx = _ctx("20260724000546", mgsc_mgop_rcpd_bgd="2026년 09월 17일", mgsc_mgop_rcpd_edd="2026년 10월 16일")
    dissent = {"notice_start_date": "2026-09-17", "notice_end_date": "2026-10-16"}
    assert evaluate_field(_row("dissent_notice_procedure", dissent), ctx).status == "passed"
    assert evaluate_field(
        _row("dissent_notice_procedure", dict(dissent, notice_end_date="2026-10-17")), ctx
    ).reason_code == "dissent_period_mismatch"
    # No API reference → nothing was checked → not shown. Never a free pass.
    blank = _ctx("20260724000546", mgsc_mgop_rcpd_bgd="-", mgsc_mgop_rcpd_edd="-")
    verdict = evaluate_field(_row("dissent_notice_procedure", dissent), blank)
    assert verdict.status == "not_evaluable" and verdict.exposable is False


def test_the_withdrawal_detector_takes_the_real_rows_and_leaves_the_boilerplate():
    """썸에이지's real 정정사항 row, and the ③ text that a keyword test would eat."""
    withdrawn = [
        item
        for item in parse_correction(_doc("20260805000454")).items
        if is_withdrawal_row(item)
    ]
    assert len(withdrawn) == 1
    assert withdrawn[0].item.strip() == "유상증자 결정" and "철회" in withdrawn[0].after

    def item(name: str, before: str, after: str) -> CorrectionItem:
        return CorrectionItem(
            item=name, item_span=None, reason=None, reason_span=None,
            before=before, before_span=None, after=after, after_span=None,
        )

    # ③ generalises on shape alone (no case in today's corpus — untested there).
    assert is_withdrawal_row(item("회사합병 결정", "회사합병 결정", "회사합병 철회"))
    # 코퍼스코리아's shape: the 항목 is the bare 전 항목 and the subject is named.
    assert is_withdrawal_row(item("전 항목", "-", "유상증자 발행 결정 철회"))
    # The 매수청구 boilerplate every ③ filing carries — must never fire.
    assert not is_withdrawal_row(
        item("13. 주식매수청구권에 관한 사항", "가. " + "반대의사를 표시한 주주는 매수청구를 철회할 수 있습니다 " * 3,
             "나. " + "반대의사를 표시한 주주는 매수청구를 철회할 수 있습니다 " * 3)
    )
    # A *field* withdrawing is not the filing withdrawing.
    assert not is_withdrawal_row(item("기타", "-", "청약 철회"))


def test_the_exposure_contract_blocks_a_flagged_event_and_shows_only_gated_fields():
    """O-8's answer, executable: a ``warrant_conflict`` event is not exposed."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        ensure_corp(session, "01415892", corp_name="제이알글로벌리츠")
        event = ensure_event(
            session,
            corp_code="01415892",
            report_subtype="piicDecsn",
            original_rcept_dt="20260123",
            rights_type=RightsType.SUBSCRIPTION_WARRANT,
        )
        version = ensure_version(session, event, rcept_no="20260205000605")
        session.add(
            Snapshot(
                filing_version_id=version.id,
                source="document",
                payload_bytes=b"<DOCUMENT><BODY>x</BODY></DOCUMENT>",
                content_sha1="0" * 40,
            )
        )
        for key, gate, reason in (
            ("warrant_trading_period", "passed", None),
            ("issue_price_formula", "failed", "span_unresolved"),
            ("subscription_agents", "tbd", "schedule_tbd"),
        ):
            row = _row(key, {"start_date": "2026-03-02"})
            row.event_id, row.filing_version_id = event.id, version.id
            row.gate_status, row.gate_reason_code = gate, reason
            session.add(row)
        session.flush()

        clean = event_exposure(session, event)
        assert clean.state == "exposable"
        assert {f.field_key for f in clean.renderable_fields} == {
            "warrant_trading_period", "subscription_agents"
        }
        assert clean.fields["subscription_agents"].display == "추후결정"
        # A ``tbd`` field carries the notice, never the superseded value (N40).
        assert clean.fields["subscription_agents"].value is None
        assert clean.fields["issue_price_formula"].exposable is False

        # 본문 18. denies the 증서 that ic_mthn implies → the whole event is held
        # back, gated fields and all (O-8). Nothing is deleted.
        event.add_flag("warrant_conflict")
        conflicted = event_exposure(session, event)
        assert conflicted.state == "flagged" and conflicted.reason_code == "warrant_conflict"
        assert conflicted.renderable_fields == [] and len(conflicted.exposable_fields) == 2

        # 철회 outranks a conflict: the notice is the more specific truth.
        event.add_flag("withdrawn")
        withdrawn = event_exposure(session, event)
        assert withdrawn.state == "withdrawn"
        assert withdrawn.notice_ko == "이 유상증자는 철회되었습니다"


def test_every_displayed_number_is_deterministic_arithmetic():
    """§3.6: the AI reads and speaks; **계산은 결정론**. KST, floors, Decimal."""
    assert d_day(date(2026, 9, 7), date(2026, 9, 4)).label == "D-3"
    assert d_day(date(2026, 9, 7), date(2026, 9, 7)).label == "D-DAY"
    assert d_day(date(2026, 9, 7), date(2026, 9, 9)).label == "D+2"
    assert d_day(None) is None  # a `tbd` field has nothing to count to

    # 15:00 UTC is already tomorrow in Seoul — the countdown must not be a day off.
    from datetime import datetime, timezone

    assert today_kst(datetime(2026, 9, 6, 15, 0, tzinfo=timezone.utc)) == date(2026, 9, 7)

    # The window is inclusive at both ends: the last 청약일 is still a 청약일.
    assert window_state(date(2026, 9, 3), date(2026, 9, 4), date(2026, 9, 4)) == "open"
    assert window_state(date(2026, 9, 3), date(2026, 9, 4), date(2026, 9, 5)) == "closed"
    assert window_state(date(2026, 9, 3), date(2026, 9, 4), date(2026, 9, 2)) == "upcoming"

    # 단수주 절사, on the real 10-decimal ratio of 계양전기.
    assert allotted_shares(1_000, 0.2314082845) == 231
    assert excess_subscription_cap(231, 0.2) == 46
    # ₩ in Decimal, rounded once at the end (a float here is silently wrong).
    # 8,200,000 × 0.2314082845 × 1,250 = 2,371,934,916.125 → 2,371,934,916
    assert lapsed_warrant_value(8_200_000, 0.2314082845, 1_250) == Decimal("2371934916")
    assert lapsed_warrant_value(0, 0.5, 1_000) == Decimal(0)
