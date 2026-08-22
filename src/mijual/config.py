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

    # -- serving policy (P5.S3). Both are ``None`` = "use the stated default",
    # which lives beside its reasoning in ``mijual.present`` / ``mijual.web``
    # rather than being duplicated here.
    #: ``MIJUAL_COUNTDOWN_CUTOFF_TIME`` — the KST wall-clock time on the 소멸 day
    #: that the landing countdown ticks down to. ``24:00`` (the default) means
    #: end of day, i.e. midnight at the **start of the next** day. R2 assumed
    #: exactly that for 계양전기 2026-09-04; the real 접수 마감 시각 is an operator
    #: fact, and when it is known this setting takes it **without a code change**.
    countdown_cutoff_time: str | None = None
    #: ``MIJUAL_STALE_AFTER_HOURS`` — how old the corpus may get before the board
    #: says so (default :data:`mijual.present.DEFAULT_STALE_AFTER_HOURS`, 18 h,
    #: derived from the beat schedule). The board never goes dark either way.
    stale_after_hours: int | None = None

    # -- reader auth (P5.S7). See ``mijual.web.auth`` for what each one does.
    #: ``MIJUAL_SESSION_SECRET`` — the reader session key `security` names. It
    #: **keys the digest** of a session/reset token rather than signing a
    #: self-contained cookie (the session is a row: see
    #: :class:`mijual.db.models.AuthSession`), so a database dump alone holds
    #: nothing replayable. Unset is a **development** state, not a production
    #: one: the digest falls back to unkeyed SHA-256 and
    #: :func:`mijual.web.auth.session_pepper` logs a warning once. Rotating it
    #: logs every reader out, which is the intended emergency lever.
    session_secret: str | None = None
    #: ``MIJUAL_COOKIE_SECURE`` — send the session cookie only over HTTPS.
    #: Defaults to **off** because local development is plain http; **P4 must
    #: set it** in every deployed environment.
    cookie_secure: bool = False
    #: ``MIJUAL_APP_BASE_URL`` — the origin the *frontend* is served from, used
    #: to build the password-reset link. The Next.js dev server's default.
    app_base_url: str = "http://localhost:3000"

    # -- the operator door (P5.S9, R7 §6.4). See ``mijual.web.ops``.
    #: ``MIJUAL_OPS_ID`` — the 운영자 ID. **A separate credential**, with no join
    #: to the reader account table and no admin flag on a reader row: `security`
    #: says it is issued and rotated in the deployment environment, so there is no
    #: signup, no reset and no account row for it anywhere.
    ops_id: str | None = None
    #: ``MIJUAL_OPS_PASSWORD`` — the 운영자 비밀번호, in plaintext, exactly as the
    #: deployment secret store hands it over. It is never compared with ``==``:
    #: :mod:`mijual.web.ops` hashes it once per process and every login — hit,
    #: wrong password, unknown ID, credential unset — spends exactly one scrypt
    #: verification, so the four causes are indistinguishable in body *and* in
    #: timing. **Unset means the door never opens**, which is the right default
    #: for a surface with no signup.
    ops_password: str | None = None

    # -- the vocky 관찰 뷰 (P5.S18, R7 §6.3). See ``mijual.web.vocky``.
    #: ``MIJUAL_VOCKY_API_BASE`` — the origin of the operator's vocky service
    #: (``https://vocky.hi2vi.com`` in production, a local stack in development).
    #: The observation endpoint itself is fixed in :mod:`mijual.web.vocky`; only
    #: the origin is configuration, because only the origin is deployment-specific.
    vocky_api_base: str | None = None
    #: ``MIJUAL_VOCKY_API_KEY`` — vocky's ``vk_``-prefixed ingest credential. It is
    #: a **secret** with the same handling as the two API keys above: masked in
    #: ``__repr__``, never logged, and it raises only when *used*
    #: (:meth:`require_vocky_api_key`), so a build with no vocky wiring runs
    #: normally and the panel simply reports 연결 전. Note that vocky has no
    #: read-only key scope today — the same key could write — which is why
    #: :mod:`mijual.web.vocky` issues ``GET`` and nothing else.
    vocky_api_key: str | None = None

    # -- the 운영자 연락처 (P6.S2, R6 §의견·문의). See ``mijual.agent.tools``.
    #: ``MIJUAL_OPERATOR_CONTACT`` — the string ``get_contact()`` answers with.
    #: R6 fixes it as a **deploy setting and nothing else**: 「운영자 문의: 연락처
    #: 문자열은 배포 설정값 — 미정, 운영자 지정 (하드코딩 발명 금지)」, and `security`
    #: records it as the one operator-identifying string the product will publish.
    #: **Unset is the shipped state today** and the tool says so honestly rather
    #: than inventing an address or a 「준비 중」 line — which is why there is no
    #: default here and no ``require_`` accessor: nothing in the product may fail
    #: for want of it, and nothing may substitute for it.
    operator_contact: str | None = None

    def require_dart_api_key(self) -> str:
        if not self.dart_api_key:
            raise MissingSecret(
                "DART_API_KEY not found (repo-root .env or environment). "
                "Offline work against a cached response set needs no key."
            )
        return self.dart_api_key

    def require_session_secret(self) -> str:
        """The reader session key, for a caller that must not run without one.

        Nothing in P5 calls this: the session digest degrades to unkeyed on
        purpose so local development needs no secret at all (and the degradation
        is announced, once, in the log). It exists for **P4**, which should fail
        a deployment that forgot the key rather than serve peppered-by-nothing
        cookies — the same "raises only on use" shape as the two API keys above.
        """
        if not self.session_secret:
            raise MissingSecret(
                "MIJUAL_SESSION_SECRET not found (repo-root .env or environment)."
            )
        return self.session_secret

    def require_vocky_api_key(self) -> str:
        """The vocky ingest key, for a caller that must not run without one.

        Nothing in P5 calls it: the 관찰 뷰 degrades to 연결 전 rather than
        failing, which is what the design asks for. It exists so **P4** can fail a
        deployment that meant to wire vocky and forgot — the same "raises only on
        use" shape as :meth:`require_dart_api_key`.
        """
        if not self.vocky_api_key:
            raise MissingSecret(
                "MIJUAL_VOCKY_API_KEY not found (repo-root .env or environment)."
            )
        return self.vocky_api_key

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
            "Settings(dart_api_key={}, gemini_api_key={}, session_secret={}, "
            "ops_id={}, ops_password={}, vocky_api_key={}, "
            "database_url={!r}, redis_url={!r}, cache_dir={!r})"
        ).format(
            mark(self.dart_api_key),
            mark(self.gemini_api_key),
            mark(self.session_secret),
            mark(self.ops_id),
            mark(self.ops_password),
            mark(self.vocky_api_key),
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
    stale_after = pick("MIJUAL_STALE_AFTER_HOURS")
    return Settings(
        dart_api_key=pick("DART_API_KEY"),
        gemini_api_key=pick("GEMINI_API_KEY"),
        session_secret=pick("MIJUAL_SESSION_SECRET"),
        database_url=pick("DATABASE_URL") or DEFAULT_DATABASE_URL,
        redis_url=pick("REDIS_URL") or DEFAULT_REDIS_URL,
        cache_dir=Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR,
        countdown_cutoff_time=pick("MIJUAL_COUNTDOWN_CUTOFF_TIME"),
        # A malformed value is ignored rather than crashing the service: a
        # mistyped ops env var must not take the board down.
        stale_after_hours=int(stale_after) if (stale_after or "").isdigit() else None,
        # Off unless explicitly turned on: a truthy string is a decision, an
        # empty or misspelled one is not. The failure direction matters —
        # `secure` on a plain-http dev server makes the cookie silently vanish.
        cookie_secure=(pick("MIJUAL_COOKIE_SECURE") or "").lower()
        in ("1", "true", "yes", "on"),
        app_base_url=(pick("MIJUAL_APP_BASE_URL") or "http://localhost:3000").rstrip("/"),
        # No default and no fallback: an operator door with a built-in credential
        # would be a back door. Unset simply never opens (`mijual.web.ops`).
        ops_id=pick("MIJUAL_OPS_ID"),
        ops_password=pick("MIJUAL_OPS_PASSWORD"),
        # Unset (either half) is the 연결 전 state, not an error: vocky is an
        # external product and the panel says so rather than failing.
        vocky_api_base=pick("MIJUAL_VOCKY_API_BASE"),
        vocky_api_key=pick("MIJUAL_VOCKY_API_KEY"),
        # 미정 until the operator supplies it (R6). Unset is a *state the product
        # states*, never a hole something else fills in.
        operator_contact=pick("MIJUAL_OPERATOR_CONTACT"),
    )
