"""Servidor MCP do LedgerLouis (stdio). Ferramentas só de leitura nesta fase.

Rodar: uv run python -m ledgerlouis.interfaces.mcp_server   (de dentro de backend/)
"""

import json
import os
from datetime import date, datetime
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.http import Http404  # noqa: E402
from fastmcp import FastMCP  # noqa: E402
from fastmcp.exceptions import ToolError  # noqa: E402

from ledgerlouis.market.models import Asset, NewsItem, Niche, ScreenContext  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from ledgerlouis.portfolio import services as portfolio  # noqa: E402
from ledgerlouis.portfolio.models import Alert, PendingChange, Proposal  # noqa: E402
from ledgerlouis.portfolio.views import item_payload  # noqa: E402
from ledgerlouis.market.views import request_navigation  # noqa: E402
from ledgerlouis.market.views import (  # noqa: E402
    asset_full,
    asset_payload,
    group_payload,
    groups_payload,
    latest_macro,
    news_payload,
)

INSTRUCTIONS = """Você é o analista do LedgerLouis, a plataforma pessoal de investimentos do Erick.
Regras:
1. Use só números vindos destas ferramentas. Não calcule indicadores por conta própria: P/L, EV/EBITDA,
   margens e medianas já vêm calculados pelo motor do LedgerLouis.
2. Cite a fonte e a data (campos source e fetched_at/date) de todo número que usar.
3. Separe fato (dado da ferramenta), estimativa (projeção com premissas explícitas) e interpretação (sua leitura).
4. Projeção não é promessa: mostre premissas, riscos, contrapontos e o grau de incerteza.
5. Fale em "hipóteses para investigar" e "proposta"; a decisão final é sempre do Erick. Nenhuma ordem é executada.
6. Para perguntas sobre "esta tela", comece por get_screen_context.
7. Indicador null significa dado ausente ou sem sentido (ex.: lucro negativo); diga isso em vez de estimar.
8. Você só grava rascunhos (save_proposal_draft), teses avulsas (record_thesis) e sugestões de mudança na
   carteira ou no perfil (propose_holding_change, propose_profile_change). Aplicar, aprovar, recusar ou ajustar
   é sempre do Erick, na interface. Diga que a sugestão está esperando a confirmação dele.
9. Use show_on_screen para abrir no dashboard a tela de que você está falando (uma ação, a carteira, uma proposta)."""

# shortcut: cada thread do FastMCP mantém sua conexão Django aberta (limitado ao pool de threads);
# se o Postgres reclamar de conexões, chamar django.db.close_old_connections() ao fim de cada ferramenta.
mcp = FastMCP("LedgerLouis", instructions=INSTRUCTIONS)


def _default(x):
    if isinstance(x, Decimal):
        return float(x)
    if isinstance(x, datetime | date):
        return x.isoformat()
    raise TypeError(type(x))


def plain(data):
    """Decimal e datas -> tipos JSON simples, como a API REST entrega."""
    return json.loads(json.dumps(data, default=_default))


@mcp.tool
def get_screen_context() -> dict:
    """O que o Erick está vendo agora no dashboard: rota, título, grupo ou ação e tickers visíveis."""
    ctx = ScreenContext.objects.first()
    if not ctx:
        return {"screen": None, "note": "Nenhuma tela aberta ainda no dashboard."}
    return plain({"screen": ctx.payload, "updated_at": ctx.updated_at})


@mcp.tool
def list_groups() -> dict:
    """Setores e nichos com variação do dia ponderada, valor de mercado e medianas dos indicadores."""
    return plain(groups_payload())


@mcp.tool
def get_group(kind: str, slug: str) -> dict:
    """Detalhe de um setor (kind='sector') ou nicho (kind='niche'): membros, medianas, macro e notícias."""
    try:
        return plain(group_payload(kind, slug))
    except Http404:
        raise ToolError(f"grupo não encontrado: {kind}/{slug}. Use list_groups para ver os disponíveis.")


@mcp.tool
def list_assets(sector: str | None = None, market: str = "B3") -> list[dict]:
    """Ações da base com cotação, indicadores calculados, fonte e data. Filtro opcional por nome exato do
    setor. market: 'B3' (padrão) ou 'US' para as empresas de tecnologia dos EUA."""
    qs = Asset.objects.filter(active=True, market=market)
    if sector:
        qs = qs.filter(sector=sector)
    return plain([asset_payload(a) for a in qs])


