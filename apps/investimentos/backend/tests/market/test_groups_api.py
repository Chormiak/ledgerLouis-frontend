from datetime import date, timedelta
from decimal import Decimal as D

import pytest
from django.utils import timezone

from ledgerlouis.market.models import Asset, MacroPoint, NewsItem, Niche, Quote

pytestmark = pytest.mark.django_db


def make(ticker, sector, cap, change):
    a = Asset.objects.create(ticker=ticker, name=ticker, sector=sector)
    Quote.objects.create(
        asset=a, price=D(10), change_pct=D(change), market_cap=D(cap), source="brapi", fetched_at=timezone.now()
    )
    return a


@pytest.fixture
def data():
    a = make("BANK4", "Finance", 1, 10)
    b = make("BANK3", "Finance", 3, 0)
    c = make("SHOP3", "Retail Trade", 2, -1)
    niche = Niche.objects.create(name="Varejo", slug="varejo", macro_codes=["432"])
    niche.assets.add(c)
    MacroPoint.objects.create(
        code="432", name="Selic meta", unit="% a.a.", date=date(2026, 10, 1), value=D("10.5"), source="bcb-sgs",
        fetched_at=timezone.now(),
    )
    now = timezone.now()
    old = NewsItem.objects.create(title="Antiga", url="https://x/1", source="CVM", kind="fato_relevante", published_at=now - timedelta(days=2))
    new = NewsItem.objects.create(title="Nova", url="https://x/2", source="CVM", kind="fato_relevante", published_at=now)
    old.assets.add(c)
    new.assets.add(c)
    return a, b, c


def test_groups_list(client, data):
    body = client.get("/api/groups").json()
    finance = next(s for s in body["sectors"] if s["slug"] == "finance")
    assert (finance["name"], finance["kind"], finance["count"]) == ("Finance", "sector", 2)
    assert finance["change_pct"] == 2.5
    assert [n["slug"] for n in body["niches"]] == ["varejo"]


def test_niche_detail_has_members_macro_and_news(client, data):
    body = client.get("/api/groups/niche/varejo").json()
    assert [m["ticker"] for m in body["members"]] == ["SHOP3"]
    assert body["macro"][0]["code"] == "432"
    assert [n["title"] for n in body["news"]] == ["Nova", "Antiga"]
    assert body["news"][0]["tickers"] == ["SHOP3"]


def test_sector_detail_and_404(client, data):
    body = client.get("/api/groups/sector/finance").json()
    assert body["count"] == 2
    assert body["macro"] == []
    assert client.get("/api/groups/sector/nada").status_code == 404
    assert client.get("/api/groups/outro/varejo").status_code == 404
