"""The read endpoints (P5.S3): what the board ranks, and what a page may say.

One tiny corpus in SQLite — no docker, no network, no model — carrying exactly the
cases the design's rules are about: an ① whose 발행가 is not fixed, an ② that
opened last month, an event with no date at all, and a 유상증자결정 whose
``rcept_no`` also sits under a suppressed twin (840 of them do in the real
corpus).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.db.models import (
    Base,
    CorrectionKind,
    Extraction,
    OfferingInput,
    PerformanceReport,
    RightsType,
    Snapshot,
)
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.web.app import create_app
from mijual.web.deps import get_session

#: 계양전기's real filing numbers; the ② row is 삼성제약's.
R1_RCEPT, R1_OLD, R2_RCEPT = "20260724000546", "20260611000483", "20250820000220"


def _extraction(event, version, key, value, *, gate="passed"):
    return Extraction(
        event_id=event.id,
        filing_version_id=version.id,
        rcept_no=version.rcept_no,
        field_key=key,
        status="extracted",
        value=value,
        quote="※ 원문 구절",
        span_start=10,
        span_end=20,
        span_status="resolved",
        gate_status=gate,
    )


def _corpus(session, *, today: date) -> None:
    ensure_corp(session, "00102618", corp_name="계양전기")
    ensure_corp(session, "00126414", corp_name="삼성제약")

    # ① — two versions, a stored 본문 on the newest, 발행가 아직 미확정.
    warrant = ensure_event(
        session,
        corp_code="00102618",
        report_subtype="piicDecsn",
        original_rcept_dt="20260508",
        rights_type=RightsType.SUBSCRIPTION_WARRANT,
    )
    warrant.exposure_state = "exposable"
    old = ensure_version(session, warrant, rcept_no=R1_OLD, rcept_dt=date(2026, 6, 11),
                         correction_kind=CorrectionKind.DISCLOSURE)
    new = ensure_version(session, warrant, rcept_no=R1_RCEPT, rcept_dt=date(2026, 7, 24),
                         correction_kind=CorrectionKind.DISCLOSURE)
    body = "<DOCUMENT><COMPANY-NAME>계양전기(주)</COMPANY-NAME></DOCUMENT>".encode()
    for version in (old, new):
        session.add(Snapshot(filing_version_id=version.id, source="document",
                             payload_bytes=body, content_sha1=version.rcept_no))
    session.add_all([
        _extraction(warrant, new, "warrant_trading_period",
                    {"start_date": str(today - timedelta(days=3)),
                     "end_date": str(today + timedelta(days=3))}),
        _extraction(warrant, new, "correction_interpretation",
                    {"field_moves": [{"field_key": "issue_price", "old": "4,985", "new": "3,200"}],
                     "interpretation": {"summary": "1차 발행가액 확정에 따라 조정되었습니다.",
                                        "schedule_impact": "일정 변동 없음", "changes": []}}),
        # The superseded version is gated too, and must never be read (N4).
        _extraction(warrant, old, "warrant_trading_period",
                    {"end_date": str(today + timedelta(days=90))}),
    ])
    session.add(OfferingInput(
        event_id=warrant.id,
        corp_code="00102618",
        decision_rcept_no=R1_RCEPT,
        price_confirmed=False,
        subscription_start=today + timedelta(days=12),
        subscription_end=today + timedelta(days=13),
        inputs={"rcept_no": R1_RCEPT, "planned_price": "3200", "discount_rate": "0.2",
                "allotment_ratio": "0.2314082845",
                "subscription": {"구주주": {"start": str(today + timedelta(days=12)),
                                          "end": str(today + timedelta(days=13))}}},
    ))

    # The pairing twin: same filing number, suppressed. Resolving must not open it.
    twin = ensure_event(
        session,
        corp_code="00102618",
        report_subtype="piicDecsn",
        original_rcept_dt="20260611",
        rights_type=RightsType.SUBSCRIPTION_WARRANT,
    )
    twin.suppressed_reason = "superseded_by_pairing"
    twin.exposure_state = "suppressed"
    ensure_version(session, twin, rcept_no=R1_RCEPT, rcept_dt=date(2026, 7, 24),
                   correction_kind=CorrectionKind.DISCLOSURE)

    # ② — 전환청구 opened a month ago: 진행 중, never 종료.
    overhang = ensure_event(
        session,
        corp_code="00126414",
        report_subtype="cvbdIsDecsn",
        original_rcept_dt="20250820",
        rights_type=RightsType.CONVERTIBLE_OVERHANG,
    )
    overhang.exposure_state = "exposable"
    cb_version = ensure_version(session, overhang, rcept_no=R2_RCEPT, rcept_dt=date(2025, 8, 20))
    session.add(Snapshot(
        filing_version_id=cb_version.id,
        source="cvbdIsDecsn",
        payload_json={"rcept_no": R2_RCEPT, "cv_prc": "1,591",
                      "cvrqpd_bgd": str(today - timedelta(days=30)),
                      "cvrqpd_edd": str(today + timedelta(days=1000)),
                      "cvisstk_cnt": "16,907,605", "cvisstk_tisstk_vs": "15.22",
                      "bd_fta": "26,900,000,000", "bdis_mthn": "사모",
                      "bd_mtd": str(today + timedelta(days=1000))},
        content_sha1="cb",
    ))

    # One closed offering, so the headline has something to add up.
    session.add(PerformanceReport(
        event_id=None, corp_code="00162461", corp_name="한화솔루션",
        rcept_no="20260730000366", parse_status="parsed",
        facts={"warrants_issued": {"value": "42165422", "raw": "42,165,422", "span": [1, 2]}},
        lapse={"status": "valued", "lapsed": 3734925, "warrants_issued": 42165422,
               "confirmed_price": "22100", "value_krw": "20635460625",
               "value_floor_krw": "16554561031"},
    ))
    # 기준시각: the corpus was last observed three days ago, so the board is
    # stale and must say so — and must still serve every row.
    session.flush()
    stamp = datetime.now(timezone.utc) - timedelta(days=3)
    for event in (warrant, twin, overhang):
        event.last_seen_at = stamp
    session.flush()


@pytest.fixture()
def client():
    today = datetime.now(timezone(timedelta(hours=9))).date()
    # One shared in-memory connection: TestClient serves on a worker thread.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    _corpus(session, today=today)

    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as test_client:
        test_client.today = today  # type: ignore[attr-defined]
        yield test_client
    session.close()


def test_the_board_ranks_by_dday_and_pins_what_does_not_rank(client) -> None:
    body = client.get("/board").json()
    assert body["counts"] == {"all": 2, "R1": 1, "R2": 1}
    # Only the ① is ahead of us; the ② opened a month ago and lives in its strip,
    # labelled by its window state and never as 종료.
    assert [row["corp_name"] for row in body["rows"]] == ["계양전기"]
    assert body["open_now"]["count"] == 1
    opened = body["open_now"]["rows"][0]["countdown"]
    assert opened["window_state"] == "open" and opened["dday"].startswith("D+")
    assert body["tbd"] == {"count": 0, "total": 0, "rows": []}
    assert body["freshness"]["stale_after_hours"] == 18

    row = body["rows"][0]
    assert row["rcept_no"] == R1_RCEPT  # the current readable version, not the old one
    assert row["countdown"]["date"] == str(client.today + timedelta(days=3))
    # ①'s extras: the 청약 window and the 발행가 확정 전 state — and no money.
    assert row["offering"]["price_confirmed"] is False
    assert not [key for key in row["offering"] if "value" in key]
    assert "fields" not in row  # a board row renders no field values


def test_the_summary_is_one_object_with_the_headline_and_its_freshness(client) -> None:
    body = client.get("/board/summary").json()
    assert body["watching"] == 2 and body["by_rights"] == {"R1": 1, "R2": 1}
    assert body["open_now"] == 1 and body["performance_reports"] == 1
    assert body["lapsed_value"] == {"value": "20635460625", "estimated": True}
    assert body["lapsed_warrants"]["estimated"] is False  # a cited count is a fact
    assert body["lapse_pending"] == 1  # the ① whose 청약 has not closed
    # 동시 마감 (R9 §6): one offering pending, so the strip names it rather than
    # counting — the tie count is that same list's head-date population.
    assert body["next_lapse"]["tie_count"] == 1
    # The countdown ticks to the end of the 청약 day, as an absolute KST instant.
    assert body["next_lapse"]["target"] == f"{client.today + timedelta(days=14)}T00:00:00+09:00"
    fresh = body["freshness"]
    assert fresh["stale"] is True and fresh["age_hours"] >= 71  # floored, and stale


def test_a_detail_page_reads_todays_version_and_a_blocked_event_is_a_404(client) -> None:
    body = client.get(f"/events/{R1_RCEPT}").json()
    # The filing number sits under a suppressed twin too; the renderable one wins.
    assert body["state"] == "exposable" and body["corp_name"] == "계양전기"
    assert body["countdown"]["date"] == str(client.today + timedelta(days=3))
    assert set(body["fields"]) == {"warrant_trading_period", "correction_interpretation"}
    assert body["corrections"]["summary"].startswith("1차 발행가액")
    assert body["offering"]["price_confirmed"] is False

    # An old filing number still resolves — and still renders today's reading.
    assert client.get(f"/events/{R1_OLD}").json()["rcept_no"] == R1_RCEPT
    missing = client.get("/events/99999999999999")
    assert missing.status_code == 404 and missing.json()["error"]["code"] == "not_found"
    assert "message_ko" not in missing.json()["error"]  # no Korean is invented


def test_the_version_rail_marks_exactly_the_version_being_read(client) -> None:
    body = client.get(f"/events/{R1_RCEPT}/corrections").json()
    assert [v["rcept_no"] for v in body["versions"]] == [R1_OLD, R1_RCEPT]
    assert [v["is_current_readable"] for v in body["versions"]] == [False, True]
    assert body["interpretation"]["schedule_impact"] == "일정 변동 없음"  # verbatim
    assert body["field_moves"][0]["new"] == "3,200"


def test_the_convertible_strip_is_the_six_api_facts_and_nothing_derived(client) -> None:
    body = client.get(f"/events/{R2_RCEPT}").json()
    strip = body["convertible"]
    assert strip["conversion_price"]["value"] == "1591"
    assert strip["shares"]["value"] == 16907605 and strip["issue_method"] == "사모"
    assert all(not fig["estimated"] for fig in (strip["conversion_price"], strip["shares"]))
    assert body["fields"] == {}  # a sparse ② renders from the API row alone
