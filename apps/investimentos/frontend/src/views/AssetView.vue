<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed, watchEffect } from 'vue'
import { fetchAssetFull, fetchPortfolio, fetchScoreboard } from '../api'
import ErrorBox from '../components/ErrorBox.vue'
import HealthPanel from '../components/HealthPanel.vue'
import NewsList from '../components/NewsList.vue'
import PriceChart from '../components/PriceChart.vue'
import SourceNote from '../components/SourceNote.vue'
import AnimatedNumber from '../components/AnimatedNumber.vue'
import { formatBRL, formatCompact, formatFraction, formatMoney, formatPoints, trendArrow, trendClass } from '../lib/format'
import { usePublishScreen } from '../lib/screen'

const props = defineProps<{ ticker: string }>()
const asset = useQuery({ queryKey: computed(() => ['asset', props.ticker]), queryFn: () => fetchAssetFull(props.ticker) })
const portfolio = useQuery({ queryKey: ['portfolio'], queryFn: fetchPortfolio })
const board = useQuery({ queryKey: ['scoreboard'], queryFn: fetchScoreboard })

const a = computed(() => asset.data.value)
const position = computed(() => portfolio.data.value?.positions.find((p) => p.ticker === a.value?.ticker))
const theses = computed(() => board.data.value?.rows.filter((r) => r.ticker === a.value?.ticker) ?? [])
const pct = (v: number | null | undefined) => (v === null || v === undefined ? '—' : formatPoints(v * 100))
const rsiNote = (v: number | null) => (v === null ? '' : v >= 70 ? 'sobrecomprado (≥ 70)' : v <= 30 ? 'sobrevendido (≤ 30)' : 'zona neutra')

watchEffect(() => {
  if (a.value) document.title = `${a.value.ticker} | LedgerLouis`
})
usePublishScreen(() => ({ view: 'asset', ticker: props.ticker.toUpperCase(), tickers: [props.ticker.toUpperCase()] }))
</script>

