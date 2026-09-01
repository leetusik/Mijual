"""Schema bootstrap: ``python -m mijual.db ensure``.

    python -m mijual.db ensure                       # $DATABASE_URL
    python -m mijual.db ensure --database-url ...    # an explicit target

This project has **no migrations, by design** (:mod:`mijual.db.models`): every
row is re-collectable, so the schema is brought forward additively instead.
``ensure`` is exactly what ``make db-ensure`` has always inlined —
:func:`~mijual.db.session.create_all` for missing *tables*, then
:func:`~mijual.db.schema_sync.ensure_columns` for declared-but-missing *nullable
columns* — lifted out of the Makefile so the container can run the same code path
(``compose.prod.yml``'s ``mijual-schema`` one-shot) and the Makefile now
delegates here.

It is **additive and idempotent**: it creates what is absent and touches nothing
that exists, so it is safe on every deploy and safe to re-run. It never drops
anything — that is :func:`~mijual.db.session.reset_schema`, which is not reachable
from this CLI on purpose.

Why it must run before the API serves a request: the serving process deliberately
creates no tables (the engine is lazy), so a **fresh** database has zero tables
and, historically, a database created before the P6 conversation tables existed
had 16 of 18 — with every ``/ask`` turn failing at persistence and nothing else
looking wrong. ``ensure`` is what closes both gaps.

Exit codes: ``0`` the schema is current, ``1`` it could not be made current (the
reason is printed to stderr — a compose one-shot that exits non-zero is what
keeps the API from starting against a broken database).
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m mijual.db", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    ensure = sub.add_parser(
        "ensure", help="create missing tables and additive columns (idempotent)"
    )
    ensure.add_argument(
        "--database-url",
        default=None,
        help="target database (default: DATABASE_URL / the configured default)",
    )
    return parser


def ensure(database_url: str | None = None) -> int:
    # Imported inside the function so `--help` costs no SQLAlchemy import and no
    # engine construction.
    from mijual.config import load_settings
    from mijual.db import create_all, make_engine
    from mijual.db.models import Base
    from mijual.db.schema_sync import ensure_columns

    url = database_url or load_settings().database_url
    engine = make_engine(url)
    create_all(engine)
    added = ensure_columns(engine, Base)
    # The Makefile's exact line, so the container log and a dev run read alike.
    print("schema ok" + (f" (+{len(added)} columns)" if added else ""))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "ensure":
        try:
            return ensure(args.database_url)
        except Exception as exc:  # noqa: BLE001 - the CLI's job is to report and fail
            # Type + message only: a connection URL can carry a password, and
            # SQLAlchemy's own repr already redacts it, so nothing is re-derived
            # here beyond what the exception itself says.
            print(f"schema FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
