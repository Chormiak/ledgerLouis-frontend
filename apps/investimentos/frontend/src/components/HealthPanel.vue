<script setup lang="ts">
import type { Health, Indicators, Medians } from '../api'
import { formatFraction, formatRatio } from '../lib/format'

defineProps<{ indicators: Indicators; medians: Partial<Medians>; health: Record<keyof Indicators, Health>; sector: string }>()

const ROWS: { key: keyof Indicators; label: string; hint: string; fmt: (v: number | null | undefined) => string }[] = [
  { key: 'pe', label: 'P/L', hint: 'menor é melhor', fmt: formatRatio },
  { key: 'ev_ebitda', label: 'EV/EBITDA', hint: 'menor é melhor', fmt: formatRatio },
  { key: 'net_debt_ebitda', label: 'Dív. líq./EBITDA', hint: 'menor é melhor', fmt: formatRatio },
  { key: 'net_margin', label: 'Margem líquida', hint: 'maior é melhor', fmt: formatFraction },
  { key: 'roe', label: 'ROE', hint: 'maior é melhor', fmt: formatFraction },
]
const STATUS = {
  melhor: { icon: '▲', text: 'Melhor que a mediana', cls: 'border-up/50 text-up' },
  na_media: { icon: '=', text: 'Na média', cls: 'border-accent/50 text-accent' },
  pior: { icon: '▼', text: 'Pior que a mediana', cls: 'border-down/50 text-down' },
}
</script>

<template>
  <ul class="grid gap-px overflow-hidden rounded border border-rule bg-rule sm:grid-cols-5">
    <li v-for="r in ROWS" :key="r.key" class="bg-panel p-4">
      <p class="text-sm text-muted">{{ r.label }}</p>
      <p class="num mt-1 text-2xl">{{ r.fmt(indicators[r.key]) }}</p>
      <p class="num text-xs text-muted">mediana {{ r.fmt(medians[r.key]) }}</p>
      <p
        v-if="health[r.key]"
        class="mt-2 inline-flex items-center gap-1 rounded border px-1.5 text-xs"
        :class="STATUS[health[r.key]!].cls"
      >
        <span aria-hidden="true">{{ STATUS[health[r.key]!].icon }}</span>{{ STATUS[health[r.key]!].text }}
      </p>
      <p v-else class="mt-2 text-xs text-muted">Sem comparação</p>
      <p class="mt-1 text-[11px] text-muted">{{ r.hint }}</p>
    </li>
  </ul>
  <p class="mt-2 text-xs text-muted">
    Comparação com a mediana de {{ sector }}; dentro de 10% da mediana conta como "na média". Não é nota de investimento.
  </p>
</template>
