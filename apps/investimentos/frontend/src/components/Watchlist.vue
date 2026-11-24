<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { fetchAssets, fetchPortfolio, fetchSparklines, type Asset } from '../api'
import { formatBRL, formatPoints, trendClass } from '../lib/format'
import { vAutoAnimate } from '@formkit/auto-animate/vue'
import AnimatedNumber from './AnimatedNumber.vue'
import Sparkline from './Sparkline.vue'

const assets = useQuery({ queryKey: ['assets'], queryFn: fetchAssets, refetchInterval: 5 * 60_000 })
const portfolio = useQuery({ queryKey: ['portfolio'], queryFn: fetchPortfolio })
const sparks = useQuery({ queryKey: ['sparklines'], queryFn: fetchSparklines })

const held = computed(() => new Set(portfolio.data.value?.positions.map((p) => p.ticker) ?? []))
const byVolume = (a: Asset, b: Asset) => (b.quote?.volume ?? 0) - (a.quote?.volume ?? 0)
const groups = computed(() => {
  const all = assets.data.value ?? []
  return [
    { title: 'Sua carteira', items: all.filter((a) => held.value.has(a.ticker)) },
    { title: 'Mais negociadas', items: all.filter((a) => !held.value.has(a.ticker)).sort(byVolume).slice(0, 12) },
  ].filter((g) => g.items.length)
})
</script>

<template>
  <nav aria-label="Lista de ações" class="space-y-5">
    <p v-if="assets.isPending.value" class="text-sm text-muted">Carregando…</p>
    <section v-for="g in groups" :key="g.title">
      <h2 class="mb-2 px-2 text-xs text-muted">{{ g.title }}</h2>
      <ul v-auto-animate class="space-y-1">
        <li v-for="a in g.items" :key="a.ticker">
          <RouterLink
            :to="`/acoes/${a.ticker}`"
            class="flex items-center gap-3 rounded-lg px-2 py-2 hover:bg-raise"
            active-class="bg-raise ring-1 ring-accent/40"
          >
            <span class="min-w-0 flex-1">
              <span class="num block text-sm text-paper">{{ a.ticker }}</span>
              <span class="num block text-xs text-muted"><AnimatedNumber :value="a.quote?.price" :format="formatBRL" /></span>
            </span>
            <Sparkline :values="sparks.data.value?.[a.ticker] ?? []" />
            <span class="num w-16 text-right text-xs" :class="trendClass(a.quote?.change_pct)">{{ formatPoints(a.quote?.change_pct) }}</span>
          </RouterLink>
        </li>
      </ul>
    </section>
  </nav>
</template>
