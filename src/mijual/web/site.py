"""Site-wide configuration the chrome reads — today, the 운영자 연락처.

``MIJUAL_OPERATOR_CONTACT`` is **one free-text string** and stays one: `security`
records it as the single operator-identifying string the product publishes, and
:func:`mijual.agent.tools.get_contact` hands that exact string to a reader.
Splitting the setting into two fields would give the product two contact truths
that could disagree.

The footer needs the parts anyway — R1 makes numerals mono while Korean and
addresses are Pretendard, so the phone and the email cannot share one span — so
the **derivation** lives here, once, on the server, beside the setting. The
frontend receives what it renders and parses nothing; the agent receives the
string and parses nothing. One value, one parser, two readouts that cannot drift.

The parser is deliberately tolerant of however the operator writes the value:
it finds an address and a phone number anywhere in the string, so
``leetusik@gmail.com · 010-3772-9916`` and ``이메일 … · 전화 …`` both work, and a
string carrying neither shape simply yields ``None`` for both parts while
``contact`` still carries the operator's words verbatim.
"""

from __future__ import annotations

import re

__all__ = ["contact_payload", "split_contact"]

#: Deliberately loose. This is not validation — the operator's own string is not
#: something this service gets to refuse — it is "which run of characters is the
#: address", so the separators the operator might use (spaces, ·, commas) are the
#: only characters excluded.
_EMAIL = re.compile(r"[^\s<>@,·]+@[^\s<>@,·]+\.[^\s<>@,·]+")

#: A Korean phone number as anyone writes one: 010-3772-9916, 02-000-0000, or the
#: same digits unhyphenated. Searched **after** the address is removed, so an
#: address carrying digits cannot donate them to the phone.
_PHONE = re.compile(r"\+?\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{4}")


def split_contact(raw: str | None) -> tuple[str | None, str | None, str | None]:
    """``(contact, email, phone)`` from the operator's one string.

    ``contact`` is the string as the operator wrote it (stripped, and ``None``
    when unset or blank) — the same value the agent answers with.
    """
    contact = (raw or "").strip()
    if not contact:
        return None, None, None

    email_match = _EMAIL.search(contact)
    email = email_match.group(0) if email_match else None

    rest = contact.replace(email, " ") if email else contact
    phone_match = _PHONE.search(rest)
    phone = phone_match.group(0).strip() if phone_match else None

    return contact, email, phone


def contact_payload(raw: str | None) -> dict[str, str | None]:
    """The JSON body ``GET /site/contact`` serves. All three keys, always.

    A key is ``null`` rather than absent because an unset contact is a **state
    the product states**, not a hole: the chrome renders no contact line at all
    (never an empty label), and the agent's honest 「연락처 미설정」 line stays the
    agent's own voice.
    """
    contact, email, phone = split_contact(raw)
    return {"contact": contact, "email": email, "phone": phone}
