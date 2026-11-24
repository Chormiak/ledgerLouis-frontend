# LedgerLouis — Fase 3: Claude via MCP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** O Claude (Desktop ou Code, pela assinatura) consulta o LedgerLouis por ferramentas MCP somente leitura, inclusive o que está aberto na tela.

**Architecture:** `ledgerlouis/interfaces/mcp_server.py` (FastMCP 4.1.4, stdio) inicializa o Django e reaproveita os payloads da API. O frontend publica o contexto da tela em `POST /api/screen-context`, guardado no banco (o servidor MCP é outro processo).

**Spec:** [Prompt do projeto — LedgerLouis](https://claude.ai/artifact/Kt5fukDquoqiry7FbFN5Np), seção "Backend → Ferramentas MCP".

## Global Constraints

- Ferramentas desta fase são só leitura. Escrita (`save_proposal_draft`, `record_thesis`) entra na fase 4. Nenhuma ferramenta aprova proposta ou executa ordem.
- Todo número devolvido carrega `source` e data; as instruções do servidor mandam o Claude citar fonte e data e não calcular indicadores por conta própria.
- `fastmcp==4.1.4` fixado.

## Review Focus

- Tela ainda não publicada: `get_screen_context` responde "nenhuma tela aberta" em vez de erro.
- Ticker em minúsculas ou inexistente: normaliza; inexistente devolve erro claro.
- Decimal no retorno: vira número JSON, não texto.
- Corpo do POST de contexto grande ou malformado: rejeitado com 400, nada gravado.
- O servidor MCP precisa rodar sem o servidor web estar de pé (lê o banco direto).

### Task 1: Contexto da tela
- [ ] Model `ScreenContext` (linha única), `POST/GET /api/screen-context` com validação (path obrigatório, até 4 KB), testes.

### Task 2: Servidor MCP
- [ ] Ferramentas: `get_screen_context`, `list_groups`, `get_group`, `list_assets`, `get_asset`, `get_macro`, `get_news`. Testes chamando pelo `fastmcp.Client` em memória.

### Task 3: Frontend publica a tela
- [ ] Composable `usePublishScreen` chamado por cada view com rota, título, grupo/ticker e tickers visíveis.

### Task 4: README com a configuração do Claude Desktop e do Claude Code.
