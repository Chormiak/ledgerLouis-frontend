<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { colorForTag } from '@/utils/tagColor';

const analyticsStore = useAnalyticsStore();

onMounted(() => {
  if (!analyticsStore.overallStats) analyticsStore.fetchOverallStats();
});

const onToggle = (event: Event) => {
  const checked = (event.target as HTMLInputElement).checked;
  analyticsStore.setGroupByTag(checked);
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const periodLabel = (period: string) => {
  const [year, month] = period.split('-');
  const date = new Date(Number(year), Number(month) - 1, 1);
  return date.toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' });
};

const overall = computed(() => analyticsStore.overallStats);

const sortedByTagStats = computed(() =>
  [...analyticsStore.byTagStats]
    .filter((stat) => stat.count > 0)
    .sort((a, b) => b.mean - a.mean),
);

const overallChartCategories = computed(() => {
  if (!overall.value) return [];
  return [...overall.value.months.map((point) => periodLabel(point.period)), 'Previsão'];
});

const overallChartSeries = computed(() => {
  if (!overall.value) return [];

  const actualData: (number | null)[] = overall.value.months.map((point) => point.total);
  const forecastLead: (number | null)[] = overall.value.months.map(() => null);

  return [
    { name: 'Gastos mensais', data: [...actualData, null] },
    {
      name: 'Previsão',
      data: [...forecastLead, overall.value.forecastNextMonth],
    },
  ];
});

const overallChartOptions = computed(() => ({
  chart: {
    type: 'line',
    toolbar: { show: false },
    fontFamily: 'var(--font-body)',
  },
  colors: ['#27B969', '#94a3b8'],
  stroke: {
    curve: 'smooth',
    width: [3, 2],
    dashArray: [0, 6],
  },
  markers: {
    size: 4,
    strokeWidth: 0,
  },
  fill: {
    type: ['gradient', 'solid'],
    gradient: {
      shadeIntensity: 0.4,
      opacityFrom: 0.28,
      opacityTo: 0.02,
    },
    opacity: [1, 0],
  },
  dataLabels: { enabled: false },
  grid: {
    borderColor: 'rgba(148, 163, 184, 0.16)',
    strokeDashArray: 4,
  },
  xaxis: {
    categories: overallChartCategories.value,
    labels: { style: { colors: '#64748b', fontSize: '12px' } },
  },
  yaxis: {
    labels: {
      style: { colors: '#64748b', fontSize: '12px' },
      formatter: (value: number) => `R$ ${Math.round(value / 100) / 10}k`,
    },
  },
  legend: { show: false },
  tooltip: {
    y: { formatter: (value: number) => formatCurrency(value) },
  },
}));
</script>

<template>
  <section class="chart-card insights-card">
    <header class="chart-header">
      <div>
        <p class="chart-kicker">Estatísticas de gastos</p>
        <h2>Variação e previsão</h2>
      </div>

      <label class="toggle">
        <input
          type="checkbox"
          :checked="analyticsStore.groupByTag"
          @change="onToggle"
        />
        <span class="toggle-track"><span class="toggle-thumb"></span></span>
        <span class="toggle-label">Agrupar por tag</span>
      </label>
    </header>

    <div v-if="analyticsStore.loading && !overall && sortedByTagStats.length === 0" class="insights-empty">
      Calculando estatísticas...
    </div>

    <template v-else>
      <div v-if="!analyticsStore.groupByTag" class="overall-view">
        <div v-if="!overall || overall.count === 0" class="insights-empty">
          Ainda não há despesas suficientes para calcular estatísticas.
        </div>

        <template v-else>
          <div class="stat-tiles">
            <div class="stat-tile">
              <span class="stat-tile-label">Média mensal</span>
              <strong class="stat-tile-value">{{ formatCurrency(overall.mean) }}</strong>
            </div>
            <div class="stat-tile">
              <span class="stat-tile-label">Desvio padrão</span>
              <strong class="stat-tile-value">{{ formatCurrency(overall.standardDeviation) }}</strong>
            </div>
            <div class="stat-tile">
              <span class="stat-tile-label">Variância</span>
              <strong class="stat-tile-value">{{ formatCurrency(overall.variance) }}</strong>
            </div>
            <div class="stat-tile stat-tile--forecast">
              <span class="stat-tile-label">Previsão próx. mês</span>
              <strong class="stat-tile-value">
                {{ overall.forecastNextMonth !== null ? formatCurrency(overall.forecastNextMonth) : '—' }}
              </strong>
            </div>
          </div>

          <div class="chart-wrapper">
            <apexchart type="line" height="220" :options="overallChartOptions" :series="overallChartSeries" />
          </div>
        </template>
      </div>

      <ul v-else class="tag-stats-list">
        <li v-if="sortedByTagStats.length === 0" class="insights-empty">
          Nenhuma tag com despesas registradas ainda.
        </li>

        <li v-for="stat in sortedByTagStats" :key="stat.tagId" class="tag-stats-row">
          <span class="tag-stats-dot" :style="{ backgroundColor: colorForTag(stat.tagId) }"></span>

          <div class="tag-stats-info">
            <strong>{{ stat.tagName }}</strong>
            <span>{{ stat.count }} despesa(s)</span>
          </div>

          <div class="tag-stats-metrics">
            <div>
              <span>Média</span>
              <strong>{{ formatCurrency(stat.mean) }}</strong>
            </div>
            <div>
              <span>Desvio</span>
              <strong>{{ formatCurrency(stat.standardDeviation) }}</strong>
            </div>
            <div>
              <span>Previsão</span>
              <strong>{{ stat.forecastNextMonth !== null ? formatCurrency(stat.forecastNextMonth) : '—' }}</strong>
            </div>
          </div>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.chart-card {
  padding: 18px;
  border-radius: 28px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 52px rgba(15, 23, 42, 0.06);
}

.chart-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
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

.toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.toggle input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-track {
  width: 38px;
  height: 22px;
  border-radius: 999px;
  background: var(--color-border);
  position: relative;
  transition: background 0.2s ease;
  flex-shrink: 0;
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.16);
  transition: transform 0.2s ease;
}

