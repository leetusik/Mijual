"""익명 대화 저장소 (P6.S1): the anonymity is a schema property, so it is a test.

R7 §대화 로그: 「계정·이메일·IP·UA 컬럼은 저장하지 않음 — 표시 정책이 아니라
스키마」 and 「계정↔대화 연결 컴럼·조인·추정 매칭 금지」. A promise kept by
discipline is a promise nobody can check, so the first case below walks the two
tables' columns and foreign keys instead of trusting the reviewer. The rest is the
port's read contract: the keys the built panel reads, newest first, filtered, and
paged by an opaque cursor.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mijual.db.models import Account, Base, ConversationFeedback, ConversationTurn
from mijual.web.conversations import Conversations
from mijual.web.conversationstore import (
    REFUSAL_FAMILIES,
    SCOPE_ALL_KO,
    DbConversations,
    new_session_hash,
    record_feedback,
    record_turn,
    session_hash_or_new,
)
from mijual.web.errors import ApiError


@pytest.fixture()
def store():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    yield session, DbConversations(factory)
    session.close()


def test_no_conversation_column_can_name_a_person_and_none_joins_an_account() -> None:
    """The promise, read off the schema: no 계정/이메일/IP/UA column, no FK at all.

    ``conversation_feedback.email`` is the single exception R7 signs — 답장 이메일
    (선택 — 사용자가 자발 입력한 경우에만 값 존재) — and it is spelled out here so
    a second one cannot arrive unnoticed.
    """
    forbidden = ("account", "email", "ip", "user_agent", "useragent", "holding", "portfolio")
    for table in (ConversationTurn.__table__, ConversationFeedback.__table__):
        for column in table.columns:
            named = [
                word
                for word in forbidden
                if word in column.name.lower()
                and not (table.name == "conversation_feedback" and column.name == "email")
            ]
            assert not named, f"{table.name}.{column.name} would identify a person: {named}"
        # 계정↔대화 조인 금지 — there is no foreign key to join *through*, in
        # either direction, and no relationship reaching this side either.
        assert not table.foreign_keys, f"{table.name} has a foreign key"
    reachable = {
        fk.column.table.name
        for table in Base.metadata.tables.values()
        for fk in table.foreign_keys
        if table.name.startswith("conversation_") or fk.column.table.name.startswith("conversation_")
    }
    assert not reachable, f"a foreign key crosses the conversation boundary: {reachable}"
    assert not any(
        column.name.startswith("session_hash") or "conversation" in column.name
        for column in Account.__table__.columns
    )


def test_the_log_reads_back_newest_first_with_the_keys_the_panel_names(store) -> None:
    """The three tabs' rows, their filters, and the opaque cursor's page boundary."""
    session, port = store
    assert isinstance(port, Conversations)  # the P5 protocol, structurally satisfied

    thread, other = new_session_hash(), new_session_hash()
    record_turn(
        session,
        session_hash=thread,
        question="신주인수권 매매 언제 끝나나요?",
        kind="answer",
        answer="증서 매매기간은 2026-05-20까지입니다.",
        scope_rcept_no="20260508000928",
        evidence=["20260508000928"],
        quotes=["신주인수권증서의 매매기간: 2026.05.14 ~ 2026.05.20"],
    )
    record_turn(
        session,
        session_hash=thread,
        question="발행가는 얼마인가요?",
        kind="refusal",
        answer="확정발행가는 아직 공시되지 않았습니다.",
        scope_rcept_no="20260508000928",
        refusal_category="확정 전",
        evidence=["20260508000928"],
        quotes=["확정 발행가액은 2026.06.02에 확정될 예정"],
    )
    record_turn(
        session,
        session_hash=other,
        question="전체 공시에서 오늘 마감인 게 있나요?",
        kind="answer",
        answer="오늘 마감인 이벤트는 없습니다.",
    )
    record_feedback(session, text="설명이 좋았어요", email="reader@mijual.kr", session_hash=thread)
    record_feedback(session, text="이건 잘 모르겠어요")
    session.commit()

    log = port.conversations()
    assert log.total == 3
    assert [row["question"] for row in log.rows][0] == "전체 공시에서 오늘 마감인 게 있나요?"
    newest = log.rows[0]
    assert set(newest) == {
        "session_hash", "at", "scope", "question", "kind", "answer", "evidence", "quotes"
    }
    assert newest["at"].endswith("+09:00") and newest["scope"] == SCOPE_ALL_KO
    refusal = next(row for row in log.rows if row["kind"] == "refusal")
    assert refusal["refusal_category"] == "확정 전"
    assert refusal["scope"] == "20260508000928"
    assert refusal["quotes"] == ["확정 발행가액은 2026.06.02에 확정될 예정"]

    # R7's filters, and only those.
    assert port.conversations(kind="refusal").total == 1
    assert port.conversations(refusal_category="확정 전").rows[0]["question"] == "발행가는 얼마인가요?"
    assert port.conversations(session_hash=other).total == 1

    # 시간 역순 커서 페이지네이션: the cursor is opaque, and absent at the end.
    first = port.conversations(limit=2)
    assert first.next_cursor and "next_cursor" in first.payload()
    rest = port.conversations(limit=2, cursor=first.next_cursor)
    assert rest.next_cursor is None and "next_cursor" not in rest.payload()
    assert [row["question"] for row in rest.rows] == [log.rows[2]["question"]]
    with pytest.raises(ApiError):
        port.conversations(cursor="not-a-cursor-this-service-minted")

    # 익명 세션 = 대화 로그의 집계면, and it counts refusals rather than tracking a
    # person: two turns, one of them a refusal, and the newest turn's 범위.
    sessions = port.sessions()
    assert sessions.total == 2
    aggregate = next(row for row in sessions.rows if row["session_hash"] == thread)
    assert aggregate["questions"] == 2 and aggregate["refusals"] == 1
    assert aggregate["last_scope"] == "20260508000928"
    assert set(aggregate) == {
        "session_hash", "last_activity", "questions", "refusals", "last_scope"
    }

    queue = port.feedback()
    assert queue.total == 2 and queue.rows[0]["text"] == "이건 잘 모르겠어요"
    assert "email" not in queue.rows[0] and "session_hash" not in queue.rows[0]
    assert queue.rows[1] == {
        "at": queue.rows[1]["at"],
        "text": "설명이 좋았어요",
        "email": "reader@mijual.kr",
        "session_hash": thread,
    }


def test_the_write_api_takes_the_five_signed_families_and_refuses_anything_else(store) -> None:
    """R6: 카테고리 5종만. An invented family would filter to nothing in the panel.

    And the handle is checked on the way in — a client-supplied string that is not
    a minted handle never reaches the column, which is what keeps an address out
    of it.
    """
    session, _ = store
    for family in REFUSAL_FAMILIES:
        record_turn(
            session,
            session_hash=new_session_hash(),
            question="?",
            kind="refusal",
            answer="…",
            refusal_category=family,
        )
    assert session.query(ConversationTurn).count() == 5

    def refused(**kw):
        with pytest.raises(ValueError):
            record_turn(session, question="?", answer="…", **kw)
        session.rollback()

    handle = new_session_hash()
    refused(session_hash=handle, kind="refusal", refusal_category="게이트 실패")
    refused(session_hash=handle, kind="refusal")  # a refusal without its family
    refused(session_hash=handle, kind="answer", refusal_category="철회")
    refused(session_hash=handle, kind="error")
    refused(session_hash="reader@mijual.kr", kind="answer")

    with pytest.raises(ValueError):
        record_feedback(session, text="   ")
    with pytest.raises(ValueError):
        record_feedback(session, text="의견", session_hash="reader@mijual.kr")

    # The handle is minted, never derived: two are different, and a token that is
    # not one is replaced rather than trusted.
    assert new_session_hash() != new_session_hash()
    assert session_hash_or_new(handle) == handle
    assert session_hash_or_new("reader@mijual.kr") != "reader@mijual.kr"
