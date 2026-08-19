"""Engine / session helpers.

No Alembic in P2 — see :mod:`mijual.db.models`. :func:`reset_schema` is the
sanctioned way to evolve the schema while every row is still re-collectable.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from mijual.config import load_settings
from mijual.db.models import Base

__all__ = [
    "make_engine",
    "make_session_factory",
    "session_scope",
    "create_all",
    "reset_schema",
]


def make_engine(url: str | None = None, *, echo: bool = False) -> Engine:
    """Engine for ``url`` (defaults to ``DATABASE_URL`` / the local docker Postgres)."""
    return create_engine(url or load_settings().database_url, echo=echo, future=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Commit on success, roll back on failure, always close."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def reset_schema(engine: Engine) -> None:
    """Drop and recreate every table. Destructive by design (P2 has no migrations)."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
