from datetime import date, timedelta
from decimal import Decimal as D

import pytest
from django.utils import timezone

from ledgerlouis.market.models import Asset, FundamentalsSnapshot, Niche, PriceBar, Quote

pytestmark = pytest.mark.django_db


def make(ticker, eps):
    a = Asset.objects.create(ticker=ticker, name=ticker, sector="Finance")
    now = timezone.now()
    Quote.objects.create(asset=a, price=D(30), change_pct=D(1), market_cap=D(1000), source="brapi", fetched_at=now)
    FundamentalsSnapshot.objects.create(asset=a, eps=D(eps), revenue=D(400), ebitda=D(13), total_debt=D(40),
                                        total_cash=D(10), roe_reported=D("0.18"), source="brapi", fetched_at=now)
    return a


def test_asset_detail_has_history_technicals_health_and_niches(client):
    a = make("AAAA3", 6)  # P/L 5
    make("BBBB3", 3)  # P/L 10
    make("CCCC3", 2)  # P/L 15
    Niche.objects.create(name="Bancos", slug="bancos").assets.add(a)
    start = date(2026, 8, 1)
    for i in range(30):
        PriceBar.objects.create(asset=a, date=start + timedelta(days=i), open=D(10), high=D(11), low=D(9),
                                close=D(10 + i), volume=D(100), source="brapi", fetched_at=timezone.now())

    body = client.get("/api/assets/aaaa3").json()

    h = body["history"]
    assert h["days"] == 30 and len(h["bars"]) == 30
    assert h["sma20"][18] is None and h["sma20"][19] == 19.5
    assert h["rsi14"] == 100
    assert h["return_period"] == pytest.approx(29 / 10)
    assert body["sector_group"]["medians"]["pe"] == 10
    assert body["health"]["pe"] == "melhor"
    assert body["niches"] == [{"slug": "bancos", "name": "Bancos"}]


def test_asset_detail_without_history_or_sector(client):
    Asset.objects.create(ticker="ZZZZ3", name="Z")
    body = client.get("/api/assets/ZZZZ3").json()
    assert body["history"]["days"] == 0 and body["history"]["rsi14"] is None
    assert body["sector_group"] is None
    assert set(body["health"].values()) == {None}


def test_sparklines_last_30_in_order(client):
    a = Asset.objects.create(ticker="AAAA3", name="A")
    for i in range(35):
        PriceBar.objects.create(asset=a, date=date(2026, 8, 1) + timedelta(days=i), open=D(1), high=D(1), low=D(1),
                                close=D(i), volume=D(1), source="brapi", fetched_at=timezone.now())
    closes = client.get("/api/sparklines").json()["AAAA3"]
    assert closes == list(range(5, 35))