@mcp.tool
def get_asset(ticker: str) -> dict:
    """Uma ação: cotação, indicadores, técnicos (RSI 14, volatilidade anualizada, retornos), saúde de cada
    indicador contra a mediana do setor ('melhor', 'na_media', 'pior'), nichos e últimas notícias."""
    a = Asset.objects.filter(ticker=ticker.strip().upper()).first()
    if not a:
        raise ToolError(f"ticker não está na base: {ticker}. Use list_assets para ver os disponíveis.")
    return plain(asset_full(a, with_bars=False))


@mcp.tool
def get_macro() -> list[dict]:
    """Última leitura de cada série macro (Selic meta, IPCA 12 meses, dólar PTAX), com data de referência e fonte."""
    return plain(latest_macro())


@mcp.tool
def get_news(ticker: str | None = None, kind: str | None = None, limit: int = 20) -> list[dict]:
    """Notícias e fatos relevantes mais recentes. kind: 'fato_relevante', 'comunicado' ou 'noticia'."""
    qs = NewsItem.objects.prefetch_related("assets")
    if ticker:
        qs = qs.filter(assets__ticker=ticker.strip().upper())
    if kind:
        qs = qs.filter(kind=kind)
    items = list(qs[: max(1, min(limit, 100))])
    tickers = sorted({a.ticker for n in items for a in n.assets.all()})
    return plain(news_payload(items, tickers))


class ProposalItemIn(BaseModel):
    ticker: str
    action: str = Field(description="entrar, sair, aumentar, reduzir ou manter")
    target_weight: float = Field(description="peso alvo como fração da carteira: 0.15 = 15%")
    thesis: str = Field(description="tese em até 3 linhas")
    risks: str
    invalidation: str = Field(description="o que invalidaria a tese")
    sources: list[str] = Field(description="fonte e data de cada número usado, ex.: 'brapi, cotação de 29/10/2026'")


@mcp.tool
def get_profile() -> dict:
    """Perfil do Erick: horizonte, tolerância a risco, aporte mensal, setores a evitar, limiares de alerta e o que falta preencher."""
    return plain(portfolio.profile_payload())


@mcp.tool
def get_portfolio() -> dict:
    """Carteira atual: posições, valor, pesos, ganho sobre o preço médio, exposição por setor e o perfil."""
    return plain(portfolio.portfolio_payload())


@mcp.tool
def get_latest_proposal() -> dict:
    """A proposta mais recente com as decisões do Erick em cada item (para comparar com a próxima)."""
    p = Proposal.objects.first()
    if not p:
        return {"proposal": None, "note": "Ainda não há propostas."}
    return plain({"period": p.period, "summary": p.summary, "status": p.status, "created_at": p.created_at,
                  "items": [item_payload(i) for i in p.items.select_related("asset")]})


@mcp.tool
def save_proposal_draft(period: str, summary: str, items: list[ProposalItemIn]) -> dict:
    """Grava uma proposta de carteira como RASCUNHO para o Erick revisar item a item. Não executa nada.
    Rejeita a proposta inteira se houver ticker fora da base, peso fora de 0-100%, soma acima de 100%,
    ação inválida ou item sem tese, riscos, invalidação ou fontes."""
    try:
        p = portfolio.save_proposal(period, summary, [i.model_dump() for i in items])
    except portfolio.ProposalInvalid as exc:
        raise ToolError("Proposta rejeitada: " + "; ".join(exc.problems))
    return {"id": p.id, "status": p.status, "review": f"/carteira/propostas/{p.id}"}


@mcp.tool
def record_thesis(ticker: str, summary: str, expectation: str, sources: list[str], horizon_days: int | None = None) -> dict:
    """Registra uma tese avulsa no placar (expectation: alta, baixa ou neutra), com o preço atual como entrada."""
    try:
        t = portfolio.record_thesis(ticker, summary, expectation, horizon_days, sources)
    except ValueError as exc:
        raise ToolError(str(exc))
    return plain({"id": t.id, "ticker": t.asset.ticker, "entry_price": t.entry_price, "created_at": t.created_at})


