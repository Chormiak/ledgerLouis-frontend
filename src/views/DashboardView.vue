<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { ArrowDownToLine, ArrowUpFromLine, Plus, ReceiptText } from 'lucide-vue-next';
import PageHeader from '@/components/ui/PageHeader.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ExportMenu from '@/components/ui/ExportMenu.vue';
import BalanceHero from '@/components/dashboard/BalanceHero.vue';
import DashboardCard from '@/components/dashboard/DashboardCard.vue';
import RecentTransactions from '@/components/dashboard/RecentTransactions.vue';
import CashflowChart from '@/components/dashboard/CashflowChart.vue';
import TagFilterChips from '@/components/dashboard/TagFilterChips.vue';
import TagRanking from '@/components/dashboard/TagRanking.vue';
import SpendingOutlook from '@/components/dashboard/SpendingOutlook.vue';
import { useTransactionStore } from '@/stores/transactionStore';
import { useCompanyStore } from '@/stores/CompanyStore';
import { useTagStore } from '@/stores/tagStore';
import { exportTransactionsCsv, exportTransactionsPdf } from '@/utils/exportTransactions';
import { useGsapScope } from '@/composables/useGsapScope';
import { buildMonthlySeries } from '@/utils/monthlySeries';
import { formatCurrency } from '@/utils/format';

const SPARKLINE_MONTHS = 6;

const transactionStore = useTransactionStore();
const companyStore = useCompanyStore();
const tagStore = useTagStore();

onMounted(async () => {
  await Promise.all([transactionStore.fetchTransactions(), transactionStore.fetchAccountValue()]);
});

const activeTagName = computed(() => tagStore.tags.find((tag) => tag.id === tagStore.activeTagId)?.name);

const filteredTransactions = computed(() => {
  const activeTagId = tagStore.activeTagId;
  if (!activeTagId) return transactionStore.transactions;
  return transactionStore.transactions.filter((t) => tagStore.transactionHasTag(t.id, activeTagId));
});

const monthly = computed(() => buildMonthlySeries(filteredTransactions.value, SPARKLINE_MONTHS));

const current = computed(() => monthly.value[monthly.value.length - 1]!);
const previous = computed(() => monthly.value[monthly.value.length - 2]!);

const percentChange = (now: number, before: number) => (before === 0 ? null : ((now - before) / before) * 100);

// O backend devolve o saldo como texto decimal ("142344.00").
const accountValue = computed(() => Number(transactionStore.accountValue) || 0);

const monthsNet = computed(() => monthly.value.map((m) => ({ label: m.label, net: m.net })));

// Entrada em cascata dos blocos: o olhar desce do saldo para o detalhe.
const root = ref<HTMLElement>();
useGsapScope(root, ({ gsap }) => {
  gsap.from('.stage', { opacity: 0, y: 8, duration: 0.4, stagger: 0.04, ease: 'power2.out', clearProps: 'all' });
});

const tagSuffix = computed(() => (activeTagName.value ? ` · ${activeTagName.value}` : ''));

const handleExport = (format: 'csv' | 'pdf') => {
  if (format === 'csv') {
    exportTransactionsCsv(filteredTransactions.value, tagStore.transactionTagsMap);
  } else {
    exportTransactionsPdf(filteredTransactions.value, tagStore.transactionTagsMap, companyStore.company.name);
  }
};
</script>

<template>
  <div ref="root" class="page flat-ui">
    <div class="page-shell">
      <PageHeader
        class="stage"
        title="Visão geral"
        :description="`Saldo, entradas e saídas de ${companyStore.company.name || 'sua empresa'}.`"
      >
        <template #actions>
          <ExportMenu @export="handleExport" />
          <BaseButton :to="{ name: 'addExpense' }">
            <Plus :size="18" />
            Novo lançamento
          </BaseButton>
        </template>
      </PageHeader>

      <TagFilterChips class="stage" />

      <section class="overview stage" aria-label="Resumo financeiro">
        <BalanceHero
          class="overview-balance"
          :balance="accountValue"
          :income="current.income"
          :expense="current.expense"
          :months="monthsNet"
        />

        <div class="overview-metrics card list-divided">
          <DashboardCard
            title="Entradas do mês"
            :value="formatCurrency(current.income)"
            :icon="ArrowDownToLine"
            tone="positive"
            :trend="percentChange(current.income, previous.income)"
            :description="`vs mês anterior${tagSuffix}`"
            :series="monthly.map((m) => m.income)"
          />
          <DashboardCard
            title="Saídas do mês"
            :value="formatCurrency(current.expense)"
            :icon="ArrowUpFromLine"
            tone="negative"
            invert-trend
            :trend="percentChange(current.expense, previous.expense)"
            :description="`vs mês anterior${tagSuffix}`"
            :series="monthly.map((m) => m.expense)"
          />
          <DashboardCard
            title="Lançamentos do mês"
            :value="current.count.toString()"
            :icon="ReceiptText"
            :trend="percentChange(current.count, previous.count)"
            :description="`vs mês anterior${tagSuffix}`"
            :series="monthly.map((m) => m.count)"
          />
        </div>
      </section>

      <section class="flow stage" aria-label="Fluxo de caixa e tags">
        <CashflowChart class="flow-chart" :transactions="filteredTransactions" />
        <TagRanking class="flow-ranking" :transactions="filteredTransactions" />
      </section>

      <SpendingOutlook class="stage" />

      <RecentTransactions class="stage" :transactions="filteredTransactions" />
    </div>
  </div>
</template>

<style scoped>
/* Grade de 12 colunas: cada faixa soma 12, sem celulas vazias. */
.overview,
.flow {
  display: grid;
  grid-auto-flow: dense;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--space-4);
}

.overview > *,
.flow > * {
  grid-column: 1 / -1;
  min-width: 0;
}

/* Metricas empilhadas em um unico painel, divididas por filetes. */
.overview-metrics {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0;
}

.overview-metrics > :deep(*) {
  flex: 1;
}

.overview-metrics > :deep(* + *) {
  border-top: 1px solid var(--color-border);
}

@media (min-width: 1100px) {
  .overview-balance {
    grid-column: span 7;
  }

  .overview-metrics {
    grid-column: span 5;
  }

  .flow-chart {
    grid-column: span 8;
  }

  .flow-ranking {
    grid-column: span 4;
  }
}
</style>
