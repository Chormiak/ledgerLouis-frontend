"""Agregação de setores e nichos. Puro Python."""

from decimal import Decimal

Num = Decimal | None


def median(values: list[Num]) -> Num:
    xs = sorted(v for v in values if v is not None)
    if not xs:
        return None
    mid = len(xs) // 2
    return xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2


def summarize(members: list[dict]) -> dict:
    """members: dicts com market_cap, change_pct e indicators (como na API de ativos)."""
    caps = [m["market_cap"] for m in members if m["market_cap"] is not None]
    weighted = [(m["market_cap"], m["change_pct"]) for m in members if m["market_cap"] and m["change_pct"] is not None]
    weight = sum(c for c, _ in weighted)
    keys = members[0]["indicators"].keys() if members else []
    return {
        "count": len(members),
        "market_cap": sum(caps) if caps else None,
        "change_pct": sum(c * ch for c, ch in weighted) / weight if weight else None,
        "medians": {k: median([m["indicators"][k] for m in members]) for k in keys},
    }
