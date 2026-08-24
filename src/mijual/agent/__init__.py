"""`mijual.agent` — the AI 질문 agent's server side (P6).

**Why this is a top-level package and not a module under `mijual.web`.** The
architecture's loudest invariant is "no OpenDART call and no LLM call happens in a
request path", and P6's agent is an LLM call in a request path by design — SSE
streaming cannot be anything else. So the boundary is redrawn rather than
quietly broken (`P6` Finding 1): ``mijual.web`` still imports no spending module
and still speaks HTTP in exactly one file, and **the model is reached only through
this package**. `P6.S4` re-aimed the AST scans onto that shape — ``mijual.web``
imports no OpenDART module and no model SDK, and ``mijual.dart`` /
``mijual.collect`` / ``mijual.extract`` stay out of ``mijual.agent`` too. The
agent reads persisted rows, it never collects or extracts, and it does not borrow
``mijual.extract.client``'s Gemini wrapper however convenient that would be.

What lives here, in the order the phase builds it:

* :mod:`mijual.agent.context` — :class:`~mijual.agent.context.ToolContext`, the
  server-side half of a tool call (session, KST day, anonymous handle, account or
  ``None``, 범위). No tool takes an identity as an argument.
* :mod:`mijual.agent.tools` — the six tools: R6's five, returning **verified
  contract values only**, each with its signed 사실 행 and its citations, plus
  R16's ``calculate`` — the one auditable window onto arithmetic, a window onto
  :mod:`mijual.calc` rather than a second implementation of it.
* :mod:`mijual.agent.copy` — the Korean strings, transcribed from R6 with their
  provenance. Inventing a Korean sentence is a design change.
* :mod:`mijual.agent.declarations` — the Gemini ``FunctionDeclaration`` set, built
  from plain data with a **local** SDK import, so the package imports with no SDK
  and no credential present.
* :mod:`mijual.agent.client` — the agent's **own** streaming Gemini client, with
  the two ideas copied (never imported) from ``mijual.extract``: a structural call
  budget and a ▷ usage ledger. Also the neutral message/chunk types the loop
  speaks, so a test can drive the real loop with a scripted fake.
* :mod:`mijual.agent.instructions` — the system instruction. It **advises**; it
  never commands a tool call.
* :mod:`mijual.agent.citations` — 인용 강제 as a gate on the generation boundary:
  an unverified claim cannot enter the stream (R6), and the never-compute rule
  rides the same gate.
* :mod:`mijual.agent.events` — the typed event stream `P6.S4` serializes and
  `P6.S5` renders, ending in one terminal that carries everything persistence needs.
* :mod:`mijual.agent.loop` — :func:`~mijual.agent.loop.run_turn`, the autonomous
  function-calling turn. **The model decides** which tools to call, in what order,
  across how many rounds, and when it is ready to answer.
* Nothing here speaks HTTP or persists a turn: `P6.S4`'s transport
  (:mod:`mijual.web.ask`) streams these events as SSE, owns the turn's
  transaction, and stores the terminal as one anonymous row.

Importing this package costs no connection, no credential and no SDK.
"""

from __future__ import annotations

from mijual.agent.context import ToolContext
from mijual.agent.events import (
    AgentEvent,
    CitationEvent,
    FooterEvent,
    LinksEvent,
    RefusalEvent,
    TextEvent,
    ToolRowEvent,
    TurnEnd,
)
from mijual.agent.loop import HistoryTurn, TurnBudget, run_turn
from mijual.agent.tools import (
    TOOL_NAMES,
    Citation,
    ToolResult,
    UnknownTool,
    calculate,
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
    "AgentEvent",
    "Citation",
    "CitationEvent",
    "FooterEvent",
    "HistoryTurn",
    "LinksEvent",
    "RefusalEvent",
    "TextEvent",
    "ToolContext",
    "ToolResult",
    "ToolRowEvent",
    "TurnBudget",
    "TurnEnd",
    "UnknownTool",
    "calculate",
    "call_tool",
    "citations_in",
    "fact_rows",
    "get_contact",
    "get_event",
    "get_portfolio",
    "run_turn",
    "save_feedback",
    "search_events",
]
