<template>
  <section class="chart-card chart-card--revenue">
    <header class="chart-header">
      <div>
        <p class="chart-kicker">Entradas vs Saídas</p>
        <h2>Movimentação mensal</h2>
      </div>

      <button class="chart-filter" type="button">
        Mensal
        <ChevronDown :size="16" />
      </button>
    </header>

    <div class="chart-legend" aria-label="Legendas do gráfico de barras">
      <span><i class="legend-dot legend-dot--income"></i> Entradas</span>
      <span><i class="legend-dot legend-dot--expense"></i> Saídas</span>
    </div>

    <div class="chart-wrapper">
      <apexchart type="bar" height="320" :options="chartOptions" :series="chartSeries" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ChevronDown } from 'lucide-vue-next';

const chartSeries = [
  {
    name: 'Entradas',
    data: [72, 74, 69, 78, 76, 81],
  },
  {
    name: 'Saídas',
    data: [34, 37, 32, 35, 31, 36],
  },
];

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    fontFamily: 'var(--font-body)',
  },
  colors: ['#27B969', '#FF585A'],
  plotOptions: {
    bar: {
      borderRadius: 8,
      columnWidth: '45%',
    },
  },
  dataLabels: {
    enabled: false,
  },
  grid: {
    borderColor: 'rgba(148, 163, 184, 0.16)',
    strokeDashArray: 4,
  },
  xaxis: {
    categories: ['Dez', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
    labels: {
      style: {
        colors: '#64748b',
        fontSize: '12px',
      },
    },
  },
  yaxis: {
    labels: {
      style: {
        colors: '#64748b',
        fontSize: '12px',
      },
      formatter: (value: number) => `R$ ${value}k`,
    },
  },
  legend: {
    show: false,
  },
  tooltip: {
    y: {
      formatter: (value: number) => `R$ ${value}.000,00`,
    },
  },
  responsive: [
    {
      breakpoint: 768,
      options: {
        plotOptions: {
          bar: {
            columnWidth: '58%',
          },
        },
      },
    },
  ],
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

.chart-filter {
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft);
  color: var(--color-text);
  min-height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
}

.chart-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 14px;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-right: 8px;
}

.legend-dot--income {
  background: #27b969;
}

.legend-dot--expense {
  background: #ff585a;
}

.chart-wrapper {
  margin-left: -10px;
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
