<template>
  <li class="transaction-item">
    <div class="transaction-icon" :class="iconClass">
      <component :is="iconComponent" :size="18" />
    </div>

    <div class="transaction-content">
      <div class="transaction-copy">
        <strong>{{ title }}</strong>
        <span>{{ subtitle }}</span>
      </div>

      <div class="transaction-meta">
        <span>{{ date }}</span>
        <strong :class="amountClass">{{ amount }}</strong>
      </div>
    </div>
  </li>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ArrowDownRight, ArrowUpRight } from 'lucide-vue-next';

type TransactionKind = 'income' | 'expense';

const props = defineProps<{
  title: string;
  subtitle: string;
  amount: string;
  date: string;
  kind: TransactionKind;
}>();

const iconComponent = computed(() => (props.kind === 'income' ? ArrowUpRight : ArrowDownRight));

const iconClass = computed(() => ({
  'transaction-icon--income': props.kind === 'income',
  'transaction-icon--expense': props.kind === 'expense',
}));

const amountClass = computed(() => ({
  'amount--income': props.kind === 'income',
  'amount--expense': props.kind === 'expense',
}));
</script>

<style scoped>
.transaction-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 14px;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
}

.transaction-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.transaction-icon {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.transaction-icon--income {
  background: rgba(29, 205, 108, 0.14);
  color: var(--color-success-dark);
}

.transaction-icon--expense {
  background: rgba(229, 33, 36, 0.12);
  color: var(--color-danger);
}

.transaction-content {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.transaction-copy strong {
  display: block;
  color: var(--color-text);
  font-size: 14px;
  font-weight: 800;
  margin-bottom: 4px;
}

.transaction-copy span,
.transaction-meta span {
  color: var(--color-text-secondary);
  font-size: 12px;
  line-height: 1.5;
}

.transaction-meta {
  text-align: right;
}

.transaction-meta strong {
  display: block;
  font-size: 14px;
  font-weight: 800;
  margin-top: 4px;
}

.amount--income {
  color: var(--color-success-dark);
}

.amount--expense {
  color: var(--color-danger);
}
</style>
