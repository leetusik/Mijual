"""The start cards' selection (`P11.F1`): a card that can never be a dead question.

Two cases, because two things can go wrong. The corpus **has** answerable
companies → the endpoint names one per card shape, each one findable by the
agent's own search, and never the same issuer twice. The corpus has **none** →
both slots come back ``null`` so the surface falls back to its static sentences,
which is a 200 with two nulls and never an error on the product's first screen.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.db.models import Base, Extraction, OfferingInput, RightsType, Snapshot
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.web.app import create_app
from mijual.web.deps import get_session
from mijual.web.reads import find_corps

CB_CORP, OFFER_CORP = "00900001", "00900002"


def _offering(session, *, today: date) -> None:
    """An ① 30 days out with a 배정비율 — the 계산 card's whole requirement."""
    event = ensure_event(
        session, corp_code=OFFER_CORP, report_subtype="piicDecsn",
        original_rcept_dt="20260701", rights_type=RightsType.SUBSCRIPTION_WARRANT,
    )
    event.exposure_state = "exposable"
    version = ensure_version(session, event, rcept_no="20260701000001", rcept_dt=date(2026, 7, 1))
    session.add(Snapshot(
        filing_version_id=version.id, source="document", content_sha1=version.rcept_no,
        payload_bytes="<DOCUMENT><COMPANY-NAME>유상증자공업(주)</COMPANY-NAME></DOCUMENT>".encode(),
    ))
    session.add(Extraction(
        event_id=event.id, filing_version_id=version.id, rcept_no=version.rcept_no,
        field_key="warrant_trading_period", status="extracted",
        value={"start_date": str(today + timedelta(days=25)),
               "end_date": str(today + timedelta(days=30))},
        quote="신주인수권증서의 상장·매매기간", span_start=10, span_end=30,
        span_status="resolved", gate_status="passed",
    ))
    session.add(OfferingInput(
        event_id=event.id, corp_code=OFFER_CORP, decision_rcept_no=version.rcept_no,
        price_confirmed=False,
        inputs={"rcept_no": version.rcept_no, "allotment_ratio": "0.5"},
    ))


def _convertibles(session, *, today: date, count: int) -> None:
    """``count`` ② filings for one issuer — the 검색 card's multi-hit."""
    for n in range(count):
        event = ensure_event(
            session, corp_code=CB_CORP, report_subtype="cvbdIsDecsn",
            original_rcept_dt=f"2025082{n}", rights_type=RightsType.CONVERTIBLE_OVERHANG,
        )
        event.exposure_state = "exposable"
        rcept_no = f"2025082000000{n}"
        version = ensure_version(session, event, rcept_no=rcept_no, rcept_dt=date(2025, 8, 20))
        session.add(Snapshot(
            filing_version_id=version.id, source="cvbdIsDecsn", content_sha1=rcept_no,
            payload_json={"rcept_no": rcept_no, "cv_prc": "1,591",
                          "cvrqpd_bgd": str(today + timedelta(days=40 + n)),
                          "cvrqpd_edd": str(today + timedelta(days=900)),
                          "cvisstk_cnt": "16,907,605", "cvisstk_tisstk_vs": "15.22",
                          "bd_fta": "26,900,000,000", "bdis_mthn": "사모",
                          "bd_mtd": str(today + timedelta(days=900))},
        ))


@pytest.fixture()
def cards():
    today = datetime.now(timezone(timedelta(hours=9))).date()
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    def build(*, populated: bool) -> TestClient:
        ensure_corp(session, CB_CORP, corp_name="전환사채상사")
        ensure_corp(session, OFFER_CORP, corp_name="유상증자공업")
        if populated:
            _convertibles(session, today=today, count=3)
            _offering(session, today=today)
        session.flush()
        app = create_app()
        app.dependency_overrides[get_session] = lambda: session
        client = TestClient(app)
        client.session = session  # type: ignore[attr-defined]
        client.today = today  # type: ignore[attr-defined]
        return client

    yield build
    session.close()


def test_each_card_names_a_company_that_can_answer_it(cards) -> None:
    client = cards(populated=True)
    body = client.get("/ask/start-cards").json()
    assert body["reference"] == str(client.today)

    # 검색 card: the multi-hit issuer, with the count the search will list.
    search = body["search_events"]
    assert search["corp_name"] == "전환사채상사" and search["filings"] == 3

    # 계산 card: the ① that still exposes a 배정비율 before its deadline — and a
    # *different* issuer, because the corpus allows one.
    calculate = body["calculate"]
    assert calculate["corp_name"] == "유상증자공업" and calculate["days"] == 30
    assert calculate["dday"] == "D-30" and calculate["rcept_no"] == "20260701000001"
    assert calculate["corp_code"] != search["corp_code"]

    # Both names are findable by the agent's own search — the card's sentence
    # travels to `search_events`, not to `resolve_corp`, so a name that reached
    # two issuers would make the card a question about somebody else's filings.
    for pick in (search, calculate):
        found = find_corps(client.session, pick["corp_name"])
        assert [corp.corp_code for corp in found] == [pick["corp_code"]]


def test_a_corpus_with_nothing_to_offer_answers_nulls_not_an_error(cards) -> None:
    """Both issuers exist; neither has an exposable filing. The screen still draws."""
    client = cards(populated=False)
    response = client.get("/ask/start-cards")
    assert response.status_code == 200
    assert response.json() == {
        "reference": str(client.today),
        "search_events": None,
        "calculate": None,
    }
