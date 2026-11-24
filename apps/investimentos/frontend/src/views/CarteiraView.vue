<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, reactive } from 'vue'
import { deleteHolding, fetchAssets, fetchPortfolio, fetchProposals, saveHolding } from '../api'
import ErrorBox from '../components/ErrorBox.vue'
import ExposureDonut from '../components/ExposureDonut.vue'
import ProfileForm from '../components/ProfileForm.vue'
import SourceNote from '../components/SourceNote.vue'
import { formatBRL, formatFraction, formatPoints, trendArrow, trendClass } from '../lib/format'
import { usePublishScreen } from '../lib/screen'

const qc = useQueryClient()
const portfolio = useQuery({ queryKey: ['portfolio'], queryFn: fetchPortfolio })
const assets = useQuery({ queryKey: ['assets'], queryFn: fetchAssets })
const proposals = useQuery({ queryKey: ['proposals'], queryFn: fetchProposals })

const p = computed(() => portfolio.data.value)
const latest = computed(() => proposals.data.value?.[0])
const form = reactive({ ticker: '', quantity: '', avg: '' })

const refresh = () => qc.invalidateQueries({ queryKey: ['portfolio'] })
const add = useMutation({
  mutationFn: () => saveHolding(form.ticker.trim().toUpperCase(), form.quantity.replace(',', '.'), form.avg.replace(',', '.')),
  onSuccess: () => {
    Object.assign(form, { ticker: '', quantity: '', avg: '' })
    refresh()
  },
})
const remove = useMutation({ mutationFn: deleteHolding, onSuccess: refresh })

const STATUS = { rascunho: 'Aguardando sua revisão', em_revisao: 'Revisão em andamento', concluida: 'Revisada' }
const field = 'mt-1 w-full rounded border border-rule bg-panel px-2 py-1.5 text-paper'

usePublishScreen(() => ({ view: 'portfolio', tickers: p.value?.positions.map((x) => x.ticker) ?? [] }))
</script>

