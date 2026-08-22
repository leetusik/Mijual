"""`mijual.agent` — the AI 질문 agent's server side (P6).

**Why this is a top-level package and not a module under `mijual.web`.** The
architecture's loudest invariant is "no OpenDART call and no LLM call happens in a
request path", and P6's agent is an LLM call in a request path by design — SSE
streaming cannot be anything else. So the boundary is redrawn rather than
quietly broken (`P6` Finding 1): ``mijual.web`` still imports no spending module
and still speaks HTTP in exactly one file, and **the model is reached only through
this package**. `P6.S4` re-aims the two AST scans onto that shape and adds the
third: ``mijual.dart`` / ``mijual.collect`` / ``mijual.extract`` must stay out of
``mijual.agent`` too — the agent reads persisted rows, it never collects or
extracts, and it does not borrow ``mijual.extract.client``'s Gemini wrapper
however convenient that would be.

What lives here, in the order the phase builds it:

* :mod:`mijual.agent.context` — :class:`~mijual.agent.context.ToolContext`, the
  server-side half of a tool call (session, KST day, anonymous handle, account or
  ``None``, 범위). No tool takes an identity as an argument.
* :mod:`mijual.agent.tools` — the five tools R6 signs, returning **verified
  contract values only**, each with its signed 사실 행 and its citations.
* :mod:`mijual.agent.copy` — the Korean strings, transcribed from R6 with their
  provenance. Inventing a Korean sentence is a design change.
* :mod:`mijual.agent.declarations` — the Gemini ``FunctionDeclaration`` set, built
  from plain data with a **local** SDK import, so the package imports with no SDK
  and no credential present.
* `P6.S3` adds the autonomous function-calling loop and `P6.S4` the transport.

Importing this package costs no connection, no credential and no SDK.
"""

from __future__ import annotations

from mijual.agent.context import ToolContext
from mijual.agent.tools import (
    TOOL_NAMES,
    Citation,
    ToolResult,
    UnknownTool,
    call_tool,
    citations_in,
    fact_rows,
    get_contact,
    get_event,
    get_portfolio,
    save_feedback,
    search_events,
)

__all__ = [
    "TOOL_NAMES",
    "Citation",
    "ToolContext",
    "ToolResult",
    "UnknownTool",
    "call_tool",
    "citations_in",
    "fact_rows",
    "get_contact",
    "get_event",
    "get_portfolio",
    "save_feedback",
    "search_events",
]
