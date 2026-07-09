<template>
  <section class="chart-card expenses-card">
    <header class="chart-header">
      <div>
        <p class="chart-kicker">Distribuição de gastos</p>
        <h2>Onde o dinheiro está indo</h2>
      </div>
    </header>

    <div class="expenses-layout">
      <div class="donut-panel">
        <div class="chart-wrapper">
          <apexchart type="donut" height="260" :options="chartOptions" :series="chartSeries" />
        </div>
      </div>

      <ul class="breakdown-list" aria-label="Categorias de gastos">
        <li v-for="item in breakdown" :key="item.label">
          <span class="breakdown-marker" :style="{ backgroundColor: item.color }"></span>
          <div>
            <strong>{{ item.label }}</strong>
            <span>{{ item.percentage }}%</span>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const breakdown = [
  { label: 'Despesas operacionais', percentage: 40, color: '#22c55e' },
  { label: 'Marketing', percentage: 20, color: '#8bdf57' },
  { label: 'Salários', percentage: 20, color: '#f59e0b' },
  { label: 'Serviços', percentage: 10, color: '#fb7185' },
  { label: 'Outros', percentage: 10, color: '#a855f7' },
];

const chartSeries = breakdown.map((item) => item.percentage);

const chartOptions = computed(() => ({
  chart: {
    type: 'donut',
    toolbar: { show: false },
    fontFamily: 'var(--font-body)',
  },
  labels: breakdown.map((item) => item.label),
  colors: breakdown.map((item) => item.color),
  legend: { show: false },
  dataLabels: { enabled: false },
  stroke: {
    width: 0,
  },
  plotOptions: {
    pie: {
      donut: {
        size: '66%',
        labels: {
          show: true,
          name: {
            show: true,
            offsetY: 16,
            fontSize: '12px',
            color: '#64748b',
          },
          value: {
            show: true,
            fontSize: '28px',
            fontWeight: 800,
            color: '#111827',
            formatter: () => 'R$ 30.698,65',
          },
          total: {
            show: true,
            label: 'Total mensal',
            fontSize: '13px',
            color: '#64748b',
            formatter: () => '100%',
          },
        },
      },
    },
  },
  tooltip: {
    y: {
      formatter: (value: number) => `${value}%`,
    },
  },
}));
</script>

<style scoped>
.chart-card {
  padding: 18px;
  border-radius: 28px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 52px rgba(15, 23, 42, 0.06);
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

.expenses-layout {
  display: grid;
  gap: 10px;
}

.donut-panel {
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-wrapper {
  width: 100%;
  max-width: 300px;
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

@media (min-width: 700px) {
  .expenses-layout {
    grid-template-columns: minmax(0, 1.05fr) minmax(230px, 0.95fr);
    align-items: center;
  }
}

@media (min-width: 768px) {
  .chart-card {
    padding: 24px;
  }
}
</style>
