<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { fetchCategoryNews, fetchGroup } from '../api'
import AssetsTable from '../components/AssetsTable.vue'
import ErrorBox from '../components/ErrorBox.vue'
import NewsList from '../components/NewsList.vue'
import SectorTreemap from '../components/SectorTreemap.vue'
import SourceNote from '../components/SourceNote.vue'
import { formatCompact, formatPoints, trendArrow, trendClass } from '../lib/format'
import { usePublishScreen } from '../lib/screen'

const US_NICHE_SLUG = 'global-tech-ia-eua'

const group = useQuery({ queryKey: ['group', 'niche', US_NICHE_SLUG], queryFn: () => fetchGroup('niche', US_NICHE_SLUG) })
const geopolitics = useQuery({ queryKey: ['news', 'geopolitica'], queryFn: () => fetchCategoryNews('geopolitica') })
const aiBubble = useQuery({ queryKey: ['news', 'ia_bolha'], queryFn: () => fetchCategoryNews('ia_bolha') })

const g = computed(() => group.data.value)
const withQuote = computed(() => g.value?.members.filter((m) => m.quote?.market_cap) ?? [])
const quoteAt = computed(() => g.value?.members.map((a) => a.quote?.fetched_at).filter(Boolean).sort().at(-1))

usePublishScreen(() => ({ view: 'mercado-eua', tickers: g.value?.members.slice(0, 60).map((m) => m.ticker) ?? [] }))
</script>

<template>
  <ErrorBox :error="group.error.value ?? geopolitics.error.value ?? aiBubble.error.value" />

  <header>
    <h1 class="font-display text-3xl font-medium">Mercado EUA</h1>
    <p class="mt-1 max-w-prose text-sm text-muted">Grandes empresas de tecnologia e IA dos EUA, fora da B3.</p>
  </header>

  <p v-if="group.isPending.value" class="py-20 text-center text-muted">Carregando…</p>
  <template v-else-if="g">
    <dl class="mt-6 grid grid-cols-2 gap-px border-y border-rule bg-rule sm:grid-cols-3">
      <div class="bg-panel py-4 pr-4">
        <dt class="text-sm text-muted">Variação do dia</dt>
        <dd class="num mt-1 text-2xl" :class="trendClass(g.change_pct)">
          <span aria-hidden="true" class="mr-1 text-sm">{{ trendArrow(g.change_pct) }}</span>{{ formatPoints(g.change_pct) }}
        </dd>
        <dd class="text-xs text-muted">ponderada por valor de mercado</dd>
      </div>
      <div class="bg-panel py-4 sm:px-4">
        <dt class="text-sm text-muted">Valor de mercado</dt>
        <dd class="num mt-1 text-2xl">{{ formatCompact(g.market_cap, 'US') }}</dd>
      </div>
      <div class="col-span-2 bg-panel py-4 sm:col-span-1 sm:px-4">
        <dt class="text-sm text-muted">Empresas na base</dt>
        <dd class="num mt-1 text-2xl">{{ g.count }}</dd>
      </div>
    </dl>

    <p v-if="!g.members.length" class="mt-8 rounded border border-dashed border-rule py-12 text-center text-sm text-muted">
      Nenhuma ação ainda. Rode <code class="num text-paper">python manage.py sync_market --only us_stocks</code>.
    </p>

    <section v-if="withQuote.length" class="mt-10" aria-labelledby="eua-map">
      <h2 id="eua-map" class="font-display mb-3 text-xl font-medium">Empresas do grupo</h2>
      <SectorTreemap :assets="withQuote" />
    </section>

    <section v-if="g.members.length" class="mt-10" aria-labelledby="eua-table">
      <h2 id="eua-table" class="font-display mb-3 text-xl font-medium">Indicadores</h2>
      <AssetsTable :assets="g.members" />
      <SourceNote class="mt-3" label="Cotações" :source="g.members[0]?.quote?.source" :at="quoteAt" />
    </section>

    <section class="mt-12" aria-labelledby="eua-news">
      <h2 id="eua-news" class="font-display mb-3 text-xl font-medium">Notícias das empresas</h2>
      <NewsList :items="g.news" />
    </section>
  </template>

  <section class="mt-12" aria-labelledby="geo-news">
    <h2 id="geo-news" class="font-display mb-3 text-xl font-medium">Geopolítica</h2>
    <p class="mb-3 max-w-prose text-sm text-muted">Notícias amplas que afetam o mercado, não só as empresas acima.</p>
    <NewsList :items="geopolitics.data.value ?? []" empty-text="Sem notícias de geopolítica ainda." />
  </section>

  <section class="mt-12" aria-labelledby="bubble-news">
    <h2 id="bubble-news" class="font-display mb-3 text-xl font-medium">Bolha da IA?</h2>
    <NewsList :items="aiBubble.data.value ?? []" empty-text="Sem notícias sobre a bolha da IA ainda." />
  </section>
</template>
