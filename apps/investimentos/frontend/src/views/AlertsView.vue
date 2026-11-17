<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { fetchAlerts, markAlertSeen } from '../api'
import ErrorBox from '../components/ErrorBox.vue'
import { usePublishScreen } from '../lib/screen'

const qc = useQueryClient()
const alerts = useQuery({ queryKey: ['alerts'], queryFn: fetchAlerts })
const seen = useMutation({ mutationFn: markAlertSeen, onSuccess: () => qc.invalidateQueries({ queryKey: ['alerts'] }) })

const KIND = { queda_forte: 'Queda forte', concentracao_ativo: 'Concentração em um ativo', concentracao_setor: 'Concentração em um setor', fato_relevante: 'Fato relevante' }
const day = (iso: string) => iso.split('-').reverse().join('/')

usePublishScreen(() => ({ view: 'alerts', unseen: alerts.data.value?.filter((a) => !a.seen).length ?? 0 }))
</script>

<template>
  <ErrorBox :error="alerts.error.value" />
  <p class="max-w-prose text-sm text-muted">
    Gatilhos simples, sem IA, rodam a cada <code class="num">sync_market</code>. Para uma explicação, peça ao Claude
    o atalho <span class="text-paper">explicar_alertas</span>. Os limiares ficam no seu perfil, na Carteira.
  </p>

  <p v-if="alerts.isPending.value" class="py-20 text-center text-muted">Carregando alertas…</p>
  <ol v-else-if="alerts.data.value?.length" class="mt-6 divide-y divide-rule/60 border-y border-rule">
    <li v-for="a in alerts.data.value" :key="a.id" class="flex flex-wrap items-start justify-between gap-3 py-3" :class="a.seen && 'opacity-60'">
      <div>
        <p class="text-xs text-muted"><span class="num">{{ day(a.created_on) }}</span>, {{ KIND[a.kind] }}</p>
        <p class="mt-1">
          <a v-if="a.detail.url" :href="a.detail.url" target="_blank" rel="noopener noreferrer" class="underline decoration-rule underline-offset-4 hover:decoration-accent">{{ a.title }}</a>
          <span v-else>{{ a.title }}</span>
        </p>
      </div>
      <button v-if="!a.seen" type="button" class="text-sm text-muted hover:text-paper" @click="seen.mutate(a.id)">Marcar como visto</button>
      <span v-else class="text-xs text-muted">Visto</span>
    </li>
  </ol>
  <p v-else class="mt-6 rounded border border-dashed border-rule py-12 text-center text-sm text-muted">Nenhum alerta. Os gatilhos olham só as ações da sua carteira.</p>
</template>
