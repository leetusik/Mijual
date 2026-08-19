"""Process configuration.

Secrets (``DART_API_KEY``, ``GEMINI_API_KEY``) live in the gitignored repo-root
``.env`` or in the real environment, are read **in process**, and are NEVER
echoed, logged, embedded in a cached URL/filename, or committed.  ``Settings``
carries a masking ``__repr__`` so an accidental ``print(settings)`` cannot leak
one, and a missing secret only raises when it is actually *used* — never at
import or construction time, so offline work (cached fixtures, tests) needs no
credential at all.

Generalised from ``scripts/spike/dart.py``'s in-process ``.env`` parsing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path

__all__ = [
    "MissingSecret",
    "Settings",
    "load_settings",
    "repo_root",
    "DEFAULT_DATABASE_URL",
    "DEFAULT_REDIS_URL",
    "SPIKE_CACHE_DIR",
]

#: Local docker Postgres from ``compose.yaml`` (host port 5433 keeps a system
#: Postgres on 5432 out of the way).
DEFAULT_DATABASE_URL = "postgresql+psycopg://mijual:mijual@localhost:5433/mijual"
#: Celery broker + result backend and the scheduler's run-lock store (P2.S6).
#: Host port 6380 matches ``compose.yaml`` and keeps the machine's own
#: redis-server (and another project's container) on 6379 out of the way.
DEFAULT_REDIS_URL = "redis://localhost:6380/0"


class MissingSecret(RuntimeError):
    """Raised when a secret is *used* but was never provided."""


def repo_root() -> Path:
    """Repo root: nearest ancestor holding ``pyproject.toml``, else the cwd."""
    override = os.environ.get("MIJUAL_ROOT")
    if override:
        return Path(override).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return Path.cwd()


ROOT = repo_root()
#: Default on-disk OpenDART response cache for pipeline runs (gitignored).
DEFAULT_CACHE_DIR = ROOT / "var" / "dart-cache"
#: The P1 spike's 1,002-response cache — byte-compatible with this package's
#: cache scheme, so pointing a client here gives a full offline fixture path.
SPIKE_CACHE_DIR = ROOT / "scripts" / "spike" / "samples"


def _parse_dotenv(path: Path) -> dict[str, str]:
    """``KEY=value`` lines from a ``.env`` file. Values are never logged."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        values[name.strip()] = value.strip().strip('"').strip("'")
    return values


@dataclass(frozen=True)
class Settings:
    """Immutable process settings. Never print secrets — see ``__repr__``."""

    dart_api_key: str | None = None
    gemini_api_key: str | None = None
    database_url: str = DEFAULT_DATABASE_URL
    redis_url: str = DEFAULT_REDIS_URL
    cache_dir: Path = DEFAULT_CACHE_DIR

    def require_dart_api_key(self) -> str:
        if not self.dart_api_key:
            raise MissingSecret(
                "DART_API_KEY not found (repo-root .env or environment). "
                "Offline work against a cached response set needs no key."
            )
        return self.dart_api_key

    def require_gemini_api_key(self) -> str:
        # Reserved for P2.S4; absent today and must not crash anything until used.
        if not self.gemini_api_key:
            raise MissingSecret(
                "GEMINI_API_KEY not found (repo-root .env or environment)."
            )
        return self.gemini_api_key

    def with_cache_dir(self, cache_dir: Path | str) -> "Settings":
        return replace(self, cache_dir=Path(cache_dir))

    def __repr__(self) -> str:  # pragma: no cover - trivial, but load-bearing
        def mark(value: str | None) -> str:
            return "<set>" if value else "<unset>"

        return (
            "Settings(dart_api_key={}, gemini_api_key={}, database_url={!r}, "
            "redis_url={!r}, cache_dir={!r})"
        ).format(
            mark(self.dart_api_key),
            mark(self.gemini_api_key),
            self.database_url,
            self.redis_url,
            str(self.cache_dir),
        )

    __str__ = __repr__


def load_settings(*, env_file: Path | None = None) -> Settings:
    """Environment first, then the repo-root ``.env``, then defaults."""
    dotenv = _parse_dotenv(env_file if env_file is not None else ROOT / ".env")

    def pick(name: str) -> str | None:
        value = os.environ.get(name) or dotenv.get(name)
        return value.strip() or None if value else None

    cache_dir = pick("DART_CACHE_DIR")
    return Settings(
        dart_api_key=pick("DART_API_KEY"),
        gemini_api_key=pick("GEMINI_API_KEY"),
        database_url=pick("DATABASE_URL") or DEFAULT_DATABASE_URL,
        redis_url=pick("REDIS_URL") or DEFAULT_REDIS_URL,
        cache_dir=Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR,
    )
