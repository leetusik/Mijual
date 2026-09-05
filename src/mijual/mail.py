"""The mail seam, its rendering step, and the real SMTP transport.

**P5 built the seam; `P4.S2` filled it.** ``Message(to, kind, data)`` and the
:class:`Mailer` protocol were shaped so that the password-reset flow could ship
without dragging a provider decision into that phase, and so that plugging a real
transport in would touch no route. That is what happened here: this module grew
:func:`render` and :class:`SmtpMailer`, and
:func:`mijual.web.app.create_app` picks one transport or the other from
``Settings`` alone.

**A message carries data, not copy.** :class:`Message` has ``kind`` and ``data``
and no rendered subject or body — a Korean-only-surface rule rather than a design
taste: user-visible copy is locked, so a module that wrote a Korean subject line
would be **inventing product copy**. :func:`render` is where a message becomes
words, and every word it uses comes from :mod:`mijual.mailcopy`, which carries a
provenance comment per string. Nothing in this module contains a Korean sentence.

**Three kinds, deliberately — and the third one arrived exactly the way this
paragraph said it would have to.** :data:`DEADLINE` (마감 임박 알림),
:data:`PASSWORD_RESET` (the reset link) and, from ``P13``,
:data:`SIGNUP_VERIFICATION` (the 6-digit 가입 인증번호). Until P13 this paragraph
read「Two kinds, and there will not quietly be a third」; it is rewritten rather
than quietly outgrown, because the guarantee was never the number — it was that a
new kind costs a constant here, a branch in :func:`render`, and two renderers in
:mod:`mijual.mailcopy`, all of it in a diff and in a review. `security` states
the policy as 「Notifications: email only … **No marketing or digest mail, ever**
— only the deadline notifications the user configured」, and all three kinds
still satisfy it: every one of them is a mail the reader themselves set in motion
(a deadline they configured, a reset they asked for, a 가입 they just pressed).
There will not quietly be a fourth.

**Which transport, and how it is chosen.** :func:`mailer_for` returns
:class:`SmtpMailer` when ``SMTP_HOST`` is set and :class:`ConsoleMailer`
otherwise. **Unset is a supported state, not an error**: local development and the
whole test suite run credential-free and send nothing, and every process that
builds a mailer logs :func:`describe_transport` once so a deployment can see which
one it got instead of discovering it from a reader who never received a mail.

**TLS is explicit and never opportunistic** (:meth:`Settings.smtp_tls_mode`):
port 465 is implicit TLS, anything else is STARTTLS-**required** — refused if the
server does not offer it — and plaintext happens only when ``SMTP_TLS=none`` is
set deliberately, which exists for a local sink and is documented in
``.env.prod.example`` as never-in-production.

**No failure this module raises carries an address or a credential.**
:class:`MailError` is constructed from an exception's *type name* (and an SMTP
status code when there is one), the same rule the agent's model errors and the
vocky client already follow — an ``smtplib`` message routinely quotes the
recipient the server rejected, and a transport error travels into logs.

This module imports nothing but the standard library (``smtplib``, ``ssl``,
``email``) — in particular nothing that can spend an OpenDART request or a model
call, so it is safe on a request path.
"""

from __future__ import annotations

import logging
import smtplib
import ssl
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from email.message import EmailMessage
from typing import IO, TYPE_CHECKING, Protocol, runtime_checkable

from mijual import mailcopy

if TYPE_CHECKING:  # pragma: no cover - imported for types only
    from mijual.config import Settings

__all__ = [
    "DEADLINE",
    "PASSWORD_RESET",
    "SIGNUP_VERIFICATION",
    "ConsoleMailer",
    "MailError",
    "Mailer",
    "Message",
    "Rendered",
    "SmtpMailer",
    "describe_transport",
    "mailer_for",
    "render",
]

log = logging.getLogger(__name__)

#: The reset link P5 sends. Its ``data``: ``url``, ``expires_at``.
PASSWORD_RESET = "password_reset"
#: 마감 임박 알림 — `P4.S2`'s D-day mail. Its ``data`` is one candidate deadline
#: as :mod:`mijual.notify` composes it (``corp_name`` · ``label_ko`` · ``dday`` ·
#: ``date`` · the window · ``shares`` · ①'s ``allotted_shares`` and
#: ``price_state`` · ``rcept_no`` · ``event_url`` · ``settings_url``). **No key
#: of it is a won amount and none is a sentence.**
DEADLINE = "deadline"
#: 가입 인증번호 — ``P13``'s signup gate. Its ``data``: ``code`` (six characters,
#: **a string**, leading zeros intact) and ``expires_at``. The code travels here
#: and nowhere else: it is never in an HTTP response body, which is what keeps
#: the mailbox — rather than the network — the thing being proven.
SIGNUP_VERIFICATION = "signup_verification"

