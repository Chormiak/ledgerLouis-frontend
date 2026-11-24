<script setup lang="ts">
import { computed, ref } from 'vue';
import type { TransactionDto } from '@/services/transactionService';
import { buildMonthlySeries, niceCeil } from '@/utils/monthlySeries';
import { formatCompactCurrency, formatCurrency } from '@/utils/format';

const props = defineProps<{ transactions: TransactionDto[] }>();

const RANGES = [
  { value: 3, label: '3 meses' },
  { value: 6, label: '6 meses' },
  { value: 12, label: '12 meses' },
] as const;

const range = ref<number>(6);
const series = computed(() => buildMonthlySeries(props.transactions, range.value));

const ceiling = computed(() => niceCeil(Math.max(...series.value.flatMap((m) => [m.income, m.expense]), 0)));
const ticks = computed(() => [4, 3, 2, 1, 0].map((step) => (ceiling.value / 4) * step));
const heightOf = (value: number) => `${Math.max((value / ceiling.value) * 100, value > 0 ? 1.5 : 0)}%`;

const hasData = computed(() => series.value.some((m) => m.count > 0));

// O mes sob o cursor (ou com foco) vira a leitura; sem interacao, o mais recente.
const focused = ref<number | null>(null);
const activeIndex = computed(() => Math.min(focused.value ?? series.value.length - 1, series.value.length - 1));
const active = computed(() => series.value[activeIndex.value]!);
</script>

<template>
  <section class="card cashflow" aria-labelledby="cashflow-title">
    <header class="cashflow-head">
      <div>
        <h2 id="cashflow-title" class="card-title">Fluxo de caixa</h2>
        <p class="cashflow-legend">
          <span><i class="dot" style="background: var(--color-primary)" /> Entradas</span>
          <span><i class="dot" style="background: var(--color-danger)" /> Saídas</span>
        </p>
      </div>

      <div class="segmented" role="group" aria-label="Período do gráfico">
        <button
          v-for="option in RANGES"
          :key="option.value"
          type="button"
          class="segmented-item"
          :class="{ 'is-active': range === option.value }"
          :aria-pressed="range === option.value"
          @click="range = option.value"
        >
          {{ option.label }}
        </button>
      </div>
    </header>

    <div v-if="!hasData" class="empty-state">Registre lançamentos para acompanhar o fluxo de caixa mês a mês.</div>

    <template v-else>
      <dl class="readout" aria-live="polite">
        <div class="readout-month">
          <dt class="sr-only">Mês</dt>
          <dd>{{ active.fullLabel }}</dd>
        </div>
        <div>
          <dt>Entradas</dt>
          <dd class="figure text-income">{{ formatCurrency(active.income) }}</dd>
        </div>
        <div>
          <dt>Saídas</dt>
          <dd class="figure text-expense">{{ formatCurrency(active.expense) }}</dd>
        </div>
        <div>
          <dt>Resultado</dt>
          <dd class="figure" :class="active.net >= 0 ? 'text-income' : 'text-expense'">
            {{ formatCurrency(active.net) }}
          </dd>
        </div>
      </dl>

      <div class="plot">
        <ul class="axis" aria-hidden="true">
          <li v-for="tick in ticks" :key="tick" class="figure">{{ formatCompactCurrency(tick) }}</li>
        </ul>

        <div class="columns" :style="{ '--count': series.length }" @pointerleave="focused = null">
          <button
            v-for="(month, index) in series"
            :key="month.key"
            type="button"
            class="column"
            :class="{ 'is-active': index === activeIndex }"
            :aria-label="`${month.fullLabel}: entradas ${formatCurrency(month.income)}, saídas ${formatCurrency(month.expense)}`"
            @pointerenter="focused = index"
            @focus="focused = index"
            @blur="focused = null"
          >
            <span class="bars" aria-hidden="true">
              <span class="bar bar--income" :style="{ height: heightOf(month.income) }" />
              <span class="bar bar--expense" :style="{ height: heightOf(month.expense) }" />
            </span>
            <span class="column-label" aria-hidden="true">{{ month.label }}</span>
          </button>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.cashflow {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.cashflow-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3) var(--space-4);
}

.cashflow-legend {
  display: flex;
  gap: var(--space-4);
  margin-top: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
}

.cashflow-legend span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.segmented-item {
  min-height: 32px;
  padding: 4px 14px;
}

.readout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--space-3) var(--space-4);
  padding: var(--space-4) 0;
  border-block: 1px solid var(--color-border);
}

.readout > div:not(.readout-month) {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-3);
}

.readout > div:not(.readout-month) dt {
  margin-bottom: 0;
}

.readout-month {
  grid-column: 1 / -1;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.readout dt {
  margin-bottom: 2px;
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
}

.readout dd.figure {
  font-size: var(--text-md);
  font-weight: 500;
  overflow-wrap: anywhere;
}

@media (min-width: 720px) {
  .readout {
    grid-template-columns: auto repeat(3, minmax(0, 1fr));
    align-items: end;
  }

  .readout > div:not(.readout-month) {
    display: block;
  }

  .readout > div:not(.readout-month) dt {
    margin-bottom: 2px;
  }

  .readout-month {
    grid-column: auto;
    min-width: 11ch;
  }
}

.plot {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: var(--space-3);
  height: 280px;
}

/* Eixo Y: cada rotulo ocupa uma faixa igual; o ultimo (zero) alinha com a base das barras. */
.axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  /* reserva a altura do rotulo dos meses para o zero cair na linha de base */
  padding-bottom: 28px;
  font-size: 11px;
  color: var(--color-text-subtle);
  text-align: right;
}

/* Itens de altura zero: o texto fica centrado exatamente sobre a linha de grade. */
.axis li {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 0;
  white-space: nowrap;
}

.columns {
  position: relative;
  display: grid;
  grid-template-columns: repeat(var(--count), minmax(0, 1fr));
  /* linhas de grade desenhadas na area das barras (acima do rotulo de 28px) */
  background-image:
    repeating-linear-gradient(to bottom, var(--color-border) 0 1px, transparent 1px 25%),
    linear-gradient(var(--color-border-strong), var(--color-border-strong));
  background-size:
    100% calc(100% - 28px),
    100% 1px;
  background-position:
    0 0,
    0 calc(100% - 28px);
  background-repeat: no-repeat;
}

.column {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-end;
  min-width: 0;
  padding: 0 var(--space-1);
  border-radius: var(--radius-sm);
  transition: background-color var(--duration-fast) ease;
}

.column.is-active {
  background: rgba(255, 255, 255, 0.03);
}

.bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 3px;
  min-height: 0;
}

.bar {
  width: min(22px, 40%);
  border-radius: 3px 3px 0 0;
  transition:
    height 700ms var(--ease-out),
    opacity var(--duration-fast) ease;
}

.bar--income {
  background: var(--color-primary);
}

.bar--expense {
  background: var(--color-danger);
  opacity: 0.85;
}

.column:not(.is-active) .bar {
  opacity: 0.55;
}

.column-label {
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  text-transform: capitalize;
  color: var(--color-text-subtle);
}

.column.is-active .column-label {
  color: var(--color-text);
}
</style>
