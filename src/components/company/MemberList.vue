<script setup lang="ts">
import { RefreshCw } from 'lucide-vue-next';
import BaseButton from '@/components/ui/BaseButton.vue';
import { roleLabel } from './roles';

export interface Member {
  userId: string;
  name: string;
  email: string;
  role: string;
}

defineProps<{ members: Member[]; loading: boolean }>();
defineEmits<{ refresh: [] }>();
</script>

<template>
  <section class="card" aria-labelledby="members-title">
    <header class="head">
      <div>
        <h2 id="members-title" class="card-title">Membros</h2>
        <p class="card-subtitle">Quem tem acesso às finanças desta empresa.</p>
      </div>
      <BaseButton variant="ghost" size="sm" :loading="loading" @click="$emit('refresh')">
        <RefreshCw :size="14" />
        Atualizar
      </BaseButton>
    </header>

    <div v-if="loading && members.length === 0" class="skeletons">
      <span v-for="n in 2" :key="n" class="skeleton" style="height: 48px" />
    </div>
    <p v-else-if="members.length === 0" class="empty-state">Nenhum membro encontrado.</p>

    <ul v-else class="list-divided">
      <li v-for="member in members" :key="member.userId" class="person">
        <span class="avatar" aria-hidden="true">{{ member.name.charAt(0).toUpperCase() }}</span>
        <div class="copy">
          <strong>{{ member.name }}</strong>
          <span>{{ member.email }}</span>
        </div>
        <span class="badge" :data-tone="member.role === 'owner' ? 'success' : undefined">{{ roleLabel(member.role) }}</span>
      </li>
    </ul>

    <slot />
  </section>
</template>

<style scoped>
.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-3);
}

.skeletons {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.person {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) 0;
}

.avatar {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-surface-3);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  font-weight: 600;
}

.copy {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.copy strong {
  font-size: var(--text-sm);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
}

.copy span {
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
  overflow-wrap: anywhere;
}
</style>
