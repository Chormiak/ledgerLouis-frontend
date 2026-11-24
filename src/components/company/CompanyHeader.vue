<script setup lang="ts">
import { LogOut } from 'lucide-vue-next';
import BaseButton from '@/components/ui/BaseButton.vue';
import { roleLabel } from './roles';

defineProps<{ name: string; role?: string }>();
defineEmits<{ leave: [] }>();
</script>

<template>
  <header class="company-header">
    <div class="mark" aria-hidden="true">{{ name.charAt(0).toUpperCase() }}</div>

    <div class="copy">
      <h1>{{ name }}</h1>
      <p v-if="role">Você participa como <strong>{{ roleLabel(role) }}</strong></p>
    </div>

    <BaseButton variant="secondary" size="sm" class="leave" @click="$emit('leave')">
      <LogOut :size="15" />
      Trocar de empresa
    </BaseButton>
  </header>
</template>

<style scoped>
.company-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-4) var(--space-5);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.mark {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-primary-ring);
  background: var(--color-primary-soft);
  color: var(--color-primary-strong);
  font-size: 1.5rem;
  font-weight: 600;
}

.copy {
  flex: 1 1 240px;
  min-width: 0;
}

h1 {
  font-size: var(--text-2xl);
  font-weight: 600;
  letter-spacing: -0.04em;
  overflow-wrap: anywhere;
}

.copy p {
  margin-top: var(--space-1);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.copy strong {
  font-weight: 500;
  color: var(--color-text);
}

@media (max-width: 560px) {
  .leave {
    width: 100%;
  }
}
</style>
