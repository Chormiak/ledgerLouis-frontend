from dataclasses import dataclass
from datetime import date
from decimal import Decimal


def dec(x) -> Decimal | None:
    """Número vindo de JSON (float, int ou texto com vírgula) -> Decimal exato."""
    if x is None or x == "":
        return None
    return Decimal(str(x).replace(",", "."))


@dataclass(frozen=True)
class ListedStock:
    ticker: str
    name: str
    kind: str
    sector: str
    subsector: str
    logo_url: str
    price: Decimal | None
    change_pct: Decimal | None
    volume: Decimal | None
    market_cap: Decimal | None


@dataclass(frozen=True)
class FundamentalsData:
    ticker: str
    revenue: Decimal | None
    ebitda: Decimal | None
    total_debt: Decimal | None
    total_cash: Decimal | None
    eps: Decimal | None
    roe: Decimal | None


@dataclass(frozen=True)
class MacroData:
    date: date
    value: Decimal


@dataclass(frozen=True)
class Bar:
    date: date
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    volume: Decimal | None
