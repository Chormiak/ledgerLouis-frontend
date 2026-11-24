"""Dispara a atualização dos dados quando o Erick abre o site, sem travar a resposta."""

import logging
import threading

from django.conf import settings
from django.db import close_old_connections
from django.http import JsonResponse

from ledgerlouis.infrastructure.providers.bcb import BcbClient
from ledgerlouis.infrastructure.providers.brapi import BrapiClient
from ledgerlouis.infrastructure.providers.cvm import CvmClient
from ledgerlouis.infrastructure.providers.yfinance_provider import YFinanceClient
from ledgerlouis.portfolio.services import run_alerts

from . import sync

logger = logging.getLogger(__name__)


def _run() -> None:
    try:
        brapi_client = BrapiClient(settings.BRAPI_TOKEN)
        sync.sync_stocks(brapi_client)
        sync.sync_fundamentals(brapi_client)
        sync.sync_history(brapi_client)
        yf_client = YFinanceClient()
        sync.sync_us_stocks(yf_client)
        sync.sync_us_history(yf_client)
        sync.sync_macro(BcbClient())
        sync.sync_news(CvmClient())
        run_alerts()  # gatilho barato, sem IA, sobre os dados que acabaram de chegar
    except Exception:
        logger.exception("sync-trigger falhou")
    finally:
        close_old_connections()


def trigger(request):
    """Cada job já não faz nada se o TTL não passou: seguro chamar a cada abertura do site."""
    threading.Thread(target=_run, daemon=True).start()
    return JsonResponse({"started": True})
