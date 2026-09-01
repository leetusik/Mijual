"""The production entrypoint: ``python -m mijual.web``.

    python -m mijual.web                      # 0.0.0.0:8010
    python -m mijual.web --host 127.0.0.1 --port 8011
    MIJUAL_API_HOST=127.0.0.1 MIJUAL_API_PORT=8011 python -m mijual.web

Why this module exists rather than a bare ``uvicorn mijual.web.app:app`` in the
container's ``CMD``:

**1. The root logging config, or the ▷ ledger goes nowhere.** The per-turn
agent-spend line (`operations` § *Observability*) is ``log.info`` on
:mod:`mijual.web.ask`'s own logger. ``uvicorn`` configures **only** its own
loggers, so under a bare ``uvicorn`` the root logger stays at ``WARNING`` and
agent spend is recorded *nowhere at all*. Nothing in the application calls
``basicConfig`` on purpose — a library that does pre-empts the deployment's own
choice — **so the deployment must make one**, and this module is the deployment.
It installs the same format ``make api-up`` inlines, then hands uvicorn
``log_config=None`` so uvicorn does not overwrite it.

**2. One worker, deliberately.** :class:`mijual.web.ask.TurnLimiter` and the
login-attempt counters are **per process**: N workers would mean N× the stated
cap, silently. The deploy target is a small shared box, so the honest
configuration is one worker and a limiter that means what it says. Scaling the
service is a decision to make with the limiter, not around it.

The module opens no connection and reads no secret of its own: everything comes
from :class:`mijual.config.Settings` inside the app, which the container fills
through compose's ``env_file``.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

#: The same format ``make api-up`` inlines, so a dev log and a container log read
#: alike.
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8010


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m mijual.web", description=__doc__)
    parser.add_argument(
        "--host",
        default=os.environ.get("MIJUAL_API_HOST") or DEFAULT_HOST,
        help=f"bind address (default: $MIJUAL_API_HOST or {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MIJUAL_API_PORT") or DEFAULT_PORT),
        help=f"bind port (default: $MIJUAL_API_PORT or {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--log-level",
        default=os.environ.get("MIJUAL_LOG_LEVEL") or "INFO",
        help="root log level (default: $MIJUAL_LOG_LEVEL or INFO)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # The whole point of this entrypoint — see the module docstring.
    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format=LOG_FORMAT,
    )

    import uvicorn

    uvicorn.run(
        "mijual.web.app:app",
        host=args.host,
        port=args.port,
        # Do not let uvicorn replace the configuration installed above.
        log_config=None,
        # Per-process limiter state — see the docstring. Not a knob.
        workers=1,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
