"""The presentation contract's invariants (P5.S2).

Not a coverage sweep: one case per rule the contract exists to make impossible to
break. No database, no network, no fixtures — every input is a dataclass built
right here, which is the point of a derivation layer that takes loaded rows.
"""

from __future__ import annotations

import ast
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from mijual.cb import ConvertibleFacts
from mijual.estimate import EventInputs, LapseRow
from mijual.extract.fields import FIELDS
from mijual.extract.labelfields import LABEL_SPECS
from mijual.gates.exposure import EventExposure, FieldView
from mijual.present import (
    COUNTDOWN_LABELS_KO,
    FIELD_NAMES_KO,
    Figure,
    OfferingInputs,
    board_summary,
    countdown_of,
    event_view,
    field_payloads,
    freshness,
    identity_of,
    instant,
    issuer_disagreement,
    lapse_result,
    lapse_totals,
    offering_inputs,
)
from mijual.web import clock

PRESENT_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "mijual" / "present"
SPENDING = ("mijual.dart", "mijual.collect", "mijual.extract")
TODAY = date(2026, 8, 20)


def _field(key: str, value: object = None, *, status: str = "passed") -> FieldView:
    exposable = status in ("passed", "tbd")
    return FieldView(
        field_key=key,
        gate_status=status,
        reason_code=None if exposable else "span_unresolved",
        exposable=exposable,
        display=("추후결정" if status == "tbd" else ("value" if exposable else None)),
        value=value if status == "passed" else None,
        quote="※ 원문 구절" if exposable else None,
        span=(10, 20) if exposable else None,
        rcept_no="20260724000546",
    )


def _exposure(*, rights: str = "R1", state: str = "exposable", fields=(), corp_name="계양전기"):
    return EventExposure(
        event_id=3,
        corp_code="00102618",
        corp_name=corp_name,
        rights_type=rights,
        original_rcept_dt=date(2026, 5, 8),
        rcept_no="20260724000546",
        state=state,
        reason_code=None if state == "exposable" else state,
        fields={view.field_key: view for view in fields},
    )


# ---------------------------------------------------------------------------
# the countdown: one anchor per rights type, and 지남 is not one thing
# ---------------------------------------------------------------------------
def test_each_rights_type_counts_down_to_its_own_governing_date() -> None:
    warrant = _exposure(
        fields=[_field("warrant_trading_period", {"start_date": "2026-08-19",
                                                  "end_date": "2026-08-25"})]
    )
    one = countdown_of(warrant, today=TODAY)
    assert (one.label_ko, one.date, one.dday, one.window_state) == (
        "신주인수권증서 매매 마감", "2026-08-25", "D-5", "open"
    )
    assert one.reference == "2026-08-20"  # the KST day the server used, carried along

    dissent = _exposure(
        rights="R3",
        fields=[_field("dissent_notice_procedure", {"notice_start_date": "2026-08-13",
                                                    "notice_end_date": "2026-08-27"})],
    )
    three = countdown_of(dissent, today=TODAY)
    assert (three.label_ko, three.date, three.dday) == ("반대의사 통지 마감", "2026-08-27", "D-7")


def test_a_past_conversion_opening_is_open_not_closed() -> None:
    """ui-traps #5: ②'s 개시일 behind us means the dilution is live *right now*."""
    facts = ConvertibleFacts(
        rcept_no="20250820000220",
        request_begin=date(2026, 6, 1),
        request_end=date(2029, 6, 1),
    )
    two = countdown_of(_exposure(rights="R2"), facts=facts, today=TODAY)
    assert two.label_ko == "전환청구 개시"
    assert two.dday == "D+80" and two.is_past  # the anchor is behind us …
    assert two.is_open and two.window_state == "open"  # … and the window is open
    # The layer never writes the Korean for "past": 종료 vs 진행 중 is per type,
    # so it ships machine tokens and the surface writes the signed copy.
    assert "종료" not in str(two.payload())
    with pytest.raises(ValueError):  # a forgotten 상세 row is a caller bug, not a blank row
        countdown_of(_exposure(rights="R2"), today=TODAY)


def test_a_withdrawn_event_has_no_countdown_and_no_fields() -> None:
    withdrawn = _exposure(state="withdrawn", fields=[_field("warrant_trading_period",
                                                            {"end_date": "2026-08-25"})])
    view = event_view(withdrawn, today=TODAY)
    assert view.countdown.date is None and view.countdown.dday is None
    assert view.fields == {}
    assert view.notice_ko == "이 유상증자는 철회되었습니다"  # the locked notice, per type
    assert view.renderable  # 철회 *is* a surface — it replaces the card body


