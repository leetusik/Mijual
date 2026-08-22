"""vocky 관찰 뷰 (P5.S18): the degraded paths, and the decided shape.

`CAPTURED` is a **real** response from a local vocky stack (2026-08-22), trimmed
to one record — the shape §6.3 asked this build to decide against the running
product, so the mapping is pinned against what vocky actually sends rather than
against what this repo would like it to send.
"""

from __future__ import annotations

import ast
import io
import json
from pathlib import Path

from mijual.config import Settings
from mijual.web import vocky

CAPTURED = {
    "records": [
        {
            "id": "a7cb1ae4-a445-4961-b9d4-e65282b47491",
            "message": "종목 조회에서 보유량을 넣으면 환산액이 바로 보여서 좋았어요",
            "source_product": "mijual",
            "feedback_value": 1,
            "comment": None,
            "channel": "web",
            "source_integration": "web-backend",
            "recorded_by": "human",
            "conversation_id": None,
            "session_id": None,
            "user_id": None,
            "trigger_type": "like",
            "trigger_message": "의견 보내기",
            "trigger_metadata": {},
            "target_type": "surface",
            "target_id": "/stocks",
            "target_role": None,
            "target_text": "내 종목 조회",
            "event_at": None,
            "ingested_at": "2026-08-22T07:33:03.057136Z",
            "tags": [],
            "messages": [],
            "used_context": [],
            "source_metadata": {},
            "attributes": {},
        }
    ],
    "next_cursor": "eyJpZCI6ImE3Y2IxYWU0In0",
}

CONFIGURED = Settings(vocky_api_base="http://vocky.invalid", vocky_api_key="vk_test")


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _answer(monkeypatch, body, url_box: list[str] | None = None):
    def fake_open(request, timeout=None):
        if url_box is not None:
            url_box.append(request.full_url)
        assert request.get_method() == "GET", "the observation API is read-only"
        assert request.get_header("Authorization", "").startswith("Bearer vk_")
        return _Response(json.dumps(body).encode("utf-8"))

    monkeypatch.setattr(vocky._OPENER, "open", fake_open)


def test_unconfigured_is_a_state_not_a_failure() -> None:
    """연결 전: the surface renders 「API shape 확정 대기」, so the API says which."""
    body = vocky.observe(Settings()).payload()
    assert body["state"] == "unconfigured"
    assert body["rows"] == [] and body["count"] == 0
    # No base is echoed and no cursor/reason is invented for a state with none.
    assert "base" not in body["source"] and "next_cursor" not in body
    # The decided field set travels even with nothing to put in it — that is what
    # replaces the card's `?` column names.
    assert body["fields"] == list(vocky.ROW_FIELDS)


def test_the_decided_shape_maps_a_real_vocky_record(monkeypatch) -> None:
    urls: list[str] = []
    _answer(monkeypatch, CAPTURED, urls)
    body = vocky.observe(CONFIGURED, limit=2, cursor="prev").payload()

    assert body["state"] == "ok" and body["count"] == 1
    row = body["rows"][0]
    # Absolute KST, never vocky's UTC: the ops `Stamp` slices this string.
    assert row["ingested_at"] == "2026-08-22T16:33:03+09:00"
    # vocky's own key names, and only the observed ones.
    assert set(row) <= set(vocky.ROW_FIELDS)
    assert row["message"].startswith("종목 조회에서") and row["trigger_type"] == "like"
    # Correlation handles and free-form blobs are not forwarded at all.
    assert not {"user_id", "session_id", "attributes", "source_metadata"} & set(row)
    # An absent value is absent, never null or an empty list.
    assert "comment" not in row and "tags" not in row
    # vocky's opaque cursor travels through untouched, both ways.
    assert body["next_cursor"] == CAPTURED["next_cursor"]
    assert "cursor=prev" in urls[0] and "limit=2" in urls[0]


def test_an_unreachable_vocky_degrades_and_never_fabricates_a_row(monkeypatch) -> None:
    """`P5.S9`'s Redis precedent: the panel reports the failure and stays up."""

    def boom(request, timeout=None):
        raise TimeoutError("slow")

    monkeypatch.setattr(vocky._OPENER, "open", boom)
    body = vocky.observe(CONFIGURED).payload()
    assert body["state"] == "unreachable" and body["reason"] == "TimeoutError"
    assert body["rows"] == [] and body["count"] == 0

    # A body that is not vocky's is the same kind of fact, not a crash.
    _answer(monkeypatch, {"unexpected": True})
    assert vocky.observe(CONFIGURED).payload()["state"] == "unreachable"


def test_only_the_vocky_module_may_speak_http(monkeypatch) -> None:
    """The one outbound call `mijual.web` makes itself lives in one file, by test.

    **Re-aimed in `P6.S4`.** `test_web_smoke` keeps OpenDART out of `web/`
    entirely and keeps every model SDK out of it too — the AI 질문 agent's model
    call is reached through `mijual.agent`, which owns the SDK, the credential and
    the budget. So this scan's sentence is now precise: **`mijual.web` itself
    speaks HTTP in exactly one file**, and a later slice cannot quietly add a
    second external dependency to a request path. What travels through
    `mijual.agent` is HTTP too — it is just not `mijual.web`'s, and it is scanned
    from the other side (`tests/test_agent_tools.py`).
    """
    package = Path(__file__).resolve().parents[1] / "src" / "mijual" / "web"
    clients = ("urllib", "http.client", "socket", "requests", "httpx")
    offenders = []
    for path in sorted(package.rglob("*.py")):
        if path.name == "vocky.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
            )
            offenders += [
                f"{path.name}: {name}"
                for name in names
                if any(name == m or name.startswith(m + ".") for m in clients)
            ]
    assert not offenders, f"one outbound HTTP client, in vocky.py: {offenders}"
