<script setup lang="ts">
import { computed } from 'vue';
import { useTagStore } from '@/stores/tagStore';
import { colorForTag } from '@/utils/tagColor';
import { formatCurrency } from '@/utils/format';
import type { TransactionDto } from '@/services/transactionService';

const props = defineProps<{ transactions: TransactionDto[] }>();

const tagStore = useTagStore();

/** Soma o valor dos lancamentos de saida por tag: e onde o dinheiro vai. */
const ranking = computed(() => {
  const totals = new Map<string, number>();
  for (const transaction of props.transactions) {
    if (transaction.entryType !== 'debit') continue;
    for (const tag of tagStore.transactionTagsMap[transaction.id] ?? []) {
      totals.set(tag.id, (totals.get(tag.id) ?? 0) + transaction.amount);
    }
  }

  const rows = tagStore.tags
    .map((tag) => ({ id: tag.id, name: tag.name, total: totals.get(tag.id) ?? 0, color: colorForTag(tag.id) }))
    .filter((row) => row.total > 0)
    .sort((a, b) => b.total - a.total);

  const grand = rows.reduce((sum, row) => sum + row.total, 0);
  const top = rows[0]?.total ?? 1;
  return rows.map((row) => ({ ...row, share: grand ? Math.round((row.total / grand) * 100) : 0, width: (row.total / top) * 100 }));
});

const grandTotal = computed(() => ranking.value.reduce((sum, row) => sum + row.total, 0));
</script>

<template>
  <section class="card ranking" aria-labelledby="ranking-title">
    <header>
      <h2 id="ranking-title" class="card-title">Para onde vai o dinheiro</h2>
      <p class="card-subtitle">Saídas por tag{{ ranking.length ? ` · ${formatCurrency(grandTotal)}` : '' }}</p>
    </header>

    <p v-if="ranking.length === 0" class="empty-state">Marque saídas com tags para ver o ranking aqui.</p>

    <ol v-else class="rows">
      <li v-for="row in ranking" :key="row.id">
        <button
          type="button"
          class="row"
          :class="{ 'is-active': tagStore.activeTagId === row.id }"
          :aria-pressed="tagStore.activeTagId === row.id"
          :title="`Filtrar o painel por ${row.name}`"
          @click="tagStore.setActiveTag(row.id)"
        >
          <span class="row-name">{{ row.name }}</span>
          <span class="row-value figure">{{ formatCurrency(row.total) }}</span>
          <span class="row-share figure">{{ row.share }}%</span>
          <span class="row-track" aria-hidden="true">
            <span class="row-fill" :style="{ width: `${row.width}%`, background: row.color }" />
          </span>
        </button>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.ranking {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.rows {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto 4ch;
  grid-template-areas:
    'name value share'
    'track track track';
  align-items: baseline;
  gap: 8px var(--space-3);
  margin: 0 calc(var(--space-3) * -1);
  padding: var(--space-3);
  width: calc(100% + var(--space-3) * 2);
  border-radius: var(--radius-md);
  text-align: left;
  transition: background-color var(--duration-fast) ease;
}

.row:hover {
  background: var(--color-surface-3);
}

.row.is-active {
  background: var(--color-primary-soft);
  box-shadow: 0 0 0 1px var(--color-primary-ring) inset;
}

.row-name {
  grid-area: name;
  font-size: var(--text-sm);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-value {
  grid-area: value;
  font-size: var(--text-sm);
}

.row-share {
  grid-area: share;
  font-size: var(--text-xs);
  text-align: right;
  color: var(--color-text-subtle);
}

.row-track {
  grid-area: track;
  height: 4px;
  border-radius: var(--radius-full);
  background: var(--color-surface-3);
  overflow: hidden;
}

.row-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  opacity: 0.9;
  transition: width 700ms var(--ease-out);
}
</style>
