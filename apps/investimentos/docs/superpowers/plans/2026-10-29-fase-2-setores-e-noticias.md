# LedgerLouis — Fase 2: Setores, nichos e notícias — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Páginas por setor e por nicho temático com indicadores agregados, ranking, macro relevante e notícias (fatos relevantes da CVM e feeds RSS).

**Architecture:** Agregação pura em `domain/groups.py`. Nichos e feeds são editáveis no admin do Django. Notícias guardam só título, link, fonte e data (nunca o texto da matéria). Frontend ganha rotas.

**Tech Stack:** o da fase 1 + feedparser (backend) e vue-router (frontend).

**Spec:** [Prompt do projeto — LedgerLouis](https://claude.ai/artifact/Kt5fukDquoqiry7FbFN5Np), seção "Setores e nichos".

## Global Constraints

- As da fase 1 continuam valendo.
- Notícias: guardar e exibir só título, link, fonte e data; o resumo do Claude entra na fase 3.
- Nicho é uma lista editável pelo Erick (admin); a lista inicial é um ponto de partida, não uma verdade.
- Desempenho por período (mês, ano, 5 anos) depende de histórico de preços, que fica para quando houver a fonte; nesta fase só o dia.

## Review Focus

- Grupo sem nenhum indicador válido: medianas viram `null`, nunca erro.
- Mediana com quantidade par de valores: média dos dois do meio.
- Ticker citado num título RSS que não está na base: ignorado, sem criar ativo.
- CSV da CVM em latin-1 e separado por `;`: ler sem quebrar acentos.
- Coluna esperada ausente no CSV da CVM: erro claro dizendo qual coluna, sem gravar nada parcial.

---

### Task 1: Agregação de grupos (domínio)

**Files:** Create `backend/ledgerlouis/domain/groups.py`, `backend/tests/domain/test_groups.py`

**Interfaces:** Produces `median(values: list[Decimal | None]) -> Decimal | None` e `summarize(members: list[dict]) -> dict`, onde cada membro tem `market_cap`, `change_pct` e `indicators` (dict da fase 1). Saída: `count`, `market_cap` (soma), `change_pct` (média ponderada por valor de mercado, ignorando quem não tem os dois), `medians` (mesmas chaves de `indicators`).

- [ ] Tests: mediana ímpar, par, com `None`, vazia; média ponderada (10 com peso 1 e 0 com peso 3 = 2,5); grupo vazio.

### Task 2: Nichos

**Files:** Modify `market/models.py` (models `Niche(name, slug, description, macro_codes, assets M2M)`), migração, admin, `market/management/commands/seed_niches.py`, `market/niches_default.py`, tests

- [ ] `seed_niches` cria os 8 nichos da spec com descrição e séries macro, e liga só os tickers que já existem na base; rodar duas vezes não duplica.

### Task 3: API de grupos

**Files:** Modify `market/views.py`, `market/urls.py`, tests

**Interfaces:** `GET /api/groups` → `{sectors: [summary], niches: [summary]}`; summary = `slug, name, kind, count, market_cap, change_pct, medians`. `GET /api/groups/{kind}/{slug}` → summary + `description`, `members` (payload da fase 1), `macro` (últimas leituras das séries do nicho), `news` (últimas 30 ligadas aos membros).

### Task 4: Notícias

**Files:** Create `infrastructure/providers/cvm.py`, `infrastructure/providers/rss.py`; Modify models (`Asset.cnpj`, `NewsFeed(name, url, active)`, `NewsItem(title, url unique, source, kind, published_at, assets M2M)`), `market/sync.py`, comando `sync_news`, tests com fixtures

- [ ] CVM: lê o ZIP anual do IPE (`ipe_cia_aberta_{ano}.zip`), filtra `Categoria` = "Fato Relevante" e "Comunicado ao Mercado", liga por `CNPJ_Companhia`. O mapa CNPJ → ticker vem do FCA `valor_mobiliario` (`CNPJ_Companhia`, `Codigo_Negociacao`).
- [ ] RSS: feeds do admin; liga notícia a ativo quando o título cita um ticker existente.
- [ ] TTL de 6 h por fonte.

### Task 5: Frontend

**Files:** `src/router.ts`, `src/views/{OverviewView,GroupsView,GroupView}.vue`, `src/components/{NavBar,GroupBars,NewsList}.vue`

- [ ] Navegação: Visão geral, Setores e nichos; seletor de grupo no topo.
- [ ] Setores e nichos: barras de variação do dia por grupo, com sinal e seta.
- [ ] Página do grupo: medianas, mapa de calor só dos membros, tabela com a posição de cada empresa contra a mediana, macro do nicho e lista de notícias com fonte e data.
- [ ] `npm run build`, screenshot desktop e celular.
