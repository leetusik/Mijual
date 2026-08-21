"""The three things the HTTP skeleton must not get wrong (P5.S1).

No database, no network, no fixtures beyond the client — which is also the point
of the first test: the app has to serve while Postgres is down, because the board
is meant to go **stale, never dark**.
"""

from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient

from mijual.web.app import create_app

WEB_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "mijual" / "web"
#: The modules that spend an OpenDART request or an LLM call. See `mijual.web`.
SPENDING = ("mijual.dart", "mijual.collect", "mijual.extract")


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
    """The `architecture` boundary, kept structurally rather than by discipline."""
    offenders = []
    for path in sorted(WEB_PACKAGE.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            offenders += [
                f"{path.name}: {name}"
                for name in names
                if any(name == m or name.startswith(m + ".") for m in SPENDING)
            ]
    assert not offenders, f"no OpenDART/LLM call in a request path: {offenders}"
