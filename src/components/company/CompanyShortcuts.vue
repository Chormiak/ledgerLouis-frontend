<script setup lang="ts">
import { ArrowRight, ReceiptText, Repeat, Tag } from 'lucide-vue-next';

const shortcuts = [
  { to: { name: 'transactions' }, icon: ReceiptText, title: 'Lançamentos', description: 'Histórico completo, busca e exportação.' },
  { to: { name: 'recurring' }, icon: Repeat, title: 'Recorrências', description: 'Receitas e despesas fixas lançadas sozinhas.' },
  { to: { name: 'tags' }, icon: Tag, title: 'Tags', description: 'Rótulos para catalogar e filtrar.' },
];
</script>

<template>
  <nav class="card shortcuts" aria-labelledby="shortcuts-title">
    <h2 id="shortcuts-title" class="card-title">Atalhos</h2>

    <ul class="list-divided">
      <li v-for="shortcut in shortcuts" :key="shortcut.title">
        <RouterLink :to="shortcut.to" class="shortcut">
          <component :is="shortcut.icon" :size="18" :stroke-width="1.75" class="shortcut-icon" />
          <span class="shortcut-copy">
            <strong>{{ shortcut.title }}</strong>
            <span>{{ shortcut.description }}</span>
          </span>
          <ArrowRight :size="16" class="shortcut-arrow" />
        </RouterLink>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.shortcuts ul {
  margin-top: var(--space-3);
}

.shortcut {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: 0 calc(var(--space-3) * -1);
  padding: var(--space-4) var(--space-3);
  border-radius: var(--radius-md);
  transition: background-color var(--duration-fast) ease;
}

.shortcut:hover {
  background: var(--color-surface-3);
}

.shortcut-icon {
  flex-shrink: 0;
  color: var(--color-primary);
}

.shortcut-copy {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.shortcut-copy strong {
  font-size: var(--text-sm);
  font-weight: 500;
}

.shortcut-copy span {
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
}

.shortcut-arrow {
  color: var(--color-text-subtle);
  transition: color var(--duration-fast) ease;
}

.shortcut:hover .shortcut-arrow {
  color: var(--color-primary);
}
</style>
