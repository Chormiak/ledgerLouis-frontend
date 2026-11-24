<script setup lang="ts">
import { computed } from 'vue'
import type { Asset } from '../api'
import { formatPoints } from '../lib/format'

const props = defineProps<{ assets: Asset[] }>()

const moved = computed(() => props.assets.filter((a) => a.quote?.change_pct !== null && a.quote?.change_pct !== undefined))
const ups = computed(() => moved.value.filter((a) => a.quote!.change_pct! > 0).length)
const downs = computed(() => moved.value.filter((a) => a.quote!.change_pct! < 0).length)
const sorted = computed(() => [...moved.value].sort((a, b) => b.quote!.change_pct! - a.quote!.change_pct!))
const top = computed(() => sorted.value.slice(0, 3).filter((a) => a.quote!.change_pct! > 0))
const bottom = computed(() => sorted.value.slice(-3).reverse().filter((a) => a.quote!.change_pct! < 0))
</script>

<template>
  <section v-if="moved.length" aria-label="Pulso do mercado hoje" class="mb-8 grid gap-6 sm:grid-cols-[auto_1fr_1fr] sm:items-center">
    <div>
      <p class="font-display text-2xl">
        <span class="num text-up">{{ ups }}</span> sobem, <span class="num text-down">{{ downs }}</span> caem
      </p>
      <!-- barra de amplitude: proporção de altas e quedas, com o número ao lado para não depender de cor -->
      <div class="mt-2 flex h-1.5 w-56 overflow-hidden rounded-sm bg-rule" aria-hidden="true">
        <span class="bg-up" :style="{ width: `${(ups / moved.length) * 100}%` }" />
        <span class="ml-auto bg-down" :style="{ width: `${(downs / moved.length) * 100}%` }" />
      </div>
    </div>
    <div>
      <p class="text-xs text-muted">Maiores altas</p>
      <p class="mt-1 flex flex-wrap gap-x-4 text-sm">
        <RouterLink v-for="a in top" :key="a.ticker" :to="`/acoes/${a.ticker}`" class="num hover:text-paper">
          {{ a.ticker }} <span class="text-up">▲ {{ formatPoints(a.quote!.change_pct) }}</span>
        </RouterLink>
        <span v-if="!top.length" class="text-muted">nenhuma</span>
      </p>
    </div>
    <div>
      <p class="text-xs text-muted">Maiores quedas</p>
      <p class="mt-1 flex flex-wrap gap-x-4 text-sm">
        <RouterLink v-for="a in bottom" :key="a.ticker" :to="`/acoes/${a.ticker}`" class="num hover:text-paper">
          {{ a.ticker }} <span class="text-down">▼ {{ formatPoints(a.quote!.change_pct) }}</span>
        </RouterLink>
        <span v-if="!bottom.length" class="text-muted">nenhuma</span>
      </p>
    </div>
  </section>
</template>
