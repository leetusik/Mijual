"""One run at a time — the lock that makes overlapping runs impossible.

Re-running a window is nearly free and never duplicates a row (N14/N25: the
second live pass over the same window added zero events and zero versions), so
repetition is safe. **Concurrency is not.** Two runs of the same window overlap
in time, both see "no 본문 held for this version yet", and both fetch it — the
one failure mode idempotent upserts cannot fix, because it is spent quota, not a
duplicated row.

So every corpus-writing entry point takes the same single lock:

* :class:`RedisLock` — ``SET key token NX PX ttl`` against the broker Redis the
  worker already talks to. Released by **compare-and-delete**, never a bare
  ``DEL``: a run that overran its TTL must not delete the lock its successor now
  holds.
* :class:`FileLock` — the same semantics on one host via ``O_CREAT|O_EXCL``, for
  the inline ``python -m mijual.scheduler once`` path when no broker is running.
  A lock whose TTL has expired is stolen (a crashed run must not wedge the
  schedule for good), and that is recorded.

Both are advisory and both are *fail-closed on contention*: a busy lock does not
raise, it returns ``False``, and the caller reports a skipped run rather than
running anyway.
"""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "DEFAULT_TTL_S",
    "FileLock",
    "NullLock",
    "RedisLock",
    "make_lock",
]

#: How long a lock lives if the holder never releases it (crash, kill -9).
DEFAULT_TTL_S = 3600
#: Redis key prefix. One namespace for the whole workspace.
KEY_PREFIX = "mijual:lock:"


def _now() -> float:
    return time.time()


def _token() -> str:
    """Owner token: enough to tell two runs apart, nothing identifying."""
    return f"{os.getpid()}-{uuid.uuid4().hex[:8]}"


@dataclass
class NullLock:
    """Explicitly unlocked — for a dry run, a test, or ``--no-lock``."""

    name: str = "pipeline"
    kind: str = "none"
    token: str = ""

    def acquire(self) -> bool:
        return True

    def release(self) -> bool:
        return True

    def holder(self) -> str | None:
        return None


class RedisLock:
    """``SET NX PX`` mutual exclusion with compare-and-delete release."""

    kind = "redis"

    def __init__(self, client: Any, *, name: str = "pipeline", ttl_s: int = DEFAULT_TTL_S) -> None:
        self.client = client
        self.name = name
        self.key = f"{KEY_PREFIX}{name}"
        self.ttl_s = ttl_s
        self.token = _token()
        self.acquired = False

    @staticmethod
    def _text(value: Any) -> str | None:
        if value is None:
            return None
        return value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)

    def acquire(self) -> bool:
        self.acquired = bool(
            self.client.set(self.key, self.token, nx=True, px=int(self.ttl_s * 1000))
        )
        return self.acquired

    def release(self) -> bool:
        """Delete the key **only** if we still own it (TTL may have expired)."""
        if not self.acquired:
            return False
        owned = self._text(self.client.get(self.key)) == self.token
        if owned:
            self.client.delete(self.key)
        self.acquired = False
        return owned

    def holder(self) -> str | None:
        return self._text(self.client.get(self.key))


class FileLock:
    """Single-host lock file with the same TTL and ownership rules."""

    kind = "file"

    def __init__(
        self, path: Path | str, *, name: str = "pipeline", ttl_s: int = DEFAULT_TTL_S
    ) -> None:
        self.path = Path(path)
        self.name = name
        self.ttl_s = ttl_s
        self.token = _token()
        self.acquired = False
        self.stolen = False

    def _write(self) -> bool:
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            return False
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"{self.token}\n{_now() + self.ttl_s:.0f}\n")
        return True

    def _expiry(self) -> float | None:
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
            return float(lines[1])
        except (OSError, IndexError, ValueError):
            return None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self._write():
            self.acquired = True
            return True
        expiry = self._expiry()
        if expiry is not None and expiry > _now():
            return False
        # Expired (or unreadable) — the holder died. Steal it, and say so.
        try:
            self.path.unlink()
        except FileNotFoundError:  # pragma: no cover - lost the race, retry below
            pass
        self.acquired = self._write()
        self.stolen = self.acquired
        return self.acquired

    def release(self) -> bool:
        if not self.acquired:
            return False
        self.acquired = False
        try:
            owner = self.path.read_text(encoding="utf-8").splitlines()[0]
        except (OSError, IndexError):
            return False
        if owner != self.token:
            return False
        self.path.unlink(missing_ok=True)
        return True

    def holder(self) -> str | None:
        try:
            return self.path.read_text(encoding="utf-8").splitlines()[0]
        except (OSError, IndexError):
            return None


def make_lock(
    *,
    redis_url: str | None,
    name: str = "pipeline",
    ttl_s: int = DEFAULT_TTL_S,
    fallback_dir: Path | str | None = None,
    log=None,
) -> RedisLock | FileLock | NullLock:
    """A Redis lock when a broker answers, else a single-host file lock.

    The worker path always has Redis (it is the broker). The inline path may not,
    and a missing broker must not mean *no* lock — so it degrades to a file lock
    and reports which one it got, rather than pretending to be distributed.
    """
    if redis_url:
        try:
            import redis  # local import: the package is only needed here

            client = redis.Redis.from_url(redis_url, socket_connect_timeout=2)
            client.ping()
            return RedisLock(client, name=name, ttl_s=ttl_s)
        except Exception as exc:  # noqa: BLE001 - any redis/transport failure degrades
            if log:
                log(f"lock      : redis unavailable ({type(exc).__name__}) — file lock")
    directory = Path(fallback_dir) if fallback_dir else Path("var") / "locks"
    return FileLock(directory / f"{name}.lock", name=name, ttl_s=ttl_s)
