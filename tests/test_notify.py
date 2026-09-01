"""마감 임박 이메일 (P4.S2): who gets one, once, and what it may say.

Very core behaviour only, in the established DB-free style (in-memory SQLite,
``StaticPool``, no network, no SMTP): **who is selected**, **that nobody is mailed
twice**, **that a moved 마감 is a new deadline**, **that the ceiling stops**, and
the two copy rules the round signed — the subject template, and 확정발행가 전
금액 금지 applying to the mail. Everything else about the transport is verified
live against a local sink, not asserted here.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.db.models import (
    Account,
    Base,
    Extraction,
    Holding,
    NotificationPref,
    NotificationSend,
    OfferingInput,
    RightsType,
    Snapshot,
)
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.mail import DEADLINE, Message, render
from mijual.notify import send_deadlines

TODAY = date(2026, 9, 2)
KEYANG, SEGI = "00102618", "00133618"
BASE_URL = "https://jujutower.com"


class Recorder:
    """A mailer that records instead of sending. The seam is the whole point."""

    def __init__(self) -> None:
        self.sent: list[Message] = []

    def send(self, message: Message) -> None:
        self.sent.append(message)


def _warrant(session, *, corp_code: str, end: date) -> None:
    """An exposable ① whose 증서 매매 마감 is ``end``. 발행가 확정 전, so no money."""
    event = ensure_event(
        session, corp_code=corp_code, report_subtype="piicDecsn",
        original_rcept_dt="20260724", rights_type=RightsType.SUBSCRIPTION_WARRANT,
    )
    event.exposure_state = "exposable"
    version = ensure_version(
        session, event, rcept_no="20260724000546", rcept_dt=date(2026, 7, 24)
    )
    session.add(Snapshot(
        filing_version_id=version.id, source="document",
        payload_bytes=b"<DOCUMENT/>", content_sha1=version.rcept_no,
    ))
    session.add(Extraction(
        event_id=event.id, filing_version_id=version.id, rcept_no=version.rcept_no,
        field_key="warrant_trading_period", status="extracted",
        value={"start_date": str(end - timedelta(days=5)), "end_date": str(end)},
        quote="신주인수권증서의 상장·매매기간", span_start=10, span_end=30,
        span_status="resolved", gate_status="passed",
    ))
    session.add(Extraction(
        event_id=event.id, filing_version_id=version.id, rcept_no=version.rcept_no,
        field_key="issue_price_formula", status="extracted",
        value={"final_price_date": str(end + timedelta(days=2))},
        quote="발행가액 확정", span_start=1, span_end=8,
        span_status="resolved", gate_status="passed",
    ))
    session.add(OfferingInput(
        event_id=event.id, corp_code=corp_code, decision_rcept_no=version.rcept_no,
        price_confirmed=False, subscription_start=end + timedelta(days=7),
        subscription_end=end + timedelta(days=8),
        # 발행가 확정 전: a planned price, never a confirmed one — so nothing
        # downstream may render a won amount.
        inputs={"rcept_no": version.rcept_no, "planned_price": "3200",
                "allotment_ratio": "0.2314082845"},
    ))


def _dissent(session, *, corp_code: str, end: date) -> None:
    """An exposable ③ whose 반대의사 통지 마감 is ``end``. No price fact at all."""
    event = ensure_event(
        session, corp_code=corp_code, report_subtype="cmpMgDecsn",
        original_rcept_dt="20260713", rights_type=RightsType.APPRAISAL_RIGHT,
    )
    event.exposure_state = "exposable"
    version = ensure_version(
        session, event, rcept_no="20260713000345", rcept_dt=date(2026, 7, 13)
    )
    session.add(Snapshot(
        filing_version_id=version.id, source="document",
        payload_bytes=b"<DOCUMENT/>", content_sha1=version.rcept_no,
    ))
    session.add(Extraction(
        event_id=event.id, filing_version_id=version.id, rcept_no=version.rcept_no,
        field_key="dissent_notice_procedure", status="extracted",
        value={"notice_start_date": str(end - timedelta(days=14)),
               "notice_end_date": str(end)},
        quote="반대의사 통지", span_start=1, span_end=8,
        span_status="resolved", gate_status="passed",
    ))


@pytest.fixture()
def factory():
    """One reader holding two companies: an ① at D-7 and an ③ at D-1."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    make = sessionmaker(bind=engine)
    with make() as session:
        ensure_corp(session, KEYANG, corp_name="계양전기", stock_code="012200")
        ensure_corp(session, SEGI, corp_name="세기상사", stock_code="002420")
        _warrant(session, corp_code=KEYANG, end=TODAY + timedelta(days=7))
        _dissent(session, corp_code=SEGI, end=TODAY + timedelta(days=1))
        account = Account(email="reader@mijual.kr", password_hash="scrypt$fake")
        session.add(account)
        session.flush()
        session.add(Holding(account_id=account.id, corp_code=KEYANG, shares=500))
        session.add(Holding(account_id=account.id, corp_code=SEGI, shares=100))
        session.commit()
    return make


def _run(factory, mailer, *, today: date = TODAY, max_mails: int | None = 200):
    return send_deadlines(
        factory, mailer, today=today, app_base_url=BASE_URL, max_mails=max_mails
    )


