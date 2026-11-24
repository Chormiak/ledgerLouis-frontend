import json
from decimal import Decimal as D
from pathlib import Path

import httpx
import respx

from ledgerlouis.infrastructure.providers.brapi import BRAPI_URL, BrapiClient

FIX = Path(__file__).parent.parent / "fixtures"


@respx.mock
def test_list_stocks_maps_fields_and_sends_token():
    route = respx.get(f"{BRAPI_URL}/quote/list").mock(
        return_value=httpx.Response(200, json=json.loads((FIX / "brapi_list.json").read_text()))
    )
    stocks = BrapiClient("tok").list_stocks(limit=50)

    req = route.calls.last.request
    assert req.headers["Authorization"] == "Bearer tok"
    assert req.url.params["limit"] == "50"
    assert req.url.params["type"] == "stock"
    petr = stocks[0]
    assert (petr.ticker, petr.name, petr.sector) == ("PETR4", "PETROBRAS PN", "Energy Minerals")
    assert petr.price == D("37.85")
    assert petr.change_pct == D("1.25")
    assert petr.market_cap == D("492000000000")
    assert stocks[1].subsector == ""


@respx.mock
def test_fundamentals_maps_fields():
    respx.get(f"{BRAPI_URL}/quote/PETR4").mock(
        return_value=httpx.Response(200, json=json.loads((FIX / "brapi_quote_fundamentals.json").read_text()))
    )
    f = BrapiClient("tok").fundamentals("PETR4")
    assert f.revenue == D("490000000000")
    assert f.ebitda == D("240000000000")
    assert f.total_debt == D("320000000000")
    assert f.total_cash == D("70000000000")
    assert f.eps == D("6.1")
    assert f.roe == D("0.21")


@respx.mock
def test_fundamentals_blocked_or_unknown_is_none():
    respx.get(f"{BRAPI_URL}/quote/XPTO3").mock(return_value=httpx.Response(403, json={"error": True}))
    respx.get(f"{BRAPI_URL}/quote/NADA3").mock(return_value=httpx.Response(404, json={"error": True}))
    client = BrapiClient("tok")
    assert client.fundamentals("XPTO3") is None
    assert client.fundamentals("NADA3") is None


@respx.mock
def test_no_token_sends_no_auth_header():
    route = respx.get(f"{BRAPI_URL}/quote/list").mock(return_value=httpx.Response(200, json={"stocks": []}))
    BrapiClient("").list_stocks(limit=5)
    assert "Authorization" not in route.calls.last.request.headers


@respx.mock
def test_history_parses_bars_and_falls_back_on_plan_limit():
    route = respx.get(f"{BRAPI_URL}/quote/PETR4")
    route.side_effect = [
        httpx.Response(403, json={"error": True}),  # 3mo fora do plano
        httpx.Response(200, json={"results": [{"historicalDataPrice": [
            {"date": 1761696000, "open": 37.0, "high": 38.1, "low": 36.9, "close": 37.85, "volume": 1000, "adjustedClose": 37.85},
            {"date": 1761782400, "open": 37.9, "high": 38.0, "low": 37.0, "close": None, "volume": 10},
        ]}]}),
    ]
    bars = BrapiClient("tok").history("PETR4")
    assert [c.request.url.params["range"] for c in route.calls] == ["3mo", "1mo"]
    assert len(bars) == 1  # sem fechamento é descartado
    assert (str(bars[0].date), bars[0].close, bars[0].volume) == ("2025-10-29", D("37.85"), D("1000"))


@respx.mock
def test_history_unknown_ticker_is_none():
    respx.get(f"{BRAPI_URL}/quote/NADA3").mock(return_value=httpx.Response(404, json={"error": True}))
    assert BrapiClient("tok").history("NADA3") is None
