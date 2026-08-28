<template>
  <section class="chart-card chart-card--revenue">
    <header class="chart-header">
      <div>
        <p class="chart-kicker">Entradas vs Saídas</p>
        <h2>Movimentação financeira</h2>
      </div>
      
      <div class="chart-controls">
        <select v-model="selectedPeriod" class="period-select">
          <option value="daily">Diário</option>
          <option value="weekly">Semanal</option>
          <option value="monthly">Mensal</option>
          <option value="annual">Anual</option>
        </select>
      </div>
    </header>

    <div class="chart-legend" aria-label="Legendas do gráfico de barras">
      <span><i class="legend-dot legend-dot--income"></i> Entradas ({{ incomePercentage }}%)</span>
      <span><i class="legend-dot legend-dot--expense"></i> Saídas ({{ expensePercentage }}%)</span>
    </div>

    <div class="chart-wrapper">
      <apexchart
        :key="`${selectedPeriod}-${source.length}-${isDark}`"
        type="bar"
        height="320"
        :options="chartOptions"
        :series="chartSeries"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useTransactionStore } from '@/stores/transactionStore';
import { useThemeStore } from '@/stores/themeStore';
import type { TransactionDto } from '@/services/transactionService';

const props = defineProps<{ transactions?: TransactionDto[] }>();

const transactionStore = useTransactionStore();
const themeStore = useThemeStore();
const isDark = computed(() => themeStore.theme === 'dark');
const selectedPeriod = ref('monthly');
const source = computed(() => props.transactions ?? transactionStore.transactions);

const chartSeries = computed(() => [
  {
    name: 'Entradas',
    data: periodData.value?.income || [],
  },
  {
    name: 'Saídas',
    data: periodData.value?.expense || [],
  },
]);

const totalIncome = computed(() => 
  source.value
    .filter(t => t.entryType === 'credit')
    .reduce((sum, t) => sum + t.amount, 0)
);

const totalExpense = computed(() => 
  source.value
    .filter(t => t.entryType === 'debit')
    .reduce((sum, t) => sum + t.amount, 0)
);

const total = computed(() => totalIncome.value + totalExpense.value);

const incomePercentage = computed(() => {
  const totalVal = total.value;
  if (totalVal === 0) return 0;
  return Math.round((totalIncome.value / totalVal) * 100);
});

const expensePercentage = computed(() => {
  const totalVal = total.value;
  if (totalVal === 0) return 0;
  return Math.round((totalExpense.value / totalVal) * 100);
});

const periodData = computed(() => {
  const now = new Date();
  let categories: string[] = [];
  let incomeData: number[] = [];
  let expenseData: number[] = [];

  if (selectedPeriod.value === 'daily') {
    // Últimos 7 dias
    categories = [];
    incomeData = [];
    expenseData = [];
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      categories.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }));
      
      const dayIncome = source.value
        .filter(t => t.entryType === 'credit' && t.date === dateStr)
        .reduce((sum, t) => sum + t.amount, 0);
      const dayExpense = source.value
        .filter(t => t.entryType === 'debit' && t.date === dateStr)
        .reduce((sum, t) => sum + t.amount, 0);
      
      incomeData.push(dayIncome);
      expenseData.push(dayExpense);
    }
  } else if (selectedPeriod.value === 'weekly') {
    // Últimas 4 semanas
    categories = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'];
    incomeData = [0, 0, 0, 0];
    expenseData = [0, 0, 0, 0];
    
    source.value.forEach((transaction) => {
      const date = new Date(transaction.date);
      const weekNum = Math.floor((now.getTime() - date.getTime()) / (7 * 24 * 60 * 60 * 1000));
      
      if (weekNum >= 0 && weekNum < 4) {
        if (transaction.entryType === 'credit') {
          incomeData[3 - weekNum] = (incomeData[3 - weekNum] ?? 0) + transaction.amount;
        } else {
          expenseData[3 - weekNum] = (expenseData[3 - weekNum] ?? 0) + transaction.amount;
        }
      }
    });
  } else if (selectedPeriod.value === 'monthly') {
    // Últimos 12 meses
    categories = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    incomeData = new Array(12).fill(0);
    expenseData = new Array(12).fill(0);
    
    source.value.forEach((transaction) => {
      const date = new Date(transaction.date);
      const month = date.getMonth();
      
      if (transaction.entryType === 'credit') {
        incomeData[month] = (incomeData[month] ?? 0) + transaction.amount;
      } else {
        expenseData[month] = (expenseData[month] ?? 0) + transaction.amount;
      }
    });
  } else if (selectedPeriod.value === 'annual') {
    // Últimos 5 anos
    const currentYear = now.getFullYear();
    categories = [];
    incomeData = [];
    expenseData = [];
    
    for (let i = 4; i >= 0; i--) {
      const year = currentYear - i;
      categories.push(year.toString());
      
      const yearIncome = source.value
        .filter(t => {
          const date = new Date(t.date);
          return t.entryType === 'credit' && date.getFullYear() === year;
        })
        .reduce((sum, t) => sum + t.amount, 0);
      
      const yearExpense = source.value
        .filter(t => {
          const date = new Date(t.date);
          return t.entryType === 'debit' && date.getFullYear() === year;
        })
        .reduce((sum, t) => sum + t.amount, 0);
      
      incomeData.push(yearIncome);
      expenseData.push(yearExpense);
    }
  }

  return { income: incomeData, expense: expenseData, categories };
});

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
    borderColor: isDark.value ? 'rgba(163, 170, 184, 0.14)' : 'rgba(148, 163, 184, 0.16)',
    strokeDashArray: 4,
  },
  xaxis: {
    categories: periodData.value?.categories || [],
    labels: {
      style: {
        colors: isDark.value ? '#a3aab8' : '#64748b',
        fontSize: '12px',
      },
    },
  },
  yaxis: {
    decimalsInFloat: 1,
    labels: {
      style: {
        colors: isDark.value ? '#a3aab8' : '#64748b',
        fontSize: '12px',
      },
      formatter: (value: number) => `R$ ${Math.round(value / 100) / 10}k`,
    },
  },
  legend: {
    show: false,
  },
  tooltip: {
    theme: isDark.value ? 'dark' : 'light',
    y: {
      formatter: (value: number) =>
        `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
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
  border-radius: 16px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
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

.chart-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.period-select {
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft);
  color: var(--color-text);
  min-height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  font-weight: 700;
  cursor: pointer;
  outline: none;
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