.toggle input:checked + .toggle-track {
  background: var(--color-success-gradient);
}

.toggle input:checked + .toggle-track .toggle-thumb {
  transform: translateX(16px);
}

.toggle-label {
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 700;
}

.insights-empty {
  padding: 24px 12px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 13px;
  background: var(--color-surface-soft);
  border-radius: 18px;
  border: 1px dashed var(--color-border);
}

.stat-tiles {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.stat-tile {
  padding: 12px 14px;
  border-radius: 18px;
  background: var(--color-surface-soft);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-tile--forecast {
  background: rgba(29, 205, 108, 0.1);
}

.stat-tile-label {
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 600;
}

.stat-tile-value {
  color: var(--color-text);
  font-size: 15px;
  font-weight: 800;
}

.chart-wrapper {
  margin-left: -10px;
}

.tag-stats-list {
  display: grid;
  gap: 10px;
}

.tag-stats-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 18px;
  background: var(--color-surface-soft);
}

.tag-stats-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  flex-shrink: 0;
}

.tag-stats-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.tag-stats-info strong {
  color: var(--color-text);
  font-size: 14px;
}

.tag-stats-info span {
  color: var(--color-text-secondary);
  font-size: 12px;
}

.tag-stats-metrics {
  display: flex;
  gap: 16px;
}

.tag-stats-metrics > div {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.tag-stats-metrics span {
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 600;
}

.tag-stats-metrics strong {
  color: var(--color-text);
  font-size: 13px;
  font-weight: 800;
}

:deep(.apexcharts-text),
:deep(.apexcharts-legend-text) {
  font-family: var(--font-body) !important;
}

@media (min-width: 560px) {
  .stat-tiles {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .tag-stats-row {
    grid-template-columns: 1fr;
  }

  .tag-stats-metrics {
    justify-content: space-between;
  }

  .tag-stats-metrics > div {
    align-items: flex-start;
  }
}

@media (min-width: 768px) {
  .chart-card {
    padding: 24px;
  }
}
</style>
