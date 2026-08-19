"""Additive column reconciliation — the narrow gap ``create_all`` leaves open.

P2 runs **without Alembic on purpose** (N16): the schema evolves by editing
``models.py`` and re-running, because every row is re-collectable. That works
until a table holds data you do not want to re-collect — and after ``P2.S2`` it
does: 434 events / 1,226 versions / 1,612 snapshots that cost 291 live OpenDART
requests against an **unmeasured** daily quota (O-1). ``Base.metadata.create_all``
creates missing *tables*; it never adds a missing *column*, so a one-column
addition would otherwise force a full ``reset_schema``.

:func:`ensure_columns` closes exactly that gap and nothing else:

* it only ever **adds** columns that the models declare and the live table lacks;
* it refuses anything that is not nullable and default-free, so it can never
  rewrite or lose a row;
* it is idempotent, and it is a no-op on a database that ``create_all`` just built.

This is deliberately **not** a migration tool: no version table, no history, no
down-grade, no type changes, no drops. If a change ever needs more than this,
that is the signal to reset the schema (still cheap) or to revisit N16.
"""

from __future__ import annotations

from sqlalchemy import Engine, inspect, text
from sqlalchemy.orm import DeclarativeBase

__all__ = ["ensure_columns"]


def ensure_columns(engine: Engine, base: type[DeclarativeBase]) -> list[str]:
    """Add every declared-but-missing nullable column. Returns what it added."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    added: list[str] = []

    with engine.begin() as connection:
        for table in base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue  # create_all's job, not ours
            live = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in live:
                    continue
                if not column.nullable or column.default is not None or column.server_default:
                    raise RuntimeError(
                        f"{table.name}.{column.name} is not a safe additive column "
                        "(NOT NULL or defaulted) — reset the schema instead"
                    )
                ddl = column.type.compile(dialect=engine.dialect)
                connection.execute(
                    text(f'ALTER TABLE {table.name} ADD COLUMN "{column.name}" {ddl}')
                )
                added.append(f"{table.name}.{column.name}")
    return added