#: How long any SMTP conversation may hang before it is a failure rather than a
#: wait. Bounded on purpose (the pattern is `hi2vi_web/src/lib/mailer.ts`'s):
#: the reset mail is sent **from a request handler**, so an unreachable SMTP host
#: with no timeout would hold a worker open for the OS default — minutes.
DEFAULT_TIMEOUT_S = 10.0


class MailError(RuntimeError):
    """A send failed. Carries a type name and maybe a status code — never more.

    Deliberately *not* wrapping the underlying exception's message: an SMTP
    rejection quotes the recipient address back at you, and this error is written
    to a log and put in a pipeline stage summary.
    """


@dataclass(frozen=True)
class Message:
    """What to send, to whom — never *how it reads*.

    ``kind`` names the template :func:`render` will use; ``data`` carries the
    values it renders with. No key of ``data`` is ever a sentence.
    """

    to: str
    kind: str
    data: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Rendered:
    """One message as words: a subject line and a ``text/plain`` body.

    There is deliberately **no HTML alternative**. `security`'s measured signed
    property is that no page contacts a third-party origin, and the same
    reasoning reaches mail: an HTML part invites a logo, a web font and a
    tracking pixel, each of which is a third-party fetch performed by a reader's
    mail client on this product's behalf. Plain text cannot carry one.
    """

    subject: str
    text: str


def render(message: Message) -> Rendered:
    """A message as the words a reader sees. Every string is :mod:`mijual.mailcopy`'s.

    An unknown kind raises rather than sending something empty: a mail with no
    body is worse than a stage that reports it could not render one.
    """
    if message.kind == DEADLINE:
        return Rendered(
            subject=mailcopy.deadline_subject(message.data),
            text=mailcopy.deadline_body(message.data),
        )
    if message.kind == PASSWORD_RESET:
        return Rendered(
            subject=mailcopy.password_reset_subject(message.data),
            text=mailcopy.password_reset_body(message.data),
        )
    if message.kind == SIGNUP_VERIFICATION:
        return Rendered(
            subject=mailcopy.signup_verification_subject(message.data),
            text=mailcopy.signup_verification_body(message.data),
        )
    raise MailError(f"no mail template for kind {message.kind!r}")


@runtime_checkable
class Mailer(Protocol):
    """The seam. Everything else in the product sends through this one method."""

    def send(self, message: Message) -> None: ...


