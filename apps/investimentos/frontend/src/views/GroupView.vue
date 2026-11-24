<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed, watchEffect } from 'vue'
import { fetchGroup } from '../api'
import AssetsTable from '../components/AssetsTable.vue'
import ErrorBox from '../components/ErrorBox.vue'
import MacroStrip from '../components/MacroStrip.vue'
import NewsList from '../components/NewsList.vue'
import SectorTreemap from '../components/SectorTreemap.vue'
import SourceNote from '../components/SourceNote.vue'
import { formatCompact, formatPoints, trendArrow, trendClass } from '../lib/format'
import { usePublishScreen } from '../lib/screen'

const props = defineProps<{ kind: string; slug: string }>()

const group = useQuery({
  queryKey: computed(() => ['group', props.kind, props.slug]),
  queryFn: () => fetchGroup(props.kind, props.slug),
})

const g = computed(() => group.data.value)
const withQuote = computed(() => g.value?.members.filter((m) => m.quote?.market_cap) ?? [])
const quoteAt = computed(() => g.value?.members.map((a) => a.quote?.fetched_at).filter(Boolean).sort().at(-1))

usePublishScreen(() => ({
  view: 'group',
  kind: props.kind,
  slug: props.slug,
  name: g.value?.name,
  tickers: g.value?.members.slice(0, 60).map((m) => m.ticker) ?? [],
}))

watchEffect(() => {
  if (g.value) document.title = `${g.value.name} | LedgerLouis`
})
</script>

<template>
  <ErrorBox :error="group.error.value" />
  <RouterLink to="/grupos" class="text-sm text-muted hover:text-paper">Setores e nichos</RouterLink>

  <p v-if="group.isPending.value" class="py-20 text-center text-muted">Carregando…</p>
  <template v-else-if="g">
    <header class="mt-2">
      <h1 class="font-display text-3xl font-medium">{{ g.name }}</h1>
      <p class="mt-1 max-w-prose text-sm text-muted">
        {{ g.kind === 'niche' ? 'Nicho' : 'Setor' }}<template v-if="g.description">. {{ g.description }}</template>
      </p>
    </header>

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
        <dd class="num mt-1 text-2xl">{{ formatCompact(g.market_cap) }}</dd>
      </div>
      <div class="col-span-2 bg-panel py-4 sm:col-span-1 sm:px-4">
        <dt class="text-sm text-muted">Empresas na base</dt>
        <dd class="num mt-1 text-2xl">{{ g.count }}</dd>
      </div>
    </dl>

    <p v-if="!g.members.length" class="mt-8 rounded border border-dashed border-rule py-12 text-center text-sm text-muted">
      Nenhuma ação deste grupo está na base ainda. Rode <code class="num text-paper">sync_market</code> ou edite o nicho no admin.
    </p>

    <section v-if="g.macro.length" class="mt-10" aria-labelledby="g-macro">
      <h2 id="g-macro" class="font-display mb-3 text-xl font-medium">Macro que mais pesa</h2>
      <MacroStrip :points="g.macro" />
    </section>

    <section v-if="withQuote.length" class="mt-10" aria-labelledby="g-map">
      <h2 id="g-map" class="font-display mb-3 text-xl font-medium">Empresas do grupo</h2>
      <SectorTreemap :assets="withQuote" />
    </section>

    <section v-if="g.members.length" class="mt-10" aria-labelledby="g-table">
      <h2 id="g-table" class="font-display mb-3 text-xl font-medium">Indicadores contra a mediana</h2>
      <AssetsTable :assets="g.members" :medians="g.medians" />
      <SourceNote class="mt-3" label="Cotações" :source="g.members[0]?.quote?.source" :at="quoteAt" />
    </section>

    <section class="mt-12" aria-labelledby="g-news">
      <h2 id="g-news" class="font-display mb-3 text-xl font-medium">Notícias e fatos relevantes</h2>
      <NewsList :items="g.news" />
    </section>
  </template>
</template>
