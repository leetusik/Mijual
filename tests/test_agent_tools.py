"""The five agent tools (P6.S2): what they may return, and what they must not.

Deterministic and free — no model, no key, no network, no docker. The corpus is
the same in-memory SQLite shape ``test_web_board.py`` uses, cut to the cases R6's
rules are about: an ① whose 발행가 is not fixed (share counts, never money), an ②
that opened last month, and a 철회된 filing that must be *readable by number* and
*absent from search*.
"""

from __future__ import annotations

import ast
import inspect
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mijual.agent import ToolContext, get_contact, get_event, get_portfolio, save_feedback
from mijual.agent import search_events
from mijual.agent.declarations import TOOL_SPECS
from mijual.agent.figures import grouped
from mijual.agent.tools import TOOL_NAMES, call_tool
from mijual.config import Settings
from mijual.db.models import (
    Account,
    Base,
    ConversationFeedback,
    Extraction,
    Holding,
    OfferingInput,
    RightsType,
    Snapshot,
)
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.web.conversationstore import new_session_hash

AGENT_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "mijual" / "agent"
#: The modules that spend an OpenDART request or an LLM call (`P6` Finding 1).
SPENDING = ("mijual.dart", "mijual.collect", "mijual.extract")

KEYANG, SOME, R1_RCEPT, R2_RCEPT = "00102618", "00999001", "20260724000546", "20250820000220"
#: R6's own 철회 example (썸에이지), under a fixture corp code.
WITHDRAWN_RCEPT = "20260805000454"


def _corpus(session, *, today: date) -> None:
    ensure_corp(session, KEYANG, corp_name="계양전기", stock_code="012200")
    ensure_corp(session, SOME, corp_name="썸에이지", stock_code="123420")

    # ① live: 매매기간 closes in three days, 발행가 아직 미확정.
    warrant = ensure_event(
        session, corp_code=KEYANG, report_subtype="piicDecsn",
        original_rcept_dt="20260508", rights_type=RightsType.SUBSCRIPTION_WARRANT,
    )
    warrant.exposure_state = "exposable"
    version = ensure_version(session, warrant, rcept_no=R1_RCEPT, rcept_dt=date(2026, 7, 24))
    session.add(Snapshot(
        filing_version_id=version.id, source="document", content_sha1=R1_RCEPT,
        payload_bytes="<DOCUMENT><COMPANY-NAME>계양전기(주)</COMPANY-NAME></DOCUMENT>".encode(),
    ))
    session.add(Extraction(
        event_id=warrant.id, filing_version_id=version.id, rcept_no=R1_RCEPT,
        field_key="warrant_trading_period", status="extracted",
        value={"start_date": str(today - timedelta(days=3)),
               "end_date": str(today + timedelta(days=3))},
        quote="신주인수권증서의 상장·매매기간", span_start=10, span_end=30,
        span_status="resolved", gate_status="passed",
    ))
    session.add(OfferingInput(
        event_id=warrant.id, corp_code=KEYANG, decision_rcept_no=R1_RCEPT,
        price_confirmed=False, subscription_start=today + timedelta(days=12),
        subscription_end=today + timedelta(days=13),
        inputs={"rcept_no": R1_RCEPT, "planned_price": "3200",
                "allotment_ratio": "0.2314082845"},
    ))

    # ② 전환청구 opened a month ago — 진행 중, and it ranks below the ①.
    overhang = ensure_event(
        session, corp_code=KEYANG, report_subtype="cvbdIsDecsn",
        original_rcept_dt="20250820", rights_type=RightsType.CONVERTIBLE_OVERHANG,
    )
    overhang.exposure_state = "exposable"
    cb = ensure_version(session, overhang, rcept_no=R2_RCEPT, rcept_dt=date(2025, 8, 20))
    session.add(Snapshot(
        filing_version_id=cb.id, source="cvbdIsDecsn", content_sha1="cb",
        payload_json={"rcept_no": R2_RCEPT, "cv_prc": "1,591",
                      "cvrqpd_bgd": str(today - timedelta(days=30)),
                      "cvrqpd_edd": str(today + timedelta(days=900)),
                      "cvisstk_cnt": "16,907,605", "cvisstk_tisstk_vs": "15.22",
                      "bd_fta": "26,900,000,000", "bdis_mthn": "사모",
                      "bd_mtd": str(today + timedelta(days=900))},
    ))

    # 철회: readable by filing number, never a search result.
    pulled = ensure_event(
        session, corp_code=SOME, report_subtype="piicDecsn",
        original_rcept_dt="20260610", rights_type=RightsType.SUBSCRIPTION_WARRANT,
    )
    pulled.add_flag("withdrawn")
    pulled.exposure_state = "withdrawn"
    ensure_version(session, pulled, rcept_no=WITHDRAWN_RCEPT, rcept_dt=date(2026, 8, 5))
    session.flush()


