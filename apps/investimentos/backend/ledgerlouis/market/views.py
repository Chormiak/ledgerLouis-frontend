import json
import re

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from ledgerlouis.domain.fundamentals import compute_indicators
from ledgerlouis.domain.groups import summarize
from ledgerlouis.domain.health import compare_to_median
from ledgerlouis.domain.technical import annualized_volatility, period_return, rsi, sma

from .models import Asset, MacroPoint, NewsFeed, NewsItem, Niche, PriceBar, ScreenCommand, ScreenContext


def asset_payload(asset: Asset) -> dict:
    q = asset.latest_quote()
    f = asset.latest_fundamentals()
    snapshot = {}
    if q:
        snapshot |= {"price": q.price, "market_cap": q.market_cap}
    if f:
        snapshot |= {
            "eps": f.eps,
            "revenue": f.revenue,
            "ebitda": f.ebitda,
            "total_debt": f.total_debt,
            "total_cash": f.total_cash,
            "roe_reported": f.roe_reported,
        }
    return {
        "ticker": asset.ticker,
        "name": asset.name,
        "sector": asset.sector,
        "subsector": asset.subsector,
        "logo_url": asset.logo_url,
        "quote": q
        and {
            "price": q.price,
            "change_pct": q.change_pct,
            "volume": q.volume,
            "market_cap": q.market_cap,
            "source": q.source,
            "fetched_at": q.fetched_at,
        },
        "indicators": compute_indicators(snapshot),
        "fundamentals_source": f.source if f else None,
        "fundamentals_fetched_at": f.fetched_at if f else None,
    }


@api_view()
def assets(request):
    return Response([asset_payload(a) for a in Asset.objects.filter(active=True, market="B3")])


@api_view()
def asset_detail(request, ticker):
    return Response(asset_full(get_object_or_404(Asset, ticker=ticker.upper())))


