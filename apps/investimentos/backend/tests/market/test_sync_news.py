from datetime import UTC, date, datetime

import pytest

from ledgerlouis.infrastructure.providers.cvm import Filing
from ledgerlouis.infrastructure.providers.rss import FeedItem
from ledgerlouis.market.models import Asset, NewsFeed, NewsItem
from ledgerlouis.market.sync import sync_news

pytestmark = pytest.mark.django_db


class FakeCvm:
    def __init__(self):
        self.calls = 0

    def tickers_by_cnpj(self, year):
        return {"33000167000101": {"PETR3", "PETR4"}}

    def filings(self, year):
        self.calls += 1
        return [
            Filing("33000167000101", "PETROBRAS", "fato_relevante", "Fato relevante: X", date(2026, 10, 21), "https://cvm/1"),
            Filing("99999999000199", "OUTRA", "fato_relevante", "Fato relevante: Y", date(2026, 10, 21), "https://cvm/2"),
        ]


def fake_fetch(url, now):
    return [
        FeedItem("PETR4 e VALE3 em destaque", "https://n/1", datetime(2026, 10, 28, tzinfo=UTC)),
        FeedItem("XXXX3 desconhecida", "https://n/2", datetime(2026, 10, 28, tzinfo=UTC)),
    ]


@pytest.fixture
def assets():
    return Asset.objects.create(ticker="PETR4", name="Petrobras"), Asset.objects.create(ticker="VALE3", name="Vale")


def test_cvm_links_by_cnpj_and_fills_cnpj(assets):
    report = sync_news(FakeCvm(), fetch=fake_fetch, year=2026)
    assert report.errors == []
    petr = Asset.objects.get(ticker="PETR4")
    assert petr.cnpj == "33000167000101"
    item = NewsItem.objects.get(url="https://cvm/1")
    assert (item.source, item.kind) == ("CVM", "fato_relevante")
    assert list(item.assets.values_list("ticker", flat=True)) == ["PETR4"]
    assert not NewsItem.objects.filter(url="https://cvm/2").exists()  # empresa fora da base


def test_rss_links_cited_tickers_only(assets):
    NewsFeed.objects.create(name="Economia", url="https://feed/rss")
    sync_news(FakeCvm(), fetch=fake_fetch, year=2026)
    item = NewsItem.objects.get(url="https://n/1")
    assert sorted(item.assets.values_list("ticker", flat=True)) == ["PETR4", "VALE3"]
    assert item.source == "Economia"
    assert NewsItem.objects.get(url="https://n/2").assets.count() == 0


def test_ttl_and_no_duplicates(assets):
    cvm = FakeCvm()
    sync_news(cvm, fetch=fake_fetch, year=2026)
    sync_news(cvm, fetch=fake_fetch, year=2026)
    assert cvm.calls == 1
    assert NewsItem.objects.filter(url="https://cvm/1").count() == 1


def test_cvm_failure_does_not_stop_rss(assets):
    class Broken(FakeCvm):
        def tickers_by_cnpj(self, year):
            raise RuntimeError("CVM fora do ar")

    NewsFeed.objects.create(name="Economia", url="https://feed/rss")
    report = sync_news(Broken(), fetch=fake_fetch, year=2026)
    assert any("CVM fora do ar" in e for e in report.errors)
    assert NewsItem.objects.filter(url="https://n/1").exists()


def test_rss_links_by_alias_for_us_tickers():
    Asset.objects.create(ticker="AMZN", name="Amazon", market="US", aliases=["Amazon"])

    def fetch(url, now):
        return [FeedItem("Amazon anuncia resultados", "https://n/amzn", datetime(2026, 10, 28, tzinfo=UTC))]

    NewsFeed.objects.create(name="Tech", url="https://feed/tech")
    sync_news(FakeCvm(), fetch=fetch, year=2026)
    item = NewsItem.objects.get(url="https://n/amzn")
    assert list(item.assets.values_list("ticker", flat=True)) == ["AMZN"]


def test_ia_bolha_feed_keeps_only_matching_titles():
    def fetch(url, now):
        return [
            FeedItem("A bolha da IA pode estourar?", "https://n/ia1", datetime(2026, 10, 28, tzinfo=UTC)),
            FeedItem("Assunto qualquer sem relação", "https://n/ia2", datetime(2026, 10, 28, tzinfo=UTC)),
        ]

    NewsFeed.objects.create(name="TechCrunch", url="https://feed/tc", category="ia_bolha")
    sync_news(FakeCvm(), fetch=fetch, year=2026)
    assert NewsItem.objects.filter(url="https://n/ia1").exists()
    assert not NewsItem.objects.filter(url="https://n/ia2").exists()
