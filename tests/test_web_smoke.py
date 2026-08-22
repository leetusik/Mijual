"""The things the HTTP skeleton must not get wrong (P5.S1, re-aimed by P6.S4).

No database, no network, no fixtures beyond the client — which is also the point
of the first test: the app has to serve while Postgres is down, because the board
is meant to go **stale, never dark**.

The two scans below are the `architecture` boundary in its current shape: **no
OpenDART call in any request path**, and **the model reached only through
`mijual.agent`**. The second replaces the absolute "no LLM call in a request
path" that P5 could assert and P6 deliberately spent — see `P6` Finding 1.
"""

from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient

from mijual.web.app import create_app

WEB_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "mijual" / "web"
#: The modules that spend an OpenDART request or an LLM call. See `mijual.web`.
SPENDING = ("mijual.dart", "mijual.collect", "mijual.extract")
#: Model SDKs. The agent's client lives in `mijual.agent` and owns the
#: credential, the call budget and the ▷ ledger; a request-path module that
#: imported one of these would be a second door to a model with none of that.
MODEL_SDKS = ("google", "openai", "anthropic")


def _imported_names(package: Path):
    """``(file, dotted name)`` for every import in every module under ``package``."""
    for path in sorted(package.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                yield path.name, name


def _offenders(package: Path, banned: tuple[str, ...]) -> list[str]:
    return [
        f"{file}: {name}"
        for file, name in _imported_names(package)
        if any(name == module or name.startswith(module + ".") for module in banned)
    ]


def test_health_answers_without_a_database_and_in_kst() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    # Absolute KST, offset included: the browser diffs this, it never derives it.
    assert body["now_kst"].endswith("+09:00")


def test_an_unknown_route_comes_back_in_the_envelope() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/no-such-route")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "not_found"
    assert isinstance(error["message"], str)
    # No Korean is invented for an error the design wrote no copy for, and an
    # absent optional key is absent rather than null.
    assert "message_ko" not in error


def test_no_request_path_module_imports_a_spending_module() -> None:
    """The `architecture` boundary, kept structurally rather than by discipline.

    **Re-aimed in `P6.S4`, not relaxed.** Through P5 the sentence was "no OpenDART
    call *and no LLM call* happens in a request path". R6's AI 질문 agent is a
    model call in a request path by design — SSE cannot be anything else — so the
    invariant this scan carries is now the half that is still absolutely true:
    **no OpenDART call happens in any request path**. `mijual.web` reads persisted
    rows, which is what keeps a dead worker leaving the board stale, never dark.
    The model half is the next test's, and it is a *routing* rule rather than an
    absence.
    """
    offenders = _offenders(WEB_PACKAGE, SPENDING)
    assert not offenders, f"no OpenDART call in a request path: {offenders}"


def test_the_model_is_reached_only_through_the_agent_package() -> None:
    """The other half of the re-aimed boundary (`P6` Finding 1).

    `mijual.web` now imports `mijual.agent` and the service now makes a model call
    in a request path — through that **one** seam. This scan is what stops a
    second one from appearing: no module under `mijual.web` may import a model SDK
    directly, so the credential, the per-turn call budget, the citation gate and
    the ▷ ledger cannot be bypassed by a handler that talks to the API itself.

    Its sibling scans are ``test_web_vocky.py`` (one outbound HTTP client, in
    `vocky.py`) and ``test_agent_tools.py`` (no spending module inside
    `mijual.agent` either).
    """
    offenders = _offenders(WEB_PACKAGE, MODEL_SDKS)
    assert not offenders, f"the model is reached only through mijual.agent: {offenders}"
