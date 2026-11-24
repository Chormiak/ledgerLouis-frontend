from datetime import date
from decimal import Decimal as D

import pytest

from ledgerlouis.infrastructure.providers.types import Bar, FundamentalsData, ListedStock, MacroData
from ledgerlouis.market import sync
from ledgerlouis.market.models import Asset, FundamentalsSnapshot, MacroPoint, PriceBar, Quote

pytestmark = pytest.mark.django_db


def stock(ticker, price="10"):
    return ListedStock(ticker, f"{ticker} SA", "stock", "Finance", "", "", D(price), D("1"), D("100"), D("1000"))


class FakeBrapi:
    def __init__(self, stocks=(), fundamentals=None):
        self.stocks = list(stocks)
        self.funds = fundamentals or {}
        self.list_calls = 0
        self.fund_calls = []

    def list_stocks(self, limit):
        self.list_calls += 1
        return self.stocks[:limit]

    def fundamentals(self, ticker):
        self.fund_calls.append(ticker)
        value = self.funds.get(ticker)
        if isinstance(value, Exception):
            raise value
        return value


class FakeBcb:
    def __init__(self):
        self.calls = []

    def series(self, code, last):
        self.calls.append(code)
        return [MacroData(date(2026, 10, 1), D("10.5"))]


def test_sync_stocks_creates_assets_and_quotes():
    report = sync.sync_stocks(FakeBrapi([stock("PETR4"), stock("VALE3")]), limit=50)
    assert report.ok == 2
    assert Asset.objects.count() == 2
    q = Asset.objects.get(ticker="PETR4").latest_quote()
    assert (q.price, q.source) == (D("10"), "brapi")


def test_sync_stocks_respects_ttl():
    client = FakeBrapi([stock("PETR4")])
    sync.sync_stocks(client, limit=50)
    report = sync.sync_stocks(client, limit=50)
    assert client.list_calls == 1
    assert report.skipped == 1
    assert Quote.objects.count() == 1


def test_sync_fundamentals_skips_failures_and_continues():
    sync.sync_stocks(FakeBrapi([stock("AAAA3"), stock("BBBB3"), stock("CCCC3")]), limit=50)
    good = FundamentalsData("CCCC3", D(1), D(1), D(1), D(1), D(1), D("0.1"))
    client = FakeBrapi(fundamentals={"AAAA3": None, "BBBB3": RuntimeError("timeout"), "CCCC3": good})

    report = sync.sync_fundamentals(client)

    assert report.ok == 1
    assert report.skipped == 1
    assert len(report.errors) == 1 and "BBBB3" in report.errors[0]
    assert FundamentalsSnapshot.objects.get().asset.ticker == "CCCC3"


def test_sync_fundamentals_respects_ttl():
    sync.sync_stocks(FakeBrapi([stock("CCCC3")]), limit=50)
    good = FundamentalsData("CCCC3", D(1), D(1), D(1), D(1), D(1), None)
    client = FakeBrapi(fundamentals={"CCCC3": good})
    sync.sync_fundamentals(client)
    sync.sync_fundamentals(client)
    assert client.fund_calls == ["CCCC3"]


def test_sync_macro_upserts_and_respects_ttl():
    client = FakeBcb()
    sync.sync_macro(client)
    sync.sync_macro(client)
    assert sorted(client.calls) == [1, 432, 13522]
    assert MacroPoint.objects.count() == 3
    assert MacroPoint.objects.get(code="432").name == "Selic meta"


class FakeHistory:
    def __init__(self, bars):
        self.bars = bars
        self.calls = []

    def history(self, ticker):
        self.calls.append(ticker)
        value = self.bars.get(ticker)
        if isinstance(value, Exception):
            raise value
        return value


def bar(day, close):
    return Bar(date(2026, 10, day), D(close), D(close), D(close), D(close), D(100))