# ---------------------------------------------------------------------------
# fields: blocked is absent, 추후결정 has no date, nothing is an estimate
# ---------------------------------------------------------------------------
def test_a_blocked_field_is_absent_and_a_tbd_field_carries_no_date() -> None:
    exposure = _exposure(
        fields=[
            _field("excess_subscription", {"ratio": 0.2}),
            _field("issue_price_formula", status="failed"),
            _field("warrant_trading_period", status="tbd"),
        ]
    )
    payloads = field_payloads(exposure)
    assert set(payloads) == {"excess_subscription", "warrant_trading_period"}
    assert "issue_price_formula" not in event_view(exposure, today=TODAY).payload()["fields"]

    tbd = payloads["warrant_trading_period"].payload()
    assert tbd["display"] == "추후결정" and "value" not in tbd
    assert payloads["excess_subscription"].korean_name == "초과청약 조건 (비율)"
    assert all(p.payload()["estimated"] is False for p in payloads.values())

    with pytest.raises(ValueError):  # a date beside 추후결정 cannot be constructed
        type(payloads["warrant_trading_period"])(
            field_key="warrant_trading_period",
            korean_name=None,
            display="추후결정",
            value={"end_date": "2026-08-25"},
            estimated=False,
        )


def test_the_display_name_states_a_disagreement_but_ignores_the_legal_form() -> None:
    trap = identity_of(_exposure(corp_name="풍전약품"), "에스씨엠생명과학 주식회사")
    assert trap.corp_name == "풍전약품"  # the master name is what a card shows
    assert trap.corp_name_agrees_with_body is False
    ordinary = identity_of(_exposure(corp_name="한화솔루션"), "한화솔루션(주)")
    assert ordinary.corp_name_agrees_with_body is True
    assert identity_of(_exposure()).payload() == {"corp_name": "계양전기"}


# ---------------------------------------------------------------------------
# money: none of it before 확정발행가, and every derived won is 「추정」
# ---------------------------------------------------------------------------
def test_no_money_number_exists_before_the_price_is_confirmed() -> None:
    """계양전기 today: 예정발행가 only, so no 증서 가치 and no won amount anywhere."""
    exposure = _exposure(fields=[_field("issue_price_formula",
                                        {"final_price_date": "2026-08-28"})])
    inputs = EventInputs(
        rcept_no="20260724000546",
        planned_price=3200.0,
        discount_rate=0.2,
        allotment_ratio=0.2314082845,
    )
    offering = offering_inputs(exposure, inputs)
    assert offering.price_confirmed is False
    assert offering.unit_value is None and offering.unit_value_floor is None
    payload = offering.payload()
    assert not {"confirmed_price", "unit_value", "unit_value_floor"} & set(payload)
    # Share counts and the schedule still render; the 배정비율 keeps every digit.
    assert payload["allotment_ratio"] == {"value": "0.2314082845", "estimated": False,
                                          "rcept_no": "20260724000546"}
    assert payload["final_price_date"] == "2026-08-28"

    with pytest.raises(ValueError):  # the invariant is structural, not a habit
        OfferingInputs(confirmed_price=None, unit_value=Figure.estimate("5525"))


def test_a_confirmed_price_is_a_fact_and_everything_derived_from_it_is_tagged() -> None:
    """한솔테크닉스: 확정 6,580원 · 할인율 20% → 「추정」 증서 1주 1,645원."""
    exposure = _exposure(fields=[_field("issue_price_formula", {"discount_rate": 0.2})])
    inputs = EventInputs(
        rcept_no="20260709000212",
        confirmed_price=6580.0,
        price_span=(100, 120),
        discount_rate=0.2,
        allotment_ratio=0.2444331297,
    )
    payload = offering_inputs(exposure, inputs).payload()
    assert payload["confirmed_price"] == {"value": "6580", "estimated": False,
                                          "span": [100, 120], "rcept_no": "20260709000212"}
    assert payload["unit_value"]["value"] == "1645"
    assert payload["unit_value"]["estimated"] is True
    assert payload["unit_value_floor"]["value"].startswith("1321.8870188682")
    # 할인율 is a fact, and it cites the gate-passing field it was read from.
    assert payload["discount_rate"]["estimated"] is False
    assert payload["discount_rate"]["quote"] == "※ 원문 구절"
    with pytest.raises(ValueError):  # no filing states a derived number
        Figure(value="1645", estimated=True, quote="증서 1주 이론가치는 1,645원입니다")