class ConsoleMailer:
    """Development transport: writes the message server-side, sends no mail.

    The reset link is printed in full, because the developer running the service
    is the intended recipient — and printed **server-side only**: it never
    travels in an HTTP response, which would defeat 가입 여부 비노출 exactly as
    thoroughly as a different response body would.

    It is also what a **production process with no SMTP configured** falls back
    to, and that is the honest failure: the notify stage's summary says
    ``transport console`` and its count of mails "sent" is a count of mails
    printed. Nothing pretends to have mailed anybody.
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


def _header(value: str) -> str:
    """A header value with CR/LF removed — header injection, closed at the seam.

    Every one of these values is composed by this codebase rather than typed by a
    reader, so this is a belt on braces; it is here because ``SMTP_FROM`` comes
    from a ``.env`` file an operator edits by hand, and because the recipient
    address is the one header value that originates outside the code at all.
    """
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split())


class SmtpMailer:
    """The real transport: ``smtplib`` over the operator's SMTP account.

    **One connection per batch, not per message.** :meth:`open` /
    :meth:`close` (or the context-manager form) hold a single conversation open,
    so a 50-mail notify run is one login rather than fifty. A bare
    :meth:`send` outside that block still works — it opens and closes around the
    one message — which is what the password-reset path on a request handler
    wants.

    Constructed from ``Settings`` by :meth:`from_settings`; the four keys and the
    TLS policy are documented on :class:`mijual.config.Settings`.
    """

    def __init__(
        self,
        *,
        host: str,
        port: int = 587,
        username: str | None = None,
        password: str | None = None,
        sender: str,
        tls: str = "starttls",
        timeout: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        self.host = host
        self.port = port
        self.sender = _header(sender)
        self.tls = tls
        self.timeout = timeout
        self._username = username
        self._password = password
        self._smtp: smtplib.SMTP | None = None

    @classmethod
    def from_settings(cls, settings: "Settings") -> "SmtpMailer":
        settings.require_smtp()
        return cls(
            host=settings.smtp_host or "",
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            sender=settings.smtp_from or "",
            tls=settings.smtp_tls_mode(),
        )

    # -- the connection ----------------------------------------------------
    def _connect(self) -> smtplib.SMTP:
        context = ssl.create_default_context()
        if self.tls == "ssl":
            smtp: smtplib.SMTP = smtplib.SMTP_SSL(
                self.host, self.port, timeout=self.timeout, context=context
            )
        else:
            smtp = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
        smtp.ehlo()
        if self.tls == "starttls":
            if not smtp.has_extn("starttls"):
                # Required, never opportunistic: falling back to plaintext here
                # would hand the credential over without saying so.
                smtp.close()
                raise MailError("smtp server does not offer STARTTLS")
            smtp.starttls(context=context)
            smtp.ehlo()
        # AUTH only when the server offers it: the local `aiosmtpd` sink used for
        # verification speaks no AUTH, and issuing one would fail the whole
        # conversation on a transport that is working perfectly well.
        if self._username and self._password and smtp.has_extn("auth"):
            smtp.login(self._username, self._password)
        return smtp

    def open(self) -> "SmtpMailer":
        if self._smtp is None:
            self._smtp = self._guarded(self._connect)
        return self

    def close(self) -> None:
        smtp, self._smtp = self._smtp, None
        if smtp is not None:
            try:
                smtp.quit()
            except Exception:  # noqa: BLE001 - closing must never raise
                pass

    def __enter__(self) -> "SmtpMailer":
        return self.open()

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # -- sending -----------------------------------------------------------
    def send(self, message: Message) -> None:
        if self._smtp is not None:
            self._guarded(self._deliver, self._smtp, message)
            return
        with self:
            self._guarded(self._deliver, self._smtp, message)

    def send_many(self, messages: Iterable[Message]) -> None:
        """Every message over one connection. Any failure stops the batch.

        Callers that must not stop (the notify stage: one bad address may not
        cost every other reader their mail) hold the connection open themselves
        and call :meth:`send` per message inside their own ``try``.
        """
        with self:
            for message in messages:
                self.send(message)

    def _deliver(self, smtp: smtplib.SMTP, message: Message) -> None:
        rendered = render(message)
        mail = EmailMessage()
        mail["From"] = self.sender
        mail["To"] = _header(message.to)
        mail["Subject"] = _header(rendered.subject)
        mail.set_content(rendered.text)
        smtp.send_message(mail)
        # The kind and the address, at INFO, because a mail that went out is an
        # operational fact. `mijual.notify` logs its own lines with account ids
        # and never an address; this one is the transport's own record.
        log.info("smtp mailer: sent %s", message.kind)

    def _guarded(self, fn, *args):
        """Run ``fn``, converting any transport failure into a bare :class:`MailError`."""
        try:
            return fn(*args)
        except MailError:
            raise
        except smtplib.SMTPResponseException as exc:
            raise MailError(f"{type(exc).__name__} (smtp {exc.smtp_code})") from None
        except (smtplib.SMTPException, OSError, ssl.SSLError) as exc:
            raise MailError(type(exc).__name__) from None


def mailer_for(settings: "Settings") -> Mailer:
    """The transport this process should use: SMTP when configured, else console.

    ``SMTP_HOST`` is the switch. A half-configured deployment (a host but no
    ``SMTP_FROM``) raises through :meth:`Settings.require_smtp` rather than
    silently degrading — an operator who set one key meant to send mail.
    """
    if settings.smtp_host:
        return SmtpMailer.from_settings(settings)
    return ConsoleMailer()


def describe_transport(settings: "Settings") -> str:
    """One line naming the transport, for the log. **Never the password.**"""
    if not settings.smtp_host:
        return "console (SMTP_HOST unset — messages are printed, no mail is sent)"
    return (
        f"smtp {settings.smtp_host}:{settings.smtp_port} "
        f"tls={settings.smtp_tls_mode()} from={settings.smtp_from or '<unset>'}"
    )