def test_sync_history_upserts_skips_and_respects_ttl():
    for t in ["AAAA3", "BBBB3", "CCCC3"]:
        Asset.objects.create(ticker=t, name=t)
    client = FakeHistory({"AAAA3": [bar(1, "10"), bar(2, "11")], "BBBB3": None, "CCCC3": RuntimeError("timeout")})
    report = sync.sync_history(client)
    assert (report.ok, report.skipped, len(report.errors)) == (1, 1, 1)
    assert list(PriceBar.objects.values_list("close", flat=True)) == [D(10), D(11)]
    sync.sync_history(client)
    assert client.calls.count("AAAA3") == 1  # TTL de 24 h


def test_sync_history_ignores_us_assets():
    Asset.objects.create(ticker="AAPL", name="Apple", market="US")
    client = FakeHistory({"AAPL": [bar(1, "10")]})
    sync.sync_history(client)
    assert client.calls == []
    assert PriceBar.objects.count() == 0


class FakeYFinance:
    def __init__(self, snapshots=(), bars=None):
        self.snapshots = dict(snapshots)
        self.bars = bars or {}
        self.snapshot_calls = []
        self.history_calls = []

    def snapshot(self, ticker, name):
        self.snapshot_calls.append(ticker)
        value = self.snapshots[ticker]
        if isinstance(value, Exception):
            raise value
        return value

    def history(self, ticker):
        self.history_calls.append(ticker)
        value = self.bars.get(ticker)
        if isinstance(value, Exception):
            raise value
        return value


def us_stock(ticker, price="100"):
    return ListedStock(ticker, f"{ticker} Inc", "stock", "", "", "", D(price), D("1"), D("100"), D("1000"))


def test_sync_us_stocks_creates_assets_with_market_us_and_aliases():
    good = FundamentalsData("AAPL", D(1), D(1), D(1), D(1), D(1), D("0.2"))
    client = FakeYFinance({"AAPL": (us_stock("AAPL"), good)})
    specs = [{"ticker": "AAPL", "name": "Apple", "aliases": ["Apple"]}]

    report = sync.sync_us_stocks(client, specs=specs)

    assert report.ok == 1
    asset = Asset.objects.get(ticker="AAPL")
    assert (asset.market, asset.aliases) == ("US", ["Apple"])
    assert asset.latest_quote().source == "yfinance"
    assert FundamentalsSnapshot.objects.get().asset.ticker == "AAPL"


def test_sync_us_stocks_respects_ttl_and_fundamentals_gate():
    good = FundamentalsData("AAPL", D(1), D(1), D(1), D(1), D(1), None)
    client = FakeYFinance({"AAPL": (us_stock("AAPL"), good)})
    specs = [{"ticker": "AAPL", "name": "Apple", "aliases": []}]
    sync.sync_us_stocks(client, specs=specs)

    report = sync.sync_us_stocks(client, specs=specs)
    assert report.skipped == 1
    assert client.snapshot_calls == ["AAPL"]  # TTL de cotação bloqueou a segunda chamada
    assert FundamentalsSnapshot.objects.count() == 1  # gate de 24h também vale


def test_sync_us_stocks_skips_failures_and_continues():
    client = FakeYFinance({"AAPL": RuntimeError("yfinance fora do ar"), "MSFT": (us_stock("MSFT"), None)})
    specs = [{"ticker": "AAPL", "name": "Apple", "aliases": []}, {"ticker": "MSFT", "name": "Microsoft", "aliases": []}]

    report = sync.sync_us_stocks(client, specs=specs)

    assert report.ok == 1
    assert len(report.errors) == 1 and "AAPL" in report.errors[0]
    assert not Asset.objects.filter(ticker="AAPL").exists()
    assert Asset.objects.get(ticker="MSFT").latest_fundamentals() is None


def test_sync_us_history_only_targets_us_assets_and_respects_ttl():
    Asset.objects.create(ticker="AAPL", name="Apple", market="US")
    Asset.objects.create(ticker="PETR4", name="Petrobras", market="B3")
    client = FakeYFinance(bars={"AAPL": [bar(1, "10")]})

    report = sync.sync_us_history(client)

    assert client.history_calls == ["AAPL"]
    assert report.ok == 1
    sync.sync_us_history(client)
    assert client.history_calls.count("AAPL") == 1  # TTL de 24h
