<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { fetchScoreboard } from '../api'
import ErrorBox from '../components/ErrorBox.vue'
import SourceNote from '../components/SourceNote.vue'
import { formatAsOf, formatBRL, formatFraction, formatPoints, trendClass } from '../lib/format'
import { usePublishScreen } from '../lib/screen'

const board = useQuery({ queryKey: ['scoreboard'], queryFn: fetchScoreboard })
const b = computed(() => board.data.value)
const EXP = { alta: '▲ alta', baixa: '▼ baixa', neutra: '— neutra' }
const DEC: Record<string, string> = { aprovado: 'Aprovada', recusado: 'Recusada', ajustado: 'Ajustada', '': 'Avulsa' }

usePublishScreen(() => ({ view: 'scoreboard', hit_rate: b.value?.hit_rate ?? null }))
</script>

<template>
  <ErrorBox :error="board.error.value" />
  <p class="max-w-prose text-sm text-muted">
    Cada tese é registrada com o preço do dia. Acerto = o preço andou na direção esperada desde então. Teses que você
    recusou também contam: assim dá para ver se recusar foi a decisão certa.
  </p>

  <p v-if="board.isPending.value" class="py-20 text-center text-muted">Carregando placar…</p>
  <template v-else-if="b">
    <dl class="mt-6 grid grid-cols-3 gap-px border-y border-rule bg-rule">
      <div class="bg-panel py-4 pr-4"><dt class="text-sm text-muted">Taxa de acerto</dt><dd class="num mt-1 text-3xl text-accent">{{ formatFraction(b.hit_rate) }}</dd></div>
      <div class="bg-panel p-4"><dt class="text-sm text-muted">Acertos</dt><dd class="num mt-1 text-3xl">{{ b.hits }}</dd></div>
      <div class="bg-panel p-4"><dt class="text-sm text-muted">Teses avaliadas</dt><dd class="num mt-1 text-3xl">{{ b.scored }}</dd></div>
    </dl>

    <div v-if="b.rows.length" class="mt-8 overflow-x-auto">
      <table class="w-full min-w-[820px] text-sm">
        <caption class="sr-only">Teses registradas com retorno desde a entrada</caption>
        <thead>
          <tr class="border-b border-rule text-muted">
            <th scope="col" class="py-2 text-left font-normal">Data</th>
            <th scope="col" class="py-2 text-left font-normal">Ação</th>
            <th scope="col" class="py-2 text-left font-normal">Esperado</th>
            <th scope="col" class="py-2 text-left font-normal">Sua decisão</th>
            <th scope="col" class="py-2 text-right font-normal">Entrada</th>
            <th scope="col" class="py-2 text-right font-normal">Atual</th>
            <th scope="col" class="py-2 text-right font-normal">Retorno</th>
            <th scope="col" class="py-2 text-right font-normal">Resultado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in b.rows" :key="i" class="border-b border-rule/60" :title="r.summary">
            <td class="num py-2 text-muted">{{ formatAsOf(r.created_at).split(' ')[0] }}</td>
            <th scope="row" class="num py-2 text-left font-normal"><RouterLink :to="`/acoes/${r.ticker}`" class="hover:text-accent">{{ r.ticker }}</RouterLink></th>
            <td class="py-2">{{ EXP[r.expectation] }}</td>
            <td class="py-2 text-muted">{{ DEC[r.decision] ?? r.decision }}</td>
            <td class="num py-2 text-right">{{ formatBRL(r.entry_price) }}</td>
            <td class="num py-2 text-right">{{ formatBRL(r.current_price) }}</td>
            <td class="num py-2 text-right" :class="trendClass(r.return_pct)">{{ r.return_pct === null ? '—' : formatPoints(r.return_pct * 100) }}</td>
            <td class="py-2 text-right" :class="r.hit === null ? 'text-muted' : r.hit ? 'text-up' : 'text-down'">
              {{ r.hit === null ? 'Não avaliada' : r.hit ? '✓ Acertou' : '✗ Errou' }}
            </td>
          </tr>
        </tbody>
      </table>
      <SourceNote class="mt-2" label="Preço atual" :source="b.rows.find((r) => r.price_source)?.price_source" :at="b.rows.find((r) => r.price_fetched_at)?.price_fetched_at" />
    </div>
    <p v-else class="mt-6 rounded border border-dashed border-rule py-12 text-center text-sm text-muted">
      Nenhuma tese ainda. Elas entram quando você decide os itens de uma proposta.
    </p>
  </template>
</template>
