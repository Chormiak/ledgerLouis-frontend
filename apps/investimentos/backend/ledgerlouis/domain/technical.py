"""Indicadores técnicos sobre fechamentos diários (float). Puro Python."""

import math
import statistics

TRADING_DAYS = 252


def sma(closes: list[float], n: int) -> list[float | None]:
    """Média móvel simples alinhada à entrada: as n-1 primeiras posições ficam None."""
    return [None if i + 1 < n else sum(closes[i + 1 - n : i + 1]) / n for i in range(len(closes))]


def rsi(closes: list[float], n: int = 14) -> float | None:
    """RSI de Wilder do último dia; None sem n+1 fechamentos."""
    if len(closes) < n + 1:
        return None
    changes = [b - a for a, b in zip(closes, closes[1:])]
    gain = sum(max(c, 0) for c in changes[:n]) / n
    loss = sum(max(-c, 0) for c in changes[:n]) / n
    for c in changes[n:]:
        gain = (gain * (n - 1) + max(c, 0)) / n
        loss = (loss * (n - 1) + max(-c, 0)) / n
    if loss == 0:
        return 100.0
    return 100 - 100 / (1 + gain / loss)


def annualized_volatility(closes: list[float]) -> float | None:
    """Desvio padrão amostral dos retornos log diários, anualizado. Precisa de 2 retornos."""
    rets = [math.log(b / a) for a, b in zip(closes, closes[1:]) if a > 0 and b > 0]
    if len(rets) < 2:
        return None
    return statistics.stdev(rets) * math.sqrt(TRADING_DAYS)


def period_return(closes: list[float], days: int) -> float | None:
    if len(closes) <= days or closes[-1 - days] <= 0:
        return None
    return closes[-1] / closes[-1 - days] - 1
