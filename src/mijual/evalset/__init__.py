"""``mijual.evalset`` — the labelled-evalset accuracy measurement (P2.S9).

The phase's last evidence deliverable: a deterministic, stratified sample of the
corpus, a sheet the operator labels by hand, and a report that turns those labels
into **per-field precision + gate-block-rate** at 0 OpenDART requests and 0 LLM
calls.

Three properties are load-bearing and every module here defends one of them.

**The sample is frozen, not recomputed.** ``sample.json`` carries every row the
operator was shown — value, quote, context, gate verdict — plus the corpus-wide
counts the report needs. So the report is regenerable against *exactly* the
sample the labels were made on, even after the corpus moves under it (N55: a
count is only true at the document coverage it was measured at). Nothing in
:mod:`mijual.evalset.report` touches the database.

**The measurement is unbiased where it claims to be.** Two picks are mixed on
purpose: a seeded **random** draw per stratum, and a **forced** set of known hard
cases (철회, 추후결정, span-unresolved, gate failures, the 실권주 cells that
disagree with their own tables). Hard cases are the point of an evalset and also
poison for an average, so every row records how it was picked and the report
computes precision on the random draw alone, listing the forced rows separately.
A ``booster`` pick adds 정정-해석 rows *only* — never the other fields of the same
filing — so no field's own sample stops being random.

**Both error directions are measured.** §3.6's gate is a trust claim with a
price: it blocks fields that were in fact read correctly (▷ 49.2억원 of the S8
headline, N76). So the sheet carries gate-**blocked** rows too, and the report
states the over-blocking rate beside the precision of what the product shows.

Nothing here reads a secret, calls a model, or fetches a filing.
"""

from __future__ import annotations

from mijual.evalset.labels import (
    LABEL_VALUES,
    LabelError,
    load_labels,
    parse_label,
    read_sheet_labels,
)
from mijual.evalset.report import EvalReport, build_report, wilson_interval
from mijual.evalset.sample import (
    DEFAULT_QUOTAS,
    DEFAULT_SEED,
    EvalSample,
    Row,
    load_sample,
    select_sample,
)
from mijual.evalset.sheet import SHEET_COLUMNS, write_sheet

__all__ = [
    "DEFAULT_QUOTAS",
    "DEFAULT_SEED",
    "EvalReport",
    "EvalSample",
    "LABEL_VALUES",
    "LabelError",
    "Row",
    "SHEET_COLUMNS",
    "build_report",
    "load_labels",
    "load_sample",
    "parse_label",
    "read_sheet_labels",
    "select_sample",
    "wilson_interval",
    "write_sheet",
]
