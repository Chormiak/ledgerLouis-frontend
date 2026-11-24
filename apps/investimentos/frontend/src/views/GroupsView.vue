<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { fetchGroups } from '../api'
import ErrorBox from '../components/ErrorBox.vue'
import GroupBars from '../components/GroupBars.vue'
import { usePublishScreen } from '../lib/screen'

const groups = useQuery({ queryKey: ['groups'], queryFn: fetchGroups })
usePublishScreen(() => ({ view: 'groups' }))
const scale = computed(() => {
  const all = [...(groups.data.value?.niches ?? []), ...(groups.data.value?.sectors ?? [])]
  return Math.max(1, ...all.map((g) => Math.abs(g.change_pct ?? 0)))
})
</script>

<template>
  <ErrorBox :error="groups.error.value" />
  <p class="max-w-prose text-sm text-muted">
    Variação do dia de cada grupo, ponderada pelo valor de mercado das empresas. Nichos são listas suas e mudam no
    admin do Django; setores vêm da classificação da fonte.
  </p>

  <p v-if="groups.isPending.value" class="py-20 text-center text-muted">Carregando grupos…</p>
  <template v-else-if="groups.data.value">
    <section class="mt-8" aria-labelledby="niches-title">
      <h2 id="niches-title" class="font-display mb-3 text-xl font-medium">Nichos</h2>
      <GroupBars v-if="groups.data.value.niches.length" :groups="groups.data.value.niches" :scale="scale" />
      <p v-else class="text-sm text-muted">
        Nenhum nicho ainda. Rode <code class="num text-paper">python manage.py seed_niches</code> depois do primeiro
        <code class="num text-paper">sync_market</code>.
      </p>
    </section>
    <section class="mt-12" aria-labelledby="sectors-title">
      <h2 id="sectors-title" class="font-display mb-3 text-xl font-medium">Setores</h2>
      <GroupBars :groups="groups.data.value.sectors" :scale="scale" />
    </section>
  </template>
</template>
