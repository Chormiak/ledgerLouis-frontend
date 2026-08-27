<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { Tags } from 'lucide-vue-next';
import { useTagStore } from '@/stores/tagStore';
import { useTransactionStore } from '@/stores/transactionStore';
import { colorForTag } from '@/utils/tagColor';

const tagStore = useTagStore();
const transactionStore = useTransactionStore();

const transactionIds = computed(() => transactionStore.transactions.map((t) => t.id));

const loadTagData = async () => {
  await tagStore.fetchTags();
  await tagStore.loadTagsForTransactions(transactionIds.value);
};

onMounted(loadTagData);

watch(
  () => transactionIds.value.join(','),
  () => {
    tagStore.loadTagsForTransactions(transactionIds.value);
  },
);

const tagCounts = computed(() => {
  const counts = new Map<string, number>();

  for (const transaction of transactionStore.transactions) {
    const tags = tagStore.transactionTagsMap[transaction.id] ?? [];
    for (const tag of tags) {
      counts.set(tag.id, (counts.get(tag.id) ?? 0) + 1);
    }
  }

  return counts;
});

const visibleTags = computed(() => tagStore.tags.filter((tag) => (tagCounts.value.get(tag.id) ?? 0) > 0));

const selectTag = (id: string | null) => {
  tagStore.setActiveTag(id);
};

const activeChipStyle = (id: string) => ({
  backgroundColor: colorForTag(id),
  borderColor: colorForTag(id),
  color: '#fff',
});
</script>

<template>
  <section v-if="visibleTags.length > 0" class="tag-filter-bar" aria-label="Filtrar transações por tag">
    <div class="tag-filter-kicker">
      <Tags :size="16" />
      <span>Filtrar por tag</span>
      <router-link class="tag-manage-link" :to="{ name: 'tags' }">Gerenciar tags</router-link>
    </div>

    <div class="tag-chip-row">
      <button
        type="button"
        class="tag-chip"
        :class="{ 'tag-chip--active': tagStore.activeTagId === null }"
        @click="selectTag(null)"
      >
        Todas
      </button>

      <button
        v-for="tag in visibleTags"
        :key="tag.id"
        type="button"
        class="tag-chip"
        :class="{ 'tag-chip--active': tagStore.activeTagId === tag.id }"
        :style="tagStore.activeTagId === tag.id ? activeChipStyle(tag.id) : {}"
        @click="selectTag(tag.id)"
      >
        <span class="tag-chip-dot" :style="{ backgroundColor: colorForTag(tag.id) }"></span>
        {{ tag.name }}
        <span class="tag-chip-count">{{ tagCounts.get(tag.id) ?? 0 }}</span>
      </button>
    </div>
  </section>
</template>

<style scoped>
.tag-filter-bar {
  display: grid;
  gap: 10px;
  padding: 16px 18px;
  border-radius: 16px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.tag-filter-kicker {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 700;
}

.tag-manage-link {
  margin-left: auto;
  color: var(--color-success-dark);
  text-decoration: none;
  font-size: 12px;
  font-weight: 700;
}

.tag-manage-link:hover {
  text-decoration: underline;
}

.tag-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft);
  color: var(--color-text);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.tag-chip:hover {
  border-color: var(--color-text-secondary);
}

.tag-chip--active {
  background: var(--color-primary);
  color: var(--color-surface);
  border-color: var(--color-primary);
}

.tag-chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  flex-shrink: 0;
}

.tag-chip-count {
  opacity: 0.7;
  font-weight: 600;
}
</style>
