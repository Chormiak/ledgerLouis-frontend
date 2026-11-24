from datetime import timedelta
from decimal import Decimal as D

import pytest
from django.utils import timezone

from ledgerlouis.market.models import Asset, FundamentalsSnapshot, Quote

pytestmark = pytest.mark.django_db


def test_latest_quote_is_most_recent():
    asset = Asset.objects.create(ticker="PETR4", name="Petrobras")
    now = timezone.now()
    Quote.objects.create(asset=asset, price=D(30), source="brapi", fetched_at=now - timedelta(hours=1))
    newest = Quote.objects.create(asset=asset, price=D(31), source="brapi", fetched_at=now)
    assert asset.latest_quote() == newest


def test_latest_without_data_is_none():
    asset = Asset.objects.create(ticker="VALE3", name="Vale")
    assert asset.latest_quote() is None
    assert asset.latest_fundamentals() is None


def test_latest_fundamentals():
    asset = Asset.objects.create(ticker="ITUB4", name="Itaú")
    snap = FundamentalsSnapshot.objects.create(asset=asset, eps=D(4), source="brapi", fetched_at=timezone.now())
    assert asset.latest_fundamentals() == snap
