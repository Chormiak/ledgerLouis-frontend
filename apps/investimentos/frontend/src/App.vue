<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchAlerts, fetchAssets, fetchGroups, fetchMacro } from './api'
import ChatPanel from './components/ChatPanel.vue'
import Watchlist from './components/Watchlist.vue'
import { useScreenCommands } from './lib/screenCommands'

const route = useRoute()
const router = useRouter()
const groups = useQuery({ queryKey: ['groups'], queryFn: fetchGroups })
const assets = useQuery({ queryKey: ['assets'], queryFn: fetchAssets })
const macro = useQuery({ queryKey: ['macro'], queryFn: fetchMacro })
const alerts = useQuery({ queryKey: ['alerts'], queryFn: fetchAlerts, refetchInterval: 5 * 60_000 })
const unseen = computed(() => alerts.data.value?.filter((a) => !a.seen).length ?? 0)
const { notice } = useScreenCommands()

const chatOpen = ref(false) // gaveta do chat em telas menores
watch(() => route.fullPath, () => (chatOpen.value = false))

function go(e: Event) {
  const value = (e.target as HTMLSelectElement).value
  if (value) router.push(value)
}

const links = [
  { to: '/', label: 'Visão geral' },
  { to: '/grupos', label: 'Setores' },
  { to: '/mercado-eua', label: 'Mercado EUA' },
  { to: '/carteira', label: 'Carteira' },
  { to: '/alertas', label: 'Alertas' },
  { to: '/placar', label: 'Placar' },
]

const tape = computed(() =>
  (macro.data.value ?? []).map((p) => ({
    code: p.code,
    name: p.name.replace(' (venda)', ''),
    value: p.unit === 'R$' ? `R$ ${p.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}` : `${p.value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}%`,
  })),
)
</script>

<template>
  <div class="min-h-screen">
    <header class="sticky top-0 z-20 border-b border-rule bg-ink/95 backdrop-blur">
      <div class="flex flex-wrap items-center gap-x-6 gap-y-3 px-4 py-3 lg:flex-nowrap">
        <RouterLink to="/" class="font-display text-2xl font-bold tracking-tight">Ledger<span class="text-accent">Louis</span></RouterLink>

        <nav aria-label="Principal" class="flex gap-1 overflow-x-auto text-sm">
          <RouterLink
            v-for="l in links"
            :key="l.to"
            :to="l.to"
            class="shrink-0 rounded-lg px-3 py-1.5 text-muted hover:bg-raise hover:text-paper"
            :active-class="l.to === '/' ? '' : '!bg-raise !text-paper ring-1 ring-rule'"
            exact-active-class="!bg-raise !text-paper ring-1 ring-rule"
          >
            {{ l.label }}
            <span v-if="l.to === '/alertas' && unseen" class="num ml-1 rounded-full bg-down px-1.5 text-[11px] text-ink">
              {{ unseen }}<span class="sr-only"> não vistos</span>
            </span>
          </RouterLink>
        </nav>

        <ul aria-label="Indicadores" class="hidden flex-1 items-center justify-end gap-5 overflow-hidden text-xs xl:flex">
          <li v-for="t in tape" :key="t.code" class="flex shrink-0 items-baseline gap-2 border-l border-rule pl-5 first:border-0">
            <span class="text-muted">{{ t.name }}</span><span class="num text-paper">{{ t.value }}</span>
          </li>
        </ul>

        <label class="ml-auto flex items-center xl:ml-0">
          <span class="sr-only">Ir para ação, setor ou nicho</span>
          <select
            class="w-48 rounded-lg border border-rule bg-panel px-2 py-1.5 text-sm text-paper"
            :value="route.path.startsWith('/grupos/') || route.path.startsWith('/acoes/') ? route.path : ''"
            @change="go"
          >
            <option value="">Buscar ação ou setor</option>
            <optgroup v-if="assets.data.value?.length" label="Ações">
              <option v-for="a in assets.data.value" :key="a.ticker" :value="`/acoes/${a.ticker}`">{{ a.ticker }} {{ a.name }}</option>
            </optgroup>
            <optgroup v-if="groups.data.value?.niches.length" label="Nichos">
              <option v-for="g in groups.data.value.niches" :key="g.slug" :value="`/grupos/niche/${g.slug}`">{{ g.name }}</option>
            </optgroup>
            <optgroup v-if="groups.data.value?.sectors.length" label="Setores">
              <option v-for="g in groups.data.value.sectors" :key="g.slug" :value="`/grupos/sector/${g.slug}`">{{ g.name }}</option>
            </optgroup>
          </select>
        </label>
      </div>
    </header>

    <div class="grid gap-4 p-4 lg:grid-cols-[15rem_minmax(0,1fr)] 2xl:grid-cols-[15rem_minmax(0,1fr)_24rem]">
      <aside class="hidden rounded-xl border border-rule bg-panel p-2 lg:sticky lg:top-[4.5rem] lg:block lg:h-[calc(100vh-5.5rem)] lg:overflow-y-auto">
        <Watchlist />
      </aside>

      <main class="min-w-0 rounded-xl border border-rule bg-panel p-4 sm:p-6">
        <RouterView />
      </main>

      <!-- o painel do Claude fica fixo em telas largas; nas menores vira uma gaveta -->
      <aside
        class="fixed inset-0 z-30 bg-panel 2xl:sticky 2xl:inset-auto 2xl:top-[4.5rem] 2xl:z-auto 2xl:block 2xl:h-[calc(100vh-5.5rem)] 2xl:rounded-xl 2xl:border 2xl:border-rule"
        :class="chatOpen ? 'block' : 'hidden'"
      >
        <ChatPanel>
          <template #actions>
            <button type="button" class="text-sm text-muted hover:text-paper 2xl:hidden" @click="chatOpen = false">Fechar</button>
          </template>
        </ChatPanel>
      </aside>
    </div>

    <button
      v-if="!chatOpen"
      type="button"
      class="fixed right-4 bottom-4 z-20 rounded-full bg-accent px-5 py-3 font-medium text-ink shadow-lg 2xl:hidden"
      @click="chatOpen = true"
    >
      Perguntar ao Claude
    </button>

    <div
      v-if="notice"
      role="status"
      class="fixed bottom-20 left-1/2 z-40 w-[min(28rem,calc(100vw-2rem))] -translate-x-1/2 rounded-lg border border-accent/50 bg-raise px-4 py-2 text-sm"
    >
      <span class="text-accent">O Claude abriu esta tela.</span> <span class="text-muted">{{ notice.reason }}</span>
    </div>
  </div>
</template>
