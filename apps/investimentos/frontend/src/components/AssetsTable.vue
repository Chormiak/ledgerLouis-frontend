<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Asset, Medians } from '../api'
import { formatCompact, formatFraction, formatMoney, formatPoints, formatRatio, trendArrow, trendClass } from '../lib/format'

const props = defineProps<{ assets: Asset[]; medians?: Partial<Medians> }>()

// linha de referência: as mesmas colunas de indicadores, com as medianas do grupo
const medianRow = computed(() => props.medians && ({ indicators: { pe: null, ev_ebitda: null, net_debt_ebitda: null, net_margin: null, roe: null, ...props.medians } } as Asset))

type Col = {
  key: string
  label: string
  title?: string
  value: (a: Asset) => number | string | null | undefined
  show: (a: Asset) => string
  numeric?: boolean
}

const cols: Col[] = [
  { key: 'ticker', label: 'Ação', value: (a) => a.ticker, show: (a) => a.ticker },
  { key: 'sector', label: 'Setor', value: (a) => a.sector, show: (a) => a.sector || '—' },
  { key: 'price', label: 'Preço', value: (a) => a.quote?.price, show: (a) => formatMoney(a.quote?.price, a.market), numeric: true },
  { key: 'change', label: 'Dia', value: (a) => a.quote?.change_pct, show: (a) => formatPoints(a.quote?.change_pct), numeric: true },
  { key: 'cap', label: 'Valor de mercado', value: (a) => a.quote?.market_cap, show: (a) => formatCompact(a.quote?.market_cap, a.market), numeric: true },
  { key: 'pe', label: 'P/L', title: 'Preço sobre lucro por ação', value: (a) => a.indicators.pe, show: (a) => formatRatio(a.indicators.pe), numeric: true },
  { key: 'ev', label: 'EV/EBITDA', title: 'Valor da firma sobre EBITDA', value: (a) => a.indicators.ev_ebitda, show: (a) => formatRatio(a.indicators.ev_ebitda), numeric: true },
  { key: 'nd', label: 'Dív. líq./EBITDA', title: 'Dívida líquida sobre EBITDA; negativo = caixa líquido', value: (a) => a.indicators.net_debt_ebitda, show: (a) => formatRatio(a.indicators.net_debt_ebitda), numeric: true },
  { key: 'margin', label: 'Margem líq.', value: (a) => a.indicators.net_margin, show: (a) => formatFraction(a.indicators.net_margin), numeric: true },
  { key: 'roe', label: 'ROE', title: 'Retorno sobre patrimônio, como informado pela fonte', value: (a) => a.indicators.roe, show: (a) => formatFraction(a.indicators.roe), numeric: true },
]

const sortKey = ref('cap')
const desc = ref(true)

function sortBy(key: string) {
  if (sortKey.value === key) desc.value = !desc.value
  else {
    sortKey.value = key
    desc.value = cols.find((c) => c.key === key)!.numeric === true
  }
}

const rows = computed(() => {
  const col = cols.find((c) => c.key === sortKey.value)!
  return [...props.assets].sort((x, y) => {
    const a = col.value(x)
    const b = col.value(y)
    if (a === null || a === undefined) return 1 // vazios sempre no fim
    if (b === null || b === undefined) return -1
    const cmp = typeof a === 'number' ? a - (b as number) : String(a).localeCompare(String(b), 'pt-BR')
    return desc.value ? -cmp : cmp
  })
})

</script>

<template>
  <div class="overflow-x-auto">
    <table class="w-full min-w-[920px] border-collapse text-sm">
      <caption class="sr-only">Ações da B3 com cotação e indicadores. Clique no cabeçalho para ordenar.</caption>
      <thead>
        <tr class="border-b border-rule text-muted">
          <th
            v-for="c in cols"
            :key="c.key"
            scope="col"
            :aria-sort="sortKey === c.key ? (desc ? 'descending' : 'ascending') : 'none'"
            class="py-2 font-normal"
            :class="c.numeric ? 'text-right' : 'text-left'"
          >
            <button
              type="button"
              :title="c.title"
              class="inline-flex items-center gap-1 rounded px-1 hover:text-paper"
              :class="sortKey === c.key && 'text-paper'"
              @click="sortBy(c.key)"
            >
              {{ c.label }}
              <span aria-hidden="true" class="w-2 text-accent">{{ sortKey === c.key ? (desc ? '↓' : '↑') : '' }}</span>
            </button>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="medianRow" class="border-b border-accent/40 text-accent">
          <th scope="row" colspan="5" class="py-2 text-left font-normal">Mediana do grupo</th>
          <td v-for="c in cols.slice(5)" :key="c.key" class="num py-2 text-right">{{ c.show(medianRow) }}</td>
        </tr>
        <tr v-for="a in rows" :key="a.ticker" class="border-b border-rule/60 hover:bg-panel">
          <th scope="row" class="py-2 pr-4 text-left font-normal">
            <RouterLink :to="`/acoes/${a.ticker}`" class="num font-medium text-paper underline decoration-rule underline-offset-4 hover:decoration-accent">{{ a.ticker }}</RouterLink>
            <span class="ml-2 text-muted">{{ a.name }}</span>
          </th>
          <td class="py-2 pr-4 text-muted">{{ a.sector || '—' }}</td>
          <td class="num py-2 text-right">{{ formatMoney(a.quote?.price, a.market) }}</td>
          <td class="num py-2 text-right" :class="trendClass(a.quote?.change_pct)">
            <span aria-hidden="true" class="mr-1 text-[10px]">{{ trendArrow(a.quote?.change_pct) }}</span>{{ formatPoints(a.quote?.change_pct) }}
          </td>
          <td v-for="c in cols.slice(4)" :key="c.key" class="num py-2 text-right">{{ c.show(a) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
