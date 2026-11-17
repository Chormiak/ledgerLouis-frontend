<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { fetchPortfolio, fetchProposal } from '../api'
import ErrorBox from '../components/ErrorBox.vue'
import KindTag from '../components/KindTag.vue'
import ProposalItemCard from '../components/ProposalItemCard.vue'
import { formatAsOf, formatFraction } from '../lib/format'
import { usePublishScreen } from '../lib/screen'

const props = defineProps<{ id: string }>()
const proposal = useQuery({ queryKey: computed(() => ['proposal', props.id]), queryFn: () => fetchProposal(props.id) })
const portfolio = useQuery({ queryKey: ['portfolio'], queryFn: fetchPortfolio })

const p = computed(() => proposal.data.value)
const pending = computed(() => p.value?.items.filter((i) => i.decision === 'pendente').length ?? 0)

// antes x depois: peso atual na carteira contra o peso proposto
const rows = computed(() => {
  const now = new Map((portfolio.data.value?.positions ?? []).map((x) => [x.ticker, x.weight ?? 0]))
  return (p.value?.items ?? []).map((i) => ({ ticker: i.ticker, before: now.get(i.ticker) ?? 0, after: i.target_weight }))
})
const max = computed(() => Math.max(0.01, ...rows.value.flatMap((r) => [r.before, r.after])))

usePublishScreen(() => ({ view: 'proposal', proposal_id: props.id, period: p.value?.period, pending: pending.value }))
</script>

<template>
  <ErrorBox :error="proposal.error.value" />
  <RouterLink to="/carteira" class="text-sm text-muted hover:text-paper">Carteira</RouterLink>

  <p v-if="proposal.isPending.value" class="py-20 text-center text-muted">Carregando proposta…</p>
  <template v-else-if="p">
    <header class="mt-2 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="font-display text-3xl font-medium">Proposta de {{ p.period }}</h1>
        <p class="text-sm text-muted">Criada em <span class="num">{{ formatAsOf(p.created_at) }}</span></p>
      </div>
      <p class="text-sm" role="status">
        <span v-if="pending" class="text-accent">{{ pending }} de {{ p.items.length }} itens esperando sua decisão</span>
        <span v-else class="text-up">Todos os itens decididos e registrados no placar</span>
      </p>
    </header>

    <section class="mt-6 rounded border border-rule p-4" aria-labelledby="sum-title">
      <h2 id="sum-title" class="mb-2 flex items-center gap-2 text-sm text-muted">Resumo do Claude <KindTag kind="ia" /></h2>
      <p class="max-w-prose whitespace-pre-line">{{ p.summary }}</p>
      <p class="mt-3 text-xs text-muted">Proposta, não recomendação garantida: a decisão de cada item é sua. O LedgerLouis não executa ordens.</p>
    </section>

    <section class="mt-10" aria-labelledby="ba-title">
      <h2 id="ba-title" class="font-display mb-3 text-xl font-medium">Peso atual e proposto</h2>
      <ul class="space-y-3">
        <li v-for="r in rows" :key="r.ticker" class="grid grid-cols-[5rem_minmax(0,1fr)_6.5rem] items-center gap-3 text-sm">
          <span class="num">{{ r.ticker }}</span>
          <span class="space-y-1" aria-hidden="true">
            <span class="block h-2 rounded-sm bg-muted/50" :style="{ width: `${(r.before / max) * 100}%` }" />
            <span class="block h-2 rounded-sm bg-accent" :style="{ width: `${(r.after / max) * 100}%` }" />
          </span>
          <span class="num text-right text-xs"><span class="text-muted">{{ formatFraction(r.before) }}</span> → {{ formatFraction(r.after) }}</span>
        </li>
      </ul>
      <p class="mt-2 flex gap-4 text-xs text-muted">
        <span class="flex items-center gap-1"><span class="h-2 w-4 rounded-sm bg-muted/50" /> atual</span>
        <span class="flex items-center gap-1"><span class="h-2 w-4 rounded-sm bg-accent" /> proposto</span>
        <span>Soma dos pesos sem os itens recusados: <span class="num text-paper">{{ formatFraction(p.approved_weight) }}</span></span>
      </p>
    </section>

    <section class="mt-10 space-y-4" aria-labelledby="items-title">
      <h2 id="items-title" class="font-display text-xl font-medium">Itens para revisar</h2>
      <ProposalItemCard v-for="i in p.items" :key="i.id" :item="i" :proposal-id="p.id" />
    </section>
  </template>
</template>
