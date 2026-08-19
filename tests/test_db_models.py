"""The schema invariants that protect the 정정 story (N2). SQLite — no docker needed."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event as sa_event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from mijual.db.models import Base, CorrectionKind, RightsType, Snapshot
from mijual.db.repository import ensure_corp, ensure_event, ensure_snapshot, ensure_version


@pytest.fixture()
def session():
    engine = create_engine("sqlite://")

    @sa_event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):  # CHECK/UNIQUE are on by default, FKs are not
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        ensure_corp(s, "00102618", corp_name="계양전기", corp_cls="Y")
        yield s


def _event(session, **kw):
    return ensure_event(
        session,
        corp_code="00102618",
        report_subtype="piicDecsn",
        original_rcept_dt="20260508",
        rights_type=RightsType.SUBSCRIPTION_WARRANT,
        **kw,
    )


def test_event_key_is_corp_subtype_original_date(session):
    """The same event seen again is the same row; every rcept_no is a version."""
    first = _event(session)
    assert _event(session).id == first.id  # get-or-create on the N2 key

    for rcept_no, nm in [
        ("20260508000928", "주요사항보고서(유상증자결정)"),
        ("20260611000483", "[기재정정]주요사항보고서(유상증자결정)"),
        ("20260724000546", "[기재정정]주요사항보고서(유상증자결정)"),
    ]:
        ensure_version(session, first, rcept_no=rcept_no, rcept_dt=rcept_no[:8], report_nm=nm)
    session.commit()

    assert len(first.versions) == 3
    assert first.latest_version.rcept_no == "20260724000546"
    assert [v.is_correction for v in first.versions] == [False, True, True]
    # ... and re-observing a version does not duplicate it
    ensure_version(session, first, rcept_no="20260724000546", report_nm="x")
    assert len(first.versions) == 3


def test_duplicate_event_key_is_rejected_at_the_database(session):
    from mijual.db.models import Event

    _event(session)
    session.add(
        Event(
            corp_code="00102618",
            report_subtype="piicDecsn",
            original_rcept_dt=__import__("datetime").date(2026, 5, 8),
            rights_type=RightsType.SUBSCRIPTION_WARRANT,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_snapshot_is_idempotent_but_a_changed_body_is_kept(session):
    version = ensure_version(session, _event(session), rcept_no="20260724000546")
    first = ensure_snapshot(session, version, source="list", payload_json={"a": 1})
    assert ensure_snapshot(session, version, source="list", payload_json={"a": 1}).id == first.id
    assert ensure_snapshot(session, version, source="list", payload_json={"a": 2}).id != first.id
    assert ensure_snapshot(session, version, source="document", payload_bytes=b"PK\x03\x04").byte_size == 4
    session.commit()
    assert session.query(Snapshot).count() == 3

    with pytest.raises(ValueError):  # exactly one body, enforced before the DB
        ensure_snapshot(session, version, source="list", payload_json={"a": 1}, payload_bytes=b"x")


def test_correction_kind_from_report_nm():
    f = CorrectionKind.from_report_nm
    assert f("주요사항보고서(유상증자결정)") is CorrectionKind.ORIGINAL
    assert f("[기재정정]주요사항보고서(유상증자결정)") is CorrectionKind.DISCLOSURE
    assert f("[첨부정정]주요사항보고서(유상증자결정)") is CorrectionKind.ATTACHMENT


def test_ensure_columns_adds_a_missing_column_without_touching_rows():
    """The one gap ``create_all`` leaves: P2 has no Alembic, but the S2 corpus
    (291 live requests, unmeasured quota) must survive a one-column addition."""
    from sqlalchemy import inspect, text

    from mijual.db.schema_sync import ensure_columns

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO corp (corp_code, corp_name, updated_at) "
                "VALUES ('00102618', '계양전기', '2026-08-19 00:00:00')"
            )
        )
        conn.execute(text("ALTER TABLE corp DROP COLUMN corp_cls"))

    assert ensure_columns(engine, Base) == ["corp.corp_cls"]
    assert ensure_columns(engine, Base) == []  # idempotent
    assert "corp_cls" in {c["name"] for c in inspect(engine).get_columns("corp")}
    with engine.connect() as conn:
        assert conn.execute(text("SELECT corp_name FROM corp")).scalar() == "계양전기"
