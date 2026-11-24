<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { colorForTag } from '@/utils/tagColor';
import { niceCeil } from '@/utils/monthlySeries';
import { smoothPath, type Point } from '@/utils/sparkPath';
import { formatCompactCurrency, formatCurrency } from '@/utils/format';
import DashboardSparkline from '@/components/dashboard/DashboardSparkline.vue';

const analyticsStore = useAnalyticsStore();

onMounted(() => {
  if (!analyticsStore.overallStats) analyticsStore.fetchOverallStats();
});

const view = computed({
  get: () => (analyticsStore.groupByTag ? 'tags' : 'total'),
  set: (value: 'total' | 'tags') => analyticsStore.setGroupByTag(value === 'tags'),
});

const overall = computed(() => analyticsStore.overallStats);
const hasOverall = computed(() => !!overall.value && overall.value.count > 0);

const monthLabel = (period: string) => {
  const [year, month] = period.split('-').map(Number);
  return new Date(year!, month! - 1, 1).toLocaleDateString('pt-BR', { month: 'short' }).replace('.', '');
};

// ---- Grafico: gastos reais + ponto de previsao ----
const W = 640;
const H = 220;

const plot = computed(() => {
  const stats = overall.value;
  if (!stats || stats.months.length === 0) return null;

  const labels = [...stats.months.map((m) => monthLabel(m.period)), 'previsão'];
  const values = stats.months.map((m) => m.total);
  const forecast = stats.forecastNextMonth;
  const showBand = stats.months.length >= 2;

  const top = niceCeil(Math.max(...values, forecast ?? 0, showBand ? stats.mean + stats.standardDeviation : 0));
  const slots = labels.length;
  const xOf = (i: number) => ((i + 0.5) / slots) * W;
  const yOf = (v: number) => (1 - v / top) * H;
  const pct = (v: number) => `${(v / top) * 100}%`;

  const real: Point[] = values.map((v, i) => ({ x: xOf(i), y: yOf(v) }));
  const last = real[real.length - 1]!;
  const forecastPoint = forecast === null ? null : { x: xOf(slots - 1), y: yOf(forecast) };

  return {
    labels,
    slots,
    ticks: [4, 3, 2, 1, 0].map((step) => (top / 4) * step),
    line: smoothPath(real),
    area: real.length > 1 ? `${smoothPath(real)} L${last.x},${H} L${real[0]!.x},${H} Z` : '',
    forecastLine: forecastPoint ? `M${last.x},${last.y} L${forecastPoint.x},${forecastPoint.y}` : '',
    dots: real.map((p, i) => ({ left: `${(p.x / W) * 100}%`, top: `${(p.y / H) * 100}%`, value: values[i]! })),
    forecastDot: forecastPoint
      ? { left: `${(forecastPoint.x / W) * 100}%`, top: `${(forecastPoint.y / H) * 100}%`, value: forecast! }
      : null,
    band: showBand
      ? {
          bottom: pct(Math.max(stats.mean - stats.standardDeviation, 0)),
          height: `${((Math.min(stats.mean + stats.standardDeviation, top) - Math.max(stats.mean - stats.standardDeviation, 0)) / top) * 100}%`,
        }
      : null,
    mean: { bottom: pct(stats.mean) },
  };
});

const tagRows = computed(() =>
  [...analyticsStore.byTagStats].filter((stat) => stat.count > 0).sort((a, b) => b.mean - a.mean),
);
</script>