def asset_full(asset: Asset, with_bars: bool = True) -> dict:
    """Página da ação: payload da lista + histórico, técnicos, saúde contra a mediana do setor, nichos e notícias."""
    base = asset_payload(asset)
    bars = list(asset.bars.all())
    closes = [float(b.close) for b in bars]
    peers = [asset_payload(a) for a in Asset.objects.filter(active=True, sector=asset.sector)] if asset.sector else []
    medians = summary("sector", slugify(asset.sector), asset.sector, peers)["medians"] if peers else {}
    history = {
        "source": bars[-1].source if bars else None,
        "fetched_at": bars[-1].fetched_at if bars else None,
        "days": len(bars),
        "rsi14": rsi(closes, 14),
        "volatility": annualized_volatility(closes),
        "return_1m": period_return(closes, 21),
        "return_period": period_return(closes, len(closes) - 1) if len(closes) > 1 else None,
    }
    if with_bars:
        history["bars"] = [
            {"date": b.date, "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume}
            for b in bars
        ]
        history["sma20"] = sma(closes, 20)
    news = asset.news.prefetch_related("assets")[:15]
    return {
        **base,
        "history": history,
        "sector_group": {"slug": slugify(asset.sector), "name": asset.sector, "count": len(peers), "medians": medians}
        if asset.sector
        else None,
        "health": compare_to_median(base["indicators"], medians),
        "niches": [{"slug": n.slug, "name": n.name} for n in asset.niches.all()],
        "news": news_payload(news, [asset.ticker]),
    }


def latest_macro(codes=None) -> list[dict]:
    latest = {}
    qs = MacroPoint.objects.all() if codes is None else MacroPoint.objects.filter(code__in=codes)
    for p in qs:  # ordenado por code, -date: o primeiro de cada série é o mais recente
        latest.setdefault(p.code, p)
    return [
        {
            "code": p.code,
            "name": p.name,
            "unit": p.unit,
            "date": p.date,
            "value": p.value,
            "source": p.source,
            "fetched_at": p.fetched_at,
        }
        for p in latest.values()
    ]


@api_view()
def macro(request):
    return Response(latest_macro())


def summary(kind: str, slug: str, name: str, members: list[dict]) -> dict:
    s = summarize(
        [
            {
                "market_cap": m["quote"] and m["quote"]["market_cap"],
                "change_pct": m["quote"] and m["quote"]["change_pct"],
                "indicators": m["indicators"],
            }
            for m in members
        ]
    )
    return {"kind": kind, "slug": slug, "name": name, **s}


def sector_members() -> dict[str, tuple[str, list[dict]]]:
    """slug -> (nome do setor, payloads dos ativos)."""
    groups: dict[str, tuple[str, list[dict]]] = {}
    for a in Asset.objects.filter(active=True, market="B3").exclude(sector=""):
        groups.setdefault(slugify(a.sector), (a.sector, []))[1].append(asset_payload(a))
    return groups


def news_payload(items, tickers: list[str]) -> list[dict]:
    return [
        {
            "title": n.title,
            "url": n.url,
            "source": n.source,
            "kind": n.kind,
            "published_at": n.published_at,
            "tickers": sorted(a.ticker for a in n.assets.all() if a.ticker in tickers),
        }
        for n in items
    ]


def groups_payload() -> dict:
    return {
        "sectors": [summary("sector", slug, name, ms) for slug, (name, ms) in sector_members().items()],
        "niches": [
            summary("niche", n.slug, n.name, [asset_payload(a) for a in n.assets.filter(active=True)])
            for n in Niche.objects.filter(external=False)
        ],
    }


def group_payload(kind: str, slug: str) -> dict:
    """Levanta Http404 para grupo inexistente."""
    if kind == "sector":
        name, members = sector_members().get(slug) or (None, None)
        if name is None:
            raise Http404
        description, macro_codes = "", []
    elif kind == "niche":
        niche = get_object_or_404(Niche, slug=slug)
        name, description, macro_codes = niche.name, niche.description, niche.macro_codes
        members = [asset_payload(a) for a in niche.assets.filter(active=True)]
    else:
        raise Http404
    tickers = [m["ticker"] for m in members]
    news = NewsItem.objects.filter(assets__ticker__in=tickers).distinct().prefetch_related("assets")[:30]
    return {
        **summary(kind, slug, name, members),
        "description": description,
        "members": members,
        "macro": latest_macro(macro_codes) if macro_codes else [],
        "news": news_payload(news, tickers),
    }


@api_view()
def groups(request):
    return Response(groups_payload())


@api_view()
def group_detail(request, kind, slug):
    return Response(group_payload(kind, slug))


MAX_CONTEXT_BYTES = 4096


@api_view(["GET", "POST"])
@authentication_classes([])  # uso local de um só usuário; sem sessão, o DRF não exige CSRF
@permission_classes([])
def screen_context(request):
    if request.method == "GET":
        ctx = ScreenContext.objects.first()
        return Response({"payload": ctx and ctx.payload, "updated_at": ctx and ctx.updated_at})
    body = request.data
    if (
        not isinstance(body, dict)
        or not isinstance(body.get("path"), str)
        or len(json.dumps(body)) > MAX_CONTEXT_BYTES
    ):
        return Response({"error": "esperado um objeto JSON com 'path' (texto), até 4 KB"}, status=400)
    ScreenContext.objects.update_or_create(pk=1, defaults={"payload": body})
    return Response(status=204)


# Telas que o Claude pode abrir no dashboard (as mesmas rotas do frontend)
SCREEN_PATH = re.compile(
    r"^/(grupos(/(sector|niche)/[a-z0-9-]+)?|mercado-eua|acoes/[A-Z0-9]{4,7}|carteira(/propostas/\d+)?|alertas|placar)?$"
)


def request_navigation(path: str, reason: str) -> ScreenCommand:
    path = path.strip()
    if path.startswith("/acoes/"):
        path = "/acoes/" + path[len("/acoes/"):].upper()
    if not SCREEN_PATH.match(path):
        raise ValueError(f"tela desconhecida: {path}")
    return ScreenCommand.objects.create(action="navigate", payload={"path": path, "reason": reason.strip()[:300]})


@api_view()
def screen_commands(request):
    """Comandos mais novos que ?after=<id>. Sem 'after', devolve só o último id (o dashboard começa dali)."""
    last = ScreenCommand.objects.order_by("-id").first()
    after = request.query_params.get("after")
    if after is None or not after.isdigit():
        return Response({"latest_id": last.id if last else 0, "commands": []})
    new = ScreenCommand.objects.filter(id__gt=int(after)).order_by("id")[:20]
    return Response(
        {
            "latest_id": last.id if last else 0,
            "commands": [{"id": c.id, "action": c.action, "payload": c.payload, "created_at": c.created_at} for c in new],
        }
    )


@api_view()
def sparklines(request):
    """Últimos 30 fechamentos de cada ação ativa, para os minigráficos da lista lateral."""
    out: dict[str, list] = {}
    bars = PriceBar.objects.filter(asset__active=True, asset__market="B3").order_by("asset__ticker", "-date")
    for ticker, close in bars.values_list("asset__ticker", "close"):
        if len(out.setdefault(ticker, [])) < 30:
            out[ticker].append(close)
    return Response({t: closes[::-1] for t, closes in out.items()})


@api_view()
def category_news(request, category):
    """Notícias de uma categoria de feed (geopolitica, ia_bolha) mesmo sem ligação com uma ação."""
    feed_names = NewsFeed.objects.filter(category=category).values_list("name", flat=True)
    items = list(NewsItem.objects.filter(source__in=feed_names).prefetch_related("assets")[:30])
    tickers = sorted({a.ticker for n in items for a in n.assets.all()})
    return Response(news_payload(items, tickers))
