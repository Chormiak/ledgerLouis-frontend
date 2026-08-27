<template>
  <main class="invitations-page">
    <section class="invitations-container">
      <header class="header-block">
        <p class="kicker">Convites</p>
        <h1>Seus <span class="accent-text">convites</span></h1>
        <p class="description">
          Veja os convites recebidos para participar de empresas.
        </p>
      </header>

      <div v-if="tokenInvitation" class="invitation-card token-card">
        <div class="invitation-info">
          <div class="invitation-header">
            <h3>Convite para participar de uma empresa</h3>
            <span class="role-badge">{{ tokenInvitation.role }}</span>
          </div>
          <p class="invitation-detail">
            <span class="detail-label">Email:</span> {{ tokenInvitation.email }}
          </p>
          <p class="invitation-detail">
            <span class="detail-label">Expira em:</span> {{ formatDate(tokenInvitation.expiresAt) }}
          </p>
        </div>
        <div class="invitation-actions">
          <PrimaryButton :loading="acceptingId !== null" @click="handleTokenAccept">
            Aceitar convite
          </PrimaryButton>
        </div>
      </div>

      <div v-else-if="tokenError" class="empty-state">
        <p>{{ tokenError }}</p>
      </div>

      <div v-else-if="loading" class="loading-state">
        <p>Carregando convites...</p>
      </div>

      <div v-else-if="invitations.length === 0" class="empty-state">
        <p>Você não tem convites pendentes no momento.</p>
      </div>

      <ul v-else class="invitations-list">
        <li v-for="invitation in invitations" :key="invitation.id" class="invitation-card">
          <div class="invitation-info">
            <div class="invitation-header">
              <h3>Convite para empresa</h3>
              <span class="role-badge" :data-role="invitation.role">{{ invitation.role }}</span>
            </div>
            <p class="invitation-detail">
              <span class="detail-label">Email:</span> {{ invitation.email }}
            </p>
            <p class="invitation-detail">
              <span class="detail-label">Expira em:</span> {{ formatDate(invitation.expiresAt) }}
            </p>
          </div>
          <div class="invitation-actions">
            <PrimaryButton :loading="acceptingId === invitation.id" @click="handleAccept(invitation)">
              Aceitar convite
            </PrimaryButton>
          </div>
        </li>
      </ul>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import CompanyService, { type UserInvitationDto } from '@/services/companyService';
import PrimaryButton from '@/components/ui/PrimaryButton.vue';

const service = new CompanyService();
const route = useRoute();
const router = useRouter();

const loading = ref(true);
const acceptingId = ref<string | null>(null);
const invitations = ref<UserInvitationDto[]>([]);
const tokenInvitation = ref<Omit<UserInvitationDto, 'id'> | null>(null);
const tokenError = ref('');

const formatDate = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('pt-BR');
};

const loadInvitations = async () => {
  loading.value = true;
  try {
    const data = await service.listUserInvitations();
    invitations.value = data.items;
  } catch (error) {
    console.error('Erro ao carregar convites:', error);
    invitations.value = [];
  } finally {
    loading.value = false;
  }
};

const handleAccept = async (invitation: UserInvitationDto) => {
  acceptingId.value = invitation.id;
  try {
    await service.acceptInvitationById(invitation.id);
    await loadInvitations();
  } catch (error) {
    console.error('Erro ao aceitar convite:', error);
  } finally {
    acceptingId.value = null;
  }
};

const handleTokenAccept = async () => {
  const token = route.params.token;
  if (typeof token !== 'string') return;

  acceptingId.value = token;
  try {
    await service.acceptInvitation(token);
    tokenInvitation.value = null;
    tokenError.value = '';
  } catch (error) {
    console.error('Erro ao aceitar convite:', error);
    tokenError.value = 'Não foi possível aceitar este convite.';
  } finally {
    acceptingId.value = null;
  }
};

onMounted(async () => {
  const token = route.params.token;
  if (typeof token === 'string') {
    try {
      tokenInvitation.value = await service.getInvitation(token);
    } catch (error) {
      console.error('Erro ao carregar convite:', error);
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const status = (error as { response?: { status?: number } }).response?.status;
        if (status === 401) {
          await router.replace({ name: 'entrar', query: { redirect: route.fullPath } });
          return;
        }
      }
      tokenError.value = 'Convite inválido, expirado ou destinado a outro email.';
    } finally {
      loading.value = false;
    }
    return;
  }

  await loadInvitations();
});
</script>

<style scoped>
.invitations-page {
  min-height: calc(100vh - 65px);
  padding: 48px 20px 64px;
  background: var(--color-bg);
}

.invitations-container {
  max-width: 720px;
  margin: 0 auto;
}

.header-block {
  margin-bottom: 24px;
}

.kicker {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin-bottom: 14px;
}

h1 {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 800;
  line-height: 1.2;
  color: var(--color-text);
  margin-bottom: 14px;
  text-wrap: balance;
}

.accent-text {
  background: var(--color-success-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.description {
  color: var(--color-text-secondary);
  font-size: 16px;
  line-height: 1.7;
}

.loading-state,
.empty-state {
  padding: 24px;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background: var(--color-surface-alt);
  color: var(--color-text-secondary);
}

.invitations-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 16px;
}

.invitation-card {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  padding: 20px 22px;
  border-radius: 22px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-alt);
}

.invitation-info {
  flex: 1;
  min-width: 0;
}

.invitation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.invitation-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
}

.invitation-detail {
  margin: 4px 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.detail-label {
  font-weight: 600;
  color: var(--color-text);
}

.invitation-actions {
  flex-shrink: 0;
}

.invitation-actions :deep(.primary-btn) {
  width: auto;
  min-width: 160px;
}

.role-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-transform: capitalize;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.role-badge[data-role='owner'] {
  background: var(--color-primary-glow);
  color: var(--color-primary);
  border-color: transparent;
}

@media (max-width: 640px) {
  .invitation-card {
    flex-direction: column;
    align-items: stretch;
  }

  .invitation-actions :deep(.primary-btn) {
    width: 100%;
  }
}
</style>
