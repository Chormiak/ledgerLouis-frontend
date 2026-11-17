"""Coleta dos provedores para o banco. Respeita TTL para não gastar a cota gratuita."""

import re
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta

from django.utils import timezone

from ledgerlouis.infrastructure.providers import bcb, brapi, cvm, yfinance_provider
from ledgerlouis.infrastructure.providers.rss import fetch_feed

from .models import Asset, FundamentalsSnapshot, MacroPoint, NewsFeed, NewsItem, PriceBar, Quote
from .us_stocks_default import US_STOCKS

QUOTE_TTL = timedelta(minutes=15)
SLOW_TTL = timedelta(hours=24)
NEWS_TTL = timedelta(hours=6)
TICKER_RE = re.compile(r"\b[A-Z]{4}\d{1,2}\b")
AI_BUBBLE_RE = re.compile(r"\b(ia|ai|inteligência artificial|artificial intelligence|bolha|bubble)\b", re.IGNORECASE)


@dataclass
class SyncReport:
    ok: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def sync_stocks(client, limit: int = 50) -> SyncReport:
    now = timezone.now()
    if Quote.objects.filter(source=brapi.SOURCE, fetched_at__gte=now - QUOTE_TTL).exists():
        return SyncReport(skipped=1)
    report = SyncReport()
    for s in client.list_stocks(limit=limit):
        asset, _ = Asset.objects.update_or_create(
            ticker=s.ticker,
            defaults={
                "name": s.name,
                "kind": s.kind,
                "sector": s.sector,
                "subsector": s.subsector,
                "logo_url": s.logo_url,
            },
        )
        Quote.objects.create(
            asset=asset,
            price=s.price,
            change_pct=s.change_pct,
            volume=s.volume,
            market_cap=s.market_cap,
            source=brapi.SOURCE,
            fetched_at=now,
        )
        report.ok += 1
    return report


def sync_fundamentals(client) -> SyncReport:
    now = timezone.now()
    report = SyncReport()
    for asset in Asset.objects.filter(active=True, market="B3"):
        last = asset.latest_fundamentals()
        if last and last.fetched_at >= now - SLOW_TTL:
            continue
        try:
            data = client.fundamentals(asset.ticker)
        except Exception as exc:  # um ativo com problema não derruba os outros
            report.errors.append(f"{asset.ticker}: {exc}")
            continue
        if data is None:
            report.skipped += 1
            continue
        FundamentalsSnapshot.objects.create(
            asset=asset,
            revenue=data.revenue,
            ebitda=data.ebitda,
            total_debt=data.total_debt,
            total_cash=data.total_cash,
            eps=data.eps,
            roe_reported=data.roe,
            source=brapi.SOURCE,
            fetched_at=now,
        )
        report.ok += 1
    return report


def sync_history(client) -> SyncReport:
    """Candles diários por ativo, uma vez por dia (cada ativo é uma chamada à cota da brapi)."""
    now = timezone.now()
    report = SyncReport()
    for asset in Asset.objects.filter(active=True, market="B3"):
        last = asset.bars.order_by("-fetched_at").first()
        if last and last.fetched_at >= now - SLOW_TTL:
            continue
        try:
            bars = client.history(asset.ticker)
        except Exception as exc:
            report.errors.append(f"{asset.ticker}: {exc}")
            continue
        if not bars:
            report.skipped += 1
            continue
        for b in bars:
            PriceBar.objects.update_or_create(
                asset=asset,
                date=b.date,
                defaults={"open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume,
                          "source": brapi.SOURCE, "fetched_at": now},
            )
        report.ok += 1
    return report


def sync_us_stocks(client, specs=US_STOCKS) -> SyncReport:
    """Cotação + fundamentos dos EUA numa chamada só por ativo (yfinance). Cotação a cada 15 min,
    fundamentos só a cada 24h (mesmo snapshot já serve: não vale gastar outra ida à rede pra descartar)."""
    now = timezone.now()
    if Quote.objects.filter(source=yfinance_provider.SOURCE, fetched_at__gte=now - QUOTE_TTL).exists():
        return SyncReport(skipped=1)
    report = SyncReport()
    for spec in specs:
        try:
            stock, fundamentals = client.snapshot(spec["ticker"], spec["name"])
        except Exception as exc:
            report.errors.append(f"{spec['ticker']}: {exc}")
            continue
        asset, _ = Asset.objects.update_or_create(
            ticker=spec["ticker"],
            defaults={"name": stock.name, "kind": stock.kind, "market": "US", "aliases": spec["aliases"]},
        )
        Quote.objects.create(
            asset=asset,
            price=stock.price,
            change_pct=stock.change_pct,
            volume=stock.volume,
            market_cap=stock.market_cap,
            source=yfinance_provider.SOURCE,
            fetched_at=now,
        )
        last = asset.latest_fundamentals()
        if fundamentals is not None and (not last or last.fetched_at < now - SLOW_TTL):
            FundamentalsSnapshot.objects.create(
                asset=asset,
                revenue=fundamentals.revenue,
                ebitda=fundamentals.ebitda,
                total_debt=fundamentals.total_debt,
                total_cash=fundamentals.total_cash,
                eps=fundamentals.eps,
                roe_reported=fundamentals.roe,
                source=yfinance_provider.SOURCE,
                fetched_at=now,
            )
        report.ok += 1
    return report


