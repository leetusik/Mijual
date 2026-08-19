"""The four things ② must not get wrong (P2.S7).

Offline by construction: the API rows come from the P1 response cache with the
client offline, the exposure cases are built on SQLite, and nothing here needs a
key, a network, the Postgres corpus or an LLM.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mijual.bodydoc.correction import CorrectionItem
from mijual.cb import facts_from_row, overhang_calendar
from mijual.collect import chunk_windows, parse_report_nm
from mijual.collect.filters import evaluate
from mijual.collect.targets import BY_SUBTYPE_NM, DEFAULT_ENDPOINTS
from mijual.config import SPIKE_CACHE_DIR
from mijual.dart import CacheMiss, DartClient, rows
from mijual.db.models import Base, Extraction, RightsType, Snapshot
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.gates import event_exposure, is_withdrawal_row


def _api_row(corp_code: str, rcept_no: str) -> dict:
    """One real ``cvbdIsDecsn`` row from the P1 cache — never invented JSON."""
    if not SPIKE_CACHE_DIR.exists():
        pytest.skip("P1 sample cache is gitignored")
    client = DartClient(cache_dir=SPIKE_CACHE_DIR, offline=True)
    try:
        body = client.get_json(
            "cvbdIsDecsn", corp_code=corp_code, bgn_de="20260101", end_de="20260818"
        )
    except CacheMiss:  # pragma: no cover - the cache is regenerable, not required
        pytest.skip(f"{rcept_no} is not in the P1 response cache")
    for row in rows(body):
        if row["rcept_no"] == rcept_no:
            return row
    pytest.skip(f"{rcept_no} no longer in the cached window")


def test_the_cb_target_matches_the_issuance_report_and_nothing_that_looks_like_it():
    """``pblntf_ty=B`` carries six CB-ish subtypes; only one is a ② event."""
    assert parse_report_nm("[기재정정]주요사항보고서(전환사채권발행결정)") == (
        "기재정정", "전환사채권발행결정"
    )
    assert BY_SUBTYPE_NM["전환사채권발행결정"].endpoint == "cvbdIsDecsn"
    assert BY_SUBTYPE_NM["전환사채권발행결정"].rights_type is RightsType.CONVERTIBLE_OVERHANG
    # Measured on the 2026 KOSPI+KOSDAQ list: these five would all be collected by
    # a substring match on 전환사채 (and EB is out of scope by D-1).
    for lookalike in (
        "자기전환사채매도결정",
        "자기전환사채만기전취득결정",
        "전환사채매수선택권행사자지정",
        "제3자의전환사채매수선택권행사",
        "신주인수권부사채권발행결정",
        "교환사채권발행결정",
    ):
        assert lookalike not in BY_SUBTYPE_NM
    assert "cvbdIsDecsn" in DEFAULT_ENDPOINTS  # → the daily pipeline collects it
    # ② has no "grants no right" class: every CB issuance creates overhang.
    assert evaluate("cvbdIsDecsn", {"cv_prc": "-"}) is None


def test_the_api_row_parses_into_the_numbers_the_field_matrix_measured():
    """field-matrix §2.1's evidence row, re-derived by this package's parser."""
    facts = facts_from_row(_api_row("00101044", "20260521000775"))
    assert facts.conversion_price == Decimal("4433")
    assert (facts.request_begin, facts.request_end) == (date(2027, 5, 29), date(2031, 4, 29))
    assert (facts.shares, facts.overhang_pct) == (Decimal("2255808"), Decimal("15.65"))
    assert facts.refixing_floor == Decimal("3103")  # gate 6's reference value
    assert facts.complete and facts.days_to_open(date(2026, 9, 7)) == 264

    # A 38.45 % dilution whose 전환청구기간 the filing simply does not state.
    partial = facts_from_row(_api_row("00781202", "20260722000285"))
    assert partial.overhang_pct == Decimal("38.45")
    assert [key for key, _ in partial.missing] == ["cvrqpd_bgd", "cvrqpd_edd"]


def test_r2_exposure_needs_the_api_countdown_and_not_a_본문():
    """②'s countdown is API tier (N6): no 본문 is required, the detail row is."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        ensure_corp(session, "00101044", corp_name="에이프로젠바이오로직스")
        event = ensure_event(
            session,
            corp_code="00101044",
            report_subtype="cvbdIsDecsn",
            original_rcept_dt="20260521",
            rights_type=RightsType.CONVERTIBLE_OVERHANG,
        )
        version = ensure_version(session, event, rcept_no="20260521000775")

        # No detail snapshot at all → nothing to render, and not a suppression.
        assert event_exposure(session, event).state == "no_detail"

        row = _api_row("00101044", "20260521000775")
        snapshot = Snapshot(
            filing_version_id=version.id, source="cvbdIsDecsn",
            payload_json=row, content_sha1="0" * 40,
        )
        session.add(snapshot)
        session.flush()
        exposed = event_exposure(session, event)
        assert exposed.state == "exposable" and exposed.rcept_no == "20260521000775"
        assert exposed.renderable_fields == []  # zero prose fields, still exposable

        # Drop one countdown field: the card would show a blank window → blocked.
        snapshot.payload_json = dict(row, cvrqpd_bgd="-")
        session.flush()
        blocked = event_exposure(session, event)
        assert blocked.state == "incomplete_api_row" and "전환청구기간 개시일" in blocked.note

        # 철회 outranks everything, with ②'s own notice.
        snapshot.payload_json = row
        event.add_flag("withdrawn")
        session.flush()
        assert event_exposure(session, event).notice_ko == "이 사채 발행은 철회되었습니다"

        # The calendar reads exactly the exposure contract's verdict.
        event.drop_flags("withdrawn")
        event.exposure_state = "exposable"
        session.flush()
        calendar = overhang_calendar(session, today=date(2026, 9, 7))
        assert len(calendar.opening_within(365)) == 1
        assert calendar.opening_within(180) == []  # opens 2027-05-29, not in 180d


