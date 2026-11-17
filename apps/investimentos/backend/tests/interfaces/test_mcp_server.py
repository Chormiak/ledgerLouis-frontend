from decimal import Decimal as D

import pytest
from django.utils import timezone
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ledgerlouis.interfaces.mcp_server import mcp
from ledgerlouis.market.models import Asset, NewsItem, Niche, Quote, ScreenContext

# transaction=True: as ferramentas podem rodar em outra thread, que precisa ver os dados gravados
pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.anyio]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def data():
    a = Asset.objects.create(ticker="MGLU3", name="Magalu", sector="Retail Trade")
    Quote.objects.create(asset=a, price=D("12.5"), change_pct=D("1"), market_cap=D(1000), source="brapi", fetched_at=timezone.now())
    n = Niche.objects.create(name="Varejo", slug="varejo")
    n.assets.add(a)
    item = NewsItem.objects.create(title="Fato relevante: X", url="https://cvm/1", source="CVM", kind="fato_relevante", published_at=timezone.now())
    item.assets.add(a)
    return a


async def call(name, args=None):
    async with Client(mcp) as c:
        return (await c.call_tool(name, args or {})).structured_content


async def test_tools_are_registered_and_read_only():
    async with Client(mcp) as c:
        names = {t.name for t in await c.list_tools()}
    assert names == {
        "get_screen_context", "list_groups", "get_group", "list_assets", "get_asset", "get_macro", "get_news",
        "get_profile", "get_portfolio", "get_latest_proposal", "save_proposal_draft", "record_thesis",
        "get_alerts", "get_scoreboard", "show_on_screen", "propose_holding_change", "propose_profile_change",
        "get_pending_changes",
    }
    # nada que aprove, decida ou execute
    assert not any(word in n for n in names for word in ("approve", "decide", "apply", "order", "buy", "sell"))


async def test_screen_context_empty_then_filled():
    assert (await call("get_screen_context"))["screen"] is None
    await ScreenContext.objects.acreate(pk=1, payload={"path": "/grupos/niche/varejo"})
    assert (await call("get_screen_context"))["screen"] == {"path": "/grupos/niche/varejo"}


async def test_get_asset_normalizes_ticker_and_returns_numbers(data):
    body = await call("get_asset", {"ticker": " mglu3 "})
    assert body["ticker"] == "MGLU3"
    assert body["quote"]["price"] == 12.5  # número, não texto
    assert body["quote"]["source"] == "brapi"
    assert body["niches"] == [{"slug": "varejo", "name": "Varejo"}]
    assert "bars" not in body["history"]  # MCP recebe só os técnicos, não os candles
    assert body["news"][0]["kind"] == "fato_relevante"


async def test_unknown_ticker_and_group_are_clear_errors(data):
    with pytest.raises(ToolError, match="ticker não está na base"):
        await call("get_asset", {"ticker": "NADA3"})
    with pytest.raises(ToolError, match="grupo não encontrado"):
        await call("get_group", {"kind": "niche", "slug": "nada"})


async def test_group_and_news(data):
    body = await call("get_group", {"kind": "niche", "slug": "varejo"})
    assert [m["ticker"] for m in body["members"]] == ["MGLU3"]
    news = await call("get_news", {"ticker": "MGLU3"})
    assert news["result"][0]["tickers"] == ["MGLU3"]


async def test_save_proposal_draft_valid_and_invalid(data):
    item = {"ticker": "MGLU3", "action": "entrar", "target_weight": 0.2, "thesis": "t", "risks": "r",
            "invalidation": "i", "sources": ["brapi, 29/10/2026"]}
    ok = await call("save_proposal_draft", {"period": "2026-11", "summary": "resumo", "items": [item]})
    assert ok["status"] == "rascunho"
    with pytest.raises(ToolError, match="soma dos pesos"):
        await call("save_proposal_draft", {"period": "2026-11", "summary": "resumo", "items": [item | {"target_weight": 0.6}, item | {"ticker": "MGLU3", "target_weight": 0.6}]})


async def test_prompts_registered():
    async with Client(mcp) as c:
        names = {p.name for p in await c.list_prompts()}
        text = (await c.get_prompt("proposta_mensal", {"periodo": "novembro de 2026"})).messages[0].content.text
    assert names == {"proposta_mensal", "explicar_alertas"}
    assert "novembro de 2026" in text and "save_proposal_draft" in text


async def test_show_on_screen_validates_path(data):
    ok = await call("show_on_screen", {"path": "/acoes/mglu3", "reason": "mostrar a ação"})
    assert ok["path"] == "/acoes/MGLU3"
    with pytest.raises(ToolError, match="tela desconhecida"):
        await call("show_on_screen", {"path": "https://evil.example"})


async def test_proposals_of_changes_do_not_change_anything(data):
    from ledgerlouis.portfolio.models import Holding

    r = await call("propose_holding_change", {"ticker": "MGLU3", "quantity": 100, "avg_price": 10, "reason": "registrar compra"})
    assert r["status"] == "pendente"
    assert not await Holding.objects.aexists()  # nada aplicado sem o Erick
    pending = await call("get_pending_changes")
    assert pending["result"][0]["payload"]["ticker"] == "MGLU3"
    with pytest.raises(ToolError, match="inválid"):
        await call("propose_profile_change", {"changes": {"risk_tolerance": "yolo"}, "reason": "x"})
