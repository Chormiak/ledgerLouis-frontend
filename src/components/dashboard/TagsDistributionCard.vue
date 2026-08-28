<script setup lang="ts">
import { computed } from 'vue';
import { useTagStore } from '@/stores/tagStore';
import { useTransactionStore } from '@/stores/transactionStore';
import { useThemeStore } from '@/stores/themeStore';
import { colorForTag } from '@/utils/tagColor';
import type { TransactionDto } from '@/services/transactionService';

const props = defineProps<{ transactions?: TransactionDto[] }>();

const tagStore = useTagStore();
const transactionStore = useTransactionStore();
const themeStore = useThemeStore();
const isDark = computed(() => themeStore.theme === 'dark');
const source = computed(() => props.transactions ?? transactionStore.transactions);

interface TagAggregate {
  id: string;
  label: string;
  total: number;
  color: string;
}

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const aggregates = computed<TagAggregate[]>(() => {
  const totals = new Map<string, number>();

  for (const transaction of source.value) {
    const tags = tagStore.transactionTagsMap[transaction.id] ?? [];
    for (const tag of tags) {
      totals.set(tag.id, (totals.get(tag.id) ?? 0) + transaction.amount);
    }
  }

  return tagStore.tags
    .map((tag) => ({
      id: tag.id,
      label: tag.name,
      total: totals.get(tag.id) ?? 0,
      color: colorForTag(tag.id),
    }))
    .filter((item) => item.total > 0)
    .sort((a, b) => b.total - a.total);
});

const grandTotal = computed(() => aggregates.value.reduce((sum, item) => sum + item.total, 0));

const chartSeries = computed(() => aggregates.value.map((item) => item.total));

const percentage = (value: number) => {
  if (grandTotal.value === 0) return 0;
  return Math.round((value / grandTotal.value) * 100);
};

const chartOptions = computed(() => ({
  chart: {
    type: 'donut',
    toolbar: { show: false },
    fontFamily: 'var(--font-body)',
  },
  labels: aggregates.value.map((item) => item.label),
  colors: aggregates.value.map((item) => item.color),
  legend: { show: false },
  dataLabels: { enabled: false },
  stroke: {
    width: 0,
  },
  plotOptions: {
    pie: {
      donut: {
        size: '72%',
        // Labels nativos do Apex desligados — o centro é renderizado por cima
        // com HTML/CSS nosso (.donut-center), que dá controle total do
        // espaçamento sem brigar com o posicionamento interno do Apex.
        labels: { show: false },
      },
    },
  },
  tooltip: {
    theme: isDark.value ? 'dark' : 'light',
    y: {
      formatter: (value: number) => formatCurrency(value),
    },
  },
}));
</script>

<template>
  <section class="chart-card tags-card">
    <header class="chart-header">
      <div>
        <p class="chart-kicker">Distribuição por tag</p>
        <h2>Onde as tags estão concentradas</h2>
      </div>
    </header>

    <div v-if="aggregates.length === 0" class="tags-empty">
      Marque suas transações com tags para ver a distribuição aqui.
    </div>

    <div v-else class="expenses-layout">
      <div class="donut-panel">
        <div class="chart-wrapper">
          <apexchart
            :key="`${aggregates.length}-${isDark}`"
            type="donut"
            height="260"
            :options="chartOptions"
            :series="chartSeries"
          />

          <div class="donut-center" aria-hidden="true">
            <span class="donut-center-label">Total marcado</span>
            <strong class="donut-center-value">{{ formatCurrency(grandTotal) }}</strong>
          </div>
        </div>
      </div>

      <ul class="breakdown-list" aria-label="Totais por tag">
        <li v-for="item in aggregates" :key="item.id">
          <span class="breakdown-marker" :style="{ backgroundColor: item.color }"></span>
          <div>
            <strong>{{ item.label }}</strong>
            <span>{{ formatCurrency(item.total) }} · {{ percentage(item.total) }}%</span>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.chart-card {
  padding: 18px;
  border-radius: 16px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.chart-header {
  margin-bottom: 14px;
}

.chart-kicker {
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 6px;
}

h2 {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-text);
}

.tags-empty {
  padding: 24px 12px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 13px;
  background: var(--color-surface-soft);
  border-radius: 18px;
  border: 1px dashed var(--color-border);
}

.expenses-layout {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  align-items: center;
}

.donut-panel {
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-wrapper {
  position: relative;
  width: 100%;
  max-width: 300px;
  min-width: 0;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  max-width: 62%;
  text-align: center;
  pointer-events: none;
}

.donut-center-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-secondary);
}

.donut-center-value {
  font-size: 17px;
  font-weight: 800;
  line-height: 1.15;
  color: var(--color-text);
  overflow-wrap: anywhere;
}

.breakdown-list {
  display: grid;
  gap: 12px;
}

.breakdown-list li {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 18px;
  background: var(--color-surface-soft);
}

.breakdown-list strong {
  display: block;
  color: var(--color-text);
  font-size: 14px;
  margin-bottom: 3px;
}

.breakdown-list span {
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.breakdown-marker {
  width: 12px;
  height: 12px;
  border-radius: 999px;
}

:deep(.apexcharts-text),
:deep(.apexcharts-legend-text) {
  font-family: var(--font-body) !important;
}


@media (min-width: 768px) {
  .chart-card {
    padding: 24px;
  }
}
</style>
