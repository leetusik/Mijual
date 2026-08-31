"""``GET /site/contact`` — the operator's one string, and the parts it splits into.

Two cases, because two things can go wrong. Set → the route serves the words
verbatim **and** the address/number the footer types apart, from however the
operator wrote them. Unset → three nulls with a 200, never an error and never a
placeholder: the chrome then renders no contact line at all.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from mijual.config import Settings
from mijual.web.app import create_app
from mijual.web.site import split_contact


def _client(contact: str | None) -> TestClient:
    return TestClient(create_app(settings=Settings(operator_contact=contact)))


def test_a_set_contact_is_served_verbatim_and_split_into_its_parts() -> None:
    raw = "이메일 leetusik@gmail.com · 전화 010-3772-9916"
    body = _client(raw).get("/site/contact").json()

    assert body == {
        "contact": raw,
        "email": "leetusik@gmail.com",
        "phone": "010-3772-9916",
    }
    # However it is written: labels, order and hyphens are the operator's choice.
    assert split_contact("01037729916, leetusik@gmail.com") == (
        "01037729916, leetusik@gmail.com",
        "leetusik@gmail.com",
        "01037729916",
    )


def test_an_unset_contact_is_three_nulls_and_a_200() -> None:
    response = _client(None).get("/site/contact")
    assert response.status_code == 200
    assert response.json() == {"contact": None, "email": None, "phone": None}