<template>
  <ErrorBox v-if="asset.error.value && !asset.error.value.message.includes('404')" :error="asset.error.value" />
  <p v-if="asset.error.value?.message.includes('404')" class="py-16 text-center text-muted">
    {{ ticker.toUpperCase() }} não está na base. Rode <code class="num text-paper">sync_market</code> ou confira o ticker.
  </p>
  <p v-else-if="asset.isPending.value" class="py-20 text-center text-muted">Carregando {{ ticker.toUpperCase() }}…</p>

  <template v-else-if="a">
    <header class="flex flex-wrap items-end justify-between gap-6">
      <div class="flex items-center gap-4">
        <img v-if="a.logo_url" :src="a.logo_url" alt="" class="h-12 w-12 rounded bg-paper/5 p-1" />
        <div>
          <h1 class="font-display text-3xl font-medium"><span class="num">{{ a.ticker }}</span> <span class="text-muted">{{ a.name }}</span></h1>
          <p class="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-sm">
            <RouterLink v-if="a.sector_group" :to="`/grupos/sector/${a.sector_group.slug}`" class="text-muted underline decoration-rule underline-offset-4 hover:text-paper">
              {{ a.sector_group.name }}
            </RouterLink>
            <RouterLink v-for="n in a.niches" :key="n.slug" :to="`/grupos/niche/${n.slug}`" class="rounded border border-rule px-1.5 text-muted hover:text-paper">
              {{ n.name }}
            </RouterLink>
          </p>
        </div>
      </div>
      <div class="sm:text-right">
        <p class="num text-3xl"><AnimatedNumber :value="a.quote?.price" :format="(v) => formatMoney(v, a?.market)" /></p>
        <p class="num" :class="trendClass(a.quote?.change_pct)">
          <span aria-hidden="true" class="mr-1 text-xs">{{ trendArrow(a.quote?.change_pct) }}</span>{{ formatPoints(a.quote?.change_pct) }} hoje
        </p>
        <p class="text-xs text-muted">valor de mercado {{ formatCompact(a.quote?.market_cap, a.market) }}</p>
      </div>
    </header>

    <dl class="mt-8 grid grid-cols-2 gap-px border-y border-rule bg-rule sm:grid-cols-4">
      <div class="bg-panel py-4 pr-4">
        <dt class="text-sm text-muted">Retorno em {{ a.history.days }} pregões</dt>
        <dd class="num mt-1 text-2xl" :class="trendClass(a.history.return_period)">{{ pct(a.history.return_period) }}</dd>
      </div>
      <div class="bg-panel p-4">
        <dt class="text-sm text-muted">Retorno em 1 mês</dt>
        <dd class="num mt-1 text-2xl" :class="trendClass(a.history.return_1m)">{{ pct(a.history.return_1m) }}</dd>
        <dd class="text-xs text-muted">21 pregões</dd>
      </div>
      <div class="bg-panel py-4 pr-4 sm:p-4">
        <dt class="text-sm text-muted">RSI (14)</dt>
        <dd class="num mt-1 text-2xl">{{ a.history.rsi14 === null ? '—' : a.history.rsi14.toLocaleString('pt-BR', { maximumFractionDigits: 0 }) }}</dd>
        <dd class="text-xs text-muted">{{ rsiNote(a.history.rsi14) }}</dd>
      </div>
      <div class="bg-panel p-4">
        <dt class="text-sm text-muted">Volatilidade anualizada</dt>
        <dd class="num mt-1 text-2xl">{{ formatFraction(a.history.volatility) }}</dd>
      </div>
    </dl>

    <section class="mt-8" aria-labelledby="chart-title">
      <h2 id="chart-title" class="sr-only">Gráfico de preço</h2>
      <PriceChart v-if="a.history.bars.length" :bars="a.history.bars" :sma20="a.history.sma20" :label="`Preço diário de ${a.ticker} nos últimos ${a.history.days} pregões`" />
      <p v-else class="rounded border border-dashed border-rule py-16 text-center text-sm text-muted">
        Sem histórico ainda. Rode <code class="num text-paper">python manage.py sync_market --only history</code>.
      </p>
      <SourceNote class="mt-1" label="Histórico" :source="a.history.source" :at="a.history.fetched_at" />
    </section>

    <section class="mt-12" aria-labelledby="health-title">
      <h2 id="health-title" class="font-display mb-3 text-xl font-medium">Saúde contra o setor</h2>
      <HealthPanel v-if="a.sector_group" :indicators="a.indicators" :medians="a.sector_group.medians" :health="a.health" :sector="a.sector_group.name" />
      <p v-else class="text-sm text-muted">Sem setor cadastrado para comparar.</p>
    </section>

    <section v-if="position || theses.length" class="mt-12 grid gap-8 sm:grid-cols-2" aria-label="Sua relação com esta ação">
      <div v-if="position">
        <h2 class="font-display mb-3 text-xl font-medium">Sua posição</h2>
        <dl class="num grid grid-cols-2 gap-2 text-sm">
          <dt class="font-sans text-muted">Quantidade</dt><dd>{{ position.quantity.toLocaleString('pt-BR') }}</dd>
          <dt class="font-sans text-muted">Preço médio</dt><dd>{{ formatBRL(position.avg_price) }}</dd>
          <dt class="font-sans text-muted">Valor</dt><dd>{{ formatBRL(position.value) }}</dd>
          <dt class="font-sans text-muted">Peso na carteira</dt><dd>{{ formatFraction(position.weight) }}</dd>
          <dt class="font-sans text-muted">Ganho</dt><dd :class="trendClass(position.gain_pct)">{{ pct(position.gain_pct) }}</dd>
        </dl>
      </div>
      <div v-if="theses.length">
        <h2 class="font-display mb-3 text-xl font-medium">Teses no placar</h2>
        <ul class="space-y-2 text-sm">
          <li v-for="(t, i) in theses" :key="i" class="border-b border-rule/60 pb-2">
            <p>{{ t.summary }}</p>
            <p class="num text-xs text-muted">
              esperado {{ t.expectation }}, retorno {{ pct(t.return_pct) }},
              <span :class="t.hit === null ? '' : t.hit ? 'text-up' : 'text-down'">{{ t.hit === null ? 'não avaliada' : t.hit ? 'acertou' : 'errou' }}</span>
            </p>
          </li>
        </ul>
      </div>
    </section>

    <section class="mt-12" aria-labelledby="news-title">
      <h2 id="news-title" class="font-display mb-3 text-xl font-medium">Notícias e fatos relevantes</h2>
      <NewsList :items="a.news" empty-text="Sem notícias desta ação ainda." />
    </section>
  </template>
</template>
