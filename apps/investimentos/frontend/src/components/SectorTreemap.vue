<script setup lang="ts">
import { TreemapChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import VChart from 'vue-echarts'
import type { Asset } from '../api'
import { formatCompact, formatMoney, formatPoints } from '../lib/format'

use([TreemapChart, TooltipComponent, CanvasRenderer])

const props = defineProps<{ assets: Asset[] }>()
const router = useRouter()
function open(p: { data?: unknown }) {
  const asset = (p.data as { asset?: Asset } | undefined)?.asset
  if (asset) router.push(`/acoes/${asset.ticker}`)
}

const css = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim()
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

function hexToRgb(hex: string) {
  const n = parseInt(hex.slice(1), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

/** Cor divergente: queda -> pauta -> alta, saturando em ±3%. */
function colorFor(change: number | null): { fill: string; text: string } {
  const rgb =
    change === null
      ? hexToRgb(css('--rule'))
      : (() => {
          const t = Math.max(-1, Math.min(1, change / 3))
          const base = hexToRgb(css('--panel'))
          const end = hexToRgb(t >= 0 ? css('--up') : css('--down'))
          return base.map((b, i) => Math.round(b + (end[i] - b) * (0.25 + 0.75 * Math.abs(t))))
        })()
  // texto claro ou escuro conforme a luminância do bloco, para manter contraste nos dois temas
  const lum = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
  return { fill: `rgb(${rgb.join(',')})`, text: lum > 0.55 ? '#18202e' : '#ffffff' }
}

const option = computed(() => {
  const bySector = new Map<string, Asset[]>()
  for (const a of props.assets) {
    if (!a.quote?.market_cap) continue
    const key = a.sector || 'Sem setor'
    bySector.set(key, [...(bySector.get(key) ?? []), a])
  }
  return {
    animation: !reduceMotion,
    tooltip: {
      backgroundColor: css('--panel'),
      borderColor: css('--rule'),
      textStyle: { color: css('--paper'), fontFamily: "'IBM Plex Sans', system-ui, sans-serif" },
      formatter: (info: { data: { asset?: Asset; name: string } }) => {
        const a = info.data.asset
        if (!a) return info.data.name
        return `<b>${a.ticker}</b> ${a.name}<br/>${formatMoney(a.quote?.price, a.market)} (${formatPoints(a.quote?.change_pct)})<br/>Valor de mercado ${formatCompact(a.quote?.market_cap, a.market)}`
      },
    },
    series: [
      {
        type: 'treemap',
        roam: false,
        nodeClick: false,
        breadcrumb: { show: false },
        width: '100%',
        height: '100%',
        top: 0,
        left: 0,
        upperLabel: {
          show: true,
          height: 22,
          color: css('--muted'),
          fontFamily: "'IBM Plex Sans', system-ui, sans-serif",
          fontSize: 12,
        },
        itemStyle: { borderColor: css('--ink'), borderWidth: 1, gapWidth: 1 },
        levels: [
          { itemStyle: { borderColor: css('--ink'), borderWidth: 0, gapWidth: 3 } },
          { itemStyle: { borderColor: css('--ink'), borderWidth: 3, gapWidth: 1 } },
        ],
        label: {
          color: css('--paper'),
          fontFamily: "'IBM Plex Mono', ui-monospace, monospace",
          fontSize: 12,
          lineHeight: 16,
          // nós de setor não têm ativo; só as folhas mostram ticker e variação
          formatter: (p: { name: string; data: { asset?: Asset } }) =>
            p.data.asset ? `${p.data.asset.ticker}\n${formatPoints(p.data.asset.quote?.change_pct)}` : p.name,
        },
        data: [...bySector].map(([sector, list]) => ({
          name: sector,
          children: list.map((a) => {
            const c = colorFor(a.quote!.change_pct)
            return { name: a.ticker, value: a.quote!.market_cap, asset: a, itemStyle: { color: c.fill }, label: { color: c.text } }
          }),
        })),
      },
    ],
  }
})

const summary = computed(() => {
  const withQuote = props.assets.filter((a) => a.quote?.change_pct !== null && a.quote?.change_pct !== undefined)
  const ups = withQuote.filter((a) => a.quote!.change_pct! > 0).length
  return `${ups} de ${withQuote.length} ações em alta hoje`
})
</script>

<template>
  <figure>
    <!-- a altura fica no contêiner: o CSS do vue-echarts (height: 100%) vence as utilidades do Tailwind -->
    <div class="h-[420px] sm:h-[520px]">
      <VChart :option="option" autoresize role="img" class="cursor-pointer" @click="open" :aria-label="`Mapa de calor do mercado por setor. ${summary}.`" />
    </div>
    <figcaption class="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs text-muted">
      <span>Área = valor de mercado. Cor = variação do dia, saturando em ±3%. {{ summary }}. Clique num bloco para abrir a ação.</span>
      <span class="flex items-center gap-2" aria-hidden="true">
        <span class="num">−3%</span>
        <span class="h-2 w-24 rounded-sm" style="background: linear-gradient(90deg, var(--down), var(--panel), var(--up))" />
        <span class="num">+3%</span>
      </span>
    </figcaption>
  </figure>
</template>
