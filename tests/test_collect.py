"""The four things the collector must not get wrong (P2.S2).

Everything runs against the P1 response cache with the client offline — no key,
no network, no invented JSON.
"""

from __future__ import annotations

import pytest
from sqlalchemy import func, select

from mijual.collect import chunk_windows, collect_window, parse_report_nm
from mijual.collect.filters import evaluate
from mijual.collect.pairing import FilingIndex, pair_correction
from mijual.config import SPIKE_CACHE_DIR
from mijual.dart import DartClient
from mijual.db import Event, FilingVersion, make_engine, make_session_factory, session_scope
from mijual.db.models import Base, CorrectionKind

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def _row(rcept_no, report_nm, corp_code="00000001"):
    return {
        "corp_code": corp_code,
        "corp_name": "테스트",
        "rcept_no": rcept_no,
        "rcept_dt": rcept_no[:8],
        "report_nm": report_nm,
    }


def test_report_nm_prefixes_seen_in_the_wild():
    """``[첨부추가]``/``[정정명령부과]`` exist too — reading them as originals
    would mint phantom events (measured on the 2026 KOSPI+KOSDAQ list)."""
    assert parse_report_nm("[기재정정]주요사항보고서(유상증자결정)") == ("기재정정", "유상증자결정")
    assert parse_report_nm("주요사항보고서(회사합병결정)") == (None, "회사합병결정")
    kinds = {nm: CorrectionKind.from_report_nm(f"[{nm}]주요사항보고서(유상증자결정)")
             for nm in ("기재정정", "첨부정정", "첨부추가", "정정명령부과")}
    assert kinds == {
        "기재정정": CorrectionKind.DISCLOSURE,
        "첨부정정": CorrectionKind.ATTACHMENT,
        "첨부추가": CorrectionKind.ATTACHMENT,
        "정정명령부과": CorrectionKind.DISCLOSURE,
    }


def test_chunk_windows_honours_the_three_month_cap():
    # exactly P1's sampling windows — and the API accepts a 3-month edge.
    assert chunk_windows("20260101", "20260818") == [
        ("20260101", "20260331"), ("20260401", "20260630"), ("20260701", "20260818")
    ]
    assert chunk_windows("20260701", "20260819") == [("20260701", "20260819")]


def test_a_correction_chain_lands_on_its_original_not_on_its_predecessor():
    """디모아 filed 6 corrections against one 유증: nearest-earlier *original*."""
    index = FilingIndex()
    original = _row("20260128000001", "주요사항보고서(유상증자결정)")
    chain = [_row(f"202602{d:02d}000001", "[기재정정]주요사항보고서(유상증자결정)")
             for d in (2, 25)] + [_row("20260312000001", "[기재정정]주요사항보고서(유상증자결정)")]
    index.add([original, *chain])

    for correction in chain:
        paired = pair_correction(index, correction, "유상증자결정")
        assert paired.original["rcept_no"] == original["rcept_no"]
        assert paired.method == "earlier"

    # ... and with no original in sight the correction is reported, not guessed.
    orphan = FilingIndex()
    orphan.add(chain)
    assert pair_correction(orphan, chain[-1], "유상증자결정").method == "unpaired"


def test_correctness_filters_suppress_only_what_grants_no_right():
    keep = ["주주배정후 실권주 일반공모", "주주배정증자", "주주우선공모증자"]  # O-5: 우선공모 stays
    drop = ["제3자배정증자", "일반공모증자"]
    assert all(evaluate("piicDecsn", {"ic_mthn": v}) is None for v in keep)
    assert {evaluate("piicDecsn", {"ic_mthn": v}).reason for v in drop} == {"no_warrant_class"}

    small = {"mg_stn": "소규모합병", "aprskh_plnprc": "-", "mgsc_aprskh_expd_bgd": "-"}
    full = {"mg_stn": "해당사항없음", "aprskh_plnprc": "5,649",
            "mgsc_aprskh_expd_bgd": "2026년 07월 07일"}
    bare = {"mg_stn": "해당사항없음", "aprskh_plnprc": "-", "mgsc_aprskh_expd_bgd": "-"}
    assert evaluate("cmpMgDecsn", small).reason == "no_appraisal_right"
    assert evaluate("cmpMgDecsn", bare).reason == "no_appraisal_right"
    assert evaluate("cmpMgDecsn", full) is None
    assert evaluate("piicDecsn", None) is None  # no detail row = undecided, not dropped


@pytest.mark.skipif(not SPIKE_CACHE_DIR.exists(), reason="P1 sample cache is gitignored")
def test_offline_window_collects_the_fixture_event_and_re_runs_clean(tmp_path):
    """계양전기's 유증, end to end and twice: same counts, no duplicate versions."""
    client = DartClient(cache_dir=SPIKE_CACHE_DIR, offline=True)
    engine = make_engine(f"sqlite:///{tmp_path/'collect.db'}")
    Base.metadata.create_all(engine)
    factory = make_session_factory(engine)

    def run():
        return collect_window(
            client, factory, bgn_de="20260401", end_de="20260630", markets=("Y",),
            detail_window=("20260101", "20260818"), with_documents=False,
        )

    def counts():
        with session_scope(factory) as session:
            return tuple(
                session.scalar(select(func.count()).select_from(m))
                for m in (Event, FilingVersion)
            )

    first = run()
    after_first = counts()
    second = run()  # re-running the same window must add nothing (N14)
    assert first.requests == 0 and second.requests == 0  # pure cache, no network
    assert first.target_rows > 50
    assert after_first == counts() == (second.db_before[:2])

    with session_scope(factory) as session:
        event = session.scalar(
            select(Event).where(Event.corp_code == "00102618", Event.report_subtype == "piicDecsn")
        )
        assert str(event.original_rcept_dt) == "2026-05-08"  # the ORIGINAL's 접수일 (N2)
        assert not event.is_suppressed  # 주주배정후 실권주 일반공모 → keeps its 증서
        rcept_nos = {v.rcept_no: v.pairing_method for v in event.versions}
        # 05-08 original + its 06-11 정정 from the window, and the 07-24 version
        # only the detail endpoint knows about (it is the row it returns, §4.2).
        assert rcept_nos == {
            "20260508000928": "original",
            "20260611000483": "earlier",
            "20260724000546": "detail_only",
        }

    assert (first.events_planned, first.versions_planned) == (
        second.events_planned, second.versions_planned
    )
