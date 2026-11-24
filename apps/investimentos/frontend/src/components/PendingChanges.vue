<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { vAutoAnimate } from '@formkit/auto-animate/vue'
import { decideChange, fetchPendingChanges, type PendingChange } from '../api'
import { formatBRL } from '../lib/format'

const qc = useQueryClient()
const changes = useQuery({ queryKey: ['pending-changes'], queryFn: fetchPendingChanges, refetchInterval: 10_000 })
const decide = useMutation({
  mutationFn: ({ id, verb }: { id: string; verb: 'apply' | 'reject' }) => decideChange(id, verb),
  onSuccess: () => ['pending-changes', 'portfolio', 'profile', 'alerts'].forEach((k) => qc.invalidateQueries({ queryKey: [k] })),
})

const PROFILE_LABEL: Record<string, string> = {
  horizon_years: 'horizonte (anos)', risk_tolerance: 'tolerância a risco', monthly_contribution: 'aporte mensal',
  avoid_sectors: 'setores a evitar', notes: 'observações', alert_daily_drop_pct: 'alerta de queda (%)',
  alert_max_asset_weight: 'limite por ativo', alert_max_sector_weight: 'limite por setor',
}

function describe(c: PendingChange): string {
  const p = c.payload as Record<string, string | null>
  if (c.kind === 'holding') {
    if (Number(p.quantity) === 0) return `Remover ${p.ticker} da carteira`
    const avg = p.avg_price ? `, preço médio ${formatBRL(Number(p.avg_price))}` : ''
    return `${p.ticker}: ${Number(p.quantity).toLocaleString('pt-BR')} ações${avg}`
  }
  return Object.entries(c.payload).map(([k, v]) => `${PROFILE_LABEL[k] ?? k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('; ')
}
</script>

<template>
  <section v-if="changes.data.value?.length" v-auto-animate aria-label="Sugestões do Claude esperando você" class="space-y-2">
    <article v-for="c in changes.data.value" :key="c.id" class="rounded-lg border border-accent/40 bg-raise p-3 text-sm">
      <p class="text-xs text-accent">Sugestão do Claude, {{ c.kind === 'holding' ? 'carteira' : 'perfil' }}</p>
      <p class="mt-1 text-paper">{{ describe(c) }}</p>
      <p class="mt-1 text-xs text-muted">{{ c.reason }}</p>
      <div class="mt-2 flex gap-2">
        <button type="button" class="rounded-md bg-accent px-3 py-1 text-xs font-medium text-ink disabled:opacity-60" :disabled="decide.isPending.value" @click="decide.mutate({ id: c.id, verb: 'apply' })">
          Aplicar
        </button>
        <button type="button" class="rounded-md border border-rule px-3 py-1 text-xs text-muted hover:text-paper disabled:opacity-60" :disabled="decide.isPending.value" @click="decide.mutate({ id: c.id, verb: 'reject' })">
          Recusar
        </button>
      </div>
    </article>
    <p v-if="decide.error.value" role="alert" class="text-xs text-down">{{ decide.error.value.message }}</p>
  </section>
</template>
