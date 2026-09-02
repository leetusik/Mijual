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
    "mask_url_password",
]

#: Local docker Postgres from ``compose.yaml`` (host port 5434 keeps other
#: Postgres instances out of the way: 5432 is the system default and 5433 is
#: held by another project of the operator's).
DEFAULT_DATABASE_URL = "postgresql+psycopg://mijual:mijual@localhost:5434/mijual"
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


def mask_url_password(url: str) -> str:
    """A database URL with its password replaced by ``***``.

    ``Settings.__repr__`` masked every API key and password and then printed
    ``database_url`` **verbatim, password included** — the one hole in the
    "printing settings cannot leak a secret" property, found by ``P4.S1`` while
    writing the deploy runbook (a runbook step that echoes settings is exactly
    where it would have leaked). SQLAlchemy's own URL parser does the masking, so
    there is no second dialect-aware URL parser in this codebase; a URL it cannot
    parse is reported as unparseable rather than printed on the chance that it
    holds no password.
    """
    try:
        from sqlalchemy.engine import make_url

        return make_url(url).render_as_string(hide_password=True)
    except Exception:  # noqa: BLE001 - a repr must never raise, and never guess
        return "<unparseable database url>"


def _positive_int(name: str, raw: str | None) -> int | None:
    """``raw`` as an integer ``>= 1``, or ``None`` when it is unset.

    The message names the **key** and never the value — the same register every
    other message in this module keeps — and the built-in ``int()`` error is not
    chained for exactly that reason (it quotes the offending literal).
    """
    if raw is None:
        return None
    text = raw.strip()
    if not text.isdigit() or int(text) < 1:
        raise ValueError(f"{name} must be a positive integer (>= 1)")
    return int(text)


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

    # -- scheduled-run ceilings (P4.F4) -------------------------------------
    #: ``MIJUAL_EXTRACT_MAX_CALLS`` — the LLM call ceiling of a scheduled run.
    #: ``None`` (unset) means "use the stated default", which lives with its
    #: reasoning in :class:`mijual.scheduler.config.PipelineConfig` (60) rather
    #: than being duplicated here. It exists because the ceiling is the one knob
    #: a corpus can outgrow: a 정정 backlog larger than one run's budget leaves
    #: rows waiting for the next run (measured on production 2026-09-02 —
    #: ``60 of 60 calls, BUDGET EXHAUSTED``), and raising it must not be a code
    #: change. Read by the beat/worker path
    #: (:meth:`~mijual.scheduler.config.PipelineConfig.from_kwargs`) and by
    #: ``python -m mijual.scheduler once``, where an explicit ``--max-calls``
    #: still wins. **Unparseable is fatal, not ignored** — unlike
    #: ``MIJUAL_STALE_AFTER_HOURS`` above, this is a spend ceiling, and quietly
    #: falling back to 60 would run a whole schedule at a budget the operator
    #: believes they raised.
    extract_max_calls: int | None = None

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
    app_base_url: str = "http://localhost:3010"

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

    # -- mail (P4.S2). The D-day 마감 임박 알림 and the password-reset link both
    # travel over this one transport; see :mod:`mijual.mail`. **Unset is a real,
    # supported state**: :func:`mijual.mail.mailer_for` falls back to
    # :class:`~mijual.mail.ConsoleMailer`, which prints and sends nothing, and
    # the process says which transport it got in one INFO line at startup. That
    # is what keeps local development and the test suite credential-free.
    #: ``SMTP_HOST`` — ``mail.privateemail.com`` in production. **Its presence is
    #: the switch**: set = real mail, unset = the console transport.
    smtp_host: str | None = None
    #: ``SMTP_PORT`` — 587 (STARTTLS) or 465 (implicit TLS). It also *derives*
    #: :meth:`smtp_tls_mode` when ``SMTP_TLS`` is not set explicitly.
    smtp_port: int = 587
    smtp_user: str | None = None
    #: ``SMTP_PASS`` — a **secret**, with the same handling as every other one
    #: here: masked in ``__repr__``, never logged, raising only when used.
    smtp_password: str | None = None
    #: ``SMTP_FROM`` — the envelope/header sender **with a display name**
    #: (``"주주의관제탑 <hi@hi2vi.com>"``). Gmail renders a bare address as its
    #: local-part, so the display name is not decoration.
    smtp_from: str | None = None
    #: ``SMTP_TLS`` — ``ssl`` | ``starttls`` | ``none``. ``None`` means "derive
    #: it from the port", which is the only mode a deployment should ever need.
    #: ``none`` exists for a **local sink** (an ``aiosmtpd`` that speaks no TLS)
    #: and must be set deliberately: the failure direction matters, so an unset
    #: or misspelled value gives STARTTLS-required, never plaintext.
    smtp_tls: str | None = None

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

    def smtp_tls_mode(self) -> str:
        """``ssl`` | ``starttls`` | ``none`` — the explicit setting, else the port.

        465 is implicit TLS and everything else is STARTTLS-required. There is no
        "opportunistic" mode: a transport that would happily fall back to
        plaintext when a server declines STARTTLS is a transport that can leak a
        credential without saying so.
        """
        mode = (self.smtp_tls or "").strip().lower()
        if mode in ("ssl", "starttls", "none"):
            return mode
        return "ssl" if self.smtp_port == 465 else "starttls"

    def require_smtp(self) -> "Settings":
        """Fail loudly for a caller that must not run without a real transport.

        Names the **missing keys**, never a value — the same shape as
        :meth:`require_dart_api_key`. Nothing in the product calls it on a
        request path: the notify stage and ``create_app`` both *degrade* to the
        console transport and say so, so a deployment that forgot the keys sends
        no mail rather than failing to serve.
        """
        missing = [
            name
            for name, value in (
                ("SMTP_HOST", self.smtp_host),
                ("SMTP_FROM", self.smtp_from),
            )
            if not value
        ]
        if missing:
            raise MissingSecret(
                f"{', '.join(missing)} not found (deployment env or .env.prod)."
            )
        return self

    def with_cache_dir(self, cache_dir: Path | str) -> "Settings":
        return replace(self, cache_dir=Path(cache_dir))

    def __repr__(self) -> str:  # pragma: no cover - trivial, but load-bearing
        def mark(value: str | None) -> str:
            return "<set>" if value else "<unset>"

        return (
            "Settings(dart_api_key={}, gemini_api_key={}, session_secret={}, "
            "ops_id={}, ops_password={}, vocky_api_key={}, smtp_password={}, "
            "database_url={!r}, redis_url={!r}, cache_dir={!r})"
        ).format(
            mark(self.dart_api_key),
            mark(self.gemini_api_key),
            mark(self.session_secret),
            mark(self.ops_id),
            mark(self.ops_password),
            mark(self.vocky_api_key),
            mark(self.smtp_password),
            mask_url_password(self.database_url),
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
    smtp_port = pick("SMTP_PORT")
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
        # The one env value here that REFUSES to be mistyped (P4.F4): it is a
        # spend ceiling, so "ignore it and use the default" would silently run a
        # whole schedule at a budget the operator believes they raised. Every
        # process that loads settings fails at startup instead, loudly and by key
        # name — which `deploy/deploy.sh`'s health gate turns into a rollback.
        extract_max_calls=_positive_int(
            "MIJUAL_EXTRACT_MAX_CALLS", pick("MIJUAL_EXTRACT_MAX_CALLS")
        ),
        # Off unless explicitly turned on: a truthy string is a decision, an
        # empty or misspelled one is not. The failure direction matters —
        # `secure` on a plain-http dev server makes the cookie silently vanish.
        cookie_secure=(pick("MIJUAL_COOKIE_SECURE") or "").lower()
        in ("1", "true", "yes", "on"),
        app_base_url=(pick("MIJUAL_APP_BASE_URL") or "http://localhost:3010").rstrip("/"),
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
        # Mail (P4.S2). ``SMTP_HOST`` unset is the console transport — a
        # supported state, announced in one INFO line, not an error. A
        # non-numeric port is ignored rather than fatal, the same rule
        # ``MIJUAL_STALE_AFTER_HOURS`` follows: a mistyped ops var must not take
        # a process down.
        smtp_host=pick("SMTP_HOST"),
        smtp_port=int(smtp_port) if (smtp_port or "").isdigit() else 587,
        smtp_user=pick("SMTP_USER"),
        smtp_password=pick("SMTP_PASS"),
        smtp_from=pick("SMTP_FROM"),
        smtp_tls=pick("SMTP_TLS"),
    )
