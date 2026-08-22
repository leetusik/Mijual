"""What the model is told the five tools are — the Gemini function declarations.

The agent is an **agent, not a chain** (the operator's binding addition to this
phase): the model chooses which tool to call, in what order, and across as many
rounds as it needs. That choice is only as good as these declarations, so the
descriptions carry the product's rules — *values are already computed, quote them
and never do arithmetic; a claim needs the span that backs it; nothing may be
invented when a tool says it found nothing* — rather than only naming the
parameters.

**Two layers, on purpose.** :data:`TOOL_SPECS` is plain data (names, English
descriptions, JSON-Schema parameters) and imports nothing; :func:`declarations`
turns it into ``google.genai.types.FunctionDeclaration`` with a **local import**
of the SDK, the convention :mod:`mijual.extract.client` uses. So this module —
and therefore the whole ``mijual.agent`` package — imports cleanly with no SDK
installed and no credential in the environment, which is what lets `P6.S2`'s
tests run the tools against the corpus for free.

The names match :data:`mijual.agent.tools.TOOL_NAMES` exactly and a test pins
them together: a declaration the dispatcher cannot execute would be a tool the
model calls into nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["TOOL_SPECS", "ToolSpec", "declarations", "spec_of"]


@dataclass(frozen=True)
class ToolSpec:
    """One tool as the model sees it. English — this is internal, not a surface."""

    name: str
    description: str
    #: JSON Schema for the arguments. ``None`` = the tool takes none.
    parameters: dict[str, Any] | None = field(default=None)


_NEVER_COMPUTE = (
    "Every number in the result is already computed upstream in KST and is final: "
    "quote it exactly as given, never recompute, re-derive or do arithmetic on it. "
    "A value tagged estimated=true must keep its 「추정」 mark in the answer. "
    "A value that is absent does not exist — never fill it in."
)

TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        name="search_events",
        description=(
            "Search the corpus for disclosure events (유상증자/전환사채/주식매수청구권) by "
            "company name, ticker, or a 14-digit DART filing number (rcept_no). Returns a "
            "list of candidates — several matches are normal and may all be named. Only "
            "events that pass the exposure contract are searchable; withdrawn, suppressed "
            "and gate-failed events never appear here. When count is 0 the result carries "
            "the exact Korean sentence to state (none_found_ko) and a pointer to the board: "
            "state it verbatim and never guess at what the reader might have meant — but if "
            "the query was a filing number, call get_event first, because a withdrawn event "
            "is readable by number without being searchable. "
            "Each hit identifies an event (company, type, rcept_no, countdown); call "
            "get_event for the quotable field values of the one that matters. " + _NEVER_COMPUTE
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Company name, 6-digit ticker, or 14-digit rcept_no as the reader "
                        "wrote it. Do not translate or normalise it."
                    ),
                }
            },
            "required": ["query"],
        },
    ),
    ToolSpec(
        name="get_event",
        description=(
            "Read one event's full verification contract by its 14-digit rcept_no: identity, "
            "the governing countdown, and every field that passed the gate with its verbatim "
            "quote, character span and source filing number. This is the only source of "
            "quotable 본문 passages — a factual claim about an event must rest on a quote "
            "returned here (API-tier facts have no quote and use rcept_no as the citation "
            "handle). A field that is missing from the payload does not exist for the reader: "
            "say so, do not infer it. A withdrawn event returns state='withdrawn' with its "
            "notice and the correction row that retracted it. found=false means the filing "
            "number is unknown or not readable. " + _NEVER_COMPUTE
        ),
        parameters={
            "type": "object",
            "properties": {
                "rcept_no": {
                    "type": "string",
                    "description": "The 14-digit DART filing number, digits only.",
                }
            },
            "required": ["rcept_no"],
        },
    ),
    ToolSpec(
        name="get_portfolio",
        description=(
            "Read the current reader's own portfolio: their holdings and the upcoming/past "
            "deadline rows with D-day, ratios and amounts already computed upstream. Takes no "
            "arguments — it always reads the caller's own session and can read nobody else's. "
            "For an anonymous reader it returns the fixed sample portfolio with sample=true; "
            "in that case the answer must say 구성 예시 (it is an illustrative composition, "
            "not the reader's holdings). " + _NEVER_COMPUTE
        ),
    ),
    ToolSpec(
        name="save_feedback",
        description=(
            "Save the reader's feedback about this product into the operator's review queue. "
            "Call it when the reader offers an opinion, a complaint or a suggestion about "
            "Mijual itself. The email is optional and only for a reply — pass it only if the "
            "reader volunteered it; never ask for it in order to save. ok=false means the "
            "save failed and the reader should be offered a retry."
        ),
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The reader's comment, in their own words.",
                },
                "email": {
                    "type": "string",
                    "description": "Reply address, only if the reader volunteered one.",
                },
            },
            "required": ["text"],
        },
    ),
    ToolSpec(
        name="get_contact",
        description=(
            "Read the operator's contact string from deployment settings. Call it when the "
            "reader asks how to reach the operator. configured=false means no contact string "
            "exists yet — say that plainly and never invent, guess or substitute an address, "
            "a form, or a promise that one is coming."
        ),
    ),
)


def spec_of(name: str) -> ToolSpec | None:
    """One tool's declaration data by name."""
    return next((spec for spec in TOOL_SPECS if spec.name == name), None)


def _schema(node: dict[str, Any], types: Any) -> Any:
    """A JSON-Schema fragment as ``types.Schema``, built field by field.

    Constructed explicitly rather than handed to the SDK as a dict: the SDK's
    schema type is its own model with its own enum for ``type``, and a silently
    ignored key here would become a parameter the model never fills in.
    """
    kind = str(node.get("type", "string")).upper()
    properties = {
        key: _schema(value, types) for key, value in (node.get("properties") or {}).items()
    }
    return types.Schema(
        type=kind,
        description=node.get("description"),
        properties=properties or None,
        required=list(node.get("required") or ()) or None,
    )


def declarations() -> list[Any]:
    """The five as ``google.genai.types.FunctionDeclaration``, for `P6.S3`'s loop.

    The SDK is imported **here**, inside the call, so importing this package
    costs nothing and needs nothing installed (:mod:`mijual.extract.client`'s
    convention, and the reason the tool tests run with no credential).
    """
    from google.genai import types  # local import: the SDK is only needed live

    return [
        types.FunctionDeclaration(
            name=spec.name,
            description=spec.description,
            parameters=(_schema(spec.parameters, types) if spec.parameters else None),
        )
        for spec in TOOL_SPECS
    ]
