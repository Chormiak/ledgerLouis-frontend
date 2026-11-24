"""Carteira: valor, pesos, exposição e validação de proposta. Puro Python."""

from decimal import Decimal

ACTIONS = {"entrar", "sair", "aumentar", "reduzir", "manter"}
MISSING_TEXT = {"thesis": "tese vazia", "risks": "riscos vazios", "invalidation": "falta dizer o que invalida a tese"}


def valuate(positions: list[dict]) -> dict:
    """positions: ticker, sector, quantity, price (None se sem cotação). Sem cotação fica fora dos pesos."""
    valued = [p | {"value": p["quantity"] * p["price"] if p["price"] is not None else None} for p in positions]
    total = sum((p["value"] for p in valued if p["value"] is not None), Decimal(0))
    out = [p | {"weight": p["value"] / total if p["value"] is not None and total else None} for p in valued]
    return {
        "positions": out,
        "total": total if total else None,
        "unpriced": [p["ticker"] for p in out if p["value"] is None],
    }


def exposure(valued_positions: list[dict], key: str) -> dict[str, Decimal]:
    out: dict[str, Decimal] = {}
    for p in valued_positions:
        if p["weight"] is not None:
            out[p[key] or "Sem classificação"] = out.get(p[key] or "Sem classificação", Decimal(0)) + p["weight"]
    return out


def validate_proposal(items: list[dict], known_tickers: set[str]) -> list[str]:
    """Devolve todos os problemas de uma vez; lista vazia = proposta válida."""
    if not items:
        return ["a proposta não tem itens"]
    problems = []
    seen = set()
    for it in items:
        t = it.get("ticker", "?")
        if t in seen:
            problems.append(f"{t}: ticker repetido")
        seen.add(t)
        if t not in known_tickers:
            problems.append(f"{t}: ticker fora da base")
        if it.get("action") not in ACTIONS:
            problems.append(f"{t}: ação inválida ({it.get('action')}); use {', '.join(sorted(ACTIONS))}")
        w = it.get("target_weight")
        if w is None or not (0 <= w <= 1):
            problems.append(f"{t}: peso fora de 0 a 100%")
        for field, message in MISSING_TEXT.items():
            if not str(it.get(field) or "").strip():
                problems.append(f"{t}: {message}")
        if not it.get("sources"):
            problems.append(f"{t}: sem fontes")
    total = sum((it.get("target_weight") or Decimal(0)) for it in items if (it.get("target_weight") or 0) > 0)
    if total > 1:
        problems.append(f"soma dos pesos é {total:.2%}, acima de 100%")
    return problems
