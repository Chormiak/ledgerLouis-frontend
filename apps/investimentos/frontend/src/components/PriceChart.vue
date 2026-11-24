<script setup lang="ts">
import {
  CandlestickSeries,
  createChart,
  HistogramSeries,
  LineSeries,
  type IChartApi,
  type UTCTimestamp,
} from 'lightweight-charts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { Bar } from '../api'

const props = defineProps<{ bars: Bar[]; sma20: (number | null)[]; label: string }>()
const el = ref<HTMLDivElement>()
let chart: IChartApi | undefined

const css = (n: string) => getComputedStyle(document.documentElement).getPropertyValue(n).trim()
const compact = new Intl.NumberFormat('pt-BR', { notation: 'compact', maximumFractionDigits: 1 })
const price = { type: 'custom' as const, formatter: (v: number) => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
const t = (d: string) => (Date.parse(`${d}T00:00:00Z`) / 1000) as UTCTimestamp

function draw() {
  chart?.remove()
  if (!el.value || !props.bars.length) return
  const [up, down, muted, rule, accent] = ['--up', '--down', '--muted', '--rule', '--accent'].map(css)
  chart = createChart(el.value, {
    autoSize: true,
    layout: { background: { color: 'transparent' }, textColor: muted, fontFamily: "'IBM Plex Mono', ui-monospace, monospace", attributionLogo: false },
    grid: { vertLines: { color: rule }, horzLines: { color: rule } },
    rightPriceScale: { borderColor: rule },
    timeScale: { borderColor: rule },
    // formato por série: um priceFormatter global aqui sobrescreveria também o eixo do volume
    localization: { locale: 'pt-BR' },
  })
  chart
    .addSeries(CandlestickSeries, { priceFormat: price, upColor: up, downColor: down, borderVisible: false, wickUpColor: up, wickDownColor: down })
    .setData(
      props.bars
        .filter((b) => b.open !== null && b.high !== null && b.low !== null)
        .map((b) => ({ time: t(b.date), open: b.open!, high: b.high!, low: b.low!, close: b.close })),
    )
  chart
    .addSeries(LineSeries, { priceFormat: price, color: accent, lineWidth: 2, priceLineVisible: false, lastValueVisible: false })
    .setData(props.bars.flatMap((b, i) => (props.sma20[i] === null ? [] : [{ time: t(b.date), value: props.sma20[i]! }])))
  chart
    .addSeries(HistogramSeries, { color: muted, priceFormat: { type: 'custom', formatter: (v: number) => compact.format(v) }, priceLineVisible: false }, 1)
    .setData(props.bars.map((b) => ({ time: t(b.date), value: b.volume ?? 0, color: (b.open ?? b.close) <= b.close ? `${up}88` : `${down}88` })))
  chart.panes()[1]?.setStretchFactor(0.25)
  chart.timeScale().fitContent()
}

onMounted(draw)
watch(() => props.bars, draw)
onBeforeUnmount(() => chart?.remove())
</script>

<template>
  <figure>
    <div ref="el" class="h-[360px] w-full sm:h-[420px]" role="img" :aria-label="label" />
    <figcaption class="mt-2 flex flex-wrap gap-4 text-xs text-muted">
      <span class="flex items-center gap-1"><span class="h-0.5 w-4 bg-accent" /> média móvel de 20 dias</span>
      <span>Candles diários; volume no painel de baixo.</span>
    </figcaption>
  </figure>
</template>