@mcp.tool
def get_alerts(unseen_only: bool = True) -> list[dict]:
    """Alertas disparados pelas regras (queda forte, concentração, fato relevante), com os dados do gatilho."""
    qs = Alert.objects.select_related("asset")
    if unseen_only:
        qs = qs.filter(seen=False)
    return plain([{"id": a.id, "kind": a.kind, "title": a.title, "ticker": a.asset and a.asset.ticker,
                   "detail": a.detail, "created_on": a.created_on} for a in qs[:50]])


@mcp.tool
def get_scoreboard() -> dict:
    """Placar: cada tese com preço de entrada, preço atual, retorno, se acertou a direção e a decisão do Erick."""
    return plain(portfolio.scoreboard())


@mcp.tool
def show_on_screen(path: str, reason: str = "") -> dict:
    """Abre uma tela no dashboard do Erick. Caminhos: /, /grupos, /grupos/sector/<slug>, /grupos/niche/<slug>,
    /mercado-eua, /acoes/<TICKER>, /carteira, /carteira/propostas/<id>, /alertas, /placar."""
    try:
        c = request_navigation(path, reason)
    except ValueError as exc:
        raise ToolError(str(exc))
    return {"ok": True, "path": c.payload["path"], "note": "O dashboard abre a tela em alguns segundos, se estiver aberto."}


@mcp.tool
def propose_holding_change(ticker: str, quantity: float, reason: str, avg_price: float | None = None) -> dict:
    """Sugere registrar, corrigir ou remover (quantity=0) uma posição da carteira. NÃO altera nada:
    vira um cartão com Aplicar/Recusar para o Erick decidir."""
    try:
        c = portfolio.propose_holding_change(ticker, quantity, avg_price, reason)
    except ValueError as exc:
        raise ToolError(str(exc))
    return {"id": c.id, "status": c.status}


@mcp.tool
def propose_profile_change(changes: dict, reason: str) -> dict:
    """Sugere mudar campos do perfil (horizon_years, risk_tolerance, monthly_contribution, avoid_sectors, notes,
    alert_daily_drop_pct, alert_max_asset_weight, alert_max_sector_weight). NÃO altera nada até o Erick aplicar."""
    try:
        c = portfolio.propose_profile_change(changes, reason)
    except ValueError as exc:
        raise ToolError(str(exc))
    return {"id": c.id, "status": c.status}


@mcp.tool
def get_pending_changes() -> list[dict]:
    """Sugestões suas ainda esperando o Erick aplicar ou recusar."""
    return plain([{"id": c.id, "kind": c.kind, "payload": c.payload, "reason": c.reason, "created_at": c.created_at}
                  for c in PendingChange.objects.filter(status="pendente")])


@mcp.prompt
def proposta_mensal(periodo: str) -> str:
    """Monta a proposta de carteira do mês para o Erick revisar."""
    return f"""Monte a proposta de carteira de {periodo} do LedgerLouis.
1. Leia get_profile. Se faltar horizonte, risco ou aporte, diga quais e pergunte antes de seguir.
2. Leia get_portfolio, get_latest_proposal, get_scoreboard, get_macro, list_groups e get_alerts.
3. Para cada ativo que entra, sai ou muda de peso, consulte get_asset e use só números das ferramentas, com fonte e data.
4. Explique em poucas linhas: concentração por setor, o que mudou desde a proposta anterior e como foram as teses dela.
5. Grave com save_proposal_draft (pesos como fração; soma até 1). Cada item: tese em até 3 linhas, riscos,
   o que invalidaria a tese e fontes.
6. Termine dizendo que a proposta está em rascunho e que a decisão é do Erick na tela de revisão."""


@mcp.prompt
def explicar_alertas() -> str:
    """Explica os alertas novos da carteira."""
    return """Leia get_alerts. Para cada alerta: resumo em uma linha, por que importa para a carteira (get_portfolio),
os dados que o sustentam com fonte e data (get_asset, get_news), riscos, contrapontos e o que investigar.
Não sugira ordens; no máximo, se vale antecipar a revisão da carteira."""


if __name__ == "__main__":
    mcp.run()