def test_the_default_chips_select_two_deadlines_and_a_rerun_sends_nothing(factory) -> None:
    """R5's default is 7일+1일, and the record of a send is what stops the second one."""
    mailer = Recorder()
    report = _run(factory, mailer)
    assert (report.accounts, report.candidates, report.sent) == (1, 2, 2)
    assert (report.already_sent, report.skipped_no_chips, report.failed) == (0, 0, 0)
    # One mail per (reader, event, lead day, anchor date) — written after the
    # transport accepted it, which is what makes the second run a no-op.
    with factory() as session:
        rows = session.scalars(select(NotificationSend)).all()
        assert sorted(row.lead_day for row in rows) == [1, 7]
        assert {row.account_id for row in rows} == {rows[0].account_id}

    again = _run(factory, Recorder())
    assert (again.candidates, again.sent, again.already_sent) == (2, 0, 2)
    with factory() as session:
        assert len(session.scalars(select(NotificationSend)).all()) == 2


def test_an_empty_chip_selection_is_the_off_switch_and_it_is_honoured(factory) -> None:
    """`[]` persists and means no mail — R5's only 해지 control (`알림 설정에서 끌 수`)."""
    with factory() as session:
        account = session.scalars(select(Account)).first()
        session.add(NotificationPref(account_id=account.id, lead_days=[]))
        session.commit()

    mailer = Recorder()
    report = _run(factory, mailer)
    assert (report.sent, report.candidates, report.skipped_no_chips) == (0, 0, 1)
    assert mailer.sent == []
    with factory() as session:
        assert session.scalars(select(NotificationSend)).all() == []


def test_a_moved_deadline_is_a_new_deadline_and_mails_again(factory) -> None:
    """A 정정 that shifts the 마감 must re-alert; one that does not must not.

    The whole value of the alert is the date, so a reader told "D-7 = 9월 9일"
    who is never told it moved has been actively misled.
    """
    assert _run(factory, Recorder()).sent == 2

    # 정정: the ① 매매 마감 moves one day later. Tomorrow it is D-7 again — a
    # different anchor date, so a different deadline.
    with factory() as session:
        row = session.scalars(
            select(Extraction).where(Extraction.field_key == "warrant_trading_period")
        ).first()
        row.value = {"start_date": str(TODAY + timedelta(days=2)),
                     "end_date": str(TODAY + timedelta(days=8))}
        session.commit()

    moved = _run(factory, Recorder(), today=TODAY + timedelta(days=1))
    assert moved.sent == 1 and moved.already_sent == 0
    with factory() as session:
        anchors = sorted(row.anchor_date for row in session.scalars(select(NotificationSend)))
        assert anchors == [str(TODAY + timedelta(days=1)),   # the ③, D-1
                           str(TODAY + timedelta(days=7)),   # the ① before the 정정
                           str(TODAY + timedelta(days=8))]   # and after it


def test_the_mail_ceiling_is_a_reported_stop_not_an_exception(factory) -> None:
    """Structural, like every other outward budget in this codebase."""
    mailer = Recorder()
    report = _run(factory, mailer, max_mails=1)
    assert report.sent == 1 and report.budget_exhausted is True
    assert len(mailer.sent) == 1 and report.notes
    with factory() as session:
        assert len(session.scalars(select(NotificationSend)).all()) == 1


def test_the_subject_is_re_signed_and_a_pending_price_mail_carries_no_won_amount(
    factory,
) -> None:
    """The two copy rules: D23's re-signature, and 확정발행가 전 금액 금지 in the mail."""
    mailer = Recorder()
    _run(factory, mailer)
    warrant = next(m for m in mailer.sent if m.data["rights_type"] == "R1")
    dissent = next(m for m in mailer.sent if m.data["rights_type"] == "R3")

    subject, body = render(warrant).subject, render(warrant).text
    assert subject == (
        "[주주의관제탑] 계양전기 — 신주인수권증서 매매 마감 D-7 (2026-09-09)"
    )
    assert "미주알" not in subject and "미주알" not in body

    # 확정발행가 전 금액 금지 — 메일에도 동일. The rule is about a **won amount**,
    # so the assert is a money pattern rather than the character 원: R5's signed
    # footer says 「회원님이 설정한…」 and that 원 is not a figure.
    assert re.search(r"[0-9][0-9,]*\s*원", body) is None
    assert "3200" not in body  # the 예정발행가 never reaches a reader's mail
    assert "발행가: 확정 전 (확정 예정일 2026-09-11)" in body
    # ①'s one derived count: ⌊500 × 0.2314082845⌋ = 115 (R5's own example).
    assert "보유: 500주 기준 115주" in body
    assert f"{BASE_URL}/events/20260724000546" in body
    assert f"{BASE_URL}/portfolio/notifications" in body
    assert "알림 설정에서 끌 수 있습니다" in body

    # ③ has neither a share conversion nor a price fact, so it states neither.
    third = render(dissent).text
    assert "발행가" not in third and "기준" not in third
    assert "보유: 100주" in third
    assert render(dissent).subject.startswith("[주주의관제탑] 세기상사 — 반대의사 통지 마감 D-1")


def test_an_unknown_message_kind_refuses_to_render_rather_than_send_nothing() -> None:
    with pytest.raises(Exception):
        render(Message(to="x@example.invalid", kind="marketing", data={}))
    # The two kinds that exist are the two the product is allowed to send.
    assert DEADLINE == "deadline"