def test_the_withdrawal_shape_generalises_to_the_cb_subtype():
    """``전환사채권 발행결정 → … 철회`` passes the same four shape rules as ①'s."""

    def item(name: str, before: str, after: str) -> CorrectionItem:
        return CorrectionItem(
            item=name, item_span=None, reason=None, reason_span=None,
            before=before, before_span=None, after=after, after_span=None,
        )

    assert is_withdrawal_row(
        item("전환사채권 발행결정", "전환사채권 발행결정", "전환사채권 발행결정 철회")
    )
    assert is_withdrawal_row(item("전 항목", "-", "전환사채 발행 결정 철회"))
    # ②'s own boilerplate: a *field* describing a 청구 철회 is not the filing being
    # withdrawn, and a numbered 항목 is a field inside the filing, never the filing.
    assert not is_withdrawal_row(
        item("9. 전환에 관한 사항", "전환청구를 철회할 수 있다", "전환청구를 철회할 수 있다")
    )
    assert not is_withdrawal_row(item("기타", "-", "청약 철회"))


def test_gate_8_derives_the_lockup_release_date_instead_of_trusting_the_model():
    """§7 #8, corrected by the corpus: a CB states a *duration*, not a date."""
    from mijual.calc import lockup_release_date
    from mijual.gates import evaluate_field
    from mijual.gates.context import VersionContext

    assert lockup_release_date(date(2025, 9, 12), 12) == date(2026, 9, 12)
    assert lockup_release_date(date(2025, 1, 31), 1) == date(2025, 2, 28)  # clamped
    assert lockup_release_date(None, 12) is None

    ctx = VersionContext(
        event=None, version=None, doc=None, labels=None, correction=None,
        api={"pymd": "2025년 09월 12일"},
    )

    def row(value):
        return Extraction(
            field_key="lockup_release", status="extracted", value=value, quote="근거",
            span_status="resolved", span_verified=True, schema_version="v1",
        )

    # 31 of 62 real rows look like this: a duration and no date. Derived, passed.
    derived = evaluate_field(row({"months": 12, "release_date": None}), ctx)
    assert derived.status == "passed" and "2026-09-12" in derived.note
    # A model-stated date is now checked *against* the API-derived one …
    assert evaluate_field(row({"months": 12, "release_date": "2026-09-12"}), ctx).status == "passed"
    off = evaluate_field(row({"months": 12, "release_date": "2027-12-30"}), ctx)
    assert off.status == "failed" and off.reason_code == "release_date_not_derived"
    # … and a 전매제한 the filing does not quantify is nothing to judge.
    silent = evaluate_field(row({"months": None, "release_date": None}), ctx)
    assert silent.status == "not_evaluable" and silent.exposable is False


def test_the_backfill_window_chunks_2025_H2_inside_the_three_month_cap():
    """D-1's condition: discovery back to 2025-06, in list.json-legal chunks."""
    assert chunk_windows("20250601", "20251231") == [
        ("20250601", "20250831"), ("20250901", "20251130"), ("20251201", "20251231")
    ]


def test_routine_extraction_runs_cheap_and_reasoning_keeps_the_preset():
    """Operator directive 2026-08-20: thinking level is per task, LOW by default.

    Measured live on one real ``r2_prose`` prompt (11,491 prompt tokens):
    preset → 866 thinking tokens, explicit ``LOW`` → **0**, with every *gated*
    value identical. Asserted here structurally so the map cannot drift back.
    """
    from mijual.extract.client import GeminiClient

    client = GeminiClient(api_key="unused", dry_run=True)
    assert client.thinking_for("r2_prose") == "LOW"
    assert client.thinking_for("r1_prose") == client.thinking_for("r3_prose") == "LOW"
    # Reasoning keeps the operator's preset — ``None`` means "send no config".
    assert client.thinking_for("correction") is None
    # An unlisted task is cheap by default, never silently HIGH.
    assert client.thinking_for("some_new_reader") == "LOW"
    # The level a call ran at is recorded, not assumed.
    result = client.generate_json(prompt="x", schema={}, task="r2_prose")
    assert result.thinking_level == "LOW"
    assert client.generate_json(prompt="x", schema={}, task="correction").thinking_level is None