def test_a_lapse_reads_the_same_from_a_report_row_and_from_its_stored_json() -> None:
    row = LapseRow(
        corp_code="00157399",
        corp_name="한솔테크닉스",
        status="valued",
        decision_rcept_no="20260709000212",
        performance_rcept_no="20260722000448",
        subscription_end=date(2026, 7, 14),
        warrants_issued=9920295,
        warrants_exercised=9156211,
        lapsed=764084,
        lapse_rate=Decimal("0.0770"),
        confirmed_price=Decimal("6580"),
        discount_rate=0.2,
        allotment_ratio=0.2444331297,
        unit_value=Decimal("1645"),
        value=Decimal("1256918180"),
    )
    result = lapse_result(row)
    payload = result.payload()
    # 소멸 주수 and 소멸률 are cited counts, never estimates; the won amount is.
    assert payload["lapsed"] == {"value": 764084, "estimated": False,
                                 "rcept_no": "20260722000448"}
    assert payload["lapse_rate"]["estimated"] is False
    assert payload["value"] == {"value": "1256918180", "estimated": True}
    assert lapse_result(row.as_json()).payload() == payload


def test_two_readings_of_the_same_실권주_stay_two_readings() -> None:
    """대한광통신: the issuer's own cell disagrees with the issuer's own Ⅶ table."""
    facts = {
        "rcept_no": "20260306000600",
        "warrants_issued": {"value": "23465365", "raw": "23,465,365", "span": [1, 2],
                            "label": "신주인수권증서 발행 계"},
        "warrants_exercised": {"value": "21382063", "raw": "21,382,063", "span": [3, 4],
                               "label": "신주인수권증서 청약"},
        "lapse_stated": {"value": "2117937", "raw": "2,117,937", "span": [5, 6],
                         "label": "신주인수권증서 청약 실권주"},
        "lapse_derived": 2083302,
    }
    clash = issuer_disagreement(facts)
    assert clash is not None and clash.label_ko == "발행사 기재 불일치"
    payload = clash.payload()
    assert "value" not in payload  # nothing reconciled, averaged or picked silently
    stated, derived = payload["readings"]
    assert (stated["value"], stated["used"]) == (2117937, False)
    assert stated["quote"] == "2,117,937" and stated["span"] == [5, 6]
    assert (derived["value"], derived["used"]) == (2083302, True)
    assert [c["quote"] for c in derived["inputs"]] == ["23,465,365", "21,382,063"]
    assert issuer_disagreement({**facts, "lapse_derived": 2117937}) is None


# ---------------------------------------------------------------------------
# the summary: one shape, so two cards cannot disagree
# ---------------------------------------------------------------------------
def test_one_summary_counts_the_board_and_tags_the_headline() -> None:
    urgent = event_view(
        _exposure(fields=[_field("warrant_trading_period", {"start_date": "2026-08-19",
                                                            "end_date": "2026-08-25"})]),
        today=TODAY,
    )
    distant = event_view(
        _exposure(fields=[_field("warrant_trading_period", {"end_date": "2026-12-25"})]),
        today=TODAY,
    )
    live_cb = event_view(
        _exposure(rights="R2"),
        facts=ConvertibleFacts(request_begin=date(2026, 6, 1), request_end=date(2029, 6, 1)),
        today=TODAY,
    )
    no_date = event_view(_exposure(rights="R3"), today=TODAY)

    summary = board_summary(
        [urgent, distant, live_cb, no_date],
        as_of=datetime(2026, 8, 20, 9, 30, tzinfo=timezone.utc),
        performance_reports=69,
        lapse_pending=15,
        lapsed_value=Decimal("71812971649"),
        lapsed_value_floor=Decimal("54870000000"),
        lapsed_warrants=51253956,
        next_lapse_date=date(2026, 9, 4),
        next_lapse_corp_name="계양전기",
    )
    payload = summary.payload()
    assert payload["watching"] == 4 and payload["by_rights"] == {"R1": 2, "R2": 1, "R3": 1}
    assert payload["within_30d"] == 1  # 0 <= days <= 30, inclusive
    assert payload["open_now"] == 1  # the already-open ②, never counted as 종료
    assert payload["tbd"] == 1  # exposable, watched, no countdown date at all
    assert payload["lapse_pending"] == 15 and payload["performance_reports"] == 69
    assert payload["lapsed_value"] == {"value": "71812971649", "estimated": True}
    assert payload["lapsed_warrants"]["estimated"] is False
    assert payload["as_of"] == "2026-08-20T18:30:00+09:00"  # absolute KST, always
    assert payload["next_lapse"] == {"date": "2026-09-04", "corp_name": "계양전기"}
    assert summary.countdown_target is None  # the 마감 instant is not assumed


