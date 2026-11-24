<script setup lang="ts">
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { ref } from 'vue'
import { decide, type Decision, type ProposalItem } from '../api'
import { formatBRL, formatFraction } from '../lib/format'
import KindTag from './KindTag.vue'

const props = defineProps<{ item: ProposalItem; proposalId: string }>()
const qc = useQueryClient()

const comment = ref(props.item.comment)
const adjusting = ref(props.item.decision === 'ajustado')
const newWeight = ref(props.item.adjusted_weight === null ? '' : String(Math.round(props.item.adjusted_weight * 1000) / 10))

const mutation = useMutation({
  mutationFn: (d: Decision) =>
    decide(props.item.id, d, d === 'ajustado' ? Number(newWeight.value.replace(',', '.')) / 100 : null, comment.value),
  onSuccess: () => {
    qc.invalidateQueries({ queryKey: ['proposal', String(props.proposalId)] })
    qc.invalidateQueries({ queryKey: ['proposals'] })
    qc.invalidateQueries({ queryKey: ['scoreboard'] })
  },
})

const ACTION = { entrar: 'Entrar', sair: 'Sair', aumentar: 'Aumentar', reduzir: 'Reduzir', manter: 'Manter' }
const DECISION = { pendente: 'Pendente', aprovado: 'Aprovado', recusado: 'Recusado', ajustado: 'Ajustado' }
const decisionClass = { pendente: 'text-muted', aprovado: 'text-up', recusado: 'text-down', ajustado: 'text-accent' }
const priceMove = (i: ProposalItem) =>
  i.price_at_proposal && i.current_price ? (i.current_price / i.price_at_proposal - 1) * 100 : null
</script>

<template>
  <article class="rounded-xl border border-rule bg-raise p-4" :aria-labelledby="`item-${item.id}`">
    <header class="flex flex-wrap items-baseline justify-between gap-2">
      <h3 :id="`item-${item.id}`" class="text-lg">
        <span class="mr-2 rounded bg-ink px-2 py-0.5 text-sm text-accent">{{ ACTION[item.action] }}</span>
        <RouterLink :to="`/acoes/${item.ticker}`" class="num underline decoration-rule underline-offset-4 hover:decoration-accent">{{ item.ticker }}</RouterLink> <span class="text-muted">{{ item.name }}</span>
      </h3>
      <p class="num text-sm">
        peso alvo <span class="text-paper">{{ formatFraction(item.target_weight) }}</span>
        <span v-if="item.decision === 'ajustado'" class="text-accent"> → {{ formatFraction(item.adjusted_weight) }}</span>
      </p>
    </header>

    <dl class="mt-3 space-y-3 text-sm">
      <div>
        <dt class="flex items-center gap-2 text-muted">Tese <KindTag kind="ia" /></dt>
        <dd class="mt-1 max-w-prose">{{ item.thesis }}</dd>
      </div>
      <div>
        <dt class="flex items-center gap-2 text-muted">Riscos <KindTag kind="ia" /></dt>
        <dd class="mt-1 max-w-prose">{{ item.risks }}</dd>
      </div>
      <div>
        <dt class="flex items-center gap-2 text-muted">O que invalidaria a tese <KindTag kind="ia" /></dt>
        <dd class="mt-1 max-w-prose">{{ item.invalidation }}</dd>
      </div>
      <div>
        <dt class="flex items-center gap-2 text-muted">Preço <KindTag kind="fato" /></dt>
        <dd class="num mt-1">
          {{ formatBRL(item.price_at_proposal) }} na proposta, {{ formatBRL(item.current_price) }} agora
          <span v-if="priceMove(item) !== null" class="text-muted">({{ priceMove(item)!.toLocaleString('pt-BR', { maximumFractionDigits: 1, signDisplay: 'always' }) }}%)</span>
        </dd>
      </div>
      <div>
        <dt class="text-muted">Fontes citadas</dt>
        <dd class="mt-1"><ul class="list-inside list-disc text-muted"><li v-for="src in item.sources" :key="src">{{ src }}</li></ul></dd>
      </div>
    </dl>

    <form class="mt-4 border-t border-rule pt-4" @submit.prevent>
      <p class="mb-2 text-sm">
        Sua decisão: <span :class="decisionClass[item.decision]">{{ DECISION[item.decision] }}</span>
      </p>
      <label class="block text-sm text-muted">
        Comentário (opcional)
        <textarea v-model="comment" rows="2" class="mt-1 w-full rounded border border-rule bg-ink px-2 py-1.5 text-paper" />
      </label>
      <div class="mt-3 flex flex-wrap items-end gap-2">
        <button type="button" class="rounded border border-up px-3 py-1.5 text-up hover:bg-up hover:text-ink" :disabled="mutation.isPending.value" @click="mutation.mutate('aprovado')">Aprovar</button>
        <button type="button" class="rounded border border-down px-3 py-1.5 text-down hover:bg-down hover:text-ink" :disabled="mutation.isPending.value" @click="mutation.mutate('recusado')">Recusar</button>
        <button v-if="!adjusting" type="button" class="rounded border border-accent px-3 py-1.5 text-accent" @click="adjusting = true">Ajustar peso</button>
        <template v-else>
          <label class="text-sm text-muted">
            Novo peso (%)
            <input v-model="newWeight" inputmode="decimal" class="mt-1 block w-24 rounded border border-rule bg-ink px-2 py-1.5 text-paper" />
          </label>
          <button type="button" class="rounded bg-accent px-3 py-1.5 font-medium text-ink" :disabled="mutation.isPending.value || newWeight === ''" @click="mutation.mutate('ajustado')">Salvar ajuste</button>
        </template>
      </div>
      <p v-if="mutation.error.value" class="mt-2 text-sm text-down" role="alert">{{ mutation.error.value.message }}</p>
    </form>
  </article>
</template>
