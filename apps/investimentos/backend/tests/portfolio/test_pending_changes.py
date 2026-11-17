from decimal import Decimal as D

import pytest

from ledgerlouis.market.models import Asset, ScreenCommand
from ledgerlouis.portfolio import services as s
from ledgerlouis.portfolio.models import Holding, InvestorProfile

pytestmark = pytest.mark.django_db
J = {"content_type": "application/json"}


@pytest.fixture
def a():
    return Asset.objects.create(ticker="AAAA3", name="A")


def test_apply_holding_change_via_api(client, a):
    c = s.propose_holding_change("aaaa3", "100", "20", "registrar compra")
    assert [x["id"] for x in client.get("/api/pending-changes").json()] == [c.id]
    assert client.post(f"/api/pending-changes/{c.id}/apply", **J).json()["status"] == "aplicada"
    h = Holding.objects.get()
    assert (h.quantity, h.avg_price) == (D(100), D(20))
    assert client.post(f"/api/pending-changes/{c.id}/apply", **J).status_code == 400  # não aplica duas vezes
    assert client.get("/api/pending-changes").json() == []


def test_remove_and_reject(client, a):
    Holding.objects.create(asset=a, quantity=D(5))
    remove = s.propose_holding_change("AAAA3", 0, None, "vendi tudo")
    other = s.propose_holding_change("AAAA3", 7, None, "corrigir")
    assert client.post(f"/api/pending-changes/{other.id}/reject", **J).json()["status"] == "recusada"
    client.post(f"/api/pending-changes/{remove.id}/apply", **J)
    assert not Holding.objects.exists()
    assert client.post(f"/api/pending-changes/{other.id}/qualquer", **J).status_code == 404


@pytest.mark.parametrize("args", [("NADA3", 1, None, "x"), ("AAAA3", -1, None, "x"), ("AAAA3", 1, None, " "), ("AAAA3", 0, None, "x")])
def test_invalid_holding_suggestions(a, args):
    with pytest.raises(ValueError):
        s.propose_holding_change(*args)


def test_profile_change_applies_only_on_confirm(client):
    c = s.propose_profile_change({"risk_tolerance": "moderado", "monthly_contribution": "500"}, "você disse que aporta 500")
    assert InvestorProfile.get().risk_tolerance == ""
    client.post(f"/api/pending-changes/{c.id}/apply", **J)
    p = InvestorProfile.get()
    assert (p.risk_tolerance, p.monthly_contribution) == ("moderado", D(500))


def test_screen_commands_polling(client):
    assert client.get("/api/screen-commands").json() == {"latest_id": 0, "commands": []}
    from ledgerlouis.market.views import request_navigation

    first = request_navigation("/carteira", "ver carteira")
    request_navigation("/acoes/petr4", "ver PETR4")
    body = client.get(f"/api/screen-commands?after={first.id}").json()
    assert [c["payload"]["path"] for c in body["commands"]] == ["/acoes/PETR4"]
    with pytest.raises(ValueError):
        request_navigation("/admin/", "x")
    assert ScreenCommand.objects.count() == 2
