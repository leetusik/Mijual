"""The evalset: the draw is deterministic, the import is strict, the math is honest (P2.S9).

Offline and database-free by construction — the sampler's draw and the whole
report are pure functions, which is the property that lets the accuracy numbers
be regenerated long after the corpus has moved (N55/N83).
"""

from __future__ import annotations

import pytest

from mijual.evalset.labels import (
    LabelError,
    Labels,
    Provenance,
    load_labels,
    parse_label,
    read_sheet_labels,
)
from mijual.evalset.report import build_report, wilson_interval
from mijual.evalset.sample import CORRECTION_FIELD, EvalSample, Row, select_sample

FIELDS_R1 = ("warrant_trading_period", "subscription_agents", CORRECTION_FIELD)


def _row(rcept_no: str, field_key: str, *, stratum="R1_prose", gate="passed", hard="") -> Row:
    return Row(
        unit=f"extraction:{rcept_no}",
        kind="extraction",
        stratum=stratum,
        rights="R1",
        corp_code="00000001",
        corp_name=f"corp{rcept_no[-2:]}",
        rcept_no=rcept_no,
        field_key=field_key,
        field_ko=field_key,
        field_order=1,
        extracted_value="v",
        quote="q",
        context="c",
        gate_status=gate,
        gate_reason_code="" if gate == "passed" else "span_unresolved",
        gate_reason_ko="",
        span_status="resolved",
        is_current=True,
        hard_case=hard,
        source_id=int(rcept_no),
    )


def _pool() -> list[Row]:
    rows: list[Row] = []
    for index in range(20):
        rcept_no = f"2026010100{index:04d}"
        for field_key in FIELDS_R1:
            rows.append(_row(rcept_no, field_key))
    rows.append(_row("20260101009999", "warrant_trading_period", gate="failed", hard="span_unresolved"))
    return rows


# --- the draw --------------------------------------------------------------
def test_the_draw_is_deterministic_and_keeps_the_hard_case():
    quotas = {"R1_prose": 5}
    first = select_sample(_pool(), quotas=quotas, booster=3, seed=20260907)
    second = select_sample(_pool(), quotas=quotas, booster=3, seed=20260907)
    assert [(r.row_id, r.rcept_no, r.field_key, r.pick) for r in first] == [
        (r.row_id, r.rcept_no, r.field_key, r.pick) for r in second
    ]
    # The known-difficult filing is forced in, and a different seed moves the
    # random draw without ever dropping it.
    assert "20260101009999" in {r.rcept_no for r in first if r.pick == "forced"}
    other = select_sample(_pool(), quotas=quotas, booster=3, seed=1)
    assert "20260101009999" in {r.rcept_no for r in other if r.pick == "forced"}
    assert {r.rcept_no for r in first if r.pick == "random"} != {
        r.rcept_no for r in other if r.pick == "random"
    }


def test_a_booster_filing_contributes_only_its_correction_row():
    """Otherwise field 10's boost would quietly bias every other field's sample."""
    chosen = select_sample(_pool(), quotas={"R1_prose": 5}, booster=4, seed=20260907)
    boosted = [r for r in chosen if r.pick == "booster"]
    assert boosted and {r.field_key for r in boosted} == {CORRECTION_FIELD}
    assert len({r.unit for r in boosted}) == 4


# --- reading the labels back ------------------------------------------------
def test_an_unknown_label_is_refused_and_nothing_is_imported(tmp_path):
    sample = EvalSample(
        seed=1, generated_at="", quotas={}, booster=0, corpus={}, strata={},
        field_stats={}, correction_recall={}, duplicates_collapsed=0,
        rows=[_row("20260101000001", "warrant_trading_period")],
    )
    sample.rows[0] = Row(**{**sample.rows[0].__dict__, "row_id": "E0001"})
    path = tmp_path / "sheet.csv"
    path.write_text(
        "row_id,label,corrected_value\nE0001,probably?,\n", encoding="utf-8"
    )
    with pytest.raises(LabelError, match="unknown label"):
        read_sheet_labels(path, sample)

    path.write_text("row_id,label,corrected_value\nE0001, O ,2026-09-01\n", encoding="utf-8")
    labels = read_sheet_labels(path, sample)
    assert labels.labelled == {"E0001": "correct"}
    assert labels.corrections == {"E0001": "2026-09-01"}
    assert parse_label("") is None


