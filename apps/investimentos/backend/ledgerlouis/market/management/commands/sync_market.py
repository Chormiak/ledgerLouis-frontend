from django.conf import settings
from django.core.management.base import BaseCommand

from ledgerlouis.infrastructure.providers.bcb import BcbClient
from ledgerlouis.infrastructure.providers.brapi import BrapiClient
from ledgerlouis.infrastructure.providers.cvm import CvmClient
from ledgerlouis.infrastructure.providers.yfinance_provider import YFinanceClient
from ledgerlouis.market import sync
from ledgerlouis.portfolio.services import run_alerts


class Command(BaseCommand):
    help = (
        "Busca cotações e fundamentos (brapi e yfinance), macro (Banco Central) e notícias (CVM e RSS), "
        "respeitando o cache."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--only", choices=["stocks", "fundamentals", "history", "us_stocks", "us_history", "macro", "news"]
        )
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, only=None, limit=50, **opts):
        brapi_client = BrapiClient(settings.BRAPI_TOKEN)
        yf_client = YFinanceClient()
        if not settings.BRAPI_TOKEN and only in (None, "stocks", "fundamentals", "history"):
            self.stderr.write("BRAPI_TOKEN vazio: sem token a brapi só responde alguns tickers de teste.")
        jobs = {
            "stocks": lambda: sync.sync_stocks(brapi_client, limit=limit),
            "fundamentals": lambda: sync.sync_fundamentals(brapi_client),
            "history": lambda: sync.sync_history(brapi_client),
            "us_stocks": lambda: sync.sync_us_stocks(yf_client),
            "us_history": lambda: sync.sync_us_history(yf_client),
            "macro": lambda: sync.sync_macro(BcbClient()),
            "news": lambda: sync.sync_news(CvmClient()),
        }
        for name, job in jobs.items():
            if only and name != only:
                continue
            report = job()
            self.stdout.write(f"{name}: {report.ok} ok, {report.skipped} pulados, {len(report.errors)} erros")
            for err in report.errors:
                self.stderr.write(f"  {err}")
        # gatilhos baratos, sem IA, sobre os dados que acabaram de chegar
        self.stdout.write(f"alertas novos: {run_alerts()}")
