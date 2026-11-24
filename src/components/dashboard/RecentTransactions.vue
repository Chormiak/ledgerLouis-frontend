<script setup lang="ts">
import { computed } from 'vue';
import { ArrowRight } from 'lucide-vue-next';
import BaseButton from '@/components/ui/BaseButton.vue';
import { useTransactionStore } from '@/stores/transactionStore';
import { useTagStore } from '@/stores/tagStore';
import { colorForTag } from '@/utils/tagColor';
import { formatShortDate, formatSignedAmount } from '@/utils/format';
import type { TransactionDto } from '@/services/transactionService';

const props = defineProps<{ transactions?: TransactionDto[] }>();

const transactionStore = useTransactionStore();
const tagStore = useTagStore();

const recent = computed(() => (props.transactions ?? transactionStore.transactions).slice(0, 6));
</script>

<template>
  <section class="card recent" aria-labelledby="recent-title">
    <header class="recent-head">
      <h2 id="recent-title" class="card-title">Últimos lançamentos</h2>
      <BaseButton variant="ghost" size="sm" :to="{ name: 'transactions' }">
        Ver todos
        <ArrowRight :size="15" />
      </BaseButton>
    </header>

    <p v-if="recent.length === 0" class="empty-state">Nenhum lançamento registrado ainda.</p>

    <table v-else class="ledger">
      <thead class="sr-only">
        <tr>
          <th scope="col">Data</th>
          <th scope="col">Descrição</th>
          <th scope="col">Valor</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="transaction in recent" :key="transaction.id">
          <td class="date">{{ formatShortDate(transaction.date) }}</td>
          <th scope="row" class="what">
            <div class="what-inner">
            <span class="what-text">{{ transaction.description }}</span>
            <span class="what-date">{{ formatShortDate(transaction.date) }}</span>
            <span v-if="tagStore.tagsForTransaction(transaction.id).length" class="what-tags">
              <span
                v-for="tag in tagStore.tagsForTransaction(transaction.id)"
                :key="tag.id"
                class="what-tag"
                :style="{ '--tag-color': colorForTag(tag.id) }"
              >
                {{ tag.name }}
              </span>
            </span>
            </div>
          </th>
          <td class="amount figure" :class="transaction.entryType === 'credit' ? 'text-income' : 'text-expense'">
            {{ formatSignedAmount(transaction.amount, transaction.entryType) }}
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.recent {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.recent-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.ledger {
  width: 100%;
}

.ledger td,
.ledger th {
  padding: var(--space-3) var(--space-2);
  border-top: 1px solid var(--color-border);
  text-align: left;
  vertical-align: middle;
}

.date {
  width: 7ch;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: capitalize;
  white-space: nowrap;
  color: var(--color-text-subtle);
}

.what {
  font-weight: 500;
}

.what-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px var(--space-3);
}

.what-date {
  display: none;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-text-subtle);
}

@media (max-width: 559px) {
  .date {
    display: none;
  }

  .what-date {
    display: inline;
  }
}

.what-text {
  min-width: 0;
  overflow-wrap: anywhere;
}

.what-tags {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 4px;
}

.what-tag {
  padding: 1px 8px;
  border-radius: var(--radius-full);
  background: color-mix(in srgb, var(--tag-color) 12%, transparent);
  color: color-mix(in srgb, var(--tag-color) 60%, white);
  font-size: 11px;
  font-weight: 500;
}

.amount {
  text-align: right !important;
  white-space: nowrap;
  font-weight: 500;
}
</style>
