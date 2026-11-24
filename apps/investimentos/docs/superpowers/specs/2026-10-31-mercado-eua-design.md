# Mercado EUA & notícias de geopolítica/IA — design

## Intenção e por quê

O LedgerLouis hoje cobre só a B3 (ações, fundamentos, macro, notícias). O Erick quer
acompanhar também as grandes empresas de tecnologia/IA dos EUA (Amazon, Google e outras),
numa seção separada dos nichos atuais — não misturada com "IA e tecnologia" (que hoje só tem
BDRs). Junto, ele quer: dados atualizando sozinhos sempre que abre o site (hoje só atualiza
rodando `sync_market` manualmente), notícias de geopolítica que afetam o mercado, e notícias
sobre a "bolha da IA".

## Goals

- Uma seção própria, fora da listagem de "Setores e nichos", com ~20 grandes empresas de
  tecnologia/IA dos EUA: cotação, fundamentos básicos, histórico de preço — mesmo padrão de
  informação que já existe para a B3.
- Notícias dessas empresas vindas de fontes dos EUA (não só CVM/B3).
- Um painel de notícias de geopolítica (o que afeta o mercado de forma mais ampla).
- Um painel de notícias sobre a "bolha da IA".
- Abrir o site no navegador dispara a atualização dos dados (respeitando os limites de cache
  já existentes — 15 min cotação, 6h notícia, 24h fundamentos/macro/histórico), sem precisar
  rodar `sync_market` na mão.

## Non-goals

- Não gerar automaticamente um texto de "por que isso afeta o mercado" pras notícias de
  geopolítica — o chat do Claude já embutido no dashboard responde isso quando perguntado,
  com a notícia na tela; não é preciso duplicar isso em um gerador de texto.
- Não usar provedor pago nem com token pra dados dos EUA.
- Não misturar as empresas dos EUA na listagem/página atual de "Setores e nichos" da B3.
- Não fazer backfill de histórico alem do que a fonte gratuita entrega de cara (mesma
  tolerância que a brapi já tem hoje: o que a fonte não der, fica em branco, sem erro).

## Anti-goals (seria falha mesmo funcionando)

- Furar a disciplina de TTL que protege a cota gratuita da brapi — os novos jobs dos EUA
  (cotação, fundamentos, histórico) têm seu próprio TTL independente, nunca reaproveitam nem
  pulam o TTL já existente do brapi.
- Travar a abertura do site esperando uma chamada de rede lenta (Yahoo Finance, RSS) — o
  gatilho de sync ao abrir o site não pode bloquear a tela.

## Restrições

- Sem token/chave nova paga: só `yfinance` (não-oficial, grátis, sem token) e feeds RSS
  gratuitos.
- Reaproveitar os modelos existentes (`Asset`, `Quote`, `FundamentalsSnapshot`, `PriceBar`,
  `NewsItem`, `NewsFeed`, `Niche`) sempre que já servirem; só adicionar campo quando o formato
  atual não dá pra expressar a necessidade nova.
- Manter a regra de nunca guardar o texto da notícia, só título/link/fonte/data — vale pros
  feeds novos também.
- Mesma stack: Python 3.13 / Django 5.2 / `uv` no backend; Vue 3 / TypeScript / Vite no
  frontend.

## Decisões já tomadas (minhas, a confirmar com o Erick)

1. **Fonte de dados dos EUA:** `yfinance` (não-oficial, grátis, sem token) pra cotação,
   fundamentos (o subconjunto que a lib expõe de forma confiável) e histórico diário (~3
   meses, mesmo horizonte que a brapi já entrega). Um cliente novo em
   `ledgerlouis/infrastructure/providers/yfinance_provider.py` devolve as mesmas dataclasses
   de `types.py` (`ListedStock`, `FundamentalsData`, `Bar`) que a brapi já usa, pra `sync.py`
   continuar agnóstico de provedor.

   **Dois jobs, não três:** diferente da brapi (que exige uma chamada separada pra
   fundamentos), o `yfinance` costuma devolver cotação e fundamentos na mesma consulta
   (`Ticker.info`). Pra não desperdiçar isso buscando fundamentos a cada 15 min só pra
   descartar a maior parte do retorno, `sync_us_stocks()` faz essa consulta uma vez por ativo
   e grava `Quote` (gate de 15 min) sempre, mas só grava `FundamentalsSnapshot` quando o
   último snapshot daquele ativo já passou das 24h (mesma lógica de gate que `sync_fundamentals`
   já usa pra brapi, só que sem precisar de uma segunda ida à rede). `sync_us_history()`
   continua separado (dado de outro formato, série de candles), espelhando a brapi. Resultado:
   dois `--only` novos em `sync_market` (`us_stocks`, `us_history`), e dois jobs na lista do
   sync-trigger do item 8.

2. **Lista de empresas (seed fixo, 20 tickers):** AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA,
   AMD, AVGO, ORCL, CRM, ADBE, PLTR, SNOW, IBM, INTC, NOW, SMCI, MU, TSM. Mesmo padrão dos
   nichos hoje: ticker que não for encontrado é ignorado sem erro, editável depois no
   `/admin`.

