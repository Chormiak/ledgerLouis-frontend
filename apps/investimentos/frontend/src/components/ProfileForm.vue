<script setup lang="ts">
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { reactive, watch } from 'vue'
import { saveProfile, type Profile } from '../api'

const props = defineProps<{ profile: Profile }>()
const qc = useQueryClient()

// formulário em unidades humanas (%), convertido para fração ao salvar
const form = reactive({ horizon: '', risk: '', contribution: '', avoid: '', notes: '', drop: '', asset: '', sector: '' })
watch(
  () => props.profile,
  (p) =>
    Object.assign(form, {
      horizon: p.horizon_years?.toString() ?? '',
      risk: p.risk_tolerance,
      contribution: p.monthly_contribution?.toString() ?? '',
      avoid: p.avoid_sectors.join(', '),
      notes: p.notes,
      drop: String(p.alert_daily_drop_pct),
      asset: String(Math.round(p.alert_max_asset_weight * 1000) / 10),
      sector: String(Math.round(p.alert_max_sector_weight * 1000) / 10),
    }),
  { immediate: true },
)

const save = useMutation({
  mutationFn: () =>
    saveProfile({
      horizon_years: form.horizon === '' ? null : Number(form.horizon),
      risk_tolerance: form.risk as Profile['risk_tolerance'],
      monthly_contribution: form.contribution === '' ? null : Number(form.contribution.replace(',', '.')),
      avoid_sectors: form.avoid.split(',').map((s) => s.trim()).filter(Boolean),
      notes: form.notes,
      alert_daily_drop_pct: Number(form.drop.replace(',', '.')),
      alert_max_asset_weight: Number(form.asset.replace(',', '.')) / 100,
      alert_max_sector_weight: Number(form.sector.replace(',', '.')) / 100,
    }),
  onSuccess: () => {
    qc.invalidateQueries({ queryKey: ['portfolio'] })
    qc.invalidateQueries({ queryKey: ['profile'] })
  },
})

const field = 'mt-1 w-full rounded border border-rule bg-panel px-2 py-1.5 text-paper'
const MISSING: Record<string, string> = { horizon_years: 'horizonte', risk_tolerance: 'tolerância a risco', monthly_contribution: 'aporte mensal' }
</script>

<template>
  <form class="grid gap-4 sm:grid-cols-3" @submit.prevent="save.mutate()">
    <p v-if="profile.missing.length" class="rounded border border-accent/50 px-3 py-2 text-sm sm:col-span-3">
      Falta preencher: {{ profile.missing.map((m) => MISSING[m]).join(', ') }}. Sem isso o Gemini pergunta antes de propor.
    </p>
    <label class="text-sm text-muted">
      Horizonte (anos)
      <input v-model="form.horizon" type="number" min="0" max="100" inputmode="numeric" :class="field" />
    </label>
    <label class="text-sm text-muted">
      Tolerância a risco
      <select v-model="form.risk" :class="field">
        <option value="">Não informado</option>
        <option value="conservador">Conservador</option>
        <option value="moderado">Moderado</option>
        <option value="arrojado">Arrojado</option>
      </select>
    </label>
    <label class="text-sm text-muted">
      Aporte mensal (R$)
      <input v-model="form.contribution" inputmode="decimal" :class="field" />
    </label>
    <label class="text-sm text-muted sm:col-span-3">
      Setores a evitar (separados por vírgula)
      <input v-model="form.avoid" :class="field" />
    </label>
    <label class="text-sm text-muted sm:col-span-3">
      Observações para o Gemini
      <textarea v-model="form.notes" rows="2" :class="field" />
    </label>
    <fieldset class="grid gap-4 sm:col-span-3 sm:grid-cols-3">
      <legend class="mb-2 text-sm text-paper">Limiares dos alertas</legend>
      <label class="text-sm text-muted">Queda no dia a partir de (%)<input v-model="form.drop" inputmode="decimal" :class="field" /></label>
      <label class="text-sm text-muted">Ativo acima de (% da carteira)<input v-model="form.asset" inputmode="decimal" :class="field" /></label>
      <label class="text-sm text-muted">Setor acima de (% da carteira)<input v-model="form.sector" inputmode="decimal" :class="field" /></label>
    </fieldset>
    <div class="flex items-center gap-3 sm:col-span-3">
      <button type="submit" class="rounded bg-accent px-4 py-1.5 font-medium text-ink disabled:opacity-60" :disabled="save.isPending.value">
        Salvar perfil
      </button>
      <span v-if="save.isSuccess.value" class="text-sm text-up" role="status">Perfil salvo</span>
      <span v-if="save.error.value" class="text-sm text-down" role="alert">{{ save.error.value.message }}</span>
    </div>
  </form>
</template>
