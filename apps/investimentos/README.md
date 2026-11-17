# LedgerLouis

Plataforma pessoal de inteligência financeira.

- **Fase 1:** cotações e fundamentos das 50 ações de maior volume da B3, macro do Banco Central e um dashboard com faixa macro, mapa de calor por setor e tabela de indicadores.
- **Fase 2:** páginas por setor e por nicho (varejo, IA e tecnologia, imóveis...), com variação ponderada, medianas, macro relevante e notícias (fatos relevantes da CVM e feeds RSS).
- **Fase 3:** servidor MCP para o Claude consultar a plataforma e saber o que está na tela.
- **Página de cada ação:** candles de ~3 meses com média de 20 dias e volume, RSI, volatilidade, retornos, saúde de cada indicador contra a mediana do setor, nichos, notícias, sua posição e suas teses.
- **Fase 4:** perfil, carteira, proposta mensal que o Claude grava em rascunho e você decide item a item, alertas por regras e placar de teses.

Especificação: [Prompt do projeto](https://claude.ai/artifact/Kt5fukDquoqiry7FbFN5Np) · Plano da fase 1: `docs/superpowers/plans/`

## Pré-requisitos

- Python 3.12+ e [uv](https://docs.astral.sh/uv/)
- Node 20+
- Docker (para Postgres e Redis), opcional: sem `DATABASE_URL` o backend usa SQLite
- Token gratuito da [brapi](https://brapi.dev)

## Rodar

```bash
cp .env.example .env          # preencha BRAPI_TOKEN
docker compose up -d          # Postgres e Redis locais

cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py sync_market      # cotações, fundamentos, macro e notícias
uv run python manage.py seed_niches      # cria os nichos iniciais e liga as ações já sincronizadas
uv run python manage.py createsuperuser  # para editar nichos, CNPJs e feeds em /admin
uv run python manage.py runserver        # http://localhost:8000

cd ../frontend
npm install
npm run dev                              # http://localhost:5173
```

`sync_market` respeita cache: cotações são buscadas no máximo a cada 15 min, notícias a cada 6 h, fundamentos e macro a cada 24 h, para não gastar a cota gratuita. O histórico de preços (um pedido por ação, uma vez por dia) entra no mesmo comando. Use `--only stocks|fundamentals|history|macro|news` para rodar uma parte.

### Notícias

- **Fatos relevantes e comunicados** vêm dos dados abertos da CVM, ligados às ações pelo CNPJ. O CNPJ de cada ação é preenchido sozinho a partir do cadastro FCA da CVM; você pode corrigir no admin.
- **Feeds RSS:** cadastre em `/admin` → News feeds (nome e URL). Uma notícia é ligada a uma ação quando o título cita o ticker (ex.: "PETR4").
- O LedgerLouis guarda só título, link, fonte e data, nunca o texto da matéria.

### Nichos

Os 8 nichos iniciais estão em `backend/ledgerlouis/market/niches_default.py` e são um ponto de partida: tickers mudam com fusões e trocas de código. Edite em `/admin` → Niches.

## Conversar com o Claude (MCP)

O backend expõe ferramentas MCP de leitura (`get_screen_context`, `list_groups`, `get_group`, `list_assets`, `get_asset`, `get_macro`, `get_news`, `get_profile`, `get_portfolio`, `get_latest_proposal`, `get_alerts`, `get_scoreboard`, `get_pending_changes`) e poucas de escrita, todas sem efeito direto na carteira:

- `save_proposal_draft` grava um rascunho de proposta, e `record_thesis` registra uma tese no placar.
- `show_on_screen` abre uma tela no dashboard (uma ação, um setor, a carteira), com aviso de que foi o Claude.
- `propose_holding_change` e `propose_profile_change` criam uma **sugestão** de mudança. Ela aparece no painel do Claude com os botões Aplicar e Recusar, e nada muda até você clicar.

O Claude usa a sua assinatura; não há custo de API. Ele não calcula indicadores sozinho, cita fonte e data, e nenhuma ferramenta compra, vende, aprova ou recusa nada.

### Chat dentro do dashboard

O painel à direita (ou o botão "Perguntar ao Claude" em telas menores) conversa com o Claude Code rodando no seu computador. O backend chama `claude -p` em modo headless, só com as ferramentas do LedgerLouis liberadas: sem terminal, sem leitura de arquivos, sem internet.

- Precisa do Claude Code instalado e logado (`claude` no PATH). Para outro caminho, use `CLAUDE_BIN` no `.env`; para escolher o modelo, `CLAUDE_CHAT_MODEL` (vazio usa o padrão).
- O `runserver` precisa estar de pé. A conversa continua entre mensagens e fica salva neste navegador; "Nova conversa" recomeça.
- O mesmo vale pelo terminal: com o dashboard aberto, o Claude Code na pasta do projeto também consegue abrir telas e deixar sugestões no painel.

Dois atalhos prontos (prompts MCP), que aparecem no Claude Desktop e no Claude Code:

- **proposta_mensal** (com o mês): o Claude lê seu perfil, carteira, placar e mercado e grava a proposta. Você revisa em Carteira → Abrir revisão.
- **explicar_alertas:** o Claude explica cada alerta novo, com dados, riscos e contrapontos.

Com o dashboard aberto, cada página publica o que está na tela; pergunte "o que você acha desta tela?" e o Claude começa por `get_screen_context`.

**Claude Code:** abra o Claude Code na pasta do projeto. O arquivo `.mcp.json` já registra o servidor; aprove quando ele perguntar. Confira com `/mcp`.

**Claude Desktop:** em Configurações → Desenvolvedor → Editar configuração, adicione (troque o caminho):

```json
{
  "mcpServers": {
    "ledgerlouis": {
      "command": "uv",
      "args": ["--directory", "/caminho/para/ledgerlouis/backend", "run", "python", "-m", "ledgerlouis.interfaces.mcp_server"]
    }
  }
}
```

Se o projeto estiver no WSL e o Claude Desktop no Windows, use `"command": "wsl"` e `"args": ["bash", "-lc", "cd /caminho/para/ledgerlouis/backend && uv run python -m ledgerlouis.interfaces.mcp_server"]`.

O servidor lê o banco direto: não precisa do `runserver` de pé, só do mesmo `.env`.

## Fluxo mensal da carteira

1. Preencha o perfil e as posições em **Carteira** (nada é assumido; o que faltar, o Claude pergunta).
2. Rode `sync_market` para ter cotações, notícias e alertas atualizados.
3. No Claude, use o atalho `proposta_mensal` com o mês.
4. Em **Carteira → Abrir revisão**, aprove, recuse ou ajuste o peso de cada item, com comentário.
5. Cada decisão vira uma tese no **Placar**, com o preço do dia. Com o tempo, o placar mostra se as propostas acertam.

Para agendar, use o agendador do seu sistema (cron no Linux, Agendador de Tarefas no Windows) chamando `uv run python manage.py sync_market` de hora em hora em dias úteis.

## Testes

```bash
cd backend && uv run pytest
cd frontend && npm test
```

## Limitações conhecidas

- Fundamentos vêm do módulo `financialData` da brapi; se o seu plano não liberar o módulo, a tabela mostra "—" nos indicadores.
- P/VP e dividend yield ainda não entram (precisam de balanço patrimonial e proventos).
- ROE é o informado pela fonte; os demais indicadores são calculados pelo LedgerLouis em `backend/ledgerlouis/domain/fundamentals.py`.
- O plano gratuito da brapi dá cerca de 3 meses de histórico; desempenho de setores por ano e 5 anos precisa de um plano maior. Por enquanto, setores mostram a variação do dia.
- O placar mede a direção do preço desde a tese; comparação com Ibovespa e S&P 500 entra quando houver histórico de índices.
- A API não tem login: o LedgerLouis foi feito para rodar só no seu computador (`localhost`). Não exponha a porta na internet. Ela aceita só JSON, e o CORS libera só o dashboard; assim, outro site aberto no navegador não consegue aprovar nada por você.
- Os nomes das colunas do arquivo FCA da CVM não puderam ser conferidos ao vivo durante o desenvolvimento. Se a CVM mudar o formato, `sync_market --only news` mostra qual coluna faltou.
