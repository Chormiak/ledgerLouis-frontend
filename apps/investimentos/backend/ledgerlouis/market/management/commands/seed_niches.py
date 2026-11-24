from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ledgerlouis.market.models import Asset, Niche, NewsFeed
from ledgerlouis.market.niches_default import DEFAULT_NEWS_FEEDS, DEFAULT_NICHES


def seed_news_feeds() -> int:
    """Cadastra os feeds iniciais de geopolítica e bolha da IA. Idempotente (url é unique)."""
    created = 0
    for spec in DEFAULT_NEWS_FEEDS:
        _, was_created = NewsFeed.objects.get_or_create(
            url=spec["url"], defaults={"name": spec["name"], "category": spec["category"]}
        )
        created += was_created
    return created


def seed_niches() -> int:
    """Cria os nichos iniciais e liga os tickers existentes. Idempotente; não remove ligações feitas no admin."""
    linked = 0
    for spec in DEFAULT_NICHES:
        niche, _ = Niche.objects.get_or_create(
            slug=slugify(spec["name"]),
            defaults={
                "name": spec["name"],
                "description": spec["description"],
                "macro_codes": spec["macro"],
                "external": spec.get("external", False),
            },
        )
        assets = Asset.objects.filter(ticker__in=spec["tickers"])
        niche.assets.add(*assets)
        linked += assets.count()
    return linked


class Command(BaseCommand):
    help = "Cria os nichos iniciais (varejo, IA e tecnologia, imóveis...) e liga os tickers já sincronizados."

    def handle(self, *args, **opts):
        linked = seed_niches()
        feeds = seed_news_feeds()
        self.stdout.write(f"{Niche.objects.count()} nichos prontos, {linked} ativos ligados, {feeds} feeds novos")
