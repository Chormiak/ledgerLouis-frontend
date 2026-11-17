<script setup lang="ts">
import type { NewsItem } from '../api'
import { formatAsOf } from '../lib/format'

defineProps<{ items: NewsItem[]; emptyText?: string }>()

const KIND = { fato_relevante: 'Fato relevante', comunicado: 'Comunicado', noticia: 'Notícia' } as const
</script>

<template>
  <ol v-if="items.length" class="divide-y divide-rule/60 border-y border-rule">
    <li v-for="n in items" :key="n.url" class="grid gap-1 py-3 sm:grid-cols-[9rem_minmax(0,1fr)] sm:gap-4">
      <p class="text-xs text-muted">
        <time class="num" :datetime="n.published_at">{{ formatAsOf(n.published_at).split(' ')[0] }}</time>
        <span class="block">{{ n.source }}</span>
      </p>
      <div>
        <a :href="n.url" target="_blank" rel="noopener noreferrer" class="text-paper underline decoration-rule underline-offset-4 hover:decoration-accent">
          {{ n.title }}
        </a>
        <p class="mt-1 flex flex-wrap gap-2 text-xs">
          <span class="rounded border px-1.5" :class="n.kind === 'noticia' ? 'border-rule text-muted' : 'border-accent/60 text-accent'">
            {{ KIND[n.kind] }}
          </span>
          <RouterLink v-for="t in n.tickers" :key="t" :to="`/acoes/${t}`" class="num text-muted hover:text-paper">{{ t }}</RouterLink>
        </p>
      </div>
    </li>
  </ol>
  <p v-else class="text-sm text-muted">
    {{ emptyText ?? 'Sem notícias para este grupo.' }} Rode <code class="num text-paper">python manage.py sync_market --only news</code> e
    cadastre feeds RSS no admin.
  </p>
</template>
