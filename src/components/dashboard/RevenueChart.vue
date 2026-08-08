<template>
  <section class="chart-card chart-card--revenue">
    <header class="chart-header">
      <div>
        <p class="chart-kicker">Entradas vs Saídas</p>
        <h2>Movimentação financeira</h2>
      </div>
      
      <div class="chart-controls">
        <button class="chart-filter" type="button" @click="showExportMenu = !showExportMenu">
          <Download :size="16" />
        </button>
        
        <div v-if="showExportMenu" class="export-menu">
          <button @click="exportToCSV">Exportar CSV</button>
          <button @click="exportToPDF">Exportar PDF</button>
        </div>

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
      <apexchart type="bar" height="320" :options="chartOptions" :series="chartSeries" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Download } from 'lucide-vue-next';
import { useTransactionStore } from '@/stores/transactionStore';

const transactionStore = useTransactionStore();
const selectedPeriod = ref('monthly');
const showExportMenu = ref(false);

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
  transactionStore.transactions
    .filter(t => t.entryType === 'credit')
    .reduce((sum, t) => sum + t.amount, 0)
);

const totalExpense = computed(() => 
  transactionStore.transactions
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
      
      const dayIncome = transactionStore.transactions
        .filter(t => t.entryType === 'credit' && t.date === dateStr)
        .reduce((sum, t) => sum + t.amount, 0);
      const dayExpense = transactionStore.transactions
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
    
    transactionStore.transactions.forEach((transaction) => {
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
    
    transactionStore.transactions.forEach((transaction) => {
      const date = new Date(transaction.date);
      const month = date.getMonth();
      
      if (transaction.entryType === 'credit') {
        incomeData[month] = (incomeData[month] ?? 0) + transaction.amount;
      } else {
        incomeData[month] = (incomeData[month] ?? 0) + transaction.amount;
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
      
      const yearIncome = transactionStore.transactions
        .filter(t => {
          const date = new Date(t.date);
          return t.entryType === 'credit' && date.getFullYear() === year;
        })
        .reduce((sum, t) => sum + t.amount, 0);
      
      const yearExpense = transactionStore.transactions
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
    borderColor: 'rgba(148, 163, 184, 0.16)',
    strokeDashArray: 4,
  },
  xaxis: {
    categories: periodData.value?.categories || [],
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
      formatter: (value: number) => `R$ ${value / 1000}k`,
    },
  },
  legend: {
    show: false,
  },
  tooltip: {
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

const exportToCSV = () => {
  const transactions = transactionStore.transactions;
  const headers = ['Data', 'Descrição', 'Tipo', 'Valor'];
  const rows = transactions.map(t => [
    t.date,
    t.description,
    t.entryType === 'credit' ? 'Entrada' : 'Saída',
    t.amount.toFixed(2)
  ]);
  
  const csvContent = [headers, ...rows]
    .map(row => row.join(','))
    .join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `transacoes_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
};

const exportToPDF = () => {
  // Simples exportação para PDF usando print
  const printWindow = window.open('', '_blank');
  if (!printWindow) return;
  
  const transactions = transactionStore.transactions;
  const totalIncomeVal = totalIncome.value;
  const totalExpenseVal = totalExpense.value;
  const balance = totalIncomeVal - totalExpenseVal;
  
  printWindow.document.write(`
    <html>
      <head>
        <title>Relatório Financeiro</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { color: #27B969; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #27B969; color: white; }
          .summary { margin: 20px 0; }
          .summary div { margin: 10px 0; }
        </style>
      </head>
      <body>
        <h1>Relatório Financeiro</h1>
        <p>Gerado em: ${new Date().toLocaleDateString('pt-BR')}</p>
        
        <div class="summary">
          <div><strong>Total de Entradas:</strong> R$ ${totalIncomeVal.toFixed(2)}</div>
          <div><strong>Total de Saídas:</strong> R$ ${totalExpenseVal.toFixed(2)}</div>
          <div><strong>Saldo:</strong> R$ ${balance.toFixed(2)}</div>
        </div>
        
        <h2>Transações</h2>
        <table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Descrição</th>
              <th>Tipo</th>
              <th>Valor</th>
            </tr>
          </thead>
          <tbody>
            ${transactions.map(t => `
              <tr>
                <td>${new Date(t.date).toLocaleDateString('pt-BR')}</td>
                <td>${t.description}</td>
                <td>${t.entryType === 'credit' ? 'Entrada' : 'Saída'}</td>
                <td>R$ ${t.amount.toFixed(2)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </body>
    </html>
  `);
  
  printWindow.document.close();
  printWindow.print();
};
</script>

<style scoped>
.chart-card {
  padding: 18px;
  border-radius: 28px;
  border: 1px solid var(--color-border);
  background: rgba(var(--color-surface-rgb), 0.96);
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

.chart-controls {
  display: flex;
  gap: 10px;
  align-items: center;
  position: relative;
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
  cursor: pointer;
}

.export-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  min-width: 150px;
}

.export-menu button {
  display: block;
  width: 100%;
  padding: 10px 16px;
  border: none;
  background: none;
  color: var(--color-text);
  font-size: 14px;
  cursor: pointer;
  text-align: left;
}

.export-menu button:hover {
  background: var(--color-surface-soft);
}

.export-menu button:first-child {
  border-radius: 12px 12px 0 0;
}

.export-menu button:last-child {
  border-radius: 0 0 12px 12px;
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
