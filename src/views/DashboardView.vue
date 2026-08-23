<template>
  <main class="dashboard-page">
    <div class="dashboard-backdrop dashboard-backdrop--left" aria-hidden="true"></div>
    <div class="dashboard-backdrop dashboard-backdrop--right" aria-hidden="true"></div>

    <div class="dashboard-shell">
      <DashboardHeader />

      <TagFilterChips />

      <section class="metrics-grid" aria-label="Resumo financeiro">
        <DashboardCard
          title="Saldo total"
          :value="formattedAccountValue"
          description="Saldo disponível"
          :trend-value="balanceTrend"
          trend-label="vs mês anterior"
          :tone="accountValue >= 0 ? 'positive' : 'negative'"
        >
          <template #icon>
            <div class="card-icon" :class="accountValue >= 0 ? 'card-icon--positive' : 'card-icon--negative'">
              <WalletMinimal :size="20" />
            </div>
          </template>

          <template #sparkline>
            <DashboardSparkline :variant="accountValue >= 0 ? 'success' : 'danger'" />
          </template>
        </DashboardCard>

        <DashboardCard
          title="Entradas do mês"
          :value="formattedIncome"
          :description="entriesDescription"
          trend-value="+ 8,3%"
          trend-label="vs mês anterior"
          tone="positive"
        >
          <template #icon>
            <div class="card-icon card-icon--positive">
              <ArrowDownToLine :size="20" />
            </div>
          </template>

          <template #sparkline>
            <DashboardSparkline variant="success" />
          </template>
        </DashboardCard>

        <DashboardCard
          title="Saídas do mês"
          :value="formattedExpense"
          :description="exitsDescription"
          trend-value="+ 3,7%"
          trend-label="vs mês anterior"
          tone="negative"
        >
          <template #icon>
            <div class="card-icon card-icon--negative">
              <ArrowUpFromLine :size="20" />
            </div>
          </template>

          <template #sparkline>
            <DashboardSparkline variant="danger" />
          </template>
        </DashboardCard>

        <DashboardCard
          title="Transações"
          :value="transactionCount.toString()"
          :description="countDescription"
          trend-value="+ 5,2%"
          trend-label="vs mês anterior"
          tone="neutral"
        >
          <template #icon>
            <div class="card-icon card-icon--neutral">
              <ChartNoAxesCombined :size="20" />
            </div>
          </template>

          <template #sparkline>
            <DashboardSparkline variant="success" />
          </template>
        </DashboardCard>
      </section>

      <section class="charts-grid" aria-label="Gráficos financeiros">
        <RevenueChart />
        <TagsDistributionCard />
      </section>

      <section class="insights-grid" aria-label="Estatísticas de gastos">
        <ExpenseInsightsCard />
      </section>

      <RecentTransactions :transactions="filteredTransactions" />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { ArrowDownToLine, ArrowUpFromLine, ChartNoAxesCombined, WalletMinimal } from 'lucide-vue-next';

import DashboardCard from '@/components/dashboard/DashboardCard.vue';
import DashboardHeader from '@/components/dashboard/DashboardHeader.vue';
import DashboardSparkline from '@/components/dashboard/DashboardSparkline.vue';
import RecentTransactions from '@/components/dashboard/RecentTransactions.vue';
import RevenueChart from '@/components/dashboard/RevenueChart.vue';
import TagFilterChips from '@/components/dashboard/TagFilterChips.vue';
import TagsDistributionCard from '@/components/dashboard/TagsDistributionCard.vue';
import ExpenseInsightsCard from '@/components/dashboard/ExpenseInsightsCard.vue';
import { useTransactionStore } from '@/stores/transactionStore';
import { useCompanyStore } from '@/stores/CompanyStore';
import { useTagStore } from '@/stores/tagStore';

const transactionStore = useTransactionStore();
const companyStore = useCompanyStore();
const tagStore = useTagStore();

onMounted(async () => {
  if (companyStore.company.hasCompany) {
    await transactionStore.fetchTransactions();
    await transactionStore.fetchAccountValue();
  }
});

const accountValue = computed(() => transactionStore.accountValue);

const activeTagName = computed(
  () => tagStore.tags.find((tag) => tag.id === tagStore.activeTagId)?.name,
);

const filteredTransactions = computed(() => {
  const activeTagId = tagStore.activeTagId;
  if (!activeTagId) return transactionStore.transactions;

  return transactionStore.transactions.filter((transaction) =>
    tagStore.transactionHasTag(transaction.id, activeTagId),
  );
});

const formattedAccountValue = computed(() => {
  const value = accountValue.value;
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
});

const balanceTrend = computed(() => {
  const value = accountValue.value;
  if (value > 0) return '+ 12,5%';
  if (value < 0) return '- 5,2%';
  return '0%';
});

const income = computed(() => {
  return filteredTransactions.value
    .filter(t => t.entryType === 'credit')
    .reduce((sum, t) => sum + t.amount, 0);
});

const expense = computed(() => {
  return filteredTransactions.value
    .filter(t => t.entryType === 'debit')
    .reduce((sum, t) => sum + t.amount, 0);
});

const formattedIncome = computed(() => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(income.value);
});

const formattedExpense = computed(() => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(expense.value);
});

const transactionCount = computed(() => {
  return filteredTransactions.value.length;
});

const entriesDescription = computed(() =>
  activeTagName.value ? `Total de entradas · Tag: ${activeTagName.value}` : 'Total de entradas',
);

const exitsDescription = computed(() =>
  activeTagName.value ? `Total de saídas · Tag: ${activeTagName.value}` : 'Total de saídas',
);

const countDescription = computed(() =>
  activeTagName.value ? `Total de transações · Tag: ${activeTagName.value}` : 'Total de transações',
);
</script>

<style scoped>
.dashboard-page {
  position: relative;
  min-height: calc(100vh - 165px);
  padding: 20px 16px 32px;
  background:
    radial-gradient(circle at top left, rgba(39, 185, 105, 0.14), transparent 28%),
    radial-gradient(circle at top right, rgba(29, 205, 108, 0.12), transparent 32%),
    linear-gradient(180deg, #f4f7fb 0%, #eef3f8 100%);
}

.dashboard-shell {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 18px;
  max-width: 1240px;
  margin: 0 auto;
}

.dashboard-backdrop {
  position: absolute;
  border-radius: 999px;
  filter: blur(24px);
  opacity: 0.55;
  pointer-events: none;
}

.dashboard-backdrop--left {
  top: 84px;
  left: -40px;
  width: 180px;
  height: 180px;
  background: rgba(29, 205, 108, 0.16);
}

.dashboard-backdrop--right {
  right: -50px;
  top: 320px;
  width: 220px;
  height: 220px;
  background: rgba(229, 33, 36, 0.12);
}

.metrics-grid,
.charts-grid,
.insights-grid {
  display: grid;
  gap: 16px;
}

.card-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 14px;
}

.card-icon--positive {
  color: var(--color-success-dark);
  background: rgba(29, 205, 108, 0.12);
}

.card-icon--negative {
  color: var(--color-danger);
  background: rgba(229, 33, 36, 0.12);
}

.card-icon--neutral {
  color: var(--color-text-secondary);
  background: rgba(107, 114, 128, 0.12);
}

@media (min-width: 640px) {
  .dashboard-page {
    padding-inline: 20px;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .dashboard-page {
    padding: 28px 24px 40px;
  }

  .metrics-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .charts-grid {
    grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.95fr);
    align-items: stretch;
  }
}
</style>
