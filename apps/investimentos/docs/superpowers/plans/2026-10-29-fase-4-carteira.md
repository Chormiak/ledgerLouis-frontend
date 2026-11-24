# LedgerLouis — Fase 4: Carteira, proposta, alertas e placar — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** O Erick registra perfil e carteira; o Claude, via MCP, grava uma proposta mensal em rascunho; o Erick aprova, recusa ou ajusta cada item; tudo vira tese no placar; regras baratas geram alertas entre propostas.

**Architecture:** App Django `ledgerlouis.portfolio`. Cálculos puros em `domain/portfolio.py` e `domain/alerts.py`. O Claude escreve só rascunhos (`save_proposal_draft`) e teses avulsas (`record_thesis`); decidir é ação exclusiva da interface. Prompts MCP `proposta_mensal` e `explicar_alertas` viram atalhos no Claude Desktop/Code.

**Spec:** [Prompt do projeto — LedgerLouis](https://claude.ai/artifact/Kt5fukDquoqiry7FbFN5Np), seção "Fluxo da carteira".

## Global Constraints

- Nenhuma ferramenta MCP aprova, recusa, compra ou vende.
- Perfil não é assumido: campos vazios ficam vazios e a proposta avisa que faltam.
- Limiares de alerta ficam no perfil, com padrão editável: queda diária ≥ 5%, ativo acima de 20% da carteira, setor acima de 35%.
- Pesos são frações (0,25 = 25%); a soma dos pesos propostos não passa de 100%.
- Uso local de um usuário: a API de escrita não tem login; o servidor escuta só em localhost.

## Review Focus

- Carteira vazia ou ativo sem cotação: métricas não quebram; o ativo aparece com valor "—" e fica fora dos pesos.
- Proposta com ticker fora da base, peso negativo, soma acima de 100% ou item sem fonte: rejeitada inteira, com a lista de problemas.
- Decidir duas vezes o mesmo item: a segunda decisão substitui a primeira e a tese é atualizada, não duplicada.
- Ajuste sem novo peso: rejeitado.
- Alerta repetido no mesmo dia para o mesmo gatilho: não duplica.

### Task 1: Domínio — pesos, exposição, concentração, validação de proposta, gatilhos (testes primeiro)
### Task 2: Modelos — InvestorProfile, Holding, Proposal, ProposalItem, Thesis, Alert
### Task 3: API — perfil, carteira, propostas e decisão por item, alertas, placar
### Task 4: MCP — get_profile, get_portfolio, save_proposal_draft, record_thesis, get_alerts, get_scoreboard; prompts proposta_mensal e explicar_alertas
### Task 5: Alertas no sync_market
### Task 6: Frontend — Carteira (com perfil), Proposta (revisão item a item), Alertas, Placar