@pytest.fixture()
def store():
    today = datetime.now(timezone(timedelta(hours=9))).date()
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    _corpus(session, today=today)
    yield session, today
    session.close()


def _ctx(store, **kw) -> ToolContext:
    session, today = store
    kw.setdefault("session_hash", new_session_hash())
    kw.setdefault("settings", Settings())
    return ToolContext(session=session, today=today, **kw)


def test_search_lists_the_exposable_events_scope_first_and_declines_honestly(store) -> None:
    """이벤트 목록/단건, in the signed row format — and 0건 with the signed sentence."""
    found = search_events(_ctx(store), "계양전기")
    assert found.payload["count"] == 2
    # The ① deadline is ahead; the ② opened last month and ranks below it.
    assert found.fact_row == (
        f"이벤트 검색 「계양전기」 → 2건 · ① 유상증자 · {R1_RCEPT} · ② 전환사채 · {R2_RCEPT}"
    )
    assert [row["rcept_no"] for row in found.payload["results"]] == [R1_RCEPT, R2_RCEPT]
    # A hit identifies an event and cites it by filing number (API-tier handle).
    assert found.evidence == (R1_RCEPT, R2_RCEPT) and found.quotes == ()
    assert all(citation.api_tier for citation in found.citations)

    # 범위 puts the reader's own event first, and hides nothing.
    scoped = search_events(_ctx(store, scope_rcept_no=R2_RCEPT), "계양전기")
    assert [row["rcept_no"] for row in scoped.payload["results"]] == [R2_RCEPT, R1_RCEPT]

    # A filing number resolves to the single event it names.
    assert search_events(_ctx(store), R1_RCEPT).payload["count"] == 1

    # 0건 = the signed sentence + the 관제 현황판 pointer, and no guess.
    miss = search_events(_ctx(store), "없는회사")
    assert miss.ok and miss.payload["count"] == 0 and miss.payload["results"] == []
    assert miss.fact_row == "이벤트 검색 「없는회사」 → 0건"
    assert miss.payload["none_found_ko"] == "「없는회사」에 해당하는 공시를 찾지 못했습니다"
    # No href: the route belongs to the frontend, and a path in a payload is a
    # string the gate would let the model say (`P6.S7`).
    assert miss.payload["pointer"] == {"label_ko": "관제 현황판"}

    # 게이트 실패 데이터로 답변 금지, structurally: a 철회된 event is not a result.
    assert search_events(_ctx(store), "썸에이지").payload["count"] == 0
    # …but it is readable by number, and the empty search says so to the model
    # (a machine hint, not copy) rather than letting 「찾지 못했습니다」 stand as the
    # answer about an event that has a page and a 철회 notice.
    assert "hint" in search_events(_ctx(store), WITHDRAWN_RCEPT).payload


def test_get_event_is_the_detail_contract_with_its_citations_and_no_money(store) -> None:
    """The verification contract, verbatim — quotes, spans, and nothing derived."""
    result = get_event(_ctx(store), R1_RCEPT)
    assert result.payload["found"] is True and result.payload["state"] == "exposable"
    assert result.fact_row == f"이벤트 읽기 → 계양전기 · ① 유상증자 · {R1_RCEPT}"

    period = result.payload["fields"]["warrant_trading_period"]
    assert period["quote"] == "신주인수권증서의 상장·매매기간" and period["span"] == [10, 30]
    assert result.quotes == ("신주인수권증서의 상장·매매기간",)  # verbatim, never rebuilt
    assert result.evidence == (R1_RCEPT,)
    # 확정발행가 없음 ⇒ 확정 전 금액 is unconstructable rather than refused by prompt.
    assert result.payload["offering"]["price_confirmed"] is False
    assert not [key for key in result.payload["offering"] if "value" in key]

    # A figure travels display-ready (`P6.F1`): the reader's 3,200 beside the
    # contract's exact 3200, and nothing added to a ratio or to an identifier.
    price = result.payload["offering"]["planned_price"]
    assert (price["value"], price["value_display"]) == ("3200", "3,200")
    assert "value_display" not in result.payload["offering"]["allotment_ratio"]
    assert grouped(R1_RCEPT) is None and grouped(16907605) == "16,907,605"

    # 철회 is a surface with its own evidence, not a miss — R6: 거절도 인용 강제.
    pulled = get_event(_ctx(store), WITHDRAWN_RCEPT)
    assert pulled.payload["found"] is True and pulled.payload["state"] == "withdrawn"
    assert pulled.payload["notice_ko"] == "이 유상증자는 철회되었습니다"
    assert pulled.payload["fields"] == {} and pulled.payload["countdown"]["date"] is None

    # An unknown filing number is a fact, not an error, and carries no guess.
    unknown = get_event(_ctx(store), "99999999999999")
    assert unknown.ok and unknown.payload["found"] is False
    assert unknown.fact_row == "이벤트 읽기 → 0건"
    assert unknown.payload["none_found_ko"].endswith("해당하는 공시를 찾지 못했습니다")


