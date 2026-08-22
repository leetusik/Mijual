"""내 종목 조회 (P5.S4): what resolves, what ranks, and what a stock's 2026 cost it.

The same DB-free pattern as ``test_web_board.py`` — in-memory SQLite, a
``get_session`` override, no docker and no network — over a corpus cut to the
rules R4 states as prohibitions: a live ① with no 확정발행가 (share counts, never
money), an ② whose window opened last month, an offering that lapsed inside 2026
beside one that lapsed in 2025 (outside coverage: **unstated, never 0**), and a
listed company with no rights at all.
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
    Extraction,
    OfferingInput,
    PerformanceReport,
    RightsType,
    Snapshot,
)
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.web.app import create_app
from mijual.web.deps import get_session

KEYANG, SENERGY, QUIET = "00102618", "00585538", "00999999"


def _warrant(session, *, corp_code, subtype_day, start, end, inputs, price_confirmed):
    event = ensure_event(
        session,
        corp_code=corp_code,
        report_subtype="piicDecsn",
        original_rcept_dt=subtype_day,
        rights_type=RightsType.SUBSCRIPTION_WARRANT,
    )
    event.exposure_state = "exposable"
    version = ensure_version(session, event, rcept_no=f"2026{subtype_day[4:]}000100",
                             rcept_dt=date(2026, 1, 1))
    session.add(Snapshot(filing_version_id=version.id, source="document",
                         payload_bytes=b"<DOCUMENT/>", content_sha1=version.rcept_no))
    session.add(Extraction(
        event_id=event.id, filing_version_id=version.id, rcept_no=version.rcept_no,
        field_key="warrant_trading_period", status="extracted",
        value={"start_date": str(start), "end_date": str(end)},
        quote="신주인수권증서의 상장·매매기간", span_start=10, span_end=30,
        span_status="resolved", gate_status="passed",
    ))
    session.add(OfferingInput(
        event_id=event.id, corp_code=corp_code, decision_rcept_no=version.rcept_no,
        price_confirmed=price_confirmed,
        subscription_start=end + timedelta(days=7), subscription_end=end + timedelta(days=8),
        inputs=inputs,
    ))
    return event


def _corpus(session, *, today: date) -> None:
    ensure_corp(session, KEYANG, corp_name="계양전기", stock_code="012200")
    ensure_corp(session, SENERGY, corp_name="에스에너지", stock_code="095910")
    ensure_corp(session, QUIET, corp_name="조용한기업", stock_code="999999")

    # Name-only issuers for the suggestion list (P7.S4). They carry no events on
    # purpose — a suggestion is about who exists, not about what is happening to
    # them. Nine 삼성* rows so the cap of eight has something to cut, and a 하이
    # family where the query lands at the front of two names and inside a third.
    for index, name in enumerate([
        "삼성전자", "삼성전기", "삼성물산", "삼성화재", "삼성증권", "삼성카드",
        "삼성중공업", "삼성생명", "삼성바이오로직스",
        "하이록코리아", "하이스틸", "SK하이닉스",
    ]):
        ensure_corp(session, f"0090{index:04d}", corp_name=name, stock_code=f"0059{index:02d}")

    # ① live: 매매기간 closes in three days and the 발행가 is not fixed yet.
    _warrant(
        session, corp_code=KEYANG, subtype_day="20260508",
        start=today - timedelta(days=3), end=today + timedelta(days=3),
        price_confirmed=False,
        inputs={"rcept_no": "20260508000100", "planned_price": "3200",
                "allotment_ratio": "0.2314082845"},
    )
    # ② live: 전환청구 opened a month ago — 진행 중, and it ranks below the ①.
    overhang = ensure_event(
        session, corp_code=KEYANG, report_subtype="cvbdIsDecsn",
        original_rcept_dt="20250820", rights_type=RightsType.CONVERTIBLE_OVERHANG,
    )
    overhang.exposure_state = "exposable"
    cb = ensure_version(session, overhang, rcept_no="20250820000220", rcept_dt=date(2025, 8, 20))
    session.add(Snapshot(
        filing_version_id=cb.id, source="cvbdIsDecsn", content_sha1="cb",
        payload_json={"rcept_no": "20250820000220", "cv_prc": "1,591",
                      "cvrqpd_bgd": str(today - timedelta(days=30)),
                      "cvrqpd_edd": str(today + timedelta(days=900)),
                      "cvisstk_cnt": "16,907,605", "cvisstk_tisstk_vs": "15.22",
                      "bd_fta": "26,900,000,000", "bdis_mthn": "사모",
                      "bd_mtd": str(today + timedelta(days=900))},
    ))

    # ① lapsed inside coverage: 매매기간 closed, 청약 결과 filed and valued.
    lapsed = _warrant(
        session, corp_code=SENERGY, subtype_day="20260227",
        start=date(2026, 2, 20), end=date(2026, 2, 26),
        price_confirmed=True,
        inputs={"rcept_no": "20260227000100", "confirmed_price": "848",
                "discount_rate": "0.3", "allotment_ratio": "0.4521000000"},
    )
    session.add(PerformanceReport(
        event_id=lapsed.id, corp_code=SENERGY, corp_name="에스에너지",
        rcept_no="20260312000380", rcept_dt=date(2026, 3, 12), parse_status="parsed",
        facts={"warrants_issued": {"value": "14000000", "raw": "14,000,000", "span": [1, 2]}},
        lapse={"status": "valued", "subscription_end": "2026-03-05", "lapsed": 1990157,
               "warrants_issued": 14000000, "warrants_exercised": 12009843,
               "lapse_rate": "0.1422", "confirmed_price": "848", "unit_value": "363",
               "value_krw": "722627000", "value_floor_krw": "600000000"},
    ))
    # A second 2026 offering with **no 확정발행가**: shares lapsed, worth unstated.
    session.add(PerformanceReport(
        event_id=None, corp_code=SENERGY, corp_name="에스에너지",
        rcept_no="20260811000597", rcept_dt=date(2026, 8, 11), parse_status="parsed",
        lapse={"status": "counted_only", "subscription_end": "2026-08-04",
               "lapsed": 2080336, "warrants_issued": 12000000, "confirmed_price": None},
    ))
    # 2025: outside the fixed coverage boundary. Not a row, and not a zero.
    session.add(PerformanceReport(
        event_id=None, corp_code=SENERGY, corp_name="에스에너지",
        rcept_no="20251220000111", rcept_dt=date(2025, 12, 20), parse_status="parsed",
        lapse={"status": "valued", "subscription_end": "2025-12-15", "lapsed": 999999,
               "warrants_issued": 9000000, "confirmed_price": "1000",
               "value_krw": "111111111"},
    ))
    session.flush()


@pytest.fixture()
def client():
    today = datetime.now(timezone(timedelta(hours=9))).date()
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


def test_a_stock_resolves_by_name_or_code_and_a_miss_is_a_result_not_an_error(client) -> None:
    by_name = client.get("/stocks", params={"q": "계양전기"}).json()
    assert by_name["found"] is True and by_name["stock"]["corp_code"] == "00102618"
    assert client.get("/stocks", params={"q": "012200"}).json()["stock"]["stock_code"] == "012200"
    # Legal form and spacing are not a different company; a unique prefix is not a guess.
    assert client.get("/stocks", params={"q": "계양 전기(주)"}).json()["found"] is True
    assert client.get("/stocks", params={"q": "계양"}).json()["found"] is True

    miss = client.get("/stocks", params={"q": "없는종목"})
    assert miss.status_code == 200
    assert miss.json() == {"query": "없는종목", "found": False}  # no reason, no Korean


def test_live_rights_rank_a_closing_deadline_above_an_open_window(client) -> None:
    rows = client.get("/stocks", params={"q": "계양전기"}).json()["rights"]["rows"]
    assert [row["rights_type"] for row in rows] == ["R1", "R2"]

    warrant, overhang = rows
    assert warrant["countdown"]["date"] == str(client.today + timedelta(days=3))
    # 발행가 확정 전: the factors are there, and not one won amount.
    assert warrant["offering"]["price_confirmed"] is False
    assert warrant["offering"]["allotment_ratio"]["value"] == "0.2314082845"  # ten decimals
    assert not [key for key in warrant["offering"] if "value" in key]
    # A past ② opening is 진행 중, never 종료 — and the row carries its dilution.
    assert overhang["countdown"]["window_state"] == "open"
    assert overhang["countdown"]["dday"].startswith("D+")
    assert overhang["convertible"]["overhang_pct"]["value"] == "15.22"


def test_the_breakdown_covers_2026_only_and_states_no_money_without_a_price(client) -> None:
    body = client.get("/stocks", params={"q": "095910"}).json()
    lapse = body["lapse"]
    assert lapse["coverage"] == {"start": "2026-01-01", "end": str(client.today),
                                 "convertible_start": "2025-06-01"}
    # Two 2026 offerings; the 2025 one is outside coverage and is not counted at all.
    assert lapse["totals"]["offerings"] == 2 and lapse["totals"]["valued"] == 1
    assert lapse["totals"]["lapsed"] == {"value": 4070493, "estimated": False}
    assert lapse["totals"]["value"] == {"value": "722627000", "estimated": True}
    assert [row["lapse"]["subscription_end"] for row in lapse["rows"]] == [
        "2026-08-04", "2026-03-05"  # most recent 청약 종료 first
    ]

    unpriced, valued = lapse["rows"]
    assert unpriced["lapse"]["lapsed"]["value"] == 2080336  # the shares still lapsed
    assert not [key for key in unpriced["lapse"] if "value" in key or "price" in key]
    assert valued["lapse"]["value"]["estimated"] is True
    assert valued["countdown"]["dday"].startswith("D+")  # 기간 지남, computed upstream
    assert valued["warrant_trading_period"]["quote"] == "신주인수권증서의 상장·매매기간"
    assert "pending" not in lapse  # every 청약 of this stock has closed


def test_a_stock_with_nothing_to_show_is_a_page_and_an_unknown_code_is_a_404(client) -> None:
    body = client.get("/stocks", params={"q": "조용한기업"}).json()
    assert body["found"] is True and body["rights"] == {"count": 0, "rows": []}
    assert body["lapse"]["totals"] == {"offerings": 0, "valued": 0}  # no figures, no zeros

    # 계양전기's ① 청약 is still ahead: the 소멸 여부 is not yet a fact.
    pending = client.get(f"/stocks/{KEYANG}").json()["lapse"]["pending"]
    assert pending == {"count": 1, "subscription_end": str(client.today + timedelta(days=11))}

    missing = client.get("/stocks/00000000")
    assert missing.status_code == 404 and missing.json()["error"]["code"] == "not_found"
    assert "message_ko" not in missing.json()["error"]


def test_suggest_offers_candidates_a_reader_chooses_and_still_never_resolves_one(client) -> None:
    def names(query: str) -> list[str]:
        body = client.get("/stocks/suggest", params={"q": query}).json()
        assert body["query"] == query
        return [candidate["corp_name"] for candidate in body["candidates"]]

    # Declared before /stocks/{corp_code}, or "suggest" would be read as a code.
    hit = client.get("/stocks/suggest", params={"q": "계양"})
    assert hit.status_code == 200
    assert hit.json()["candidates"][0] == {
        "corp_code": KEYANG, "corp_name": "계양전기", "stock_code": "012200"
    }

    assert names("012") == ["계양전기"]  # 종목코드 prefix
    assert names("12200") == ["계양전기"]  # zero-padded, the way resolve_corp reads a ticker
    assert names("삼성전") == ["삼성전기", "삼성전자"]  # the prefix resolve_corp declines
    assert names("하이") == ["하이록코리아", "하이스틸", "SK하이닉스"]  # prefix, then substring
    assert len(names("삼성")) == 8  # capped — a shortlist, not the corpus
    assert names("없는종목") == []  # a result, not a 404

    # Offering the choice does not make the resolver guess: 삼성전 still resolves
    # to neither company on submit, and 계양 still resolves to exactly one.
    assert client.get("/stocks", params={"q": "삼성전"}).json()["found"] is False
    assert client.get("/stocks", params={"q": "계양"}).json()["stock"]["corp_code"] == KEYANG
