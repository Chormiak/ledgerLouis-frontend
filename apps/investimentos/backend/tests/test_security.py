import pytest
from django.utils import timezone

from ledgerlouis.market.models import Asset, Quote
from ledgerlouis.portfolio import services as s
from ledgerlouis.portfolio.models import ProposalItem

pytestmark = pytest.mark.django_db


def test_form_post_from_another_site_cannot_decide(client):
    a = Asset.objects.create(ticker="AAAA3", name="A")
    Quote.objects.create(asset=a, price=30, source="brapi", fetched_at=timezone.now())
    prop = s.save_proposal("2026-11", "r", [{"ticker": "AAAA3", "action": "entrar", "target_weight": "0.2", "thesis": "t",
                                            "risks": "r", "invalidation": "i", "sources": ["x"]}])
    item = prop.items.get()
    # formulário HTML comum (application/x-www-form-urlencoded) não passa por preflight de CORS
    r = client.post(f"/api/proposal-items/{item.id}/decision", {"decision": "aprovado"})
    assert r.status_code == 415
    item.refresh_from_db()
    assert item.decision == ProposalItem.PENDING


def test_cors_only_allows_the_dashboard(client):
    r = client.options("/api/profile", HTTP_ORIGIN="https://site-malicioso.example", HTTP_ACCESS_CONTROL_REQUEST_METHOD="PUT")
    assert "access-control-allow-origin" not in r.headers
    r = client.options("/api/profile", HTTP_ORIGIN="http://localhost:5173", HTTP_ACCESS_CONTROL_REQUEST_METHOD="PUT")
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
