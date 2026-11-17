"""Indicadores fundamentalistas. Puro Python: sem Django, sem rede, sem IA.

Convenção: qualquer entrada ausente, ou um denominador que torna o número
enganoso (lucro, EBITDA ou receita <= 0), devolve None, exibido como "—".
"""

from decimal import Decimal

Num = Decimal | None


def _positive(x: Num) -> bool:
    return x is not None and x > 0


def price_to_earnings(price: Num, eps: Num) -> Num:
    if price is None or not _positive(eps):
        return None
    return price / eps


def enterprise_value(market_cap: Num, total_debt: Num, total_cash: Num) -> Num:
    if None in (market_cap, total_debt, total_cash):
        return None
    return market_cap + total_debt - total_cash


def ev_to_ebitda(ev: Num, ebitda: Num) -> Num:
    if ev is None or not _positive(ebitda):
        return None
    return ev / ebitda


def net_debt_to_ebitda(total_debt: Num, total_cash: Num, ebitda: Num) -> Num:
    if None in (total_debt, total_cash) or not _positive(ebitda):
        return None
    return (total_debt - total_cash) / ebitda


def net_income_from_eps(eps: Num, market_cap: Num, price: Num) -> Num:
    """Lucro = LPA × número de ações, com ações = valor de mercado / preço."""
    if None in (eps, market_cap) or not _positive(price):
        return None
    return eps * market_cap / price


def net_margin(net_income: Num, revenue: Num) -> Num:
    if net_income is None or not _positive(revenue):
        return None
    return net_income / revenue


def compute_indicators(s: dict) -> dict:
    g = s.get
    ev = enterprise_value(g("market_cap"), g("total_debt"), g("total_cash"))
    net_income = net_income_from_eps(g("eps"), g("market_cap"), g("price"))
    return {
        "pe": price_to_earnings(g("price"), g("eps")),
        "ev_ebitda": ev_to_ebitda(ev, g("ebitda")),
        "net_debt_ebitda": net_debt_to_ebitda(g("total_debt"), g("total_cash"), g("ebitda")),
        "net_margin": net_margin(net_income, g("revenue")),
        # ROE vem pronto do provedor (sem patrimônio no plano grátis); a fonte fica registrada.
        "roe": g("roe_reported"),
    }
