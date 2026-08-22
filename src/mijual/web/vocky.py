"""vocky 관찰 뷰 — the read-only proxy onto vocky's real feedback read API.

R7 §6.3 delegated one decision to this build:

    운영자 위임: **관찰 API의 반환 shape (필드·granularity·pagination)는 Claude Code가
    vocky 쪽 실물에 맞춰 결정**하고, 결정한 shape를 이 절에 기록해 갱신할 것.

``P5.S18`` made it against the running product (vocky's own repository and a local
stack of it), and the decision is written back into that section of the landed
record. What follows is the same decision as code.

**The endpoint.** vocky exposes four read surfaces; exactly one of them fits an
external product's own operator panel, and vocky's own contract says so:

    Project Feedback API (v2) — Consumers: An external service's own admin panel /
    operator page … reading and managing its project's feedback directly by API.

So the observation API is ``GET {base}/api/project/feedback``, authenticated by a
``vk_``-prefixed key in ``Authorization: Bearer``. The scope is **implicit in the
credential** — there is no project parameter to send and none is sent. The other
three were considered and rejected on the record: ``GET /api/feedback`` is a
single product *user's* self-read (it requires a ``user_id``), ``/app/feedback``
needs a human session token rather than a service credential, and
``/api/project/usage`` returns the org's **credentials** — key metadata a
different product's panel has no business rendering (최소 열람).

**Read-only is enforced here, not promised.** The same ``vk_`` key can ``PATCH``
and ``DELETE`` on that surface — vocky has no read-scoped credential today
("There are still no per-credential permission scopes: one ``vk_`` key does
capture and full read+manage across its whole scope") — so this module issues
``GET`` and nothing else, and there is no code path that could issue another
method. That is the Mijual-side implementation of 「읽기 전용 (관찰 API의 정의 —
vocky 상태 변경 없음)」, and the same rule §6.5 already puts on the whole panel.

**The fields are an allowlist, not a pass-through** (:data:`ROW_FIELDS`). vocky's
record carries 25 keys, several of which are correlation handles (``user_id``,
``session_id``, ``conversation_id``) or free-form blobs (``source_metadata``,
``attributes``, ``messages``, ``used_context``). Forwarding them would put another
product's user identifiers on this panel for no observational gain, against R7's
최소 열람 and 사용자 추적 용도 금지. What is forwarded is what the view observes:
when it landed, what was said, on which surface, through which trigger. **Do not
widen this to "everything vocky sends"** — widen it deliberately, field by field,
and the frontend needs no change either way (its table renders any served key).

**Keys keep vocky's own English names.** §6.1/§6.2 sign raw English for codes and
identifiers on this operator-only surface, and renaming another system's fields
would be inventing field names §6.3 forbids. The one transformation is the
timestamp: vocky serializes UTC (``…Z``, microseconds), Mijual serves **absolute
KST** like every other instant in this API (:mod:`mijual.web.clock`), so the ops
``Stamp`` atom — which slices a string and never ``Date``-parses it — reads it
correctly.

**Degraded honestly, never a 500** — the precedent is ``P5.S9``'s Redis lock
chip: an external dependency that is down is a fact the operator wants, not a
reason to fail the tab. Three states, and they are the payload's ``state``:

======================  ====================================================
``unconfigured``        no base URL and/or no key. **연결 전** — the surface
                        renders R7's signed 「API shape 확정 대기」 + skeleton.
``unreachable``         configured, but the call failed (timeout, DNS, 401,
                        a redirect, a malformed body). ``reason`` carries the
                        raw English exception name, ``status`` an HTTP code
                        when there was one. **No fabricated rows, ever.**
``ok``                  vocky answered; ``rows`` is what it returned.
======================  ====================================================

**Timeout, no retries, no redirects.** This is an external HTTP call in a request
path. It is neither an OpenDART request nor an LLM call, so the `architecture`
boundary is untouched, but a tab must not be able to hang the panel:
:data:`TIMEOUT_SECONDS` is short and a failure is a state rather than a second
attempt. Redirects are **refused** rather than followed, because
``urllib.request`` re-sends the ``Authorization`` header to the redirect target —
a redirected base URL would hand the ``vk_`` key to whatever answered.

**The key is a secret and is treated as one.** It lives in ``Settings``
(``MIJUAL_VOCKY_API_KEY``), is masked in its ``repr``, raises only when *used*,
travels in a header (never in a URL or a log line), and nothing here logs the
request, the response or the exception's text.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence

from mijual.config import Settings
from mijual.web import clock

__all__ = [
    "DEFAULT_LIMIT",
    "MAX_LIMIT",
    "ROW_FIELDS",
    "TIMEOUT_SECONDS",
    "VOCKY_ENDPOINT",
    "Observation",
    "observe",
    "row_view",
]

#: vocky's project-scoped read. The credential decides the scope; there is no
#: project parameter on this surface and none is sent.
VOCKY_ENDPOINT = "/api/project/feedback"

#: Short on purpose: the ops panel must stay usable when vocky does not answer.
#: One attempt — a retry would multiply the wait an operator sits through.
TIMEOUT_SECONDS = 3.0

#: **vocky's own ceiling is 100** (`limit must be between 1 and 100`, measured
#: against the running service). Mijual caps its own parameter at the same number
#: rather than forwarding a value vocky answers 400 to.
DEFAULT_LIMIT = 50
MAX_LIMIT = 100

#: The decided field set, in the order the panel's table renders it. vocky's own
#: key names (§6.1: raw English identifiers on an operator surface). See the
#: module docstring for what is deliberately **not** here and why.
ROW_FIELDS: tuple[str, ...] = (
    "ingested_at",
    "message",
    "feedback_value",
    "trigger_type",
    "trigger_message",
    "target_type",
    "target_id",
    "target_text",
    "channel",
    "recorded_by",
    "source_product",
    "source_integration",
    "comment",
    "tags",
    "id",
    "project_id",
)

#: Keys whose value is an instant: served as absolute KST, like every other
#: timestamp this API emits.
_INSTANT_FIELDS = frozenset({"ingested_at"})


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects instead of following them with the credential attached."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


@dataclass(frozen=True)
class Observation:
    """One page of vocky's collected feedback, or the honest reason there is none.

    ``count`` is **this page's** row count, not a total: vocky's list surface
    returns a keyset page and no total, and inventing one is exactly the class of
    number R7 forbids. ``next_cursor`` is vocky's opaque cursor, passed through
    untouched and **omitted** rather than serialized as ``null`` when the list
    ends — the contract-wide rule for an absent value.
    """

    state: str = "unconfigured"
    rows: Sequence[Mapping[str, Any]] = ()
    next_cursor: str | None = None
    reason: str | None = None
    status: int | None = None
    base: str | None = None

    def payload(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "state": self.state,
            "source": {"endpoint": VOCKY_ENDPOINT},
            "fields": list(ROW_FIELDS),
            "count": len(self.rows),
            "rows": [dict(row) for row in self.rows],
        }
        if self.base is not None:
            body["source"]["base"] = self.base
        if self.next_cursor is not None:
            body["next_cursor"] = self.next_cursor
        if self.reason is not None:
            body["reason"] = self.reason
        if self.status is not None:
            body["status"] = self.status
        return body


def _instant(value: Any) -> str | None:
    """vocky's UTC ISO-8601 (``…Z``, microseconds) as an absolute KST instant.

    An unparseable value is dropped rather than guessed at: a timestamp this
    service cannot state truthfully is absent, never approximate.
    """
    if not isinstance(value, str):
        return None
    try:
        return clock.iso(datetime.fromisoformat(value))
    except ValueError:
        return None


def row_view(record: Mapping[str, Any]) -> dict[str, Any]:
    """One vocky record reduced to the observed fields, in the decided order.

    An absent, ``null`` or empty value is **left out** rather than rendered as
    ``null`` (the same rule :mod:`mijual.present` and :mod:`mijual.web.errors`
    follow), so a column is blank because the record genuinely has nothing there.
    """
    row: dict[str, Any] = {}
    for key in ROW_FIELDS:
        value = record.get(key)
        if key in _INSTANT_FIELDS:
            value = _instant(value)
        if value is None or value == "" or value == [] or value == {}:
            continue
        row[key] = value
    return row


def _url(base: str, *, limit: int, cursor: str | None) -> str:
    query: dict[str, str] = {"limit": str(max(1, min(limit, MAX_LIMIT)))}
    if cursor:
        query["cursor"] = cursor
    return f"{base.rstrip('/')}{VOCKY_ENDPOINT}?{urllib.parse.urlencode(query)}"


def observe(
    settings: Settings, *, limit: int = DEFAULT_LIMIT, cursor: str | None = None
) -> Observation:
    """Read one page of vocky's collected feedback. **Never raises.**

    Every failure — unset credential, bad URL, timeout, 401, redirect, garbage
    body — becomes a state on the way out, because the panel's job is to say what
    is true, and "vocky did not answer" is true and worth seeing.
    """
    base = (settings.vocky_api_base or "").strip()
    key = settings.vocky_api_key
    if not base or not key:
        return Observation(state="unconfigured")

    if urllib.parse.urlparse(base).scheme not in ("http", "https"):
        # A typo'd base must not become a `file://` read; it is unreachable.
        return Observation(state="unreachable", reason="UnsupportedScheme", base=base)

    request = urllib.request.Request(
        _url(base, limit=limit, cursor=cursor),
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with _OPENER.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # The status is the useful half (401 = the key; 404 = the base URL). The
        # body is another product's text and is never echoed onto this panel.
        return Observation(
            state="unreachable", reason=type(exc).__name__, status=exc.code, base=base
        )
    except Exception as exc:  # noqa: BLE001 - any transport/decode failure degrades
        return Observation(state="unreachable", reason=type(exc).__name__, base=base)

    if not isinstance(body, dict) or not isinstance(body.get("records"), list):
        return Observation(state="unreachable", reason="UnexpectedShape", base=base)

    rows = tuple(
        row_view(record) for record in body["records"] if isinstance(record, Mapping)
    )
    next_cursor = body.get("next_cursor")
    return Observation(
        state="ok",
        rows=rows,
        next_cursor=next_cursor if isinstance(next_cursor, str) else None,
        base=base,
    )
