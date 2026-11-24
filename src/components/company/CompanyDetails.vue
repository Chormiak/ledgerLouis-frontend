<script setup lang="ts">
import { computed } from 'vue';
import { formatCnpj } from './formatCnpj';

const props = defineProps<{ name: string; cnpj?: string; email?: string; phone?: string }>();

const rows = computed(() => [
  { label: 'Razão social', value: props.name },
  { label: 'CNPJ', value: props.cnpj ? formatCnpj(props.cnpj) : '', mono: true },
  { label: 'E-mail', value: props.email },
  { label: 'Telefone', value: props.phone, mono: true },
]);
</script>

<template>
  <section class="card" aria-labelledby="details-title">
    <h2 id="details-title" class="card-title">Dados da empresa</h2>

    <dl class="rows">
      <div v-for="row in rows" :key="row.label" class="row">
        <dt>{{ row.label }}</dt>
        <dd :class="{ 'is-empty': !row.value, figure: row.mono && row.value }">{{ row.value || 'Não informado' }}</dd>
      </div>
    </dl>
  </section>
</template>

<style scoped>
.rows {
  margin-top: var(--space-4);
}

.row {
  display: grid;
  grid-template-columns: minmax(110px, 0.35fr) minmax(0, 1fr);
  gap: var(--space-4);
  padding: var(--space-3) 0;
  border-top: 1px solid var(--color-border);
  font-size: var(--text-sm);
}

dt {
  color: var(--color-text-subtle);
}

dd {
  font-weight: 500;
  overflow-wrap: anywhere;
}

dd.figure {
  letter-spacing: -0.02em;
}

dd.is-empty {
  font-weight: 400;
  color: var(--color-text-subtle);
}
</style>
