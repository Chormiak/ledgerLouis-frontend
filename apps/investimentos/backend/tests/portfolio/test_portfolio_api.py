from decimal import Decimal as D

import pytest
from django.utils import timezone

from ledgerlouis.market.models import Asset, Quote
from ledgerlouis.portfolio import services as s
from ledgerlouis.portfolio.models import Alert, Holding

pytestmark = pytest.mark.django_db
J = {"content_type": "application/json"}


@pytest.fixture
def a():
    a = Asset.objects.create(ticker="AAAA3", name="A", sector="Fin")
    Quote.objects.create(asset=a, price=D(30), change_pct=D(1), market_cap=D(1000), source="brapi", fetched_at=timezone.now())
    return a


def test_profile_get_put_and_validation(client):
    assert client.get("/api/profile").json()["missing"] == ["horizon_years", "risk_tolerance", "monthly_contribution"]
    ok = client.put("/api/profile", {"horizon_years": 10, "risk_tolerance": "moderado", "monthly_contribution": "500", "avoid_sectors": ["Tabaco"]}, **J)
    assert ok.status_code == 200
    assert ok.json()["missing"] == []
    bad = client.put("/api/profile", {"risk_tolerance": "yolo", "horizon_years": -1, "alert_max_asset_weight": 2}, **J)
    assert bad.status_code == 400
    assert set(bad.json()["errors"]) == {"risk_tolerance", "horizon_years", "alert_max_asset_weight"}


def test_holdings_put_get_delete(client, a):
    assert client.put("/api/holdings/aaaa3", {"quantity": "10", "avg_price": "20"}, **J).status_code == 200
    body = client.get("/api/portfolio").json()
    assert body["positions"][0]["weight"] == 1.0
    assert body["exposure"]["sector"] == {"Fin": 1.0}
    assert client.put("/api/holdings/NADA3", {"quantity": "1"}, **J).status_code == 404
    assert client.put("/api/holdings/AAAA3", {"quantity": "-1"}, **J).status_code == 400
    assert client.delete("/api/holdings/AAAA3").status_code == 204
    assert not Holding.objects.exists()


def test_proposal_review_flow(client, a):
    prop = s.save_proposal("2026-11", "resumo", [{"ticker": "AAAA3", "action": "entrar", "target_weight": "0.3", "thesis": "t", "risks": "r", "invalidation": "i", "sources": ["brapi"]}])
    listed = client.get("/api/proposals").json()
    assert listed[0]["status"] == "rascunho"
    detail = client.get(f"/api/proposals/{prop.id}").json()
    item = detail["items"][0]
    assert (item["ticker"], item["target_weight"], item["current_price"]) == ("AAAA3", 0.3, 30.0)
    r = client.post(f"/api/proposal-items/{item['id']}/decision", {"decision": "ajustado", "adjusted_weight": "0.2", "comment": "menos"}, **J)
    assert r.status_code == 200 and r.json()["decision"] == "ajustado"
    assert client.post(f"/api/proposal-items/{item['id']}/decision", {"decision": "ajustado"}, **J).status_code == 400
    assert client.get("/api/scoreboard").json()["rows"][0]["decision"] == "ajustado"


def test_alerts_list_and_mark_seen(client, a):
    alert = Alert.objects.create(kind="queda_forte", key="k", title="caiu", created_on=timezone.localdate())
    assert client.get("/api/alerts").json()[0]["title"] == "caiu"
    assert client.post(f"/api/alerts/{alert.id}/seen").status_code == 204
    alert.refresh_from_db()
    assert alert.seen