def test_an_anonymous_portfolio_is_the_labelled_sample_and_takes_no_client_holdings(store) -> None:
    """R6-3 + Finding 5: the sample, said out loud — and no way to post holdings."""
    session, _ = store
    anonymous = get_portfolio(_ctx(store))
    assert anonymous.fact_row == "내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)"
    assert anonymous.payload["sample"] is True
    assert anonymous.payload["sample_label_ko"] == "구성 예시"
    # The tool's whole argument list is the server-side context: nothing a client
    # sends can name an account, an email or a holding.
    assert list(inspect.signature(get_portfolio).parameters) == ["ctx"]

    account = Account(email="reader@mijual.kr", password_hash="scrypt$x$y$z")
    session.add(account)
    session.flush()
    session.add(Holding(account_id=account.id, corp_code=KEYANG, shares=500))
    session.flush()

    owned = get_portfolio(_ctx(store, account=account))
    assert owned.fact_row == "내 포트폴리오 읽기 → 1종목"
    assert owned.payload["sample"] is False
    assert owned.payload["holdings"][0]["corp_name"] == "계양전기"
    # Upstream D-day, and factors rather than products (R5's hard rule).
    assert owned.payload["upcoming"][0]["countdown"]["reference"] == owned.payload["reference"]


def test_feedback_lands_in_the_queue_and_the_contact_is_honest_when_unset(store) -> None:
    """의견 저장 → 운영자 검토 대기열; 연락처 미정 stays 미정."""
    session, _ = store
    handle = new_session_hash()
    saved = save_feedback(
        _ctx(store, session_hash=handle), "설명이 좋았어요", email="reader@mijual.kr"
    )
    assert saved.ok and saved.fact_row == "의견 저장 → 운영자 검토 대기열"
    row = session.query(ConversationFeedback).one()
    assert (row.text, row.email, row.session_hash) == (
        "설명이 좋았어요", "reader@mijual.kr", handle
    )

    # A failure is the 재시도 행 and writes nothing — no invented Korean anywhere.
    empty = save_feedback(_ctx(store), "   ")
    assert not empty.ok and empty.fact_row == "의견 저장 → 재시도"
    assert session.query(ConversationFeedback).count() == 1

    unset = get_contact(_ctx(store))
    assert unset.payload == {"configured": False} and unset.fact_row == "운영자 연락처 → 미정"
    given = get_contact(_ctx(store, settings=Settings(operator_contact="ops@mijual.kr")))
    assert given.payload == {"configured": True, "contact": "ops@mijual.kr"}
    assert given.fact_row == "운영자 연락처 → ops@mijual.kr"

    # The dispatcher runs exactly the five the model is declared, and no sixth.
    assert tuple(spec.name for spec in TOOL_SPECS) == TOOL_NAMES
    assert call_tool("get_contact", _ctx(store)).fact_row == unset.fact_row
    with pytest.raises(ValueError):
        call_tool("delete_everything", _ctx(store))


def test_the_agent_package_imports_no_spending_module() -> None:
    """`P6` Finding 1: the agent reads persisted rows — it never collects or extracts.

    `P6.S4` re-aims the two ``mijual.web`` scans onto the new boundary; this is
    the third one, and it is cheap insurance while the package is being built.
    """
    offenders = []
    for path in sorted(AGENT_PACKAGE.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
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
    assert not offenders, f"the agent may not reach a spending module: {offenders}"
