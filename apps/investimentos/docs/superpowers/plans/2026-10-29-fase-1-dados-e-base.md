# LedgerLouis — Fase 1: Dados e base — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Coletar cotações e fundamentos de 50 ações da B3 e a macro brasileira, guardar com fonte e data, calcular indicadores no backend e mostrar tudo num dashboard inicial.

**Architecture:** Django com camadas leves: `domain/` (fórmulas puras, sem Django), `infrastructure/providers/` (clientes HTTP que devolvem dataclasses), app `market` (models, sync, API). Frontend Vue 3 consome a API REST.

**Tech Stack:** Python 3.13, Django 5, DRF, httpx, django-environ, pytest, respx · Vue 3, TypeScript, Vite, Tailwind CSS 4, TanStack Query, ECharts (vue-echarts), Vitest.

**Spec:** [Prompt do projeto — LedgerLouis](https://claude.ai/artifact/Kt5fukDquoqiry7FbFN5Np), seções "Fases", "Backend", "Identidade visual", "Dashboards".

## Global Constraints

- A IA não calcula: todo indicador sai de `ledgerlouis/domain/fundamentals.py`.
- Todo dado guardado tem `source` (ex.: `brapi`, `bcb-sgs`) e `as_of` ou `fetched_at`.
- Nenhuma chave no código: `BRAPI_TOKEN` e `DATABASE_URL` vêm do ambiente (`.env`, fora do git).
- Banco: `DATABASE_URL` (Postgres no docker-compose); sem ela, SQLite local (temporário para desenvolvimento).
- Commits sem nenhuma menção a IA; autor = Erick.
- Toda chamada externa respeita TTL de cache: não buscar de novo dentro de 15 min (cotações) e 24 h (fundamentos e macro).

## Review Focus

- Lucro negativo ou zero: P/L e margens devem virar `None` (exibido "—"), nunca número negativo enganoso nem divisão por zero.
- EBITDA zero ou negativo: EV/EBITDA e dívida líquida/EBITDA viram `None`.
- Ticker que a brapi rejeita ou módulo bloqueado no plano grátis (403): o sync pula aquele ativo/módulo, registra o erro e segue os demais.
- API fora do ar ou timeout: o dashboard continua mostrando o último dado salvo, com a data antiga visível.
- Valores do BCB vêm como texto com data `dd/mm/aaaa`: converter para `Decimal` e `date` sem perder precisão.

---

### Task 1: Base do backend

**Files:** Create `backend/pyproject.toml`, `backend/manage.py`, `backend/config/{__init__,settings,urls,wsgi}.py`, `backend/tests/test_health.py`, `.gitignore`, `.env.example`

**Interfaces:** Produces `GET /api/health` → `{"status": "ok"}`.

- [ ] Test `test_health_ok`: `client.get("/api/health").json() == {"status": "ok"}`.
- [ ] Settings: environ lê `DEBUG`, `SECRET_KEY` (default só em DEBUG), `DATABASE_URL` (default `sqlite:///db.sqlite3`), `BRAPI_TOKEN` (default vazio), `CORS_ALLOWED_ORIGINS` (default `http://localhost:5173`).
- [ ] Run `uv run pytest` → PASS. Commit.

### Task 2: Fórmulas fundamentalistas

**Files:** Create `backend/ledgerlouis/domain/fundamentals.py`, `backend/tests/domain/test_fundamentals.py`

**Interfaces:** Produces, todas com argumentos `Decimal | None` e retorno `Decimal | None`:
`price_to_earnings(price, eps)`, `enterprise_value(market_cap, total_debt, total_cash)`, `ev_to_ebitda(ev, ebitda)`, `net_debt_to_ebitda(total_debt, total_cash, ebitda)`, `net_income_from_eps(eps, market_cap, price)`, `net_margin(net_income, revenue)`, e `compute_indicators(snapshot: dict) -> dict` que aplica todas.

- [ ] Tests com valores conferidos à mão: P/L(30, 3) = 10; EV(100, 40, 10) = 130; EV/EBITDA(130, 13) = 10; dív.líq/EBITDA(40, 10, 15) = 2; lucro(3, 1000, 30) = 100; margem(100, 400) = 0.25.
- [ ] Tests de borda: eps ≤ 0 → None; ebitda ≤ 0 → None; receita ≤ 0 → None; qualquer argumento None → None; caixa maior que dívida dá dív.líq/EBITDA negativo (é válido).
- [ ] Implementar; arredondar só na exibição, nunca no cálculo. Run → PASS. Commit.

### Task 3: Modelos

**Files:** Create `backend/ledgerlouis/market/{apps,models,admin}.py`, migração, `backend/tests/market/test_models.py`

**Interfaces:** Produces models:
- `Asset(ticker unique, name, kind, sector, subsector, logo_url, active)`
- `Quote(asset FK, price, change_pct, volume, market_cap, source, fetched_at)` — última por `fetched_at`
- `FundamentalsSnapshot(asset FK, revenue, ebitda, total_debt, total_cash, eps, roe_reported, source, fetched_at)`
- `MacroPoint(code, name, unit, date, value, source, fetched_at)`, unique (`code`, `date`)
- `Asset.latest_quote()` e `Asset.latest_fundamentals()`.

- [ ] Test: criar ativo com duas cotações, `latest_quote()` devolve a mais recente. Run → PASS. Commit.

### Task 4: Clientes brapi e BCB

**Files:** Create `backend/ledgerlouis/infrastructure/providers/{types,brapi,bcb}.py`, `backend/tests/providers/{test_brapi,test_bcb}.py`, fixtures JSON em `backend/tests/fixtures/`

**Interfaces:** Produces:
- `BrapiClient(token: str, http: httpx.Client | None = None)` com `list_stocks(limit: int) -> list[ListedStock]` (`GET /api/quote/list?type=stock&sortBy=volume&sortOrder=desc&limit=`) e `fundamentals(ticker: str) -> FundamentalsData | None` (`GET /api/quote/{t}?modules=financialData`; 403/404 → None).
- `BcbClient(http=None)` com `series(code: int, last: int) -> list[MacroData]` (`GET https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados/ultimos/{last}?formato=json`).
- Séries: 432 Selic meta (% a.a.), 13522 IPCA 12 meses (%), 1 Dólar PTAX venda (R$).

- [ ] Tests com respx e fixtures: mapeamento de campos (`stock, name, close, change, volume, market_cap, sector, subsector, logo`; `financialData.totalRevenue, ebitda, totalDebt, totalCash, returnOnEquity`, `earningsPerShare`), header `Authorization: Bearer`, 403 → None, data `dd/mm/aaaa` → `date`, `"10,50"`/`"10.50"` → `Decimal`.
- [ ] Run → PASS. Commit.

### Task 5: Sincronização

**Files:** Create `backend/ledgerlouis/market/sync.py`, `backend/ledgerlouis/market/management/commands/sync_market.py`, `backend/tests/market/test_sync.py`

**Interfaces:** Consumes Task 3 e 4. Produces `sync_stocks(client, limit=50) -> SyncReport`, `sync_fundamentals(client) -> SyncReport`, `sync_macro(client) -> SyncReport`; `SyncReport(ok: int, skipped: int, errors: list[str])`. Comando `python manage.py sync_market [--only stocks|fundamentals|macro]`.

- [ ] Tests com clientes falsos: cria ativos e cotações; respeita TTL (segunda chamada dentro de 15 min não chama o cliente); erro num ticker não para os outros.
- [ ] Run → PASS. Commit.

### Task 6: API

**Files:** Create `backend/ledgerlouis/market/{serializers,views,urls}.py`, `backend/tests/market/test_api.py`

**Interfaces:** Produces:
- `GET /api/assets` → lista: `ticker, name, sector, subsector, logo_url, quote{price, change_pct, volume, market_cap, source, fetched_at}, indicators{pe, ev_ebitda, net_debt_ebitda, net_margin, roe}, fundamentals_source, fundamentals_fetched_at`
- `GET /api/assets/{ticker}` → o mesmo item
- `GET /api/macro` → última leitura de cada série: `code, name, unit, date, value, source, fetched_at`

- [ ] Tests: indicadores vêm de `compute_indicators`; ativo sem fundamentos traz indicadores `null`; ticker inexistente → 404.
- [ ] Run → PASS. Commit.

### Task 7: Frontend — base e design system

**Files:** Create `frontend/` (Vite Vue TS), `frontend/src/styles/tokens.css`, `frontend/src/lib/format.ts`, `frontend/src/lib/format.test.ts`

**Interfaces:** Produces `formatBRL(v)`, `formatPct(v)`, `formatCompact(v)`, `formatRatio(v)`, `formatAsOf(iso)` — `null` → "—".

- [ ] Tokens: escuro primeiro (fundo quase preto quente), modo claro, uma cor de destaque, verde/vermelho para alta/queda, fonte de números monoespaçada tabular.
- [ ] Tests de `format.ts` (pt-BR, `null` → "—", sinal explícito em %). Run `npm test` → PASS. Commit.

### Task 8: Frontend — dashboard

**Files:** Create `frontend/src/api.ts`, `frontend/src/views/DashboardView.vue`, `frontend/src/components/{MacroStrip,SectorTreemap,AssetsTable,SourceNote}.vue`

**Interfaces:** Consumes Task 6.

- [ ] Faixa macro, mapa de calor (área = valor de mercado, cor = variação, agrupado por setor), tabela ordenável de ativos com indicadores; cada bloco com nota de fonte e data; estados de carregando, vazio ("rode `sync_market`") e erro.
- [ ] Alta/queda sempre com sinal ou seta, não só cor. `prefers-reduced-motion` respeitado.
- [ ] `npm run build` → sem erros. Commit.

### Task 9: Infra e README

**Files:** Create `docker-compose.yml` (Postgres 16 + Redis 7), `README.md`

- [ ] README: pré-requisitos, `.env`, subir banco, `uv run python manage.py migrate`, `sync_market`, rodar backend e frontend.
- [ ] Commit.
