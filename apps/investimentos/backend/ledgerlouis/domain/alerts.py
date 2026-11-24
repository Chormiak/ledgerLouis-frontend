"""Gatilhos baratos de alerta, sem IA. O Claude só explica o que já disparou."""

from dataclasses import dataclass, field
from decimal import Decimal


def pct(fraction: Decimal) -> str:
    """0.372 -> '37,2%' (vírgula decimal, como no resto da interface)."""
    return f"{fraction:.1%}".replace(".", ",")


@dataclass(frozen=True)
class Thresholds:
    daily_drop_pct: Decimal  # pontos percentuais (5 = queda de 5% no dia)
    max_asset_weight: Decimal  # fração
    max_sector_weight: Decimal  # fração


@dataclass(frozen=True)
class Trigger:
    kind: str
    key: str  # identifica o mesmo gatilho para não repetir no mesmo dia
    title: str
    ticker: str | None = None
    detail: dict = field(default_factory=dict)


def triggers(positions: list[dict], sectors: dict[str, Decimal], t: Thresholds, new_filings: list[dict]) -> list[Trigger]:
    """positions: ticker, sector, weight, change_pct. new_filings: ticker, title, url (fatos novos de ativos da carteira)."""
    out = []
    for p in positions:
        if p["change_pct"] is not None and p["change_pct"] <= -t.daily_drop_pct:
            out.append(
                Trigger("queda_forte", f"queda_forte:{p['ticker']}", f"{p['ticker']} caiu {pct(-p['change_pct'] / 100)} hoje",
                        p["ticker"], {"change_pct": p["change_pct"]})
            )
        if p["weight"] is not None and p["weight"] > t.max_asset_weight:
            out.append(
                Trigger("concentracao_ativo", f"concentracao_ativo:{p['ticker']}",
                        f"{p['ticker']} ocupa {pct(p['weight'])} da carteira", p["ticker"],
                        {"weight": p["weight"], "limit": t.max_asset_weight})
            )
    for sector, w in sectors.items():
        if w > t.max_sector_weight:
            out.append(
                Trigger("concentracao_setor", f"concentracao_setor:{sector}", f"{sector} ocupa {pct(w)} da carteira",
                        None, {"sector": sector, "weight": w, "limit": t.max_sector_weight})
            )
    for f in new_filings:
        out.append(Trigger("fato_relevante", f"fato_relevante:{f['url']}", f"{f['ticker']}: {f['title']}", f["ticker"],
                           {"url": f["url"]}))
    return out