<template>
  <section class="card outlook" aria-labelledby="outlook-title">
    <header class="outlook-head">
      <div>
        <h2 id="outlook-title" class="card-title">Gastos e previsão</h2>
        <p class="card-subtitle">Média, variação e projeção do próximo mês a partir das saídas registradas.</p>
      </div>

      <div class="segmented" role="group" aria-label="Agrupamento">
        <button
          type="button"
          class="segmented-item"
          :class="{ 'is-active': view === 'total' }"
          :aria-pressed="view === 'total'"
          @click="view = 'total'"
        >
          Total
        </button>
        <button
          type="button"
          class="segmented-item"
          :class="{ 'is-active': view === 'tags' }"
          :aria-pressed="view === 'tags'"
          @click="view = 'tags'"
        >
          Por tag
        </button>
      </div>
    </header>

    <p v-if="analyticsStore.loading && !overall && tagRows.length === 0" class="empty-state">
      Calculando estatísticas...
    </p>

    <template v-else-if="view === 'total'">
      <p v-if="!hasOverall || !plot" class="empty-state">Ainda não há saídas suficientes para calcular a previsão.</p>

      <template v-else>
        <dl class="stats">
          <div>
            <dt>Média mensal</dt>
            <dd class="figure">{{ formatCurrency(overall!.mean) }}</dd>
          </div>
          <div>
            <dt>Variação típica</dt>
            <dd class="figure">± {{ formatCurrency(overall!.standardDeviation) }}</dd>
          </div>
          <div class="stats-forecast">
            <dt>Previsão do próximo mês</dt>
            <dd class="figure">{{ overall!.forecastNextMonth !== null ? formatCurrency(overall!.forecastNextMonth) : '-' }}</dd>
          </div>
        </dl>

        <div class="plot">
          <ul class="axis" aria-hidden="true">
            <li v-for="tick in plot.ticks" :key="tick" class="figure">{{ formatCompactCurrency(tick) }}</li>
          </ul>

          <div class="canvas">
            <span v-if="plot.band" class="band" :style="plot.band" />
            <span class="mean" :style="plot.mean"><em>média</em></span>

            <svg :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none" role="img" aria-label="Gastos mensais e previsão">
              <defs>
                <linearGradient id="outlook-fill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" stop-color="#34b585" stop-opacity="0.22" />
                  <stop offset="1" stop-color="#34b585" stop-opacity="0" />
                </linearGradient>
              </defs>
              <path v-if="plot.area" :d="plot.area" fill="url(#outlook-fill)" />
              <path :d="plot.line" fill="none" stroke="var(--color-primary)" stroke-width="2.5" stroke-linecap="round" vector-effect="non-scaling-stroke" />
              <path v-if="plot.forecastLine" :d="plot.forecastLine" fill="none" stroke="var(--color-warning)" stroke-width="2" stroke-dasharray="5 5" vector-effect="non-scaling-stroke" />
            </svg>

            <span
              v-for="(dot, i) in plot.dots"
              :key="i"
              class="dot-point"
              :style="{ left: dot.left, top: dot.top }"
              :title="formatCurrency(dot.value)"
            />
            <span
              v-if="plot.forecastDot"
              class="dot-point dot-point--forecast"
              :style="{ left: plot.forecastDot.left, top: plot.forecastDot.top }"
              :title="formatCurrency(plot.forecastDot.value)"
            />
          </div>

          <ul class="months" :style="{ '--count': plot.slots }" aria-hidden="true">
            <li v-for="label in plot.labels" :key="label" :class="{ 'is-forecast': label === 'previsão' }">{{ label }}</li>
          </ul>
        </div>
      </template>
    </template>

    <template v-else>
      <p v-if="tagRows.length === 0" class="empty-state">Nenhuma tag com saídas registradas ainda.</p>

      <table v-else class="table">
        <thead>
          <tr>
            <th scope="col">Tag</th>
            <th scope="col" class="col-spark"><span class="sr-only">Evolução</span></th>
            <th scope="col" class="num">Média</th>
            <th scope="col" class="num col-wide">Variação</th>
            <th scope="col" class="num">Previsão</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="stat in tagRows" :key="stat.tagId">
            <th scope="row">
              <span class="tag-name">
                <i class="dot" :style="{ background: colorForTag(stat.tagId) }" />
                {{ stat.tagName }}
              </span>
              <small>{{ stat.count }} {{ stat.count === 1 ? 'saída' : 'saídas' }}</small>
            </th>
            <td class="col-spark">
              <DashboardSparkline v-if="stat.months.length > 1" :data="stat.months.map((m) => m.total)" tone="neutral" />
            </td>
            <td class="num figure">{{ formatCurrency(stat.mean) }}</td>
            <td class="num figure col-wide">± {{ formatCurrency(stat.standardDeviation) }}</td>
            <td class="num figure">{{ stat.forecastNextMonth !== null ? formatCurrency(stat.forecastNextMonth) : '-' }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </section>
</template>

<style scoped>
.outlook {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.outlook-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3) var(--space-4);
}

.segmented-item {
  min-height: 32px;
  padding: 4px 14px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3) var(--space-4);
  padding: var(--space-4) 0;
  border-block: 1px solid var(--color-border);
}

.stats dt {
  margin-bottom: 2px;
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
}

.stats dd {
  font-size: var(--text-md);
  font-weight: 500;
  overflow-wrap: anywhere;
}

.stats-forecast dt {
  color: var(--color-warning-strong);
}

.stats-forecast dd {
  color: var(--color-warning-strong);
}

@media (max-width: 559px) {
  .stats {
    grid-template-columns: minmax(0, 1fr);
  }
}

/* ---- grafico ---- */
.plot {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  grid-template-rows: 220px auto;
  gap: var(--space-2) var(--space-3);
}

.axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-text-subtle);
}

.axis li {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 0;
  white-space: nowrap;
}

.canvas {
  position: relative;
  background-image: repeating-linear-gradient(to bottom, var(--color-border) 0 1px, transparent 1px 25%);
  border-bottom: 1px solid var(--color-border-strong);
}

.canvas svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.band {
  position: absolute;
  inset-inline: 0;
  background: var(--color-primary-soft);
}

.mean {
  position: absolute;
  inset-inline: 0;
  border-top: 1px dashed var(--color-border-strong);
}

.mean em {
  position: absolute;
  right: 0;
  bottom: 3px;
  font-size: 11px;
  font-style: normal;
  color: var(--color-text-subtle);
}

.dot-point {
  position: absolute;
  width: 9px;
  height: 9px;
  transform: translate(-50%, -50%);
  border: 2px solid var(--color-surface);
  border-radius: 50%;
  background: var(--color-primary);
}

.dot-point--forecast {
  width: 13px;
  height: 13px;
  background: var(--color-warning);
}

.months {
  grid-column: 2;
  display: grid;
  grid-template-columns: repeat(var(--count), minmax(0, 1fr));
  font-size: var(--text-xs);
  text-align: center;
  text-transform: capitalize;
  color: var(--color-text-subtle);
}

.months .is-forecast {
  color: var(--color-warning-strong);
}

/* ---- tabela por tag ---- */
.table {
  width: 100%;
  font-size: var(--text-sm);
}

.table th,
.table td {
  padding: var(--space-3) var(--space-2);
  border-top: 1px solid var(--color-border);
  text-align: left;
  vertical-align: middle;
}

.table thead th {
  border-top: 0;
  padding-block: 0 var(--space-2);
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-subtle);
}

.table tbody th {
  font-weight: 500;
}

.table small {
  display: block;
  margin-left: 18px;
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--color-text-subtle);
}

.tag-name {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.num {
  text-align: right !important;
  white-space: nowrap;
}

.col-spark {
  width: 110px;
}

@media (max-width: 639px) {
  .col-spark,
  .col-wide {
    display: none;
  }
}
</style>
