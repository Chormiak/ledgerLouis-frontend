<script setup lang="ts">
import type { MacroPoint } from '../api'
import SourceNote from './SourceNote.vue'

const props = defineProps<{ points: MacroPoint[] }>()

const value = (p: MacroPoint) =>
  p.unit === 'R$'
    ? `R$ ${p.value.toLocaleString('pt-BR', { minimumFractionDigits: 4, maximumFractionDigits: 4 })}`
    : `${p.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}${p.unit.startsWith('%') ? '%' : ''}`

const refDate = (iso: string) => iso.split('-').reverse().join('/')
const latest = () => props.points.map((p) => p.fetched_at).sort().at(-1)
</script>

<template>
  <section aria-labelledby="macro-title">
    <h2 id="macro-title" class="sr-only">Indicadores macroeconômicos</h2>
    <dl class="grid grid-cols-1 border-y border-rule sm:grid-cols-3 sm:divide-x sm:divide-rule">
      <div v-for="p in points" :key="p.code" class="border-b border-rule/60 py-4 last:border-0 sm:border-0 sm:px-6 sm:first:pl-0">
        <dt class="text-sm text-muted">
          {{ p.name }}<span v-if="p.unit === '% a.a.'"> (ao ano)</span>
        </dt>
        <dd class="num mt-1 text-2xl text-paper">{{ value(p) }}</dd>
        <dd class="mt-1 text-xs text-muted">referência {{ refDate(p.date) }}</dd>
      </div>
      <p v-if="!points.length" class="py-4 text-sm text-muted sm:col-span-3">
        Sem dados macro. Rode <code class="num">python manage.py sync_market --only macro</code> no backend.
      </p>
    </dl>
    <SourceNote class="mt-2" :source="points[0]?.source === 'bcb-sgs' ? 'Banco Central (SGS)' : points[0]?.source" :at="latest()" />
  </section>
</template>
