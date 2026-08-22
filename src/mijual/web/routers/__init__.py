"""One router module per surface; :func:`mijual.web.app.create_app` includes them.

:mod:`~mijual.web.routers.health`, :mod:`~mijual.web.routers.board` and
:mod:`~mijual.web.routers.events` (`P5.S3`), and :mod:`~mijual.web.routers.stocks`
— 내 종목 조회 (`P5.S4`). :mod:`~mijual.web.routers.auth` (`P5.S7`) and
:mod:`~mijual.web.routers.portfolio` (`P5.S8`) are the reader's own rows, and
:mod:`~mijual.web.routers.ops` (`P5.S9`) is 운영 관제 — the one surface behind a
*separate* credential, and the only one that is read-only by rule rather than by
habit. :mod:`~mijual.web.routers.ask` (`P6.S4`) is AI 질문 — the only route that
streams, and the only one that reaches a model (through :mod:`mijual.agent`, and
nowhere else). A router file never spans two signed design surfaces, so a review
can isolate a regression to one of them.

Routers stay thin: they validate the request, call the presentation contract
(`P5.S2`) and serialize. **Derivation does not live here** — the failure mode the
design names is "two divergent readouts for the same number", and it starts with
an endpoint computing its own version of one.
"""

from __future__ import annotations

__all__: list[str] = []