<template>
  <ErrorBox :error="portfolio.error.value" />

  <section v-if="latest" class="mb-10 flex flex-wrap items-center justify-between gap-3 rounded border border-rule bg-panel px-4 py-3">
    <p>
      <span class="text-muted">Proposta de {{ latest.period }}:</span> {{ STATUS[latest.status] }}
      <span class="text-muted">({{ latest.count }} itens)</span>
    </p>
    <RouterLink :to="`/carteira/propostas/${latest.id}`" class="rounded bg-accent px-3 py-1 font-medium text-ink">Abrir revisão</RouterLink>
  </section>

  <section aria-labelledby="pos-title">
    <h2 id="pos-title" class="font-display mb-3 text-xl font-medium">Posições</h2>
    <p v-if="p && !p.positions.length" class="mb-4 text-sm text-muted">Nenhuma posição ainda. Adicione abaixo o que você já tem.</p>
    <div v-if="p?.positions.length" class="overflow-x-auto">
      <table class="w-full min-w-[760px] text-sm">
        <caption class="sr-only">Posições da carteira com peso e ganho sobre o preço médio</caption>
        <thead>
          <tr class="border-b border-rule text-muted">
            <th scope="col" class="py-2 text-left font-normal">Ação</th>
            <th scope="col" class="py-2 text-right font-normal">Quantidade</th>
            <th scope="col" class="py-2 text-right font-normal">Preço médio</th>
            <th scope="col" class="py-2 text-right font-normal">Preço</th>
            <th scope="col" class="py-2 text-right font-normal">Dia</th>
            <th scope="col" class="py-2 text-right font-normal">Valor</th>
            <th scope="col" class="py-2 text-right font-normal">Peso</th>
            <th scope="col" class="py-2 text-right font-normal">Ganho</th>
            <th scope="col"><span class="sr-only">Ações</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="x in p.positions" :key="x.ticker" class="border-b border-rule/60">
            <th scope="row" class="py-2 text-left font-normal">
              <RouterLink :to="`/acoes/${x.ticker}`" class="num font-medium text-paper underline decoration-rule underline-offset-4 hover:decoration-accent">{{ x.ticker }}</RouterLink> <span class="text-muted">{{ x.sector }}</span>
            </th>
            <td class="num py-2 text-right">{{ x.quantity.toLocaleString('pt-BR') }}</td>
            <td class="num py-2 text-right">{{ formatBRL(x.avg_price) }}</td>
            <td class="num py-2 text-right">{{ formatBRL(x.price) }}</td>
            <td class="num py-2 text-right" :class="trendClass(x.change_pct)">
              <span aria-hidden="true" class="mr-1 text-[10px]">{{ trendArrow(x.change_pct) }}</span>{{ formatPoints(x.change_pct) }}
            </td>
            <td class="num py-2 text-right">{{ formatBRL(x.value) }}</td>
            <td class="num py-2 text-right">{{ formatFraction(x.weight) }}</td>
            <td class="num py-2 text-right" :class="trendClass(x.gain_pct)">{{ x.gain_pct === null ? '—' : formatPoints(x.gain_pct * 100) }}</td>
            <td class="py-2 text-right">
              <button type="button" class="text-xs text-muted hover:text-down" :aria-label="`Remover ${x.ticker}`" @click="remove.mutate(x.ticker)">Remover</button>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <th scope="row" colspan="5" class="py-2 text-left font-normal text-muted">Total</th>
            <td class="num py-2 text-right text-paper">{{ formatBRL(p.total) }}</td>
            <td colspan="3" />
          </tr>
        </tfoot>
      </table>
      <p v-if="p.unpriced.length" class="mt-2 text-xs text-muted">Sem cotação, fora dos pesos: {{ p.unpriced.join(', ') }}.</p>
      <SourceNote class="mt-1" label="Cotações" :source="p.positions.find((x) => x.source)?.source" :at="p.positions.find((x) => x.fetched_at)?.fetched_at" />
    </div>

    <form class="mt-6 grid gap-3 sm:grid-cols-[1fr_1fr_1fr_auto] sm:items-end" @submit.prevent="add.mutate()">
      <label class="text-sm text-muted">
        Ação
        <input v-model="form.ticker" list="tickers" required placeholder="PETR4" autocapitalize="characters" :class="field" />
        <datalist id="tickers"><option v-for="a in assets.data.value ?? []" :key="a.ticker" :value="a.ticker">{{ a.name }}</option></datalist>
      </label>
      <label class="text-sm text-muted">Quantidade<input v-model="form.quantity" required inputmode="decimal" :class="field" /></label>
      <label class="text-sm text-muted">Preço médio (opcional)<input v-model="form.avg" inputmode="decimal" :class="field" /></label>
      <button type="submit" class="rounded border border-accent px-4 py-1.5 text-accent hover:bg-accent hover:text-ink">Adicionar ou atualizar</button>
      <p v-if="add.error.value" class="text-sm text-down sm:col-span-4" role="alert">
        {{ add.error.value.message.includes('404') ? 'Essa ação não está na base. Rode sync_market ou confira o ticker.' : add.error.value.message }}
      </p>
    </form>
  </section>

  <section v-if="p && Object.keys(p.exposure.sector).length" class="mt-12" aria-labelledby="exp-title">
    <h2 id="exp-title" class="font-display mb-3 text-xl font-medium">Exposição por setor</h2>
    <ExposureDonut :exposure="p.exposure.sector" />
  </section>

  <section v-if="p" class="mt-12" aria-labelledby="profile-title">
    <h2 id="profile-title" class="font-display mb-1 text-xl font-medium">Seu perfil</h2>
    <p class="mb-4 text-sm text-muted">O Gemini lê isto antes de montar a proposta. Nada aqui é preenchido por ele.</p>
    <ProfileForm :profile="p.profile" />
  </section>
</template>
