"""내 포트폴리오 (P5.S8): whose rows these are, and what they may say.

DB-free, the established pattern — in-memory SQLite, dependency overrides, no
docker and no network. One mixed corpus covers the cases R5 states as rules: an ①
whose 발행가 is not fixed (shares, never money), an ② whose window opened last
month (진행 중, never 지나간), an ③ whose 통지 마감 has passed, and an ① that lapsed
inside coverage (the 놓친 돈 row the 챙긴 돈 mark re-labels).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.config import Settings
from mijual.db.models import (
    Base,
    Extraction,
    Holding,
    LapseClaim,
    OfferingInput,
    PerformanceReport,
    RightsType,
    Snapshot,
)
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.web.app import create_app
from mijual.web.csrf import CSRF_HEADER
from mijual.web.deps import get_session, get_write_session

KEYANG, HANWHA, DAEDONG, SEGI = "00102618", "00162461", "00109310", "00133618"
LAPSE_RCEPT = "20260730000366"


def _warrant(session, *, corp_code, day, start, end, inputs, price_confirmed):
    event = ensure_event(
        session, corp_code=corp_code, report_subtype="piicDecsn",
        original_rcept_dt=day, rights_type=RightsType.SUBSCRIPTION_WARRANT,
    )
    event.exposure_state = "exposable"
    version = ensure_version(session, event, rcept_no=f"{day}000100", rcept_dt=date(2026, 1, 1))
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
        price_confirmed=price_confirmed, subscription_start=end + timedelta(days=7),
        subscription_end=end + timedelta(days=8), inputs=inputs,
    ))
    return event


def _corpus(session, *, today: date) -> None:
    ensure_corp(session, KEYANG, corp_name="계양전기", stock_code="012200")
    ensure_corp(session, HANWHA, corp_name="한화솔루션", stock_code="009830")
    ensure_corp(session, DAEDONG, corp_name="대동기어", stock_code="008830")
    ensure_corp(session, SEGI, corp_name="세기상사", stock_code="002420")

    # ① live, 발행가 확정 전 — factors only, not one won amount.
    _warrant(session, corp_code=KEYANG, day="20260724",
             start=today - timedelta(days=2), end=today + timedelta(days=3),
             price_confirmed=False,
             inputs={"rcept_no": "20260724000100", "planned_price": "3200",
                     "allotment_ratio": "0.2314082845"})

    # ① past, 소멸 — the row 챙긴 돈 re-labels. R4's own 한화솔루션 factors.
    lapsed = _warrant(session, corp_code=HANWHA, day="20260720",
                      start=today - timedelta(days=40), end=today - timedelta(days=33),
                      price_confirmed=True,
                      inputs={"rcept_no": "20260720000100", "confirmed_price": "22100",
                              "discount_rate": "0.2", "allotment_ratio": "0.2465120994"})
    session.add(PerformanceReport(
        event_id=lapsed.id, corp_code=HANWHA, corp_name="한화솔루션",
        rcept_no=LAPSE_RCEPT, rcept_dt=today - timedelta(days=20), parse_status="parsed",
        facts={}, lapse={"status": "valued", "subscription_end": str(today - timedelta(days=25)),
                         "lapsed": 3734925, "warrants_issued": 42165422,
                         "warrants_exercised": 38430497, "lapse_rate": "0.0886",
                         "confirmed_price": "22100.0", "allotment_ratio": 0.2465120994,
                         "unit_value": "5525.0", "value_krw": "20635460625",
                         "value_floor_krw": "16554561031",
                         "performance_rcept_no": LAPSE_RCEPT},
    ))

    # ② opened a month ago: 진행 중, and never in 지나간 마감.
    overhang = ensure_event(session, corp_code=DAEDONG, report_subtype="cvbdIsDecsn",
                            original_rcept_dt="20251016",
                            rights_type=RightsType.CONVERTIBLE_OVERHANG)
    overhang.exposure_state = "exposable"
    cb = ensure_version(session, overhang, rcept_no="20251016000315", rcept_dt=date(2025, 10, 16))
    session.add(Snapshot(
        filing_version_id=cb.id, source="cvbdIsDecsn", content_sha1="cb",
        payload_json={"rcept_no": "20251016000315", "cv_prc": "1,591",
                      "cvrqpd_bgd": str(today - timedelta(days=30)),
                      "cvrqpd_edd": str(today + timedelta(days=900)),
                      "cvisstk_cnt": "16,907,605", "cvisstk_tisstk_vs": "6.68",
                      "bd_fta": "26,900,000,000", "bdis_mthn": "사모",
                      "bd_mtd": str(today + timedelta(days=900))},
    ))

    # ③ 통지 마감 지남 — a past deadline with no money anywhere near it.
    dissent = ensure_event(session, corp_code=SEGI, report_subtype="cmpMgDecsn",
                           original_rcept_dt="20260713",
                           rights_type=RightsType.APPRAISAL_RIGHT)
    dissent.exposure_state = "exposable"
    merge = ensure_version(session, dissent, rcept_no="20260713000345", rcept_dt=date(2026, 7, 13))
    session.add(Snapshot(filing_version_id=merge.id, source="document",
                         payload_bytes=b"<DOCUMENT/>", content_sha1="merge"))
    session.add(Extraction(
        event_id=dissent.id, filing_version_id=merge.id, rcept_no=merge.rcept_no,
        field_key="dissent_notice_procedure", status="extracted",
        value={"notice_start_date": str(today - timedelta(days=60)),
               "notice_end_date": str(today - timedelta(days=45))},
        quote="반대의사 통지", span_start=1, span_end=8, span_status="resolved",
        gate_status="passed",
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

    app = create_app(Settings(session_secret="test-session-secret"))
    app.dependency_overrides[get_session] = lambda: session

    def _write():
        yield session
        session.commit()

    app.dependency_overrides[get_write_session] = _write
    with TestClient(app, headers={CSRF_HEADER: "1"}) as test_client:
        test_client.today = today  # type: ignore[attr-defined]
        test_client.db = session  # type: ignore[attr-defined]
        yield test_client
    session.close()


def _login(client, email="reader@mijual.kr"):
    client.cookies.clear()
    client.post("/auth/signup", json={"email": email, "password": "portfolio-8"})


def _add(client, corp_code, shares):
    return client.post("/portfolio/holdings", json={"corp_code": corp_code, "shares": shares})


def test_holdings_are_the_owners_only_and_a_strangers_row_is_a_404(client) -> None:
    _login(client)
    created = _add(client, KEYANG, 500)
    assert created.status_code == 201
    holding = created.json()["holding"]
    assert holding["corp_name"] == "계양전기" and holding["shares"] == 500

    # 담기 of a company already held is refused, never merged into a new count.
    assert _add(client, KEYANG, 100).json()["error"]["code"] == "holding_exists"
    assert _add(client, "00000000", 100).status_code == 404  # not in the corpus
    assert _add(client, KEYANG, 0).json()["error"]["code"] == "invalid_shares"

    assert client.patch(f"/portfolio/holdings/{holding['id']}",
                        json={"shares": 1200}).json()["holding"]["shares"] == 1200

    _login(client, "stranger@mijual.kr")
    assert client.get("/portfolio").json()["holdings"] == []
    for call in (
        client.patch(f"/portfolio/holdings/{holding['id']}", json={"shares": 9}),
        client.delete(f"/portfolio/holdings/{holding['id']}"),
    ):
        # Not 403: a row that is not yours must not be confirmed to exist.
        assert call.status_code == 404 and call.json()["error"]["code"] == "not_found"
    assert client.db.scalars(select(Holding)).all()[0].shares == 1200

    client.cookies.clear()
    assert client.get("/portfolio").status_code == 401  # the only gated surface


def test_the_dday_list_splits_two_sections_and_never_prices_a_2_or_a_3(client) -> None:
    _login(client)
    for code, shares in ((KEYANG, 500), (DAEDONG, 300), (SEGI, 100), (HANWHA, 500)):
        assert _add(client, code, shares).status_code == 201

    body = client.get("/portfolio").json()
    assert body["reference"] == str(client.today)  # 기준 (KST), served not computed

    # 다가오는: the dated deadline first, then the ② that is 진행 중 — never 종료,
    # and never filed under 지나간.
    assert [row["rights_type"] for row in body["upcoming"]] == ["R1", "R2"]
    live, overhang = body["upcoming"]
    assert live["countdown"]["days"] == 3 and live["shares"] == 500
    assert live["offering"]["price_confirmed"] is False
    assert not [key for key in live["offering"] if "value" in key]  # 확정 전 → 금액 없음
    assert overhang["countdown"]["window_state"] == "open"
    assert "offering" not in overhang and "lapse" not in overhang  # ② 금액 금지
    assert overhang["convertible"]["overhang_pct"]["value"] == "6.68"

    # 지나간, 최근순: the ① 소멸 (D+33) before the ③ 통지 마감 (D+45), no money on ③.
    assert [row["rights_type"] for row in body["past"]] == ["R1", "R3"]
    lapse_row, dissent = body["past"]
    assert lapse_row["countdown"]["dday"] == "D+33" and dissent["countdown"]["dday"] == "D+45"
    assert not [key for key in dissent if key in ("offering", "lapse", "convertible")]

    # The 소멸 row serves factors, not products: no per-holding won amount exists
    # in the payload, and ⌊500 × 0.2465120994⌋ × 5,525 = 679,575원 is the client's.
    assert lapse_row["lapse"]["value"] == {"value": "20635460625", "estimated": True}
    assert lapse_row["lapse"]["unit_value"] == {"value": "5525", "estimated": True}
    assert lapse_row["shares"] == 500 and lapse_row["claimed"] is False

    # The holding row's 진행 중인 권리 chip is the same countdown object, not a copy.
    keyang = next(h for h in body["holdings"] if h["corp_code"] == KEYANG)
    assert keyang["rights"] == {"count": 1, "next": {
        "event_id": live["event_id"], "rcept_no": live["rcept_no"],
        "rights_type": "R1", "countdown": live["countdown"]}}


def test_a_claim_relabels_one_row_and_stores_no_amount(client) -> None:
    _login(client)
    _add(client, HANWHA, 500)
    assert client.put(f"/portfolio/claims/{LAPSE_RCEPT}").json() == {
        "rcept_no": LAPSE_RCEPT, "claimed": True
    }
    body = client.get("/portfolio").json()
    row = body["past"][0]
    assert row["claimed"] is True
    # 금액 동일, 「추정」 유지 — a user claim changes a label, never a figure.
    assert row["lapse"]["value"] == {"value": "20635460625", "estimated": True}
    # …and it reaches no aggregate, because the payload has none to reach.
    assert "totals" not in body
    stored = client.db.scalars(select(LapseClaim)).all()
    assert len(stored) == 1 and not hasattr(stored[0], "value")

    assert client.put("/portfolio/claims/20260101000001").status_code == 404  # no such 소멸
    assert client.delete(f"/portfolio/claims/{LAPSE_RCEPT}").json()["claimed"] is False
    assert client.get("/portfolio").json()["past"][0]["claimed"] is False
    assert client.db.scalars(select(LapseClaim)).all() == []


def test_notifications_default_to_7_and_1_and_the_address_is_the_account(client) -> None:
    _login(client)
    assert client.get("/portfolio/notifications").json() == {
        "address": "reader@mijual.kr", "lead_days": [7, 1]
    }
    saved = client.put("/portfolio/notifications", json={"lead_days": [0, 3]})
    assert saved.json()["lead_days"] == [3, 0]  # chip order, deduped
    assert client.get("/portfolio/notifications").json()["lead_days"] == [3, 0]
    # Deselecting every chip is R5's only off switch — it must persist, not reset.
    assert client.put("/portfolio/notifications", json={"lead_days": []}).json()["lead_days"] == []
    assert client.get("/portfolio/notifications").json()["lead_days"] == []
    assert client.put("/portfolio/notifications",
                      json={"lead_days": [5]}).json()["error"]["code"] == "invalid_lead_days"

    # 수신 주소 "변경" edits the account itself — there is no second address.
    assert client.patch("/auth/account", json={"email": "New@Mijual.KR"}).status_code == 200
    assert client.get("/portfolio/notifications").json()["address"] == "new@mijual.kr"
    assert client.get("/auth/me").json()["account"]["email"] == "new@mijual.kr"


def test_the_sample_is_anonymous_and_carries_no_account_fact(client) -> None:
    body = client.get("/portfolio/sample")  # no cookie at all
    assert body.status_code == 200
    payload = body.json()
    assert payload["sample"] is True
    assert [(h["corp_code"], h["shares"]) for h in payload["holdings"]] == [
        (KEYANG, 500), (DAEDONG, 300), (HANWHA, 500), (SEGI, 100)
    ]
    text = body.text
    assert "@" not in text and "claimed" not in text  # 가짜 이메일·알림 이력 렌더 금지
    assert "notifications" not in payload and "address" not in payload
    # Real corpus events, the same composition as a real portfolio.
    assert [row["rights_type"] for row in payload["upcoming"]] == ["R1", "R2"]
    assert payload["past"][0]["lapse"]["value"]["estimated"] is True
    assert client.db.scalars(select(Holding)).all() == []  # nothing was stored