3. **Agrupamento:** reaproveita o model `Niche` como está (um registro "Global Tech & IA
   (EUA)"), com um campo novo `Niche.external` (boolean, default `False`) que tira esse nicho
   da listagem normal de "/grupos" (Setores e nichos); a página nova do frontend busca esse
   nicho direto pelo slug, sem aparecer na lista geral.

   **Isso não basta por si só** — várias telas e endpoints hoje listam todo `Asset` ativo sem
   filtrar por nicho, e por padrão um `Asset` novo entra como `active=True`:
   - `GET /api/assets` (tela "Visão geral": pulso de mercado, treemap por setor, tabela
     principal de ações);
   - `sector_members()` (aba "Setores" de `/grupos`), que agrupa por `Asset.sector` direto,
     sem passar pelo `Niche` — se o `yfinance` gravar setor em inglês ("Technology"), nasce um
     setor novo ali, fora do controle do `Niche.external`;
   - `/api/sparklines` e o `Watchlist.vue` (barra lateral fixa em toda página, ranking "Mais
     negociadas" por volume) — ações dos EUA, com volume bem maior, dominariam esse painel
     sempre visível;
   - as ferramentas MCP `list_assets`/`get_asset`.

   Minha decisão: todos esses pontos passam a filtrar por `Asset.market="B3"` por padrão
   (homepage, treemap, `sector_members`, `/api/sparklines`, `Watchlist.vue`, e as ferramentas
   MCP de listagem); `Asset.sector`/`subsector` ficam em branco para os ativos dos EUA (sem
   setor em inglês vazando pro treemap da B3); a seção nova busca os ativos dela filtrando por
   `market="US"` (ou pelo nicho, que dá no mesmo). Isso segue direto do que você já pediu
   ("mais fora sim dos nichos") — não é uma decisão nova, só a lista de onde isso precisa ser
   aplicado.

4. **Campo `Asset.market`:** novo `CharField` (`"B3"` / `"US"`, default `"B3"`) pra
   formatar moeda e exibição certas (US$ vs R$) sem precisar inferir pelo formato do ticker.

5. **Campo `Asset.aliases`:** novo `JSONField` (default `[]`) com nomes alternativos pra
   casar notícia (ex.: `AMZN -> ["Amazon"]`, `GOOGL -> ["Google", "Alphabet"]`), porque
   ticker dos EUA raramente aparece literal no título da notícia (diferente de "PETR4" na
   B3).

6. **Casamento de notícia estendido:** `_sync_rss` passa a checar também cada alias (substring,
   sem diferenciar maiúscula/minúscula) no título, além da regex de ticker que já existe — a
   mesma função, o mesmo model `NewsItem`, sem infraestrutura nova de notícia.

7. **Categorias novas de feed, via `NewsFeed.category`:** campo novo (`"ticker"` padrão /
   `"geopolitica"` / `"ia_bolha"`), pra notícia de geopolítica e de "bolha da IA" aparecerem
   nos painéis próprios mesmo sem estarem ligadas a uma ação específica. Feeds iniciais
   (editável depois no `/admin`, igual já é hoje):
   - Geopolítica: Reuters World News e AP Top News (RSS grátis, sem chave).
   - Bolha da IA: 1-2 feeds de tecnologia/IA grátis (ex.: Ars Technica AI, TechCrunch AI),
     com filtro extra por palavra-chave ("IA", "inteligência artificial", "AI", "bolha",
     "bubble") na hora do sync, pra manter a categoria no assunto mesmo se o feed cobrir
     mais coisa.

8. **Atualizar ao abrir o site:** endpoint novo (`GET /api/sync-trigger` ou nome parecido) que
   dispara a mesma lista de jobs de `sync.py` (agora incluindo os jobs novos dos EUA, item 9
   abaixo) numa `threading.Thread` **dentro do próprio processo do backend** — chamando as
   funções de `sync.py` direto, não um subprocesso novo do `manage.py` (diferente do
   `/api/chat`, que é um processo externo de verdade; aqui só preciso do "não travar a
   resposta", e abrir um processo Python/Django novo a cada vez que alguém abre o site custa
   mais do que precisa). A thread fecha a conexão do banco no final
   (`django.db.close_old_connections()`) e loga qualquer erro em vez de deixar passar
   silencioso. `run_alerts()` entra nessa mesma lista — o comentário do `sync_market` já
   chama isso de "gatilho barato, sem IA", então não tem motivo pra deixar de fora. Como cada
   job já não faz nada se o TTL não passou, chamar isso toda vez que o site abre é seguro e,
   na maioria das vezes, não custa nada. O frontend chama isso uma vez ao montar o app
   (`main.ts`).

9. **Frontend:** uma view nova (nome final em aberto) com um item de menu de nível superior
   (fora de "Setores e nichos"), reaproveitando os componentes que já existem
   (`AssetsTable`, `NewsList`, `MacroStrip`), mais dois painéis `NewsList` novos pras
   categorias de geopolítica e bolha da IA.

## O que fica pro implementador decidir

- URL exata de cada feed RSS (confirmar que cada um está de fato grátis/estável antes de
  cadastrar).
- Formato exato do retorno do `yfinance` pros campos de fundamentos (lib não-oficial, pode
  faltar campo pra algum ticker — mesma tolerância que a brapi já tem: o que faltar, fica
  nulo).
- Nome final da rota/menu da seção nova no frontend.
- Se o endpoint de sync-trigger precisa de algum limite próprio na camada HTTP (provavelmente
  não, já que o TTL de cada job já evita trabalho repetido — vale uma checada na hora de
  implementar).
