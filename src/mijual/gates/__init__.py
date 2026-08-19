"""``mijual.gates`` — §3.6 layer 2, the product's trust claim in code.

Layer 1 (``mijual.extract``) reads. **This layer judges**, and the invariant it
enforces has no exceptions anywhere in the phase:

    a field is exposed **only** after passing its named deterministic gate; a
    field that fails is recorded with a reason code and **never shown**.

Four things live here.

**The gates** (:mod:`mijual.gates.rules`) — one function per field-matrix §7 row,
plus a citation gate that runs first on every field: a value whose quote cannot
be re-located in the stored snapshot is not a citation, so it is blocked. Every
comparison is against evidence the model never saw — 본문 labels and the stored
API detail row — which is N38's *never put the gate's reference value in the
prompt* read from the other side.

**The verdict vocabulary** (:mod:`mijual.gates.outcome`) — ``passed`` / ``failed``
/ ``tbd`` / ``not_evaluable``. ``tbd`` exists because the corpus has a third
document state: a 정정 that suspends the schedule (``추후결정``) is a *verified
citation with null dates*, not a missing field, and the board must show it as
추후결정 rather than fall back to the superseded date (N40).

**The 철회 detector** (:mod:`mijual.gates.withdrawal`) — two currently-exposable ①
events have already been withdrawn and every layer above says they are healthy
(N39). The signal is one 정정사항 row shaped ``유상증자 결정 → 유상증자 철회``; a
keyword test on ``철회`` does not work and is measured not to.

**The exposure contract** (:mod:`mijual.gates.exposure`) — the single derivation
P3 reads, event level and field level. P3 never decides exposure itself.

All of it is **LLM-free and request-free**: pure functions over stored snapshots
plus one persisted verdict per row. All *arithmetic* the product displays lives in
:mod:`mijual.calc`, deterministic by §3.6's own rule.

    .venv/bin/python -m mijual.gates run       # judge the corpus, persist verdicts
    .venv/bin/python -m mijual.gates summary   # what is exposable today
    .venv/bin/python -m mijual.gates show 20260724000546
"""

from __future__ import annotations

from mijual.gates.context import VersionContext, version_context
from mijual.gates.exposure import (
    BLOCKING_FLAGS,
    EventExposure,
    FieldView,
    WITHDRAWN_NOTICE_KO,
    current_version,
    event_exposure,
    exposure_of_all,
)
from mijual.gates.outcome import (
    FAILED,
    NOT_EVALUABLE,
    PASSED,
    TBD,
    Check,
    Outcome,
    REASON_LABELS_KO,
)
from mijual.gates.rules import GATES, citation_check, evaluate_field
from mijual.gates.runner import GateReport, gate_event, run_gates
from mijual.gates.withdrawal import Withdrawal, detect_withdrawal, is_withdrawal_row

__all__ = [
    "BLOCKING_FLAGS",
    "Check",
    "EventExposure",
    "FAILED",
    "FieldView",
    "GATES",
    "GateReport",
    "NOT_EVALUABLE",
    "Outcome",
    "PASSED",
    "REASON_LABELS_KO",
    "TBD",
    "VersionContext",
    "WITHDRAWN_NOTICE_KO",
    "Withdrawal",
    "citation_check",
    "current_version",
    "detect_withdrawal",
    "evaluate_field",
    "event_exposure",
    "exposure_of_all",
    "gate_event",
    "is_withdrawal_row",
    "run_gates",
    "version_context",
]
