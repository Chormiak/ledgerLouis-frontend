<script setup lang="ts">
import { Mail, RefreshCw } from 'lucide-vue-next';
import BaseButton from '@/components/ui/BaseButton.vue';
import { formatDateTime } from '@/utils/format';
import { roleLabel } from './roles';

export interface Invitation {
  id: string;
  email: string;
  role: string;
  expiresAt: string;
}

defineProps<{ invitations: Invitation[]; loading: boolean }>();
defineEmits<{ refresh: []; revoke: [invitation: Invitation] }>();
</script>

<template>
  <section class="card" aria-labelledby="invitations-title">
    <header class="head">
      <div>
        <h2 id="invitations-title" class="card-title">Convites pendentes</h2>
        <p class="card-subtitle">Enviados e ainda não aceitos.</p>
      </div>
      <BaseButton variant="ghost" size="sm" :loading="loading" @click="$emit('refresh')">
        <RefreshCw :size="14" />
        Atualizar
      </BaseButton>
    </header>

    <p v-if="!loading && invitations.length === 0" class="empty-state">Nenhum convite pendente.</p>

    <ul v-else class="list-divided">
      <li v-for="invitation in invitations" :key="invitation.id" class="item">
        <span class="icon" aria-hidden="true"><Mail :size="16" /></span>
        <div class="copy">
          <strong>{{ invitation.email }}</strong>
          <span>{{ roleLabel(invitation.role) }} · expira em {{ formatDateTime(invitation.expiresAt) }}</span>
        </div>
        <BaseButton variant="ghost" size="sm" class="revoke" @click="$emit('revoke', invitation)">Revogar</BaseButton>
      </li>
    </ul>
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

.item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) 0;
}

.icon {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-surface-3);
  color: var(--color-text-muted);
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
  overflow-wrap: anywhere;
}

.copy span {
  font-size: var(--text-xs);
  color: var(--color-text-subtle);
}

.revoke {
  color: var(--color-danger);
}
</style>
