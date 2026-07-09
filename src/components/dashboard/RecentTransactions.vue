<template>
  <section class="transactions-card">
    <header class="transactions-header">
      <div>
        <p class="chart-kicker">Últimas movimentações</p>
        <h2>Atividade recente</h2>
      </div>

      <button class="transactions-action" type="button">Ver todas</button>
    </header>

    <ul class="transactions-list">
      <TransactionItem
        v-for="transaction in transactions"
        :key="transaction.title + transaction.date"
        :title="transaction.title"
        :subtitle="transaction.subtitle"
        :amount="transaction.amount"
        :date="transaction.date"
        :kind="transaction.kind"
      />
    </ul>
  </section>
</template>

<script setup lang="ts">
import TransactionItem from '@/components/dashboard/TransactionItem.vue';

const transactions = [
  {
    title: 'Venda de serviço',
    subtitle: 'Receita operacional',
    amount: '+ R$ 2.450,00',
    date: 'Hoje, 10:30',
    kind: 'income' as const,
  },
  {
    title: 'Aluguel do escritório',
    subtitle: 'Despesa fixa',
    amount: '- R$ 1.500,00',
    date: 'Hoje, 08:15',
    kind: 'expense' as const,
  },
  {
    title: 'Venda de produto',
    subtitle: 'Receita operacional',
    amount: '+ R$ 5.800,00',
    date: 'Ontem, 16:45',
    kind: 'income' as const,
  },
  {
    title: 'Material de escritório',
    subtitle: 'Despesa administrativa',
    amount: '- R$ 320,50',
    date: 'Ontem, 14:20',
    kind: 'expense' as const,
  },
];
</script>

<style scoped>
.transactions-card {
  padding: 18px;
  border-radius: 28px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 52px rgba(15, 23, 42, 0.06);
}

.transactions-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 8px;
}

.chart-kicker {
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 6px;
}

h2 {
  color: var(--color-text);
  font-size: 20px;
  font-weight: 800;
}

.transactions-action {
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface-soft);
  color: var(--color-text);
  min-height: 40px;
  padding: 0 14px;
  font-weight: 700;
}

.transactions-list {
  display: grid;
}

@media (min-width: 768px) {
  .transactions-card {
    padding: 24px;
  }
}
</style>
