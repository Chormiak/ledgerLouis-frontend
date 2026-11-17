from datetime import UTC, datetime

import httpx

from .types import Bar, FundamentalsData, ListedStock, dec

BRAPI_URL = "https://brapi.dev/api"
SOURCE = "brapi"


class BrapiClient:
    def __init__(self, token: str, http: httpx.Client | None = None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.http = http or httpx.Client(base_url=BRAPI_URL, headers=headers, timeout=20)

    def list_stocks(self, limit: int) -> list[ListedStock]:
        r = self.http.get(
            "/quote/list",
            params={"type": "stock", "sortBy": "volume", "sortOrder": "desc", "limit": limit},
        )
        r.raise_for_status()
        return [
            ListedStock(
                ticker=s["stock"],
                name=s.get("name") or s["stock"],
                kind=s.get("type") or "stock",
                sector=s.get("sector") or "",
                subsector=s.get("subsector") or "",
                logo_url=s.get("logo") or "",
                price=dec(s.get("close")),
                change_pct=dec(s.get("change")),
                volume=dec(s.get("volume")),
                market_cap=dec(s.get("market_cap")),
            )
            for s in r.json().get("stocks", [])
        ]

    def fundamentals(self, ticker: str) -> FundamentalsData | None:
        """None quando o ticker não existe ou o módulo não está no plano (403/404)."""
        r = self.http.get(f"/quote/{ticker}", params={"modules": "financialData"})
        if r.status_code in (400, 401, 403, 404):
            return None
        r.raise_for_status()
        results = r.json().get("results") or []
        if not results:
            return None
        q = results[0]
        fd = q.get("financialData") or {}
        return FundamentalsData(
            ticker=ticker,
            revenue=dec(fd.get("totalRevenue")),
            ebitda=dec(fd.get("ebitda")),
            total_debt=dec(fd.get("totalDebt")),
            total_cash=dec(fd.get("totalCash")),
            eps=dec(q.get("earningsPerShare")),
            roe=dec(fd.get("returnOnEquity")),
        )

    def history(self, ticker: str, ranges=("3mo", "1mo")) -> list[Bar] | None:
        """Candles diários. Tenta o maior intervalo e recua se o plano não permitir; None se nenhum serve."""
        for rng in ranges:
            r = self.http.get(f"/quote/{ticker}", params={"range": rng, "interval": "1d"})
            if r.status_code in (400, 401, 403):
                continue
            if r.status_code == 404:
                return None
            r.raise_for_status()
            results = r.json().get("results") or []
            rows = results[0].get("historicalDataPrice") or [] if results else []
            return [
                Bar(
                    date=datetime.fromtimestamp(b["date"], UTC).date(),
                    open=dec(b.get("open")),
                    high=dec(b.get("high")),
                    low=dec(b.get("low")),
                    close=dec(b.get("close")),
                    volume=dec(b.get("volume")),
                )
                for b in rows
                if b.get("date") and b.get("close") is not None
            ]
        return None
