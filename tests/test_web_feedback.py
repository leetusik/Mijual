"""의견 보내기 (P8.S3, R8): the three outcomes the signed surface can show.

vocky is mocked at the same seam ``test_web_vocky.py`` uses — ``vocky._OPENER`` —
so this exercises the real route, the real payload construction and the real
error mapping, with no network. What is asserted is what the screen branches on:
a 202 carries vocky's own ``request_id``, an empty message never leaves this
service, and a refused credential comes back **not retryable**.
"""

from __future__ import annotations

import io
import json

import pytest
import urllib.error
from fastapi.testclient import TestClient

from mijual.config import Settings
from mijual.web import vocky
from mijual.web.app import create_app
from mijual.web.csrf import CSRF_HEADER

CONFIGURED = Settings(vocky_api_base="http://vocky.invalid", vocky_api_key="vk_test")


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(CONFIGURED))


def test_a_202_passes_vockys_own_receipt_through(monkeypatch, client) -> None:
    sent: list[dict] = []

    def fake_open(request, timeout=None):
        assert request.get_method() == "POST"
        assert request.get_header("Authorization", "").startswith("Bearer vk_")
        assert request.full_url.endswith("/api/feedback")
        sent.append(json.loads(request.data.decode("utf-8")))
        return _Response(
            json.dumps(
                {
                    "request_id": "fb_9c1d",
                    "accepted_at": "2026-08-23T04:05:06.123456Z",
                    "status": "accepted",
                }
            ).encode("utf-8")
        )

    monkeypatch.setattr(vocky._OPENER, "open", fake_open)
    answer = client.post(
        "/feedback",
        json={"message": "  청약 기간이 공시와 다릅니다  ", "channel": "mobile"},
        headers={CSRF_HEADER: "1"},
    )

    assert answer.status_code == 202
    # The 접수 번호 is vocky's, never minted here; the instant is served in KST.
    assert answer.json() == {
        "request_id": "fb_9c1d",
        "accepted_at": "2026-08-23T13:05:06+09:00",
    }
    # R8's payload exactly, trimmed message, no invented field, no session id.
    assert sent == [
        {
            "message": "청약 기간이 공시와 다릅니다",
            "source": {"product": "mijual"},
            "recorded_by": "human",
            "channel": "mobile",
            "target_type": "surface",
        }
    ]


def test_an_empty_message_never_leaves_this_service(monkeypatch, client) -> None:
    def fake_open(request, timeout=None):  # pragma: no cover - must not run
        raise AssertionError("a blank 의견 must not reach vocky")

    monkeypatch.setattr(vocky._OPENER, "open", fake_open)
    answer = client.post("/feedback", json={"message": "   "}, headers={CSRF_HEADER: "1"})
    assert answer.status_code == 400
    assert answer.json()["error"]["code"] == "feedback_empty"


def test_a_refused_credential_is_failed_without_retry(monkeypatch, client) -> None:
    def fake_open(request, timeout=None):
        raise urllib.error.HTTPError(request.full_url, 401, "Unauthorized", {}, None)

    monkeypatch.setattr(vocky._OPENER, "open", fake_open)
    answer = client.post("/feedback", json={"message": "의견"}, headers={CSRF_HEADER: "1"})

    assert answer.status_code == 502
    body = answer.json()["error"]
    assert body["code"] == "feedback_rejected" and body["retryable"] is False
    # A 5xx is the other half of the same mapping: 실패 + 다시 시도.
    monkeypatch.setattr(
        vocky._OPENER,
        "open",
        lambda request, timeout=None: (_ for _ in ()).throw(TimeoutError()),
    )
    again = client.post("/feedback", json={"message": "의견"}, headers={CSRF_HEADER: "1"})
    assert again.status_code == 503
    assert again.json()["error"]["retryable"] is True
