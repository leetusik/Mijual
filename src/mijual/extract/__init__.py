"""``mijual.extract`` — §3.6 **layer 1**: the schema-based reading layer.

This is the only part of the pipeline that spends money and the only one whose
output is non-deterministic, so it is fenced in on four sides:

**It reads only what no parser can.** The registry (:mod:`mijual.extract.fields`)
is field-matrix §7's closed list of 10 targets. Everything else the service shows
is an ``API`` field or a ``본문-label`` row that :mod:`mijual.bodydoc` already
reads for free — paying an LLM for those is the phase's explicit anti-rule.

**It never supplies its own evidence.** The model returns a value *and a verbatim
quote*; the citation span is then located deterministically in the stored
snapshot (:mod:`mijual.extract.locate`). A quote that cannot be found leaves the
extraction ``span_unresolved`` — recorded, never exposed. No span is ever taken
from the model.

**It never calculates.** §3.6 fixes calculation as deterministic: 금액 환산 and
D-day are Python's job, gates are ``P2.S5``'s, and this layer only normalises the
shape of what the document says (ISO dates, decimal ratios, enums).

**It spends under a ceiling.** :class:`~mijual.extract.client.GeminiClient` counts
every call, refuses the one past ``max_calls``, and prices the run from a
published rate card (▷ estimate — the token counts are measured, the dollars are
not billed figures).

Entry points::

    python -m mijual.extract probe                  # one call: does the preset think?
    python -m mijual.extract run --rights R1        # ① fields 1-5 over the corpus
    python -m mijual.extract corrections --rights R1  # §7 #10, re-extract + diff
    python -m mijual.extract show <rcept_no>        # what was stored, with spans
"""

from __future__ import annotations

from mijual.extract.client import (
    CallBudgetExceeded,
    CallResult,
    DEFAULT_MODEL,
    GeminiClient,
    GeminiError,
    Usage,
    UsageLedger,
)
from mijual.extract.fields import FIELDS, SCHEMA_VERSION, TASKS, FieldSpec, TaskSpec, response_schema
from mijual.extract.inputs import DocumentInput, build_input
from mijual.extract.locate import Located, QuoteLocator, locate_quote
from mijual.extract.prompt import build_correction_prompt, build_field_prompt
from mijual.extract.runner import (
    ExtractionReport,
    run_corrections,
    run_extraction,
    select_targets,
)
from mijual.extract.store import record_call, upsert_extraction

__all__ = [
    "CallBudgetExceeded",
    "CallResult",
    "DEFAULT_MODEL",
    "DocumentInput",
    "ExtractionReport",
    "FIELDS",
    "FieldSpec",
    "GeminiClient",
    "GeminiError",
    "Located",
    "QuoteLocator",
    "SCHEMA_VERSION",
    "TASKS",
    "TaskSpec",
    "Usage",
    "UsageLedger",
    "build_correction_prompt",
    "build_field_prompt",
    "build_input",
    "locate_quote",
    "record_call",
    "response_schema",
    "run_corrections",
    "run_extraction",
    "select_targets",
    "upsert_extraction",
]