def test_the_board_says_how_old_it_is_rather_than_going_dark() -> None:
    """Freshness is a served fact, never a client-side clock diff (P5.S3)."""
    as_of = datetime(2026, 8, 20, 5, 2, tzinfo=timezone(timedelta(hours=9)))
    fresh = freshness(as_of, now=as_of + timedelta(hours=11, minutes=59))
    stale = freshness(as_of, now=as_of + timedelta(hours=44))
    assert fresh.stale is False and fresh.age_hours == 11  # a healthy 12h beat gap
    assert stale.stale is True and stale.age_hours == 44  # floored, never rounded up
    assert stale.payload()["as_of"] == "2026-08-20T05:02:00+09:00"
    assert freshness(None, now=as_of).stale is True  # an unknown 기준시각 is stale


def test_the_totals_add_up_and_a_cell_that_does_not_state_the_number_is_not_cited() -> None:
    """D4's shape, live in 4 of 32 reports: 청약 is a sum, its cell is one addend."""
    rows = [
        {"status": "valued", "lapsed": 3734925, "warrants_issued": 42165422,
         "confirmed_price": "22100", "value_krw": "20635460625",
         "value_floor_krw": "16554561031"},
        {"status": "counted_only", "lapsed": 2080336, "warrants_issued": 11955000},
    ]
    totals = lapse_totals(rows)
    assert totals.lapsed == 5815261 and totals.issued == 54120422  # counted, valued or not
    assert totals.value == Decimal("20635460625") and totals.valued == 1

    facts = {
        "warrants_issued": {"value": "42165422", "raw": "42,165,422", "span": [1, 2]},
        "warrants_exercised": {"value": "38430497", "raw": "38,427,609", "span": [3, 4]},
    }
    result = lapse_result(rows[0] | {"warrants_exercised": 38430497}, facts=facts).payload()
    assert result["warrants_issued"]["quote"] == "42,165,422"
    # The 청약 cell states one of the two rows that were summed — no false chip.
    exercised = result["warrants_exercised"]
    assert exercised["value"] == 38430497
    assert "quote" not in exercised and "span" not in exercised


def test_offering_inputs_read_the_same_from_an_object_and_from_its_stored_json() -> None:
    """The worker writes ``as_json``; the request path reads it. One shape, both ways."""
    inputs = EventInputs(
        rcept_no="20260720000067",
        confirmed_price=22100,
        discount_rate=0.2,
        allotment_ratio=0.2314082845,
        new_shares=8200000,
        record_date=date(2026, 7, 28),
        subscription={"구주주": {"start": date(2026, 9, 3), "end": date(2026, 9, 4)}},
    )
    exposure = _exposure(fields=[_field("issue_price_formula", {"discount_rate": 0.2})])
    live = offering_inputs(exposure, inputs).payload()
    stored = offering_inputs(exposure, inputs.as_json()).payload()
    assert live == stored
    assert stored["allotment_ratio"]["value"] == "0.2314082845"  # all ten decimals
    assert stored["unit_value"]["estimated"] is True  # 「추정」, both ways


# ---------------------------------------------------------------------------
# the two things this layer copies rather than imports, pinned to their source
# ---------------------------------------------------------------------------
def test_nothing_korean_here_has_drifted_from_the_code_that_owns_it() -> None:
    assert FIELD_NAMES_KO == {
        key: spec.name for key, spec in {**FIELDS, **LABEL_SPECS}.items()
    }
    assert set(COUNTDOWN_LABELS_KO) == {"R1", "R2", "R3"}


def test_an_instant_serializes_exactly_as_the_web_clock_would() -> None:
    moment = datetime(2026, 8, 20, 9, 30, 15, 123456, tzinfo=timezone.utc)
    assert instant(moment) == clock.iso(moment) == "2026-08-20T18:30:15+09:00"
    assert instant(None) is None


def test_the_derivation_layer_imports_no_module_that_spends() -> None:
    """`present` is on a request path: the `architecture` boundary applies here too."""
    offenders = []
    for path in sorted(PRESENT_PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        guarded = {
            node
            for branch in ast.walk(tree)
            if isinstance(branch, ast.If) and "TYPE_CHECKING" in ast.dump(branch.test)
            for node in ast.walk(branch)
        }
        for node in ast.walk(tree):
            if node in guarded:
                continue  # type-only imports never execute
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            offenders += [
                f"{path.name}: {name}"
                for name in names
                if any(name == m or name.startswith(m + ".") for m in SPENDING)
            ]
    assert not offenders, f"no OpenDART/LLM module in the derivation layer: {offenders}"
