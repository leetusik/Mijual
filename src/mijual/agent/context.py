"""What a tool call is allowed to know about its caller.

One object, constructed **per request by the transport** (`P6.S4`) and passed to
every tool. Its shape is the boundary that makes three of the phase's promises
structural rather than remembered:

* **No tool takes an identity.** A tool's declared arguments are the ones the
  *model* fills in (a query, a filing number, a comment), and the model never
  sees an account id, an email or a session handle — those live here, on the
  server side of the call. So there is no argument a hallucinated function call
  could fill with somebody else's identifier: ``get_portfolio()`` reads the
  caller's own account or the sample, and nothing else exists to ask for.
* **No client-supplied holdings.** R5 kept anonymous state out of the server
  entirely (`P6` Finding 5), so there is no field here for a browser to post a
  portfolio into and no tool argument that could carry one. An anonymous caller
  gets the labelled 샘플 포트폴리오 — the designed answer — and not a payload it
  sent to itself.
* **One clock, upstream.** ``today`` is the KST calendar day every D-day in the
  answer was computed against (`mijual.web.clock`), fixed once for the whole turn
  so two tool calls in one conversation cannot straddle midnight and give the
  reader two different D-days for one deadline.

``session_hash`` is the anonymous thread handle `P6.S1` mints
(:func:`mijual.web.conversationstore.session_hash_or_new`) — random, never
derived from an address or an account — and is used by exactly one tool
(``save_feedback``, as R7's 원 대화 링크).

**The session must be a write session for ``save_feedback`` to survive.**
:func:`~mijual.web.conversationstore.record_feedback` flushes and does not
commit, which is this codebase's rule everywhere: the transport's session owns
the transaction (:func:`mijual.web.deps.get_write_session`).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from mijual.config import Settings
from mijual.db.models import Account

__all__ = ["ToolContext"]


@dataclass(frozen=True)
class ToolContext:
    """The server-side half of a tool call. Constructed once per request."""

    #: The request's own SQLAlchemy session. A **write** session when the turn
    #: may call ``save_feedback``.
    session: Session
    #: The KST calendar day the answer is computed against — ``clock.now().date()``.
    today: date
    #: The anonymous thread handle (`P6.S1`). Not an identity: see the module docstring.
    session_hash: str
    #: The authenticated reader, when there is one. R6: 「계정 로그인 여부와 무관하게
    #: 동일 동작」 — the only thing this changes is *whose* portfolio
    #: ``get_portfolio`` reads, never whether the agent answers.
    account: Account | None = None
    #: 범위 (R6 §범위 모델): the event the widget was opened on, or ``None`` for
    #: 전체 공시. Advisory to the tools — ``search_events`` ranks the scoped event
    #: first and still searches honestly; nothing is hidden because of it.
    scope_rcept_no: str | None = None
    #: Process settings, for ``get_contact``. ``None`` means "load them" — the
    #: transport passes the app's own, and a test passes a literal.
    settings: Settings | None = None

    def config(self) -> Settings:
        """The settings this call reads. Loaded on demand, never cached here."""
        if self.settings is not None:
            return self.settings
        from mijual.config import load_settings

        return load_settings()