# --- provenance -------------------------------------------------------------
def test_labels_cannot_be_written_unstamped_and_the_report_prints_the_stamp(tmp_path):
    """The judge travels inside the artifact, and the report reads it from there."""
    rows = [Row(**{**_row("20260101000001", "warrant_trading_period").__dict__, "row_id": "E0001"})]
    sample = EvalSample(
        seed=1, generated_at="", quotas={}, booster=0, corpus={}, strata={},
        field_stats={"warrant_trading_period": {"order": 1, "total": 1, "blocked": 0}},
        correction_recall={}, duplicates_collapsed=0, rows=rows,
    )
    sheet = tmp_path / "sheet.csv"
    sheet.write_text("row_id,label,corrected_value\nE0001,correct,\n", encoding="utf-8")

    unstamped = read_sheet_labels(sheet, sample)
    with pytest.raises(LabelError, match="without provenance"):
        unstamped.write(tmp_path / "labels.json")
    assert not (tmp_path / "labels.json").exists()
    # An unstamped file still loads, and the report says so rather than implying a judge.
    assert "미기재" in build_report(sample, unstamped).render()

    stamp = Provenance.stamp("claude (cross-model)", "operator directive — not ground truth")
    path = read_sheet_labels(sheet, sample, provenance=stamp).write(tmp_path / "labels.json")
    reloaded = load_labels(path)
    assert reloaded.provenance == stamp and reloaded.labelled == {"E0001": "correct"}
    assert "claude (cross-model)" in build_report(sample, reloaded).render()
    with pytest.raises(LabelError, match="empty"):
        Provenance.stamp("  ")


# --- the arithmetic ---------------------------------------------------------
def test_the_report_scores_both_error_directions_and_ignores_forced_rows():
    rows = []
    for index, (gate, pick) in enumerate(
        [("passed", "random")] * 4 + [("failed", "random")] * 2 + [("failed", "forced")],
        start=1,
    ):
        row = _row(f"2026010100{index:04d}", "warrant_trading_period", gate=gate)
        rows.append(Row(**{**row.__dict__, "pick": pick, "row_id": f"E{index:04d}"}))
    sample = EvalSample(
        seed=1, generated_at="", quotas={}, booster=0, corpus={}, strata={},
        field_stats={
            "warrant_trading_period": {"order": 1, "total": 100, "blocked": 20, "reasons": {}}
        },
        correction_recall={}, duplicates_collapsed=0, rows=rows,
    )
    labels = Labels(
        source="test",
        labelled={
            "E0001": "correct", "E0002": "correct", "E0003": "partial", "E0004": "skip",
            "E0005": "correct", "E0006": "wrong",
            "E0007": "correct",  # forced — must not move any rate
        },
        corrections={},
    )
    score = build_report(sample, labels).scores["warrant_trading_period"]

    assert (score.shown.correct, score.shown.partial, score.shown.skipped) == (2, 1, 1)
    assert score.shown.strict == pytest.approx(2 / 3)  # skip left the denominator
    assert score.shown.lenient == pytest.approx(1.0)
    assert score.over_block_rate == pytest.approx(0.5)  # 1 of 2 blocked rows was right
    assert score.block_rate == pytest.approx(0.2)  # corpus-wide, not sample-wide
    assert score.over_blocked_estimate == pytest.approx(10.0)


def test_wilson_stays_honest_where_the_textbook_interval_collapses():
    low, high = wilson_interval(21, 21)
    assert low < 1.0 and high == 1.0  # 21/21 is not "100% ± 0"
    assert wilson_interval(0, 0) is None
