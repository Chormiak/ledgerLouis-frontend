<script setup lang="ts">
import { PieChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { formatFraction } from '../lib/format'

use([PieChart, TooltipComponent, CanvasRenderer])

const props = defineProps<{ exposure: Record<string, number> }>()
const css = (n: string) => getComputedStyle(document.documentElement).getPropertyValue(n).trim()
const entries = computed(() => Object.entries(props.exposure).sort((a, b) => b[1] - a[1]))
// tons de uma só família (ciano) para não competir com alta/queda
const palette = ['#34b585', '#2c9a72', '#247f5e', '#1d654b', '#174f3b', '#123c2e', '#0d2b21']

const option = computed(() => ({
  animation: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  tooltip: { formatter: (p: { name: string; value: number }) => `${p.name}: ${formatFraction(p.value)}`, backgroundColor: css('--panel'), borderColor: css('--rule'), textStyle: { color: css('--paper') } },
  series: [{
    type: 'pie',
    radius: ['58%', '80%'],
    label: { show: false },
    itemStyle: { borderColor: css('--ink'), borderWidth: 2 },
    data: entries.value.map(([name, value], i) => ({ name, value, itemStyle: { color: palette[i % palette.length] } })),
  }],
}))
</script>

<template>
  <div class="grid items-center gap-6 sm:grid-cols-[220px_minmax(0,1fr)]">
    <div class="h-[220px]">
      <VChart :option="option" autoresize role="img" :aria-label="`Exposição por setor: ${entries.map(([n, v]) => `${n} ${formatFraction(v)}`).join(', ')}`" />
    </div>
    <ul class="space-y-2 text-sm">
      <li v-for="([name, value], i) in entries" :key="name" class="flex items-center justify-between gap-4 border-b border-rule/60 pb-2">
        <span class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-sm" :style="{ background: palette[i % palette.length] }" />{{ name }}</span>
        <span class="num">{{ formatFraction(value) }}</span>
      </li>
    </ul>
  </div>
</template>
