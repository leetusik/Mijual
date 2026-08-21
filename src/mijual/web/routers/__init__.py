"""One router module per surface; :func:`mijual.web.app.create_app` includes them.

:mod:`~mijual.web.routers.health`, :mod:`~mijual.web.routers.board` and
:mod:`~mijual.web.routers.events` (`P5.S3`), and :mod:`~mijual.web.routers.stocks`
— 내 종목 조회 (`P5.S4`). `P5.S9` adds the ops ones, each as its own module here —
so a router file never spans two signed design surfaces and a review can isolate
a regression to one of them.

Routers stay thin: they validate the request, call the presentation contract
(`P5.S2`) and serialize. **Derivation does not live here** — the failure mode the
design names is "two divergent readouts for the same number", and it starts with
an endpoint computing its own version of one.
"""

from __future__ import annotations

__all__: list[str] = []
