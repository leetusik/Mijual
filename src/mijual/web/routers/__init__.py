"""One router module per surface; :func:`mijual.web.app.create_app` includes them.

Today there is only :mod:`~mijual.web.routers.health`. `P5.S3`+ add the reader
surfaces (board, event detail, 내 종목 조회) and `P5.S9` the ops ones, each as its
own module here — so a router file never spans two signed design surfaces and a
review can isolate a regression to one of them.

Routers stay thin: they validate the request, call the presentation contract
(`P5.S2`) and serialize. **Derivation does not live here** — the failure mode the
design names is "two divergent readouts for the same number", and it starts with
an endpoint computing its own version of one.
"""

from __future__ import annotations

__all__: list[str] = []
