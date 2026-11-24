from datetime import date
from decimal import Decimal as D

import pytest
from django.utils import timezone

from ledgerlouis.market.models import Asset, FundamentalsSnapshot, MacroPoint, Quote

pytestmark = pytest.mark.django_db


@pytest.fixture
def petr():
    a = Asset.objects.create(ticker="PETR4", name="Petrobras", sector="Energy Minerals")
    now = timezone.now()
    Quote.objects.create(
        asset=a, price=D(30), change_pct=D("1.5"), volume=D(10), market_cap=D(1000), source="brapi", fetched_at=now
    )
    FundamentalsSnapshot.objects.create(
        asset=a,
        revenue=D(400),
        ebitda=D(13),
        total_debt=D(40),
        total_cash=D(10),
        eps=D(3),
        roe_reported=D("0.18"),
        source="brapi",
        fetched_at=now,
    )
    return a


def test_assets_list_has_quote_and_computed_indicators(client, petr):
    [item] = client.get("/api/assets").json()
    assert item["ticker"] == "PETR4"
    assert item["quote"]["price"] == 30
    assert item["quote"]["source"] == "brapi"
    assert item["quote"]["fetched_at"]
    assert item["indicators"]["pe"] == 10
    assert item["indicators"]["net_margin"] == 0.25
    assert item["indicators"]["roe"] == 0.18
    assert item["fundamentals_source"] == "brapi"


def test_asset_without_fundamentals_has_null_indicators(client):
    Asset.objects.create(ticker="VALE3", name="Vale")
    [item] = client.get("/api/assets").json()
    assert item["quote"] is None
    assert set(item["indicators"].values()) == {None}
    assert item["fundamentals_fetched_at"] is None


def test_asset_detail_and_404(client, petr):
    assert client.get("/api/assets/PETR4").json()["ticker"] == "PETR4"
    assert client.get("/api/assets/petr4").status_code == 200
    assert client.get("/api/assets/NADA3").status_code == 404


def test_macro_returns_latest_point_per_series(client):
    now = timezone.now()
    for d, v in [(date(2026, 9, 1), "10.5"), (date(2026, 10, 1), "10.75")]:
        MacroPoint.objects.create(
            code="432", name="Selic meta", unit="% a.a.", date=d, value=D(v), source="bcb-sgs", fetched_at=now
        )
    [item] = client.get("/api/macro").json()
    assert (item["code"], item["date"], item["value"]) == ("432", "2026-10-01", 10.75)
    assert item["source"] == "bcb-sgs"
