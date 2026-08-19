"""Collection layer for ① 유상증자 신주인수권 and ③ 주식매수청구권.

    .venv/bin/python -m mijual.collect --bgn 20260701 --end 20260819

Four things this layer exists to get right, all of them measured upstream:

1. **Discovery runs on ``list.json``, never on the detail endpoints.** The
   detail window filters on the *original* 접수일, so a "yesterday's filings"
   poll misses 100% of 정정 (40/40, note N3) — and 정정 outnumber originals
   2.6 : 1 for ①.
2. **Every version of an event is kept and snapshotted.** The detail endpoint
   returns one row per event, newest version only, and superseded structured
   values are unrecoverable (§4.2/N2).
3. **정정 are paired to their original before storage**, because the event key
   is ``(corp_code, report_subtype, original_rcept_dt)``.
4. **The correctness filters suppress, they do not delete** (N15) — a
   제3자배정 유증 or a 소규모합병 stays collected with a reason code.

See :mod:`mijual.collect.runner` for the run itself.
"""

from mijual.collect.discovery import chunk_windows, discover, parse_report_nm
from mijual.collect.filters import Suppression, evaluate
from mijual.collect.pairing import FilingIndex, Pairing, pair_correction
from mijual.collect.runner import CollectionReport, collect_window
from mijual.collect.targets import TARGETS, Target

__all__ = [
    "CollectionReport",
    "FilingIndex",
    "Pairing",
    "Suppression",
    "TARGETS",
    "Target",
    "chunk_windows",
    "collect_window",
    "discover",
    "evaluate",
    "pair_correction",
    "parse_report_nm",
]