def sync_us_history(client) -> SyncReport:
    now = timezone.now()
    report = SyncReport()
    for asset in Asset.objects.filter(active=True, market="US"):
        last = asset.bars.order_by("-fetched_at").first()
        if last and last.fetched_at >= now - SLOW_TTL:
            continue
        try:
            bars = client.history(asset.ticker)
        except Exception as exc:
            report.errors.append(f"{asset.ticker}: {exc}")
            continue
        if not bars:
            report.skipped += 1
            continue
        for b in bars:
            PriceBar.objects.update_or_create(
                asset=asset,
                date=b.date,
                defaults={"open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume,
                          "source": yfinance_provider.SOURCE, "fetched_at": now},
            )
        report.ok += 1
    return report


def sync_macro(client, last: int = 13) -> SyncReport:
    now = timezone.now()
    report = SyncReport()
    for code, (name, unit) in bcb.SERIES.items():
        if MacroPoint.objects.filter(code=str(code), fetched_at__gte=now - SLOW_TTL).exists():
            report.skipped += 1
            continue
        try:
            points = client.series(code, last=last)
        except Exception as exc:
            report.errors.append(f"SGS {code}: {exc}")
            continue
        for p in points:
            MacroPoint.objects.update_or_create(
                code=str(code),
                date=p.date,
                defaults={"name": name, "unit": unit, "value": p.value, "source": bcb.SOURCE, "fetched_at": now},
            )
        report.ok += 1
    return report


def _due(feed: NewsFeed, now) -> bool:
    return feed.fetched_at is None or feed.fetched_at < now - NEWS_TTL


def _sync_cvm(client, year: int, now, report: SyncReport) -> None:
    feed, _ = NewsFeed.objects.get_or_create(url=cvm.ipe_url(year), defaults={"name": "CVM: fatos relevantes"})
    if not _due(feed, now):
        report.skipped += 1
        return
    try:
        # CNPJ preenchido no admin tem prioridade; o FCA só completa os vazios
        for cnpj, tickers in client.tickers_by_cnpj(year).items():
            Asset.objects.filter(ticker__in=tickers, cnpj="").update(cnpj=cnpj)
        by_cnpj: dict[str, list[Asset]] = {}
        for a in Asset.objects.exclude(cnpj=""):
            by_cnpj.setdefault(cvm.only_digits(a.cnpj), []).append(a)
        for f in client.filings(year):
            if f.cnpj not in by_cnpj:
                continue
            item, _ = NewsItem.objects.get_or_create(
                url=f.url,
                defaults={
                    "title": f.title,
                    "source": cvm.SOURCE,
                    "kind": f.kind,
                    "published_at": timezone.make_aware(datetime.combine(f.delivered, time())),
                },
            )
            item.assets.add(*by_cnpj[f.cnpj])
            report.ok += 1
    except Exception as exc:
        report.errors.append(f"CVM: {exc}")
        return
    feed.fetched_at = now
    feed.save(update_fields=["fetched_at"])


def _matching_assets(title: str, known: dict[str, Asset], aliased: list[Asset]) -> set[Asset]:
    """Ticker (regex, formato B3) ou alias (substring, sem diferenciar maiúscula/minúscula) no título."""
    hits = {known[t] for t in set(TICKER_RE.findall(title)) if t in known}
    low = title.lower()
    hits |= {a for a in aliased if any(alias.lower() in low for alias in a.aliases)}
    return hits


def _sync_rss(fetch, now, report: SyncReport) -> None:
    known = {a.ticker: a for a in Asset.objects.all()}
    aliased = [a for a in known.values() if a.aliases]
    for feed in NewsFeed.objects.filter(active=True).exclude(url__startswith=cvm.BASE):
        if not _due(feed, now):
            report.skipped += 1
            continue
        try:
            items = fetch(feed.url, now=now)
        except Exception as exc:
            report.errors.append(f"{feed.name}: {exc}")
            continue
        if feed.category == "ia_bolha":
            items = [i for i in items if AI_BUBBLE_RE.search(i.title)]
        for i in items:
            item, _ = NewsItem.objects.get_or_create(
                url=i.url,
                defaults={"title": i.title, "source": feed.name, "kind": "noticia", "published_at": i.published_at},
            )
            item.assets.add(*_matching_assets(i.title, known, aliased))
            report.ok += 1
        feed.fetched_at = now
        feed.save(update_fields=["fetched_at"])


def sync_news(cvm_client, fetch=fetch_feed, year: int | None = None) -> SyncReport:
    now = timezone.now()
    report = SyncReport()
    _sync_cvm(cvm_client, year or now.year, now, report)
    _sync_rss(fetch, now, report)
    return report
