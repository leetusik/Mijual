"""The mailer seam — an interface, and a development transport that sends nothing.

P5 has **no email dependency and no deploy dependency**. The D-day alert channel
— provider, scheduled send, and the mail body R5 designs — is **P4's** (phase
note 6), and a password reset that needed a real transport would have dragged
that whole decision into this phase. So the reset flow goes through this seam,
and P4 plugs the real transport into the same two methods.

**A message carries data, not copy.** :class:`Message` has ``kind`` and ``data``
and no rendered subject or body, and that is a Korean-only-surface rule rather
than a design taste: user-visible copy is locked and comes from the design's own
inventory, so a P5 module that wrote a Korean subject line would be **inventing
product copy** — a design change. The transport that eventually sends real mail
renders it, in P4, from R5's signed mail spec (제목 "[미주알] {종목} — {마감명}
D-{n} ({date})", 사실 블록, 푸터). Until then :class:`ConsoleMailer` prints the
structured message, in English, to the server's own log.

Where it is used: ``mijual.web`` sets one on ``app.state.mailer``
(:func:`mijual.web.app.create_app` takes a ``mailer=`` argument), and the auth
router hands it a ``password_reset`` message whose ``data`` carries the link and
its expiry.

This module imports nothing but the standard library — in particular nothing that
can spend an OpenDART request or a model call, so it is safe on a request path.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from typing import IO, Mapping, Protocol, runtime_checkable

__all__ = ["ConsoleMailer", "Mailer", "Message", "PASSWORD_RESET"]

log = logging.getLogger(__name__)

#: The one message kind P5 sends. P4's D-day alert adds its own.
PASSWORD_RESET = "password_reset"


@dataclass(frozen=True)
class Message:
    """What to send, to whom — never *how it reads*.

    ``kind`` names the template the transport will render; ``data`` carries the
    values it renders with (for :data:`PASSWORD_RESET`: ``url`` and
    ``expires_at``). No key of ``data`` is ever a sentence.
    """

    to: str
    kind: str
    data: Mapping[str, str] = field(default_factory=dict)


@runtime_checkable
class Mailer(Protocol):
    """The seam. P4 implements this over a real provider and nothing else moves."""

    def send(self, message: Message) -> None: ...


class ConsoleMailer:
    """Development transport: writes the message server-side, sends no mail.

    The reset link is printed in full, because the developer running the service
    is the intended recipient in P5 — and printed **server-side only**: it never
    travels in an HTTP response, which would defeat 가입 여부 비노출 exactly as
    thoroughly as a different response body would.
    """

    def __init__(self, stream: IO[str] | None = None) -> None:
        #: ``None`` means "the process's own stderr at call time" — a test can
        #: pass a buffer, and nothing captures a stream at import.
        self._stream = stream

    def send(self, message: Message) -> None:
        rendered = " ".join(f"{k}={v}" for k, v in message.data.items())
        line = f"[mail:{message.kind}] to={message.to} {rendered}"
        stream = self._stream if self._stream is not None else sys.stderr
        print(line, file=stream, flush=True)
        log.info("console mailer: %s to %s", message.kind, message.to)
