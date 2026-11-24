import pytest

from ledgerlouis.market.models import ScreenContext

pytestmark = pytest.mark.django_db


def test_post_then_get(client):
    body = {"path": "/grupos/niche/varejo", "title": "Varejo", "kind": "niche", "slug": "varejo", "tickers": ["MGLU3"]}
    assert client.post("/api/screen-context", body, content_type="application/json").status_code == 204
    got = client.get("/api/screen-context").json()
    assert got["payload"] == body
    assert got["updated_at"]
    client.post("/api/screen-context", {"path": "/"}, content_type="application/json")
    assert ScreenContext.objects.count() == 1


def test_get_before_any_post(client):
    assert client.get("/api/screen-context").json() == {"payload": None, "updated_at": None}


@pytest.mark.parametrize("body", [{"title": "sem path"}, {"path": 3}, {"path": "/", "tickers": "x" * 5000}, ["lista"]])
def test_invalid_body_is_rejected(client, body):
    r = client.post("/api/screen-context", body, content_type="application/json")
    assert r.status_code == 400
    assert not ScreenContext.objects.exists()
