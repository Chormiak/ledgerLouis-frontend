<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { fetchAssets, fetchMacro } from '../api'
import AssetsTable from '../components/AssetsTable.vue'
import ErrorBox from '../components/ErrorBox.vue'
import MacroStrip from '../components/MacroStrip.vue'
import MarketPulse from '../components/MarketPulse.vue'
import SectorTreemap from '../components/SectorTreemap.vue'
import SourceNote from '../components/SourceNote.vue'
import { usePublishScreen } from '../lib/screen'

const assets = useQuery({ queryKey: ['assets'], queryFn: fetchAssets, refetchInterval: 5 * 60_000 })
const macro = useQuery({ queryKey: ['macro'], queryFn: fetchMacro })

const list = computed(() => assets.data.value ?? [])
const quoteAt = computed(() => list.value.map((a) => a.quote?.fetched_at).filter(Boolean).sort().at(-1))
const fundAt = computed(() => list.value.map((a) => a.fundamentals_fetched_at).filter(Boolean).sort().at(-1))

usePublishScreen(() => ({ view: 'overview', tickers: list.value.slice(0, 60).map((a) => a.ticker) }))
</script>

<template>
  <ErrorBox :error="assets.error.value ?? macro.error.value" />

  <MarketPulse :assets="list" />
  <MacroStrip :points="macro.data.value ?? []" />

  <section class="mt-10" aria-labelledby="map-title">
    <h2 id="map-title" class="font-display mb-3 text-xl font-medium">Mercado por setor</h2>
    <p v-if="assets.isPending.value" class="py-20 text-center text-muted">Carregando cotações…</p>
    <p v-else-if="!list.length" class="rounded border border-dashed border-rule py-16 text-center text-muted">
      Ainda não há ações. Rode <code class="num text-paper">python manage.py sync_market</code> no backend.
    </p>
    <SectorTreemap v-else :assets="list" />
  </section>

  <section v-if="list.length" class="mt-12" aria-labelledby="table-title">
    <h2 id="table-title" class="font-display mb-3 text-xl font-medium">Ações e indicadores</h2>
    <AssetsTable :assets="list" />
    <div class="mt-3 space-y-1">
      <SourceNote label="Cotações" :source="list[0]?.quote?.source" :at="quoteAt" />
      <SourceNote label="Fundamentos" :source="list.find((a) => a.fundamentals_source)?.fundamentals_source" :at="fundAt" />
      <p class="text-xs text-muted">
        Indicadores calculados pelo LedgerLouis a partir dos dados da fonte; ROE como informado pela fonte. "—" = dado
        ausente ou sem sentido (ex.: lucro negativo).
      </p>
    </div>
  </section>
</template>
