import yfinance as yf

from .types import Bar, FundamentalsData, ListedStock, dec

SOURCE = "yfinance"


class YFinanceClient:
    """yfinance é não-oficial e sem SLA: qualquer campo ausente vira None, sem erro."""

    def snapshot(self, ticker: str, name: str) -> tuple[ListedStock, FundamentalsData | None]:
        info = yf.Ticker(ticker).info or {}
        stock = ListedStock(
            ticker=ticker,
            name=info.get("longName") or info.get("shortName") or name,
            kind="stock",
            sector="",
            subsector="",
            logo_url="",
            price=dec(info.get("currentPrice") or info.get("regularMarketPrice")),
            change_pct=dec(info.get("regularMarketChangePercent")),
            volume=dec(info.get("regularMarketVolume") or info.get("volume")),
            market_cap=dec(info.get("marketCap")),
        )
        if not info:
            return stock, None
        fundamentals = FundamentalsData(
            ticker=ticker,
            revenue=dec(info.get("totalRevenue")),
            ebitda=dec(info.get("ebitda")),
            total_debt=dec(info.get("totalDebt")),
            total_cash=dec(info.get("totalCash")),
            eps=dec(info.get("trailingEps")),
            roe=dec(info.get("returnOnEquity")),
        )
        return stock, fundamentals

    def history(self, ticker: str) -> list[Bar] | None:
        rows = yf.Ticker(ticker).history(period="3mo", interval="1d")
        if rows.empty:
            return None
        return [
            Bar(
                date=idx.date(),
                open=dec(row.Open),
                high=dec(row.High),
                low=dec(row.Low),
                close=dec(row.Close),
                volume=dec(row.Volume),
            )
            for idx, row in rows.iterrows()
        ]
